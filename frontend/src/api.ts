import type {
  ApiErrorBody,
  DashboardPayload,
  DashboardResult,
  IngestPayload,
  SchemaPayload,
  ValidationErrorDetail,
} from "./types";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;
  code?: string;
  details?: ValidationErrorDetail[];

  constructor(
    status: number,
    message: string,
    code?: string,
    details?: ValidationErrorDetail[],
  ) {
    super(message);
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    const text = await response.text();
    const body: ApiErrorBody | T = text ? JSON.parse(text) : {};

    if (!response.ok) {
      const errorBody = body as ApiErrorBody;
      const details = Array.isArray(errorBody.details)
        ? (errorBody.details as ValidationErrorDetail[])
        : undefined;
      throw new ApiError(
        response.status,
        errorBody.message ?? errorBody.error ?? `Request failed (${response.status})`,
        errorBody.error,
        details,
      );
    }

    return body as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(0, "Network error — is the backend running?");
  }
}

export function registerSchema(payload: SchemaPayload): Promise<{ name: string }> {
  return request("/schema", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function ingestData(payload: IngestPayload): Promise<{ ingested: number }> {
  return request("/ingest", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function registerDashboard(
  payload: DashboardPayload,
): Promise<{ name: string }> {
  return request("/dashboard", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getDashboard(name: string): Promise<DashboardResult> {
  return request(`/dashboard/${encodeURIComponent(name)}`);
}
