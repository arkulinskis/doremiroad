/* dr-core.js: Doremi Road's browser core (moved unchanged from the JavaScript version's native_libraries.html):
   window.DR helpers (esc, store, settings, touch mode, toast, modal), the synthesized piano + sounds (DR.Sound) and
   input from MIDI / computer keys / on-screen keys (DR.Input). The pages are Python Forms (client_code). */
(function () {
  'use strict';
  var DR = window.DR = window.DR || {};
  DR.components = DR.components || {};

  /* ---------- Python ⇄ JS bridge ----------
     Python mounts a component with window.DR.mount(name, rootNode, jsonString, emit).
     The component calls emit(event, payload) and gets a Promise of whatever Python returned
     (dr_ui sends it back as a JSON string; we parse it here). */
  DR.wrapEmit = function (emit) {
    return function (name, payload) {
      var r;
      try { r = emit ? emit(name, JSON.stringify(payload == null ? {} : payload)) : null; }
      catch (e) { console.error(e); return Promise.reject(e); }
      return Promise.resolve(r).then(function (v) {
        if (typeof v === 'string') { try { return JSON.parse(v); } catch (e) { return v; } }
        return v;
      });
    };
  };
  DR.define = function (name, mountFn) { DR.components[name] = mountFn; };
  DR.mount = function (name, root, json, emit) {
    var fn = DR.components[name];
    if (!fn) { console.error('DR component not loaded: ' + name); return null; }
    if (!root) { console.error('DR mount: no root node for ' + name); return null; }
    var data = typeof json === 'string' ? JSON.parse(json || '{}') : (json || {});
    return fn(root, data, DR.wrapEmit(emit));
  };

  /* ---------- small helpers ---------- */
  DR.esc = function (s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  };
  DR.store = {
    get: function (k, dflt) { try { var v = localStorage.getItem(k); return v == null ? dflt : JSON.parse(v); } catch (e) { return dflt; } },
    set: function (k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} },
    del: function (k) { try { localStorage.removeItem(k); } catch (e) {} }
  };
  DR.today = function () {
    var d = new Date();
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  };
  DR.isTouch = function () { return ('ontouchstart' in window) || navigator.maxTouchPoints > 0; };
  DR.fmt = function (n) { return Math.round(n).toLocaleString('en-US'); };

  /* Player settings, kept in this browser. */
  var SETTINGS_DEFAULT = { sfx: true, ambient: true, keySound: true, midiSound: false, labels: 'c', letters: true, volume: 0.8, metronome: true, touch: 'auto' };
  DR.settings = Object.assign({}, SETTINGS_DEFAULT, DR.store.get('dr.settings', {}));
  DR.saveSettings = function () { DR.store.set('dr.settings', DR.settings); };

  /* Touch-screen piano: bigger keys, tap hints instead of computer-key hints, octave buttons.
     settings.touch: 'auto' (when the main pointer is a finger: tablets, phones), 'on' or 'off'. <html> gets .dr-touch. */
  var coarse = null;
  try { coarse = window.matchMedia('(pointer: coarse)'); } catch (e) {}
  DR.touchUI = function () {
    var t = DR.settings.touch;
    if (t === 'on') return true;
    if (t === 'off') return false;
    return coarse ? coarse.matches : DR.isTouch();
  };
  DR.applyTouch = function () {
    document.documentElement.classList.toggle('dr-touch', DR.touchUI());
    if (DR.Input) DR.Input.setBase(DR.Input.base);   // tells keyboards and hint lines to redraw
  };
  DR.applyTouch();
  // an iPad that gets a trackpad (or loses it) switches by itself
  if (coarse) { try { coarse.addEventListener('change', DR.applyTouch); } catch (e) {} }

  DR.toast = function (msg, kind) {
    var box = document.querySelector('.dr-toasts');
    if (!box) { box = document.createElement('div'); box.className = 'dr dr-toasts'; document.body.appendChild(box); }
    var t = document.createElement('div');
    t.className = 'dr-toast' + (kind === true || kind === 'err' ? ' err' : kind === 'gold' ? ' gold' : '');
    t.innerHTML = msg;
    box.appendChild(t);
    setTimeout(function () { t.style.transition = 'opacity .3s, transform .3s'; t.style.opacity = '0'; t.style.transform = 'translateY(-8px)'; }, 2800);
    setTimeout(function () { t.remove(); }, 3200);
  };

  // DR.modal(html, {onClose, cls, noClose}) → {el, close}. Clicking the backdrop or × closes it.
  DR.modal = function (html, opts) {
    opts = opts || {};
    var bg = document.createElement('div');
    bg.className = 'dr dr-modal-bg';
    bg.innerHTML = '<div class="dr-card dr-modal ' + (opts.cls || '') + '" role="dialog">' + (opts.noClose ? '' : '<button class="dr-x" aria-label="Close">✕</button>') + html + '</div>';
    document.body.appendChild(bg);
    var closed = false;
    function close() {
      if (closed) return; closed = true;
      bg.remove();
      document.removeEventListener('keydown', onKey, true);
      if (opts.onClose) opts.onClose();
    }
    function onKey(e) { if (e.key === 'Escape' && !opts.noClose) { e.stopPropagation(); close(); } }
    document.addEventListener('keydown', onKey, true);
    bg.addEventListener('click', function (e) {
      if ((e.target === bg && !opts.noClose) || (e.target.closest && e.target.closest('.dr-x'))) { DR.Sound.sfx('click'); close(); }
    });
    return { el: bg.querySelector('.dr-modal'), close: close, bg: bg };
  };

  /* ---------- Sound: a synthesized piano, effects, a metronome and soft ambience (no audio files) ---------- */
  var Sound = DR.Sound = { ctx: null, voices: {}, order: [] };
  Sound.init = function () {
    if (Sound.ctx) { if (Sound.ctx.state === 'suspended') Sound.ctx.resume(); return Sound.ctx; }
    var AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return null;
    // iPhone/iPad: play even when the silent switch is on (Safari 17+), like a music app
    try { if (navigator.audioSession) navigator.audioSession.type = 'playback'; } catch (e) {}
    try {
      var c = Sound.ctx = new AC({ latencyHint: 'interactive' });
      Sound.master = c.createGain(); Sound.master.gain.value = DR.settings.volume;
      var comp = c.createDynamicsCompressor(); comp.threshold.value = -14; comp.ratio.value = 3;
      Sound.master.connect(comp); comp.connect(c.destination);
      // a small synthetic room
      var len = Math.floor(c.sampleRate * 1.8), imp = c.createBuffer(2, len, c.sampleRate);
      for (var ch = 0; ch < 2; ch++) { var d = imp.getChannelData(ch); for (var i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 3.2); }
      Sound.verb = c.createConvolver(); Sound.verb.buffer = imp;
      var wet = c.createGain(); wet.gain.value = 0.22; Sound.verb.connect(wet); wet.connect(Sound.master);
      Sound.piano = c.createGain(); Sound.piano.gain.value = 0.9; Sound.piano.connect(Sound.master); Sound.piano.connect(Sound.verb);
      Sound.fx = c.createGain(); Sound.fx.gain.value = 0.55; Sound.fx.connect(Sound.master);
      Sound.amb = c.createGain(); Sound.amb.gain.value = 0.32; Sound.amb.connect(Sound.master); Sound.amb.connect(Sound.verb);
    } catch (e) { Sound.ctx = null; }
    return Sound.ctx;
  };
  // (older iOS only unlocks audio on touchend)
  ['pointerdown', 'keydown', 'touchstart', 'touchend'].forEach(function (ev) {
    window.addEventListener(ev, function () { Sound.init(); if (Sound.wantAmbient) Sound.ambient(Sound.wantAmbient); }, { passive: true });
  });
  Sound.setVolume = function (v) {
    DR.settings.volume = v; DR.saveSettings(); if (Sound.master) Sound.master.gain.value = v;
    if (window.ArkMusic) ArkMusic.volume(0.32 * v);
  };
  function freq(m) { return 440 * Math.pow(2, (m - 69) / 12); }

  // One piano-ish voice: a few partials with a falling filter, a hammer tick and a pitch-dependent decay.
  function voice(midi, vel, when, dest) {
    var c = Sound.ctx, f = freq(midi), t = when || c.currentTime;
    var g = c.createGain(), filt = c.createBiquadFilter();
    var v = 0.18 + 0.32 * (vel == null ? 0.75 : vel);
    var decay = Math.max(0.35, Math.min(2.6, 1.5 * Math.pow(2, -(midi - 60) / 22)));
    filt.type = 'lowpass'; filt.Q.value = 0.7;
    filt.frequency.setValueAtTime(Math.min(12000, f * 9), t);
    filt.frequency.setTargetAtTime(Math.min(6000, f * 2.6), t + 0.01, decay * 0.35);
    g.gain.setValueAtTime(0.0001, t);
    g.gain.linearRampToValueAtTime(v, t + 0.006);
    g.gain.setTargetAtTime(v * 0.42, t + 0.008, 0.09);
    g.gain.setTargetAtTime(0.0001, t + 0.12, decay);
    filt.connect(g); g.connect(dest || Sound.piano);
    var parts = [[1, 'triangle', 1], [1.0015, 'sawtooth', 0.12], [2, 'sine', 0.32], [3, 'sine', 0.1], [4.02, 'sine', 0.04]];
    var oscs = parts.map(function (p) {
      var o = c.createOscillator(), og = c.createGain();
      o.type = p[1]; o.frequency.value = f * p[0]; og.gain.value = p[2];
      o.connect(og); og.connect(filt); o.start(t); return o;
    });
    // hammer
    var n = Math.floor(c.sampleRate * 0.03), buf = c.createBuffer(1, n, c.sampleRate), d = buf.getChannelData(0);
    for (var i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / n);
    var src = c.createBufferSource(), bp = c.createBiquadFilter(), hg = c.createGain();
    src.buffer = buf; bp.type = 'bandpass'; bp.frequency.value = Math.min(8000, f * 5); hg.gain.value = v * 0.35;
    src.connect(bp); bp.connect(hg); hg.connect(dest || Sound.piano); src.start(t);
    var stopAt = t + decay * 5 + 0.3;
    oscs.forEach(function (o) { o.stop(stopAt); });
    return { g: g, oscs: oscs, release: function (at) {
      var tt = Math.max(at || c.currentTime, t + 0.02);
      g.gain.cancelScheduledValues(tt); g.gain.setTargetAtTime(0.0001, tt, 0.07);
      oscs.forEach(function (o) { try { o.stop(tt + 0.6); } catch (e) {} });
    } };
  }
  Sound.noteOn = function (midi, vel) {
    if (!Sound.init()) return;
    if (Sound.voices[midi]) Sound.voices[midi].release();
    Sound.voices[midi] = voice(midi, vel);
    Sound.order.push(midi);
    if (Sound.order.length > 28) { var old = Sound.order.shift(); if (Sound.voices[old] && old !== midi) { Sound.voices[old].release(); delete Sound.voices[old]; } }
  };
  Sound.noteOff = function (midi) {
    var v = Sound.voices[midi];
    if (v) { v.release(); delete Sound.voices[midi]; }
  };
  // Play notes for listening: items are MIDI numbers or arrays (chords). Returns the duration in seconds.
  Sound.play = function (items, opts) {
    if (!Sound.init()) return 0;
    opts = opts || {};
    var gap = opts.gap || 0.55, dur = opts.dur || gap * 0.95, t = Sound.ctx.currentTime + 0.05;
    items.forEach(function (it, i) {
      var group = Array.isArray(it) ? it : [it];
      group.forEach(function (m, j) {
        var at = t + i * gap + (opts.roll ? j * 0.03 : 0);
        var vv = voice(m, opts.vel || 0.7, at);
        vv.release(at + dur);
      });
    });
    return items.length * gap;
  };

  function tone(f, start, dur, type, vol, slideTo, dest) {
    var c = Sound.ctx, o = c.createOscillator(), g = c.createGain();
    o.type = type || 'sine';
    o.frequency.setValueAtTime(f, start);
    if (slideTo) o.frequency.exponentialRampToValueAtTime(slideTo, start + dur);
    g.gain.setValueAtTime(0.0001, start);
    g.gain.exponentialRampToValueAtTime(vol || 0.2, start + 0.008);
    g.gain.exponentialRampToValueAtTime(0.0001, start + dur);
    o.connect(g); g.connect(dest || Sound.fx);
    o.start(start); o.stop(start + dur + 0.05);
  }
  function noise(start, dur, vol, filterFreq, type) {
    var c = Sound.ctx, n = Math.floor(c.sampleRate * dur), buf = c.createBuffer(1, n, c.sampleRate), d = buf.getChannelData(0);
    for (var i = 0; i < n; i++) d[i] = Math.random() * 2 - 1;
    var src = c.createBufferSource(), f = c.createBiquadFilter(), g = c.createGain();
    src.buffer = buf; f.type = type || 'lowpass'; f.frequency.value = filterFreq || 1200;
    g.gain.setValueAtTime(vol || 0.2, start); g.gain.exponentialRampToValueAtTime(0.0001, start + dur);
    src.connect(f); f.connect(g); g.connect(Sound.fx); src.start(start);
  }
  function bell(fs, t, gap, vol) { fs.forEach(function (f, i) { tone(f, t + i * gap, 0.5, 'sine', vol || 0.12); tone(f * 2, t + i * gap, 0.25, 'sine', (vol || 0.12) * 0.3); }); }
  var SFX = {
    click: function (t) { tone(1200, t, 0.03, 'sine', 0.06); },
    hover: function (t) { tone(1800, t, 0.02, 'sine', 0.02); },
    good: function (t) { tone(1320, t, 0.08, 'sine', 0.06); tone(1760, t + 0.05, 0.12, 'sine', 0.05); },
    perfect: function (t) { tone(1568, t, 0.1, 'sine', 0.06); tone(2093, t + 0.04, 0.16, 'sine', 0.05); },
    wrong: function (t) { tone(180, t, 0.16, 'square', 0.05, 120); },
    miss: function (t) { noise(t, 0.08, 0.06, 500); },
    step: function (t) { bell([659, 988], t, 0.09, 0.08); },
    star: function (t) { bell([1047, 1568], t, 0.07, 0.1); },
    coin: function (t) { tone(1976, t, 0.05, 'square', 0.03); tone(2637, t + 0.05, 0.12, 'square', 0.03); },
    unlock: function (t) { bell([523, 659, 784, 1047], t, 0.08, 0.1); },
    card: function (t) { noise(t, 0.25, 0.05, 4000, 'highpass'); bell([784, 988, 1175, 1568], t + 0.15, 0.07, 0.09); },
    win: function (t) { bell([523, 659, 784, 1047, 1319], t, 0.1, 0.11); },
    fail: function (t) { [392, 349, 311, 262].forEach(function (f, i) { tone(f, t + i * 0.15, 0.22, 'triangle', 0.08); }); },
    conquer: function (t) { [262, 330, 392, 523].forEach(function (f, i) { tone(f, t + i * 0.12, 0.6, 'sawtooth', 0.035); tone(f * 2, t + i * 0.12, 0.6, 'triangle', 0.05); }); bell([1047, 1319, 1568, 2093], t + 0.55, 0.09, 0.1); },
    tick: function (t) { tone(1600, t, 0.03, 'square', 0.035); },
    tock: function (t) { tone(1000, t, 0.03, 'square', 0.025); },
    page: function (t) { noise(t, 0.18, 0.05, 2500, 'bandpass'); }
  };
  Sound.sfx = function (name, at) {
    if (!DR.settings.sfx || !Sound.init() || !SFX[name]) return;
    try { SFX[name](at || Sound.ctx.currentTime + 0.005); } catch (e) {}
  };
  Sound.click = function (at) { if (Sound.init()) try { SFX.tick(at); } catch (e) {} };
  Sound.clickSoft = function (at) { if (Sound.init()) try { SFX.tock(at); } catch (e) {} };

  /* Ambience: slow, quiet piano arpeggios over a four-chord loop, for the map and menus. */
  var AMB = [[48, 55, 64, 67, 72], [45, 52, 60, 64, 69], [41, 48, 57, 60, 65], [43, 50, 59, 62, 67]];
  /* Map music: two soft Audiio tracks (both in G minor) streamed by ArkMusic (the ark-music block above);
     the generated chords below are the fallback when the files can't load. */
  Sound.useFiles = !!window.ArkMusic;
  if (window.ArkMusic) ArkMusic.onfail(function () { Sound.useFiles = false; if (Sound.wantAmbient) Sound.ambient(true); });
  Sound.ambient = function (on) {
    Sound.wantAmbient = on ? true : null;
    if (Sound.useFiles) {
      if (on && DR.settings.ambient) ArkMusic.play(['toulouse', 'bright-road'], { volume: 0.32 * (DR.settings.volume == null ? 1 : DR.settings.volume), fade: 2 });
      else ArkMusic.stop(1.2);
      return;
    }
    if (!on || !DR.settings.ambient) { if (Sound.ambTimer) { clearInterval(Sound.ambTimer); Sound.ambTimer = null; } return; }
    if (Sound.ambTimer || !Sound.ctx || Sound.ctx.state !== 'running') return;
    var c = Sound.ctx, next = c.currentTime + 0.2, step = 0;
    Sound.ambTimer = setInterval(function () {
      while (next < c.currentTime + 0.6) {
        var ch = AMB[Math.floor(step / 8) % 4], k = step % 8;
        var m = k === 0 ? ch[0] : ch[1 + Math.floor(Math.random() * 4)] + (Math.random() < 0.25 ? 12 : 0);
        if (k === 0 || Math.random() < 0.7) { var vv = voice(m, k === 0 ? 0.5 : 0.25 + Math.random() * 0.2, next, Sound.amb); vv.release(next + 1.6); }
        next += 0.62; step++;
      }
    }, 150);
  };

  /* ---------- Input: MIDI keyboards, the computer keyboard and on-screen keys, as one stream ----------
     DR.Input.on(fn) → off(). fn('on'|'off', midi, velocity, source). Sources: 'midi', 'keys', 'mouse'.
     The computer keyboard only plays while something has called DR.Input.capture(true). */
  var Input = DR.Input = { subs: [], held: {}, base: 48, captured: 0, last: null,
    midi: { status: navigator.requestMIDIAccess ? 'off' : 'unsupported', inputs: [], access: null } };
  // KeyboardEvent.code → semitones above the base C. Z-row = one octave, Q-row = the next (like most DAWs).
  Input.KEYMAP = {
    KeyZ: 0, KeyS: 1, KeyX: 2, KeyD: 3, KeyC: 4, KeyV: 5, KeyG: 6, KeyB: 7, KeyH: 8, KeyN: 9, KeyJ: 10, KeyM: 11,
    Comma: 12, KeyL: 13, Period: 14, Semicolon: 15, Slash: 16,
    KeyQ: 12, Digit2: 13, KeyW: 14, Digit3: 15, KeyE: 16, KeyR: 17, Digit5: 18, KeyT: 19, Digit6: 20, KeyY: 21, Digit7: 22, KeyU: 23,
    KeyI: 24, Digit9: 25, KeyO: 26, Digit0: 27, KeyP: 28, BracketLeft: 29, Equal: 30, BracketRight: 31
  };
  // The letter shown on each on-screen key: the Z-row for the first octave, the Q-row above it.
  Input.LABELS = (function () {
    var out = {}, names = { BracketLeft: '[', BracketRight: ']', Equal: '=' }, zTail = ['Comma', 'KeyL', 'Period', 'Semicolon', 'Slash'];
    Object.keys(Input.KEYMAP).forEach(function (code) {
      if (zTail.indexOf(code) < 0) out[Input.KEYMAP[code]] = names[code] || code.replace('Key', '').replace('Digit', '');
    });
    return out;
  })();
  Input.on = function (fn) { Input.subs.push(fn); return function () { Input.subs = Input.subs.filter(function (f) { return f !== fn; }); }; };
  function emitIn(type, midi, vel, src) { Input.subs.slice().forEach(function (fn) { try { fn(type, midi, vel, src); } catch (e) { console.error(e); } }); }
  Input.noteOn = function (midi, vel, src) {
    if (midi < 21 || midi > 108) return;
    if (Input.held[midi]) Input.noteOff(midi, Input.held[midi]);
    Input.held[midi] = src || 'mouse';
    Input.last = src;
    if (src === 'midi' ? DR.settings.midiSound : DR.settings.keySound) Sound.noteOn(midi, vel);
    emitIn('on', midi, vel == null ? 0.75 : vel, src);
  };
  Input.noteOff = function (midi, src) {
    if (!Input.held[midi]) return;
    delete Input.held[midi];
    Sound.noteOff(midi);
    emitIn('off', midi, 0, src);
  };
  Input.releaseAll = function () { Object.keys(Input.held).forEach(function (m) { Input.noteOff(+m, Input.held[m]); }); };
  Input.capture = function (on) { Input.captured = Math.max(0, Input.captured + (on ? 1 : -1)); if (!Input.captured) Input.releaseAll(); };
  Input.setBase = function (b) {
    Input.base = Math.max(24, Math.min(84, b));
    emitIn('base', Input.base, 0, 'keys');
  };
  Input.keyFor = function (midi) {
    var s = midi - Input.base;
    return s >= 0 && Input.LABELS[s] != null ? Input.LABELS[s] : null;
  };
  function typing(e) {
    var t = e.target;
    return t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.tagName === 'SELECT' || t.isContentEditable);
  }
  window.addEventListener('keydown', function (e) {
    if (!Input.captured || typing(e) || e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.code === 'ArrowUp' || e.code === 'ArrowDown') { e.preventDefault(); Input.releaseAll(); Input.setBase(Input.base + (e.code === 'ArrowUp' ? 12 : -12)); return; }
    var s = Input.KEYMAP[e.code];
    if (s == null) return;
    e.preventDefault();
    if (e.repeat) return;
    Input.noteOn(Input.base + s, 0.75, 'keys');
  });
  window.addEventListener('keyup', function (e) {
    var s = Input.KEYMAP[e.code];
    if (s == null) return;
    var m = Input.base + s;
    if (Input.held[m] === 'keys') Input.noteOff(m, 'keys');
  });
  window.addEventListener('blur', function () { Input.releaseAll(); });
  // a tablet switching apps mid-chord: don't leave notes ringing
  document.addEventListener('visibilitychange', function () { if (document.hidden) Input.releaseAll(); });

  function onMidiMessage(ev) {
    var d = ev.data, cmd = d[0] & 0xf0, note = d[1], vel = d[2];
    if (cmd === 0x90 && vel > 0) Input.noteOn(note, vel / 127, 'midi');
    else if (cmd === 0x80 || (cmd === 0x90 && vel === 0)) { if (Input.held[note] === 'midi') Input.noteOff(note, 'midi'); }
  }
  function attachMidi(access) {
    var names = [];
    access.inputs.forEach(function (inp) { inp.onmidimessage = onMidiMessage; if (inp.state !== 'disconnected') names.push(inp.name || 'MIDI keyboard'); });
    Input.midi.inputs = names;
    Input.midi.status = names.length ? 'on' : 'ready';
    emitIn('midi', 0, 0, 'midi');
  }
  // Ask the browser for MIDI access. silent: only if permission was already given (no prompt).
  Input.enableMidi = function (silent) {
    if (!navigator.requestMIDIAccess) { Input.midi.status = 'unsupported'; return Promise.resolve(Input.midi); }
    var go = function () {
      Input.midi.status = 'pending';
      return navigator.requestMIDIAccess({ sysex: false }).then(function (access) {
        Input.midi.access = access;
        attachMidi(access);
        access.onstatechange = function () { attachMidi(access); };
        DR.store.set('dr.midi', true);
        return Input.midi;
      }, function () { Input.midi.status = 'denied'; emitIn('midi', 0, 0, 'midi'); return Input.midi; });
    };
    if (!silent) return go();
    if (!navigator.permissions || !navigator.permissions.query) return Promise.resolve(Input.midi);
    return navigator.permissions.query({ name: 'midi' }).then(function (st) {
      return st.state === 'granted' ? go() : Input.midi;
    }, function () { return Input.midi; });
  };
  if (DR.store.get('dr.midi', false)) setTimeout(function () { Input.enableMidi(true); }, 300);
})();
