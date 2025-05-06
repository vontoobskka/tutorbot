# gui.py
import tkinter as tk
from tkinter import scrolledtext

class GUIManager:
    def __init__(self, api_client, user):
        self.api_client = api_client
        self.user = user

        self.window = tk.Tk()
        self.window.title("TutorBot - Powered by Gemini")
        self.window.geometry("600x500")

        # Chat display area
        self.chat_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD, state='disabled')
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # User input field
        self.user_input = tk.Entry(self.window, font=("Arial", 12))
        self.user_input.pack(padx=10, pady=(0,10), fill=tk.X)
        self.user_input.bind("<Return>", self.send_message)

        # Send button
        self.send_button = tk.Button(self.window, text="Send", command=self.send_message)
        self.send_button.pack(pady=(0, 10))

    def send_message(self, event=None):
        user_msg = self.user_input.get().strip()
        if user_msg == "":
            return

        self.display_message(f"You: {user_msg}")
        self.user_input.delete(0, tk.END)

        bot_reply = self.api_client.get_response(user_msg)
        self.display_message(f"TutorBot: {bot_reply}")

    def display_message(self, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, message + "\n\n")
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)

    def run(self):
        self.window.mainloop()
