from anvil import *
import anvil.js
from anvil.js import window

from ._anvil_designer import KeysTemplate
from ... import dr


class Keys(KeysTemplate):
    """An on-screen piano from the engine. One job at a time: a codex example, or the Practice Room."""

    def __init__(self, **properties):
        self._api = None
        super().__init__(**properties)

    def show_example(self, example, skin="classic"):
        self.stop()
        self._api = window.DR.UI.codexKeyboard(self.dom_nodes["host"], dr.js(example), skin)

    def practice(self, ps, chord, info, rng):
        """The Practice Room engine. chord(big, small), info(text, midi_link), rng(text, can_down, can_up) are called
        back from JavaScript whenever something changes."""
        self.stop()
        hooks = dr.js({})
        hooks.chord = anvil.js.report_exceptions(chord)
        hooks.info = anvil.js.report_exceptions(info)
        hooks.range = anvil.js.report_exceptions(rng)
        self._api = window.DR.UI.practice(self.dom_nodes["host"], dr.js(ps), hooks)
        return self._api

    @property
    def api(self):
        return self._api

    def hear(self):
        if self._api is not None:
            self._api.hear()

    def stop(self):
        if self._api is not None:
            try:
                self._api.destroy()
            except Exception:
                pass
            self._api = None
            self.dom_nodes["host"].innerHTML = ""

    @handle("", "hide")
    def form_hide(self, **event_args):
        self.stop()
