import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Travel Preferences - AI Travel Magic",
    page_icon="✈️",
    layout="wide"
)

# Initialize session state variables if not already done
if 'destination' not in st.session_state:
    st.session_state.destination = ""
    st.switch_page("pages/01_Destination_and_Budget.py")
if 'trip_purpose' not in st.session_state:
    st.session_state.trip_purpose = ""
if 'preferences' not in st.session_state:
    st.session_state.preferences = []

# Title and description
st.title("🧭 Travel Preferences")
st.markdown(f"### Personalize your trip to {st.session_state.destination}")

st.markdown("""
<div class="highlight-box">
    <p>Tell us about your interests and the purpose of your trip. This will help us tailor your itinerary to activities you'll enjoy!</p>
</div>
""", unsafe_allow_html=True)

# Trip purpose
st.markdown("### Purpose of Your Trip")
st.markdown("What's the main reason for this journey?")

trip_purposes = [
    "Relaxation & Leisure", 
    "Cultural Exploration", 
    "Adventure & Outdoor Activities",
    "Food & Culinary Experience", 
    "Photography & Sightseeing",
    "Historical Tour",
    "Romantic Getaway",
    "Family Vacation",
    "Business Trip with Free Time"
]

col1, col2, col3 = st.columns(3)
purpose_buttons = {}

for i, purpose in enumerate(trip_purposes):
    with [col1, col2, col3][i % 3]:
        is_selected = purpose == st.session_state.trip_purpose
        button_style = "primary" if is_selected else "secondary"
        if st.button(
            purpose, 
            key=f"purpose_{i}", 
            use_container_width=True,
            type=button_style
        ):
            st.session_state.trip_purpose = purpose
            st.rerun()

# Activity preferences
st.markdown("### Activities & Interests")
st.markdown("Select activities and experiences you're interested in:")

activity_options = [
    "Museums & Art Galleries",
    "Historical Sites & Landmarks",
    "Local Cuisine & Food Tours",
    "Outdoor Adventures",
    "Shopping & Markets",
    "Parks & Nature",
    "Beaches & Water Activities",
    "Nightlife & Entertainment",
    "Wellness & Spa",
    "Local Tours & Guided Experiences",
    "Wildlife & Animal Encounters",
    "Cultural Performances",
    "Religious & Sacred Sites",
    "Photography Spots",
    "Architecture",
    "Wine Tasting & Vineyards",
    "Off-the-beaten-path Locations",
    "Family-friendly Activities"
]

# Convert activity options to a multiselect
selected_activities = st.multiselect(
    "Choose your preferred activities (select multiple):",
    options=activity_options,
    default=st.session_state.preferences,
    key="activity_multiselect"
)

st.session_state.preferences = selected_activities

# Special requirements or notes
st.markdown("### Special Requirements")
st.markdown("Any special needs or additional notes for your trip?")

if 'special_notes' not in st.session_state:
    st.session_state.special_notes = ""

special_notes = st.text_area(
    "Optional: Add any special requirements or notes",
    value=st.session_state.special_notes,
    key="special_notes",
    help="Examples: accessibility needs, dietary restrictions, traveling with children, etc.",
    placeholder="E.g., Need wheelchair accessibility, vegetarian food options, child-friendly activities..."
)

# Update session state when the value changes (will be done automatically by Streamlit)

# Navigation buttons
st.markdown("---")
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("← Back to Destination", use_container_width=True):
        st.switch_page("pages/01_Destination_and_Budget.py")

with col2:
    # Enable the next button only if at least purpose is selected
    next_disabled = not st.session_state.trip_purpose
    if st.button("Next: Select Dates →", disabled=next_disabled, use_container_width=True):
        st.switch_page("pages/03_Calendar_and_Weather.py")

# Show error if trying to proceed without purpose
if next_disabled:
    st.error("Please select a purpose for your trip to continue.")
