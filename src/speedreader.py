import customtkinter as ctk
from tkinter import filedialog, Toplevel, Listbox, Scale, ttk, colorchooser
import threading
import time
import os
import shutil
import json
from datetime import datetime
import pyttsx3

class SpeedReader:
    def __init__(self, root):
        self.root = root
        self.root.title("Speed Reader Pro")
        self.root.geometry("1000x700")
        
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Default speech rate
        self.speech_enabled = False
        self.speech_thread = None
        
        # Get available voices
        self.voices = self.engine.getProperty('voices')
        self.current_voice = 0  # Default to first voice
        
        # Filter for English voices
        self.english_voices = [i for i, voice in enumerate(self.voices) if "english" in voice.name.lower()]
        if not self.english_voices:
            self.english_voices = [0]  # Fallback to first voice if no English voices found
        
        # Theme configurations
        self.themes = {
            "dark": {
                "bg": "#1C1C3C",
                "fg": "#EAEAEA",
                "accent": "#2A2A5A",
                "button": "#3A3A5A",
                "highlight": "#FFD700"
            },
            "light": {
                "bg": "#F0F0F0",
                "fg": "#333333",
                "accent": "#E0E0E0",
                "button": "#D0D0D0",
                "highlight": "#FFA500"
            },
            "ocean": {
                "bg": "#1B3B4B",
                "fg": "#E0F4FF",
                "accent": "#2A4B5C",
                "button": "#3A5B6C",
                "highlight": "#00FFFF"
            },
            "forest": {
                "bg": "#1B3B1B",
                "fg": "#E0FFE0",
                "accent": "#2A4B2A",
                "button": "#3A5B3A",
                "highlight": "#00FF00"
            },
            "sunset": {
                "bg": "#4B1B1B",
                "fg": "#FFE0E0",
                "accent": "#5C2A2A",
                "button": "#6C3A3A",
                "highlight": "#FF4500"
            }
        }
        
        # Initialize variables
        self.text = []
        self.index = 0
        self.running = False
        self.speed = 0.09
        self.font_size = 42
        self.current_book = None
        self.bookmarks = []
        self.reading_stats = {
            "total_words_read": 0,
            "total_time": 0,
            "average_speed": 0,
            "sessions": []
        }
        self.reading_mode = "word"  # word, sentence, or paragraph
        self.display_mode = "standard"  # standard, focus, or dynamic
        self.auto_scroll = False
        self.show_progress = True
        self.show_stats_overlay = False
        self.font_family = "Poppins"
        self.highlight_color = "#FFD700"
        self.current_theme = "dark"
        self.custom_colors = {
            "bg": None,
            "fg": None,
            "accent": None,
            "button": None,
            "highlight": None
        }
        
        # Create data directories if they don't exist
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.books_dir = os.path.join(self.base_dir, "data", "books")
        self.stats_dir = os.path.join(self.base_dir, "data", "stats")
        os.makedirs(self.books_dir, exist_ok=True)
        os.makedirs(self.stats_dir, exist_ok=True)
        
        # Load saved data
        self.load_stats()
        self.load_bookmarks()
        self.load_theme_preferences()
        
        # Create main container
        self.main_container = ctk.CTkFrame(root)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Top bar with theme toggle and stats
        self.top_bar = ctk.CTkFrame(self.main_container)
        self.top_bar.pack(fill="x", pady=(0, 10))
        
        # Theme selector
        self.theme_var = ctk.StringVar(value=self.current_theme)
        self.theme_menu = ctk.CTkOptionMenu(
            self.top_bar,
            values=list(self.themes.keys()),
            variable=self.theme_var,
            command=self.apply_theme,
            width=120
        )
        self.theme_menu.pack(side="left", padx=5)
        
        # Custom color button
        self.custom_color_button = ctk.CTkButton(
            self.top_bar,
            text="Custom Colors",
            command=self.choose_custom_colors,
            width=120
        )
        self.custom_color_button.pack(side="left", padx=5)
        
        self.stats_button = ctk.CTkButton(
            self.top_bar,
            text="Reading Stats",
            command=self.show_stats,
            width=120
        )
        self.stats_button.pack(side="left", padx=5)
        
        # Main display
        self.label = ctk.CTkLabel(
            self.main_container,
            text="Select a file to begin",
            font=("Poppins", 36, "bold"),
            wraplength=800
        )
        self.label.pack(pady=20)
        
        # Control panel
        self.control_frame = ctk.CTkFrame(self.main_container)
        self.control_frame.pack(pady=10)
        
        # Speed control
        self.speed_label = ctk.CTkLabel(self.control_frame, text="Speed:")
        self.speed_label.pack()
        
        self.speed_slider = ctk.CTkSlider(
            self.control_frame,
            from_=0.02,
            to=0.2,
            number_of_steps=18,
            command=self.update_speed
        )
        self.speed_slider.set(0.09)
        self.speed_slider.pack(pady=5)
        
        # Font size control
        self.font_label = ctk.CTkLabel(self.control_frame, text="Font Size:")
        self.font_label.pack()
        
        self.font_slider = ctk.CTkSlider(
            self.control_frame,
            from_=20,
            to=60,
            number_of_steps=20,
            command=self.update_font_size
        )
        self.font_slider.set(42)
        self.font_slider.pack(pady=5)
        
        # Reading mode selector
        self.mode_frame = ctk.CTkFrame(self.control_frame)
        self.mode_frame.pack(pady=5)
        
        self.mode_label = ctk.CTkLabel(self.mode_frame, text="Reading Mode:")
        self.mode_label.pack(side="left", padx=5)
        
        self.mode_var = ctk.StringVar(value="word")
        modes = [
            ("Word", "word"),
            ("Sentence", "sentence"),
            ("Paragraph", "paragraph")
        ]
        
        for text, mode in modes:
            rb = ctk.CTkRadioButton(
                self.mode_frame,
                text=text,
                variable=self.mode_var,
                value=mode,
                command=self.update_reading_mode
            )
            rb.pack(side="left", padx=5)
        
        # Display options frame
        self.display_frame = ctk.CTkFrame(self.control_frame)
        self.display_frame.pack(pady=10)
        
        # Display mode selector
        self.display_label = ctk.CTkLabel(self.display_frame, text="Display Mode:")
        self.display_label.pack(side="left", padx=5)
        
        self.display_var = ctk.StringVar(value="standard")
        self.display_menu = ctk.CTkOptionMenu(
            self.display_frame,
            values=["Standard", "Focus", "Dynamic"],
            variable=self.display_var,
            command=self.update_display_mode,
            width=120
        )
        self.display_menu.pack(side="left", padx=5)

        # Font selector
        self.font_frame = ctk.CTkFrame(self.control_frame)
        self.font_frame.pack(pady=5)
        
        self.font_label = ctk.CTkLabel(self.font_frame, text="Font:")
        self.font_label.pack(side="left", padx=5)
        
        self.font_var = ctk.StringVar(value="Poppins")
        self.font_menu = ctk.CTkOptionMenu(
            self.font_frame,
            values=["Poppins", "Arial", "Helvetica", "Times New Roman", "Georgia", "Verdana"],
            variable=self.font_var,
            command=self.update_font,
            width=120
        )
        self.font_menu.pack(side="left", padx=5)

        # Options frame for checkboxes
        self.options_frame = ctk.CTkFrame(self.control_frame)
        self.options_frame.pack(pady=10)
        
        # Show progress option
        self.progress_var = ctk.BooleanVar(value=True)
        self.progress_cb = ctk.CTkCheckBox(
            self.options_frame,
            text="Show Progress",
            variable=self.progress_var,
            command=self.toggle_progress
        )
        self.progress_cb.pack(side="left", padx=10)
        
        # Show stats overlay option
        self.stats_overlay_var = ctk.BooleanVar(value=False)
        self.stats_overlay_cb = ctk.CTkCheckBox(
            self.options_frame,
            text="Stats Overlay",
            variable=self.stats_overlay_var,
            command=self.toggle_stats_overlay
        )
        self.stats_overlay_cb.pack(side="left", padx=10)
        
        # Add speech controls to options frame
        self.speech_var = ctk.BooleanVar(value=False)
        self.speech_cb = ctk.CTkCheckBox(
            self.options_frame,
            text="Text-to-Speech",
            variable=self.speech_var,
            command=self.toggle_speech
        )
        self.speech_cb.pack(side="left", padx=10)
        
        # Speech rate control
        self.speech_rate_label = ctk.CTkLabel(self.control_frame, text="Speech Rate:")
        self.speech_rate_label.pack()
        
        self.speech_rate_slider = ctk.CTkSlider(
            self.control_frame,
            from_=100,
            to=300,
            number_of_steps=20,
            command=self.update_speech_rate
        )
        self.speech_rate_slider.set(150)
        self.speech_rate_slider.pack(pady=5)
        
        # Add voice selection to control frame
        self.voice_frame = ctk.CTkFrame(self.control_frame)
        self.voice_frame.pack(pady=5)
        
        self.voice_label = ctk.CTkLabel(self.voice_frame, text="Voice:")
        self.voice_label.pack(side="left", padx=5)
        
        # Create voice names list
        voice_names = [voice.name for voice in self.voices]
        self.voice_var = ctk.StringVar(value=voice_names[0])
        self.voice_menu = ctk.CTkOptionMenu(
            self.voice_frame,
            values=voice_names,
            variable=self.voice_var,
            command=self.update_voice,
            width=200
        )
        self.voice_menu.pack(side="left", padx=5)
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(self.main_container)
        self.progress.set(0)
        self.progress.pack(pady=20, padx=20, fill="x")
        
        # Button frame
        self.button_frame = ctk.CTkFrame(self.main_container)
        self.button_frame.pack(pady=20)
        
        # Buttons with modern styling
        button_style = {
            "width": 120,
            "height": 40,
            "corner_radius": 10
        }
        
        self.import_button = ctk.CTkButton(
            self.button_frame,
            text="Import",
            command=self.import_book,
            **button_style
        )
        self.import_button.pack(side="left", padx=10)
        
        self.library_button = ctk.CTkButton(
            self.button_frame,
            text="Library",
            command=self.open_library,
            **button_style
        )
        self.library_button.pack(side="left", padx=10)
        
        self.restart_button = ctk.CTkButton(
            self.button_frame,
            text="Restart",
            command=self.restart,
            **button_style
        )
        self.restart_button.pack(side="left", padx=10)
        
        self.bookmark_button = ctk.CTkButton(
            self.button_frame,
            text="Bookmark",
            command=self.add_bookmark,
            **button_style
        )
        self.bookmark_button.pack(side="left", padx=10)
        
        # Apply initial theme
        self.apply_theme(self.current_theme)
        
        # Keyboard bindings
        self.root.bind("<space>", self.toggle)
        self.root.bind("<Escape>", lambda e: self.stop())
        self.root.bind("<Left>", lambda e: self.change_word(-1))
        self.root.bind("<Right>", lambda e: self.change_word(1))
        
    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        theme = self.themes[theme_name]
        
        # Apply theme colors
        self.main_container.configure(fg_color=theme["bg"])
        self.top_bar.configure(fg_color=theme["accent"])
        self.control_frame.configure(fg_color=theme["accent"])
        self.button_frame.configure(fg_color=theme["accent"])
        
        # Update label colors
        self.label.configure(text_color=theme["fg"])
        
        # Update button colors
        for button in [self.custom_color_button, self.stats_button,
                      self.import_button, self.library_button, self.restart_button,
                      self.bookmark_button]:
            button.configure(
                fg_color=theme["button"],
                hover_color=theme["accent"],
                text_color=theme["fg"]
            )
        
        # Configure theme menu separately
        self.theme_menu.configure(
            fg_color=theme["button"],
            text_color=theme["fg"]
        )
        
        # Update sliders
        self.speed_slider.configure(
            fg_color=theme["accent"],
            button_color=theme["button"],
            button_hover_color=theme["highlight"]
        )
        self.font_slider.configure(
            fg_color=theme["accent"],
            button_color=theme["button"],
            button_hover_color=theme["highlight"]
        )
        
        # Update progress bar
        self.progress.configure(
            fg_color=theme["accent"],
            progress_color=theme["highlight"]
        )
        
        # Save theme preference
        self.save_theme_preferences()
        
    def choose_custom_colors(self):
        color_window = ctk.CTkToplevel(self.root)
        color_window.title("Custom Colors")
        color_window.geometry("400x300")
        
        def choose_color(color_type):
            color = colorchooser.askcolor(title=f"Choose {color_type} color")[1]
            if color:
                self.custom_colors[color_type] = color
                self.apply_custom_colors()
        
        # Create buttons for each color type
        for color_type in ["bg", "fg", "accent", "button", "highlight"]:
            btn = ctk.CTkButton(
                color_window,
                text=f"Choose {color_type} color",
                command=lambda ct=color_type: choose_color(ct)
            )
            btn.pack(pady=5)
        
        # Reset button
        reset_btn = ctk.CTkButton(
            color_window,
            text="Reset to Theme",
            command=self.reset_custom_colors
        )
        reset_btn.pack(pady=10)
        
    def apply_custom_colors(self):
        if all(self.custom_colors.values()):
            self.apply_theme("custom")
            
    def reset_custom_colors(self):
        self.custom_colors = {k: None for k in self.custom_colors}
        self.apply_theme(self.current_theme)
        
    def save_theme_preferences(self):
        theme_prefs = {
            "current_theme": self.current_theme,
            "custom_colors": self.custom_colors
        }
        theme_path = os.path.join(self.stats_dir, "theme_preferences.json")
        with open(theme_path, "w") as f:
            json.dump(theme_prefs, f)
            
    def load_theme_preferences(self):
        theme_path = os.path.join(self.stats_dir, "theme_preferences.json")
        try:
            if os.path.exists(theme_path) and os.path.getsize(theme_path) > 0:
                with open(theme_path, "r") as f:
                    theme_prefs = json.load(f)
                    self.current_theme = theme_prefs.get("current_theme", "dark")
                    self.custom_colors = theme_prefs.get("custom_colors", {k: None for k in self.custom_colors})
        except (FileNotFoundError, json.JSONDecodeError):
            self.current_theme = "dark"
            self.custom_colors = {k: None for k in self.custom_colors}
            
    def toggle_theme(self):
        current_theme = ctk.get_appearance_mode()
        new_theme = "light" if current_theme == "dark" else "dark"
        ctk.set_appearance_mode(new_theme)
        
    def update_reading_mode(self):
        self.reading_mode = self.mode_var.get()
        
    def show_stats(self):
        stats_window = ctk.CTkToplevel(self.root)
        stats_window.title("Reading Statistics")
        stats_window.geometry("400x300")
        
        stats_text = f"""
        Total Words Read: {self.reading_stats['total_words_read']}
        Total Reading Time: {self.reading_stats['total_time']:.1f} minutes
        Average Speed: {self.reading_stats['average_speed']:.1f} wpm
        """
        
        stats_label = ctk.CTkLabel(stats_window, text=stats_text, font=("Poppins", 14))
        stats_label.pack(pady=20)
        
    def add_bookmark(self):
        if self.text and self.current_book:
            bookmark = {
                "book": self.current_book,
                "position": self.index,
                "word": self.text[self.index],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.bookmarks.append(bookmark)
            self.save_bookmarks()
            
            # Show notification
            self.show_notification("Bookmark added!")
            
    def show_notification(self, message):
        notification = ctk.CTkLabel(
            self.main_container,
            text=message,
            font=("Poppins", 12),
            fg_color="#4CAF50",
            corner_radius=5
        )
        notification.pack(pady=5)
        self.root.after(2000, notification.destroy)
        
    def save_bookmarks(self):
        bookmarks_path = os.path.join(self.stats_dir, "bookmarks.json")
        with open(bookmarks_path, "w") as f:
            json.dump(self.bookmarks, f)
            
    def load_bookmarks(self):
        bookmarks_path = os.path.join(self.stats_dir, "bookmarks.json")
        try:
            # Check if file exists and is not empty
            if os.path.exists(bookmarks_path) and os.path.getsize(bookmarks_path) > 0:
                with open(bookmarks_path, "r") as f:
                    self.bookmarks = json.load(f)
            else:
                # Initialize with empty list if file doesn't exist or is empty
                self.bookmarks = []
                self.save_bookmarks()
        except (FileNotFoundError, json.JSONDecodeError):
            # Handle both missing file and invalid JSON
            self.bookmarks = []
            self.save_bookmarks()
            
    def save_stats(self):
        stats_path = os.path.join(self.stats_dir, "reading_stats.json")
        with open(stats_path, "w") as f:
            json.dump(self.reading_stats, f)
            
    def load_stats(self):
        stats_path = os.path.join(self.stats_dir, "reading_stats.json")
        try:
            # Check if file exists and is not empty
            if os.path.exists(stats_path) and os.path.getsize(stats_path) > 0:
                with open(stats_path, "r") as f:
                    self.reading_stats = json.load(f)
            else:
                # Initialize with default stats if file doesn't exist or is empty
                self.reading_stats = {
                    "total_words_read": 0,
                    "total_time": 0,
                    "average_speed": 0,
                    "sessions": []
                }
                self.save_stats()
        except (FileNotFoundError, json.JSONDecodeError):
            # Handle both missing file and invalid JSON
            self.reading_stats = {
                "total_words_read": 0,
                "total_time": 0,
                "average_speed": 0,
                "sessions": []
            }
            self.save_stats()
            
    def update_speed(self, val):
        self.speed = float(val)
        
    def update_font_size(self, val):
        self.font_size = int(val)
        if self.text and self.index < len(self.text):
            self.label.configure(font=("Poppins", self.font_size, "bold"))
            
    def update_font(self, font_name):
        self.font_family = font_name
        if self.text and self.index < len(self.text):
            self.label.configure(font=(self.font_family, self.font_size, "bold"))
            
    def import_book(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if filepath:
            filename = os.path.basename(filepath)
            dest_path = os.path.join(self.books_dir, filename)
            shutil.copy(filepath, dest_path)
            self.show_notification(f"{filename} imported!")
            self.load_file(dest_path)
            
    def open_library(self):
        library_window = ctk.CTkToplevel(self.root)
        library_window.title("Library")
        library_window.geometry("500x400")
        
        # Create tabs for books and bookmarks
        tabview = ctk.CTkTabview(library_window)
        tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Books tab
        books_tab = tabview.add("Books")
        listbox = Listbox(
            books_tab,
            font=("Poppins", 14),
            bg="#2A2A5A",
            fg="#EAEAEA",
            selectbackground="#3A3A5A",
            selectforeground="white",
            bd=0
        )
        listbox.pack(fill="both", expand=True, padx=20, pady=20)
        
        books = os.listdir(self.books_dir)
        for book in books:
            listbox.insert("end", book)
            
        # Bookmarks tab
        bookmarks_tab = tabview.add("Bookmarks")
        bookmarks_listbox = Listbox(
            bookmarks_tab,
            font=("Poppins", 14),
            bg="#2A2A5A",
            fg="#EAEAEA",
            selectbackground="#3A3A5A",
            selectforeground="white",
            bd=0
        )
        bookmarks_listbox.pack(fill="both", expand=True, padx=20, pady=20)
        
        for bookmark in self.bookmarks:
            bookmarks_listbox.insert("end", f"{bookmark['book']} - {bookmark['word']}")
            
        def load_selected_book():
            selected_index = listbox.curselection()
            if selected_index:
                selected_book = books[selected_index[0]]
                self.load_file(os.path.join(self.books_dir, selected_book))
                library_window.destroy()
                
        select_btn = ctk.CTkButton(
            library_window,
            text="Read",
            command=load_selected_book,
            width=120,
            height=40
        )
        select_btn.pack(pady=15)
        
    def load_file(self, filepath):
        if filepath:
            with open(filepath, "r", encoding="utf-8") as f:
                self.text = f.read().split()
            self.index = 0
            self.current_book = os.path.basename(filepath)
            self.progress.set(0)
            self.label.configure(text="Press SPACE to begin")
            
    def restart(self):
        if self.text:
            self.index = 0
            self.running = False
            self.progress.set(0)
            self.label.configure(text="Press SPACE to begin")
            
    def stop(self):
        self.running = False
        
    def change_word(self, direction):
        if self.text:
            self.index = max(0, min(len(self.text) - 1, self.index + direction))
            self.label.configure(text=self.text[self.index])
            self.progress.set(self.index / len(self.text))
            
    def toggle(self, event=None):
        if self.running:
            self.running = False
            if self.speech_enabled:
                self.stop_speech()
        else:
            self.running = True
            if self.speech_enabled:
                self.start_speech()
            threading.Thread(target=self.run, daemon=True).start()
            
    def update_display_mode(self, mode):
        self.display_mode = mode.lower()
        if self.text and self.index < len(self.text):
            self.apply_display_mode(self.text[self.index])
            
    def apply_display_mode(self, text):
        if self.display_mode == "focus":
            # Highlight the middle character
            mid = len(text) // 2
            display_text = f"{text[:mid]}|{text[mid]}|{text[mid+1:]}"
        elif self.display_mode == "dynamic":
            # Adjust size based on word length
            size = max(20, min(60, 60 - len(text)))
            self.label.configure(font=(self.font_family, size, "bold"))
            display_text = text
        else:  # standard
            self.label.configure(font=(self.font_family, self.font_size, "bold"))
            display_text = text
            
        self.label.configure(text=display_text)
            
    def toggle_progress(self):
        self.show_progress = self.progress_var.get()
        self.progress.pack() if self.show_progress else self.progress.pack_forget()
        
    def toggle_stats_overlay(self):
        self.show_stats_overlay = self.stats_overlay_var.get()
        if self.show_stats_overlay:
            self.create_stats_overlay()
        else:
            self.remove_stats_overlay()
            
    def create_stats_overlay(self):
        if not hasattr(self, 'stats_overlay'):
            self.stats_overlay = ctk.CTkLabel(
                self.main_container,
                text="",
                font=("Poppins", 12),
                corner_radius=5
            )
            self.stats_overlay.place(relx=1, rely=0, anchor="ne")
        self.update_stats_overlay()
            
    def remove_stats_overlay(self):
        if hasattr(self, 'stats_overlay'):
            self.stats_overlay.destroy()
            delattr(self, 'stats_overlay')
            
    def update_stats_overlay(self):
        if hasattr(self, 'stats_overlay') and self.show_stats_overlay:
            current_speed = (
                self.index / ((time.time() - self.start_time) / 60)
                if hasattr(self, 'start_time') and self.running
                else 0
            )
            stats_text = f"WPM: {current_speed:.0f}\n"
            stats_text += f"Progress: {(self.index / len(self.text) * 100):.1f}%"
            self.stats_overlay.configure(text=stats_text)
            self.root.after(1000, self.update_stats_overlay)

    def run(self):
        self.start_time = time.time()
        while self.running and self.index < len(self.text):
            if self.reading_mode == "word":
                current_text = self.text[self.index]
            elif self.reading_mode == "sentence":
                # Collect words until we find end of sentence
                sentence = []
                while self.index < len(self.text):
                    word = self.text[self.index]
                    sentence.append(word)
                    self.index += 1
                    if word.endswith(('.', '!', '?')):
                        break
                current_text = ' '.join(sentence)
                self.index -= 1  # Adjust for the extra increment
            else:  # paragraph
                # Collect words until we find double newline or reach limit
                paragraph = []
                word_count = 0
                while self.index < len(self.text) and word_count < 50:
                    word = self.text[self.index]
                    paragraph.append(word)
                    self.index += 1
                    word_count += 1
                    if word.endswith('\n\n'):
                        break
                current_text = ' '.join(paragraph)
                self.index -= 1  # Adjust for the extra increment
            
            # Apply the current display mode
            self.apply_display_mode(current_text)
            
            if self.show_progress:
                self.progress.set(self.index / len(self.text))
                
            self.index += 1
            
            # Wait for the specified speed
            time.sleep(self.speed)
            
            # Update reading statistics
            end_time = time.time()
            reading_time = (end_time - self.start_time) / 60  # Convert to minutes
            words_read = self.index
            wpm = (words_read / reading_time) if reading_time > 0 else 0
            
            self.reading_stats["total_words_read"] += words_read
            self.reading_stats["total_time"] += reading_time
            self.reading_stats["average_speed"] = (
                self.reading_stats["total_words_read"] / self.reading_stats["total_time"]
                if self.reading_stats["total_time"] > 0 else 0
            )
            
            self.reading_stats["sessions"].append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "words_read": words_read,
                "time": reading_time,
                "speed": wpm
            })
            
            # Save updated statistics
            self.save_stats()
            
            if self.index >= len(self.text):
                self.running = False
                self.show_notification("Reading completed!")

    def toggle_speech(self):
        self.speech_enabled = self.speech_var.get()
        if self.speech_enabled and self.text and self.index < len(self.text):
            self.start_speech()
        else:
            self.stop_speech()
            
    def update_speech_rate(self, rate):
        self.engine.setProperty('rate', int(rate))
        
    def update_voice(self, voice_name):
        # Find the index of the selected voice
        for i, voice in enumerate(self.voices):
            if voice.name == voice_name:
                self.current_voice = i
                self.engine.setProperty('voice', voice.id)
                break
                
    def start_speech(self):
        if self.speech_thread and self.speech_thread.is_alive():
            self.stop_speech()
            
        def speak_text():
            while self.speech_enabled and self.running and self.index < len(self.text):
                if self.reading_mode == "word":
                    word = self.text[self.index]
                    self.engine.say(word)
                    self.engine.runAndWait()
                    time.sleep(self.speed)
                elif self.reading_mode == "sentence":
                    # Collect words until we find end of sentence
                    sentence = []
                    temp_index = self.index
                    while temp_index < len(self.text):
                        word = self.text[temp_index]
                        sentence.append(word)
                        temp_index += 1
                        if word.endswith(('.', '!', '?')):
                            break
                    sentence_text = ' '.join(sentence)
                    self.engine.say(sentence_text)
                    self.engine.runAndWait()
                    time.sleep(self.speed * len(sentence))
                else:  # paragraph
                    # Collect words until we find double newline or reach limit
                    paragraph = []
                    temp_index = self.index
                    word_count = 0
                    while temp_index < len(self.text) and word_count < 50:
                        word = self.text[temp_index]
                        paragraph.append(word)
                        temp_index += 1
                        word_count += 1
                        if word.endswith('\n\n'):
                            break
                    paragraph_text = ' '.join(paragraph)
                    self.engine.say(paragraph_text)
                    self.engine.runAndWait()
                    time.sleep(self.speed * len(paragraph))
                
        self.speech_thread = threading.Thread(target=speak_text, daemon=True)
        self.speech_thread.start()
        
    def stop_speech(self):
        if self.speech_thread and self.speech_thread.is_alive():
            self.speech_thread.join(timeout=0.1)
        self.engine.stop()

if __name__ == "__main__":
    root = ctk.CTk()
    app = SpeedReader(root)
    root.mainloop() 