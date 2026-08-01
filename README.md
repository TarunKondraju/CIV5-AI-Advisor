# Civilization V AI Advisor (macOS Edition)

A real-time AI strategic advisor and live map visualizer for **Sid Meier's Civilization V (macOS)**.

## Features
- **Real-Time Live Map Renderer**: Synchronizes automatically with Civ 5 turn updates and unit movements.
- **Unified Custom Graphics**: Official Civ 5 civilization emblems, custom JCB backhoe loader mine graphics, and complete map legends.
- **Detailed Faction & City Production Tracking**: Displays science, culture, and gold per turn, active city construction, turns remaining, and production hammers (including AI cities).
- **Interactive Map Controls**: Click/hover floating tile cards, unified feature emojis, map zoom, and collapsible left panel controls.
- **AI Strategy Chat**: Integrated with local LLMs (Ollama / Llama 3.1) for live tactical recommendations.

## macOS Quick Start
1. Ensure **Civ 5** and **Python 3** are installed on your Mac.
2. Enable logging in Civ 5:
   Edit `~/Documents/Aspyr/Sid Meier's Civilization 5/config.ini` and set `LoggingEnabled = 1`.
3. Copy `StateExporter.lua` to your Civ 5 MODS folder:
   `~/Library/Application Support/Sid Meier's Civilization 5/MODS/Civ5AIBridge/StateExporter.lua`
4. Run the macOS Launcher:
   ```bash
   ./Launch_Advisor.command
   ```
