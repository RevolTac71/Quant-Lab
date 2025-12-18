import pandas as pd
import requests
import os
from datetime import datetime, timedelta

# GitHub Secrets에서 키 가져오기
AUTH_KEY = os.environ.get("EXIM_KEY")
DATA_PATH = "data/exchange_rates.csv"

def fetch_today_rate():
    # 오늘 날짜 (주말이면 데이터가 없으므로 최근 평일 로직이 필요하지만, 
    # 여기서는 매일 실행하되 데이터가 있을 때만 저장하는 방식으로 처리)
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
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200 and response.json():
            json_data = response.json()
            for item in json_data:
                if item['cur_unit'] == "USD":
                    rate = float(item['deal_bas_r'].replace(",", ""))
                    return {"Date": display_date, "USD_KRW": rate}
    except Exception as e:
        print(f"Error fetching data: {e}")
    
    return None

def update_csv():
    # 1. 기존 파일 읽기 (없으면 생성)
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
    else:
        df = pd.DataFrame(columns=["Date", "USD_KRW"])
    
    # 2. 오늘 데이터 가져오기
    new_data = fetch_today_rate()
    
    if new_data:
        print(f"✅ 오늘 환율 확보: {new_data}")
        
        # 날짜 중복 체크
        if new_data['Date'] not in df['Date'].values:
            new_row = pd.DataFrame([new_data])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(DATA_PATH, index=False)
            print("💾 CSV 업데이트 완료")
        else:
            print("ℹ️ 이미 존재하는 날짜입니다.")
    else:
        print("❌ 오늘은 환율 데이터가 없습니다 (휴일 또는 장 마감 전)")

if __name__ == "__main__":
    # 데이터 폴더가 없으면 생성
    if not os.path.exists('data'):
        os.makedirs('data')
        
    update_csv()