import os 
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
API_KEY = os.getenv("MISTRAL_API_KEY")
team_captains = ["Dipesh Shrestha", "Benson Kioko", "Felix Mathenge", "Dip Sunuwar", "Pranav Ghimire", "Michael Kiio", "Manil Shrestha"] 