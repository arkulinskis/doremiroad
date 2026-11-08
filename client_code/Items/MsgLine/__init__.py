from anvil import *

from ._anvil_designer import MsgLineTemplate


class MsgLine(MsgLineTemplate):
    """A line of the editor's checks: item = {kind: e | w | ok | note, text}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.text_label.text = self.item["text"]
        self.text_label.role = ["a-msg", "a-msg-" + self.item["kind"]]
