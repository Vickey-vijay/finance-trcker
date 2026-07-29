"""Central configuration. Reads from environment / .env file."""
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "smartedit-ai-dev-secret")
    # Defaults to smartedit.db beside the application. Overridable so the data
    # file can live elsewhere, and so the test suite can point at a scratch
    # database instead of the real one.
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SMARTEDIT_DATABASE_URI",
        "sqlite:///" + os.path.join(BASE_DIR, "smartedit.db"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

    # AI provider
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "local").lower()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

    # Local quantized model (llama.cpp)
    MODEL_DIR = os.getenv("MODEL_DIR", os.path.join(BASE_DIR, "models"))
    LOCAL_MODEL_REPO = os.getenv("LOCAL_MODEL_REPO", "Qwen/Qwen2.5-1.5B-Instruct-GGUF")
    LOCAL_MODEL_FILE = os.getenv("LOCAL_MODEL_FILE", "qwen2.5-1.5b-instruct-q4_k_m.gguf")
    LOCAL_MODEL_CTX = int(os.getenv("LOCAL_MODEL_CTX", "4096"))
    LOCAL_MODEL_THREADS = int(os.getenv("LOCAL_MODEL_THREADS", "0")) or (os.cpu_count() or 4)
    LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "120"))
    CHAT_MAX_TOKENS = int(os.getenv("CHAT_MAX_TOKENS", "400"))
