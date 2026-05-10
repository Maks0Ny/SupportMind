import logging

from app.core.config import settings
from app.ml.model import PredictionResult
from app.ml.text_preprocessing import normalize_ticket_text


logger = logging.getLogger(__name__)


class SupportTicketPredictor:
    category_keywords: dict[str, tuple[str, ...]] = {
        "payment_bug": (
            "payment",
            "checkout",
            "card",
            "invoice",
            "billing",
            "refund",
            "charge",
            "оплат",
            "платеж",
            "карт",
            "счет",
            "возврат",
        ),
        "login_issue": (
            "login",
            "sign in",
            "password",
            "auth",
            "account access",
            "2fa",
            "логин",
            "парол",
            "авторизац",
            "войти",
            "аккаунт",
        ),
        "performance_issue": (
            "slow",
            "freeze",
            "lag",
            "timeout",
            "loading",
            "performance",
            "медленно",
            "завис",
            "тормоз",
            "загруз",
        ),
        "delivery_issue": (
            "delivery",
            "shipping",
            "order",
            "courier",
            "package",
            "достав",
            "заказ",
            "курьер",
            "посыл",
        ),
        "account_issue": (
            "profile",
            "subscription",
            "plan",
            "settings",
            "email",
            "профиль",
            "подписк",
            "тариф",
            "настройк",
            "почт",
        ),
        "technical_bug": (
            "crash",
            "bug",
            "error",
            "exception",
            "blank screen",
            "broken",
            "fail",
            "ошиб",
            "баг",
            "вылет",
            "слом",
            "экран",
        ),
    }

    high_priority_keywords: tuple[str, ...] = (
        "urgent",
        "critical",
        "crash",
        "blocked",
        "payment",
        "refund",
        "security",
        "can't work",
        "срочно",
        "критично",
        "вылет",
        "оплат",
        "безопас",
    )
    low_priority_keywords: tuple[str, ...] = (
        "question",
        "how to",
        "feature request",
        "suggestion",
        "minor",
        "вопрос",
        "как",
        "предложение",
        "незнач",
    )
    negative_keywords: tuple[str, ...] = (
        "bad",
        "broken",
        "angry",
        "crash",
        "fail",
        "failed",
        "error",
        "problem",
        "does not work",
        "can't",
        "cannot",
        "ужас",
        "плохо",
        "слом",
        "ошиб",
        "не работает",
        "не могу",
        "вылет",
    )
    positive_keywords: tuple[str, ...] = (
        "thanks",
        "thank you",
        "great",
        "good",
        "works",
        "спасибо",
        "отлично",
        "хорошо",
    )

    def __init__(self) -> None:
        self.trained_predictor = self._load_trained_predictor()

    def predict(self, text: str) -> PredictionResult:
        normalized_text = normalize_ticket_text(text)
        category, category_score, category_confidence = self._predict_category_with_model(
            raw_text=text,
            normalized_text=normalized_text,
        )
        priority, priority_score = self._predict_priority(normalized_text)
        sentiment, sentiment_score = self._predict_sentiment(normalized_text)

        if category_confidence is None:
            confidence = self._calculate_confidence(
                category_score=category_score,
                priority_score=priority_score,
                sentiment_score=sentiment_score,
            )
        else:
            confidence = round(category_confidence, 2)

        return PredictionResult(
            category=category,
            priority=priority,
            sentiment=sentiment,
            confidence=confidence,
        )

    def _load_trained_predictor(self):
        if not settings.ML_USE_TRAINED_MODEL:
            logger.info(
                "Trained ML predictor is disabled. "
                "Rule-based category predictor is used."
            )
            return None

        try:
            from app.ml.trained_predictor import TrainedCategoryPredictor

            return TrainedCategoryPredictor(device=settings.ML_DEVICE)
        except Exception:
            logger.exception(
                "Trained ML predictor is unavailable. Rule-based fallback is used."
            )
            return None

    def _predict_category_with_model(
        self,
        raw_text: str,
        normalized_text: str,
    ) -> tuple[str, int, float | None]:
        if self.trained_predictor is None:
            category, category_score = self._predict_category(normalized_text)
            return category, category_score, None

        category, confidence = self.trained_predictor.predict_category(raw_text)
        return category, 1, confidence

    def _predict_category(self, text: str) -> tuple[str, int]:
        scores = {
            category: self._count_matches(text, keywords)
            for category, keywords in self.category_keywords.items()
        }
        best_category = max(scores, key=lambda category: scores[category])
        best_score = scores[best_category]

        if best_score == 0:
            return "general_support", 0

        return best_category, best_score

    def _predict_priority(self, text: str) -> tuple[str, int]:
        high_score = self._count_matches(text, self.high_priority_keywords)
        low_score = self._count_matches(text, self.low_priority_keywords)

        if high_score > 0:
            return "high", high_score

        if low_score > 0:
            return "low", low_score

        return "medium", 0

    def _predict_sentiment(self, text: str) -> tuple[str, int]:
        negative_score = self._count_matches(text, self.negative_keywords)
        positive_score = self._count_matches(text, self.positive_keywords)

        if negative_score > positive_score:
            return "negative", negative_score

        if positive_score > negative_score:
            return "positive", positive_score

        return "neutral", 0

    def _calculate_confidence(
        self,
        category_score: int,
        priority_score: int,
        sentiment_score: int,
    ) -> float:
        total_score = category_score + priority_score + sentiment_score

        if total_score <= 0:
            return 0.55

        confidence = 0.62 + min(total_score, 6) * 0.055
        return round(min(confidence, 0.95), 2)

    def _count_matches(self, text: str, keywords: tuple[str, ...]) -> int:
        return sum(1 for keyword in keywords if keyword in text)


predictor = SupportTicketPredictor()
