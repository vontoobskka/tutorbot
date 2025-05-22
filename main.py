import os
from dotenv import load_dotenv
from pathlib import Path
from api_handler import APIClient
from user_profile import UserProfile

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
    # Load .env from the same directory as this script
    load_dotenv(dotenv_path=Path(__file__).parent / ".env")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")
    
    user = UserProfile("Guest")  # Make sure UserProfile class exists and works
    api = APIClient(api_key)     # Make sure APIClient class is properly implemented
    
    chat_loop(api)

if __name__ == "__main__":
    main()
