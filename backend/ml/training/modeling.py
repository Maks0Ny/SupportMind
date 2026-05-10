import torch
import torch.nn as nn
from transformers import AutoModel


class E5Classifier(nn.Module):
    # Класс модели отвечает только за архитектуру: encoder + dropout + classifier.
    def __init__(self, model_name: str, num_labels: int, dropout: float = 0.3):
        super().__init__()

        # Encoder превращает входной текст в векторные представления токенов.
        self.encoder = AutoModel.from_pretrained(model_name)

        # Dropout помогает снизить переобучение во время training.
        self.dropout = nn.Dropout(dropout)

        # Linear-слой превращает вектор текста в logits по количеству классов.
        self.classifier = nn.Linear(
            self.encoder.config.hidden_size,
            num_labels,
        )

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
    ) -> torch.Tensor:
        # Передаём токены в transformer-модель.
        outputs = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask,
        )

        # Берём представление первого токена как общий вектор всего текста.
        pooled_output = outputs.last_hidden_state[:, 0]
        pooled_output = self.dropout(pooled_output)

        # Возвращаем сырые предсказания модели. Softmax отдельно делать не нужно,
        # потому что CrossEntropyLoss ожидает именно logits.
        return self.classifier(pooled_output)
