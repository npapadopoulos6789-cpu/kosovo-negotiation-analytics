"""
Κεντρικό σημείο φόρτωσης env vars -- ένα load_dotenv() για όλο το app.
database.py/security.py συνεχίζουν να δουλεύουν όπως πριν, απλά
διαβάζουν τις τιμές από εδώ αντί να κάνουν ο καθένας το δικό του
os.getenv().
"""
import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
