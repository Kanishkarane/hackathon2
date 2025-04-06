how to strcuture the website:
1. local_run.py.main.py,destination_scaper.py should be inside a folder named, "hackathon"
2. create an inside folder called "pages" and add the following programs:
    i.01_Destination_and_Budget.py
    ii.02_Travel_Preferences.py
    iii.03_Calendar_and_Weather.py
    iv.04_Itinerary_Generation.py
    v.05_Trip_Preview.py
    vi.06_Video_Generation.py
    vii.07_Bookings.py
    viii.08_Settings.py
3. Inside the .streamlit folder, add the api keys in a file called secrets.toml needed for running the program

i.e.

UNSPLASH_ACCESS_KEY = "enter api key here"
PEXELS_API_KEY = "enter api key here"
HUGGINGFACE_API_KEY = "enter api key here"
