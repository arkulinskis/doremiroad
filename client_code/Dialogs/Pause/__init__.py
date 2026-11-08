from anvil import *

from ._anvil_designer import PauseTemplate
from ... import dr, state


class Pause(PauseTemplate):
    """The pause menu: closes with "resume", "restart", "settings" or "quit" (Escape / outside = resume)."""

    def __init__(self, **properties):
        super().__init__(**properties)
        state.heading(self.title_label, 2)

    def _close(self, value):
        dr.sfx("click")
        self.raise_event("x-close-alert", value=value)

    @handle("resume_button", "click")
    def resume_button_click(self, **event_args):
        self._close("resume")

    @handle("restart_button", "click")
    def restart_button_click(self, **event_args):
        self._close("restart")

    @handle("settings_button", "click")
    def settings_button_click(self, **event_args):
        self._close("settings")

    @handle("quit_button", "click")
    def quit_button_click(self, **event_args):
        self._close("quit")

    @handle("", "show")
    def form_show(self, **event_args):
        state.focus(self.resume_button)
