import { useState, useRef, useEffect } from "react";
import "./styles.css";

const API = import.meta.env.VITE_API_URL || "";

export default function App() {
  const [question, setQuestion] = useState("");
  const [turns, setTurns] = useState([]);
  const [busy, setBusy] = useState(false);
  const [health, setHealth] = useState(null);
  const endRef = useRef(null);

  useEffect(() => {
    const tick = () => fetch(`${API}/api/healthz`).then(r => r.json()).then(setHealth).catch(() => setHealth(null));
    tick();
    const id = setInterval(tick, 15000);
    return () => clearInterval(id);
  }, []);
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [turns]);

  async function ask(e) {
    e.preventDefault();
    if (!question.trim() || busy) return;
    const q = question.trim();
    setQuestion("");
    setTurns(t => [...t, { role: "user", text: q }]);
    setBusy(true);
    try {
      const r = await fetch(`${API}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      const body = await r.json();
      if (!r.ok) throw new Error(body.detail || `HTTP ${r.status}`);
      setTurns(t => [...t, {
        role: "copilot",
        text: body.answer,
        citations: body.citations || [],
        latency_ms: body.latency_ms,
        model: body.model,
      }]);
    } catch (err) {
      setTurns(t => [...t, { role: "error", text: String(err.message) }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="app">
      <header>
        <h1>Support Copilot</h1>
        <div className="meta">
          <span className={`dot ${health ? "ok" : ""}`} />
          {health ? `${health.index_chunks} chunks · ${health.model}` : "backend offline"}
        </div>
      </header>

      <main>
        {turns.length === 0 && (
          <div className="empty">
            <p>Ask about the support knowledge base — every answer is grounded and cited.</p>
            <div className="samples">
              {["How do I deploy to App Service?", "Cosmos DB returns 429 — what do I do?",
                "What is the Sev1 escalation SLA?", "Show me KQL for failed requests"].map(s => (
                <button key={s} onClick={() => setQuestion(s)}>{s}</button>
              ))}
            </div>
          </div>
        )}
        {turns.map((t, i) => (
          <div key={i} className={`turn ${t.role}`}>
            <div className="bubble">
              {t.text}
              {t.role === "copilot" && (
                <>
                  <div className="citebox">
                    <span className="lbl">Sources</span>
                    {t.citations.map(c => (
                      <span key={c.n} className="cite">[{c.n}] {c.title} — {c.header} ({c.score})</span>
                    ))}
                  </div>
                  <div className="stats">{t.latency_ms} ms · {t.model} · AI-generated, verify against sources</div>
                </>
              )}
            </div>
          </div>
        ))}
        {busy && <div className="turn copilot"><div className="bubble">searching docs…</div></div>}
        <div ref={endRef} />
      </main>

      <form onSubmit={ask}>
        <input
          value={question}
          onChange={e => setQuestion(e.target.value)}
          placeholder="Ask a support question…"
          disabled={busy}
        />
        <button disabled={busy || !question.trim()}>Ask</button>
      </form>
    </div>
  );
}
