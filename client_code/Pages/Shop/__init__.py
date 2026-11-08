from anvil import *

from ._anvil_designer import ShopTemplate
from ... import dr, game, router, state

KINDS = [("skins", "Keyboards", "How the keys look while you play."),
         ("trails", "Note trails", "The falling notes in rush challenges."),
         ("banners", "Banners", "Your colour on the knowledge map.")]


class Shop(ShopTemplate):
    """#shop (Operate): keyboards, note trails and banners, bought with ducats and put to use."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        state.heading(self.title_label, 1)
        self.sections_panel.add_event_handler("x-buy", self._buy)
        self.sections_panel.add_event_handler("x-equip", self._equip)
        self._draw()

    def _draw(self):
        if not game.ensure():
            return
        p = game.S["progress"]
        self.lede_label.text = ("You have 🪙 %s ducats. Earn more by clearing levels, winning stars and practising daily."
                                % dr.fmt(p["ducats"]))
        sections = []
        for kind, title, desc in KINDS:
            items = []
            for x in game.S["catalog"]["shop"][kind]:
                items.append({"kind": kind, "key": x["key"], "name": x["name"], "desc": x.get("desc") or "",
                              "price": x["price"], "own": x["key"] in p["owned"][kind], "eq": p["equip"].get(kind) == x["key"],
                              "afford": p["ducats"] >= x["price"], "art": dr.shop_preview(kind, x)})
            sections.append({"title": title, "desc": desc, "items": items})
        self.sections_panel.items = sections

    def _buy(self, kind, key, **event_args):
        r = game.act("buy", kind, key)
        if r:
            dr.sfx("coin")
            state.toast("Yours: " + game.C["shop"][kind][key]["name"], "ok")
            for k in (r.get("report") or {}).get("new_badges") or []:
                b = game.C["badges"].get(k)
                if b:
                    state.toast("%s Badge earned: %s" % (b["emoji"], b["name"]), "ok")
            self._draw()
            router.refresh_shell()

    def _equip(self, kind, key, **event_args):
        if game.act("equip", kind, key):
            dr.sfx("click")
            self._draw()
            router.refresh_shell()

    @handle("", "show")
    def form_show(self, **event_args):
        dr.ambient(True)
