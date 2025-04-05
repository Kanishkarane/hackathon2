import streamlit as st
import json
import os
import pandas as pd
import random
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(
    page_title="AI Travel Magic - Itinerary & Trip Trailer Generator",
    page_icon="✈️",
    layout="wide"
)

# App styling
st.markdown("""
<style>
    .main {
        background-color: #f5f7f9;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    h1, h2, h3 {
        color: #1e3a8a;
    }
    .stButton button {
        background-color: #3b82f6;
        color: white;
        font-weight: bold;
    }
    .highlight-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #dbeafe;
        margin-bottom: 20px;
    }
    .cinematic-text {
        font-family: Georgia, serif;
        line-height: 1.6;
        font-size: 18px;
        color: #1f2937;
        padding: 25px;
        border-radius: 10px;
        background-color: #f8fafc;
        border-left: 5px solid #3b82f6;
        margin: 20px 0;
    }
    /* Improved styling for itinerary display */
    .itinerary-container ul {
        margin-top: 0.5rem;
        padding-left: 1.5rem;
    }
    .itinerary-container li {
        margin-bottom: 0.5rem;
    }
    .itinerary-container h2 {
        margin-top: 1.5rem;
        border-bottom: 2px solid #3b82f6;
        padding-bottom: 0.5rem;
    }
    .itinerary-container h3 {
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        color: #4b5563;
    }
    .itinerary-container blockquote {
        background-color: #f0f9ff;
        border-left: 4px solid #3b82f6;
        padding: 0.5rem 1rem;
        margin: 1rem 0;
    }
    .budget-indicator {
        color: #4b5563;
        font-size: 0.9rem;
    }
    /* Calendar Styling */
    .calendar-container {
        background-color: #f0f9ff;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        border: 1px solid #d1d5db;
    }
    .calendar-container h4 {
        color: #3b82f6;
        margin-top: 0;
        margin-bottom: 10px;
    }
    .date-display {
        font-weight: bold;
        color: #1e3a8a;
        margin-top: 5px;
    }
    /* Weather display styling */
    .weather-indicator {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        margin-left: 8px;
        background-color: #e0f2fe;
        color: #0369a1;
    }
    .weather-section {
        background-color: #f0f9ff;
        border-left: 4px solid #38bdf8;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0 1rem 0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'itinerary' not in st.session_state:
    st.session_state.itinerary = None
if 'cinematic_trailer' not in st.session_state:
    st.session_state.cinematic_trailer = None
if 'video_path' not in st.session_state:
    st.session_state.video_path = None
if 'llm_model' not in st.session_state:
    st.session_state.llm_model = None
if 'llm_tokenizer' not in st.session_state:
    st.session_state.llm_tokenizer = None
if 'weather_model' not in st.session_state:
    st.session_state.weather_model = None
if 'weather_tokenizer' not in st.session_state:
    st.session_state.weather_tokenizer = None
if 'llm_loading_attempted' not in st.session_state:
    st.session_state.llm_loading_attempted = False
if 'weather_model_loaded' not in st.session_state:
    st.session_state.weather_model_loaded = False
if 'destination_details' not in st.session_state:
    st.session_state.destination_details = {}
if 'weather_cache' not in st.session_state:
    st.session_state.weather_cache = {}
if 'start_date' not in st.session_state:
    st.session_state.start_date = datetime.now().date()
if 'end_date' not in st.session_state:
    # Default to a week after start date
    st.session_state.end_date = (datetime.now() + timedelta(days=7)).date()
if 'destination' not in st.session_state:
    st.session_state.destination = ""
if 'budget' not in st.session_state:
    st.session_state.budget = "Medium"
if 'trip_purpose' not in st.session_state:
    st.session_state.trip_purpose = ""
if 'preferences' not in st.session_state:
    st.session_state.preferences = []
if 'season' not in st.session_state:
    st.session_state.season = "Summer"

# Simplified mock LLM model function
def load_llm_model():
    st.warning("Using simplified text generation. Actual AI model is not available.")
    return None, None

# Welcome page content
st.title("✈️ AI Travel Magic")
st.markdown("### Your personal travel itinerary & trip trailer generator")

# Hero section with welcome message
st.markdown("""
<div class="highlight-box">
    <h2>Welcome to AI Travel Magic!</h2>
    <p>Plan your perfect trip with our AI-powered travel assistant. We'll help you create a personalized itinerary and a cinematic trip trailer to get you excited about your upcoming adventure.</p>
    <p>Just tell us where you want to go, what you like to do, and when you're traveling - we'll handle the rest!</p>
</div>
""", unsafe_allow_html=True)

# Key features
st.markdown("## ✨ What You Can Do")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📍 Destination Planner")
    st.markdown("Select your dream destination and budget to start planning your perfect trip.")

with col2:
    st.markdown("### 🧭 Personalized Itinerary")
    st.markdown("Get a day-by-day travel plan tailored to your interests and preferences.")

with col3:
    st.markdown("### 🎬 Trip Trailer")
    st.markdown("Generate a cinematic preview of your journey to share with friends and family.")

# User guidance
st.markdown("## 🚀 Getting Started")
st.markdown("""
1. **Tell us where you're going** - Choose your destination and budget
2. **Share your interests** - Select activities and trip purpose
3. **Pick your dates** - Select travel dates and see weather predictions
4. **Generate itinerary** - Get your personalized travel plan
5. **Create trip trailer** - Generate a visual preview of your adventure
""")

# Load models in background if not already attempted
if not st.session_state.llm_loading_attempted:
    st.session_state.llm_loading_attempted = True
    with st.spinner("Setting up AI models (this may take a moment)..."):
        st.session_state.llm_model, st.session_state.llm_tokenizer = load_llm_model()
        st.session_state.weather_model, st.session_state.weather_tokenizer = load_llm_model()  # Reusing same model

# CTA Button
st.markdown("### Ready to plan your adventure?")
if st.button("Start Planning Your Trip", key="start_button", use_container_width=True):
    # Navigate to the first page
    st.switch_page("pages/01_Destination_and_Budget.py")
