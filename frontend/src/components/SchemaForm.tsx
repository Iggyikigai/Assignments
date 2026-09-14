import { useState } from "react";
import { ApiError, registerSchema } from "../api";
import { DEFAULT_SCHEMA_FIELDS } from "../defaults";
import type { FieldDefinition, FieldType } from "../types";
import { onTabAutofill } from "../utils/tabAutofill";
import { ErrorDisplay } from "./ErrorDisplay";
import { TabLayout } from "./TabLayout";

const EMPTY_FIELD: FieldDefinition = {
  name: "",
  type: "string",
  required: false,
};

interface SchemaFormProps {
  name: string;
  fields: FieldDefinition[];
  onNameChange: (name: string) => void;
  onFieldsChange: (fields: FieldDefinition[]) => void;
}

export function SchemaForm({
  name,
  fields,
  onNameChange,
  onFieldsChange,
}: SchemaFormProps) {
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function updateField(index: number, patch: Partial<FieldDefinition>) {
    onFieldsChange(
      fields.map((field, i) => (i === index ? { ...field, ...patch } : field)),
    );
  }

  function addField() {
    onFieldsChange([...fields, { ...EMPTY_FIELD }]);
  }

  function removeField(index: number) {
    onFieldsChange(fields.filter((_, i) => i !== index));
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setSuccess(null);
    setError(null);

    try {
      const payload = {
        name: name.trim(),
        fields: fields
          .filter((field) => field.name.trim())
          .map((field) => {
            const entry: FieldDefinition = {
              name: field.name.trim(),
              type: field.type,
              required: field.required ?? false,
            };
            if (field.aggregation) {
              entry.aggregation = field.aggregation;
            }
            return entry;
          }),
      };

      const result = await registerSchema(payload);
      setSuccess(`Schema "${result.name}" registered successfully.`);
    } catch (err) {
      setError(err instanceof ApiError ? err : new ApiError(0, "Unexpected error"));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <TabLayout
      title="How to register a schema"
      instructions={[
        "Enter a unique schema name (e.g. trade).",
        "Add one or more fields with a name and type (string, number, or boolean).",
        "Mark fields as required if they must be present in every ingested row.",
        "Aggregation metadata is optional and descriptive only.",
        "Click Register schema — duplicate names return a 409 conflict.",
        "Press Tab in an empty field to accept the suggested placeholder value.",
      ]}
    >
      <section className="card">
        <h2>Register Schema</h2>
        <form onSubmit={handleSubmit}>
          <label>
            Schema name
            <input
              type="text"
              value={name}
              onChange={(e) => onNameChange(e.target.value)}
              onKeyDown={(e) => onTabAutofill(e, name, onNameChange)}
              placeholder="trade"
              required
            />
          </label>

          <fieldset>
            <legend>Fields</legend>
            {fields.map((field, index) => (
              <div className="field-row" key={index}>
                <input
                  type="text"
                  value={field.name}
                  onChange={(e) => updateField(index, { name: e.target.value })}
                  onKeyDown={(e) =>
                    onTabAutofill(
                      e,
                      field.name,
                      (value) => updateField(index, { name: value }),
                      DEFAULT_SCHEMA_FIELDS[index]?.name,
                    )
                  }
                  placeholder={DEFAULT_SCHEMA_FIELDS[index]?.name ?? "field name"}
                  aria-label={`Field ${index + 1} name`}
                />
                <select
                  value={field.type}
                  onChange={(e) =>
                    updateField(index, { type: e.target.value as FieldType })
                  }
                  aria-label={`Field ${index + 1} type`}
                >
                  <option value="string">string</option>
                  <option value="number">number</option>
                  <option value="boolean">boolean</option>
                </select>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={field.required ?? false}
                    onChange={(e) => updateField(index, { required: e.target.checked })}
                  />
                  required
                </label>
                <select
                  value={field.aggregation ?? ""}
                  onChange={(e) =>
                    updateField(index, {
                      aggregation: e.target.value
                        ? (e.target.value as "sum")
                        : undefined,
                    })
                  }
                  aria-label={`Field ${index + 1} aggregation`}
                >
                  <option value="">no aggregation</option>
                  <option value="sum">sum</option>
                </select>
                <button
                  type="button"
                  className="btn-remove"
                  onClick={() => removeField(index)}
                  disabled={fields.length === 1}
                >
                  Remove
                </button>
              </div>
            ))}
            <button type="button" className="btn-add" onClick={addField}>
              Add field
            </button>
          </fieldset>

          <button type="submit" disabled={submitting}>
            {submitting ? "Registering…" : "Register schema"}
          </button>
        </form>

        {success && <div className="feedback feedback-success">{success}</div>}
        {error && (
          <ErrorDisplay
            title={
              error.code === "VALIDATION_ERROR" ? "Validation failed" : "Registration failed"
            }
            message={error.message}
            details={error.details}
          />
        )}
      </section>
    </TabLayout>
  );
}
