import streamlit as st
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(
    page_title="Destination & Budget - AI Travel Magic",
    page_icon="✈️",
    layout="wide"
)

# Initialize session state variables if not already done
if 'destination' not in st.session_state:
    st.session_state.destination = ""
if 'budget' not in st.session_state:
    st.session_state.budget = "Medium"
if 'trip_purpose' not in st.session_state:
    st.session_state.trip_purpose = ""
if 'preferences' not in st.session_state:
    st.session_state.preferences = []
if 'season' not in st.session_state:
    current_month = datetime.now().month
    if 3 <= current_month <= 5:
        st.session_state.season = "Spring"
    elif 6 <= current_month <= 8:
        st.session_state.season = "Summer"
    elif 9 <= current_month <= 11:
        st.session_state.season = "Fall"
    else:
        st.session_state.season = "Winter"

# Title and description
st.title("✈️ Where to Next?")
st.markdown("### Let's start planning your dream trip!")

st.markdown("""
<div class="highlight-box">
    <p>First, tell us where you want to go and your budget range. This will help us create a personalized itinerary that matches your expectations.</p>
</div>
""", unsafe_allow_html=True)

# Create two columns for destination and budget
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("### Destination")
    st.markdown("Where would you like to travel to?")
    
    # Popular destinations suggestions
    st.markdown("#### Popular destinations:")
    popular_cols = st.columns(3)
    
    popular_destinations = [
        "Paris, France", 
        "Tokyo, Japan", 
        "New York City, USA", 
        "Rome, Italy", 
        "Bali, Indonesia",
        "Barcelona, Spain"
    ]
    
    buttons = []
    for i, dest in enumerate(popular_destinations):
        with popular_cols[i % 3]:
            if st.button(dest, key=f"popular_{i}", use_container_width=True):
                st.session_state.destination = dest
                st.rerun()
    
    # Custom destination input
    st.markdown("#### Or enter your own destination:")
    destination = st.text_input(
        "City, Country",
        value=st.session_state.destination,
        key="destination_input",
        help="Enter a city and country"
    )
    
    if destination:
        st.session_state.destination = destination

with col2:
    st.markdown("### Budget Range")
    st.markdown("What's your budget for this trip?")
    
    budget = st.radio(
        "Select your budget level:",
        options=["Budget", "Medium", "Luxury"],
        index=1 if st.session_state.budget == "Medium" else 0 if st.session_state.budget == "Budget" else 2,
        key="budget_radio"
    )
    
    st.session_state.budget = budget
    
    # Display budget explanation
    if budget == "Budget":
        st.markdown("""
        <div class="budget-indicator">
            💰 Economy accommodations, public transportation, affordable dining
        </div>
        """, unsafe_allow_html=True)
    elif budget == "Medium":
        st.markdown("""
        <div class="budget-indicator">
            💰💰 Mid-range hotels, mix of transportation options, casual and occasional upscale dining
        </div>
        """, unsafe_allow_html=True)
    else:  # Luxury
        st.markdown("""
        <div class="budget-indicator">
            💰💰💰 Luxury hotels, private transportation, fine dining experiences
        </div>
        """, unsafe_allow_html=True)

    # Season selection
    st.markdown("### Travel Season")
    season = st.selectbox(
        "When are you planning to travel?",
        options=["Spring", "Summer", "Fall", "Winter"],
        index=["Spring", "Summer", "Fall", "Winter"].index(st.session_state.season),
        key="season_select"
    )
    st.session_state.season = season

# Navigation buttons
st.markdown("---")
col1, col2 = st.columns([1, 1])

with col2:
    # Enable the next button only if destination is provided
    next_disabled = not st.session_state.destination
    if st.button("Next: Travel Preferences →", disabled=next_disabled, use_container_width=True):
        st.switch_page("pages/02_Travel_Preferences.py")

with col1:
    if st.button("← Back to Home", use_container_width=True):
        st.switch_page("main.py")

# Show error if trying to proceed without destination
if next_disabled:
    st.error("Please enter a destination to continue.")
