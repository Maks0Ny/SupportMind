import json
import logging
import sys
from pathlib import Path
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.cuda.amp import GradScaler, autocast
from transformers import AutoTokenizer, get_linear_schedule_with_warmup
from torch.optim import AdamW
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import warnings
from tqdm.auto import tqdm
import os
import random
from sklearn.metrics import classification_report
warnings.filterwarnings('ignore')

ML_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ML_DIR))

from prepare_dataset import df_train, df_val, df_test
from text_dataset import TextDataset
from modeling import E5Classifier
from configs.config import settings_ml
from visualization import plot_confusion_matrix, plot_final_metrics, plot_training_history

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

tokenizer = AutoTokenizer.from_pretrained(settings_ml.MODEL_NAME)

# category является целевой колонкой, которую модель учится предсказывать.
category_names = sorted(df_train["category"].unique())
category_to_id = {category: index for index, category in enumerate(category_names)}
id_to_category = {index: category for category, index in category_to_id.items()}


for df in (df_train, df_val, df_test):
    df["target"] = df["category"].map(category_to_id)

train_dataset = TextDataset(
    df_train, 
    tokenizer, 
    max_length=settings_ml.MAX_LENGTH)

val_dataset = TextDataset(
    df_val, 
    tokenizer, 
    max_length=settings_ml.MAX_LENGTH)
    
test_dataset = TextDataset(
    df_test, 
    tokenizer, 
    max_length=settings_ml.MAX_LENGTH)


train_loader = DataLoader(train_dataset, batch_size=settings_ml.BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=settings_ml.BATCH_SIZE, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=settings_ml.BATCH_SIZE, shuffle=False)


def set_seed(seed):
    # Фиксируем random seed, чтобы эксперименты были более воспроизводимыми.
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def resolve_device():

    if settings_ml.DEVICE == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")

    if settings_ml.DEVICE == "cuda":
        logger.warning("CUDA requested, but it is not available. Training will use CPU.")

    return torch.device("cpu")


def train_one_epoch(model, data_loader, optimizer, scheduler, criterion, device, epoch, scaler, use_amp):
    # Один полный проход по train dataset.
    model.train()

    losses = []
    predictions = []
    targets = []

    progress_bar = tqdm(data_loader, desc=f"Epoch {epoch} train")

    for batch in progress_bar:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)

        optimizer.zero_grad()

        # AMP ускоряет обучение на CUDA и уменьшает расход видеопамяти.
        with autocast(enabled=use_amp):
            logits = model(input_ids=input_ids, attention_mask=attention_mask)
            loss = criterion(logits, labels)

        scaler.scale(loss).backward()

        # Gradient clipping защищает обучение от слишком больших градиентов.
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), settings_ml.GRADIENT_CLIP_NORM)

        scaler.step(optimizer)
        scaler.update()
        scheduler.step()

        batch_predictions = torch.argmax(logits, dim=1)

        losses.append(loss.item())
        predictions.extend(batch_predictions.detach().cpu().tolist())
        targets.extend(labels.detach().cpu().tolist())

        progress_bar.set_postfix(
            loss=sum(losses) / len(losses),
            f1=f1_score(targets, predictions, average="weighted"),
        )

    return {
        "loss": sum(losses) / len(losses),
        "accuracy": accuracy_score(targets, predictions),
        "f1": f1_score(targets, predictions, average="weighted"),
    }


def evaluate(model, data_loader, criterion, device, stage, use_amp):
    # Оценка модели без обновления весов.
    model.eval()

    losses = []
    predictions = []
    targets = []

    with torch.no_grad():
        for batch in tqdm(data_loader, desc=stage):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            # На evaluation тоже можно использовать AMP, потому что веса не обновляются.
            with autocast(enabled=use_amp):
                logits = model(input_ids=input_ids, attention_mask=attention_mask)
                loss = criterion(logits, labels)

            batch_predictions = torch.argmax(logits, dim=1)

            losses.append(loss.item())
            predictions.extend(batch_predictions.cpu().tolist())
            targets.extend(labels.cpu().tolist())

    return {
        "loss": sum(losses) / len(losses),
        "accuracy": accuracy_score(targets, predictions),
        "precision": precision_score(targets, predictions, average="weighted", zero_division=0),
        "recall": recall_score(targets, predictions, average="weighted", zero_division=0),
        "f1": f1_score(targets, predictions, average="weighted"),
        "targets": targets,
        "predictions": predictions,
    }


def save_artifacts(model, test_metrics):
    # Сохраняем веса модели, соответствие классов и итоговые метрики.
    artifacts_dir = ML_DIR / "artifacts"
    os.makedirs(artifacts_dir, exist_ok=True)

    torch.save(model.state_dict(), artifacts_dir / "category_model.pt")

    with open(artifacts_dir / "label_mapping.json", "w", encoding="utf-8") as file:
        json.dump(
            {
                "category_to_id": category_to_id,
                "id_to_category": id_to_category,
                "model_name": settings_ml.MODEL_NAME,
                "max_length": settings_ml.MAX_LENGTH,
            },
            file,
            ensure_ascii=False,
            indent=2,
        )

    with open(artifacts_dir / "metrics.json", "w", encoding="utf-8") as file:
        json.dump(
            {
                "test_loss": test_metrics["loss"],
                "test_accuracy": test_metrics["accuracy"],
                "test_precision": test_metrics["precision"],
                "test_recall": test_metrics["recall"],
                "test_f1": test_metrics["f1"],
            },
            file,
            ensure_ascii=False,
            indent=2,
        )


def save_training_history(history):
    # История нужна, чтобы после обучения построить графики и сравнить эпохи.
    artifacts_dir = ML_DIR / "artifacts"
    os.makedirs(artifacts_dir, exist_ok=True)

    with open(artifacts_dir / "training_history.json", "w", encoding="utf-8") as file:
        json.dump(history, file, ensure_ascii=False, indent=2)


def build_test_metrics_for_plot(test_metrics):
    # Для bar chart оставляем только числовые метрики качества.
    return {
        "accuracy": test_metrics["accuracy"],
        "precision": test_metrics["precision"],
        "recall": test_metrics["recall"],
        "f1": test_metrics["f1"],
    }


def main():
    set_seed(settings_ml.RANDOM_SEED)

    device = resolve_device()
    use_amp = settings_ml.USE_AMP and device.type == "cuda"

    logger.info("Training started")
    logger.info("Device: %s", device)
    if device.type == "cuda":
        logger.info("CUDA device name: %s", torch.cuda.get_device_name(0))
    logger.info("Model: %s", settings_ml.MODEL_NAME)
    logger.info("Epochs: %s", settings_ml.NUM_EPOCHS)
    logger.info("Batch size: %s", settings_ml.BATCH_SIZE)
    logger.info("Max length: %s", settings_ml.MAX_LENGTH)
    logger.info("Learning rate: %s", settings_ml.LEARNING_RATE)
    logger.info("Warmup ratio: %s", settings_ml.WARMUP_RATIO)
    logger.info("Gradient clip norm: %s", settings_ml.GRADIENT_CLIP_NORM)
    logger.info("Mixed precision AMP: %s", use_amp)
    logger.info("Train size: %s", len(train_dataset))
    logger.info("Validation size: %s", len(val_dataset))
    logger.info("Test size: %s", len(test_dataset))
    logger.info("Categories: %s", len(category_names))

    model = E5Classifier(
        model_name=settings_ml.MODEL_NAME,
        num_labels=len(category_names),
    ).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = AdamW(model.parameters(), lr=settings_ml.LEARNING_RATE)
    scaler = GradScaler(enabled=use_amp)

    total_steps = len(train_loader) * settings_ml.NUM_EPOCHS
    warmup_steps = int(total_steps * settings_ml.WARMUP_RATIO)
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=warmup_steps,
        num_training_steps=total_steps,
    )

    best_val_f1 = 0
    history = []

    for epoch in range(1, settings_ml.NUM_EPOCHS + 1):
        logger.info("Epoch %s/%s started", epoch, settings_ml.NUM_EPOCHS)
        train_metrics = train_one_epoch(
            model,
            train_loader,
            optimizer,
            scheduler,
            criterion,
            device,
            epoch,
            scaler,
            use_amp,
        )
        val_metrics = evaluate(model, val_loader, criterion, device, "validation", use_amp)

        history.append(
            {
                "epoch": epoch,
                "train_loss": train_metrics["loss"],
                "train_accuracy": train_metrics["accuracy"],
                "train_f1": train_metrics["f1"],
                "val_loss": val_metrics["loss"],
                "val_accuracy": val_metrics["accuracy"],
                "val_precision": val_metrics["precision"],
                "val_recall": val_metrics["recall"],
                "val_f1": val_metrics["f1"],
            }
        )
        save_training_history(history)

        print(
            f"Epoch {epoch}: "
            f"train_loss={train_metrics['loss']:.4f}, "
            f"train_f1={train_metrics['f1']:.4f}, "
            f"val_loss={val_metrics['loss']:.4f}, "
            f"val_f1={val_metrics['f1']:.4f}"
        )
        logger.info(
            "Epoch %s metrics | train_loss=%.4f | train_f1=%.4f | val_loss=%.4f | val_f1=%.4f",
            epoch,
            train_metrics["loss"],
            train_metrics["f1"],
            val_metrics["loss"],
            val_metrics["f1"],
        )

        if val_metrics["f1"] > best_val_f1:
            best_val_f1 = val_metrics["f1"]
            save_artifacts(model, val_metrics)
            logger.info("Best model saved | val_f1=%.4f", best_val_f1)

    test_metrics = evaluate(model, test_loader, criterion, device, "test", use_amp)
    save_artifacts(model, test_metrics)
    save_training_history(history)

    # После обучения строим графики для анализа качества модели.
    artifacts_dir = ML_DIR / "artifacts"
    plot_training_history(history, artifacts_dir)
    plot_final_metrics(build_test_metrics_for_plot(test_metrics), artifacts_dir)
    plot_confusion_matrix(
        test_metrics["targets"],
        test_metrics["predictions"],
        category_names,
        artifacts_dir,
    )

    logger.info("Final model and metrics saved")
    logger.info("Training plots saved to %s", artifacts_dir)

    print(classification_report(
        test_metrics["targets"],
        test_metrics["predictions"],
        target_names=category_names,
        zero_division=0,
    ))
    print(f"Test accuracy: {test_metrics['accuracy']:.4f}")
    print(f"Test f1: {test_metrics['f1']:.4f}")
    logger.info("Training finished | test_accuracy=%.4f | test_f1=%.4f", test_metrics["accuracy"], test_metrics["f1"])


if __name__ == "__main__":
    main()
