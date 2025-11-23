# ai.py
BADWORDS_FILE = "frontend/badwords.txt"  # you had this file previously; adjust path if removed

# simple bad words loader
def load_badwords():
    try:
        with open(BADWORDS_FILE, "r", encoding="utf-8") as f:
            return {w.strip().lower() for w in f if w.strip()}
    except Exception:
        # minimal fallback list
        return {"die", "idiot", "stupid", "f***"}  # you can expand

BADWORDS = load_badwords()

def moderate_text(text: str) -> bool:
    """Return True if text is allowed, False if toxic."""
    if not text:
        return True
    t = text.lower()
    for w in BADWORDS:
        if w in t:
            return False
    return True

def check_toxicity(text: str) -> bool:
    """Alias for moderate_text to match older names."""
    return moderate_text(text)

def analyze_sentiment(text: str) -> dict:
    """Very simple sentiment stub: positive if happy words, negative if sad words."""
    text = (text or "").lower()
    pos = any(x in text for x in ("good", "great", "happy", "love"))
    neg = any(x in text for x in ("bad", "sad", "hate", "angry"))
    if pos and not neg:
        sentiment = "positive"
    elif neg and not pos:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    return {"sentiment": sentiment}
