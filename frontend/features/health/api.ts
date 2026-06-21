import { apiGet } from "@/lib/api-client";
import type { HealthResponse } from "./types";

export function getHealth(): Promise<HealthResponse> {
  return apiGet<HealthResponse>("/api/health");
}