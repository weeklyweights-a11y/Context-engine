import type { ReactNode } from "react";

interface EmptyStateProps {
  message: string;
  cta?: { label: string; onClick: () => void };
  actions?: ReactNode;
}

export default function EmptyState({ message, cta, actions }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <p className="text-gray-400 dark:text-gray-500 mb-4">{message}</p>
      {actions}
      {!actions && cta && (
        <button
          onClick={cta.onClick}
          className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg"
        >
          {cta.label}
        </button>
      )}
    </div>
  );
}
