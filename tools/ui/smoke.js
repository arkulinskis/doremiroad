/* Smoke test (tools/ui_test.py runs it at 1280 px and at 390 px): every page address opens without errors, is not
   empty and doesn't scroll sideways, signed out (a guest on the road), then as a new member, then as admin (every
   editor tab, a level open in the editor). The level engine starts on #play/<level> and #play/daily. Python/JS errors
   are also caught by ui_test.py from the browser log. Resolves to {ok, log}. */
(async function () {
  const log = [], bad = [];
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  async function until(fn, what, ms) {
    const end = Date.now() + (ms || 20000);
    while (Date.now() < end) { try { const v = fn(); if (v) return v; } catch (e) {} await sleep(150); }
    throw new Error('timed out waiting for: ' + what);
  }
  const $ = (s) => document.querySelector(s), $$ = (s) => Array.from(document.querySelectorAll(s));
  const errs = [];
  window.addEventListener('error', (e) => errs.push(String(e.message || e)));
  function type(input, value) {
    input.focus(); input.value = value;
    input.dispatchEvent(new Event('input', { bubbles: true })); input.dispatchEvent(new Event('change', { bubbles: true }));
  }
  function button(re, root) { return $$((root || '') + ' button').find((b) => re.test(b.textContent) && b.offsetParent !== null); }
  async function open(hash, expect, check) {
    if (location.hash !== hash) window.UI_READY = false;
    location.hash = hash;
    await until(() => window.UI_READY && location.hash === hash, hash, 30000);
    await sleep(900);
    const main = $('.ui-main');
    const text = main ? main.innerText.trim() : '';
    const w = document.documentElement.scrollWidth, vw = screen.width <= 500 ? screen.width : window.innerWidth;
    const problems = [];
    if (text.length < 40) problems.push('empty page');
    if (expect && !new RegExp(expect.source, 'i').test(text)) problems.push('missing ' + expect);
    if (w > vw + 1) {
      const wide = $$('body *').filter((e) => { const r = e.getBoundingClientRect(); return r.width && r.right > vw + 1; })
        .slice(0, 3).map((e) => e.tagName.toLowerCase() + '.' + String(e.className).split(' ').slice(0, 2).join('.'));
      problems.push('scrolls sideways (' + w + ' > ' + vw + ') ' + wide.join(' '));
    }
    if (check) { const c = check(); if (c) problems.push(c); }
    if (errs.length) problems.push('errors: ' + errs.splice(0).join(' / '));
    if (problems.length) bad.push(hash + ': ' + problems.join('; '));
    log.push((problems.length ? 'BAD  ' : 'ok   ') + hash);
  }
  async function closeDialog() {
    const x = $$('.anvil-modal .anvil-close, .modal .close, [data-dismiss="modal"]').find((b) => b.offsetParent !== null);
    if (x) x.click(); else document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
    await until(() => !$$('.anvil-modal-content, .modal-content').some((m) => m.offsetParent !== null), 'dialog closed', 8000).catch(() => {});
    await sleep(400);
  }
  async function road(who) {
    await open('#map', /Daily Practice/, () => (!$('.dr-map-svg') ? 'no map drawn' : !$$('.m-lv').length ? 'no levels listed' : ''));
    const lv = $$('.m-lv.open, .m-lv.done')[0];
    if (lv) {
      lv.click();
      await until(() => $$('.lv-card').some((c) => /Leaderboard/.test(c.innerText)), 'the level card', 15000);
      await sleep(800);
      log.push('ok   ' + who + ' level card opens');
      await closeDialog();
    } else bad.push(who + ': no open level on the map');
    button(/^(Start|Replay)$/, '.m-daily').click();
    await until(() => $$('.lv-card').some((c) => /Daily Practice/.test(c.innerText)), 'the daily card', 15000);
    log.push('ok   ' + who + ' daily card opens');
    await closeDialog();
    await open('#codex', /The Codex/, () => ($$('.cx').length < 10 ? 'codex tiles missing' : ''));
    await open('#collection', /Composer cards/, () => ($$('.cd svg').length < 5 ? 'medallions missing' : ''));
    await open('#practice', /You are playing/, () => (!$('.pr-kb .kb .k') ? 'no keyboard' : ''));
    await open('#badges', /earned/, () => ($$('.bd').length < 10 ? 'badges missing' : ''));
    await open('#shop', /ducats/, () => ($$('.sh').length < 5 ? 'shop items missing' : ''));
    await open('#play/ivory-1', /Score/, () => (!$('.st .st-prompt') ? 'the level engine did not start' : ''));
    await open('#play/daily', /Daily Practice/, () => (!$('.st .st-kb .k') ? 'the daily level did not start' : ''));
  }
  async function signUp(name, email, password) {
    location.hash = '#auth/signup';
    await until(() => window.UI_READY && $$('.au-card input').length >= 3, 'sign-up form');
    await sleep(400);
    const inputs = $$('.au-card input[type=text], .au-card input[type=email], .au-card input[type=password]');
    type(inputs[0], name); type(inputs[1], email); type(inputs[2], password);
    const tick = $('.au-card input[type=checkbox]'); if (tick && !tick.checked) tick.click();
    button(/Create account/, '.au-card .anvil-role-btn-block').click();
    const end = Date.now() + 30000;
    while (Date.now() < end) {
      if (location.hash.indexOf('#map') === 0 && window.UI_READY) return true;
      const msg = $('.au-card .anvil-role-msg-error');
      if (msg && msg.offsetParent !== null && msg.textContent.trim()) { log.push('sign-up said: ' + msg.textContent.trim()); return false; }
      await sleep(200);
    }
    log.push('sign-up: still on ' + location.hash);
    return false;
  }
  async function signIn(email, password, to) {
    location.hash = '#auth';
    await until(() => window.UI_READY && $$('.au-card input[type=password]').length, 'sign-in form');
    await sleep(400);
    type($('.au-card input[type=email]'), email); type($('.au-card input[type=password]'), password);
    button(/Sign in/, '.au-card .anvil-role-btn-block').click();
    await until(() => location.hash.indexOf(to || '#map') === 0 && window.UI_READY, 'signed in as ' + email, 30000);
  }
  async function signOut() {
    await open('#landing', /Doremi/);
    button(/^Sign out$/, '.g-title').click();
    await until(() => button(/Begin the journey/, '.g-title'), 'signed out');
    await sleep(500);
  }
  try {
    // ---- signed out: the title screen, the whole road as a guest
    await open('#landing', /Begin the journey/, () => (!$('.g-title canvas') ? 'no title scene' : !/Watch Doremi Road/.test($('.ui-main').innerText) ? 'no Watch section' : ''));
    await road('guest');
    await open('#auth', /Sign in/);
    await open('#auth/signup', /Create account/);

    // ---- a new member
    const ok = await signUp('Smoke Tester', 'smoke' + Date.now() + '@example.com', 'Dr-' + Math.random().toString(36).slice(2) + '-Kq7');
    if (!ok) throw new Error('sign-up failed');
    await road('member');
    await open('#map', /Daily Practice/);
    $('.anvil-role-avatar button').click();
    await until(() => $$('.pf').some((c) => /Settings/.test(c.innerText)), 'the profile dialog', 15000);
    log.push('ok   profile + settings dialog');
    await closeDialog();
    await signOut();

    // ---- admin (Game.ADMIN_EMAILS): sign up the first time, sign in after that
    const adminPw = 'Dr-smoke-adm-93Kx-7q';
    if (!(await signUp('Admin Tester', 'arkulinskis@gmail.com', adminPw))) await signIn('arkulinskis@gmail.com', adminPw);
    await open('#admin', /Pick a level/, () => ($$('.a-lv').length < 10 ? 'level list missing' : ''));
    $('.a-lv .anvil-role-a-lv-name').click();
    await until(() => $$('.a-step').length >= 1 && /Checks/.test($('.ui-main').innerText), 'a level in the editor', 15000);
    log.push('ok   #admin level editor opens a level (' + $$('.a-step').length + ' steps)');
    await open('#admin/territories', /Colour on the map/, () => (!$('.a-mapprev svg') ? 'no map preview' : ''));
    await open('#admin/players', /Players/, () => ($$('.a-prow').length < 1 ? 'no players listed' : ''));
    await signOut();
    log.push(bad.length ? 'PROBLEMS: ' + bad.join(' | ') : 'PASSED');
    return { ok: !bad.length, log: log };
  } catch (e) {
    log.push(String(e && e.message || e));
    if (bad.length) log.push('PROBLEMS: ' + bad.join(' | '));
    return { ok: false, log: log };
  }
})();
