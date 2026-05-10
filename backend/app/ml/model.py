from dataclasses import dataclass


@dataclass(frozen=True)
class PredictionResult:
    category: str
    priority: str
    sentiment: str
    confidence: float
