from anvil import *

from ._anvil_designer import SwatchTemplate
from ... import state


class Swatch(SwatchTemplate):
    """A territory colour: item = {color, on, host}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.dot.style["background"] = self.item["color"]
        state.set_attr(self.dot, "aria-label", "Colour " + self.item["color"])
        self.set_on(self.item["on"])

    def set_on(self, on):
        self.dot.classes["on"] = bool(on)
        state.set_attr(self.dot, "aria-pressed", "true" if on else "false")

    def dot_click(self, event):
        self.item["host"].pick_colour(self.item["color"])
