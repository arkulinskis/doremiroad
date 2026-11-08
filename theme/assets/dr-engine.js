/* Doremi Road — the engine (DR.Keyboard, DR.Stage).
   DR.Keyboard: an on-screen piano that shows held keys, targets and hints, and plays through DR.Input.
   DR.Stage: runs one level, step by step, scores it and reports the result.
   Result (what the server checks): {items, hits, score, combo, perfects, notes, chords, ear, quiz, time, midi}. */
(function () {
  'use strict';
  var DR = window.DR = window.DR || {};
  var M = DR.Music, esc = function (s) { return DR.esc(s); };
  var mod = M.mod;

  var CSS = [
    /* keyboard */
    '.kb { position: relative; height: 100%; min-height: 96px; user-select: none; -webkit-user-select: none; -webkit-touch-callout: none; touch-action: none; border-radius: 0 0 10px 10px; }',
    /* touch-screen piano: taller keys, bigger names */
    '.dr-touch .st-kb { height: clamp(140px, 31vh, 270px); } .dr-touch .kb .k .nm { font-size: 13px; margin-bottom: 9px; } .dr-touch .kb .b .nm { font-size: 11px; }',
    '.kb .k { position: absolute; top: 0; box-sizing: border-box; display: flex; flex-direction: column; justify-content: flex-end; align-items: center; cursor: pointer; transition: background .06s, transform .06s, box-shadow .1s; }',
    '.kb .w { height: 100%; background: linear-gradient(180deg, #f3ecdc 0%, #fbf7ee 70%, #e9dfc8 100%); border: 1px solid #2a2a33; border-top: 0; border-radius: 0 0 7px 7px; z-index: 1; box-shadow: inset 0 -6px 0 rgba(0,0,0,.08); }',
    '.kb .b { height: 62%; background: linear-gradient(180deg, #2b2b33, #121217 80%, #2a2a31); border: 1px solid #000; border-top: 0; border-radius: 0 0 5px 5px; z-index: 2; box-shadow: inset 0 -5px 0 rgba(255,255,255,.07), 0 3px 4px rgba(0,0,0,.45); }',
    '.kb .w.down { background: linear-gradient(180deg, #e3d7bd, #efe6d2); transform: translateY(1px); box-shadow: inset 0 -2px 0 rgba(0,0,0,.08); }',
    '.kb .b.down { background: linear-gradient(180deg, #3b3b46, #24242c); transform: translateY(1px); }',
    '.kb .k .nm { font: 600 11px Inter, sans-serif; color: #6c6559; margin-bottom: 6px; pointer-events: none; white-space: nowrap; }',
    '.kb .k .kl { font: 600 10px Inter, sans-serif; color: rgba(60,55,45,.42); margin-bottom: 3px; pointer-events: none; border: 1px solid rgba(60,55,45,.2); border-radius: 4px; padding: 0 4px; min-width: 14px; text-align: center; }',
    '.kb .b .nm { color: #d9cfb9; font-size: 9.5px; } .kb .b .kl { color: rgba(240,231,211,.45); border-color: rgba(240,231,211,.2); }',
    '.kb.noletters .kl { display: none; }',
    '.kb .k.target { background: linear-gradient(180deg, #f4d58f, #e2b25a) !important; box-shadow: 0 0 18px rgba(226,178,90,.75), inset 0 -4px 0 rgba(0,0,0,.12); }',
    '.kb .k.target .nm, .kb .k.lesson .nm, .kb .k.hint .nm { color: #2a1d06; font-weight: 700; }',
    '.kb .b.target .nm, .kb .b.lesson .nm, .kb .b.hint .nm { color: #2a1d06; }',
    '.kb .k.hint { background: linear-gradient(180deg, #f1e2bd, #e8cf94) !important; }',
    '.kb .b.hint { background: linear-gradient(180deg, #b8964f, #8f7036) !important; }',
    '.kb .k.lesson { background: linear-gradient(180deg, #c9d8f5, #9fb9ea) !important; }',
    '.kb .b.lesson { background: linear-gradient(180deg, #6f8fd0, #4b6bb0) !important; }',
    '.kb .k.lane { box-shadow: inset 0 0 0 2px rgba(226,178,90,.65); }',
    '.kb .k.ok { background: linear-gradient(180deg, #a6e8c3, #5cc58d) !important; }',
    '.kb .k.bad { background: linear-gradient(180deg, #f2a39b, #d9584f) !important; }',
    /* skins */
    '.kb.skin-rosewood { background: linear-gradient(180deg,#5a2e1f,#3b1d14); padding: 0 6px 6px; }',
    '.kb.skin-rosewood .w { background: linear-gradient(180deg,#efe2c4,#f6edd8 70%,#dccba4); }',
    '.kb.skin-ebony .w { background: linear-gradient(180deg,#26262e,#1a1a20 75%,#2c2c35); border-color: #000; } .kb.skin-ebony .w .nm { color: #c9bfa9; } .kb.skin-ebony .w .kl { color: rgba(240,231,211,.4); border-color: rgba(240,231,211,.2); }',
    '.kb.skin-ebony .b { background: linear-gradient(180deg,#f4efe3,#d9d1bf); border-color: #888; } .kb.skin-ebony .b .nm { color: #3c352a; } .kb.skin-ebony .b .kl { color: rgba(40,35,30,.5); border-color: rgba(40,35,30,.25); }',
    '.kb.skin-jade .w { background: linear-gradient(180deg,#d7eadf,#eef7f1 70%,#bcd8c8); border-color: #a9863e; } .kb.skin-jade .b { background: linear-gradient(180deg,#2f6b55,#174233); border-color: #a9863e; }',
    '.kb.skin-neon { background: #07060f; } .kb.skin-neon .w { background: linear-gradient(180deg,#14112a,#1d1838); border-color: #ff3ea5; box-shadow: inset 0 -3px 0 #ff3ea5; } .kb.skin-neon .w .nm { color: #ff9bd2; } .kb.skin-neon .kl { color: rgba(255,155,210,.55); border-color: rgba(255,155,210,.3); }',
    '.kb.skin-neon .b { background: linear-gradient(180deg,#0c0a1a,#05040c); border-color: #3ee3ff; box-shadow: inset 0 -3px 0 #3ee3ff, 0 0 8px rgba(62,227,255,.4); } .kb.skin-neon .b .nm { color: #9cf1ff; }',
    '.kb.skin-glass .w { background: linear-gradient(180deg,rgba(220,235,255,.55),rgba(255,255,255,.22)); border-color: rgba(255,255,255,.35); backdrop-filter: blur(2px); } .kb.skin-glass .w .nm { color: #e8f1ff; } .kb.skin-glass .kl { color: rgba(232,241,255,.6); border-color: rgba(232,241,255,.3); }',
    '.kb.skin-glass .b { background: linear-gradient(180deg,rgba(40,60,100,.85),rgba(20,30,60,.9)); border-color: rgba(255,255,255,.3); }',
    '.kb.skin-gilded { background: linear-gradient(180deg,#5a4214,#2c1f08); padding: 0 6px 6px; } .kb.skin-gilded .w { background: linear-gradient(180deg,#fbf3dc,#fff9ea 70%,#ead7a4); border-color: #b58b2c; }',
    '.kb.skin-gilded .b { background: linear-gradient(180deg,#e7c368,#b88a2a 80%,#d8ad4b); border-color: #6f5212; } .kb.skin-gilded .b .nm { color: #3a2a06; } .kb.skin-gilded .b .kl { color: rgba(58,42,6,.6); border-color: rgba(58,42,6,.3); }',
    /* stage */
    '.st { position: absolute; inset: 0; display: flex; flex-direction: column; background: radial-gradient(ellipse at 50% 0%, #1b2442 0%, #0c1020 70%); color: var(--dr-ink); overflow: hidden; }',
    '.st-top { display: flex; align-items: center; gap: 14px; padding: 12px 18px; border-bottom: 1px solid var(--dr-line); background: rgba(10,13,26,.6); flex: none; }',
    '.st-pause { width: 38px; height: 38px; border-radius: 50%; border: 1px solid var(--dr-line-2); background: rgba(255,255,255,.04); color: var(--dr-ink); font-size: 13px; flex: none; }',
    '.st-title { min-width: 0; } .st-title small { display: block; color: var(--dr-soft); font-size: 11px; letter-spacing: .6px; text-transform: uppercase; } .st-title b { font: 600 20px var(--dr-title); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block; }',
    '.st-dots { display: flex; gap: 5px; margin: 0 auto; flex-wrap: wrap; justify-content: center; } .st-dots i { width: 26px; height: 6px; border-radius: 4px; background: rgba(255,255,255,.1); }',
    '.st-dots i.done { background: var(--dr-gold-2); } .st-dots i.cur { background: var(--dr-gold); box-shadow: 0 0 10px rgba(226,178,90,.6); }',
    '.st-stats { display: flex; gap: 18px; flex: none; } .st-stats div { text-align: right; } .st-stats small { display: block; color: var(--dr-soft); font-size: 10.5px; letter-spacing: .6px; text-transform: uppercase; } .st-stats b { font: 600 20px var(--dr-title); font-variant-numeric: tabular-nums; }',
    '.st-main { flex: 1; min-height: 0; display: flex; flex-direction: column; padding: 14px 18px 8px; position: relative; }',
    '.st-head { text-align: center; flex: none; margin-bottom: 8px; } .st-kind { display: inline-flex; gap: 6px; align-items: center; font-size: 11.5px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: var(--dr-gold); }',
    '.st-prompt { font: 600 26px var(--dr-title); margin-top: 4px; }',
    '.st-body { flex: 1; min-height: 0; position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px; }',
    '.st-kbwrap { flex: none; padding: 0 18px 14px; } .st-kbinfo { display: flex; justify-content: space-between; gap: 10px; font-size: 12px; color: var(--dr-soft); padding: 6px 2px; flex-wrap: wrap; }',
    '.st-kbinfo b { color: var(--dr-ink-2); font-weight: 600; } .st-kb { height: clamp(110px, 22vh, 190px); border-top: 3px solid #6b1f2a; border-radius: 0 0 10px 10px; box-shadow: 0 -4px 14px rgba(0,0,0,.4); }',
    '.st-banner { position: absolute; left: 50%; top: 40%; transform: translate(-50%,-50%); background: rgba(10,13,26,.92); border: 1px solid var(--dr-gold); border-radius: 14px; padding: 16px 28px; text-align: center; z-index: 20; animation: drPop .25s; box-shadow: 0 10px 40px rgba(0,0,0,.5); }',
    '.st-banner b { display: block; font: 600 24px var(--dr-title); color: var(--dr-gold); } .st-banner span { color: var(--dr-ink-2); font-size: 14px; }',
    /* note & chord steps */
    '.nt-big { font: 600 64px var(--dr-title); line-height: 1; color: var(--dr-ink); text-shadow: 0 0 30px rgba(226,178,90,.25); min-height: 64px; }',
    '.nt-big small { display: block; font: 500 15px var(--dr-font); color: var(--dr-ink-2); margin-top: 8px; letter-spacing: .2px; }',
    '.nt-label { font: 500 italic 26px var(--dr-title); color: var(--dr-gold); text-align: center; }',
    '.nt-chips { display: flex; gap: 6px; flex-wrap: wrap; justify-content: center; max-width: 760px; }',
    '.nt-chip { min-width: 40px; padding: 6px 10px; border-radius: 9px; border: 1px solid var(--dr-line); background: rgba(255,255,255,.03); text-align: center; font-weight: 600; font-size: 14px; color: var(--dr-ink-2); }',
    '.nt-chip.cur { border-color: var(--dr-gold); color: var(--dr-gold); background: var(--dr-gold-soft); transform: translateY(-2px); } .nt-chip.done { color: #8fdcb1; border-color: rgba(76,179,125,.4); } .nt-chip.miss { color: #f0a49e; border-color: rgba(224,96,90,.45); }',
    '.nt-chip .rn { display: block; font: 600 22px var(--dr-title); color: var(--dr-ink); } .nt-chip.cur .rn { color: var(--dr-gold); } .nt-chip small { font-size: 11px; font-weight: 600; }',
    '.nt-tip { font-size: 13px; color: var(--dr-soft); min-height: 18px; text-align: center; }',
    '.nt-staff { background: rgba(255,255,255,.02); border: 1px solid var(--dr-line); border-radius: 12px; padding: 4px 8px; max-width: 100%; overflow-x: auto; }',
    '.shake { animation: drShake .3s; } @keyframes drShake { 25% { transform: translateX(-6px); } 75% { transform: translateX(6px); } }',
    /* lesson */
    '.ls { max-width: 720px; text-align: center; } .ls h3 { font: 600 30px var(--dr-title); color: var(--dr-gold); margin-bottom: 10px; } .ls p { font-size: 17px; line-height: 1.6; color: var(--dr-ink); margin: 0 auto 14px; max-width: 640px; }',
    '.ls .ls-btns { display: flex; gap: 10px; justify-content: center; margin-top: 8px; }',
    /* ear & quiz */
    '.ear-play { width: 110px; height: 110px; border-radius: 50%; border: 1px solid var(--dr-gold); background: radial-gradient(circle at 40% 35%, #2c3560, #151b33); color: var(--dr-gold); font-size: 38px; box-shadow: 0 0 30px rgba(226,178,90,.25); }',
    '.ear-play.on { animation: drPulse .6s ease-in-out infinite; box-shadow: 0 0 40px rgba(226,178,90,.55); }',
    '.opts { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; width: 100%; max-width: 720px; }',
    '.opt { padding: 14px 16px; border-radius: 12px; border: 1px solid var(--dr-line-2); background: rgba(255,255,255,.035); color: var(--dr-ink); font-size: 15.5px; font-weight: 500; text-align: left; transition: background .15s, border-color .15s, transform .08s; }',
    '.opt:hover { background: rgba(255,255,255,.07); border-color: rgba(232,212,168,.5); } .opt:active { transform: scale(.99); } .opt[disabled] { cursor: default; }',
    '.opt.right { background: rgba(76,179,125,.18); border-color: #4cb37d; color: #c9f2db; } .opt.wrong { background: rgba(224,96,90,.16); border-color: #e0605a; color: #f6c9c5; }',
    '.opt .n { display: inline-flex; width: 22px; height: 22px; border-radius: 6px; align-items: center; justify-content: center; font-size: 11.5px; font-weight: 700; background: rgba(255,255,255,.07); margin-right: 10px; color: var(--dr-ink-2); }',
    '.qz-q { font: 600 30px var(--dr-title); text-align: center; max-width: 760px; } .qz-ex { font-size: 15px; color: var(--dr-ink-2); text-align: center; max-width: 640px; min-height: 22px; }',
    /* rush */
    '.rush { position: absolute; inset: 0; } .rush canvas { position: absolute; inset: 0; width: 100%; height: 100%; }',
    '.rush-meter { position: absolute; right: 0; top: 6px; bottom: 10px; width: 10px; border-radius: 6px; background: rgba(255,255,255,.07); overflow: hidden; border: 1px solid var(--dr-line); }',
    '.rush-meter i { position: absolute; left: 0; right: 0; bottom: 0; background: linear-gradient(0deg, #e0605a, #e2b25a 45%, #4cb37d); transition: height .2s; }',
    '.rush-judge { position: absolute; left: 50%; top: 32%; transform: translateX(-50%); font: 700 30px var(--dr-caps); letter-spacing: 3px; pointer-events: none; text-shadow: 0 0 18px currentColor; }',
    '.rush-judge.pop { animation: drJudge .5s ease-out forwards; } @keyframes drJudge { from { transform: translateX(-50%) scale(1.25); opacity: 1; } to { transform: translateX(-50%) translateY(-14px) scale(1); opacity: 0; } }',
    '.rush-count { position: absolute; left: 50%; top: 40%; transform: translate(-50%,-50%); font: 600 90px var(--dr-title); color: var(--dr-gold); pointer-events: none; text-shadow: 0 0 40px rgba(226,178,90,.6); }',
    '.rush-combo { position: absolute; left: 6px; top: 6px; font: 600 15px var(--dr-font); color: var(--dr-ink-2); pointer-events: none; } .rush-combo b { font: 600 30px var(--dr-title); color: var(--dr-gold); display: block; line-height: 1; }',
    '@media (max-width: 700px) { .st-top { padding: 8px 10px; gap: 8px; flex-wrap: wrap; } .st-dots { order: 5; width: 100%; } .st-dots i { width: 16px; } .st-stats { gap: 10px; } .st-stats b { font-size: 16px; }',
    '  .st-prompt { font-size: 20px; } .st-main { padding: 8px 10px 4px; } .st-kbwrap { padding: 0 6px 8px; } .nt-big { font-size: 46px; } .qz-q { font-size: 22px; } .ls p { font-size: 15px; } .ls h3 { font-size: 24px; } .st-title b { font-size: 16px; } }',
    /* short screens (a phone held sideways): a compact stage so the keys keep their room */
    '@media (max-height: 520px) { .dr-touch .st-kb { height: clamp(96px, 30vh, 150px); }',
    '  .st-top { padding: 5px 12px; } .st-pause { width: 32px; height: 32px; } .st-title small { display: none; } .st-title b { font-size: 16px; } .st-stats small { font-size: 9.5px; } .st-stats b { font-size: 15px; }',
    '  .st-main { padding: 4px 12px 2px; } .st-head { margin-bottom: 2px; } .st-kind { display: none; } .st-prompt { font-size: 18px; margin-top: 0; }',
    '  .st-body { gap: 6px; overflow-y: auto; justify-content: safe center; } .nt-big { font-size: 34px; min-height: 0; } .nt-big small { font-size: 12px; margin-top: 2px; } .nt-label { font-size: 18px; } .nt-tip { font-size: 12px; min-height: 0; }',
    '  .nt-chip { padding: 3px 8px; min-width: 32px; } .nt-chip .rn { font-size: 16px; } .st-kbinfo { display: none; } .st-kbwrap { padding-bottom: 6px; }',
    '  .ear-play { width: 64px; height: 64px; font-size: 24px; } .opts { gap: 6px; } .opt { padding: 7px 12px; font-size: 14px; } .qz-q { font-size: 20px; } .qz-ex { font-size: 13px; }',
    '  .ls h3 { font-size: 20px; margin-bottom: 4px; } .ls p { font-size: 13.5px; line-height: 1.45; margin-bottom: 6px; } .st-banner { padding: 10px 20px; } }'
  ].join('\n');
  (function () { var s = document.createElement('style'); s.textContent = CSS; document.head.appendChild(s); })();

  /* ---------- the on-screen keyboard ---------- */
  function Keyboard(host, o) {
    o = o || {};
    var el = document.createElement('div');
    host.appendChild(el);
    var keys = {}, low = 60, high = 83, pointers = {};
    // computer-key letters only make sense with a computer keyboard
    function cls() { el.className = 'kb skin-' + (o.skin || 'ivory') + (DR.settings.letters && !DR.touchUI() ? '' : ' noletters'); }
    function label(m) {
      var k = keys[m];
      if (!k) return;
      var named = k.classList.contains('target') || k.classList.contains('lesson') || k.classList.contains('hint') || k.dataset.named;
      var pc = mod(m, 12), lab = '';
      if (named) lab = k.dataset.named || M.pcName(pc, o.flats);
      else if (DR.settings.labels === 'all' && !M.isBlack(m)) lab = M.pcName(pc);
      else if (DR.settings.labels !== 'none' && pc === 0) lab = 'C' + (Math.floor(m / 12) - 1);
      k.querySelector('.nm').textContent = lab;
      var kl = DR.Input.keyFor(m);
      k.querySelector('.kl').textContent = kl || '';
      k.querySelector('.kl').style.visibility = kl ? '' : 'hidden';
    }
    function build(lo, hi) {
      low = lo; high = hi; keys = {};
      el.innerHTML = '';
      cls();
      var whites = [];
      for (var m = lo; m <= hi; m++) if (!M.isBlack(m)) whites.push(m);
      var ww = 100 / whites.length;
      whites.forEach(function (m, i) {
        var d = document.createElement('div');
        d.className = 'k w'; d.dataset.m = m;
        d.style.left = (i * ww) + '%'; d.style.width = ww + '%';
        d.innerHTML = '<span class="nm"></span><span class="kl"></span>';
        el.appendChild(d); keys[m] = d;
      });
      for (var b = lo; b <= hi; b++) {
        if (!M.isBlack(b)) continue;
        var wi = whites.indexOf(b - 1);
        if (wi < 0) continue;
        var bw = ww * 0.6, shift = { 1: -0.1, 3: 0.1, 6: -0.12, 8: 0, 10: 0.12 }[mod(b, 12)] || 0;
        var d2 = document.createElement('div');
        d2.className = 'k b'; d2.dataset.m = b;
        d2.style.left = ((wi + 1) * ww - bw / 2 + shift * bw) + '%'; d2.style.width = bw + '%';
        d2.innerHTML = '<span class="nm"></span><span class="kl"></span>';
        el.appendChild(d2); keys[b] = d2;
      }
      Object.keys(DR.Input.held).forEach(function (h) { if (keys[h]) keys[h].classList.add('down'); });
      relabel();
    }
    function relabel() { cls(); Object.keys(keys).forEach(function (m) { label(+m); }); }
    function keyAt(x, y) { var t = document.elementFromPoint(x, y); return t && t.closest ? t.closest('.kb .k') : null; }
    /* Mouse and fingers. pointers: pointerId → the key under it (null once it slides off the keys).
       Each finger is its own pointer, so chords are just several fingers down at once. */
    function holders(m) { var n = 0; for (var id in pointers) if (pointers[id] === m) n++; return n; }
    // Like a tablet piano app: tapping lower on a key plays louder.
    function velAt(k, y) { var r = k.getBoundingClientRect(), f = r.height ? (y - r.top) / r.height : 0.55; return Math.max(0.45, Math.min(1, 0.45 + 0.55 * f)); }
    function press(id, k, y) { var m = +k.dataset.m; pointers[id] = m; DR.Input.noteOn(m, velAt(k, y), 'mouse'); }
    function lift(id) {
      var m = pointers[id];
      pointers[id] = null;
      if (m != null && !holders(m) && DR.Input.held[m] === 'mouse') DR.Input.noteOff(m, 'mouse');
    }
    el.addEventListener('pointerdown', function (e) {
      var k = e.target.closest('.k');
      if (!k) return;
      e.preventDefault();
      DR.Sound.init();
      if (pointers[e.pointerId] != null) lift(e.pointerId);
      press(e.pointerId, k, e.clientY);
    });
    // sliding a finger along the keys plays each one (a glissando); off the keys it stops
    el.addEventListener('pointermove', function (e) {
      if (!(e.pointerId in pointers)) return;
      var k = keyAt(e.clientX, e.clientY), m = k ? +k.dataset.m : null;
      if (m === pointers[e.pointerId]) return;
      lift(e.pointerId);
      if (k) press(e.pointerId, k, e.clientY);
    });
    function up(e) {
      if (!(e.pointerId in pointers)) return;
      lift(e.pointerId);
      delete pointers[e.pointerId];
    }
    ['pointerup', 'pointercancel'].forEach(function (ev) { window.addEventListener(ev, up); });
    el.addEventListener('contextmenu', function (e) { e.preventDefault(); });   // long-press on Android
    var off = DR.Input.on(function (type, m) {
      if (type === 'base' || type === 'midi') { relabel(); return; }
      var k = keys[m];
      if (!k) return;
      if (type === 'on') k.classList.add('down'); else if (type === 'off') k.classList.remove('down');
    });
    build(low, high);
    var api = {
      el: el,
      range: function () { return [low, high]; },
      setRange: function (lo, hi) { if (lo !== low || hi !== high) build(lo, hi); },
      setSkin: function (s) { o.skin = s; cls(); },
      setFlats: function (f) { o.flats = !!f; relabel(); },
      // mark(midis, cls, names): add a class to keys; names: optional {midi: label}
      mark: function (midis, c, names) {
        (midis || []).forEach(function (m) { var k = keys[m]; if (k) { k.classList.add(c); if (names && names[m]) k.dataset.named = names[m]; label(m); } });
      },
      unmark: function (c) {
        el.querySelectorAll('.k.' + c).forEach(function (k) { k.classList.remove(c); delete k.dataset.named; label(+k.dataset.m); });
      },
      flash: function (m, c, ms) {
        var k = keys[m];
        if (!k) return;
        k.classList.add(c);
        setTimeout(function () { k.classList.remove(c); }, ms || 260);
      },
      // x position and width of a key, in px from the keyboard's left edge (clamped to the ends)
      keyRect: function (m) {
        var k = keys[Math.max(low, Math.min(high, m))] || keys[low];
        var r = el.getBoundingClientRect(), kr = k.getBoundingClientRect();
        return { x: kr.left - r.left, w: kr.width, black: M.isBlack(m), left: r.left };
      },
      relabel: relabel,
      destroy: function () { off(); ['pointerup', 'pointercancel'].forEach(function (ev) { window.removeEventListener(ev, up); }); el.remove(); }
    };
    return api;
  }
  // A keyboard range (whole octaves, C to B) that shows all these notes: at least minOct octaves, at most 4.
  function rangeFor(midis, minOct) {
    midis = (midis || []).filter(function (m) { return m != null; });
    if (!midis.length) midis = [60];
    var lo = Math.min.apply(null, midis), hi = Math.max.apply(null, midis);
    var a = Math.floor(lo / 12) * 12, b = Math.floor(hi / 12) * 12 + 11;
    minOct = minOct || 1;
    while ((b - a + 1) / 12 < minOct) { if (b < 95) b += 12; else a -= 12; }
    while ((b - a + 1) / 12 > 4) b -= 12;
    return [a, b];
  }

  /* ---------- items per step: must match Levels._step_items on the server ---------- */
  function stepItems(s) {
    switch (s && s.t) {
      case 'notes': return (s.notes || []).length;
      case 'chords': return (s.chords || []).length;
      case 'progression': return (s.numerals || []).length;
      case 'rush': var p = M.parseSeq(s.seq); return p ? p[0].length : 0;
      case 'ear': var c = parseInt(s.count, 10); return Math.max(1, Math.min(12, isNaN(c) ? 1 : c));
      case 'quiz': return 1;
      default: return 0;
    }
  }
  function levelItems(data) { return (data.steps || []).reduce(function (a, s) { return a + stepItems(s); }, 0); }

  var TRAILS = {
    lantern: function () { return ['#f6d38a', '#d49a3e']; },
    ember: function () { return ['#ffcf6e', '#ff5a2d']; },
    frost: function () { return ['#e2f6ff', '#6cc4f5']; },
    aurora: function (m) { return mod(m, 2) ? ['#a8ffd8', '#3ccf91'] : ['#d6c2ff', '#8b62f2']; },
    prism: function (m) { var h = mod(m, 12) * 30; return ['hsl(' + h + ',90%,78%)', 'hsl(' + h + ',75%,52%)']; }
  };

  /* ---------- the stage: one level ---------- */
  function Stage(root, level, o) {
    o = o || {};
    var data = level.data || {}, steps = data.steps || [];
    var dbg = Stage.debug;
    var S = { i: -1, hits: 0, judged: 0, score: 0, streak: 0, combo: 0, maxCombo: 0, perfects: 0, notes: 0, chords: 0, ear: 0, quiz: 0,
      midi: false, t0: performance.now(), paused: false, over: false, stepHits: 0, stepItems: 0, meter: 0.6 };
    var totalItems = levelItems(data);
    var minOct = window.innerWidth < 700 ? 1 : 2;
    root.innerHTML = '<div class="dr st">' +
      '<div class="st-top"><button class="st-pause" data-a="pause" aria-label="Pause">❚❚</button>' +
      '<div class="st-title"><small>' + esc(o.subtitle || '') + '</small><b>' + esc(level.name || 'Level') + '</b></div>' +
      '<div class="st-dots">' + steps.map(function () { return '<i></i>'; }).join('') + '</div>' +
      '<div class="st-stats"><div><small>Score</small><b class="v-score">0</b></div><div><small>Accuracy</small><b class="v-acc">–</b></div><div><small>Streak</small><b class="v-streak">0</b></div></div></div>' +
      '<div class="st-main"><div class="st-head"><div class="st-kind"></div><h2 class="st-prompt"></h2></div><div class="st-body"></div></div>' +
      '<div class="st-kbwrap"><div class="st-kbinfo"><span class="v-input"></span><span class="v-keys"></span></div><div class="st-kb"></div></div></div>';
    var $ = function (s) { return root.querySelector(s); };
    var body = $('.st-body'), kb = Keyboard($('.st-kb'), { skin: o.skin });
    var cur = null, timers = [];
    function later(fn, ms) { var id = setTimeout(function () { timers = timers.filter(function (x) { return x !== id; }); if (!S.over) fn(); }, dbg.auto ? Math.min(ms, 40) : ms); timers.push(id); return id; }
    var captured = true;
    DR.Input.capture(true);
    function release() { if (captured) { captured = false; DR.Input.capture(false); } }
    var offIn = DR.Input.on(function (type, m, vel, src) {
      if (type === 'midi' || type === 'base') { info(); return; }
      if (S.paused || S.over || !cur) return;
      if (type === 'on') { if (src === 'midi') S.midi = true; if (cur.on) cur.on(m, src); }
      else if (type === 'off' && cur.off) cur.off(m);
    });
    function info() {
      var mi = DR.Input.midi, touch = DR.touchUI();
      $('.v-input').innerHTML = mi.status === 'on' ? '🎹 <b>' + esc(mi.inputs[0]) + '</b>' : touch ? '👆 <b>Tap the keys</b> · several fingers at once for chords' : '⌨️ Computer keyboard or click the keys';
      var b = DR.Input.base;
      $('.v-keys').innerHTML = mi.status === 'on' || touch ? '' : '<b>Z</b>–<b>M</b> = ' + M.nameOf(b) + ' octave · <b>Q</b>–<b>U</b> = ' + M.nameOf(b + 12) + ' octave · <b>↑ ↓</b> shift octave';
    }
    info();
    function stats() {
      $('.v-score').textContent = DR.fmt(S.score);
      $('.v-acc').textContent = S.judged ? Math.round(100 * S.hits / S.judged) + '%' : '–';
      $('.v-streak').textContent = S.streak;
    }
    function dots() {
      root.querySelectorAll('.st-dots i').forEach(function (d, i) { d.className = i < S.i ? 'done' : i === S.i ? 'cur' : ''; });
    }
    // Score one item. pts: 0..1 (rush can give part marks). kind: notes|chords|ear|quiz.
    function award(pts, kind, rush) {
      S.hits += pts; S.judged++; S.stepHits += pts;
      if (pts > 0) {
        S.streak++;
        if (kind) S[kind]++;
        S.score += Math.round(100 * pts * (rush ? 1 + Math.min(S.combo, 20) / 40 : 1 + Math.min(S.streak, 10) / 20));
      } else S.streak = 0;
      stats();
    }
    function mistake() { S.streak = 0; stats(); DR.Sound.sfx('wrong'); }
    function setRange(midis, flats) {
      var r = rangeFor(midis, minOct);
      kb.setRange(r[0], r[1]);
      kb.setFlats(flats);
      if (DR.Input.base !== r[0]) DR.Input.setBase(r[0]);
    }
    function head(kind, prompt) {
      $('.st-kind').innerHTML = '<span class="dr-emoji">' + (DR.Art.STEP_ICONS[kind] || '') + '</span> ' + esc(DR.Art.STEP_NAMES[kind] || kind) +
        ' <span class="dr-muted">· step ' + (S.i + 1) + ' of ' + steps.length + '</span>';
      $('.st-prompt').textContent = prompt || '';
    }
    function clearKb() { ['target', 'hint', 'lesson', 'lane', 'ok', 'bad'].forEach(function (c) { kb.unmark(c); }); }

    function next() {
      if (cur && cur.destroy) cur.destroy();
      cur = null;
      clearKb();
      S.i++;
      dots();
      if (S.i >= steps.length) return end();
      var st = steps[S.i];
      S.stepHits = 0; S.stepItems = stepItems(st);
      body.innerHTML = '';
      var R = RUNNERS[st.t] || RUNNERS.lesson;
      cur = R(st);
      if (o.onEvent) o.onEvent('step', { i: S.i, n: steps.length, t: st.t });
      if (dbg.auto && cur.auto) later(function () { if (cur && cur.auto) cur.auto(); }, 30);
    }
    function stepDone() {
      if (S.over) return;
      var n = S.stepItems;
      if (cur && cur.destroy) cur.destroy();
      cur = null;
      clearKb();
      if (!n) return next();
      DR.Sound.sfx('step');
      var pct = Math.round(100 * S.stepHits / n);
      var bn = document.createElement('div');
      bn.className = 'st-banner';
      bn.innerHTML = '<b>' + (pct >= 95 ? 'Superb' : pct >= 80 ? 'Well played' : pct >= 60 ? 'Step complete' : 'Keep going') + '</b><span>' +
        (Math.round(S.stepHits * 10) / 10) + ' / ' + n + ' · ' + pct + '%</span>';
      $('.st-main').appendChild(bn);
      later(function () { bn.remove(); next(); }, 1100);
    }
    function end() {
      S.over = true;
      release();
      var acc = totalItems ? 100 * S.hits / totalItems : 100;
      var result = { items: totalItems, hits: Math.round(S.hits * 1000) / 1000, score: S.score, combo: S.maxCombo, perfects: S.perfects,
        notes: S.notes, chords: S.chords, ear: S.ear, quiz: S.quiz, time: Math.round((performance.now() - S.t0) / 100) / 10, midi: S.midi };
      var pass = data.pass == null ? 60 : data.pass;
      if (acc < pass) { if (o.onFail) o.onFail({ reason: 'accuracy', accuracy: acc, pass: pass, result: result }); }
      else if (o.onFinish) o.onFinish(result, acc);
    }
    function fail(reason) {
      if (S.over) return;
      S.over = true;
      if (cur && cur.destroy) cur.destroy();
      cur = null;
      release();
      DR.Sound.sfx('fail');
      if (o.onFail) o.onFail({ reason: reason, accuracy: S.judged ? 100 * S.hits / S.judged : 0 });
    }

    /* ----- lesson ----- */
    function runLesson(st) {
      head('lesson', '');
      var show = (st.show || []).map(M.parseNote).filter(function (m) { return m != null; });
      setRange(show.length ? show : [60], (st.show || []).some(function (n) { return /b\d$/.test(n); }));
      var names = {};
      (st.show || []).forEach(function (n) { var m = M.parseNote(n); if (m != null) names[m] = M.pretty(n, true); });
      kb.mark(show, 'lesson', names);
      var paras = String(st.text || '').split(/\n\s*\n/).map(function (p) { return '<p>' + esc(p) + '</p>'; }).join('');
      body.innerHTML = '<div class="ls"><h3>' + esc(st.title || 'Lesson') + '</h3>' + paras +
        (st.staff && st.show && st.show.length ? '<div class="nt-staff" style="display:inline-block;margin-bottom:12px">' + DR.Art.staff(st.show, { clef: st.staff, names: true }) + '</div>' : '') +
        '<div class="ls-btns">' + (show.length ? '<button class="dr-btn" data-a="hear">▶ Hear it</button>' : '') +
        '<button class="dr-btn gold" data-a="cont">Continue ▸</button></div><div class="nt-tip">Try the highlighted keys.' + (DR.touchUI() ? '' : ' Press Enter to continue.') + '</div></div>';
      function onClick(e) {
        var a = e.target.closest('[data-a]');
        if (!a) return;
        if (a.dataset.a === 'hear') DR.Sound.play(show, { gap: 0.45 });
        if (a.dataset.a === 'cont') { DR.Sound.sfx('click'); stepDone(); }
      }
      function onKey(e) { if (e.key === 'Enter' && !S.paused) { e.preventDefault(); stepDone(); } }
      body.addEventListener('click', onClick);
      window.addEventListener('keydown', onKey);
      return {
        on: function (m) { if (show.indexOf(m) >= 0) kb.flash(m, 'ok', 200); },
        auto: function () { stepDone(); },
        destroy: function () { body.removeEventListener('click', onClick); window.removeEventListener('keydown', onKey); }
      };
    }

    /* ----- notes: play each note in turn ----- */
    function runNotes(st) {
      var list = st.notes || [], midis = list.map(M.parseNote), idx = 0, tries = 0, exact = !!st.exact;
      var mode = st.show || 'keys', labels = st.labels || [], missed = {};
      head('notes', st.prompt);
      setRange(midis, list.some(function (n) { return /b-?\d$/.test(n); }));
      body.innerHTML = '<div class="nt-label"></div><div class="nt-big"></div><div class="nt-staff" style="display:none"></div><div class="nt-chips"></div><div class="nt-tip"></div>';
      var $l = body.querySelector('.nt-label'), $b = body.querySelector('.nt-big'), $s = body.querySelector('.nt-staff'),
        $c = body.querySelector('.nt-chips'), $t = body.querySelector('.nt-tip');
      function nm(i) { return M.pretty(list[i], !exact); }
      function draw() {
        var hide = mode === 'staff' || labels.length;
        $l.textContent = labels[idx] || '';
        $b.innerHTML = mode === 'staff' || labels[idx] ? '' : esc(nm(idx)) + (mode === 'keys' ? '<small>Play the glowing key</small>' : exact ? '<small>Exact octave</small>' : '');
        $b.style.display = $b.innerHTML ? '' : 'none';
        if (mode === 'staff') { $s.style.display = ''; $s.innerHTML = DR.Art.staff(list, { clef: st.clef, current: idx, done: idx, names: 'done' }); }
        $c.innerHTML = list.length > 1 ? list.map(function (n, i) {
          return '<span class="nt-chip ' + (i < idx ? (missed[i] ? 'miss' : 'done') : i === idx ? 'cur' : '') + '">' + (i < idx || !hide ? esc(nm(i)) : i === idx ? '?' : '·') + '</span>';
        }).join('') : '';
        kb.unmark('target'); kb.unmark('hint');
        var names = {}; names[midis[idx]] = M.pretty(list[idx], true);
        if (mode === 'keys') kb.mark([midis[idx]], 'target', names);
        else if (tries >= 2) kb.mark([midis[idx]], 'hint', names);
        $t.textContent = tries >= 2 ? 'Here it is: ' + M.pretty(list[idx], true) + '. Play it to go on.' : exact ? 'The octave counts here.' : 'Any octave counts.';
      }
      draw();
      return {
        on: function (m) {
          if (idx >= list.length) return;
          var ok = exact ? m === midis[idx] : mod(m, 12) === mod(midis[idx], 12);
          if (ok) {
            kb.flash(m, 'ok');
            award(tries === 0 ? 1 : 0, 'notes');
            if (tries) missed[idx] = true;
            idx++; tries = 0;
            if (idx >= list.length) { draw(); later(stepDone, 250); } else draw();
          } else {
            kb.flash(m, 'bad');
            tries++;
            mistake();
            $b.classList.remove('shake'); void $b.offsetWidth; $b.classList.add('shake');
            if (tries === 2) draw();
          }
        },
        auto: function step() { if (idx < list.length && !S.over) { this.on(midis[idx]); later(step.bind(this), 20); } }
      };
    }

    /* ----- chords and progressions: play each chord (all its notes) ----- */
    function runChords(st, prog) {
      var items = prog ? (st.numerals || []).map(function (n) { return M.parseNumeral(n, st.key); }) : (st.chords || []).map(M.chordOf);
      var exact = !prog && !!st.exact, hint = !!st.hint, labels = st.labels || [], idx = 0, tries = 0, pressed = [], fresh = 0, missed = {}, lock = false;
      var flats = prog ? M.keyUsesFlats(st.key) : items.some(function (c) { return c && /♭/.test(c.symbol); });
      head(prog ? 'progression' : 'chords', st.prompt);
      var all = [];
      items.forEach(function (c) { if (c) all = all.concat(c.notes); });
      setRange(all, flats);
      body.innerHTML = (prog ? '<div class="nt-label">Key of ' + esc(M.keyName(st.key)) + '</div>' : '<div class="nt-label"></div>') +
        '<div class="nt-big"></div><div class="nt-chips"></div><div class="nt-tip"></div>';
      var $l = body.querySelector('.nt-label'), $b = body.querySelector('.nt-big'), $c = body.querySelector('.nt-chips'), $t = body.querySelector('.nt-tip');
      function draw() {
        var c = items[idx];
        if (!prog) $l.textContent = labels[idx] || '';
        if (c) {
          var showName = !prog || st.names !== false || tries >= 2;
          $b.innerHTML = prog ? esc(c.numeral) + '<small>' + (showName ? esc(c.symbol) + ' · ' + esc(c.name) : 'Work out the chord from the numeral') + '</small>'
            : esc(c.type === '?' ? c.name : c.symbol) + '<small>' + esc(c.type === '?' ? 'Play these notes together' : c.name) + (hint || tries >= 2 ? ' · ' + esc(c.spelled.join(' ')) : '') + '</small>';
        }
        $c.innerHTML = items.length > 1 ? items.map(function (x, i) {
          var top = prog ? x.numeral : (x.type === '?' ? (i < idx || i === idx ? x.name : '?') : x.symbol);
          var sub = prog ? (st.names !== false || i < idx ? x.symbol : '') : '';
          return '<span class="nt-chip ' + (i < idx ? (missed[i] ? 'miss' : 'done') : i === idx ? 'cur' : '') + '"><span class="rn">' + esc(top) + '</span>' + (sub ? '<small>' + esc(sub) + '</small>' : '') + '</span>';
        }).join('') : '';
        kb.unmark('hint');
        if (c && (hint || tries >= 2)) {
          var names = {};
          c.notes.forEach(function (m, j) { names[m] = c.spelled[j] || M.pcName(m); });
          kb.mark(c.notes, 'hint', names);
        }
        $t.textContent = tries >= 2 ? 'The lit keys show it. Play them together.' : exact ? 'Play exactly these keys (this shape and octave).' : 'Any octave or inversion counts. Hold the notes together, or play them quickly one after another.';
      }
      function satisfied(c) {
        var now = performance.now();
        pressed = pressed.filter(function (p) { return now - p[1] < 1500; });
        var active = Object.keys(DR.Input.held).map(Number).concat(pressed.map(function (p) { return p[0]; }));
        if (exact) return c.notes.every(function (m) { return active.indexOf(m) >= 0; });
        var have = M.pcs(active);
        return M.pcs(c.notes).every(function (p) { return have.indexOf(p) >= 0; });
      }
      draw();
      var api = {
        on: function (m) {
          var c = items[idx];
          if (!c || lock) return;
          var inT = exact ? c.notes.indexOf(m) >= 0 : M.pcs(c.notes).indexOf(mod(m, 12)) >= 0;
          if (!inT) {
            kb.flash(m, 'bad');
            tries++; mistake(); pressed = [];
            $b.classList.remove('shake'); void $b.offsetWidth; $b.classList.add('shake');
            if (tries === 2) draw();
            return;
          }
          pressed.push([m, performance.now()]); fresh++;
          if (fresh && satisfied(c)) {
            c.notes.forEach(function (n) { kb.flash(n, 'ok', 380); });
            award(tries === 0 ? 1 : 0, 'chords');
            if (tries) missed[idx] = true;
            idx++; tries = 0; pressed = []; fresh = 0; lock = true;
            if (idx >= items.length) { draw(); later(stepDone, 350); }
            else later(function () { lock = false; draw(); }, 260);
          }
        },
        auto: function step() {
          if (S.over || idx >= items.length) return;
          if (!lock) items[idx].notes.forEach(function (m) { api.on(m); });
          later(step, 20);
        }
      };
      return api;
    }

    /* ----- rush: notes fall to the keys, in time ----- */
    function runRush(st) {
      var parsed = M.parseSeq(st.seq) || [[], 0], bpm = st.bpm || 90, spb = 60 / bpm, lead = 4 * spb, exact = !!st.exact;
      var trail = TRAILS[o.trail] || TRAILS.lantern;
      var evs = parsed[0].map(function (e) {
        var lab = e.label || (st.hint && e.names ? e.names.map(function (x) { return M.pretty(x, true); }).join(' ') : null);
        return { t: lead + e.t * spb, d: e.d * spb, notes: e.notes, pcs: M.pcs(e.notes), label: lab, hit: {}, done: false, res: null, chord: e.notes.length > 1 };
      });
      var lastEnd = evs.length ? Math.max.apply(null, evs.map(function (e) { return e.t + e.d; })) : lead;
      head('rush', st.prompt);
      var all = [];
      evs.forEach(function (e) { all = all.concat(e.notes); });
      setRange(all, /b\d/.test(st.seq || ''));
      body.innerHTML = '<div class="rush"><canvas></canvas><div class="rush-meter"><i></i></div><div class="rush-combo"></div><div class="rush-judge"></div><div class="rush-count"></div></div>';
      var cv = body.querySelector('canvas'), ctx = cv.getContext('2d'), $m = body.querySelector('.rush-meter i'), $j = body.querySelector('.rush-judge'),
        $n = body.querySelector('.rush-count'), $cb = body.querySelector('.rush-combo');
      var actx = DR.Sound.init(), scale = dbg.timeScale || 1;
      function raw() { return actx && actx.state === 'running' && !dbg.auto ? actx.currentTime : performance.now() / 1000; }
      var start = raw() + 0.4, pausedAt = null, pausedFor = 0, beat = 0, alive = true, laneKey = '';
      function now() { return ((pausedAt != null ? pausedAt : raw()) - start - pausedFor) * scale; }
      var P = 0.07, G = 0.12, OK = 0.18;
      function judgeText(txt, col) {
        $j.textContent = txt; $j.style.color = col;
        $j.classList.remove('pop'); void $j.offsetWidth; $j.classList.add('pop');
      }
      function meter(d) {
        S.meter = Math.max(0, Math.min(1, S.meter + d));
        $m.style.height = (S.meter * 100) + '%';
        if (S.meter <= 0 && !dbg.auto) fail('meter');
      }
      meter(0);
      function judge(e, dt) {
        e.done = true;
        var a = Math.abs(dt);
        e.res = a <= P ? 'perfect' : a <= G ? 'great' : 'good';
        var pts = { perfect: 1, great: 0.85, good: 0.6 }[e.res];
        S.combo++; S.maxCombo = Math.max(S.maxCombo, S.combo);
        if (e.res === 'perfect') S.perfects++;
        award(pts, e.chord ? 'chords' : 'notes', true);
        meter(e.res === 'perfect' ? 0.035 : 0.025);
        judgeText(e.res.toUpperCase(), e.res === 'perfect' ? '#f6d38a' : e.res === 'great' ? '#9fe0bd' : '#c4bba6');
        e.notes.forEach(function (n) { kb.flash(n, 'ok', 160); });
        $cb.innerHTML = S.combo >= 5 ? '<b>' + S.combo + '</b>combo' : '';
      }
      function miss(e) {
        e.done = true; e.res = 'miss';
        S.combo = 0;
        award(0, null, true);
        judgeText('MISS', '#e0605a');
        DR.Sound.sfx('miss');
        $cb.innerHTML = '';
        meter(-0.09);
      }
      function press(m, at) {
        var t = at == null ? now() : at, best = null, bd = 1e9;
        evs.forEach(function (e) {
          if (e.done) return;
          var dt = t - e.t;
          if (Math.abs(dt) > OK) return;
          var k = exact ? m : mod(m, 12);
          if ((exact ? e.notes : e.pcs).indexOf(k) < 0 || e.hit[k] != null) return;
          if (Math.abs(dt) < bd) { bd = Math.abs(dt); best = e; }
        });
        if (!best) {
          kb.flash(m, 'bad', 180);
          S.combo = 0; S.streak = 0; stats(); $cb.innerHTML = '';
          meter(-0.03);
          return;
        }
        var key = exact ? m : mod(m, 12);
        best.hit[key] = t - best.t;
        var need = exact ? best.notes : best.pcs;
        if (need.every(function (k) { return best.hit[k] != null; })) {
          var worst = 0;
          need.forEach(function (k) { if (Math.abs(best.hit[k]) > Math.abs(worst)) worst = best.hit[k]; });
          judge(best, worst);
        }
      }
      function draw(t) {
        var w = cv.clientWidth, h = cv.clientHeight, dpr = Math.min(2, window.devicePixelRatio || 1);
        if (cv.width !== Math.round(w * dpr) || cv.height !== Math.round(h * dpr)) { cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr); }
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        ctx.clearRect(0, 0, w, h);
        var cvLeft = cv.getBoundingClientRect().left, hitY = h - 8, speed = (h - 20) / 2.3;
        // lanes
        var r = kb.range();
        for (var m = r[0]; m <= r[1]; m++) {
          if (M.isBlack(m)) continue;
          var kr = kb.keyRect(m), x = kr.x + kr.left - cvLeft;
          ctx.fillStyle = 'rgba(255,255,255,.018)';
          if (mod(m, 12) === 0) { ctx.fillStyle = 'rgba(226,178,90,.05)'; }
          ctx.fillRect(x + 1, 0, kr.w - 2, h);
          ctx.fillStyle = 'rgba(255,255,255,.035)'; ctx.fillRect(x, 0, 1, h);
        }
        // beat lines
        for (var b = Math.ceil((t - 0.3) / spb); b * spb < t + 2.4; b++) {
          var by = hitY - (b * spb - t) * speed;
          if (by < 0 || by > h) continue;
          ctx.fillStyle = (b - 4) % 4 === 0 && b >= 4 ? 'rgba(226,178,90,.16)' : 'rgba(255,255,255,.05)';
          ctx.fillRect(0, by, w, 1);
        }
        // hit line
        var hl = ctx.createLinearGradient(0, hitY - 14, 0, hitY + 6);
        hl.addColorStop(0, 'rgba(226,178,90,0)'); hl.addColorStop(1, 'rgba(226,178,90,.35)');
        ctx.fillStyle = hl; ctx.fillRect(0, hitY - 14, w, 20);
        ctx.fillStyle = '#e2b25a'; ctx.fillRect(0, hitY, w, 2);
        var lanes = [];
        evs.forEach(function (e) {
          var dt = e.t - t;
          if (dt > 2.5 || e.t + e.d - t < -0.6) return;
          if (e.done && e.res !== 'miss' && t - e.t > 0.35) return;
          if (!e.done && dt < 0.45 && dt > -OK) lanes = lanes.concat(e.notes);
          e.notes.forEach(function (n, j) {
            var kr = kb.keyRect(n), x = kr.x + kr.left - cvLeft, wd = kr.w;
            var yb = hitY - dt * speed, ht = Math.max(14, e.d * speed - 6), yt = yb - ht;
            var cols = trail(n), pad = kr.black ? 1 : 3;
            ctx.globalAlpha = e.res === 'miss' ? 0.25 : e.done ? Math.max(0, 1 - (t - e.t) / 0.35) : 1;
            var g = ctx.createLinearGradient(0, yt, 0, yb);
            g.addColorStop(0, cols[1]); g.addColorStop(1, cols[0]);
            ctx.fillStyle = g;
            ctx.shadowColor = cols[1]; ctx.shadowBlur = e.done ? 24 : 10;
            roundRect(ctx, x + pad, yt, wd - pad * 2, ht, 6); ctx.fill();
            ctx.shadowBlur = 0;
            ctx.fillStyle = 'rgba(255,255,255,.55)'; roundRect(ctx, x + pad + 2, yb - 5, wd - pad * 2 - 4, 3, 2); ctx.fill();
            if (e.label && j === 0) {
              ctx.globalAlpha = Math.min(ctx.globalAlpha, 1);
              ctx.font = '600 12px Inter, sans-serif'; ctx.textAlign = 'left';
              ctx.fillStyle = '#10131f';
              var txt = e.label, tx = x + pad + 4;
              if (e.notes.length === 1) { ctx.textAlign = 'center'; tx = x + wd / 2; }
              ctx.fillText(txt, tx, yb - 9);
            }
            ctx.globalAlpha = 1;
          });
        });
        var lk = lanes.sort().join(',');
        if (lk !== laneKey) { laneKey = lk; kb.unmark('lane'); kb.mark(lanes, 'lane'); }
      }
      function roundRect(c, x, y, w, h, r) {
        r = Math.min(r, w / 2, h / 2);
        c.beginPath(); c.moveTo(x + r, y); c.arcTo(x + w, y, x + w, y + h, r); c.arcTo(x + w, y + h, x, y + h, r); c.arcTo(x, y + h, x, y, r); c.arcTo(x, y, x + w, y, r); c.closePath();
      }
      function loop() {
        if (!alive) return;
        var t = now();
        if (pausedAt == null) {
          // metronome and count-in
          while (beat * spb < t + 0.12 && beat * spb <= lastEnd) {
            var bt = beat * spb, at = actx ? start + pausedFor + bt / scale : 0;
            if (beat < 4) {
              if (!dbg.auto) DR.Sound.click(actx && actx.state === 'running' ? at : undefined);
              (function (n) { setTimeout(function () { if (alive) { $n.textContent = n; $n.style.opacity = 1; } }, Math.max(0, (bt - t) * 1000 / scale)); })(4 - beat);
            } else if (beat === 4) {
              setTimeout(function () { if (alive) $n.textContent = ''; }, Math.max(0, (bt - t) * 1000 / scale));
              if (DR.settings.metronome && !dbg.auto) DR.Sound.clickSoft(actx && actx.state === 'running' ? at : undefined);
            } else if (DR.settings.metronome && !dbg.auto) DR.Sound.clickSoft(actx && actx.state === 'running' ? at : undefined);
            beat++;
          }
          if (dbg.auto) evs.forEach(function (e) { if (!e.done && e.t <= t) e.notes.forEach(function (n) { press(n, e.t); }); });
          evs.forEach(function (e) { if (!e.done && t > e.t + OK) miss(e); });
          if (S.over) return;
          if (evs.every(function (e) { return e.done; }) && t > lastEnd + 0.4) { alive = false; kb.unmark('lane'); stepDone(); return; }
        }
        draw(t);
        requestAnimationFrame(loop);
      }
      requestAnimationFrame(loop);
      return {
        on: function (m) { if (pausedAt == null) press(m); },
        pause: function () { if (pausedAt == null) pausedAt = raw(); },
        resume: function () { if (pausedAt != null) { pausedFor += raw() - pausedAt; pausedAt = null; } },
        destroy: function () { alive = false; kb.unmark('lane'); }
      };
    }

    /* ----- ear training ----- */
    function runEar(st) {
      var mode = st.mode || 'note', pool = st.pool || [], count = stepItems(st), q = 0, tries = 0, lastPick = null, answered = false, cur2 = null;
      head('ear', st.prompt);
      function pick() {
        var choices = pool.length > 1 ? pool.filter(function (p) { return p !== lastPick; }) : pool;
        var p = choices[Math.floor(Math.random() * choices.length)];
        lastPick = p;
        if (mode === 'note') return { answer: p, notes: [M.parseNote(p)], show: [M.parseNote(p)] };
        if (mode === 'chord') {
          var roots = ['C', 'D', 'E', 'F', 'G', 'A', 'Bb'], root = roots[Math.floor(Math.random() * roots.length)];
          var c = M.parseChord(root + (M.EAR_CHORDS[p] || ''));
          return { answer: p, chord: c.notes, show: c.notes, name: c.symbol };
        }
        var semi = (M.INTERVALS[p] || [7])[0], lo = 55 + Math.floor(Math.random() * 10);
        return { answer: p, pair: [lo, lo + semi], show: [lo, lo + semi] };
      }
      var all = mode === 'note' ? pool.map(M.parseNote) : mode === 'chord' ? [48, 76] : [55, 81];
      setRange(all, false);
      var opts = mode === 'note' ? '' : '<div class="opts">' + pool.map(function (p, i) {
        return '<button class="opt" data-o="' + esc(p) + '"><span class="n">' + (i + 1) + '</span>' + esc(mode === 'interval' ? (M.INTERVALS[p] || [0, p])[1] : p) + '</button>';
      }).join('') + '</div>';
      body.innerHTML = '<button class="ear-play" data-a="play" aria-label="Listen again">▶</button><div class="nt-tip v-q"></div>' + opts + '<div class="nt-big" style="font-size:40px;min-height:40px"></div><div class="nt-tip v-t"></div>';
      var $p = body.querySelector('.ear-play'), $q = body.querySelector('.v-q'), $b = body.querySelector('.nt-big'), $t = body.querySelector('.v-t');
      function play() {
        if (!cur2) return;
        var d;
        if (mode === 'note') d = DR.Sound.play(cur2.notes, { gap: 1, dur: 1.1 });
        else if (mode === 'chord') { d = DR.Sound.play([cur2.chord], { gap: 1.3, dur: 1.4, roll: true }); later(function () { DR.Sound.play(cur2.chord, { gap: 0.3, dur: 0.6 }); }, 1300); d += 1.2; }
        else d = DR.Sound.play([cur2.pair[0], cur2.pair[1], cur2.pair], { gap: 0.75, dur: 0.8 });
        $p.classList.add('on');
        later(function () { $p.classList.remove('on'); }, d * 1000);
      }
      function ask() {
        cur2 = pick(); tries = 0; answered = false;
        $q.textContent = 'Question ' + (q + 1) + ' of ' + count + (mode === 'note' ? ' · play the note you hear' : ' · choose the answer');
        $b.textContent = ''; $t.textContent = '';
        body.querySelectorAll('.opt').forEach(function (b) { b.className = 'opt'; b.disabled = false; });
        kb.unmark('target');
        later(play, 350);
      }
      function nextQ(ms) { q++; later(function () { if (q >= count) stepDone(); else ask(); }, ms); }
      function reveal() {
        if (mode === 'note') { $b.textContent = M.pretty(cur2.answer, true); var nm = {}; nm[cur2.notes[0]] = M.pretty(cur2.answer, true); kb.mark(cur2.notes, 'target', nm); }
        else $b.textContent = mode === 'chord' ? cur2.name : (M.INTERVALS[cur2.answer] || [0, ''])[1];
      }
      function choose(ans) {
        if (answered) return;
        answered = true;
        var right = ans === cur2.answer;
        body.querySelectorAll('.opt').forEach(function (b) {
          b.disabled = true;
          if (b.dataset.o === cur2.answer) b.classList.add('right');
          else if (b.dataset.o === ans) b.classList.add('wrong');
        });
        award(right ? 1 : 0, 'ear');
        if (right) DR.Sound.sfx('good'); else mistake();
        reveal();
        nextQ(right ? 900 : 1700);
      }
      function onClick(e) {
        var a = e.target.closest('[data-a="play"]'), b = e.target.closest('.opt');
        if (a) play();
        if (b && !b.disabled) choose(b.dataset.o);
      }
      body.addEventListener('click', onClick);
      ask();
      return {
        on: function (m) {
          if (mode !== 'note' || answered || !cur2) return;
          if (mod(m, 12) === mod(cur2.notes[0], 12)) {
            answered = true;
            kb.flash(m, 'ok');
            award(tries === 0 ? 1 : 0, 'ear');
            reveal();
            $t.textContent = tries === 0 ? 'Right!' : '';
            nextQ(900);
          } else {
            kb.flash(m, 'bad'); tries++; mistake();
            if (tries >= 2) { reveal(); $t.textContent = 'This is the note. Play it to go on.'; }
            else $t.textContent = 'Not quite. Listen again.';
          }
        },
        auto: function step() {
          if (S.over || q >= count) return;
          if (!answered && cur2) { if (mode === 'note') this.on(cur2.notes[0]); else choose(cur2.answer); }
          later(step.bind(this), 30);
        },
        destroy: function () { body.removeEventListener('click', onClick); }
      };
    }

    /* ----- quiz ----- */
    function runQuiz(st) {
      var opts = (st.options || []).map(function (t, i) { return { t: t, i: i }; }).filter(function (x) { return String(x.t).trim(); });
      for (var i = opts.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)), x = opts[i]; opts[i] = opts[j]; opts[j] = x; }
      var answered = false;
      head('quiz', '');
      body.innerHTML = '<div class="qz-q">' + esc(st.q) + '</div><div class="opts">' + opts.map(function (x, n) {
        return '<button class="opt" data-i="' + x.i + '"><span class="n">' + (n + 1) + '</span>' + esc(x.t) + '</button>';
      }).join('') + '</div><div class="qz-ex"></div><div class="ls-btns" style="display:flex;justify-content:center;min-height:42px"></div>';
      var $e = body.querySelector('.qz-ex'), $btns = body.querySelector('.ls-btns');
      function choose(idx) {
        if (answered) return;
        answered = true;
        var right = idx === (st.answer || 0);
        body.querySelectorAll('.opt').forEach(function (b) {
          b.disabled = true;
          if (+b.dataset.i === (st.answer || 0)) b.classList.add('right'); else if (+b.dataset.i === idx) b.classList.add('wrong');
        });
        award(right ? 1 : 0, 'quiz');
        if (right) DR.Sound.sfx('good'); else mistake();
        $e.innerHTML = (right ? '<b class="dr-gold-text">Correct.</b> ' : '<b style="color:var(--dr-red)">Not quite.</b> ') + esc(st.explain || '');
        $btns.innerHTML = '<button class="dr-btn gold" data-a="cont">Continue ▸</button>';
      }
      function onClick(e) {
        var b = e.target.closest('.opt'), c = e.target.closest('[data-a="cont"]');
        if (b && !b.disabled) choose(+b.dataset.i);
        if (c) stepDone();
      }
      function onKey(e) { if (e.key === 'Enter' && answered && !S.paused) { e.preventDefault(); stepDone(); } }
      body.addEventListener('click', onClick);
      window.addEventListener('keydown', onKey);
      return {
        auto: function () { choose(st.answer || 0); later(stepDone, 30); },
        destroy: function () { body.removeEventListener('click', onClick); window.removeEventListener('keydown', onKey); }
      };
    }

    var RUNNERS = { lesson: runLesson, notes: runNotes, chords: function (s) { return runChords(s, false); },
      progression: function (s) { return runChords(s, true); }, rush: runRush, ear: runEar, quiz: runQuiz };

    root.querySelector('[data-a="pause"]').addEventListener('click', function () { if (o.onPause) o.onPause(); });
    var api = {
      start: function () { S.t0 = performance.now(); next(); },
      pause: function () { S.paused = true; if (cur && cur.pause) cur.pause(); DR.Input.releaseAll(); },
      resume: function () { S.paused = false; if (cur && cur.resume) cur.resume(); },
      isPaused: function () { return S.paused; },
      destroy: function () {
        S.over = true;
        timers.forEach(clearTimeout);
        if (cur && cur.destroy) cur.destroy();
        offIn();
        release();
        kb.destroy();
        root.innerHTML = '';
      },
      skip: function () { if (cur && !S.over) { if (cur.destroy) cur.destroy(); cur = null; clearKb(); next(); } },
      state: function () { return { step: S.i, steps: steps.length, hits: S.hits, judged: S.judged, items: totalItems, score: S.score, combo: S.combo, meter: S.meter, over: S.over }; },
      keyboard: kb
    };
    return api;
  }
  Stage.debug = { auto: false, timeScale: 1 };

  DR.Keyboard = Keyboard;
  DR.Stage = Stage;
  DR.Engine = { rangeFor: rangeFor, stepItems: stepItems, levelItems: levelItems, TRAILS: TRAILS };
})();
