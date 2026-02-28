from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Auth / Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # MinIO / Object Storage
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET_DESIGNS: str
    MINIO_BUCKET_IMAGES: str
    MINIO_USE_SSL: bool = False

    # Detection Webhook
    DETECTION_WEBHOOK_SECRET: str

    class Config:
        env_file = ".env"


settings = Settings()