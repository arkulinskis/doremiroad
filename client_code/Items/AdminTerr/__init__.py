from anvil import *

from ._anvil_designer import AdminTerrTemplate
from ... import state


class AdminTerr(AdminTerrTemplate):
    """A territory in the editor's level list: item = {t, cur, host}. ＋ makes a new level here."""

    def __init__(self, **properties):
        super().__init__(**properties)
        t = self.item["t"]
        self.name_label.text = "%s %s" % (t["emoji"], t["name"])
        state.heading(self.name_label, 3)
        self.hidden_chip.visible = not t["published"]
        state.set_control_attr(self.new_button, "aria-label", "New level in " + t["name"])
        self.new_button.tooltip = "New level here"
        self.levels_panel.items = [{"l": l, "on": l["key"] == self.item["cur"], "host": self.item["host"]} for l in t["levels"]]

    @handle("new_button", "click")
    def new_button_click(self, **event_args):
        self.item["host"].new_level(self.item["t"]["key"])
