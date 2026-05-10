export type AnalyzeResponse = {
  ticket_id: number;
  category: string;
  priority: string;
  sentiment: string;
  confidence: number;
};

export type TicketListItem = {
  id: number;
  text: string;
  created_at: string;
};

export type PredictionData = {
  category: string;
  priority: string;
  sentiment: string;
  confidence: number;
  created_at: string;
};

export type TicketDetail = {
  id: number;
  text: string;
  created_at: string;
  prediction: PredictionData | null;
};

export type TicketFilters = {
  category?: string;
  priority?: string;
  sentiment?: string;
};

export type PredictionUpdate = {
  category: string;
  priority: string;
  sentiment: string;
  confidence: number;
};