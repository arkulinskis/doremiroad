from anvil import *

from ._anvil_designer import BadgesTemplate
from ... import dr, game, state


class Badges(BadgesTemplate):
    """#badges (Operate): all 32 badges, earned ones lit with their date."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        state.heading(self.title_label, 1)
        if not game.ensure():
            return
        have = game.S["progress"]["badges"]
        cat = game.S["catalog"]["badges"]
        self.lede_label.text = "%d of %d earned." % (len(have), len(cat))
        self.badges_panel.items = [{"emoji": b["emoji"], "name": b["name"], "desc": b["desc"], "earned": have.get(b["key"])}
                                   for b in cat]

    @handle("", "show")
    def form_show(self, **event_args):
        dr.ambient(True)
