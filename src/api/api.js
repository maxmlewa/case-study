
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

export const getAIMessage = async (userQuery, context = {}) => {
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: getSessionId(),
        message: userQuery,
        context // TO DO: { appliance_type, model_number, ... }
      })
    });

    if (!res.ok) {
      const txt = await res.text();
      return {
        message: { role: "assistant", content: `Backend error (${res.status}): ${txt}` },
        cards: []
      };
    }

    const data = await res.json();
   

    // FastAPI returns: { messages: [{ role, content, citations }], cards, memory }
    const assistant = data?.messages?.[0];
    return {
      message: {
        role: "assistant",
        content: assistant?.content || "I didn't get a valid response from the backend."
      },
      cards: data?.cards || []
    };
  } catch (err) {
    return {
      message: {
        role: "assistant",
        content: `Could not reach backend. Is it running on port 8000? (${err.message})`
      },
      cards: []
    };
  }
};
