import streamlit as st
from login import display_login_form, display_signup_form, init_db
from tasks import display_tasks
from chatbot import display_chatbot

def main():
    init_db()
    
    # Initialize session state variables if not already done
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'page' not in st.session_state:
        st.session_state['page'] = 'login'

    # Main content
    if st.session_state['logged_in']:
        if st.session_state['page'] == 'tasks':
            display_tasks(st.session_state['username'], st)
        elif st.session_state['page'] == 'chatbot':
            display_chatbot()
    else:
        if st.session_state['page'] == 'login':
            display_login_form()
        elif st.session_state['page'] == 'signup':
            display_signup_form()

if __name__ == "__main__":
    main()
