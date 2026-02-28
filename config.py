from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")
APP_SECRET = os.getenv("APP_SECRET", "change-me")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
