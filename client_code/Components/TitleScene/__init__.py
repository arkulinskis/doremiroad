from anvil import *
from anvil.js import window

from ._anvil_designer import TitleSceneTemplate


class TitleScene(TitleSceneTemplate):
    """The title screen's animated canvas (the art engine draws it; it stops when the page goes away)."""

    def __init__(self, **properties):
        self._anim = None
        super().__init__(**properties)

    @handle("", "show")
    def form_show(self, **event_args):
        if self._anim is None:
            self._anim = window.DR.Art.titleScene(self.dom_nodes["canvas"])

    @handle("", "hide")
    def form_hide(self, **event_args):
        self.stop()

    def stop(self):
        if self._anim is not None:
            try:
                self._anim.stop()
            except Exception:
                pass
            self._anim = None
