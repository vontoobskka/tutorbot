import os
from dotenv import load_dotenv
from pathlib import Path
from api_handler import APIClient
from user_profile import UserProfile

def chat_loop(api):
    print("Chatbot started! Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        response = api.get_response(user_input)
        print("Bot:", response)

def main():
    load_dotenv(dotenv_path=Path(__file__).parent / ".env")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")
    
    user = UserProfile("Guest")
    api = APIClient(api_key)
    
    chat_loop(api)  # Start console chat for testing

if __name__ == "__main__":
    main()
