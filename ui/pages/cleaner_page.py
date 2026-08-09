# ==========================================================
# ui/pages/cleaner_page.py
# ==========================================================

import tkinter as tk
from tkinter import messagebox
from engine.scanner import Scanner
from engine.cleaner import Cleaner


class CleanerPage(tk.Frame):
    def __init__(self, parent, colors: dict):
        super().__init__(parent, bg=colors["bg_content"])

        self.colors = colors
        self.selected_categories = {}
        self.scanner = Scanner()
        self.cleaner = Cleaner()
        self.last_results = {}

        self.create_widgets()

    def create_widgets(self):
        tk.Label(
            self,
            text="Select what you want to clean",
            font=("Segoe UI", 13),
            bg=self.colors["bg_content"],
            fg="#FFFFFF"
        ).pack(anchor="w", pady=(5, 12))

        card = tk.Frame(self, bg="#1E2633", padx=20, pady=15)
        card.pack(fill="both", expand=True)

        self.create_section_title(card, "System")

        self.add_category(card, "temp_files", "Temporary files", True)
        self.add_category(card, "windows_logs", "Windows logs", True)
        self.add_category(card, "thumbnails", "Thumbnail cache", True)
        self.add_category(card, "update_leftovers", "Windows Update leftovers", True)
        self.add_category(card, "crash_dumps", "Crash dumps", True)
        self.add_category(card, "recycle_bin", "Recycle Bin", True)
        self.add_category(card, "prefetch", "Windows Prefetch", False)

        tk.Frame(card, bg="#2A3344", height=1).pack(fill="x", pady=14)

        self.create_section_title(card, "Browsers")

        self.add_category(card, "browser_cache", "Browser cache", True)
        self.add_category(card, "browser_history", "Browsing history", True)
        self.add_category(card, "download_history", "Download history", True)
        self.add_category(card, "cookies", "Cookies", False)

        buttons_zone = tk.Frame(self, bg=self.colors["bg_content"])
        buttons_zone.pack(fill="x", pady=(18, 8))

        self.total_label = tk.Label(
            buttons_zone,
            text="Selected: 0 B",
            font=("Segoe UI", 12, "bold"),
            bg=self.colors["bg_content"],
            fg="#FFFFFF"
        )
        self.total_label.pack(pady=(0, 12))

        btn_frame = tk.Frame(buttons_zone, bg=self.colors["bg_content"])
        btn_frame.pack()

        self.analyze_btn = tk.Button(
            btn_frame,
            text="Analyze",
            font=("Segoe UI", 12, "bold"),
            bg="#3F444B",
            fg="#FFFFFF",
            disabledforeground="#FFFFFF",
            activebackground="#3B82F6",
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            highlightthickness=0,
            width=14,
            height=2,
            cursor="hand2",
            command=self.on_analyze
        )
        self.analyze_btn.pack(side="left", padx=8)

        self.clean_btn = tk.Button(
            btn_frame,
            text="Clean",
            font=("Segoe UI", 12, "bold"),
            bg="#3B82F6",
            fg="#FFFFFF",
            disabledforeground="#FFFFFF",
            activebackground="#2563EB",
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            highlightthickness=0,
            width=14,
            height=2,
            cursor="hand2",
            state="disabled",
            command=self.on_clean
        )
        self.clean_btn.pack(side="left", padx=8)

    def create_section_title(self, parent, text):
        tk.Label(
            parent,
            text=text,
            font=("Segoe UI", 12, "bold"),
            bg="#1E2633",
            fg="#FFFFFF"
        ).pack(anchor="w", pady=(0, 8))

    def add_category(self, parent, key, label, default=True):
        var = tk.BooleanVar(value=default)
        self.selected_categories[key] = var

        frame = tk.Frame(parent, bg="#1E2633")
        frame.pack(fill="x", pady=3)

        cb = tk.Checkbutton(
            frame,
            text=label,
            variable=var,
            font=("Segoe UI", 11),
            bg="#1E2633",
            fg="#FFFFFF",
            activebackground="#1E2633",
            activeforeground="#FFFFFF",
            selectcolor="#2A3344",
            highlightthickness=0,
            bd=0,
            cursor="hand2"
        )
        cb.pack(side="left")

        size_label = tk.Label(
            frame,
            text="—",
            font=("Segoe UI", 10),
            bg="#1E2633",
            fg="#C7CCD4"
        )
        size_label.pack(side="right")

        var.size_label = size_label

    def on_analyze(self):
        self.analyze_btn.config(state="disabled", text="Scanning...")
        self.clean_btn.config(state="disabled")
        self.update_idletasks()

        selected = {
            key: var.get()
            for key, var in self.selected_categories.items()
        }

        results = self.scanner.scan_all(selected)
        self.last_results = results

        total = 0
        for key, var in self.selected_categories.items():
            size = results.get(key, 0)
            total += size
            var.size_label.config(text=self.scanner.format_size(size))

        self.total_label.config(text=f"Selected: {self.scanner.format_size(total)}")

        self.analyze_btn.config(state="normal", text="Analyze")
        if total > 0:
            self.clean_btn.config(state="normal")

    def on_clean(self):
        selected = {
            key: var.get()
            for key, var in self.selected_categories.items()
        }

        total = sum(self.last_results.get(key, 0) for key, enabled in selected.items() if enabled)

        if total == 0:
            messagebox.showinfo("CleanLoc", "Nothing to clean.")
            return

        confirm = messagebox.askyesno(
            "Confirm Cleaning",
            f"You are about to permanently delete:\n\n{self.scanner.format_size(total)}\n\nThis action cannot be undone.\n\nContinue?"
        )

        if not confirm:
            return

        self.clean_btn.config(state="disabled", text="Cleaning...")
        self.analyze_btn.config(state="disabled")
        self.update_idletasks()

        results = self.cleaner.clean_all(selected)
        cleaned_total = sum(results.values())

        for key, var in self.selected_categories.items():
            var.size_label.config(text="—")

        self.total_label.config(text="Selected: 0 B")
        self.last_results = {}

        self.clean_btn.config(state="disabled", text="Clean")
        self.analyze_btn.config(state="normal")

        if cleaned_total > 0:
            messagebox.showinfo(
            "Cleaning Complete",
            f"Successfully cleaned: {self.scanner.format_size(cleaned_total)}"
        )
        else:
            messagebox.showinfo(
            "Nothing deleted",
            "No files could be deleted.\n\n"
            "They are probably still in use by Windows or another program."
        )