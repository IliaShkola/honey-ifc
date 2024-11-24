# Honeycomb (Ifc Data Extractor)
<p align="center">
  <img src="https://github.com/user-attachments/assets/90647bf4-276a-4488-8e53-3d561a665910" width="30%" alt="Description of your image">
</p>

This Python Textual app allows users to export data in XLS from IFC model from selected IfcCategory and Property set (Pset). Work in CLI and looks cool.

<p align="center">
  <img src="https://github.com/user-attachments/assets/01f2ebc0-4aa5-48dc-8595-bada0a97c97a" width="45%" />
  <img src="https://github.com/user-attachments/assets/6b9189d0-a679-4350-bda8-659ae898dd1f" width="45%" />
</p>

Introduction
---
Introduction of this app

Features
---
* Extracting selected IfcCategory Pset infro in xlsx
* Supporting IFC2x3, IFC4.0
* Nvim navigation style

Build With
---
* Python
* Textual
* IfcOpenShell
* XLWT

Installation and Setup
---
Follow these steps to install the necessary libraries and set up the tool:

1. Upgrade pip
```
python -m pip install --upgrade pip
```
2. Install the required libraries:

```
pip install -r .\requirements.txt
```

3. Create an executable file using PyInstaller:
```
pyinstaller.exe .\app.spec
```
To use the executable from any folder in the terminal, add the folder containing the executable to your PATH in the Windows settings.

Usage
---


License
---
[Specify the license here, e.g., MIT, GPL, etc.]
