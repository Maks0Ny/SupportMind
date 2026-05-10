from app.ml.category_predictor import SupportTicketPredictor


def test_predictor_detects_payment_bug() -> None:
    predictor = SupportTicketPredictor()

    result = predictor.predict("After the update the app crashes during payment")

    assert result.category == "payment_bug"
    assert result.priority == "high"
    assert result.sentiment == "negative"
    assert result.confidence >= 0.8


def test_predictor_detects_login_issue() -> None:
    predictor = SupportTicketPredictor()

    result = predictor.predict("I cannot login because the password reset page is broken")

    assert result.category == "login_issue"
    assert result.priority == "medium"
    assert result.sentiment == "negative"


def test_predictor_falls_back_to_general_support() -> None:
    predictor = SupportTicketPredictor()

    result = predictor.predict("I have a question about available product options")

    assert result.category == "general_support"
    assert result.priority == "low"
    assert result.sentiment == "neutral"
