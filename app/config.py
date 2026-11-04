import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if present
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Students Database CRUD Application")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    
    # SQLite Database Configuration (supports Embarko's DATA_DIR for persistent storage)
    data_dir = os.getenv("DATA_DIR")
    if data_dir:
        default_db = f"sqlite:///{Path(data_dir) / 'students.db'}"
    else:
        default_db = "sqlite:///./students.db"
    DATABASE_URL: str = os.getenv("DATABASE_URL", default_db)
    
    # Ollama AI Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
    OLLAMA_TIMEOUT_SECONDS: float = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "30.0"))

settings = Settings()
