from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix


def plot_training_history(history: list[dict], output_dir: Path) -> None:
    # Этот график показывает, как loss и F1 менялись по эпохам.
    if not history:
        return

    epochs = [row["epoch"] for row in history]
    train_loss = [row["train_loss"] for row in history]
    val_loss = [row["val_loss"] for row in history]
    train_f1 = [row["train_f1"] for row in history]
    val_f1 = [row["val_f1"] for row in history]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].plot(epochs, train_loss, marker="o", label="train loss")
    axes[0].plot(epochs, val_loss, marker="o", label="validation loss")
    axes[0].set_title("Loss by epoch")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Loss")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(epochs, train_f1, marker="o", label="train F1")
    axes[1].plot(epochs, val_f1, marker="o", label="validation F1")
    axes[1].set_title("F1 by epoch")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("F1")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(output_dir / "training_history.png", dpi=160)
    plt.close(fig)


def plot_final_metrics(metrics: dict, output_dir: Path) -> None:
    # Этот график быстро показывает итоговое качество модели на test dataset.
    metric_names = ["accuracy", "precision", "recall", "f1"]
    metric_values = [
        metrics["accuracy"],
        metrics["precision"],
        metrics["recall"],
        metrics["f1"],
    ]

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=metric_names, y=metric_values, ax=ax)
    ax.set_ylim(0, 1)
    ax.set_title("Final test metrics")
    ax.set_ylabel("Score")
    ax.grid(True, axis="y", alpha=0.3)

    fig.tight_layout()
    fig.savefig(output_dir / "final_metrics.png", dpi=160)
    plt.close(fig)


def plot_confusion_matrix(
    targets: list[int],
    predictions: list[int],
    category_names: list[str],
    output_dir: Path,
) -> None:
    # Confusion matrix показывает, какие категории модель чаще всего путает.
    matrix = confusion_matrix(targets, predictions)

    fig, ax = plt.subplots(figsize=(max(10, len(category_names)), max(8, len(category_names) * 0.6)))
    sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=category_names,
        yticklabels=category_names,
        ax=ax,
    )
    ax.set_title("Confusion matrix")
    ax.set_xlabel("Predicted category")
    ax.set_ylabel("True category")

    fig.tight_layout()
    fig.savefig(output_dir / "confusion_matrix.png", dpi=160)
    plt.close(fig)
