import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Credentials ---
GH_ACCOUNT = os.environ.get("GH_ACCOUNT")
GH_APPKEY = os.environ.get("GH_APPKEY")
GH_APPSECRET = os.environ.get("GH_APPSECRET")

if not all([GH_ACCOUNT, GH_APPKEY, GH_APPSECRET]):
    raise ValueError("Missing required environment variables. Please check your .env file.")

# Account parsing
# Assuming GH_ACCOUNT is a 10 digit string like '1234567801'
if len(GH_ACCOUNT) == 10:
    CANO = GH_ACCOUNT[:8]
    ACNT_PRDT_CD = GH_ACCOUNT[8:]
else:
    # Fallback if it's just 8 digits, though usually product code 01 is required
    CANO = GH_ACCOUNT
    ACNT_PRDT_CD = "01"

# --- Constants ---
TARGET_SYMBOL = "005930"  # Samsung Electronics
PRICE_DELTA = 1000        # KRW offset for buy/sell limits

# Trading Window (시간 제한 없음 - 24시간 실행)
START_TIME = "00:00:00"
END_TIME = "23:59:59"

# --- API Endpoints (Mock Trading) ---
BASE_URL = "https://openapivts.koreainvestment.com:29443"

# Common Headers
# Used to determine if it's mock or real, but domain already ensures mock.
# Note: For mock trading, the App Key and Secret are different from the real trading ones.

# Polling configuration
POLLING_INTERVAL = 30  # Seconds to wait between full trading cycles
