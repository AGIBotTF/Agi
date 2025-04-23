import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# File paths
USER_DATA_FILE = "user_data.json"
CONVERSATION_HISTORY_FILE = "conversation_history.json"
CONFIG_FILE = "assistant/config.json"

# AI Model settings
AI_MODEL = "gpt-4.1-mini"
MAX_RETRY_DEPTH = 3

# Audio settings
AUDIO_LANGUAGE = "en"
AUDIO_TLD = "us"

# Default configuration
DEFAULT_CONFIG = {
    "mode": "voice",  # "voice" or "chat"
    "voice_id": "default_user",  # Default voice ID for chat mode
    "use_tts": True  # Whether to use text-to-speech in chat mode
}

def load_config():
    try:
        print(CONFIG_FILE)
        if os.path.exists(CONFIG_FILE) and os.path.getsize(CONFIG_FILE) > 0:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading config: {e}")
        print("Creating new config file with defaults...")
    return DEFAULT_CONFIG

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    except IOError as e:
        print(f"Error saving config: {e}")

# Load current configuration
current_config = load_config() 