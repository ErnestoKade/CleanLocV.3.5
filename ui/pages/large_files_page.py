# ==========================================================
# ui/pages/large_files_page.py
# ==========================================================

import tkinter as tk
from tkinter import filedialog, messagebox
import os
from engine.large_files import LargeFilesFinder


class LargeFilesPage(tk.Frame):
    def __init__(self, parent, colors: dict):
        super().__init__(parent, bg=colors["bg_content"])

        self.colors = colors
        self.finder = LargeFilesFinder()
        self.results = []
        self.selected_item = None

        self.create_widgets()

    def create_widgets(self):
        top = tk.Frame(self, bg=self.colors["bg_content"])
        top.pack(fill="x", pady=(5, 12))

        tk.Label(
            top,
            text="Find large files on your drives",
            font=("Segoe UI", 13),
            bg=self.colors["bg_content"],
            fg="#FFFFFF"
        ).pack(side="left")

        options = tk.Frame(self, bg=self.colors["bg_content"])
        options.pack(fill="x", pady=(0, 10))

        tk.Label(
            options,
            text="Min size:",
            font=("Segoe UI", 10),
            bg=self.colors["bg_content"],
            fg="#FFFFFF"
        ).pack(side="left")

        self.size_var = tk.StringVar(value="100 MB")
        sizes = ["50 MB", "100 MB", "200 MB", "500 MB", "1 GB"]
        self.size_menu = tk.OptionMenu(options, self.size_var, *sizes)
        self.size_menu.config(
            bg="#3F444B",
            fg="#FFFFFF",
            activebackground="#3B82F6",
            activeforeground="#FFFFFF",
            relief="flat",
            highlightthickness=0
        )
        self.size_menu.pack(side="left", padx=(8, 15))

        self.scan_btn = tk.Button(
            options,
            text="Scan Drive C:",
            font=("Segoe UI", 10),
            bg="#3F444B",
            fg="#FFFFFF",
            disabledforeground="#FFFFFF",
            activebackground="#3B82F6",
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            highlightthickness=0,
            width=14,
            cursor="hand2",
            command=lambda: self.start_scan("C:\\")
        )
        self.scan_btn.pack(side="left", padx=(0, 8))

        self.choose_btn = tk.Button(
            options,
            text="Choose Folder",
            font=("Segoe UI", 10),
            bg="#3F444B",
            fg="#FFFFFF",
            disabledforeground="#FFFFFF",
            activebackground="#3B82F6",
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            highlightthickness=0,
            width=14,
            cursor="hand2",
            command=self.choose_folder
        )
        self.choose_btn.pack(side="left")

        card = tk.Frame(self, bg="#1E2633")
        card.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(card, bg="#1E2633", highlightthickness=0)
        scrollbar = tk.Scrollbar(card, orient="vertical", command=self.canvas.yview)
        self.list_frame = tk.Frame(self.canvas, bg="#1E2633")

        self.list_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        bottom = tk.Frame(self, bg=self.colors["bg_content"])
        bottom.pack(fill="x", pady=(12, 5))

        self.info_label = tk.Label(
            bottom,
            text="Select a folder or drive to scan",
            font=("Segoe UI", 10),
            bg=self.colors["bg_content"],
            fg="#FFFFFF"
        )
        self.info_label.pack(side="left")

        self.open_btn = tk.Button(
            bottom,
            text="Open Location",
            font=("Segoe UI", 10),
            bg="#3F444B",
            fg="#FFFFFF",
            disabledforeground="#FFFFFF",
            activebackground="#3B82F6",
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            highlightthickness=0,
            width=14,
            cursor="hand2",
            command=self.open_location
        )
        self.open_btn.pack(side="right")

    def get_min_size_mb(self) -> int:
        mapping = {
            "50 MB": 50,
            "100 MB": 100,
            "200 MB": 200,
            "500 MB": 500,
            "1 GB": 1024
        }
        return mapping.get(self.size_var.get(), 100)

    def choose_folder(self):
        folder = filedialog.askdirectory(title="Select folder to scan")
        if folder:
            self.start_scan(folder)

    def start_scan(self, path: str):
        self.scan_btn.config(state="disabled")
        self.choose_btn.config(state="disabled")
        self.info_label.config(text="Scanning... please wait")
        self.selected_item = None
        self.update_idletasks()

        for widget in self.list_frame.winfo_children():
            widget.destroy()

        min_size = self.get_min_size_mb()
        self.results = self.finder.scan(path, min_size_mb=min_size)

        self.scan_btn.config(state="normal")
        self.choose_btn.config(state="normal")

        if not self.results:
            self.info_label.config(text="No large files found")
            tk.Label(
                self.list_frame,
                text="No files found with the selected minimum size.",
                font=("Segoe UI", 12),
                bg="#1E2633",
                fg="#FFFFFF"
            ).pack(pady=40)
            return

        self.info_label.config(text=f"{len(self.results)} large file(s) found")
        for item in self.results:
            self.create_row(item)

    def create_row(self, item):
        frame = tk.Frame(self.list_frame, bg="#1E2633", cursor="hand2")
        frame.pack(fill="x", pady=2, padx=8)

        name_label = tk.Label(
            frame,
            text=item["name"],
            font=("Segoe UI", 11, "bold"),
            bg="#1E2633",
            fg="#FFFFFF",
            anchor="w"
        )
        name_label.pack(fill="x", padx=12, pady=(8, 0))

        info_text = f"{item['size_str']}  •  {item['folder']}"
        info_label = tk.Label(
            frame,
            text=info_text[:90] + ("..." if len(info_text) > 90 else ""),
            font=("Segoe UI", 9),
            bg="#1E2633",
            fg="#C7CCD4",
            anchor="w"
        )
        info_label.pack(fill="x", padx=12, pady=(2, 8))

        def on_click(e, it=item, fr=frame):
            self.select_item(it, fr)

        frame.bind("<Button-1>", on_click)
        name_label.bind("<Button-1>", on_click)
        info_label.bind("<Button-1>", on_click)
        item["frame"] = frame

    def select_item(self, item, frame):
        if self.selected_item and "frame" in self.selected_item:
            try:
                self.selected_item["frame"].config(bg="#1E2633")
                for child in self.selected_item["frame"].winfo_children():
                    child.config(bg="#1E2633")
            except Exception:
                pass

        frame.config(bg="#2A3344")
        for child in frame.winfo_children():
            child.config(bg="#2A3344")

        self.selected_item = item
        self.info_label.config(text=f"Selected: {item['name']} ({item['size_str']})")

    def open_location(self):
        if not self.selected_item:
            messagebox.showwarning("CleanLoc", "Select a file first.")
            return

        folder = self.selected_item.get("folder")
        if not folder:
            messagebox.showerror("Error", "No folder path found.")
            return

        try:
            os.startfile(folder)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open folder:\n{folder}\n\n{e}")