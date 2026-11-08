from anvil import *

from ._anvil_designer import MapTemplate
from ... import dr, game, router


class Map(MapTemplate):
    """#map (Operate): the knowledge map (Components/KnowledgeMap), Daily Practice, and the chosen territory with its
    levels. A level opens Dialogs/LevelCard; Play goes to #play/<level key> (#play/daily for the daily practice)."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        self.levels_panel.add_event_handler("x-level", self._level)
        self._draw()

    def _draw(self):
        ok = game.ensure()
        self.wrap.visible = ok
        self.failed_box.visible = not ok
        if not ok:
            return
        S = game.S
        cur = game.current_terr()
        if not S["sel"] or not game.find_terr(S["sel"]):
            S["sel"] = cur["key"] if cur else None
        cleared = {k: v.get("stars", 0) for k, v in (S["progress"]["levels"] or {}).items()}
        st = S["status"]
        self.map_view.draw(S["journey"], {"cleared": cleared, "unlocked": st["unlocked"], "conquered": st["conquered"],
                                          "mastered": st["mastered"], "banner": game.banner_colour(),
                                          "current": cur["key"] if cur else None, "selected": S["sel"]})
        self._daily()
        self._terr()
        self.victory.visible = bool(st["territories_max"]) and len(st["conquered"]) == st["territories_max"]

    def _daily(self):
        d = game.S["daily"]
        self.daily_icon.text = "✅" if d["done"] else "📜"
        if d["done"]:
            self.daily_text.text = "Done for today. Come back tomorrow" + (" to make it %d days." % (d["streak"] + 1) if d["streak"] else ".")
        else:
            self.daily_text.text = ("🔥 %d-day streak. Keep it alive!" % d["streak"]) if d["streak"] else "A fresh warm-up every day. Build a streak."
        self.daily_button.text = "Replay" if d["done"] else "Start"
        self.daily_button.role = ["btn", "btn-sm"] if d["done"] else ["btn", "btn-primary", "btn-sm"]

    def _terr(self):
        t = game.find_terr(game.S["sel"])
        if t is None:
            return
        state_ = game.terr_state(t)
        lv = t["levels"]
        done = len([l for l in lv if game.rec(l["key"])["stars"]])
        star_n = sum(game.rec(l["key"])["stars"] for l in lv)
        self.crest.content = dr.art_crest(t, state_, 54)
        self.terr_name.text = t["name"]
        self.terr_blurb.text = t["blurb"]
        self.prog_text.text = "%d / %d provinces" % (done, len(lv))
        self.prog_bar.style["width"] = "%d%%" % (int(100 * done / len(lv)) if lv else 0)
        self.prog_bar.style["background"] = game.banner_colour()
        self.prog_stars.text = "★ %d/%d" % (star_n, 3 * len(lv))
        self.terr_note.visible = state_ in ("conquered", "mastered")
        self.terr_note.text = ("🏆 Mastered: three stars on every level." if state_ == "mastered"
                               else "🚩 Conquered. Three-star every level to master it.")
        banner = game.banner_colour()
        rows = []
        for i, l in enumerate(lv):
            r = game.rec(l["key"])
            rows.append({"key": l["key"], "name": l["name"], "i": i, "stars": r["stars"], "best": r["best"],
                         "open": game.unlocked(l["key"]), "trial": bool(l["data"].get("trial")), "banner": banner,
                         "icons": game.step_icons(l["data"])})
        self.levels_panel.items = rows
        idx = game.S["journey"].index(t)
        prev = game.S["journey"][idx - 1] if idx > 0 else None
        self.lock_note.visible = state_ == "locked"
        self.lock_note.text = "🔒 Conquer %s to open this land." % (prev["name"] if prev else "the territory before")

    @handle("map_view", "pick")
    def map_view_pick(self, key, **event_args):
        if not game.find_terr(key):
            return
        dr.sfx("page")
        game.S["sel"] = key
        self.map_view.select(key)
        self._terr()

    def _level(self, key, **event_args):
        dr.sfx("click")
        from ...Dialogs.LevelCard import LevelCard
        if alert(LevelCard(key=key), buttons=[], large=True, role="app-dialog", dismissible=True) == "play":
            router.go("play", key)

    @handle("daily_button", "click")
    def daily_button_click(self, **event_args):
        dr.sfx("click")
        from ...Dialogs.DailyCard import DailyCard
        if alert(DailyCard(), buttons=[], role="app-dialog", dismissible=True) == "play":
            router.go("play", "daily")

    @handle("retry_button", "click")
    def retry_button_click(self, **event_args):
        self._draw()
        router.refresh_shell()

    @handle("", "show")
    def form_show(self, **event_args):
        dr.ambient(True)
