# Game — Server Module. Everything a player does: load the road, finish levels, daily practice, shop.
#
# Progress is one Simple Object per player (users.progress). Guests keep the same object in their
# browser and send it with each call (the guest_* functions), so every rule lives here once:
# the apply_* functions take a progress dict and return a new one plus a report for the results screen.
import datetime as dt
import random
import re

import anvil.server
import anvil.tables as tables
import anvil.users
from anvil.tables import app_tables

from . import Catalog as C
from . import Levels as L

# Accounts with these emails become admins the first time they sign in (users.is_admin can also be ticked by hand).
ADMIN_EMAILS = {"arkulinskis@gmail.com"}

STAT_KEYS = ("notes", "chords", "ear", "quiz", "perfects", "runs", "flawless", "max_combo", "midi_runs", "dailies",
             "xp_earned", "ducats_earned")


def _now():
    return dt.datetime.now(dt.timezone.utc)


def _iso(d):
    return d.isoformat() if d else None


def _client_today(today):
    """The player's local date, accepted only within a day of UTC (it drives the daily practice)."""
    utc = _now().date()
    try:
        d = dt.date.fromisoformat(str(today)[:10])
        if abs((d - utc).days) <= 1:
            return d
    except Exception:
        pass
    return utc


# ---------------------------------------------------------------- seeding and the road

def ensure_seeded():
    if len(app_tables.territories.search()) == 0:
        seed_defaults()


def seed_defaults():
    """Add the built-in territories and levels that aren't in the tables yet. Returns how many were added."""
    added = 0
    have_t = {r["key"]: r for r in app_tables.territories.search()}
    for i, t in enumerate(L.TERRITORIES):
        if t["key"] not in have_t:
            have_t[t["key"]] = app_tables.territories.add_row(
                key=t["key"], name=t["name"], emoji=t["emoji"], blurb=t["blurb"], color=t["color"],
                x=float(t["x"]), y=float(t["y"]), position=float(i), published=True)
            added += 1
    have_l = {r["key"] for r in app_tables.levels.search()}
    pos = {}
    for lv in L.LEVELS:
        pos[lv["territory"]] = pos.get(lv["territory"], -1) + 1
        if lv["key"] not in have_l:
            app_tables.levels.add_row(key=lv["key"], territory=have_t[lv["territory"]], name=lv["name"],
                                      position=float(pos[lv["territory"]]), data=lv["data"], published=True,
                                      updated=_now(), builtin=True, clears=0)
            added += 1
    return added


def journey(include_unpublished=False):
    """Territories in order, each with its levels in order (published only, unless asked)."""
    out = []
    levels = {}
    for lv in app_tables.levels.search():
        if (lv["published"] or include_unpublished) and lv["territory"] is not None:
            levels.setdefault(lv["territory"]["key"], []).append(lv)
    for t in sorted(app_tables.territories.search(), key=lambda r: (r["position"] or 0, r["name"] or "")):
        if not (t["published"] or include_unpublished):
            continue
        rows = sorted(levels.get(t["key"], []), key=lambda r: (r["position"] or 0, r["name"] or ""))
        out.append({"key": t["key"], "name": t["name"], "emoji": t["emoji"] or "\U0001F3B5", "blurb": t["blurb"] or "",
                    "color": t["color"] or "#8b93b8", "x": t["x"] if t["x"] is not None else 50,
                    "y": t["y"] if t["y"] is not None else 50, "published": bool(t["published"]),
                    "levels": [{"key": r["key"], "name": r["name"], "data": r["data"], "published": bool(r["published"]),
                                "builtin": bool(r["builtin"]), "clears": r["clears"] or 0, "_row": r} for r in rows]})
    return out


def _public_journey(jr):
    return [{k: t[k] for k in ("key", "name", "emoji", "blurb", "color", "x", "y")} |
            {"levels": [{"key": l["key"], "name": l["name"], "data": l["data"]} for l in t["levels"]]}
            for t in jr]


# ---------------------------------------------------------------- progress

def new_progress():
    return {"v": 1, "xp": 0, "ducats": 0, "levels": {}, "codex": [], "cards": {}, "badges": {},
            "stats": {k: 0 for k in STAT_KEYS}, "daily": {"last": None, "streak": 0, "best": 0},
            "owned": {kind: [C.DEFAULTS[kind]] for kind in C.SHOP}, "equip": dict(C.DEFAULTS)}


def _int(v, lo=0, hi=10 ** 7):
    try:
        v = int(v)
    except Exception:
        return lo
    return max(lo, min(hi, v))


def _num(v, lo, hi):
    try:
        v = float(v)
    except Exception:
        return lo
    if v != v:  # NaN
        return lo
    return max(lo, min(hi, v))


def normalize(p):
    """A clean copy of a progress dict: known keys only, sane numbers (guests send theirs from the browser)."""
    base = new_progress()
    if not isinstance(p, dict):
        return base
    base["xp"] = _int(p.get("xp"), 0, 10 ** 7)
    base["ducats"] = _int(p.get("ducats"), 0, 10 ** 6)
    for k, v in (p.get("levels") or {}).items():
        if isinstance(v, dict) and isinstance(k, str) and len(k) < 80:
            base["levels"][k] = {"stars": _int(v.get("stars"), 0, 3), "best": _num(v.get("best"), 0, 100),
                                 "score": _int(v.get("score"), 0, 10 ** 7), "clears": _int(v.get("clears"), 0, 10 ** 5),
                                 "c1": bool(v.get("c1")), "c3": bool(v.get("c3"))}
    base["codex"] = [k for k in dict.fromkeys(p.get("codex") or []) if k in C.CODEX_BY_KEY]
    for k, v in (p.get("cards") or {}).items():
        if k in C.COMPOSER_BY_KEY and _int(v) > 0:
            base["cards"][k] = _int(v, 0, 999)
    for k, v in (p.get("badges") or {}).items():
        if k in C.BADGE_KEYS:
            base["badges"][k] = str(v)[:10]
    for k in STAT_KEYS:
        base["stats"][k] = _int((p.get("stats") or {}).get(k), 0, 10 ** 7)
    d = p.get("daily") or {}
    base["daily"] = {"last": str(d.get("last"))[:10] if d.get("last") else None,
                     "streak": _int(d.get("streak"), 0, 10 ** 4), "best": _int(d.get("best"), 0, 10 ** 4)}
    owned = p.get("owned") or {}
    for kind in C.SHOP:
        keys = [x for x in (owned.get(kind) or []) if x in C.SHOP_BY_KEY[kind]]
        base["owned"][kind] = [C.DEFAULTS[kind]] + [x for x in dict.fromkeys(keys) if x != C.DEFAULTS[kind]]
        e = (p.get("equip") or {}).get(kind)
        base["equip"][kind] = e if e in base["owned"][kind] else C.DEFAULTS[kind]
    return base


def rank_of(xp):
    idx = 0
    for i, (need, _) in enumerate(C.RANKS):
        if xp >= need:
            idx = i
    nxt = C.RANKS[idx + 1][0] if idx + 1 < len(C.RANKS) else None
    return {"idx": idx, "name": C.RANKS[idx][1], "xp": xp, "from": C.RANKS[idx][0], "next": nxt}


def status(p, jr):
    """What's unlocked, cleared and conquered, plus totals the screens show."""
    unlocked, conquered, mastered, cleared = [], [], [], []
    prev_conquered = True
    for t in jr:
        keys = [l["key"] for l in t["levels"]]
        done = [k for k in keys if p["levels"].get(k, {}).get("stars", 0) >= 1]
        cleared += done
        if prev_conquered:
            for i, k in enumerate(keys):
                if i == 0 or keys[i - 1] in done:
                    unlocked.append(k)
        t_conq = prev_conquered and bool(keys) and len(done) == len(keys)
        if t_conq:
            conquered.append(t["key"])
            if all(p["levels"].get(k, {}).get("stars", 0) >= 3 for k in keys):
                mastered.append(t["key"])
        prev_conquered = t_conq or not keys and prev_conquered
    all_keys = [l["key"] for t in jr for l in t["levels"]]
    return {
        "unlocked": unlocked, "cleared": cleared, "conquered": conquered, "mastered": mastered,
        "stars": sum(p["levels"].get(k, {}).get("stars", 0) for k in all_keys), "stars_max": 3 * len(all_keys),
        "levels_max": len(all_keys), "territories_max": len([t for t in jr if t["levels"]]),
        "codex": len(p["codex"]), "codex_max": len(C.CODEX), "cards": len(p["cards"]), "cards_max": len(C.COMPOSERS),
        "rank": rank_of(p["xp"]),
    }


def check_badges(p, jr, today):
    st = status(p, jr)
    have = p["badges"]
    tests = {
        "first_note": len(st["cleared"]) >= 1,
        "road_10": len(st["cleared"]) >= 10,
        "road_25": len(st["cleared"]) >= 25,
        "road_all": st["levels_max"] > 0 and len(st["cleared"]) >= st["levels_max"],
        "stars_30": st["stars"] >= 30,
        "stars_75": st["stars"] >= 75,
        "first_flag": len(st["conquered"]) >= 1,
        "flags_5": len(st["conquered"]) >= 5,
        "flags_all": st["territories_max"] > 0 and len(st["conquered"]) >= st["territories_max"],
        "mastery": len(st["mastered"]) >= 1,
        "codex_10": len(p["codex"]) >= 10,
        "codex_all": len(p["codex"]) >= len(C.CODEX),
        "cards_5": len(p["cards"]) >= 5,
        "cards_all": len(p["cards"]) >= len(C.COMPOSERS),
        "daily_3": p["daily"]["best"] >= 3,
        "daily_7": p["daily"]["best"] >= 7,
        "daily_30": p["daily"]["best"] >= 30,
        "stylist": any(len(v) > 1 for v in p["owned"].values()),
        "virtuoso": st["rank"]["idx"] >= 6,
    }
    new = []
    for b in C.BADGES:
        if b["key"] in have:
            continue
        ok = p["stats"].get(b["stat"], 0) >= b["at"] if "stat" in b else tests.get(b["key"])
        if ok:
            have[b["key"]] = today.isoformat()
            new.append(b["key"])
    return new


def view(p, jr, today, me, full=True):
    """What the client needs. Actions send full=False: the road and catalog don't change."""
    st = status(p, jr)
    dl = L.daily(today, L.daily_tier(len(st["conquered"])))
    out = {"me": me, "progress": p, "status": st, "today": today.isoformat(),
           "daily": {"level": dl, "done": p["daily"]["last"] == today.isoformat(), "streak": p["daily"]["streak"]}}
    if full:
        out.update(journey=_public_journey(jr), catalog=C.public())
    return out


# ---------------------------------------------------------------- the rules

class GameError(Exception):
    pass


def _score_run(data, result):
    """Check a run's result against what the level holds. Returns (accuracy %, clean numbers)."""
    tot = L.totals(data)
    result = result if isinstance(result, dict) else {}
    if _int(result.get("items"), -1, 10 ** 6) != tot["items"]:
        raise GameError("This level was changed while you played. Reload the page and try again.")
    items = tot["items"]
    hits = _num(result.get("hits"), 0, items)
    acc = 100.0 if items == 0 else round(100.0 * hits / items, 1)
    clean = {
        "items": items, "hits": hits, "accuracy": acc,
        "score": _int(result.get("score"), 0, items * 150 + 100),
        "combo": _int(result.get("combo"), 0, tot["rush"]),
        "perfects": _int(result.get("perfects"), 0, tot["rush"]),
        "notes": _int(result.get("notes"), 0, tot["notes"] + tot["rush_notes"]),
        "chords": _int(result.get("chords"), 0, tot["chords"] + tot["rush_chords"]),
        "ear": _int(result.get("ear"), 0, tot["ear"]),
        "quiz": _int(result.get("quiz"), 0, tot["quiz"]),
        "time": _num(result.get("time"), 1, 24 * 3600),
        "midi": bool(result.get("midi")),
    }
    return acc, clean


def _stars(data, acc):
    two = _int(data.get("two"), 0, 100) if data.get("two") is not None else L.DEFAULT_TWO
    three = _int(data.get("three"), 0, 100) if data.get("three") is not None else L.DEFAULT_THREE
    return 1 + (acc >= two) + (acc >= three)


def _add_stats(p, clean):
    s = p["stats"]
    for k in ("notes", "chords", "ear", "quiz", "perfects"):
        s[k] += clean[k]
    s["runs"] += 1
    s["max_combo"] = max(s["max_combo"], clean["combo"])
    if clean["items"] and clean["accuracy"] >= 100:
        s["flawless"] += 1
    if clean["midi"]:
        s["midi_runs"] += 1


def _give_card(p, key, report):
    """Add a composer card. A duplicate is sold for ducats instead."""
    if not key or key not in C.COMPOSER_BY_KEY:
        return
    if p["cards"].get(key):
        coins = C.RARITY[C.COMPOSER_BY_KEY[key]["rarity"]]["dupe"]
        p["cards"][key] += 1
        p["ducats"] += coins
        report.setdefault("dupes", []).append({"card": key, "ducats": coins})
    else:
        p["cards"][key] = 1
        report.setdefault("cards", []).append(key)


def apply_finish(p, lv, jr, result, today):
    """Score a cleared level. `result` comes from the browser, so it is checked against what the level holds."""
    key = lv["key"]
    before = status(p, jr)
    if key not in before["unlocked"]:
        raise GameError("That level isn't unlocked yet.")
    data = lv["data"] or {}
    acc, clean = _score_run(data, result)
    need = _int(data.get("pass"), 0, 100) if data.get("pass") is not None else L.DEFAULT_PASS
    if acc < need:
        raise GameError("You need %d%% accuracy to clear this level." % need)
    stars = _stars(data, acc)
    rec = p["levels"].get(key) or {"stars": 0, "best": 0.0, "score": 0, "clears": 0, "c1": False, "c3": False}
    first_clear = rec["stars"] == 0
    new_stars = max(0, stars - rec["stars"])
    new_best = acc > rec["best"]
    new_hi = clean["score"] > rec["score"]
    rec.update(stars=max(rec["stars"], stars), best=max(rec["best"], acc), score=max(rec["score"], clean["score"]),
               clears=rec["clears"] + 1)
    report = {"level": key, "accuracy": acc, "stars": stars, "new_stars": new_stars, "first_clear": first_clear,
              "best": rec["best"], "new_best": new_best and not first_clear, "score": clean["score"],
              "high_score": rec["score"], "new_high": new_hi and not first_clear, "combo": clean["combo"]}
    # Cards: once per level each.
    cards = data.get("cards") or {}
    if cards.get("clear") and not rec["c1"]:
        rec["c1"] = True
        _give_card(p, cards["clear"], report)
    if cards.get("three") and stars >= 3 and not rec["c3"]:
        rec["c3"] = True
        _give_card(p, cards["three"], report)
    p["levels"][key] = rec
    # Codex pages.
    new_codex = [k for k in data.get("codex") or [] if k in C.CODEX_BY_KEY and k not in p["codex"]]
    p["codex"] += new_codex
    # XP and ducats.
    R = C.REWARDS
    xp_parts, d_parts = [], []
    if first_clear:
        xp_parts.append(("First clear", R["xp_first"] + R["xp_per_item"] * clean["items"]))
        d_parts.append(("First clear", R["ducats_first"]))
    else:
        xp_parts.append(("Practice", R["xp_replay"] + clean["items"] // 2))
        d_parts.append(("Practice", R["ducats_replay"] + R["ducats_replay_star"] * stars))
    if new_stars:
        xp_parts.append(("New stars", R["xp_star"] * new_stars))
        d_parts.append(("New stars", R["ducats_star"] * new_stars))
    xp = sum(v for _, v in xp_parts)
    ducats = sum(v for _, v in d_parts)
    p["xp"] += xp
    p["ducats"] += ducats
    p["stats"]["xp_earned"] += xp
    p["stats"]["ducats_earned"] += ducats
    _add_stats(p, clean)
    after = status(p, jr)
    terr = next((t for t in jr if any(l["key"] == key for l in t["levels"])), None)
    report.update(
        xp=xp, ducats=ducats, xp_parts=[list(x) for x in xp_parts], ducat_parts=[list(x) for x in d_parts],
        codex=new_codex, unlocked=[k for k in after["unlocked"] if k not in before["unlocked"]],
        territory=terr["key"] if terr else None,
        conquered=terr["key"] if terr and terr["key"] in after["conquered"] and terr["key"] not in before["conquered"] else None,
        mastered=terr["key"] if terr and terr["key"] in after["mastered"] and terr["key"] not in before["mastered"] else None,
        rank_up=after["rank"]["name"] if after["rank"]["idx"] > before["rank"]["idx"] else None,
        new_badges=check_badges(p, jr, today))
    return p, report


def apply_daily(p, jr, today, result):
    """Daily practice: rewards once a day, a streak for consecutive days and a chance of a composer card."""
    st = status(p, jr)
    dl = L.daily(today, L.daily_tier(len(st["conquered"])))
    acc, clean = _score_run(dl["data"], result)
    if acc < dl["data"]["pass"]:
        raise GameError("You need %d%% accuracy to complete the daily practice." % dl["data"]["pass"])
    _add_stats(p, clean)
    d = p["daily"]
    report = {"daily": True, "accuracy": acc, "stars": _stars(dl["data"], acc), "score": clean["score"],
              "combo": clean["combo"], "xp": 0, "ducats": 0, "xp_parts": [], "ducat_parts": [], "codex": [],
              "unlocked": [], "conquered": None, "mastered": None, "rank_up": None}
    if d["last"] == today.isoformat():
        report["repeat"] = True
        report["new_badges"] = check_badges(p, jr, today)
        return p, report
    yesterday = (today - dt.timedelta(days=1)).isoformat()
    d["streak"] = d["streak"] + 1 if d["last"] == yesterday else 1
    d["best"] = max(d["best"], d["streak"])
    d["last"] = today.isoformat()
    R = C.REWARDS
    ducats = R["daily_ducats"] + R["daily_streak_bonus"] * (min(d["streak"], R["daily_streak_cap"]) - 1)
    xp = R["xp_daily"]
    p["ducats"] += ducats
    p["xp"] += xp
    p["stats"]["dailies"] += 1
    p["stats"]["xp_earned"] += xp
    p["stats"]["ducats_earned"] += ducats
    report.update(xp=xp, ducats=ducats, streak=d["streak"], xp_parts=[["Daily practice", xp]],
                  ducat_parts=[["Daily practice", R["daily_ducats"]]] +
                  ([["Streak bonus", ducats - R["daily_ducats"]]] if ducats > R["daily_ducats"] else []))
    pool = [c["key"] for c in C.COMPOSERS if c["rarity"] in ("common", "rare") and not p["cards"].get(c["key"])]
    if pool and random.random() < R["daily_card_chance"]:
        _give_card(p, random.choice(pool), report)
    rank_before = rank_of(p["xp"] - xp)["idx"]
    if rank_of(p["xp"])["idx"] > rank_before:
        report["rank_up"] = rank_of(p["xp"])["name"]
    report["new_badges"] = check_badges(p, jr, today)
    return p, report


def apply_buy(p, kind, key, jr, today):
    item = C.SHOP_BY_KEY.get(kind, {}).get(key)
    if not item:
        raise GameError("That isn't in the shop.")
    if key in p["owned"][kind]:
        raise GameError("You already own it.")
    if p["ducats"] < item["price"]:
        raise GameError("Not enough ducats.")
    p["ducats"] -= item["price"]
    p["owned"][kind].append(key)
    p["equip"][kind] = key
    return p, {"kind": kind, "key": key, "new_badges": check_badges(p, jr, today)}


def apply_equip(p, kind, key):
    if kind not in C.SHOP or key not in p["owned"][kind]:
        raise GameError("You don't own that yet.")
    p["equip"][kind] = key
    return p, {"kind": kind, "key": key}


# ---------------------------------------------------------------- signed-in players

def _user():
    u = anvil.users.get_user()
    if u is None:
        raise anvil.server.PermissionDenied("Please sign in.")
    return u


def is_admin(u):
    if u is None:
        return False
    if u["is_admin"]:
        return True
    if (u["email"] or "").lower() in ADMIN_EMAILS:
        u["is_admin"] = True
        return True
    return False


def _me(u):
    return {"name": u["display_name"] or (u["email"] or "Player").split("@")[0], "email": u["email"],
            "is_admin": is_admin(u), "guest": False}


def _load(u):
    return normalize(u["progress"]) if u["progress"] else new_progress()


def _ok(p, jr, today, me, report=None, full=True):
    out = view(p, jr, today, me, full)
    out["ok"] = True
    if report is not None:
        out["report"] = report
    return out


def _run(fn, *args):
    try:
        return fn(*args)
    except GameError as e:
        return {"ok": False, "error": str(e)}


def _level_row(level_key, jr):
    for t in jr:
        for l in t["levels"]:
            if l["key"] == level_key:
                return l
    raise GameError("That level doesn't exist any more.")


@anvil.server.callable
def get_state(today=None):
    ensure_seeded()
    u = _user()
    t = _client_today(today)
    jr = journey()
    p = _load(u)
    if u["progress"] is None:
        u["progress"] = p
    u["last_played"] = _now()
    if not u["display_name"]:
        u["display_name"] = (u["email"] or "Player").split("@")[0][:24]
    return _ok(p, jr, t, _me(u))


def _user_action(today, fn):
    u = _user()
    t = _client_today(today)
    jr = journey()

    def go():
        p, report = fn(_load(u), jr, t)
        u["progress"] = p
        u["last_played"] = _now()
        return _ok(p, jr, t, _me(u), report, full=False)
    return _run(go)


@anvil.server.callable
def finish_level(level_key, result, today=None):
    u = _user()

    def fn(p, jr, t):
        lv = _level_row(level_key, jr)
        p, report = apply_finish(p, lv, jr, result, t)
        row = lv["_row"]
        row["clears"] = (row["clears"] or 0) + 1
        _save_score(u, row, report["score"], report["accuracy"], p["levels"][level_key]["stars"])
        report["leaderboard"] = _board(row, u)
        return p, report
    return _user_action(today, fn)


@anvil.server.callable
def finish_daily(result, today=None):
    return _user_action(today, lambda p, jr, t: apply_daily(p, jr, t, result))


@anvil.server.callable
def buy(kind, key, today=None):
    return _user_action(today, lambda p, jr, t: apply_buy(p, kind, key, jr, t))


@anvil.server.callable
def equip(kind, key, today=None):
    return _user_action(today, lambda p, jr, t: apply_equip(p, kind, key))


@anvil.server.callable
def set_name(name, today=None):
    u = _user()
    name = re.sub(r"\s+", " ", str(name or "")).strip()[:24]
    if len(name) < 2:
        return {"ok": False, "error": "Pick a name with at least 2 letters."}
    u["display_name"] = name
    return get_state(today)


@anvil.server.callable
def import_guest(progress, today=None):
    """After sign-up: adopt the guest's browser progress if the account has none yet."""
    u = _user()
    mine = _load(u)
    g = normalize(progress)
    if not mine["levels"] and not mine["xp"] and (g["levels"] or g["xp"] or g["ducats"]):
        jr = journey()
        known = {l["key"] for t in jr for l in t["levels"]}
        g["levels"] = {k: v for k, v in g["levels"].items() if k in known}
        u["progress"] = g
    return get_state(today)


def _save_score(u, level_row, score, accuracy, stars):
    row = app_tables.scores.get(user=u, level=level_row)
    if row is None:
        app_tables.scores.add_row(user=u, level=level_row, score=float(score), accuracy=float(accuracy),
                                  stars=float(stars), at=_now())
    else:
        if score > (row["score"] or 0):
            row["score"] = float(score)
            row["at"] = _now()
        row["accuracy"] = float(max(accuracy, row["accuracy"] or 0))
        row["stars"] = float(max(stars, row["stars"] or 0))


def _board(level_row, u=None, n=10):
    rows = list(app_tables.scores.search(tables.order_by("score", ascending=False), level=level_row))
    out = []
    you = None
    for i, r in enumerate(rows):
        usr = r["user"]
        name = (usr["display_name"] or "Player") if usr is not None else "Player"
        entry = {"rank": i + 1, "name": name, "score": int(r["score"] or 0), "accuracy": r["accuracy"] or 0,
                 "stars": int(r["stars"] or 0), "you": usr == u}
        if i < n:
            out.append(entry)
        if usr == u:
            you = entry
    return {"top": out, "you": you, "total": len(rows)}


@anvil.server.callable
def leaderboard(level_key):
    row = app_tables.levels.get(key=level_key)
    if row is None:
        return {"top": [], "you": None, "total": 0}
    return _board(row, anvil.users.get_user())


# ---------------------------------------------------------------- guests (progress lives in the browser)

GUEST = {"name": "Traveller", "email": None, "is_admin": False, "guest": True}


def _guest(progress, today, fn=None):
    ensure_seeded()
    t = _client_today(today)
    jr = journey()
    p = normalize(progress)
    if fn is None:
        return _ok(p, jr, t, GUEST)

    def go():
        p2, report = fn(p, jr, t)
        return _ok(p2, jr, t, GUEST, report, full=False)
    return _run(go)


@anvil.server.callable
def guest_state(progress, today=None):
    return _guest(progress, today)


@anvil.server.callable
def guest_finish_level(progress, level_key, result, today=None):
    def fn(p, jr, t):
        lv = _level_row(level_key, jr)
        p, report = apply_finish(p, lv, jr, result, t)
        report["leaderboard"] = _board(lv["_row"], None)
        return p, report
    return _guest(progress, today, fn)


@anvil.server.callable
def guest_finish_daily(progress, result, today=None):
    return _guest(progress, today, lambda p, jr, t: apply_daily(p, jr, t, result))


@anvil.server.callable
def guest_buy(progress, kind, key, today=None):
    return _guest(progress, today, lambda p, jr, t: apply_buy(p, kind, key, jr, t))


@anvil.server.callable
def guest_equip(progress, kind, key, today=None):
    return _guest(progress, today, lambda p, jr, t: apply_equip(p, kind, key))
