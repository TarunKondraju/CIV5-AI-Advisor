"""Compact per-turn briefing from the Civ5AIBridge export (bridge v1.2+).

Usage: py turn_brief.py [--json out.json] [--full] [--map]
Keeps .advisor_cache/ with the previous turn's units to detect armies on the move.
"""
import json, os, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".advisor_cache")
if sys.platform == "darwin":
    LOG = os.path.expanduser("~/Library/Application Support/Sid Meier's Civilization 5/Logs/Lua.log")
else:
    LOG = os.path.expanduser(r"~\OneDrive\Documents\My Games\Sid Meier's Civilization 5\Logs\Lua.log")
    if not os.path.exists(LOG):
        LOG = os.path.expanduser(r"~\Documents\My Games\Sid Meier's Civilization 5\Logs\Lua.log")

WONDERS = {"Pyramids", "Stonehenge", "Great Library", "Temple of Artemis", "Hanging Gardens", "Colossus", "Oracle",
           "Great Lighthouse", "Mausoleum of Halicarnassus", "Statue of Zeus", "Terracotta Army", "Petra", "Great Wall",
           "Chichen Itza", "Machu Picchu", "Hagia Sophia", "Angkor Wat", "Alhambra", "Notre Dame", "Borobudur",
           "Great Mosque of Djenne", "Parthenon", "Himeji Castle", "Forbidden Palace", "Leaning Tower of Pisa",
           "Porcelain Tower", "Taj Mahal", "Sistine Chapel", "Kremlin", "Globe Theatre", "Uffizi", "Red Fort",
           "Louvre", "Big Ben", "Brandenburg Gate", "Neuschwanstein", "Statue of Liberty", "Eiffel Tower",
           "Broadway", "Cristo Redentor", "Prora", "Pentagon", "Sydney Opera House", "Hubble Space Telescope",
           "CN Tower", "United Nations", "Great Firewall", "Banaue Rice Terraces", "Summer Palace", "Kilwa Kisiwani"}
FOCUS = {-1: "?", 0: "default", 1: "food", 2: "production", 3: "gold", 4: "science", 5: "culture",
         6: "great people", 7: "faith"}
DIRS = ["E", "NE", "N", "NW", "W", "SW", "S", "SE"]


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


def make_geo(st):
    width = max(p["x"] for p in st["map"]) + 1 if st.get("map") else 80

    def cube(x, y):
        q = x - (y - (y & 1)) // 2
        return q, y, -q - y

    def dist(a, b):
        best = 999
        for dx in (0, width, -width):
            ax, ay, az = cube(a[0] + dx, a[1]); bx, by, bz = cube(b[0], b[1])
            best = min(best, max(abs(ax - bx), abs(ay - by), abs(az - bz)))
        return best

    def direction(frm, to):
        import math
        dx = to[0] - frm[0]
        if dx > width / 2: dx -= width
        if dx < -width / 2: dx += width
        dy = to[1] - frm[1]  # Civ y grows northwards
        ang = math.degrees(math.atan2(dy, dx)) % 360
        return DIRS[int((ang + 22.5) // 45) % 8]
    return dist, direction


def tile_value(f, p, g, s, c, fa, goal):
    w = {"growth": (3, 1.5, 0.5, 1, 1, 0.5), "production": (1.5, 3, 0.5, 1, 1, 0.5),
         "balanced": (2, 2, 0.8, 1.2, 1.2, 0.6)}[goal]
    return f * w[0] + p * w[1] + g * w[2] + s * w[3] + c * w[4] + fa * w[5]


def main():
    full = "--full" in sys.argv
    st = load_state()
    if "--json" in sys.argv:
        json.dump(st, open(sys.argv[sys.argv.index("--json") + 1], "w", encoding="utf-8"), indent=1)
    dist, direction = make_geo(st)
    me_id = st["active_player"]
    P = {p["id"]: p for p in st["players"]}
    me = P[me_id]
    a = st.get("advisor", {})
    R = {int(k): v.replace("RESOURCE_", "") for k, v in st.get("resource_dict", {}).items()}
    I = {int(k): v.replace("IMPROVEMENT_", "") for k, v in st.get("improvement_dict", {}).items()}
    my_cities = me.get("cities", [])
    cap = next(((c["x"], c["y"]) for c in a.get("cities", []) if c.get("capital")),
               (my_cities[0]["x"], my_cities[0]["y"]) if my_cities else None)
    if cap is None:
        s = [u for u in me["units"] if "Settler" in u["name"]]
        cap = (s[0]["x"], s[0]["y"]) if s else (0, 0)

    def near_city(x, y):
        if not my_cities: return None, dist((x, y), cap)
        c = min(my_cities, key=lambda c: dist((x, y), (c["x"], c["y"])))
        return c["name"], dist((x, y), (c["x"], c["y"]))

    print(f"LOG updated {datetime.datetime.fromtimestamp(os.path.getmtime(LOG)):%Y-%m-%d %H:%M}")
    print(f"TURN {st['turn']}  {me['name']} ({me['civ']})  {a.get('difficulty','')} {a.get('game_speed','')}  era={a.get('era','')}"
          f"  ideology={a.get('my_ideology') or '-'}")
    if "error" in a: print("!! ADVISOR BLOCK ERROR:", a["error"])
    if a.get("todo"): print("TODO NOW:", " | ".join(a["todo"]))
    print(f"gold {a.get('gold','?')} ({a.get('gpt', me['gold']):+}/t)  sci {me['sci']}/t  cul {me['cul']}/t "
          f"(policy {a.get('culture_stored','?')}/{a.get('next_policy_cost','?')})  happy {a.get('happiness','?')} "
          f"(+{a.get('happiness_total','?')} -{a.get('unhappiness_total','?')})  GA {a.get('golden_age_progress','?')}/{a.get('golden_age_needed','?')}"
          f"{' ACTIVE ' + str(a['golden_age_turns']) + 't' if a.get('golden_age_turns') else ''}")
    print(f"research: {a.get('research') or 'NONE'} ({a.get('research_turns','?')}t)  techs {a.get('my_techs','?')}  "
          f"military {a.get('my_military','?')}  trade {a.get('trade_routes','?')}/{a.get('trade_routes_max','?')}  tourism {a.get('tourism','?')}")
    print("techs available:", ", ".join(f"{t['n']}({t['turns']})" for t in sorted(a.get("techs_available", []), key=lambda t: t["turns"])))
    print("policies:", ", ".join(a.get("policies", [])) or "-")
    if a.get("projects"): print("projects:", a["projects"])
    if a.get("wonders"): print("my wonders:", ", ".join(a["wonders"]))
    if full: print("techs known:", ", ".join(a.get("techs_known", [])))

    # --- Religion
    print(f"\nRELIGION faith {a.get('faith','?')} (+{a.get('fpt','?')}/t)  pantheon={'yes' if a.get('has_pantheon') else 'no'}"
          f" (needs {a.get('faith_for_pantheon','?')})  religion={a.get('religion') or '-'}  prophet at {a.get('faith_for_prophet','?')}"
          f"  religions left to found: {a.get('religions_left','?')}")
    if a.get("pantheons_available") and not a.get("has_pantheon"):
        print(" pantheons open:", "; ".join(f"{b['n']}: {b['d']}" for b in a["pantheons_available"]) if full else
              ", ".join(b["n"] for b in a["pantheons_available"]))

    # --- Resources & trades
    mine = {r["n"]: r for r in a.get("my_resources", [])}
    lux_have = [n for n, r in mine.items() if r["lux"] and r["avail"] > 0]
    spare = [n for n, r in mine.items() if r["lux"] and r["avail"] >= 2]
    print(f"\nLUXURIES ({len(lux_have)}): {', '.join(lux_have) or '-'}  spare copies: {', '.join(spare) or '-'}")
    strat = [f"{n} {r['avail']}" for n, r in mine.items() if not r["lux"]]
    if strat: print("strategic:", ", ".join(strat))
    deals = []
    for r in a.get("rivals", []):
        if not r.get("met") or r.get("war"): continue
        theirs = {x["n"]: x for x in r.get("resources", [])}
        wants = [l for l in spare if theirs.get(l, {}).get("avail", 0) <= 0]
        offers = [n for n, x in theirs.items() if x["lux"] and x["avail"] >= 2 and mine.get(n, {}).get("avail", 0) <= 0]
        if wants or offers:
            deals.append(f" {r['civ']} (treasury {r.get('treasury','?')}, {r.get('gpt',0):+}/t): "
                         f"sell them {wants or '-'}; buy/swap for {offers or '-'}")
    if deals: print("TRADE OPPORTUNITIES:"); print("\n".join(deals))

    # --- Cities + citizens
    print("\nCITIES")
    for c in a.get("cities", []):
        flags = ("CAPITAL " if c.get("capital") else "") + ("PUPPET " if c.get("puppet") else "") + \
                (f"RESIST{c['resistance']} " if c.get("resistance") else "") + \
                ("NOT-CONNECTED " if c.get("connected") is False else "") + \
                (f"DAMAGED {c['hp']}/{c['maxhp']} " if c.get("hp", 1) < c.get("maxhp", 1) else "")
        print(f" {c['name']} ({c['x']},{c['y']}) pop {c['pop']} {flags}| food {c.get('food',0):+} grow {c.get('growth_turns','?')}t "
              f"prod {c.get('prod','?')} gold {c.get('gold','?')} sci {c.get('sci','?')} cul {c.get('cul','?')} faith {c.get('faith','?')} "
              f"str {c.get('strength','?')} focus {FOCUS.get(c.get('focus', -1), c.get('focus'))} religion {c.get('religion') or '-'}")
        print(f"   building: {c.get('build')} ({c.get('build_turns')}t)")
        print(f"   has: {', '.join(c.get('buildings', [])) or '-'}")
        cb = sorted(c.get("can_build", []), key=lambda b: b["turns"])
        print(f"   can build: {', '.join(f'{b['n']}({b['turns']}t/{b['buy']}g)' for b in cb)}")
        if c.get("can_project"): print(f"   projects: {', '.join(c['can_project'])}")
        if full: print(f"   units: {', '.join(c.get('can_train', []))}")
        sl = c.get("specialist_slots", [])
        if sl or c.get("unemployed"):
            print("   specialists:", ", ".join(f"{s['n']} {s['count']}/{s['slots']} (GP {s['gpp']})" for s in sl),
                  f"| UNEMPLOYED {c['unemployed']}" if c.get("unemployed") else "")
        if c.get("great_work_slots"): print(f"   great works {c.get('great_works',0)}/{c['great_work_slots']}")
        tiles = c.get("tiles", [])
        if tiles:
            goal = "growth" if c["pop"] < 8 or c.get("food", 0) <= 2 else "balanced"
            worked = [t for t in tiles if t[8]]
            free = [t for t in tiles if not t[8]]
            val = lambda t: tile_value(*t[2:8], goal)
            worked.sort(key=val); free.sort(key=val, reverse=True)
            fmt = lambda t: f"({t[0]},{t[1]}) {t[2]}f{t[3]}p{t[4]}g" + (f"{t[5]}s" if t[5] else "") + (f"{t[6]}c" if t[6] else "") + \
                (f"{t[7]}fa" if t[7] else "") + (f" {R.get(t[9], '')}" if t[9] >= 0 else "") + (f" [{I.get(t[10], '')}]" if t[10] >= 0 else "") + \
                (" PILLAGED" if t[11] else "")
            swaps = [(w, f) for w, f in zip(worked, free) if val(f) > val(w) + 1.5]
            if swaps:
                print(f"   CITIZENS ({goal}): swap " + "; ".join(f"{fmt(w)} -> {fmt(f)}" for w, f in swaps[:3]))
            if full:
                print("   worked:", "; ".join(fmt(t) for t in worked))
                print("   best free:", "; ".join(fmt(t) for t in free[:6]))

    # --- Units
    idle, promo, upg, workers_idle = [], [], [], []
    for u in me["units"]:
        if u.get("civilian") is False and not u.get("fortified") and not u.get("automated") and u.get("moves") == u.get("max_moves") and u.get("moves"):
            idle.append(f"{u['name']}@({u['x']},{u['y']})")
        if u.get("can_promote"): promo.append(u["name"])
        if u.get("can_upgrade"): upg.append(f"{u['name']}->{u['upgrade_to'].replace('UNIT_', '')} {u['upgrade_cost']}g")
        if "Worker" in u["name"] and "build" in u and not u["build"] and not u.get("automated"):
            workers_idle.append(f"({u['x']},{u['y']})")
    print("\nMY UNITS:", "; ".join(f"{u['name']}@({u['x']},{u['y']})" + (f" hp{u['hp']}" if u['hp'] < u.get('max_hp', 100) else "")
                                   for u in me["units"]))
    if idle: print(" unmoved military:", ", ".join(idle))
    if promo: print(" PROMOTION READY:", ", ".join(promo))
    if upg: print(" can upgrade:", ", ".join(upg))
    if workers_idle: print(" idle workers at:", ", ".join(workers_idle))

    # --- Unimproved resources inside borders
    if st.get("map"):
        unimproved = [f"{R.get(p['r'])}({p['x']},{p['y']})" for p in st["map"]
                      if p.get("o") == me_id and p.get("r", -1) >= 0 and p.get("i", -1) < 0 and not p.get("fog")
                      and R.get(p["r"]) not in ("ARTIFACTS", "HIDDEN_ARTIFACTS")]
        pill = [f"({p['x']},{p['y']})" for p in st["map"] if p.get("o") == me_id and p.get("pil")]
        if unimproved: print(" unimproved resources:", ", ".join(unimproved))
        if pill: print(" PILLAGED tiles:", ", ".join(pill))

    # --- Rivals
    print("\nRIVALS")
    for r in a.get("rivals", []):
        if not r.get("met"):
            print(f" ?? {r['civ']} (not met) techs {r['techs']} score {r['score']}")
            continue
        tags = [k.upper() for k in ("war", "dof", "denounced_me", "denounced_by_me", "open_borders_with_me") if r.get(k)]
        print(f" {r['civ']} {' '.join(tags)} | approach {P.get(next((pid for pid, p in P.items() if p['civ'] == r['civ']), -1), {}).get('dip', '?')} "
              f"| era {r['era']} techs {r['techs']} score {r['score']} mil {r['military']} gold {r.get('treasury','?')}({r.get('gpt',0):+}) "
              f"tourism {r['tourism']} infl_over {r['influential_over']} on_me {r['their_influence_on_me']} "
              f"rel {r.get('religion') or '-'} ideo {r.get('ideology') or '-'} own_cap {r['holds_own_capital']} proj {r['projects']}")
    if a.get("ai_wars"): print(" AI wars:", ", ".join(a["ai_wars"]))
    cg = a.get("congress", {})
    if cg.get("active"): print(f" World Congress: host {cg.get('host')}, my votes {cg.get('my_votes')}, session in {cg.get('turns_until_session')}t")

    # --- Wonder race: AI cities building wonders I could also build
    my_can = {b["n"] for c in a.get("cities", []) for b in c.get("can_build", [])}
    race = [f"{p['civ']}:{c['name']} {c['build']}" for pid, p in P.items() if pid != me_id and pid < 22
            for c in p.get("cities", []) if c.get("build") in WONDERS]
    if race:
        print(" AI building wonders:", "; ".join(race), "| contested with you:",
              ", ".join(sorted({x.split(' ', 1)[1] for x in race} & my_can)) or "none")

    # --- City-states
    cs = [c for c in a.get("city_states", []) if c.get("met")]
    if cs:
        print("\nCITY-STATES (dist/dir from capital)")
        for c in sorted(cs, key=lambda c: dist((c["x"], c["y"]), cap) if c.get("x", -1) >= 0 else 99):
            loc = f"({c['x']},{c['y']}) {dist((c['x'], c['y']), cap)} {direction(cap, (c['x'], c['y']))}" if c.get("x", -1) >= 0 else "?"
            print(f" {c['name']} [{c['type']}] {loc} infl {c['influence']} ally={c['ally'] or '-'}"
                  f"{'(' + str(c['ally_influence']) + ')' if c.get('ally_influence') else ''}"
                  f"{' WAR' if c['war'] else ''}{' PROTECTED' if c.get('protected_by_me') else ''}"
                  f"{' quests: ' + ','.join(c['quests']) if c.get('quests') else ''}"
                  f"{' bully:' + str(c['bully_gold']) + 'g' if c.get('can_bully_gold') else ''}")

    # --- Threats & army movement
    os.makedirs(CACHE, exist_ok=True)
    prev_path = os.path.join(CACHE, "units_prev.json")
    base_path = os.path.join(CACHE, "units_baseline.json")  # last seen state of an earlier turn
    prev, rotate = {}, False
    if os.path.exists(prev_path):
        pv = json.load(open(prev_path))
        if pv.get("turn", -1) < st["turn"]:
            prev, rotate = pv.get("units", {}), True
        elif os.path.exists(base_path):
            prev = json.load(open(base_path)).get("units", {})
    cur = {}
    print("\nTHREATS (foreign military within 7 tiles; d = change in distance since last turn)")
    groups = {}
    for pid, p in P.items():
        if pid == me_id: continue
        barb = pid >= 63 or p["civ"].lower().startswith("barbarian")
        for u in p.get("units", []):
            if u.get("civilian") or (u.get("civilian") is None and any(k in u["name"] for k in ("Worker", "Settler", "Great", "Caravan", "Cargo", "Missionary", "Archaeologist", "Work Boat"))):
                continue
            key = f"{pid}:{u['id']}"
            cname, d = near_city(u["x"], u["y"])
            cur[key] = [u["x"], u["y"]]
            if d > 7: continue
            delta = None
            if key in prev:
                _, d0 = near_city(*prev[key])
                delta = d - d0
            g = groups.setdefault((p["civ"] + (" (barbarian)" if barb else ""), cname), {"n": 0, "str": 0, "closest": 99, "approach": 0, "units": []})
            g["n"] += 1; g["str"] += max(u.get("str", 0), u.get("rstr", 0)); g["closest"] = min(g["closest"], d)
            if delta is not None and delta < 0: g["approach"] += 1
            g["units"].append(f"{u['name']}@({u['x']},{u['y']}){'' if delta is None else f' d{delta:+d}'}")
    war_civs = {r["civ"] for r in a.get("rivals", []) if r.get("war")}
    if not groups: print(" none")
    for (civ, cname), g in sorted(groups.items(), key=lambda kv: kv[1]["closest"]):
        level = "AT WAR" if civ.split(" ")[0] in war_civs or "barbarian" in civ else ("WATCH" if g["approach"] else "near")
        print(f" [{level}] {civ}: {g['n']} units, strength {g['str']}, closest {g['closest']} tiles from {cname}, "
              f"{g['approach']} moving closer | {', '.join(g['units'][:8])}")
    if rotate:
        os.replace(prev_path, base_path)
    json.dump({"turn": st["turn"], "units": cur}, open(prev_path, "w"))

    # --- Barbarian camps
    if st.get("map"):
        camp_id = next((k for k, v in I.items() if v == "BARBARIAN_CAMP"), None)
        camps = [(p["x"], p["y"]) for p in st["map"] if p.get("i") == camp_id and not p.get("fog")]
        if camps:
            print("\nBARBARIAN CAMPS (seen):", ", ".join(f"({x},{y}) {near_city(x, y)[1]} from {near_city(x, y)[0] or 'start'}"
                                                     for x, y in sorted(camps, key=lambda c: near_city(*c)[1])[:8]))
        fog = sum(1 for p in st["map"] if p.get("fog"))
        print(f"\nMAP: {fog}/{len(st['map'])} tiles unexplored")


if __name__ == "__main__":
    main()
