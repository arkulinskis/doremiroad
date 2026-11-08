from anvil import *

from ._anvil_designer import ShopSectionTemplate
from ... import state


class ShopSection(ShopSectionTemplate):
    """One shelf of the shop: item = {title, desc, items}. Buy / Use go up to the page."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.title_label.text = self.item["title"]
        state.heading(self.title_label, 2)
        self.desc_label.text = self.item["desc"]
        self.items_panel.items = self.item["items"]
        self.items_panel.add_event_handler("x-buy", lambda kind, key, **e: self.parent.raise_event("x-buy", kind=kind, key=key))
        self.items_panel.add_event_handler("x-equip", lambda kind, key, **e: self.parent.raise_event("x-equip", kind=kind, key=key))
