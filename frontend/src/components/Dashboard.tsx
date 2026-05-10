import type { DashboardSummary } from "../types/dashboard";
import { DashboardDict } from "./DashboardDict";

type DashboardProps = {
  dashboard: DashboardSummary | null;
  isLoading: boolean;
};

export function Dashboard({ dashboard, isLoading }: DashboardProps) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2 className="panel-title">Dashboard</h2>
          <p className="panel-caption">Сводка по обращениям и prediction-меткам</p>
        </div>
      </div>

      <div className="panel-body">
        {isLoading && <div className="loading-state">Загрузка статистики...</div>}

        {!isLoading && !dashboard ? (
          <div className="empty-state">
            <div>
              <p className="empty-title">Статистика недоступна</p>
              <p>Проверь подключение к backend.</p>
            </div>
          </div>
        ) : null}

        {!isLoading && dashboard ? (
          <>
            <div className="dashboard-metrics">
              <article className="metric-card">
                <p className="metric-label">Всего тикетов</p>
                <p className="metric-value">{dashboard.total_tickets}</p>
                <p className="metric-note">Создано в истории</p>
              </article>

              <article className="metric-card">
                <p className="metric-label">High priority</p>
                <p className="metric-value">{dashboard.high_priority_count}</p>
                <p className="metric-note">Требуют внимания</p>
              </article>

              <article className="metric-card">
                <p className="metric-label">Negative sentiment</p>
                <p className="metric-value">{dashboard.negative_sentiment_count}</p>
                <p className="metric-note">Негативная тональность</p>
              </article>
            </div>

            <div className="dashboard-breakdown">
              <DashboardDict title="По категориям" data={dashboard.by_category} />
              <DashboardDict title="По приоритетам" data={dashboard.by_priority} />
              <DashboardDict title="По тональности" data={dashboard.by_sentiment} />
            </div>
          </>
        ) : null}
      </div>
    </section>
  );
}
