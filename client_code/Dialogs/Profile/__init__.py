from anvil import *

from ._anvil_designer import ProfileTemplate
from ... import auth, dr, game, router, state


class Profile(ProfileTemplate):
    """Profile and settings (the round button in the bar): rank and XP, rename, settings, the level editor for admins,
    How to play, Privacy & Terms, and sign in / create an account / sign out."""

    def __init__(self, **properties):
        super().__init__(**properties)
        S = game.S
        me, r = S["me"] or {}, S["status"]["rank"]
        guest = S["guest"]
        self.avatar_label.text = (me.get("name") or "?")[:1].upper()
        self.name_label.text = me.get("name") or "Traveller"
        state.heading(self.name_label, 2)
        nxt = ""
        if r.get("next"):
            nxt = " (%s to %s)" % (dr.fmt(r["next"] - r["xp"]), S["catalog"]["ranks"][r["idx"] + 1]["name"])
        self.rank_label.text = "%s · %s XP%s" % (r["name"], dr.fmt(r["xp"]), nxt)
        self.who_label.text = "Playing as a guest: progress lives in this browser." if guest else (me.get("email") or "")
        self.rename_box.visible = not guest
        self.name_box.text = me.get("name") or ""
        state.set_control_attr(self.name_box, "maxlength", "24")
        state.set_control_attr(self.name_box, "autocomplete", "nickname")
        self.admin_button.visible = bool(me.get("is_admin"))
        self.signup_button.visible = guest
        self.signin_button.visible = guest
        self.signout_button.visible = not guest

    def _close(self, v=None):
        self.raise_event("x-close-alert", value=v)

    @handle("rename_button", "click")
    def rename_button_click(self, **event_args):
        if game.rename(self.name_box.text or ""):
            state.toast("Name saved", "ok")
            self._close()

    @handle("name_box", "pressed_enter")
    def name_box_pressed_enter(self, **event_args):
        self.rename_button_click()

    @handle("admin_button", "click")
    def admin_button_click(self, **event_args):
        self._close()
        router.go("admin")

    @handle("how_button", "click")
    def how_button_click(self, **event_args):
        self._close()
        router.go("landing", "how")

    @handle("signup_button", "click")
    def signup_button_click(self, **event_args):
        self._close()
        router.go("auth", "signup")

    @handle("signin_button", "click")
    def signin_button_click(self, **event_args):
        self._close()
        router.go("auth")

    @handle("signout_button", "click")
    def signout_button_click(self, **event_args):
        self._close()
        auth.sign_out()
        state.toast("Signed out. Your road waits for you.")
        router.go("landing")
