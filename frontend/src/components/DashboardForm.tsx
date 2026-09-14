import { useState } from "react";
import { ApiError, registerDashboard } from "../api";
import type {
  SummaryViewFormState,
  TableViewFormState,
} from "../defaults";
import type { ViewDefinition } from "../types";
import { onTabAutofill } from "../utils/tabAutofill";
import { ErrorDisplay } from "./ErrorDisplay";
import { TabLayout } from "./TabLayout";

const EMPTY_SUMMARY: SummaryViewFormState = {
  type: "summary",
  field: "",
  aggregation: "sum",
};

const EMPTY_TABLE: TableViewFormState = {
  type: "table",
  columns: "",
};

function toViewDefinitions(
  summaryViews: SummaryViewFormState[],
  tableViews: TableViewFormState[],
): ViewDefinition[] {
  const summaries: ViewDefinition[] = summaryViews.map((view) => ({
    type: "summary",
    field: view.field.trim(),
    aggregation: "sum",
  }));
  const tables: ViewDefinition[] = tableViews.map((view) => ({
    type: "table",
    columns: view.columns
      .split(",")
      .map((col) => col.trim())
      .filter(Boolean),
  }));
  return [...summaries, ...tables];
}

interface DashboardFormProps {
  name: string;
  schemaName: string;
  summaryViews: SummaryViewFormState[];
  tableViews: TableViewFormState[];
  onNameChange: (name: string) => void;
  onSchemaNameChange: (name: string) => void;
  onSummaryViewsChange: (views: SummaryViewFormState[]) => void;
  onTableViewsChange: (views: TableViewFormState[]) => void;
}

export function DashboardForm({
  name,
  schemaName,
  summaryViews,
  tableViews,
  onNameChange,
  onSchemaNameChange,
  onSummaryViewsChange,
  onTableViewsChange,
}: DashboardFormProps) {
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function updateSummary(index: number, patch: Partial<SummaryViewFormState>) {
    onSummaryViewsChange(
      summaryViews.map((view, i) =>
        i === index ? { ...view, ...patch } : view,
      ),
    );
  }

  function updateTable(index: number, patch: Partial<TableViewFormState>) {
    onTableViewsChange(
      tableViews.map((view, i) => (i === index ? { ...view, ...patch } : view)),
    );
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setSuccess(null);
    setError(null);

    try {
      const result = await registerDashboard({
        name: name.trim(),
        schema: schemaName.trim(),
        views: toViewDefinitions(summaryViews, tableViews),
      });
      setSuccess(`Dashboard "${result.name}" registered successfully.`);
    } catch (err) {
      setError(err instanceof ApiError ? err : new ApiError(0, "Unexpected error"));
    } finally {
      setSubmitting(false);
    }
  }

  const totalViews = summaryViews.length + tableViews.length;

  return (
    <TabLayout
      title="How to register a dashboard"
      instructions={[
        "Enter a unique dashboard name and the schema it references.",
        "Add summary views to aggregate numeric fields (sum only).",
        "Add table views to project specific columns from ingested rows.",
        "Field and column names must exist in the referenced schema.",
        "Configuration is validated at registration — errors appear before storage.",
        "Press Tab in an empty field to accept the suggested placeholder value.",
      ]}
    >
      <section className="card">
        <h2>Register Dashboard</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-section">
            <h3 className="section-heading">Dashboard details</h3>
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

            <label>
              Schema name
              <input
                type="text"
                value={schemaName}
                onChange={(e) => onSchemaNameChange(e.target.value)}
                onKeyDown={(e) => onTabAutofill(e, schemaName, onSchemaNameChange)}
                placeholder="trade"
                required
              />
            </label>
          </div>

          <fieldset>
            <legend>Views</legend>

            <div className="view-type-section">
              <div className="view-type-header">
                <h4>Summary views</h4>
                <p className="section-hint">
                  Aggregate a numeric field. Only <code>sum</code> is supported.
                </p>
              </div>

              {summaryViews.map((view, index) => (
                <div className="view-block view-block-summary" key={`summary-${index}`}>
                  <span className="view-badge">Summary #{index + 1}</span>
                  <label>
                    Field
                    <input
                      type="text"
                      value={view.field}
                      onChange={(e) => updateSummary(index, { field: e.target.value })}
                      onKeyDown={(e) =>
                        onTabAutofill(e, view.field, (value) =>
                          updateSummary(index, { field: value }),
                        )
                      }
                      placeholder="amount"
                      required
                    />
                  </label>
                  <label>
                    Aggregation
                    <select value="sum" disabled>
                      <option value="sum">sum</option>
                    </select>
                  </label>
                  <button
                    type="button"
                    className="btn-remove"
                    onClick={() =>
                      onSummaryViewsChange(
                        summaryViews.filter((_, i) => i !== index),
                      )
                    }
                    disabled={totalViews <= 1}
                  >
                    Remove summary
                  </button>
                </div>
              ))}

              <button
                type="button"
                className="btn-add"
                onClick={() =>
                  onSummaryViewsChange([...summaryViews, { ...EMPTY_SUMMARY }])
                }
              >
                Add summary view
              </button>
            </div>

            <div className="view-type-section">
              <div className="view-type-header">
                <h4>Table views</h4>
                <p className="section-hint">
                  Project columns from ingested rows. Enter comma-separated column names.
                </p>
              </div>

              {tableViews.map((view, index) => (
                <div className="view-block view-block-table" key={`table-${index}`}>
                  <span className="view-badge">Table #{index + 1}</span>
                  <label>
                    Columns (comma-separated)
                    <input
                      type="text"
                      value={view.columns}
                      onChange={(e) => updateTable(index, { columns: e.target.value })}
                      onKeyDown={(e) =>
                        onTabAutofill(e, view.columns, (value) =>
                          updateTable(index, { columns: value }),
                        )
                      }
                      placeholder="tradeId, amount, status"
                      required
                    />
                  </label>
                  <button
                    type="button"
                    className="btn-remove"
                    onClick={() =>
                      onTableViewsChange(tableViews.filter((_, i) => i !== index))
                    }
                    disabled={totalViews <= 1}
                  >
                    Remove table
                  </button>
                </div>
              ))}

              <button
                type="button"
                className="btn-add"
                onClick={() => onTableViewsChange([...tableViews, { ...EMPTY_TABLE }])}
              >
                Add table view
              </button>
            </div>
          </fieldset>

          <button type="submit" disabled={submitting}>
            {submitting ? "Registering…" : "Register dashboard"}
          </button>
        </form>

        {success && <div className="feedback feedback-success">{success}</div>}
        {error && (
          <ErrorDisplay
            title="Registration failed"
            message={error.message}
            details={error.details}
          />
        )}
      </section>
    </TabLayout>
  );
}
