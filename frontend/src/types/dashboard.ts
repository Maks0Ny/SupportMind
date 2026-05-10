export type DashboardSummary = {
  total_tickets: number;
  high_priority_count: number;
  negative_sentiment_count: number;
  by_category: Record<string, number>;
  by_priority: Record<string, number>;
  by_sentiment: Record<string, number>;
};