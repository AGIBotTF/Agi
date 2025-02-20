import ollama
from assistant_config import config
from assistant import answer

if __name__ == "__main__":
    assistantName = config["name"]
    print(f"{assistantName}: How can i help you?")
    userPrompt = input("User: ")
    answer(userPrompt)
    