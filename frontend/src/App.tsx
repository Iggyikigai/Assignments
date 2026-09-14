import { useState } from "react";
import {
  type SummaryViewFormState,
  type TableViewFormState,
} from "./defaults";
import { DashboardForm } from "./components/DashboardForm";
import { DashboardViewer } from "./components/DashboardViewer";
import { IngestForm } from "./components/IngestForm";
import { SchemaForm } from "./components/SchemaForm";
import type { FieldDefinition } from "./types";

type Tab = "schema" | "ingest" | "dashboard" | "view";

const TABS: { id: Tab; label: string; description: string }[] = [
  {
    id: "schema",
    label: "Register Schema",
    description: "Define field names, types, and validation rules",
  },
  {
    id: "ingest",
    label: "Ingest Data",
    description: "Submit JSON rows against a registered schema",
  },
  {
    id: "dashboard",
    label: "Register Dashboard",
    description: "Configure summary and table views",
  },
  {
    id: "view",
    label: "View Dashboard",
    description: "Load and render dashboard results",
  },
];

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>("schema");

  const [schemaName, setSchemaName] = useState("");
  const [schemaFields, setSchemaFields] = useState<FieldDefinition[]>([
    { name: "", type: "string", required: false },
  ]);

  const [ingestSchemaName, setIngestSchemaName] = useState("");
  const [rowsJson, setRowsJson] = useState("");

  const [dashboardName, setDashboardName] = useState("");
  const [dashboardSchemaName, setDashboardSchemaName] = useState("");
  const [summaryViews, setSummaryViews] = useState<SummaryViewFormState[]>([
    { type: "summary", field: "", aggregation: "sum" },
  ]);
  const [tableViews, setTableViews] = useState<TableViewFormState[]>([
    { type: "table", columns: "" },
  ]);

  const [viewerDashboardName, setViewerDashboardName] = useState("");

  return (
    <div className="app">
      <header>
        <h1>Schema-Driven Dashboard Platform</h1>
        <p className="subtitle">
          Register schemas, ingest rows, configure dashboards, and view results.
        </p>
      </header>

      <nav className="tabs" aria-label="Main sections">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            className={`tab tab-${tab.id}${activeTab === tab.id ? " active" : ""}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="tab-label">{tab.label}</span>
            {activeTab === tab.id && (
              <span className="tab-description">{tab.description}</span>
            )}
          </button>
        ))}
      </nav>

      <main className={`workflow workflow-${activeTab}`}>
        {activeTab === "schema" && (
          <SchemaForm
            name={schemaName}
            fields={schemaFields}
            onNameChange={setSchemaName}
            onFieldsChange={setSchemaFields}
          />
        )}
        {activeTab === "ingest" && (
          <IngestForm
            schemaName={ingestSchemaName}
            rowsJson={rowsJson}
            onSchemaNameChange={setIngestSchemaName}
            onRowsJsonChange={setRowsJson}
          />
        )}
        {activeTab === "dashboard" && (
          <DashboardForm
            name={dashboardName}
            schemaName={dashboardSchemaName}
            summaryViews={summaryViews}
            tableViews={tableViews}
            onNameChange={setDashboardName}
            onSchemaNameChange={setDashboardSchemaName}
            onSummaryViewsChange={setSummaryViews}
            onTableViewsChange={setTableViews}
          />
        )}
        {activeTab === "view" && (
          <DashboardViewer
            name={viewerDashboardName}
            onNameChange={setViewerDashboardName}
          />
        )}
      </main>
    </div>
  );
}
