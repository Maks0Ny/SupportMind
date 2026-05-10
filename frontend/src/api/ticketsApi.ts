import { API_BASE_URL } from "./client";
import type {
  AnalyzeResponse,
  PredictionUpdate,
  TicketDetail,
  TicketFilters,
  TicketListItem,
} from "../types/ticket";

export async function analyzeTicket(text: string): Promise<AnalyzeResponse> {
  const response = await fetch(`${API_BASE_URL}/tickets/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    throw new Error("Failed to analyze ticket");
  }

  return response.json();
}

export async function getTickets(filters: TicketFilters = {}): Promise<TicketListItem[]> {
  const params = new URLSearchParams();

  if (filters.category?.trim()) {
    params.append("category", filters.category.trim());
  }

  if (filters.priority?.trim()) {
    params.append("priority", filters.priority.trim());
  }

  if (filters.sentiment?.trim()) {
    params.append("sentiment", filters.sentiment.trim());
  }

  const queryString = params.toString();
  const url = `${API_BASE_URL}/tickets${queryString ? `?${queryString}` : ""}`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error("Failed to load tickets");
  }

  return response.json();
}

export async function getTicketById(ticketId: number): Promise<TicketDetail> {
  const response = await fetch(`${API_BASE_URL}/tickets/${ticketId}`);

  if (!response.ok) {
    throw new Error("Failed to load ticket");
  }

  return response.json();
}

export async function updatePrediction(
  ticketId: number,
  payload: PredictionUpdate,
): Promise<AnalyzeResponse> {
  const params = new URLSearchParams({
    category: payload.category,
    priority: payload.priority,
    sentiment: payload.sentiment,
    confidence: String(payload.confidence),
  });

  const response = await fetch(`${API_BASE_URL}/tickets/${ticketId}/prediction?${params}`, {
    method: "PUT",
  });

  if (!response.ok) {
    throw new Error("Failed to update prediction");
  }

  return response.json();
}

export async function deleteTicket(ticketId: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/tickets/${ticketId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error("Failed to delete ticket");
  }
}