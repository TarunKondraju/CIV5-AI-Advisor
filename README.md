# Civilization V AI Advisor (Universal - Windows & macOS)

A real-time AI strategic advisor and live map visualizer for **Sid Meier's Civilization V (Windows & macOS)**.

## Features
- **Real-Time Live Map Renderer**: Synchronizes automatically with Civ 5 turn updates and unit movements.
- **Unified Custom Graphics**: Official Civ 5 civilization emblems, custom JCB backhoe loader mine graphics, and complete map legends.
- **Detailed Faction & City Production Tracking**: Displays science, culture, and gold per turn, active city construction, turns remaining, and production hammers (including AI cities).
- **Interactive Map Controls**: Click/hover floating tile cards, unified feature emojis, map zoom, and collapsible left panel controls.
- **AI Strategy Chat**: Integrated with local LLMs (Ollama / Llama 3.1) for live tactical recommendations.

---

## 🪟 Windows Setup Instructions

1. Ensure **Civilization V** and **Python 3** are installed.
2. Install Python dependencies:
   ```cmd
   pip install pywebview requests
   ```
3. Enable logging in Civ 5:
   Edit `Documents\My Games\Sid Meier's Civilization 5\config.ini` and set:
   ```ini
   LoggingEnabled = 1
   ```
4. Copy the `Civ5AIBridge` folder into your Civ 5 MODS folder:
   `Documents\My Games\Sid Meier's Civilization 5\MODS\Civ5AIBridge`
5. Double-click **`Launch_Advisor.bat`** to run!

---

## 🍏 macOS Setup Instructions

1. Ensure **Civilization V** and **Python 3** are installed.
2. Enable logging in Civ 5:
   Edit `~/Documents/Aspyr/Sid Meier's Civilization 5/config.ini` and set:
   ```ini
   LoggingEnabled = 1
   ```
3. Copy the `Civ5AIBridge` folder into your Civ 5 MODS folder:
   `~/Library/Application Support/Sid Meier's Civilization 5/MODS/Civ5AIBridge`
4. Double-click **`Launch_Advisor.command`** to run!
