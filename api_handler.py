import google.generativeai as genai

class APIClient:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.chat = self.model.start_chat(history=[])

    def get_response(self, text=None, image_bytes=None):
        try:
            if image_bytes and text:
                response = self.chat.send_message([
                    text,
                    {"mime_type": "image/jpeg", "data": image_bytes}
                ])
            elif image_bytes:
                response = self.chat.send_message({
                    "mime_type": "image/jpeg",
                    "data": image_bytes
                })
            elif text:
                response = self.chat.send_message(text)
            else:
                return "No input provided."

            return response.text
        except Exception as e:
            return f"Bot Error: {str(e)}"
