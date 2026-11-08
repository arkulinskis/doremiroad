from anvil import *

from ._anvil_designer import BadgeTileTemplate


class BadgeTile(BadgeTileTemplate):
    """A badge: item = {emoji, name, desc, earned (date or None)}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        self.tile.classes["no"] = not it["earned"]
        self.emoji_label.text = it["emoji"]
        self.name_label.text = it["name"]
        self.desc_label.text = it["desc"]
        self.earned_label.text = ("Earned " + it["earned"]) if it["earned"] else "Not earned yet"
