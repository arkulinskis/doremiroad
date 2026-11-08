/* Doremi Road — everything drawn (DR.Art): the knowledge map, music staves, crests, composer medallions,
   step icons and the title screen's night road. All SVG strings or canvas; no image files. */
(function () {
  'use strict';
  var DR = window.DR = window.DR || {};
  var esc = function (s) { return DR.esc(s); };

  function rng(seedText) {
    var h = 2166136261;
    for (var i = 0; i < seedText.length; i++) { h ^= seedText.charCodeAt(i); h = Math.imul(h, 16777619); }
    return function () { h ^= h << 13; h ^= h >>> 17; h ^= h << 5; return ((h >>> 0) % 100000) / 100000; };
  }
  function hexToRgb(h) { var n = parseInt(h.slice(1), 16); return [n >> 16 & 255, n >> 8 & 255, n & 255]; }
  function mix(a, b, t) {
    var x = hexToRgb(a), y = hexToRgb(b);
    return 'rgb(' + [0, 1, 2].map(function (i) { return Math.round(x[i] + (y[i] - x[i]) * t); }).join(',') + ')';
  }
  // A closed smooth path through points (Catmull-Rom → cubic Bézier).
  function smoothPath(pts) {
    var n = pts.length, d = 'M' + pts[0][0].toFixed(1) + ',' + pts[0][1].toFixed(1);
    for (var i = 0; i < n; i++) {
      var p0 = pts[(i - 1 + n) % n], p1 = pts[i], p2 = pts[(i + 1) % n], p3 = pts[(i + 2) % n];
      var c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6], c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
      d += 'C' + c1[0].toFixed(1) + ',' + c1[1].toFixed(1) + ' ' + c2[0].toFixed(1) + ',' + c2[1].toFixed(1) + ' ' + p2[0].toFixed(1) + ',' + p2[1].toFixed(1);
    }
    return d + 'Z';
  }
  function blob(cx, cy, r, key, wobble) {
    var R = rng('blob:' + key), pts = [], n = 16;
    var phase = R() * Math.PI * 2;
    for (var i = 0; i < n; i++) {
      var a = phase + i / n * Math.PI * 2;
      var rr = r * (0.8 + (wobble || 0.32) * (R() - 0.35)) * (1 + 0.1 * Math.sin(a * 3 + phase));
      pts.push([cx + Math.cos(a) * rr * 1.18, cy + Math.sin(a) * rr * 0.92]);
    }
    return smoothPath(pts);
  }

  /* ---------- the knowledge map ----------
     DR.Art.map(territories, opts) → SVG string.
     territories: [{key, name, emoji, color, x, y, levels: [{key, ...}]}]
     opts: {cleared: {levelKey: stars}, unlocked: [levelKeys], conquered: [keys], mastered: [keys], banner: '#hex',
            current: territory key, selected: territory key} */
  var W = 1000, H = 680;
  function mapPos(t) { return [t.x / 100 * W, t.y / 100 * H]; }
  function roadPath(pts) {
    if (pts.length < 2) return '';
    var d = 'M' + pts[0][0].toFixed(1) + ',' + pts[0][1].toFixed(1);
    for (var i = 0; i < pts.length - 1; i++) {
      var p0 = pts[Math.max(0, i - 1)], p1 = pts[i], p2 = pts[i + 1], p3 = pts[Math.min(pts.length - 1, i + 2)];
      var c1 = [p1[0] + (p2[0] - p0[0]) / 5, p1[1] + (p2[1] - p0[1]) / 5], c2 = [p2[0] - (p3[0] - p1[0]) / 5, p2[1] - (p3[1] - p1[1]) / 5];
      d += 'C' + c1[0].toFixed(1) + ',' + c1[1].toFixed(1) + ' ' + c2[0].toFixed(1) + ',' + c2[1].toFixed(1) + ' ' + p2[0].toFixed(1) + ',' + p2[1].toFixed(1);
    }
    return d;
  }
  function compass(x, y, r) {
    var s = '<g transform="translate(' + x + ',' + y + ')" opacity=".55">';
    s += '<circle r="' + r + '" fill="none" stroke="rgba(232,212,168,.35)" stroke-width="1"/>';
    s += '<circle r="' + (r * 0.78) + '" fill="none" stroke="rgba(232,212,168,.2)" stroke-width="1" stroke-dasharray="2 4"/>';
    [0, 90, 180, 270].forEach(function (a, i) {
      s += '<path transform="rotate(' + a + ')" d="M0,' + (-r * 1.05) + ' L' + (r * 0.16) + ',0 L0,' + (r * 0.16) + ' L' + (-r * 0.16) + ',0Z" fill="' + (i === 0 ? '#e2b25a' : 'rgba(232,212,168,.5)') + '"/>';
    });
    [45, 135, 225, 315].forEach(function (a) { s += '<path transform="rotate(' + a + ')" d="M0,' + (-r * 0.62) + ' L' + (r * 0.09) + ',0 L' + (-r * 0.09) + ',0Z" fill="rgba(232,212,168,.35)"/>'; });
    s += '<text y="' + (-r * 1.2) + '" text-anchor="middle" font-family="Cinzel, serif" font-size="13" fill="#e2b25a">N</text></g>';
    return s;
  }
  function mapSVG(ts, o) {
    o = o || {};
    var cleared = o.cleared || {}, unlocked = o.unlocked || [], conquered = o.conquered || [], mastered = o.mastered || [];
    var banner = o.banner || '#c8434e';
    var R = rng('sea');
    var s = '<svg class="dr-map-svg" viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg">';
    s += '<defs>' +
      '<radialGradient id="mSea" cx="50%" cy="45%" r="75%"><stop offset="0" stop-color="#18213d"/><stop offset=".7" stop-color="#0f152a"/><stop offset="1" stop-color="#090c18"/></radialGradient>' +
      '<pattern id="mHatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><line x1="0" y1="0" x2="0" y2="7" stroke="rgba(232,212,168,.07)" stroke-width="2"/></pattern>' +
      '<filter id="mGlow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>' +
      '<filter id="mSoft"><feGaussianBlur stdDeviation="2.2"/></filter>' +
      '</defs>';
    s += '<rect width="' + W + '" height="' + H + '" fill="url(#mSea)"/>';
    // graticule
    for (var gx = 1; gx < 10; gx++) s += '<line x1="' + gx * 100 + '" y1="0" x2="' + gx * 100 + '" y2="' + H + '" stroke="rgba(232,212,168,.035)"/>';
    for (var gy = 1; gy < 7; gy++) s += '<line x1="0" y1="' + gy * 100 + '" x2="' + W + '" y2="' + gy * 100 + '" stroke="rgba(232,212,168,.035)"/>';
    // waves
    for (var wv = 0; wv < 34; wv++) {
      var wx = R() * W, wy = R() * H;
      s += '<path d="M' + wx.toFixed(0) + ',' + wy.toFixed(0) + ' q6,-5 12,0 t12,0" fill="none" stroke="rgba(150,175,230,.09)" stroke-width="1.4"/>';
    }
    s += compass(W - 70, H - 78, 34);
    // cartouche
    s += '<g transform="translate(26,26)"><rect width="250" height="58" rx="6" fill="rgba(12,16,32,.65)" stroke="rgba(226,178,90,.45)"/>' +
      '<rect x="4" y="4" width="242" height="50" rx="4" fill="none" stroke="rgba(226,178,90,.2)"/>' +
      '<text x="125" y="27" text-anchor="middle" font-family="Cinzel, serif" font-size="17" font-weight="600" fill="#e2b25a" letter-spacing="2">THE REALM OF HARMONY</text>' +
      '<text x="125" y="45" text-anchor="middle" font-family="Cormorant Garamond, serif" font-style="italic" font-size="14" fill="rgba(240,231,211,.7)">a map of musical knowledge</text></g>';

    var pts = ts.map(mapPos);
    // the road: travelled part brighter
    var curIdx = Math.max(0, ts.findIndex(function (t) { return t.key === o.current; }));
    var road = roadPath(pts);
    if (road) {
      s += '<path d="' + road + '" fill="none" stroke="rgba(0,0,0,.45)" stroke-width="9" stroke-linecap="round"/>';
      s += '<path d="' + road + '" fill="none" stroke="rgba(226,178,90,.28)" stroke-width="4" stroke-dasharray="2 9" stroke-linecap="round"/>';
      var done = roadPath(pts.slice(0, curIdx + 1));
      if (done) s += '<path class="m-road-done" d="' + done + '" fill="none" stroke="#e2b25a" stroke-width="3.2" stroke-dasharray="10 7" stroke-linecap="round"/>';
    }
    ts.forEach(function (t, i) {
      var p = pts[i], r = 74, keys = t.levels.map(function (l) { return l.key; });
      var isOpen = keys.some(function (k) { return unlocked.indexOf(k) >= 0; });
      var isConq = conquered.indexOf(t.key) >= 0, isMast = mastered.indexOf(t.key) >= 0;
      var path = blob(p[0], p[1], r, t.key);
      var clipId = 'mc-' + i;
      var base = isOpen ? mix(t.color, '#121830', 0.48) : '#1c2240';
      s += '<g class="m-terr' + (isOpen ? ' open' : ' locked') + (o.selected === t.key ? ' sel' : '') + '" data-t="' + esc(t.key) + '" tabindex="0" role="button" aria-label="' + esc(t.name) + '">';
      s += '<clipPath id="' + clipId + '"><path d="' + path + '"/></clipPath>';
      s += '<path d="' + path + '" fill="rgba(0,0,0,.5)" transform="translate(5,8)" filter="url(#mSoft)"/>';
      if (isConq) s += '<path d="' + path + '" fill="' + banner + '" opacity=".35" filter="url(#mGlow)"/>';
      s += '<path class="m-land" d="' + path + '" fill="' + base + '"/>';
      // provinces: one wedge per level, filled with your banner colour once cleared
      var n = Math.max(1, keys.length), R2 = rng('prov:' + t.key), a0 = R2() * Math.PI * 2;
      s += '<g clip-path="url(#' + clipId + ')">';
      keys.forEach(function (k, j) {
        var a1 = a0 + j / n * Math.PI * 2, a2 = a0 + (j + 1) / n * Math.PI * 2, rr = r * 2;
        var wedge = 'M' + p[0] + ',' + p[1] + ' L' + (p[0] + Math.cos(a1) * rr).toFixed(1) + ',' + (p[1] + Math.sin(a1) * rr).toFixed(1) +
          ' A' + rr + ',' + rr + ' 0 0,1 ' + (p[0] + Math.cos(a2) * rr).toFixed(1) + ',' + (p[1] + Math.sin(a2) * rr).toFixed(1) + 'Z';
        var st = cleared[k] || 0;
        if (st) s += '<path d="' + wedge + '" fill="' + banner + '" opacity="' + (0.38 + 0.12 * st) + '"/>';
        if (n > 1) s += '<line x1="' + p[0] + '" y1="' + p[1] + '" x2="' + (p[0] + Math.cos(a1) * rr).toFixed(1) + '" y2="' + (p[1] + Math.sin(a1) * rr).toFixed(1) + '" stroke="rgba(10,12,24,.5)" stroke-width="1.2" stroke-dasharray="3 3"/>';
      });
      if (!isOpen) s += '<rect x="' + (p[0] - 120) + '" y="' + (p[1] - 100) + '" width="240" height="200" fill="url(#mHatch)"/>';
      // texture
      for (var k2 = 0; k2 < 7; k2++) {
        var tx = p[0] + (R2() - 0.5) * r * 1.6, ty = p[1] + (R2() - 0.5) * r * 1.2;
        s += '<path d="M' + tx.toFixed(0) + ',' + ty.toFixed(0) + ' l5,-8 l5,8" fill="none" stroke="rgba(255,255,255,' + (isOpen ? '.10' : '.04') + ')" stroke-width="1.3"/>';
      }
      s += '</g>';
      s += '<path class="m-coast" d="' + path + '" fill="none" stroke="' + (isMast ? '#e2b25a' : isOpen ? 'rgba(232,212,168,.55)' : 'rgba(232,212,168,.16)') + '" stroke-width="' + (isMast ? 2.6 : 1.5) + '"/>';
      s += '<path d="' + path + '" fill="none" stroke="rgba(232,212,168,.08)" stroke-width="7" transform="translate(0,0)"/>';
      // emblem
      var doneN = keys.filter(function (k) { return cleared[k]; }).length;
      s += '<g class="m-emb" transform="translate(' + p[0] + ',' + (p[1] - 6) + ')">';
      s += '<circle r="25" fill="rgba(10,13,26,.78)" stroke="' + (isConq ? banner : 'rgba(232,212,168,.4)') + '" stroke-width="' + (isConq ? 2.5 : 1.2) + '"/>';
      s += '<text y="9" text-anchor="middle" font-size="24" font-family="Segoe UI Emoji, Apple Color Emoji, Noto Color Emoji, sans-serif"' + (isOpen ? '' : ' opacity=".35"') + '>' + esc(t.emoji) + '</text>';
      if (!isOpen) s += '<g transform="translate(15,13)"><circle r="9" fill="#0c1020" stroke="rgba(232,212,168,.4)"/><path d="M-3.5,-1 v-2.5 a3.5,3.5 0 0,1 7,0 v2.5" fill="none" stroke="rgba(232,212,168,.7)" stroke-width="1.4"/><rect x="-4.5" y="-1" width="9" height="6.5" rx="1.2" fill="rgba(232,212,168,.7)"/></g>';
      s += '</g>';
      if (isConq) {
        s += '<g transform="translate(' + (p[0] + 20) + ',' + (p[1] - 58) + ')"><line x1="0" y1="0" x2="0" y2="30" stroke="#e8d9b8" stroke-width="2"/>' +
          '<path d="M1,1 h20 l-5,6 l5,6 h-20z" fill="' + banner + '" stroke="rgba(0,0,0,.4)"/>' + (isMast ? '<text x="9" y="11" font-size="9" text-anchor="middle" fill="#fff3cf">★</text>' : '') + '</g>';
      }
      s += '<text class="m-name" x="' + p[0] + '" y="' + (p[1] + 40) + '" text-anchor="middle" font-family="Cinzel, serif" font-weight="600" font-size="14.5" letter-spacing="1.2" fill="' + (isOpen ? '#f0e7d3' : 'rgba(240,231,211,.4)') + '" stroke="rgba(8,10,20,.85)" stroke-width="3.5" paint-order="stroke">' + esc(t.name.toUpperCase()) + '</text>';
      s += '<text x="' + p[0] + '" y="' + (p[1] + 56) + '" text-anchor="middle" font-family="Inter, sans-serif" font-size="11" font-weight="600" fill="' + (isConq ? '#e2b25a' : 'rgba(240,231,211,.55)') + '" stroke="rgba(8,10,20,.8)" stroke-width="3" paint-order="stroke">' +
        (isOpen ? doneN + ' / ' + keys.length + ' provinces' : 'locked') + '</text>';
      s += '</g>';
    });
    // you are here
    if (pts[curIdx]) {
      var cp = pts[curIdx];
      s += '<g class="m-you" transform="translate(' + (cp[0] - 30) + ',' + (cp[1] - 48) + ')"><circle r="16" fill="#e2b25a" opacity=".25" class="m-pulse"/>' +
        '<path d="M0,10 C-9,-2 -9,-14 0,-14 C9,-14 9,-2 0,10Z" fill="#e2b25a" stroke="#1d160a" stroke-width="1.5"/>' +
        '<text y="-3" text-anchor="middle" font-size="11" font-weight="700" fill="#1d160a">♪</text></g>';
    }
    return s + '</svg>';
  }

  /* ---------- a music staff ----------
     DR.Art.staff(notes, {clef, current, done, wrong, w, names, scale}) → SVG string.
     notes: ['C4', 'E4', ...] (a '+' joins notes into one chord). done: how many are finished. */
  function staff(notes, o) {
    o = o || {};
    var clef = o.clef || 'treble', gap = 10, lineTop = 46, bottomY = lineTop + 4 * gap;
    var lead = 66, step = o.step || 50, n = notes.length;
    var width = o.w || Math.max(260, lead + n * step + 30);
    var height = 150;
    var col = function (i) { return i < (o.done || 0) ? '#6fc79a' : i === o.current ? '#e2b25a' : '#f0e7d3'; };
    var s = '<svg class="dr-staff" viewBox="0 0 ' + width + ' ' + height + '" width="' + width * (o.scale || 1) + '" height="' + height * (o.scale || 1) + '" xmlns="http://www.w3.org/2000/svg">';
    for (var l = 0; l < 5; l++) s += '<line x1="8" x2="' + (width - 8) + '" y1="' + (lineTop + l * gap) + '" y2="' + (lineTop + l * gap) + '" stroke="rgba(240,231,211,.75)" stroke-width="1.2"/>';
    s += '<line x1="8" x2="8" y1="' + lineTop + '" y2="' + bottomY + '" stroke="rgba(240,231,211,.75)" stroke-width="1.2"/>';
    s += '<line x1="' + (width - 8) + '" x2="' + (width - 8) + '" y1="' + lineTop + '" y2="' + bottomY + '" stroke="rgba(240,231,211,.75)" stroke-width="2"/>';
    if (clef === 'bass') s += '<text x="14" y="' + (lineTop + gap * 3.05) + '" font-family="Noto Music, Segoe UI Symbol, serif" font-size="' + (gap * 3.9) + '" fill="#f0e7d3">𝄢</text>';
    else s += '<text x="12" y="' + (lineTop + gap * 3.6) + '" font-family="Noto Music, Segoe UI Symbol, serif" font-size="' + (gap * 4.5) + '" fill="#f0e7d3">𝄞</text>';
    notes.forEach(function (item, i) {
      var x = lead + i * step + step / 2;
      var group = String(item).split('+');
      var c = col(i);
      var ps = group.map(function (nn) { return DR.Music.staffPos(nn, clef); }).filter(Boolean);
      if (!ps.length) return;
      var lo = Math.min.apply(null, ps.map(function (p) { return p.pos; })), hi = Math.max.apply(null, ps.map(function (p) { return p.pos; }));
      // ledger lines
      for (var q = -2; q >= lo; q -= 2) s += '<line x1="' + (x - 12) + '" x2="' + (x + 12) + '" y1="' + (bottomY - q * gap / 2) + '" y2="' + (bottomY - q * gap / 2) + '" stroke="rgba(240,231,211,.75)" stroke-width="1.2"/>';
      for (var q2 = 10; q2 <= hi; q2 += 2) s += '<line x1="' + (x - 12) + '" x2="' + (x + 12) + '" y1="' + (bottomY - q2 * gap / 2) + '" y2="' + (bottomY - q2 * gap / 2) + '" stroke="rgba(240,231,211,.75)" stroke-width="1.2"/>';
      if (i === o.current) s += '<rect x="' + (x - step / 2 + 4) + '" y="10" width="' + (step - 8) + '" height="' + (height - 20) + '" rx="8" fill="rgba(226,178,90,.09)" stroke="rgba(226,178,90,.3)"/>';
      ps.forEach(function (p) {
        var y = bottomY - p.pos * gap / 2;
        if (p.acc) s += '<text x="' + (x - 20) + '" y="' + (y + 5) + '" font-family="Noto Music, Segoe UI Symbol, serif" font-size="17" text-anchor="middle" fill="' + c + '">' + p.acc + '</text>';
        s += '<ellipse cx="' + x + '" cy="' + y + '" rx="6.4" ry="4.7" transform="rotate(-20 ' + x + ' ' + y + ')" fill="' + c + '"/>';
      });
      var mid = (lo + hi) / 2, up = mid < 4;
      var yLo = bottomY - lo * gap / 2, yHi = bottomY - hi * gap / 2;
      if (up) s += '<line x1="' + (x + 5.8) + '" x2="' + (x + 5.8) + '" y1="' + yLo + '" y2="' + (yHi - 34) + '" stroke="' + c + '" stroke-width="1.4"/>';
      else s += '<line x1="' + (x - 5.8) + '" x2="' + (x - 5.8) + '" y1="' + yHi + '" y2="' + (yLo + 34) + '" stroke="' + c + '" stroke-width="1.4"/>';
      if (o.names && (o.names === true || i < (o.done || 0))) {
        s += '<text x="' + x + '" y="' + (height - 6) + '" text-anchor="middle" font-family="Inter, sans-serif" font-size="11" font-weight="600" fill="' + c + '">' + esc(group.map(function (g) { return DR.Music.pretty(g, true); }).join(' ')) + '</text>';
      }
    });
    return s + '</svg>';
  }

  /* ---------- crests, medallions, icons ---------- */
  function crest(t, state, size) {
    size = size || 64;
    var won = state !== 'locked' && state !== 'open', gold = state === 'mastered';
    var fill = won ? mix(t.color, '#121830', 0.25) : '#1a2038';
    var s = '<svg width="' + size + '" height="' + size * 1.15 + '" viewBox="0 0 64 74" xmlns="http://www.w3.org/2000/svg">';
    s += '<path d="M32,3 L58,11 V36 C58,54 44,66 32,71 C20,66 6,54 6,36 V11Z" fill="' + fill + '" stroke="' + (gold ? '#e2b25a' : won ? 'rgba(232,212,168,.7)' : 'rgba(232,212,168,.2)') + '" stroke-width="' + (gold ? 3 : 1.5) + '"/>';
    s += '<path d="M32,9 L52,15 V36 C52,50 41,60 32,64 C23,60 12,50 12,36 V15Z" fill="none" stroke="rgba(255,255,255,' + (won ? '.18' : '.05') + ')"/>';
    s += '<text x="32" y="44" text-anchor="middle" font-size="24" font-family="Segoe UI Emoji, Apple Color Emoji, Noto Color Emoji, sans-serif"' + (won ? '' : ' opacity=".25"') + '>' + esc(t.emoji) + '</text>';
    if (gold) s += '<text x="32" y="17" text-anchor="middle" font-size="10" fill="#e2b25a">★</text>';
    return s + '</svg>';
  }
  var RARITY_COL = { common: '#b98f62', rare: '#a9b7cc', epic: '#e2b25a', legendary: '#d98ce0' };
  function medallion(c, owned, size) {
    size = size || 96;
    var col = RARITY_COL[c.rarity] || '#b98f62';
    var initials = c.name.split(' ').filter(function (w) { return /^[A-ZÀ-Þ]/.test(w) && w !== 'van'; });
    initials = (initials[0] || '?').charAt(0) + (initials.length > 1 ? initials[initials.length - 1].charAt(0) : '');
    var R = rng('med:' + c.key), s = '<svg width="' + size + '" height="' + size + '" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">';
    s += '<defs><radialGradient id="md' + c.key + '" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="' + (owned ? mix(col, '#ffffff', 0.25) : '#2a3150') + '"/><stop offset="1" stop-color="' + (owned ? mix(col, '#121830', 0.55) : '#151a30') + '"/></radialGradient></defs>';
    s += '<circle cx="50" cy="50" r="46" fill="url(#md' + c.key + ')" stroke="' + (owned ? col : 'rgba(232,212,168,.2)') + '" stroke-width="2.5"/>';
    // laurel
    for (var i = 0; i < 9; i++) {
      [-1, 1].forEach(function (side) {
        var a = (200 + i * 15) * Math.PI / 180, x = 50 + side * Math.cos(a) * 37, y = 52 - Math.sin(a) * 37;
        s += '<ellipse cx="' + x.toFixed(1) + '" cy="' + y.toFixed(1) + '" rx="2.2" ry="5.5" transform="rotate(' + (side * (i * 15 - 20)) + ' ' + x.toFixed(1) + ' ' + y.toFixed(1) + ')" fill="' + (owned ? 'rgba(255,255,255,.35)' : 'rgba(232,212,168,.08)') + '"/>';
      });
    }
    s += '<circle cx="50" cy="50" r="30" fill="rgba(10,12,24,' + (owned ? '.35' : '.5') + ')" stroke="rgba(255,255,255,.15)"/>';
    s += '<text x="50" y="60" text-anchor="middle" font-family="Cormorant Garamond, serif" font-weight="700" font-size="28" fill="' + (owned ? '#fff7e4' : 'rgba(240,231,211,.25)') + '">' + (owned ? esc(initials) : '?') + '</text>';
    if (owned) for (var k = 0; k < 4; k++) s += '<text x="' + (20 + R() * 60).toFixed(0) + '" y="' + (16 + R() * 10).toFixed(0) + '" font-size="8" fill="rgba(255,255,255,.4)">♪</text>';
    return s + '</svg>';
  }
  var STEP_ICONS = { lesson: '📖', notes: '🎹', chords: '🎼', progression: '🧭', rush: '⚡', ear: '👂', quiz: '❓' };
  var STEP_NAMES = { lesson: 'Lesson', notes: 'Notes', chords: 'Chords', progression: 'Progression', rush: 'Rush', ear: 'Ear training', quiz: 'Theory quiz' };

  /* ---------- the title screen: a road of light under the stars ---------- */
  function titleScene(cv) {
    var ctx = cv.getContext('2d'), stars = [], notes = [], alive = true, t0 = performance.now();
    var R = rng('title');
    for (var i = 0; i < 140; i++) stars.push([R(), R() * 0.62, R() * 1.4 + 0.3, R() * 6]);
    var GLYPHS = ['♪', '♫', '♩', '♬'];
    function frame(now) {
      if (!alive) return;
      var w = cv.clientWidth, h = cv.clientHeight, dpr = Math.min(2, window.devicePixelRatio || 1);
      if (cv.width !== Math.round(w * dpr)) { cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr); }
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      var t = (now - t0) / 1000;
      var g = ctx.createLinearGradient(0, 0, 0, h);
      g.addColorStop(0, '#070a16'); g.addColorStop(0.55, '#121a36'); g.addColorStop(1, '#1c1730');
      ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
      stars.forEach(function (s) {
        ctx.globalAlpha = 0.35 + 0.35 * Math.sin(t * 1.3 + s[3]);
        ctx.fillStyle = '#f5ecd6'; ctx.beginPath(); ctx.arc(s[0] * w, s[1] * h, s[2] * 0.8, 0, 7); ctx.fill();
      });
      ctx.globalAlpha = 1;
      // horizon glow
      var hy = h * 0.6, vx = w * 0.5;
      var hg = ctx.createRadialGradient(vx, hy, 0, vx, hy, w * 0.55);
      hg.addColorStop(0, 'rgba(226,178,90,.32)'); hg.addColorStop(1, 'rgba(226,178,90,0)');
      ctx.fillStyle = hg; ctx.fillRect(0, 0, w, h);
      // hills
      ctx.fillStyle = '#0b0f20';
      ctx.beginPath(); ctx.moveTo(0, hy);
      for (var x = 0; x <= w; x += 20) ctx.lineTo(x, hy - 18 - 22 * Math.sin(x / w * 7 + 1) - 12 * Math.sin(x / w * 17));
      ctx.lineTo(w, h); ctx.lineTo(0, h); ctx.fill();
      // the road: five staff lines converging on the horizon
      for (var l = 0; l < 5; l++) {
        var off = (l - 2) / 2;
        ctx.strokeStyle = 'rgba(226,178,90,' + (0.5 - Math.abs(off) * 0.12) + ')'; ctx.lineWidth = 1.4;
        ctx.beginPath(); ctx.moveTo(vx + off * 4, hy); ctx.lineTo(vx + off * w * 0.32, h); ctx.stroke();
      }
      // bar lines scrolling towards you
      for (var b = 0; b < 8; b++) {
        var z = ((b / 8) + t * 0.08) % 1, y = hy + Math.pow(z, 2.2) * (h - hy), half = 4 + Math.pow(z, 2.2) * w * 0.32;
        ctx.strokeStyle = 'rgba(226,178,90,' + (0.15 * z + 0.04) + ')'; ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(vx - half, y); ctx.lineTo(vx + half, y); ctx.stroke();
      }
      // notes drifting along the road
      if (notes.length < 16 && Math.random() < 0.05) notes.push({ z: 0, lane: (Math.random() - 0.5) * 1.6, g: GLYPHS[Math.floor(Math.random() * 4)], bob: Math.random() * 6 });
      notes = notes.filter(function (n) { return n.z < 1.05; });
      notes.forEach(function (n) {
        n.z += 0.0022;
        var e = Math.pow(n.z, 2.2), y = hy + e * (h - hy) - 30 * e - Math.sin(t * 2 + n.bob) * 4 * e, x = vx + n.lane * (4 + e * w * 0.32) / 2;
        ctx.globalAlpha = Math.min(1, n.z * 3) * (1 - Math.max(0, n.z - 0.85) * 6);
        ctx.fillStyle = '#f3cf86'; ctx.shadowColor = 'rgba(226,178,90,.9)'; ctx.shadowBlur = 12;
        ctx.font = (10 + e * 46).toFixed(0) + 'px "Cormorant Garamond", serif';
        ctx.textAlign = 'center'; ctx.fillText(n.g, x, y);
        ctx.shadowBlur = 0;
      });
      ctx.globalAlpha = 1;
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
    return { stop: function () { alive = false; } };
  }

  DR.Art = { map: mapSVG, staff: staff, crest: crest, medallion: medallion, titleScene: titleScene, rng: rng, mix: mix,
    STEP_ICONS: STEP_ICONS, STEP_NAMES: STEP_NAMES, RARITY_COL: RARITY_COL };
})();
