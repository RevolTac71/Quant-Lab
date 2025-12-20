import pandas as pd
import requests
import os
from datetime import datetime, timedelta

# GitHub Secrets에서 키 가져오기
AUTH_KEY = os.environ.get("EXIM_KEY")
DATA_PATH = "data/exchange_rates.csv"

def fetch_today_rate():
    target_date = datetime.now()
    search_date_str = target_date.strftime("%Y%m%d")
    display_date = target_date.strftime("%Y-%m-%d")
    
    url = "https://oapi.koreaexim.go.kr/site/program/financial/exchangeJSON"
    params = {
        "authkey": AUTH_KEY,
        "searchdate": search_date_str,
        "data": "AP01"
    }
    
    try:
        # 타임아웃 5초 설정 (응답 없으면 빨리 끊기)
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200 and response.json():
            json_data = response.json()
            for item in json_data:
                if item['cur_unit'] == "USD":
                    rate = float(item['deal_bas_r'].replace(",", ""))
                    return {"Date": display_date, "USD_KRW": rate}
                    
    except Exception as e:
        print(f"⚠️ API 호출 중 에러 (휴일일 수 있음): {e}")
    
    return None

def update_csv():
    # 1. 기존 파일 읽기 (없으면 빈 DataFrame 생성)
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
    else:
        df = pd.DataFrame(columns=["Date", "USD_KRW"])
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # 2. 이미 오늘 데이터가 있는지 확인 (중복 방지)
    if today_str in df['Date'].values:
        print(f"ℹ️ {today_str} 데이터는 이미 존재합니다.")
        return

    # 3. 오늘 데이터 가져오기 시도
    new_data = fetch_today_rate()
    
    if new_data:
        # [CASE 1] 평일: API 데이터가 정상적으로 있음
        print(f"✅ 오늘 환율 확보: {new_data}")
        new_row = pd.DataFrame([new_data])
        df = pd.concat([df, new_row], ignore_index=True)
        
    else:
        # [CASE 2] 휴일/주말: API 데이터가 없음 -> '직전 데이터' 복사
        print("❌ 오늘은 환율 데이터가 없습니다 (휴일/주말). 직전 데이터를 불러옵니다.")
        
        if not df.empty:
            last_rate = df.iloc[-1]['USD_KRW'] # 가장 마지막 행의 환율 가져오기
            print(f"🔄 직전 환율({last_rate})로 오늘({today_str}) 데이터를 채웁니다.")
            
            fill_data = {"Date": today_str, "USD_KRW": last_rate}
            new_row = pd.DataFrame([fill_data])
            df = pd.concat([df, new_row], ignore_index=True)
        else:
            print("⚠️ 기존 데이터가 하나도 없어 채울 수 없습니다.")
            return

    # 4. 저장
    df.to_csv(DATA_PATH, index=False)
    print("💾 CSV 업데이트 완료")

if __name__ == "__main__":
    # 데이터 폴더가 없으면 생성
    if not os.path.exists('data'):
        os.makedirs('data')
        
    update_csv()