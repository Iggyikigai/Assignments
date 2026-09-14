import type { KeyboardEvent } from "react";

/**
 * UX feature: When Tab is pressed on an empty field, fill it with the suggested value
 * (placeholder or explicit suggestion) before focus moves to the next control.
 */
export function onTabAutofill(
  event: KeyboardEvent<HTMLInputElement | HTMLTextAreaElement>,
  currentValue: string,
  onFill: (value: string) => void,
  suggestion?: string,
): void {
  if (event.key !== "Tab" || event.shiftKey || currentValue.trim()) {
    return;
  }

  const suggested =
    suggestion ?? event.currentTarget.placeholder.trim();

  if (!suggested) {
    return;
  }

  onFill(suggested);
}
