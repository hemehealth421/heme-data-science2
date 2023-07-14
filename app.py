import streamlit as st
import boto3
from botocore.exceptions import NoCredentialsError
from scripts.ocr import TextractExtractor
from scripts.info_extraction import LLMExtractor
from scripts.prescription_extraction import pre_extract
from scripts.vertexai_llm import *
from scripts.output_format import *
from scripts.patient_info import *


ds_bucket_name = "attributes-extraction-heme"

def upload_file_to_s3(file, bucket_name):
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_fileobj(file, bucket_name, file.name)
        st.success(f'**{file.name}**   -   File uploaded successfully.')
    except NoCredentialsError:
        st.error("AWS credentials not found.")
    except Exception as e:
        st.error(f"Error uploading file to S3: {str(e)}")

st.title('🩺 Virtual Doctor')

st.markdown("---")
st.header('👤 Patient Demographics')

# User Profile Input
age = st.number_input('Enter your Age (Optional)', min_value=0, max_value=120, step=1, value=0)
gender = st.selectbox('Select your Gender (Optional)', ['-', 'Male', 'Female', 'Other'])
race_ethnicity = st.selectbox('Select your Race/Ethnicity (Optional)', ['-', 'African', 'Middle Eastern', 'Indian', 'Hispanic', 'Mediterranean', 'Caucasian', 'Northern European', 'African American', 'Native American', 'Asian American', 'Ashkenazi Jewish', 'Italian', 'Greek', 'Asian', 'Turkish', 'Other'])

st.markdown("---")
st.header('🌡️ Symptoms')

# Symptoms
symptoms = st.text_area('Enter your symptoms (Optional)', '')
onset = st.text_input('Enter the onset of your symptoms (Optional)', '')
duration = st.text_input('Enter the duration of your symptoms (Optional)', '')
severity = st.text_input('Enter the severity of your symptoms (Optional)', '')
associated_symptoms = st.text_area('Enter any associated symptoms (Optional)', '')

st.markdown("---")
st.header('📚 Medical and Family History')

# Medical and Family History
medical_history = st.text_area('Enter your medical history details (Optional)', '')
prior_conditions = st.text_area('Enter your prior conditions (Optional)', '')
surgeries = st.text_area('Enter any surgeries you have had (Optional)', '')
medications = st.text_area('Enter any medications you are currently taking (Optional)', '')
family_history = st.text_area('Enter your family medical history details (Optional)', '')

st.markdown("---")
st.header('🧑‍💼 Social History')

# Social History
occupation = st.text_input('Enter your occupation (Optional)', '')
habits = st.text_area('Enter any habits (Optional)', '')
exposures = st.text_area('Enter any significant exposures (Optional)', '')

st.markdown("---")
st.header('🔎 Physical Exam Findings')

# Physical Examination
physical_exam = st.text_area('Enter your physical examination details (Optional)', '')

st.markdown("---")
st.header('🔬 Diagnostic Tests')

# Diagnostic Tests
diagnostic_tests = st.text_area('Enter your diagnostic tests details (Optional)', '')
labs = st.text_area('Enter your lab results (Optional)', '')
imaging = st.text_area('Enter any imaging results (Optional)', '')
pathology_reports = st.text_area('Enter any pathology reports (Optional)', '')

st.markdown("---")
st.header('📤 Upload Medical Documents')

# File upload
uploaded_files = st.file_uploader('Choose a file (Optional)', type=["pdf", "png", "jpg", "jpeg", "txt"], accept_multiple_files=True)

st.markdown("---")
st.header('🧠 Select Language Model')

llm_options = ["OpenAI", "Anthropic", "VertexAI"]
selected_llm = st.selectbox("LLM choice", llm_options)

# Create an instance of the TextractExtractor
text_extractor = TextractExtractor()

# Initialize the LLMExtractor
llm_extractor = LLMExtractor(selected_llm)

st.markdown("---")
st.header('🔍 Get Differential Diagnosis')

if st.button('Analyze'):
    if uploaded_files is None and not symptoms:
        st.error('Please enter symptoms or upload a file.')
    else:
        progress_message = st.empty()
        progress_message.text('Virtual consultation in progress...')
        final_extracted_text = ""
        for uploaded_file in uploaded_files:
            # Upload the file to S3
            upload_file_to_s3(uploaded_file, ds_bucket_name)
            # Use the extractor to get the text from the file
            extracted_text = text_extractor.get_raw_text_list(ds_bucket_name, uploaded_file.name)
            final_extracted_text = f"{final_extracted_text} \n {extracted_text}" 

        patient_details = create_patient_details(age, gender, race_ethnicity, symptoms, onset, duration, severity, associated_symptoms, medical_history, prior_conditions, surgeries, medications, family_history, occupation, habits, exposures, physical_exam, diagnostic_tests, labs, imaging, pathology_reports, final_extracted_text)
        # print(patient_details)

        diagnosis = llm_extractor.differential_diagnosis(patient_details)

        # st.write('Differential Diagnosis:')
        st.write(diagnosis)
