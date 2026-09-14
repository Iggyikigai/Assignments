import type { ValidationErrorDetail } from "../types";

interface ErrorDisplayProps {
  title?: string;
  message?: string;
  details?: ValidationErrorDetail[];
}

export function ErrorDisplay({ title = "Error", message, details }: ErrorDisplayProps) {
  if (!message && (!details || details.length === 0)) {
    return null;
  }

  return (
    <div className="feedback feedback-error" role="alert">
      <strong>{title}</strong>
      {message && <p>{message}</p>}
      {details && details.length > 0 && (
        <ul className="error-list">
          {details.map((detail, index) => (
            <li key={`${detail.row}-${detail.field}-${index}`}>
              {detail.row !== undefined && `Row ${detail.row}`}
              {detail.field && ` — ${detail.field}`}
              {detail.message && `: ${detail.message}`}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
