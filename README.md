# 🌍 Civilization V AI Advisor (Universal - Windows & macOS)

A real-time AI strategic advisor and interactive live map companion for **Sid Meier's Civilization V** (compatible with both Windows and macOS).

---

## ✨ Features
- 🗺️ **Real-Time Live Tactical Map**: Synchronizes automatically with Civ 5 turn updates, territory expansion, and unit movements.
- 🏛️ **Faction & City Analytics**: Real-time tracking of Science, Culture, Faith, Gold per turn, active city production, remaining turns, and production hammers across all known civilizations.
- 🕵️ **Super Spy Diplomatic Intel**: Unveils hidden AI leader approaches (e.g., *Guarded*, *Hostile*, or *Deceptive - Planning Attack!*).
- 🤖 **AI Strategy Advisor**: Integrated with local LLMs (**Ollama / Llama 3.1**) or cloud models (**OpenAI GPT-4o**) for turn-by-turn military, economic, and tactical advice.
- 📸 **High-Resolution Map & AI Log Export**: Export full-resolution map images along with a comprehensive game state text log (`_Log.txt`) to easily share or paste into ChatGPT / Claude.

---

## 🏗️ How It Works

The system operates using two lightweight components:
1. **The In-Game Mod (`Civ5AIBridge`)**: A lightweight Lua script that runs inside Civilization V and writes your empire's state to `Lua.log` whenever a turn begins or units move.
2. **The Desktop Advisor App**: A standalone companion app (built with Python & HTML/JS) that tails `Lua.log` in real-time to render the live map and provide AI strategy chat.

---

## 🪟 Windows Installation Guide

### Prerequisites
- **Sid Meier's Civilization V** (Steam or standalone).
- **Python 3.8+** or **Anaconda/Miniconda** installed. *(If you do not have Python, download it from [python.org](https://www.python.org/downloads/) and check **"Add Python to PATH"**).*

---

### Step 1: Install the In-Game Mod
1. Download or clone this repository to your computer.
2. Locate the **`Civ5AIBridge`** folder inside this repository.
3. Copy the entire **`Civ5AIBridge`** folder into your Civ 5 MODS folder:
   ```text
   %USERPROFILE%\Documents\My Games\Sid Meier's Civilization 5\MODS\
   ```
   *(Full path: `C:\Users\<YourUsername>\Documents\My Games\Sid Meier's Civilization 5\MODS\Civ5AIBridge`)*

---

### Step 2: Enable Logging in Civ 5
Civ 5 needs logging enabled so the mod can export game state data:
1. Open the file:
   ```text
   %USERPROFILE%\Documents\My Games\Sid Meier's Civilization 5\config.ini
   ```
2. Find the following lines (use <kbd>Ctrl</kbd> + <kbd>F</kbd>) and ensure they are both set to **`1`**:
   ```ini
   LoggingEnabled = 1
   MessageLog = 1
   ```
3. Save and close `config.ini`.

---

### Step 3: Install App Dependencies
Open **Command Prompt** (<kbd>Win</kbd> + <kbd>R</kbd> $\rightarrow$ type `cmd` $\rightarrow$ hit Enter) and run:
```cmd
pip install pywebview
```
*(If you encounter permission errors, run: `pip install --user pywebview` or `conda install -c conda-forge pywebview`).*

---

### Step 4: Launch the Companion App
- Double-click **`Launch_Advisor.bat`** in the project folder to open the Advisor App window.

---

### Step 5: Enable the Mod in Civilization V
1. Start **Sid Meier's Civilization V**.
2. From the Main Menu, click **MODS**.
3. Check the box next to **Civ 5 AI Bridge** to enable it.
4. Click **NEXT** (Accept).
5. Click **Single Player** $\rightarrow$ **Set Up Game** or **Load Game**.
6. Once in game, the Desktop Advisor will automatically detect the game and sync your map!

---

## 🍏 macOS Installation Guide

### Prerequisites
- **Sid Meier's Civilization V** (Steam or Aspyr Mac App Store).
- **Python 3** installed.

---

### Step 1: Install the In-Game Mod
1. Download or clone this repository.
2. Open **Finder**, press <kbd>Cmd</kbd> + <kbd>Shift</kbd> + <kbd>G</kbd>, and paste:
   ```text
   ~/Library/Application Support/Sid Meier's Civilization 5/MODS/
   ```
   *(If the `MODS` folder does not exist, create it).*
3. Copy the **`Civ5AIBridge`** folder into that `MODS` folder.

---

### Step 2: Enable Logging in Civ 5
1. Press <kbd>Cmd</kbd> + <kbd>Shift</kbd> + <kbd>G</kbd> in Finder and navigate to:
   - **Steam version**: `~/Library/Application Support/Sid Meier's Civilization 5/`
   - **Aspyr / App Store version**: `~/Documents/Aspyr/Sid Meier's Civilization 5/`
2. Open `config.ini` in TextEdit and ensure the following lines are set:
   ```ini
   LoggingEnabled = 1
   MessageLog = 1
   ```
3. Save and close the file.

---

### Step 3: Install App Dependencies & Launch
1. Open **Terminal** and install `pywebview`:
   ```bash
   pip3 install pywebview
   ```
2. In the project folder, double-click **`Launch_Advisor.command`** (or run `python3 app.py` in Terminal).
3. Start Civ 5, go to **MODS**, activate **Civ 5 AI Bridge**, and start your game.

---

## 🛠️ Workarounds for `pywebview` Issues

If you cannot install or run `pywebview` on your system (e.g. permission restrictions, locked Python environments, or missing C++ compilers), use any of these simple workarounds:

### Workaround 1: Use the `--user` Installation Flag
If `pip install pywebview` fails due to access denied / permissions:
```bash
pip install --user pywebview
```

### Workaround 2: Anaconda / Conda Environments
If you are using Anaconda or Miniconda:
```bash
conda install -c conda-forge pywebview
```
Or open the **Anaconda Prompt**, navigate to the project folder, and run `python app.py`.

### Workaround 3: Zero-Install / Web Browser Method (Direct Log Export)
You don't even need the companion app to get full AI strategy advice!
1. Enable the mod in Civ 5 and play your turns normally.
2. Civ 5 will automatically export complete tactical data to:
   - **Windows:** `Documents\My Games\Sid Meier's Civilization 5\Logs\Lua.log`
   - **macOS:** `~/Library/Application Support/Sid Meier's Civilization 5/Logs/Lua.log`
3. Simply **drag and drop `Lua.log` directly into ChatGPT (GPT-4o) or Claude** in your web browser and ask:
   > *"Analyze my Civ 5 game state log. What should be my next technology, city production focus, and military strategy?"*

---

## 🤖 Configuring an AI Brain (Optional)

The software functions fully offline as a **Live Tactical Map Viewer** without an AI. To activate live AI strategy recommendations:

Click the **⚙️ AI Settings** button in the left sidebar:

### Option A: 100% Free & Local AI (Ollama)
1. Download and install [Ollama](https://ollama.com).
2. Open your terminal/command prompt and run:
   ```bash
   ollama run llama3.1
   ```
3. In the Advisor App's **⚙️ AI Settings**:
   - **Endpoint**: `http://127.0.0.1:11434/api/chat`
   - **Model**: `llama3.1`
   - **API Key**: *(Leave blank)*

### Option B: Cloud AI (OpenAI ChatGPT)
1. Get an API key from [platform.openai.com](https://platform.openai.com/api-keys).
2. In the Advisor App's **⚙️ AI Settings**:
   - **Endpoint**: `https://api.openai.com/v1/chat/completions`
   - **Model**: `gpt-4o` (or `gpt-4-turbo`)
   - **API Key**: Paste your secret key.

---

## ❓ Troubleshooting & FAQ

| Problem | Solution |
| :--- | :--- |
| **"Waiting for game data..." / Map not loading** | Make sure you launched the game through the **MODS** menu and that `LoggingEnabled = 1` is in `config.ini`. |
| **Mod is not showing up in Civ 5 MODS menu** | Verify that `Civ5AIBridge.modinfo` and `StateExporter.lua` are directly inside `Documents\My Games\Sid Meier's Civilization 5\MODS\Civ5AIBridge\`. |
| **`Launch_Advisor.bat` closes immediately** | Open `cmd`, navigate to the folder, and run `python app.py` to check for missing dependencies (`pip install pywebview`). |
| **Old data showing from previous game** | Delete the contents of `Documents\My Games\Sid Meier's Civilization 5\cache` and restart Civ 5. |

---

## 📜 License
MIT License. Created for the Civilization V community.
