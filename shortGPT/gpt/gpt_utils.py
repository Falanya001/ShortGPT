import json
import os
import re
from time import sleep, time
import google.generativeai as genai
import yaml

from shortGPT.config.api_db import ApiKeyManager


def num_tokens_from_messages(texts, model="gemini-1.5-pro-002"):
    """Returns the number of tokens used by a list of messages."""
    try:
        # For Gemini, we'll use a simple character-based estimation
        if isinstance(texts, str):
            texts = [texts]
        score = 0
        for text in texts:
            # Rough estimation: 4 characters per token
            score += len(str(text)) // 4
        return score
    except Exception as e:
        print(f"Error estimating tokens: {e}")
        return 0


def extract_biggest_json(string):
    json_regex = r"\{(?:[^{}]|(?R))*\}"
    json_objects = re.findall(json_regex, string)
    if json_objects:
        return max(json_objects, key=len)
    return None


def get_first_number(string):
    pattern = r'\b(0|[1-9]|10)\b'
    match = re.search(pattern, string)
    if match:
        return int(match.group())
    else:
        return None


def load_yaml_file(file_path: str) -> dict:
    """Reads and returns the contents of a YAML file as dictionary"""
    return yaml.safe_load(open_file(file_path))


def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    return json_data


from pathlib import Path


def load_local_yaml_prompt(file_path):
    _here = Path(__file__).parent
    _absolute_path = (_here / '..' / file_path).resolve()
    json_template = load_yaml_file(str(_absolute_path))
    return json_template['chat_prompt'], json_template['system_prompt']


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


def llm_completion(chat_prompt="", system="", temp=0.7, max_tokens=2000, remove_nl=True, conversation=None):
    """Use Gemini for text generation"""
    gemini_key = ApiKeyManager.get_api_key("GEMINI_API_KEY")
    if not gemini_key:
        raise Exception("Gemini API Key not found. Please set GEMINI_API_KEY in your environment.")
    
    try:
        # Configure Gemini
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-1.5-pro-002')
        
        try:
            if conversation:
                # Handle chat history
                chat = model.start_chat(history=conversation)
                response = chat.send_message(chat_prompt)
            else:
                # Combine system and user prompts
                full_prompt = f"{system}\n\nUser Request: {chat_prompt}" if system else chat_prompt
                generation_config = genai.types.GenerationConfig(
                    temperature=temp,
                    max_output_tokens=max_tokens,
                )
                response = model.generate_content(
                    full_prompt,
                    generation_config=generation_config
                )
            
            if not response.text:
                raise Exception("Empty response from Gemini")
                
            text = response.text.strip()
            if remove_nl:
                text = ' '.join(text.split())
            
            # Log the response
            filename = f'{time()}_llm_completion.txt'
            if not os.path.exists('.logs/gpt_logs'):
                os.makedirs('.logs/gpt_logs')
            with open(f'.logs/gpt_logs/{filename}', 'w', encoding='utf-8') as outfile:
                outfile.write(
                    f"System prompt: ===\n{system}\n===\n"
                    f"Chat prompt: ===\n{chat_prompt}\n===\n"
                    f'RESPONSE:\n====\n{text}\n===\n'
                )
            return text
            
        except Exception as e:
            raise Exception(f"Error with Gemini API: {str(e)}")
            
    except Exception as e:
        raise Exception(f"Failed to initialize Gemini: {str(e)}")
