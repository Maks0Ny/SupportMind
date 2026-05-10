# API Documentation

Base URL:

```text
http://localhost:8000/api/v1
```

Swagger UI:

```text
http://localhost:8000/docs
```

---

## Response Headers

Every response includes:

```text
X-Request-ID
```

If a client sends this header, the backend preserves it. Otherwise, the backend generates a new request ID.

---

## Endpoints

```http
GET    /health
POST   /tickets/analyze
GET    /tickets
GET    /tickets/{ticket_id}
PUT    /tickets/{ticket_id}/prediction
DELETE /tickets/{ticket_id}
GET    /dashboard/summary
```

---

## Health

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

---

## Analyze Ticket

```http
POST /tickets/analyze
```

Request:

```json
{
  "text": "I cannot login to my account after password reset"
}
```

Validation:

- `text` is required;
- minimum length is 5 characters;
- maximum length is 2000 characters.

Response:

```json
{
  "ticket_id": 1,
  "category": "it_support",
  "priority": "medium",
  "sentiment": "negative",
  "confidence": 0.91
}
```

Prediction behavior:

- `category` comes from the trained model when artifacts are available;
- fallback category prediction is rule-based;
- `priority` and `sentiment` are currently rule-based;
- the API response contract does not change between trained and fallback modes.

---

## List Tickets

```http
GET /tickets
```

Response:

```json
[
  {
    "id": 3,
    "text": "The dashboard does not load",
    "created_at": "2026-05-11T12:30:00"
  }
]
```

---

## Filter Tickets

```http
GET /tickets?category=technical_support&priority=high&sentiment=negative
```

Query parameters:

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `category` | string | no | Prediction category |
| `priority` | string | no | Prediction priority |
| `sentiment` | string | no | Prediction sentiment |

---

## Ticket Details

```http
GET /tickets/{ticket_id}
```

Response:

```json
{
  "id": 1,
  "text": "The dashboard does not load",
  "created_at": "2026-05-11T12:30:00",
  "prediction": {
    "category": "technical_support",
    "priority": "high",
    "sentiment": "negative",
    "confidence": 0.88,
    "created_at": "2026-05-11T12:30:00"
  }
}
```

Not found:

```json
{
  "detail": "Ticket not found"
}
```

---

## Update Prediction

```http
PUT /tickets/{ticket_id}/prediction
```

Example:

```http
PUT /tickets/1/prediction?category=technical_support&priority=medium&sentiment=neutral&confidence=0.77
```

Response:

```json
{
  "ticket_id": 1,
  "category": "technical_support",
  "priority": "medium",
  "sentiment": "neutral",
  "confidence": 0.77
}
```

Updating a prediction clears the dashboard cache.

---

## Delete Ticket

```http
DELETE /tickets/{ticket_id}
```

Response:

```json
{
  "message": "Ticket deleted successfully"
}
```

Deleting a ticket also deletes its prediction and clears the dashboard cache.

---

## Dashboard Summary

```http
GET /dashboard/summary
```

Response:

```json
{
  "total_tickets": 10,
  "high_priority_count": 3,
  "negative_sentiment_count": 4,
  "by_category": {
    "technical_support": 4,
    "billing_and_payments": 2
  },
  "by_priority": {
    "high": 3,
    "medium": 5,
    "low": 2
  },
  "by_sentiment": {
    "negative": 4,
    "neutral": 4,
    "positive": 2
  }
}
```

The summary is cached in Redis under `dashboard:summary`.
