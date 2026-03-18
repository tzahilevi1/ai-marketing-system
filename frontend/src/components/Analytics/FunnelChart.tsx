import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

const FUNNEL_DATA = [
  { stage: 'Impressions', value: 500000, color: '#3b82f6' },
  { stage: 'Clicks', value: 15000, color: '#6366f1' },
  { stage: 'Leads', value: 1500, color: '#8b5cf6' },
  { stage: 'Purchases', value: 350, color: '#a855f7' },
]

export default function FunnelChart() {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
      <h3 className="text-base font-semibold text-gray-900 mb-4">Conversion Funnel</h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={FUNNEL_DATA} layout="vertical">
          <XAxis type="number" tick={{ fontSize: 11 }} />
          <YAxis dataKey="stage" type="category" tick={{ fontSize: 12 }} width={80} />
          <Tooltip formatter={(v: number) => v.toLocaleString()} />
          <Bar dataKey="value" radius={[0, 4, 4, 0]}>
            {FUNNEL_DATA.map((entry, i) => <Cell key={i} fill={entry.color} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
