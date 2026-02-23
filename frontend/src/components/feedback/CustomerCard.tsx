import { Link } from "react-router-dom";
import { AlertCircle } from "lucide-react";
import type { Customer } from "../../types/customer";

function healthColor(score: number | undefined): string {
  if (score == null) return "text-gray-400";
  if (score >= 70) return "text-green-400";
  if (score >= 40) return "text-amber-400";
  return "text-red-400";
}

function daysToRenewal(renewalDate: string | undefined): number | null {
  if (!renewalDate) return null;
  const r = new Date(renewalDate);
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  r.setHours(0, 0, 0, 0);
  return Math.ceil((r.getTime() - now.getTime()) / (24 * 60 * 60 * 1000));
}

function formatCurrency(n: number | undefined): string {
  if (n == null) return "—";
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `$${(n / 1_000).toFixed(1)}K`;
  return `$${n}`;
}

interface CustomerCardProps {
  customer: Customer | null;
  className?: string;
}

export function CustomerCard({ customer, className = "" }: CustomerCardProps) {
  if (!customer) return null;

  const days = daysToRenewal(customer.renewal_date);
  const renewalWarning = days != null && days < 60 && days >= 0;

  return (
    <div className={`rounded-lg border border-gray-600 bg-gray-800/50 p-4 ${className}`}>
      <Link
        to={`/customers/${customer.id}`}
        className="font-medium text-indigo-400 hover:text-indigo-300 hover:underline"
      >
        {customer.company_name}
      </Link>
      <div className="mt-2 space-y-1 text-sm text-gray-300">
        {customer.segment && (
          <span className="mr-2 rounded bg-gray-700 px-2 py-0.5 text-gray-400">{customer.segment}</span>
        )}
        {(customer.mrr != null || customer.arr != null) && (
          <p>
            MRR {formatCurrency(customer.mrr)} / ARR {formatCurrency(customer.arr)}
          </p>
        )}
        {customer.health_score != null && (
          <p>
            Health: <span className={healthColor(customer.health_score)}>{customer.health_score}</span>
          </p>
        )}
        {customer.account_manager && <p>Manager: {customer.account_manager}</p>}
        {customer.renewal_date && (
          <p className="flex items-center gap-1">
            Renewal: {new Date(customer.renewal_date).toLocaleDateString()}
            {renewalWarning && <AlertCircle className="h-4 w-4 text-amber-500" aria-label="Renewal soon" />}
          </p>
        )}
      </div>
    </div>
  );
}
