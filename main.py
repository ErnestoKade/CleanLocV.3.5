# ==========================================================
# main.py
# ==========================================================

import tkinter as tk
from ui.main_window import MainWindow

def main():
    root = tk.Tk()
    root.title("CleanLocV3.5 By ErnestoKade")
    root.geometry("1100x750")
    root.minsize(900, 600)
    root.configure(bg="#0f0f0f")
    root.iconbitmap("assets/icon.ico")

    # Centrer la fenêtre
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")

    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()