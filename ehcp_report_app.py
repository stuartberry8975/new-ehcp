import streamlit as st
import pandas as pd
import datetime
import pdfplumber
import docx
from io import StringIO

def load_data(uploaded_file):
    """Load CSV, Excel, PDF, or Word file into a DataFrame."""
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                return pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                return pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.pdf'):
                return extract_text_from_pdf(uploaded_file)
            elif uploaded_file.name.endswith('.docx'):
                return extract_text_from_word(uploaded_file)
        except Exception as e:
            st.error(f"Error loading file: {e}")
            return None

def extract_text_from_pdf(uploaded_file):
    """Extract text from PDFs, including scanned documents."""
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:  # Prevents NoneType errors
                text += extracted_text + "\n"
    return pd.DataFrame({'Extracted Text': [text]})

def extract_text_from_word(uploaded_file):
    """Extract text from Word files."""
    doc = docx.Document(uploaded_file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return pd.DataFrame({'Extracted Text': [text]})

def generate_report(student_data, feedback_data, comparison_data):
    """Generate EHCP review report for each student."""
    report_date = datetime.date.today().strftime("%Y-%m-%d")
    reports = []
    
    for _, student in student_data.iterrows():
        student_name = student.get('Name', 'Unknown Student')
        ehcp_targets = student.get('EHCP Targets', 'No targets provided')
        feedback = feedback_data if not feedback_data.empty else pd.DataFrame({'Extracted Text': ["No feedback available."]})
        grades = comparison_data if not comparison_data.empty else pd.DataFrame({'Extracted Text': ["No grade data available."]})
        
        feedback_summary = '\n'.join(feedback['Extracted Text'])
        key_challenges = ', '.join(feedback['Extracted Text'].dropna().unique()) if not feedback.empty else "No key challenges noted."
        suggested_targets = ', '.join(feedback['Extracted Text'].dropna().unique()) if not feedback.empty else "No targets suggested."
        
        grade_comparison = '\n'.join(grades['Extracted Text']) if not grades.empty else "No grade data available."
        
        report_text = f"""
        **EHCP Review Meeting – {report_date}**
        
        **Student Name:** {student_name}
        
        **EHCP Targets:**
        {ehcp_targets}
        
        **Teacher Feedback:**
        {feedback_summary}
        
        **Key Challenges:**
        {key_challenges}
        
        **Suggested Future Targets:**
        {suggested_targets}
        
        **Grade Comparison:**
        {grade_comparison}
        """
        reports.append(report_text)
    
    return reports

st.title("EHCP Review Report Generator")

student_file = st.file_uploader("Upload Student Data (CSV/Excel/PDF/DOCX)", type=["csv", "xlsx", "pdf", "docx"])
feedback_file = st.file_uploader("Upload Teacher Feedback (CSV/Excel/PDF/DOCX)", type=["csv", "xlsx", "pdf", "docx"])
grades_file = st.file_uploader("Upload Grade Data (CSV/Excel/PDF/DOCX)", type=["csv", "xlsx", "pdf", "docx"])

if st.button("Generate Report"):
    if student_file and feedback_file and grades_file:
        student_data = load_data(student_file)
        feedback_data = load_data(feedback_file)
        comparison_data = load_data(grades_file)
        
        if student_data is not None and feedback_data is not None and comparison_data is not None:
            reports = generate_report(student_data, feedback_data, comparison_data)
            for report in reports:
                st.text_area("Generated Report", report, height=300)
    else:
        st.error("Please upload all required files.")
