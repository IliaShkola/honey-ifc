# Honey
<p align="center">
   <img src="https://github.com/user-attachments/assets/105e78b9-38cc-472b-ae8e-6b788fb362e2" width="20%" alt="Bee">
</p>
<p align="center">
   <img src="https://github.com/user-attachments/assets/0dc9337c-c8e8-4bf6-b087-770aeb936b36" width="30%" alt="scr1">
   <img src="https://github.com/user-attachments/assets/1b0cf5f9-44d4-4e9d-b0e8-05a5a06eaaed" width="30%" alt="scr2">
   <img src="https://github.com/user-attachments/assets/24ae73a8-5c82-43c5-bd81-c26274ab4caf" width="30%" alt="scr3">
</p>

**Honey** is a lightweight desktop application designed for analyzing and exporting data from IFC (Industry Foundation Classes) files. It offers a faster, easier, and more visually appealing way to explore and interact with the data hidden inside complex IFC models.

Whether you're an engineer, architect, or just a curious mind, Honey makes working with IFC files less painful — and a lot more fun.

## Why Honey?

Dealing with IFC files can be tedious — Honey aims to change that. It’s a fun side project built to bring a little joy (and a lot of usability) to the otherwise dry world of BIM data.

## Features

- Intuitive and fast browsing of IFC data (supports IFC 2x3 and IFC 4)  
- Export functionality for structured data (currently to XLSX format)  
- Stylish and user-friendly interface  
- Designed to make BIM work feel less like work

## Tech Stack

- Python  
- Textual (TUI Framework)  
- IfcOpenShell

## Getting Started

### Prerequisites
- Python 3.11 or higher
- Recommended: Create and activate a virtual environment

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/IliaShkola/honey-ifc.git
   cd honey
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
   
3. Create an executable:
   If you want to create an executable for the application, you can use PyInstaller:
   ```sh
   pyinstaller app.spec
   ```
   This will generate a standalone executable in the `dist/` directory.

### Configuration File
When launched, Honey automatically creates a configuration folder to store user preferences and settings. The location of this folder depends on your operating system:

- Windows:
`%LOCALAPPDATA%\Honey\config.ini`
(typically something like `C:\Users\YourName\AppData\Local\honeycomb\config.ini`)

- Linux/macOS:
`~/.local/share/honeycomb/config.ini`

This is done to persist your interface theme.
No personal or sensitive data is collected or transmitted.

## Running the Application
Run the Honey executable from the folder with IFC files to analyze.

### Running the application from the folder context menu
You can run the application directly from the folder containing your IFC files. This allows you to easily access and analyze your IFC data without needing to specify paths.
To do this, you need to add the folder containing your IFC files to the system PATH. This can be done by modifying the environment variables on your operating system.


## Project Structure
- `app.py` - Main application entry point
- `config_manager.py` - Configuration and settings management
- `honeyThemes.py` - Theme definitions
- `*_mod*.py` - Modules for handling IFC data
- `static/` - Static assets (icons, etc.)
- `styles/` - Theme and style files

## Contributing
Contributions are welcome! Please open issues or submit pull requests for improvements and bug fixes.

## License
This project is licensed under the GPL-3.0.

## Author

Made with ❤️ by [Ilia Shkola]

