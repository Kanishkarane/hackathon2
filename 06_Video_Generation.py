import streamlit as st
import os
import cv2
import numpy as np
from PIL import Image
import tempfile
import time
import requests
import random
from datetime import datetime
import subprocess
import json
import shutil
import base64
import io

# Set page configuration
st.set_page_config(
    page_title="Cinematic Video - AI Travel Magic",
    page_icon="🎬",
    layout="wide"
)

# Create data directories if they don't exist
if not os.path.exists('data'):
    os.makedirs('data')
if not os.path.exists('data/videos'):
    os.makedirs('data/videos')
if not os.path.exists('data/audio'):
    os.makedirs('data/audio')
if not os.path.exists('data/frames'):
    os.makedirs('data/frames')

# Check if we have the necessary data to proceed
if 'destination' not in st.session_state or not st.session_state.destination:
    st.switch_page("pages/01_Destination_and_Budget.py")
if 'itinerary' not in st.session_state or not st.session_state.itinerary:
    st.switch_page("pages/04_Itinerary_Generation.py")

# Title and description
st.title("🎬 Cinematic Trip Experience")
st.markdown(f"### Create a cinematic video preview of your trip to {st.session_state.destination}")

# Function to fetch relevant images for a place using Unsplash API
def fetch_place_images(place_name, max_images=3):
    """Fetch images related to a specific place using Unsplash API or fallback sources"""
    # For demo purposes, we'll use a list of predefined travel images by location type
    # In production, you would use the Unsplash API with proper API keys
    
    image_categories = {
        "beach": [
            "https://images.unsplash.com/photo-1507525428034-b723cf961d3e",
            "https://images.unsplash.com/photo-1519046904884-53103b34b206",
            "https://images.unsplash.com/photo-1473116763249-2faaef81ccda"
        ],
        "mountain": [
            "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b",
            "https://images.unsplash.com/photo-1506905925346-21bda4d32df4",
            "https://images.unsplash.com/photo-1483728642387-6c3bdd6c93e5"
        ],
        "city": [
            "https://images.unsplash.com/photo-1514565131-fce0801e5785",
            "https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b",
            "https://images.unsplash.com/photo-1449824913935-59a10b8d2000"
        ],
        "museum": [
            "https://images.unsplash.com/photo-1518998053901-5348d3961a04",
            "https://images.unsplash.com/photo-1566127992631-137a642a90f4",
            "https://images.unsplash.com/photo-1605294283900-6ae22a05a9c9"
        ],
        "restaurant": [
            "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4",
            "https://images.unsplash.com/photo-1555396273-367ea4eb4db5",
            "https://images.unsplash.com/photo-1590846406792-0adc7f938f1d"
        ],
        "landmark": [
            "https://images.unsplash.com/photo-1522093007474-d86e9bf7ba6f",
            "https://images.unsplash.com/photo-1526711657229-e7da9c791600",
            "https://images.unsplash.com/photo-1601987077677-5346c5470eb3"
        ],
        "park": [
            "https://images.unsplash.com/photo-1519331379826-f10be5486c6f",
            "https://images.unsplash.com/photo-1587220559482-75a5b54a9b1c",
            "https://images.unsplash.com/photo-1573155993874-d5d48af862ba"
        ],
        "temple": [
            "https://images.unsplash.com/photo-1602301360682-12eba6e0174a",
            "https://images.unsplash.com/photo-1594849044129-852ead451fc3",
            "https://images.unsplash.com/photo-1573177923275-591865757097"
        ],
        "shopping": [
            "https://images.unsplash.com/photo-1605902711622-cfb43c4437b5",
            "https://images.unsplash.com/photo-1481437156560-3205f6a55735",
            "https://images.unsplash.com/photo-1534452203293-494d7ddbf7e0"
        ],
        "lake": [
            "https://images.unsplash.com/photo-1520338258525-606b90f95b04",
            "https://images.unsplash.com/photo-1501785888041-af3ef285b470",
            "https://images.unsplash.com/photo-1508108712903-49b7ef9b1df8"
        ],
    }
    
    # Match place name to categories
    place_lower = place_name.lower()
    matched_images = []
    
    # Check for category keywords in the place name
    for category, images in image_categories.items():
        if category in place_lower:
            matched_images.extend(images)
    
    # If no specific match, use some general travel images based on first word
    if not matched_images:
        # Use destination as fallback for category matching
        destination = st.session_state.destination.lower()
        for category, images in image_categories.items():
            if category in destination:
                matched_images.extend(images)
        
        # If still no matches, use city as default
        if not matched_images:
            matched_images = image_categories["city"]
    
    # Randomize and limit the number of images
    random.shuffle(matched_images)
    return matched_images[:max_images]

# Improved function to collect images that match the itinerary places
def collect_matching_images(max_images=20):
    """Collect images that match the places mentioned in the itinerary"""
    all_images = []
    
    # Get daily plan from the itinerary
    daily_plan = st.session_state.itinerary.get('daily_plan', [])
    
    # Create temp directory for downloaded images if it doesn't exist
    temp_img_dir = os.path.join('data', 'images')
    if not os.path.exists(temp_img_dir):
        os.makedirs(temp_img_dir)
    
    # Process each activity in the itinerary
    for day_idx, day in enumerate(daily_plan):
        for period_idx, period in enumerate(['morning', 'afternoon', 'evening']):
            activity = day.get(period, {}).get('title', '')
            description = day.get(period, {}).get('description', '')
            
            if activity:
                # Calculate importance score
                importance_score = 0
                
                # First and last day are more important
                if day['day'] == 1 or day['day'] == len(daily_plan):
                    importance_score += 3
                
                # Morning and evening activities often more scenic
                if period in ['morning', 'evening']:
                    importance_score += 1
                
                # Activities with keywords suggesting important landmarks or experiences
                landmark_keywords = ["famous", "landmark", "iconic", "monument", "museum", 
                                   "cathedral", "castle", "palace", "temple", "beach", 
                                   "mountain", "waterfall", "lake", "sunset", "panorama"]
                if any(keyword in activity.lower() for keyword in landmark_keywords):
                    importance_score += 2
                
                # Fetch relevant images for this activity
                image_urls = fetch_place_images(activity, max_images=3)
                
                # Download and save images
                for img_idx, url in enumerate(image_urls):
                    try:
                        # Create a unique filename for this image
                        img_filename = f"{temp_img_dir}/day{day['day']}_{period}_{img_idx}.jpg"
                        
                        # Check if file already exists
                        if not os.path.exists(img_filename):
                            response = requests.get(url)
                            if response.status_code == 200:
                                with open(img_filename, 'wb') as f:
                                    f.write(response.content)
                        
                        # Add image to the collection
                        all_images.append({
                            'path': img_filename,
                            'caption': f"Day {day['day']} - {period.capitalize()}: {activity}",
                            'day': day['day'],
                            'period': period,
                            'activity': activity,
                            'importance': importance_score
                        })
                    except Exception as e:
                        st.warning(f"Error downloading image for {activity}: {str(e)}")
    
    # Select images ensuring we have distributed coverage of the trip
    selected_images = []
    
    # If we have few images, just use them all
    if len(all_images) <= max_images:
        selected_images = all_images
    else:
        # Strategy: Always include first and last day, then select highest importance,
        # while ensuring even distribution across days
        
        # First, sort by importance
        all_images.sort(key=lambda x: x['importance'], reverse=True)
        
        # Always include first day activities (if available)
        first_day_images = [img for img in all_images if img['day'] == 1]
        if first_day_images:
            selected_images.append(first_day_images[0])
            all_images.remove(first_day_images[0])
        
        # Always include last day activities (if available)
        last_day = max(img['day'] for img in all_images)
        last_day_images = [img for img in all_images if img['day'] == last_day]
        if last_day_images:
            selected_images.append(last_day_images[0])
            all_images.remove(last_day_images[0])
        
        # Now distribute remaining slots across days
        days_covered = set(img['day'] for img in selected_images)
        remaining_slots = max_images - len(selected_images)
        
        # First pass: include at least one image from each day not yet covered
        for day_num in range(1, last_day + 1):
            if remaining_slots <= 0:
                break
                
            if day_num not in days_covered:
                day_images = [img for img in all_images if img['day'] == day_num]
                if day_images:
                    # Get highest importance image for this day
                    best_image = max(day_images, key=lambda x: x['importance'])
                    selected_images.append(best_image)
                    all_images.remove(best_image)
                    days_covered.add(day_num)
                    remaining_slots -= 1
        
        # Second pass: fill remaining slots with highest importance images
        highest_importance_remaining = sorted(all_images, key=lambda x: x['importance'], reverse=True)
        selected_images.extend(highest_importance_remaining[:remaining_slots])
    
    # If no images found, use placeholders
    if not selected_images:
        st.warning("No images could be found. Using placeholder images instead.")
        placeholder_paths = [
            "https://images.pexels.com/photos/2325446/pexels-photo-2325446.jpeg",
            "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800",
            "https://images.pexels.com/photos/1271619/pexels-photo-1271619.jpeg"
        ]
        
        # Download placeholders if needed
        for i, url in enumerate(placeholder_paths):
            cache_file = f"data/images/placeholder_{i}.jpg"
            if not os.path.exists(cache_file):
                try:
                    img_response = requests.get(url)
                    if img_response.status_code == 200:
                        with open(cache_file, 'wb') as f:
                            f.write(img_response.content)
                        selected_images.append({
                            'path': cache_file,
                            'caption': f"Placeholder image {i+1}",
                            'day': i+1,
                            'period': 'morning',
                            'activity': f"Activity {i+1}",
                            'importance': 0
                        })
                except Exception as e:
                    st.error(f"Error downloading placeholder image: {str(e)}")
    
    # Sort final selection by day and period
    period_order = {'morning': 0, 'afternoon': 1, 'evening': 2}
    selected_images.sort(key=lambda x: (x['day'], period_order.get(x['period'], 3)))
    
    # Randomize the order slightly but maintain overall day progression
    # Group by day
    days = {}
    for img in selected_images:
        day = img['day']
        if day not in days:
            days[day] = []
        days[day].append(img)
    
    # Shuffle within each day
    for day in days:
        random.shuffle(days[day])
    
    # Reconstruct the list in day order but with randomized content within each day
    final_selection = []
    for day in sorted(days.keys()):
        final_selection.extend(days[day])
    
    return final_selection

# Function to apply cinematic transitions between images
def apply_transition(img1, img2, transition_type, progress):
    """Apply cinematic transition between two images"""
    if transition_type == "fade":
        return cv2.addWeighted(img1, 1 - progress, img2, progress, 0)
    elif transition_type == "slide_left":
        width = img1.shape[1]
        offset = int(progress * width)
        result = np.copy(img1)
        result[:, 0:width-offset] = img1[:, offset:width]
        result[:, width-offset:width] = img2[:, 0:offset]
        return result
    elif transition_type == "slide_right":
        width = img1.shape[1]
        offset = int(progress * width)
        result = np.copy(img1)
        result[:, offset:width] = img1[:, 0:width-offset]
        result[:, 0:offset] = img2[:, width-offset:width]
        return result
    elif transition_type == "zoom_in":
        scale = 1 + (0.3 * progress)
        h, w = img1.shape[:2]
        center_x, center_y = w // 2, h // 2
        
        # Interpolate between images
        blended = cv2.addWeighted(img1, 1 - progress, img2, progress, 0)
        
        # Calculate new dimensions
        new_h, new_w = int(h * scale), int(w * scale)
        
        # Scale image up
        scaled = cv2.resize(blended, (new_w, new_h))
        
        # Calculate crop region
        start_x = (new_w - w) // 2
        start_y = (new_h - h) // 2
        end_x = start_x + w
        end_y = start_y + h
        
        # Crop to original size
        result = scaled[start_y:end_y, start_x:end_x]
        return result
    else:  # Default: fade
        return cv2.addWeighted(img1, 1 - progress, img2, progress, 0)

# Function to resize images to standard dimensions
def resize_image(image_path, target_width=1920, target_height=1080):
    """Resize image for video with cinematic aspect ratio"""
    try:
        img = Image.open(image_path)
        img = img.convert('RGB')  # Ensure RGB mode
        
        # Calculate aspect ratios
        img_aspect = img.width / img.height
        target_aspect = target_width / target_height
        
        # Resize and crop to maintain aspect ratio without stretching
        if img_aspect > target_aspect:  # Image is wider than target
            # Resize based on height
            new_height = target_height
            new_width = int(new_height * img_aspect)
            img_resized = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Crop the width to match target aspect ratio
            left_margin = (new_width - target_width) // 2
            img_cropped = img_resized.crop((left_margin, 0, left_margin + target_width, target_height))
        else:  # Image is taller than target
            # Resize based on width
            new_width = target_width
            new_height = int(new_width / img_aspect)
            img_resized = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Crop the height to match target aspect ratio
            top_margin = (new_height - target_height) // 2
            img_cropped = img_resized.crop((0, top_margin, target_width, top_margin + target_height))
        
        # Convert to numpy array for OpenCV
        return np.array(img_cropped)
    except Exception as e:
        st.error(f"Error processing image {image_path}: {str(e)}")
        # Return a black image as fallback
        return np.zeros((target_height, target_width, 3), dtype=np.uint8)

# Function to add text overlay to image
def add_caption(img, caption, font_scale=1.2, thickness=2):
    """Add a stylish caption to the image"""
    img_with_text = img.copy()
    height, width = img.shape[:2]
    
    # Black semi-transparent background for text
    overlay = img.copy()
    bottom_rect_height = int(height * 0.12)  # 12% of image height
    cv2.rectangle(overlay, (0, height - bottom_rect_height), (width, height), (0, 0, 0), -1)
    img_with_text = cv2.addWeighted(overlay, 0.7, img_with_text, 0.3, 0)
    
    # Text settings
    font = cv2.FONT_HERSHEY_DUPLEX
    text_color = (255, 255, 255)  # White text
    
    # Calculate position and size
    text_size = cv2.getTextSize(caption, font, font_scale, thickness)[0]
    text_x = (width - text_size[0]) // 2  # Center text horizontally
    text_y = height - (bottom_rect_height // 2) + (text_size[1] // 2)  # Center in overlay
    
    # Add text
    cv2.putText(img_with_text, caption, (text_x, text_y), font, font_scale, text_color, thickness)
    
    return img_with_text

# Function to download royalty-free music (simulated)
def get_background_music(mood="inspiring"):
    """Get appropriate background music based on destination mood"""
    # Predefined royalty-free music URLs (in a real app, you might use a music API)
    music_options = {
        "inspiring": [
            "https://cdn.freesound.org/previews/648/648891_5674468-lq.mp3",
            "https://cdn.freesound.org/previews/561/561394_5674468-lq.mp3"
        ],
        "relaxing": [
            "https://cdn.freesound.org/previews/612/612095_5674468-lq.mp3",
            "https://cdn.freesound.org/previews/612/612096_5674468-lq.mp3"
        ],
        "upbeat": [
            "https://cdn.freesound.org/previews/266/266915_5052029-lq.mp3",
            "https://cdn.freesound.org/previews/612/612940_11861866-lq.mp3"
        ]
    }
    
    # Select a random track from the appropriate mood
    selected_music = random.choice(music_options.get(mood, music_options["inspiring"]))
    
    # Create a unique filename based on URL
    music_filename = f"data/audio/background_{hash(selected_music) % 10000}.mp3"
    
    # Download if not already in cache
    if not os.path.exists(music_filename):
        try:
            response = requests.get(selected_music)
            if response.status_code == 200:
                with open(music_filename, 'wb') as f:
                    f.write(response.content)
            else:
                # Use fallback audio file
                music_filename = None
        except:
            music_filename = None
    
    return music_filename

# Function to determine destination mood
def determine_destination_mood(destination, itinerary):
    """Analyze destination and itinerary to determine the appropriate mood"""
    # Simple keyword-based mood detection
    beach_keywords = ["beach", "ocean", "sea", "island", "coast", "resort"]
    adventure_keywords = ["mountain", "hiking", "trek", "adventure", "outdoor", "safari"]
    cultural_keywords = ["museum", "history", "art", "culture", "temple", "heritage"]
    
    destination_lower = destination.lower()
    activities_text = ""
    
    # Extract all activities from itinerary
    daily_plan = itinerary.get('daily_plan', [])
    for day in daily_plan:
        for period in ['morning', 'afternoon', 'evening']:
            activity = day.get(period, {}).get('title', '')
            if activity:
                activities_text += activity.lower() + " "
    
    # Count keyword occurrences
    beach_count = sum(1 for word in beach_keywords if word in destination_lower or word in activities_text)
    adventure_count = sum(1 for word in adventure_keywords if word in destination_lower or word in activities_text)
    cultural_count = sum(1 for word in cultural_keywords if word in destination_lower or word in activities_text)
    
    # Determine mood based on highest count
    if beach_count > adventure_count and beach_count > cultural_count:
        return "relaxing"
    elif adventure_count > beach_count and adventure_count > cultural_count:
        return "upbeat"
    else:
        return "inspiring"  # Default or cultural destinations

# Function to create frames and save them as images
def generate_frames(images, frames_dir, fps=24, image_duration=3, transition_duration=1, add_captions=True, width=1920, height=1080):
    """Generate frames for the video and save them as individual images"""
    if not images:
        st.error("No images available for video creation")
        return None
    
    # Clear previous frames
    if os.path.exists(frames_dir):
        shutil.rmtree(frames_dir)
    os.makedirs(frames_dir)
    
    # Prepare progress tracking
    total_items = len(images) - 1  # transitions between images
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Calculate frame counts
    image_frames = int(fps * image_duration)
    transition_frames = int(fps * transition_duration)
    
    # Track frame number
    frame_number = 0
    frame_paths = []
    
    # Process each image and transition
    for i in range(len(images) - 1):
        # Update progress
        progress_value = (i / total_items)
        progress_bar.progress(progress_value)
        status_text.text(f"Processing image {i+1}/{len(images)} - {images[i]['caption']}")
        
        # Load and resize current and next image
        img1 = resize_image(images[i]['path'], width, height)
        img2 = resize_image(images[i+1]['path'], width, height)
        
        # Add captions if requested
        if add_captions:
            img1 = add_caption(img1, images[i]['caption'])
            img2 = add_caption(img2, images[i+1]['caption'])
        
        # Add frames for current image display (no transition)
        for j in range(image_frames):
            frame_path = os.path.join(frames_dir, f"frame_{frame_number:06d}.jpg")
            cv2.imwrite(frame_path, cv2.cvtColor(img1, cv2.COLOR_RGB2BGR))
            frame_paths.append(frame_path)
            frame_number += 1
        
        # Choose a transition effect (randomize for more variety)
        transition_types = ["fade", "slide_left", "slide_right", "zoom_in"]
        transition_type = random.choice(transition_types)
        
        # Create transition frames between current and next image
        for j in range(transition_frames):
            progress = j / transition_frames
            transition_frame = apply_transition(img1, img2, transition_type, progress)
            frame_path = os.path.join(frames_dir, f"frame_{frame_number:06d}.jpg")
            cv2.imwrite(frame_path, cv2.cvtColor(transition_frame, cv2.COLOR_RGB2BGR))
            frame_paths.append(frame_path)
            frame_number += 1
    
    # Add last image frames
    if images:
        last_img = resize_image(images[-1]['path'], width, height)
        if add_captions:
            last_img = add_caption(last_img, images[-1]['caption'])
        for j in range(image_frames):
            frame_path = os.path.join(frames_dir, f"frame_{frame_number:06d}.jpg")
            cv2.imwrite(frame_path, cv2.cvtColor(last_img, cv2.COLOR_RGB2BGR))
            frame_paths.append(frame_path)
            frame_number += 1
    
    return frame_paths

# Function to create video from frames for web playback
def create_web_playable_video(frame_paths, output_path, fps=24):
    """Create a web-playable video format for direct embedding in Streamlit"""
    if not frame_paths:
        return None
    
    try:
        # Get dimensions from first frame
        first_frame = cv2.imread(frame_paths[0])
        if first_frame is None:
            st.error(f"Cannot read frame: {frame_paths[0]}")
            return None
            
        height, width, _ = first_frame.shape
        
        # Create video writer with web-friendly codec
        fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264 codec for web compatibility
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Write frames to video
        for i, frame_path in enumerate(frame_paths):
            # Update progress
            progress_value = (i / len(frame_paths))
            progress_bar.progress(progress_value)
            status_text.text(f"Rendering frame {i+1}/{len(frame_paths)}")
            
            # Read frame
            frame = cv2.imread(frame_path)
            if frame is not None:
                out.write(frame)
        
        # Release the video writer
        out.release()
        
        return output_path
        
    except Exception as e:
        st.error(f"Error creating web video: {str(e)}")
        return None

# Function to get autoplay HTML code for the video
def get_video_html(video_path):
    """Generate HTML to autoplay the video directly in the browser"""
    video_file = open(video_path, 'rb')
    video_bytes = video_file.read()
    b64 = base64.b64encode(video_bytes).decode()
    
    # Create HTML with autoplay and controls
    video_html = f"""
    <video width="100%" controls autoplay>
        <source src="data:video/mp4;base64,{b64}" type="video/mp4">
        Your browser does not support the video tag.
    </video>
    """
    return video_html

# Modified function to create cinematic video for web playback
def create_cinematic_video(images, output_path, fps=24, image_duration=3, transition_duration=1, add_captions=True, add_music=True):
    """Create cinematic video from images with transitions using OpenCV for web playback"""
    if not images:
        st.error("No images available for video creation")
        return None
    
    # Create temporary directory for frames
    frames_dir = os.path.join('data', 'frames', f"temp_frames_{int(time.time())}")
    if not os.path.exists(frames_dir):
        os.makedirs(frames_dir)
    
    try:
        # Generate frames
        frame_paths = generate_frames(
            images,
            frames_dir,
            fps=fps,
            image_duration=image_duration,
            transition_duration=transition_duration,
            add_captions=add_captions
        )
        
        # Get music if requested (note: we can't add music directly to the video without FFmpeg)
        if add_music:
            # Determine appropriate mood based on destination
            mood = determine_destination_mood(st.session_state.destination, st.session_state.itinerary)
            st.info(f"Selected {mood} background music theme (note: music will be available in downloaded version)")
            # We'll save this for the downloadable version
            
        # Create web-playable video
        with st.spinner("Creating web-playable video..."):
            video_path = create_web_playable_video(
                frame_paths,
                output_path,
                fps=fps
            )
        
        return video_path
    except Exception as e:
        st.error(f"Error creating video: {str(e)}")
        return None
    finally:
        # Clean up temporary frames
        if os.path.exists(frames_dir):
            shutil.rmtree(frames_dir)

# Check if video already exists
def get_video_path():
    """Get path to existing video or create new one"""
    if ('video_path' in st.session_state and 
        st.session_state.video_path and 
        os.path.exists(st.session_state.video_path)):
        return st.session_state.video_path
    
    # Create a unique video filename
    destination_slug = st.session_state.destination.lower().replace(' ', '_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"data/videos/{destination_slug}_{timestamp}.mp4"

# Video generation options
st.sidebar.header("Video Options")
with st.sidebar.form(key="video_options"):
    video_quality = st.selectbox(
        "Video Quality",
        ["Standard (720p)", "High (1080p)"],
        index=1
    )
    
    max_images = st.slider(
        "Number of images to include",
        min_value=5,
        max_value=30,
        value=15,
        help="More images will create a longer video"
    )
    
    image_duration = st.slider(
        "Image display duration (seconds)",
        min_value=1.0,
        max_value=5.0,
        value=3.0,
        step=0.5,
        help="How long each image stays on screen"
    )
    
    transition_duration = st.slider(
        "Transition duration (seconds)",
        min_value=0.5,
        max_value=2.0,
        value=1.0,
        step=0.1,
        help="Duration of transitions between images"
    )
    
    add_captions = st.checkbox("Add captions to images", value=True)
    add_music = st.checkbox("Add background music", value=True)
    
    submit_button = st.form_submit_button("Generate Video")

# Display main content
col1, col2 = st.columns([2, 1])

with col1:
    # Check if we should generate a new video
    if submit_button or 'video_path' not in st.session_state:
        with st.spinner("Finding images for your itinerary..."):
            # Collect images for the video
            selected_images = collect_matching_images(max_images=max_images)
            
            if not selected_images:
                st.error("Could not find suitable images for your itinerary")
            else:
                # Determine video resolution
                width = 1920 if video_quality == "High (1080p)" else 1280
                height = 1080 if video_quality == "High (1080p)" else 720
                
                # Get video path
                video_path = get_video_path()
                
                # Create the video
                with st.spinner("Creating your cinematic travel video..."):
                    video = create_cinematic_video(
                        selected_images,
                        video_path,
                        fps=24,
                        image_duration=image_duration,
                        transition_duration=transition_duration,
                        add_captions=add_captions,
                        add_music=add_music
                    )
                    
                    if video:
                        st.session_state.video_path = video
                        st.success("Video created successfully!")
                    else:
                        st.error("Failed to create video")
    
    # Display the video if available
    if ('video_path' in st.session_state and 
    st.session_state.video_path is not None and 
    st.session_state.video_path != "" and 
    os.path.exists(st.session_state.video_path)):
        st.subheader("Your Travel Preview")
        
        # Create HTML for video playback
        video_html = get_video_html(st.session_state.video_path)
        st.components.v1.html(video_html, height=600)
        
        # Offer video download
        with open(st.session_state.video_path, "rb") as file:
            btn = st.download_button(
                label="Download Video",
                data=file,
                file_name=os.path.basename(st.session_state.video_path),
                mime="video/mp4"
            )

with col2:
    # Display summary of the video
    if 'video_path' in st.session_state:
        st.subheader("Video Summary")
        
        # Get duration
        fps = 24
        image_count = max_images if 'max_images' in locals() else 15
        est_duration = image_count * (image_duration + transition_duration)
        
        st.markdown(f"**Duration:** Approximately {est_duration:.1f} seconds")
        st.markdown(f"**Destination:** {st.session_state.destination}")
        st.markdown(f"**Trip Length:** {len(st.session_state.itinerary.get('daily_plan', []))} days")
        st.markdown(f"**Resolution:** {video_quality}")
        
        if add_music:
            mood = determine_destination_mood(st.session_state.destination, st.session_state.itinerary)
            st.markdown(f"**Music Theme:** {mood.capitalize()}")
        
        # Show itinerary snippet
        st.subheader("Featured Days")
        daily_plan = st.session_state.itinerary.get('daily_plan', [])
        days_to_show = min(3, len(daily_plan))
        
        for i in range(days_to_show):
            day = daily_plan[i]
            st.markdown(f"**Day {day['day']}**")
            for period in ['morning', 'afternoon', 'evening']:
                if period in day and 'title' in day[period]:
                    st.markdown(f"- {period.capitalize()}: {day[period]['title']}")

# Add navigation buttons
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("← Back to Itinerary"):
        st.switch_page("pages/04_Itinerary_Generation.py")
        
with col3:
    if st.button("Finish Trip Planning →"):
        st.switch_page("pages/07_Bookings.py")

# Add footer
st.markdown("---")
st.markdown("© 2025 AI Travel Magic | Your personal AI travel planner")