from anvil import *

from ._anvil_designer import FailTemplate
from ... import dr, state


class Fail(FailTemplate):
    """A level that didn't clear (or a result that didn't save): closes with "retry" or "map"."""

    def __init__(self, kicker="", title="", text="", **properties):
        super().__init__(**properties)
        self.title_label.text = title
        state.heading(self.title_label, 2)
        self.kicker_label.text = kicker
        self.text_label.text = text

    @handle("retry_button", "click")
    def retry_button_click(self, **event_args):
        dr.sfx("click")
        self.raise_event("x-close-alert", value="retry")

    @handle("map_button", "click")
    def map_button_click(self, **event_args):
        dr.sfx("click")
        self.raise_event("x-close-alert", value="map")

    @handle("", "show")
    def form_show(self, **event_args):
        state.focus(self.retry_button)
