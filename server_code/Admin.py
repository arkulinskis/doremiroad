# Admin — Server Module. The level editor's server side (#admin). Every callable checks the admin flag.
import re
import secrets

import anvil.server
import anvil.users
from anvil.tables import app_tables

from . import Catalog as C
from . import Game as G
from . import Levels as L


def _admin():
    u = anvil.users.get_user()
    if not G.is_admin(u):
        raise anvil.server.PermissionDenied("Admins only.")
    return u


@anvil.server.callable
def admin_whoami():
    u = anvil.users.get_user()
    if u is None:
        return {"signed_in": False}
    return {"signed_in": True, "email": u["email"], "name": u["display_name"] or (u["email"] or "").split("@")[0],
            "is_admin": G.is_admin(u)}


def _level_out(l):
    errors, warnings = L.check(l["data"])
    return {"key": l["key"], "name": l["name"], "data": l["data"], "published": l["published"], "builtin": l["builtin"],
            "clears": l["clears"], "errors": errors, "warnings": warnings, "items": L.totals(l["data"])["items"]}


@anvil.server.callable
def admin_state():
    _admin()
    G.ensure_seeded()
    jr = G.journey(include_unpublished=True)
    users = list(app_tables.users.search())
    return {
        "ok": True,
        "territories": [{"key": t["key"], "name": t["name"], "emoji": t["emoji"], "blurb": t["blurb"], "color": t["color"],
                         "x": t["x"], "y": t["y"], "published": t["published"],
                         "levels": [_level_out(l) for l in t["levels"]]} for t in jr],
        "catalog": C.public(),
        "stats": {"players": len(users), "clears": sum((l["clears"] or 0) for l in app_tables.levels.search()),
                  "levels": len(app_tables.levels.search())},
        "builtin_keys": [lv["key"] for lv in L.LEVELS],
    }


def _slug(text):
    s = re.sub(r"[^a-z0-9]+", "-", (text or "level").lower()).strip("-")[:30] or "level"
    return "%s-%s" % (s, secrets.token_hex(2))


def _s(v, n):
    return str(v if v is not None else "")[:n]


def _list(v, n, each=40):
    if isinstance(v, str):
        v = v.split()
    return [str(x).strip()[:each] for x in (v or []) if str(x).strip()][:n]


def _clean_step(s):
    t = s.get("t")
    if t == "lesson":
        return {"t": t, "title": _s(s.get("title"), 80), "text": _s(s.get("text"), 1200), "show": _list(s.get("show"), 24),
                "staff": s.get("staff") if s.get("staff") in L.CLEFS else None}
    if t == "notes":
        return {"t": t, "prompt": _s(s.get("prompt"), 160), "notes": _list(s.get("notes"), 64),
                "labels": [_s(x, 80) for x in (s.get("labels") or [])][:64],
                "show": s.get("show") if s.get("show") in L.SHOW_MODES else "keys",
                "clef": s.get("clef") if s.get("clef") in L.CLEFS else "treble", "exact": bool(s.get("exact"))}
    if t == "chords":
        return {"t": t, "prompt": _s(s.get("prompt"), 160), "chords": _list(s.get("chords"), 32),
                "labels": [_s(x, 80) for x in (s.get("labels") or [])][:32], "hint": bool(s.get("hint")),
                "exact": bool(s.get("exact"))}
    if t == "progression":
        return {"t": t, "prompt": _s(s.get("prompt"), 160), "key": _s(s.get("key"), 6).strip(),
                "numerals": _list(s.get("numerals"), 32, 10), "hint": bool(s.get("hint")), "names": bool(s.get("names"))}
    if t == "rush":
        return {"t": t, "prompt": _s(s.get("prompt"), 160), "seq": " ".join(_s(s.get("seq"), 4000).split()),
                "bpm": L._int(s.get("bpm"), 30, 240, 90), "hint": bool(s.get("hint")), "exact": bool(s.get("exact"))}
    if t == "ear":
        mode = s.get("mode") if s.get("mode") in L.EAR_MODES else "note"
        pool = s.get("pool") or []
        pool = _list(pool, 16) if mode != "chord" else [str(x)[:20] for x in pool if str(x).strip()][:8]
        return {"t": t, "prompt": _s(s.get("prompt"), 160), "mode": mode, "pool": pool,
                "count": L._int(s.get("count"), 1, 12, 4)}
    if t == "quiz":
        opts = [_s(o, 120) for o in (s.get("options") or [])][:6]
        return {"t": t, "q": _s(s.get("q"), 240), "options": opts, "answer": L._int(s.get("answer"), 0, 5, 0),
                "explain": _s(s.get("explain"), 400)}
    return None


def clean_data(d):
    """Keep only what the game understands; reject anything that isn't a level."""
    if not isinstance(d, dict):
        raise ValueError("Level data must be an object.")
    steps = [x for x in (_clean_step(s) for s in (d.get("steps") or [])[:40] if isinstance(s, dict)) if x]
    cards = d.get("cards") or {}
    return {"intro": _s(d.get("intro"), 400), "steps": steps,
            "pass": L._int(d.get("pass"), 0, 100, L.DEFAULT_PASS), "two": L._int(d.get("two"), 0, 100, L.DEFAULT_TWO),
            "three": L._int(d.get("three"), 0, 100, L.DEFAULT_THREE),
            "codex": [k for k in dict.fromkeys(d.get("codex") or []) if k in C.CODEX_BY_KEY],
            "cards": {w: cards[w] for w in ("clear", "three") if cards.get(w) in C.COMPOSER_BY_KEY},
            "trial": bool(d.get("trial"))}


def _territory(key):
    t = app_tables.territories.get(key=key)
    if t is None:
        raise ValueError("Unknown territory.")
    return t


@anvil.server.callable
def save_level(spec):
    """Create or update a level. A level with errors is saved as a draft (unpublished)."""
    _admin()
    try:
        data = clean_data(spec.get("data"))
        terr = _territory(spec.get("territory"))
    except (ValueError, TypeError) as e:
        return {"ok": False, "error": str(e)}
    errors, warnings = L.check(data)
    publish = bool(spec.get("published")) and not errors
    name = (str(spec.get("name") or "").strip() or "Untitled level")[:40]
    row = app_tables.levels.get(key=spec["key"]) if spec.get("key") else None
    if row is None:
        siblings = [l for l in app_tables.levels.search() if l["territory"] == terr]
        row = app_tables.levels.add_row(key=_slug(name), territory=terr, name=name, data=data, published=publish,
                                        updated=G._now(), builtin=False, clears=0,
                                        position=float(max([l["position"] or 0 for l in siblings] + [-1]) + 1))
    else:
        if row["territory"] != terr:
            siblings = [l for l in app_tables.levels.search() if l["territory"] == terr]
            row["position"] = float(max([l["position"] or 0 for l in siblings] + [-1]) + 1)
        row.update(territory=terr, name=name, data=data, published=publish, updated=G._now())
    out = admin_state()
    out.update(saved=row["key"], errors=errors, warnings=warnings,
               note="Saved as a draft: fix the errors to publish it." if spec.get("published") and errors else None)
    return out


@anvil.server.callable
def delete_level(key):
    _admin()
    row = app_tables.levels.get(key=key)
    if row is not None:
        for s in app_tables.scores.search(level=row):
            s.delete()
        row.delete()
    return admin_state()


@anvil.server.callable
def move_level(key, step):
    _admin()
    row = app_tables.levels.get(key=key)
    if row is None:
        return admin_state()
    sibs = sorted([l for l in app_tables.levels.search() if l["territory"] == row["territory"]],
                  key=lambda r: (r["position"] or 0, r["name"] or ""))
    i = sibs.index(row)
    j = max(0, min(len(sibs) - 1, i + (1 if step > 0 else -1)))
    sibs.insert(j, sibs.pop(i))
    for n, l in enumerate(sibs):
        l["position"] = float(n)
    return admin_state()


@anvil.server.callable
def save_territory(spec):
    _admin()
    name = (str(spec.get("name") or "").strip() or "New territory")[:40]
    color = str(spec.get("color") or "")
    fields = {"name": name, "emoji": (str(spec.get("emoji") or "\U0001F3B5"))[:8], "blurb": str(spec.get("blurb") or "")[:240],
              "color": color if re.match(r"^#[0-9a-fA-F]{6}$", color) else C.COLORS[0],
              "x": float(L._int(spec.get("x"), 3, 97, 50)), "y": float(L._int(spec.get("y"), 3, 97, 50)),
              "published": bool(spec.get("published", True))}
    row = app_tables.territories.get(key=spec["key"]) if spec.get("key") else None
    if row is None:
        pos = max([t["position"] or 0 for t in app_tables.territories.search()] + [-1]) + 1
        app_tables.territories.add_row(key=_slug(name), position=float(pos), **fields)
    else:
        row.update(**fields)
    return admin_state()


@anvil.server.callable
def move_territory(key, step):
    _admin()
    rows = sorted(app_tables.territories.search(), key=lambda r: (r["position"] or 0, r["name"] or ""))
    row = next((r for r in rows if r["key"] == key), None)
    if row is not None:
        i = rows.index(row)
        j = max(0, min(len(rows) - 1, i + (1 if step > 0 else -1)))
        rows.insert(j, rows.pop(i))
        for n, r in enumerate(rows):
            r["position"] = float(n)
    return admin_state()


@anvil.server.callable
def delete_territory(key):
    _admin()
    row = app_tables.territories.get(key=key)
    if row is not None:
        if any(l["territory"] == row for l in app_tables.levels.search()):
            out = admin_state()
            out.update(ok=False, error="Move or delete this territory's levels first.")
            return out
        row.delete()
    return admin_state()


@anvil.server.callable
def restore_level(key):
    """Put a built-in level back to how it shipped."""
    _admin()
    lv = next((x for x in L.LEVELS if x["key"] == key), None)
    row = app_tables.levels.get(key=key)
    if lv and row is not None:
        row.update(data=lv["data"], name=lv["name"], updated=G._now())
    return admin_state()


@anvil.server.callable
def restore_defaults():
    """Add back any built-in territories or levels that were deleted (edited ones are left alone)."""
    _admin()
    n = G.seed_defaults()
    out = admin_state()
    out["note"] = "Restored %d missing item(s)." % n if n else "Nothing was missing."
    return out


@anvil.server.callable
def list_players():
    _admin()
    jr = G.journey()
    out = []
    for u in app_tables.users.search():
        p = G.normalize(u["progress"]) if u["progress"] else G.new_progress()
        st = G.status(p, jr)
        out.append({"email": u["email"], "name": u["display_name"] or "", "is_admin": bool(u["is_admin"]),
                    "signed_up": G._iso(u["signed_up"]), "last_played": G._iso(u["last_played"]),
                    "rank": st["rank"]["name"], "xp": p["xp"], "stars": st["stars"], "cleared": len(st["cleared"]),
                    "conquered": len(st["conquered"]), "codex": len(p["codex"]), "cards": len(p["cards"]),
                    "streak": p["daily"]["streak"]})
    out.sort(key=lambda r: r["last_played"] or "", reverse=True)
    return {"ok": True, "players": out[:500]}


@anvil.server.callable
def set_admin(email, flag):
    me = _admin()
    u = app_tables.users.get(email=email)
    if u is None:
        return {"ok": False, "error": "No such player."}
    if u == me and not flag:
        return {"ok": False, "error": "You can't remove your own admin rights."}
    u["is_admin"] = bool(flag)
    return list_players()

