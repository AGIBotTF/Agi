import speech_recognition as sr
import time
import wave
import pyaudio
from openai import OpenAI
import os
import hashlib
import json
import numpy as np
from scipy.io import wavfile
from scipy.fft import fft
from assistant import answer, speak

client = OpenAI()

# Voice profiles storage
VOICE_PROFILES_FILE = "voice_profiles.json"

def load_voice_profiles():
    try:
        if os.path.exists(VOICE_PROFILES_FILE) and os.path.getsize(VOICE_PROFILES_FILE) > 0:
            with open(VOICE_PROFILES_FILE, 'r') as f:
                profiles = json.load(f)
                # Update old profiles to new format if needed
                for voice_id, profile in profiles.items():
                    if 'features' not in profile:
                        profile['features'] = {
                            'mean': 0,
                            'std': 0,
                            'max': 0,
                            'min': 0,
                            'spectral_centroid': 0,
                            'spectral_bandwidth': 0
                        }
                return profiles
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading voice profiles: {e}")
        print("Creating new voice profiles file...")
    return {}

def save_voice_profiles(profiles):
    try:
        with open(VOICE_PROFILES_FILE, 'w') as f:
            json.dump(profiles, f, indent=4)  # Add indent for better readability
    except IOError as e:
        print(f"Error saving voice profiles: {e}")

def extract_voice_features(audio_data):
    # Convert audio data to numpy array
    audio_array = np.frombuffer(audio_data.get_raw_data(), dtype=np.int16)
    
    # Calculate basic audio features
    mean = np.mean(audio_array)
    std = np.std(audio_array)
    max_val = np.max(audio_array)
    min_val = np.min(audio_array)
    
    # Calculate spectral features
    fft_result = np.abs(fft(audio_array))
    spectral_centroid = np.sum(fft_result * np.arange(len(fft_result))) / np.sum(fft_result)
    spectral_bandwidth = np.sqrt(np.sum(fft_result * (np.arange(len(fft_result)) - spectral_centroid)**2) / np.sum(fft_result))
    
    return {
        'mean': float(mean),
        'std': float(std),
        'max': float(max_val),
        'min': float(min_val),
        'spectral_centroid': float(spectral_centroid),
        'spectral_bandwidth': float(spectral_bandwidth)
    }

def calculate_similarity(features1, features2):
    # Calculate similarity score between two sets of features
    weights = {
        'mean': 0.2,
        'std': 0.2,
        'max': 0.1,
        'min': 0.1,
        'spectral_centroid': 0.2,
        'spectral_bandwidth': 0.2
    }
    
    score = 0
    for feature in weights:
        # Normalize the difference
        diff = abs(features1[feature] - features2[feature])
        max_val = max(abs(features1[feature]), abs(features2[feature]))
        if max_val != 0:
            normalized_diff = diff / max_val
            score += (1 - normalized_diff) * weights[feature]
    
    return score

def recognize_voice(audio_data, voice_profiles):
    # Extract features from current audio
    current_features = extract_voice_features(audio_data)
    
    # Calculate similarity with existing profiles
    best_match = None
    best_score = 0.7  # Minimum similarity threshold
    
    for voice_id, profile in voice_profiles.items():
        # Ensure profile has features
        if 'features' not in profile:
            profile['features'] = current_features  # Initialize with current features
        
        similarity = calculate_similarity(current_features, profile['features'])
        if similarity > best_score:
            best_score = similarity
            best_match = voice_id
    
    if best_match:
        # Update the profile with new features (moving average)
        profile = voice_profiles[best_match]
        for feature in current_features:
            profile['features'][feature] = 0.7 * profile['features'][feature] + 0.3 * current_features[feature]
        profile['usage_count'] = profile.get('usage_count', 0) + 1
        save_voice_profiles(voice_profiles)
        return best_match, profile
    
    # If no good match found, create new profile
    new_voice_id = hashlib.sha256(str(time.time()).encode()).hexdigest()[:10]
    voice_profiles[new_voice_id] = {
        'features': current_features,
        'first_seen': time.time(),
        'usage_count': 1
    }
    save_voice_profiles(voice_profiles)
    return new_voice_id, voice_profiles[new_voice_id]

def listen_for_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        # Adjust for ambient noise
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            # Listen for speech with a longer timeout and phrase time limit
            audio = recognizer.listen(source, timeout=30, phrase_time_limit=20)
            print("Processing speech...")
            
            # Get the actual frame rate from the audio data
            frame_rate = audio.sample_rate
            
            # Save raw audio data to a WAV file
            with wave.open("raw_audio.wav", "wb") as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 2 bytes per sample
                wav_file.setframerate(frame_rate)  # Use actual frame rate
                wav_file.writeframes(audio.get_raw_data())
            
            # Transcribe using Whisper with English language specified
            with open("raw_audio.wav", "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text",
                    language="en" 
                )
            
            # Recognize voice and get voice ID
            voice_profiles = load_voice_profiles()
            voice_id, voice_profile = recognize_voice(audio, voice_profiles)
            
            print(f"Voice ID: {voice_id}")
            print(f"Usage count: {voice_profile.get('usage_count', 0)}")
            
            return transcript, voice_id
        except sr.WaitTimeoutError:
            print("No speech detected")
            return None, None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None, None

def main():
    print("Voice Recognition System is ready. Press Ctrl+C to exit.")
    while True:
        try:
            # Wait for user to start speaking
            user_input, voice_id = listen_for_speech()
            if user_input and voice_id:
                response = answer(user_input, voice_id)
                print(response)
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

if __name__ == "__main__":
    main() 