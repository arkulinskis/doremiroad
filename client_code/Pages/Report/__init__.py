from anvil import *
from anvil.js import window

from ._anvil_designer import ReportTemplate
from ... import dr, game, homework, router, state


def _loose(x):
    return x


class Report(ReportTemplate):
    """#report (Operate): this player's last 7 days from the practice log, homework ticks, what was cleared; "Send to my
    teacher" shares it as a link and Print gives one page with a line for a parent's initials.
    #r/<code> (Read): the same report from a link, read-only, for the teacher. Nothing is written to any table."""

    def __init__(self, args=(), page="report", **properties):
        super().__init__(**properties)
        state.heading(self.title_label, 1)
        state.live(self.share_label)
        self._mine = page == "report"
        self._data = _loose(None)
        self.share_label.visible = False
        ok = game.ensure()
        if self._mine:
            self._data = homework.my_report(dr.today()) if ok else None
        else:
            self._data = homework.parse_report(args[0] if args else "")
        broken = self._data is None
        self.broken_box.visible = broken
        self.sheet.visible = not broken
        self.actions.visible = not broken
        if broken:
            if self._mine:
                self.broken_box.visible = False
                self.sheet.visible = True
                self.range_label.text = "Your week couldn't load. Check your connection and try again."
            return
        self._draw()

    def _draw(self):
        d = self._data
        end = d["e"]
        start = homework.add_days(end, -6)
        self.title_label.text = "My practice week" if self._mine else "Practice report"
        self.range_label.text = "%s to %s" % (homework.nice_date(start), homework.nice_date(end))
        goal = (d.get("h") or {}).get("g") or [0, 0, 0]
        top = max([30] + d["m"])
        days = []
        for i, m in enumerate(d["m"]):
            day = homework.add_days(start, i)
            days.append({"day": homework.DAY_NAMES[homework.to_date(day).weekday()], "date": homework.nice_date(day, False),
                         "min": m, "pct": int(100 * m / top), "today": i == 6 and self._mine,
                         "goal": bool(goal[0]) and m >= goal[0]})
        self.days_panel.items = days
        total = sum(d["m"])
        active = len([m for m in d["m"] if m > 0])
        self.total_label.text = "%d min on %d day%s" % (total, active, "" if active == 1 else "s")
        self.empty_label.visible = total == 0
        levels = len([c for c in d["c"] if c.startswith("l:")])
        songs = len([c for c in d["c"] if c.startswith("s:")])
        self.stats_panel.items = [
            {"label": "Minutes played", "value": str(total)},
            {"label": "Days with practice", "value": "%d of 7" % active},
            {"label": "Runs", "value": dr.fmt(d["r"])},
            {"label": "Levels cleared", "value": str(levels)},
            {"label": "Songs cleared", "value": str(songs)},
            {"label": "Daily streak", "value": "🔥 %d" % d["k"] if d["k"] else "0"},
            {"label": "Stars on the road", "value": "★ %d" % d["s"]},
            {"label": "Current territory", "value": d["t"] or "–"},
        ]
        h = d.get("h")
        self.hw_box.visible = bool(h)
        if h:
            rows = []
            for i, x in enumerate(h["x"]):
                title, sub = homework.task_label(x[0])
                rows.append({"i": i, "task": x[0], "title": title, "sub": sub, "done": bool(x[1]), "view": "report"})
            g = h.get("g") or [0, 0, 0]
            if g[0] and g[1]:
                rows.append({"i": len(rows), "task": "", "title": "Practise %d minutes on %d days" % (g[0], g[1]),
                             "sub": "%d of %d days" % (min(g[2], g[1]), g[1]), "done": g[2] >= g[1], "view": "report"})
            self.hw_panel.items = rows
            done = len([r for r in rows if r["done"]])
            self.hw_label.text = "From %s%s · %d of %d done" % (h["t"] or "the teacher",
                                                                (", due " + homework.nice_date(h["d"])) if h.get("d") else "",
                                                                done, len(rows))
        lines = homework.cleared_lines(d["c"])
        self.cleared_box.visible = bool(lines)
        self.cleared_panel.items = lines
        self.send_button.visible = self._mine
        self.dom_nodes["hw_link"].style.display = "" if self._mine and homework.stored() else "none"
        self.dom_nodes["teacher_link"].style.display = "none" if self._mine else ""
        self.note_label.text = ("Counted by the game as you play: finished, failed and quit runs, and Practice Room "
                                "playing. It stays in this browser until you send it." if self._mine else
                                "Sent from Doremi Road. This report travels inside its link: nothing about the student "
                                "is saved on Doremi Road's server.")

    def _link(self):
        code = dr.b64e(self._data)
        return str(window.location.href).split("#")[0] + "#r/" + code

    @handle("send_button", "click")
    def send_button_click(self, **event_args):
        url = self._link()
        total = sum(self._data["m"])
        text = "My Doremi Road practice this week: %d minutes." % total
        if getattr(window.navigator, "share", None):
            try:
                window.navigator.share({"title": "My practice week", "text": text, "url": url})
                return
            except Exception as e:
                if "Abort" in type(e).__name__ + str(e):
                    return
        try:
            window.navigator.clipboard.writeText(url)
            self.share_label.text = "Link copied. Paste it in a message to your teacher."
        except Exception:
            self.share_label.text = "Copy this link and send it to your teacher: " + url
        self.share_label.visible = True

    @handle("print_button", "click")
    def print_button_click(self, **event_args):
        window.print()

    @handle("", "show")
    def form_show(self, **event_args):
        dr.ambient(False)
