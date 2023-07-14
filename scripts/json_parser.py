import json

def parse_json(json_str):
    # Input validation
    if not isinstance(json_str, str):
        raise ValueError("The input data should be a string.")
        
    # Find the start and end of JSON
    try:
        json_start = json_str.index("{")
        json_end = json_str.rindex("}") + 1  # rindex gets the last occurrence of "}"
    except ValueError:
        raise ValueError("No valid JSON object found in the input string.")
        
    # Extract the JSON part from the string
    json_string = json_str[json_start:json_end]
    
    # Remove control characters and replace newline characters
    text = ''.join(c for c in json_string if c > '\u001f')
    text = text.replace('\n', '\\n')
    
    # Try to parse the JSON
    try: 
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
    
    # If any value in the data dictionary is a list, convert it to a string
    for key, value in data.items():
        if isinstance(value, list):
            # Join the list elements into a single string with newlines between elements
            data[key] = '\n'.join(str(v) for v in value)
    
    return data
