# ==========================================================
# engine/cleaner.py
# ==========================================================

import os
import shutil
from pathlib import Path
from engine.scanner import Scanner


class Cleaner:
    def __init__(self):
        self.scanner = Scanner()
        self.cleaned = {}
        self.errors = []

    def safe_delete_file(self, path: Path) -> int:
        """Supprime un fichier et retourne sa taille. Retourne 0 en cas d'erreur."""
        try:
            if path.is_file():
                size = path.stat().st_size
                path.unlink()
                return size
        except (PermissionError, FileNotFoundError, OSError) as e:
            self.errors.append(f"{path} → {e}")
        return 0

    def safe_delete_folder_content(self, path: Path) -> int:
        """
        Supprime le contenu d'un dossier (pas le dossier lui-même).
        Retourne la taille totale supprimée.
        """
        if not path.exists() or not path.is_dir():
            return 0

        total = 0

        try:
            for root, dirs, files in os.walk(path, topdown=False):
                for name in files:
                    file_path = Path(root) / name
                    total += self.safe_delete_file(file_path)

                for name in dirs:
                    dir_path = Path(root) / name
                    try:
                        dir_path.rmdir()  # ne supprime que s'il est vide
                    except OSError:
                        pass
        except (PermissionError, OSError) as e:
            self.errors.append(f"{path} → {e}")

        return total

    def clean_temp_files(self) -> int:
        paths = [
            os.getenv("TEMP"),
            os.getenv("TMP"),
            r"C:\Windows\Temp",
        ]
        total = 0
        for p in paths:
            if p:
                total += self.safe_delete_folder_content(Path(p))
        return total

    def clean_windows_logs(self) -> int:
        paths = [
            r"C:\Windows\Logs",
            r"C:\Windows\System32\LogFiles",
        ]
        total = 0
        for p in paths:
            total += self.safe_delete_folder_content(Path(p))
        return total

    def clean_thumbnails(self) -> int:
        path = Path(os.getenv("LOCALAPPDATA", "")) / "Microsoft" / "Windows" / "Explorer"
        total = 0
        if path.exists():
            for f in path.glob("thumbcache_*.db"):
                total += self.safe_delete_file(f)
        return total

    def clean_update_leftovers(self) -> int:
        paths = [
            r"C:\Windows\SoftwareDistribution\Download",
        ]
        total = 0
        for p in paths:
            total += self.safe_delete_folder_content(Path(p))
        return total

    def clean_crash_dumps(self) -> int:
        paths = [
            Path(os.getenv("LOCALAPPDATA", "")) / "CrashDumps",
            r"C:\Windows\Minidump",
        ]
        total = 0
        for p in paths:
            p = Path(p)
            if p.is_file():
                total += self.safe_delete_file(p)
            else:
                total += self.safe_delete_folder_content(p)

        # MEMORY.DMP
        memory_dump = Path(r"C:\Windows\MEMORY.DMP")
        total += self.safe_delete_file(memory_dump)
        return total

    def clean_recycle_bin(self) -> int:
        total = 0
        try:
            # Méthode plus propre via PowerShell serait mieux,
            # mais on reste simple et local pour l'instant
            for drive in "CDEFGHIJKLMNOPQRSTUVWXYZ":
                recycle = Path(f"{drive}:/$Recycle.Bin")
                if recycle.exists():
                    total += self.safe_delete_folder_content(recycle)
        except Exception as e:
            self.errors.append(f"Recycle Bin → {e}")
        return total

    def clean_prefetch(self) -> int:
        return self.safe_delete_folder_content(Path(r"C:\Windows\Prefetch"))

    def clean_browser_cache(self) -> int:
        total = 0
        local = Path(os.getenv("LOCALAPPDATA", ""))
        roaming = Path(os.getenv("APPDATA", ""))

        browser_paths = [
            # Chrome
            local / "Google" / "Chrome" / "User Data" / "Default" / "Cache",
            local / "Google" / "Chrome" / "User Data" / "Default" / "Code Cache",
            # Edge
            local / "Microsoft" / "Edge" / "User Data" / "Default" / "Cache",
            local / "Microsoft" / "Edge" / "User Data" / "Default" / "Code Cache",
            # Firefox
            roaming / "Mozilla" / "Firefox" / "Profiles",
            # Opera
            local / "Opera Software" / "Opera Stable" / "Cache",
            # Brave
            local / "BraveSoftware" / "Brave-Browser" / "User Data" / "Default" / "Cache",
        ]

        for p in browser_paths:
            if not p.exists():
                continue

            if "Profiles" in str(p):  # Firefox
                for profile in p.iterdir():
                    cache2 = profile / "cache2"
                    if cache2.exists():
                        total += self.safe_delete_folder_content(cache2)
            else:
                total += self.safe_delete_folder_content(p)

        return total

    def clean_browser_history(self) -> int:
        # Pour l'instant on ne touche pas (plus sensible)
        return 0

    def clean_download_history(self) -> int:
        return 0

    def clean_cookies(self) -> int:
        # Désactivé par défaut et sensible → on ne touche pas encore
        return 0

    def clean_all(self, selected: dict) -> dict:
        """
        selected = { "temp_files": True, ... }
        Retourne un dict avec la taille réellement nettoyée.
        """
        mapping = {
            "temp_files": self.clean_temp_files,
            "windows_logs": self.clean_windows_logs,
            "thumbnails": self.clean_thumbnails,
            "update_leftovers": self.clean_update_leftovers,
            "crash_dumps": self.clean_crash_dumps,
            "recycle_bin": self.clean_recycle_bin,
            "prefetch": self.clean_prefetch,
            "browser_cache": self.clean_browser_cache,
            "browser_history": self.clean_browser_history,
            "download_history": self.clean_download_history,
            "cookies": self.clean_cookies,
        }

        results = {}
        self.errors = []

        for key, enabled in selected.items():
            if enabled and key in mapping:
                results[key] = mapping[key]()
            else:
                results[key] = 0

        self.cleaned = results
        return results