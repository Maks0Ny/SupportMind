type DashboardDictProps = {
  title: string;
  data: Record<string, number>;
};

export function DashboardDict({ title, data }: DashboardDictProps) {
  const entries = Object.entries(data);
  const maxValue = Math.max(...entries.map(([, value]) => value), 1);

  return (
    <article className="dict-card">
      <h3 className="dict-title">{title}</h3>

      {entries.length === 0 ? (
        <p className="panel-caption">Нет данных</p>
      ) : (
        <ul className="dict-list">
          {entries.map(([key, value]) => (
            <li className="dict-row" key={key}>
              <div className="dict-row-top">
                <span className="dict-key">{key}</span>
                <span className="dict-value">{value}</span>
              </div>
              <div className="bar" aria-hidden="true">
                <span className="bar-fill" style={{ width: `${(value / maxValue) * 100}%` }} />
              </div>
            </li>
          ))}
        </ul>
      )}
    </article>
  );
}
