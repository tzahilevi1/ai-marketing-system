interface KPIs {
  total_spend: number
  total_revenue: number
  roas: number
  total_conversions: number
  cpa: number
}

interface Props {
  metrics: KPIs | null
}

function KPICard({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <p className="text-sm text-gray-500 font-medium">{label}</p>
      <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  )
}

export default function KPICards({ metrics }: Props) {
  if (!metrics) return <div className="grid grid-cols-5 gap-4">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="bg-white rounded-xl h-28 animate-pulse" />)}</div>
  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
      <KPICard label="Total Spend" value={`$${metrics.total_spend.toLocaleString()}`} />
      <KPICard label="Revenue" value={`$${metrics.total_revenue.toLocaleString()}`} />
      <KPICard label="ROAS" value={`${metrics.roas.toFixed(2)}x`} sub="Return on ad spend" />
      <KPICard label="Conversions" value={metrics.total_conversions.toLocaleString()} />
      <KPICard label="CPA" value={`$${metrics.cpa.toFixed(2)}`} sub="Cost per acquisition" />
    </div>
  )
}
