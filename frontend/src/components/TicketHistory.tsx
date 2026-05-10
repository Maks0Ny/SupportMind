import type { TicketListItem } from "../types/ticket";

type TicketHistoryProps = {
  tickets: TicketListItem[];
  selectedTicketId?: number;
  isLoading: boolean;
  onSelectTicket: (ticketId: number) => void;
  onDeleteTicket: (ticketId: number) => void;
};

export function TicketHistory({
  tickets,
  selectedTicketId,
  isLoading,
  onSelectTicket,
  onDeleteTicket,
}: TicketHistoryProps) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2 className="panel-title">История тикетов</h2>
          <p className="panel-caption">{tickets.length} записей в текущем списке</p>
        </div>
      </div>

      <div className="panel-body">
        {isLoading && <div className="loading-state">Загрузка истории...</div>}

        {!isLoading && tickets.length === 0 ? (
          <div className="empty-state">
            <div>
              <p className="empty-title">История пока пустая</p>
              <p>Создай первый тикет через форму анализа.</p>
            </div>
          </div>
        ) : null}

        {!isLoading && tickets.length > 0 ? (
          <ul className="ticket-list">
            {tickets.map((ticket) => (
              <li
                className={`ticket-item ${
                  selectedTicketId === ticket.id ? "ticket-item-active" : ""
                }`}
                key={ticket.id}
              >
                <div className="ticket-item-header">
                  <span className="ticket-id">#{ticket.id}</span>
                  <span className="ticket-date">{new Date(ticket.created_at).toLocaleString()}</span>
                </div>

                <p className="ticket-text">{ticket.text}</p>

                <div className="actions">
                  <button
                    className="button button-secondary"
                    onClick={() => onSelectTicket(ticket.id)}
                  >
                    Открыть
                  </button>

                  <button className="button button-danger" onClick={() => onDeleteTicket(ticket.id)}>
                    Удалить
                  </button>
                </div>
              </li>
            ))}
          </ul>
        ) : null}
      </div>
    </section>
  );
}
