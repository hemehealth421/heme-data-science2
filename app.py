import streamlit as st
from streamlit_chat import message as smessage
import boto3
from botocore.exceptions import NoCredentialsError
from scripts.ocr import TextractExtractor,PDFMinerExtractor
from scripts.info_extraction import LLMExtractor
from scripts.vertexai_llm import *
from scripts.output_format import *
from scripts.patient_info import create_patient_details
from scripts.chat_gpt_llm import hemebot_chatgpt_response, get_key_insights, hemebot_chatgpt_response1
# from scripts.hemebot_prompts import *
from scripts.chat_gpt_llm import hemebot_chatgpt_response2,hemebot_chatgpt_response3


ds_bucket_name = "attributes-extraction-heme"

def upload_file_to_s3(file, bucket_name):
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_fileobj(file, bucket_name, file.name)
    except NoCredentialsError:
        st.error("AWS credentials not found.")
    except Exception as e:
        st.error(f"Error uploading file to S3: {str(e)}")



# Define the structure of each section
def patient_demographics_section():
    st.header('👤 Patient Demographics')
    patient_demographics = dict()
    patient_demographics["age"] = st.number_input('Enter your Age (Optional)', min_value=0, max_value=120, step=1, value=0)
    patient_demographics["gender"] = st.selectbox('Select your Gender (Optional)', ['-', 'Male', 'Female', 'Other'])
    patient_demographics["race_ethnicity"] = st.selectbox('Select your Race/Ethnicity (Optional)', ['-', 'African', 'Middle Eastern', 'Indian', 'Hispanic', 'Mediterranean', 'Caucasian', 'Northern European', 'African American', 'Native American', 'Asian American', 'Ashkenazi Jewish', 'Italian', 'Greek', 'Asian', 'Turkish', 'Other'])
    return patient_demographics
     


def symptoms_section():
    st.header('🌡️ Symptoms')
    patient_symptoms = dict()
    patient_symptoms["symptoms"] = st.text_area('Enter your symptoms (Optional)', '')
    
    return patient_symptoms

def detailed_symptom_section():
    st.subheader('🔍 Detailed Symptom Information')
    detailed_symptom = dict()
    with st.expander('Detailed Symptom Information'):
        detailed_symptom["onset"] = st.text_input('Enter the onset of your symptoms (Optional)', '')
        detailed_symptom["duration"] = st.text_input('Enter the duration of your symptoms (Optional)', '')
        detailed_symptom["severity"] = st.text_input('Enter the severity of your symptoms (Optional)', '')
        detailed_symptom["associated_symptoms"] = st.text_area('Enter any associated symptoms (Optional)', '')
    return detailed_symptom

def medical_family_history_section():
    st.header('📚 Medical and Family History')
    medical_family_history = dict()
    with st.expander('Medical and Family History'):
        medical_family_history["medical_history"] = st.text_area('Enter your medical history details (Optional)', '')
        medical_family_history["prior_conditions"] = st.text_area('Enter your prior conditions (Optional)', '')
        medical_family_history["surgeries"] = st.text_area('Enter any surgeries you have had (Optional)', '')
        medical_family_history["medications"] = st.text_area('Enter any medications you are currently taking (Optional)', '')
        medical_family_history["family_history"] = st.text_area('Enter your family medical history details (Optional)', '')
    return medical_family_history

def social_history_section():
    st.header('🧑‍💼 Social History')
    social_history = dict()
    with st.expander('Social History'):
        social_history["occupation"] = st.text_input('Enter your occupation (Optional)', '')
        social_history["habits"] = st.text_area('Enter any habits (Optional)', '')
        social_history["exposures"] = st.text_area('Enter any significant exposures (Optional)', '')
    return social_history

def physical_exam_section():
    st.header('🔎 Physical Exam Findings')
    physical_exam_data = dict()
    with st.expander('Physical Exam Findings'):
        physical_exam_data["physical_exam"] = st.text_area('Enter your physical examination details (Optional)', '')
    return physical_exam_data

def diagnostic_tests_section():
    st.header('🔬 Diagnostic Tests')
    diagnostic_tests_data = dict()
    with st.expander('Diagnostic Tests'):
        diagnostic_tests_data["diagnostic_tests"] = st.text_area('Enter your diagnostic tests details (Optional)', '')
        diagnostic_tests_data["labs"] = st.text_area('Enter your lab results (Optional)', '')
        diagnostic_tests_data["imaging"] = st.text_area('Enter any imaging results (Optional)', '')
        diagnostic_tests_data["pathology_reports"] = st.text_area('Enter any pathology reports (Optional)', '')
    return diagnostic_tests_data

def doctors_note_section():
    doctor_input = st.text_input('Add Doctors Note (Optional)', value=st.session_state.doctors_note)
    st.session_state.doctors_note = doctor_input  # Save the value to st.session_state

    doctor_input = f"Doctor Note: {doctor_input}"
    return doctor_input





def upload_documents_section(uploaded_files):
    if not uploaded_files:
        return ""

    text_extractor = TextractExtractor()
    pdfminer_extractor = PDFMinerExtractor()

    final_extracted_text = ""

    # Progress bar setup
    progress_bar = st.progress(0)

    for index, uploaded_file in enumerate(uploaded_files):
        try:
            # Feedback: Showing which file is being uploaded
            with st.spinner(f"📤 Uploading **{uploaded_file.name}**"):
                upload_file_to_s3(uploaded_file, ds_bucket_name)

            # Provide feedback that file uploaded successfully
            st.success(f'Successfully uploaded **{uploaded_file.name}**')

            # Extracting text based on file type
            with st.spinner(f"📄 Extracting information from **{uploaded_file.name}**"):
                extracted_text = ""  # Initialize with None
                
                if uploaded_file.name.lower().endswith('.pdf'):
                    extracted_text = pdfminer_extractor.extract_text(ds_bucket_name, uploaded_file.name)

                # Use text_extractor if file is not PDF or if no text is extracted from PDF
                if not extracted_text:
                    extracted_text = text_extractor.get_raw_text_list(ds_bucket_name, uploaded_file.name)

                final_extracted_text += f"\n{extracted_text}"

            # Provide individual feedback for each file's text extraction
            st.success(f'Successfully extracted information from **{uploaded_file.name}**')

        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
            continue  # Move on to the next file

        finally:
            # Always update the progress bar, whether there was an error or not
            progress_bar.progress((index + 1) / len(uploaded_files))

    if not final_extracted_text:
        st.warning('No text was extracted. Please check the uploaded files.')

    return final_extracted_text




    


def select_language_model():
    st.header('🧠 Select Language Model')
    
    llm_options = ["OpenAI", "Anthropic", "VertexAI"]
    selected_llm = st.selectbox("LLM choice", llm_options)
    
    return selected_llm



# Initial setup for session state
if "page" not in st.session_state:
    st.session_state.page = "home"

if "history" not in st.session_state:
    st.session_state.history = []

if 'input_text' not in st.session_state:
    st.session_state.input_text = ''

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": MY_HEMEBOT_PROMPT},
    ]


if "doctors_note" not in st.session_state:
    st.session_state.doctors_note = ''


# Main page layout and logic
def home_page():
    st.title('🩺 Virtual Doctor')
    st.markdown("---")

    
  # Get data from the sections
    demographics = patient_demographics_section()
    symptoms_data = symptoms_section()
    detailed_symptoms = detailed_symptom_section()
    medical_history_data = medical_family_history_section()
    social_history_data = social_history_section()
    physical_exam_data = physical_exam_section()
    diagnostic_tests_data = diagnostic_tests_section()

    combined_data = {**demographics, **symptoms_data, **detailed_symptoms, **medical_history_data, **social_history_data, **physical_exam_data, **diagnostic_tests_data}

    cleaned_data = {k: v for k, v in combined_data.items() if v and v not in [0, '-']}

    language_model = select_language_model()
    
    st.header('📁 Upload Documents')
    uploaded_files = st.file_uploader('Choose a file (Optional)', type=["pdf", "png", "jpg", "jpeg", "txt"], accept_multiple_files=True)


    # If the 'Analyze' button is clicked, it'll run whatever analysis you have set up.
    st.markdown("---")
    st.header('⚙️ Process Health Details')


    if st.button('🔄 Process'):

        uploaded_documents = upload_documents_section(uploaded_files)
        patient_details = f"{cleaned_data}\n{uploaded_documents}"

        with st.spinner('**🩺 AI consultation in progress...**'):
            llm_extractor = LLMExtractor(language_model)
            diagnosis = llm_extractor.differential_diagnosis(patient_details)
            st.write(diagnosis)

        st.markdown("---")

        with st.spinner('**📡 Sending details to hemebot...**'):
            response_text = get_key_insights(patient_details)
            key_insights = f"{response_text}\n\n{diagnosis}"

            st.session_state.messages.append({"role": "user", "content": key_insights})
            st.chat_message("user").write(key_insights)

        with st.spinner('**🤖 Getting hemebot response...**'):
            initial_bot_response = hemebot_chatgpt_response2(st.session_state.messages)
            msg = initial_bot_response.choices[0].message

        # Add the bot's response to the messages list and display it
            st.session_state.messages.append(msg)
            st.chat_message("assistant").write(msg.content)

            # st.session_state.history.append({"message": key_insights, "is_user": True})
            # st.session_state.history.append({"message": initial_bot_response, "is_user": False})

    

    # If the 'Chat with HemeBot' button is clicked, the session state for the page is changed to "chat".
    st.markdown("---")
    st.write("*(Double click on 'Chat with 🤖 HemeBot')*")
    if st.button('Chat with 🤖 HemeBot'):
        st.session_state.page = "chat"
    st.markdown("---")
    

def chat_page():
    st.title('🤖 HemeBot')  # This will ensure title remains at the top
    st.markdown("---")

    # Display chat history before the input box
    # Display chat history
    for msg in st.session_state.messages:
        if msg["role"] != "system":  # Only display non-system messages
            st.chat_message(msg["role"]).write(msg["content"])

    # User chat input
    user_input = st.chat_input()

    if user_input:
        with st.spinner('🤖 Bot is typing...'):
            # Add the user's message to the messages list
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Display the user's message in the chat interface
            st.chat_message("user").write(user_input)
            
            # Fetch the bot's response
            response = hemebot_chatgpt_response2(st.session_state.messages)
            msg = response.choices[0].message

        # Add the bot's response to the messages list and display it
        st.session_state.messages.append(msg)
        st.chat_message("assistant").write(msg.content)
    
   # Sidebar for Doctor's note and 'Process' button
    st.sidebar.header('Doctor Note')
    doctor_input = st.sidebar.text_input('Add Doctors Note (Optional)')

    if st.sidebar.button('🔄 Process'):
        data_to_process = f"{st.session_state.messages}\n\n{doctor_input}"

        # if doctor_input:
        processing_text = st.sidebar.text('⚙️ Processing...')
        response = hemebot_chatgpt_response3(data_to_process)
        summary = get_key_insights(data_to_process)
        processing_text.empty()  # This removes the "Processing" text
        st.sidebar.subheader("AI Response💡")
        st.sidebar.write(f"{summary}\n\n🧠 : {response}")








# Main page rendering based on session state
if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "chat":
    chat_page()
# elif st.session_state.page == "doctor_chat":
#     doctor_chat()

