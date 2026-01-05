
// session id for backend to recall things with. TO DO
function getSessionId() {
  const key = "instalily_session_id";
  let sid = window.localStorage.getItem(key);
  if (!sid) {
    sid = `sess_${Math.random().toString(16).slice(2)}`;
    window.localStorage.setItem(key, sid);
  }
  return sid;
}

export const getAIMessage = async (userQuery) => {
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: getSessionId(),
        message: userQuery,
        context: {} // TO DO: { appliance_type, model_number, ... }
      })
    });

    if (!res.ok) {
      const txt = await res.text();
      return {
        role: "assistant",
        content: `Backend error (${res.status}): ${txt}`
      };
    }

    const data = await res.json();

    // FastAPI returns: { messages: [{ role, content, citations }], cards, memory }
    const assistant = data?.messages?.[0];
    if (!assistant?.content) {
      return { role: "assistant", content: "I didn't get a valid response from the backend." };
    }

    // Return in the shape that UI expects
    return {
      role: "assistant",
      content: assistant.content
    };
  } catch (err) {
    return {
      role: "assistant",
      content: `Could not reach backend. Is it running on port 8000? (${err.message})`
    };
  }
};
