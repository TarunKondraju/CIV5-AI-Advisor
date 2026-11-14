"""Recommend city sites from the live Civ5AIBridge export.

Scores every legal land plot for: luxuries (new types weighted most), food tiles, production,
fresh water, coast, mountains (Observatory), defensibility, distance to your own cities,
and diplomatic risk from settling near AI civs / city-states. Then picks a non-overlapping
plan of N cities.

Usage: py city_sites.py [--n 5] [--from X,Y] [--top 15] [--json out.json]
  --from X,Y   origin when you have no city yet (e.g. your settler's tile)
"""
import json, sys
from turn_brief import load_state

GRASS, PLAINS, DESERT, TUNDRA, SNOW, COAST, OCEAN = range(7)
BONUS_FOOD = {"WHEAT", "COW", "SHEEP", "DEER", "BANANA", "FISH", "BISON", "CRAB"}
STRATEGIC = {"IRON", "HORSE", "COAL", "OIL", "ALUMINUM", "URANIUM"}
LUXURY = {"WHALE", "PEARLS", "GOLD", "SILVER", "GEMS", "MARBLE", "IVORY", "FUR", "DYE", "SPICES",
          "SILK", "SUGAR", "COTTON", "WINE", "INCENSE", "COPPER", "SALT", "CRAB_X", "TRUFFLES",
          "CITRUS", "NUTMEG", "CLOVES", "PEPPER", "COCOA", "JEWELRY", "PORCELAIN"}
NATURAL_WONDERS = {"FUJI", "GIBRALTAR", "GEYSER", "FOUNTAIN_YOUTH", "POTOSI", "EL_DORADO", "SRI_PADA",
                   "MT_SINAI", "MT_KAILASH", "ULURU", "LAKE_VICTORIA", "KILIMANJARO", "SOLOMONS_MINES",
                   "CRATER", "MESA", "VOLCANO"}


def cube(x, y):
    q = x - (y - (y & 1)) // 2
    return q, y, -q - y


def hexdist(a, b, width):
    best = 99
    for dx in (0, width, -width):  # map wraps horizontally
        ax, ay, az = cube(a[0] + dx, a[1]); bx, by, bz = cube(b[0], b[1])
        best = min(best, max(abs(ax - bx), abs(ay - by), abs(az - bz)))
    return best


def tile_yield(p, R, F):
    """Rough (food, prod, gold) of a tile once improved early-game."""
    t, feat = p["t"], F.get(p.get("f"), "")
    res = R.get(p.get("r"), "")
    if p.get("m"): return (0, 0, 0)
    if feat == "ICE": return (0, 0, 0)
    fresh = p.get("rw") or p.get("rnw") or p.get("rne")
    food, prod, gold = {GRASS: (2, 0, 0), PLAINS: (1, 1, 0), DESERT: (0, 0, 0), TUNDRA: (1, 0, 0),
                        SNOW: (0, 0, 0), COAST: (1, 0, 1), OCEAN: (1, 0, 1)}[t]
    if p.get("h"): food, prod = 0, 2 + 1  # hill + mine
    elif t in (GRASS, PLAINS) and not feat: food += 1  # farm
    if feat == "FOREST": food, prod = 1, 2  # forest (+lumbermill later)
    elif feat == "JUNGLE": food, prod, gold = 2, 0, 1  # jungle trading post / science later
    elif feat == "MARSH": food = max(0, food - 1)
    elif feat == "OASIS": food, gold = 3, 1
    elif feat == "FLOOD_PLAINS": food = 3
    elif feat in ("ATOLL", "REEF"): food, prod = food + 1, prod + 1
    if fresh: gold += 1
    if res in BONUS_FOOD: food += 2
    elif res == "STONE": prod += 1
    elif res in STRATEGIC: prod += 1
    elif res in LUXURY: gold += 2
    if t == OCEAN: food -= 0.5  # weaker until harbour
    return (food, prod, gold)


def main():
    args = sys.argv
    n_pick = int(args[args.index("--n") + 1]) if "--n" in args else 5
    top = int(args[args.index("--top") + 1]) if "--top" in args else 15
    st = load_state()
    R = {int(k): v.replace("RESOURCE_", "") for k, v in st["resource_dict"].items()}
    F = {int(k): v.replace("FEATURE_", "") for k, v in st["feature_dict"].items()}
    width = max(p["x"] for p in st["map"]) + 1
    plots = {(p["x"], p["y"]): p for p in st["map"]}
    me = st["active_player"]
    P = {p["id"]: p for p in st["players"]}
    my_cities = [(c["x"], c["y"]) for c in P[me]["cities"]]
    ai_cities = [((c["x"], c["y"]), p["civ"]) for pid, p in P.items() if pid != me and pid < 22 for c in p["cities"]]
    cs_cities = [((c["x"], c["y"]), p["civ"]) for pid, p in P.items() if 22 <= pid < 63 for c in p["cities"]]
    all_cities = my_cities + [c for c, _ in ai_cities + cs_cities]
    if "--from" in args:
        origin = tuple(int(v) for v in args[args.index("--from") + 1].split(","))
    elif my_cities:
        origin = my_cities[0]
    else:
        settlers = [(u["x"], u["y"]) for u in P[me]["units"] if "Settler" in u["name"]]
        origin = settlers[0] if settlers else None
    owned_lux = {R.get(p.get("r")) for p in st["map"] if p.get("o") == me and R.get(p.get("r")) in LUXURY}

    def ring(c, rad):
        x0, y0 = c
        for dy in range(-rad, rad + 1):
            for dx in range(-rad - 1, rad + 2):
                q = ((x0 + dx) % width, y0 + dy)
                if q in plots:
                    d = hexdist(c, q, width)
                    if 0 < d <= rad: yield plots[q], d

    def score(c, taken_lux, planned):
        p = plots[c]
        if p["t"] in (COAST, OCEAN, SNOW) or p.get("m") or F.get(p.get("f")) in ("ICE", *NATURAL_WONDERS): return None
        if p.get("o", -1) not in (-1, me): return None  # inside someone else's borders
        if any(hexdist(c, o, width) < 4 for o in all_cities + planned): return None
        food_tiles = sum(1 for q, d in ring(c, 2) if tile_yield(q, R, F)[0] >= 2 and not q.get("m"))
        if food_tiles < 2: return None
        yld, lux, lux_new, nw, mtn_adj, coast, water_adj, hills_r1 = 0, set(), set(), [], 0, False, 0, 0
        for q, d in ring(c, 3):
            if q.get("o", -1) not in (-1, me): continue
            near_other = any(hexdist((q["x"], q["y"]), o, width) <= 3 for o in all_cities + planned)
            w = (1.0 if d <= 2 else 0.5) * (0.3 if near_other else 1.0)
            f_, pr, g = tile_yield(q, R, F)
            yld += w * (1.3 * f_ + 1.0 * pr + 0.4 * g)
            res = R.get(q.get("r"))
            if res in LUXURY and not near_other:
                lux.add(res)
                if res not in owned_lux and res not in taken_lux: lux_new.add(res)
            if F.get(q.get("f")) in NATURAL_WONDERS: nw.append(F[q["f"]])
            if d == 1:
                if q.get("m"): mtn_adj += 1
                if q["t"] == COAST: coast = True
                if q["t"] in (COAST, OCEAN): water_adj += 1
                if q.get("h"): hills_r1 += 1
        fresh = bool(p.get("rw") or p.get("rnw") or p.get("rne")) or any(
            (q.get("rw") or q.get("rnw") or q.get("rne")) for q, d in ring(c, 1))
        s = yld + 14 * len(lux_new) + 3 * (len(lux) - len(lux_new)) + 4 * len(nw)
        s += 5 * bool(p.get("h")) + 4 * fresh + 3 * coast + 4 * min(mtn_adj, 1)
        defence = 2 * bool(p.get("h")) + mtn_adj + 0.5 * water_adj + 0.5 * hills_r1
        # distance from my empire
        d_me = min((hexdist(c, o, width) for o in my_cities + planned), default=None)
        d_cap = hexdist(c, origin, width) if origin else None
        if d_me is not None and d_me > 7: s -= 3 * (d_me - 7)
        if d_cap is not None and d_cap > 10: s -= 2 * (d_cap - 10)
        # diplomatic risk
        near_ai = min(((hexdist(c, o, width), civ) for o, civ in ai_cities), default=(99, ""))
        near_cs = min(((hexdist(c, o, width), civ) for o, civ in cs_cities), default=(99, ""))
        risk = "low"
        if near_ai[0] <= 5: risk = "HIGH"
        elif near_ai[0] <= 7: risk = "medium"
        if near_cs[0] <= 4 and risk == "low": risk = "medium (city-state tiles)"
        forward = near_ai[0] < 99 and d_cap is not None and near_ai[0] < d_cap
        if risk == "HIGH": s -= 6 - min(defence, 4)  # defensible forward settles are penalised less
        return dict(x=c[0], y=c[1], score=round(s, 1), lux=sorted(lux), new_lux=sorted(lux_new),
                    food_tiles=food_tiles, hill=bool(p.get("h")), fresh_water=fresh, coastal=coast,
                    mountain_adj=mtn_adj, defence=round(defence, 1), natural_wonders=nw,
                    dist_from_me=d_me, dist_from_capital=d_cap,
                    nearest_ai=f"{near_ai[1]} {near_ai[0]}" if near_ai[1] else "-",
                    nearest_cs=f"{near_cs[1]} {near_cs[0]}" if near_cs[1] else "-",
                    risk=risk, forward_settle=forward)

    def ranked(taken, planned, limit_from=None):
        out = []
        for c in plots:
            if limit_from and hexdist(c, limit_from, width) > 12: continue
            r = score(c, taken, planned)
            if r: out.append(r)
        return sorted(out, key=lambda r: -r["score"])

    ref = origin
    cand = ranked(set(), [], ref)
    print(f"Turn {st['turn']} | origin {origin} | luxuries you own: {sorted(x for x in owned_lux if x) or 'none'}")
    print(f"\nTOP {top} SITES within 12 tiles (score | x,y | luxuries [NEW] | food tiles | features | risk)")
    for r in cand[:top]:
        feats = [k for k in ("hill", "fresh_water", "coastal") if r[k]] + (["mountain"] if r["mountain_adj"] else []) + r["natural_wonders"]
        print(f" {r['score']:6} | {r['x']},{r['y']} | {', '.join(r['lux']) or '-'} [{', '.join(r['new_lux']) or '-'}] | "
              f"food {r['food_tiles']} | {' '.join(feats)} | def {r['defence']} | from you {r['dist_from_me']} | "
              f"AI {r['nearest_ai']} CS {r['nearest_cs']} | risk {r['risk']}{' FORWARD' if r['forward_settle'] else ''}")

    # greedy plan
    plan, taken = [], set()
    for i in range(n_pick - len(my_cities)):
        options = ranked(taken, [(p["x"], p["y"]) for p in plan], ref)
        if not options: break
        best = options[0]
        plan.append(best); taken |= set(best["new_lux"])
    print(f"\nPLAN for {n_pick} cities (you have {len(my_cities)}):")
    for i, r in enumerate(plan, 1):
        print(f" #{i} settle ({r['x']},{r['y']}) score {r['score']} new luxuries {r['new_lux'] or '-'} risk {r['risk']}"
              f"{' (forward settle, defence ' + str(r['defence']) + ')' if r['forward_settle'] else ''}")
    if "--json" in args:
        json.dump({"top": cand[:top], "plan": plan}, open(args[args.index("--json") + 1], "w"), indent=1)


if __name__ == "__main__":
    main()
