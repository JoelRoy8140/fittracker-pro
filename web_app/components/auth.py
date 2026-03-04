# web_app/components/auth.py
import streamlit as st
import bcrypt
from web_app.database import create_user, verify_user, get_user_by_username

def auth_component():
    """
    Renders login and registration tabs. 
    Returns True if user successfully logged in or registered, False otherwise.
    Sets st.session_state['user'] upon success.
    """
    st.title("🏋️‍♂️ Welcome to FitTracker Pro")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login to your account")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if not username or not password:
                    st.error("Please enter both username and password.")
                else:
                    user = verify_user(username, password)
                    if user:
                        st.session_state['user'] = user
                        st.success(f"Welcome back, {user['name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
                        
    with tab2:
        st.subheader("Create a new account")
        with st.form("register_form"):
            new_name = st.text_input("Full Name")
            new_username = st.text_input("Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            submitted = st.form_submit_button("Register")
            
            if submitted:
                if not new_name or not new_username or not new_email or not new_password:
                    st.error("Please fill in all fields.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif get_user_by_username(new_username):
                    st.error("Username already exists. Please choose another.")
                else:
                    # Hash the password
                    salt = bcrypt.gensalt()
                    password_hash = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
                    
                    # Create basic user payload for the DB
                    new_user_data = {
                        "username": new_username,
                        "password_hash": password_hash,
                        "name": new_name,
                        "email": new_email,
                        "age": 25, # defaults that will be updated in profile setup
                        "gender": "Not Specified",
                        "height": 0.0,
                        "weight": 0.0,
                        "activity_level": "Beginner",
                        "goal": "General",
                        "diet_preferences": [],
                        "equipment": []
                    }
                    
                    try:
                        create_user(new_user_data)
                        st.success("Account created successfully! Please login.")
                    except Exception as e:
                        st.error(f"Error creating account: {e}")
    
    return False
