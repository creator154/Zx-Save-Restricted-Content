# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os

# Login System: True = Enable, False = Disable
LOGIN_SYSTEM = os.environ.get(
    "LOGIN_SYSTEM", "True"
).strip().lower() in ("true", "1", "yes")

if not LOGIN_SYSTEM:
    STRING_SESSION = os.environ.get("STRING_SESSION", "")
else:
    STRING_SESSION = None

# Telegram Bot Token
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Telegram API ID
API_ID = int(os.environ.get("API_ID", "0"))

# Telegram API Hash
API_HASH = os.environ.get("API_HASH", "")

# Owner / Admin ID
ADMINS = int(os.environ.get("ADMINS", "6073523936"))

# Channel ID (Optional)
CHANNEL_ID = os.environ.get("CHANNEL_ID", "")

# MongoDB Database
DB_URI = os.environ.get("DB_URI", "")
DB_NAME = os.environ.get("DB_NAME", "vjsavecontentbot")

# Waiting Time
WAITING_TIME = int(os.environ.get("WAITING_TIME", "10"))

# Error Messages
ERROR_MESSAGE = os.environ.get(
    "ERROR_MESSAGE", "True"
).strip().lower() in ("true", "1", "yes")
