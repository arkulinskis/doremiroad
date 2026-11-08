"""Page addresses: #name/arg1/arg2 -> a page Form (open_form), with sign-in rules.

Links in templates are plain <a href="#map">; code calls router.go("play", key).

    PAGES[name] = (who may open it, browser-tab title)   who: None = anyone (guests play too), "guest" = signed out
                                                        only, "admin"
    NAV = the hub's tabs (header): (page, label, icon).
The JavaScript version had only two addresses: "" (the game) and #admin (the level editor); both still work.
New page: add it to PAGES and _form() (and NAV if it is a hub tab).
"""
import anvil
import anvil.js
from anvil.js import window

from . import state

PAGES = {
    "landing": (None, "Learn piano and music theory as a game"),
    "map": (None, "The map"),
    "codex": (None, "The Codex"),
    "collection": (None, "Collection"),
    "practice": (None, "Practice Room"),
    "badges": (None, "Badges"),
    "shop": (None, "The Shop"),
    "play": (None, "Playing"),
    "auth": ("guest", "Sign in"),
    "admin": ("admin", "Level editor"),
}
NAV = [("map", "Map", "map"), ("codex", "Codex", "book"), ("collection", "Collection", "star"),
       ("practice", "Practice Room", "music"), ("badges", "Badges", "shield"), ("shop", "Shop", "grid")]
APP_NAME = "Doremi Road"
_r: dict = {"after": "", "listening": False, "page": None}


def _form(name):
    """The page's Form class (imported when first needed, so start-up stays quick)."""
    if name == "landing":
        from .Pages.Landing import Landing
        return Landing
    if name == "map":
        from .Pages.Map import Map
        return Map
    if name == "codex":
        from .Pages.Codex import Codex
        return Codex
    if name == "collection":
        from .Pages.Collection import Collection
        return Collection
    if name == "practice":
        from .Pages.Practice import Practice
        return Practice
    if name == "badges":
        from .Pages.Badges import Badges
        return Badges
    if name == "shop":
        from .Pages.Shop import Shop
        return Shop
    if name == "play":
        from .Pages.Play import Play
        return Play
    if name == "auth":
        from .Pages.Auth import Auth
        return Auth
    from .Pages.Admin import Admin
    return Admin


def parse(hash_text):
    h = (hash_text or "").lstrip("#").lstrip("!").lstrip("/").split("?")[0]
    parts = [window.decodeURIComponent(p) for p in h.split("/") if p]
    name = parts[0] if parts else ""
    if name.lower() == "admin":  # the old app accepted #Admin, #admin/ ...
        name = "admin"
    return name, parts[1:]


def href(name, *args):
    """'#name/arg1/arg2' with every part URL-encoded."""
    return "#" + "/".join([name] + [window.encodeURIComponent(str(a)) for a in args if a not in (None, "")])


def home_page():
    return "landing"


def current():
    return _r["page"]


def show():
    """Open the page for the current address."""
    name, args = parse(window.location.hash)
    if name not in PAGES:
        name, args = home_page(), []
    who = PAGES[name][0]
    if who == "guest" and state.me():
        name, args = "map", []
        replace("map")
    elif who == "admin" and not state.me():
        _r["after"] = window.location.hash
        name, args = "auth", []
    elif who == "admin" and not state.is_admin():
        state.toast("The level editor is for admins only.", "error")
        name, args = "map", []
        replace("map")
    old = _r["page"]
    if old is not None and hasattr(old, "leave"):
        try:
            old.leave()  # stop timers, engines, input capture
        except Exception as e:
            print("leave failed: %r" % e)
    window.document.title = PAGES[name][1] + " · " + APP_NAME
    window.UI_READY = False
    page = _form(name)(args=args)
    _r["page"] = page
    anvil.open_form(page)
    shell = getattr(page, "layout", None)
    if shell is not None and hasattr(shell, "refresh"):
        shell.refresh(name)  # Anvil reuses the layout between pages: tell it who is signed in and which page is open
    window.scrollTo(0, 0)
    if not getattr(page, "waits", False):
        window.UI_READY = True  # tests and screenshots wait for this (engine pages set it themselves)


def go(name, *args):
    """Go to a page. Same address again = reload the page."""
    target = href(name, *args)
    if window.location.hash == target:
        show()
    else:
        window.location.hash = target


def replace(name, *args):
    """Change the address without opening anything."""
    window.history.replaceState(None, "", href(name, *args))


def after_sign_in():
    """Where to go once someone signs in: the page they were heading for, or the map."""
    target = _r["after"]
    _r["after"] = ""
    if target and target != window.location.hash:
        window.location.hash = target
    else:
        go("map")


def remember_after(target):
    _r["after"] = target


def refresh_shell():
    """Redraw the header (ducats, rank, streak) after a game action on the same page."""
    page = _r["page"]
    shell = getattr(page, "layout", None) if page is not None else None
    if shell is not None and hasattr(shell, "refresh"):
        name, args = parse(window.location.hash)
        shell.refresh(name if name in PAGES else home_page())


def _on_hash(event):
    show()


def start():
    if not _r["listening"]:
        window.addEventListener("hashchange", anvil.js.report_exceptions(_on_hash))
        _r["listening"] = True
    show()
