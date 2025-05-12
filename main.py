# main.py
import os
from dotenv import load_dotenv
from gui import GUIManager
from api_handler import APIClient
from user_profile import UserProfile

def main():
    # Load API key from .env file
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")

    # Initialize user profile
    user = UserProfile("Guest")

    # Initialize Gemini API client
    api = APIClient(api_key)

    # Start GUI
    app = GUIManager(api_client=api, user=user)
    app.run()

if __name__ == "__main__":
    main()
