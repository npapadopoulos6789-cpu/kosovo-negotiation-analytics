"""
Λεπτό wrapper πάνω στο Anthropic SDK. Μοναδική δουλειά: στείλε
system+user prompt, πάρε πίσω έγκυρο JSON. Καμία γνώση για negotiation
events/analytics εδώ -- αυτό μένει στο negotiation_analysis.py.
"""
import json

import anthropic

from app.core.config import ANTHROPIC_API_KEY

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 8192


class LLMCallError(Exception):
    """
    Καλύπτει ΚΑΘΕ αποτυχία γύρω από την κλήση στο LLM -- network/auth/
    rate limit από το SDK, ή μη-έγκυρο JSON στην απάντηση. Ο caller
    (negotiation_analysis.create_analysis) ΔΕΝ πρέπει να αποθηκεύσει
    τίποτα στη ΒΔ όταν σηκωθεί αυτό το exception.
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def _strip_code_fence(text: str) -> str:
    # Το Claude κάποιες φορές τυλίγει το JSON σε ```json ... ``` παρόλο
    # που το system prompt το απαγορεύει ρητά -- αφαιρούμε το fence αν
    # υπάρχει, χωρίς να αλλάξουμε τίποτα άλλο στο περιεχόμενο.
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.split("\n", 1)[1] if "\n" in stripped else stripped
        if stripped.endswith("```"):
            stripped = stripped.rsplit("```", 1)[0]
    return stripped.strip()


def call_llm(system_prompt: str, user_message: str, max_tokens: int = MAX_TOKENS) -> dict:
    """
    Επιστρέφει {"raw_text": <το ακριβές JSON string, όπως θα αποθηκευτεί
    στο llm_answer>, "model": <το model που όντως απάντησε>}.
    Σηκώνει LLMCallError αν κάτι πάει στραβά -- ΔΕΝ γυρνάει ποτέ μερικό
    ή άκυρο αποτέλεσμα.

    max_tokens: default MAX_TOKENS=8192 (το γενικό, συντηρητικό όριο, ίδιο
    με πριν). Ο caller (negotiation_analysis.py) περνάει χαμηλότερη τιμή
    ΜΟΝΟ όπου υπάρχει πραγματικό logged evidence ότι το flow χρειάζεται
    λιγότερα -- βλ. σχόλιο εκεί. Καμία γνώση για ΠΟΙΟ flow καλεί εδώ, το
    llm_client παραμένει thin/domain-agnostic.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            temperature=0,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
    except anthropic.APIError as e:
        raise LLMCallError(f"Anthropic API error: {e}") from e

    raw_text = _strip_code_fence(response.content[0].text)

    try:
        json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise LLMCallError(f"Το LLM δεν επέστρεψε έγκυρο JSON: {e}") from e

    # Καθαρό print, ΟΧΙ αποθήκευση -- ώστε να βλέπουμε στο terminal αν
    # το MAX_TOKENS=8192 είναι άνετο ή οριακό, χωρίς migration/νέο πεδίο.
    print(
        f"[llm_client] tokens -- input: {response.usage.input_tokens}, "
        f"output: {response.usage.output_tokens} (max_tokens={max_tokens})"
    )

    return {
        "raw_text": raw_text,
        "model": response.model,
        "output_tokens": response.usage.output_tokens,
    }
