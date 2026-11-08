from anvil import *

from ._anvil_designer import SettingsTemplate
from ... import state


class Settings(SettingsTemplate):
    """Settings from the pause menu (the same panel as in the profile)."""

    def __init__(self, **properties):
        super().__init__(**properties)
        state.heading(self.title_label, 2)

    @handle("done_button", "click")
    def done_button_click(self, **event_args):
        self.raise_event("x-close-alert", value=True)
