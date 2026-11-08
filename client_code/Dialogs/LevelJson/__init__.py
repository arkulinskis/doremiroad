import json

from anvil import *

from ._anvil_designer import LevelJsonTemplate
from ... import state


class LevelJson(LevelJsonTemplate):
    """The level's raw data as JSON. Apply closes with the new data (a dict with a "steps" list)."""

    def __init__(self, data=None, **properties):
        super().__init__(**properties)
        state.heading(self.title_label, 2)
        self.json_box.text = json.dumps(data or {}, indent=2, ensure_ascii=False)
        state.set_control_attr(self.json_box, "aria-label", "Level data as JSON")
        state.set_control_attr(self.json_box, "spellcheck", "false")

    @handle("apply_button", "click")
    def apply_button_click(self, **event_args):
        try:
            d = json.loads(self.json_box.text or "")
            if not isinstance(d, dict) or not isinstance(d.get("steps"), list):
                raise ValueError('It needs a "steps" list.')
        except Exception as e:
            self.error_label.text = str(e)
            self.error_label.visible = True
            return
        self.raise_event("x-close-alert", value=d)
