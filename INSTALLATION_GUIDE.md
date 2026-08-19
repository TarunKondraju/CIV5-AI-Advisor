# 🌍 Civilization V AI Advisor (Universal - Windows & macOS)

A real-time AI strategic advisor and interactive live tactical map companion for **Sid Meier's Civilization V** (compatible with both Windows and macOS).

---

## ⚡ Quick Summary: Do I Need to Install Python or `pywebview`?

| Your Operating System / Usage | Need to Install Python or `pywebview`? | How to Run |
| :--- | :---: | :--- |
| 🪟 **Windows (Standalone App)** | ❌ **NO (Zero Setup)** | Double-click **`windows/Civ5_AI_Advisor/Civ5_AI_Advisor.exe`** |
| 🍏 **macOS / Source Code Users** | ✅ **YES** | Run `pip3 install pywebview`, then `python3 app.py` |
| 🌐 **Zero-Install (Browser Method)** | ❌ **NO (No App Needed)** | Drag & drop your game's **`Lua.log`** straight into ChatGPT / Claude |

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
1. **The In-Game Mod (`Civ5AIBridge`)**: A clean Lua script that runs inside Civilization V and writes your empire's state to `Lua.log` whenever a turn begins or units move.
2. **The Desktop Advisor App**: A standalone companion app that reads `Lua.log` in real-time to render your live map and provide AI strategy chat.

---

## 🪟 Windows Setup (Zero Python Setup Needed)

Everything is pre-packaged for Windows in the **`windows/`** folder.

### Step 1: Install the In-Game Mod
1. Copy the folder named **`Civ5AIBridge`** (located in `windows/Civ5AIBridge` or the root folder).
2. Paste it into your Civilization 5 `MODS` folder:
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

### Step 3: Launch the Advisor App
- Open the **`windows/Civ5_AI_Advisor/`** folder and double-click **`Civ5_AI_Advisor.exe`** *(or run `Launch_Advisor.bat`)*.
- **You do NOT need Python or `pywebview` installed on Windows.**

---

### Step 4: Enable the Mod in Civilization V
1. Start **Sid Meier's Civilization V**.
2. From the Main Menu, click **MODS** *(do not click standard Single Player)*.
3. Check the box next to **Civ 5 AI Bridge** so it turns green.
4. Click **NEXT** (Accept).
5. Click **Single Player** $\rightarrow$ **Set Up Game** (or **Load Game** for modded saves).
6. Start your game. As soon as you enter the world or take a turn, the AI Advisor will switch to **`● LIVE`** and render your live map!

> ⚠️ **Important Note on Saved Games**: In Civilization V, loading an unmodded standard save file will disable active mods. To play with the AI Advisor, always start a new match or load from your **`ModdedSaves`** list via the **MODS** menu!

---

## 🍏 macOS Setup Instructions

### Step 1: Install the In-Game Mod
1. Open **Finder**, press <kbd>Cmd</kbd> + <kbd>Shift</kbd> + <kbd>G</kbd>, and paste:
   ```text
   ~/Library/Application Support/Sid Meier's Civilization 5/MODS/
   ```
   *(If the `MODS` folder does not exist, create it).*
2. Copy the **`Civ5AIBridge`** folder into that `MODS` folder.

---

### Step 2: Enable Logging in Civ 5
1. In Finder (<kbd>Cmd</kbd> + <kbd>Shift</kbd> + <kbd>G</kbd>), go to:
   - **Steam version**: `~/Library/Application Support/Sid Meier's Civilization 5/`
   - **Aspyr / App Store version**: `~/Documents/Aspyr/Sid Meier's Civilization 5/`
2. Open `config.ini` in TextEdit and ensure:
   ```ini
   LoggingEnabled = 1
   MessageLog = 1
   ```
3. Save and close the file.

---

### Step 3: Launch & Play (macOS)
1. Open **Terminal** and install `pywebview`:
   ```bash
   pip3 install pywebview
   ```
2. In the project folder, double-click **`Launch_Advisor.command`** (or run `python3 app.py` in Terminal).
3. Start Civ 5 $\rightarrow$ **MODS** $\rightarrow$ enable **Civ 5 AI Bridge** $\rightarrow$ Play!

---

## 🌐 Zero-Install Web Browser Alternative

If you do not want to install any applications:
1. Enable the mod in Civ 5 and play your turns normally.
2. Civ 5 automatically writes your full game state to:
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
| **"Waiting for game data..." / Map not loading** | Make sure you launched the match through the **MODS** menu and that `LoggingEnabled = 1` and `MessageLog = 1` are set in `config.ini`. |
| **Mod is not showing up in Civ 5 MODS menu** | Verify that `Civ5AIBridge.modinfo` and `StateExporter.lua` are directly inside `Documents\My Games\Sid Meier's Civilization 5\MODS\Civ5AIBridge\`. |
| **Old data showing from previous game** | Delete the contents of `Documents\My Games\Sid Meier's Civilization 5\cache\` and restart Civ 5. |

---

## 📜 License
MIT License. Created for the Civilization V community.
