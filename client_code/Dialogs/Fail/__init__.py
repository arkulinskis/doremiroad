from anvil import *

from ._anvil_designer import FailTemplate
from ... import dr, state


class Fail(FailTemplate):
    """A level that didn't clear (or a result that didn't save): closes with "retry", "slower" (the slower way to play
    it: 75% / 50% speed, or a song's easier mode; only when slower_text is given) or "map" (back)."""

    def __init__(self, kicker="", title="", text="", slower_text="", back_text="Back to the map", **properties):
        super().__init__(**properties)
        self.title_label.text = title
        state.heading(self.title_label, 2)
        self.kicker_label.text = kicker
        self.text_label.text = text
        self.slower_button.text = slower_text
        self.slower_button.visible = bool(slower_text)
        self.map_button.text = back_text or "Back to the map"

    @handle("retry_button", "click")
    def retry_button_click(self, **event_args):
        dr.sfx("click")
        self.raise_event("x-close-alert", value="retry")

    @handle("slower_button", "click")
    def slower_button_click(self, **event_args):
        dr.sfx("click")
        self.raise_event("x-close-alert", value="slower")

    @handle("map_button", "click")
    def map_button_click(self, **event_args):
        dr.sfx("click")
        self.raise_event("x-close-alert", value="map")

    @handle("", "show")
    def form_show(self, **event_args):
        state.focus(self.retry_button)
