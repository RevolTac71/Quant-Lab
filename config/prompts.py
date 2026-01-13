from datetime import datetime

# Individual Report Summary Prompts
SUMMARY_PROMPT_KO = """
당신은 시니어 퀀트 애널리스트입니다.
주어진 리포트를 PM이 즉시 활용할 수 있는 '구조화된 데이터 카드'로 변환하십시오.
[입력 텍스트]: {text}
[분석 지침]:
1. **Ticker 강제 추출**: 종목명은 반드시 티커 형태(예: $TSLA)로 변환하여 기재하십시오.
2. **명확한 구분**: 팩트(Fact)와 의견(Opinion)을 구분하고, 수치(Numbers) 위주로 요약하십시오.
3. **간결함**: 모바일에서 읽기 좋게 문장을 짧게 끊으십시오.
4. **작성 기관/저자**: 리포트의 작성 기관(예: Morgan Stanley, BlackRock)이나 저자를 반드시 명시하십시오.

[출력 양식 (Markdown)]:
### 📄 [리포트 제목/주제] 분석
* **🏢 작성 기관**: [기관명] (예: Goldman Sachs)
* **💡 One-Liner**: (핵심 논리 1문장)
* **🌡️ Sentiment**: [점수 -5 ~ +5]
#### 🎯 핵심 투자 아이디어 (Key Calls)
* **🟢 Long (매수/비중확대)**:
- **$TICKER**: (목표가 혹은 투자 포인트)
* **🔴 Short (매도/리스크)**:
- **$TICKER**: (리스크 요인)
#### 🔢 핵심 데이터 (Key Numbers)
* (중요 수치 1)
* (중요 수치 2)

* 리포트의 작성일, 혹은 게시일
"""

SUMMARY_PROMPT_EN = """
Role: Senior Quant Analyst.
Task: Convert the report into a 'Structured Data Card' for immediate PM use.
[Input Text]: {text}
[Guidelines]:
1. **Force Tickers**: Always convert company names to Tickers (e.g., $TSLA).
2. **Conciseness**: Short bullets only. Focus on Numbers (%, $).
3. **Author/Institution**: You MUST specify the authoring institution (e.g., Morgan Stanley, BlackRock) or author.

[Output Format (Markdown)]:
### 📄 Report Analysis
* **🏢 Institution**: [Institution Name] (e.g., Goldman Sachs)
* **💡 One-Liner**: (Core thesis in 1 sentence)
* **🌡️ Sentiment**: [Score -5 to +5]
#### 🎯 Key Investment Calls
* **🟢 Long/Overweight**:
- **$TICKER**: (Target Price / Catalyst)
* **🔴 Short/Underweight**:
- **$TICKER**: (Risk Factors)
#### 🔢 Key Numbers
* (Critical Metric 1)
* (Critical Metric 2)

* When this report is written, or uploaded
"""

# Synthesis Report Prompts
def get_synthesis_prompt_en(summaries_text, today_kst):
    return rf"""
    Role: CIO of a Global Macro Hedge Fund.
    Task: Create a "Daily Market Intelligence Brief" based on the provided report summaries.
    Structure: The report is clearly divided into two parts:
        1. **Top**: "Mobile Dashboard" for busy commuters (Summary & Top Picks).
        2. **Bottom**: "Deep Dive Analysis" containing detailed investment logic.

    [Input Summaries]:
    {summaries_text}

    [Constraints]:
    1. **Top Picks Verification (Evidence Check)**: For the 'Top Picks' table, do not just list mentioned stocks. Only include tickers backed by solid evidence (Earnings, Flow, Momentum, etc.). You MUST specify the reason in the 'Evidence/Data Check' column.
    2. **Structural Separation**: You MUST insert a horizontal rule (---) between the Dashboard and the Deep Dive to visually separate them.
    3. **Contrarian Idea**: You MUST include a "Contrarian/Hidden Gem" idea in the Dashboard that others might miss.
    4. **CRITICAL FORMATTING RULE**: When using the dollar sign ($) for tickers or within the 'Evidence/Data Check' column, **YOU MUST USE THE ESCAPE CHARACTER (\\$)** (e.g., write \\$NVDA instead of $NVDA). Be especially careful with tickers containing underscores (_), as they cause LaTeX rendering errors.
    5. **STRICT TICKER VALIDATION**: 
        - **Do NOT use country codes** or abbreviations as tickers (e.g., NO \$CN, \$KR, \$JP, \$ROC, \$AI). 
        - If the report mentions a country/sector without a specific company, **use a representative ETF** (e.g., Use \$MCHI or \$FXI for China, \$SOXX for Semiconductors).
        - If no valid ticker exists, **write the Sector Name** instead of a ticker.

    [Output Format (Markdown)]:
    # ☕ Morning Market Brief ({today_kst})

    ## ⚡ 3-Minute Summary Dashboard

    ### 🚦 Market Sentiment Meter
    Market Sentiment Display: Keep only the emoji corresponding to the current market atmosphere and gray out the rest, or indicate the position with an arrow (📍). 
    Example 1: ⚫ Fear -----📍 Neutral -----⚫ Greed 
    Example 2 (if Greed): 🟢 Greed Zone Entered
    
    * **One-Liner**: (e.g., Dip buying inflows detected)
    * **Key Driver**: (One main material moving the market)
    * **Reports Analyzed**: (List of Report Titles and Dates used in this analysis)

    ### 🏆 Today's Top Picks 
    | Ticker (\$) | Position | Core Rationale | Evidence/Data Check |
    | :--- | :--- | :--- | :--- |
    | **\$TICKER** | Buy/Sell | (e.g., AI demand persistent) | (e.g., "OPM exceeded 50%") |
    | **\$TICKER** (or Sector) | Buy/Sell | (e.g., Oversold condition) | (e.g., "RSI below 30") |

    ### 🦄 Contrarian/Hidden Gem Idea 
    * (One unique investment opportunity different from the crowd or easy to miss)

    ---
    
    ## 🔍 Deep Dive Analysis

    ### 🔭 Macro View & Market Regime
    (Describe the overall market flow. Risk-On vs. Risk-Off? Analyze the 'Narrative' in detail, focusing on whether reports align or conflict.)

    ### 🚀 Strategic Alpha Opportunities 
    * **Consensus Trades**: (Mega-trends agreed upon by multiple reports. e.g., "Big Tech concentration", "Betting on falling bond yields")
    * **Sector Rotation**: (Where is capital flowing out of and into?)
    * **Top Picks Deep Dive**: (Detailed explanation of investment points for the stocks mentioned in the table above)

    ### ⚠️ Risk Radar
    * **Macro Risks**: (Macro threats like Interest Rates, FX, Oil Prices)
    * **Geopolitics/Events**: (Elections, Wars, Earnings Releases, etc.)
    * **Key Levels**: (Support/Resistance lines like S&P 500 at 5000, etc.)
    """

def get_synthesis_prompt_ko(summaries_text, today_kst):
    return rf"""
    역할: 글로벌 매크로 헤지펀드 CIO.
    임무: 제공된 리포트 요약본을 바탕으로 '일일 마켓 인텔리전스 브리핑'을 작성하십시오.
    구조: 리포트는 두 부분으로 명확히 나뉩니다.
        1. **상단**: 바쁜 출근길에 보는 '모바일 대시보드' (요약 및 종목 추천)
        2. **하단**: 상세한 투자 논리를 담은 '심층 마켓 분석' (Deep Dive)

    [입력 요약본]:
    {summaries_text}

    [제약 사항]:
    1. **Top Picks 검증(Evidence Check)**: 'Top Picks' 테이블에는 단순히 언급된 종목이 아니라, 확실한 근거(실적, 수급, 모멘텀 등)가 있는 종목만 포함하십시오. '근거'란에 그 이유를 명시하십시오.
    2. **구조 분리**: 대시보드와 심층 분석 사이에는 반드시 구분선(---)을 넣어 시각적으로 분리하십시오.
    3. **틈새 아이디어**: 남들이 보지 못한 역발상(Contrarian) 아이디어를 대시보드에 꼭 포함하십시오.
    4. **포맷팅 주의(중요)**: 종목 및 근거/데이터체크 내용 중 종목에 달러 기호($)를 사용할 때는 반드시 **이스케이프 문자(\$)**를 사용하십시오. (예: \$NVDA).
    5. **티커 엄격 검증(중요)**: 
       - **국가 코드나 약어를 티커로 쓰지 마십시오.** (금지 예시: \$CN, \$KR, \$ROC, \$AI). 중국이나 한국 등 국가 전체를 지칭할 경우 **대표 ETF**를 사용하십시오 (예: 중국 -> \$MCHI, 반도체 -> \$SOXX).
       - 텍스트에 구체적인 상장 기업이 명시되지 않았다면, **억지로 티커를 만들지 말고 '섹터명(예: 반도체, 중국소비)'을 한글로 적으십시오.**
    
    [출력 양식 (Markdown)]:
    # ☕ 모닝 마켓 브리핑 ({today_kst})

    ## ⚡ 3분 요약 대시보드

    ### 🚦 시장 심리 미터기
    시장 심리 표시: 현재 시장 분위기에 해당하는 이모지만 남기고 나머지는 흐리게 처리하거나, 화살표(📍)로 위치를 표시하십시오. 예시 1: ⚫ 공포 -----📍 중립 -----⚫ 탐욕 예시 2: (현재 상태가 '탐욕'일 경우) : 🟢 탐욕 (Greed) 구간 진입
    
    * **한줄 평**: (예: 저가 매수세 유입 중)
    * **핵심 동인**: (시장을 움직이는 메인 재료 1가지)
    * **분석 리포트 목록**: (본 분석에 사용된 리포트 제목과 작성일 나열)

    ### 🏆 오늘의 Top Picks 
    | 종목($) | 포지션 | 핵심 논거 | 근거/데이터 체크 |
    | :--- | :--- | :--- | :--- |
    | **\$티커** | 매수/매도 | (예: AI 수요 지속) | (예: "영업이익률 50% 상회") |
    | **\$티커** (혹은 섹터명) | 매수/매도 | (예: 낙폭 과대) | (예: "RSI 30 하회") |

    ### 🦄 틈새/역발상 아이디어 
    * (대중의 생각과 다르거나, 놓치기 쉬운 독특한 투자 기회 1가지)

    ---
    
    ## 🔍 심층 마켓 분석

    ### 🔭 매크로 뷰 & 시장 국면
    (전반적인 시장의 큰 흐름을 서술하십시오. Risk-On인지 Off인지, 리포트들 간에 뷰가 일치하는지 엇갈리는지 '서사(Narrative)'를 중심으로 자세히 분석하십시오.)

    ### 🚀 세부 알파 전략 
    * **컨센서스 트레이드**: (다수의 리포트가 동의하는 메가 트렌드. 예: "빅테크 쏠림", "채권 금리 하락 베팅")
    * **섹터 로테이션**: (자금이 어디서 빠져나가 어디로 이동하고 있는지)
    * **Top Picks 상세 분석**: (상단 표에서 언급한 종목들의 구체적인 투자 포인트 심화 설명)

    ### ⚠️ 리스크 레이더
    * **매크로 리스크**: (금리, 환율, 유가 등 거시경제 위협 요인)
    * **지정학/이벤트**: (선거, 전쟁, 실적 발표 등)
    * **주요 레벨**: (코스피 2500선, 나스닥 15000선 등 지지/저항 라인)
    """
