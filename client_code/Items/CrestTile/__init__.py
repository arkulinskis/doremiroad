from anvil import *

from ._anvil_designer import CrestTileTemplate


class CrestTile(CrestTileTemplate):
    """A territory crest: item = {name, state, art}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.crest.content = self.item["art"]
        self.name_label.text = self.item["name"]
        self.state_label.text = self.item["state"]
