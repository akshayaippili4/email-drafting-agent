const form = document.getElementById("draft-form");
const submitBtn = document.getElementById("submit-btn");
const btnLabel = submitBtn.querySelector(".btn__label");
const btnSpinner = submitBtn.querySelector(".btn__spinner");
const outputArea = document.getElementById("output-area");
const outputStatus = document.getElementById("output-status");
const copyBtn = document.getElementById("copy-btn");
const errorAlert = document.getElementById("error-alert");

let currentEmail = "";

function setLoading(loading) {
  submitBtn.disabled = loading;
  btnLabel.textContent = loading ? "Drafting…" : "Draft email";
  btnSpinner.hidden = !loading;

  if (loading) {
    errorAlert.hidden = true;
    copyBtn.hidden = true;
    outputStatus.textContent = "Agents are working on your draft…";
    outputArea.innerHTML = `
      <div class="output__loading">
        <div class="output__loading-spinner"></div>
        <p>Analyzing context &amp; writing email</p>
        <small>This may take a minute with local models</small>
      </div>`;
  }
}

function showError(message) {
  errorAlert.textContent = message;
  errorAlert.hidden = false;
  outputStatus.textContent = "Something went wrong.";
}

function showEmail(email) {
  currentEmail = email;
  outputStatus.textContent = "Draft ready — review and copy below.";
  copyBtn.hidden = false;
  outputArea.innerHTML = `<pre class="output__content">${escapeHtml(email)}</pre>`;
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const context = document.getElementById("context").value.trim();
  if (!context) {
    showError("Please describe what the email should be about.");
    return;
  }

  const payload = {
    context,
    tone: document.getElementById("tone").value,
    recipient: document.getElementById("recipient").value.trim() || "the recipient",
  };

  setLoading(true);

  try {
    const res = await fetch("/api/draft", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok) {
      showError(data.error || "Failed to draft email.");
      outputArea.innerHTML = `
        <div class="output__placeholder">
          <p>Unable to generate email. Check that Ollama is running.</p>
        </div>`;
      return;
    }

    showEmail(data.email);
  } catch {
    showError("Network error — is the server running?");
    outputArea.innerHTML = `
      <div class="output__placeholder">
        <p>Could not reach the server.</p>
      </div>`;
  } finally {
    setLoading(false);
  }
});

copyBtn.addEventListener("click", async () => {
  if (!currentEmail) return;

  try {
    await navigator.clipboard.writeText(currentEmail);
    copyBtn.textContent = "Copied!";
    copyBtn.classList.add("copied");
    setTimeout(() => {
      copyBtn.textContent = "Copy to clipboard";
      copyBtn.classList.remove("copied");
    }, 2000);
  } catch {
    showError("Could not copy to clipboard.");
  }
});
