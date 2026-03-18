interface AdCopy {
  headline: string
  primary_text: string
  description: string
  cta: string
  platform: string
  variant_id: string
}

interface Props {
  copies: AdCopy[]
  isLoading: boolean
}

export default function CopyVariants({ copies, isLoading }: Props) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[1, 2, 3].map(i => <div key={i} className="bg-white rounded-xl border border-gray-100 h-48 animate-pulse" />)}
      </div>
    )
  }
  if (copies.length === 0) return null
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {copies.map((copy, i) => (
        <div key={copy.variant_id} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-medium text-primary-600 bg-primary-50 px-2 py-0.5 rounded-full">Variant {i + 1}</span>
            <span className="text-xs text-gray-400">{copy.platform}</span>
          </div>
          <p className="font-bold text-gray-900 text-sm">{copy.headline}</p>
          <p className="text-sm text-gray-600 mt-2">{copy.primary_text}</p>
          <p className="text-xs text-gray-400 mt-2">{copy.description}</p>
          <div className="mt-4 pt-3 border-t border-gray-50">
            <span className="text-xs bg-blue-600 text-white px-3 py-1 rounded-full">{copy.cta}</span>
          </div>
        </div>
      ))}
    </div>
  )
}
