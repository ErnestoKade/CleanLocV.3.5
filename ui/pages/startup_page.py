# ==========================================================
# ui/pages/startup_page.py
# ==========================================================

import tkinter as tk
from tkinter import messagebox
from engine.startup_manager import StartupManager


class StartupPage(tk.Frame):
    def __init__(self, parent, colors: dict):
        super().__init__(parent, bg=colors["bg_content"])

        self.colors = colors
        self.manager = StartupManager()
        self.entries = []
        self.selected_entry = None

        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        header = tk.Frame(self, bg=self.colors["bg_content"])
        header.pack(fill="x", pady=(5, 12))

        tk.Label(
            header,
            text="Programs that start with Windows",
            font=("Segoe UI", 13),
            bg=self.colors["bg_content"],
            fg="#FFFFFF"
        ).pack(side="left")

        self.refresh_btn = tk.Button(
            header,
            text="Refresh",
            font=("Segoe UI", 10),
            bg="#3F444B",
            fg="#FFFFFF",
            disabledforeground="#FFFFFF",
            activebackground="#3B82F6",
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            highlightthickness=0,
            width=10,
            cursor="hand2",
            command=self.refresh_list
        )
        self.refresh_btn.pack(side="right")

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
        bottom.pack(fill="x", pady=(15, 5))

        self.info_label = tk.Label(
            bottom,
            text="Select an item to enable or disable it",
            font=("Segoe UI", 10),
            bg=self.colors["bg_content"],
            fg="#FFFFFF"
        )
        self.info_label.pack(side="left")

        btn_frame = tk.Frame(bottom, bg=self.colors["bg_content"])
        btn_frame.pack(side="right")

        self.disable_btn = tk.Button(
            btn_frame,
            text="Disable",
            font=("Segoe UI", 11),
            bg="#3F444B",
            fg="#FFFFFF",
            disabledforeground="#FFFFFF",
            activebackground="#3B82F6",
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            highlightthickness=0,
            width=12,
            height=2,
            cursor="hand2",
            state="disabled",
            command=self.disable_selected
        )
        self.disable_btn.pack(side="left", padx=(0, 8))

        self.enable_btn = tk.Button(
            btn_frame,
            text="Enable",
            font=("Segoe UI", 11),
            bg="#3B82F6",
            fg="#FFFFFF",
            disabledforeground="#FFFFFF",
            activebackground="#2563EB",
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            highlightthickness=0,
            width=12,
            height=2,
            cursor="hand2",
            state="disabled",
            command=self.enable_selected
        )
        self.enable_btn.pack(side="left")

    def refresh_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        self.entries = self.manager.get_all_entries()
        self.selected_entry = None
        self.disable_btn.config(state="disabled")
        self.enable_btn.config(state="disabled")
        self.info_label.config(text=f"{len(self.entries)} startup item(s) found")

        if not self.entries:
            tk.Label(
                self.list_frame,
                text="No startup programs found.",
                font=("Segoe UI", 12),
                bg="#1E2633",
                fg="#FFFFFF"
            ).pack(pady=40)
            return

        for entry in self.entries:
            self.create_entry_row(entry)

    def create_entry_row(self, entry):
        frame = tk.Frame(self.list_frame, bg="#1E2633", cursor="hand2")
        frame.pack(fill="x", pady=2, padx=8)

        name_label = tk.Label(
            frame,
            text=entry["name"],
            font=("Segoe UI", 11, "bold"),
            bg="#1E2633",
            fg="#FFFFFF",
            anchor="w"
        )
        name_label.pack(fill="x", padx=12, pady=(8, 0))

        cmd = entry.get("command", "")
        cmd_label = tk.Label(
            frame,
            text=cmd[:80] + ("..." if len(cmd) > 80 else ""),
            font=("Segoe UI", 9),
            bg="#1E2633",
            fg="#C7CCD4",
            anchor="w"
        )
        cmd_label.pack(fill="x", padx=12, pady=(2, 8))

        def on_click(e, ent=entry, fr=frame):
            self.select_entry(ent, fr)

        frame.bind("<Button-1>", on_click)
        name_label.bind("<Button-1>", on_click)
        cmd_label.bind("<Button-1>", on_click)

        entry["frame"] = frame

    def select_entry(self, entry, frame):
        if self.selected_entry and "frame" in self.selected_entry:
            try:
                self.selected_entry["frame"].config(bg="#1E2633")
                for child in self.selected_entry["frame"].winfo_children():
                    child.config(bg="#1E2633")
            except Exception:
                pass

        frame.config(bg="#2A3344")
        for child in frame.winfo_children():
            child.config(bg="#2A3344")

        self.selected_entry = entry
        self.info_label.config(text=f"Selected: {entry['name']}")

        if entry.get("source") == "registry":
            self.disable_btn.config(state="normal")
            self.enable_btn.config(state="disabled")
        else:
            self.disable_btn.config(state="disabled")
            self.enable_btn.config(state="disabled")

    def disable_selected(self):
        if not self.selected_entry:
            return

        entry = self.selected_entry
        confirm = messagebox.askyesno(
            "Disable Startup Item",
            f"Disable \"{entry['name']}\" from starting with Windows?\n\nYou can re-enable it later."
        )
        if not confirm:
            return

        success = self.manager.disable_registry_entry(entry)
        if success:
            messagebox.showinfo("Success", f"\"{entry['name']}\" has been disabled.")
            self.refresh_list()
        else:
            messagebox.showerror(
                "Error",
                "Failed to disable this item.\nTry running CleanLoc as Administrator."
            )

    def enable_selected(self):
        messagebox.showinfo(
            "Info",
            "Enable function will be improved in the next version."
        )