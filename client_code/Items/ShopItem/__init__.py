from anvil import *

from ._anvil_designer import ShopItemTemplate
from ... import state


class ShopItem(ShopItemTemplate):
    """A shop item: item = {kind, key, name, desc, price, own, eq, afford, art}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        self.card.classes["eq"] = it["eq"]
        self.preview.content = it["art"]
        self.name_label.text = it["name"]
        self.desc_label.text = it["desc"]
        self.desc_label.visible = bool(it["desc"])
        self.use_button.visible = it["own"] and not it["eq"]
        self.buy_button.visible = not it["own"]
        if it["eq"]:
            self.status_label.text = "✓ In use"
        elif it["own"]:
            self.status_label.text = "Owned"
        else:
            self.status_label.text = "🪙 %d" % it["price"]
            self.status_label.role = ["sh-price"]
            self.buy_button.enabled = it["afford"]
            self.buy_button.role = ["btn", "btn-sm", "btn-primary"] if it["afford"] else ["btn", "btn-sm"]
        state.set_control_attr(self.buy_button, "aria-label", "Buy %s for %d ducats" % (it["name"], it["price"]))
        state.set_control_attr(self.use_button, "aria-label", "Use " + it["name"])

    @handle("buy_button", "click")
    def buy_button_click(self, **event_args):
        self.parent.raise_event("x-buy", kind=self.item["kind"], key=self.item["key"])

    @handle("use_button", "click")
    def use_button_click(self, **event_args):
        self.parent.raise_event("x-equip", kind=self.item["kind"], key=self.item["key"])
