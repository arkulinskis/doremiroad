# Levels — Server Module (no callables). The level format, its checks, the daily practice generator,
# and the built-in road: 9 territories and their levels.
#
# A level's data (levels.data, a Simple Object):
#   intro    text on the level card
#   steps    list of challenges, played in order (formats below)
#   pass     accuracy % needed to clear (default 60);  two / three: accuracy % for 2 and 3 stars (80 / 95)
#   codex    Codex page keys unlocked by clearing it
#   cards    {"clear": composer key, "three": composer key}: cards given the first time it's cleared / three-starred
#   trial    true for a territory's final level (drawn as a fortress on the road)
#
# Steps (every step has "t"; "prompt" is the line shown above it):
#   lesson       title, text, show: [notes to light up], staff: "treble"|"bass"|None      (not scored)
#   notes        notes: ["C4", ...], labels: [...] (optional, one per note), show: "keys"|"names"|"staff",
#                clef: "treble"|"bass", exact: play the exact octave (default: any octave counts)
#   chords       chords: ["C", "Am", "G7", "E4+G4+C5"], labels (optional), hint: light up the keys, exact
#   progression  key: "C", numerals: ["I", "V", "vi", "IV"], hint, names: show chord names under the numerals
#   rush         bpm, seq: "C4 D4 E4:2 | {Am}:4" (see Music.parse_seq), hint: names on the falling notes, exact
#   ear          mode: "note" (play what you hear) | "chord" | "interval" (pick the answer), pool, count
#   quiz         q, options, answer (index), explain
import datetime as dt
import hashlib
import random

from . import Catalog as C
from . import Music as M

STEP_TYPES = ("lesson", "notes", "chords", "progression", "rush", "ear", "quiz")
SHOW_MODES = ("keys", "names", "staff")
CLEFS = ("treble", "bass")
EAR_MODES = ("note", "chord", "interval")
DEFAULT_PASS, DEFAULT_TWO, DEFAULT_THREE = 60, 80, 95


# ---------------------------------------------------------------- step helpers for the built-in levels

def lesson(title, text, show=None, staff=None):
    return {"t": "lesson", "title": title, "text": text, "show": show or [], "staff": staff}


def notes(prompt, ns, show="keys", labels=None, clef="treble", exact=False):
    ns = ns.split() if isinstance(ns, str) else ns
    return {"t": "notes", "prompt": prompt, "notes": ns, "labels": labels or [], "show": show, "clef": clef,
            "exact": exact}


def chords(prompt, cs, hint=True, labels=None, exact=False):
    cs = cs.split() if isinstance(cs, str) else cs
    return {"t": "chords", "prompt": prompt, "chords": cs, "labels": labels or [], "hint": hint, "exact": exact}


def prog(prompt, key, numerals, hint=True, names=True):
    numerals = numerals.split() if isinstance(numerals, str) else numerals
    return {"t": "progression", "prompt": prompt, "key": key, "numerals": numerals, "hint": hint, "names": names}


def rush(prompt, seq, bpm=90, hint=True, exact=False):
    return {"t": "rush", "prompt": prompt, "seq": " ".join(seq.split()), "bpm": bpm, "hint": hint, "exact": exact}


def ear(prompt, mode, pool, count=4):
    pool = pool.split() if isinstance(pool, str) and mode != "chord" else pool
    return {"t": "ear", "prompt": prompt, "mode": mode, "pool": pool, "count": count}


def quiz(q, options, answer=0, explain=""):
    return {"t": "quiz", "q": q, "options": options, "answer": answer, "explain": explain}


def level(key, territory, name, intro, steps, codex=(), cards=None, trial=False, **kw):
    data = {"intro": intro, "steps": steps, "pass": kw.get("pass_", DEFAULT_PASS), "two": DEFAULT_TWO,
            "three": DEFAULT_THREE, "codex": list(codex), "cards": cards or {}, "trial": trial}
    return {"key": key, "territory": territory, "name": name, "data": data}


def scale(key, kind="major", octave=4, down=False):
    s = M.scale_notes(key, kind, octave)
    return list(reversed(s)) if down else s


# ---------------------------------------------------------------- melodies (all traditional or public domain)
MARY = "E4 D4 C4 D4 | E4 E4 E4:2 | D4 D4 D4:2 | E4 G4 G4:2 | E4 D4 C4 D4 | E4 E4 E4 E4 | D4 D4 E4 D4 | C4:4"
ODE = ("E4 E4 F4 G4 | G4 F4 E4 D4 | C4 C4 D4 E4 | E4:1.5 D4:0.5 D4:2 | "
       "E4 E4 F4 G4 | G4 F4 E4 D4 | C4 C4 D4 E4 | D4:1.5 C4:0.5 C4:2")
TWINKLE_F = "F4 F4 C5 C5 | D5 D5 C5:2 | Bb4 Bb4 A4 A4 | G4 G4 F4:2"
ELISE = ("E5:0.5 D#5:0.5 E5:0.5 D#5:0.5 E5:0.5 B4:0.5 D5:0.5 C5:0.5 | A4:1.5 r:0.5 C4:0.5 E4:0.5 A4:0.5 | "
         "B4:1.5 r:0.5 E4:0.5 G#4:0.5 B4:0.5 | C5:2")
GRACE = "G3 | C4:2 E4:0.5 C4:0.5 | E4:2 D4 | C4:2 A3 | G3:2 G3 | C4:2 E4:0.5 C4:0.5 | E4:2 D4 | G4:3"
GREENSLEEVES = ("A4 | C5:2 D5 | E5:1.5 F5:0.5 E5 | D5:2 B4 | G4:1.5 A4:0.5 B4 | C5:2 A4 | "
                "A4:1.5 G#4:0.5 A4 | B4:2 G#4 | E4:2")
MINUET = ("D5 G4:0.5 A4:0.5 B4:0.5 C5:0.5 | D5 G4 G4 | E5 C5:0.5 D5:0.5 E5:0.5 F#5:0.5 | G5 G4 G4")
BLACK_KEYS = "F#4 G#4 A#4 C#5 | D#5:2 C#5 A#4 | G#4 F#4 G#4 A#4 | F#4:4"
CHROMATIC = "C4:0.5 C#4:0.5 D4:0.5 D#4:0.5 E4:0.5 F4:0.5 F#4:0.5 G4:0.5 G#4:0.5 A4:0.5 A#4:0.5 B4:0.5 C5:2"
BLUES_RIFF = ("C4:0.5 Eb4:0.5 F4:0.5 Gb4:0.5 G4 Bb4 | C5:2 Bb4:0.5 G4:0.5 Gb4:0.5 F4:0.5 | Eb4 C4:3")


def chord_seq(symbols, beats):
    return " ".join("{%s}:%s" % (s, beats) for s in symbols.split())


TWELVE_BAR = chord_seq("C7 C7 C7 C7 F7 F7 C7 C7 G7 F7 C7 G7", 2)

# ---------------------------------------------------------------- the built-in road
TERRITORIES = [
    {"key": "ivory", "name": "Ivory Shore", "emoji": "\U0001F3DD️", "color": "#d1b98a", "x": 13, "y": 80,
     "blurb": "Where every pianist begins: the shape of the keyboard, the names of the notes and your first tunes."},
    {"key": "sharpwood", "name": "Sharpwood", "emoji": "\U0001F332", "color": "#4f8c66", "x": 30, "y": 62,
     "blurb": "A forest of black keys. Sharps, flats and the smallest steps in music."},
    {"key": "highlands", "name": "Major Highlands", "emoji": "⛰️", "color": "#8b93b8", "x": 17, "y": 33,
     "blurb": "Climb the major scale, the pattern behind most melodies you know, and learn to measure intervals."},
    {"key": "vale", "name": "Triad Vale", "emoji": "\U0001F304", "color": "#c47a55", "x": 40, "y": 17,
     "blurb": "Three notes at once. Build the major and minor chords that hold music together."},
    {"key": "marsh", "name": "Minor Marsh", "emoji": "\U0001F32B️", "color": "#5e9690", "x": 50, "y": 46,
     "blurb": "Mist and shadow: minor scales, relative keys and the tense chords in between."},
    {"key": "pass", "name": "Progression Pass", "emoji": "\U0001F6E4️", "color": "#cfa245", "x": 66, "y": 75,
     "blurb": "Chords on the move. Roman numerals, cadences and the progressions behind thousands of songs."},
    {"key": "citadel", "name": "Staff Citadel", "emoji": "\U0001F3F0", "color": "#9a6fae", "x": 83, "y": 56,
     "blurb": "The scholars' fortress. Read the treble and bass clefs, from the first lines to sight-reading."},
    {"key": "bayou", "name": "Blue Bayou", "emoji": "\U0001F3B7", "color": "#4c7cc4", "x": 66, "y": 28,
     "blurb": "Smoky clubs and slow water. Seventh chords, the blues and a first taste of jazz."},
    {"key": "summit", "name": "Circle Summit", "emoji": "\U0001F300", "color": "#d05e6a", "x": 86, "y": 13,
     "blurb": "The top of the road: the circle of fifths, every key signature and the Maestro's final test."},
]

LEVELS = [
    # ------------------------------------------------ Ivory Shore
    level("ivory-1", "ivory", "First Light", "Learn the shape of the keyboard and find C anywhere on it.", [
        lesson("The pattern", "Piano keys repeat a pattern: seven white keys and five black ones. Look at the black "
               "keys: they come in a group of two, then a group of three, over and over.",
               ["C#4", "D#4", "F#4", "G#4", "A#4"]),
        lesson("Finding C", "C is the white key just left of each group of two black keys. The one nearest the "
               "middle of the piano is middle C (C4). Every C sounds like the same note, higher or lower.",
               ["C4", "C5"]),
        notes("Play C. The glowing key shows you where.", "C4 C5 C4", show="keys"),
        quiz("Where do you find C?", ["Just left of a group of two black keys", "Just left of a group of three black keys",
                                      "Between two black keys"], 0,
             "C sits just left of the pair of black keys. F sits just left of the group of three."),
        notes("Now find C on your own. Any C counts.", "C4 C5 C4 C5", show="names"),
    ], codex=["keyboard", "find_c"]),
    level("ivory-2", "ivory", "The Musical Alphabet", "Seven letters name every white key. Learn them up and down.", [
        lesson("A to G", "White keys use the letters A to G, then start again. From C: C D E F G A B, then C.",
               ["C4", "D4", "E4", "F4", "G4", "A4", "B4"]),
        notes("Walk up from C to G.", "C4 D4 E4 F4 G4", show="keys"),
        quiz("Which letter comes after G?", ["A", "H", "C"], 0, "The alphabet only runs from A to G, then starts again."),
        notes("Climb the whole octave, C to C, by name.", "C4 D4 E4 F4 G4 A4 B4 C5", show="names"),
        notes("And back down again.", "C5 B4 A4 G4 F4 E4 D4 C4", show="names"),
        notes("Find each note by name.", "F4 A4 D4 G4 B4 E4", show="names"),
    ], codex=["alphabet"], cards={"three": "vivaldi"}),
    level("ivory-3", "ivory", "Octaves", "Same letter, different height. Play in the right octave and train your ear.", [
        lesson("Octaves", "Two notes with the same letter, eight white keys apart, form an octave. Middle C is C4; "
               "the C above it is C5. In this level the octave counts: play the exact key.", ["C4", "C5"]),
        notes("Play these exact keys.", "C4 C5 E4 E5 G4 G5", show="keys", exact=True),
        quiz("Middle C is written as...", ["C4", "C3", "C5"], 0, "Middle C is C4. The C above it is C5."),
        notes("By name, in the right octave.", "C5 C4 A4 F4 D5", show="names", exact=True),
        ear("Listen, then play the note you hear (any octave).", "note", "C4 E4 G4", 3),
    ], codex=["octave"]),
    level("ivory-4", "ivory", "Shore Trial", "Your first songs, in time. Hit the notes as they reach the keys.", [
        lesson("Rush challenges", "Notes fall towards the keyboard. Play each one as it reaches the line. Hit it on "
               "time for a PERFECT, keep a combo going, and don't let the harmony meter run dry. A quarter note lasts "
               "one beat; longer notes are longer bars.", ["C4", "D4", "E4"]),
        rush("Mary Had a Little Lamb", MARY, bpm=88),
        rush("Ode to Joy (Beethoven)", ODE, bpm=96),
    ], codex=["rhythm"], cards={"clear": "satie"}, trial=True),

    # ------------------------------------------------ Sharpwood
    level("sharp-1", "sharpwood", "Black Keys", "Sharps go up, flats go down. Every black key has two names.", [
        lesson("Sharps and flats", "A sharp (♯) is the very next key up; a flat (♭) the very next key down. "
               "The black key between C and D is both C♯ and D♭.", ["C4", "C#4", "D4"]),
        notes("Play the sharps.", "F#4 C#4 G#4 D#4 A#4", show="keys"),
        notes("Now the flats, by name.", "Bb4 Eb4 Ab4 Db4 Gb4", show="names"),
        quiz("C♯ and D♭ are...", ["The same key", "Two different keys", "Not on a piano"], 0,
             "Two names for one sound: they are enharmonic."),
        notes("Mixed names. Think about which way to go.", "F#4 Bb4 C#5 Ab4 D#4", show="names"),
    ], codex=["sharps_flats"]),
    level("sharp-2", "sharpwood", "Half & Whole Steps", "Measure the smallest distances in music.", [
        lesson("Steps", "A half step is the very next key. A whole step is two half steps. E–F and B–C are half "
               "steps: no black key sits between them.", ["E4", "F4", "B4", "C5"]),
        quiz("Which pair is a half step apart?", ["E and F", "C and D", "F and G"], 0,
             "E and F have no black key between them."),
        notes("Find each note.", "F4 D4 C5 F#4 A4", show="names",
              labels=["A half step above E", "A whole step above C", "A half step above B", "A whole step above E",
                      "A whole step above G"]),
        quiz("How many half steps make a whole step?", ["2", "1", "3"], 0),
        notes("Down this time.", "B4 G4 Eb4 A4", show="names",
              labels=["A half step below C", "A whole step below A", "A half step below E", "A whole step below B"]),
    ], codex=["half_whole"], cards={"three": "fanny"}),
    level("sharp-3", "sharpwood", "Chromatic Climb", "Every key in a row, then a melody on the black keys only.", [
        lesson("The chromatic scale", "Play every key, black and white, and you move in half steps. Twelve of them "
               "take you up an octave.", ["C4", "C#4", "D4", "D#4", "E4"]),
        rush("Chromatic climb", CHROMATIC, bpm=84),
        rush("Black-key song", BLACK_KEYS, bpm=92),
    ], codex=["chromatic"]),
    level("sharp-4", "sharpwood", "Sharpwood Trial", "Ears, names and a famous opening. Prove you know the forest.", [
        ear("Play the note you hear.", "note", "C4 D4 E4 F4 G4", 4),
        notes("Sharps, flats and naturals.", "F#4 Bb4 E4 Db4 G#4 B4", show="names"),
        rush("Für Elise (Beethoven)", ELISE, bpm=76),
    ], codex=[], cards={"clear": "grieg"}, trial=True),

    # ------------------------------------------------ Major Highlands
    level("high-1", "highlands", "The Major Formula", "Whole, whole, half, whole, whole, whole, half.", [
        lesson("The major scale", "A major scale follows a pattern of steps: whole, whole, half, whole, whole, whole, "
               "half. From C it uses only white keys.", scale("C")),
        notes("Play C major, up.", scale("C"), show="keys"),
        quiz("The major scale pattern is...", ["W W H W W W H", "W H W W H W W", "W W W H W W H"], 0),
        notes("Now down, by name.", scale("C", down=True), show="names"),
        rush("C major, in time", " ".join(scale("C")) + " " + " ".join(scale("C", down=True)[1:]), bpm=96),
    ], codex=["major_scale"]),
    level("high-2", "highlands", "G Major", "Start the formula on G and meet your first key with a sharp.", [
        lesson("G major", "Start the pattern on G and the 7th note must be F♯ to keep a half step below the top.",
               scale("G")),
        notes("G major, up.", scale("G"), show="names"),
        quiz("Which note is sharp in G major?", ["F♯", "C♯", "B♭"], 0),
        rush("G major up and down", " ".join(scale("G")) + " " + " ".join(scale("G", down=True)[1:]), bpm=100),
    ], codex=["g_major"]),
    level("high-3", "highlands", "F Major", "Start the formula on F and meet your first flat.", [
        lesson("F major", "Start on F and the 4th note must be B♭, a half step above A.", scale("F")),
        notes("F major, up.", scale("F"), show="names"),
        quiz("F major has one flat. Which one?", ["B♭", "E♭", "F♭"], 0),
        rush("Twinkle, Twinkle in F", TWINKLE_F, bpm=92),
    ], codex=["f_major"], cards={"three": "haydn"}),
    level("high-4", "highlands", "Intervals", "Measure the distance between two notes, and hear it.", [
        lesson("Counting intervals", "Count letter names, including both ends. C to E is a 3rd (C, D, E). C to G is "
               "a 5th. C to the next C is an octave.", ["C4", "E4", "G4", "C5"]),
        notes("Find each note above C.", "E4 G4 C5 F4 A4", show="names",
              labels=["A 3rd above C", "A 5th above C", "An octave above C", "A 4th above C", "A 6th above C"]),
        lesson("The perfect fifth", "Seven half steps, C to G. After the octave it is the most stable sound there is. "
               "Listen for its open, hollow sound.", ["C4", "G4"]),
        ear("Which interval did you hear?", "interval", "M3 P5 P8", 5),
        quiz("C up to G is a...", ["5th", "4th", "3rd"], 0, "C, D, E, F, G: five letters, so a 5th."),
    ], codex=["intervals", "fifths"]),
    level("high-5", "highlands", "Highlands Trial", "Five notes that never clash, a famous hymn and a fast scale.", [
        lesson("The pentatonic scale", "Leave out the 4th and 7th of the major scale and you get C D E G A: five "
               "notes with no half steps. Amazing Grace uses only these.", ["C4", "D4", "E4", "G4", "A4"]),
        rush("Amazing Grace", GRACE, bpm=84),
        ear("Play the note you hear.", "note", "C4 E4 G4 A4", 3),
        rush("C major at speed", " ".join(scale("C")) + " " + " ".join(scale("C", down=True)[1:]), bpm=126,
             hint=False),
    ], codex=["pentatonic"], cards={"clear": "handel"}, trial=True),

    # ------------------------------------------------ Triad Vale
    level("vale-1", "vale", "Stacking Thirds", "Three notes, one sound. Build your first chords.", [
        lesson("Triads", "A triad is a root, a 3rd and a 5th. On white keys, skip one key between each note: C–E–G.",
               ["C4", "E4", "G4"]),
        lesson("Playing a chord", "Press all three keys together. On a computer keyboard hold them at once; with a "
               "mouse, click them one after another quickly.", ["C4", "E4", "G4"]),
        chords("Play these major chords.", "C F G", hint=True),
        chords("Same chords, no lights.", "C G F C", hint=False),
    ], codex=["triads", "major_chord"]),
    level("vale-2", "vale", "Major & Minor", "Lower one note and the mood turns. Hear the difference.", [
        lesson("Minor chords", "Lower the middle note of a major chord by a half step and it becomes minor. A minor "
               "is A–C–E.", ["A3", "C4", "E4"]),
        chords("Play these minor chords.", "Am Dm Em", hint=True),
        lesson("Thirds", "A major 3rd is four half steps (C–E); a minor 3rd is three (C–E♭). Major sounds "
               "bright, minor sounds darker.", ["C4", "E4", "Eb4"]),
        ear("Major or minor?", "chord", ["major", "minor"], 6),
        chords("Mixed, no lights.", "C Am F Dm", hint=False),
    ], codex=["minor_chord", "thirds"]),
    level("vale-3", "vale", "Chord Rush", "Chords falling in time. Land all three notes together.", [
        rush("Four chords", chord_seq("C F G C", 4), bpm=84),
        quiz("Which chord is A–C–E?", ["A minor", "A major", "C major"], 0),
        rush("Eight chords", chord_seq("C Am Dm G C F G C", 4), bpm=92),
    ], codex=[], cards={"three": "schubert"}),
    level("vale-4", "vale", "Inversions", "Reorder the notes, keep the name, move your hand less.", [
        lesson("Inversions", "C–E–G is root position. E–G–C is the 1st inversion, G–C–E the 2nd. "
               "Same chord, different shape.", ["E4", "G4", "C5"]),
        chords("Play these exact shapes.", ["C4+E4+G4", "E4+G4+C5", "G4+C5+E5"], hint=True, exact=True,
               labels=["C major, root position", "C major, 1st inversion", "C major, 2nd inversion"]),
        quiz("E–G–C is which inversion of C major?", ["1st", "2nd", "Root position"], 0,
             "The 3rd (E) is at the bottom: 1st inversion."),
        chords("Smooth moves: C to F to G using inversions.", ["C4+E4+G4", "C4+F4+A4", "B3+D4+G4", "C4+E4+G4"],
               hint=True, exact=True, labels=["C", "F (2nd inversion)", "G (1st inversion)", "C"]),
    ], codex=["inversions"]),
    level("vale-5", "vale", "Vale Trial", "Chords by name, by ear and in time.", [
        chords("No lights. Name to keys.", "G Em C D", hint=False),
        ear("Major or minor?", "chord", ["major", "minor"], 5),
        rush("Chord rush", chord_seq("C Am F G C Am F G", 2), bpm=96, hint=False),
    ], codex=[], cards={"clear": "mendelssohn"}, trial=True),

    # ------------------------------------------------ Minor Marsh
    level("marsh-1", "marsh", "Natural Minor", "Whole, half, whole, whole, half, whole, whole.", [
        lesson("The natural minor scale", "A minor uses only white keys, from A to A. Its pattern is W H W W H W W.",
               scale("Am", "minor", 3)),
        notes("A minor, up.", scale("Am", "minor", 3), show="keys"),
        quiz("The natural minor pattern is...", ["W H W W H W W", "W W H W W W H", "H W W H W W W"], 0),
        notes("Down, by name.", scale("Am", "minor", 3, down=True), show="names"),
    ], codex=["natural_minor"]),
    level("marsh-2", "marsh", "Relative Keys", "Every major key has a minor twin with the same notes.", [
        lesson("Relatives", "C major and A minor share every note. The relative minor starts three half steps below "
               "the major key's home note.", ["C4", "A3"]),
        quiz("What is the relative minor of C major?", ["A minor", "C minor", "E minor"], 0),
        quiz("What is the relative minor of G major?", ["E minor", "G minor", "B minor"], 0,
             "Three half steps below G is E."),
        chords("Major and its relative.", "C Am G Em", hint=False),
        rush("Greensleeves (traditional)", GREENSLEEVES, bpm=104),
    ], codex=["relative"]),
    level("marsh-3", "marsh", "Diminished & Augmented", "Two more colours of triad: tense and floating.", [
        lesson("Diminished and augmented", "Two minor 3rds make a diminished chord (B–D–F). Two major 3rds make "
               "an augmented chord (C–E–G♯).", ["B3", "D4", "F4"]),
        chords("Build them.", "Bdim Caug Ddim Faug", hint=True),
        ear("Which kind of chord?", "chord", ["major", "minor", "diminished", "augmented"], 6),
    ], codex=["dim_aug"]),
    level("marsh-4", "marsh", "Harmonic Minor", "Raise the 7th and the scale turns dramatic.", [
        lesson("Harmonic minor", "Raise the 7th of A minor from G to G♯. The new note leans hard into the A above.",
               scale("Am", "harmonic", 3)),
        notes("A harmonic minor, by name.", scale("Am", "harmonic", 3), show="names"),
        rush("Harmonic minor run", " ".join(scale("Am", "harmonic", 3)) + " " +
             " ".join(scale("Am", "harmonic", 3, down=True)[1:]), bpm=104),
    ], codex=["harmonic_minor"], cards={"three": "chopin"}),
    level("marsh-5", "marsh", "Marsh Trial", "A haunting progression, sharp ears and a minor scale on its own.", [
        rush("The Rising Sun (traditional)", chord_seq("Am C D F Am C E E", 3), bpm=120),
        ear("Which kind of chord?", "chord", ["major", "minor", "diminished", "augmented"], 5),
        notes("E natural minor, by name.", scale("Em", "minor", 4), show="names"),
    ], codex=[], cards={"clear": "tchaikovsky"}, trial=True),

    # ------------------------------------------------ Progression Pass
    level("prog-1", "pass", "Roman Numerals", "Number the chords of a key and play them by number.", [
        lesson("Numbering chords", "Each note of the scale has a chord. In C major: I = C, ii = Dm, iii = Em, IV = F, "
               "V = G, vi = Am. Upper case is major, lower case minor.", ["C4", "E4", "G4"]),
        quiz("In C major, what is V?", ["G", "F", "A minor"], 0, "Count up the scale: C D E F G. The 5th note is G."),
        prog("I – IV – V – I in C.", "C", "I IV V I", hint=True),
        lesson("I, IV and V", "The three major chords of a key contain every note of its scale. Countless songs use "
               "nothing else.", ["F4", "A4", "C5"]),
        prog("The same in G major.", "G", "I IV V I", hint=False),
    ], codex=["numerals", "one_four_five"]),
    level("prog-2", "pass", "Cadences", "How music says 'the end', 'amen' and 'to be continued'.", [
        lesson("Cadences", "V to I is the strongest ending in music. IV to I is the gentle 'Amen'. Ending on V leaves "
               "the phrase hanging.", ["G3", "B3", "D4"]),
        prog("An authentic cadence.", "C", "IV V I", hint=True),
        lesson("The dominant", "V is the dominant. Its chord holds the leading tone (B in C), a half step under home, "
               "and that is what pulls it back to I.", ["B3", "C4"]),
        prog("The 'Amen' cadence in F.", "F", "I IV I", hint=True),
        quiz("Which is the strongest 'full stop'?", ["V → I", "IV → I", "I → V"], 0),
    ], codex=["cadences", "dominant"]),
    level("prog-3", "pass", "The Pop Engine", "Four chords, a thousand songs.", [
        lesson("I – V – vi – IV", "C, G, Am, F. Loop it and you will recognise it everywhere.",
               ["C4", "E4", "G4"]),
        prog("Play the loop in C.", "C", "I V vi IV", hint=True),
        rush("In time", chord_seq("C G Am F C G Am F", 2), bpm=100),
        prog("In G, from the numerals alone.", "G", "I V vi IV", hint=False, names=False),
    ], codex=["pop_progression"], cards={"three": "joplin"}),
    level("prog-4", "pass", "Doo-Wop & Canon", "Two classics: the fifties ballad and Pachelbel's walk.", [
        lesson("I – vi – IV – V", "The doo-wop progression: C, Am, F, G.", ["A3", "C4", "E4"]),
        prog("Doo-wop in C.", "C", "I vi IV V", hint=True),
        lesson("The Canon", "Pachelbel's Canon: I V vi iii IV I IV V.", ["E3", "G3", "B3"]),
        rush("Canon in C", chord_seq("C G Am Em F C F G", 2), bpm=92),
    ], codex=["fifties", "canon"]),
    level("prog-5", "pass", "Pass Trial", "Any key, from the numerals. Show you can think in progressions.", [
        prog("I – IV – V – I in D.", "D", "I IV V I", hint=False),
        quiz("In G major, vi is...", ["E minor", "A minor", "D major"], 0, "G A B C D E: the 6th note is E, and vi is minor."),
        prog("Doo-wop in F, numerals only.", "F", "I vi IV V", hint=False, names=False),
        rush("Pop loop in G", chord_seq("G D Em C G D Em C", 2), bpm=104, hint=False),
    ], codex=[], cards={"clear": "liszt"}, trial=True),

    # ------------------------------------------------ Staff Citadel
    level("staff-1", "citadel", "The Staff", "Five lines that hold every melody ever written down.", [
        lesson("The staff", "Notes sit on the five lines or in the spaces between them. Higher on the staff means "
               "higher in pitch.", ["E4", "F4", "G4"], staff="treble"),
        lesson("Treble clef lines", "From the bottom: E G B D F.", ["E4", "G4", "B4", "D5", "F5"], staff="treble"),
        notes("Play the lines.", "E4 G4 B4 D5 F5", show="staff"),
        lesson("Treble clef spaces", "From the bottom they spell FACE.", ["F4", "A4", "C5", "E5"], staff="treble"),
        notes("Play the spaces.", "F4 A4 C5 E5", show="staff"),
    ], codex=["staff", "treble"]),
    level("staff-2", "citadel", "Treble Reading", "Read the treble clef, note by note.", [
        notes("Read and play.", "G4 C5 E4 A4 D5 F4 B4", show="staff"),
        quiz("Treble clef lines from the bottom:", ["E G B D F", "F A C E", "G B D F A"], 0),
        notes("A little tune. Read it.", "E4 D4 C4 D4 E4 E4 E4", show="staff"),
        notes("Higher up.", "C5 D5 E5 F5 G5 E5 C5", show="staff"),
    ], codex=[]),
    level("staff-3", "citadel", "Bass Clef", "The left hand's home: the bass clef.", [
        lesson("Bass clef lines", "From the bottom: G B D F A.", ["G2", "B2", "D3", "F3", "A3"], staff="bass"),
        notes("Play the lines.", "G2 B2 D3 F3 A3", show="staff", clef="bass"),
        lesson("Bass clef spaces", "From the bottom: A C E G.", ["A2", "C3", "E3", "G3"], staff="bass"),
        notes("Play the spaces.", "A2 C3 E3 G3", show="staff", clef="bass"),
        quiz("Bass clef lines from the bottom:", ["G B D F A", "E G B D F", "A C E G"], 0),
        notes("Read and play.", "C3 F3 A2 D3 G3 B2", show="staff", clef="bass"),
    ], codex=["bass"]),
    level("staff-4", "citadel", "Middle C & Ledger Lines", "Where the two clefs meet.", [
        lesson("Ledger lines", "Middle C sits on a short ledger line below the treble staff, and on one above the bass "
               "staff.", ["C4"], staff="treble"),
        notes("Around middle C, treble clef. Exact octave.", "C4 D4 B3 C4 A3", show="staff", exact=True),
        notes("Around middle C, bass clef. Exact octave.", "C4 B3 D4 A3 C4", show="staff", clef="bass", exact=True),
        notes("High ledger lines.", "A5 G5 B5 C6", show="staff", exact=True),
    ], codex=["ledger"], cards={"three": "clara"}),
    level("staff-5", "citadel", "Citadel Trial", "Sight-read in both clefs, then play a minuet in 3/4.", [
        notes("Treble clef, exact octave.", "C4 E4 G4 C5 A4 F4 D4 B3", show="staff", exact=True),
        notes("Bass clef, exact octave.", "C3 G2 E3 A2 F3 D3 B2 C3", show="staff", clef="bass", exact=True),
        lesson("3/4 time", "A minuet counts three beats to a bar: ONE two three, ONE two three.", ["D5", "G4"]),
        rush("Minuet in G (attributed to Petzold)", MINUET, bpm=100, hint=False),
    ], codex=["time_sig"], cards={"clear": "mozart"}, trial=True),

    # ------------------------------------------------ Blue Bayou
    level("bayou-1", "bayou", "Seventh Chords", "Add one more third and the colours deepen.", [
        lesson("Sevenths", "Cmaj7 is dreamy, C7 restless, Cm7 mellow. Each one adds a 7th on top of a triad.",
               ["C4", "E4", "G4", "B4"]),
        chords("Play the three sevenths on C.", "Cmaj7 C7 Cm7", hint=True),
        ear("Which seventh chord?", "chord", ["major 7th", "dominant 7th", "minor 7th"], 6),
        chords("No lights.", "G7 Dm7 Fmaj7", hint=False),
    ], codex=["sevenths"]),
    level("bayou-2", "bayou", "The Blues Scale", "Six notes and one of them is blue.", [
        lesson("The blues scale", "C E♭ F G♭ G B♭ C. The G♭ is the 'blue note'.",
               ["C4", "Eb4", "F4", "Gb4", "G4", "Bb4", "C5"]),
        notes("Play the blues scale.", "C4 Eb4 F4 Gb4 G4 Bb4 C5", show="keys"),
        rush("A blues riff", BLUES_RIFF, bpm=92),
        notes("By name, down.", "C5 Bb4 G4 Gb4 F4 Eb4 C4", show="names"),
    ], codex=["blues_scale"]),
    level("bayou-3", "bayou", "Twelve-Bar Blues", "The form behind the blues and early rock 'n' roll.", [
        lesson("Twelve bars", "I I I I | IV IV I I | V IV I V, usually as dominant 7th chords.",
               ["C4", "E4", "G4", "Bb4"]),
        prog("Twelve-bar blues in C.", "C", "I7 I7 I7 I7 IV7 IV7 I7 I7 V7 IV7 I7 V7", hint=True),
        rush("In time", TWELVE_BAR, bpm=112),
    ], codex=["twelve_bar"], cards={"three": "ellington"}),
    level("bayou-4", "bayou", "ii – V – I", "Jazz's favourite sentence.", [
        lesson("ii – V – I", "Dm7, G7, Cmaj7. Each root falls a fifth to the next.", ["D4", "F4", "A4", "C5"]),
        prog("ii – V – I in C.", "C", "ii7 V7 Imaj7", hint=True),
        prog("In F.", "F", "ii7 V7 Imaj7", hint=False),
        prog("In B♭, numerals only.", "Bb", "ii7 V7 Imaj7", hint=False, names=False),
        rush("Swing it", chord_seq("Dm7 G7", 4) + " {Cmaj7}:8", bpm=90),
    ], codex=["two_five_one"]),
    level("bayou-5", "bayou", "Bayou Trial", "Ears, form and feel. The bayou's final test.", [
        ear("Which chord?", "chord", ["major", "minor", "dominant 7th", "major 7th", "minor 7th"], 6),
        prog("Blues in G, no lights.", "G", "I7 IV7 I7 V7 IV7 I7", hint=False),
        rush("Blues riff at speed", BLUES_RIFF, bpm=112, hint=False),
    ], codex=[], cards={"clear": "gershwin"}, trial=True),

    # ------------------------------------------------ Circle Summit
    level("summit-1", "summit", "Circle of Fifths", "Every key, arranged in a circle.", [
        lesson("The circle", "Up a fifth from C is G (one sharp), then D (two), A (three). Down a fifth from C is F "
               "(one flat), then B♭ (two).", ["C4", "G4", "D4"]),
        quiz("A fifth above C is...", ["G", "F", "D"], 0),
        quiz("Which key has two sharps?", ["D major", "A major", "B♭ major"], 0),
        notes("Walk the circle by fifths.", "C4 G4 D4 A4 E4 B4 F#4", show="names",
              labels=["C: no sharps", "G: 1 sharp", "D: 2 sharps", "A: 3 sharps", "E: 4 sharps", "B: 5 sharps",
                      "F♯: 6 sharps"]),
    ], codex=["circle"]),
    level("summit-2", "summit", "Key Signatures", "Read a key from its sharps and flats.", [
        lesson("Key signatures", "Sharps arrive in the order F C G D A E B, flats in the order B E A D G C F.",
               ["F#4", "C#5"]),
        quiz("The order of sharps begins...", ["F C G", "B E A", "C G D"], 0),
        quiz("Which major key has three flats?", ["E♭ major", "A♭ major", "B♭ major"], 0,
             "B♭, E♭, A♭: three flats is E♭ major."),
        notes("D major, by name.", scale("D"), show="names"),
        notes("B♭ major, by name.", scale("Bb", octave=3), show="names"),
    ], codex=["key_sigs"], cards={"three": "rachmaninoff"}),
    level("summit-3", "summit", "Modes", "Same notes, new home, new mood.", [
        lesson("Dorian and Mixolydian", "White keys from D to D give the Dorian mode: minor with a bright 6th. From G to "
               "G, the Mixolydian: major with a flat 7th.", scale("D", "dorian")),
        notes("D Dorian, by name.", scale("D", "dorian"), show="names"),
        rush("G Mixolydian", " ".join(scale("G", "mixolydian", 3)) + " " +
             " ".join(scale("G", "mixolydian", 3, down=True)[1:]), bpm=108),
    ], codex=["modes"], cards={"three": "debussy"}),
    level("summit-4", "summit", "The Maestro's Ascent", "Everything you've learned, in one last climb.", [
        prog("Canon in D, numerals only.", "D", "I V vi iii IV I IV V", hint=False, names=False),
        ear("Which interval?", "interval", "m3 M3 P4 P5 M6 P8", 5),
        chords("Chords from anywhere.", "Bb F#m Ebmaj7 B7 Gm", hint=False),
        rush("Ode to Joy, the finale", ODE, bpm=120, hint=False),
        rush("C major, two octaves at speed",
             " ".join(scale("C", octave=4) + scale("C", octave=5)[1:]) + " " +
             " ".join(scale("C", octave=5, down=True)[1:] + scale("C", octave=4, down=True)[1:]), bpm=132, hint=False),
    ], codex=[], cards={"clear": "beethoven", "three": "bach"}, trial=True),
]


# ---------------------------------------------------------------- checking and totals

def _step_items(s):
    """How many scored items a step has, and what kind they are: (count, kind)."""
    t = s.get("t")
    if t == "notes":
        return len(s.get("notes") or []), "notes"
    if t == "chords":
        return len(s.get("chords") or []), "chords"
    if t == "progression":
        return len(s.get("numerals") or []), "chords"
    if t == "rush":
        parsed = M.parse_seq(s.get("seq"))
        return (len(parsed[0]) if parsed else 0), "rush"
    if t == "ear":
        return _int(s.get("count"), 1, 12), "ear"
    if t == "quiz":
        return 1, "quiz"
    return 0, None


def _int(v, lo, hi, default=None):
    try:
        v = int(v)
    except Exception:
        return default if default is not None else lo
    return max(lo, min(hi, v))


def totals(data):
    """What a level holds: scored items (all, and by kind) and steps."""
    out = {"items": 0, "steps": 0, "notes": 0, "chords": 0, "rush": 0, "rush_notes": 0, "rush_chords": 0,
           "ear": 0, "quiz": 0}
    for s in (data or {}).get("steps") or []:
        if not isinstance(s, dict):
            continue
        n, kind = _step_items(s)
        out["steps"] += 1
        out["items"] += n
        if kind:
            out[kind] += n
        if kind == "rush":
            parsed = M.parse_seq(s.get("seq"))
            for e in (parsed[0] if parsed else []):
                out["rush_chords" if len(e["notes"]) > 1 else "rush_notes"] += 1
    return out


def check(data):
    """Problems with a level: (errors, warnings). Errors stop it being published.

    forms/AdminPage.html has the same rules for live checks (it uses lib/music.js); keep them in step.
    """
    errors, warnings = [], []
    steps = (data or {}).get("steps") or []
    if not steps:
        errors.append("The level has no steps.")
    scored = 0
    for i, s in enumerate(steps):
        where = "Step %d" % (i + 1)
        t = s.get("t") if isinstance(s, dict) else None
        if t not in STEP_TYPES:
            errors.append("%s: unknown kind of step." % where)
            continue
        n, _ = _step_items(s)
        scored += n
        if t == "lesson":
            if not (s.get("text") or "").strip():
                warnings.append("%s: the lesson has no text." % where)
            for x in s.get("show") or []:
                if M.parse_note(x) is None:
                    errors.append("%s: '%s' isn't a note (write it like C4, F#3 or Bb4)." % (where, x))
        elif t == "notes":
            if not s.get("notes"):
                errors.append("%s: add at least one note." % where)
            for x in s.get("notes") or []:
                if M.parse_note(x) is None:
                    errors.append("%s: '%s' isn't a note (write it like C4, F#3 or Bb4)." % (where, x))
            if s.get("show") == "staff":
                for x in s.get("notes") or []:
                    m = M.parse_note(x)
                    if m is not None and not (36 <= m <= 88):
                        warnings.append("%s: %s is far off the staff." % (where, x))
        elif t == "chords":
            if not s.get("chords"):
                errors.append("%s: add at least one chord." % where)
            for x in s.get("chords") or []:
                if M.chord_of(x) is None:
                    errors.append("%s: '%s' isn't a chord I know (try C, Am, G7, Bdim or C4+E4+G4)." % (where, x))
        elif t == "progression":
            if M.parse_key(s.get("key")) is None:
                errors.append("%s: '%s' isn't a key (try C, G, Bb or Am)." % (where, s.get("key")))
            elif not s.get("numerals"):
                errors.append("%s: add at least one numeral." % where)
            else:
                for x in s.get("numerals") or []:
                    if M.parse_numeral(x, s.get("key")) is None:
                        errors.append("%s: '%s' isn't a Roman numeral I know (try I, ii, V7, vii°)." % (where, x))
        elif t == "rush":
            parsed = M.parse_seq(s.get("seq"))
            if parsed is None:
                errors.append("%s: the note sequence has a token I can't read." % where)
            elif not parsed[0]:
                errors.append("%s: the note sequence is empty." % where)
            elif parsed[1] > 400:
                warnings.append("%s: that's a very long rush (%d beats)." % (where, parsed[1]))
            bpm = _int(s.get("bpm"), 0, 1000)
            if not (30 <= bpm <= 240):
                errors.append("%s: tempo must be between 30 and 240 BPM." % where)
        elif t == "ear":
            mode = s.get("mode")
            pool = s.get("pool") or []
            if mode not in EAR_MODES:
                errors.append("%s: choose what the ear question plays." % where)
            elif len(pool) < (1 if mode == "note" else 2):
                errors.append("%s: the answer pool needs %s." % (where, "a note" if mode == "note" else "at least 2 answers"))
            else:
                for x in pool:
                    ok = (M.parse_note(x) is not None) if mode == "note" else \
                        (x in M.EAR_CHORDS) if mode == "chord" else (x in M.INTERVALS)
                    if not ok:
                        errors.append("%s: '%s' can't be used in this ear question." % (where, x))
        elif t == "quiz":
            opts = [o for o in s.get("options") or [] if str(o).strip()]
            if not (s.get("q") or "").strip():
                errors.append("%s: the quiz has no question." % where)
            if len(opts) < 2:
                errors.append("%s: the quiz needs at least 2 answers." % where)
            elif not (0 <= _int(s.get("answer"), -1, 99, -1) < len(opts)):
                errors.append("%s: pick which answer is right." % where)
    for k in (data or {}).get("codex") or []:
        if k not in C.CODEX_BY_KEY:
            errors.append("Unknown Codex page '%s'." % k)
    for when, k in ((data or {}).get("cards") or {}).items():
        if k and k not in C.COMPOSER_BY_KEY:
            errors.append("Unknown composer card '%s'." % k)
    p, two, three = (_int((data or {}).get(k), 0, 100, d) for k, d in
                     (("pass", DEFAULT_PASS), ("two", DEFAULT_TWO), ("three", DEFAULT_THREE)))
    if not (p <= two <= three):
        errors.append("Star thresholds must go up: pass ≤ two stars ≤ three stars.")
    if steps and scored == 0:
        warnings.append("Nothing in this level is scored (only lessons): everyone gets three stars.")
    return errors, warnings


# ---------------------------------------------------------------- daily practice

def daily_tier(conquered):
    """Which pool the daily practice draws from, by territories conquered."""
    return 0 if conquered < 2 else 1 if conquered < 4 else 2 if conquered < 6 else 3


def daily(day, tier):
    """Today's practice level: the same for every player in the same tier, different each day."""
    tier = max(0, min(3, int(tier)))
    seed = int(hashlib.sha256(("daily:%s:%d" % (day.isoformat(), tier)).encode()).hexdigest()[:12], 16)
    rnd = random.Random(seed)
    keys = [["C"], ["C", "G", "F"], ["C", "G", "F", "D", "Bb"], ["C", "G", "F", "D", "Bb", "A", "Eb"]][tier]
    key = rnd.choice(keys)
    sc = M.scale_notes(key, "major", 4)
    steps = []
    ear_pool = [sc[0], sc[2], sc[4]] if tier == 0 else sc[:7]
    steps.append(ear("Warm up your ears: play the note you hear.", "note", ear_pool, 4))
    if tier == 0:
        steps.append(notes("Find these notes by name.", [rnd.choice(sc[:7]) for _ in range(6)], show="names"))
    else:
        pool = [M.parse_numeral(n, key)["symbol"].replace("♯", "#").replace("♭", "b")
                for n in (["I", "ii", "IV", "V", "vi"] if tier < 3 else ["ii7", "V7", "Imaj7", "vi7", "IV"])]
        steps.append(chords("Chords in %s." % M.key_name(key), [rnd.choice(pool) for _ in range(5)], hint=tier < 2))
    if tier >= 2:
        steps.append(prog("A progression in %s." % M.key_name(key), key,
                          rnd.choice(["I V vi IV", "I vi IV V", "ii V I", "I IV V I", "vi IV I V"]), hint=False))
    if tier >= 1:
        steps.append(ear("Which chord?", "chord", ["major", "minor"] + (["dominant 7th"] if tier >= 3 else []), 3))
    # a melody: a random walk on the pentatonic notes of the key
    penta = [sc[i] for i in (0, 1, 2, 4, 5)] + [sc[7]]
    i, toks = 0, []
    for n in range(12 + 4 * tier):
        i = max(0, min(len(penta) - 1, i + rnd.choice([-2, -1, -1, 1, 1, 2])))
        toks.append(penta[i] + (":2" if n % 4 == 3 else ""))
    toks.append(sc[0] + ":2")
    steps.append(rush("A melody in %s." % M.key_name(key), " ".join(toks), bpm=84 + 8 * tier, hint=tier < 2))
    return {"key": "daily-%s-t%d" % (day.isoformat(), tier), "name": "Daily Practice",
            "data": {"intro": "A fresh warm-up every day. Keep your streak alive for bigger rewards.",
                     "steps": steps, "pass": 50, "two": 80, "three": 95, "codex": [], "cards": {}, "trial": False}}
