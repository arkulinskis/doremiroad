from anvil import *

from ._anvil_designer import PlayerRowTemplate
from ... import state


class PlayerRow(PlayerRowTemplate):
    """A player in the Players tab: item = {p, host, me}. The tick box grants or removes admin rights."""

    def __init__(self, **properties):
        super().__init__(**properties)
        p = self.item["p"]
        self.name_label.text = p["name"] or "—"
        self.email_label.text = p["email"] or ""
        self.rank_label.text = "%s · %s XP" % (p["rank"], p["xp"])
        self.cleared_label.text = str(p["cleared"])
        self.stars_label.text = str(p["stars"])
        self.conq_label.text = str(p["conquered"])
        self.codex_label.text = str(p["codex"])
        self.cards_label.text = str(p["cards"])
        self.streak_label.text = str(p["streak"])
        self.last_label.text = (p.get("last_played") or "")[:10]
        self.admin_box.checked = bool(p["is_admin"])
        state.set_control_attr(self.admin_box, "aria-label", "Admin rights for " + (p["email"] or p["name"] or "player"))

    @handle("admin_box", "change")
    def admin_box_change(self, **event_args):
        if not self.item["host"].set_admin(self.item["p"]["email"], bool(self.admin_box.checked)):
            self.admin_box.checked = not self.admin_box.checked
