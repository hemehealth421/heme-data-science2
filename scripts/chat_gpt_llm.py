import json
import openai
import os
from scripts.output_format import *
# from scripts.hemebot.prompts import *
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


def get_chatgpt_response1(pre_text):
    gpt4_res = openai.ChatCompletion.create(model="gpt-4",
                                        messages=[{"role": "system", "content": HEMEBOT_PROMPT},
                                                  {"role": "user", "content": pre_text}],
                                        temperature=0)

    response_text = gpt4_res["choices"][0]["message"]["content"]
    # parsed_res = parse_json(response_text)
    return response_text

def get_key_insights(patient_details, diagnosis):
    pre_text = f"patient_details: {patient_details} \n differential_diagnosis: {diagnosis}"

    gpt4_res = openai.ChatCompletion.create(model="gpt-4",
                                        messages=[{"role": "system", "content": KEY_INSIGHT_PROMPT},
                                                  {"role": "user", "content": pre_text}],
                                        temperature=0)

    response_text = gpt4_res["choices"][0]["message"]["content"]
    # parsed_res = parse_json(response_text)
    return response_text




def update_content(user_q_list):
    logger.debug(f" processing request ")

    try:
        sys_def = {"role": "system", "content":HEMEBOT_PROMPT}
        updated_list = list()
        updated_list.append(sys_def)
        updated_list.extend(user_q_list)
        return updated_list
    except Exception as error:
        logger.debug(f" update_content did not worked due to : {error}")
        logger.exception(f" error details : ")
        return user_q_list


def check_options(bot_message):
    messages = [{"role": "system", "content": OPTIONS_SYS},
           {"role": "user", "content": bot_message}]
 
    check_options_response = openai.ChatCompletion.create(model=openai_model,
                                                           messages=messages,
                                                           temperature=0)
    
    response_text = check_options_response["choices"][0]["message"]["content"]
    
    try:
        regx = re.search("{", response_text)
        start_ind = regx.start()
        dict_text = response_text[start_ind:]
        res_json = json.loads(dict_text)
        res_json = list(res_json.values())
        return res_json
    except:
        try:
            regx1 = re.search("\[", response_text)
            regx2 = re.search("\]", response_text)

            start_ind1 = regx1.start()
            start_ind2 = regx2.start()

            options_list = ast.literal_eval(response_text[start_ind1:start_ind2+1])

            return options_list
            
        except:
            res_json = []
            return res_json


def chat_completion_with_options(user_query):
       
    logger.debug(f" requested with payload : {user_query}")

    try:
        updated_user_query = update_content(user_query)

        response = openai.ChatCompletion.create(model="gpt-4",messages=updated_user_query,temperature=0)
        
        response_text = response["choices"][0]["message"]
        r_text = response_text["content"]
        response_text["options"] = check_options(r_text)
        response_text["type"] = "tappable"
        #count number tokens processed till now in this conversation
        token_count = response["usage"]["total_tokens"]

        if token_count>2000:
            logger.debug(f" token limit exceeded, token_count : {token_count}")
            response_text = {"role": "assistant",
            "content": "Token limit has exceeded, please clear chat to proceed",
            "type": "tappable"}
            return response_text
        else:
            logger.debug(f" hemebot responded with : {response_text}")
            return response_text

    except Exception as error:
        logger.debug(f" chat_completion_with_options did not worked due to : {error}")
        logger.exception(f" ERROR details : ")
        response_text = {"role": "assistant",
                         "content": "chatbot is not responding",
                         "type": "tappable"}
        return response_text