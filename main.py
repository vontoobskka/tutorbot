# main.py
from gui import GUIManager
from api_handler import APIClient
from user_profile import UserProfile

def main():
    # Initialize user profile
    user = UserProfile("Guest")

    # Initialize Gemini API client
    api = APIClient("YOUR_API_KEY_HERE")

    # Start GUI
    app = GUIManager(api_client=api, user=user)
    app.run()

if __name__ == "__main__":
    main()