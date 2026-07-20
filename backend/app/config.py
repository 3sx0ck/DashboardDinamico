from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    jwt_expire_minutes: int = 480
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str = "pmk-raw"
    admin_email: str
    admin_password: str
    class Config:
        env_file = ".env"

settings = Settings()
