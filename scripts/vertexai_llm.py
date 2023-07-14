import vertexai
from vertexai.preview.language_models import TextGenerationModel

import json
import os
from scripts.output_format import *



from langchain.chat_models import ChatVertexAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import HumanMessage, SystemMessage


from dotenv import load_dotenv
load_dotenv()

gcp_cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
vertex_model = os.environ.get("VERTEX_MODEL")



import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)




output_format1 = """extract all lab test parameters and their values and unit, Give a response in the JSON format considering these details:
{"parameter name":"parameter value with unit"}"""

output_format2 = """Give a response in the JSON format considering these details: {"differential_diagnosis": make a differential diagnosis about patient report using ICD 10 standards,
"key_insights": key insights about patients health as per the report,
"recommended_test_confirm_diagnosis": tests that are needed for further diagnoses,
"recommended_specialist": specialist doctor who needs to be visited}"""


def parse_json(json_str):
    text = ''.join(c for c in json_str if c > '\u001f')
    text = text.replace('\n', '\\n')
    try: 
        data = json.loads(text)
        return data
    except json.JSONDecodeError as e:
        print(f'Invalid JSON: {e}')
        return {}

def vertex_ai_llm(
    project_id: str,
    model_name: str,
    temperature: float,
    max_decode_steps: int,
    top_p: float,
    top_k: int,
    content: str,
    location: str = "us-central1",
    tuned_model_name: str = "",
    ) :
    """Predict using a Large Language Model."""
    vertexai.init(project=project_id, location=location)
    model = TextGenerationModel.from_pretrained(model_name)
    if tuned_model_name:
        model = model.get_tuned_model(tuned_model_name)
    response = model.predict(
        content,
        temperature=temperature,
        max_output_tokens=max_decode_steps,
        top_k=top_k,
        top_p=top_p,)
#     print(f"Response from Model: {response.text}")
    
    return response.text

def get_vertex_response(patient_details):
    final_prompt = f"{virtual_doctor_system_prompt}\n{patient_details}"
    vertex_resonse = vertex_ai_llm("dev-heme-platform", "text-bison@001", 0.2, 1000, 0.8, 40,final_prompt, "us-central1")
    return vertex_resonse



def get_vertex_ai_response(input_text):
    """
    Extract the response from the VertexAI LLM for the given chat prompt.
    """
    # Initialize the ChatVertexAI instance
    chat_model = ChatVertexAI()
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
    logger.debug(f'VertexAI LLM response content: {content}')
    
    return content




