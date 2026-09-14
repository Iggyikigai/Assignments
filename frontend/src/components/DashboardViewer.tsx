import { useState } from "react";
import { ApiError, getDashboard } from "../api";
import type { DashboardResult, TableViewResult, ViewResult } from "../types";
import { onTabAutofill } from "../utils/tabAutofill";
import { ErrorDisplay } from "./ErrorDisplay";
import { TabLayout } from "./TabLayout";

function SummaryViewDisplay({ view }: { view: ViewResult }) {
  if (view.type !== "summary") return null;

  const label = `Total ${view.field}`;
  const displayValue =
    view.value === null || view.value === undefined ? "No data" : String(view.value);

  return (
    <div className="summary-view">
      <h3>{label}</h3>
      <p className="summary-value">{displayValue}</p>
    </div>
  );
}

function TableViewDisplay({ view }: { view: ViewResult }) {
  if (view.type !== "table") return null;

  const tableView = view as TableViewResult;

  return (
    <div className="table-view">
      <h3>Table</h3>
      {tableView.rows.length === 0 ? (
        <p className="muted">No rows</p>
      ) : (
        <table>
          <thead>
            <tr>
              {tableView.columns.map((col) => (
                <th key={col}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {tableView.rows.map((row, index) => (
              <tr key={index}>
                {tableView.columns.map((col) => (
                  <td key={col}>
                    {row[col] === null || row[col] === undefined
                      ? ""
                      : String(row[col])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

interface DashboardViewerProps {
  name: string;
  onNameChange: (name: string) => void;
}

export function DashboardViewer({ name, onNameChange }: DashboardViewerProps) {
  const [result, setResult] = useState<DashboardResult | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleLoad(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const data = await getDashboard(name.trim());
      setResult(data);
    } catch (err) {
      setError(err instanceof ApiError ? err : new ApiError(0, "Unexpected error"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <TabLayout
      title="How to view a dashboard"
      instructions={[
        "Enter the name of a dashboard you registered.",
        "Click Load dashboard to fetch computed results from the backend.",
        "Summary views show aggregated totals; null means no data was ingested.",
        "Table views list projected columns in ingestion order.",
        "A warning appears when the schema has no ingested rows yet.",
        "Press Tab in an empty field to accept the suggested placeholder value.",
      ]}
    >
      <section className="card">
        <h2>View Dashboard</h2>
        <form onSubmit={handleLoad} className="inline-form">
          <label>
            Dashboard name
            <input
              type="text"
              value={name}
              onChange={(e) => onNameChange(e.target.value)}
              onKeyDown={(e) => onTabAutofill(e, name, onNameChange)}
              placeholder="trade-dashboard"
              required
            />
          </label>
          <button type="submit" disabled={loading}>
            {loading ? "Loading…" : "Load dashboard"}
          </button>
        </form>

        {error && (
          <ErrorDisplay title="Failed to load dashboard" message={error.message} />
        )}

        {result && (
          <div className="dashboard-result">
            <h3>{result.name}</h3>
            {result.warning && (
              <div className="feedback feedback-warning">{result.warning}</div>
            )}
            {result.views.map((view, index) =>
              view.type === "summary" ? (
                <SummaryViewDisplay key={index} view={view} />
              ) : (
                <TableViewDisplay key={index} view={view} />
              ),
            )}
          </div>
        )}
      </section>
    </TabLayout>
  );
}
