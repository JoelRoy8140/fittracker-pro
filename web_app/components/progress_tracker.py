import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sqlite3
from datetime import datetime, timedelta

def progress_tracker_component():
    st.subheader("📈 Progress Tracking Dashboard")
    
    # Load user data
    user_profile = load_user_profile()
    if not user_profile:
        st.warning("Please complete your profile first!")
        return
    
    # Load measurements data
    measurements_df = load_measurements_data(user_profile['id'])
    
    if measurements_df.empty:
        st.info("No measurements recorded yet. Start scanning to track your progress!")
        return
    
    # Display summary cards
    display_progress_summary(measurements_df, user_profile)
    
    # Display charts
    display_progress_charts(measurements_df)
    
    # Display measurement history
    display_measurement_history(measurements_df)

def load_user_profile():
    """Load user profile from database"""
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
            'goal': user[8]
        }
    return None

def load_measurements_data(user_id):
    """Load measurements data from database"""
    conn = sqlite3.connect('data/users.db')
    query = "SELECT * FROM measurements WHERE user_id = ? ORDER BY date DESC"
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    return df

def display_progress_summary(measurements_df, user_profile):
    """Display progress summary cards"""
    latest = measurements_df.iloc[0]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Latest BMI", f"{latest['bmi']:.1f}", 
                 delta=f"{latest['bmi'] - measurements_df.iloc[-1]['bmi']:.1f}" if len(measurements_df) > 1 else None)
    
    with col2:
        st.metric("Body Fat %", f"{latest['body_fat']:.1f}%", 
                 delta=f"{latest['body_fat'] - measurements_df.iloc[-1]['body_fat']:.1f}%" if len(measurements_df) > 1 else None)
    
    with col3:
        st.metric("Weight", f"{latest['weight']:.1f} kg", 
                 delta=f"{latest['weight'] - measurements_df.iloc[-1]['weight']:.1f} kg" if len(measurements_df) > 1 else None)
    
    with col4:
        # Calculate trend
        if len(measurements_df) > 1:
            trend = "📉 Improving" if latest['bmi'] < measurements_df.iloc[-1]['bmi'] else "📈 Need Attention"
        else:
            trend = "📊 New"
        st.metric("Trend", trend)

def display_progress_charts(measurements_df):
    """Display progress charts"""
    st.subheader("📊 Progress Over Time")
    
    # Convert date column to datetime
    measurements_df['date'] = pd.to_datetime(measurements_df['date'])
    
    # BMI and Body Fat Chart
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=measurements_df['date'], y=measurements_df['bmi'], 
                             mode='lines+markers', name='BMI', line=dict(color='blue')))
    fig1.add_trace(go.Scatter(x=measurements_df['date'], y=measurements_df['body_fat'], 
                             mode='lines+markers', name='Body Fat %', line=dict(color='red')))
    fig1.update_layout(title="BMI & Body Fat Trend", 
                      xaxis_title="Date", 
                      yaxis_title="Values")
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # Weight Chart
    fig2 = px.line(measurements_df, x='date', y='weight', 
                   title='Weight Progress', 
                   markers=True)
    fig2.update_layout(yaxis_title="Weight (kg)")
    
    st.plotly_chart(fig2, use_container_width=True)

def display_measurement_history(measurements_df):
    """Display measurement history table"""
    st.subheader("📋 Measurement History")
    
    # Format the dataframe for display
    display_df = measurements_df[['date', 'bmi', 'body_fat', 'weight']].copy()
    display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d %H:%M')
    
    st.dataframe(display_df.style.format({
        'bmi': '{:.1f}',
        'body_fat': '{:.1f}%',
        'weight': '{:.1f} kg'
    }))

def calculate_goals_progress(user_profile, measurements_df):
    """Calculate progress towards user goals"""
    if measurements_df.empty:
        return None
    
    latest = measurements_df.iloc[0]
    goal = user_profile.get('goal', '')
    
    progress_data = {}
    
    if 'Weight Loss' in goal:
        # Assuming ideal BMI is 22
        ideal_weight = 22 * (user_profile['height']/100)**2
        current_weight = latest['weight']
        progress_data['weight_loss_goal'] = {
            'current': current_weight,
            'target': ideal_weight,
            'progress': ((current_weight - ideal_weight) / (user_profile['weight'] - ideal_weight)) * 100
        }
    
    return progress_data
