const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const vm = require('node:vm');
const script = readFileSync('app/static/waitlist.js', 'utf8');

function setup(fetch, configured = true) {
  let submit;
  const button = { disabled: false, textContent: 'Join the waitlist' };
  const status = { dataset: {}, textContent: '' };
  const form = {
    dataset: { configured: String(configured) },
    action: 'https://api.web3forms.com/submit',
    resets: 0,
    reportValidity: () => true,
    querySelector: () => button,
    addEventListener: (_, fn) => { submit = fn; },
    setAttribute: () => {}, removeAttribute: () => {},
    reset() { this.resets++; },
  };
  vm.runInNewContext(script, {
    document: { querySelector: (selector) => selector === '#waitlist-form' ? form : status },
    fetch, AbortController, setTimeout, clearTimeout,
    FormData: class { delete() {} },
  });
  return { form, button, status, submit: () => submit({ preventDefault() {} }) };
}

test('confirmed acceptance shows success and clears the email', async () => {
  const ui = setup(async () => ({ ok: true, json: async () => ({ success: true }) }));
  await ui.submit();
  assert.equal(ui.status.dataset.state, 'success');
  assert.equal(ui.form.resets, 1);
  assert.equal(ui.button.disabled, false);
});

for (const [name, fetch] of [
  ['API rejection', async () => ({ ok: true, json: async () => ({ success: false }) })],
  ['HTTP error', async () => ({ ok: false, json: async () => ({ success: true }) })],
  ['malformed response', async () => ({ ok: true, json: async () => { throw new Error(); } })],
  ['offline', async () => { throw new Error('offline'); }],
  ['timeout', async () => { const error = new Error(); error.name = 'AbortError'; throw error; }],
]) {
  test(`${name} preserves the email and permits retry`, async () => {
    const ui = setup(fetch);
    await ui.submit();
    assert.equal(ui.status.dataset.state, 'error');
    assert.equal(ui.form.resets, 0);
    assert.equal(ui.button.disabled, false);
  });
}

test('missing configuration never sends a signup', async () => {
  let calls = 0;
  const ui = setup(async () => { calls++; }, false);
  await ui.submit();
  assert.equal(calls, 0);
  assert.match(ui.status.textContent, /aren’t open/);
});

test('double submit sends only one request while pending', async () => {
  let resolve;
  let calls = 0;
  const ui = setup(() => { calls++; return new Promise(r => { resolve = r; }); });
  const first = ui.submit();
  await ui.submit();
  assert.equal(calls, 1);
  assert.equal(ui.button.disabled, true);
  resolve({ ok: true, json: async () => ({ success: true }) });
  await first;
});
