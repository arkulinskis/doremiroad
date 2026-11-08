from anvil import *

from ._anvil_designer import ArtTemplate


class Art(ArtTemplate):
    """A picture from the art engine (SVG markup made by dr-art.js / dr-ui.js from game data, never user text)."""

    def __init__(self, **properties):
        self._content, self._label, self._ready = "", "", False
        super().__init__(**properties)
        self._ready = True
        self._draw()

    def _draw(self):
        if not self._ready:
            return
        host = self.dom_nodes["host"]
        host.innerHTML = self._content or ""
        if self._label:
            host.setAttribute("role", "img")
            host.setAttribute("aria-label", self._label)
        else:
            host.removeAttribute("role")
            host.removeAttribute("aria-label")
            host.setAttribute("aria-hidden", "true")

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value or ""
        self._draw()

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        self._label = value or ""
        self._draw()
