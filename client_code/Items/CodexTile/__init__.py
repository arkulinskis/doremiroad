from anvil import *

from ._anvil_designer import CodexTileTemplate
from ... import state


class CodexTile(CodexTileTemplate):
    """A codex page tile: item = {key, ok, glyph, title, sub}. Locked tiles say where the page is learnt."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        self.glyph_label.text = it["glyph"]
        self.title_label.text = it["title"]
        self.sub_label.text = it["sub"]
        self.tile.classes["locked"] = not it["ok"]
        if not it["ok"]:
            state.set_attr(self.tile, "aria-disabled", "true")
            state.set_attr(self.tile, "aria-label", "Locked page. " + it["sub"])

    def tile_click(self, event):
        if self.item["ok"]:
            self.parent.raise_event("x-open", key=self.item["key"])
