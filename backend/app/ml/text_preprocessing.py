import re


def normalize_ticket_text(text: str) -> str:
    normalized = text.lower().strip()
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized
