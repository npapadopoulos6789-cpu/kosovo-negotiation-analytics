# Ίδιο version με το venv που ήδη χρησιμοποιείται τοπικά (python --version)
FROM python:3.14-slim

WORKDIR /app

# Ξεχωριστό COPY μόνο του requirements.txt πριν το υπόλοιπο source code --
# το Docker layer cache μένει έγκυρο όσο δεν αλλάζουν τα dependencies,
# άρα δεν ξανατρέχει pip install σε κάθε build μόνο επειδή άλλαξε ένα .py
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# alembic upgrade head (idempotent -- no-op αν είμαστε ήδη στο head) +
# conditional seed (βλ. app/scripts/seed.py, skip αν η ΒΔ έχει ήδη
# δεδομένα) πριν το uvicorn, ΚΑΘΕ φορά που ξεκινάει το container.
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
