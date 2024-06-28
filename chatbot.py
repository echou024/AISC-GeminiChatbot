from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
import google.generativeai as genai

# Load environment variables from .env
load_dotenv()

# Configure API key for Google's generative AI service
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get response from the appropriate Gemini model, depending on input type
def get_gemini_response(input_text, image=None):
    if image:
        model = genai.GenerativeModel('gemini-pro-vision')
        response = model.generate_content([input_text, image])
    else:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(input_text)
    return response.text

def display_chatbot():
    st.set_page_config(page_title="Chatbot")

    # Custom CSS to inject into the webpage to style the header
    st.markdown("""
    <style>
    .custom-header {
        color: orange;
    }
    </style>
    <h1 class="custom-header">Chatbot</h1>
    """, unsafe_allow_html=True)

    # Navigation buttons
    col1, col2 = st.columns([0.5, 0.5])
    with col1:
        if st.button('Logout'):
            st.session_state['logged_in'] = False
            st.session_state.pop('username', None)
            st.session_state['page'] = 'login'
            st.experimental_rerun()
    with col2:
        if st.button('Tasks Dashboard'):
            st.session_state['page'] = 'tasks'
            st.experimental_rerun()

    # User input for text
    input_text = st.text_input("How can I help you?", on_change=None, placeholder="Type here and press 'Get Response' ")

    # Optional image upload
    uploaded_file = st.file_uploader("Optionally, upload an image (jpg, jpeg, png):", type=["jpg", "jpeg", "png"])
    image = None
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image.", use_column_width=True)

    # Button to submit query
    submit = st.button("Get Response")

    # Process the query when the button is clicked
    if submit:
        response = get_gemini_response(input_text, image)
        st.subheader("The Response is")
        st.write(response)
