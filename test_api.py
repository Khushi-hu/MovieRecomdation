import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("TMDB_API_KEY")

if api_key:
    print("TMDB API key loaded successfully!")
else:
    print("TMDB API key NOT found!")