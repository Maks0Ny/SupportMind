import type { TicketDetail } from "../types/ticket";

type TicketDetailsProps = {
  selectedTicket: TicketDetail | null;
  editCategory: string;
  editPriority: string;
  editSentiment: string;
  editConfidence: string;
  setEditCategory: (value: string) => void;
  setEditPriority: (value: string) => void;
  setEditSentiment: (value: string) => void;
  setEditConfidence: (value: string) => void;
  onUpdatePrediction: () => void;
};

export function TicketDetails({
  selectedTicket,
  editCategory,
  editPriority,
  editSentiment,
  editConfidence,
  setEditCategory,
  setEditPriority,
  setEditSentiment,
  setEditConfidence,
  onUpdatePrediction,
}: TicketDetailsProps) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2 className="panel-title">Детали тикета</h2>
          <p className="panel-caption">
            {selectedTicket ? `Выбран тикет #${selectedTicket.id}` : "Тикет не выбран"}
          </p>
        </div>
      </div>

      <div className="panel-body">
        {!selectedTicket ? (
          <div className="empty-state">
            <div>
              <p className="empty-title">Выбери тикет</p>
              <p>Детали и форма редактирования появятся здесь.</p>
            </div>
          </div>
        ) : (
          <>
            <div className="details-grid">
              <div className="data-tile">
                <p className="data-label">ID</p>
                <p className="data-value">#{selectedTicket.id}</p>
              </div>
              <div className="data-tile">
                <p className="data-label">Создан</p>
                <p className="data-value">{new Date(selectedTicket.created_at).toLocaleString()}</p>
              </div>
            </div>

            <hr className="section-divider" />

            <p className="data-label">Текст обращения</p>
            <p className="details-text">{selectedTicket.text}</p>

            <hr className="section-divider" />

            {!selectedTicket.prediction ? (
              <div className="empty-state">
                <div>
                  <p className="empty-title">Prediction отсутствует</p>
                  <p>Для этого тикета нет связанных данных prediction.</p>
                </div>
              </div>
            ) : (
              <>
                <div className="result-grid">
                  <div className="data-tile">
                    <p className="data-label">Category</p>
                    <span className="badge badge-category">{selectedTicket.prediction.category}</span>
                  </div>
                  <div className="data-tile">
                    <p className="data-label">Priority</p>
                    <span className="badge badge-priority">{selectedTicket.prediction.priority}</span>
                  </div>
                  <div className="data-tile">
                    <p className="data-label">Sentiment</p>
                    <span className="badge badge-sentiment">{selectedTicket.prediction.sentiment}</span>
                  </div>
                  <div className="data-tile">
                    <p className="data-label">Confidence</p>
                    <span className="badge badge-confidence">
                      {selectedTicket.prediction.confidence}
                    </span>
                  </div>
                </div>

                <hr className="section-divider" />

                <div className="edit-grid">
                  <label className="field">
                    <span className="field-label">Category</span>
                    <input
                      className="input"
                      value={editCategory}
                      onChange={(event) => setEditCategory(event.target.value)}
                      placeholder="billing_and_payments"
                    />
                  </label>

                  <label className="field">
                    <span className="field-label">Priority</span>
                    <select
                      className="select"
                      value={editPriority}
                      onChange={(event) => setEditPriority(event.target.value)}
                    >
                      <option value="high">high</option>
                      <option value="medium">medium</option>
                      <option value="low">low</option>
                    </select>
                  </label>

                  <label className="field">
                    <span className="field-label">Sentiment</span>
                    <select
                      className="select"
                      value={editSentiment}
                      onChange={(event) => setEditSentiment(event.target.value)}
                    >
                      <option value="negative">negative</option>
                      <option value="neutral">neutral</option>
                      <option value="positive">positive</option>
                    </select>
                  </label>

                  <label className="field">
                    <span className="field-label">Confidence</span>
                    <input
                      className="input"
                      inputMode="decimal"
                      value={editConfidence}
                      onChange={(event) => setEditConfidence(event.target.value)}
                      placeholder="0.91"
                    />
                  </label>
                </div>

                <div className="actions actions-spaced">
                  <button className="button button-primary" onClick={onUpdatePrediction}>
                    Сохранить изменения
                  </button>
                </div>
              </>
            )}
          </>
        )}
      </div>
    </section>
  );
}
