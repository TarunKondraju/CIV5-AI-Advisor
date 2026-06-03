import webview
import json
import urllib.request
import os
import sys
import threading
import time

class Api:
    def __init__(self):
        self._window = None
        self._game_state = {}
        self._state_version = 0
        self._running = True
        self._last_size = 0
        self._chat_history = []
        
        # Start background thread to tail log file
        threading.Thread(target=self._tail_log, daemon=True).start()

    def set_window(self, window):
        self._window = window
        
    def _get_config_path(self):
        appdata = os.getenv('APPDATA')
        dir_path = os.path.join(appdata, 'Civ5_AI_Advisor')
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return os.path.join(dir_path, 'config.json')

    def get_config(self):
        config_path = self._get_config_path()
        if not os.path.exists(config_path):
            default_cfg = {
                "ai_endpoint": "http://127.0.0.1:11434/api/chat",
                "ai_model": "llama3.1",
                "api_key": ""
            }
            with open(config_path, 'w') as f:
                json.dump(default_cfg, f, indent=4)
            return default_cfg
        with open(config_path, 'r') as f:
            return json.load(f)
            
    def save_config(self, cfg):
        config_path = self._get_config_path()
        with open(config_path, 'w') as f:
            json.dump(cfg, f, indent=4)
        return "Saved"
        
    def _tail_log(self):
        LOG_FILE = os.path.expanduser(r"~\OneDrive\Documents\My Games\Sid Meier's Civilization 5\Logs\Lua.log")
        
        while self._running:
            if not os.path.exists(LOG_FILE):
                time.sleep(1)
                continue
                
            with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                self._last_size = 0
                
                while self._running:
                    try:
                        current_size = os.path.getsize(LOG_FILE)
                        if current_size != self._last_size:
                            print(f"DEBUG: File size changed from {self._last_size} to {current_size}")
                            self._last_size = current_size
                            f.seek(0)
                            data = f.read()
                            print(f"DEBUG: Read {len(data)} bytes.")
                            
                            idx = data.rfind("CIV5_AI_BRIDGE_DATA:")
                            if idx != -1:
                                end_idx = data.find('\n', idx)
                                if end_idx == -1: end_idx = len(data)
                                line = data[idx:end_idx]
                                json_str = line.split("CIV5_AI_BRIDGE_DATA:")[1].strip()
                                try:
                                    self._game_state = json.loads(json_str)
                                    self._state_version += 1
                                    print(f"DEBUG: Successfully parsed JSON. Found {len(self._game_state.get('map', []))} map tiles. Version {self._state_version}")
                                except Exception as e:
                                    print(f"JSON Parse Error: {e}")
                    except Exception as e:
                        pass
                    time.sleep(1)
                    
    def get_state(self, client_version):
        if self._state_version > client_version:
            return json.dumps({"version": self._state_version, "data": self._game_state})
        return ""
        
    def send_chat_message(self, message):
        if not self._game_state:
            return "❌ Error: Please wait for map data to load first."
            
        # 1. Minify JSON to save memory/speed for the Local AI
        # Filter the map to ONLY include tiles near the active player
        active_coords = []
        for p in self._game_state.get('players', []):
            if p.get('id') == self._game_state.get('active_player'):
                for c in p.get('cities', []): active_coords.append((c['x'], c['y']))
                for u in p.get('units', []): active_coords.append((u['x'], u['y']))
                
        clean_map = []
        for t in self._game_state.get('map', []):
            # Only send tiles within 4 hexes of a player unit/city
            is_near = False
            for ax, ay in active_coords:
                if abs(t['x'] - ax) <= 4 and abs(t['y'] - ay) <= 4:
                    is_near = True
                    break
            if not is_near: continue
            
            clean_t = [t['x'], t['y'], t['t']]
            if 'f' in t: clean_t.append(f"f:{t['f']}")
            if 'r' in t: clean_t.append(f"r:{t['r']}")
            if 'i' in t: clean_t.append(f"i:{t['i']}")
            if t.get('h'): clean_t.append('h')
            if t.get('m'): clean_t.append('m')
            clean_map.append(clean_t)
            
        clean_state = {
            "turn": self._game_state.get("turn"),
            "active_player": self._game_state.get("active_player"),
            "players": self._game_state.get("players", []),
            "resource_dict": self._game_state.get("resource_dict", {}),
            "feature_dict": self._game_state.get("feature_dict", {}),
            "improvement_dict": self._game_state.get("improvement_dict", {}),
            "map_format": "[x, y, terrain_id, extra...]. m=mountain, h=hill, f:ID=feature, r:ID=resource, i:ID=improvement",
            "map": clean_map
        }
            
        system_prompt = """You are a top-tier, veteran Civilization V (Civ 5) Grandmaster AI. You are NOT playing Civ 6 (no districts, no campuses).
You are playing Civ 5. 
The user wants EXACT, precise, and ruthless instructions to win as fast as possible.
Do NOT give vague advice. Give exact build orders (e.g., Scout -> Monument -> Shrine).
Give exact technology paths (e.g., Pottery -> Animal Husbandry).
Give EXACT tile coordinates for settling (e.g., "Settle your second city exactly on the Hill at X:15, Y:22 to grab the Salt and River").
Analyze the provided JSON map data. Look at the `resource_dict` and the `map` array to find the best yields (Salt, Wheat, Iron, etc.).
Analyze the `players` array to see the active player's civilization and units.
Speak like a strict, veteran military commander and grand strategy master. Give exact turn-by-turn directives."""

        if not self._chat_history:
            self._chat_history.append({"role": "system", "content": system_prompt})
            
        # Add ONLY the user's message to the permanent history
        self._chat_history.append({"role": "user", "content": message})
        
        # Create a temporary payload for Ollama
        import copy
        payload_messages = copy.deepcopy(self._chat_history)
        
        # Inject the current game state into the LAST message invisibly
        contextual_message = f"CURRENT GAME STATE JSON:\n{json.dumps(clean_state)}\n\nUSER QUESTION:\n{message}"
        payload_messages[-1]["content"] = contextual_message
        
        cfg = self.get_config()
        url = cfg.get("ai_endpoint", "http://127.0.0.1:11434/api/chat")
        model = cfg.get("ai_model", "llama3.1")
        
        # If the user put a URL but it's empty, or they disabled AI
        if not url or url.strip() == "":
            return "❌ No AI Endpoint configured. Operating in Map Viewer Mode."
            
        payload = {
            "model": model,
            "messages": payload_messages,
            "stream": True,
            "options": {
                "num_ctx": 8192
            }
        }
        
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
            
            # Add API Key if present
            api_key = cfg.get("api_key", "").strip()
            if api_key:
                req.add_header("Authorization", f"Bearer {api_key}")
                
            with urllib.request.urlopen(req, timeout=600) as response:
                self._window.evaluate_js("createAiBubble()")
                full_text = ""
                for line in response:
                    if line:
                        chunk = json.loads(line)
                        if 'message' in chunk and 'content' in chunk['message']:
                            text = chunk['message']['content']
                            full_text += text
                            self._window.evaluate_js(f"appendAiText({json.dumps(text)})")
                            
                self._chat_history.append({"role": "assistant", "content": full_text})
                return ""
        except Exception as e:
            self._chat_history.pop()
            return f"❌ Ollama Local API Error: {str(e)}"
            
    def save_map_image(self, b64_data, suggested_name):
        import base64
        import webview
        try:
            result = self._window.create_file_dialog(
                webview.SAVE_DIALOG, 
                directory='', 
                save_filename=suggested_name,
                file_types=('Image Files (*.jpg;*.jpeg;*.png)', 'All Files (*.*)')
            )
            if result and len(result) > 0:
                file_path = result[0]
                if "," in b64_data:
                    b64_data = b64_data.split(",", 1)[1]
                data = base64.b64decode(b64_data)
                with open(file_path, "wb") as f:
                    f.write(data)
                
                try:
                    data_path = file_path + "_Data.json"
                    with open(data_path, "w", encoding="utf-8") as df:
                        json.dump(self._game_state, df, indent=4)
                except Exception as e2:
                    pass
                    
                try:
                    log_path = file_path + "_Log.txt"
                    with open(log_path, "w", encoding="utf-8") as lf:
                        gs = self._game_state
                        
                        lf.write(f"# CIV 5 GAME STATE LOG\n")
                        lf.write(f"Turn: {gs.get('turn', 'Unknown')}\n")
                        lf.write(f"Active Player ID: {gs.get('active_player', 'Unknown')}\n\n")
                        
                        lf.write("## PLAYERS & CIVILIZATIONS\n")
                        for p in gs.get('players', []):
                            is_active = " (ACTIVE PLAYER)" if p.get('id') == gs.get('active_player') else ""
                            lf.write(f"### Player {p.get('id')}: {p.get('name')} - {p.get('civ')}{is_active}\n")
                            lf.write(f"- Treasury: {p.get('gold', 0)} Gold ({p.get('gpt', 0)} GPT)\n")
                            lf.write(f"- Science: {p.get('science', 0)}/turn\n")
                            lf.write(f"- Culture: {p.get('culture', 0)} ({p.get('cpt', 0)}/turn)\n")
                            lf.write(f"- Faith: {p.get('faith', 0)} ({p.get('fpt', 0)}/turn)\n")
                            lf.write(f"- Happiness: {p.get('happiness', 0)}\n")
                            lf.write(f"- Golden Age Progress: {p.get('goldenAge', 0)}\n")
                            lf.write(f"- Active Research: {p.get('activeTech', 'None')}\n")
                            
                            techs = p.get('techs', [])
                            if techs:
                                tech_names = [gs.get('tech_dict', {}).get(str(t), str(t)) for t in techs]
                                lf.write(f"- Unlocked Techs: {', '.join(tech_names)}\n")
                                
                            relations = p.get('relations', [])
                            if relations:
                                rel_strs = []
                                for r in relations:
                                    target_id = r.get('civ')
                                    target_name = "Unknown"
                                    for target in gs.get('players', []):
                                        if target.get('id') == target_id:
                                            target_name = target.get('civ')
                                            break
                                    rel_strs.append(f"{target_name} ({r.get('status')})")
                                lf.write(f"- Diplomacy: {', '.join(rel_strs)}\n")
                            
                            cities = p.get('cities', [])
                            if cities:
                                lf.write(f"\n#### Cities ({len(cities)}):\n")
                                for c in cities:
                                    y = c.get('yields', {})
                                    lf.write(f"  - {c.get('name')} at X:{c.get('x')} Y:{c.get('y')} | Pop: {c.get('pop')} | HP: {c.get('maxhp', 100) - c.get('hp', 0)}/{c.get('maxhp', 100)}\n")
                                    lf.write(f"    Building: {c.get('build', 'Nothing')}\n")
                                    lf.write(f"    Yields: {y.get('food', 0)} Food, {y.get('prod', 0)} Prod, {y.get('gold', 0)} Gold, {y.get('science', 0)} Sci, {y.get('culture', 0)} Cult, {y.get('faith', 0)} Faith\n")
                            
                            units = p.get('units', [])
                            if units:
                                lf.write(f"\n#### Units ({len(units)}):\n")
                                for u in units:
                                    fort = "Fortified" if u.get('fortified') else "Active"
                                    lf.write(f"  - {u.get('name')} at X:{u.get('x')} Y:{u.get('y')} | HP: {u.get('hp')}/{u.get('max_hp')} | Lvl {u.get('lvl')} (XP {u.get('xp')}) | STR: {u.get('str')} | Status: {fort}\n")
                            
                            lf.write("\n")
                except Exception as e3:
                    print("Log error:", e3)
                    
                return "Saved successfully to " + file_path
            return "Cancelled"
        except Exception as e:
            return "Error: " + str(e)

if __name__ == '__main__':
    def start_app():
        api = Api()
        
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        html_file = os.path.join(base_path, 'index.html')
        
        window = webview.create_window('Civ 5 AI Advisor', html_file, js_api=api, width=1280, height=720, text_select=True)
        api.set_window(window)
        webview.start()
        
    start_app()
