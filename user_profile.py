# user_profile.py

class UserProfile:
    def __init__(self, name):
        self.name = name
        self.session_history = []

    def add_to_history(self, question, response):
        self.session_history.append({
            "question": question,
            "response": response
        })

    def get_history(self):
        return self.session_history
