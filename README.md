# Quant-Lab

금융 리포트 수집·요약과 투자 데이터 분석을 위한 개인 프로젝트입니다. Streamlit 대시보드에서 시장 브리핑을 확인하고, 별도 페이지에서 포트폴리오 시뮬레이션과 종목 분석을 할 수 있습니다.

## 주요 기능

- **시장 브리핑**: 검색한 리포트에서 텍스트를 추출하고 Gemini로 요약·종합하여 Supabase에 저장합니다. 한국어·영어 종합 브리핑을 대시보드에 표시하고 구독자에게 이메일을 발송하는 작업이 포함되어 있습니다.
- **포트폴리오 시뮬레이션**: yfinance 주가와 Supabase 환율 데이터를 활용합니다. 환율 데이터가 없으면 코드에 설정된 고정 환율로 대체하므로 결과를 해석할 때 주의해야 합니다.
- **종목 분석**: 주가·거래량과 RSI, 이동평균 등 기술 지표를 활용합니다.

자동 수집·요약에는 외부 API와 데이터베이스, 이메일 설정이 필요합니다. 수집 가능 여부 및 결과는 외부 서비스와 데이터 품질에 영향을 받습니다. 분석과 시뮬레이션 결과는 투자 판단의 보조 자료이며 수익을 보장하지 않습니다.

## 구성

| 경로 | 역할 |
| --- | --- |
| `main.py` | Streamlit 메인 화면과 구독 신청·취소 |
| `pages/` | 포트폴리오 시뮬레이션 및 종목 분석 페이지 |
| `daily_job.py` | 리포트 검색·추출·요약·저장 및 이메일 발송 |
| `services/` | 검색, 크롤링, LLM, 데이터베이스, 이메일 서비스 |
| `config/` | 환경 설정과 요약 프롬프트 |
| `update_rates.py` | 환율 데이터 갱신 스크립트 |
| `.github/workflows/` | 정기 실행 워크플로 |

## 로컬 실행

워크플로에는 Python 3.12가 설정되어 있습니다. 의존성과 외부 서비스의 현재 호환성은 별도 확인이 필요합니다.

```bash
git clone https://github.com/RevolTac71/Quant-Lab.git
cd Quant-Lab
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run main.py
```

메인 화면의 데이터 조회에는 Supabase 연결이 필요합니다. `config/settings.py`는 환경변수 또는 `.streamlit/secrets.toml`에서 설정을 읽습니다. 환경변수 이름은 다음과 같습니다.

- Supabase: `SUPABASE_URL`, `SUPABASE_KEY`
- 검색·요약: `GOOGLE_SEARCH_API_KEY`, `SEARCH_ENGINE_ID`, `GEMINI_API_KEY`
- 이메일: `GMAIL_USER`, `GMAIL_APP_PWD`

`secrets.toml`에서는 각각 `[supabase]`, `[google]`, `[GMAIL]` 아래에 같은 이름의 값을 둡니다. 데이터베이스 테이블 및 접근 권한이 별도로 필요하며, 이 저장소에는 전체 스키마 생성 절차가 문서화되어 있지 않습니다. 실제 키와 구독자 데이터는 커밋하지 마세요.

## 정기 작업

`.github/workflows/daily_run.yml`은 리포트 작업을 매일 UTC 22:30(한국 시간 다음 날 07:30)에 실행하도록 설정합니다. GitHub Actions의 실행 시간은 지연될 수 있습니다. `python daily_job.py`는 리포트 저장과 이메일 발송을 수행할 수 있으므로, 실행 전 연결 대상과 구독자 데이터를 확인하세요.

## 현재 확인이 필요한 부분

- 저장소에는 데이터베이스 스키마와 재현용 샘플 데이터가 제공되지 않습니다.
- 의존성 버전이 고정되어 있지 않아 새 환경에서 설치·동작이 달라질 수 있습니다.
- 외부 API와 실제 서비스 연결을 포함한 전체 실행은 이 문서 작성 과정에서 검증하지 않았습니다.
