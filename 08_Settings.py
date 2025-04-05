import streamlit as st
import json
import os
import time

# Set page configuration
st.set_page_config(
    page_title="Settings - AI Travel Magic",
    page_icon="⚙️",
    layout="wide"
)

# Function to create and update the config file
def save_settings(settings_dict):
    # Create .streamlit directory if it doesn't exist
    if not os.path.exists('.streamlit'):
        os.makedirs('.streamlit')
    
    # Parse the config to update only the theme section
    server_section = """
[server]
headless = true
address = "0.0.0.0"
port = 5000
"""
    
    # Create theme section based on settings
    theme_section = """
[theme]
primaryColor = "{}"
backgroundColor = "{}"
secondaryBackgroundColor = "{}"
textColor = "{}"
font = "{}"
""".format(
        settings_dict['primaryColor'],
        settings_dict['backgroundColor'],
        settings_dict['secondaryBackgroundColor'],
        settings_dict['textColor'],
        settings_dict['font']
    )
    
    # Combine sections
    new_config = server_section + theme_section
    
    # Write the updated config
    config_path = '.streamlit/config.toml'
    with open(config_path, 'w') as f:
        f.write(new_config)
    
    return True

# Title and description
st.title("⚙️ Settings")
st.markdown("### Customize your app experience")

st.markdown("""
<div class="highlight-box">
    <p>Personalize your travel planning experience by adjusting the app's appearance and other settings.</p>
</div>
""", unsafe_allow_html=True)

# Function to load settings from config.toml
def load_settings_from_config():
    import re  # Import re at the top of the function
    
    try:
        config_path = '.streamlit/config.toml'
        if not os.path.exists(config_path):
            # Return default settings if config doesn't exist
            return {
                'theme': 'Light',
                'primaryColor': '#FF4B4B',
                'backgroundColor': '#FFFFFF',
                'secondaryBackgroundColor': '#F0F2F6',
                'textColor': '#262730',
                'font': 'sans serif',
                'notifications': True,
                'animations': True,
            }
        
        # Read the config file
        with open(config_path, 'r') as f:
            config_content = f.read()
        
        # Extract theme settings
        settings = {
            'notifications': True,  # Default value
            'animations': True,     # Default value
            'font': 'sans serif',   # Default value
            'theme': 'Light'        # Default value
        }
        
        # Parse the primary color
        if 'primaryColor' in config_content:
            primary_match = re.search(r'primaryColor\s*=\s*"([^"]+)"', config_content)
            if primary_match:
                settings['primaryColor'] = primary_match.group(1)
        
        # Parse the background color
        if 'backgroundColor' in config_content:
            bg_match = re.search(r'backgroundColor\s*=\s*"([^"]+)"', config_content)
            if bg_match:
                settings['backgroundColor'] = bg_match.group(1)
        
        # Parse the secondary background color
        if 'secondaryBackgroundColor' in config_content:
            sec_bg_match = re.search(r'secondaryBackgroundColor\s*=\s*"([^"]+)"', config_content)
            if sec_bg_match:
                settings['secondaryBackgroundColor'] = sec_bg_match.group(1)
        
        # Parse the text color
        if 'textColor' in config_content:
            text_match = re.search(r'textColor\s*=\s*"([^"]+)"', config_content)
            if text_match:
                settings['textColor'] = text_match.group(1)
        
        # Parse the font
        if 'font' in config_content:
            font_match = re.search(r'font\s*=\s*"([^"]+)"', config_content)
            if font_match:
                settings['font'] = font_match.group(1)
        
        # Determine theme based on colors
        if settings.get('backgroundColor', '') == '#0E1117':
            settings['theme'] = 'Dark'
        elif settings.get('backgroundColor', '') == '#FFFFFF':
            settings['theme'] = 'Light'
        else:
            settings['theme'] = 'Custom'
            
        return settings
    
    except Exception as e:
        st.warning(f"Error loading settings: {e}")
        # Return default settings on error
        return {
            'theme': 'Light',
            'primaryColor': '#FF4B4B',
            'backgroundColor': '#FFFFFF',
            'secondaryBackgroundColor': '#F0F2F6',
            'textColor': '#262730',
            'font': 'sans serif',
            'notifications': True,
            'animations': True,
        }

# Initialize settings in session state if not already done
if 'app_settings' not in st.session_state:
    # Load settings from config file
    st.session_state.app_settings = load_settings_from_config()

# Theme selection (Light/Dark)
st.markdown("## 🎨 Appearance")
theme = st.radio(
    "Color Theme",
    options=["Light", "Dark", "Custom"],
    index=0 if st.session_state.app_settings['theme'] == 'Light' else 
            1 if st.session_state.app_settings['theme'] == 'Dark' else 2,
    horizontal=True
)

if theme == "Light":
    # Light theme presets
    primary_color = '#FF4B4B'
    background_color = '#FFFFFF'
    secondary_bg_color = '#F0F2F6'
    text_color = '#262730'
elif theme == "Dark":
    # Dark theme presets
    primary_color = '#FF4B4B'
    background_color = '#0E1117'
    secondary_bg_color = '#262730'
    text_color = '#FAFAFA'
else:
    # Custom theme - Show color pickers
    st.markdown("### Custom Colors")
    
    col1, col2 = st.columns(2)
    
    with col1:
        primary_color = st.color_picker(
            "Primary Color (Buttons, Links)",
            value=st.session_state.app_settings['primaryColor']
        )
        
        background_color = st.color_picker(
            "Background Color",
            value=st.session_state.app_settings['backgroundColor']
        )
    
    with col2:
        secondary_bg_color = st.color_picker(
            "Secondary Background Color",
            value=st.session_state.app_settings['secondaryBackgroundColor']
        )
        
        text_color = st.color_picker(
            "Text Color",
            value=st.session_state.app_settings['textColor']
        )

# Font selection
font = st.selectbox(
    "Font Family",
    options=["sans serif", "serif", "monospace"],
    index=["sans serif", "serif", "monospace"].index(st.session_state.app_settings['font'])
)

st.markdown("## 🔔 Notification Settings")

# Notifications toggle
notifications = st.toggle(
    "Show app notifications",
    value=st.session_state.app_settings['notifications']
)

# Animations toggle
animations = st.toggle(
    "Enable animations",
    value=st.session_state.app_settings['animations']
)

# Save button (outside of form)
if st.button("Save Settings", use_container_width=True):
    # Update session state with new settings
    st.session_state.app_settings = {
        'theme': theme,
        'primaryColor': primary_color,
        'backgroundColor': background_color,
        'secondaryBackgroundColor': secondary_bg_color,
        'textColor': text_color,
        'font': font,
        'notifications': notifications,
        'animations': animations,
    }
    
    # Save to config file
    if save_settings(st.session_state.app_settings):
        st.success("Settings saved successfully! Refreshing page to apply changes...")
        time.sleep(2)  # Give user time to see the success message
        st.rerun()
    else:
        st.error("Failed to save settings. Please try again.")

# Preview section
st.markdown("## 👁️ Preview")
st.markdown("This is a preview of how your settings will look. The actual changes will be applied after you save.")

# CSS for preview
preview_css = f"""
<style>
.preview-container {{
    padding: 20px;
    border-radius: 10px;
    background-color: {background_color};
    color: {text_color};
    font-family: {font};
    margin-bottom: 20px;
}}
.preview-button {{
    background-color: {primary_color};
    color: white;
    padding: 8px 16px;
    border-radius: 5px;
    text-align: center;
    display: inline-block;
    margin-top: 10px;
    cursor: pointer;
}}
.preview-card {{
    background-color: {secondary_bg_color};
    border-radius: 5px;
    padding: 15px;
    margin-top: 15px;
}}
</style>
"""

# Preview HTML
preview_html = f"""
{preview_css}
<div class="preview-container">
    <h3>Settings Preview</h3>
    <p>This is how your text will appear with the selected settings.</p>
    
    <div class="preview-button">Button Example</div>
    
    <div class="preview-card">
        <h4>Card Example</h4>
        <p>This shows how cards and secondary elements will look.</p>
    </div>
</div>
"""

st.markdown(preview_html, unsafe_allow_html=True)

# Apply theme styles globally for preview
global_css = f"""
<style>
    .main .block-container {{
        background-color: {background_color};
        color: {text_color};
    }}
    h1, h2, h3, h4, h5, h6, p, div {{
        color: {text_color} !important;
    }}
    .stButton>button {{
        background-color: {primary_color} !important;
        color: white !important;
    }}
    .stSelectbox, .stMultiselect, .stRadio {{
        background-color: {secondary_bg_color} !important;
    }}
</style>
"""
st.markdown(global_css, unsafe_allow_html=True)

# Navigation buttons
st.markdown("---")
col1, col2 = st.columns([1, 1])

with col1:
    # Back button - go back to previous page
    if st.button("← Back", use_container_width=True):
        if st.session_state.get('destination', ''):
            # If in the middle of planning, go to the main app
            st.switch_page("main.py")
        else:
            # If destination not set, go to home
            st.switch_page("main.py")

with col2:
    # Continue planning button - shown only if a trip is in progress
    if st.session_state.get('destination', ''):
        if st.button("Continue Planning →", use_container_width=True):
            if st.session_state.get('itinerary'):
                st.switch_page("pages/05_Trip_Preview.py")
            elif st.session_state.get('weather_data'):
                st.switch_page("pages/04_Itinerary_Generation.py")
            elif st.session_state.get('start_date'):
                st.switch_page("pages/03_Calendar_and_Weather.py")
            elif st.session_state.get('trip_purpose'):
                st.switch_page("pages/02_Travel_Preferences.py")
            else:
                st.switch_page("pages/01_Destination_and_Budget.py")
    else:
        # Start planning button - shown if no trip is in progress
        if st.button("Start Planning →", use_container_width=True):
            st.switch_page("pages/01_Destination_and_Budget.py")