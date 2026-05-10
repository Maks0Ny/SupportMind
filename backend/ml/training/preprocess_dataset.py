import re
from pathlib import Path

import pandas as pd


ML_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = ML_DIR / "data" / "raw" / "dataset-tickets-multi-lang-4-20k.csv"
PREPARED_DATA_PATH = ML_DIR / "data" / "processed" / "prepared.csv"

# Названия колонок из сырого CSV.
TEXT_COLUMN = "body"
SUBJECT_COLUMN = "subject"
CATEGORY_COLUMN = "queue"
PRIORITY_COLUMN = "priority"
LANGUAGE_COLUMN = "language"

# Простые словари для базовой разметки sentiment до обучения модели.
NEGATIVE_KEYWORDS = (
    "bad",
    "broken",
    "angry",
    "crash",
    "failed",
    "error",
    "problem",
    "does not work",
    "can't",
    "cannot",
)
POSITIVE_KEYWORDS = (
    "thanks",
    "thank you",
    "great",
    "good",
    "works",
)


def normalize_text(value: object) -> str:
    # Приводим пустые значения к строке, уменьшаем регистр и чистим лишние пробелы.
    text = "" if value is None or (isinstance(value, float) and value != value) else str(value)
    text = text.lower().strip()
    return re.sub(r"\s+", " ", text)


def normalize_label(value: object) -> str:
    # Превращаем текстовые классы в стабильный формат для ML: login issue -> login_issue.
    label = normalize_text(value)
    label = re.sub(r"[^a-z0-9]+", "_", label)
    label = re.sub(r"_+", "_", label).strip("_")
    return label or "unknown"


def normalize_priority(value: object) -> str:
    # Сводим разные варианты priority из датасета к трём понятным классам.
    priority = normalize_label(value)

    if priority in {"1", "low", "minor", "normal"}:
        return "low"

    if priority in {"2", "medium", "moderate"}:
        return "medium"

    if priority in {"3", "4", "5", "high", "critical", "urgent"}:
        return "high"

    return "medium"


def build_ticket_text(row: pd.Series) -> str:
    # Объединяем subject и body, чтобы модель видела больше контекста обращения.
    subject = normalize_text(row[SUBJECT_COLUMN]) if SUBJECT_COLUMN in row else ""
    body = normalize_text(row[TEXT_COLUMN])
    return f"{subject} {body}".strip()


def infer_sentiment(text: str) -> str:
    # Временная эвристика для sentiment, пока нет отдельной обученной модели.
    negative_score = sum(1 for keyword in NEGATIVE_KEYWORDS if keyword in text)
    positive_score = sum(1 for keyword in POSITIVE_KEYWORDS if keyword in text)

    if negative_score > positive_score:
        return "negative"

    if positive_score > negative_score:
        return "positive"

    return "neutral"


def main() -> None:

    df = pd.read_csv(RAW_DATA_PATH)

    # Проверяем, что в сыром файле есть все колонки, без которых подготовка невозможна.
    required_columns = {
        TEXT_COLUMN,
        CATEGORY_COLUMN,
        PRIORITY_COLUMN,
        LANGUAGE_COLUMN,
    }
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Raw dataset is missing required columns: {missing}")

    # Собираем новый чистый датасет в формате, который удобно использовать для обучения.
    df_prepared = pd.DataFrame()
    df_prepared["label"] = df.apply(build_ticket_text, axis=1)
    df_prepared["category"] = df[CATEGORY_COLUMN].apply(normalize_label)
    df_prepared["priority"] = df[PRIORITY_COLUMN].apply(normalize_priority)
    df_prepared["sentiment"] = df_prepared["label"].apply(infer_sentiment)
    df_prepared["language"] = df[LANGUAGE_COLUMN].apply(normalize_label)

    # Убираем слишком короткие тексты, дубликаты и оставляем только нужные ML-колонки.
    df_prepared = df_prepared[df_prepared["label"].str.len() >= 5]
    df_prepared = df_prepared.drop_duplicates(subset=["label"])
    df_prepared = df_prepared[["label", "category", "priority", "sentiment", "language"]]
    df_prepared = df_prepared.reset_index(drop=True)

    # Создаём папку processed и сохраняем подготовленный CSV.
    PREPARED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_prepared.to_csv(PREPARED_DATA_PATH, index=False)

    print(f"Saved prepared dataset: {len(df_prepared)} rows")
    print(f"Output file: {PREPARED_DATA_PATH}")


if __name__ == "__main__":
    main()
