# Music — Server Module (no callables). Music theory the server needs to check and score levels:
# note names, chord symbols, Roman numerals in a key, and the "rush" note sequences.
#
# lib/music.js is the same code for the browser. Keep the two in step: tools/check.py compares them
# on a list of inputs (tools/testing/music_parity.py).
import re

LETTERS = "CDEFGAB"
LETTER_PC = [0, 2, 4, 5, 7, 9, 11]
MAJOR = [0, 2, 4, 5, 7, 9, 11]
MINOR = [0, 2, 3, 5, 7, 8, 10]
ACC = {"": 0, "#": 1, "##": 2, "x": 2, "b": -1, "bb": -2, "♯": 1, "♭": -1}

# Chord types: symbol suffix → list of (semitones above root, letter steps above root's letter).
CHORD_TYPES = {
    "": [(0, 0), (4, 2), (7, 4)],
    "m": [(0, 0), (3, 2), (7, 4)],
    "dim": [(0, 0), (3, 2), (6, 4)],
    "aug": [(0, 0), (4, 2), (8, 4)],
    "sus2": [(0, 0), (2, 1), (7, 4)],
    "sus4": [(0, 0), (5, 3), (7, 4)],
    "5": [(0, 0), (7, 4)],
    "6": [(0, 0), (4, 2), (7, 4), (9, 5)],
    "m6": [(0, 0), (3, 2), (7, 4), (9, 5)],
    "7": [(0, 0), (4, 2), (7, 4), (10, 6)],
    "maj7": [(0, 0), (4, 2), (7, 4), (11, 6)],
    "m7": [(0, 0), (3, 2), (7, 4), (10, 6)],
    "m7b5": [(0, 0), (3, 2), (6, 4), (10, 6)],
    "dim7": [(0, 0), (3, 2), (6, 4), (9, 6)],
    "add9": [(0, 0), (4, 2), (7, 4), (14, 1)],
    "9": [(0, 0), (4, 2), (7, 4), (10, 6), (14, 1)],
}
CHORD_ALIASES = {"maj": "", "M": "", "min": "m", "-": "m", "°": "dim", "o": "dim", "+": "aug",
                 "ø": "m7b5", "ø7": "m7b5", "°7": "dim7", "o7": "dim7", "M7": "maj7",
                 "Δ": "maj7", "Δ7": "maj7", "min7": "m7", "-7": "m7", "dom7": "7", "sus": "sus4"}
CHORD_NAMES = {"": "major", "m": "minor", "dim": "diminished", "aug": "augmented", "sus2": "sus2", "sus4": "sus4",
               "5": "power chord", "6": "major sixth", "m6": "minor sixth", "7": "dominant seventh",
               "maj7": "major seventh", "m7": "minor seventh", "m7b5": "half-diminished", "dim7": "diminished seventh",
               "add9": "add nine", "9": "dominant ninth"}
# Ear training: chord qualities and intervals the player can be asked about.
EAR_CHORDS = {"major": "", "minor": "m", "diminished": "dim", "augmented": "aug", "dominant 7th": "7",
              "major 7th": "maj7", "minor 7th": "m7"}
INTERVALS = {"m2": (1, "minor 2nd"), "M2": (2, "major 2nd"), "m3": (3, "minor 3rd"), "M3": (4, "major 3rd"),
             "P4": (5, "perfect 4th"), "TT": (6, "tritone"), "P5": (7, "perfect 5th"), "m6": (8, "minor 6th"),
             "M6": (9, "major 6th"), "m7": (10, "minor 7th"), "M7": (11, "major 7th"), "P8": (12, "octave")}

NOTE_RE = re.compile(r"^([A-Ga-g])(##|#|x|bb|b|♯|♭)?(-?\d)$")
CHORD_RE = re.compile(r"^([A-G])(#|b|♯|♭)?([^/]*)(?:/([A-G])(#|b|♯|♭)?)?$")
KEY_RE = re.compile(r"^([A-G])(#|b|♯|♭)?(m|min|minor)?$")
NUMERAL_RE = re.compile(r"^(b|#|♭|♯)?(VII|VI|V|IV|III|II|I|vii|vi|v|iv|iii|ii|i)"
                        r"(°|o|\+|ø)?(maj7|M7|7)?$")
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII"]
BEATS_RE = re.compile(r"^\d*\.?\d+$")


def acc_text(a):
    return {0: "", 1: "♯", 2: "\U0001D12A", -1: "♭", -2: "\U0001D12B"}.get(a, "")


def spell(letter, pc):
    """Name for pitch class pc written on letter (0=C..6=B), e.g. spell(6, 10) → 'B♭'."""
    a = (pc - LETTER_PC[letter]) % 12
    if a > 6:
        a -= 12
    return LETTERS[letter] + acc_text(a)


def parse_note(s):
    """'C4' → 60, 'F#3' → 54, 'Bb4' → 70. None if it isn't a note."""
    m = NOTE_RE.match(str(s or "").strip())
    if not m:
        return None
    letter = LETTERS.index(m.group(1).upper())
    midi = (int(m.group(3)) + 1) * 12 + LETTER_PC[letter] + ACC[m.group(2) or ""]
    return midi if 21 <= midi <= 108 else None


def note_letter(s):
    m = NOTE_RE.match(str(s or "").strip())
    return LETTERS.index(m.group(1).upper()) if m else None


def name_of(midi, flats=False):
    pc = midi % 12
    names = ["C", "D♭", "D", "E♭", "E", "F", "G♭", "G", "A♭", "A", "B♭", "B"] if flats else \
        ["C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯", "A", "A♯", "B"]
    return names[pc] + str(midi // 12 - 1)


def parse_chord(sym, octave=None):
    """'Am' → {'root': 9, 'type': 'm', 'name': 'A minor', 'notes': [57, 60, 64], 'spelled': ['A','C','E']}."""
    s = str(sym or "").strip()
    m = CHORD_RE.match(s)
    if not m:
        return None
    letter = LETTERS.index(m.group(1))
    pc = (LETTER_PC[letter] + ACC[m.group(2) or ""]) % 12
    q = m.group(3) or ""
    q = CHORD_ALIASES.get(q, q)
    if q not in CHORD_TYPES:
        return None
    if octave is None:
        octave = 4 if pc <= 5 else 3
    root = (octave + 1) * 12 + pc
    notes = [root + semi for semi, _ in CHORD_TYPES[q]]
    spelled = [spell((letter + steps) % 7, (pc + semi) % 12) for semi, steps in CHORD_TYPES[q]]
    if m.group(4):
        bl = LETTERS.index(m.group(4))
        bpc = (LETTER_PC[bl] + ACC[m.group(5) or ""]) % 12
        bass = notes[0] - ((notes[0] - bpc) % 12 or 12)
        notes = [bass] + [n for n in notes if n % 12 != bpc]
        spelled = [spell(bl, bpc)] + [x for x, n in zip(spelled, [root + s2 for s2, _ in CHORD_TYPES[q]]) if n % 12 != bpc]
    root_name = spell(letter, pc)
    return {"root": pc, "type": q, "symbol": root_name + q + (("/" + spelled[0]) if m.group(4) else ""),
            "name": root_name + " " + CHORD_NAMES[q], "notes": notes, "spelled": spelled}


def parse_key(k):
    """'C' → (0, 0, 'major'), 'Am' → (9, 5, 'minor'): (pitch class, letter, mode)."""
    m = KEY_RE.match(str(k or "").strip())
    if not m:
        return None
    letter = LETTERS.index(m.group(1))
    return ((LETTER_PC[letter] + ACC[m.group(2) or ""]) % 12, letter, "minor" if m.group(3) else "major")


def key_name(k):
    pk = parse_key(k)
    if not pk:
        return str(k)
    return spell(pk[1], pk[0]) + (" minor" if pk[2] == "minor" else " major")


def parse_numeral(num, key):
    """'V7' in 'C' → the G7 chord dict (plus 'numeral'). None if either doesn't parse."""
    pk = parse_key(key)
    m = NUMERAL_RE.match(str(num or "").strip())
    if not pk or not m:
        return None
    kpc, kletter, mode = pk
    roman = m.group(2)
    degree = ROMAN.index(roman.upper())
    scale = MINOR if mode == "minor" else MAJOR
    acc = ACC.get(m.group(1) or "", 0)
    pc = (kpc + scale[degree] + acc) % 12
    letter = (kletter + degree) % 7
    mark, seventh = m.group(3) or "", m.group(4) or ""
    upper = roman.isupper()
    if mark == "ø":
        q = "m7b5"
    elif mark in ("°", "o"):
        q = "dim7" if seventh else "dim"
    elif mark == "+":
        q = "aug"
    elif upper:
        q = {"": "", "7": "7", "maj7": "maj7", "M7": "maj7"}[seventh]
    else:
        q = "m7" if seventh else "m"
    sym = spell(letter, pc) + q
    c = parse_chord(sym.replace("♯", "#").replace("♭", "b"))
    if c is None:
        return None
    c["numeral"] = str(num).strip()
    return c


def scale_notes(key, kind="major", octave=4):
    """Ascending one-octave scale, as note names with octaves: scale_notes('G') → ['G4', 'A4', ... 'G5']."""
    pk = parse_key(key)
    if not pk:
        return []
    kpc, kletter, _ = pk
    steps = {"major": MAJOR, "minor": MINOR, "harmonic": [0, 2, 3, 5, 7, 8, 11], "dorian": [0, 2, 3, 5, 7, 9, 10],
             "mixolydian": [0, 2, 4, 5, 7, 9, 10]}[kind]
    base = (octave + 1) * 12 + kpc
    return [ascii_name((kletter + i) % 7, base + semi) for i, semi in enumerate(steps + [12])]


def ascii_name(letter, midi):
    """midi written on a letter, ASCII with octave: ascii_name(3, 66) → 'F#4' (the octave follows the letter)."""
    a = (midi % 12 - LETTER_PC[letter]) % 12
    if a > 6:
        a -= 12
    natural = midi - a
    return LETTERS[letter] + {0: "", 1: "#", 2: "##", -1: "b", -2: "bb"}[a] + str(natural // 12 - 1)


def parse_seq(text):
    """A rush sequence → (events, total beats). Tokens are separated by spaces; '|' bar lines are ignored.

    C4        one note, 1 beat          C4:2     two beats       C4:0.5   half a beat
    C4+E4+G4  notes together            {Am}:4   a chord symbol  r:1      a rest (also _ or -)
    Returns None if a token doesn't parse.
    """
    events = []
    t = 0.0
    for tok in str(text or "").split():
        if tok == "|":
            continue
        body, _, beats = tok.partition(":")
        if beats and not BEATS_RE.match(beats):
            return None
        d = float(beats) if beats else 1.0
        if not (0 < d <= 16):
            return None
        if body in ("r", "_", "-"):
            t += d
            continue
        if body.startswith("{") and body.endswith("}"):
            c = parse_chord(body[1:-1])
            if c is None:
                return None
            events.append({"t": t, "d": d, "notes": c["notes"], "label": c["symbol"]})
        else:
            notes = [parse_note(x) for x in body.split("+")]
            if not notes or any(n is None for n in notes):
                return None
            events.append({"t": t, "d": d, "notes": sorted(set(notes)), "label": None})
        t += d
    return events, t


def chord_of(item):
    """A chord step item: a symbol ('G7') or notes joined by + ('C4+E4+G4')."""
    s = str(item or "").strip()
    if "+" in s and parse_note(s.split("+")[0]) is not None:
        notes = [parse_note(x) for x in s.split("+")]
        if any(n is None for n in notes):
            return None
        spelled = [pretty(x, True) for x in s.split("+")]
        return {"root": notes[0] % 12, "type": "?", "symbol": s, "name": " ".join(spelled), "notes": sorted(notes),
                "spelled": spelled}
    return parse_chord(s)


def pretty(s, no_octave=False):
    """'F#4' → 'F♯4' (or 'F♯' with no_octave)."""
    m = NOTE_RE.match(str(s or "").strip())
    if not m:
        return str(s or "")
    acc = {"": "", "#": "♯", "##": "\U0001D12A", "x": "\U0001D12A", "b": "♭", "bb": "\U0001D12B",
           "♯": "♯", "♭": "♭"}[m.group(2) or ""]
    return m.group(1).upper() + acc + ("" if no_octave else m.group(3))
