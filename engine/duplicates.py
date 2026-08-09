# ==========================================================
# engine/duplicates.py
# ==========================================================

import os
import hashlib
from pathlib import Path
from collections import defaultdict


class DuplicatesFinder:
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

    def file_hash(self, path: Path, block_size: int = 65536) -> str | None:
        """Calcule le SHA-256 d'un fichier."""
        try:
            h = hashlib.sha256()
            with open(path, "rb") as f:
                while True:
                    data = f.read(block_size)
                    if not data:
                        break
                    h.update(data)
            return h.hexdigest()
        except (PermissionError, FileNotFoundError, OSError):
            return None

    def scan(self, root_path: str, min_size_kb: int = 100, max_files: int = 5000) -> list:
        """
        Trouve les doublons.
        Étape 1 : grouper par taille
        Étape 2 : hasher uniquement les fichiers de même taille
        """
        root = Path(root_path)
        if not root.exists():
            return []

        ignore_dirs = {
            "$Recycle.Bin", "System Volume Information", "Windows",
            "Program Files", "Program Files (x86)", "ProgramData",
            "AppData", "Recovery", "PerfLogs", "node_modules", ".git"
        }

        # Étape 1 : grouper par taille
        size_map = defaultdict(list)
        file_count = 0
        min_size = min_size_kb * 1024

        try:
            for dirpath, dirnames, filenames in os.walk(root):
                dirnames[:] = [d for d in dirnames if d not in ignore_dirs]

                for filename in filenames:
                    if file_count >= max_files:
                        break
                    try:
                        filepath = Path(dirpath) / filename
                        size = filepath.stat().st_size
                        if size >= min_size:
                            size_map[size].append(filepath)
                            file_count += 1
                    except (PermissionError, FileNotFoundError, OSError):
                        continue
                if file_count >= max_files:
                    break
        except (PermissionError, OSError):
            pass

        # Étape 2 : hasher les groupes de même taille
        hash_map = defaultdict(list)

        for size, files in size_map.items():
            if len(files) < 2:
                continue
            for f in files:
                h = self.file_hash(f)
                if h:
                    hash_map[h].append({
                        "path": str(f),
                        "name": f.name,
                        "size": size,
                        "size_str": self.format_size(size),
                        "folder": str(f.parent)
                    })

        # Garder uniquement les vrais doublons
        duplicates = []
        for h, group in hash_map.items():
            if len(group) > 1:
                duplicates.append({
                    "hash": h,
                    "size": group[0]["size"],
                    "size_str": group[0]["size_str"],
                    "count": len(group),
                    "files": group
                })

        # Trier par taille (plus gros d'abord)
        duplicates.sort(key=lambda x: x["size"], reverse=True)
        self.results = duplicates
        return duplicates