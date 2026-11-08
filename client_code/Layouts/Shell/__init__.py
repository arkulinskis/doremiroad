import datetime

from anvil import *

from ._anvil_designer import ShellTemplate
from ... import dr, game, router, state


class Shell(ShellTemplate):
    """The hub frame around every page: the bar (brand, the six tabs, rank + XP, ducats, streak, the profile button)
    and the footer (Submit feedback, Privacy & Terms, Contact developer, Parent company).

    Anvil keeps ONE Shell while pages come and go, so everything that depends on the player or the page is drawn in
    refresh(), which router.show() calls after every page change (and router.refresh_shell() after a purchase)."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.copyright_label.text = "© %d Doremi Road" % datetime.date.today().year
        self.refresh("")

    def refresh(self, page):
        me = state.me()
        self.classes.update({"signed-in": bool(me), "signed-out": not me, "no-chrome": page == "play",
                             "no-header": page == "landing", "is-admin-page": page == "admin"})
        loaded = game.ready()
        dot = loaded and game.can_buy_any()
        self.nav_panel.items = [{"page": p, "label": label, "icon": icon, "on": p == page, "dot": p == "shop" and dot}
                                for p, label, icon in router.NAV]
        self.me_box.visible = loaded or bool(me)
        self.guest_box.visible = not me and page not in ("auth",)
        self.rank_link.visible = loaded
        self.ducats.visible = loaded
        self.streak.visible = False
        if loaded:
            r = game.S["status"]["rank"]
            self.rank_name.text = r["name"]
            self.rank_xp.text = game.rank_line()
            state.set_attr(self.rank_link, "title", "%s XP" % dr.fmt(r["xp"]))
            state.set_attr(self.rank_link, "aria-label", "%s, %s. Profile and settings" % (r["name"], game.rank_line()))
            self.xp_bar.style["width"] = "%d%%" % game.rank_pct()
            self.ducats.text = "🪙 " + dr.fmt(game.S["progress"]["ducats"])
            streak = (game.S["daily"] or {}).get("streak") or 0
            self.streak.visible = bool(streak)
            self.streak.text = "🔥 %d" % streak
        name = (game.S["me"] or {}).get("name") if loaded else (me or {}).get("name")
        self.avatar_button.text = (name or "?")[:1].upper()
        state.set_control_attr(self.avatar_button, "aria-label", "Profile and settings")

    def profile_click(self, event):
        event.preventDefault()
        self.avatar_button_click()

    @handle("avatar_button", "click")
    def avatar_button_click(self, **event_args):
        dr.sfx("click")
        from ...Dialogs.Profile import Profile
        if not game.ensure():
            return
        alert(Profile(), buttons=[], large=True, role="app-dialog", dismissible=True)
        router.refresh_shell()
