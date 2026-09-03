import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Peblo TV API"
    API_V1_STR: str = ""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./peblo.db")
    
    # Storage & Seed Paths (resolve relative to project root c:\Users\Palash\PEBLO)
    STORAGE_DIR: str = os.getenv(
        "STORAGE_DIR",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "storage"))
    )
    SEED_DATA_DIR: str = os.getenv(
        "SEED_DATA_DIR",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "seed_data"))
    )
    
    # Auth secret
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-peblo-admin-key-2026")
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
