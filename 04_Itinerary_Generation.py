import streamlit as st
from datetime import datetime, timedelta
import json
import random
import pandas as pd
import time
import destination_scraper

# Set page configuration
st.set_page_config(
    page_title="Itinerary - AI Travel Magic",
    page_icon="✈️",
    layout="wide"
)

# Function to generate content using a simplified fallback approach
def generate_llm_content(prompt, model, tokenizer, max_length=1024):
    try:
        # We're using a simplified approach since the LLM model is not available
        if not st.session_state.get('suppress_itinerary_warnings', False):
            st.warning("Using simplified itinerary generation. LLM-based generation will be available in the full app.")
            st.session_state.suppress_itinerary_warnings = True
            
        # Simulate AI generation with a delay
        with st.spinner("Generating content..."):
            time.sleep(1)  # Add a small delay to simulate processing
            
        # We'll return a placeholder for the example
        response = ""
        return response.strip()
    except Exception as e:
        st.error(f"Error generating content with LLM: {e}")
        return "LLM generation failed. Using basic template generation as fallback."

# Initialize destination_details in session state if it doesn't exist
if 'destination_details' not in st.session_state:
    st.session_state.destination_details = {}

# Function to get destination details using web scraping
def get_destination_details(destination, season, model, tokenizer):
    # First check if we already have this info in session state
    cache_key = f"{destination}_{season}"
    if cache_key in st.session_state.destination_details:
        return st.session_state.destination_details[cache_key]
    
    try:
        with st.spinner(f"Gathering information about {destination}..."):
            # Get real information about the destination using web scraping
            details = destination_scraper.get_destination_info(destination)
            
            # Add weather description based on season
            weather_descriptions = {
                "Spring": f"Mild temperatures with occasional rain showers in {destination}. Perfect for outdoor activities with proper rain gear.",
                "Summer": f"Warm to hot temperatures in {destination}. Great for outdoor activities, but stay hydrated and use sun protection.",
                "Fall": f"Cool temperatures with beautiful foliage in {destination}. Pack layers for changing temperatures throughout the day.",
                "Winter": f"Cold temperatures with possible snow in {destination}. Dress warmly and check for winter activity availability."
            }
            
            details["weather_description"] = weather_descriptions.get(season, f"Typical {season} weather in {destination}")
            
            # Cache the result
            st.session_state.destination_details[cache_key] = details
            return details
        
    except Exception as e:
        st.warning(f"Error getting destination details: {e}. Using web scraping with generic enhancements.")
        # Return enhanced fallback information
        fallback_details = {
            "attractions": [
                f"{destination} National Museum",
                f"{destination} Cathedral", 
                f"Historic District of {destination}",
                f"{destination} Castle",
                f"{destination} Art Gallery",
                f"Old Town {destination}",
                f"{destination} Botanical Gardens",
                f"{destination} Viewpoint"
            ],
            "restaurants": [
                f"The {destination} Kitchen",
                f"Cafe {destination}",
                f"{destination} Bistro",
                f"Traditional {destination} Restaurant",
                f"{destination} Fine Dining",
                f"Local Cuisine of {destination}",
                f"{destination} Street Food Market",
                f"Authentic {destination} Eatery"
            ],
            "activities": [
                f"Walking Tour of {destination}",
                f"{destination} Boat Cruise",
                f"Hiking in {destination}",
                f"{destination} Cultural Experience",
                f"Shopping in {destination}",
                f"{destination} Nightlife Tour",
                f"Cooking Class in {destination}",
                f"{destination} Wine Tasting"
            ],
            "weather_description": f"Typical {season} weather in {destination}",
            "colors": [[66, 135, 245], [240, 140, 50], [66, 186, 150]]
        }
        
        # Cache the fallback result too
        st.session_state.destination_details[cache_key] = fallback_details
        return fallback_details

# Helper function to create a detailed itinerary
def create_template_itinerary(destination, start_date, end_date, budget, preferences, trip_purpose, weather_data, season):
    # Calculate trip duration
    trip_duration = (end_date - start_date).days
    
    # Try to get destination details from session state or use defaults
    try:
        details = get_destination_details(
            destination, 
            season,
            st.session_state.get('llm_model'),
            st.session_state.get('llm_tokenizer')
        )
    except Exception as e:
        st.warning(f"Error getting destination details: {e}")
        details = {
            "attractions": [f"Visit {destination} landmark", "Local museum", "Historic site", "Popular viewpoint", "Cultural center"],
            "restaurants": ["Local cuisine restaurant", "Popular cafe", "Street food", "Traditional eatery", "Dining experience"],
            "activities": ["City tour", "Cultural experience", "Local market", "Outdoor activity", "Evening entertainment"]
        }
    
    attractions = details.get("attractions", [f"Visit {destination}"])
    restaurants = details.get("restaurants", ["Local restaurant"])
    general_activities = details.get("activities", ["Explore the area"])
    
    # Get preference-specific activities for this destination
    preference_activities = destination_scraper.get_specific_activities(destination, preferences)
    
    # Budget-specific accommodation and dining options
    budget_accommodations = {
        "Budget": [
            f"Hostel in {destination}", 
            f"Budget hotel in {destination}", 
            f"Guesthouse in {destination}", 
            f"Affordable Airbnb in {destination}",
            f"Backpacker's lodge in {destination}"
        ],
        "Medium": [
            f"3-star hotel in {destination}", 
            f"Boutique hotel in {destination}", 
            f"Comfortable Airbnb in {destination}", 
            f"Mid-range resort in {destination}",
            f"Charming B&B in {destination}"
        ],
        "Luxury": [
            f"5-star hotel in {destination}", 
            f"Luxury resort in {destination}", 
            f"Premium apartment in {destination}", 
            f"Upscale villa in {destination}",
            f"Exclusive hotel in {destination}"
        ]
    }
    
    # Budget-specific activities
    budget_activities = {
        "Budget": [
            f"Free walking tour of {destination}", 
            f"Visit to public parks in {destination}", 
            f"Explore local markets in {destination}", 
            f"Street food tasting in {destination}", 
            f"Self-guided tour of {destination}"
        ],
        "Medium": [
            f"Guided museum tour in {destination}", 
            f"Day tour around {destination}", 
            f"Boat ride in {destination}", 
            f"Cultural show in {destination}", 
            f"Cooking class in {destination}"
        ],
        "Luxury": [
            f"Private guided tour of {destination}", 
            f"Exclusive experience in {destination}", 
            f"VIP access to attractions in {destination}", 
            f"Helicopter tour over {destination}", 
            f"Private chef experience in {destination}"
        ]
    }
    
    # Add budget-specific activities
    budget_options = budget_activities.get(budget, budget_activities["Medium"])
    accommodations = budget_accommodations.get(budget, budget_accommodations["Medium"])
    
    # Combine all activities by category
    all_activities = attractions + general_activities + budget_options
    
    # Create day-by-day itinerary
    itinerary = []
    current_date = start_date
    
    # Find weather data for each day
    weather_by_date = {w["date"]: w for w in weather_data} if weather_data else {}
    
    # For each preference, get at least one activity
    preference_options = []
    for pref, activities in preference_activities.items():
        if activities:
            preference_options.extend(activities)
    
    # Create activities for each day with more detailed descriptions
    for day in range(1, trip_duration + 1):
        date_str = current_date.strftime("%Y-%m-%d")
        day_weather = weather_by_date.get(date_str, {
            "weather": f"Typical {season} weather",
            "temperature": "Typical temperature",
            "icon": "☀️"
        })
        
        # Choose activities based on preferences if possible
        if day <= len(preferences) and day <= len(preference_options) and preference_options:
            morning = preference_options.pop(0)
        else:
            morning = random.choice(all_activities)
            all_activities = [a for a in all_activities if a != morning]
            
        # Remove the selected activity to avoid duplication    
        afternoon_options = [a for a in all_activities + attractions if a != morning]
        if afternoon_options:
            afternoon = random.choice(afternoon_options)
        else:
            afternoon = f"Explore the neighborhoods of {destination}"
            
        evening = random.choice(restaurants)
        
        # Create detailed descriptions
        morning_desc = f"Start your day at {morning}. "
        if "Museum" in morning or "Gallery" in morning:
            morning_desc += f"Explore the fascinating exhibits and learn about the cultural heritage of {destination}. Allow 2-3 hours to fully appreciate the collections."
        elif "Park" in morning or "Garden" in morning or "Nature" in morning:
            morning_desc += f"Enjoy the natural beauty and fresh air while taking a leisurely stroll through this scenic area. Perfect for morning photography in the {season} light."
        elif "Tour" in morning:
            morning_desc += f"This guided experience will introduce you to the highlights of {destination}, with expert commentary on the history and significance of key landmarks."
        else:
            morning_desc += f"This is one of {destination}'s must-visit attractions, offering a perfect start to your day with unforgettable experiences."
        
        afternoon_desc = f"Head to {afternoon} for your afternoon activities. "
        if "Historic" in afternoon or "Castle" in afternoon or "Cathedral" in afternoon:
            afternoon_desc += f"Immerse yourself in the rich history of this landmark, dating back centuries and showcasing impressive architecture and cultural significance."
        elif "Market" in afternoon or "Shopping" in afternoon:
            afternoon_desc += f"Browse the various stalls and shops, where you can find local handicrafts, souvenirs, and specialty products unique to {destination}."
        elif "Cruise" in afternoon or "Boat" in afternoon:
            afternoon_desc += f"Enjoy spectacular views of {destination} from the water, with opportunities for photos and a new perspective on this beautiful location."
        else:
            afternoon_desc += f"This experience showcases the authentic culture and charm of {destination}, allowing you to create lasting memories of your trip."
        
        evening_desc = f"For dinner, enjoy a meal at {evening}. "
        if "Traditional" in evening or "Local" in evening:
            evening_desc += f"Sample authentic dishes from {destination}'s cuisine, prepared with traditional methods and local ingredients that capture the essence of the region."
        elif "Fine" in evening or "Luxury" in evening:
            evening_desc += f"Indulge in an exceptional dining experience with premium ingredients and expert preparation in an elegant atmosphere."
        elif "Cafe" in evening or "Bistro" in evening:
            evening_desc += f"Enjoy a casual yet delicious meal in a charming setting, perfect for relaxing after a day of exploration."
        else:
            evening_desc += f"The menu features a range of options that will satisfy your taste buds and provide a genuine taste of {destination}."
        
        # Choose accommodation
        accommodation = random.choice(accommodations)
        
        # Create day entry with detailed descriptions
        day_entry = {
            "day": day,
            "date": date_str,
            "day_name": current_date.strftime("%A"),
            "weather": day_weather.get("weather", ""),
            "temperature": day_weather.get("temperature", ""),
            "weather_icon": day_weather.get("icon", "☀️"),
            "morning": {
                "title": morning,
                "description": morning_desc
            },
            "afternoon": {
                "title": afternoon,
                "description": afternoon_desc
            },
            "evening": {
                "title": evening,
                "description": evening_desc
            },
            "accommodation": f"Stay at {accommodation}, offering comfortable {budget.lower()}-level accommodations with convenient access to the city's attractions."
        }
        
        itinerary.append(day_entry)
        current_date += timedelta(days=1)
    
    # Create a more detailed trip summary
    summary = f"Experience the best of {destination} on this personalized {trip_duration}-day {budget.lower()} adventure. "
    
    if trip_purpose:
        if "family" in trip_purpose.lower():
            summary += f"This family-friendly itinerary includes activities that will delight travelers of all ages. "
        elif "romantic" in trip_purpose.lower():
            summary += f"Your romantic getaway features intimate experiences and beautiful settings perfect for couples. "
        elif "adventure" in trip_purpose.lower():
            summary += f"Packed with exciting activities, this adventure trip will satisfy your thirst for exploration. "
        elif "relaxation" in trip_purpose.lower():
            summary += f"Focused on relaxation and rejuvenation, this trip gives you plenty of time to unwind and enjoy. "
        elif "cultural" in trip_purpose.lower() or "educational" in trip_purpose.lower():
            summary += f"Immerse yourself in the rich culture and history of {destination} with this educational journey. "
    
    if preferences:
        if len(preferences) == 1:
            summary += f"With a focus on {preferences[0]}, you'll discover the very best experiences {destination} has to offer."
        else:
            pref_str = ", ".join(preferences[:-1]) + " and " + preferences[-1]
            summary += f"Featuring {pref_str}, this itinerary is tailored to your specific interests and designed to create unforgettable memories."
    
    # Additional trip information
    trip_info = {
        "destination": destination,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "duration": trip_duration,
        "budget": budget,
        "preferences": preferences,
        "purpose": trip_purpose,
        "season": season,
        "summary": summary
    }
    
    return {"trip_info": trip_info, "daily_plan": itinerary}

# Function to generate an LLM-powered itinerary
def generate_detailed_itinerary(destination, start_date, end_date, budget, preferences, trip_purpose, weather_data, season, model, tokenizer):
    # First try to generate with LLM
    try:
        if model is None or tokenizer is None:
            raise ValueError("LLM model not available")
        
        # Calculate trip duration
        trip_duration = (end_date - start_date).days
        
        # Format preferences as a comma-separated list
        pref_str = ", ".join(preferences) if preferences else "general sightseeing"
        
        # Format weather data as a string
        weather_str = ""
        for w in weather_data:
            weather_str += f"{w['date']}: {w['weather']}, {w['temperature']}\n"
        
        # Create the prompt for the LLM
        prompt = f"""Create a detailed travel itinerary for a {trip_duration}-day trip to {destination} with the following details:
- Budget level: {budget}
- Travel dates: {start_date.strftime("%B %d, %Y")} to {end_date.strftime("%B %d, %Y")}
- Season: {season}
- Trip purpose: {trip_purpose}
- Preferences: {pref_str}

Weather forecast:
{weather_str}

Return a complete itinerary with day-by-day activities formatted as valid JSON with this structure:
{{
  "trip_info": {{
    "destination": "{destination}",
    "start_date": "{start_date.strftime("%Y-%m-%d")}",
    "end_date": "{end_date.strftime("%Y-%m-%d")}",
    "duration": {trip_duration},
    "budget": "{budget}",
    "preferences": {json.dumps(preferences)},
    "purpose": "{trip_purpose}",
    "season": "{season}",
    "summary": "Brief 2-3 sentence overview of the trip"
  }},
  "daily_plan": [
    {{
      "day": 1,
      "date": "{start_date.strftime("%Y-%m-%d")}",
      "day_name": "{start_date.strftime("%A")}",
      "weather": "Weather description",
      "temperature": "Temperature range",
      "weather_icon": "Weather emoji",
      "morning": {{
        "title": "Morning activity name",
        "description": "Detailed description of morning activity"
      }},
      "afternoon": {{
        "title": "Afternoon activity name",
        "description": "Detailed description of afternoon activity"
      }},
      "evening": {{
        "title": "Evening activity name",
        "description": "Detailed description of evening activity"
      }},
      "accommodation": "Accommodation details"
    }},
    // Additional days...
  ]
}}

Make sure to:
1. Include realistic activities specific to {destination}
2. Consider the weather forecast when suggesting outdoor activities
3. Match activities to the user's preferences
4. Suggest accommodation and dining options appropriate for the {budget} level
5. Include specific names of attractions, restaurants, and places
6. Format the response as valid JSON that can be parsed without errors
"""
        
        # Generate itinerary with LLM
        response = generate_llm_content(prompt, model, tokenizer, max_length=2048)
        
        # Extract JSON from response
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            json_str = response.split("```")[1].strip()
        else:
            json_str = response
            
        try:
            itinerary = json.loads(json_str)
            return itinerary
        except json.JSONDecodeError as e:
            st.warning(f"Error parsing LLM response: {e}. Using template itinerary.")
            raise ValueError("Failed to parse LLM response")
            
    except Exception as e:
        st.warning(f"Using template itinerary generator: {e}")
        # Fallback to template itinerary
        return create_template_itinerary(
            destination, start_date, end_date, budget,
            preferences, trip_purpose, weather_data, season
        )

# Check if we have the necessary session state variables
if 'destination' not in st.session_state or not st.session_state.destination:
    st.switch_page("pages/01_Destination_and_Budget.py")
if 'trip_purpose' not in st.session_state or not st.session_state.trip_purpose:
    st.switch_page("pages/02_Travel_Preferences.py")
if 'start_date' not in st.session_state or 'end_date' not in st.session_state:
    st.switch_page("pages/03_Calendar_and_Weather.py")

# Title and description
st.title("🗺️ Your Personalized Travel Itinerary")
st.markdown(f"### {st.session_state.destination} - {st.session_state.start_date.strftime('%b %d')} to {st.session_state.end_date.strftime('%b %d, %Y')}")

# Trip summary box
trip_duration = (st.session_state.end_date - st.session_state.start_date).days
preferences_str = ", ".join(st.session_state.preferences) if st.session_state.preferences else "General sightseeing"

st.markdown(f"""
<div class="highlight-box">
    <h3>Trip Summary</h3>
    <p><strong>Destination:</strong> {st.session_state.destination}</p>
    <p><strong>Dates:</strong> {st.session_state.start_date.strftime('%B %d')} - {st.session_state.end_date.strftime('%B %d, %Y')} ({trip_duration} days)</p>
    <p><strong>Purpose:</strong> {st.session_state.trip_purpose}</p>
    <p><strong>Budget:</strong> {st.session_state.budget}</p>
    <p><strong>Interests:</strong> {preferences_str}</p>
</div>
""", unsafe_allow_html=True)

# Check if we already have an itinerary
if 'itinerary' not in st.session_state or st.session_state.itinerary is None:
    # Show progress while generating itinerary
    with st.spinner("Creating your personalized itinerary..."):
        # Simulate some processing time if needed
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.02)  # Simulated delay
            progress_bar.progress(i + 1)
        
        # Generate the itinerary
        st.session_state.itinerary = generate_detailed_itinerary(
            st.session_state.destination,
            st.session_state.start_date,
            st.session_state.end_date,
            st.session_state.budget,
            st.session_state.preferences,
            st.session_state.trip_purpose,
            st.session_state.get('weather_data', []),
            st.session_state.season,
            st.session_state.get('llm_model'),
            st.session_state.get('llm_tokenizer')
        )

# Display the itinerary once generated
if st.session_state.itinerary:
    itinerary = st.session_state.itinerary
    
    # Display overall trip summary
    st.markdown(f"""
    <div class="cinematic-text">
        {itinerary.get('trip_info', {}).get('summary', f"A {trip_duration}-day journey to {st.session_state.destination} awaits you!")}
    </div>
    """, unsafe_allow_html=True)
    
    # Display daily itinerary
    st.markdown("## Day-by-Day Itinerary")
    
    daily_plan = itinerary.get('daily_plan', [])
    
    if not daily_plan:
        st.error("No daily plan found in the itinerary. Please try regenerating.")
    else:
        # Create tabs for each day
        day_tabs = st.tabs([f"Day {day['day']}: {day.get('day_name', '')}" for day in daily_plan])
        
        for i, day in enumerate(daily_plan):
            with day_tabs[i]:
                # Weather information
                weather = day.get('weather', '')
                temp = day.get('temperature', '')
                weather_icon = day.get('weather_icon', '☀️')
                
                st.markdown(f"""
                <div class="weather-section">
                    <h4>{day.get('date', '')} - {day.get('day_name', '')}</h4>
                    <p>{weather_icon} <strong>{weather}</strong> | {temp}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Morning activities
                st.markdown("### Morning")
                morning = day.get('morning', {})
                st.markdown(f"**{morning.get('title', 'Morning activities')}**")
                st.markdown(morning.get('description', ''))
                
                # Afternoon activities
                st.markdown("### Afternoon")
                afternoon = day.get('afternoon', {})
                st.markdown(f"**{afternoon.get('title', 'Afternoon activities')}**")
                st.markdown(afternoon.get('description', ''))
                
                # Evening activities
                st.markdown("### Evening")
                evening = day.get('evening', {})
                st.markdown(f"**{evening.get('title', 'Evening activities')}**")
                st.markdown(evening.get('description', ''))
                
                # Accommodation
                st.markdown("### Accommodation")
                st.markdown(day.get('accommodation', f"Your {st.session_state.budget.lower()} accommodation in {st.session_state.destination}"))
    
    # Download and Save options
    col_download, col_save = st.columns(2)
    
    with col_download:
        if st.download_button(
            "Download Itinerary (JSON)",
            data=json.dumps(itinerary, indent=2),
            file_name=f"{st.session_state.destination.replace(' ', '_')}_itinerary.json",
            mime="application/json",
            use_container_width=True
        ):
            st.success("Download started!")
    
    with col_save:
        if st.button("Save Itinerary", use_container_width=True):
            # Make sure saved_itineraries exists in session state
            if 'saved_itineraries' not in st.session_state:
                st.session_state.saved_itineraries = []
                
            # Create a user ID if it doesn't exist yet
            if 'user_id' not in st.session_state:
                from datetime import datetime
                st.session_state.user_id = f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
            # Prepare itinerary data
            itinerary_data = {
                "name": f"Trip to {st.session_state.destination}",
                "destination": st.session_state.destination,
                "start_date": st.session_state.start_date.isoformat() if hasattr(st.session_state.start_date, 'isoformat') else st.session_state.start_date,
                "end_date": st.session_state.end_date.isoformat() if hasattr(st.session_state.end_date, 'isoformat') else st.session_state.end_date,
                "budget": st.session_state.budget,
                "trip_purpose": st.session_state.trip_purpose,
                "preferences": st.session_state.preferences,
                "special_notes": st.session_state.get('special_notes', ''),
                "weather_data": st.session_state.get('weather_data', []),
                "season": st.session_state.get('season', ''),
                "itinerary": itinerary,
                "user_id": st.session_state.user_id,
                "id": f"itin_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(st.session_state.saved_itineraries)}",
                "created_at": datetime.now().isoformat()
            }
            
            # Add to saved itineraries
            st.session_state.saved_itineraries.append(itinerary_data)
            st.success("Itinerary saved successfully! View it in the Saved Itineraries page.")
    
    # Navigation buttons
    st.markdown("---")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button("← Back to Calendar", use_container_width=True):
            st.switch_page("pages/03_Calendar_and_Weather.py")
    
    with col2:
        if st.button("Regenerate Itinerary", use_container_width=True):
            st.session_state.itinerary = None
            st.rerun()
            
    with col3:
        if st.button("Create Trip Preview →", use_container_width=True):
            st.switch_page("pages/05_Trip_Preview.py")
            
    with col4:
        if st.button("View Saved Itineraries", use_container_width=True):
            st.switch_page("pages/06_Saved_Itineraries.py")
else:
    st.error("Failed to generate itinerary. Please try again.")
    if st.button("Try Again", use_container_width=True):
        st.session_state.itinerary = None
        st.rerun()
