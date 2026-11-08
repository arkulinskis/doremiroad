"""lib/music.js and server_code/Music.py must agree. Runs both on the same inputs and compares.

    python -I tools/testing/music_parity.py      # prints PARITY OK at the end
"""
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
sys.path.insert(0, str(PROJECT / "server_code"))
import Music as M  # noqa: E402  (Music.py has no relative imports)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NOTES = ["C4", "c4", "F#3", "Bb4", "B#3", "Cb4", "E##4", "Abb2", "A0", "C8", "H4", "C", "C10", "D♯5", "G♭3", ""]
CHORDS = ["C", "Am", "G7", "Bdim", "Caug", "C+", "Ebmaj7", "F#m", "Dm7", "Bm7b5", "Bø", "Gdim7", "Csus4", "Dsus2", "A5",
          "C6", "Am6", "Cadd9", "G9", "C/E", "G/B", "Am/C", "F/C", "CM7", "C-7", "Cxyz", "H", "c", "B♭", "C4+E4+G4",
          "E4+G4+C5", "C4+Q4"]
KEYS = ["C", "G", "F", "D", "Bb", "Eb", "A", "E", "F#", "Am", "Em", "Dm", "C#m", "Bbm", "X"]
NUMERALS = ["I", "ii", "iii", "IV", "V", "vi", "vii°", "V7", "Imaj7", "ii7", "viiø7", "viio7", "bVII", "#iv°",
            "III+", "i", "iv", "v", "VI", "VII", "IX", "v7"]
SEQS = ["C4 D4:2 | r:1 C4+E4+G4:0.5 {Am}:4", "C4 X9", "C4:0", "C4:1e1", "{G7}:2 {Cmaj7}:.5 _:1 -:2", "C4+C4:3", "", "E5:16 D5:17"]
SCALES = [("C", "major", 4), ("G", "major", 4), ("F", "major", 4), ("Bb", "major", 3), ("Am", "minor", 3),
          ("Am", "harmonic", 3), ("D", "dorian", 4), ("G", "mixolydian", 3), ("F#", "major", 4), ("Eb", "minor", 4)]


def chord_view(c):
    return None if c is None else {k: c[k] for k in ("root", "type", "symbol", "name", "notes", "spelled")}


def python_side():
    return {
        "notes": [M.parse_note(n) for n in NOTES],
        "chords": [chord_view(M.chord_of(c)) for c in CHORDS],
        "keys": [list(M.parse_key(k)) if M.parse_key(k) else None for k in KEYS] + [M.key_name(k) for k in KEYS],
        "numerals": [chord_view(M.parse_numeral(n, k)) for k in ("C", "F", "Bb", "Am", "D") for n in NUMERALS],
        "seqs": [None if M.parse_seq(s) is None else
                 [[{k: e[k] for k in ("t", "d", "notes", "label")} for e in M.parse_seq(s)[0]], M.parse_seq(s)[1]]
                 for s in SEQS],
        "scales": [M.scale_notes(*a) for a in SCALES],
        "names": [M.name_of(m) for m in range(21, 109, 7)] + [M.name_of(m, True) for m in range(21, 109, 7)],
    }


JS = r"""
require(process.argv[1]);
const M = globalThis.DR.Music;
const I = JSON.parse(process.argv[2]);
const cv = c => c == null ? null : {root: c.root, type: c.type, symbol: c.symbol, name: c.name, notes: c.notes, spelled: c.spelled};
const out = {
  notes: I.NOTES.map(M.parseNote),
  chords: I.CHORDS.map(c => cv(M.chordOf(c))),
  keys: I.KEYS.map(k => M.parseKey(k)).concat(I.KEYS.map(M.keyName)),
  numerals: [].concat(...['C', 'F', 'Bb', 'Am', 'D'].map(k => I.NUMERALS.map(n => cv(M.parseNumeral(n, k))))),
  seqs: I.SEQS.map(s => { const r = M.parseSeq(s); return r == null ? null : [r[0].map(e => ({t: e.t, d: e.d, notes: e.notes, label: e.label})), r[1]]; }),
  scales: I.SCALES.map(a => M.scaleNotes(a[0], a[1], a[2])),
  names: [],
};
for (let m = 21; m < 109; m += 7) out.names.push(M.nameOf(m));
for (let m = 21; m < 109; m += 7) out.names.push(M.nameOf(m, true));
process.stdout.write(JSON.stringify(out));
"""


def main():
    inputs = {"NOTES": NOTES, "CHORDS": CHORDS, "KEYS": KEYS, "NUMERALS": NUMERALS, "SEQS": SEQS, "SCALES": SCALES}
    r = subprocess.run(["node", "-e", JS, str(PROJECT / "lib" / "music.js"), json.dumps(inputs)], capture_output=True,
                       text=True, encoding="utf-8")
    if r.returncode != 0:
        print("FAIL node: " + r.stderr.strip()[-500:])
        sys.exit(1)
    js = json.loads(r.stdout)
    py = json.loads(json.dumps(python_side()))
    bad = 0
    for k in py:
        for i, (a, b) in enumerate(zip(py[k], js[k])):
            if a != b:
                bad += 1
                print("FAIL %s[%d]: python %s  js %s" % (k, i, json.dumps(a, ensure_ascii=False), json.dumps(b, ensure_ascii=False)))
        if len(py[k]) != len(js[k]):
            bad += 1
            print("FAIL %s: lengths differ" % k)
    print("PARITY OK" if not bad else "%d DIFFERENCES" % bad)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
