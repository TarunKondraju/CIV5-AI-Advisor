"""Always-on-top Civ 5 advisor window.

- Watches Lua.log for new turns exported by the Civ5AIBridge mod.
- Shows instant rule-based alerts every turn.
- Shows the advisor's orders from advisor_orders.json (written by Claude).
- "Ask" writes .advisor_cache/request.json so Claude can answer a question / do a full analysis.

Run Civ 5 in Windowed or Borderless mode so this window can stay on top.
"""
import json, os, subprocess, sys, threading, time, datetime
import tkinter as tk
from tkinter import ttk

import advisor_core as core
from turn_brief import LOG, load_state, HERE

BG, FG, DIM = "#1b1d22", "#e8e6e1", "#8b8f98"
COL = {"red": "#ff6b6b", "amber": "#f5b041", "info": "#7fb3ff", "ok": "#6fcf97"}
POLL_MS = 2000


class AdvisorWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Civ 5 Advisor")
        self.root.geometry("440x640+20+60")
        self.root.configure(bg=BG)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.93)
        self.log_mtime = 0
        self.orders_mtime = 0
        self.state = None
        self.alerts, self.reasons = [], []
        self.busy = False
        self._build()
        self.root.after(200, self.poll)

    # ---------- UI ----------
    def _build(self):
        f = ("Segoe UI", 10)
        top = tk.Frame(self.root, bg=BG); top.pack(fill="x", padx=8, pady=(8, 2))
        self.header = tk.Label(top, text="Waiting for Civ 5…", bg=BG, fg=FG, font=("Segoe UI Semibold", 12), anchor="w")
        self.header.pack(side="left", fill="x", expand=True)
        self.pin = tk.Button(top, text="📌", command=self.toggle_pin, bg=BG, fg=FG, bd=0, activebackground=BG)
        self.pin.pack(side="right")
        self.stats = tk.Label(self.root, text="", bg=BG, fg=DIM, font=("Segoe UI", 9), anchor="w", justify="left")
        self.stats.pack(fill="x", padx=8)
        self.status = tk.Label(self.root, text="", bg=BG, fg=COL["info"], font=("Segoe UI", 10, "bold"), anchor="w",
                               wraplength=420, justify="left")
        self.status.pack(fill="x", padx=8, pady=(4, 4))

        tk.Label(self.root, text="ALERTS", bg=BG, fg=DIM, font=("Segoe UI", 8, "bold"), anchor="w").pack(fill="x", padx=8)
        self.alert_box = tk.Text(self.root, height=8, bg="#22252b", fg=FG, font=f, wrap="word", bd=0, padx=6, pady=4)
        self.alert_box.pack(fill="x", padx=8)
        for k, v in COL.items(): self.alert_box.tag_configure(k, foreground=v)

        tk.Label(self.root, text="ORDERS", bg=BG, fg=DIM, font=("Segoe UI", 8, "bold"), anchor="w").pack(fill="x", padx=8, pady=(8, 0))
        self.orders_box = tk.Text(self.root, bg="#22252b", fg=FG, font=f, wrap="word", bd=0, padx=6, pady=4)
        self.orders_box.pack(fill="both", expand=True, padx=8)
        self.orders_box.tag_configure("h", font=("Segoe UI Semibold", 11), foreground="#ffd479")
        self.orders_box.tag_configure("dim", foreground=DIM)

        bottom = tk.Frame(self.root, bg=BG); bottom.pack(fill="x", padx=8, pady=8)
        self.q = tk.Entry(bottom, bg="#2a2d34", fg=FG, insertbackground=FG, bd=0, font=f)
        self.q.pack(side="left", fill="x", expand=True, ipady=4)
        self.q.insert(0, "Ask the advisor… (Enter)")
        self.q.bind("<FocusIn>", lambda e: self.q.delete(0, "end") if self.q.get().startswith("Ask the advisor") else None)
        self.q.bind("<Return>", lambda e: self.ask())
        tk.Button(bottom, text="Ask", command=self.ask, bg="#3b6fd8", fg="white", bd=0, padx=10).pack(side="left", padx=(6, 0))
        tk.Button(bottom, text="Full analysis", command=lambda: self.ask("Full analysis please"), bg="#444a55", fg="white",
                  bd=0, padx=8).pack(side="left", padx=(6, 0))
        self.alpha = ttk.Scale(self.root, from_=0.4, to=1.0, value=0.93, command=lambda v: self.root.attributes("-alpha", float(v)))
        self.alpha.pack(fill="x", padx=8, pady=(0, 6))

    def toggle_pin(self):
        on = not self.root.attributes("-topmost")
        self.root.attributes("-topmost", on)
        self.pin.configure(fg=FG if on else DIM)

    # ---------- data ----------
    def poll(self):
        try:
            m = os.path.getmtime(LOG) if os.path.exists(LOG) else 0
            if m != self.log_mtime and not self.busy:
                self.log_mtime = m
                self.busy = True
                threading.Thread(target=self.load, daemon=True).start()
            om = os.path.getmtime(core.ORDERS) if os.path.exists(core.ORDERS) else 0
            if om != self.orders_mtime:
                self.orders_mtime = om
                self.render()
        except Exception as e:
            self.status.configure(text=f"Error: {e}", fg=COL["red"])
        self.root.after(POLL_MS, self.poll)

    def load(self):
        try:
            st = load_state()
            if self.state is None or st["turn"] != self.state["turn"] or st.get("advisor") != self.state.get("advisor"):
                self.state = st
                self.alerts, self.reasons = core.process_turn(st)
                with open(core.BRIEF, "w", encoding="utf-8") as fh:  # full text briefing for Claude
                    subprocess.run([sys.executable, os.path.join(HERE, "turn_brief.py")], stdout=fh,
                                   stderr=subprocess.STDOUT, cwd=HERE, timeout=60)
                self.root.after(0, self.render)
        except SystemExit as e:
            self.root.after(0, lambda: self.status.configure(text=str(e), fg=COL["amber"]))
        except Exception as e:
            self.root.after(0, lambda: self.status.configure(text=f"Read error: {e}", fg=COL["red"]))
        finally:
            self.busy = False

    def ask(self, text=None):
        text = text or self.q.get().strip()
        if not text or text.startswith("Ask the advisor"): return
        os.makedirs(core.CACHE, exist_ok=True)
        json.dump({"turn": self.state["turn"] if self.state else None, "question": text,
                   "time": datetime.datetime.now().isoformat(timespec="seconds")}, open(core.REQUEST, "w"))
        self.q.delete(0, "end")
        self.status.configure(text=f"Sent to advisor: “{text}” — answer will appear below", fg=COL["info"])

    # ---------- render ----------
    def render(self):
        st = self.state
        if st:
            P = {p["id"]: p for p in st["players"]}
            me = P[st["active_player"]]; a = st.get("advisor", {})
            self.header.configure(text=f"Turn {st['turn']} · {me['civ']}")
            self.stats.configure(text=f"Gold {a.get('gold', '?')} ({a.get('gpt', me['gold']):+})   Sci {me['sci']}   Cul {me['cul']}   "
                                      f"Happy {a.get('happiness', '?')}   Faith {a.get('faith', '?')}\n"
                                      f"Research: {a.get('research') or '—'} ({a.get('research_turns', '?')}t)")
        orders = core.read_orders()
        turn = st["turn"] if st else None
        if orders and turn is not None and orders.get("turn") == turn:
            self.status.configure(text=f"✓ Orders ready for turn {turn}", fg=COL["ok"])
        elif self.reasons:
            self.status.configure(text="Advisor analysing… (" + ", ".join(self.reasons[:4]) + ")", fg=COL["amber"])
        elif st:
            self.status.configure(text="Quick turn — nothing major changed. Clear the alerts and end turn.", fg=COL["info"])

        self.alert_box.configure(state="normal"); self.alert_box.delete("1.0", "end")
        if not self.alerts: self.alert_box.insert("end", "No alerts.\n", "ok")
        icon = {"red": "● ", "amber": "▲ ", "info": "• "}
        for lvl, txt in self.alerts:
            self.alert_box.insert("end", icon.get(lvl, "• ") + txt + "\n", lvl)
        self.alert_box.configure(state="disabled")

        self.orders_box.configure(state="normal"); self.orders_box.delete("1.0", "end")
        if orders:
            if turn is not None and orders.get("turn") != turn:
                self.orders_box.insert("end", f"(from turn {orders.get('turn')} — still useful until updated)\n", "dim")
            for line in orders.get("text", "").splitlines():
                if line.startswith("#"):
                    self.orders_box.insert("end", line.lstrip("# ") + "\n", "h")
                else:
                    self.orders_box.insert("end", line + "\n")
        else:
            self.orders_box.insert("end", "No orders yet. Start your game; the advisor will write orders here.", "dim")
        self.orders_box.configure(state="disabled")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    AdvisorWindow().run()
