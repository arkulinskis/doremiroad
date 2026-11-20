from anvil import *

from ._anvil_designer import DayBarTemplate
from ... import state


class DayBar(DayBarTemplate):
    """One day of the weekly report: item = {day ("Mon"), date ("16 Nov"), min, pct (bar height 0-100), today, goal
    (minutes reached the homework's daily goal)}. Plain CSS bars, no chart library."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        m = int(it.get("min") or 0)
        self.col.classes.update({"today": bool(it.get("today")), "zero": m == 0, "goal": bool(it.get("goal"))})
        self.dom_nodes["mins"].textContent = str(m) if m else "–"
        self.dom_nodes["bar"].style.height = "%d%%" % max(0, min(100, int(it.get("pct") or 0)))
        self.dom_nodes["day"].textContent = it["day"]
        state.set_attr(self.col, "aria-label", "%s %s: %d minute%s" % (it["day"], it["date"], m, "" if m == 1 else "s"))
        state.set_attr(self.col, "role", "img")
