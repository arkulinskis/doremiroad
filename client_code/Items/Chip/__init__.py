from anvil import *

from ._anvil_designer import ChipTemplate
from ... import state


class Chip(ChipTemplate):
    """A toggle chip in the editor (codex pages, ear answers) or an Add-a-step button.
    item = {label, key, kind, on?, used?, title?, host}; clicking calls host.chip_clicked(kind, key)."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        self.chip_button.text = it["label"]
        roles = ["a-cx"]
        if it.get("on"):
            roles.append("on")
        if it.get("used"):
            roles.append("used")
        if it["kind"] == "add":
            roles = ["btn", "btn-sm"]
        self.chip_button.role = roles
        if it.get("title"):
            self.chip_button.tooltip = it["title"]
        if it["kind"] != "add":
            state.set_control_attr(self.chip_button, "aria-pressed", "true" if it.get("on") else "false")

    @handle("chip_button", "click")
    def chip_button_click(self, **event_args):
        self.item["host"].chip_clicked(self.item["kind"], self.item["key"])
