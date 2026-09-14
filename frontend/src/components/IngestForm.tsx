import { useState } from "react";
import { ApiError, ingestData } from "../api";
import { DEFAULT_ROWS_JSON } from "../defaults";
import { onTabAutofill } from "../utils/tabAutofill";
import { ErrorDisplay } from "./ErrorDisplay";
import { TabLayout } from "./TabLayout";

interface IngestFormProps {
  schemaName: string;
  rowsJson: string;
  onSchemaNameChange: (name: string) => void;
  onRowsJsonChange: (json: string) => void;
}

export function IngestForm({
  schemaName,
  rowsJson,
  onSchemaNameChange,
  onRowsJsonChange,
}: IngestFormProps) {
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [parseError, setParseError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setSuccess(null);
    setError(null);
    setParseError(null);

    let rows: Record<string, unknown>[];
    try {
      const parsed = JSON.parse(rowsJson);
      if (!Array.isArray(parsed)) {
        throw new Error("Rows must be a JSON array.");
      }
      rows = parsed;
    } catch (err) {
      setParseError(
        err instanceof Error ? err.message : "Invalid JSON in rows textarea.",
      );
      setSubmitting(false);
      return;
    }

    try {
      const result = await ingestData({ schema: schemaName.trim(), rows });
      setSuccess(`Ingested ${result.ingested} row(s) successfully.`);
    } catch (err) {
      setError(err instanceof ApiError ? err : new ApiError(0, "Unexpected error"));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <TabLayout
      title="How to ingest data"
      instructions={[
        "Enter the schema name you registered earlier.",
        "Paste rows as a JSON array in the textarea.",
        "Each row object must match the schema field names and types exactly.",
        "The backend validates all rows before saving — a failed batch writes nothing.",
        "Validation errors show the row index, field, and message.",
        "Press Tab in an empty field to accept the suggested placeholder value.",
      ]}
    >
      <section className="card">
        <h2>Ingest Data</h2>
        <form onSubmit={handleSubmit}>
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

          <label>
            Rows (JSON array)
            <textarea
              value={rowsJson}
              onChange={(e) => onRowsJsonChange(e.target.value)}
              onKeyDown={(e) =>
                onTabAutofill(e, rowsJson, onRowsJsonChange, DEFAULT_ROWS_JSON)
              }
              rows={12}
              spellCheck={false}
              placeholder='[{"tradeId": "T001", "amount": 1000}]'
            />
          </label>

          <button type="submit" disabled={submitting}>
            {submitting ? "Ingesting…" : "Ingest rows"}
          </button>
        </form>

        {parseError && <ErrorDisplay title="Invalid JSON" message={parseError} />}
        {success && <div className="feedback feedback-success">{success}</div>}
        {error && (
          <ErrorDisplay
            title={
              error.code === "VALIDATION_ERROR" || error.details
                ? "Validation failed"
                : "Ingestion failed"
            }
            message={error.message}
            details={error.details}
          />
        )}
      </section>
    </TabLayout>
  );
}
