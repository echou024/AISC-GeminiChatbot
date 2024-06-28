import sqlite3
import streamlit as st
from datetime import datetime

# You might need to pass the DATABASE_URL or import from a config file or environment
DATABASE_URL = 'users.db'  # Ensure this aligns with your settings

def add_task(username, title, time, period, date, db_path=DATABASE_URL):
    # Combine time and period to form the complete time
    time_with_period = f"{time} {period}"
    # Convert date to month, day, year format
    formatted_date = date.strftime("%B %d, %Y")

    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO tasks (username, title, time, date, done) VALUES (?, ?, ?, ?, ?)',
                  (username, title, time_with_period, formatted_date, 0))
        conn.commit()
    # After adding, fetch and print all tasks to check
    c.execute('SELECT * FROM tasks WHERE username = ?', (username,))
    tasks = c.fetchall()
    print("Current tasks:", tasks)  # This will print to the console running Streamlit

def get_tasks(username, db_path=DATABASE_URL):
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        # Retrieve tasks without sorting
        c.execute('SELECT id, title, time, date, done FROM tasks WHERE username = ?', (username,))
        return c.fetchall()

def delete_task(task_id, db_path=DATABASE_URL):
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()

def update_task_done(task_id, done, db_path=DATABASE_URL):
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('UPDATE tasks SET done = ? WHERE id = ?', (done, task_id))
        conn.commit()

def order_tasks(tasks):
    # Convert date and time strings to datetime objects for sorting
    ordered_tasks = sorted(tasks, key=lambda task: (datetime.strptime(task[3], "%B %d, %Y"), datetime.strptime(task[2], "%I:%M %p")))
    return ordered_tasks

def display_tasks(username, st):
    # Place a logout button and chatbot button at the top of the page
    col1, col2 = st.columns([0.5, 0.5])
    with col1:
        if st.button('Logout'):
            # Reset session states related to user session
            st.session_state['logged_in'] = False
            st.session_state.pop('username', None)  # Safely remove 'username' if exists
            st.session_state['page'] = 'login'  # Set mode to login to redirect user
            st.experimental_rerun()  # Rerun the app to reflect changes immediately
    with col2:
        if st.button('Chatbot'):
            st.session_state['page'] = 'chatbot'
            st.experimental_rerun()

    st.markdown("""
    <style>
    .custom-header {
        color: orange;
    }
    .task-box {
        border: 2px solid #f0f0f0;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
    }
    .checkbox {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: 10px; /* Adjust this value to move the checkbox lower */
    }
    /* Additional styling to hide automatically injected label by Streamlit */
    .checkbox label {
        visibility: hidden;  /* Hide the label text */
    }
    .checkbox div {
        background-color: transparent !important; /* Ensures no background color */
    }
    </style>
    <h1 class="custom-header">Welcome to your Tasks Dashboard!</h1>
    """, unsafe_allow_html=True)

    st.write("Double-click a task to delete it.")

    tasks = get_tasks(username)
    ordered_tasks = order_tasks(tasks)
    if not ordered_tasks:
        st.write("No tasks found.")
    else:
        for task in ordered_tasks:
            task_id = task[0]
            task_title = f"**{task[1]}**  (Due: {task[2]}, {task[3]})"
            task_done = task[4]

            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                if st.button(task_title, key=f"task_{task_id}"):
                    if f"task_{task_id}_clicked" not in st.session_state:
                        st.session_state[f"task_{task_id}_clicked"] = 0
                    st.session_state[f"task_{task_id}_clicked"] += 1

                    if st.session_state[f"task_{task_id}_clicked"] == 2:
                        st.session_state[f"task_{task_id}_confirm"] = True
                        st.session_state[f"task_{task_id}_clicked"] = 0  # Reset click count

                if st.session_state.get(f"task_{task_id}_confirm", False):
                    st.write(f"Delete this task?")
                    col3, col4 = st.columns(2)
                    with col3:
                        if st.button("Yes", key=f"yes_{task_id}"):
                            delete_task(task_id)
                            st.session_state.pop(f"task_{task_id}_confirm")
                            st.experimental_rerun()
                    with col4:
                        if st.button("No", key=f"no_{task_id}"):
                            st.session_state.pop(f"task_{task_id}_confirm")
                            st.experimental_rerun()

            with col2:
                st.markdown("<div class='checkbox'>", unsafe_allow_html=True)
                if st.checkbox("", key=f"done_{task_id}", value=task_done, help="Mark as done"):
                    with sqlite3.connect(DATABASE_URL) as conn:
                        c = conn.cursor()
                        new_done_value = 1 if not task_done else 0
                        c.execute('UPDATE tasks SET done = ? WHERE id = ?', (new_done_value, task_id))
                        conn.commit()
                    st.experimental_rerun()  # Refresh the page to reflect changes
                st.markdown("</div>", unsafe_allow_html=True)

    with st.form("task_form"):
        title = st.text_input("Task title")
        time = st.text_input("Task time (e.g., 02:30)", placeholder="HH:MM")
        period = st.selectbox("AM/PM", ["AM", "PM"])
        date = st.date_input("Task due date")
        formatted_date = date.strftime("%m-%d-%Y")  # Format the date as MM-DD-YYYY in the entry box
        st.write(f"Selected date: {formatted_date}")
        submit_task = st.form_submit_button("Add Task")

        if submit_task:
            # Validate time input
            try:
                datetime.strptime(time, "%I:%M")
                add_task(username, title, time, period, date)
                st.experimental_rerun()
            except ValueError:
                st.error("Please enter a valid time in HH:MM format.")
