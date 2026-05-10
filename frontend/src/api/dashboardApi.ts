import { API_BASE_URL } from "./client";
import type { DashboardSummary } from "../types/dashboard";

export async function getDashboardSummary(): Promise<DashboardSummary> {
  const response = await fetch(`${API_BASE_URL}/dashboard/summary`);

  if (!response.ok) {
    throw new Error("Failed to load dashboard");
  }

  return response.json();
}