import json
import time
import openai
import os
import re
import requests
from scripts.output_format import *
from scripts.json_parser import *

from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT


from langchain.chat_models import ChatOpenAI
from langchain.chat_models import ChatAnthropic

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

from dotenv import load_dotenv
load_dotenv()

anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
# anthropic_model = os.environ.get("ANTHROPIC_MODEL")
anthropic_model = "claude-2"


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_anthropic_response(input_text):
    """
    Extract the response from the Anthropic LLM for the given chat prompt.
    """
    # Initialize the ChatAnthropic instance
    chat_model = ChatAnthropic(temperature=0, anthropic_api_key=anthropic_api_key, model=anthropic_model)

    # Construct the system and human message prompts
    template = virtual_doctor_system_prompt
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template = input_text
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    # Create a chat prompt from the message prompts
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

    # Send the chat prompt to the LLM and store the response
    llm_res = chat_model(chat_prompt.format_prompt(system_message=system_message_prompt,
                                                   human_message=human_message_prompt).to_messages())

    # Log the content of the LLM response
    content = llm_res.content
    logger.debug(f'Anthropic LLM response content: {content}')
    
    return content



def get_anthropic_response1(patient_details):
    url = "https://api.anthropic.com/v1/complete"
    api_key = anthropic_api_key
    model = anthropic_model
    max_tokens_to_sample = "20000"

    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }

    payload = json.dumps({
        "prompt": f"\n\nHuman: {virtual_doctor_system_prompt}\n{patient_details}\n\nAssistant:",
        "model": model,
        "max_tokens_to_sample": max_tokens_to_sample
    })

    response = requests.post(url, headers=headers, data=payload)

    response_text = parse_json(response.text)

    return response_text



def get_anthropic_completion(patient_details, model="claude-2", max_tokens=300):
    final_prompt = f"{virtual_doctor_system_prompt}\n{patient_details}"
    # Initialize Anthropic client
    anthropic = Anthropic(api_key=anthropic_api_key)

    # Create a completion
    completion = anthropic.completions.create(temperature=0,
        model=model,
        max_tokens_to_sample=max_tokens,
        prompt=f"{HUMAN_PROMPT} {final_prompt} {AI_PROMPT}",
    )
    
    # Return the completion text
    return completion.completion




