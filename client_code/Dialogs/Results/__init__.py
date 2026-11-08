from anvil import *
from anvil.js import window

from ._anvil_designer import ResultsTemplate
from ... import dr, game, state


class Results(ResultsTemplate):
    """After a cleared level: stars (they light up one by one), accuracy, score, what was won (XP, ducats, codex
    pages, composer cards, badges, rank, conquest). A codex page or card opens its own dialog. Closes with "next",
    "again" or "map"; next_key / next_terr / map_terr tell the Play page where to go."""

    def __init__(self, report=None, key=None, name="", **properties):
        super().__init__(**properties)
        rep = report or {}
        self._rep = rep
        C, S = game.C, game.S
        self.title_label.text = name
        state.heading(self.title_label, 2)
        x = game.find_level(key) if key else None
        self.where_label.text = "Daily Practice" if key is None else (x["t"]["name"] if x else "")
        self.stars_sr.text = "%d of 3 stars" % rep.get("stars", 0)
        self.acc_label.text = "%d%%" % round(rep.get("accuracy") or 0)
        self.acc_note.text = "accuracy" + (" · new best" if rep.get("new_best") else "")
        self.score_label.text = dr.fmt(rep.get("score"))
        self.combo_box.visible = bool(rep.get("combo"))
        self.combo_label.text = str(rep.get("combo") or "")
        self.claimed_box.visible = bool(rep.get("first_clear"))

        gains: list = []
        if rep.get("repeat"):
            gains.append({"icon": "🔁", "title": "Practice run", "text": "Today's rewards are already yours. Come back tomorrow."})
        if rep.get("xp"):
            gains.append({"icon": "✨", "title": "+%d XP" % rep["xp"], "text": " · ".join("%s %s" % (a, b) for a, b in rep.get("xp_parts") or [])})
        if rep.get("ducats"):
            gains.append({"icon": "🪙", "title": "+%d ducats" % rep["ducats"], "text": " · ".join("%s %s" % (a, b) for a, b in rep.get("ducat_parts") or [])})
        if rep.get("streak"):
            gains.append({"icon": "🔥", "title": "%d-day streak" % rep["streak"],
                          "text": "Consistency is how pianists are made." if rep["streak"] > 1 else "Day one. Come back tomorrow for day two."})
        for k in rep.get("codex") or []:
            c = C["codex"].get(k)
            if c:
                gains.append({"icon": "📖", "title": "New Codex page: " + c["title"], "text": "Tap to read it", "open": "codex:" + k, "gold": True})
        for k in rep.get("cards") or []:
            c = C["composers"].get(k)
            if c:
                gains.append({"icon": "🃏", "title": "Composer card: " + c["name"],
                              "text": S["catalog"]["rarity"][c["rarity"]]["name"] + " · tap to view", "open": "card:" + k, "gold": True})
        for dd in rep.get("dupes") or []:
            c = C["composers"].get(dd["card"])
            if c:
                gains.append({"icon": "🃏", "title": "Duplicate " + c["name"], "text": "Sold for %d ducats" % dd["ducats"]})
        for k in rep.get("new_badges") or []:
            b = C["badges"].get(k)
            if b:
                gains.append({"icon": b["emoji"], "title": "Badge: " + b["name"], "text": b["desc"], "gold": True})
        if rep.get("rank_up"):
            gains.append({"icon": "🎖️", "title": "New rank: " + rep["rank_up"], "text": "Your reputation grows along the road.", "gold": True})
        if rep.get("new_high"):
            gains.append({"icon": "🏅", "title": "New high score", "text": dr.fmt(rep.get("high_score"))})

        conq = game.find_terr(rep["conquered"]) if rep.get("conquered") else None
        nxt = game.next_level(key) if key else None
        unlocked_terr = nxt["t"] if (conq and nxt and nxt["t"]["key"] != conq["key"]) else None
        self.conq_box.visible = conq is not None
        if conq:
            self.conq_crest.content = dr.art_crest(conq, "mastered" if rep.get("mastered") else "conquered", 60)
            self.conq_title.text = conq["name"] + " conquered!"
            self.conq_text.text = (("And mastered, with three stars on every level." if rep.get("mastered") else "Its crest is yours.") +
                                   (" The road opens to %s." % unlocked_terr["name"] if unlocked_terr else ""))
        elif rep.get("mastered"):
            mt = game.find_terr(rep["mastered"])
            if mt:
                gains.append({"icon": "🏆", "title": mt["name"] + " mastered", "text": "Three stars on every level.", "gold": True})
        for i, g in enumerate(gains):
            g["delay"] = 0.5 + i * 0.12
        self.gains_panel.items = gains
        self.gains_panel.add_event_handler("x-open", self._open)
        lb = rep.get("leaderboard") or {}
        you = lb.get("you")
        self.board_label.visible = bool(you)
        self.board_label.text = "Leaderboard: #%d of %d" % (you["rank"], lb.get("total") or 0) if you else ""

        self.next_key = nxt["l"]["key"] if nxt else None
        self.next_terr = nxt["t"]["key"] if nxt else None
        self.map_terr = (unlocked_terr or (x["t"] if x else None) or {}).get("key")
        self.next_button.visible = nxt is not None
        self.next_button.text = ("Next: %s ▸" % nxt["l"]["name"]) if nxt else ""
        self.map_button.role = ["btn", "btn-lg"] if nxt else ["btn", "btn-primary", "btn-lg"]
        self._conq = conq is not None

    @handle("", "show")
    def form_show(self, **event_args):
        dr.sfx("win")
        stars = [self.star1, self.star2, self.star3]
        n = int(self._rep.get("stars") or 0)
        for i in range(3):
            if i < n:
                window.setTimeout(dr.report(lambda el=stars[i]: self._light(el)), 450 + i * 320)
        if self._conq:
            window.setTimeout(dr.report(lambda: dr.sfx("conquer")), 1400)
        elif self._rep.get("cards"):
            window.setTimeout(dr.report(lambda: dr.sfx("card")), 1400)
        state.focus(self.next_button if self.next_button.visible else self.map_button)

    def _light(self, el):
        el.classes["on"] = True
        dr.sfx("star")

    def _open(self, what, **event_args):
        kind, key = what.split(":", 1)
        if kind == "codex":
            from ..CodexPage import CodexPage
            alert(CodexPage(key=key), buttons=[], large=True, role="app-dialog", dismissible=True)
        else:
            from ..ComposerView import ComposerView
            alert(ComposerView(key=key), buttons=[], role="app-dialog", dismissible=True)

    def _close(self, v):
        dr.sfx("click")
        self.raise_event("x-close-alert", value=v)

    @handle("next_button", "click")
    def next_button_click(self, **event_args):
        self._close("next")

    @handle("again_button", "click")
    def again_button_click(self, **event_args):
        self._close("again")

    @handle("map_button", "click")
    def map_button_click(self, **event_args):
        self._close("map")
