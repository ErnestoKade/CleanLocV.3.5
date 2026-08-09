# ==========================================================
# engine/scanner.py
# ==========================================================

import os
import ctypes
from ctypes import wintypes
from pathlib import Path


class Scanner:
    def __init__(self):
        self.results = {}

    def format_size(self, size: int) -> str:
        if size < 1024:
            return f"{size} B"
        elif size < 1024 ** 2:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 ** 3:
            return f"{size / (1024 ** 2):.1f} MB"
        else:
            return f"{size / (1024 ** 3):.2f} GB"

    def is_accessible(self, path: Path) -> bool:
        """True seulement si le fichier est lisible / potentiellement supprimable."""
        try:
            if not path.is_file():
                return False
            # Tentative d'ouverture exclusive légère
            with open(path, "rb"):
                pass
            return True
        except (PermissionError, FileNotFoundError, OSError):
            return False

    def get_deletable_size(self, path: str | Path) -> int:
        """
        Compte UNIQUEMENT les fichiers accessibles (pas les verrouillés).
        Comme les détenus, pas les gardiens.
        """
        path = Path(path)
        if not path.exists():
            return 0

        total = 0
        try:
            if path.is_file():
                return path.stat().st_size if self.is_accessible(path) else 0

            for root, dirs, files in os.walk(path):
                for name in files:
                    fp = Path(root) / name
                    try:
                        if self.is_accessible(fp):
                            total += fp.stat().st_size
                    except (PermissionError, FileNotFoundError, OSError):
                        continue
        except (PermissionError, OSError):
            return 0

        return total

    def scan_temp_files(self) -> int:
        paths = [
            os.getenv("TEMP"),
            os.getenv("TMP"),
            r"C:\Windows\Temp",
        ]
        total = 0
        for p in paths:
            if p:
                total += self.get_deletable_size(p)
        return total

    def scan_windows_logs(self) -> int:
        paths = [
            r"C:\Windows\Logs",
            r"C:\Windows\System32\LogFiles",
        ]
        total = 0
        for p in paths:
            total += self.get_deletable_size(p)
        return total

    def scan_thumbnails(self) -> int:
        path = Path(os.getenv("LOCALAPPDATA", "")) / "Microsoft" / "Windows" / "Explorer"
        total = 0
        if path.exists():
            for f in path.glob("thumbcache_*.db"):
                total += self.get_deletable_size(f)
        return total

    def scan_update_leftovers(self) -> int:
        paths = [
            r"C:\Windows\SoftwareDistribution\Download",
        ]
        total = 0
        for p in paths:
            total += self.get_deletable_size(p)
        return total

    def scan_crash_dumps(self) -> int:
        paths = [
            Path(os.getenv("LOCALAPPDATA", "")) / "CrashDumps",
            r"C:\Windows\Minidump",
            r"C:\Windows\MEMORY.DMP",
        ]
        total = 0
        for p in paths:
            total += self.get_deletable_size(p)
        return total

    def scan_recycle_bin(self) -> int:
        """Taille réelle de la corbeille via API Windows (pas de faux total)."""
        try:
            class SHQUERYRBINFO(ctypes.Structure):
                _fields_ = [
                    ("cbSize", wintypes.DWORD),
                    ("i64Size", ctypes.c_int64),
                    ("i64NumItems", ctypes.c_int64),
                ]

            info = SHQUERYRBINFO()
            info.cbSize = ctypes.sizeof(SHQUERYRBINFO)
            result = ctypes.windll.shell32.SHQueryRecycleBinW(None, ctypes.byref(info))
            if result == 0:
                return max(0, int(info.i64Size))
        except Exception:
            pass
        return 0

    def scan_prefetch(self) -> int:
        return self.get_deletable_size(r"C:\Windows\Prefetch")

    def scan_browser_cache(self) -> int:
        total = 0
        local = Path(os.getenv("LOCALAPPDATA", ""))
        roaming = Path(os.getenv("APPDATA", ""))

        browser_paths = [
            local / "Google" / "Chrome" / "User Data" / "Default" / "Cache",
            local / "Google" / "Chrome" / "User Data" / "Default" / "Code Cache",
            local / "Microsoft" / "Edge" / "User Data" / "Default" / "Cache",
            local / "Microsoft" / "Edge" / "User Data" / "Default" / "Code Cache",
            local / "Opera Software" / "Opera Stable" / "Cache",
            local / "BraveSoftware" / "Brave-Browser" / "User Data" / "Default" / "Cache",
        ]

        for p in browser_paths:
            total += self.get_deletable_size(p)

        # Firefox
        profiles = roaming / "Mozilla" / "Firefox" / "Profiles"
        if profiles.exists():
            try:
                for profile in profiles.iterdir():
                    total += self.get_deletable_size(profile / "cache2")
            except (PermissionError, OSError):
                pass

        return total

    def scan_browser_history(self) -> int:
        # Trop sensible / peu fiable en taille → on n'affiche pas de faux chiffre
        return 0

    def scan_download_history(self) -> int:
        return 0

    def scan_cookies(self) -> int:
        return 0

    def scan_all(self, selected: dict) -> dict:
        mapping = {
            "temp_files": self.scan_temp_files,
            "windows_logs": self.scan_windows_logs,
            "thumbnails": self.scan_thumbnails,
            "update_leftovers": self.scan_update_leftovers,
            "crash_dumps": self.scan_crash_dumps,
            "recycle_bin": self.scan_recycle_bin,
            "prefetch": self.scan_prefetch,
            "browser_cache": self.scan_browser_cache,
            "browser_history": self.scan_browser_history,
            "download_history": self.scan_download_history,
            "cookies": self.scan_cookies,
        }

        results = {}
        for key, enabled in selected.items():
            if enabled and key in mapping:
                try:
                    results[key] = mapping[key]()
                except Exception:
                    results[key] = 0
            else:
                results[key] = 0

        self.results = results
        return results