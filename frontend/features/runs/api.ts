import { apiGet, apiPost } from "@/lib/api-client";
import type {
  RunCreateRequest,
  RunCreateResponse,
  RunListResponse,
} from "./types";

export function createRun(
  payload: RunCreateRequest,
): Promise<RunCreateResponse> {
  return apiPost<RunCreateResponse, RunCreateRequest>("/api/runs", payload);
}

export function listRuns(): Promise<RunListResponse> {
  return apiGet<RunListResponse>("/api/runs");
}