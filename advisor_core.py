"""Instant rule-based alerts and turn-change triggers for the advisor window.

The window shows these immediately each turn. When a trigger fires (something important changed),
it writes .advisor_cache/pending.json so Claude can do a full analysis and write advisor_orders.json.
"""
import json, os
from turn_brief import load_state, make_geo, CACHE, HERE

ORDERS = os.path.join(HERE, "advisor_orders.json")
PENDING = os.path.join(CACHE, "pending.json")
REQUEST = os.path.join(CACHE, "request.json")
SUMMARY = os.path.join(CACHE, "summary_prev.json")
BRIEF = os.path.join(CACHE, "latest_brief.txt")


def me_and_adv(st):
    P = {p["id"]: p for p in st["players"]}
    return P, P[st["active_player"]], st.get("advisor", {})


def summarize(st):
    """Small fingerprint of the things that should trigger a full analysis when they change."""
    P, me, a = me_and_adv(st)
    return {
        "turn": st["turn"],
        "cities": sorted(c["name"] for c in me.get("cities", [])),
        "pops": {c["name"]: c["pop"] for c in me.get("cities", [])},
        "buildings": sum(len(c.get("buildings", [])) for c in a.get("cities", [])),
        "builds": {c["name"]: c.get("build") for c in a.get("cities", [])},
        "techs": a.get("my_techs", 0),
        "policies": len(a.get("policies", [])),
        "wars": sorted(r["civ"] for r in a.get("rivals", []) if r.get("war")),
        "denounced": sorted(r["civ"] for r in a.get("rivals", []) if r.get("denounced_me")),
        "dof": sorted(r["civ"] for r in a.get("rivals", []) if r.get("dof")),
        "met": sorted(r["civ"] for r in a.get("rivals", []) if r.get("met")),
        "cs_met": sorted(c["name"] for c in a.get("city_states", []) if c.get("met")),
        "great_people": sorted(u["name"] for u in me.get("units", []) if "Great" in u["name"] or "(" in u["name"]),
        "units": len(me.get("units", [])),
        "pantheon": a.get("has_pantheon"),
        "religion": a.get("religion"),
        "approach": {p["civ"]: p["dip"] for pid, p in P.items() if pid < 22 and pid != st["active_player"]},
        "era": a.get("era"),
    }


def quick_alerts(st):
    """Rule-based alerts (instant, no AI needed). Returns list of (level, text); level: 'red'|'amber'|'info'."""
    P, me, a = me_and_adv(st)
    dist, direction = make_geo(st)
    out = []
    for t in a.get("todo", []):
        out.append(("red", t))
    if a.get("happiness", 0) < 0:
        out.append(("red", f"Unhappy empire ({a['happiness']}): stop growing/settling, get a luxury or happiness building"))
    if a.get("gpt", 0) < 0:
        out.append(("red", f"Losing gold ({a['gpt']}/turn): sell a spare luxury, cut a unit, or work a gold tile"))
    for c in a.get("cities", []):
        if c.get("food", 0) < 0:
            out.append(("red", f"{c['name']} is STARVING ({c['food']} food) - move a citizen to a food tile"))
        if c.get("unemployed"):
            out.append(("amber", f"{c['name']}: {c['unemployed']} unemployed citizen(s) - assign to a tile or specialist"))
        if c.get("hp", 1) < c.get("maxhp", 1):
            out.append(("red", f"{c['name']} damaged {c['hp']}/{c['maxhp']}"))
        if c.get("resistance"):
            out.append(("info", f"{c['name']} in resistance {c['resistance']} turns"))
        if c.get("connected") is False and not c.get("capital"):
            out.append(("info", f"{c['name']} not connected to capital (no trade-route gold) - build a road"))
    # threats
    my_cities = me.get("cities", [])
    war = {r["civ"] for r in a.get("rivals", []) if r.get("war")}
    hostile = {p["civ"] for pid, p in P.items() if pid < 22 and p.get("dip", "").startswith(("Hostile", "Deceptive"))}
    if my_cities:
        for pid, p in P.items():
            if pid == st["active_player"]: continue
            barb = pid >= 63
            near = []
            for u in p.get("units", []):
                if u.get("civilian") is not False: continue
                d = min(dist((u["x"], u["y"]), (c["x"], c["y"])) for c in my_cities)
                if d <= (4 if barb else 6): near.append(u)
            if not near: continue
            if barb or p["civ"] in war:
                out.append(("red", f"{'Barbarians' if barb else p['civ']} (at war): {len(near)} units within 6 tiles"))
            elif p["civ"] in hostile and len(near) >= 3:
                out.append(("red", f"{p['civ']} is {p['dip']} and has {len(near)} military units near you - prepare defence"))
            elif len(near) >= 4 and pid < 22:
                out.append(("amber", f"{p['civ']} has {len(near)} military units near your cities"))
    for r in a.get("rivals", []):
        if r.get("denounced_me"): out.append(("amber", f"{r['civ']} has denounced you"))
    # unit chores
    workers = [u for u in me.get("units", []) if "Worker" in u["name"] and "build" in u and not u["build"] and not u.get("automated")]
    if workers: out.append(("amber", f"{len(workers)} idle worker(s)"))
    promo = [u["name"] for u in me.get("units", []) if u.get("can_promote")]
    if promo: out.append(("info", "Promotion ready: " + ", ".join(promo)))
    # opportunities
    for c in a.get("city_states", []):
        if c.get("met") and c.get("quests") and not c.get("war"):
            out.append(("info", f"{c['name']} quest: {', '.join(c['quests'])}"))
    if a.get("pantheons_available") and not a.get("has_pantheon") and a.get("faith", 0) >= a.get("faith_for_pantheon", 10**9):
        out.append(("red", "Pantheon available now"))
    cg = a.get("congress", {})
    if cg.get("active") and cg.get("turns_until_session", 99) <= 2:
        out.append(("amber", f"World Congress votes in {cg['turns_until_session']} turn(s)"))
    return out


def triggers(prev, cur):
    """Reasons why this turn needs a full analysis (empty list = quick turn)."""
    if not prev: return ["first turn seen"]
    r = []
    if cur["turn"] - prev["turn"] > 1: r.append(f"skipped {cur['turn'] - prev['turn'] - 1} turns")
    for k, label in [("cities", "city founded/lost"), ("techs", "tech finished"), ("policies", "policy adopted"),
                     ("wars", "war status changed"), ("denounced", "denunciation"), ("dof", "friendship changed"),
                     ("met", "met a new civ"), ("cs_met", "met a city-state"), ("great_people", "great person change"),
                     ("pantheon", "pantheon founded"), ("religion", "religion founded"), ("era", "new era"),
                     ("buildings", "building finished")]:
        if prev.get(k) != cur.get(k): r.append(label)
    if any(cur["pops"].get(c, 0) > p for c, p in prev.get("pops", {}).items()): r.append("city grew")
    for civ, ap in cur.get("approach", {}).items():
        if prev.get("approach", {}).get(civ) != ap and ap.startswith(("Hostile", "Deceptive", "Guarded")):
            r.append(f"{civ} now {ap}")
    return r


def process_turn(st, force=False):
    """Called by the window when a new export appears. Returns (alerts, reasons)."""
    os.makedirs(CACHE, exist_ok=True)
    prev = json.load(open(SUMMARY)) if os.path.exists(SUMMARY) else None
    cur = summarize(st)
    if prev and prev.get("turn") == cur["turn"] and not force:
        reasons = json.load(open(PENDING)).get("reasons", []) if os.path.exists(PENDING) else []
    else:
        reasons = triggers(prev, cur)
        alerts = quick_alerts(st)
        if any(lvl == "red" for lvl, _ in alerts): reasons.append("red alert")
        json.dump(cur, open(SUMMARY, "w"))
        json.dump({"turn": cur["turn"], "reasons": reasons, "full": bool(reasons),
                   "alerts": alerts}, open(PENDING, "w"), indent=1)
    return quick_alerts(st), reasons


def read_orders():
    if not os.path.exists(ORDERS): return None
    try:
        return json.load(open(ORDERS, encoding="utf-8"))
    except Exception:
        return None
