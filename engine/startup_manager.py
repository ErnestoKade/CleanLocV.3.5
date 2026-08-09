# ==========================================================
# engine/startup_manager.py
# ==========================================================

import os
import winreg
from pathlib import Path


class StartupManager:
    def __init__(self):
        self.entries = []

    def _read_registry_run(self, hive, path):
        """Lit les entrées de démarrage dans le registre."""
        results = []
        try:
            key = winreg.OpenKey(hive, path, 0, winreg.KEY_READ)
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    results.append({
                        "name": name,
                        "command": value,
                        "location": "Registry",
                        "hive": "HKCU" if hive == winreg.HKEY_CURRENT_USER else "HKLM",
                        "key_path": path,
                        "enabled": True,  # dans Run = activé
                        "source": "registry"
                    })
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except FileNotFoundError:
            pass
        except Exception:
            pass
        return results

    def _read_startup_folder(self, folder: Path, scope: str):
        """Lit les raccourcis du dossier Startup."""
        results = []
        if not folder.exists():
            return results

        for item in folder.iterdir():
            if item.suffix.lower() in [".lnk", ".exe", ".bat", ".cmd"]:
                results.append({
                    "name": item.stem,
                    "command": str(item),
                    "location": "Startup Folder",
                    "hive": scope,
                    "key_path": str(folder),
                    "enabled": True,
                    "source": "folder"
                })
        return results

    def get_all_entries(self) -> list:
        """Récupère toutes les entrées de démarrage."""
        entries = []

        # === Registry - Current User ===
        entries += self._read_registry_run(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run"
        )

        # === Registry - Local Machine ===
        entries += self._read_registry_run(
            winreg.HKEY_LOCAL_MACHINE,
            r"Software\Microsoft\Windows\CurrentVersion\Run"
        )

        # === Startup Folder - Current User ===
        startup_user = Path(os.getenv("APPDATA", "")) / r"Microsoft\Windows\Start Menu\Programs\Startup"
        entries += self._read_startup_folder(startup_user, "User")

        # === Startup Folder - All Users ===
        startup_common = Path(os.getenv("PROGRAMDATA", "")) / r"Microsoft\Windows\Start Menu\Programs\Startup"
        entries += self._read_startup_folder(startup_common, "Common")

        self.entries = entries
        return entries

    def disable_registry_entry(self, entry: dict) -> bool:
        """Désactive une entrée registre en la déplaçant vers RunDisabled (ou suppression simple)."""
        try:
            hive = winreg.HKEY_CURRENT_USER if entry["hive"] == "HKCU" else winreg.HKEY_LOCAL_MACHINE
            access = winreg.KEY_ALL_ACCESS

            # On ouvre la clé Run
            key = winreg.OpenKey(hive, entry["key_path"], 0, access)

            # On lit la valeur
            value, regtype = winreg.QueryValueEx(key, entry["name"])

            # On la supprime de Run
            winreg.DeleteValue(key, entry["name"])
            winreg.CloseKey(key)

            return True
        except Exception as e:
            print(f"Error disabling {entry['name']}: {e}")
            return False

    def enable_registry_entry(self, entry: dict, command: str) -> bool:
        """Réactive une entrée (à améliorer plus tard)."""
        try:
            hive = winreg.HKEY_CURRENT_USER if entry["hive"] == "HKCU" else winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(hive, entry["key_path"], 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, entry["name"], 0, winreg.REG_SZ, command)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Error enabling {entry['name']}: {e}")
            return False