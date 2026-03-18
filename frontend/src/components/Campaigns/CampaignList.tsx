interface Campaign {
  id: string
  name: string
  status: string
  goal: string
}

interface Props {
  campaigns: Campaign[]
  onLaunch: (id: string) => void
}

const STATUS_COLORS: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-700',
  active: 'bg-green-100 text-green-700',
  paused: 'bg-yellow-100 text-yellow-700',
  completed: 'bg-blue-100 text-blue-700',
}

export default function CampaignList({ campaigns, onLaunch }: Props) {
  if (campaigns.length === 0) {
    return <div className="text-center py-12 text-gray-500">No campaigns yet. Create your first campaign!</div>
  }
  return (
    <div className="space-y-3">
      {campaigns.map(c => (
        <div key={c.id} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 flex items-center justify-between">
          <div>
            <p className="font-semibold text-gray-900">{c.name}</p>
            <div className="flex items-center gap-2 mt-1">
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_COLORS[c.status] ?? 'bg-gray-100 text-gray-700'}`}>
                {c.status}
              </span>
              <span className="text-xs text-gray-400">{c.goal}</span>
            </div>
          </div>
          {c.status === 'draft' && (
            <button
              onClick={() => onLaunch(c.id)}
              className="text-sm bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors"
            >
              Launch
            </button>
          )}
        </div>
      ))}
    </div>
  )
}
