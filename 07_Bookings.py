import streamlit as st
import urllib.parse
import requests
from datetime import datetime, timedelta
import time

# Set page configuration
st.set_page_config(
    page_title="Travel Bookings - AI Travel Magic",
    page_icon="✈️",
    layout="wide"
)

# Helper functions for bookings
def check_url_availability(url, timeout=3):
    """Quickly check if a URL is available without fully loading it"""
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return 200 <= response.status_code < 400
    except Exception:
        return False

def format_url_safely(url_template, **kwargs):
    """Safely format URLs with proper encoding of parameters"""
    # First encode all the parameters
    encoded_params = {}
    for key, value in kwargs.items():
        if isinstance(value, str):
            # Handle different encoding needs based on parameter type
            if key in ['origin', 'destination', 'origin_code', 'dest_code']:
                # For city names: first clean with basic replacements, then URL encode
                clean_value = value.strip().lower().replace(" ", "-")
                encoded_params[key] = urllib.parse.quote(clean_value)
            else:
                # For other parameters just URL encode
                encoded_params[key] = urllib.parse.quote(value)
        else:
            encoded_params[key] = value
            
    # Now format the URL with encoded parameters
    try:
        return url_template.format(**encoded_params)
    except KeyError as e:
        st.error(f"Missing parameter in URL template: {e}")
        return None
    except Exception as e:
        st.error(f"Error formatting URL: {e}")
        return None

def get_airport_codes():
    """Return a dictionary of city names to airport codes"""
    # Common airport codes for popular destinations
    return {
        "delhi": "DEL",
        "mumbai": "BOM",
        "bangalore": "BLR",
        "chennai": "MAA",
        "kolkata": "CCU",
        "hyderabad": "HYD",
        "goa": "GOI",
        "ahmedabad": "AMD",
        "pune": "PNQ",
        "jaipur": "JAI",
        "lucknow": "LKO",
        "new york": "NYC",
        "london": "LON",
        "paris": "PAR",
        "tokyo": "TYO",
        "rome": "ROM",
        "barcelona": "BCN",
        "dubai": "DXB",
        "singapore": "SIN",
        "bangkok": "BKK",
        "sydney": "SYD",
        "berlin": "BER",
        "madrid": "MAD",
        "amsterdam": "AMS",
        "athens": "ATH",
        "vienna": "VIE",
        "zurich": "ZRH",
        "istanbul": "IST"
    }

def load_booking_options():
    """Load booking options with URLs and query parameter formats"""
    return {
        "Flights": {
            "description": "Book flights at competitive prices",
            "websites": {
                "Kayak": {
                    "base_url": "https://www.kayak.com/flights",
                    "search_url": "https://www.kayak.com/flights/{origin_code}-{dest_code}/{start_date_compact}",
                    "icon": "✈️"
                },
                "Skyscanner": {
                    "base_url": "https://www.skyscanner.com/",
                    "search_url": "https://www.skyscanner.com/transport/flights/{origin_code}/{dest_code}/{start_date_compact}/",
                    "icon": "✈️"
                },
                "Expedia": {
                    "base_url": "https://www.expedia.com/Flights",
                    "search_url": "https://www.expedia.com/Flights-Search?trip=oneway&leg1=from:{origin},to:{destination},departure:{start_date}TANYT&passengers=adults:1,children:0,seniors:0,infantinlap:N&options=cabinclass%3Aeconomy&mode=search",
                    "icon": "✈️"
                }
            }
        },
        "Hotels": {
            "description": "Find the perfect accommodation for your stay",
            "websites": {
                "Booking.com": {
                    "base_url": "https://www.booking.com/",
                    "search_url": "https://www.booking.com/searchresults.html?ss={destination}&checkin={start_date}&checkout={end_date}",
                    "icon": "🏨"
                },
                "Hotels.com": {
                    "base_url": "https://www.hotels.com/",
                    "search_url": "https://www.hotels.com/search?destination={destination}&startDate={start_date}&endDate={end_date}",
                    "icon": "🏨"
                },
                "Airbnb": {
                    "base_url": "https://www.airbnb.com/",
                    "search_url": "https://www.airbnb.com/s/{destination}/homes?checkin={start_date}&checkout={end_date}",
                    "icon": "🏠"
                }
            }
        },
        "Car Rentals": {
            "description": "Rent a car for your journey",
            "websites": {
                "Kayak": {
                    "base_url": "https://www.kayak.com/cars",
                    "search_url": "https://www.kayak.com/cars/{destination}/{start_date}/{end_date}",
                    "icon": "🚗"
                },
                "Expedia": {
                    "base_url": "https://www.expedia.com/Cars",
                    "search_url": "https://www.expedia.com/Cars-Search?locn={destination}&startDate={start_date}&endDate={end_date}",
                    "icon": "🚗"
                }
            }
        },
        "Activities": {
            "description": "Book tours, experiences and attractions",
            "websites": {
                "GetYourGuide": {
                    "base_url": "https://www.getyourguide.com/",
                    "search_url": "https://www.getyourguide.com/{destination}-l",
                    "icon": "🎭"
                },
                "Viator": {
                    "base_url": "https://www.viator.com/",
                    "search_url": "https://www.viator.com/search/{destination}",
                    "icon": "🎭"
                }
            }
        },
        "Complete Packages": {
            "description": "Book complete travel packages",
            "websites": {
                "Expedia": {
                    "base_url": "https://www.expedia.com/Vacation-Packages",
                    "search_url": "https://www.expedia.com/Vacation-Packages-Search?trip=roundtrip&origin={origin}&destination={destination}&startDate={start_date}&endDate={end_date}&adults=2",
                    "icon": "🧳"
                },
                "TripAdvisor": {
                    "base_url": "https://www.tripadvisor.com/Trips",
                    "search_url": "https://www.tripadvisor.com/Search?q={destination}",
                    "icon": "🌐"
                }
            }
        }
    }

# Check if we have the necessary data to proceed
if 'destination' not in st.session_state or not st.session_state.destination:
    st.switch_page("pages/01_Destination_and_Budget.py")
if 'start_date' not in st.session_state or not st.session_state.start_date:
    st.switch_page("pages/03_Calendar_and_Weather.py")
if 'end_date' not in st.session_state or not st.session_state.end_date:
    st.switch_page("pages/03_Calendar_and_Weather.py")

# Title and description
st.title("🏨 Book Your Travel Services")
st.markdown(f"### Find and book travel services for your trip to {st.session_state.destination}")

st.markdown("""
<div class="highlight-box">
    <p>Make your journey a reality! Find and book flights, hotels, and other travel services for your trip.</p>
</div>
""", unsafe_allow_html=True)

# Format dates for APIs
start_date_str = st.session_state.start_date.strftime("%Y-%m-%d")
end_date_str = st.session_state.end_date.strftime("%Y-%m-%d")
start_date_compact = st.session_state.start_date.strftime("%Y%m%d")
end_date_compact = st.session_state.end_date.strftime("%Y%m%d")
start_date_dmy = st.session_state.start_date.strftime("%d-%m-%Y")
end_date_dmy = st.session_state.end_date.strftime("%d-%m-%Y")

# Trip details summary
st.markdown("## 📝 Trip Details")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"**Destination:** {st.session_state.destination}")
    
with col2:
    st.markdown(f"**Dates:** {start_date_str} to {end_date_str}")
    
with col3:
    trip_duration = (st.session_state.end_date - st.session_state.start_date).days
    st.markdown(f"**Duration:** {trip_duration} {'days' if trip_duration > 1 else 'day'}")

# Additional travel parameters form
st.markdown("## 🔍 Specify Travel Details")

col1, col2 = st.columns(2)

with col1:
    # Origin city for flights
    if 'origin_city' not in st.session_state:
        st.session_state.origin_city = ""
        
    origin_city = st.text_input(
        "Departure City (for flights)",
        value=st.session_state.origin_city,
        placeholder="Enter your departure city",
        help="This will be used for flight searches"
    )
    st.session_state.origin_city = origin_city
    
    # Travelers
    if 'travelers' not in st.session_state:
        st.session_state.travelers = 2
        
    travelers = st.number_input(
        "Number of Travelers",
        min_value=1,
        max_value=10,
        value=st.session_state.travelers,
        help="How many people are traveling"
    )
    st.session_state.travelers = travelers

with col2:
    # Room preferences
    if 'room_count' not in st.session_state:
        st.session_state.room_count = 1
        
    room_count = st.number_input(
        "Number of Rooms",
        min_value=1,
        max_value=5,
        value=st.session_state.room_count,
        help="For hotel bookings"
    )
    st.session_state.room_count = room_count
    
    # Flight class
    if 'flight_class' not in st.session_state:
        st.session_state.flight_class = "Economy"
        
    flight_class = st.selectbox(
        "Flight Class",
        options=["Economy", "Premium Economy", "Business", "First"],
        index=["Economy", "Premium Economy", "Business", "First"].index(st.session_state.flight_class)
    )
    st.session_state.flight_class = flight_class

# Get airport codes
airport_codes = get_airport_codes()
destination_lower = st.session_state.destination.split(',')[0].strip().lower()
origin_lower = origin_city.split(',')[0].strip().lower() if origin_city else ""

# Try to get airport codes
destination_code = airport_codes.get(destination_lower, "")
origin_code = airport_codes.get(origin_lower, "")

# Load booking options
booking_options = load_booking_options()

# Booking Services Tabs
st.markdown("## 🔖 Booking Services")
tabs = st.tabs(list(booking_options.keys()))

# Setup parameters for URLs
params = {
    "destination": st.session_state.destination.split(',')[0].strip(),
    "origin": origin_city.split(',')[0].strip() if origin_city else "",
    "start_date": start_date_str,
    "end_date": end_date_str,
    "start_date_compact": start_date_compact,
    "end_date_compact": end_date_compact,
    "start_date_dmy": start_date_dmy,
    "end_date_dmy": end_date_dmy,
    "origin_code": origin_code,
    "dest_code": destination_code,
    "travelers": str(travelers),
    "rooms": str(room_count)
}

# For each booking type
for i, (booking_type, options) in enumerate(booking_options.items()):
    with tabs[i]:
        st.markdown(f"### {options['description']}")
        
        # If it's flights, check if origin is provided
        if booking_type == "Flights" and not origin_city:
            st.warning("Please enter your departure city to search for flights.")
        
        # Check if there are any special requirements
        missing_requirements = []
        if booking_type == "Flights":
            if not origin_code and origin_city:
                missing_requirements.append("Airport code for your departure city")
            if not destination_code:
                missing_requirements.append("Airport code for your destination")
                
        if missing_requirements:
            st.info(f"Some websites may not work correctly without: {', '.join(missing_requirements)}")
            
        # Create columns for each booking website
        num_websites = len(options["websites"])
        cols = st.columns(min(3, num_websites))
        
        # For each website offering this service
        for j, (website_name, website_details) in enumerate(options["websites"].items()):
            with cols[j % 3]:
                # Create a card for the booking option
                st.markdown(f"""
                <div style="padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 20px; text-align: center;">
                    <h3 style="margin-top: 0;">{website_details['icon']} {website_name}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Format the search URL
                search_url = format_url_safely(website_details["search_url"], **params)
                
                if search_url:
                    # Check URL availability (disable this for faster loading if needed)
                    #url_available = check_url_availability(website_details["base_url"])
                    url_available = True  # Assume available for better UX
                    
                    if url_available:
                        # Create a button that opens the link in a new tab
                        link_html = f"""
                        <a href="{search_url}" target="_blank" style="text-decoration: none;">
                            <button style="background-color: #4CAF50; color: white; padding: 10px 24px; 
                            border: none; border-radius: 4px; cursor: pointer; width: 100%;">
                                Search on {website_name}
                            </button>
                        </a>
                        """
                        st.markdown(link_html, unsafe_allow_html=True)
                    else:
                        st.error(f"{website_name} is currently unavailable.")
                else:
                    st.error(f"Could not create search URL for {website_name}.")

# Navigation buttons
st.markdown("---")
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("← Back to Trip Preview", use_container_width=True):
        st.switch_page("pages/05_Trip_Preview.py")

with col2:
    if st.button("Save Itinerary →", use_container_width=True):
        st.switch_page("pages/06_Saved_Itineraries.py")
        
# Add additional helpful information
st.markdown("---")
st.markdown("### 💡 Travel Booking Tips")
st.markdown("""
* **Book early:** Especially for peak season travel to get the best rates
* **Compare prices:** Different booking sites may offer different deals
* **Check cancellation policies:** Make sure you understand the refund policies
* **Consider travel insurance:** Protect your trip investment
* **Look for package deals:** Sometimes booking flights + hotels together saves money
""")

# Disclaimer
st.markdown("---")
st.markdown("""
<div style="font-size: 0.8rem; color: #666;">
<strong>Disclaimer:</strong> AI Travel Magic provides these booking links as a convenience. 
We don't directly handle bookings or payments. All transactions will be processed through the respective service providers. 
We're not responsible for any issues that may arise during the booking process or your stay/travel.
</div>
""", unsafe_allow_html=True)