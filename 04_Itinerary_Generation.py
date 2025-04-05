import streamlit as st
import random

# Set page configuration
st.set_page_config(
    page_title="Itinerary Generation - AI Travel Magic",
    page_icon="✈",
    layout="wide"
)

# Title and description
st.title("🗓 Your Personalized Itinerary")
st.markdown("### Here's a detailed plan for your trip")

st.markdown("""
<div class="highlight-box">
    <p>Based on your preferences and travel dates, we've created a personalized itinerary for your trip. Review the day-by-day plan below!</p>
</div>
""", unsafe_allow_html=True)

# Check if we have the necessary data to proceed
if 'destination' not in st.session_state or not st.session_state.destination:
    st.switch_page("pages/01_Destination_and_Budget.py")
if 'weather_data' not in st.session_state:
    st.switch_page("pages/03_Calendar_and_Weather.py")

# Display basic trip info
st.markdown(f"## Trip to {st.session_state.destination}")
st.markdown(f"*Budget Level:* {st.session_state.budget}")
trip_duration = (st.session_state.end_date - st.session_state.start_date).days
st.markdown(f"*Trip Duration:* {trip_duration} days")
if 'trip_purpose' in st.session_state:
    st.markdown(f"*Trip Purpose:* {st.session_state.trip_purpose}")

# Ensure we have an itinerary
if 'itinerary' not in st.session_state or not st.session_state.itinerary:
    # Create specific activities based on destination
    destination_specific = {
        "Paris": {
            "attractions": [
                "Eiffel Tower Summit & Iron Lady Restaurant",
                "Louvre Museum - Mona Lisa & Venus de Milo Gallery",
                "Notre-Dame Cathedral Reconstruction Tour",
                "Arc de Triomphe Observation Deck & Eternal Flame",
                "Palace of Versailles Hall of Mirrors & Marie Antoinette's Estate",
                "Musée d'Orsay Impressionist Collection",
                "Sainte-Chapelle Gothic Stained Glass Windows",
                "Centre Pompidou Modern Art Collection - Level 5",
                "Place des Vosges Victor Hugo House",
                "Panthéon Foucault Pendulum & Crypt"
            ],
            "restaurants": [
                "Guy Savoy - 11 Quai de Conti (3 Michelin Stars)",
                "L'Arpège - 84 Rue de Varenne (Organic French Cuisine)",
                "Le Baratin - 3 Rue Jouye-Rouve (Hidden Gem in Belleville)",
                "L'Ami Louis - 32 Rue du Vertbois (Classic French)",
                "Bistrot Paul Bert - 18 Rue Paul Bert (Traditional)",
                "Le Chateaubriand - 129 Avenue Parmentier (Modern French)",
                "Septime - 80 Rue de Charonne (Farm-to-Table)",
                "Le Baratin - 3 Rue Jouye-Rouve (Innovative)",
                "Chez L'Ami Louis - 32 Rue du Vertbois (Rustic French)",
                "L'Abeille - Shangri-La Hotel (Fine Dining)",
                "Le Grand Véfour - 17 Rue de Beaujolais (Historic)",
                "Bistrot Chez L'Ami Louis - 32 Rue du Vertbois (Classic)",
                "L'As du Fallafel - 34 Rue des Rosiers (Best Falafel)",
                "Breizh Café - 109 Rue Vieille du Temple (Best Crêpes)",
                "Du Pain et des Idées - 34 Rue Yves Toudic (Best Pastries)"
            ],
            "activities": [
                "Seine River Sunset Cruise with Ducasse sur Seine",
                "Montmartre Art Walk & Place du Tertre Portrait Session",
                "Luxembourg Gardens Picnic & Medici Fountain Visit",
                "Le Marais Vintage Shopping at Kilo Shop & Free'P'Star",
                "Wine Tasting at Caves du Louvre (52 Rue de l'Arbre Sec)",
                "Macarons Class at Pierre Hermé Academy",
                "Fat Tire Bike Tour - Hidden Paris Streets",
                "Sunrise Photography at Trocadéro Gardens",
                "Opera Garnier Marc Chagall Ceiling Tour",
                "Père Lachaise Cemetery - Oscar Wilde & Jim Morrison Graves",
                "Canal Saint-Martin Food Tour with Local Guide",
                "Marché aux Puces de Saint-Ouen Antique Hunt",
                "Saint-Germain Chocolate Tour - Patrick Roger & Pierre Marcolini",
                "Le Petit Journal Jazz Club in Saint-Germain",
                "Perruche Rooftop Bar at Printemps Haussmann"
            ],
            "morning_activities": [
                "Fresh Croissants at Du Pain et des Idées (34 Rue Yves Toudic)",
                "Market Tour at Marché d'Aligre with Local Chef",
                "Sunrise Photography at Sacré-Cœur Basilica Steps",
                "Early Access Versailles Gardens Tour",
                "Breakfast at Historic Café de Flore (172 Boulevard Saint-Germain)"
            ],
            "afternoon_activities": [
                "Shopping at Le Bon Marché & La Grande Épicerie",
                "Art Gallery Hopping in Marais - Thaddaeus Ropac & Perrotin",
                "Tea Time at Angelina Paris (226 Rue de Rivoli)",
                "Paris Plages Seine Beach Activities (Summer)",
                "Rare Book Shopping at Shakespeare & Company"
            ],
            "evening_activities": [
                "Dinner Cruise on Ducasse sur Seine",
                "Moulin Rouge Show with Champagne",
                "Wine Tasting at La Dernière Goutte",
                "Night Photography Tour - Pont Alexandre III",
                "Sunset at Montparnasse Tower Observation Deck"
            ],
            "morning_activities": [
                "Fresh Croissants at Du Pain et des Idées",
                "Market Tour at Marché d'Aligre",
                "Sunrise at Sacré-Cœur Basilica",
                "Early Visit to Musée Rodin Gardens",
                "Breakfast at Café de Flore"
            ],
            "afternoon_activities": [
                "Shopping at Le Bon Marché",
                "Art Gallery Hopping in Marais",
                "Tea Time at Angelina Paris",
                "Seine Beach (Paris Plages in summer)",
                "Bouquinistes Book Shopping"
            ],
            "evening_activities": [
                "Dinner Cruise on Seine",
                "Cabaret Show at Moulin Rouge",
                "Wine Bar Hopping in Saint-Germain",
                "Night Photography Tour",
                "Sunset at Montparnasse Tower"
            ]
        },
        "Tokyo": {
            "attractions": ["Sensoji Temple", "Meiji Shrine", "Tokyo Skytree", "Tsukiji Outer Market", "Shinjuku Gyoen"],
            "restaurants": ["Narisawa", "Sukiyabashi Jiro", "Ukai-tei", "Gonpachi Nishi-Azabu", "Tsuta Japanese Soba"],
            "activities": ["Teamlab Borderless", "Harajuku Fashion Street", "Sumo Wrestling Match", "Robot Restaurant Show", "Mt. Fuji Day Trip"]
        },
        "New York": {
            "attractions": ["Statue of Liberty", "Central Park", "Empire State Building", "Metropolitan Museum", "Times Square"],
            "restaurants": ["Le Bernardin", "Eleven Madison Park", "Peter Luger", "Katz's Delicatessen", "Grimaldi's Pizza"],
            "activities": ["Broadway Show", "High Line Walk", "Brooklyn Bridge Sunset", "Fifth Avenue Shopping", "NYC Food Tour"]
        }
    }

    # Get destination-specific details or use generic ones
    dest_details = destination_specific.get(st.session_state.destination, {
        "attractions": [f"Famous {st.session_state.destination} Landmark", f"{st.session_state.destination} Historical Site"],
        "restaurants": [f"Top-rated {st.session_state.destination} Restaurant", f"Local {st.session_state.destination} Eatery"],
        "activities": [f"{st.session_state.destination} City Tour", f"{st.session_state.destination} Cultural Experience"]
    })

    # Get time-specific activities
    morning_activities = dest_details.get('morning_activities', dest_details['activities'])
    afternoon_activities = dest_details.get('afternoon_activities', dest_details['activities'])
    evening_activities = dest_details.get('evening_activities', dest_details['activities'])

    # Create a personalized itinerary with more specific details
    st.session_state.itinerary = {
        "trip_info": {
            "destination": st.session_state.destination,
            "budget": st.session_state.budget,
            "duration": f"{trip_duration} days"
        },
        "daily_plan": [
            {
                "day": 1,
                "day_name": "Arrival & Welcome",
                "morning": {
                    "title": "Arrive at Paris Charles de Gaulle Airport",
                    "description": "Welcome to Paris! After clearing customs, take the direct train (RER B) to central Paris. Your hotel is located in the charming Saint-Germain-des-Prés neighborhood."
                },
                "afternoon": {
                    "title": "Saint-Germain-des-Prés Orientation Walk",
                    "description": "After checking in, take a guided orientation walk through the historic Saint-Germain quarter. Visit the famous Café de Flore and Les Deux Magots, then explore the charming streets lined with art galleries and boutiques."
                },
                "evening": {
                    "title": f"Welcome Dinner at {random.choice(dest_details['restaurants'])}",
                    "description": "Enjoy your first Parisian dinner at this acclaimed restaurant, known for its exceptional French cuisine and elegant atmosphere. Consider starting with escargots followed by a classic coq au vin."
                }
            },
            {
                "day": 2,
                "day_name": "Cultural Immersion",
                "morning": {
                    "title": f"Private Tour of {dest_details['attractions'][1]}",
                    "description": f"Begin your day with an expert-guided tour of the iconic {dest_details['attractions'][1]}, learning about its rich history and significance."
                },
                "afternoon": {
                    "title": dest_details['activities'][0],
                    "description": f"Explore the highlights of {st.session_state.destination} with a knowledgeable local guide, including hidden gems and popular landmarks."
                },
                "evening": {
                    "title": f"Dining Experience at {dest_details['restaurants'][1]}",
                    "description": "Savor an evening of culinary excellence at this renowned establishment known for its exceptional service and atmosphere."
                }
            },
            {
                "day": 3,
                "day_name": "Local Experience",
                "morning": {
                    "title": dest_details['activities'][1],
                    "description": f"Immerse yourself in the local culture through this authentic {st.session_state.destination} experience."
                },
                "afternoon": {
                    "title": f"Visit to {dest_details['attractions'][0]}",
                    "description": f"Explore this must-see landmark of {st.session_state.destination}, taking in its impressive architecture and surroundings."
                },
                "evening": {
                    "title": f"Dinner at {random.choice(dest_details['restaurants'])}",
                    "description": "End your day with a memorable dining experience featuring local specialties and seasonal ingredients."
                }
            }
        ]
    }

    # Add more days if needed
    if trip_duration > 3:
        for day_num in range(4, trip_duration + 1):
            day_type = "Relaxation Day" if day_num % 2 == 0 else "Discovery Day"
            new_day = {
                "day": day_num,
                "day_name": day_type,
                "morning": {"title": "Beach Visit" if day_type == "Relaxation Day" else "Local Neighborhood Walk", 
                          "description": "Relax by the beach and enjoy the sun." if day_type == "Relaxation Day" else "Explore a charming local neighborhood."},
                "afternoon": {"title": "Spa Treatment" if day_type == "Relaxation Day" else "Shopping", 
                            "description": "Indulge in a relaxing spa treatment." if day_type == "Relaxation Day" else "Shop for local crafts and souvenirs."},
                "evening": {"title": "Sunset Dinner" if day_type == "Relaxation Day" else "Local Entertainment", 
                          "description": "Enjoy dinner with a beautiful sunset view." if day_type == "Relaxation Day" else "Experience local entertainment options."}
            }
            st.session_state.itinerary["daily_plan"].append(new_day)

# Display daily itinerary
daily_plan = st.session_state.itinerary.get('daily_plan', [])

for day in daily_plan:
    st.markdown(f"### Day {day['day']}: {day['day_name']}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Morning")
        morning = day.get('morning', {})
        st.markdown(f"{morning.get('title', '')}")
        st.markdown(morning.get('description', ''))

    with col2:
        st.subheader("Afternoon")
        afternoon = day.get('afternoon', {})
        st.markdown(f"{afternoon.get('title', '')}")
        st.markdown(afternoon.get('description', ''))

    with col3:
        st.subheader("Evening")
        evening = day.get('evening', {})
        st.markdown(f"{evening.get('title', '')}")
        st.markdown(evening.get('description', ''))

    st.markdown("---")

# Add a download button for the itinerary
st.download_button(
    label="Download Itinerary as Text",
    data=str(st.session_state.itinerary),
    file_name=f"itinerary_{st.session_state.destination.replace(' ', '_')}.txt",
    mime="text/plain"
)

# Navigation buttons
st.markdown("---")
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    if st.button("← Back to Calendar", use_container_width=True):
        st.switch_page("pages/03_Calendar_and_Weather.py")

with col2:
    if st.button("Settings", use_container_width=True):
        st.switch_page("pages/08_Settings.py")

with col3:
    if st.button("Regenerate Itinerary", use_container_width=True):
        # Force regeneration by removing the current itinerary
        if 'itinerary' in st.session_state:
            del st.session_state.itinerary
        st.rerun()

with col4:
    if st.button("Continue to Trip Preview →", use_container_width=True):
        st.switch_page("pages/05_Trip_Preview.py")