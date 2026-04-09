import DealDetailClient from "@/components/deal-detail-client";

export function generateStaticParams() {
  return [{ id: "neg-047" }, { id: "neg-046" }, { id: "neg-045" }];
}

export default function DealDetailPage() {
  return <DealDetailClient />;
}
