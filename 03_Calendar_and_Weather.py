import streamlit as st
from datetime import datetime, timedelta
import json
import random

# Set page configuration
st.set_page_config(
    page_title="Calendar & Weather - AI Travel Magic",
    page_icon="✈️",
    layout="wide"
)

# Function to predict weather based on destination, season and date
def predict_weather(destination, date, season, model, tokenizer):
    """
    Generate weather prediction for a specific date at the destination.
    Uses the destination, date, and season to predict likely weather.
    
    Returns a tuple of (weather_description, temperature_range, weather_icon)
    """
    # First check cache to avoid regenerating
    cache_key = f"{destination}_{date.strftime('%Y-%m-%d')}_{season}"
    if cache_key in st.session_state.weather_cache:
        return st.session_state.weather_cache[cache_key]
    
    # Prepare prompt for weather prediction
    month_name = date.strftime("%B")
    day_of_month = date.strftime("%d")
    
    prompt = f"""Predict the most likely weather for {destination} on {month_name} {day_of_month} during {season} season.
Return the response as valid JSON in this exact format:
{{
  "weather_description": "Short 2-3 word description (e.g., 'Sunny and clear', 'Light rain', 'Partly cloudy')",
  "temperature_range": "Temperature range in both Celsius and Fahrenheit (e.g., '18-24°C (64-75°F)')",
  "weather_icon": "One of: ☀️ (sunny), ⛅ (partly cloudy), ☁️ (cloudy), 🌧️ (rainy), ⛈️ (thunderstorm), ❄️ (snow), 🌫️ (foggy)"
}}
For your prediction, consider that {destination} in {season} typically has [typical weather pattern].
"""
    
    try:
        if model is None or tokenizer is None:
            raise ValueError("Weather model not available")
            
        # Generate the weather prediction using LLM from main.py
        # For this page we'll use the fallback since the real function relies on imported functions
        raise ValueError("Using fallback weather generation")
            
    except Exception as e:
        # Fallback weather generation based on season
        if not st.session_state.get('suppress_warnings', False):
            st.warning(f"Using simplified weather prediction. LLM-based prediction will be available in the full app.")
            st.session_state.suppress_warnings = True
        
        # Generate fallback weather by season
        season_weather = {
            "Spring": [
                ("Mild and sunny", "15-22°C (59-72°F)", "⛅"),
                ("Light showers", "12-18°C (54-64°F)", "🌧️"),
                ("Partly cloudy", "14-20°C (57-68°F)", "☁️")
            ],
            "Summer": [
                ("Hot and sunny", "25-32°C (77-90°F)", "☀️"),
                ("Warm with clouds", "22-28°C (72-82°F)", "⛅"),
                ("Afternoon thunderstorm", "23-30°C (73-86°F)", "⛈️")
            ],
            "Fall": [
                ("Cool and breezy", "12-18°C (54-64°F)", "⛅"),
                ("Misty morning", "10-16°C (50-61°F)", "🌫️"),
                ("Partly cloudy", "13-20°C (55-68°F)", "☁️")
            ],
            "Winter": [
                ("Cold and clear", "2-8°C (36-46°F)", "☀️"),
                ("Light snow", "-2-5°C (28-41°F)", "❄️"),
                ("Overcast", "0-6°C (32-43°F)", "☁️")
            ]
        }
        
        # For destinations with extreme weather, modify predictions
        if "Iceland" in destination or "Norway" in destination and season == "Winter":
            season_weather["Winter"] = [
                ("Very cold", "-10-0°C (14-32°F)", "❄️"),
                ("Snow showers", "-15--5°C (5-23°F)", "❄️"),
                ("Northern lights", "-12--2°C (10-28°F)", "☀️")
            ]
        elif "Dubai" in destination or "Egypt" in destination and season == "Summer":
            season_weather["Summer"] = [
                ("Extremely hot", "35-45°C (95-113°F)", "☀️"),
                ("Hot and dry", "33-42°C (91-108°F)", "☀️"),
                ("Hot and hazy", "34-43°C (93-109°F)", "☀️")
            ]
        
        # Get random weather for the season
        result = random.choice(season_weather.get(season, season_weather["Spring"]))
        st.session_state.weather_cache[cache_key] = result
        return result

# Initialize session state variables
if 'destination' not in st.session_state or not st.session_state.destination:
    st.session_state.destination = ""
    st.switch_page("pages/01_Destination_and_Budget.py")
if 'start_date' not in st.session_state:
    st.session_state.start_date = datetime.now().date()
if 'end_date' not in st.session_state:
    # Default to a week after start date
    st.session_state.end_date = (datetime.now() + timedelta(days=7)).date()
if 'weather_cache' not in st.session_state:
    st.session_state.weather_cache = {}

# Title and description
st.title("📅 Travel Dates & Weather")
st.markdown(f"### Select your travel dates for {st.session_state.destination}")

st.markdown("""
<div class="highlight-box">
    <p>Choose your travel dates, and we'll provide weather predictions to help you pack appropriately and plan outdoor activities.</p>
</div>
""", unsafe_allow_html=True)

# Calendar for date selection
st.markdown("### Trip Duration")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Start Date")
    min_date = datetime.now().date()
    max_date = min_date + timedelta(days=365)  # Allow booking up to a year in advance
    
    start_date = st.date_input(
        "When will your trip begin?",
        value=st.session_state.start_date,
        min_value=min_date,
        max_value=max_date,
        key="start_date_input"
    )
    st.session_state.start_date = start_date

with col2:
    st.markdown("#### End Date")
    end_date = st.date_input(
        "When will your trip end?",
        value=max(st.session_state.end_date, start_date + timedelta(days=1)),
        min_value=start_date + timedelta(days=1),
        max_value=start_date + timedelta(days=30),  # Limit to 30 days trip
        key="end_date_input"
    )
    st.session_state.end_date = end_date

# Calculate trip duration
trip_duration = (end_date - start_date).days
st.markdown(f"**Trip Duration:** {trip_duration} {'days' if trip_duration > 1 else 'day'}")

# Display weather predictions
st.markdown("### Weather Forecast")
st.markdown(f"Predicted weather for your trip to {st.session_state.destination}:")

# Create weather forecast cards
current_date = start_date
weather_data = []

# Display calendar with weather in a grid
num_cols = min(5, trip_duration)  # Display 5 days per row
remaining_days = trip_duration

st.markdown('<div class="calendar-container">', unsafe_allow_html=True)

while remaining_days > 0:
    cols = st.columns(min(num_cols, remaining_days))
    
    for i in range(min(num_cols, remaining_days)):
        with cols[i]:
            date_str = current_date.strftime("%b %d")
            day_name = current_date.strftime("%A")
            
            # Get weather prediction
            weather_desc, temp_range, weather_icon = predict_weather(
                st.session_state.destination, 
                current_date, 
                st.session_state.season,
                st.session_state.get('weather_model'),
                st.session_state.get('weather_tokenizer')
            )
            
            # Store weather data for later use
            weather_data.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "day_name": day_name,
                "weather": weather_desc,
                "temperature": temp_range,
                "icon": weather_icon
            })
            
            # Display weather card
            st.markdown(f"<h4>{date_str} ({day_name})</h4>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style="text-align: center; padding: 10px;">
                <div style="font-size: 2rem;">{weather_icon}</div>
                <div><b>{weather_desc}</b></div>
                <div>{temp_range}</div>
            </div>
            """, unsafe_allow_html=True)
            
            current_date = current_date + timedelta(days=1)
            
    remaining_days -= num_cols

st.markdown('</div>', unsafe_allow_html=True)

# Save weather data to session state for use in itinerary generation
st.session_state.weather_data = weather_data

# Packing suggestions based on weather and destination
st.markdown("### Packing Suggestions")

# Determine overall weather pattern
weather_conditions = [w["weather"].lower() for w in weather_data]
temp_ranges = [w["temperature"] for w in weather_data]

# Simple packing suggestions based on weather patterns
packing_items = ["Travel documents", "Phone charger", "Comfortable walking shoes"]

# Add weather-specific items
if any("rain" in w for w in weather_conditions) or any("shower" in w for w in weather_conditions):
    packing_items.extend(["Umbrella", "Waterproof jacket", "Waterproof shoes"])
if any("hot" in w for w in weather_conditions) or any("sunny" in w for w in weather_conditions):
    packing_items.extend(["Sunscreen", "Sunglasses", "Hat", "Light clothing"])
if any("cold" in w for w in weather_conditions) or any("snow" in w for w in weather_conditions):
    packing_items.extend(["Warm jacket", "Gloves", "Scarf", "Thermal underwear"])
if "Beach" in st.session_state.preferences or "Beaches & Water Activities" in st.session_state.preferences:
    packing_items.extend(["Swimwear", "Beach towel", "Sandals"])

# Display packing list
st.markdown("Based on the predicted weather and your activities, consider packing:")
cols = st.columns(2)
half_len = len(packing_items) // 2 + len(packing_items) % 2

with cols[0]:
    for item in packing_items[:half_len]:
        st.markdown(f"- {item}")

with cols[1]:
    for item in packing_items[half_len:]:
        st.markdown(f"- {item}")

# Navigation buttons
st.markdown("---")
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("← Back to Preferences", use_container_width=True):
        st.switch_page("pages/02_Travel_Preferences.py")

with col2:
    if st.button("Next: Generate Itinerary →", use_container_width=True):
        st.switch_page("pages/04_Itinerary_Generation.py")
