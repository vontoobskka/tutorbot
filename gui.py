import tkinter as tk
from tkinter import filedialog, ttk
import threading
from api_handler import APIClient
from user_profile import UserProfile

class GUIManager:
    def __init__(self, api_client: APIClient, user: UserProfile):
        self.api = api_client
        self.user = user
        self.root = tk.Tk()
        self.root.title("TutorBot - Homework Helper")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        self.conversation_history = []
        self.selected_subject = tk.StringVar(value="General")
        self.attached_image_path = None
        self.selected_theme = tk.StringVar(value="Light")

        self.themes = {
            "Light": {"bg": "#f0f0f0", "fg": "#000000"},
            "Dark": {"bg": "#2b2b2b", "fg": "#ffffff"},
            "Red": {"bg": "#ffdddd", "fg": "#550000"},
            "Green": {"bg": "#ddffdd", "fg": "#005500"},
            "Blue": {"bg": "#ddeeff", "fg": "#002255"},
            "Yellow": {"bg": "#ffffdd", "fg": "#554400"},
            "Purple": {"bg": "#f0ddff", "fg": "#330044"},
            "Orange": {"bg": "#ffe5cc", "fg": "#663300"},
            "Cyan": {"bg": "#ddffff", "fg": "#005555"},
            "Pink": {"bg": "#ffddee", "fg": "#550033"}
        }

        self.math_only = tk.BooleanVar()
        self.science_only = tk.BooleanVar()

        self._setup_widgets()
        self._apply_theme()

    def _setup_widgets(self):
        ttk.Label(self.root, text="Subject:").place(x=20, y=20)
        ttk.Combobox(self.root, textvariable=self.selected_subject,
                     values=["Math", "Science", "History", "English", "General"]).place(x=80, y=20, width=100)

        ttk.Label(self.root, text="Theme:").place(x=200, y=20)
        ttk.Combobox(self.root, textvariable=self.selected_theme,
                     values=list(self.themes.keys()), state="readonly").place(x=250, y=20, width=100)

        tk.Button(self.root, text="Apply Theme", command=self._apply_theme).place(x=360, y=20)

        tk.Checkbutton(self.root, text="Math-only", variable=self.math_only).place(x=460, y=20)
        tk.Checkbutton(self.root, text="Science-only", variable=self.science_only).place(x=550, y=20)

        tk.Button(self.root, text="Attach Image", command=self._upload_image).place(x=670, y=20)

        self.chat_frame = tk.Frame(self.root)
        self.chat_frame.place(x=20, y=60, width=760, height=420)

        self.scrollbar = tk.Scrollbar(self.chat_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.chat_log = tk.Text(self.chat_frame, wrap="word", font=("Arial", 12),
                                yscrollcommand=self.scrollbar.set, bg="white")
        self.chat_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.chat_log.config(state="disabled")
        self.scrollbar.config(command=self.chat_log.yview)

        self.user_input = tk.Entry(self.root, font=("Arial", 12))
        self.user_input.place(x=20, y=500, width=620, height=30)
        self.user_input.bind("<Return>", self._on_enter_pressed)

        tk.Button(self.root, text="Send", command=self._on_enter_pressed).place(x=660, y=500, width=120, height=30)

        tk.Button(self.root, text="Save Conversation", command=self._save_conversation).place(x=640, y=540, width=140)

    def _apply_theme(self):
        theme = self.themes[self.selected_theme.get()]
        self.root.configure(bg=theme["bg"])
        self.chat_log.config(bg=theme["bg"], fg=theme["fg"])
        self.user_input.config(bg="white", fg="black")

    def _upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if not file_path:
            return
        self.attached_image_path = file_path
        self._add_to_chat_log("🖼️ Image attached. (It'll be sent with your next message)")

    def _on_enter_pressed(self, event=None):
        user_msg = self.user_input.get().strip()
        if not user_msg and not self.attached_image_path:
            return
        if user_msg:
            self._add_to_chat_log(f"You: {user_msg}")
        elif self.attached_image_path:
            self._add_to_chat_log("You sent an image.")

        self.user_input.delete(0, tk.END)
        self._get_ai_response(text=user_msg or None, image_path=self.attached_image_path)
        self.attached_image_path = None

    def _add_to_chat_log(self, message):
        self.chat_log.config(state="normal")
        self.chat_log.insert(tk.END, message + "\n")
        self.chat_log.see(tk.END)
        self.chat_log.config(state="disabled")

    def _get_ai_response(self, text=None, image_path=None):
        threading.Thread(target=self._fetch_response, args=(text, image_path)).start()

    def _fetch_response(self, text, image_path):
        try:
            history = "\n".join(self.conversation_history[-10:])
            subject = self.selected_subject.get()
            filters = ""
            if self.math_only.get():
                filters += "Respond only with math-related help. "
            if self.science_only.get():
                filters += "Respond only with science-related help. "

            prompt = f"{history}\nSubject: {subject}\n{filters}"
            if text:
                prompt += f"User: {text}\nBot:"

            response = self.api.get_response(prompt, image_path=image_path)
            self.conversation_history.append(f"User: {text or '[Image]'}")
            self.conversation_history.append(f"Bot: {response}")
            self._add_to_chat_log("Bot: " + response)
        except Exception as e:
            self._add_to_chat_log(f"Bot Error: {str(e)}")

    def _save_conversation(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text Files", "*.txt")])
        if not file_path:
            return
        with open(file_path, "w", encoding="utf-8") as f:
            for line in self.conversation_history:
                f.write(line + "\n")
        self._add_to_chat_log("📄 Conversation saved!")

    def run(self):
        self.root.mainloop()

