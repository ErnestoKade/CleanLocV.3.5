# ui/main_window.py

import tkinter as tk
from ui.pages.cleaner_page import CleanerPage
from ui.pages.startup_page import StartupPage
from ui.pages.large_files_page import LargeFilesPage
from ui.pages.duplicates_page import DuplicatesPage
from ui.pages.settings_page import SettingsPage

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg="#243447")

        # ==================== COULEURS ====================
       
        self.bg_main = "#111315" 
        self.bg_sidebar = "#24272B" 
        self.bg_content = "#34383D" 
        self.bg_card = "#1E2633" 
        self.bg_card_hover = "#2A3344" 
        self.bg_button = "#3F444B" 
        self.bg_button_hover = "#4A5058" 
        self.bg_button_active = "#3B82F6" 
        self.bg_button_danger = "#B45309" 
        self.bg_button_success = "#15803D" 
        self.fg_text = "#F5F5F5" 
        self.fg_title = "#FFFFFF" 
        self.fg_secondary = "#C7CCD4" 
        self.bg_status = "#0F172A"

        self.active_button = None

        self.create_layout()

    # ======================================================
    # LAYOUT
    # ======================================================
    def create_layout(self):

        # ==================== SIDEBAR ====================
        self.sidebar = tk.Frame(
            self.root,
            bg=self.bg_sidebar,
            width=210
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo / titre
        self.title_label = tk.Label(
            self.sidebar,
            text="CleanLoc V3.5",
            font=("Segoe UI", 15, "bold"),
            bg=self.bg_sidebar,
            fg=self.fg_title
        )
        self.title_label.pack(pady=(28, 2))

        # Sous-titre
        self.subtitle_label = tk.Label(
            self.sidebar,
            text="Local • Offline • Open source",
            font=("Segoe UI", 9),
            bg=self.bg_sidebar,
            fg=self.fg_secondary
        )
        self.subtitle_label.pack(pady=(0, 22))

        # Boutons
        self.btn_cleaner = self.create_sidebar_button(
            "🧹  Quick Clean", self.show_cleaner)

        self.btn_startup = self.create_sidebar_button(
            "🚀  Startup", self.show_startup)

        self.btn_large = self.create_sidebar_button(
            "💾  Large Files", self.show_large_files)

        self.btn_duplicates = self.create_sidebar_button(
            "🧬  Duplicates", self.show_duplicates)

        # Espace flexible
        tk.Frame(self.sidebar, bg=self.bg_sidebar).pack(expand=True, fill="both")

        self.btn_settings = self.create_sidebar_button(
            "⚙️  Settings", self.show_settings)

        # ==================== ZONE PRINCIPALE ====================
        self.content_frame = tk.Frame(
            self.root,
            bg=self.bg_content
        )
        self.content_frame.pack(side="right", fill="both", expand=True)

        # Header
        self.header = tk.Frame(
            self.content_frame,
            bg=self.bg_content,
            height=64
        )
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        self.header_title = tk.Label(
            self.header,
            text="Quick Clean",
            font=("Segoe UI", 17, "bold"),
            bg=self.bg_content,
            fg=self.fg_title
        )
        self.header_title.pack(side="left", padx=26, pady=16)

        # Contenu
        self.page_container = tk.Frame(
            self.content_frame,
            bg=self.bg_content
        )
        self.page_container.pack(fill="both", expand=True, padx=24, pady=(8, 14))

        # Status bar
        self.status_bar = tk.Label(
            self.content_frame,
            text="Offline • No telemetry • No internet required",
            font=("Segoe UI", 9),
            bg="#0F172A",
            fg=self.fg_secondary,
            anchor="w",
            padx=16,
            pady=8
        )
        self.status_bar.pack(side="bottom", fill="x")

        # Page par défaut
        self.show_cleaner()

    # ======================================================
    # BOUTON SIDEBAR
    # ======================================================
    def create_sidebar_button(self, text, command):

        btn = tk.Button(
            self.sidebar,
            text=text,
            font=("Segoe UI", 11),
            bg=self.bg_button,
            fg=self.fg_text,
            activebackground=self.bg_button_active,
            activeforeground="white",
            relief="flat",
            bd=0,
            highlightthickness=0,
            width=18,
            height=2,
            cursor="hand2",
            anchor="w",
            padx=14,
            command=lambda b=text: self.on_sidebar_click(b, command)
        )

        btn.pack(pady=4, padx=14, fill="x")

        btn.bind("<Enter>", lambda e, x=btn: self.on_hover(x))
        btn.bind("<Leave>", lambda e, x=btn: self.on_leave(x))

        return btn

    def on_hover(self, btn):
        if btn != self.active_button:
            btn.configure(bg=self.bg_button_hover)

    def on_leave(self, btn):
        if btn != self.active_button:
            btn.configure(bg=self.bg_button)

    def set_active(self, btn):
        if self.active_button:
            self.active_button.configure(bg=self.bg_button)

        btn.configure(bg=self.bg_button_active)
        self.active_button = btn

    def on_sidebar_click(self, text, command):

        mapping = {
            "🧹  Quick Clean": self.btn_cleaner,
            "🚀  Startup": self.btn_startup,
            "💾  Large Files": self.btn_large,
            "🧬  Duplicates": self.btn_duplicates,
            "⚙️  Settings": self.btn_settings,
        }

        self.set_active(mapping[text])
        command()

    # ======================================================
    # OUTILS
    # ======================================================
    def clear_page(self):
        for widget in self.page_container.winfo_children():
            widget.destroy()

    def create_placeholder(self, title, subtitle):
        self.clear_page()

        card = tk.Frame(
            self.page_container,
            bg="#1E2633",
            bd=0
        )
        card.pack(expand=True, fill="both")

        tk.Label(
            card,
            text=title,
            font=("Segoe UI", 22, "bold"),
            bg="#1E2633",
            fg=self.fg_title
        ).pack(pady=(70, 10))

        tk.Label(
            card,
            text=subtitle,
            font=("Segoe UI", 11),
            bg="#1E2633",
            fg=self.fg_secondary
        ).pack()

    # ======================================================
    # PAGES
    # ======================================================
    def show_cleaner(self):
        self.clear_page()
        self.header_title.config(text="Quick Clean")
        self.status_bar.config(text="Ready • Quick Clean")

        colors = {
            "bg_content": self.bg_content,
            "bg_card": self.bg_card,
            "bg_card_hover": self.bg_card_hover,
            "bg_button": self.bg_button,
            "bg_button_hover": self.bg_button_hover,
            "bg_button_active": self.bg_button_active,
            "bg_button_danger": self.bg_button_danger,
            "bg_button_success": self.bg_button_success,
            "fg_text": self.fg_text,
            "fg_title": self.fg_title,
            "fg_secondary": self.fg_secondary,
            "bg_status": self.bg_status,
        }

        page = CleanerPage(self.page_container, colors)
        page.pack(fill="both", expand=True)
        
    def show_startup(self):
        self.clear_page()
        self.header_title.config(text="Startup")
        self.status_bar.config(text="Ready • Startup")

        colors = {
            "bg_content": self.bg_content,
            "bg_card": self.bg_card,
            "bg_card_hover": self.bg_card_hover,
            "bg_button": self.bg_button,
            "bg_button_hover": self.bg_button_hover,
            "bg_button_active": self.bg_button_active,
            "bg_button_danger": self.bg_button_danger,
            "bg_button_success": self.bg_button_success,
            "fg_text": self.fg_text,
            "fg_title": self.fg_title,
            "fg_secondary": self.fg_secondary,
            "bg_status": self.bg_status,
        }
        page = StartupPage(self.page_container, colors)
        page.pack(fill="both", expand=True)

    def show_large_files(self):
        self.clear_page()
        self.header_title.config(text="Large Files")
        self.status_bar.config(text="Ready • Large Files")

        colors = {
            "bg_content": self.bg_content,
            "bg_card": self.bg_card,
            "bg_card_hover": self.bg_card_hover,
            "bg_button": self.bg_button,
            "bg_button_hover": self.bg_button_hover,
            "bg_button_active": self.bg_button_active,
            "bg_button_danger": self.bg_button_danger,
            "bg_button_success": self.bg_button_success,
            "fg_text": self.fg_text,
            "fg_title": self.fg_title,
            "fg_secondary": self.fg_secondary,
            "bg_status": self.bg_status,
        
        }

        page = LargeFilesPage(self.page_container, colors)
        page.pack(fill="both", expand=True)

    def show_duplicates(self):
        self.clear_page()
        self.header_title.config(text="Duplicates")
        self.status_bar.config(text="Ready • Duplicates")

        colors = {
            "bg_content": self.bg_content,
            "bg_card": self.bg_card,
            "bg_card_hover": self.bg_card_hover,
            "bg_button": self.bg_button,
            "bg_button_hover": self.bg_button_hover,
            "bg_button_active": self.bg_button_active,
            "bg_button_danger": self.bg_button_danger,
            "bg_button_success": self.bg_button_success,
            "fg_text": self.fg_text,
            "fg_title": self.fg_title,
            "fg_secondary": self.fg_secondary,
            "bg_status": self.bg_status,
        }

        page = DuplicatesPage(self.page_container, colors)
        page.pack(fill="both", expand=True)

    def show_settings(self):
        self.clear_page()
        self.header_title.config(text="Settings")
        self.status_bar.config(text="Ready • Settings")

        colors = {
            "bg_content": self.bg_content,
            "bg_card": self.bg_card,
            "bg_card_hover": self.bg_card_hover,
            "bg_button": self.bg_button,
            "bg_button_hover": self.bg_button_hover,
            "bg_button_active": self.bg_button_active,
            "bg_button_danger": self.bg_button_danger,
            "bg_button_success": self.bg_button_success,
            "fg_text": self.fg_text,
            "fg_title": self.fg_title,
            "fg_secondary": self.fg_secondary,
            "bg_status": self.bg_status,
        }

        page = SettingsPage(self.page_container, colors)
        page.pack(fill="both", expand=True)


