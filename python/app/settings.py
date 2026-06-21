from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    _env_path = Path(__file__).resolve().parents[1] / ".env"  # python/.env
    model_config = SettingsConfigDict(env_file=str(_env_path), env_file_encoding="utf-8", extra="ignore")

    # ── Branding (customize for your club) ──────────────
    app_name: str = Field(default="Sports Club Manager", validation_alias="APP_NAME")
    org_name: str = Field(default="My Sports Club", validation_alias="ORG_NAME")
    member_id_label: str = Field(default="Student ID", validation_alias="MEMBER_ID_LABEL")
    email_domain: str = Field(default="", validation_alias="EMAIL_DOMAIN")  # e.g. "student.university.edu"

    # ── Database ────────────────────────────────────────
    db_type: str = Field(default="mysql", validation_alias="DB_TYPE")
    db_host: str = Field(default="127.0.0.1", validation_alias="DB_HOST")
    db_port: int = Field(default=3306, validation_alias="DB_PORT")
    db_name: str = Field(default="badminton1", validation_alias="DB_NAME")
    db_user: str = Field(default="root", validation_alias="DB_USER")
    db_password: str = Field(default="123456", validation_alias="DB_PASSWORD")

    # ── SMTP (optional) ─────────────────────────────────
    smtp_host: str | None = Field(default=None, validation_alias="SMTP_HOST")
    smtp_port: int = Field(default=587, validation_alias="SMTP_PORT")
    smtp_user: str | None = Field(default=None, validation_alias="SMTP_USER")
    smtp_password: str | None = Field(default=None, validation_alias="SMTP_PASSWORD")
    smtp_from: str | None = Field(default=None, validation_alias="SMTP_FROM")

    # ── Server ──────────────────────────────────────────
    port: int = Field(default=8081, validation_alias="PORT")

    @property
    def is_sqlite(self) -> bool:
        return self.db_type.lower() == "sqlite"

    @property
    def sqlalchemy_url(self) -> str:
        if self.is_sqlite:
            db_path = Path(__file__).resolve().parents[2] / "badminton.db"
            return f"sqlite:///{db_path}"
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        )


settings = Settings()
