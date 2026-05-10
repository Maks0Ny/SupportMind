from pydantic_settings import BaseSettings


class SettingsML(BaseSettings):
    MODEL_NAME: str = "intfloat/multilingual-e5-small"
    BATCH_SIZE: int = 256
    MAX_LENGTH: int = 64
    NUM_EPOCHS: int = 10
    RANDOM_SEED: int = 42
    DEVICE: str = "cuda"
    LEARNING_RATE: float = 2e-5
    WARMUP_RATIO: float = 0.1
    GRADIENT_CLIP_NORM: float = 1.0
    USE_AMP: bool = True


settings_ml = SettingsML()
