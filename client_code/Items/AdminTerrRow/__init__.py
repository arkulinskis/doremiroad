from anvil import *

from ._anvil_designer import AdminTerrRowTemplate
from ... import state


class AdminTerrRow(AdminTerrRowTemplate):
    """A territory in the Territories tab: item = {t, on, host}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        t = self.item["t"]
        self.row.classes["on"] = bool(self.item["on"])
        self.name_link.text = "%s %s" % (t["emoji"], t["name"])
        self.hidden_chip.visible = not t["published"]
        self.count_chip.text = "%d levels" % len(t["levels"])
        state.set_control_attr(self.up_button, "aria-label", "Move %s up" % t["name"])
        state.set_control_attr(self.down_button, "aria-label", "Move %s down" % t["name"])

    @handle("name_link", "click")
    def name_link_click(self, **event_args):
        self.item["host"].pick_terr(self.item["t"]["key"])

    @handle("up_button", "click")
    def up_button_click(self, **event_args):
        self.item["host"].move_terr(self.item["t"]["key"], -1)

    @handle("down_button", "click")
    def down_button_click(self, **event_args):
        self.item["host"].move_terr(self.item["t"]["key"], 1)
