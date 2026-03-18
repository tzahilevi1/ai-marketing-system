import { create } from 'zustand'

interface Campaign {
  id: string
  name: string
  status: string
  goal: string
}

interface AppState {
  campaigns: Campaign[]
  setCampaigns: (campaigns: Campaign[]) => void
  activeCampaignId: string | null
  setActiveCampaign: (id: string | null) => void
}

export const useAppStore = create<AppState>(set => ({
  campaigns: [],
  setCampaigns: campaigns => set({ campaigns }),
  activeCampaignId: null,
  setActiveCampaign: id => set({ activeCampaignId: id }),
}))
