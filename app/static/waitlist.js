"use strict";

const trigger = document.querySelector("#waitlist-trigger");
const dialog = document.querySelector("#waitlist-dialog");
const closeButton = document.querySelector("#waitlist-close");

if (trigger && dialog && closeButton) {
  trigger.addEventListener("click", () => dialog.showModal());
  closeButton.addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
}
