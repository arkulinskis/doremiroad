from anvil import *

from ._anvil_designer import ComposerViewTemplate
from ... import dr, game, state


class ComposerView(ComposerViewTemplate):
    """A composer card, big: medallion, rarity and era, years, a fact."""

    def __init__(self, key="", **properties):
        super().__init__(**properties)
        c = game.C["composers"].get(key) or {}
        col = dr.rarity_colour(c.get("rarity"))
        self.medal.content = dr.art_medallion(c, True, 150) if c else ""
        self.medal.label = "Medallion of " + (c.get("name") or "")
        self.medal_box.style["border-color"] = col
        rarity = game.S["catalog"]["rarity"].get(c.get("rarity"), {}).get("name", "")
        self.rarity_label.text = "%s · %s" % (rarity, c.get("era") or "")
        self.rarity_label.foreground = "color-mix(in srgb, %s 70%%, var(--c-ink))" % col
        self.name_label.text = c.get("name") or ""
        state.heading(self.name_label, 2)
        self.years_label.text = c.get("years") or ""
        self.fact_label.text = c.get("fact") or ""
