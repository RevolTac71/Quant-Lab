import streamlit as st
import os
import toml
import smtplib
from email.mime.text import MIMEText
from supabase import create_client
from datetime import datetime, timedelta, timezone
from sidebar import render_sidebar

# ---------------------------------------------------------
# 1. 초기 설정 및 DB 연결
# ---------------------------------------------------------
st.set_page_config(
    page_title="Quant Lab",
    page_icon="💸",
    layout="wide"
)

# CSS 스타일
st.markdown("""
    <style>
    /* Expander(접기/펼치기) 폰트 크기 최적화 */
    .streamlit-expanderContent p {
        font-size: 1rem;
        line-height: 1.6;
    }
    /* 큰 화면에서 오른쪽 컬럼 Sticky 처리 */
    @media (min-width: 992px) {
        div[data-testid="stColumn"]:nth-of-type(2) {
            position: sticky;
            top: 2rem;
            z-index: 1000;
            height: fit-content;
        }
    }
    </style>
""", unsafe_allow_html=True)

render_sidebar()

# Supabase 연결
@st.cache_resource
def init_supabase():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    secrets_path = os.path.join(base_dir, ".streamlit", "secrets.toml")
    
    if os.path.exists(secrets_path):
        secrets = toml.load(secrets_path)
        SUPABASE_URL = secrets["supabase"]["SUPABASE_URL"]
        SUPABASE_KEY = secrets["supabase"]["SUPABASE_KEY"]
    else:
        SUPABASE_URL = os.environ.get("SUPABASE_URL")
        SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
        
        if not SUPABASE_URL:
            try:
                SUPABASE_URL = st.secrets["supabase"]["SUPABASE_URL"]
                SUPABASE_KEY = st.secrets["supabase"]["SUPABASE_KEY"]
            except:
                pass

    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = init_supabase()
except Exception as e:
    st.error(f"DB 연결 실패: secrets.toml을 확인해주세요. ({e})")
    st.stop()

# ---------------------------------------------------------
# 2. 핵심 로직 함수
# ---------------------------------------------------------

def log_action(email, action_type):
    try:
        supabase.table("subscription_logs").insert({
            "email": email,
            "action_type": action_type
        }).execute()
    except Exception as e:
        print(f"로그 저장 실패: {e}")

def send_subscription_alert(new_email):
    try:
        sender = st.secrets["GMAIL"]["GMAIL_USER"]
        password = st.secrets["GMAIL"]["GMAIL_APP_PWD"]
        admin_email = "ksmsk0701@gmail.com"

        msg = MIMEText(f"DB에 새로운 구독자가 등록되었습니다!\n\n이메일: {new_email}")
        msg['Subject'] = f"🔔 신규 구독자: {new_email}"
        msg['From'] = sender
        msg['To'] = admin_email

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"메일 발송 에러: {e}")
        return False

def subscribe_user_to_db(email, language='ko'):
    try:
        KST = timezone(timedelta(hours=9))
        now_kst = datetime.now(KST)
        current_date = now_kst.strftime("%Y-%m-%d")
        
        data = {
            "email": email, 
            "is_active": True, 
            "language": language,
            "start_date": current_date, 
        }
        
        supabase.table("subscribers").upsert(data, on_conflict='email').execute()
        log_action(email, 'SUBSCRIBE')
        send_subscription_alert(email)
        return "success"
    except Exception as e:
        return f"error: {str(e)}"

def unsubscribe_user_from_db(email):
    try:
        check = supabase.table("subscribers").select("*").eq("email", email).execute()
        if not check.data:
            return "not_found"

        KST = timezone(timedelta(hours=9))
        now_kst = datetime.now(KST)
        current_date = now_kst.strftime("%Y-%m-%d")

        supabase.table("subscribers").update({
            "is_active": False,
            "end_date": current_date
        }).eq("email", email).execute()
        
        log_action(email, 'UNSUBSCRIBE')
        return "success"
    except Exception as e:
        return f"error: {str(e)}"

# 3. 메인 페이지 구성
st.title("📰 오늘의 글로벌 기관 리포트 (Today's Global Reports)")
st.divider()

# 레이아웃 비율 [2:1]
col1, col2 = st.columns([2, 1], gap="large")

# [왼쪽 컬럼] 리포트 내용
with col1:
    lang_option = st.radio("언어 선택 (Language)", ["🇰🇷 한국어", "🇺🇸 English"], horizontal=True, label_visibility="collapsed")
    selected_lang_code = 'ko' if "한국어" in lang_option else 'en'
    
    try:
        db_response = supabase.table("daily_reports").select("*").order("created_at", desc=True).limit(1).execute()
        
        if db_response.data:
            latest_report = db_response.data[0]
            
            if selected_lang_code == 'ko':
                summary_text = latest_report.get('summary_ko', '한국어 요약이 없습니다.')
                split_keyword = "## 🔍 심층 마켓 분석"
            else:
                summary_text = latest_report.get('summary_en', 'English summary not available.')
                split_keyword = "## 🔍 Deep Dive Analysis"
            
            # [UI 개선] 섹션 제목 기준 분리
            if split_keyword in summary_text:
                parts = summary_text.split(split_keyword, 1)
                dashboard_text = parts[0].strip()
                deep_dive_text = split_keyword + parts[1]
                
                st.markdown(dashboard_text)
                st.write("") 
                
                with st.expander("🔍 심층 마켓 분석 (Deep Dive Analysis) 전체 보기", expanded=False):
                    st.markdown(deep_dive_text)
            
            # (백업) 구분선 기준 분리
            elif "---" in summary_text:
                parts = summary_text.split("---", 1)
                st.markdown(parts[0].strip())
                st.write("")
                with st.expander("🔍 심층 마켓 분석 (Deep Dive Analysis) 전체 보기", expanded=False):
                    st.markdown(parts[1].strip())
            
            else:
                st.markdown(summary_text)
            
        else:
            st.info("😴 아직 발행된 리포트가 없습니다. 내일 아침에 다시 방문해주세요!")
            
    except Exception as e:
        st.error(f"리포트를 불러오는 중 오류가 발생했습니다: {e}")

# [오른쪽 컬럼] 구독 및 안내 (사이드바 내용 제거됨)
with col2:
    with st.container(border=True):
        st.info("💡 **QuantLab 활용법**")
        st.markdown("""
        1. **매일 아침 8시** 업데이트
        2. **Dashboard**: 리포트 3분 요약
        3. **무료 구독**: 매일 이메일로 개별 리포트 요약본까지 발송
        """)
    
    st.write("")

    # 구독 탭
    tab_sub, tab_unsub = st.tabs(["📩 구독 신청", "👋 구독 취소"])
    
    with tab_sub:
        with st.form(key='sub_form'):
            sub_email = st.text_input("이메일 주소", placeholder="example@email.com")
            pref_lang = st.selectbox("리포트 언어", ["Korean (한국어)", "English (영어)"])
            sub_btn = st.form_submit_button("무료 구독하기", use_container_width=True)
            
            if sub_btn:
                if "@" not in sub_email:
                    st.warning("올바른 이메일 형식을 입력해주세요.")
                else:
                    lang_code = 'en' if "English" in pref_lang else 'ko'
                    with st.spinner("DB 등록 중..."):
                        result = subscribe_user_to_db(sub_email, lang_code)
                        if result == "success":
                            st.toast("구독 완료! 환영합니다 🎉", icon="✅")
                            st.success(f"'{sub_email}'님이 구독 리스트에 등록되었습니다.")
                        else:
                            st.error(f"오류 발생: {result}")

    with tab_unsub:
        with st.form(key='unsub_form'):
            unsub_email = st.text_input("구독했던 이메일", placeholder="example@email.com")
            unsub_btn = st.form_submit_button("구독 취소하기", use_container_width=True)
            
            if unsub_btn:
                with st.spinner("처리 중..."):
                    result = unsubscribe_user_from_db(unsub_email)
                    if result == "success":
                        st.toast("구독 취소 완료. 다음에 또 만나요! 👋", icon="✅")
                    elif result == "not_found":
                        st.warning("구독 정보를 찾을 수 없습니다.")
                    else:
                        st.error(f"오류 발생: {result}")
    
    st.divider()
                  
    st.caption("☕ **Buy Me a Coffee**")
    buymeacoffee_url = "https://www.buymeacoffee.com/revoltac"
    st.markdown(f"""
        <div style="text-align:center;">
            <a href="{buymeacoffee_url}" target="_blank">
                <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" style="width: 350px; border-radius: 8px;" >
            </a>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    st.caption("Contact: ksmsk0701@gmail.com")