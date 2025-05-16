# main.py
import os
from dotenv import load_dotenv
from pathlib import Path

def main():
    # Explicitly load .env from same folder as main.py
    load_dotenv(dotenv_path=Path(__file__).parent / ".env")
    
    api_key = os.getenv("GEMINI_API_KEY")
    print("DEBUG: Loaded key =", api_key)
    
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")

if __name__ == "__main__":
    main()
