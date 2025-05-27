import os
import tkinter as tk
from dotenv import load_dotenv
from pathlib import Path
from api_handler import APIClient
from user_profile import UserProfile
from gui import GUIManager  # Make sure this exists
from tkinter import ttk, filedialog

# Optional: fallback console chat mode
def chat_loop(api):
    print("Chatbot started! Type 'exit' to quit.")
    while True:
        try:
            user_input = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        response = api.get_response(user_input)
        print("Bot:", response)

def main():
    # Load environment variables from .env
    load_dotenv(dotenv_path=Path(__file__).parent / ".env")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")

    user = UserProfile("Guest")
    api = APIClient(api_key)

    # ✅ Launch GUI instead of console
    app = GUIManager(api_client=api, user=user)
    app.run()

    # If you ever want to run console mode instead, just use:
    # chat_loop(api)

if __name__ == "__main__":
    main()
