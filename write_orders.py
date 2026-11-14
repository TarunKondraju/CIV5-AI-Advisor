"""Write the advisor's orders for the window. Reads the order text from stdin.

Usage: py write_orders.py <turn> < orders.txt     (lines starting with '#' render as headings)
Also clears a pending Ask request once it's answered.
"""
import json, os, sys, datetime
import advisor_core as core

turn = int(sys.argv[1])
text = sys.stdin.read().strip()
tmp = core.ORDERS + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump({"turn": turn, "text": text, "time": datetime.datetime.now().isoformat(timespec="seconds")}, f, ensure_ascii=False)
os.replace(tmp, core.ORDERS)  # atomic so the window never reads half a file
if os.path.exists(core.REQUEST):
    os.replace(core.REQUEST, os.path.join(core.CACHE, "request_answered.json"))
if os.path.exists(core.PENDING):
    p = json.load(open(core.PENDING)); p["answered_turn"] = turn
    json.dump(p, open(core.PENDING, "w"), indent=1)
print(f"orders written for turn {turn} ({len(text)} chars)")
