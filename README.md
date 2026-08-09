# CleanLoc

**© ErnestoKade - 2026**

**CleanLoc** is a 100% local, open-source Windows cleaner.

No ads. No telemetry. No internet required.  
One goal: show honest numbers and let you clean safely.

---

## Features



### 1. Quick Clean

Analyze and remove common junk files.

#### System

- Temporary files
- Windows logs
- Thumbnail cache
- Windows Update leftovers
- Crash dumps
- Recycle Bin
- Windows Prefetch *(disabled by default)*

#### Browsers

- Browser cache
- Browsing history *(size not estimated)*
- Download history *(size not estimated)*
- Cookies *(disabled by default)*

#### Safety rules

- Always Analyze before Clean
- Always ask confirmation
- No automatic deletion
- Locked files are not counted in totals
- Recycle Bin size uses the Windows Shell API (`SHQueryRecycleBin`)
- If nothing could be deleted → honest message, not a fake “success”

---

### 2. Startup Manager

List programs that start with Windows.

- Read entries from:
  - Registry `HKCU/HKLM ...\Run`
  - User Startup folder
  - Common Startup folder
- Disable selected registry startup entries
- Enable support is limited in current version

---

### 3. Large Files Finder

Find files that take the most disk space.

- Scan drive C: or any folder
- Minimum size filter: 50 MB / 100 MB / 200 MB / 500 MB / 1 GB
- Sort by size (largest first)
- Open file location in Explorer
- Ignores sensitive system folders by default

---

### 4. Duplicate Files Finder

Find duplicate files by **content**, not only by name.

#### Detection method

1. Group files by size
2. Hash candidates with **SHA-256**
3. Same size + same hash = duplicate group

#### Features

- Scan confirmation before start
- Background scan (UI does not freeze)
- Blinking SCANNING status
- Progress bar + result count
- `[KEEP]` marks the first file of each group
- Checkboxes on the other duplicates
- Multi-select delete across multiple groups
- Open folder location
- Mouse wheel scrolling

---

### 5. Settings

- About CleanLoc
- Safety principles
- Open project folder

---

## Technical notes

### Stack

- Python 3
- Tkinter UI
- Standard library only for core features

Windows APIs used when needed:

- `SHQueryRecycleBinW` for real Recycle Bin size
- `SHEmptyRecycleBinW` for emptying Recycle Bin
- `winreg` for startup entries

---

## Honesty policy

CleanLoc prefers under-reporting over fake numbers.

- Accessible files only are counted when possible
- Locked files are treated as non-deletable
- Categories without reliable size estimation return `0 B`
- “Successfully cleaned: 0 B” is never shown as a success

---

## Project structure

```text
CleanLoc/
├── main.py
├── engine/
│   ├── scanner.py
│   ├── cleaner.py
│   ├── startup_manager.py
│   ├── large_files.py
│   └── duplicates.py
├── ui/
│   ├── main_window.py
│   └── pages/
│       ├── cleaner_page.py
│       ├── startup_page.py
│       ├── large_files_page.py
│       ├── duplicates_page.py
│       └── settings_page.py
├── assets/
└── README.md
```

---

## Run from source

```bash
pip install -r requirements.txt
python main.py
```

---

## Requirements

- Windows 10 / 11
- Python 3.10+

---

Principles100% offline
No cloud
No account
No telemetry
No registry cleaning by default
No background service
Preview before delete
Transparent behavior

GoalCleanLoc is not the most aggressive cleaner.It aims to be:predictable
readable
local
honest about what it can and cannot delete

No upselling. No tracking. No fake results.

Enjoy !

## License

This project is licensed under the **GNU GPL-3.0** license.





