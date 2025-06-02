import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import datetime
import json
import threading
import time
import os
import platform
import sys

try:
    import winsound  # Windows only for notification sounds
except ImportError:
    winsound = None

class TutorBotGUI:
    THEMES = {
        "Dark": {"bg": "#282c34", "fg": "white", "input_bg": "#1e2228", "input_fg": "white"},
        "Light": {"bg": "white", "fg": "black", "input_bg": "white", "input_fg": "black"},
        "Red": {"bg": "#ffcccc", "fg": "#660000", "input_bg": "#ffe6e6", "input_fg": "#660000"},
        "Green": {"bg": "#ccffcc", "fg": "#006600", "input_bg": "#e6ffe6", "input_fg": "#006600"},
        "Blue": {"bg": "#cce5ff", "fg": "#003366", "input_bg": "#e6f0ff", "input_fg": "#003366"},
        # Add more themes if you want
    }

    QUICK_REPLIES = ["Hello!", "Thanks!", "Can you help with math?", "Science question", "Explain history"]

    def __init__(self, api_client, user):
        self.api_client = api_client
        self.user = user
        self.root = tk.Tk()
        self.root.title("Tutor Bot - Homework Helper")
        self.root.geometry("700x600")
        self.root.minsize(600, 500)

        # Conversation history for export/search
        self.conversation = []

        # Current attached image bytes
        self.attached_image = None

        # Settings variables
        self.subject_var = tk.StringVar(value="Math")
        self.theme_var = tk.StringVar(value="Dark")
        self.font_size_var = tk.IntVar(value=12)
        self.show_timestamps = tk.BooleanVar(value=True)
        self.notification_sound = tk.BooleanVar(value=True)
        self.ai_delay = tk.DoubleVar(value=0.5)

        # Search variables
        self.search_var = tk.StringVar()
        self.search_results = []
        self.search_index = 0

        self._setup_widgets()
        self._apply_theme()

        # Auto dark mode based on time (6PM-6AM)
        self._auto_dark_mode()

        # Load last session conversation if exists
        self._load_last_session()

        # Drag and drop image attach (Windows only)
        if platform.system() == 'Windows':
            self._enable_drag_drop()

    def _setup_widgets(self):
        # Top frame for subject, theme, font size, toggle timestamps, save/load buttons
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=5)

        # Subject dropdown
        tk.Label(top_frame, text="Subject:").pack(side="left")
        subjects = ["Math", "Science", "English", "History", "General"]
        self.subject_dropdown = ttk.Combobox(top_frame, textvariable=self.subject_var, values=subjects, state="readonly", width=10)
        self.subject_dropdown.pack(side="left", padx=5)

        # Theme dropdown
        tk.Label(top_frame, text="Theme:").pack(side="left", padx=(10, 0))
        self.theme_dropdown = ttk.Combobox(top_frame, textvariable=self.theme_var, values=list(self.THEMES.keys()), state="readonly", width=10)
        self.theme_dropdown.pack(side="left", padx=5)
        self.theme_dropdown.bind("<<ComboboxSelected>>", lambda e: self._apply_theme())

        # Font size selector
        tk.Label(top_frame, text="Font Size:").pack(side="left", padx=(10, 0))
        self.font_spin = tk.Spinbox(top_frame, from_=8, to=20, textvariable=self.font_size_var, width=3, command=self._apply_theme)
        self.font_spin.pack(side="left", padx=5)

        # Show timestamps checkbox
        self.ts_cb = tk.Checkbutton(top_frame, text="Show Timestamps", variable=self.show_timestamps, command=self._refresh_chat)
        self.ts_cb.pack(side="left", padx=10)

        # Notification sound toggle
        self.sound_cb = tk.Checkbutton(top_frame, text="Notification Sound", variable=self.notification_sound)
        self.sound_cb.pack(side="left", padx=10)

        # Save conversation button
        self.save_btn = tk.Button(top_frame, text="Save Conversation", command=self._save_conversation)
        self.save_btn.pack(side="right", padx=5)

        # Load conversation button
        self.load_btn = tk.Button(top_frame, text="Load Conversation", command=self._load_conversation)
        self.load_btn.pack(side="right", padx=5)

        # AI response delay slider
        delay_frame = tk.Frame(self.root)
        delay_frame.pack(fill="x", padx=10, pady=(0,5))
        tk.Label(delay_frame, text="AI Response Delay (seconds):").pack(side="left")
        self.delay_slider = tk.Scale(delay_frame, variable=self.ai_delay, from_=0, to=3, resolution=0.1, orient="horizontal", length=150)
        self.delay_slider.pack(side="left", padx=5)

        # Middle frame: chat display + scrollbar
        chat_frame = tk.Frame(self.root)
        chat_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.chat_text = tk.Text(chat_frame, state="disabled", wrap="word", font=("Arial", self.font_size_var.get()), bg="#1e2228", fg="white", padx=5, pady=5)
        self.chat_text.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(chat_frame, command=self.chat_text.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.chat_text['yscrollcommand'] = self.scrollbar.set

        # Bottom frame: input + buttons + quick replies + image upload + emoji picker
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill="x", padx=10, pady=10)

        # User input
        self.user_input = tk.Entry(bottom_frame, font=("Arial", self.font_size_var.get()))
        self.user_input.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.user_input.bind("<Return>", self._on_enter)

        # Send button
        self.send_btn = tk.Button(bottom_frame, text="Send", command=self._on_enter)
        self.send_btn.pack(side="left")

        # Upload image button
        self.upload_btn = tk.Button(bottom_frame, text="Attach Image", command=self._upload_image)
        self.upload_btn.pack(side="left", padx=5)

        # Emoji picker button
        self.emoji_btn = tk.Button(bottom_frame, text="😀", command=self._show_emoji_picker)
        self.emoji_btn.pack(side="left")

        # Quick replies frame
        quick_reply_frame = tk.Frame(self.root)
        quick_reply_frame.pack(fill="x", padx=10, pady=(0,10))

        tk.Label(quick_reply_frame, text="Quick Replies:").pack(side="left")
        for qr in self.QUICK_REPLIES:
            b = tk.Button(quick_reply_frame, text=qr, command=lambda t=qr: self._insert_quick_reply(t))
            b.pack(side="left", padx=3)

        # Search frame
        search_frame = tk.Frame(self.root)
        search_frame.pack(fill="x", padx=10)

        tk.Label(search_frame, text="Search Chat:").pack(side="left")
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.search_entry.bind("<Return>", self._search_chat)

        self.search_prev_btn = tk.Button(search_frame, text="Prev", command=lambda: self._search_chat(prev=True))
        self.search_prev_btn.pack(side="left", padx=2)
        self.search_next_btn = tk.Button(search_frame, text="Next", command=lambda: self._search_chat(prev=False))
        self.search_next_btn.pack(side="left", padx=2)

    # === Theme and UI updates ===

    def _apply_theme(self, event=None):
        theme = self.THEMES.get(self.theme_var.get(), self.THEMES["Dark"])
        bg, fg, input_bg, input_fg = theme["bg"], theme["fg"], theme["input_bg"], theme["input_fg"]

        # Root background
        self.root.config(bg=bg)

        # Chat text colors + font size
        self.chat_text.config(bg=input_bg, fg=input_fg, font=("Arial", self.font_size_var.get()))

        # Input and button colors
        self.user_input.config(bg=input_bg, fg=input_fg, font=("Arial", self.font_size_var.get()), insertbackground=fg)
        self.upload_btn.config(bg=bg, fg=fg)
        self.send_btn.config(bg=bg, fg=fg)
        self.emoji_btn.config(bg=bg, fg=fg)

        # Dropdowns & checkbuttons need ttk style update (if you want, can customize further)

        # Refresh chat to apply font size and timestamps
        self._refresh_chat()

    def _refresh_chat(self):
        self.chat_text.config(state="normal")
        self.chat_text.delete(1.0, tk.END)
        for item in self.conversation:
            timestamp = f"[{item['time']}]" if self.show_timestamps.get() else ""
            prefix = f"{timestamp} {item['sender']}: " if timestamp else f"{item['sender']}: "
            self.chat_text.insert(tk.END, prefix + item['text'] + "\n")
        self.chat_text.see(tk.END)
        self.chat_text.config(state="disabled")

    def _auto_dark_mode(self):
        hour = datetime.datetime.now().hour
        if 18 <= hour or hour < 6:
            self.theme_var.set("Dark")
        else:
            self.theme_var.set("Light")
        self._apply_theme()
        # Re-run every hour
        self.root.after(3600000, self._auto_dark_mode)

    # === Conversation handling ===

    def _append_message(self, sender, text):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.conversation.append({"sender": sender, "text": text, "time": now})
        self._refresh_chat()
        if sender == "Bot" and self.notification_sound.get():
            self._play_notification_sound()

    def _play_notification_sound(self):
        if winsound:
            winsound.MessageBeep(winsound.MB_OK)
        else:
            # fallback: beep on *nix/mac
            print('\a')

    def _save_conversation(self):
        filetypes = [("Text files", "*.txt"), ("JSON files", "*.json")]
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=filetypes)
        if not filename:
            return
        try:
            if filename.endswith(".json"):
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(self.conversation, f, indent=2)
            else:
                with open(filename, "w", encoding="utf-8") as f:
                    for msg in self.conversation:
                        ts = f"[{msg['time']}]" if self.show_timestamps.get() else ""
                        f.write(f"{ts} {msg['sender']}: {msg['text']}\n")
            messagebox.showinfo("Success", f"Conversation saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def _load_conversation(self):
        filetypes = [("Text files", "*.txt"), ("JSON files", "*.json")]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if not filename:
            return
        try:
            loaded = []
            if filename.endswith(".json"):
                with open(filename, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
            else:
                with open(filename, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        # Basic parsing for txt files: "[HH:MM:SS] Sender: Text"
                        parts = line.split(" ", 2)
                        if len(parts) >= 3 and parts[0].startswith("[") and parts[0].endswith("]") and ":" in parts[1]:
                            time_str = parts[0][1:-1]
                            sender = parts[1][:-1]  # Remove colon
                            text = parts[2]
                        else:
                            time_str = ""
                            sender = "User"
                            text = line
                        loaded.append({"sender": sender, "text": text, "time": time_str})
            self.conversation = loaded
            self._refresh_chat()
            messagebox.showinfo("Success", f"Conversation loaded from {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {e}")

    def _load_last_session(self):
        path = "last_session.json"
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.conversation = json.load(f)
                self._refresh_chat()
            except:
                pass
        # Save on close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        try:
            with open("last_session.json", "w", encoding="utf-8") as f:
                json.dump(self.conversation, f, indent=2)
        except:
            pass
        self.root.destroy()

    # === Search functionality ===

    def _search_chat(self, event=None, prev=False):
        term = self.search_var.get().lower()
        if not term:
            return
        if not self.search_results:
            # Find all matches
            self.search_results = [i for i, msg in enumerate(self.conversation) if term in msg['text'].lower()]
            self.search_index = 0 if not prev else len(self.search_results) - 1
        else:
            # Navigate results
            if prev:
                self.search_index = (self.search_index - 1) % len(self.search_results)
            else:
                self.search_index = (self.search_index + 1) % len(self.search_results)
        if not self.search_results:
            messagebox.showinfo("Search", "No matches found.")
            return
        idx = self.search_results[self.search_index]
        # Scroll chat to message index
        self.chat_text.config(state="normal")
        self.chat_text.tag_remove("search", "1.0", tk.END)
        line_index = idx + 1
        self.chat_text.see(f"{line_index}.0")
        start = f"{line_index}.0"
        end = f"{line_index}.end"
        self.chat_text.tag_add("search", start, end)
        self.chat_text.tag_config("search", background="yellow", foreground="black")
        self.chat_text.config(state="disabled")

    # === Input and message sending ===

    def _on_enter(self, event=None):
        question = self.user_input.get().strip()
        if not question and not self.attached_image:
            return
        self.user_input.delete(0, tk.END)

        # Show user input in chat
        text = question if question else "(Image sent)"
        self._append_message("You", text)

        # Disable input & show typing indicator
        self._set_input_state(False)
        self._show_typing_indicator()

        # Call API with delay in separate thread
        threading.Thread(target=self._call_api, args=(question, self.attached_image), daemon=True).start()
        self.attached_image = None  # reset after sending

    def _set_input_state(self, enabled):
        state = "normal" if enabled else "disabled"
        self.user_input.config(state=state)
        self.send_btn.config(state=state)
        self.upload_btn.config(state=state)
        self.emoji_btn.config(state=state)

    def _show_typing_indicator(self):
        self._append_message("Bot", "Typing...")

    def _remove_typing_indicator(self):
        # Remove last Bot "Typing..." message
        if self.conversation and self.conversation[-1]["text"] == "Typing...":
            self.conversation.pop()
            self._refresh_chat()

    def _call_api(self, text, image_bytes):
        delay = self.ai_delay.get()
        time.sleep(delay)  # simulate thinking delay

        # Actually call the API client (replace with real call)
        if image_bytes:
            response = self.api_client.get_response(text, image_bytes=image_bytes)
        else:
            response = self.api_client.get_response(text)

        # Update UI on main thread
        self.root.after(0, self._update_bot_response, response)

    def _update_bot_response(self, response):
        self._remove_typing_indicator()
        self._append_message("Bot", response)
        self._set_input_state(True)

    # === Image attachment ===

    def _upload_image(self):
        filename = filedialog.askopenfilename(
            title="Select Homework Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if filename:
            try:
                with open(filename, "rb") as f:
                    self.attached_image = f.read()
                self._append_message("You", "(Image attached)")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")

    def _enable_drag_drop(self):
        # Windows only: support dragging image files onto window to attach
        def drop(event):
            files = self.root.tk.splitlist(event.data)
            for f in files:
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                    try:
                        with open(f, "rb") as imgf:
                            self.attached_image = imgf.read()
                        self._append_message("You", f"(Image attached: {os.path.basename(f)})")
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to load image: {e}")
                else:
                    messagebox.showwarning("Invalid file", "Only image files are supported.")
            return "break"

        # Requires tkdnd package or Windows 10+ native drag drop
        try:
            import tkinterdnd2
            self.root = tkinterdnd2.TkinterDnD.Tk()
            self.root.drop_target_register(tkinterdnd2.DND_FILES)
            self.root.dnd_bind('<<Drop>>', drop)
        except ImportError:
            # No drag and drop if module not available
            pass

    # === Quick replies ===

    def _insert_quick_reply(self, text):
        self.user_input.delete(0, tk.END)
        self.user_input.insert(0, text)
        self.user_input.focus()

    # === Emoji picker ===

    def _show_emoji_picker(self):
        # Simple emoji picker window
        emojis = "😀 😃 😄 😁 😆 😅 😂 🤣 😊 😇 🙂 🙃 😉 😌 😍 🥰 😘 😗 😙 😚"
        top = tk.Toplevel(self.root)
        top.title("Emoji Picker")
        top.geometry("300x100")
        top.transient(self.root)
        top.grab_set()

        def insert_emoji(e):
            self.user_input.insert(tk.END, e.widget.cget("text"))
            top.destroy()
            self.user_input.focus()

        for em in emojis.split():
            b = tk.Button(top, text=em, font=("Arial", 14), command=lambda e=em: insert_emoji(e))
            b.pack(side="left", padx=3)

    # === Run ===

    def run(self):
        self.root.mainloop()
