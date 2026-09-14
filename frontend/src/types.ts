export type FieldType = "string" | "number" | "boolean";

export interface FieldDefinition {
  name: string;
  type: FieldType;
  required?: boolean;
  aggregation?: "sum";
}

export interface SchemaPayload {
  name: string;
  fields: FieldDefinition[];
}

export interface IngestPayload {
  schema: string;
  rows: Record<string, unknown>[];
}

export interface SummaryView {
  type: "summary";
  field: string;
  aggregation: "sum";
}

export interface TableView {
  type: "table";
  columns: string[];
}

export type ViewDefinition = SummaryView | TableView;

export interface DashboardPayload {
  name: string;
  schema: string;
  views: ViewDefinition[];
}

export interface ValidationErrorDetail {
  row?: number;
  field?: string;
  code?: string;
  message: string;
}

export interface ApiErrorBody {
  error?: string;
  message?: string;
  details?: ValidationErrorDetail[] | unknown[];
}

export interface SummaryViewResult {
  type: "summary";
  field: string;
  aggregation: "sum";
  value: number | null;
}

export interface TableViewResult {
  type: "table";
  columns: string[];
  rows: Record<string, unknown>[];
}

export type ViewResult = SummaryViewResult | TableViewResult;

export interface DashboardResult {
  name: string;
  warning?: string;
  views: ViewResult[];
}
