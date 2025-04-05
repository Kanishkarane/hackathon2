import streamlit as st
import os
import json
from datetime import datetime
import requests
import time
import random
import hashlib
from urllib.parse import quote_plus
import base64

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

# API Keys
# Use environment variables for production or Streamlit secrets
UNSPLASH_ACCESS_KEY = st.secrets.get("UNSPLASH_ACCESS_KEY", "")
PEXELS_API_KEY = st.secrets.get("PEXELS_API_KEY", "")

# For image generation, we'll use Hugging Face Inference API
HUGGINGFACE_API_KEY = st.secrets.get("HUGGINGFACE_API_KEY", "")

# Image cache tracking
image_cache = {}
used_queries = set()
used_image_urls = set()

# Function to create unique cache keys
def create_cache_key(query, source, idx=0, activity_type=""):
    """Create a unique cache key for an image query with more context"""
    hash_obj = hashlib.md5(f"{query}_{source}_{idx}_{activity_type}".encode())
    return f"{source}_{hash_obj.hexdigest()}"

# Improved function to generate better search queries
def generate_enhanced_query(location, activity, index=0):
    """Generate more specific search queries with context awareness"""
    # Base location and activity
    location_terms = location.strip()
    activity_terms = activity.strip()
    
    # Activity type detection for context
    activity_type = "general"
    if any(term in activity_terms.lower() for term in ["restaurant", "food", "dining", "café", "cafe", "eat"]):
        activity_type = "food"
    elif any(term in activity_terms.lower() for term in ["museum", "gallery", "exhibition", "art"]):
        activity_type = "cultural"
    elif any(term in activity_terms.lower() for term in ["park", "garden", "nature", "hike", "trek", "mountain"]):
        activity_type = "nature"
    elif any(term in activity_terms.lower() for term in ["temple", "shrine", "church", "cathedral", "mosque", "religious"]):
        activity_type = "religious"
    elif any(term in activity_terms.lower() for term in ["beach", "sea", "ocean", "coast"]):
        activity_type = "coastal"
    elif any(term in activity_terms.lower() for term in ["nightlife", "club", "bar", "pub", "entertainment"]):
        activity_type = "nightlife"
    elif any(term in activity_terms.lower() for term in ["shopping", "mall", "market", "store"]):
        activity_type = "shopping"
    
    # Generate query variations based on activity type
    queries = [
        f"{activity_terms} in {location_terms}",
        f"{location_terms} {activity_terms} tourist attraction",
        f"{activity_terms} {location_terms} travel photography"
    ]
    
    # Add type-specific queries for better relevance
    if activity_type == "food":
        queries.append(f"{location_terms} cuisine {activity_terms}")
    elif activity_type == "cultural":
        queries.append(f"{activity_terms} cultural site {location_terms}")
    elif activity_type == "nature":
        queries.append(f"{activity_terms} nature {location_terms} landscape")
    elif activity_type == "religious":
        queries.append(f"{activity_terms} religious site {location_terms}")
    elif activity_type == "coastal":
        queries.append(f"{activity_terms} beach {location_terms}")
    
    # Make queries unique
    unique_queries = []
    for query in queries:
        if query not in used_queries:
            used_queries.add(query)
            unique_queries.append(query)
    
    # If all queries are exhausted, create a completely new variant
    if not unique_queries:
        random_suffix = hashlib.md5(f"{activity_terms}_{index}".encode()).hexdigest()[:6]
        new_query = f"{activity_terms} {location_terms} view {random_suffix}"
        unique_queries.append(new_query)
    
    # Return a different query based on the index to ensure variety
    return unique_queries[index % len(unique_queries)], activity_type

# Function to get image from Unsplash API
def get_unsplash_image(query, idx=0, activity_type=""):
    """Get a relevant image from Unsplash API"""
    cache_key = create_cache_key(query, "unsplash", idx, activity_type)
    cache_file = f"data/images/{cache_key}.jpg"
    
    # Check if image is already cached
    if os.path.exists(cache_file):
        return cache_file
    
    # Without API key, use demo images
    if not UNSPLASH_ACCESS_KEY:
        return get_placeholder_image(idx)
    
    try:
        # Use API key-based approach
        encoded_query = quote_plus(query)
        url = f"https://api.unsplash.com/search/photos?query={encoded_query}&per_page=30&orientation=landscape"
        
        headers = {
            "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
        }
        
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if "results" in data and len(data["results"]) > 0:
            results = data["results"]
            
            # Filter out already used images
            unused_results = [r for r in results if r["urls"]["regular"] not in used_image_urls]
            
            # If all images are used, resort to using any available
            if not unused_results:
                unused_results = results
            
            result_idx = idx % len(unused_results)
            image_url = unused_results[result_idx]["urls"]["regular"]
            
            # Mark this URL as used
            used_image_urls.add(image_url)
            
            # Download and cache the image
            img_response = requests.get(image_url)
            if img_response.status_code == 200:
                with open(cache_file, 'wb') as f:
                    f.write(img_response.content)
                return cache_file
    except Exception as e:
        st.warning(f"Unsplash image retrieval error: {str(e)}")
    
    return get_placeholder_image(idx)

# Function to get image from Pexels API
def get_pexels_image(query, idx=0, activity_type=""):
    """Get a relevant image from Pexels API"""
    cache_key = create_cache_key(query, "pexels", idx, activity_type)
    cache_file = f"data/images/{cache_key}.jpg"
    
    # Check if image is already cached
    if os.path.exists(cache_file):
        return cache_file
    
    # Without API key, use demo images
    if not PEXELS_API_KEY:
        return get_placeholder_image(idx)
    
    try:
        # Encode the search query
        encoded_query = quote_plus(query)
        
        # API endpoint
        url = f"https://api.pexels.com/v1/search?query={encoded_query}&per_page=30&orientation=landscape"
        
        headers = {
            "Authorization": PEXELS_API_KEY
        }
        
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if "photos" in data and len(data["photos"]) > 0:
            photos = data["photos"]
            
            # Filter out already used images
            unused_photos = [p for p in photos if p["src"]["large"] not in used_image_urls]
            
            # If all images are used, resort to using any available
            if not unused_photos:
                unused_photos = photos
            
            photo_idx = idx % len(unused_photos)
            photo = unused_photos[photo_idx]
            image_url = photo["src"]["large"]
            
            # Mark this URL as used
            used_image_urls.add(image_url)
            
            # Download and cache the image
            img_response = requests.get(image_url)
            if img_response.status_code == 200:
                with open(cache_file, 'wb') as f:
                    f.write(img_response.content)
                return cache_file
    except Exception as e:
        st.warning(f"Pexels image retrieval error: {str(e)}")
    
    return get_placeholder_image(idx)

# Function to generate image with Hugging Face Inference API
def get_huggingface_image(query, idx=0, activity_type=""):
    """Generate an image using Hugging Face Inference API"""
    cache_key = create_cache_key(query, "huggingface", idx, activity_type)
    cache_file = f"data/images/{cache_key}.jpg"
    
    # Check if image is already cached
    if os.path.exists(cache_file):
        return cache_file
    
    # Without API key, use demo images
    if not HUGGINGFACE_API_KEY:
        return get_placeholder_image(idx)
    
    try:
        # Use a stable diffusion model from Hugging Face
        url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        
        # Create a detailed prompt based on activity type
        style_descriptions = {
            "food": "A professional photograph of ",
            "cultural": "A detailed photograph of ",
            "nature": "A scenic landscape photograph of ",
            "religious": "An architectural photograph of ",
            "coastal": "A beautiful coastal photograph of ",
            "nightlife": "A vibrant nighttime photograph of ",
            "shopping": "A busy photograph of ",
            "general": "A high quality travel photograph of "
        }
        
        style_prefix = style_descriptions.get(activity_type, style_descriptions["general"])
        enhanced_prompt = f"{style_prefix}{query}, travel photography, 4K, high resolution"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
        }
        
        payload = {
            "inputs": enhanced_prompt,
            "parameters": {
                "negative_prompt": "text, watermark, low quality, blurry",
                "guidance_scale": 7.5
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        # Check if the response is valid image data
        if response.status_code == 200:
            with open(cache_file, 'wb') as f:
                f.write(response.content)
            return cache_file
    except Exception as e:
        st.warning(f"Hugging Face image generation error: {str(e)}")
    
    return get_placeholder_image(idx)

# Get a placeholder image from provided URLs
def get_placeholder_image(idx=0):
    """Get a generic travel placeholder image"""
    # Using open CC-licensed travel images
    placeholders = [
        "https://images.pexels.com/photos/2325446/pexels-photo-2325446.jpeg",
        "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800",
        "https://images.pexels.com/photos/1271619/pexels-photo-1271619.jpeg",
        "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1",
        "https://images.pexels.com/photos/3935702/pexels-photo-3935702.jpeg",
    ]
    
    placeholder_url = placeholders[idx % len(placeholders)]
    cache_key = f"placeholder_{idx % len(placeholders)}"
    cache_file = f"data/images/{cache_key}.jpg"
    
    if not os.path.exists(cache_file):
        try:
            img_response = requests.get(placeholder_url)
            if img_response.status_code == 200:
                with open(cache_file, 'wb') as f:
                    f.write(img_response.content)
        except:
            # Fall back to a local placeholder
            return "https://via.placeholder.com/600x400?text=Travel+Image"
    
    return cache_file if os.path.exists(cache_file) else placeholder_url

# Use a local LLM for enhanced image descriptions
def generate_image_description(location, activity):
    """Generate an enhanced image description using a local LLM"""
    try:
        # Prepare prompt for LLM
        prompt = f"""Create a detailed, accurate description for a travel image of '{activity}' in '{location}'. 
        Focus on visual elements like landscape, architecture, colors, and atmosphere. 
        Keep it under 50 words and don't include any non-visual elements."""
        
        # In real implementation, call your local LLM here
        # For now, we'll provide some handcrafted descriptions based on activity type
        if "restaurant" in activity.lower() or "food" in activity.lower() or "dining" in activity.lower():
            return f"Authentic local cuisine from {location}, showcasing traditional dishes with fresh ingredients, vibrant colors, and artful presentation."
        elif "museum" in activity.lower() or "gallery" in activity.lower():
            return f"Interior of {activity} in {location}, highlighting cultural artifacts and exhibitions in an elegant, well-lit space."
        elif "park" in activity.lower() or "garden" in activity.lower() or "nature" in activity.lower():
            return f"Lush greenery and natural beauty at {activity} in {location}, with scenic pathways and peaceful surroundings."
        elif "beach" in activity.lower() or "sea" in activity.lower() or "ocean" in activity.lower():
            return f"Crystal clear waters and sandy shoreline at {activity}, {location}, with gentle waves and stunning coastal views."
        elif "temple" in activity.lower() or "church" in activity.lower() or "mosque" in activity.lower():
            return f"Architectural details of {activity} in {location}, showcasing historical religious craftsmanship and serene atmosphere."
        elif "shopping" in activity.lower() or "market" in activity.lower():
            return f"Bustling {activity} in {location} with colorful displays of local goods, crafts, and produce."
        else:
            return f"Scenic view of {activity} in {location}, a must-visit destination with distinctive character and atmosphere."
    except:
        return f"Exploring {activity} in the beautiful destination of {location}."

# Function to get smart image
def get_smart_image(location, activity, index=0):
    """Smart function to get the most relevant image using multiple sources"""
    # Create a unique context-based query
    query, activity_type = generate_enhanced_query(location, activity, index)
    
    # Use different API source based on context and availability
    image_sources = []
    
    # Prioritize different sources based on activity type and API key availability
    if UNSPLASH_ACCESS_KEY:
        image_sources.append((get_unsplash_image, "Unsplash"))
    
    if PEXELS_API_KEY:
        image_sources.append((get_pexels_image, "Pexels"))
    
    if HUGGINGFACE_API_KEY:
        image_sources.append((get_huggingface_image, "Hugging Face"))
    
    # If no API keys are available, just use placeholders
    if not image_sources:
        return get_placeholder_image(index)
    
    # Shuffle sources based on index to ensure variety
    random.seed(index)
    random.shuffle(image_sources)
    
    # Try each source
    for img_func, source_name in image_sources:
        try:
            # Calculate a unique index for this source
            source_idx = (index + hash(source_name)) % 100
            image_path = img_func(query, source_idx, activity_type)
            if image_path:
                return image_path
        except Exception as e:
            continue
    
    # If all else fails, use placeholders
    return get_placeholder_image(index)

# Activity fingerprint to ensure uniqueness
def create_activity_fingerprint(location, activity, day_idx, period_idx):
    """Create a unique fingerprint for this specific activity instance"""
    return f"{location}_{activity}_{day_idx}_{period_idx}"

# Function to get unique image for each activity
def get_unique_activity_image(location, activity, day_idx, period_idx):
    """Ensure each activity gets a unique image"""
    # Create a unique identifier for this activity instance
    activity_fingerprint = create_activity_fingerprint(location, activity, day_idx, period_idx)
    
    # Check if we already have an image for this exact activity instance
    if activity_fingerprint in image_cache:
        return image_cache[activity_fingerprint]
    
    # Calculate base index using day and period for deterministic results
    base_idx = (day_idx * 100) + (period_idx * 10)
    
    # Get image
    image_path = get_smart_image(location, activity, base_idx)
    
    # Cache the result
    image_cache[activity_fingerprint] = image_path
    return image_path

# Clear cache for forced refresh
if st.session_state.get('refresh_images', False):
    # Clear memory caches
    image_cache.clear()  
    used_queries.clear()
    used_image_urls.clear()
    
    # Clear file cache if requested
    for file in os.listdir('data/images'):
        if file.endswith('.jpg'):
            try:
                os.remove(os.path.join('data/images', file))
            except:
                pass
                
    st.session_state.refresh_images = False

# Display daily activities with images
for day_idx, day in enumerate(daily_plan):
    st.markdown(f"### Day {day['day']}: {day['day_name']}")

    # Create three columns for morning, afternoon, and evening
    col1, col2, col3 = st.columns(3)

    # Morning activity
    with col1:
        st.subheader("Morning")
        morning_activity = day.get('morning', {}).get('title', '')
        description = day.get('morning', {}).get('description', '')
        if morning_activity:
            with st.spinner(f"Finding image for {morning_activity}..."):
                image_path = get_unique_activity_image(
                    st.session_state.destination, 
                    morning_activity, 
                    day_idx, 
                    0
                )
                # Generate enhanced description
                enhanced_description = generate_image_description(st.session_state.destination, morning_activity)
                st.image(image_path, caption=enhanced_description, use_container_width=True)
                st.markdown(f"**{morning_activity}**")
                if description:
                    with st.expander("Details"):
                        st.write(description)

    # Afternoon activity
    with col2:
        st.subheader("Afternoon")
        afternoon_activity = day.get('afternoon', {}).get('title', '')
        description = day.get('afternoon', {}).get('description', '')
        if afternoon_activity:
            with st.spinner(f"Finding image for {afternoon_activity}..."):
                image_path = get_unique_activity_image(
                    st.session_state.destination, 
                    afternoon_activity, 
                    day_idx, 
                    1
                )
                # Generate enhanced description
                enhanced_description = generate_image_description(st.session_state.destination, afternoon_activity)
                st.image(image_path, caption=enhanced_description, use_container_width=True)
                st.markdown(f"**{afternoon_activity}**")
                if description:
                    with st.expander("Details"):
                        st.write(description)

    # Evening activity
    with col3:
        st.subheader("Evening")
        evening_activity = day.get('evening', {}).get('title', '')
        description = day.get('evening', {}).get('description', '')
        if evening_activity:
            with st.spinner(f"Finding image for {evening_activity}..."):
                image_path = get_unique_activity_image(
                    st.session_state.destination, 
                    evening_activity, 
                    day_idx, 
                    2
                )
                # Generate enhanced description
                enhanced_description = generate_image_description(st.session_state.destination, evening_activity)
                st.image(image_path, caption=enhanced_description, use_container_width=True)
                st.markdown(f"**{evening_activity}**")
                if description:
                    with st.expander("Details"):
                        st.write(description)

    st.markdown("---")

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
    for idx, highlight in enumerate(highlights[:6]):  # Show top 6 highlights
        with cols[idx % 3]:
            with st.spinner(f"Finding highlight image..."):
                # Use a different approach for highlights
                image_path = get_smart_image(
                    st.session_state.destination, 
                    highlight['activity'],
                    1000 + idx  # Use 1000+ to ensure different from main listing
                )
                # Generate custom caption
                caption = generate_image_description(st.session_state.destination, highlight['activity'])
                st.image(image_path, caption=f"Day {highlight['day']}: {highlight['activity']}", use_container_width=True)

# Navigation buttons
st.markdown("---")
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    if st.button("← Back to Itinerary", use_container_width=True):
        st.switch_page("pages/04_Itinerary_Generation.py")

with col2:
    if st.button("Refresh Images", use_container_width=True):
        # Set flag to clear used combinations
        st.session_state.refresh_images = True
        st.rerun()
        
with col3:
    if st.button("Book Your Trip →", use_container_width=True):
        st.switch_page("pages/07_Bookings.py")

with col4:
    if st.button("Start New Trip", use_container_width=True):
        for key in ['destination', 'budget', 'trip_purpose', 'preferences', 
                   'itinerary', 'video_path', 'cinematic_trailer']:
            if key in st.session_state:
                del st.session_state[key]
        st.switch_page("main.py")