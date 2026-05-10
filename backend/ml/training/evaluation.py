import torch
from sklearn.metrics import accuracy_score, classification_report, f1_score, precision_score, recall_score
from torch.cuda.amp import autocast
from tqdm.auto import tqdm


def evaluate_model(
    model: torch.nn.Module,
    data_loader,
    criterion,
    device: torch.device,
    stage: str = "evaluation",
    use_amp: bool = False,
) -> dict:
    # Переводим модель в evaluation mode: dropout выключается, веса не обновляются.
    model.eval()

    losses = []
    predictions = []
    targets = []

    # torch.no_grad() экономит память, потому что градиенты на оценке не нужны.
    with torch.no_grad():
        for batch in tqdm(data_loader, desc=stage):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            # AMP можно использовать и на evaluation, если inference идёт на CUDA.
            with autocast(enabled=use_amp):
                logits = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                )
                loss = criterion(logits, labels)

            batch_predictions = torch.argmax(logits, dim=1)

            losses.append(loss.item())
            predictions.extend(batch_predictions.cpu().tolist())
            targets.extend(labels.cpu().tolist())

    return calculate_metrics(
        losses=losses,
        targets=targets,
        predictions=predictions,
    )


def calculate_metrics(
    losses: list[float],
    targets: list[int],
    predictions: list[int],
) -> dict:
    # Собираем основные метрики классификации в одном формате для train.py.
    return {
        "loss": sum(losses) / len(losses),
        "accuracy": accuracy_score(targets, predictions),
        "precision": precision_score(targets, predictions, average="weighted", zero_division=0),
        "recall": recall_score(targets, predictions, average="weighted", zero_division=0),
        "f1": f1_score(targets, predictions, average="weighted"),
        "targets": targets,
        "predictions": predictions,
    }


def build_classification_report(
    targets: list[int],
    predictions: list[int],
    category_names: list[str],
) -> str:
    # Classification report удобен для финального вывода по каждому классу отдельно.
    return classification_report(
        targets,
        predictions,
        target_names=category_names,
        zero_division=0,
    )
