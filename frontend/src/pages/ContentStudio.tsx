import { useState } from 'react'
import CopyVariants from '../components/ContentStudio/CopyVariants'
import ImageUploader from '../components/ContentStudio/ImageUploader'
import { contentApi } from '../api/client'

export default function ContentStudio() {
  const [brief, setBrief] = useState({ product_name: '', target_audience: '', unique_value_prop: '', goal: 'leads', budget: 5000, tone: 'professional', language: 'en' })
  const [platform, setPlatform] = useState('facebook')
  const [copies, setCopies] = useState([])
  const [loading, setLoading] = useState(false)

  const generate = async () => {
    setLoading(true)
    try {
      const res = await contentApi.generate(brief, platform, 3)
      setCopies(res.data.copies)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Content Studio</h1>
        <p className="text-sm text-gray-500 mt-1">Generate AI-powered ad copy and images</p>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 space-y-4">
          <h3 className="font-semibold text-gray-900">Campaign Brief</h3>
          {[['product_name', 'Product Name'], ['target_audience', 'Target Audience'], ['unique_value_prop', 'Value Proposition']].map(([key, label]) => (
            <div key={key}>
              <label className="text-xs font-medium text-gray-600">{label}</label>
              <input className="mt-1 w-full border rounded-lg px-3 py-2 text-sm" value={(brief as Record<string, string>)[key]} onChange={e => setBrief(b => ({ ...b, [key]: e.target.value }))} />
            </div>
          ))}
          <div>
            <label className="text-xs font-medium text-gray-600">Platform</label>
            <select className="mt-1 w-full border rounded-lg px-3 py-2 text-sm" value={platform} onChange={e => setPlatform(e.target.value)}>
              {['facebook', 'instagram', 'google', 'tiktok'].map(p => <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>)}
            </select>
          </div>
          <button onClick={generate} disabled={loading} className="w-full bg-primary-600 text-white py-2 rounded-lg text-sm hover:bg-primary-700 disabled:opacity-50">
            {loading ? 'Generating...' : '✨ Generate Copy'}
          </button>
        </div>
        <div className="lg:col-span-2 space-y-4">
          <CopyVariants copies={copies} isLoading={loading} />
          <ImageUploader campaignId="new" />
        </div>
      </div>
    </div>
  )
}
