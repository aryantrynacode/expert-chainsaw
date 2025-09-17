import os
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "Bounty Hunter AI"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_default_secret_key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24   # 1 day
    ALGORITHM: str = "HS256"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
    allowed_origins: list = ["http://localhost:3000"]

    @validator("allowed_origins", pre=True)   # 👈 match the field name
    def assemble_allowed_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
settings = Settings()