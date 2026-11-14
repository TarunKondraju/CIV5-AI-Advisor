"""Prints one line per event that needs Claude's attention (for a streaming monitor):
  FULL <turn> <reasons>   - a turn needs a full analysis (and orders aren't written yet)
  ASK <turn> <question>   - the player pressed Ask in the advisor window
Runs until killed. The advisor window must be running (it writes pending.json).
"""
import json, os, sys, time
import advisor_core as core

seen_pending, seen_request = None, None
while True:
    try:
        if os.path.exists(core.PENDING):
            p = json.load(open(core.PENDING))
            key = (p.get("turn"), tuple(p.get("reasons", [])))
            if key != seen_pending:
                seen_pending = key
                if p.get("full") and p.get("answered_turn") != p.get("turn"):
                    print(f"FULL {p['turn']} {', '.join(p.get('reasons', []))}", flush=True)
        if os.path.exists(core.REQUEST):
            r = json.load(open(core.REQUEST))
            key = r.get("time")
            if key != seen_request:
                seen_request = key
                print(f"ASK {r.get('turn')} {r.get('question')}", flush=True)
    except (json.JSONDecodeError, OSError):
        pass  # file mid-write; try again
    time.sleep(1.5)
