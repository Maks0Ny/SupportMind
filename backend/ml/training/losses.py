from collections.abc import Sequence

import torch
import torch.nn as nn


def build_cross_entropy_loss() -> nn.CrossEntropyLoss:
    # Обычный CrossEntropyLoss подходит, когда классы в датасете распределены примерно ровно.
    return nn.CrossEntropyLoss()


def build_weighted_cross_entropy_loss(
    labels: Sequence[int],
    device: torch.device,
) -> nn.CrossEntropyLoss:
    # Weighted loss помогает, если одних категорий в датасете сильно больше, чем других.
    label_tensor = torch.tensor(labels, dtype=torch.long)
    class_counts = torch.bincount(label_tensor)

    # Защита от деления на ноль, если какой-то класс отсутствует в train split.
    class_counts = torch.clamp(class_counts, min=1)

    # Чем реже класс встречается, тем больший вес он получает в loss-функции.
    class_weights = 1.0 / class_counts.float()
    class_weights = class_weights / class_weights.sum() * len(class_counts)

    return nn.CrossEntropyLoss(weight=class_weights.to(device))


def choose_loss(
    labels: Sequence[int],
    device: torch.device,
    use_class_weights: bool = False,
) -> nn.CrossEntropyLoss:
    # Единая функция выбора loss, чтобы train.py не знал деталей расчёта весов.
    if use_class_weights:
        return build_weighted_cross_entropy_loss(labels=labels, device=device)

    return build_cross_entropy_loss()
