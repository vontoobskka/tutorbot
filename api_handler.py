import google.generativeai as genai


class APIClient:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def get_response(self, user_input):
        try:
            response = self.model.generate_content(user_input)
            return response.text
        except Exception as e:
            return f"Error contacting AI: {e}"
