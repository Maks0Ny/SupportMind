import type { AnalyzeResponse } from "../types/ticket";
import { TicketResultCard } from "./TicketResultCard";

type TicketAnalyzeFormProps = {
  text: string;
  setText: (value: string) => void;
  result: AnalyzeResponse | null;
  isLoading: boolean;
  onAnalyze: () => void;
};

export function TicketAnalyzeForm({
  text,
  setText,
  result,
  isLoading,
  onAnalyze,
}: TicketAnalyzeFormProps) {
  const trimmedLength = text.trim().length;

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2 className="panel-title">Анализ тикета</h2>
          <p className="panel-caption">Создать обращение и получить prediction</p>
        </div>
      </div>

      <div className="panel-body">
        <div className="field-grid">
          <label className="field">
            <span className="field-label">Текст обращения</span>
            <textarea
              className="textarea"
              value={text}
              onChange={(event) => setText(event.target.value)}
              placeholder="Например: После обновления приложение вылетает при оплате заказа"
              rows={6}
            />
          </label>

          <div className="field-footer">
            <span>Минимум 5 символов</span>
            <span>{trimmedLength}/2000</span>
          </div>

          <div className="actions">
            <button className="button button-primary" onClick={onAnalyze} disabled={isLoading}>
              {isLoading ? "Анализируем..." : "Анализировать"}
            </button>
          </div>
        </div>

        {result && <TicketResultCard result={result} />}
      </div>
    </section>
  );
}
