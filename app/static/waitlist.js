"use strict";

const trigger = document.querySelector("#waitlist-trigger");
const dialog = document.querySelector("#waitlist-dialog");
const closeButton = document.querySelector("#waitlist-close");
const authNote = document.querySelector("#auth-note");
const waitlistStatus = document.querySelector("#waitlist-status");
const authBaseUrl = (document.body?.dataset.authBaseUrl || globalThis.SFWBOTS_AUTH_BASE_URL || "")
  .replace(/\/+$/, "");

if (trigger && dialog && closeButton) {
  trigger.addEventListener("click", () => dialog.showModal());
  closeButton.addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
}

if (authBaseUrl) {
  document.querySelectorAll("[data-provider]").forEach((link) => {
    link.href = `${authBaseUrl}/auth/${link.dataset.provider}`;
    link.classList.remove("is-disabled");
    link.removeAttribute("aria-disabled");
    link.removeAttribute("tabindex");
  });
  if (authNote) authNote.textContent = "We only use your name and email to create your waitlist profile.";
}

const authResult = new URLSearchParams(globalThis.location?.search || "");
if (authResult.get("joined") && trigger && waitlistStatus) {
  trigger.disabled = true;
  trigger.textContent = "You’re on the waitlist";
  waitlistStatus.dataset.state = "success";
  waitlistStatus.textContent = "We’ll be in touch when SFWbots opens.";
  globalThis.history?.replaceState({}, "", globalThis.location.pathname);
} else if (authResult.get("auth_error") && waitlistStatus) {
  waitlistStatus.dataset.state = "error";
  waitlistStatus.textContent = "We couldn’t complete sign-in. Please try again.";
  globalThis.history?.replaceState({}, "", globalThis.location.pathname);
}
