from datetime import datetime
from supabase import create_client
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

class DBService:
    def __init__(self):
        try:
            self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise

    def get_subscribers(self, lang_code=None):
        """Fetch active subscribers, optionally filtered by language."""
        try:
            query = self.client.table("subscribers").select("email").eq("is_active", True)
            if lang_code:
                query = query.eq("language", lang_code)
            response = query.execute()
            return [row['email'] for row in response.data]
        except Exception as e:
            logger.error(f"Failed to fetch subscribers: {e}")
            return []

    def save_individual_report(self, report_data):
        """Save a single individual report summary."""
        try:
            self.client.table("individual_reports").insert(report_data).execute()
            logger.info(f"Saved individual report: {report_data.get('title')}")
        except Exception as e:
            logger.error(f"Failed to save individual report: {e}")

    def save_daily_report(self, report_data):
        """Save the synthesized daily report."""
        try:
            self.client.table("daily_reports").insert(report_data).execute()
            logger.info(f"Saved daily report: {report_data.get('title')}")
        except Exception as e:
            logger.error(f"Failed to save daily report: {e}")

    def log_subscription_action(self, email, action_type):
        """Log subscription actions (subscribe/unsubscribe)."""
        try:
            self.client.table("subscription_logs").insert({
                "email": email,
                "action_type": action_type
            }).execute()
        except Exception as e:
            logger.error(f"Failed to log action for {email}: {e}")

    def subscribe_user(self, email, language='ko'):
        """Subscribe a new user."""
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            data = {
                "email": email, 
                "is_active": True, 
                "language": language,
                "start_date": current_date, 
            }
            self.client.table("subscribers").upsert(data, on_conflict='email').execute()
            self.log_subscription_action(email, 'SUBSCRIBE')
            return "success"
        except Exception as e:
            logger.error(f"Subscribe failed for {email}: {e}")
            return str(e)

    def unsubscribe_user(self, email):
        """Unsubscribe a user."""
        try:
            check = self.client.table("subscribers").select("*").eq("email", email).execute()
            if not check.data:
                return "not_found"

            current_date = datetime.now().strftime("%Y-%m-%d")
            self.client.table("subscribers").update({
                "is_active": False,
                "end_date": current_date
            }).eq("email", email).execute()
            
            self.log_subscription_action(email, 'UNSUBSCRIBE')
            return "success"
        except Exception as e:
            logger.error(f"Unsubscribe failed for {email}: {e}")
            return str(e)
            
    def get_latest_daily_report(self):
        """Get the latest daily report."""
        try:
            response = self.client.table("daily_reports").select("*").order("created_at", desc=True).limit(1).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to fetch latest report: {e}")
            return None
