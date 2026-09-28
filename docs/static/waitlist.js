"use strict";

const form = document.querySelector("#waitlist-form");
const status = document.querySelector("#form-status");
const button = form.querySelector("button[type=submit]");
let submitting = false;

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (submitting || !form.reportValidity()) return;
  if (form.dataset.configured !== "true") {
    status.textContent = "Signups aren’t open yet. Check back soon.";
    return;
  }
  submitting = true;
  button.disabled = true;
  button.textContent = "Joining…";
  form.setAttribute("aria-busy", "true");
  status.dataset.state = "pending";
  status.textContent = "Adding you to the waitlist…";
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);
  try {
    const data = new FormData(form);
    data.delete("redirect");
    const response = await fetch(form.action, {
      method: "POST",
      body: data,
      headers: { Accept: "application/json" },
      signal: controller.signal,
    });
    const result = await response.json();
    if (!response.ok || result.success !== true) throw new Error("Submission failed");
    status.dataset.state = "success";
    status.textContent = "You’re on the list. We’ll email you when SFWbots is ready.";
    form.reset();
  } catch (error) {
    status.dataset.state = "error";
    status.textContent = error.name === "AbortError"
      ? "That took too long. We couldn’t confirm your signup. Please try again."
      : "We couldn’t confirm your signup. Please try again.";
  } finally {
    clearTimeout(timeout);
    submitting = false;
    button.disabled = false;
    button.textContent = "Join the waitlist";
    form.removeAttribute("aria-busy");
  }
});
