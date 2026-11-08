"""Server tests: the real server modules against the strict in-memory table mock.

    python -I tools/testing/test_server.py      # prints ALL OK at the end
"""
import datetime as dt
import json
import pathlib
import shutil
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
tmp = pathlib.Path(tempfile.mkdtemp(prefix="drtest-"))
shutil.copytree(PROJECT / "server_code", tmp / "app")
(tmp / "app" / "__init__.py").write_text("")
sys.path[:0] = [str(HERE / "mock"), str(tmp)]

import anvil.server  # noqa: E402
import anvil.users  # noqa: E402
from anvil.tables import app_tables as T  # noqa: E402
from app import Accounts, Admin, Catalog as C, Game as G, Levels as L, Music as M  # noqa: E402

FAILS = []
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def ok(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


TODAY = dt.datetime.now(dt.timezone.utc).date()
now = dt.datetime.now(dt.timezone.utc)


def user(email, **kw):
    return T.users.add_row(email=email, signed_up=now, enabled=True, **kw)


def result(data, acc=1.0, **extra):
    """What a run in the browser reports, at a given accuracy (1.0 = perfect)."""
    tot = L.totals(data)
    r = {"items": tot["items"], "hits": tot["items"] * acc, "score": int(tot["items"] * 100 * acc),
         "combo": tot["rush"], "perfects": tot["rush"], "notes": tot["notes"] + tot["rush_notes"],
         "chords": tot["chords"] + tot["rush_chords"], "ear": tot["ear"], "quiz": tot["quiz"], "time": 60, "midi": False}
    r.update(extra)
    return r


def lv(key):
    return next(x for x in L.LEVELS if x["key"] == key)


# ---- music theory
ok(M.parse_note("C4") == 60 and M.parse_note("A4") == 69 and M.parse_note("F#3") == 54 and M.parse_note("Bb4") == 70,
   "note names to MIDI")
ok(M.parse_note("H4") is None and M.parse_note("C") is None, "bad notes are rejected")
ok(M.parse_chord("C")["notes"] == [60, 64, 67] and M.parse_chord("Am")["notes"] == [57, 60, 64], "C and Am voicings")
ok(M.parse_chord("Bdim")["spelled"] == ["B", "D", "F"], "B diminished is spelled B D F")
ok(M.parse_chord("Ebmaj7")["spelled"] == ["E♭", "G", "B♭", "D"], "Ebmaj7 spelling")
ok(M.parse_chord("F#m")["spelled"] == ["F♯", "A", "C♯"], "F#m spelling")
ok(M.parse_chord("C/E")["notes"][0] % 12 == 4, "slash chord puts E in the bass")
ok(M.parse_chord("Cxyz") is None, "unknown chord quality is rejected")
g7 = M.parse_numeral("V7", "C")
ok(g7 and g7["symbol"] == "G7" and sorted(n % 12 for n in g7["notes"]) == [2, 5, 7, 11], "V7 in C is G7")
ok(M.parse_numeral("IV", "F")["symbol"] == "B♭", "IV in F is B flat")
ok(M.parse_numeral("vii°", "C")["symbol"] == "Bdim", "vii° in C is B diminished")
ok(M.parse_numeral("ii7", "Bb")["symbol"] == "Cm7", "ii7 in Bb is Cm7")
ok(M.parse_numeral("iii", "D")["symbol"] == "F♯m", "iii in D is F# minor")
ok(M.parse_numeral("i", "Am")["symbol"] == "Am" and M.parse_numeral("V", "Am")["symbol"] == "E", "minor key numerals")
ok(M.scale_notes("G") == ["G4", "A4", "B4", "C5", "D5", "E5", "F#5", "G5"], "G major scale")
ok(M.scale_notes("F") == ["F4", "G4", "A4", "Bb4", "C5", "D5", "E5", "F5"], "F major scale")
ok(M.scale_notes("Am", "harmonic", 3)[-2] == "G#4", "A harmonic minor has G#")
ok(M.scale_notes("Bb", octave=3)[:3] == ["Bb3", "C4", "D4"], "Bb major octave numbers follow the letters")
ev, beats = M.parse_seq("C4 D4:2 | r:1 C4+E4+G4:0.5 {Am}:4")
ok(len(ev) == 4 and beats == 8.5 and ev[2]["t"] == 4 and ev[3]["label"] == "Am", "rush sequence parses")
ok(M.parse_seq("C4 X9") is None and M.parse_seq("C4:0") is None, "bad rush tokens are rejected")

# ---- every built-in level passes its own checks
ok(len(L.TERRITORIES) == 9 and len(L.LEVELS) >= 40, "9 territories, %d levels" % len(L.LEVELS))
for x in L.LEVELS:
    e, w = L.check(x["data"])
    ok(not e and not w, "level %s checks clean %s %s" % (x["key"], e, w))
codex_used = [k for x in L.LEVELS for k in x["data"]["codex"]]
ok(sorted(codex_used) == sorted(C.CODEX_BY_KEY), "every Codex page is taught by exactly one level")
cards_used = [k for x in L.LEVELS for k in x["data"]["cards"].values()]
ok(sorted(cards_used) == sorted(C.COMPOSER_BY_KEY), "every composer card comes from exactly one level")
for ex in C.CODEX:
    ok(all(all(M.parse_note(n) is not None for n in item.split("+")) for item in ex["ex"]["notes"]),
       "codex example notes parse: " + ex["key"])
for tier in range(4):
    d = L.daily(TODAY, tier)
    e, w = L.check(d["data"])
    ok(not e and d == L.daily(TODAY, tier), "daily practice tier %d is valid and stable %s" % (tier, e))
ok(L.daily(TODAY, 0) != L.daily(TODAY + dt.timedelta(days=1), 0), "daily practice changes each day")

# ---- checks catch problems
bad = {"steps": [{"t": "notes", "notes": ["C4", "Q9"]}, {"t": "chords", "chords": ["Cblah"]},
                 {"t": "progression", "key": "C", "numerals": ["IX"]}, {"t": "rush", "seq": "C4 ?", "bpm": 90},
                 {"t": "ear", "mode": "chord", "pool": ["major"]}, {"t": "quiz", "q": "?", "options": ["a", "b"], "answer": 5},
                 {"t": "dance"}], "codex": ["nope"], "pass": 90, "two": 80}
e, w = L.check(bad)
ok(len(e) >= 8, "check finds every problem (%d): %s" % (len(e), e))

# ---- guests: state, seeding
anvil.users.CURRENT[0] = None
s = G.guest_state(None, TODAY.isoformat())
ok(s["ok"] and len(s["journey"]) == 9, "guest state seeds 9 territories")
ok(s["status"]["unlocked"] == ["ivory-1"], "only the first level is unlocked")
ok(s["daily"]["level"]["key"].startswith("daily-") and not s["daily"]["done"], "daily practice offered")
p = s["progress"]

r = G.guest_finish_level(p, "ivory-2", result(lv("ivory-2")["data"]), TODAY.isoformat())
ok(not r["ok"] and "unlocked" in r["error"], "locked level is refused")
r = G.guest_finish_level(p, "ivory-1", result(lv("ivory-1")["data"], items=3), TODAY.isoformat())
ok(not r["ok"] and "changed" in r["error"], "item count must match the level")
r = G.guest_finish_level(p, "ivory-1", result(lv("ivory-1")["data"], acc=0.4), TODAY.isoformat())
ok(not r["ok"] and "accuracy" in r["error"], "a run below the pass mark is refused")

r = G.guest_finish_level(p, "ivory-1", result(lv("ivory-1")["data"], acc=0.85, hits=9999, score=10 ** 9),
                         TODAY.isoformat())
ok(r["ok"], "ivory-1 cleared")
rep = r["report"]
p = r["progress"]
ok(rep["accuracy"] == 100.0 and rep["stars"] == 3, "hits are capped at the items in the level")
ok(rep["score"] <= L.totals(lv("ivory-1")["data"])["items"] * 150 + 100, "score is capped")
ok(rep["first_clear"] and "ivory-2" in rep["unlocked"], "first clear unlocks the next level")
ok(rep["codex"] == ["keyboard", "find_c"] and p["codex"] == ["keyboard", "find_c"], "codex pages unlocked")
ok(p["xp"] == rep["xp"] > 0 and p["ducats"] == rep["ducats"] > 0, "xp and ducats awarded")
ok("first_note" in rep["new_badges"] and "flawless" in rep["new_badges"], "first badges")

r = G.guest_finish_level(p, "ivory-1", result(lv("ivory-1")["data"], acc=0.7), TODAY.isoformat())
ok(r["ok"] and not r["report"]["first_clear"] and r["progress"]["levels"]["ivory-1"]["stars"] == 3,
   "replay keeps the best stars")
ok(r["report"]["xp"] < rep["xp"], "replays pay less")
p = r["progress"]

r = G.guest_finish_level(p, "ivory-2", result(lv("ivory-2")["data"], acc=0.85), TODAY.isoformat())
ok(r["ok"] and r["report"]["stars"] == 2 and not r["report"].get("cards"), "two stars: no three-star card")
p = r["progress"]
r = G.guest_finish_level(p, "ivory-2", result(lv("ivory-2")["data"]), TODAY.isoformat())
ok(r["ok"] and r["report"]["cards"] == ["vivaldi"] and r["report"]["new_stars"] == 1, "three stars: Vivaldi's card")
p = r["progress"]
r = G.guest_finish_level(p, "ivory-2", result(lv("ivory-2")["data"]), TODAY.isoformat())
ok(r["ok"] and not r["report"].get("cards") and not r["report"].get("dupes"), "a level's card is given once")
p = r["progress"]
for k in ("ivory-3", "ivory-4"):
    r = G.guest_finish_level(p, k, result(lv(k)["data"]), TODAY.isoformat())
    p = r["progress"]
ok(r["ok"] and r["report"]["conquered"] == "ivory" and r["report"]["mastered"] == "ivory", "Ivory Shore conquered")
ok(r["report"]["cards"] == ["satie"] and "sharp-1" in r["report"]["unlocked"], "trial card and the next territory")
ok("first_flag" in r["report"]["new_badges"] and "mastery" in r["report"]["new_badges"], "conquest badges")

# ---- daily practice
dl = G.guest_state(p, TODAY.isoformat())["daily"]["level"]
r = G.guest_finish_daily(p, result(dl["data"]), TODAY.isoformat())
ok(r["ok"] and r["report"]["streak"] == 1 and r["report"]["ducats"] == C.REWARDS["daily_ducats"], "daily practice done")
ok(r["daily"]["done"], "daily marked done")
p2 = r["progress"]
r = G.guest_finish_daily(p2, result(dl["data"]), TODAY.isoformat())
ok(r["ok"] and r["report"].get("repeat") and r["report"]["ducats"] == 0, "second daily run pays nothing")
p2["daily"]["last"] = (TODAY - dt.timedelta(days=1)).isoformat()
p2["daily"]["streak"] = 6
r = G.guest_finish_daily(p2, result(dl["data"]), TODAY.isoformat())
ok(r["ok"] and r["report"]["streak"] == 7 and r["report"]["ducats"] == 30 + 60, "streak bonus grows")
ok("daily_7" in r["report"]["new_badges"], "streak badge")
r = G.guest_finish_daily(p, result(dl["data"], acc=0.2), TODAY.isoformat())
ok(not r["ok"], "daily needs the pass mark")
p = p2

# ---- shop
p["ducats"] = 400
r = G.guest_buy(p, "skins", "rosewood", TODAY.isoformat())
ok(r["ok"] and r["progress"]["equip"]["skins"] == "rosewood" and r["progress"]["ducats"] == 250, "bought a skin")
ok("stylist" in r["report"]["new_badges"], "stylist badge")
ok(not G.guest_buy(r["progress"], "skins", "rosewood", TODAY.isoformat())["ok"], "can't buy twice")
ok(not G.guest_buy(r["progress"], "skins", "gilded", TODAY.isoformat())["ok"], "can't buy without ducats")
r = G.guest_equip(r["progress"], "skins", "ivory", TODAY.isoformat())
ok(r["ok"] and r["progress"]["equip"]["skins"] == "ivory", "equip another skin")
ok(not G.guest_equip(r["progress"], "trails", "prism", TODAY.isoformat())["ok"], "can't equip what you don't own")
p = r["progress"]

# ---- normalize drops junk from a browser
junk = {"xp": -5, "ducats": "7", "codex": ["keyboard", "fake", "keyboard"], "cards": {"bach": 1, "nobody": 3},
        "levels": {"ivory-1": {"stars": 9, "best": "x"}}, "owned": {"skins": ["gilded", "fake"]},
        "equip": {"skins": "fake"}, "badges": {"fake": "x"}, "stats": {"notes": "lots"}}
n = G.normalize(junk)
ok(n["xp"] == 0 and n["ducats"] == 7 and n["codex"] == ["keyboard"] and n["cards"] == {"bach": 1}, "normalize cleans")
ok(n["levels"]["ivory-1"]["stars"] == 3 and n["levels"]["ivory-1"]["best"] == 0, "level records clamped")
ok(n["owned"]["skins"] == ["ivory", "gilded"] and n["equip"]["skins"] == "ivory" and not n["badges"], "owned/equip")

# ---- the whole road, perfectly
q = G.new_progress()
for t in L.TERRITORIES:
    for x in [y for y in L.LEVELS if y["territory"] == t["key"]]:
        r = G.guest_finish_level(q, x["key"], result(x["data"]), TODAY.isoformat())
        if not r["ok"]:
            ok(False, "whole road: %s %s" % (x["key"], r["error"]))
            break
        q = r["progress"]
st = r["status"]
ok(len(st["conquered"]) == 9 and len(st["mastered"]) == 9, "whole road: every territory conquered and mastered")
ok(st["codex"] == st["codex_max"] and st["cards"] == st["cards_max"], "whole road: every codex page and card")
ok(all(b in q["badges"] for b in ("road_all", "flags_all", "codex_all", "cards_all", "stars_75")),
   "whole road: the big badges")
ok(st["rank"]["idx"] >= 6, "whole road: rank %s" % st["rank"]["name"])

# ---- signed-in player
ana = user("ana@example.com")
anvil.users.CURRENT[0] = ana
s = G.get_state(TODAY.isoformat())
ok(s["ok"] and s["me"]["name"] == "ana" and not s["me"]["is_admin"], "signed-in state")
r = G.import_guest(p, TODAY.isoformat())
ok(r["progress"]["levels"].get("ivory-1"), "guest progress moves into a new account")
r = G.finish_level("ivory-1", result(lv("ivory-1")["data"]), TODAY.isoformat())
ok(r["ok"] and r["report"]["leaderboard"]["you"]["score"] > 0, "leaderboard entry saved")
ok(G.leaderboard("ivory-1")["total"] == 1, "leaderboard has one entry")
r = G.set_name("  Ana   Keys ", TODAY.isoformat())
ok(r["me"]["name"] == "Ana Keys", "display name set")
r = Admin.admin_state if False else None
try:
    Admin.admin_state()
    ok(False, "non-admin blocked from admin_state")
except anvil.server.PermissionDenied:
    ok(True, "non-admin blocked from admin_state")

# ---- admin
admin = user("arkulinskis@gmail.com")
anvil.users.CURRENT[0] = admin
a = Admin.admin_state()
ok(a["ok"] and len(a["territories"]) == 9 and all(not l["errors"] for t in a["territories"] for l in t["levels"]),
   "admin state lists every level, clean")
spec = {"name": "My level", "territory": "ivory", "published": True,
        "data": {"intro": "x", "steps": [{"t": "notes", "notes": ["C4", "Z1"], "show": "keys"}]}}
r = Admin.save_level(spec)
new = next(l for t in r["territories"] for l in t["levels"] if l["name"] == "My level")
ok(r["ok"] and not new["published"] and r["note"], "a level with errors is saved as a draft")
spec["key"] = new["key"]
spec["data"]["steps"][0]["notes"] = ["C4", "D4"]
spec["data"]["steps"].append({"t": "quiz", "q": "Q?", "options": ["a", "b", "", "c"], "answer": 1, "evil": 1})
r = Admin.save_level(spec)
new = next(l for t in r["territories"] for l in t["levels"] if l["key"] == spec["key"])
ok(new["published"] and new["items"] == 3 and "evil" not in new["data"]["steps"][1], "fixed level publishes, cleaned")
ok([l["key"] for l in next(t for t in r["territories"] if t["key"] == "ivory")["levels"]][-1] == spec["key"],
   "new level goes at the end of its territory")
r = Admin.move_level(spec["key"], -1)
ok([l["key"] for l in next(t for t in r["territories"] if t["key"] == "ivory")["levels"]][-2] == spec["key"],
   "level moved up")
r = Admin.save_territory({"name": "Test Isle", "emoji": "x", "color": "nope", "x": 500, "y": 20})
tt = next(t for t in r["territories"] if t["name"] == "Test Isle")
ok(tt["x"] == 97 and tt["color"] == C.COLORS[0], "territory fields cleaned")
r = Admin.delete_territory("ivory")
ok(not r["ok"] and "levels" in r["error"], "can't delete a territory with levels")
r = Admin.delete_territory(tt["key"])
ok(not any(t["name"] == "Test Isle" for t in r["territories"]), "empty territory deleted")
row = T.levels.get(key="ivory-1")
row["data"] = {"steps": []}
r = Admin.restore_level("ivory-1")
ok(T.levels.get(key="ivory-1")["data"] == lv("ivory-1")["data"], "built-in level restored")
T.levels.get(key="ivory-2").delete()
r = Admin.restore_defaults()
ok(T.levels.get(key="ivory-2") is not None and "1" in r["note"], "deleted built-in level restored")
r = Admin.delete_level(spec["key"])
ok(T.levels.get(key=spec["key"]) is None, "level deleted")
r = Admin.list_players()
ok(r["ok"] and len(r["players"]) == 2, "players listed")
r = Admin.set_admin("arkulinskis@gmail.com", False)
ok(not r["ok"], "can't remove your own admin rights")
r = Admin.set_admin("ana@example.com", True)
ok(r["ok"] and ana["is_admin"], "made ana an admin")

# ---- the Forms version's start-up call (Accounts.py)
anvil.users.CURRENT[0] = None
ok(Accounts.get_me() is None, "get_me: nobody signed in")
anvil.users.CURRENT[0] = ana
me = Accounts.get_me()
ok(me["email"] == "ana@example.com" and me["is_admin"] and bool(json.dumps(me)), "get_me: the signed-in player (JSON-able)")
ok(not Accounts.update_profile("x")["ok"], "update_profile: a name needs 2 letters")
r = Accounts.update_profile("  Ana   Lee ")
ok(r["ok"] and ana["display_name"] == "Ana Lee" and r["me"]["name"] == "Ana Lee", "update_profile: name saved, spaces tidied")

print("\nALL OK" if not FAILS else "\n%d FAILED" % len(FAILS))
sys.exit(1 if FAILS else 0)
