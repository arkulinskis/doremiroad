from anvil import *

from ._anvil_designer import LevelCardTemplate
from ... import dr, game, state


class LevelCard(LevelCardTemplate):
    """The level card (from the map): what the level teaches, your best, rewards, the leaderboard, Play.
    Closes with "play" when Play is pressed."""

    def __init__(self, key="", **properties):
        super().__init__(**properties)
        self._key = key
        x = game.find_level(key)
        if x is None:
            return
        l, d, r = x["l"], x["l"]["data"], game.rec(key)
        cards = d.get("cards") or {}
        self.title_label.text = l["name"]
        state.heading(self.title_label, 2)
        self.where_label.text = x["t"]["name"] + (" · Trial" if d.get("trial") else " · Level %d" % (x["i"] + 1))
        self.intro_label.text = d.get("intro") or ""
        self.intro_label.visible = bool(d.get("intro"))
        self.steps_panel.items = [{"icon": dr.step_icon(s.get("t")), "name": dr.step_name(s.get("t"))} for s in d.get("steps") or []]
        self.best_stars.text = game.stars_text(r["stars"])
        state.set_attr(self.best_stars, "aria-label", "%d of 3 stars" % r["stars"])
        self.best_text.text = ("Accuracy %d%% · score %s · played %d×" % (round(r["best"]), dr.fmt(r["score"]), r["clears"])
                               if r["stars"] else "Not cleared yet")
        self.marks_text.text = "Clear %s%% · ★★ %s%% · ★★★ %s%% · %d scored items" % (
            60 if d.get("pass") is None else d["pass"], 80 if d.get("two") is None else d["two"],
            95 if d.get("three") is None else d["three"], dr.level_items(d))
        rewards = []
        prog = game.S["progress"]
        for k in d.get("codex") or []:
            c = game.C["codex"].get(k)
            if c:
                rewards.append({"icon": "📖", "text": c["title"] + (" ✓" if k in prog["codex"] else "")})
        for how in ("clear", "three"):
            k = cards.get(how)
            c = game.C["composers"].get(k) if k else None
            if c:
                have = prog["cards"].get(k)
                rewards.append({"icon": "🃏", "text": (c["name"] if have else "A %s composer card" % c["rarity"]) +
                                " (%s)%s" % ("3 stars" if how == "three" else "clear", " ✓" if have else "")})
        if not rewards:
            rewards.append({"icon": "✨", "text": "XP and ducats"})
        self.rewards_panel.items = rewards
        self.play_button.text = ("Play again" if r["stars"] else "Play") + " ▸"

    @handle("", "show")
    def form_show(self, **event_args):
        b = game.leaderboard(self._key)
        guest = game.S["guest"]
        if not b or not b.get("top"):
            self.board_note.text = "No scores yet. Create an account to post yours." if guest else "No scores yet. Be the first."
            return
        rows = [{"rank": r["rank"], "name": r["name"], "score": "%s · %d%%" % (dr.fmt(r["score"]), round(r["accuracy"])),
                 "you": r["you"]} for r in b["top"][:5]]
        you = b.get("you")
        if you and you["rank"] > 5:
            rows.append({"rank": you["rank"], "name": "You", "score": dr.fmt(you["score"]), "you": True})
        self.board_panel.items = rows
        self.board_note.text = "Sign in to appear here." if guest else ""
        self.board_note.visible = guest

    @handle("play_button", "click")
    def play_button_click(self, **event_args):
        dr.sfx("click")
        self.raise_event("x-close-alert", value="play")
