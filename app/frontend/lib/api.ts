import axios from "axios";
import { ChatResponse, AlertsResponse } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

// ── Chat ────────────────────────────────────────────────────

export async function sendChatMessage(
  query: string,
  options: {
    userId?: string;
    sessionId?: string;
    platforms?: string[];
  } = {}
): Promise<ChatResponse> {
  const response = await api.post("/api/chat", {
    query,
    user_id: options.userId || "guest",
    session_id: options.sessionId || "default",
    platforms: options.platforms || ["amazon", "flipkart", "myntra"],
  });
  return response.data;
}

// ── Alerts ──────────────────────────────────────────────────

export async function getAlerts(userId: string): Promise<AlertsResponse> {
  const response = await api.get(`/api/alerts/${userId}`);
  return response.data;
}

export async function createAlert(
  userId: string,
  userQuery: string
): Promise<any> {
  const response = await api.post("/api/alerts", {
    user_id: userId,
    user_query: userQuery,
  });
  return response.data;
}

export async function deleteAlert(alertId: string): Promise<any> {
  const response = await api.delete(`/api/alerts/${alertId}`);
  return response.data;
}

export async function pauseAlert(alertId: string): Promise<any> {
  const response = await api.patch(`/api/alerts/${alertId}/pause`);
  return response.data;
}