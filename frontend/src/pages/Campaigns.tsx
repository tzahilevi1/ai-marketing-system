import { useState } from 'react'
import { useCampaigns } from '../hooks/useCampaigns'
import CampaignList from '../components/Campaigns/CampaignList'
import CampaignWizard from '../components/Campaigns/CampaignWizard'
import { campaignsApi } from '../api/client'
import { useQueryClient } from '@tanstack/react-query'

export default function Campaigns() {
  const { data: campaigns = [], isLoading } = useCampaigns()
  const [showWizard, setShowWizard] = useState(false)
  const qc = useQueryClient()

  const handleLaunch = async (id: string) => {
    await campaignsApi.launch(id)
    qc.invalidateQueries({ queryKey: ['campaigns'] })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Campaigns</h1>
          <p className="text-sm text-gray-500 mt-1">{campaigns.length} campaigns total</p>
        </div>
        <button onClick={() => setShowWizard(true)} className="bg-primary-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-primary-700">
          + New Campaign
        </button>
      </div>
      {isLoading ? <div className="text-center py-12 text-gray-400">Loading campaigns...</div> : <CampaignList campaigns={campaigns} onLaunch={handleLaunch} />}
      {showWizard && <CampaignWizard onClose={() => setShowWizard(false)} />}
    </div>
  )
}
