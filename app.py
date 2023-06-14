import streamlit as st
import boto3
from botocore.exceptions import NoCredentialsError
from scripts.ocr import TextractExtractor
from scripts.info_extraction import LLMExtractor
from scripts.prescription_extraction import pre_extract
from scripts.vertexai_llm import *

from scripts.output_format import *

ds_bucket_name = "attributes-extraction-heme"


def upload_file_to_s3(file, bucket_name):
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_fileobj(file, bucket_name, file.name)
        st.success('File uploaded successfully.')
    except NoCredentialsError:
        st.error("AWS credentials not found.")
    except Exception as e:
        st.error(f"Error uploading file to S3: {str(e)}")


# Streamlit app interface
st.title('Explain My Health Records')

uploaded_file = st.file_uploader("Choose a PDF file or an Image", type=["pdf", "png", "jpg", "jpeg"])

# Define the options for the drop-downs
llm_options = ["OpenAI", "Anthropic", "VertexAI"] 

ai_role_options = ["You are a doctor", "You are an expert", "You are a pathologist", "You are a Pharmacist"]
ai_job_options = ["extract useful information from", "Explain the given text", "Summarize the given text"]
doc_type_options = ["Pathology Test Report", "Doctor Prescription", "Medical Insurance Premium Receipt"]
ai_restriction_options = [ai_restriction] # Please replace 'ai_restriction' with the actual values

# Prompt user to select options for the arguments
selected_llm = st.selectbox("LLM choice", llm_options)

ai_role = st.selectbox("AI Role", ai_role_options)
ai_job = st.selectbox("AI Job", ai_job_options)
doc_type = st.selectbox("Doc Type", doc_type_options)
ai_restriction = st.selectbox("AI Restriction", ai_restriction_options)

# Create an instance of the TextractExtractor
text_extractor = TextractExtractor()



if uploaded_file is not None:
    # Check if the user clicked the 'Upload File' button
    if st.button('Upload File'):
        # Upload the file to S3
        upload_file_to_s3(uploaded_file, ds_bucket_name)


if st.button('Explain My Health Record'):
    # Make sure the file has been uploaded and parameters selected before trying to extract data from it
    if uploaded_file is None:
        st.error('You must upload a file first.')
    else:
        progress_message = st.empty()
        progress_message.text('Getting health details from your record...')
        
        # Use the extractor to get the text from the file
        extracted_text = text_extractor.get_raw_text_list(ds_bucket_name, uploaded_file.name)


        if doc_type == "Doctor Prescription":
            progress_message = st.empty()
            progress_message.text('Getting drug details...')
            pre_result = pre_extract(extracted_text[0])
            st.write('Drugs Details:')
            st.write(pre_result)

        else:

            if selected_llm == "VertexAI":
                
                # If VertexAI was selected, call your VertexAI function
                vertex_params = params_vertex_response(extracted_text[0])
                st.write('Your Health Details')
                st.write('Parameters:')

                st.write(vertex_params)
                progress_message = st.empty()
                progress_message.text('Getting health analysis...')

                # Parse the extracted response if it's in JSON format
                vertex_analysis = analysis_vertex_response(vertex_params)
                st.write('Health Analysis:')
                st.write(vertex_analysis)

            else:
                # Initialize LLMExtractor based on the selected LLM
                llm_extractor = LLMExtractor(selected_llm)
                # Use the extractor to get the text from the file and pass user-selected arguments
                llm_extraction_result = llm_extractor.extract(
                    ai_role=ai_role,
                    ai_job=ai_job,
                    doc_type=doc_type,
                    output_format=PARAMETER_EXTRACTION_SYS,
                    ai_restriction=ai_restriction,
                    input_text=extracted_text[0]  # Get text from extracted_text
                )

                st.write('Your Health Details')
                # st.write(llm_extraction_result.content)

                # Parse the extracted response if it's in JSON format
                parsed_response = llm_extraction_result.parse_json()
                st.write('Parameters:')
                st.write(parsed_response)


                progress_message = st.empty()
                progress_message.text('Getting health analysis...')

                llm_assess_result = llm_extractor.extract(
                    ai_role=ai_role,
                    ai_job=ai_job,
                    doc_type=doc_type,
                    output_format=REPORTS_ASSESS_PROMPT,
                    ai_restriction=ai_restriction,
                    input_text=extracted_text[0]  # Get text from extracted_text
                )

                # st.write('Your Health Details')
                # st.write(llm_extraction_result.content)

                # Parse the extracted response if it's in JSON format
                parsed_assess_response = llm_assess_result.parse_json()
                st.write('Health Analysis:')
                st.write(parsed_assess_response)