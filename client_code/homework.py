"""Homework links and the weekly practice report. No accounts and nothing about students on the server: a homework
lives in its link (#hw/<code>), the kid's browser keeps it (localStorage dr.homework), the checklist ticks itself from
the practice log in the player's progress (progress["log"], written by server_code/Game.py), and the report the kid
sends back is a link too (#r/<code>, read-only for the teacher).

Codes are compact JSON in base64url (dr.b64e / dr.b64d), so they never contain "/" (router.parse splits on it).
    homework  {"v": 1, "t": teacher name, "n": note, "f": made on, "d": due, "m": minutes a day, "k": days, "x": [tasks]}
    task      "s:<song>:<learn|practice|perform>" | "l:<level key>" | "d" (Daily Practice): the same keys the log uses
    report    {"v": 1, "e": last day, "m": [7 daily minutes], "r": runs, "c": [cleared keys], "k": streak, "s": stars,
               "t": current territory, "h": {"t", "d", "x": [[task, 0|1]], "g": [minutes, days, days met]}}
"""
import datetime
import re

from . import dr, game

STORE = "dr.homework"      # {"code", "hw", "got"}: the homework this browser received
TEACHER_STORE = "dr.teacher"  # the teacher's last name, tasks and goal (a convenience on the teacher's device)
MAX_TASKS = 6
MINUTES = [0, 5, 10, 15, 20, 30, 45, 60]
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
TASK_RE = re.compile(r"^(d|l:[a-z0-9-]{1,60}|s:[a-z0-9-]{1,60}:(learn|practice|perform))$")
DAY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ---------------------------------------------------------------- dates (ISO strings, the browser's local day)
def to_date(iso):
    return datetime.date(int(iso[:4]), int(iso[5:7]), int(iso[8:10]))


def iso(d):
    return "%04d-%02d-%02d" % (d.year, d.month, d.day)


def valid_day(s):
    if not (isinstance(s, str) and DAY_RE.match(s)):
        return False
    try:
        to_date(s)
        return True
    except Exception:
        return False


def add_days(day, n):
    return iso(to_date(day) + datetime.timedelta(days=n))


def days_between(a, b):
    return (to_date(b) - to_date(a)).days


def nice_date(day, weekday=True):
    d = to_date(day)
    return ("%s %d %s" if weekday else "%s%d %s") % (DAY_NAMES[d.weekday()] if weekday else "", d.day, MONTHS[d.month - 1])


def due_text(due, today):
    left = days_between(today, due)
    if left > 1:
        return "due %s · %d days left" % (nice_date(due), left)
    if left == 1:
        return "due tomorrow, %s" % nice_date(due)
    if left == 0:
        return "due today"
    return "was due %s · finish it anyway" % nice_date(due)


# ---------------------------------------------------------------- tasks
def task_label(t):
    """(title, what kind) for a task, from the road and the shelf this browser loaded."""
    if t == "d":
        return "Daily Practice", "Today's fresh warm-up (any day counts)"
    if t.startswith("s:"):
        _, key, mode = t.split(":")
        s = game.song(key)
        title = s["title"] if s else "A song from the Song Shelf"
        return title, "Song · %s %s (%s)" % (game.SONG_MODE_ICONS[mode], game.SONG_MODE_NAMES[mode],
                                             game.SONG_MODE_SUBS[mode])
    key = t[2:]
    x = game.find_level(key)
    if x is None:
        return "A level on the road", "This level isn't on the road any more"
    where = "Trial" if x["l"]["data"].get("trial") else "level %d" % (x["i"] + 1)
    return x["l"]["name"], "Road · %s, %s" % (x["t"]["name"], where)


def task_target(t):
    """Where the Play button goes: (args for router.go("play", ...), "") or ([], why it can't open yet)."""
    if t == "d":
        return ["daily"], ""
    if t.startswith("s:"):
        _, key, mode = t.split(":")
        return (["song", key, mode], "") if game.song(key) else ([], "That song isn't on this shelf.")
    key = t[2:]
    if game.find_level(key) is None:
        return [], "That level isn't on the road any more."
    if game.unlocked(key) or game.rec(key)["stars"]:
        return [key], ""
    return [], "Clear the levels before it on the map first: the road opens one level at a time."


# ---------------------------------------------------------------- homework codes
def make(teacher, note, due, minutes, days, tasks, today):
    return {"v": 1, "t": (teacher or "").strip()[:30], "n": (note or "").strip()[:200], "f": today, "d": due,
            "m": int(minutes or 0), "k": int(days or 0), "x": list(tasks)[:MAX_TASKS]}


def encode(obj):
    return dr.b64e(obj)


def parse(code):
    """A homework from a link, cleaned; None when the link is broken."""
    h = dr.b64d(code)
    if not isinstance(h, dict) or h.get("v") != 1:
        return None
    tasks = [t for t in (h.get("x") or []) if isinstance(t, str) and TASK_RE.match(t)][:MAX_TASKS] \
        if isinstance(h.get("x"), list) else []
    if not valid_day(h.get("f")) or not valid_day(h.get("d")) or not tasks:
        return None
    try:
        minutes = max(0, min(120, int(h.get("m") or 0)))
        days = max(0, min(7, int(h.get("k") or 0)))
    except Exception:
        return None
    return {"v": 1, "t": str(h.get("t") or "")[:30], "n": str(h.get("n") or "")[:200], "f": h["f"], "d": h["d"],
            "m": minutes, "k": days if minutes else 0, "x": tasks}


def stored():
    s = dr.store_get(STORE, None)
    if not isinstance(s, dict):
        return None
    hw = parse(s.get("code"))
    return {"code": s.get("code"), "hw": hw, "got": s.get("got")} if hw else None


def save(code, hw):
    dr.store_set(STORE, {"code": code, "got": dr.today()})


def clear():
    dr.store_del(STORE)


def teacher_name(hw):
    return hw["t"] or "your teacher"


# ---------------------------------------------------------------- the checklist (ticks itself from the practice log)
def _log():
    p = game.S["progress"] or {}
    return p.get("log") or {}


def cleared_since(since):
    out = set()
    for day, v in _log().items():
        if day >= since:
            for k in v.get("c") or []:
                out.add(k)
    return out


def ticks(hw):
    done = cleared_since(hw["f"])
    return [t in done for t in hw["x"]]


def goal(hw):
    """(days with enough minutes since the homework was made, days needed); (0, 0) when there's no weekly goal."""
    if not hw["m"] or not hw["k"]:
        return 0, 0
    need = hw["m"] * 60
    met = len([d for d, v in _log().items() if d >= hw["f"] and v.get("s", 0) >= need])
    return min(met, hw["k"]), hw["k"]


def summary(hw):
    tk = ticks(hw)
    met, need = goal(hw)
    total = len(tk) + (1 if need else 0)
    done = len([x for x in tk if x]) + (1 if need and met >= need else 0)
    return {"ticks": tk, "met": met, "need": need, "done": done, "total": total, "all": total > 0 and done == total}


def goal_text(hw):
    if not hw["m"] or not hw["k"]:
        return ""
    return "Practise %d minutes on %d day%s" % (hw["m"], hw["k"], "" if hw["k"] == 1 else "s")


def open_homework():
    """The stored homework and whether it still has open items (the header's dot). None without homework."""
    s = stored()
    if s is None:
        return None
    s["open"] = not summary(s["hw"])["all"] if game.ready() else True
    return s


# ---------------------------------------------------------------- the weekly report
def week(today):
    """The last 7 days ending today: minutes per day, runs, and what was cleared."""
    log = _log()
    days, cleared, runs, secs = [], [], 0, 0
    for i in range(6, -1, -1):
        d = add_days(today, -i)
        v = log.get(d) or {}
        s = int(v.get("s") or 0)
        secs += s
        runs += int(v.get("r") or 0)
        for k in v.get("c") or []:
            if k not in cleared:
                cleared.append(k)
        days.append({"iso": d, "min": int(round(s / 60.0))})
    return {"end": today, "days": days, "runs": runs, "cleared": cleared, "minutes": int(round(secs / 60.0))}


def my_report(today):
    """The report data for this player (the same shape a #r link carries)."""
    S = game.S
    w = week(today)
    cur = game.current_terr()
    out = {"v": 1, "e": today, "m": [d["min"] for d in w["days"]], "r": w["runs"], "c": w["cleared"][:24],
           "k": int((S["daily"] or {}).get("streak") or 0), "s": int(S["status"]["stars"]),
           "t": cur["name"] if cur else ""}
    s = stored()
    if s:
        hw = s["hw"]
        sm = summary(hw)
        out["h"] = {"t": hw["t"], "d": hw["d"], "x": [[t, 1 if ok else 0] for t, ok in zip(hw["x"], sm["ticks"])],
                    "g": [hw["m"], hw["k"], sm["met"]]}
    return out


def parse_report(code):
    r = dr.b64d(code)
    if not isinstance(r, dict) or r.get("v") != 1 or not valid_day(r.get("e")):
        return None
    try:
        m = [max(0, min(240, int(x))) for x in (r.get("m") or [])][:7]
        if len(m) != 7:
            return None
        out = {"v": 1, "e": r["e"], "m": m, "r": max(0, int(r.get("r") or 0)),
               "c": [c for c in (r.get("c") or []) if isinstance(c, str) and TASK_RE.match(c)][:24],
               "k": max(0, int(r.get("k") or 0)), "s": max(0, int(r.get("s") or 0)), "t": str(r.get("t") or "")[:60]}
        h = r.get("h")
        if isinstance(h, dict) and isinstance(h.get("x"), list):
            out["h"] = {"t": str(h.get("t") or "")[:30], "d": h.get("d") if valid_day(h.get("d")) else "",
                        "x": [[x[0], 1 if x[1] else 0] for x in h["x"]
                              if isinstance(x, list) and len(x) == 2 and isinstance(x[0], str) and TASK_RE.match(x[0])][:MAX_TASKS],
                        "g": [max(0, int(v or 0)) for v in (h.get("g") or [0, 0, 0])][:3]}
    except Exception:
        return None
    return out


def cleared_lines(keys):
    """What was cleared, in words: songs and levels by name, Daily Practice once."""
    lines = []
    for k in keys:
        title, sub = task_label(k)
        if k.startswith("s:"):
            mode = k.split(":")[2]
            lines.append({"icon": game.SONG_MODE_ICONS[mode], "text": "%s · %s" % (title, game.SONG_MODE_NAMES[mode])})
        elif k == "d":
            lines.append({"icon": "📜", "text": "Daily Practice"})
        else:
            lines.append({"icon": "🗺️", "text": "%s (%s)" % (title, sub.replace("Road · ", ""))})
    return lines
