# AdminPage — Custom HTML form: the admin sign-in and the level editor (#admin).
# HTML + JS: forms/AdminPage.html. The server checks the admin flag on every call.
from ._anvil_designer import AdminPageTemplate
from anvil import *
import anvil.server
import anvil.users

from .. import dr_ui


class AdminPage(AdminPageTemplate):
    def __init__(self, **properties):
        super().__init__(**properties)
        self.mounted = False
        self.add_event_handler("show", self._on_show)

    def _on_show(self, **event_args):
        if self.mounted:
            return
        self.mounted = True
        dr_ui.mount(self, "admin", {}, self._on_event)

    def _on_event(self, event, p):
        if event == "call":
            fn = p.get("fn")
            if fn not in dr_ui.ADMIN_CALLS:
                return {"ok": False, "error": "Unknown action."}
            return dr_ui.call(fn, *(p.get("args") or []))
        if event in ("login", "signup", "reset"):
            return dr_ui.auth(event, p)
        if event == "logout":
            anvil.users.logout()
            return {"ok": True}
        if event == "game":
            get_open_form().open_game()
        return None
