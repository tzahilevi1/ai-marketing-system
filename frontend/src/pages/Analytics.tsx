import FunnelChart from '../components/Analytics/FunnelChart'
import NLQAChat from '../components/Analytics/NLQAChat'
import { useMetrics } from '../hooks/useMetrics'
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const COLORS = ['#3b82f6', '#ef4444', '#10b981']

export default function Analytics() {
  const { data: metrics } = useMetrics()
  const platformData = metrics?.by_platform
    ? Object.entries(metrics.by_platform).map(([name, d]: [string, { spend?: number }]) => ({ name: name.charAt(0).toUpperCase() + name.slice(1), value: d.spend ?? 0 }))
    : [{ name: 'Meta', value: 6000 }, { name: 'Google', value: 3000 }, { name: 'TikTok', value: 1000 }]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="text-sm text-gray-500 mt-1">Deep performance analysis</p>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <FunnelChart />
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <h3 className="text-base font-semibold text-gray-900 mb-4">Spend by Platform</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={platformData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                {platformData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip formatter={(v: number) => `$${v.toLocaleString()}`} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
      <NLQAChat />
    </div>
  )
}
