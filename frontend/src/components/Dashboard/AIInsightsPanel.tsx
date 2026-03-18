import { useInsights } from '../../hooks/useMetrics'

export default function AIInsightsPanel() {
  const { data, isLoading } = useInsights()

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-100 p-6">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-2xl">🤖</span>
        <h3 className="text-base font-semibold text-gray-900">AI Insights</h3>
      </div>
      {isLoading ? (
        <div className="space-y-2">{[1, 2, 3].map(i => <div key={i} className="h-4 bg-blue-200 rounded animate-pulse" />)}</div>
      ) : (
        <div className="space-y-3">
          {data?.insights?.map((insight: { title: string; description: string }, i: number) => (
            <div key={i} className="bg-white rounded-lg p-3 shadow-sm">
              <p className="text-sm font-medium text-gray-800">{insight.title}</p>
              <p className="text-xs text-gray-500 mt-1">{insight.description}</p>
            </div>
          )) ?? (
            <p className="text-sm text-gray-500">No insights available. Connect your ad platforms to get started.</p>
          )}
        </div>
      )}
    </div>
  )
}
