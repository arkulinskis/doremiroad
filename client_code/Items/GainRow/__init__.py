from anvil import *

from ._anvil_designer import GainRowTemplate
from ... import state


class GainRow(GainRowTemplate):
    """Something won after a level: item = {icon, title, text, open?, gold?, delay}. With open ("codex:k" or
    "card:k") it is a button that raises x-open on the panel."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        self.icon_label.text = it["icon"]
        self.title_label.text = it["title"]
        self.text_label.text = it.get("text") or ""
        self.text_label.visible = bool(it.get("text"))
        self.box.classes.update({"gold": bool(it.get("gold")), "click": bool(it.get("open"))})
        self.box.style["animation-delay"] = "%.2fs" % it.get("delay", 0)
        if it.get("open"):
            state.set_attr(self.box, "role", "button")
            state.set_attr(self.box, "tabindex", "0")

    def box_click(self, event):
        if self.item.get("open"):
            self.parent.raise_event("x-open", what=self.item["open"])

    def box_key(self, event):
        if self.item.get("open") and getattr(event, "key", None) in ("Enter", " "):
            event.preventDefault()
            self.parent.raise_event("x-open", what=self.item["open"])
