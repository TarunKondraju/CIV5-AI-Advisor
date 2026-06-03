# Civ 5 AI Advisor 🧠🏛️

A powerful, standalone companion application for **Sid Meier's Civilization V** that connects your live game state to local or remote Large Language Models (LLMs) like Llama 3! 

By reading live memory logs exported from a custom Civ 5 Lua mod, this application provides an interactive Map Viewer and an Omniscient AI Assistant that acts as your Grandmaster military and economic advisor.

## Features ✨

- **Real-Time Map Extraction**: Renders your entire discovered Civilization V map in a beautiful, interactive web UI completely outside the game.
- **Authentic Civ 5 Graphics**: Visually overlays city and unit locations using the original high-resolution icons from the Civilization Wiki.
- **Comprehensive Game State Logging**: Exports an extremely detailed snapshot of the world whenever you want—including exact enemy troop locations, hitpoints, diplomatic relations, unlocked technologies, treasury gold, and city yields.
- **Local AI Integration**: Connects directly to **Ollama** (or any OpenAI-compatible API) to feed the live game state to an LLM. Ask the AI what to research next, where to settle your second city, or how to win a war!
- **Data Exporting**: Save the full map as a high-resolution JPEG, perfectly bundled with a structured Markdown text log of the entire game's stats. Feed these directly into any LLM (like ChatGPT or Claude) for instant analysis!

## Installation & Setup 🛠️

1. **Install the Lua Mod**: 
   Place the `Civ5AIBridge` folder into your Civilization V `MODS` directory (`Documents/My Games/Sid Meier's Civilization 5/MODS/`). Enable it in-game.
2. **Configure Logging**:
   Ensure your Civ 5 `config.ini` has `LoggingEnabled = 1` so the Lua mod can write the game state to `Lua.log`.
3. **Run the Advisor Application**:
   Run `Civ5_AI_Advisor.exe` (or `python app.py`). The app will automatically tail your `Lua.log` and render the map in real-time as you play your turns.

## Building from Source 🐍

This project uses Python, PyWebView, and PyInstaller. To build the executable yourself:

```powershell
pip install pywebview pyinstaller requests beautifulsoup4
python scrape_icons.py  # Downloads the official icons from the Civ Wiki
python -m PyInstaller -i icon.ico --name "Civ5_AI_Advisor" --onedir --windowed --add-data "index.html;." --add-data "icons;icons" app.py -y
```

## How It Works ⚙️
1. **StateExporter.lua** running inside Civ 5 dumps the complete Map, Player, Unit, and City data as a JSON string to `Lua.log`.
2. **app.py** runs a background thread that instantly detects changes to `Lua.log`, parses the JSON, and serves it to a local PyWebView window.
3. **index.html** uses HTML5 Canvas to aggressively render the thousands of hex tiles, resources, borders, and units instantly.
4. When you ask the AI for advice, the Python bridge intercepts your chat, automatically injects the latest minimized JSON game state into the prompt, and streams the AI's grand strategy response back into the UI.

## License
MIT License. Civilization V is a trademark of Firaxis Games and 2K Games.
