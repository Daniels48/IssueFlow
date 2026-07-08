from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class LoggingSettings(BaseModel):
    log_level: str = "INFO"

class RabbitSettings(BaseModel):
    host: str
    port: int
    user: str
    password: str


# class EmailSettings(BaseModel):
#     user: str
#     password: str
#     host: str
#     port: int
#     starttls: bool
#     ssl_tls: bool


class DbSettings(BaseModel):
    name: str
    test_name: str
    host: str
    user: str
    port: int
    password: str


class SecuritySettings(BaseModel):
    jwt_secret: str
    refresh_secret: str
    algorithm: str
    access_token_expire_min: int = 30
    refresh_token_expire_days: int = 7

    @property
    def access_token_expire_seconds(self) -> int:
        return self.access_token_expire_min * 60

    @property
    def refresh_token_expire_seconds(self) -> int:
        return self.refresh_token_expire_days * 24 * 60 * 60


class Settings(BaseSettings):
    db: DbSettings
    security: SecuritySettings
    rabbit: RabbitSettings
    # logging: LoggingSettings
    # email: EmailSettings


    model_config = {"env_file": BASE_DIR / ".env", "env_file_encoding": "utf-8", "env_nested_delimiter": "__"}

    def _build_db_url(self, database: str) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.db.user}:{self.db.password}"
            f"@{self.db.host}:{self.db.port}/{database}"
        )


    @property
    def async_db_url(self) -> str:
        return self._build_db_url(self.db.name)


    @property
    def test_async_db_url(self) -> str:
        return self._build_db_url(self.db.test_name)

settings = Settings()
