from anvil import *

from ._anvil_designer import CodexTemplate
from ... import dr, game, state


class Codex(CodexTemplate):
    """#codex (Operate): every theory page by topic; unlocked ones open Dialogs/CodexPage, locked ones say which
    level teaches them."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        state.heading(self.title_label, 1)
        self.topics_panel.add_event_handler("x-open", self._open)
        if not game.ensure():
            self.lede_label.text = "The road didn't load. Check your connection and reload the page."
            return
        S = game.S
        where, have = game.codex_where(), S["progress"]["codex"]
        self.lede_label.text = "Every idea you learn on the road, written down. %d of %d pages unlocked." % (
            len(have), len(S["catalog"]["codex"]))
        topics = []
        for tp in S["catalog"]["topics"]:
            pages = [c for c in S["catalog"]["codex"] if c["topic"] == tp["key"]]
            if not pages:
                continue
            tiles = []
            for c in pages:
                ok, w = c["key"] in have, where.get(c["key"])
                tiles.append({"key": c["key"], "ok": ok, "glyph": c["glyph"] if ok else "?", "title": c["title"] if ok else "???",
                              "sub": "Read" if ok else ("Learn it in %s (%s)" % (w["l"]["name"], w["t"]["name"]) if w else "Not on the road yet")})
            topics.append({"name": tp["name"], "count": "%d / %d" % (len([c for c in pages if c["key"] in have]), len(pages)),
                           "tiles": tiles})
        self.topics_panel.items = topics

    def _open(self, key, **event_args):
        dr.sfx("page")
        from ...Dialogs.CodexPage import CodexPage
        alert(CodexPage(key=key), buttons=[], large=True, role="app-dialog", dismissible=True)

    @handle("", "show")
    def form_show(self, **event_args):
        dr.ambient(True)
