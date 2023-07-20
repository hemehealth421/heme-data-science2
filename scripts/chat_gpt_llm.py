import json
import openai
import os
from scripts.output_format import *
from scripts.hemebot.prompts import *
import re 
import ast



from dotenv import load_dotenv
load_dotenv()

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
anthropic_model = os.environ.get("ANTHROPIC_MODEL")

openai_api_key = os.environ.get('OPENAI_API_KEY')
openai_model = os.environ.get('OPENAI_MODEL')

openai.api_key = openai_api_key




def parse_json(json_str):
    text = ''.join(c for c in json_str if c > '\u001f')
    text = text.replace('\n', '\\n')
    try: 
        data = json.loads(text)
        return data
    except json.JSONDecodeError as e:
        print(f'Invalid JSON: {e}')
        return {}


def get_chatgpt_response(pre_text):
    gpt4_res = openai.ChatCompletion.create(model="gpt-4",
                                        messages=[{"role": "system", "content": virtual_doctor_system_prompt},
                                                  {"role": "user", "content": pre_text}],
                                        temperature=0)

    response_text = gpt4_res["choices"][0]["message"]["content"]
    # parsed_res = parse_json(response_text)
    return response_text


def hemebot_chatgpt_response(pre_text):
    gpt4_res = openai.ChatCompletion.create(model="gpt-4",
                                        messages=[{"role": "system", "content": HEMEBOT_PROMPT},
                                                  {"role": "user", "content": pre_text}],
                                        temperature=0)

    response_text = gpt4_res["choices"][0]["message"]["content"]
    # parsed_res = parse_json(response_text)
    return response_text

def hemebot_chatgpt_response1(pre_text):
    gpt4_res = openai.ChatCompletion.create(model="gpt-4",
                                        messages=pre_text,
                                        temperature=0)

    response_text = gpt4_res["choices"][0]["message"]["content"]
    # parsed_res = parse_json(response_text)
    return response_text

def remove_extra_newlines(text):
    lines = text.split('\n')
    cleaned_lines = [line for line in lines if line.strip() != '']
    return '\n'.join(cleaned_lines)



def get_key_insights(patient_details, diagnosis):

    gpt4_res = openai.ChatCompletion.create(model="gpt-4",
                                        messages=[{"role": "system", "content": KEY_INSIGHT_PROMPT},
                                                  {"role": "user", "content": patient_details}],
                                        temperature=0)

    response_text = gpt4_res["choices"][0]["message"]["content"]
    key_insights = f"{response_text}\n\n{diagnosis}"
    cleaned_text = remove_extra_newlines(key_insights)

    return key_insights




