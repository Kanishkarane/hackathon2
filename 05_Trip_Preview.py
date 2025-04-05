import streamlit as st
import os
import requests
from PIL import Image
from io import BytesIO
import random
import time
import re

# Set page configuration
st.set_page_config(
    page_title="Trip Preview - AI Travel Magic",
    page_icon="✈️",
    layout="wide"
)

# Create data directories if they don't exist
if not os.path.exists('data'):
    os.makedirs('data')
if not os.path.exists('data/images'):
    os.makedirs('data/images')

# Check if we have the necessary data to proceed
if 'destination' not in st.session_state or not st.session_state.destination:
    st.switch_page("pages/01_Destination_and_Budget.py")
if 'itinerary' not in st.session_state or not st.session_state.itinerary:
    st.switch_page("pages/04_Itinerary_Generation.py")

# Title and description
st.title("🎬 Your Trip Preview")
st.markdown(f"### A visual journey through {st.session_state.destination}")

# Display trip details
trip_info = st.session_state.itinerary.get('trip_info', {})
daily_plan = st.session_state.itinerary.get('daily_plan', [])

# Create a cinematic preview
st.markdown("## 🌄 Complete Slideshow of Places You'll Visit")

# Initialize image tracking to avoid duplicates
if 'used_image_urls' not in st.session_state:
    st.session_state.used_image_urls = set()

# Function to create more specific search queries for activities
def create_specific_search_query(destination, activity):
    """Create a specific search query based on activity keywords with enhanced diversity"""
    
    # Clean up the activity text
    activity = activity.lower().strip()
    
    # Extract the main location from destination (e.g., "Paris" from "Paris, France")
    main_location = destination.split(',')[0].strip()
    
    # Add visual descriptors to enhance image variety
    visual_descriptors = [
        "beautiful", "scenic", "panoramic", "iconic", "famous", 
        "stunning", "picturesque", "impressive", "popular"
    ]
    
    # Select a random descriptor for variety
    descriptor = random.choice(visual_descriptors)
    
    # Dictionary of common activities and their specific visual search terms
    # The existing activities_map dictionary remains the same...
    activities_map = {
    "hiking": "mountain trail",
    "trekking": "scenic path",
    "museum": "art exhibit",
    "beach": "coastal view",
    "snorkeling": "underwater reef",
    "diving": "coral exploration",
    "skiing": "snowy slopes",
    "snowboarding": "alpine terrain",
    "shopping": "local markets",
    "nightlife": "live music scene",
    "food": "local cuisine",
    "wine tasting": "vineyard tour",
    "historical sites": "ancient ruins",
    "temples": "sacred architecture",
    "road trip": "scenic drive",
    "wildlife safari": "animal reserve",
    "kayaking": "river adventure",
    "camping": "forest campsite",
    "photography": "panoramic landscape",
    "hot air balloon": "sunrise aerial view",
    "amusement park": "rollercoaster ride",
    "cruise": "ocean voyage",
    "biking": "trail ride",
    "local tour": "city exploration",
    "cultural experience": "traditional festival",
    "street food": "food stalls",
    "spa": "relaxing retreat",
    "festival": "crowded celebration",
    "art gallery": "modern art exhibit",
    "architecture tour": "iconic buildings",
    "boat ride": "canal cruise"
}

    
    # Check for direct matches or partial matches
    for key, search_term in activities_map.items():
        if key in activity:
            # Add random descriptor to enhance variety
            return f"{descriptor} {search_term}"
    
    # If no specific match found, combine destination with activity
    # and remove generic words like "visit", "experience", etc.
    generic_words = ["visit", "experience", "tour", "discover", "explore", "enjoy", "at", "the", "a", "an", "in", "to"]
    
    # Clean up activity text
    for word in generic_words:
        activity = re.sub(r'\b' + word + r'\b', '', activity, flags=re.IGNORECASE)
    
    # Remove any extra spaces and format the query
    activity = re.sub(r'\s+', ' ', activity).strip()
    
    # If activity is now empty, use a fallback
    if not activity:
        return f"{descriptor} {main_location} landmark"
        
    return f"{descriptor} {main_location} {activity}"

def get_diverse_image(location, activity, attempt=0, uniqueness_seed=None):
    """Get image with diverse fallback options"""
    if attempt > 3:  # Limit recursion
        return get_destination_fallback(location)
    
    try:
        # Add stronger uniqueness to each query by combining activity and a seed
        if uniqueness_seed is None:
            uniqueness_seed = random.randint(1, 1000000)
        
        rand_param = f"{uniqueness_seed}"
        
        # Try specific query first
        if attempt == 0:
            # Get a specialized search query based on the activity
            search_query = create_specific_search_query(location, activity)
            query = search_query
        # First fallback: Try with just the location and activity directly
        elif attempt == 1:
            query = f"{location} {activity}"
        # Second fallback: Try with just the location
        elif attempt == 2:
            query = f"{location} {activity} travel"
        # Third fallback: Use a general travel query with the activity type
        else:
            # Extract activity type (museum, restaurant, park, etc.)
            activity_types = ["museum", "restaurant", "park", "tower", "palace", "cafe", 
                             "gallery", "market", "garden", "monument", "bistro", "shopping"]
            activity_type = "landmark"
            for t in activity_types:
                if t.lower() in activity.lower():
                    activity_type = t
                    break
            query = f"{location} {activity_type}"
            
        # Clean and format query
        query = query.strip().lower().replace(' ', '+')
        
        # Get image from multiple sources to increase variety
        # Alternate between different image sources based on uniqueness_seed
        image_sources = [
            f"https://source.unsplash.com/800x400/?{query}&rand={rand_param}",
            f"https://loremflickr.com/800/400/{query}?random={rand_param}",
            f"https://picsum.photos/seed/{query}-{rand_param}/800/400"
        ]
        
        url = image_sources[uniqueness_seed % len(image_sources)]
        
        # Check if we've used this URL before (avoid duplicates)
        if url in st.session_state.used_image_urls:
            # Try a completely different seed
            return get_diverse_image(location, activity, attempt, uniqueness_seed + 10000)
            
        response = requests.get(url, timeout=10, stream=True)
        
        if response.status_code == 200:
            try:
                # Validate image with PIL
                img = Image.open(BytesIO(response.content))
                
                # Add URL to used set
                st.session_state.used_image_urls.add(url)
                
                # Return the image content
                return response.content
            except Exception as e:
                # If PIL can't open it, try next fallback
                return get_diverse_image(location, activity, attempt + 1, uniqueness_seed)
        else:
            # If request failed, try next fallback
            return get_diverse_image(location, activity, attempt + 1, uniqueness_seed)
    except Exception as e:
        # If any error occurs, try next fallback
        return get_diverse_image(location, activity, attempt + 1, uniqueness_seed)
def get_destination_fallback(location):
    """Last resort: Get a generic image of the destination"""
    try:
        # Try to get a general image of the destination
        query = f"{location}+landmark+famous"
        url = f"https://source.unsplash.com/800x400/?{query}&rand={random.randint(1, 10000)}"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            try:
                # Validate image
                img = Image.open(BytesIO(response.content))
                return response.content
            except Exception:
                # If even this fails, use a completely generic travel image
                generic_url = "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&h=400&fit=crop"
                return requests.get(generic_url, timeout=10).content
        else:
            # Use generic travel image
            generic_url = "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&h=400&fit=crop"
            return requests.get(generic_url, timeout=10).content
    except Exception:
        # Complete fallback to a reliable image
        try:
            generic_url = "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&h=400&fit=crop"
            return requests.get(generic_url, timeout=10).content
        except Exception:
            return None

# Debug option in sidebar to see what's happening
if st.sidebar.checkbox("Show Debug Info", value=False):
    st.sidebar.write("Debug mode active")
    st.sidebar.write(f"Destination: {st.session_state.destination}")
    st.sidebar.write(f"Used image URLs: {len(st.session_state.used_image_urls)}")

# Optional clear cache button
if st.sidebar.button("Clear Image Cache"):
    st.session_state.used_image_urls = set()
    st.sidebar.success("Image cache cleared!")

# Display daily activities with images
day_index = 0
for day in daily_plan:
    st.markdown(f"### Day {day['day']}: {day['day_name']}")

    col1, col2, col3 = st.columns(3)
    
    # Generate unique seeds for each activity
    day_seed = (day_index + 1) * 1000
    morning_seed = day_seed + 1
    afternoon_seed = day_seed + 2
    evening_seed = day_seed + 3

    # Morning activity
    with col1:
        st.subheader("Morning")
        morning_activity = day.get('morning', {}).get('title', '')
        if morning_activity:
            with st.spinner(f"Loading image for {morning_activity}..."):
                image_data = get_diverse_image(
                    st.session_state.destination, 
                    morning_activity,
                    uniqueness_seed=morning_seed
                )
                if image_data:
                    try:
                        st.image(image_data, caption=morning_activity, use_container_width=True)
                    except Exception:
                        st.warning("Could not display image")
                else:
                    st.warning("Image could not be loaded")
                st.markdown(f"**{morning_activity}**")
        else:
            with st.spinner("Loading morning image..."):
                image_data = get_diverse_image(
                    st.session_state.destination, 
                    "morning view",
                    uniqueness_seed=morning_seed
                )
                if image_data:
                    st.image(image_data, use_container_width=True)

    # Afternoon activity
    with col2:
        st.subheader("Afternoon")
        afternoon_activity = day.get('afternoon', {}).get('title', '')
        if afternoon_activity:
            with st.spinner(f"Loading image for {afternoon_activity}..."):
                image_data = get_diverse_image(
                    st.session_state.destination, 
                    afternoon_activity,
                    uniqueness_seed=afternoon_seed
                )
                if image_data:
                    try:
                        st.image(image_data, caption=afternoon_activity, use_container_width=True)
                    except Exception:
                        st.warning("Could not display image")
                else:
                    st.warning("Image could not be loaded")
                st.markdown(f"**{afternoon_activity}**")
        else:
            with st.spinner("Loading afternoon image..."):
                image_data = get_diverse_image(
                    st.session_state.destination, 
                    "afternoon activity",
                    uniqueness_seed=afternoon_seed
                )
                if image_data:
                    st.image(image_data, use_container_width=True)

    # Evening activity
    with col3:
        st.subheader("Evening")
        evening_activity = day.get('evening', {}).get('title', '')
        if evening_activity:
            with st.spinner(f"Loading image for {evening_activity}..."):
                image_data = get_diverse_image(
                    st.session_state.destination, 
                    evening_activity,
                    uniqueness_seed=evening_seed
                )
                if image_data:
                    try:
                        st.image(image_data, caption=evening_activity, use_container_width=True)
                    except Exception:
                        st.warning("Could not display image")
                else:
                    st.warning("Image could not be loaded")
                st.markdown(f"**{evening_activity}**")
        else:
            with st.spinner("Loading evening image..."):
                image_data = get_diverse_image(
                    st.session_state.destination, 
                    "evening scene",
                    uniqueness_seed=evening_seed
                )
                if image_data:
                    st.image(image_data, use_container_width=True)

    st.markdown("---")
    day_index += 1
    
    # Add a small delay between days to prevent rate limiting
    time.sleep(0.5)

# Trip highlights section
st.markdown("## ✨ Trip Highlights")
highlights = []

# Extract highlights from the daily plan
for day in daily_plan:
    for period in ['morning', 'afternoon', 'evening']:
        activity = day.get(period, {}).get('title', '')
        if activity:
            highlights.append({
                'day': day['day'],
                'activity': activity
            })

# Display highlights in a grid
if highlights:
    cols = st.columns(3)
    for idx, highlight in enumerate(highlights[:6]):
        with cols[idx % 3]:
            with st.spinner(f"Loading highlight image for {highlight['activity']}..."):
                # Use a different random approach for highlights to ensure variety
                image_data = get_diverse_image(
                    st.session_state.destination, 
                    highlight['activity']
                )
                if image_data:
                    try:
                        st.image(image_data, caption=f"Day {highlight['day']}: {highlight['activity']}", 
                                use_container_width=True)
                    except Exception:
                        st.warning("Could not display highlight image")

# Navigation buttons
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("← Back to Itinerary", use_container_width=True):
        st.switch_page("pages/04_Itinerary_Generation.py")

with col2:
    if st.button("🔄 Refresh Images", use_container_width=True):
        # Clear used image URLs to get fresh images
        st.session_state.used_image_urls = set()
        st.rerun()

with col3:
    if st.button("✨ Start New Trip", use_container_width=True):
        for key in ['destination', 'budget', 'trip_purpose', 'preferences',
                   'itinerary', 'video_path', 'cinematic_trailer', 'used_image_urls']:
            if key in st.session_state:
                del st.session_state[key]
        st.switch_page("main.py")