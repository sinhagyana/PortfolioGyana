(() => {
  const API_ENDPOINT = "/api/chat";
  const MAX_HISTORY_TURNS = 8; // sent to the backend for context, trimmed further server-side

  let clientId = null;

  function getClientId() {
    if (clientId) return clientId;
    try {
      clientId = sessionStorage.getItem("gyana_chat_id");
      if (!clientId) {
        clientId = crypto.randomUUID();
        sessionStorage.setItem("gyana_chat_id", clientId);
      }
    } catch {
      clientId = "anon-" + Math.random().toString(36).slice(2);
    }
    return clientId;
  }

  /**
   * Wires up a chat UI (message log, form, input, status, hint, suggestion chips)
   * to the backend. Used for both the inline "Ask the agent" console and the
   * floating corner widget so they behave identically.
   */
  function createChatController({ log, form, input, sendBtn, status, hint, chips }) {
    if (!log || !form || !input) return null;

    /** @type {{role: "user"|"assistant", content: string}[]} */
    let history = [];

    function appendMessage(role, text, isError = false) {
      const wrap = document.createElement("div");
      wrap.className = `msg msg-${role}` + (isError ? " msg-error" : "");

      const roleLabel = document.createElement("span");
      roleLabel.className = "msg-role mono";
      roleLabel.textContent = role === "user" ? "you" : "agent";

      const p = document.createElement("p");
      p.textContent = text;

      wrap.appendChild(roleLabel);
      wrap.appendChild(p);
      log.appendChild(wrap);
      log.scrollTop = log.scrollHeight;
      return p;
    }

    function setThinking(isThinking) {
      if (sendBtn) sendBtn.disabled = isThinking;
      input.disabled = isThinking;
      if (status) {
        status.textContent = isThinking ? "● thinking" : "● online";
        status.classList.toggle("thinking", isThinking);
      }
    }

    async function ask(question) {
      if (!question.trim()) return;

      appendMessage("user", question);
      history.push({ role: "user", content: question });
      input.value = "";
      if (hint) hint.textContent = "";
      setThinking(true);

      const thinkingP = appendMessage("assistant", "…");

      try {
        const res = await fetch(API_ENDPOINT, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Client-Id": getClientId(),
          },
          body: JSON.stringify({
            message: question,
            history: history.slice(-MAX_HISTORY_TURNS),
            request_id: getClientId(),
          }),
        });

        const data = await res.json().catch(() => ({}));

        if (!res.ok) {
          throw new Error(data.detail || `Request failed (${res.status})`);
        }

        thinkingP.textContent = data.reply;
        history.push({ role: "assistant", content: data.reply });
      } catch (err) {
        thinkingP.parentElement.classList.add("msg-error");
        thinkingP.textContent =
          "Couldn't reach the agent just now. " +
          (err.message?.includes("configured")
            ? "The backend still needs an XAI_API_KEY set — see backend/.env.example."
            : "Please try again in a moment.");
      } finally {
        setThinking(false);
        input.focus();
      }
    }

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      ask(input.value);
    });

    chips.forEach((chip) => {
      chip.addEventListener("click", () => ask(chip.textContent));
    });

    return { ask };
  }

  // ---------- inline "Ask the agent" section ----------
  createChatController({
    log: document.getElementById("chat-log"),
    form: document.getElementById("chat-form"),
    input: document.getElementById("chat-input"),
    sendBtn: document.getElementById("chat-send"),
    status: document.getElementById("agent-status"),
    hint: document.getElementById("chat-hint"),
    chips: document.querySelectorAll("#suggested-questions .chip"),
  });

  // ---------- floating corner widget ----------
  createChatController({
    log: document.getElementById("chat-log-float"),
    form: document.getElementById("chat-form-float"),
    input: document.getElementById("chat-input-float"),
    sendBtn: document.getElementById("chat-send-float"),
    status: document.getElementById("agent-status-float"),
    hint: document.getElementById("chat-hint-float"),
    chips: document.querySelectorAll("#suggested-questions-float .chip"),
  });

  // ---------- FAB open/close ----------
  const fab = document.getElementById("agent-fab");
  const panel = document.getElementById("agent-float-panel");
  const closeBtn = document.getElementById("agent-float-close");
  const floatInput = document.getElementById("chat-input-float");
  const heroAskBtn = document.getElementById("hero-ask-agent");

  if (fab && panel) {
    const openPanel = () => {
      panel.hidden = false;
      fab.setAttribute("aria-expanded", "true");
      fab.classList.add("is-open");
      requestAnimationFrame(() => floatInput && floatInput.focus());
    };

    const closePanel = () => {
      panel.hidden = true;
      fab.setAttribute("aria-expanded", "false");
      fab.classList.remove("is-open");
    };

    fab.addEventListener("click", () => {
      if (panel.hidden) openPanel();
      else closePanel();
    });

    closeBtn?.addEventListener("click", closePanel);

    heroAskBtn?.addEventListener("click", (e) => {
      e.preventDefault();
      openPanel();
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && !panel.hidden) closePanel();
    });

    document.addEventListener("click", (e) => {
      if (panel.hidden) return;
      const widget = document.getElementById("agent-widget");
      if (widget && !widget.contains(e.target)) closePanel();
    });
  }
})();
