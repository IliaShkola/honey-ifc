# HoneyIfc
<p align="center">
   <img src="https://github.com/user-attachments/assets/a8c230f6-0759-4179-b6f1-a434ffe030ed" width="20%" alt="bee">
</p>
<p align="center">
   <img src="https://github.com/user-attachments/assets/0fc74502-8f17-43ce-a52a-680bb302e02d" width="30%" alt="scr1">
   <img src="https://github.com/user-attachments/assets/ac91a397-d278-44d6-bd96-c3911dc37a89" width="30%" alt="scr2">
   <img src="https://github.com/user-attachments/assets/37e152f6-6e28-4a04-8dd4-48675b2a4283" width="30%" alt="scr3">
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
   cd honey-ifc
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

