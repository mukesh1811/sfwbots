const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const vm = require('node:vm');

const script = readFileSync('app/static/waitlist.js', 'utf8');

function setup(authBaseUrl = '', search = '') {
  const triggerHandlers = {};
  const closeHandlers = {};
  const dialogHandlers = {};
  const trigger = { disabled: false, textContent: 'Join the waitlist', addEventListener: (name, fn) => { triggerHandlers[name] = fn; } };
  const closeButton = { addEventListener: (name, fn) => { closeHandlers[name] = fn; } };
  const dialog = {
    opens: 0,
    closes: 0,
    showModal() { this.opens++; },
    close() { this.closes++; },
    addEventListener: (name, fn) => { dialogHandlers[name] = fn; },
  };
  const authNote = { textContent: 'Sign-in connections are being set up.' };
  const waitlistStatus = { dataset: {}, textContent: '' };
  const links = ['google', 'linkedin'].map((provider) => ({
    dataset: { provider },
    classList: { removed: [], remove(name) { this.removed.push(name); } },
    removeAttributeCalls: [],
    removeAttribute(name) { this.removeAttributeCalls.push(name); },
  }));
  vm.runInNewContext(script, {
    URLSearchParams,
    location: { search, pathname: '/' },
    history: { replaceState() {} },
    document: {
      body: { dataset: { authBaseUrl } },
      querySelector(selector) {
        return {
          '#waitlist-trigger': trigger,
          '#waitlist-dialog': dialog,
          '#waitlist-close': closeButton,
          '#auth-note': authNote,
          '#waitlist-status': waitlistStatus,
        }[selector];
      },
      querySelectorAll: () => links,
    },
  });
  return {
    dialog,
    trigger,
    authNote,
    waitlistStatus,
    links,
    open: () => triggerHandlers.click(),
    close: () => closeHandlers.click(),
    backdrop: (target) => dialogHandlers.click({ target }),
  };
}

test('waitlist button opens the sign-in modal', () => {
  const ui = setup();
  ui.open();
  assert.equal(ui.dialog.opens, 1);
});

test('close button closes the sign-in modal', () => {
  const ui = setup();
  ui.close();
  assert.equal(ui.dialog.closes, 1);
});

test('clicking the modal backdrop closes it', () => {
  const ui = setup();
  ui.backdrop(ui.dialog);
  assert.equal(ui.dialog.closes, 1);
});

test('clicking inside the modal leaves it open', () => {
  const ui = setup();
  ui.backdrop({});
  assert.equal(ui.dialog.closes, 0);
});

test('configured auth links point to the OAuth backend', () => {
  const ui = setup('https://sfwbots-auth.example/');
  assert.equal(ui.links[0].href, 'https://sfwbots-auth.example/auth/google');
  assert.equal(ui.links[1].href, 'https://sfwbots-auth.example/auth/linkedin');
  assert.deepEqual(ui.links[0].classList.removed, ['is-disabled']);
  assert.match(ui.authNote.textContent, /name and email/);
});

test('completed OAuth sign-in updates the waitlist state', () => {
  const ui = setup('', '?joined=google');
  assert.equal(ui.trigger.disabled, true);
  assert.equal(ui.trigger.textContent, 'You’re on the waitlist');
  assert.equal(ui.waitlistStatus.dataset.state, 'success');
});
