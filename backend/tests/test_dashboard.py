from fastapi.testclient import TestClient


def create_ticket(client: TestClient, text: str) -> int:
    response = client.post("/api/v1/tickets/analyze", json={"text": text})

    assert response.status_code == 200
    return int(response.json()["ticket_id"])


def test_dashboard_summary_counts_tickets_and_predictions(client: TestClient) -> None:
    create_ticket(client, "Payment fails when I submit the checkout form")
    second_ticket_id = create_ticket(client, "Login page opens with a blank screen")

    update_response = client.put(
        f"/api/v1/tickets/{second_ticket_id}/prediction",
        params={
            "category": "login_issue",
            "priority": "low",
            "sentiment": "neutral",
            "confidence": 0.6,
        },
    )
    assert update_response.status_code == 200

    response = client.get("/api/v1/dashboard/summary")

    assert response.status_code == 200
    assert response.json() == {
        "total_tickets": 2,
        "high_priority_count": 1,
        "negative_sentiment_count": 1,
        "by_category": {
            "payment_bug": 1,
            "login_issue": 1,
        },
        "by_priority": {
            "high": 1,
            "low": 1,
        },
        "by_sentiment": {
            "negative": 1,
            "neutral": 1,
        },
    }
