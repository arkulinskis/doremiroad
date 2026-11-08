from anvil import *

from ._anvil_designer import CodexTopicTemplate
from ... import state


class CodexTopic(CodexTopicTemplate):
    """One codex topic: item = {name, count, tiles}. A tile's x-open goes up to the page."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.name_label.text = self.item["name"]
        state.heading(self.name_label, 2)
        self.count_label.text = self.item["count"]
        self.tiles_panel.items = self.item["tiles"]
        self.tiles_panel.add_event_handler("x-open", self._open)

    def _open(self, key, **event_args):
        self.parent.raise_event("x-open", key=key)
