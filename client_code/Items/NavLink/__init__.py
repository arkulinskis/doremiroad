from anvil import *

from ._anvil_designer import NavLinkTemplate
from ... import router, state


class NavLink(NavLinkTemplate):
    """A hub tab in the header. item = {page, label, icon, on, dot} from router.NAV (dot = something to buy)."""

    def __init__(self, **properties):
        super().__init__(**properties)
        state.set_attr(self, "href", router.href(self.item["page"]))
        self.classes["on"] = bool(self.item.get("on"))
        if self.item.get("on"):
            state.set_attr(self, "aria-current", "page")
        self.dot.visible = bool(self.item.get("dot"))
