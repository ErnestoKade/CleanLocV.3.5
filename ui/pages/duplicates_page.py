# ==========================================================
# ui/pages/duplicates_page.py
# ==========================================================

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
from engine.duplicates import DuplicatesFinder


class DuplicatesPage(tk.Frame):
    def __init__(self, parent, colors: dict):
        super().__init__(parent, bg=colors["bg_content"])

        self.colors = colors
        self.finder = DuplicatesFinder()
        self.results = []
        self.selected_group = None
        self.scanning = False
        self.blink_state = False
        self.file_vars = []

        self.create_widgets()

    def create_widgets(self):
        top = tk.Frame(self, bg=self.colors["bg_content"])
        top.pack(fill="x", pady=(5, 12))

        tk.Label(
            top,
            text="Find duplicate files by content (SHA-256)",
            font=("Segoe UI", 13),
            bg=self.colors["bg_content"],
            fg="#FFFFFF"
        ).pack(side="left")

        options = tk.Frame(self, bg=self.colors["bg_content"])
        options.pack(fill="x", pady=(0, 8))

        self.scan_btn = tk.Button(
            options,
            text="Scan Folder",
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
        self.scan_btn.pack(side="left")

        self.scan_status = tk.Label(
            options,
            text="",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["bg_content"],
            fg="#3B82F6"
        )
        self.scan_status.pack(side="left", padx=15)

        progress_frame = tk.Frame(self, bg=self.colors["bg_content"])
        progress_frame.pack(fill="x", pady=(0, 8))

        self.progress = ttk.Progressbar(
            progress_frame,
            mode="determinate",
            length=280,
            value=0
        )
        self.progress.pack(side="left")

        self.progress_label = tk.Label(
            progress_frame,
            text="Ready",
            font=("Segoe UI", 9),
            bg=self.colors["bg_content"],
            fg="#C7CCD4"
        )
        self.progress_label.pack(side="left", padx=10)

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

        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

        bottom = tk.Frame(self, bg=self.colors["bg_content"])
        bottom.pack(fill="x", pady=(12, 5))

        self.info_label = tk.Label(
            bottom,
            text="Select a folder to scan for duplicates",
            font=("Segoe UI", 10),
            bg=self.colors["bg_content"],
            fg="#FFFFFF"
        )
        self.info_label.pack(side="left")

        btn_frame = tk.Frame(bottom, bg=self.colors["bg_content"])
        btn_frame.pack(side="right")

        self.open_btn = tk.Button(
            btn_frame,
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
        self.open_btn.pack(side="left", padx=(0, 8))

        self.delete_btn = tk.Button(
            btn_frame,
            text="Delete selected",
            font=("Segoe UI", 10),
            bg="#3B82F6",
            fg="#FFFFFF",
            disabledforeground="#FFFFFF",
            activebackground="#2563EB",
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            highlightthickness=0,
            width=14,
            cursor="hand2",
            command=self.delete_selected
        )
        self.delete_btn.pack(side="left")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def choose_folder(self):
        if self.scanning:
            return

        folder = filedialog.askdirectory(title="Select folder to scan for duplicates")
        if not folder:
            return

        confirm = messagebox.askyesno(
            "Confirm Scan",
            f"Scan this folder for duplicates?\n\n{folder}\n\n"
            "This can take some time on large folders."
        )
        if not confirm:
            return

        self.start_scan(folder)

    def start_scan(self, path: str):
        self.scanning = True
        self.selected_group = None
        self.file_vars = []
        self.scan_btn.config(state="disabled", text="Scanning...")
        self.info_label.config(text="Scanning in progress... please wait")
        self.scan_status.config(text="● SCANNING")
        self.progress_label.config(text="Scanning...")
        self.progress.config(mode="indeterminate")
        self.progress.start(12)
        self._blink()

        for widget in self.list_frame.winfo_children():
            widget.destroy()

        def worker():
            results = self.finder.scan(path)
            self.after(0, lambda: self._scan_done(results))

        threading.Thread(target=worker, daemon=True).start()

    def _blink(self):
        if not self.scanning:
            self.scan_status.config(text="")
            return
        self.blink_state = not self.blink_state
        if self.blink_state:
            self.scan_status.config(text="● SCANNING", fg="#3B82F6")
        else:
            self.scan_status.config(text="○ SCANNING", fg="#FFFFFF")
        self.after(500, self._blink)

    def _scan_done(self, results):
        self.scanning = False
        self.scan_btn.config(state="normal", text="Scan Folder")
        self.scan_status.config(text="")
        self.progress.stop()
        self.progress.config(mode="determinate", value=100)
        self.results = results
        self.file_vars = []

        if not results:
            self.progress_label.config(text="100% • 0 result(s)")
            self.info_label.config(text="No duplicates found")
            tk.Label(
                self.list_frame,
                text="No duplicate files found in this folder.",
                font=("Segoe UI", 12),
                bg="#1E2633",
                fg="#FFFFFF"
            ).pack(pady=40)
            return

        total_groups = len(results)
        total_wasted = sum((g["count"] - 1) * g["size"] for g in results)
        self.progress_label.config(text=f"100% • {total_groups} group(s) found")
        self.info_label.config(
            text=f"{total_groups} group(s) • Potential waste: {self.finder.format_size(total_wasted)}"
        )

        for group in results:
            self.create_group(group)

    def create_group(self, group):
        frame = tk.Frame(self.list_frame, bg="#1E2633")
        frame.pack(fill="x", pady=3, padx=8)

        header = tk.Frame(frame, bg="#1E2633", cursor="hand2")
        header.pack(fill="x")

        title = f"{group['count']} files • {group['size_str']} each"
        title_label = tk.Label(
            header,
            text=title,
            font=("Segoe UI", 11, "bold"),
            bg="#1E2633",
            fg="#FFFFFF",
            anchor="w",
            cursor="hand2"
        )
        title_label.pack(fill="x", padx=12, pady=(10, 6))

        body = tk.Frame(frame, bg="#1E2633")
        body.pack(fill="x")

        first = group["files"][0]
        keep_label = tk.Label(
            body,
            text=f"  [KEEP] {first['path']}",
            font=("Segoe UI", 9),
            bg="#1E2633",
            fg="#86EFAC",
            anchor="w"
        )
        keep_label.pack(fill="x", padx=12, pady=(0, 2))

        for f in group["files"][1:]:
            row = tk.Frame(body, bg="#1E2633")
            row.pack(fill="x", padx=12, pady=1)

            var = tk.BooleanVar(value=False)
            self.file_vars.append((var, f["path"], f["size_str"]))

            cb = tk.Checkbutton(
                row,
                variable=var,
                onvalue=True,
                offvalue=False,
                bg="#1E2633",
                activebackground="#1E2633",
                selectcolor="#111827",
                fg="#FFFFFF",
                activeforeground="#FFFFFF",
                highlightthickness=0,
                bd=0,
                cursor="hand2"
            )
            cb.pack(side="left")

            path_label = tk.Label(
                row,
                text=f["path"],
                font=("Segoe UI", 9),
                bg="#1E2633",
                fg="#C7CCD4",
                anchor="w"
            )
            path_label.pack(side="left", fill="x")

            def toggle(e, v=var):
                v.set(not v.get())

            path_label.bind("<Button-1>", toggle)

        tk.Frame(body, bg="#1E2633", height=8).pack()

        def on_click(e, g=group):
            self.select_group(g)

        header.bind("<Button-1>", on_click)
        title_label.bind("<Button-1>", on_click)

        group["frame"] = frame
        group["header"] = header
        group["body"] = body

    def _set_group_colors(self, group, bg):
        try:
            group["frame"].config(bg=bg)
            group["header"].config(bg=bg)
            group["body"].config(bg=bg)
            for child in group["header"].winfo_children():
                child.config(bg=bg)
        except Exception:
            pass

    def select_group(self, group):
        if self.selected_group is group:
            return
        if self.selected_group:
            self._set_group_colors(self.selected_group, "#1E2633")
        self._set_group_colors(group, "#2A3F5F")
        self.selected_group = group
        self.info_label.config(
            text=f"Selected: {group['count']} files • {group['size_str']}"
        )

    def open_location(self):
        if not self.selected_group:
            messagebox.showwarning("CleanLoc", "Select a group first.")
            return
        try:
            folder = self.selected_group["files"][0]["folder"]
            os.startfile(folder)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open folder:\n{e}")

    def delete_selected(self):
        to_delete = [(path, size) for var, path, size in self.file_vars if var.get()]

        if not to_delete:
            messagebox.showwarning(
                "CleanLoc",
                "Check at least one duplicate file to delete."
            )
            return

        lines = "\n".join(f"- {path}" for path, _ in to_delete[:10])
        more = ""
        if len(to_delete) > 10:
            more = f"\n... and {len(to_delete) - 10} more"

        confirm = messagebox.askyesno(
            "Delete duplicates",
            f"Delete {len(to_delete)} selected duplicate file(s)?\n\n"
            f"{lines}{more}\n\n"
            "Kept files (marked [KEEP]) will not be deleted."
        )
        if not confirm:
            return

        deleted = 0
        errors = []
        for path, _ in to_delete:
            try:
                os.remove(path)
                deleted += 1
            except Exception as e:
                errors.append(f"{path} → {e}")

        msg = f"Deleted: {deleted} file(s)."
        if errors:
            msg += f"\n\nErrors: {len(errors)}"
        messagebox.showinfo("Done", msg)
        self.info_label.config(text="Files deleted. Run a new scan to refresh.")