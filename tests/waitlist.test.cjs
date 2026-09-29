const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const vm = require('node:vm');

const script = readFileSync('app/static/waitlist.js', 'utf8');

function setup() {
  const triggerHandlers = {};
  const closeHandlers = {};
  const dialogHandlers = {};
  const trigger = { addEventListener: (name, fn) => { triggerHandlers[name] = fn; } };
  const closeButton = { addEventListener: (name, fn) => { closeHandlers[name] = fn; } };
  const dialog = {
    opens: 0,
    closes: 0,
    showModal() { this.opens++; },
    close() { this.closes++; },
    addEventListener: (name, fn) => { dialogHandlers[name] = fn; },
  };
  vm.runInNewContext(script, {
    document: {
      querySelector(selector) {
        return {
          '#waitlist-trigger': trigger,
          '#waitlist-dialog': dialog,
          '#waitlist-close': closeButton,
        }[selector];
      },
    },
  });
  return {
    dialog,
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
