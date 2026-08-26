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

# Production frontend origin (π.χ. Railway domain) για CORS -- None σε
# τοπικό dev, δεν επηρεάζει το ήδη υπάρχον allow_origin_regex (localhost).
FRONTEND_URL = os.getenv("FRONTEND_URL")

# Στοιχεία του αρχικού ADMIN χρήστη που δημιουργεί το seed script (idempotent
# -- μόνο αν δεν υπάρχει ήδη κανένας ADMIN, βλ. app/scripts/seed.py). None
# εδώ σημαίνει "δεν έχουν οριστεί" -- το seed script κάνει fallback σε
# dev-only default credentials με ρητό warning, δεν σκάει.
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
