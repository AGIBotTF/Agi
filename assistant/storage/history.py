import json
import os
from datetime import datetime
from ..config import CONVERSATION_HISTORY_FILE

def load_conversation_history():
    try:
        if os.path.exists(CONVERSATION_HISTORY_FILE) and os.path.getsize(CONVERSATION_HISTORY_FILE) > 0:
            with open(CONVERSATION_HISTORY_FILE, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading conversation history: {e}")
        print("Creating new conversation history file...")
    return []

def save_conversation_history(history):
    try:
        with open(CONVERSATION_HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=4)
    except IOError as e:
        print(f"Error saving conversation history: {e}")

def add_to_conversation_history(voice_id, message, is_user=True):
    conversation_history = load_conversation_history()
    if not isinstance(conversation_history, list):
        conversation_history = []
    
    timestamp = datetime.now().isoformat()
    entry = {
        "timestamp": timestamp,
        "voice_id": voice_id,
        "message": message,
        "is_user": is_user
    }
    conversation_history.append(entry)
    
    # Keep only the last 5 messages
    if len(conversation_history) > 5:
        conversation_history = conversation_history[-5:]
    
    save_conversation_history(conversation_history)
    return conversation_history

def get_recent_conversation_context(voice_id):
    conversation_history = load_conversation_history()
    # Filter history for this user and get last 5 messages
    user_history = [msg for msg in conversation_history if msg["voice_id"] == voice_id][-5:]
    context = []
    for msg in user_history:
        speaker = "User" if msg["is_user"] else "Assistant"
        context.append(f"{speaker}: {msg['message']}")
    return "\n".join(context) 