import streamlit as st
import google.generativeai as genai
import os
import tempfile
from PyPDF2 import PdfReader
from PIL import Image
import io

# Configure Gemini API
GOOGLE_API_KEY=st.secrets['GOOGLE_API_KEY']
genai.configure(api_key=GOOGLE_API_KEY)

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_images_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    images = []
    for page in reader.pages:
        for image in page.images:
            img = Image.open(io.BytesIO(image.data))
            images.append(img)
    return images

def summarize_pdf(text, images):
    model = genai.GenerativeModel('gemini-1.5-pro')
    prompt = f"Summarize the following PDF content, including any relevant information from images:\n\n{text}"
    response = model.generate_content([prompt] + images)
    return response.text

def chat_with_pdf(text, images, user_query):
    model = genai.GenerativeModel('gemini-1.5-pro')
    prompt = f"Given the following PDF content and user query, provide a relevant response:\n\nPDF Content:\n{text}\n\nUser Query: {user_query}"
    response = model.generate_content([prompt] + images)
    return response.text

st.title("PDF Analyzer and Chatbot")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    text = extract_text_from_pdf(tmp_file_path)
    images = extract_images_from_pdf(tmp_file_path)

    st.subheader("PDF Summary")
    summary = summarize_pdf(text, images)
    st.write(summary)

    st.subheader("Chat with PDF")
    user_query = st.text_input("Ask a question about the PDF:")
    if user_query:
        response = chat_with_pdf(text, images, user_query)
        st.write("Response:", response)

    os.unlink(tmp_file_path)