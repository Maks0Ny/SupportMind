import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

import torch
from transformers import AutoTokenizer


TRAINING_DIR = Path(__file__).resolve().parent
ML_DIR = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = ML_DIR / "artifacts"

# Добавляем пути, чтобы файл можно было запускать напрямую из VS Code terminal.
sys.path.append(str(TRAINING_DIR))
sys.path.append(str(ML_DIR))

from configs.config import settings_ml
from modeling import E5Classifier


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


class CategoryInference:
    # Класс инкапсулирует всё, что нужно для inference: tokenizer, model и mapping классов.
    def __init__(
        self,
        model_path: Path | None = None,
        mapping_path: Path | None = None,
        device: str | None = None,
    ) -> None:
        self.model_path = model_path or ARTIFACTS_DIR / "category_model.pt"
        self.mapping_path = mapping_path or ARTIFACTS_DIR / "label_mapping.json"
        self.device = self._resolve_device(device or settings_ml.DEVICE)

        self._validate_artifacts()
        self.mapping = self._load_mapping()
        self.id_to_category = {
            int(index): category
            for index, category in self.mapping["id_to_category"].items()
        }
        self.model_name = self.mapping["model_name"]
        self.max_length = int(self.mapping["max_length"])

        logger.info("Loading tokenizer: %s", self.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

        logger.info("Loading model weights: %s", self.model_path)
        self.model = E5Classifier(
            model_name=self.model_name,
            num_labels=len(self.id_to_category),
        )
        self.model.load_state_dict(
            torch.load(self.model_path, map_location=self.device)
        )
        self.model.to(self.device)
        self.model.eval()

        logger.info("Inference model is ready on device: %s", self.device)

    def _resolve_device(self, requested_device: str) -> torch.device:

        if requested_device == "cuda" and torch.cuda.is_available():
            return torch.device("cuda")

        if requested_device == "cuda":
            logger.warning("CUDA requested, but it is not available. Inference will use CPU.")

        return torch.device("cpu")

    def _load_mapping(self) -> dict[str, Any]:
        # Mapping нужен, чтобы перевести числовой id модели обратно в текстовую category.
        if not self.mapping_path.exists():
            raise FileNotFoundError(f"Label mapping file not found: {self.mapping_path}")

        with open(self.mapping_path, encoding="utf-8") as file:
            return json.load(file)

    def _validate_artifacts(self) -> None:
        # Без весов модели inference невозможен, поэтому проверяем файл перед prediction.
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model weights file not found: {self.model_path}")

    def predict(self, text: str) -> dict[str, Any]:
        # Один публичный метод для предсказания категории по тексту обращения.
        self._validate_artifacts()

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
        category = self.id_to_category[category_id]

        return {
            "category": category,
            "category_id": category_id,
            "confidence": float(confidence.item()),
        }

    def predict_batch(self, texts: list[str]) -> list[dict[str, Any]]:
        # Batch-метод удобен для проверки нескольких обращений подряд.
        return [self.predict(text) for text in texts]


def main() -> None:
    # CLI нужен для быстрой проверки модели без подключения FastAPI.
    parser = argparse.ArgumentParser(description="Run SupportMind category inference.")
    parser.add_argument("text", help="Support ticket text")
    parser.add_argument(
        "--device",
        choices=["cuda", "cpu"],
        default=settings_ml.DEVICE,
        help="Device for inference",
    )
    args = parser.parse_args()

    predictor = CategoryInference(device=args.device)
    result = predictor.predict(args.text)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
