import os
import requests
import toml
from datetime import datetime, timedelta, timezone
from supabase import create_client

# 1. 환경 설정
KST = timezone(timedelta(hours=9))

try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    secrets_path = os.path.join(current_dir, ".streamlit", "secrets.toml")
    
    if os.path.exists(secrets_path): # 로컬
        secrets = toml.load(secrets_path)
        SUPABASE_URL = secrets["supabase"]["SUPABASE_URL"]
        SUPABASE_KEY = secrets["supabase"]["SUPABASE_KEY"]
        AUTH_KEY = secrets.get("exim", {}).get("EXIM_KEY")
    else: # GitHub Actions
        SUPABASE_URL = os.environ.get("SUPABASE_URL")
        SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
        AUTH_KEY = os.environ.get("EXIM_KEY")

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"❌ 설정 로드 실패: {e}")
    exit()

# 2. 기능 함수
def fetch_today_rate_api(target_date):
    search_date_str = target_date.strftime("%Y%m%d")
    url = "https://oapi.koreaexim.go.kr/site/program/financial/exchangeJSON"
    params = {"authkey": AUTH_KEY, "searchdate": search_date_str, "data": "AP01"}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            print(f"⚠️ 서버 응답 코드 에러: {response.status_code}")
            return "ERROR"

        try:
            json_data = response.json()
        except:
            return "ERROR"
        
        if not json_data:
            return None 

        for item in json_data:
            if item['cur_unit'] == "USD":
                return float(item['deal_bas_r'].replace(",", ""))
                
    except Exception as e:
        print(f"⚠️ 연결/로직 에러: {e}")
        return "ERROR"
    
    return None

def get_latest_rate_from_db():
    try:
        response = supabase.table("exchange_rates").select("*").order("date", desc=True).limit(1).execute()
        if response.data: return response.data[0]
    except Exception as e:
        print(f"❌ DB 조회 실패: {e}")
    return None

def save_to_db(date_str, rate):
    try:
        data = {"date": date_str, "usd_krw": rate}
        supabase.table("exchange_rates").upsert(data).execute()
        print(f"💾 DB 저장 완료: {date_str} - {rate}원")
    except Exception as e:
        print(f"❌ DB 저장 실패: {e}")

# 3. 메인 로직 
def update_exchange_rate():
    now_kst = datetime.now(KST)
    today_str = now_kst.strftime("%Y-%m-%d")
    
    print(f"📅 [환율 작업 시작] {today_str}")

    # 1. 중복 확인
    try:
        check = supabase.table("exchange_rates").select("date").eq("date", today_str).execute()
        if check.data:
            print(f"ℹ️ {today_str} 환율은 이미 DB에 있습니다. 종료합니다.")
            return
    except:
        pass

    # 2. API 호출
    rate = fetch_today_rate_api(now_kst)

    if isinstance(rate, float):
        print(f"✅ 오늘 환율 조회 성공: {rate}원")
        save_to_db(today_str, rate)

    elif rate == "ERROR":
        print("🚫 API 서버 오류. 작업을 중단합니다.")

    else:
        print("💤 데이터가 없습니다(주말 또는 공휴일). 직전 데이터를 복사합니다.")
        
        latest_data = get_latest_rate_from_db()
        if latest_data:
            last_rate = latest_data['usd_krw']
            print(f"🔄 직전 데이터({latest_data['date']})인 {last_rate}원을 오늘 날짜로 저장합니다.")
            save_to_db(today_str, last_rate)
        else:
            print("⚠️ 복사할 이전 데이터가 없습니다.")

if __name__ == "__main__":
    update_exchange_rate()