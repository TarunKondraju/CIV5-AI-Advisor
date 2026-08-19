# 📘 Civilization V AI Advisor - Detailed Installation Guide

This guide walks you through setting up **Civ 5 AI Advisor** on your computer step-by-step.

---

## 📑 Table of Contents
1. [Understanding the 2 Components](#1-understanding-the-2-components)
2. [Windows Setup](#2-windows-setup)
3. [macOS Setup](#3-macos-setup)
4. [pywebview Troubleshooting & Workarounds](#4-pywebview-troubleshooting--workarounds)
5. [Enabling the Mod in Civilization V](#5-enabling-the-mod-in-civilization-v)
6. [Configuring AI (Ollama / ChatGPT / Claude)](#6-configuring-ai)
7. [Troubleshooting & Common Issues](#7-troubleshooting--common-issues)

---

## 1. Understanding the 2 Components

- **Part 1: The In-Game Mod (`Civ5AIBridge`)**: A Lua script that runs quietly inside Civ 5. Whenever a turn starts or you move units, it dumps your empire's state to `Lua.log`.
- **Part 2: The Companion App (`CIV5-AI-Advisor`)**: A standalone application with a user interface that monitors `Lua.log` and renders your world map, stats, and provides AI recommendations.

---

## 2. Windows Setup

### Step 1: Install Python or Anaconda (If you don't have it)
1. Download Python from [python.org](https://www.python.org/downloads/) or install [Anaconda](https://www.anaconda.com/download).
2. When running the standard Python installer, **check the box "Add Python to PATH"** before clicking Install.

### Step 2: Install Required Dependencies
Open **Command Prompt** (<kbd>Win</kbd> + <kbd>R</kbd> $\rightarrow$ type `cmd` $\rightarrow$ press Enter) and run:
```cmd
pip install pywebview
```
*(Or if using Anaconda, run: `conda install -c conda-forge pywebview`)*

### Step 3: Copy the Mod to Your Civ 5 Folder
Copy the folder named **`Civ5AIBridge`** into your Civilization 5 `MODS` directory:
```text
C:\Users\<YourUsername>\Documents\My Games\Sid Meier's Civilization 5\MODS\
```

Inside that folder, you should have:
- `Civ5AIBridge.modinfo`
- `StateExporter.lua`

### Step 4: Turn On Logging in Civ 5
1. Open the file:
   ```text
   C:\Users\<YourUsername>\Documents\My Games\Sid Meier's Civilization 5\config.ini
   ```
2. Search for `LoggingEnabled` and `MessageLog` and set both to `1`:
   ```ini
   LoggingEnabled = 1
   MessageLog = 1
   ```
3. Save the file.

### Step 5: Launch the App
Double click **`Launch_Advisor.bat`** in the project folder.

---

## 3. macOS Setup

### Step 1: Install Python & pywebview
1. macOS comes with Python 3, or you can install it via [Homebrew](https://brew.sh) (`brew install python`).
2. Open **Terminal** and run:
   ```bash
   pip3 install pywebview
   ```

### Step 2: Copy the Mod to macOS MODS Folder
1. Open **Finder**, press <kbd>Cmd</kbd> + <kbd>Shift</kbd> + <kbd>G</kbd>, and enter:
   ```text
   ~/Library/Application Support/Sid Meier's Civilization 5/MODS/
   ```
   *(If the `MODS` folder doesn't exist, create it).*
2. Copy the **`Civ5AIBridge`** folder into it.

### Step 3: Enable Logging in Civ 5 config.ini
1. In Finder (<kbd>Cmd</kbd> + <kbd>Shift</kbd> + <kbd>G</kbd>), go to:
   - Steam: `~/Library/Application Support/Sid Meier's Civilization 5/`
   - Aspyr: `~/Documents/Aspyr/Sid Meier's Civilization 5/`
2. Open `config.ini` in TextEdit and ensure:
   ```ini
   LoggingEnabled = 1
   MessageLog = 1
   ```
3. Save the file.

### Step 4: Launch the App
Double-click **`Launch_Advisor.command`** or run `python3 app.py` in Terminal.

---

## 4. `pywebview` Troubleshooting & Workarounds

If you experience issues installing or running `pywebview` (e.g. `ModuleNotFoundError: No module named 'webview'` or `Access is denied` during pip install):

### Method A: User Flag Installation
If standard pip fails due to permissions, install it only for your current user:
```bash
pip install --user pywebview
```

### Method B: Anaconda / Conda Environments
If you use Anaconda / Miniconda, open the Anaconda Prompt and run:
```bash
conda install -c conda-forge pywebview
```
The included `Launch_Advisor.bat` will automatically detect and activate Anaconda.

### Method C: Zero-Install AI Strategy Method (Direct Log Drag & Drop)
If you cannot install Python or `pywebview` on a computer, you can still get tactical AI advice:
1. Enable the `Civ5AIBridge` mod in Civ 5 and play your game.
2. The game automatically saves every detail to:
   - `Documents\My Games\Sid Meier's Civilization 5\Logs\Lua.log`
3. Drag and drop `Lua.log` into **ChatGPT (GPT-4o)** or **Claude** in your browser and ask for turn recommendations!

---

## 5. Enabling the Mod in Civilization V

> ⚠️ **Important:** You must start your game via the Civ 5 **MODS** menu, not standard Single Player, for the data exporter to run.

1. Launch **Sid Meier's Civilization V**.
2. On the main menu, click **MODS**.
3. You will see **Civ 5 AI Bridge** listed. Click the checkbox on the right to enable it (a green checkmark will appear).
4. Click **NEXT** at the bottom.
5. Click **Single Player** $\rightarrow$ **Set Up Game** (or Load Game).
6. Start your game! The companion app will immediately detect your empire and render the map.

---

## 6. Configuring AI

### Free Local AI (Ollama - Recommended)
1. Download [Ollama](https://ollama.com).
2. Run in terminal: `ollama run llama3.1`
3. In Civ 5 AI Advisor $\rightarrow$ **⚙️ AI Settings**:
   - **Endpoint**: `http://127.0.0.1:11434/api/chat`
   - **Model**: `llama3.1`

### Cloud AI (OpenAI ChatGPT)
1. Generate an API key from [OpenAI API Keys](https://platform.openai.com/api-keys).
2. In Civ 5 AI Advisor $\rightarrow$ **⚙️ AI Settings**:
   - **Endpoint**: `https://api.openai.com/v1/chat/completions`
   - **Model**: `gpt-4o`
   - **API Key**: `sk-...`

---

## 7. Troubleshooting & Common Issues

- **The map is blank or says "Waiting for sync"**:
  - Make sure you enabled the mod in the in-game MODS menu.
  - Make sure `LoggingEnabled = 1` and `MessageLog = 1` are set in `config.ini`.
- **Mod not showing in Civ 5 MODS menu**:
  - Ensure the folder is placed in `Documents\My Games\Sid Meier's Civilization 5\MODS\Civ5AIBridge` and not doubly nested (`Civ5AIBridge\Civ5AIBridge`).
- **Game crashes on startup**:
  - Clear your cache by deleting everything inside `Documents\My Games\Sid Meier's Civilization 5\cache\`.
