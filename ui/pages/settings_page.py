# ==========================================================
# ui/pages/settings_page.py
# ==========================================================

import tkinter as tk
from tkinter import messagebox
import os
from pathlib import Path


class SettingsPage(tk.Frame):
    def __init__(self, parent, colors: dict):
        super().__init__(parent, bg=colors["bg_content"])

        self.colors = colors
        self.create_widgets()

    def create_widgets(self):
        # ===== TITLE =====
        tk.Label(
            self,
            text="Settings",
            font=("Segoe UI", 13),
            bg=self.colors["bg_content"],
            fg=self.colors["fg_secondary"]
        ).pack(anchor="w", pady=(5, 15))

        # ===== CARD =====
        card = tk.Frame(
            self,
            bg=self.colors["bg_card"],
            padx=20,
            pady=20
        )
        card.pack(fill="both", expand=True)

        # --- About ---
        tk.Label(
            card,
            text="About CleanLoc",
            font=("Segoe UI", 12, "bold"),
            bg=self.colors["bg_card"],
            fg=self.colors["fg_title"]
        ).pack(anchor="w", pady=(0, 10))

        about_text = (
            "CleanLoc v3.5\n"
            "100% local • Offline • Open source\n\n"
            "No ads • No telemetry • No internet required\n\n"
            "A simple and transparent Windows cleaner."
        )

        tk.Label(
            card,
            text=about_text,
            font=("Segoe UI", 11),
            bg=self.colors["bg_card"],
            fg=self.colors["fg_secondary"],
            justify="left"
        ).pack(anchor="w", pady=(0, 20))

        # Separator
        tk.Frame(
            card,
            bg=self.colors["bg_card_hover"],
            height=1
        ).pack(fill="x", pady=10)

        # --- Safety info ---
        tk.Label(
            card,
            text="Safety principles",
            font=("Segoe UI", 12, "bold"),
            bg=self.colors["bg_card"],
            fg=self.colors["fg_title"]
        ).pack(anchor="w", pady=(10, 10))

        safety_text = (
            "• No automatic deletion\n"
            "• Always ask confirmation before cleaning\n"
            "• No registry cleaning by default\n"
            "• Cookies and Prefetch disabled by default\n"
            "• No background services\n"
            "• No telemetry\n\n"
            "• Enjoy ! ErnestoKade"
        )

        tk.Label(
            card,
            text=safety_text,
            font=("Segoe UI", 11),
            bg=self.colors["bg_card"],
            fg=self.colors["fg_secondary"],
            justify="left"
        ).pack(anchor="w", pady=(0, 20))

        # Separator
        tk.Frame(
            card,
            bg=self.colors["bg_card_hover"],
            height=1
        ).pack(fill="x", pady=10)

        # --- Buttons ---
        btn_frame = tk.Frame(card, bg=self.colors["bg_card"])
        btn_frame.pack(anchor="w", pady=(15, 0))

        tk.Button(
            btn_frame,
            text="Open Project Folder",
            font=("Segoe UI", 10),
            bg=self.colors["bg_button"],
            fg=self.colors["fg_text"],
            activebackground=self.colors["bg_button_active"],
            activeforeground="white",
            relief="flat",
            bd=0,
            width=18,
            cursor="hand2",
            command=self.open_project_folder
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            btn_frame,
            text="About",
            font=("Segoe UI", 10),
            bg=self.colors["bg_button"],
            fg=self.colors["fg_text"],
            activebackground=self.colors["bg_button_active"],
            activeforeground="white",
            relief="flat",
            bd=0,
            width=12,
            cursor="hand2",
            command=self.show_about
        ).pack(side="left")

    def open_project_folder(self):
        try:
            path = Path(__file__).resolve().parent.parent.parent
            os.startfile(path)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_about(self):
        messagebox.showinfo(
            "About CleanLoc",
            "CleanLoc v3.5\n\n"
            "100% local Windows cleaner\n"
            "Open source • No telemetry • Offline\n\n"
            "Built to be simple and trustworthy."
        )