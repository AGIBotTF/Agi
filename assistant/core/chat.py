from ..config import current_config
from .ai import answer
from ..audio.tts import speak

def chat_loop():
    print("\nChat mode activated. Type 'exit' to quit or 'mode' to switch modes.")
    print(f"Current voice ID: {current_config['voice_id']}")
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'exit':
                print("Exiting chat mode...")
                break
                
            if user_input.lower() == 'mode':
                new_mode = input("Enter mode (voice/chat): ").lower()
                if new_mode in ['voice', 'chat']:
                    current_config['mode'] = new_mode
                    save_config(current_config)
                    print(f"Mode changed to {new_mode}")
                    break
                else:
                    print("Invalid mode. Please enter 'voice' or 'chat'")
                continue
                
            if user_input.lower() == 'voice_id':
                new_id = input("Enter your voice ID: ").strip()
                if new_id:
                    current_config['voice_id'] = new_id
                    save_config(current_config)
                    print(f"Voice ID changed to {new_id}")
                continue
                
            if user_input.lower() == 'tts':
                current_config['use_tts'] = not current_config['use_tts']
                save_config(current_config)
                status = "enabled" if current_config['use_tts'] else "disabled"
                print(f"Text-to-speech {status}")
                continue
            
            response = answer(user_input, current_config['voice_id'])
            print(f"\nAssistant: {response}")
            
            if current_config['use_tts']:
                speak(response)
                
        except KeyboardInterrupt:
            print("\nExiting chat mode...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            continue 