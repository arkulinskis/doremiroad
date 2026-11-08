/* Doremi Road — music theory for the browser (DR.Music).
   The same rules as server_code/Music.py: note names, chord symbols, Roman numerals, rush sequences.
   Keep the two in step; tools/testing/music_parity.py compares them. Also: chord detection and staff positions. */
(function (root) {
  'use strict';
  var DR = root.DR = root.DR || {};
  var LETTERS = 'CDEFGAB';
  var LETTER_PC = [0, 2, 4, 5, 7, 9, 11];
  var MAJOR = [0, 2, 4, 5, 7, 9, 11];
  var MINOR = [0, 2, 3, 5, 7, 8, 10];
  var ACC = { '': 0, '#': 1, '##': 2, 'x': 2, 'b': -1, 'bb': -2, '♯': 1, '♭': -1 };
  var CHORD_TYPES = {
    '': [[0, 0], [4, 2], [7, 4]],
    'm': [[0, 0], [3, 2], [7, 4]],
    'dim': [[0, 0], [3, 2], [6, 4]],
    'aug': [[0, 0], [4, 2], [8, 4]],
    'sus2': [[0, 0], [2, 1], [7, 4]],
    'sus4': [[0, 0], [5, 3], [7, 4]],
    '5': [[0, 0], [7, 4]],
    '6': [[0, 0], [4, 2], [7, 4], [9, 5]],
    'm6': [[0, 0], [3, 2], [7, 4], [9, 5]],
    '7': [[0, 0], [4, 2], [7, 4], [10, 6]],
    'maj7': [[0, 0], [4, 2], [7, 4], [11, 6]],
    'm7': [[0, 0], [3, 2], [7, 4], [10, 6]],
    'm7b5': [[0, 0], [3, 2], [6, 4], [10, 6]],
    'dim7': [[0, 0], [3, 2], [6, 4], [9, 6]],
    'add9': [[0, 0], [4, 2], [7, 4], [14, 1]],
    '9': [[0, 0], [4, 2], [7, 4], [10, 6], [14, 1]]
  };
  var CHORD_ALIASES = { 'maj': '', 'M': '', 'min': 'm', '-': 'm', '°': 'dim', 'o': 'dim', '+': 'aug', 'ø': 'm7b5', 'ø7': 'm7b5',
    '°7': 'dim7', 'o7': 'dim7', 'M7': 'maj7', 'Δ': 'maj7', 'Δ7': 'maj7', 'min7': 'm7', '-7': 'm7', 'dom7': '7', 'sus': 'sus4' };
  var CHORD_NAMES = { '': 'major', 'm': 'minor', 'dim': 'diminished', 'aug': 'augmented', 'sus2': 'sus2', 'sus4': 'sus4', '5': 'power chord',
    '6': 'major sixth', 'm6': 'minor sixth', '7': 'dominant seventh', 'maj7': 'major seventh', 'm7': 'minor seventh',
    'm7b5': 'half-diminished', 'dim7': 'diminished seventh', 'add9': 'add nine', '9': 'dominant ninth' };
  var EAR_CHORDS = { 'major': '', 'minor': 'm', 'diminished': 'dim', 'augmented': 'aug', 'dominant 7th': '7', 'major 7th': 'maj7', 'minor 7th': 'm7' };
  var INTERVALS = { m2: [1, 'minor 2nd'], M2: [2, 'major 2nd'], m3: [3, 'minor 3rd'], M3: [4, 'major 3rd'], P4: [5, 'perfect 4th'],
    TT: [6, 'tritone'], P5: [7, 'perfect 5th'], m6: [8, 'minor 6th'], M6: [9, 'major 6th'], m7: [10, 'minor 7th'], M7: [11, 'major 7th'], P8: [12, 'octave'] };
  var NOTE_RE = /^([A-Ga-g])(##|#|x|bb|b|♯|♭)?(-?\d)$/;
  var CHORD_RE = /^([A-G])(#|b|♯|♭)?([^/]*)(?:\/([A-G])(#|b|♯|♭)?)?$/;
  var KEY_RE = /^([A-G])(#|b|♯|♭)?(m|min|minor)?$/;
  var NUMERAL_RE = /^(b|#|♭|♯)?(VII|VI|V|IV|III|II|I|vii|vi|v|iv|iii|ii|i)(°|o|\+|ø)?(maj7|M7|7)?$/;
  var ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII'];

  function mod(a, n) { return ((a % n) + n) % n; }
  function accText(a) { return { 0: '', 1: '♯', 2: '𝄪', '-1': '♭', '-2': '𝄫' }[a] || ''; }
  function spell(letter, pc) {
    var a = mod(pc - LETTER_PC[letter], 12);
    if (a > 6) a -= 12;
    return LETTERS[letter] + accText(a);
  }
  function parseNote(s) {
    var m = NOTE_RE.exec(String(s == null ? '' : s).trim());
    if (!m) return null;
    var letter = LETTERS.indexOf(m[1].toUpperCase());
    var midi = (parseInt(m[3], 10) + 1) * 12 + LETTER_PC[letter] + ACC[m[2] || ''];
    return midi >= 21 && midi <= 108 ? midi : null;
  }
  function noteLetter(s) {
    var m = NOTE_RE.exec(String(s == null ? '' : s).trim());
    return m ? LETTERS.indexOf(m[1].toUpperCase()) : null;
  }
  var SHARPS = ['C', 'C♯', 'D', 'D♯', 'E', 'F', 'F♯', 'G', 'G♯', 'A', 'A♯', 'B'];
  var FLATS = ['C', 'D♭', 'D', 'E♭', 'E', 'F', 'G♭', 'G', 'A♭', 'A', 'B♭', 'B'];
  function nameOf(midi, flats) { return (flats ? FLATS : SHARPS)[mod(midi, 12)] + (Math.floor(midi / 12) - 1); }
  function pcName(pc, flats) { return (flats ? FLATS : SHARPS)[mod(pc, 12)]; }
  // 'F#4' → 'F♯4' (pretty, keeps the written spelling); without the octave if noOct.
  function pretty(s, noOct) {
    var m = NOTE_RE.exec(String(s || '').trim());
    if (!m) return String(s || '');
    var a = { '': '', '#': '♯', '##': '𝄪', 'x': '𝄪', 'b': '♭', 'bb': '𝄫', '♯': '♯', '♭': '♭' }[m[2] || ''];
    return m[1].toUpperCase() + a + (noOct ? '' : m[3]);
  }

  function parseChord(sym, octave) {
    var s = String(sym == null ? '' : sym).trim();
    var m = CHORD_RE.exec(s);
    if (!m) return null;
    var letter = LETTERS.indexOf(m[1]);
    var pc = mod(LETTER_PC[letter] + ACC[m[2] || ''], 12);
    var q = m[3] || '';
    if (Object.prototype.hasOwnProperty.call(CHORD_ALIASES, q)) q = CHORD_ALIASES[q];
    if (!Object.prototype.hasOwnProperty.call(CHORD_TYPES, q)) return null;
    if (octave == null) octave = pc <= 5 ? 4 : 3;
    var root = (octave + 1) * 12 + pc;
    var type = CHORD_TYPES[q];
    var notes = type.map(function (x) { return root + x[0]; });
    var spelled = type.map(function (x) { return spell((letter + x[1]) % 7, mod(pc + x[0], 12)); });
    if (m[4]) {
      var bl = LETTERS.indexOf(m[4]);
      var bpc = mod(LETTER_PC[bl] + ACC[m[5] || ''], 12);
      var bass = notes[0] - (mod(notes[0] - bpc, 12) || 12);
      var keep = notes.map(function (n, i) { return [n, spelled[i]]; }).filter(function (x) { return mod(x[0], 12) !== bpc; });
      notes = [bass].concat(keep.map(function (x) { return x[0]; }));
      spelled = [spell(bl, bpc)].concat(keep.map(function (x) { return x[1]; }));
    }
    var rootName = spell(letter, pc);
    return { root: pc, type: q, symbol: rootName + q + (m[4] ? '/' + spelled[0] : ''), name: rootName + ' ' + CHORD_NAMES[q],
      notes: notes, spelled: spelled };
  }
  function parseKey(k) {
    var m = KEY_RE.exec(String(k == null ? '' : k).trim());
    if (!m) return null;
    var letter = LETTERS.indexOf(m[1]);
    return [mod(LETTER_PC[letter] + ACC[m[2] || ''], 12), letter, m[3] ? 'minor' : 'major'];
  }
  function keyName(k) {
    var pk = parseKey(k);
    if (!pk) return String(k);
    return spell(pk[1], pk[0]) + (pk[2] === 'minor' ? ' minor' : ' major');
  }
  function keyUsesFlats(k) {
    var pk = parseKey(k);
    if (!pk) return false;
    var s = spell(pk[1], pk[0]);
    return s.indexOf('♭') >= 0 || (pk[2] === 'major' && s === 'F') || (pk[2] === 'minor' && ['D', 'G', 'C', 'F'].indexOf(s) >= 0);
  }
  function parseNumeral(num, key) {
    var pk = parseKey(key);
    var m = NUMERAL_RE.exec(String(num == null ? '' : num).trim());
    if (!pk || !m) return null;
    var roman = m[2], degree = ROMAN.indexOf(roman.toUpperCase());
    var scale = pk[2] === 'minor' ? MINOR : MAJOR;
    var acc = ACC[m[1] || ''] || 0;
    var pc = mod(pk[0] + scale[degree] + acc, 12);
    var letter = (pk[1] + degree) % 7;
    var mark = m[3] || '', seventh = m[4] || '';
    var upper = roman === roman.toUpperCase(), q;
    if (mark === 'ø') q = 'm7b5';
    else if (mark === '°' || mark === 'o') q = seventh ? 'dim7' : 'dim';
    else if (mark === '+') q = 'aug';
    else if (upper) q = { '': '', '7': '7', 'maj7': 'maj7', 'M7': 'maj7' }[seventh];
    else q = seventh ? 'm7' : 'm';
    var c = parseChord((spell(letter, pc) + q).replace(/♯/g, '#').replace(/♭/g, 'b'));
    if (!c) return null;
    c.numeral = String(num).trim();
    return c;
  }
  function asciiName(letter, midi) {
    var a = mod(mod(midi, 12) - LETTER_PC[letter], 12);
    if (a > 6) a -= 12;
    var natural = midi - a;
    return LETTERS[letter] + { 0: '', 1: '#', 2: '##', '-1': 'b', '-2': 'bb' }[a] + (Math.floor(natural / 12) - 1);
  }
  var SCALES = { major: MAJOR, minor: MINOR, harmonic: [0, 2, 3, 5, 7, 8, 11], dorian: [0, 2, 3, 5, 7, 9, 10], mixolydian: [0, 2, 4, 5, 7, 9, 10] };
  function scaleNotes(key, kind, octave) {
    var pk = parseKey(key);
    if (!pk) return [];
    octave = octave == null ? 4 : octave;
    var base = (octave + 1) * 12 + pk[0];
    return SCALES[kind || 'major'].concat([12]).map(function (semi, i) { return asciiName((pk[1] + i) % 7, base + semi); });
  }
  function parseSeq(text) {
    var events = [], t = 0, toks = String(text == null ? '' : text).split(/\s+/).filter(Boolean);
    for (var i = 0; i < toks.length; i++) {
      var tok = toks[i];
      if (tok === '|') continue;
      var cut = tok.indexOf(':'), body = cut >= 0 ? tok.slice(0, cut) : tok, beats = cut >= 0 ? tok.slice(cut + 1) : '';
      var d = beats ? Number(beats) : 1;
      if (beats && !/^\d*\.?\d+$/.test(beats)) return null;
      if (!(d > 0 && d <= 16)) return null;
      if (body === 'r' || body === '_' || body === '-') { t += d; continue; }
      if (body.charAt(0) === '{' && body.charAt(body.length - 1) === '}') {
        var c = parseChord(body.slice(1, -1));
        if (!c) return null;
        events.push({ t: t, d: d, notes: c.notes, label: c.symbol });
      } else {
        var ns = body.split('+').map(parseNote);
        if (!ns.length || ns.some(function (n) { return n == null; })) return null;
        ns = ns.filter(function (n, j) { return ns.indexOf(n) === j; }).sort(function (a, b) { return a - b; });
        events.push({ t: t, d: d, notes: ns, label: null, names: body.split('+') });
      }
      t += d;
    }
    return [events, t];
  }
  function chordOf(item) {
    var s = String(item == null ? '' : item).trim();
    if (s.indexOf('+') >= 0 && parseNote(s.split('+')[0]) != null) {
      var ns = s.split('+').map(parseNote);
      if (ns.some(function (n) { return n == null; })) return null;
      return { root: mod(ns[0], 12), type: '?', symbol: s, name: s.split('+').map(function (x) { return pretty(x, true); }).join(' '),
        notes: ns.slice().sort(function (a, b) { return a - b; }), spelled: s.split('+').map(function (x) { return pretty(x, true); }) };
    }
    return parseChord(s);
  }

  /* ---------- browser-only helpers ---------- */
  function pcs(midis) {
    var out = [];
    midis.forEach(function (m) { var p = mod(m, 12); if (out.indexOf(p) < 0) out.push(p); });
    return out.sort(function (a, b) { return a - b; });
  }
  function sameSet(a, b) { return a.length === b.length && a.every(function (x, i) { return x === b[i]; }); }
  // What chord do these keys make? → {symbol, name, inversion} or null. Prefers the lowest note as the root.
  var DETECT = ['', 'm', '7', 'maj7', 'm7', 'dim', 'aug', 'sus4', 'sus2', 'm7b5', 'dim7', '6', 'm6', '5'];
  function detectChord(midis) {
    if (!midis || midis.length < 2) return null;
    var sorted = midis.slice().sort(function (a, b) { return a - b; });
    var set = pcs(sorted), bass = mod(sorted[0], 12);
    var roots = [bass].concat(set.filter(function (p) { return p !== bass; }));
    for (var r = 0; r < roots.length; r++) {
      for (var i = 0; i < DETECT.length; i++) {
        var q = DETECT[i];
        var want = pcs(CHORD_TYPES[q].map(function (x) { return roots[r] + x[0]; }));
        if (sameSet(want, set)) {
          var name = pcName(roots[r], false);
          var sym = name + q + (roots[r] !== bass ? '/' + pcName(bass, false) : '');
          return { symbol: sym, name: name + ' ' + CHORD_NAMES[q], root: roots[r], type: q, inversion: roots[r] !== bass };
        }
      }
    }
    if (set.length === 2) {
      var semi = mod(set[1] - set[0], 12);
      var iv = Object.keys(INTERVALS).filter(function (k) { return INTERVALS[k][0] === semi; })[0];
      if (iv) return { symbol: INTERVALS[iv][1], name: INTERVALS[iv][1], interval: true };
    }
    return null;
  }
  // Staff position of a written note: diatonic steps above the bottom line (treble E4, bass G2). Also its accidental.
  function staffPos(note, clef) {
    var m = NOTE_RE.exec(String(note || '').trim());
    if (!m) return null;
    var letter = LETTERS.indexOf(m[1].toUpperCase()), oct = parseInt(m[3], 10);
    var dia = oct * 7 + letter;
    var bottom = clef === 'bass' ? 2 * 7 + 4 : 4 * 7 + 2;
    var acc = m[2] || '';
    return { pos: dia - bottom, acc: acc === '#' || acc === '♯' ? '♯' : acc === 'b' || acc === '♭' ? '♭' : acc === '##' || acc === 'x' ? '𝄪' : acc === 'bb' ? '𝄫' : '' };
  }

  DR.Music = {
    LETTERS: LETTERS, CHORD_TYPES: CHORD_TYPES, CHORD_NAMES: CHORD_NAMES, EAR_CHORDS: EAR_CHORDS, INTERVALS: INTERVALS, SCALES: SCALES,
    spell: spell, parseNote: parseNote, noteLetter: noteLetter, nameOf: nameOf, pcName: pcName, pretty: pretty,
    parseChord: parseChord, parseKey: parseKey, keyName: keyName, keyUsesFlats: keyUsesFlats, parseNumeral: parseNumeral,
    asciiName: asciiName, scaleNotes: scaleNotes, parseSeq: parseSeq, chordOf: chordOf,
    pcs: pcs, sameSet: sameSet, detectChord: detectChord, staffPos: staffPos, mod: mod,
    isBlack: function (m) { return [1, 3, 6, 8, 10].indexOf(mod(m, 12)) >= 0; }
  };
})(typeof window !== 'undefined' ? window : globalThis);
