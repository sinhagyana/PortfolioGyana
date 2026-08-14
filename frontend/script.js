(() => {
  const API_ENDPOINT = "/api/chat";
  const MAX_HISTORY_TURNS = 8; // sent to the backend for context, trimmed further server-side

  const log = document.getElementById("chat-log");
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");
  const sendBtn = document.getElementById("chat-send");
  const status = document.getElementById("agent-status");
  const hint = document.getElementById("chat-hint");
  const chips = document.querySelectorAll(".chip");

  /** @type {{role: "user"|"assistant", content: string}[]} */
  let history = [];
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
    sendBtn.disabled = isThinking;
    input.disabled = isThinking;
    status.textContent = isThinking ? "● thinking" : "● online";
    status.classList.toggle("thinking", isThinking);
  }

  async function ask(question) {
    if (!question.trim()) return;

    appendMessage("user", question);
    history.push({ role: "user", content: question });
    input.value = "";
    hint.textContent = "";
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
})();
