from anvil import *

from ._anvil_designer import KnowledgeMapTemplate
from ... import dr


def _loose(x):
    """Hide a JS NodeList's type from the validator (its stubs lack item())."""
    return x


class KnowledgeMap(KnowledgeMapTemplate):
    """The knowledge map (SVG from dr-art.js). draw() redraws it; select() moves the highlight without redrawing."""

    def __init__(self, **properties):
        super().__init__(**properties)

    def draw(self, journey, opts):
        self.dom_nodes["host"].innerHTML = dr.art_map(journey, opts)
        svg = self.dom_nodes["host"].querySelector("svg")
        if svg:
            svg.setAttribute("role", "group")
            svg.setAttribute("aria-label", "The knowledge map: pick a territory")

    def select(self, key):
        nodes = _loose(self.dom_nodes["host"].querySelectorAll(".m-terr"))
        for i in range(nodes.length):
            n = nodes.item(i)
            n.classList.toggle("sel", n.getAttribute("data-t") == key)

    def host_click(self, event):
        g = event.target.closest(".m-terr")
        if g:
            self.raise_event("pick", key=str(g.getAttribute("data-t")))

    def host_key(self, event):
        if getattr(event, "key", None) == "Enter" or getattr(event, "key", None) == " ":
            g = event.target.closest(".m-terr")
            if g:
                event.preventDefault()
                self.raise_event("pick", key=str(g.getAttribute("data-t")))
