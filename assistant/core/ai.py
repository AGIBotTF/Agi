import json
import re
from openai import OpenAI
from ..config import AI_MODEL, MAX_RETRY_DEPTH
from ..storage.history import get_recent_conversation_context
from ..storage.user_data import load_user_data
from .functions import execute_function_call

# Initialize OpenAI client
client = OpenAI()

def get_ai_response(prompt: str, depth=0, voice_id=""):
    print(f"Prompt: {prompt}")
    if depth > MAX_RETRY_DEPTH:
        return "Error: Exceeded maximum depth of 3."
    
    user_data = load_user_data()
    print(f"VoiceID: {voice_id} {user_data.get(voice_id, {})}")

    # Get recent conversation context
    conversation_context = get_recent_conversation_context(voice_id)

    system_prompt = f"""
        You are an AI assistant that answers questions and calls helper functions when needed.
        Respond **only** in JSON format.

        Recent conversation context:
        {conversation_context}

        You can use the following **helper functions**:
        - get_weather(location): returns the weather at the given location
        - get_stock_price(ticker): returns the latest stock price
        - set_user_data(voiceID, property, value): saves user-specific data (e.g. name, age) for future use
        - moove_left_hand(position): moves the left hand to the given position
        - moove_right_hand(position): moves the right hand to the given position
        - move_object(position_start, position_end): moves the object to the given position

        Use function calls like this:
        {{ "response": "The weather in New York is ((get_weather('New York')))", "functions": ["get_weather"] }}

        If no function is needed, just return:
        {{ "response": "Direct answer here." }}

        If you learn any identifiable information about the user (e.g. name, age, location, preferences), always save it using `set_user_data`, like this:
        {{
        "response": "Nice to meet you, Alex!",
        "functions": [
            "set_user_data(voiceId (from context), 'name', 'Alex')",
            "set_user_data(voiceId (from context), 'age', '17')"
        ]
        }}

        Do **not** try to remember anything implicitly—only save data through the `set_user_data` function.

        Use saved user data to personalize your responses, but always remain respectful and avoid sounding overly familiar.

        This is what you currently can see:
        {str([{'name': 'apple', 'position': [23.379230852250416, 1.7820315874077952, -42.59267250894498], 'position_in_words': 'bottom right'},
              {'name': 'banana', 'position': [50.379230852250416, 6.7820315874077952, -90.59267250894498], 'position_in_words': 'bottom right'}])}

        User data:
        """ + str(user_data.get(voice_id, {
            "voice_id": voice_id,
        }))
    
    try:
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        response_content = response.choices[0].message.content
        print(response_content)
        
        matches = re.findall(r'\(\((.*?)\)\)', response_content)
        for match in matches:
            try:
                result = execute_function_call(match)
                response_content = response_content.replace(f"(({match}))", str(result))
            except Exception as e:
                print(f"Error processing function call '{match}': {e}")
        
        try:
            response_json = json.loads(response_content)
        except json.JSONDecodeError:
            return get_ai_response(prompt, depth + 1, voice_id)

        return response_json["response"], response_json.get("functions", [])
        
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return "Sorry, I encountered an error while processing your request.", []

def answer(prompt: str, voice_id: str):
    from ..storage.history import add_to_conversation_history
    
    # Add user message to conversation history
    add_to_conversation_history(voice_id, prompt, is_user=True)
    
    response, functions = get_ai_response(prompt, voice_id=voice_id)
    for f in functions:
        execute_function_call(f)
    # Add assistant response to conversation history
    add_to_conversation_history(voice_id, response, is_user=False)
    
    return response 