from anvil import *

from ._anvil_designer import AdminLevelTemplate
from ... import state


class AdminLevel(AdminLevelTemplate):
    """A level in the editor's list: item = {l, on, host}. Click edits it; ▲ ▼ reorder."""

    def __init__(self, **properties):
        super().__init__(**properties)
        l = self.item["l"]
        self.row.classes["on"] = bool(self.item["on"])
        self.name_link.text = ("⚑ " if l["data"].get("trial") else "") + l["name"]
        n = len(l.get("errors") or [])
        self.err_chip.text = "%d err" % n
        self.err_chip.visible = bool(n)
        self.draft_chip.visible = not l["published"]
        self.bi_chip.visible = bool(l.get("builtin"))
        state.set_control_attr(self.up_button, "aria-label", "Move %s up" % l["name"])
        state.set_control_attr(self.down_button, "aria-label", "Move %s down" % l["name"])
        if self.item["on"]:
            state.set_attr(self.name_link, "aria-current", "true")

    @handle("name_link", "click")
    def name_link_click(self, **event_args):
        self.item["host"].edit(self.item["l"]["key"])

    @handle("up_button", "click")
    def up_button_click(self, **event_args):
        self.item["host"].move_level(self.item["l"]["key"], -1)

    @handle("down_button", "click")
    def down_button_click(self, **event_args):
        self.item["host"].move_level(self.item["l"]["key"], 1)
