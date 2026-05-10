import json
import logging
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer


logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = BACKEND_DIR / "ml" / "artifacts"


class E5Classifier(nn.Module):
    def __init__(self, model_name: str, num_labels: int, dropout: float = 0.3):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(self.encoder.config.hidden_size, num_labels)

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
    ) -> torch.Tensor:
        outputs = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask,
        )
        pooled_output = outputs.last_hidden_state[:, 0]
        pooled_output = self.dropout(pooled_output)
        return self.classifier(pooled_output)


class TrainedCategoryPredictor:
    def __init__(
        self,
        model_path: Path | None = None,
        mapping_path: Path | None = None,
        device: str = "cpu",
    ) -> None:
        self.model_path = model_path or ARTIFACTS_DIR / "category_model.pt"
        self.mapping_path = mapping_path or ARTIFACTS_DIR / "label_mapping.json"
        self.device = self._resolve_device(device)

        self._validate_artifacts()
        self.mapping = self._load_mapping()
        self.id_to_category = {
            int(index): category
            for index, category in self.mapping["id_to_category"].items()
        }
        self.model_name = self.mapping["model_name"]
        self.max_length = int(self.mapping["max_length"])

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = E5Classifier(
            model_name=self.model_name,
            num_labels=len(self.id_to_category),
        )
        self.model.load_state_dict(
            torch.load(self.model_path, map_location=self.device)
        )
        self.model.to(self.device)
        self.model.eval()

        logger.info("Trained category predictor loaded on %s", self.device)

    def _resolve_device(self, requested_device: str) -> torch.device:
        if requested_device == "cuda" and torch.cuda.is_available():
            return torch.device("cuda")

        if requested_device == "cuda":
            logger.warning(
                "CUDA requested for API inference, but it is unavailable. CPU is used."
            )

        return torch.device("cpu")

    def _validate_artifacts(self) -> None:
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        if not self.mapping_path.exists():
            raise FileNotFoundError(f"Mapping file not found: {self.mapping_path}")

    def _load_mapping(self) -> dict[str, Any]:
        with open(self.mapping_path, encoding="utf-8") as file:
            return json.load(file)

    def predict_category(self, text: str) -> tuple[str, float]:
        encoding = self.tokenizer(
            text,
            padding="max_length",
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        )

        input_ids = encoding["input_ids"].to(self.device)
        attention_mask = encoding["attention_mask"].to(self.device)

        with torch.no_grad():
            logits = self.model(input_ids=input_ids, attention_mask=attention_mask)
            probabilities = torch.softmax(logits, dim=1)
            confidence, prediction_id = torch.max(probabilities, dim=1)

        category_id = int(prediction_id.item())
        return self.id_to_category[category_id], float(confidence.item())
