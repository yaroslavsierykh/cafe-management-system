# App description 
CafeApp Official is a comprehensive system designed to automate the operations of a café. The application provides full management of menu items, ingredients, supplies, employees, and customer orders. It supports both offline and online ordering and generates detailed shift and sales reports.

Key features:

Menu & dishes: creation, editing, categories, ingredients, availability tracking.

Ingredients & inventory: automatic deduction, stock tracking, links to dishes.

Supplies & suppliers: delivery records, automatic inventory updates.

Orders: online/offline processing, full order history, dish popularity analytics.

Staff & shifts: employee roles, opening/closing shifts, operation tracking.

Reports: financial, inventory, shift summaries, dish popularity, sales analytics.

The application ensures fast, transparent, and efficient café operations — from the kitchen to the administrator.

# CafeApp_offical — How to run

Important: To log in to the app use the credentials  
Username: `admin`  
Password: `admin123`

## Prerequisites
- Python 3.8+ installed.
- (Optional) Virtual environment `venv` in the project root, or create one with:
  ```
  python -m venv venv
  ```
- (Optional) `requirements.txt` with dependencies.

## 1) Run via Terminal (Windows PowerShell)
1. Open PowerShell or the integrated terminal in VS Code.
2. Change to the project folder:
   ```
   cd "d:\Університет\Предмети\Бази даних\2 семестр\Курсова\CafeApp_offical"
   ```
3. Activate the virtual environment:
   - PowerShell:
     ```
     .\venv\Scripts\Activate
     ```
   - Command Prompt (cmd):
     ```
     venv\Scripts\activate.bat
     ```
   If PowerShell blocks scripts, run PowerShell as Administrator and execute:
   ```
   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
   ```
4. Install dependencies (if present):
   ```
   pip install -r requirements.txt
   ```
5. Start the app. Common options:
   - If `app.py` contains the startup code:
     ```
     python app.py
     ```
   - Using Flask CLI:
     ```
     $env:FLASK_APP = "app.py"
     $env:FLASK_ENV = "development"
     python -m flask run
     ```
   (In cmd use `set FLASK_APP=app.py` and `set FLASK_ENV=development`.)

6. Open browser: http://127.0.0.1:5000

## 2) Run via IDE (Visual Studio Code)
1. Open VS Code → File → Open Folder → select project folder.
2. Install the official Python extension (ms-python.python).
3. Select the virtual environment interpreter:
   - Ctrl+Shift+P → "Python: Select Interpreter" → choose `.\venv\Scripts\python.exe`.
4. Open an integrated terminal and activate venv:
   ```
   .\venv\Scripts\Activate
   pip install -r requirements.txt
   ```
5. Simple run:
   - Open `app.py` and click "Run Python File" or use Run and Debug.
6. Recommended: add a `.vscode/launch.json` to run `app.py`. Example:
   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "name": "Python: Run app.py",
         "type": "python",
         "request": "launch",
         "program": "${workspaceFolder}/app.py",
         "console": "integratedTerminal",
         "env": {
           "FLASK_ENV": "development"
         }
       }
     ]
   }
   ```
   Save as `.vscode/launch.json`, then use Run and Debug (green ▶).

## Troubleshooting
- "Script execution is disabled" — run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` in an elevated PowerShell.
- Import errors — ensure venv is activated and dependencies installed.
- Port in use — stop the process using the port or change the app port.

If the startup file is different (not `app.py`), or you see an error, paste the file list (`dir`) or the error text and help will be provided.