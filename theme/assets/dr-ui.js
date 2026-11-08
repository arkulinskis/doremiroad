/* dr-ui.js: the small engine pieces the Python Forms call through client_code/dr.py (window.DR.UI, window.DR.Admin).
   Moved from the JavaScript version's GamePage/AdminPage scripts: the Practice Room's keyboard logic, the codex
   example keyboard, shop previews, and the level editor's checks, summaries, previews and "hear it".
   Everything here takes and returns plain data (JSON-able) or a DOM node; no page markup. */
(function () {
  'use strict';
  var DR = window.DR = window.DR || {};
  var esc = function (s) { return DR.esc(s); };
  var M = DR.Music;
  var UI = DR.UI = {};

  function mod(m) { return ((m % 12) + 12) % 12; }

  /* ---------- shop previews (HTML/SVG strings) ---------- */
  function miniKb(skin) {
    var s = '<div class="kb skin-' + esc(skin) + '" style="pointer-events:none">', whites = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16], ww = 100 / whites.length;
    whites.forEach(function (w, i) { s += '<div class="k w" style="left:' + i * ww + '%;width:' + ww + '%"></div>'; });
    [[1, 0], [3, 1], [6, 3], [8, 4], [10, 5], [13, 7], [15, 8]].forEach(function (b) { s += '<div class="k b" style="left:' + ((b[1] + 1) * ww - ww * 0.3) + '%;width:' + ww * 0.6 + '%"></div>'; });
    return s + '</div>';
  }
  function trailPv(key) {
    var f = DR.Engine.TRAILS[key] || DR.Engine.TRAILS.lantern;
    return '<div class="pv-trail">' + [60, 64, 67, 71, 62, 69].map(function (m, i) { var c = f(m); return '<i style="height:' + [40, 58, 30, 66, 48, 36][i] + 'px;background:linear-gradient(0deg,' + c[0] + ',' + c[1] + ')"></i>'; }).join('') + '</div>';
  }
  function bannerPv(b) {
    return '<svg viewBox="0 0 200 78" width="100%" height="100%" aria-hidden="true"><rect width="200" height="78" fill="#0f152a"/><line x1="70" y1="10" x2="70" y2="70" stroke="#e8d9b8" stroke-width="3"/><path d="M72,12 h70 l-14,16 l14,16 h-70z" fill="' + esc(b.color) + '" stroke="rgba(0,0,0,.4)"/></svg>';
  }
  UI.shopPreview = function (kind, item) {
    return kind === 'skins' ? miniKb(item.key) : kind === 'trails' ? trailPv(item.key) : bannerPv(item);
  };

  /* ---------- a keyboard that shows one codex example; returns {hear, destroy} ---------- */
  UI.codexKeyboard = function (el, ex, skin) {
    var items = ex.notes.map(function (n) { var ns = n.split('+').map(M.parseNote); return ns.length > 1 ? ns : ns[0]; });
    var flat = [];
    items.forEach(function (it) { flat = flat.concat(Array.isArray(it) ? it : [it]); });
    var kb = DR.Keyboard(el, { skin: skin, flats: ex.notes.join(' ').indexOf('b') > 0 });
    var r = DR.Engine.rangeFor(flat, window.innerWidth < 600 ? 1 : 2);
    kb.setRange(r[0], r[1]);
    var names = {};
    ex.notes.forEach(function (n) { n.split('+').forEach(function (x) { var mm = M.parseNote(x), nn = M.pretty(x, true); if (mm != null) names[mm] = names[mm] && names[mm] !== nn ? names[mm] + '/' + nn : nn; }); });
    kb.mark(flat, 'lesson', names);
    return {
      hear: function () { DR.Sound.play(items, { gap: 0.6, dur: 0.75 }); },
      destroy: function () { kb.destroy(); }
    };
  };

  /* ---------- the Practice Room: keyboard + chord naming + scales + metronome ----------
     UI.practice(el, ps, hooks) -> {set(key, value), hear(), metro() -> running?, oct(+1|-1), midi(), destroy()}
     ps = {show, key, chord, bpm, lo}; hooks (Python functions): chord(big, small), info(text, showMidiLink),
     range(text, canDown, canUp), saved(ps). Moved from renderPractice in the old GamePage. */
  var EXTRA_SCALES = { penta: [0, 2, 4, 7, 9], mpenta: [0, 3, 5, 7, 10], blues: [0, 3, 5, 6, 7, 10] };
  UI.practice = function (el, ps, hooks) {
    var kb = DR.Keyboard(el, { skin: ps.skin });
    var lo = ps.lo || null, oct = 3, metro = null;
    function save() { var copy = { show: ps.show, key: ps.key, chord: ps.chord, bpm: ps.bpm, lo: ps.lo }; DR.store.set('dr.practice', copy); }
    function fit() {
      var w = el.clientWidth || window.innerWidth;
      oct = DR.touchUI() ? Math.max(1, Math.min(4, Math.floor(w / (7 * 46)))) : window.innerWidth < 700 ? 2 : 3;
      if (lo == null) lo = oct >= 3 ? 48 : 60;
      lo = Math.max(24, Math.min(lo, 108 - oct * 12, 84));
      lo -= lo % 12;
      kb.setRange(lo, lo + oct * 12 - 1);
      if (DR.Input.base !== lo) DR.Input.setBase(lo);
      hooks.range(M.nameOf(lo) + '–' + M.nameOf(lo + oct * 12 - 1), lo > 24, lo < Math.min(108 - oct * 12, 84));
      mark(); info();
    }
    function info() {
      var mi = DR.Input.midi, b = DR.Input.base;
      var text = mi.status === 'on' ? '🎹 ' + mi.inputs[0]
        : DR.touchUI() ? '👆 Tap the keys · several fingers make a chord'
        : '⌨️ Z–M = ' + M.nameOf(b) + ' octave · Q–U = ' + M.nameOf(b + 12) + ' octave · ↑ ↓ shift';
      hooks.info(text, !(mi.status === 'on' || mi.status === 'unsupported'));
    }
    function heldNow() { return Object.keys(DR.Input.held).map(Number).sort(function (a, b) { return a - b; }); }
    DR.Input.capture(true);
    var off = DR.Input.on(function (t, m) {
      if (t === 'midi') { info(); return; }
      if (t === 'base') { if (m !== lo) { lo = m; ps.lo = lo; save(); } fit(); return; }
      if (t !== 'on' && t !== 'off') return;
      var show = heldNow();
      var ch = M.detectChord(show.length >= 2 ? show : []);
      if (show.length === 1) hooks.chord(M.nameOf(show[0]).replace(/-?\d+$/, ''), M.nameOf(show[0]));
      else if (show.length >= 2) hooks.chord(ch ? ch.symbol : '?', (ch ? ch.name + ' · ' : '') + show.map(function (x) { return M.nameOf(x); }).join(' '));
    });
    function mark() {
      ['target', 'hint', 'lesson'].forEach(function (c) { kb.unmark(c); });
      var r = kb.range(), all = [], root = [], names = {};
      if (ps.show === 'chord') {
        var c = M.chordOf(ps.chord);
        if (!c) return;
        var cp = M.pcs(c.notes);
        for (var m = r[0]; m <= r[1]; m++) if (cp.indexOf(mod(m)) >= 0) all.push(m);
        c.notes.forEach(function (n, j) { names[n] = c.spelled[j]; });
        kb.mark(all, 'hint'); kb.mark(c.notes, 'target', names);
        return;
      }
      if (ps.show === 'none') return;
      var pk = M.parseKey(ps.key), steps = EXTRA_SCALES[ps.show] || M.SCALES[ps.show];
      if (!pk || !steps) return;
      var pcs = steps.map(function (s) { return (pk[0] + s) % 12; });
      var spelled = EXTRA_SCALES[ps.show] ? null : M.scaleNotes(ps.key, ps.show, 4);
      for (var m2 = r[0]; m2 <= r[1]; m2++) {
        var i = pcs.indexOf(mod(m2));
        if (i < 0) continue;
        (i === 0 ? root : all).push(m2);
        names[m2] = spelled ? M.pretty(spelled[i], true) : M.pcName(mod(m2), M.keyUsesFlats(ps.key) || /b/.test(ps.key) || ps.show === 'blues');
      }
      kb.mark(all, 'lesson', names); kb.mark(root, 'target', names);
    }
    var lastW = el.clientWidth;
    function onResize() { if (el.clientWidth !== lastW) { lastW = el.clientWidth; fit(); } }
    window.addEventListener('resize', onResize);
    function stopMetro() { if (metro) { clearInterval(metro.timer); metro = null; } }
    function startMetro() {
      var c = DR.Sound.init(); if (!c) return;
      var next = c.currentTime + 0.1, n = 0;
      metro = { timer: setInterval(function () {
        while (next < c.currentTime + 0.2) { if (n % 4 === 0) DR.Sound.click(next); else DR.Sound.clickSoft(next); next += 60 / ps.bpm; n++; }
      }, 40) };
    }
    fit();
    return {
      set: function (k, v) { ps[k] = k === 'bpm' ? +v : v; save(); mark(); },
      hear: function () {
        if (ps.show === 'chord') { var c = M.chordOf(ps.chord); if (c) DR.Sound.play([c.notes], { gap: 1.2, dur: 1.4, roll: true }); }
        else if (ps.show !== 'none') {
          var pk = M.parseKey(ps.key), steps = (EXTRA_SCALES[ps.show] || M.SCALES[ps.show]).concat([12]);
          DR.Sound.play(steps.map(function (s) { return 60 + pk[0] + s; }), { gap: 0.32, dur: 0.4 });
        }
      },
      metro: function () { if (metro) stopMetro(); else startMetro(); return !!metro; },
      oct: function (d) { lo += 12 * d; DR.Input.releaseAll(); fit(); ps.lo = lo; save(); },
      midi: function () { return DR.Input.enableMidi(false).then(info); },
      destroy: function () { off(); stopMetro(); window.removeEventListener('resize', onResize); kb.destroy(); DR.Input.capture(false); }
    };
  };

  /* ---------- the level editor's helpers (moved from the old AdminPage) ---------- */
  var A = DR.Admin = {};
  var STEP_TYPES = A.STEP_TYPES = ['lesson', 'notes', 'chords', 'progression', 'rush', 'ear', 'quiz'];
  var BLANK = {
    lesson: function () { return { t: 'lesson', title: 'New lesson', text: '', show: [], staff: null }; },
    notes: function () { return { t: 'notes', prompt: 'Play these notes.', notes: ['C4', 'D4', 'E4'], labels: [], show: 'keys', clef: 'treble', exact: false }; },
    chords: function () { return { t: 'chords', prompt: 'Play these chords.', chords: ['C', 'F', 'G'], labels: [], hint: true, exact: false }; },
    progression: function () { return { t: 'progression', prompt: 'Play the progression.', key: 'C', numerals: ['I', 'IV', 'V', 'I'], hint: true, names: true }; },
    rush: function () { return { t: 'rush', prompt: 'Play in time.', seq: 'C4 D4 E4 F4 | G4:4', bpm: 90, hint: true, exact: false }; },
    ear: function () { return { t: 'ear', prompt: 'Play the note you hear.', mode: 'note', pool: ['C4', 'E4', 'G4'], count: 4 }; },
    quiz: function () { return { t: 'quiz', q: 'Question?', options: ['Right answer', 'Wrong answer'], answer: 0, explain: '' }; }
  };
  A.blank = function (t) { return JSON.stringify(BLANK[t]()); };

  /* The same rules as Levels.check on the server. Keep them in step. Returns JSON [errors, warnings, scored]. */
  function check(data) {
    var errors = [], warnings = [], steps = (data && data.steps) || [], scored = 0;
    if (!steps.length) errors.push('The level has no steps.');
    function isInt(v) { var n = parseInt(v, 10); return isNaN(n) ? null : n; }
    steps.forEach(function (s, i) {
      var where = 'Step ' + (i + 1), t = s && s.t;
      if (STEP_TYPES.indexOf(t) < 0) { errors.push(where + ': unknown kind of step.'); return; }
      scored += DR.Engine.stepItems(s);
      if (t === 'lesson') {
        if (!String(s.text || '').trim()) warnings.push(where + ': the lesson has no text.');
        (s.show || []).forEach(function (x) { if (M.parseNote(x) == null) errors.push(where + ": '" + x + "' isn't a note (write it like C4, F#3 or Bb4)."); });
      } else if (t === 'notes') {
        if (!(s.notes || []).length) errors.push(where + ': add at least one note.');
        (s.notes || []).forEach(function (x) { if (M.parseNote(x) == null) errors.push(where + ": '" + x + "' isn't a note (write it like C4, F#3 or Bb4)."); });
        if (s.show === 'staff') (s.notes || []).forEach(function (x) { var m = M.parseNote(x); if (m != null && !(m >= 36 && m <= 88)) warnings.push(where + ': ' + x + ' is far off the staff.'); });
      } else if (t === 'chords') {
        if (!(s.chords || []).length) errors.push(where + ': add at least one chord.');
        (s.chords || []).forEach(function (x) { if (!M.chordOf(x)) errors.push(where + ": '" + x + "' isn't a chord I know (try C, Am, G7, Bdim or C4+E4+G4)."); });
      } else if (t === 'progression') {
        if (!M.parseKey(s.key)) errors.push(where + ": '" + s.key + "' isn't a key (try C, G, Bb or Am).");
        else if (!(s.numerals || []).length) errors.push(where + ': add at least one numeral.');
        else (s.numerals || []).forEach(function (x) { if (!M.parseNumeral(x, s.key)) errors.push(where + ": '" + x + "' isn't a Roman numeral I know (try I, ii, V7, vii°)."); });
      } else if (t === 'rush') {
        var p = M.parseSeq(s.seq);
        if (!p) errors.push(where + ": the note sequence has a token I can't read.");
        else if (!p[0].length) errors.push(where + ': the note sequence is empty.');
        else if (p[1] > 400) warnings.push(where + ": that's a very long rush (" + Math.round(p[1]) + ' beats).');
        var bpm = isInt(s.bpm);
        if (!(bpm >= 30 && bpm <= 240)) errors.push(where + ': tempo must be between 30 and 240 BPM.');
      } else if (t === 'ear') {
        var pool = s.pool || [];
        if (['note', 'chord', 'interval'].indexOf(s.mode) < 0) errors.push(where + ': choose what the ear question plays.');
        else if (pool.length < (s.mode === 'note' ? 1 : 2)) errors.push(where + ': the answer pool needs ' + (s.mode === 'note' ? 'a note.' : 'at least 2 answers.'));
        else pool.forEach(function (x) {
          var ok = s.mode === 'note' ? M.parseNote(x) != null : s.mode === 'chord' ? Object.prototype.hasOwnProperty.call(M.EAR_CHORDS, x) : Object.prototype.hasOwnProperty.call(M.INTERVALS, x);
          if (!ok) errors.push(where + ": '" + x + "' can't be used in this ear question.");
        });
      } else if (t === 'quiz') {
        var opts = (s.options || []).filter(function (o) { return String(o).trim(); });
        if (!String(s.q || '').trim()) errors.push(where + ': the quiz has no question.');
        if (opts.length < 2) errors.push(where + ': the quiz needs at least 2 answers.');
        else { var a = isInt(s.answer); if (!(a >= 0 && a < opts.length)) errors.push(where + ': pick which answer is right.'); }
      }
    });
    return [errors, warnings, scored];
  }
  A.checkRaw = check;
  A.check = function (json) { return JSON.stringify(check(JSON.parse(json))); };

  A.summary = function (json) {
    var s = JSON.parse(json);
    switch (s.t) {
      case 'lesson': return s.title || '';
      case 'notes': return (s.notes || []).join(' ');
      case 'chords': return (s.chords || []).join(' ');
      case 'progression': return s.key + ': ' + (s.numerals || []).join(' ');
      case 'rush': var p = M.parseSeq(s.seq); return (p ? p[0].length + ' notes · ' : '') + s.bpm + ' BPM';
      case 'ear': return s.mode + ' × ' + s.count;
      case 'quiz': return s.q || '';
    }
    return '';
  };
  /* A plain-text preview under a step's fields (resolved chords, rush length ...). */
  A.preview = function (json) {
    var s = JSON.parse(json);
    try {
      if (s.t === 'progression') { var cs = (s.numerals || []).map(function (n) { var c = M.parseNumeral(n, s.key); return c ? c.symbol : '?'; }); return 'In ' + M.keyName(s.key) + ': ' + cs.join(' – '); }
      if (s.t === 'chords') return (s.chords || []).map(function (x) { var c = M.chordOf(x); return c ? c.symbol + ' = ' + c.spelled.join(' ') : x + '?'; }).join(' · ');
      if (s.t === 'rush') { var p = M.parseSeq(s.seq); if (!p) return ''; var secs = p[1] * 60 / (s.bpm || 90); return p[0].length + ' notes · ' + p[1] + ' beats · about ' + Math.round(secs) + ' s'; }
      if (s.t === 'notes') return (s.notes || []).map(function (x) { return M.parseNote(x) == null ? x + '?' : M.pretty(x); }).join(' ');
    } catch (e) {}
    return '';
  };
  A.hear = function (json) {
    var s = JSON.parse(json);
    if (s.t === 'lesson') DR.Sound.play((s.show || []).map(M.parseNote).filter(function (m) { return m != null; }), { gap: 0.45 });
    else if (s.t === 'notes') DR.Sound.play((s.notes || []).map(M.parseNote).filter(function (m) { return m != null; }), { gap: 0.45 });
    else if (s.t === 'chords') DR.Sound.play((s.chords || []).map(M.chordOf).filter(Boolean).map(function (c) { return c.notes; }), { gap: 0.9, dur: 0.85 });
    else if (s.t === 'progression') DR.Sound.play((s.numerals || []).map(function (n) { return M.parseNumeral(n, s.key); }).filter(Boolean).map(function (c) { return c.notes; }), { gap: 0.9, dur: 0.85 });
    else if (s.t === 'rush') {
      var p = M.parseSeq(s.seq); if (!p || !DR.Sound.init()) return;
      var spb = 60 / (s.bpm || 90);
      p[0].forEach(function (e) { setTimeout(function () { DR.Sound.play([e.notes], { gap: e.d * spb, dur: e.d * spb * 0.9 }); }, e.t * spb * 1000); });
    }
  };
  /* The answers an ear question can offer: [[value, label], ...] as JSON. */
  A.earChoices = function (mode) {
    if (mode === 'chord') return JSON.stringify(Object.keys(M.EAR_CHORDS).map(function (k) { return [k, k]; }));
    return JSON.stringify(Object.keys(M.INTERVALS).map(function (k) { return [k, M.INTERVALS[k][1]]; }));
  };
})();
