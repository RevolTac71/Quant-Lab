import os
import toml
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent
SECRETS_PATH = BASE_DIR / ".streamlit" / "secrets.toml"

# Load secrets
secrets = {}
if SECRETS_PATH.exists():
    secrets = toml.load(SECRETS_PATH)

def get_secret(key, default=None, nested_key=None):
    """Retrieve secret from toml or environment variables."""
    # Try getting from secrets.toml
    value = secrets
    if nested_key:
        for k in nested_key:
            value = value.get(k, {})
        value = value.get(key)
    else:
        value = value.get(key)
    
    # If not found, try environment variable
    if value is None:
        value = os.environ.get(key, default)
    
    return value

# Supabase
SUPABASE_URL = get_secret("SUPABASE_URL", nested_key=["supabase"])
SUPABASE_KEY = get_secret("SUPABASE_KEY", nested_key=["supabase"])

# Google / Gemini
GEMINI_API_KEY = get_secret("GEMINI_API_KEY", nested_key=["google"])
GOOGLE_SEARCH_API_KEY = get_secret("GOOGLE_SEARCH_API_KEY", nested_key=["google"])
SEARCH_ENGINE_ID = get_secret("SEARCH_ENGINE_ID", nested_key=["google"])

# Email
GMAIL_USER = get_secret("GMAIL_USER", nested_key=["GMAIL"])
GMAIL_APP_PWD = get_secret("GMAIL_APP_PWD", nested_key=["GMAIL"])

# Search Configuration
TARGET_SITES = [
    "blackrock.com", "macquarie.com", "kkr.com", "brookfield.com",
    "goldmansachs.com", "jpmorgan.com", "morganstanley.com", "ubs.com",
    "mckinsey.com", "pwc.com", "bain.com", "deloitte.com",
    "worldbank.org", "adb.org", "imf.org"
]
SEARCH_KEYWORD = "Infrastructure Outlook"
