import type { AnalyzeResponse } from "../types/ticket";

type TicketResultCardProps = {
  result: AnalyzeResponse;
};

export function TicketResultCard({ result }: TicketResultCardProps) {
  return (
    <div className="result-grid result-spaced">
      <div className="data-tile">
        <p className="data-label">Ticket ID</p>
        <p className="data-value">#{result.ticket_id}</p>
      </div>
      <div className="data-tile">
        <p className="data-label">Category</p>
        <span className="badge badge-category">{result.category}</span>
      </div>
      <div className="data-tile">
        <p className="data-label">Priority</p>
        <span className="badge badge-priority">{result.priority}</span>
      </div>
      <div className="data-tile">
        <p className="data-label">Confidence</p>
        <span className="badge badge-confidence">{result.confidence}</span>
      </div>
    </div>
  );
}
