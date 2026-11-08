"""Who is signed in (the Forms version's start-up call) and their display name.

Admins: Game.ADMIN_EMAILS become admins the first time they sign in (Game.is_admin), or tick users.is_admin.
"""
import re

import anvil.server
import anvil.users

from . import Game as G


def me_dict(user):
    if user is None:
        return None
    return {"id": user.get_id(), "email": user["email"],
            "name": user["display_name"] or (user["email"] or "Player").split("@")[0],
            "is_admin": G.is_admin(user)}


@anvil.server.callable
def get_me():
    """The signed-in player (or None). Called when the app starts and after signing in."""
    return me_dict(anvil.users.get_user())


@anvil.server.callable(require_user=True)
def update_profile(name):
    """Sign-up's "Your name" (the same rule as Game.set_name)."""
    user = anvil.users.get_user()
    if user is None:
        raise anvil.server.PermissionDenied("Please sign in.")
    name = re.sub(r"\s+", " ", str(name or "")).strip()[:24]
    if len(name) < 2:
        return {"ok": False, "error": "Pick a name with at least 2 letters."}
    user["display_name"] = name
    return {"ok": True, "me": me_dict(user)}
