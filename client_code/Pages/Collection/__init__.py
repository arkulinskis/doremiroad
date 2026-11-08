from anvil import *

from ._anvil_designer import CollectionTemplate
from ... import dr, game, state

STATE_WORD = {"locked": "locked", "open": "in progress", "conquered": "conquered", "mastered": "mastered"}


class Collection(CollectionTemplate):
    """#collection (Operate): composer cards (Dialogs/ComposerView), territory crests, the player's record."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        state.heading(self.title_label, 1)
        self.cards_panel.add_event_handler("x-card", self._card)
        if not game.ensure():
            return
        S = game.S
        p, s, cat = S["progress"], S["status"], S["catalog"]
        where = game.card_where()
        owned = len([c for c in cat["composers"] if p["cards"].get(c["key"])])
        self.cards_count.text = "%d / %d" % (owned, len(cat["composers"]))
        order = sorted(cat["composers"], key=lambda c: cat["rarity"][c["rarity"]]["order"])
        cards = []
        for c in order:
            have, w = p["cards"].get(c["key"]) or 0, where.get(c["key"])
            if have:
                sub = c["years"]
            elif w:
                sub = ("★★★ " if w["how"] == "three" else "Clear ") + w["x"]["l"]["name"]
            else:
                sub = "Daily practice"
            cards.append({"key": c["key"], "have": have, "rarity": c["rarity"], "rarity_name": cat["rarity"][c["rarity"]]["name"],
                          "name": c["name"] if have else "???", "sub": sub, "art": dr.art_medallion(c, bool(have), 86)})
        self.cards_panel.items = cards
        self.crests_count.text = "%d conquered · %d mastered" % (len(s["conquered"]), len(s["mastered"]))
        self.crests_panel.items = [{"name": t["name"], "state": STATE_WORD[game.terr_state(t)],
                                    "art": dr.art_crest(t, game.terr_state(t), 64)} for t in S["journey"]]
        st = p["stats"]
        f = dr.fmt
        self.stats_panel.items = [{"label": a, "value": b} for a, b in [
            ("Levels cleared", "%d / %d" % (len(s["cleared"]), s["levels_max"])), ("Stars", "%d / %d" % (s["stars"], s["stars_max"])),
            ("Codex pages", "%d / %d" % (s["codex"], s["codex_max"])), ("Notes played right", f(st.get("notes"))),
            ("Chords played right", f(st.get("chords"))), ("Ear questions right", f(st.get("ear"))),
            ("Quiz answers right", f(st.get("quiz"))), ("Perfect hits", f(st.get("perfects"))), ("Best combo", f(st.get("max_combo"))),
            ("Flawless levels", f(st.get("flawless"))), ("Days practised", f(st.get("dailies"))), ("Longest streak", f(p["daily"]["best"]))]]

    def _card(self, key, **event_args):
        dr.sfx("card")
        from ...Dialogs.ComposerView import ComposerView
        alert(ComposerView(key=key), buttons=[], role="app-dialog", dismissible=True)

    @handle("", "show")
    def form_show(self, **event_args):
        dr.ambient(True)
