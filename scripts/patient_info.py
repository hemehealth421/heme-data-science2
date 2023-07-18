
def create_patient_details(age, gender, race_ethnicity, symptoms, onset, duration, severity, associated_symptoms, medical_history, prior_conditions, surgeries, medications, family_history, occupation, habits, exposures, physical_exam, diagnostic_tests, labs, imaging, pathology_reports, final_extracted_text):
    patient_details_list = []

    if age > 0:
        patient_details_list.append(f"Age: {age}")

    if gender != '-':
        patient_details_list.append(f"Gender: {gender}")

    if race_ethnicity != '-':
        patient_details_list.append(f"Race/Ethnicity: {race_ethnicity}")

    if symptoms:
        patient_details_list.append(f"Symptoms: {symptoms}")

    if onset:
        patient_details_list.append(f"Onset of Symptoms: {onset}")

    if duration:
        patient_details_list.append(f"Duration of Symptoms: {duration}")

    if severity:
        patient_details_list.append(f"Severity of Symptoms: {severity}")

    if associated_symptoms:
        patient_details_list.append(f"Associated Symptoms: {associated_symptoms}")

    if medical_history:
        patient_details_list.append(f"Medical History: {medical_history}")

    if prior_conditions:
        patient_details_list.append(f"Prior Conditions: {prior_conditions}")

    if surgeries:
        patient_details_list.append(f"Surgeries: {surgeries}")

    if medications:
        patient_details_list.append(f"Current Medications: {medications}")

    if family_history:
        patient_details_list.append(f"Family History: {family_history}")

    if occupation:
        patient_details_list.append(f"Occupation: {occupation}")

    if habits:
        patient_details_list.append(f"Habits: {habits}")

    if exposures:
        patient_details_list.append(f"Exposures: {exposures}")

    if physical_exam:
        patient_details_list.append(f"Physical Examination Details: {physical_exam}")

    if diagnostic_tests:
        patient_details_list.append(f"Diagnostic Tests Details: {diagnostic_tests}")

    if labs:
        patient_details_list.append(f"Lab Results: {labs}")

    if imaging:
        patient_details_list.append(f"Imaging Results: {imaging}")

    if pathology_reports:
        patient_details_list.append(f"Pathology Reports: {pathology_reports}")

    if final_extracted_text:
        patient_details_list.append(f"Uploaded Medical Documents: {final_extracted_text}")

    # Convert the list to a string for the final patient_details
    patient_details = "\n".join(patient_details_list)

    patient_details = f"patient_details: {patient_details}"

    return patient_details





