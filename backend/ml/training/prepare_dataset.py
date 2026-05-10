from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


ML_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ML_DIR / "data" / "processed"

df = pd.read_csv(DATA_DIR / "prepared.csv")

df_train_val, df_test = train_test_split(
    df,
    test_size=0.2,
    random_state=42,
    stratify=df["category"],
)

df_train, df_val = train_test_split(
    df_train_val,
    test_size=0.125,
    random_state=42,
    stratify=df_train_val["category"],
)

DATA_DIR.mkdir(parents=True, exist_ok=True)

df_train.to_csv(DATA_DIR / "train.csv", index=False)
df_val.to_csv(DATA_DIR / "val.csv", index=False)
df_test.to_csv(DATA_DIR / "test.csv", index=False)
