from anvil import *

from ._anvil_designer import ComposerCardTemplate
from ... import dr, state


class ComposerCard(ComposerCardTemplate):
    """A composer card in the collection: item = {key, have, rarity, rarity_name, name, sub, art}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        self.card.classes.update({"r-" + it["rarity"]: True, "no": not it["have"]})
        self.count_label.text = "×%d" % it["have"] if it["have"] > 1 else ""
        self.count_label.visible = it["have"] > 1
        self.rarity_label.text = it["rarity_name"]
        self.rarity_label.foreground = "color-mix(in srgb, %s 70%%, var(--c-ink))" % dr.rarity_colour(it["rarity"])
        self.medal.content = it["art"]
        self.name_label.text = it["name"]
        self.sub_label.text = it["sub"]
        if not it["have"]:
            state.set_attr(self.card, "aria-disabled", "true")
            state.set_attr(self.card, "aria-label", "Not collected yet (%s). %s" % (it["rarity_name"], it["sub"]))

    def card_click(self, event):
        if self.item["have"]:
            self.parent.raise_event("x-card", key=self.item["key"])
