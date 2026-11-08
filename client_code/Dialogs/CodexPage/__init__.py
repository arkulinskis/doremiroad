from anvil import *

from ._anvil_designer import CodexPageTemplate
from ... import dr, game, state


class CodexPage(CodexPageTemplate):
    """A codex page: the idea, a keyboard that shows the example (Components/Keys), Hear it."""

    def __init__(self, key="", **properties):
        super().__init__(**properties)
        c = game.C["codex"].get(key) or {}
        self._c = c
        topic = next((t for t in game.S["catalog"]["topics"] if t["key"] == c.get("topic")), None)
        self.glyph_label.text = c.get("glyph") or ""
        self.title_label.text = c.get("title") or ""
        state.heading(self.title_label, 2)
        self.topic_label.text = topic["name"] if topic else ""
        self.text_label.text = c.get("text") or ""
        notes = (c.get("ex") or {}).get("notes") or []
        self.notes_label.text = dr.pretty_notes(notes) if notes else ""

    @handle("", "show")
    def form_show(self, **event_args):
        if self._c.get("ex"):
            self.keys.show_example(self._c["ex"], game.S["progress"]["equip"].get("skins") or "classic")

    @handle("hear_button", "click")
    def hear_button_click(self, **event_args):
        self.keys.hear()
