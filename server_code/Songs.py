# Songs — Server Module (no callables). The Song Shelf: public-domain melodies that are open from the first minute,
# each playable three ways, built as ordinary level dicts so the engine and the result check stay the same:
#
#   learn     one `notes` step per phrase, the glowing key waits for you (no timing)
#   practice  a rush at 70% of the song's tempo, note names on the falling notes
#   perform   a rush at full tempo (names only on the easier songs)
#
# Every melody here is traditional or long out of copyright, written out by hand, melody only, in C position where
# the tune allows. Format: Music.parse_seq ("E4:2" = two beats, "r" = a one-beat rest, "|" = a bar line).
# New song: add it to SONGS (keys are permanent: progress is stored under them) and run tools/testing/test_server.py.
from . import Levels as L
from . import Music as M

MODES = ("learn", "practice", "perform")
MODE_NAMES = {"learn": "Learn", "practice": "Practice", "perform": "Perform"}
PRACTICE_SPEED = 0.7
PASS = {"learn": 50, "practice": 60, "perform": 60}

JINGLE = ("E4 E4 E4:2 | E4 E4 E4:2 | E4 G4 C4:1.5 D4:0.5 | E4:4 | F4 F4 F4 F4 | F4 E4 E4 E4:0.5 E4:0.5 | "
          "E4 D4 D4 E4 | D4:2 G4:2 | E4 E4 E4:2 | E4 E4 E4:2 | E4 G4 C4:1.5 D4:0.5 | E4:4 | F4 F4 F4 F4 | "
          "F4 E4 E4 E4:0.5 E4:0.5 | G4 G4 F4 D4 | C4:4")
WISH = ("G3 | C4 C4:0.5 D4:0.5 C4:0.5 B3:0.5 | A3 A3 A3 | D4 D4:0.5 E4:0.5 D4:0.5 C4:0.5 | B3 G3 G3 | "
        "E4 E4:0.5 F4:0.5 E4:0.5 D4:0.5 | C4 A3 G3:0.5 G3:0.5 | A3 D4 B3 | C4:2")
DECK = ("G4:1.5 F4:0.5 E4 D4 | C4 D4 E4 C4 | D4:0.5 E4:0.5 F4:0.5 D4:0.5 E4:1.5 D4:0.5 | C4 B3 C4:2 | "
        "G4:1.5 F4:0.5 E4 D4 | C4 D4 E4 C4 | D4:0.5 E4:0.5 F4:0.5 D4:0.5 E4:1.5 D4:0.5 | C4 B3 C4:2 | "
        "D4:1.5 E4:0.5 F4 D4 | E4:1.5 F4:0.5 G4 D4 | E4:0.5 F#4:0.5 G4 A4:0.5 B4:0.5 C5 | B4 A4 G4:2 | "
        "G4:1.5 F4:0.5 E4 D4 | C4 D4 E4 C4 | A4:0.5 A4:0.5 A4:0.5 A4:0.5 G4:1.5 F4:0.5 | E4 D4 C4:2")
TREE = ("G3 | C4:0.75 C4:0.25 C4:1.5 D4:0.5 | E4:0.75 E4:0.25 E4:1.5 E4:0.5 | D4:0.5 E4:0.5 F4 B3 | D4 C4 G4 | "
        "G4:0.5 E4:0.5 A4:1.5 G4:0.5 | G4:0.5 F4:0.5 F4:1.5 F4:0.5 | F4:0.5 D4:0.5 G4:1.5 F4:0.5 | "
        "F4:0.5 E4:0.5 E4 G3 | C4:0.75 C4:0.25 C4:1.5 D4:0.5 | E4:0.75 E4:0.25 E4:1.5 E4:0.5 | "
        "D4:0.5 E4:0.5 F4 B3 | D4 C4:2")
SILENT = ("G4:1.5 A4:0.5 G4 | E4:3 | G4:1.5 A4:0.5 G4 | E4:3 | D5:2 D5 | B4:3 | C5:2 C5 | G4:3 | "
          "A4:2 A4 | C5:1.5 B4:0.5 A4 | G4:1.5 A4:0.5 G4 | E4:3 | A4:2 A4 | C5:1.5 B4:0.5 A4 | "
          "G4:1.5 A4:0.5 G4 | E4:3 | D5:2 D5 | F5:1.5 D5:0.5 B4 | C5:3 | E5:3 | "
          "C5:1.5 G4:0.5 E4 | G4:1.5 F4:0.5 D4 | C4:3")
JOY = ("C5 B4:0.75 A4:0.25 | G4:1.5 F4:0.5 | E4 D4 | C4:1.5 G4:0.5 | A4:1.5 A4:0.5 | B4:1.5 B4:0.5 | "
       "C5:1.5 C5:0.5 | C5:0.5 B4:0.5 A4:0.5 G4:0.5 | G4:0.75 F4:0.25 E4 | E4:0.5 E4:0.5 E4:0.5 E4:0.25 F4:0.25 | "
       "G4:1.5 F4:0.25 E4:0.25 | D4:0.5 D4:0.5 D4:0.5 D4:0.25 E4:0.25 | F4:1.5 E4:0.25 D4:0.25 | "
       "C4:0.5 C5 A4:0.5 | G4:0.75 F4:0.25 E4:0.5 F4:0.5 | E4 D4 | C4:2")
TWINKLE = ("C4 C4 G4 G4 | A4 A4 G4:2 | F4 F4 E4 E4 | D4 D4 C4:2 | G4 G4 F4 F4 | E4 E4 D4:2 | "
           "G4 G4 F4 F4 | E4 E4 D4:2 | C4 C4 G4 G4 | A4 A4 G4:2 | F4 F4 E4 E4 | D4 D4 C4:2")
LONDON = ("G4:1.5 A4:0.5 G4 F4 | E4 F4 G4:2 | D4 E4 F4:2 | E4 F4 G4:2 | G4:1.5 A4:0.5 G4 F4 | E4 F4 G4:2 | "
          "D4:2 G4:2 | E4 C4:3")
ROW = ("C4:1.5 C4:1.5 | C4 D4:0.5 E4:1.5 | E4 D4:0.5 E4 F4:0.5 | G4:3 | "
       "C5:0.5 C5:0.5 C5:0.5 G4:0.5 G4:0.5 G4:0.5 | E4:0.5 E4:0.5 E4:0.5 C4:0.5 C4:0.5 C4:0.5 | "
       "G4 F4:0.5 E4 D4:0.5 | C4:3")
BIRTHDAY = ("G3:0.75 G3:0.25 | A3 G3 C4 | B3:2 G3:0.75 G3:0.25 | A3 G3 D4 | C4:2 G3:0.75 G3:0.25 | "
            "G4 E4 C4 | B3 A3 F4:0.75 F4:0.25 | E4 C4 D4 | C4:3")
SAINTS = ("r C4 E4 F4 | G4:4 | r C4 E4 F4 | G4:4 | r C4 E4 F4 | G4:2 E4:2 | C4:2 E4:2 | D4:4 | "
          "r E4 E4 D4 | C4:3 C4 | E4:2 G4:1.5 G4:0.5 | F4:4 | r C4 E4 F4 | G4:2 E4:2 | C4:2 D4:2 | C4:4")
CANCAN = ("C4:2 D4:0.5 F4:0.5 E4:0.5 D4:0.5 | G4 G4 G4:0.5 A4:0.5 E4:0.5 F4:0.5 | "
          "D4 D4 D4:0.5 F4:0.5 E4:0.5 D4:0.5 | C4:0.5 C5:0.5 B4:0.5 A4:0.5 G4:0.5 F4:0.5 E4:0.5 D4:0.5 | "
          "C4:2 D4:0.5 F4:0.5 E4:0.5 D4:0.5 | G4 G4 G4:0.5 A4:0.5 E4:0.5 F4:0.5 | "
          "D4 D4 D4:0.5 F4:0.5 E4:0.5 D4:0.5 | C4:0.5 G4:0.5 D4:0.5 E4:0.5 C4:2")

SHELVES = [("christmas", "Christmas"), ("favourites", "Favourites")]

# level: 1 easy (C position, simple rhythm) .. 3 hard (black keys, fast notes, no names at full speed)
SONGS: list = [
    {"key": "jingle-bells", "title": "Jingle Bells", "origin": "J. L. Pierpont, 1857", "shelf": "christmas",
     "level": 1, "bpm": 104, "seq": JINGLE},
    {"key": "we-wish-you", "title": "We Wish You a Merry Christmas", "origin": "English traditional",
     "shelf": "christmas", "level": 2, "bpm": 120, "seq": WISH},
    {"key": "deck-the-halls", "title": "Deck the Halls", "origin": "Welsh traditional, 1700s", "shelf": "christmas",
     "level": 2, "bpm": 104, "seq": DECK},
    {"key": "o-christmas-tree", "title": "O Christmas Tree", "origin": "German traditional", "shelf": "christmas",
     "level": 2, "bpm": 96, "seq": TREE},
    {"key": "silent-night", "title": "Silent Night", "origin": "Franz Gruber, 1818", "shelf": "christmas",
     "level": 2, "bpm": 72, "seq": SILENT},
    {"key": "joy-to-the-world", "title": "Joy to the World", "origin": "Lowell Mason, 1839", "shelf": "christmas",
     "level": 3, "bpm": 88, "seq": JOY},
    {"key": "twinkle", "title": "Twinkle, Twinkle, Little Star", "origin": "French traditional, 1761",
     "shelf": "favourites", "level": 1, "bpm": 96, "seq": TWINKLE},
    {"key": "mary", "title": "Mary Had a Little Lamb", "origin": "Traditional, 1830", "shelf": "favourites",
     "level": 1, "bpm": 96, "seq": L.MARY},
    {"key": "london-bridge", "title": "London Bridge", "origin": "English traditional, 1744", "shelf": "favourites",
     "level": 1, "bpm": 100, "seq": LONDON},
    {"key": "ode-to-joy", "title": "Ode to Joy", "origin": "Beethoven, 1824", "shelf": "favourites",
     "level": 1, "bpm": 96, "seq": L.ODE},
    {"key": "row-your-boat", "title": "Row, Row, Row Your Boat", "origin": "Traditional, 1852",
     "shelf": "favourites", "level": 2, "bpm": 96, "seq": ROW},
    {"key": "happy-birthday", "title": "Happy Birthday", "origin": "Mildred and Patty Hill, 1893",
     "shelf": "favourites", "level": 2, "bpm": 100, "seq": BIRTHDAY},
    {"key": "saints", "title": "When the Saints Go Marching In", "origin": "Traditional spiritual",
     "shelf": "favourites", "level": 2, "bpm": 116, "seq": SAINTS},
    {"key": "amazing-grace", "title": "Amazing Grace", "origin": "Traditional, 1829", "shelf": "favourites",
     "level": 2, "bpm": 84, "seq": L.GRACE},
    {"key": "can-can", "title": "Can-Can", "origin": "Jacques Offenbach, 1858", "shelf": "favourites",
     "level": 3, "bpm": 116, "seq": CANCAN},
    {"key": "fur-elise", "title": "Für Elise", "origin": "Beethoven, 1810", "shelf": "favourites",
     "level": 3, "bpm": 76, "seq": L.ELISE},
    {"key": "minuet-in-g", "title": "Minuet in G", "origin": "Christian Petzold, 1725", "shelf": "favourites",
     "level": 3, "bpm": 100, "seq": L.MINUET},
]
SONG_BY_KEY = {s["key"]: s for s in SONGS}


def phrases(seq):
    """The melody cut into phrases for Learn: whole bars, at least 2 bars and 6 notes each (12 notes at most)."""
    out, cur, bars = [], [], 0
    for bar in str(seq).split("|"):
        notes = [t.partition(":")[0] for t in bar.split() if t.partition(":")[0] not in ("r", "_", "-")]
        if not notes:
            continue
        cur += notes
        bars += 1
        if (bars >= 2 and len(cur) >= 6) or len(cur) >= 12:
            out.append(cur)
            cur, bars = [], 0
    if cur:
        if out and len(cur) < 4:
            out[-1] += cur
        else:
            out.append(cur)
    return out


def level(key, mode):
    """A Song Shelf level, shaped like Levels.daily(): {key, name, data}. None for an unknown song or mode."""
    s = SONG_BY_KEY.get(key)
    if s is None or mode not in MODES:
        return None
    if mode == "learn":
        ph = phrases(s["seq"])
        steps = [L.notes("Phrase %d of %d: follow the glowing keys" % (i + 1, len(ph)), p, show="keys")
                 for i, p in enumerate(ph)]
        intro = "Phrase by phrase. Each key glows and waits for you, so take your time."
    elif mode == "practice":
        steps = [L.rush(s["title"] + " at 70% speed", s["seq"], bpm=int(round(s["bpm"] * PRACTICE_SPEED)), hint=True)]
        intro = "The notes fall slower, with their names on them. Land each one on the line."
    else:
        steps = [L.rush(s["title"], s["seq"], bpm=s["bpm"], hint=s["level"] < 3)]
        intro = "The real tempo. Play it the way it goes."
    return {"key": "song-%s-%s" % (key, mode), "name": s["title"],
            "data": {"intro": intro, "steps": steps, "pass": PASS[mode], "two": L.DEFAULT_TWO,
                     "three": L.DEFAULT_THREE, "codex": [], "cards": {}, "trial": False}}


def public():
    """The shelf the browser gets: every song with its three levels (the engine plays these exact levels)."""
    out = []
    for s in SONGS:
        parsed = M.parse_seq(s["seq"])
        beats = parsed[1] if parsed else 0
        out.append({"key": s["key"], "title": s["title"], "origin": s["origin"], "shelf": s["shelf"],
                    "level": s["level"], "bpm": s["bpm"], "seq": s["seq"], "notes": len(parsed[0]) if parsed else 0,
                    "seconds": int(round(beats * 60.0 / s["bpm"])),
                    "modes": {m: level(s["key"], m) for m in MODES}})
    return {"shelves": [{"key": k, "name": n} for k, n in SHELVES], "songs": out}
