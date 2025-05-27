import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class GUIManager:
    def __init__(self, api_client, user):
        self.api_client = api_client
        self.user = user
        self.root = tk.Tk()
        self.root.title("Tutor Bot - Homework Helper")
        self.root.geometry("600x500")
        self.root.config(bg="#282c34")  # dark background color

        self._setup_widgets()

    def _setup_widgets(self):
        # Dropdown for subjects
        self.subject_var = tk.StringVar()
        subjects = ["Math", "Science", "English", "History"]
        self.subject_dropdown = ttk.Combobox(self.root, textvariable=self.subject_var, values=subjects)
        self.subject_dropdown.current(0)
        self.subject_dropdown.pack(pady=10)

        # Button to upload image
        self.upload_button = tk.Button(self.root, text="Upload Homework Image", command=self._upload_image)
        self.upload_button.pack(pady=10)

        # Textbox for user input
        self.user_input = tk.Entry(self.root, font=("Arial", 14))
        self.user_input.pack(fill='x', padx=20, pady=10)
        self.user_input.bind("<Return>", self._on_enter_pressed)

        # Text widget for bot response
        self.response_area = tk.Text(self.root, height=15, bg="#1e2228", fg="white", font=("Arial", 12))
        self.response_area.pack(fill='both', padx=20, pady=10, expand=True)
        self.response_area.config(state=tk.DISABLED)

    def _upload_image(self):
        filename = filedialog.askopenfilename(
            title="Select Homework Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if filename:
            messagebox.showinfo("Image Selected", f"Image file selected:\n{filename}")
            # TODO: Add image analysis call here using API

    def _on_enter_pressed(self, event):
        question = self.user_input.get().strip()
        if not question:
            return
        self.user_input.delete(0, tk.END)

        # Show user question in response area
        self._append_text(f"You: {question}\n")

        # Call your API client to get a response (async recommended but sync for now)
        response = self.api_client.get_response(question)

        # Show bot response
        self._append_text(f"Bot: {response}\n\n")

    def _append_text(self, text):
        self.response_area.config(state=tk.NORMAL)
        self.response_area.insert(tk.END, text)
        self.response_area.see(tk.END)
        self.response_area.config(state=tk.DISABLED)

    def run(self):
        self.root.mainloop()
