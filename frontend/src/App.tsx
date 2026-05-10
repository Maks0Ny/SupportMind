import { useEffect, useState } from "react";
import "./App.css";

import { getDashboardSummary } from "./api/dashboardApi";
import {
  analyzeTicket,
  deleteTicket,
  getTicketById,
  getTickets,
  updatePrediction,
} from "./api/ticketsApi";
import { ConfirmDialog } from "./components/ConfirmDialog";
import { Dashboard } from "./components/Dashboard";
import { TicketAnalyzeForm } from "./components/TicketAnalyzeForm";
import { TicketDetails } from "./components/TicketDetails";
import { TicketFilters } from "./components/TicketFilters";
import { TicketHistory } from "./components/TicketHistory";
import type { DashboardSummary } from "./types/dashboard";
import type { AnalyzeResponse, TicketDetail, TicketListItem } from "./types/ticket";

function App() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<AnalyzeResponse | null>(null);

  const [tickets, setTickets] = useState<TicketListItem[]>([]);
  const [selectedTicket, setSelectedTicket] = useState<TicketDetail | null>(null);
  const [dashboard, setDashboard] = useState<DashboardSummary | null>(null);

  const [categoryFilter, setCategoryFilter] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");
  const [sentimentFilter, setSentimentFilter] = useState("");

  const [editCategory, setEditCategory] = useState("");
  const [editPriority, setEditPriority] = useState("");
  const [editSentiment, setEditSentiment] = useState("");
  const [editConfidence, setEditConfidence] = useState("");

  const [isLoading, setIsLoading] = useState(false);
  const [isTicketsLoading, setIsTicketsLoading] = useState(false);
  const [isDashboardLoading, setIsDashboardLoading] = useState(false);
  const [error, setError] = useState("");
  const [ticketIdToDelete, setTicketIdToDelete] = useState<number | null>(null);

  const loadTickets = async () => {
    try {
      setIsTicketsLoading(true);
      setError("");

      const data = await getTickets({
        category: categoryFilter,
        priority: priorityFilter,
        sentiment: sentimentFilter,
      });

      setTickets(data);
    } catch {
      setError("Не удалось загрузить историю тикетов.");
    } finally {
      setIsTicketsLoading(false);
    }
  };

  const loadDashboard = async () => {
    try {
      setIsDashboardLoading(true);
      setError("");

      const data = await getDashboardSummary();
      setDashboard(data);
    } catch {
      setError("Не удалось загрузить dashboard.");
    } finally {
      setIsDashboardLoading(false);
    }
  };

  const refreshData = async () => {
    await loadTickets();
    await loadDashboard();
  };

  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setIsTicketsLoading(true);
        setIsDashboardLoading(true);

        const [ticketsData, dashboardData] = await Promise.all([
          getTickets(),
          getDashboardSummary(),
        ]);

        setTickets(ticketsData);
        setDashboard(dashboardData);
      } catch {
        setError("Не удалось загрузить стартовые данные.");
      } finally {
        setIsTicketsLoading(false);
        setIsDashboardLoading(false);
      }
    };

    void loadInitialData();
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

      const data = await analyzeTicket(text.trim());

      setResult(data);
      setText("");

      await refreshData();
    } catch {
      setError("Не удалось отправить запрос. Проверь, запущен ли backend.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectTicket = async (ticketId: number) => {
    try {
      setError("");

      const data = await getTicketById(ticketId);

      setSelectedTicket(data);

      if (data.prediction) {
        setEditCategory(data.prediction.category);
        setEditPriority(data.prediction.priority);
        setEditSentiment(data.prediction.sentiment);
        setEditConfidence(String(data.prediction.confidence));
      } else {
        setEditCategory("");
        setEditPriority("");
        setEditSentiment("");
        setEditConfidence("");
      }
    } catch {
      setError("Не удалось загрузить детали тикета.");
    }
  };

  const handleUpdatePrediction = async () => {
    if (!selectedTicket) {
      return;
    }

    if (!editCategory.trim() || !editPriority.trim() || !editSentiment.trim()) {
      setError("Заполни category, priority и sentiment.");
      return;
    }

    const confidenceValue = Number(editConfidence);

    if (Number.isNaN(confidenceValue) || confidenceValue < 0 || confidenceValue > 1) {
      setError("Confidence должен быть числом от 0 до 1.");
      return;
    }

    try {
      setError("");

      await updatePrediction(selectedTicket.id, {
        category: editCategory.trim(),
        priority: editPriority.trim(),
        sentiment: editSentiment.trim(),
        confidence: confidenceValue,
      });

      await handleSelectTicket(selectedTicket.id);
      await refreshData();
    } catch {
      setError("Не удалось обновить prediction.");
    }
  };

  const handleDeleteTicket = async (ticketId: number) => {
    try {
      setError("");

      await deleteTicket(ticketId);

      if (selectedTicket?.id === ticketId) {
        setSelectedTicket(null);
      }

      await refreshData();
    } catch {
      setError("Не удалось удалить тикет.");
    } finally {
      setTicketIdToDelete(null);
    }
  };

  const handleResetFilters = async () => {
    setCategoryFilter("");
    setPriorityFilter("");
    setSentimentFilter("");

    try {
      setIsTicketsLoading(true);
      setError("");

      const data = await getTickets();
      setTickets(data);
    } catch {
      setError("Не удалось сбросить фильтры.");
    } finally {
      setIsTicketsLoading(false);
    }
  };

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <p className="app-kicker">Support operations dashboard</p>
          <h1 className="app-title">SupportMind</h1>
          <p className="app-subtitle">
            Анализ обращений пользователей, история тикетов и сводная аналитика в одном рабочем
            интерфейсе.
          </p>
        </div>

        <div className="status-strip" aria-label="Краткая сводка">
          <span className="status-pill">
            Тикетов <strong>{dashboard?.total_tickets ?? 0}</strong>
          </span>
          <span className="status-pill">
            High <strong>{dashboard?.high_priority_count ?? 0}</strong>
          </span>
          <span className="status-pill">
            Negative <strong>{dashboard?.negative_sentiment_count ?? 0}</strong>
          </span>
        </div>
      </header>

      <div className="app-grid">
        {error && (
          <div className="alert" role="alert">
            {error}
          </div>
        )}

        <Dashboard dashboard={dashboard} isLoading={isDashboardLoading} />

        <TicketAnalyzeForm
          text={text}
          setText={setText}
          result={result}
          isLoading={isLoading}
          onAnalyze={() => void handleAnalyze()}
        />

        <TicketFilters
          categoryFilter={categoryFilter}
          priorityFilter={priorityFilter}
          sentimentFilter={sentimentFilter}
          setCategoryFilter={setCategoryFilter}
          setPriorityFilter={setPriorityFilter}
          setSentimentFilter={setSentimentFilter}
          onApply={() => void loadTickets()}
          onReset={() => void handleResetFilters()}
        />

        <section className="workspace-grid" aria-label="Рабочая область тикетов">
          <TicketHistory
            tickets={tickets}
            selectedTicketId={selectedTicket?.id}
            isLoading={isTicketsLoading}
            onSelectTicket={(ticketId) => void handleSelectTicket(ticketId)}
            onDeleteTicket={(ticketId) => setTicketIdToDelete(ticketId)}
          />

          <TicketDetails
            selectedTicket={selectedTicket}
            editCategory={editCategory}
            editPriority={editPriority}
            editSentiment={editSentiment}
            editConfidence={editConfidence}
            setEditCategory={setEditCategory}
            setEditPriority={setEditPriority}
            setEditSentiment={setEditSentiment}
            setEditConfidence={setEditConfidence}
            onUpdatePrediction={() => void handleUpdatePrediction()}
          />
        </section>
      </div>

      <ConfirmDialog
        isOpen={ticketIdToDelete !== null}
        title="Удалить тикет"
        message="Запись будет удалена вместе с prediction. Это действие нельзя отменить."
        confirmLabel="Удалить"
        cancelLabel="Отмена"
        onCancel={() => setTicketIdToDelete(null)}
        onConfirm={() => {
          if (ticketIdToDelete !== null) {
            void handleDeleteTicket(ticketIdToDelete);
          }
        }}
      />
    </main>
  );
}

export default App;
