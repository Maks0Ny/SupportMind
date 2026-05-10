from fastapi.testclient import TestClient


def analyze_ticket(
    client: TestClient, text: str = "The app crashes during payment"
) -> dict:
    response = client.post("/api/v1/tickets/analyze", json={"text": text})

    assert response.status_code == 200
    return response.json()


def test_analyze_ticket_creates_prediction(client: TestClient) -> None:
    data = analyze_ticket(client)

    assert data["ticket_id"] == 1
    assert data["category"] == "payment_bug"
    assert data["priority"] == "high"
    assert data["sentiment"] == "negative"
    assert data["confidence"] >= 0.8


def test_analyze_ticket_validates_text_length(client: TestClient) -> None:
    response = client.post("/api/v1/tickets/analyze", json={"text": "bad"})

    assert response.status_code == 422


def test_ticket_lifecycle(client: TestClient) -> None:
    created = analyze_ticket(client, "Login button does not work after update")
    ticket_id = created["ticket_id"]

    list_response = client.get("/api/v1/tickets")
    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == ticket_id

    detail_response = client.get(f"/api/v1/tickets/{ticket_id}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["text"] == "Login button does not work after update"
    assert detail["prediction"]["category"] == "login_issue"
    assert detail["prediction"]["priority"] == "medium"

    update_response = client.put(
        f"/api/v1/tickets/{ticket_id}/prediction",
        params={
            "category": "login_issue",
            "priority": "medium",
            "sentiment": "neutral",
            "confidence": 0.75,
        },
    )
    assert update_response.status_code == 200
    assert update_response.json() == {
        "ticket_id": ticket_id,
        "category": "login_issue",
        "priority": "medium",
        "sentiment": "neutral",
        "confidence": 0.75,
    }

    filtered_response = client.get("/api/v1/tickets", params={"priority": "medium"})
    assert filtered_response.status_code == 200
    assert len(filtered_response.json()) == 1

    delete_response = client.delete(f"/api/v1/tickets/{ticket_id}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": "Ticket deleted successfully"}

    missing_response = client.get(f"/api/v1/tickets/{ticket_id}")
    assert missing_response.status_code == 404
