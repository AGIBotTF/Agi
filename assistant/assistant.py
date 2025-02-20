from pymongo import MongoClient
from dotenv import load_dotenv
import os
import json
import ollama
import re


def answer(prompt: str):
    cached_response = get_cached_response(prompt)
    
    if cached_response:
        return cached_response
    
    ai_response = get_ai_response(prompt)
    
    # if ai_response and ai_response.get("cacheable", False):
    #     cache_response(prompt, ai_response["response"])
    
    return ai_response["response"]

def get_cached_response(question: str):
    """
    Retrieves the cached response for a given question from MongoDB.
    """
    try:
        load_dotenv()
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        db_name = os.getenv("MONGO_DB_NAME", "cache_db")
        collection_name = os.getenv("MONGO_COLLECTION_NAME", "responses")
        
        client = MongoClient(mongo_uri)
        db = client[db_name]
        collection = db[collection_name]
        
        result = collection.find_one({"question": question})
        return result["response"] if result else None
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None
    finally:
        client.close()

def get_ai_response(prompt: str):
    system_prompt = {
        "system": """You are an AI assistant that decides how to respond to user queries.
                   You can either answer directly or suggest calling an API function.
                   If you want to call an api give the response and say where should the api result be put
                   for example 'The weather is New York is ((get_weather("New Your"))',
                   respond in JSON in the format { response: "The weather is New York is ((get_weather("New Your"))", functions: "get_weather" }
                   respond only in json. No other words or symbols. if you use an api call say where its result will stay in the response as in the example.
                   if the function you want to use needs params you have to fill them out.
                   if you dont have the rigth api or you decide not to use one the respose still reply in the same format just leave the functions as an eampty array.
                   DO NOT use apis that are not givn to you in the list of functions. Never use a non existent api.""",
        "functions": [
            {"name": "get_weather", "params": ["location"]},
            {"name": "get_stock_price", "params": ["ticker"]}
        ]
    }
    
    full_prompt = json.dumps({"instruction": system_prompt, "user_prompt": prompt})
    
    response = ollama.chat(model="deepseek-r1", messages=[{"role": "user", "content": full_prompt}])
    response_content = response["message"]["content"]
    response_answer = re.sub(r'<think>.*?</think>', '', response_content, flags=re.DOTALL)

    print("------------------")
    print(response_content)
    print("------------------")
    print(response_answer)
    print("------------------")
    response_json = re.search(r'\{.*\}', response_answer, re.DOTALL).group(0)
    print(response_json)
    print("------------------")
    try:
        return json.loads(response_json)
    except json.JSONDecodeError:
        return {"response": "Error processing AI response.", "cacheable": False}

def cache_response(question: str, response: str):
    """
    Caches a response in MongoDB.
    """
    try:
        load_dotenv()
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        db_name = os.getenv("MONGO_DB_NAME", "cache_db")
        collection_name = os.getenv("MONGO_COLLECTION_NAME", "responses")
        
        client = MongoClient(mongo_uri)
        db = client[db_name]
        collection = db[collection_name]
        
        collection.insert_one({"question": question, "response": response})
    except Exception as e:
        print(f"Error caching response: {e}")
    finally:
        client.close()

# Example Usage
response = answer("Whats the weather in NYC")
print(response)
