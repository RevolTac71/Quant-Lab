import asyncio
import time
from datetime import datetime, timezone, timedelta
from config import settings, prompts
from services.search_service import SearchService
from services.crawler_service import CrawlerService
from services.llm_service import LLMService
from services.db_service import DBService
from services.email_service import EmailService
from utils.logger import setup_logger

logger = setup_logger(__name__)

# KST Timezone
KST = timezone(timedelta(hours=9))


async def process_report(report, crawler_service, llm_service, db_service):
    """Downloads, extracts, summarizes, and saves a single report."""
    title = report["title"]
    link = report["link"]

    logger.info(f"Processing: {title}...")

    # 1. Extract Text
    text = await crawler_service.extract_text_from_url(link)
    if not text:
        logger.warning(f"Skipping {title}: No text extracted.")
        return None

    try:
        # 2. Summarize (Korean & English) - Run in parallel
        prompt_ko = prompts.SUMMARY_PROMPT_KO.format(text=text)
        prompt_en = prompts.SUMMARY_PROMPT_EN.format(text=text)

        summary_ko_task = llm_service.generate_content_async(prompt_ko)
        summary_en_task = llm_service.generate_content_async(prompt_en)

        summary_ko, summary_en = await asyncio.gather(summary_ko_task, summary_en_task)

        # check for errors
        if not summary_ko or not summary_en:
            logger.error(f"❌ Summary generation failed for {title}")
            return None

        # 3. Save to DB
        report_data = {
            "title": title,
            "link": link,
            "summary_ko": summary_ko,
            "summary_en": summary_en,
        }
        db_service.save_individual_report(report_data)

        return report_data

    except Exception as e:
        logger.error(f"Error processing {title}: {e}")
        return None


async def main():
    logger.info("🚀 QuantLab Daily Job Started (Async)...")
    start_time = time.time()

    # Initialize Services
    search_service = SearchService()
    crawler_service = CrawlerService()
    llm_service = LLMService()
    db_service = DBService()
    email_service = EmailService()

    # 1. Search Reports
    searched_reports = search_service.search_pdf_reports(
        settings.SEARCH_KEYWORD, settings.TARGET_SITES
    )

    if not searched_reports:
        logger.info("No reports found.")
        return

    # 2. Process Reports (Sequential)
    # Process reports one by one to avoid passing API rate limits (Free Tier)
    results = []
    failed_reports = []

    for report in searched_reports:
        res = await process_report(report, crawler_service, llm_service, db_service)
        if res is None:
            failed_reports.append(report)
        else:
            results.append(res)
        # Optional: slight delay between reports to be extra safe
        # await asyncio.sleep(1)

    # Send consolidated admin alert if there are failures
    if failed_reports:
        logger.warning(f"⚠️ {len(failed_reports)} reports failed to process.")
        error_body = "The following reports failed to process (skipped):\n\n"
        for fail in failed_reports:
            error_body += f"❌ {fail['title']}\n🔗 {fail['link']}\n\n"

        email_service.send_admin_alert(
            f"[QuantLab Warning] {len(failed_reports)} Reports Failed to Process",
            error_body,
        )

    # Filter successful results
    processed_summaries = [res for res in results if res is not None]

    if not processed_summaries:
        logger.info("💤 No reports processed successfully.")
        return

    # 3. Synthesis & Email
    logger.info(f"🤖 Synthesizing {len(processed_summaries)} reports...")

    all_text_en = "\n\n".join(
        [
            f"Title: {s['title']}\nSummary: {s['summary_en']}"
            for s in processed_summaries
        ]
    )

    today_kst_str = datetime.now(KST).strftime("%Y-%m-%d")
    today_kst_md = datetime.now(KST).strftime("%m/%d")

    # Generate Synthesis (Parallel)
    prompt_syn_ko = prompts.get_synthesis_prompt_ko(all_text_en, today_kst_str)
    prompt_syn_en = prompts.get_synthesis_prompt_en(all_text_en, today_kst_str)

    final_ko_task = llm_service.generate_content_async(prompt_syn_ko)
    final_en_task = llm_service.generate_content_async(prompt_syn_en)

    final_ko, final_en = await asyncio.gather(final_ko_task, final_en_task)

    # Check for synthesis errors
    if not final_ko and not final_en:
        logger.error("❌ Synthesis generation failed (BOTH).")
        email_service.send_admin_alert(
            f"[QuantLab Error] Synthesis Failed ({today_kst_str})",
            "Both KO and EN synthesis failed.",
        )
        return

    # If partial failure, log it
    if not final_ko:
        logger.warning("⚠️ Synthesis generation failed for KO.")
    if not final_en:
        logger.warning("⚠️ Synthesis generation failed for EN.")

    # Save Daily Report
    daily_report_data = {
        "title": f"Global Market Synthesis ({today_kst_str})",
        "summary_ko": final_ko if final_ko else "",
        "summary_en": final_en if final_en else "",
    }
    db_service.save_daily_report(daily_report_data)

    # 4. Send Emails
    def build_mail_body(synthesis, summaries, lang="ko"):
        body = f"{synthesis}\n\n"
        body += "=" * 40 + "\n\n"

        if lang == "ko":
            body += "📚 [참고한 개별 리포트 원문 요약]\n\n"
            key = "summary_ko"
        else:
            body += "📚 [Individual Report Summaries]\n\n"
            key = "summary_en"

        for item in summaries:
            body += f"📌 {item['title']}\n"
            body += f"🔗 {item['link']}\n"
            body += f"{item[key]}\n"
            body += "-" * 20 + "\n"

        return body

    # Fetch subscribers
    korean_users = db_service.get_subscribers("ko")
    english_users = db_service.get_subscribers("en")

    if korean_users and final_ko:
        body_ko = build_mail_body(final_ko, processed_summaries, "ko")
        email_service.send_email_batch(
            f"[QuantLab] 오늘의 글로벌 마켓 브리핑 ({today_kst_md})",
            body_ko,
            korean_users,
        )

    if english_users and final_en:
        body_en = build_mail_body(final_en, processed_summaries, "en")
        email_service.send_email_batch(
            f"[QuantLab] Daily Market Brief ({today_kst_md})", body_en, english_users
        )

    elapsed_time = time.time() - start_time
    logger.info(f"✅ Daily Job Completed in {elapsed_time:.2f} seconds.")


if __name__ == "__main__":
    asyncio.run(main())
