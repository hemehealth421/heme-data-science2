import vertexai
from vertexai.preview.language_models import TextGenerationModel

import json

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

def params_vertex_response(report_text):
    prompt = f"{report_text}\n{output_format1}"
    vertex_resonse = vertex_ai_llm("dev-heme-platform", "text-bison@001", 0.2, 1000, 0.8, 40,prompt, "us-central1")
    parsed_response = parse_json(vertex_resonse)
    return parsed_response

def analysis_vertex_response(params):
    prompt = f"{params}\n{output_format2}"
    vertex_resonse = vertex_ai_llm("dev-heme-platform", "text-bison@001", 0.2, 1000, 0.8, 40,prompt, "us-central1")
    parsed_response = parse_json(vertex_resonse)
    return parsed_response

def get_vertex_response(report_text):
    param_vertex_response = params_vertex_response(report_text)
    vertex_response = params_vertex_response(param_vertex_response)
    return vertex_response

