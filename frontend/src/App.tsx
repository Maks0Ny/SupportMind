import { useEffect, useState } from "react";

type AnalyzeResponse = {
  ticket_id: number;
  category: string;
  priority: string;
  sentiment: string;
  confidence: number;
};

type TicketListItem = {
  id: number;
  text: string;
  created_at: string;
};

function App() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [tickets, setTickets] = useState<TicketListItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const loadTickets = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/v1/tickets");

      if (!response.ok) {
        throw new Error("Ошибка загрузки тикетов");
      }

      const data: TicketListItem[] = await response.json();
      setTickets(data);
    } catch {
      setError("Не удалось загрузить историю тикетов.");
    }
  };

  useEffect(() => {
    const loadInitialTickets = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/v1/tickets");

        if (!response.ok) {
          throw new Error("Ошибка загрузки тикетов");
        }

        const data: TicketListItem[] = await response.json();
        setTickets(data);
      } catch {
        setError("Не удалось загрузить историю тикетов.");
      }
    };

    void loadInitialTickets();
  }, []);

  const handleAnalyze = async () => {
    setError("");
    setResult(null);

    if (text.trim().length < 5) {
      setError("Введите текст минимум из 5 символов.");
      return;
    }

    try {
      setIsLoading(true);

      const response = await fetch("http://127.0.0.1:8000/api/v1/tickets/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: text.trim(),
        }),
      });

      if (!response.ok) {
        throw new Error("Ошибка при анализе тикета");
      }

      const data: AnalyzeResponse = await response.json();

      setResult(data);
      setText("");
      void loadTickets();
    } catch {
      setError("Не удалось отправить запрос. Проверь, запущен ли backend.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main style={{ maxWidth: 720, margin: "40px auto", fontFamily: "Arial, sans-serif" }}>
      <h1>SupportMind</h1>
      <p>Анализ обращений пользователей</p>

      <textarea
        value={text}
        onChange={(event) => setText(event.target.value)}
        placeholder="Например: После обновления приложение вылетает при оплате заказа"
        rows={6}
        style={{ width: "100%", padding: 12, fontSize: 16 }}
      />

      <button
        onClick={handleAnalyze}
        disabled={isLoading}
        style={{ marginTop: 12, padding: "10px 16px", cursor: "pointer" }}
      >
        {isLoading ? "Анализируем..." : "Анализировать"}
      </button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {result && (
        <section style={{ marginTop: 24, padding: 16, border: "1px solid #ddd", borderRadius: 8 }}>
          <h2>Результат</h2>
          <p>
            <b>Ticket ID:</b> {result.ticket_id}
          </p>
          <p>
            <b>Category:</b> {result.category}
          </p>
          <p>
            <b>Priority:</b> {result.priority}
          </p>
          <p>
            <b>Sentiment:</b> {result.sentiment}
          </p>
          <p>
            <b>Confidence:</b> {result.confidence}
          </p>
        </section>
      )}

      <section style={{ marginTop: 32 }}>
        <h2>История тикетов</h2>

        {tickets.length === 0 ? (
          <p>История пока пустая.</p>
        ) : (
          <ul style={{ paddingLeft: 0, listStyle: "none" }}>
            {tickets.map((ticket) => (
              <li
                key={ticket.id}
                style={{
                  padding: 12,
                  border: "1px solid #ddd",
                  borderRadius: 8,
                  marginBottom: 8,
                }}
              >
                <b>#{ticket.id}</b>
                <p>{ticket.text}</p>
                <small>{new Date(ticket.created_at).toLocaleString()}</small>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}

export default App;