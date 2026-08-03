"""
Smoke test: επιβεβαιώνει ότι το ANTHROPIC_API_KEY + η σύνδεση στο Claude
API δουλεύουν. Τίποτα άλλο -- ΔΕΝ αγγίζει το NegotiationAnalysis service.
Τρέχεται με: python -m app.scripts.test_llm
"""
import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-4-6"


def run_smoke_test():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    client = Anthropic(api_key=api_key)

    response = client.messages.create(
        model=MODEL,
        max_tokens=10,
        temperature=0,
        messages=[{"role": "user", "content": "Reply with exactly: OK"}],
    )

    print("model:", response.model)
    print("reply:", response.content[0].text)


if __name__ == "__main__":
    run_smoke_test()
