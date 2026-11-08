from anvil import *

from ._anvil_designer import StatTileTemplate


class StatTile(StatTileTemplate):
    """One number of the player's record: item = {label, value}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.label_label.text = self.item["label"]
        self.value_label.text = self.item["value"]
