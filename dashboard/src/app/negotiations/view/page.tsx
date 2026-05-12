import { Suspense } from "react";
import DealDetailClient from "@/components/deal-detail-client";

/**
 * Query-string based detail route: /negotiations/view?id=neg-xxxxxxxx
 *
 * We intentionally avoid the dynamic [id] pattern because the dashboard
 * is built with `output: "export"` — unknown dynamic IDs would 404. This
 * static route is safe for every id the backend hands out at runtime.
 *
 * The inner `DealDetailClient` calls `useSearchParams()`, which Next 16
 * requires to be wrapped in a Suspense boundary during static prerender.
 */
export default function DealDetailPage() {
  return (
    <Suspense fallback={<div className="p-6 text-xs text-[var(--color-text-faint)]">Loading…</div>}>
      <DealDetailClient />
    </Suspense>
  );
}
