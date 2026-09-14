import type { FieldDefinition } from "./types";

export const DEFAULT_SCHEMA_NAME = "trade";

export const DEFAULT_SCHEMA_FIELDS: FieldDefinition[] = [
  { name: "tradeId", type: "string", required: true },
  { name: "amount", type: "number", required: true },
  { name: "status", type: "string", required: false },
];

export const DEFAULT_ROWS_JSON = `[
  {
    "tradeId": "T001",
    "amount": 1000,
    "status": "OPEN"
  },
  {
    "tradeId": "T002",
    "amount": 2500,
    "status": "CLOSED"
  }
]`;

export const DEFAULT_DASHBOARD_NAME = "trade-dashboard";

export type SummaryViewFormState = {
  type: "summary";
  field: string;
  aggregation: "sum";
};

export type TableViewFormState = {
  type: "table";
  columns: string;
};

export const DEFAULT_SUMMARY_VIEWS: SummaryViewFormState[] = [
  { type: "summary", field: "amount", aggregation: "sum" },
];

export const DEFAULT_TABLE_VIEWS: TableViewFormState[] = [
  { type: "table", columns: "tradeId, amount, status" },
];
