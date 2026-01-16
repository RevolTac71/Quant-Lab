from datetime import datetime

# Individual Report Summary Prompts


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


TRANSLATION_PROMPT_KO = """
Role: Expert Financial Translator.
Task: Translate the following English financial report content into Korean.
[Input Text]:
{text}

[Constraints]:
1. **Format/Markdown**: You MUST preserve the exact markdown structure (headers, bullets, tables). Do NOT change the layout.
2. **Tickers**: Keep all Tickers (e.g., $NVDA) in English.
3. **Tone**: Use a professional, financial tone suitable for a hedge fund CIO (Korean).
4. **Term Mappings**:
   - "Report Analysis" -> "[리포트 제목/주제] 분석"
   - "Institution" -> "작성 기관"
   - "One-Liner" -> "한줄 평"
   - "Sentiment" -> "Sentiment" (Keep or Transliterate)
   - "Key Investment Calls" -> "핵심 투자 아이디어"
   - "Long/Overweight" -> "Long (매수/비중확대)"
   - "Short/Underweight" -> "Short (매도/리크스)"
   - "Key Numbers" -> "핵심 데이터"
   - "Key Driver" -> "핵심 동인"
   - "Contrarian/Hidden Gem" -> "틈새/역발상 아이디어"
   - "Consensus Trades" -> "컨센서스 트레이드"
   - "Sector Rotation" -> "섹터 로테이션"
   - "Risk Radar" -> "리스크 레이더"
   - "Top Picks" -> "오늘의 Top Picks"
5. **No Explanations**: Output ONLY the translated report. No preamble.
"""
