import json

from scripts.chat_gpt_llm import *
from scripts.vertexai_llm import *
from scripts.anthropic_llm import *



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
import time

import openai
import json
import os
import re
from dotenv import load_dotenv
load_dotenv()

anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
anthropic_model = os.environ.get("ANTHROPIC_MODEL")

openai_api_key = os.environ.get('OPENAI_API_KEY')
openai_model = os.environ.get('OPENAI_MODEL')



aws_default_region = os.getenv("AWS_DEFAULT_REGION")
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

gcp_cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")



import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LLMExtractor:
    """
    This class is used to interact with different Large Language Models (LLMs)
    by OpenAI and Anthropic. It sends chat prompts to the LLM and extracts
    the response.
    """
    def __init__(self, llm_name):
        """
        Initialize the LLMExtractor with the name of the LLM.
        Raise a ValueError if the LLM name is neither 'OpenAI' nor 'Anthropic'.
        """
        self.llm_res = None
        self.content = None
        self.llm_name = llm_name
        self.llm_chat = None

        

    def differential_diagnosis(self, prompt_text):

        """
        Extract the response from the LLM for the given chat prompt and ask for a differential diagnosis based on given symptoms and conditions.
        """
        # Initializing LLM based on the given name
        if self.llm_name == "OpenAI":
            self.llm_res = get_chatgpt_response(prompt_text)
        elif self.llm_name == "Anthropic":
            # self.llm_res = get_anthropic_response(prompt_text)
            # self.llm_res = get_anthropic_response1(prompt_text)
            self.llm_res = get_anthropic_completion(prompt_text)
        elif self.llm_name == "VertexAI":
            # self.llm_res = get_vertex_response(prompt_text)
            self.llm_res = get_vertex_ai_response(prompt_text)
        
        else:
            logger.exception("Invalid LLM name. Please choose either 'OpenAI' or 'Anthropic' or 'VertexAI'.")
            raise ValueError("Invalid LLM name. Please choose either 'OpenAI' or 'Anthropic' or 'VertexAI'.")

        self.content = self.llm_res
        logger.debug(f'LLM {self.llm_name} response content: {self.content}')

        # Parsing the LLM response content
        return self.content

    def parse_json(self):
        """
        Parse the JSON content of the LLM response.
        Return an empty dictionary if the content is not valid JSON.
        """
        # Preprocessing the content to remove control characters and replace newline characters
        text = ''.join(c for c in self.content if c > '\u001f')
        text = text.replace('\n', '\\n')

        # Attempting to parse the content as JSON
        try:
            data = json.loads(text)
            return data
        except json.JSONDecodeError as e:
            # Logging any JSON decoding errors
            logger.exception(f'Invalid JSON: {e}')
            return {"Response": self.content}

