import json
from pathlib import Path

import pytest
import torch

import app.ml.trained_predictor as trained_predictor_module
from app.ml.trained_predictor import TrainedCategoryPredictor


def test_trained_predictor_raises_when_artifacts_are_missing(tmp_path: Path) -> None:
    missing_model = tmp_path / "missing_model.pt"
    missing_mapping = tmp_path / "missing_mapping.json"

    with pytest.raises(FileNotFoundError):
        TrainedCategoryPredictor(
            model_path=missing_model,
            mapping_path=missing_mapping,
            device="cpu",
        )


def test_trained_predictor_uses_cpu_device() -> None:
    predictor = object.__new__(TrainedCategoryPredictor)

    assert predictor._resolve_device("cpu") == torch.device("cpu")


def test_trained_predictor_predicts_category(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model_path = tmp_path / "category_model.pt"
    mapping_path = tmp_path / "label_mapping.json"
    model_path.write_bytes(b"fake model")
    mapping_path.write_text(
        json.dumps(
            {
                "id_to_category": {
                    "0": "billing_and_payments",
                    "1": "technical_support",
                },
                "model_name": "fake-model",
                "max_length": 8,
            }
        ),
        encoding="utf-8",
    )

    class FakeTokenizer:
        def __call__(self, *args, **kwargs):
            return {
                "input_ids": torch.tensor([[1, 2, 3]]),
                "attention_mask": torch.tensor([[1, 1, 1]]),
            }

    class FakeModel:
        def load_state_dict(self, state_dict):
            return None

        def to(self, device):
            return self

        def eval(self):
            return None

        def __call__(self, input_ids, attention_mask):
            return torch.tensor([[0.1, 0.9]])

    monkeypatch.setattr(
        trained_predictor_module.AutoTokenizer,
        "from_pretrained",
        lambda model_name: FakeTokenizer(),
    )
    monkeypatch.setattr(
        trained_predictor_module,
        "E5Classifier",
        lambda model_name, num_labels: FakeModel(),
    )
    monkeypatch.setattr(
        trained_predictor_module.torch,
        "load",
        lambda *args, **kwargs: {},
    )

    predictor = TrainedCategoryPredictor(
        model_path=model_path,
        mapping_path=mapping_path,
        device="cpu",
    )

    category, confidence = predictor.predict_category("The dashboard is broken")

    assert category == "technical_support"
    assert confidence > 0.5
