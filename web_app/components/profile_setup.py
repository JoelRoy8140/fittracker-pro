import streamlit as st
import sqlite3
from datetime import datetime

def profile_setup_component():
    st.subheader("👤 Personal Information")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *")
            email = st.text_input("Email *")
            age = st.number_input("Age", 10, 100, 25)
            gender = st.radio("Gender", ["Male", "Female", "Other"])
            height = st.number_input("Height (cm)", 100, 250, 170)
        
        with col2:
            weight = st.number_input("Weight (kg)", 30, 200, 70)
            activity_level = st.select_slider(
                "Activity Level", 
                ["Sedentary", "Light", "Moderate", "Active", "Very Active"]
            )
            goal = st.selectbox(
                "Primary Goal",
                ["Weight Loss", "Muscle Gain", "Maintenance", "Strength", "General Fitness"]
            )
            
            diet_preferences = st.multiselect(
                "Diet Preferences",
                ["Vegetarian", "Vegan", "Keto", "Paleo", "Gluten-Free", "No Restrictions"]
            )
            
            equipment = st.multiselect(
                "Available Equipment",
                ["None", "Dumbbells", "Resistance Bands", 
                 "Pull-up Bar", "Yoga Mat", "Gym Access", "Kettlebell"]
            )
        
        submitted = st.form_submit_button("💾 Save Profile")
        
        if submitted:
            if name and email:
                # Save to database
                save_user_profile(name, email, age, gender, height, weight, 
                                activity_level, goal, diet_preferences, equipment)
                st.success("✅ Profile saved successfully!")
                st.session_state.profile_complete = True
                st.balloons()
            else:
                st.error("Please fill in all required fields (* marked)")

def save_user_profile(name, email, age, gender, height, weight, 
                     activity_level, goal, diet_preferences, equipment):
    conn = sqlite3.connect('data/users.db')
    c = conn.cursor()
    
    # Create tables if they don't exist
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, name TEXT, email TEXT,
                  age INTEGER, gender TEXT, height REAL, weight REAL,
                  activity_level TEXT, goal TEXT, diet_preferences TEXT,
                  equipment TEXT, created_at TIMESTAMP)''')
    
    c.execute('''INSERT INTO users 
                 (name, email, age, gender, height, weight,
                  activity_level, goal, diet_preferences, equipment, created_at) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (name, email, age, gender, height, weight,
               activity_level, goal, ','.join(diet_preferences), 
               ','.join(equipment), datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

def load_user_profile():
    conn = sqlite3.connect('data/users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users ORDER BY id DESC LIMIT 1")
    user = c.fetchone()
    conn.close()
    
    if user:
        return {
            'id': user[0],
            'name': user[1],
            'email': user[2],
            'age': user[3],
            'gender': user[4],
            'height': user[5],
            'weight': user[6],
            'activity_level': user[7],
            'goal': user[8],
            'diet_preferences': user[9].split(',') if user[9] else [],
            'equipment': user[10].split(',') if user[10] else []
        }
    return None
