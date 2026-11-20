from anvil import *

from ._anvil_designer import NavLinkTemplate
from ... import router, state


class NavLink(NavLinkTemplate):
    """A hub tab in the header. item = {page, label, short, icon, on, dot} from router.NAV (dot = something to buy, or
    homework still open). Phones show the short label."""

    def __init__(self, **properties):
        super().__init__(**properties)
        state.set_attr(self, "href", router.href(self.item["page"]))
        self.classes["on"] = bool(self.item.get("on"))
        if self.item.get("on"):
            state.set_attr(self, "aria-current", "page")
        self.dot.visible = bool(self.item.get("dot"))
        self.short_label.text = self.item.get("short") or self.item["label"]
        if self.item.get("dot"):
            state.set_attr(self, "aria-label", self.item["label"] + (" (homework to do)" if self.item["page"] == "hw"
                                                                     else " (something you can buy)"))
