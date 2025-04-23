import random
from ..storage.user_data import set_user_data

def get_weather(location):
    return "28°C and sunny"
    
def get_stock_price(ticker):
    return f"${round(100 + hash(ticker) % 50, 2)}"

def move_object(start_pos, end_pos):
    # Convert string representations of lists to actual lists
    if isinstance(start_pos, str):
        start_pos = eval(start_pos)
    if isinstance(end_pos, str):
        end_pos = eval(end_pos)
    return f"Moving object from {start_pos} to {end_pos}"

def execute_function_call(func_call):
    try:
        # Extract function name and arguments
        func_name = func_call.split("(")[0]
        args_str = func_call[func_call.find("(")+1:func_call.rfind(")")]
        
        # Parse arguments properly, handling lists
        args = []
        current_arg = ""
        bracket_count = 0
        for char in args_str:
            if char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
            elif char == ',' and bracket_count == 0:
                args.append(current_arg.strip().strip("'"))
                current_arg = ""
                continue
            current_arg += char
        if current_arg:
            args.append(current_arg.strip().strip("'"))
        
        function_map = {
            "get_weather": get_weather,
            "get_stock_price": get_stock_price,
            "set_user_data": set_user_data,
            "move_object": move_object
        }
        
        if func_name in function_map:
            result = function_map[func_name](*args)
            print(f"Executed {func_call}: {result}")
            return result
        else:
            print(f"Unknown function: {func_name}")
            return None
    except Exception as e:
        print(f"Error executing function call '{func_call}': {e}")
        return None 