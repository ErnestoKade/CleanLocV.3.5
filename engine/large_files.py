# ==========================================================
# engine/large_files.py
# ==========================================================

import os
from pathlib import Path


class LargeFilesFinder:
    def __init__(self):
        self.results = []

    def format_size(self, size: int) -> str:
        if size < 1024:
            return f"{size} B"
        elif size < 1024 ** 2:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 ** 3:
            return f"{size / (1024 ** 2):.1f} MB"
        else:
            return f"{size / (1024 ** 3):.2f} GB"

    def scan(self, root_path: str, min_size_mb: int = 100, max_results: int = 200) -> list:
        """
        Scan un dossier et retourne les plus gros fichiers.
        min_size_mb : taille minimale en Mo
        max_results : nombre max de résultats
        """
        min_size = min_size_mb * 1024 * 1024
        results = []

        root = Path(root_path)
        if not root.exists():
            return []

        # Dossiers à ignorer (sécurité + vitesse)
        ignore_dirs = {
            "$Recycle.Bin", "System Volume Information", "Windows",
            "Program Files", "Program Files (x86)", "ProgramData",
            "AppData", "Recovery", "PerfLogs"
        }

        try:
            for dirpath, dirnames, filenames in os.walk(root):
                # Filtrer les dossiers ignorés
                dirnames[:] = [d for d in dirnames if d not in ignore_dirs]

                for filename in filenames:
                    try:
                        filepath = Path(dirpath) / filename
                        size = filepath.stat().st_size

                        if size >= min_size:
                            results.append({
                                "path": str(filepath),
                                "name": filename,
                                "size": size,
                                "size_str": self.format_size(size),
                                "folder": str(filepath.parent)
                            })
                    except (PermissionError, FileNotFoundError, OSError):
                        continue

        except (PermissionError, OSError):
            pass

        # Trier du plus gros au plus petit
        results.sort(key=lambda x: x["size"], reverse=True)

        # Limiter le nombre de résultats
        self.results = results[:max_results]
        return self.results