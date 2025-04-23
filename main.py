from assistant.core.ai import answer
from assistant.audio.tts import speak
from assistant.core.chat import chat_loop
from assistant.listener import listen_for_speech
from assistant.config import current_config, save_config
import time

def voice_loop():
    print("Voice mode activated. Press Ctrl+C to exit.")
    while True:
        try:
            user_input, voice_id = listen_for_speech()
            if user_input and voice_id:
                response = answer(user_input, voice_id)
                print(response)
                speak(response)
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nExiting voice mode...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

def main():
    print("Welcome to the AI Assistant!")
    print("Available commands:")
    print("  - 'mode': Switch between voice and chat modes")
    print("  - 'voice_id': Change your voice ID")
    print("  - 'tts': Toggle text-to-speech in chat mode")
    print("  - 'exit': Exit the program")
    
    while True:
        try:
            if current_config['mode'] == 'voice':
                voice_loop()
            else:
                chat_loop()
                
            # After exiting a mode, ask if user wants to exit completely
            choice = input("\nDo you want to exit the program? (y/n): ").lower()
            if choice == 'y':
                print("Goodbye!")
                break
                
        except KeyboardInterrupt:
            print("\nExiting program...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

if __name__ == "__main__":
    main() 