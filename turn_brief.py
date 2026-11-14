"""Print a compact briefing of the latest Civ 5 turn exported by the Civ5AIBridge mod.

Usage: py turn_brief.py [--json out.json] [--full]
"""
import json, os, sys, math, datetime

if sys.platform == "darwin":
    LOG = os.path.expanduser("~/Library/Application Support/Sid Meier's Civilization 5/Logs/Lua.log")
else:
    LOG = os.path.expanduser(r"~\OneDrive\Documents\My Games\Sid Meier's Civilization 5\Logs\Lua.log")
    if not os.path.exists(LOG):
        LOG = os.path.expanduser(r"~\Documents\My Games\Sid Meier's Civilization 5\Logs\Lua.log")


def load_state():
    size = os.path.getsize(LOG)
    with open(LOG, "rb") as f:
        f.seek(max(0, size - 40_000_000))
        buf = f.read().decode("utf-8", "ignore")
    end = len(buf)
    while True:
        s = buf.rfind("CIV5_AI_BRIDGE_START", 0, end)
        if s == -1:
            raise SystemExit("No bridge export found in Lua.log - is the mod enabled and LoggingEnabled=1?")
        e = buf.find("CIV5_AI_BRIDGE_END", s)
        if e != -1:
            parts = [l.split("CIV5_AI_BRIDGE_CHUNK:", 1)[1].strip()
                     for l in buf[s:e].split("\n") if "CIV5_AI_BRIDGE_CHUNK:" in l]
            try:
                return json.loads("".join(parts))
            except json.JSONDecodeError:
                pass
        end = s


def dist(a, b):
    # offset-coords hex distance (Civ 5 uses odd-row offset)
    def cube(x, y):
        q = x - (y - (y & 1)) // 2
        return q, y, -q - y
    ax, ay, az = cube(a[0], a[1]); bx, by, bz = cube(b[0], b[1])
    return max(abs(ax - bx), abs(ay - by), abs(az - bz))


CIVILIAN = {"Worker", "Work Boat", "Caravan", "Cargo Ship", "Settler", "Missionary", "Inquisitor",
            "Great Prophet", "Archaeologist", "Great Merchant", "Great Writer", "Great Artist",
            "Great Musician", "Great Scientist", "Great Engineer", "Great General", "Great Admiral"}


def is_civilian(name):
    return name in CIVILIAN or "Great" in name or "(" in name


def main():
    full = "--full" in sys.argv
    st = load_state()
    if "--json" in sys.argv:
        json.dump(st, open(sys.argv[sys.argv.index("--json") + 1], "w", encoding="utf-8"), indent=1)
    me_id = st["active_player"]
    P = {p["id"]: p for p in st["players"]}
    me = P[me_id]
    a = st.get("advisor", {})
    print(f"LOG updated {datetime.datetime.fromtimestamp(os.path.getmtime(LOG)):%Y-%m-%d %H:%M}")
    print(f"TURN {st['turn']}  {me['name']} ({me['civ']})  {a.get('difficulty','')} {a.get('game_speed','')}  era={a.get('era','')}")
    if "error" in a:
        print("ADVISOR BLOCK ERROR:", a["error"])
    print(f"gold {a.get('gold','?')} ({a.get('gpt', me['gold']):+}/t)  sci {me['sci']}/t  cul {me['cul']}/t "
          f"(stored {a.get('culture_stored','?')}/{a.get('next_policy_cost','?')})  happy {a.get('happiness','?')}  "
          f"faith {a.get('faith','?')} (+{a.get('fpt','?')})  GA {a.get('golden_age_progress','?')}/{a.get('golden_age_needed','?')} turns={a.get('golden_age_turns',0)}")
    print(f"research: {a.get('research','?')} ({a.get('research_turns','?')}t)  techs={a.get('my_techs','?')}  "
          f"pantheon={a.get('has_pantheon')} religion={a.get('religion') or '-'}  trade {a.get('trade_routes','?')}/{a.get('trade_routes_max','?')}  tourism {a.get('tourism','?')}")
    print("available techs:", ", ".join(f"{t['n']}({t['turns']})" for t in a.get("techs_available", [])))
    print("policies:", ", ".join(a.get("policies", [])) or "-")
    if a.get("projects"): print("projects:", a["projects"])
    if a.get("wonders"): print("wonders:", ", ".join(a["wonders"]))
    if full: print("techs known:", ", ".join(a.get("techs_known", [])))

    print("\nCITIES")
    for c in a.get("cities", []):
        flags = ("CAPITAL " if c.get("capital") else "") + ("PUPPET " if c.get("puppet") else "") + \
                (f"RESIST{c['resistance']} " if c.get("resistance") else "") + \
                (f"DAMAGED {c['hp']}/{c['maxhp']} " if c.get("hp", 1) < c.get("maxhp", 1) else "")
        print(f" {c['name']} ({c['x']},{c['y']}) pop {c['pop']} {flags}| food {c.get('food',0):+} grow {c.get('growth_turns','?')}t "
              f"prod {c.get('prod','?')} gold {c.get('gold','?')} sci {c.get('sci','?')} cul {c.get('cul','?')} faith {c.get('faith','?')} str {c.get('strength','?')}")
        print(f"   building: {c.get('build')} ({c.get('build_turns')}t)  specialists {c.get('specialists',0)}")
        print(f"   has: {', '.join(c.get('buildings', []))}")
        cb = sorted(c.get("can_build", []), key=lambda b: b["turns"])
        print(f"   can build: {', '.join(f'{b['n']}({b['turns']}t/{b['buy']}g)' for b in cb)}")
        if full or c.get("can_project"):
            if c.get("can_project"): print(f"   projects: {', '.join(c['can_project'])}")
        if full: print(f"   units: {', '.join(c.get('can_train', []))}")

    print("\nMY UNITS")
    for u in me["units"]:
        hurt = f" hp{u['hp']}" if u["hp"] < u.get("max_hp", 100) else ""
        print(f" {u['name']}@({u['x']},{u['y']}){hurt}", end=";")
    print()

    print("\nRIVALS")
    for r in a.get("rivals", []):
        if not r.get("met"):
            print(f" ?? {r['civ']} (not met) techs {r['techs']} score {r['score']}")
            continue
        tags = [k for k in ("war", "dof", "denounced_me", "denounced_by_me") if r.get(k)]
        print(f" {r['civ']} ({r['name']}) {' '.join(t.upper() for t in tags)} | era {r['era']} techs {r['techs']} score {r['score']} "
              f"mil {r['military']} tourism {r['tourism']} influential_over {r['influential_over']} "
              f"their_infl_on_me {r['their_influence_on_me']} own_cap {r['holds_own_capital']} projects {r['projects']}")
    approach = {p["civ"]: p["dip"] for p in st["players"] if p["id"] < 22 and p["id"] != me_id}
    print(" approach guess:", approach)

    cs = [c for c in a.get("city_states", []) if c.get("met")]
    if cs:
        print("\nCITY-STATES")
        for c in sorted(cs, key=lambda c: -c["influence"]):
            print(f" {c['name']} [{c['type']}] infl {c['influence']} ally={c['ally'] or '-'}{' WAR' if c['war'] else ''}")

    # Threats: foreign military units within 5 tiles of my cities
    print("\nTHREATS (foreign military within 5 tiles)")
    war_civs = {r["civ"] for r in a.get("rivals", []) if r.get("war")}
    any_t = False
    for pid, p in P.items():
        if pid == me_id: continue
        for u in p.get("units", []):
            if is_civilian(u["name"]): continue
            for c in me.get("cities", []):
                d = dist((u["x"], u["y"]), (c["x"], c["y"]))
                if d <= 5:
                    any_t = True
                    w = "AT WAR " if p["civ"] in war_civs or pid >= 60 else ""
                    print(f" {w}{p['civ']} {u['name']}@({u['x']},{u['y']}) hp{u['hp']} -> {d} from {c['name']}")
                    break
    if not any_t: print(" none")


if __name__ == "__main__":
    main()
