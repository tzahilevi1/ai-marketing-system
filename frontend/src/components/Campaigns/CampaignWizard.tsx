import { useState } from 'react'
import { useCreateCampaign } from '../../hooks/useCampaigns'

interface Props {
  onClose: () => void
}

const GOALS = ['awareness', 'leads', 'sales', 'retention']
const TONES = ['professional', 'friendly', 'urgent', 'inspirational']

export default function CampaignWizard({ onClose }: Props) {
  const [step, setStep] = useState(1)
  const [form, setForm] = useState({
    product_name: '',
    target_audience: '',
    unique_value_prop: '',
    goal: 'leads',
    budget: 5000,
    tone: 'professional',
    brand_guidelines: '',
    language: 'en',
  })
  const createCampaign = useCreateCampaign()

  const handleSubmit = async () => {
    await createCampaign.mutateAsync(form)
    onClose()
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg p-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900">New Campaign — Step {step}/3</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl">×</button>
        </div>

        {step === 1 && (
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-700">Product / Service Name</label>
              <input className="mt-1 w-full border rounded-lg px-3 py-2 text-sm" value={form.product_name} onChange={e => setForm(f => ({ ...f, product_name: e.target.value }))} />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Target Audience</label>
              <input className="mt-1 w-full border rounded-lg px-3 py-2 text-sm" value={form.target_audience} onChange={e => setForm(f => ({ ...f, target_audience: e.target.value }))} />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Unique Value Proposition</label>
              <textarea className="mt-1 w-full border rounded-lg px-3 py-2 text-sm" rows={3} value={form.unique_value_prop} onChange={e => setForm(f => ({ ...f, unique_value_prop: e.target.value }))} />
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-700">Campaign Goal</label>
              <select className="mt-1 w-full border rounded-lg px-3 py-2 text-sm" value={form.goal} onChange={e => setForm(f => ({ ...f, goal: e.target.value }))}>
                {GOALS.map(g => <option key={g} value={g}>{g.charAt(0).toUpperCase() + g.slice(1)}</option>)}
              </select>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Budget ($)</label>
              <input type="number" className="mt-1 w-full border rounded-lg px-3 py-2 text-sm" value={form.budget} onChange={e => setForm(f => ({ ...f, budget: Number(e.target.value) }))} />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Tone</label>
              <select className="mt-1 w-full border rounded-lg px-3 py-2 text-sm" value={form.tone} onChange={e => setForm(f => ({ ...f, tone: e.target.value }))}>
                {TONES.map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
              </select>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-700">Brand Guidelines (optional)</label>
              <textarea className="mt-1 w-full border rounded-lg px-3 py-2 text-sm" rows={4} placeholder="Colors, fonts, messaging rules..." value={form.brand_guidelines} onChange={e => setForm(f => ({ ...f, brand_guidelines: e.target.value }))} />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Language</label>
              <select className="mt-1 w-full border rounded-lg px-3 py-2 text-sm" value={form.language} onChange={e => setForm(f => ({ ...f, language: e.target.value }))}>
                <option value="en">English</option>
                <option value="he">Hebrew (עברית)</option>
              </select>
            </div>
          </div>
        )}

        <div className="flex justify-between mt-8">
          <button onClick={() => step > 1 ? setStep(s => s - 1) : onClose()} className="text-sm text-gray-500 hover:text-gray-700">
            {step === 1 ? 'Cancel' : 'Back'}
          </button>
          {step < 3 ? (
            <button onClick={() => setStep(s => s + 1)} className="text-sm bg-primary-600 text-white px-5 py-2 rounded-lg hover:bg-primary-700">
              Next
            </button>
          ) : (
            <button onClick={handleSubmit} disabled={createCampaign.isPending} className="text-sm bg-green-600 text-white px-5 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50">
              {createCampaign.isPending ? 'Creating...' : 'Create Campaign'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
