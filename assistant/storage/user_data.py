import json
import os
from ..config import USER_DATA_FILE

def load_user_data():
    try:
        if os.path.exists(USER_DATA_FILE) and os.path.getsize(USER_DATA_FILE) > 0:
            with open(USER_DATA_FILE, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading user data: {e}")
        print("Creating new user data file...")
    return {}

def save_user_data(data):
    try:
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"Error saving user data: {e}")

def set_user_data(voice_id, property, value):
    user_data = load_user_data()
    if voice_id not in user_data:
        user_data[voice_id] = {
            "voice_id": voice_id,
        }
    user_data[voice_id][property] = value
    save_user_data(user_data)
    return f"Set {property} to {value} for user {voice_id}" 