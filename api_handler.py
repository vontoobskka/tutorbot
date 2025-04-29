# api_handler.py
import requests

class APIClient:
    def __init__(self, api_key="YOUR_API_KEY_HERE"):
        self.api_key = api_key
        self.url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def get_response(self, prompt):
        data = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }

        try:
            response = requests.post(self.url, headers=self.headers, json=data)
            response.raise_for_status()
            content = response.json()
            return content['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            return f"Error contacting AI: {e}"
