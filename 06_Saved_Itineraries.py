import streamlit as st
import json
import pandas as pd
from datetime import datetime
import os

# Set page configuration
st.set_page_config(
    page_title="Saved Itineraries - AI Travel Magic",
    page_icon="✈️",
    layout="wide"
)

# Title and description
st.title("📋 Saved Itineraries")
st.markdown("### View and manage your saved travel plans")

st.markdown("""
<div class="highlight-box">
    <p>Here you can view all your saved itineraries, export them in different formats, or share them with others.</p>
</div>
""", unsafe_allow_html=True)

# Create temp user ID if not exists (in a real app, this would come from authentication)
if 'user_id' not in st.session_state:
    st.session_state.user_id = f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}"

# Alternative to database: use session state to store itineraries
if 'saved_itineraries' not in st.session_state:
    st.session_state.saved_itineraries = []
    
# Get all itineraries for this "user"
itineraries = [itinerary for itinerary in st.session_state.saved_itineraries 
               if itinerary.get('user_id') == st.session_state.user_id]

# Save current itinerary button
if 'itinerary' in st.session_state and st.session_state.itinerary:
    st.markdown("### Save Current Itinerary")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        itinerary_name = st.text_input(
            "Give your itinerary a name (optional)",
            value=f"Trip to {st.session_state.get('destination', 'Destination')}",
            key="current_itinerary_name"
        )
    
    with col2:
        if st.button("Save Current Itinerary", use_container_width=True):
            # Prepare itinerary data
            itinerary_data = {
                "name": itinerary_name,
                "destination": st.session_state.get('destination', ''),
                "start_date": st.session_state.get('start_date', '').isoformat() if hasattr(st.session_state.get('start_date', ''), 'isoformat') else st.session_state.get('start_date', ''),
                "end_date": st.session_state.get('end_date', '').isoformat() if hasattr(st.session_state.get('end_date', ''), 'isoformat') else st.session_state.get('end_date', ''),
                "budget": st.session_state.get('budget', ''),
                "trip_purpose": st.session_state.get('trip_purpose', ''),
                "preferences": st.session_state.get('preferences', []),
                "special_notes": st.session_state.get('special_notes', ''),
                "weather_data": st.session_state.get('weather_data', []),
                "season": st.session_state.get('season', ''),
                "itinerary": st.session_state.get('itinerary', {}),
                "user_id": st.session_state.user_id
            }
            
            # Generate a unique ID for this itinerary
            itinerary_data["id"] = f"itin_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(st.session_state.saved_itineraries)}"
            # Add created timestamp
            itinerary_data["created_at"] = datetime.now().isoformat()
            
            # Add to our list of saved itineraries in session state
            st.session_state.saved_itineraries.append(itinerary_data)
            
            st.success(f"Itinerary '{itinerary_name}' saved successfully!")
            # Refresh the page to show the new itinerary in the list
            st.rerun()

# Display saved itineraries
st.markdown("---")
st.markdown("### Your Saved Itineraries")

if not itineraries:
    st.info("You haven't saved any itineraries yet. Create an itinerary and save it to see it here.")
else:
    # Create a card-like display for each itinerary
    for i, itinerary in enumerate(itineraries):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"#### Trip to {itinerary.get('destination', 'Destination')}")
            st.markdown(f"**Destination:** {itinerary.get('destination', 'N/A')}")
            
            # Format dates
            start_date = itinerary.get('start_date', 'N/A')
            end_date = itinerary.get('end_date', 'N/A')
            
            # Display dates and duration
            st.markdown(f"**Dates:** {start_date} to {end_date}")
            
            # Display budget and trip purpose
            st.markdown(f"**Budget:** {itinerary.get('budget', 'N/A')} | **Purpose:** {itinerary.get('trip_purpose', 'N/A')}")
            
            # When it was created
            created_at = itinerary.get('created_at', '')
            if created_at:
                try:
                    # Try to parse and format the timestamp
                    created_date = datetime.fromisoformat(created_at)
                    st.markdown(f"**Created:** {created_date.strftime('%B %d, %Y at %I:%M %p')}")
                except:
                    st.markdown(f"**Created:** {created_at}")
        
        with col2:
            # Action buttons
            st.markdown("#### Actions")
            
            # View button - loads this itinerary into the session state and redirects to itinerary page
            if st.button("View/Edit", key=f"view_{i}", use_container_width=True):
                # Load this itinerary into session state
                st.session_state.destination = itinerary.get('destination', '')
                st.session_state.start_date = itinerary.get('start_date', '')
                st.session_state.end_date = itinerary.get('end_date', '')
                st.session_state.budget = itinerary.get('budget', '')
                st.session_state.trip_purpose = itinerary.get('trip_purpose', '')
                st.session_state.preferences = itinerary.get('preferences', [])
                st.session_state.special_notes = itinerary.get('special_notes', '')
                st.session_state.weather_data = itinerary.get('weather_data', [])
                st.session_state.season = itinerary.get('season', '')
                st.session_state.itinerary = itinerary.get('itinerary', {})
                
                # Navigate to itinerary page
                st.switch_page("pages/04_Itinerary_Generation.py")
            
            # Export button
            export_format = st.selectbox(
                "Export Format", 
                ["CSV", "JSON"], 
                key=f"export_format_{i}"
            )
            
            if st.button("Export", key=f"export_{i}", use_container_width=True):
                if export_format == "CSV":
                    # Export to CSV
                    try:
                        # Convert itinerary to DataFrame
                        daily_plan = itinerary.get('itinerary', {}).get('daily_plan', [])
                        if not daily_plan:
                            # Try another common structure
                            daily_plan = itinerary.get('daily_plan', [])
                            
                        if daily_plan:
                            # Flatten the nested structure
                            rows = []
                            for day in daily_plan:
                                row = {
                                    'Day': day.get('day', ''),
                                    'Date': day.get('date', ''),
                                    'Day Name': day.get('day_name', ''),
                                    'Weather': day.get('weather', ''),
                                    'Temperature': day.get('temperature', ''),
                                    'Morning Activity': day.get('morning', {}).get('title', ''),
                                    'Morning Description': day.get('morning', {}).get('description', ''),
                                    'Afternoon Activity': day.get('afternoon', {}).get('title', ''),
                                    'Afternoon Description': day.get('afternoon', {}).get('description', ''),
                                    'Evening Activity': day.get('evening', {}).get('title', ''),
                                    'Evening Description': day.get('evening', {}).get('description', ''),
                                    'Accommodation': day.get('accommodation', '')
                                }
                                rows.append(row)
                                
                            # Create DataFrame and export to CSV
                            df = pd.DataFrame(rows)
                            csv_data = df.to_csv(index=False)
                            
                            # Create a download link
                            st.download_button(
                                label="Download CSV",
                                data=csv_data,
                                file_name=f"itinerary_{itinerary.get('destination', 'trip').replace(' ', '_').lower()}.csv",
                                mime="text/csv",
                                key=f"download_csv_{i}"
                            )
                        else:
                            st.error("Could not export the itinerary. The structure is not compatible with CSV format.")
                    except Exception as e:
                        st.error(f"Error exporting to CSV: {e}")
                else:  # JSON
                    # Export to JSON
                    try:
                        # Convert to JSON string
                        json_data = json.dumps(itinerary, indent=2, default=str)
                        
                        # Create a download link
                        st.download_button(
                            label="Download JSON",
                            data=json_data,
                            file_name=f"itinerary_{itinerary.get('destination', 'trip').replace(' ', '_').lower()}.json",
                            mime="application/json",
                            key=f"download_json_{i}"
                        )
                    except Exception as e:
                        st.error(f"Error exporting to JSON: {e}")
            
            # Delete button
            if st.button("Delete", key=f"delete_{i}", use_container_width=True, type="secondary"):
                # Show a confirmation
                if st.checkbox(f"Confirm deletion of '{itinerary.get('name', 'this itinerary')}'", key=f"confirm_delete_{i}"):
                    # Remove from saved_itineraries
                    st.session_state.saved_itineraries = [it for it in st.session_state.saved_itineraries if it.get('id') != itinerary.get('id')]
                    st.success("Itinerary deleted successfully!")
                    # Refresh the page
                    st.rerun()
        
        # Add a separator between itineraries
        st.markdown("---")

# Navigation buttons at the bottom
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("← Back to Trip Preview", use_container_width=True):
        st.switch_page("pages/05_Trip_Preview.py")

with col2:
    if st.button("Book Travel Services →", use_container_width=True):
        st.switch_page("pages/07_Bookings.py")