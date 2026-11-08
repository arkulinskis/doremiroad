"""The player's game state in the browser and the lookups every page uses (was the `st` object of the old GamePage).

    game.ready()             the road has been loaded this visit
    game.ensure()            load it if needed (guest progress from this browser, or the account's); False = failed
    game.act(name, *args)    a game action (finish_level, finish_daily, buy, equip): guests send their progress along
                             and the guest_* twin runs; returns the reply (with "report") or None after a toast
    game.S                   {me, progress, status, journey, catalog, daily, today, guest, sel}
    game.rec(key) / unlocked(key) / terr_state(t) / current_terr() / next_level(key) / find_level(key) ...
The server checks every result; this file only mirrors what it sends.
"""
import anvil.server

from . import dr, state

GUEST_KEY = "dr.guest"  # the JavaScript version's browser key: guest progress carries over
S: dict = {"me": None, "progress": None, "status": None, "journey": [], "catalog": None, "daily": None, "today": "",
     "guest": True, "sel": None, "loaded": False}
C: dict = {"codex": {}, "composers": {}, "badges": {}, "shop": {}}


def ready():
    return bool(S["loaded"])


def reset():
    S.update({"loaded": False, "me": None, "progress": None, "status": None, "sel": None})


def _set_catalog(c):
    S["catalog"] = c
    C["codex"] = {x["key"]: x for x in c["codex"]}
    C["composers"] = {x["key"]: x for x in c["composers"]}
    C["badges"] = {x["key"]: x for x in c["badges"]}
    C["shop"] = {k: {x["key"]: x for x in v} for k, v in c["shop"].items()}


def apply(r):
    if not r or not r.get("ok"):
        return r
    if r.get("catalog"):
        _set_catalog(r["catalog"])
    if r.get("journey") is not None:
        S["journey"] = r["journey"]
    for k in ("me", "progress", "status", "daily", "today"):
        if k in r and r[k] is not None:
            S[k] = r[k]
    if S["guest"]:
        dr.store_set(GUEST_KEY, S["progress"])
    S["loaded"] = True
    return r


def _call(fn, *args):
    try:
        return anvil.server.call(fn, *args)
    except anvil.server.AppOfflineError:
        return {"ok": False, "error": "You seem to be offline. Check your connection and try again."}
    except Exception as e:
        name = type(e).__name__
        if name == "SessionExpiredError":
            return {"ok": False, "error": "Your session expired. Reload the page and sign in again."}
        if name == "PermissionDenied":
            return {"ok": False, "error": str(e) or "Please sign in."}
        print("server call %s failed: %r" % (fn, e))
        return {"ok": False, "error": "Something went wrong on the road. Please try again."}


def load():
    S["guest"] = state.me() is None
    if S["guest"]:
        r = _call("guest_state", dr.store_get(GUEST_KEY, None), dr.today())
    else:
        r = _call("get_state", dr.today())
    if not r or not r.get("ok"):
        state.toast((r or {}).get("error") or "Could not load the road.", "error")
        return None
    return apply(r)


def ensure():
    """Load the road once per visit (and again after signing in or out)."""
    if S["loaded"] and S["guest"] == (state.me() is None):
        return True
    return load() is not None


def act(name, *args):
    if S["guest"]:
        r = _call("guest_" + name, S["progress"], *args, dr.today())
    else:
        r = _call(name, *args, dr.today())
    if not r or not r.get("ok"):
        state.toast((r or {}).get("error") or "Something went wrong.", "error")
        return None
    return apply(r)


def signed_in():
    """After signing in or up: bring the guest's browser progress along (once), then load the account's road."""
    S["guest"] = False
    g = dr.store_get(GUEST_KEY, None)
    r = _call("import_guest", g, dr.today()) if g else _call("get_state", dr.today())
    if not r or not r.get("ok"):
        state.toast((r or {}).get("error") or "Could not load your progress.", "error")
        S["loaded"] = False
        return False
    apply(r)
    if g:
        dr.store_del(GUEST_KEY)
    return True


def rename(name):
    r = _call("set_name", name, dr.today())
    if not r or not r.get("ok"):
        state.toast((r or {}).get("error") or "Could not rename.", "error")
        return False
    apply(r)
    return True


def leaderboard(key):
    try:
        return anvil.server.call_s("leaderboard", key)
    except Exception:
        return None


# ---------------------------------------------------------------- lookups
def rec(key):
    return (S["progress"].get("levels") or {}).get(key) or {"stars": 0, "best": 0, "score": 0, "clears": 0}


def unlocked(key):
    return key in S["status"]["unlocked"]


def all_levels():
    return [{"t": t, "l": l, "i": i} for t in S["journey"] for i, l in enumerate(t["levels"])]


def find_level(key):
    for x in all_levels():
        if x["l"]["key"] == key:
            return x
    return None


def find_terr(key):
    for t in S["journey"]:
        if t["key"] == key:
            return t
    return None


def terr_state(t):
    st = S["status"]
    if t["key"] in st["mastered"]:
        return "mastered"
    if t["key"] in st["conquered"]:
        return "conquered"
    return "open" if any(unlocked(l["key"]) for l in t["levels"]) else "locked"


def current_terr():
    for t in S["journey"]:
        if any(unlocked(l["key"]) and not rec(l["key"])["stars"] for l in t["levels"]):
            return t
    opened = [t for t in S["journey"] if terr_state(t) != "locked"]
    return opened[-1] if opened else (S["journey"][0] if S["journey"] else None)


def next_level(key):
    al = all_levels()
    idx = next((i for i, x in enumerate(al) if x["l"]["key"] == key), -1)
    for x in al[idx + 1:]:
        if unlocked(x["l"]["key"]):
            return x
    return None


def codex_where():
    w = {}
    for x in all_levels():
        for k in x["l"]["data"].get("codex") or []:
            w.setdefault(k, x)
    return w


def card_where():
    w = {}
    for x in all_levels():
        cards = x["l"]["data"].get("cards") or {}
        for how in ("clear", "three"):
            k = cards.get(how)
            if k and k not in w:
                w[k] = {"x": x, "how": how}
    return w


def banner_colour():
    b = C["shop"].get("banners", {}).get(S["progress"]["equip"].get("banners"))
    return b["color"] if b else "#c8434e"


def stars_text(n, total=3):
    return "★" * int(n) + "☆" * (total - int(n))


def can_buy_any():
    p = S["progress"]
    for kind, items in S["catalog"]["shop"].items():
        for x in items:
            if 0 < x["price"] <= p["ducats"] and x["key"] not in p["owned"][kind]:
                return True
    return False


def step_icons(data):
    out = []
    for s in data.get("steps") or []:
        ic = dr.step_icon(s.get("t"))
        if ic and ic not in out:
            out.append(ic)
    return " ".join(out)


def rank_line():
    r = S["status"]["rank"]
    if r.get("next"):
        return "%s / %s XP" % (dr.fmt(r["xp"]), dr.fmt(r["next"]))
    return "%s XP" % dr.fmt(r["xp"])


def rank_pct():
    r = S["status"]["rank"]
    if not r.get("next"):
        return 100
    return int(round(100.0 * (r["xp"] - r["from"]) / max(1, r["next"] - r["from"])))
