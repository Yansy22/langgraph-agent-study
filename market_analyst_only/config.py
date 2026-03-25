import os
from dotenv import load_dotenv

# Load .env file from the project root
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

CONFIG = {
    "data_cache_dir": os.path.join(os.path.dirname(__file__), "cache"),
    "llm_provider": "google",
    "model_name": "gemini-2.5-flash",
}

def get_config():
    return CONFIG.copy()
