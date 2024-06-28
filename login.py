import sqlite3
import streamlit as st
from passlib.context import CryptContext

# Database path
DATABASE_URL = 'users.db'

# Create a password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    with sqlite3.connect(DATABASE_URL) as conn:
        c = conn.cursor()
        # Create users table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                name TEXT,
                username TEXT UNIQUE,
                password TEXT
            )
        ''')
        # Create tasks table
        c.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                username TEXT,
                title TEXT,
                time TEXT,
                date TEXT,
                done INTEGER DEFAULT 0,
                FOREIGN KEY (username) REFERENCES users (username)
            )
        ''')
        # Ensure the 'done' column exists
        c.execute('PRAGMA table_info(tasks)')
        columns = [info[1] for info in c.fetchall()]
        if 'done' not in columns:
            c.execute('ALTER TABLE tasks ADD COLUMN done INTEGER DEFAULT 0')
        conn.commit()

def add_user(name, username, password):
    try:
        with sqlite3.connect(DATABASE_URL) as conn:
            c = conn.cursor()
            hashed_password = pwd_context.hash(password)
            c.execute('INSERT INTO users (name, username, password) VALUES (?, ?, ?)',
                      (name, username, hashed_password))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username is not unique

def verify_login(username, password):
    with sqlite3.connect(DATABASE_URL) as conn:
        c = conn.cursor()
        c.execute('SELECT password, name FROM users WHERE username = ?', (username,))
        result = c.fetchone()
        if result:
            db_password_hash, name = result
            if pwd_context.verify(password, db_password_hash):
                return True, name
    return False, None

def display_signup_form():
    st.markdown("""
    <style>
    .custom-header {
        color: orange;
    }
    </style>
    <h2 class="custom-header">Sign Up for your Personal Assistant Chatbot</h2>
    """, unsafe_allow_html=True)

    with st.form("signup_form"):
        name = st.text_input("Name", key="signup_name")
        username = st.text_input("Username", key="signup_username")
        password = st.text_input("Password", type="password", key="signup_password")
        submit_button = st.form_submit_button("Sign Up")
        if submit_button:
            if len(username) <= 5 or len(password) <= 5:
                st.error("Username and password must be greater than 5 characters.")
            elif add_user(name, username, password):
                st.success("You have successfully registered!")
            else:
                st.error("This username is already taken, please choose another one.")
    if st.button("Go to Login"):
        st.session_state['page'] = 'login'
        st.experimental_rerun()

def display_login_form():
    st.markdown("""
    <style>
    .custom-header {
        color: orange;
    }
    </style>
    <h2 class="custom-header">Login to your Personal Assistant Chatbot</h2>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        login_button = st.form_submit_button("Login")
        if login_button:
            if len(username) <= 5 or len(password) <= 5:
                st.error("Username and password must be greater than 5 characters.")
            else:
                success, name = verify_login(username, password)
                if success:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.session_state['page'] = 'tasks'
                    st.experimental_rerun()
                else:
                    st.error("Username or password is incorrect.")
    if st.button("Go to Sign Up"):
        st.session_state['page'] = 'signup'
        st.experimental_rerun()



