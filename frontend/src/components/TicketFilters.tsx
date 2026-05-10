type TicketFiltersProps = {
  categoryFilter: string;
  priorityFilter: string;
  sentimentFilter: string;
  setCategoryFilter: (value: string) => void;
  setPriorityFilter: (value: string) => void;
  setSentimentFilter: (value: string) => void;
  onApply: () => void;
  onReset: () => void;
};

export function TicketFilters({
  categoryFilter,
  priorityFilter,
  sentimentFilter,
  setCategoryFilter,
  setPriorityFilter,
  setSentimentFilter,
  onApply,
  onReset,
}: TicketFiltersProps) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2 className="panel-title">Фильтры</h2>
          <p className="panel-caption">Отбор истории по prediction-полям</p>
        </div>
      </div>

      <div className="panel-body">
        <div className="filter-grid">
          <label className="field">
            <span className="field-label">Category</span>
            <input
              className="input"
              value={categoryFilter}
              onChange={(event) => setCategoryFilter(event.target.value)}
              placeholder="billing_and_payments"
            />
          </label>

          <label className="field">
            <span className="field-label">Priority</span>
            <select
              className="select"
              value={priorityFilter}
              onChange={(event) => setPriorityFilter(event.target.value)}
            >
              <option value="">Любой</option>
              <option value="high">high</option>
              <option value="medium">medium</option>
              <option value="low">low</option>
            </select>
          </label>

          <label className="field">
            <span className="field-label">Sentiment</span>
            <select
              className="select"
              value={sentimentFilter}
              onChange={(event) => setSentimentFilter(event.target.value)}
            >
              <option value="">Любой</option>
              <option value="negative">negative</option>
              <option value="neutral">neutral</option>
              <option value="positive">positive</option>
            </select>
          </label>
        </div>

        <div className="actions actions-spaced">
          <button className="button button-primary" onClick={onApply}>
            Применить
          </button>
          <button className="button button-secondary" onClick={onReset}>
            Сбросить
          </button>
        </div>
      </div>
    </section>
  );
}
