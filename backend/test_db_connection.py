import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Διαβάζει το .env για να βρει το DATABASE_URL
load_dotenv()

# Fallback ίδιο με τα στοιχεία του δικού μας docker-compose.yml
# (kosovo_user / kosovo_pass / kosovo_analytics), όχι τα generic postgres/postgres
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://kosovo_user:kosovo_pass@localhost:5432/kosovo_analytics"
)


def test_connection():
    print(f"Δοκιμή σύνδεσης σε: {DATABASE_URL}")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version();")).scalar()
            print("✅ Επιτυχής σύνδεση!")
            print(f"PostgreSQL: {version}")
    except Exception as e:
        print("❌ Αποτυχία σύνδεσης:")
        print(e)


if __name__ == "__main__":
    test_connection()