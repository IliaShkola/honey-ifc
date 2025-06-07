# HoneyIFC
<p align="center">
   <img src="https://github.com/user-attachments/assets/a8c230f6-0759-4179-b6f1-a434ffe030ed" width="20%" alt="bee">
</p>
<p align="center">
   <img src="https://github.com/user-attachments/assets/0fc74502-8f17-43ce-a52a-680bb302e02d" width="30%" alt="scr1">
   <img src="https://github.com/user-attachments/assets/ac91a397-d278-44d6-bd96-c3911dc37a89" width="30%" alt="scr2">
   <img src="https://github.com/user-attachments/assets/37e152f6-6e28-4a04-8dd4-48675b2a4283" width="30%" alt="scr3">
</p>

**HoneyIFC** is a lightweight desktop application designed for analyzing and exporting data from IFC (Industry Foundation Classes) files. It offers a faster, easier, and more visually appealing way to explore and interact with the data hidden inside complex IFC models.

Whether you're an engineer, architect, or just a curious mind, Honey makes working with IFC files less painful — and a lot more fun.

# Why Honey?

Dealing with IFC files can be tedious — Honey aims to change that. It’s a fun side project built to bring a little joy (and a lot of usability) to the otherwise dry world of BIM data.

# Features

- Intuitive and fast browsing of IFC data (supports IFC 2x3 and IFC 4)  
- Export functionality for structured data (currently to XLSX format)  
- Stylish and user-friendly interface  
- Designed to make BIM work feel less like work

# Tech Stack

- Python  
- Textual (TUI Framework)  
- IfcOpenShell

# Getting Started

## Prerequisites
- Python 3.11 or higher
- Recommended: Create and activate a virtual environment

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/IliaShkola/honey-ifc.git
   ```
2. Move to the `honey-ifc` directory:
   ```sh
   cd honey-ifc
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
   
4. Create an executable:
   If you want to create an executable for the application, you can use PyInstaller:
   ```sh
   pyinstaller app.spec
   ```
   This will generate a standalone executable in the `dist/` directory.

## Configuration File
When launched, Honey automatically creates a configuration folder to store user preferences and settings. The location of this folder depends on your operating system:

- Windows:
`%LOCALAPPDATA%\Honey\config.ini`
(typically something like `C:\Users\YourName\AppData\Local\honeycomb\config.ini`)

- Linux/macOS:
`~/.local/share/honeycomb/config.ini`

This is done to persist your interface theme.
No personal or sensitive data is collected or transmitted.

# 🐝 How to Run HoneyIFC Properly

## Basic Usage

To export data from IFC files, **you must launch HoneyIFC from the same folder where your `.ifc` files are located**.  
HoneyIFC scans the current working directory and lists all available IFC models automatically.

This works well when launching `HoneyIFC.exe` manually from a terminal or file explorer, but constantly navigating to the folder and running the executable can be inconvenient.

---

## Make It Easier: Add HoneyIFC to the Right-Click Menu

To simplify launching HoneyIFC, you can add it to the **Windows right-click context menu**.  
This allows you to right-click **inside any folder** and open it directly in HoneyIFC — no need to move or copy `.ifc` files elsewhere.

---

## Manual Setup (No Scripts Required)

Follow these steps to add **“Open with HoneyIFC”** to your Windows right-click menu using the Registry Editor:

### Step-by-Step Guide

1. **Press** `Win + R`, type `regedit`, and press **Enter**  
   → This opens the **Registry Editor**

2. Navigate to the following path:
`HKEY_CLASSES_ROOT\Directory\Background\shell`


3. **Right-click** on `shell` → **New → Key**  
Name the new key:
`HoneyIFC`


4. Select the `HoneyIFC` key  
On the right side, **double-click** the default `"(Default)"` value  
Set the value data to:
`Open with HoneyIFC`


5. Now **right-click `HoneyIFC` → New → Key**  
Name it:
`command`


6. Select the `command` key  
On the right side, **double-click** the default `"(Default)"` value  
Set the value to (adjust the path as needed):
`"C:\Tools\HoneyIFC\HoneyIFC.exe" "%V"`


`"%V"` tells Windows to launch HoneyIFC **inside the folder you clicked**, passing it as the working directory.

---
## ⚙️ Alternative: Use Ready-Made Scripts

If you don't want to edit the registry manually, you can use the pre-made scripts included in the release.

### ▶️ To install context menu entry:
1. Make sure `HoneyIFC.exe` is located in a fixed folder (e.g., `C:\Tools\HoneyIFC\`)
2. Open the folder containing:
- `add_to_context.reg`
- `install_context.bat`
3. **Double-click `install_context.bat`**
- This script automatically adds HoneyIFC to the Windows context menu

### 🧼 To remove the context menu entry:
1. Run `remove_context.bat`
- This script removes HoneyIFC from the right-click menu
- Alternatively, delete the following registry key manually:
  ```
  HKEY_CLASSES_ROOT\Directory\Background\shell\HoneyIFC
  ```

---

## ✅ Done!

Now you can:
- Open any folder containing `.ifc` files
- Right-click on **empty space inside the folder**
- Choose **“Open with HoneyIFC”**

HoneyIFC will launch and show all `.ifc` models from that folder — ready to explore and export.

---

## 🔁 Updating HoneyIFC

When a new version of HoneyIFC is released, **you don’t need to reinstall or reconfigure anything**.

If you already added HoneyIFC to the context menu:

1. Download the new `HoneyIFC.exe` from the release
2. Replace the old executable at: `C:\Tools\HoneyIFC\HoneyIFC.exe`
or whichever path you used in the registry
3. That’s it! The right-click integration will keep working as expected

✅ No need to run the `.bat` or `.reg` scripts again — just overwrite the old version


## 📝 Notes

- If you ever move `HoneyIFC.exe` to another location, you’ll need to update the registry path manually
- For per-user setup (no admin rights required), you can use:
`HKEY_CURRENT_USER\Software\Classes\Directory\Background\shell`
instead of `HKEY_CLASSES_ROOT`


# Project Structure
- `app.py` - Main application entry point
- `config_manager.py` - Configuration and settings management
- `honeyThemes.py` - Theme definitions
- `*_mod*.py` - Modules for handling IFC data
- `static/` - Static assets (icons, etc.)
- `styles/` - Theme and style files

# Contributing
Contributions are welcome! Please open issues or submit pull requests for improvements and bug fixes.

# License
This project is licensed under the GPL-3.0.

# Trademark

"Honey IFC" and the bee logo are trademarks of Ilia Shkola.  
You may not use them in forks or derivative works without permission.

# Author

Made with ❤️ by [Ilia Shkola]

