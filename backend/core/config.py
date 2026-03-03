from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET_DESIGNS: str
    MINIO_BUCKET_IMAGES: str
    MINIO_USE_SSL: bool = False
    DETECTION_WEBHOOK_SECRET: str


settings = Settings()  # ← this line must be here