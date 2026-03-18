import KPICards from '../components/Dashboard/KPICards'
import TrendChart from '../components/Dashboard/TrendChart'
import AIInsightsPanel from '../components/Dashboard/AIInsightsPanel'
import { useMetrics } from '../hooks/useMetrics'

export default function Dashboard() {
  const { data: metrics } = useMetrics()
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">Your marketing performance at a glance</p>
      </div>
      <KPICards metrics={metrics ?? null} />
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <TrendChart />
        </div>
        <AIInsightsPanel />
      </div>
    </div>
  )
}
