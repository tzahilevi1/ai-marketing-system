import axios from 'axios'

export const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export const contentApi = {
  generate: (brief: object, platform: string, variants = 3) =>
    api.post('/content/generate', { brief, platform, variants }),
  abVariants: (original: string, count = 5) =>
    api.post('/content/ab-variants', null, { params: { original, count } }),
}

export const campaignsApi = {
  list: () => api.get('/campaigns/'),
  create: (brief: object) => api.post('/campaigns/', brief),
  launch: (id: string) => api.post(`/campaigns/${id}/launch`),
}

export const analyticsApi = {
  metrics: () => api.get('/analytics/metrics'),
  insights: () => api.get('/analytics/insights'),
  ask: (question: string) => api.post('/analytics/ask', null, { params: { question } }),
  report: (period = 'weekly') => api.get('/analytics/report', { params: { period } }),
}

export const imagesApi = {
  upload: (campaignId: string, file: File) => {
    const form = new FormData()
    form.append('campaign_id', campaignId)
    form.append('file', file)
    return api.post('/images/upload', form, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  generate: (brief: string, platform = 'instagram_square') =>
    api.post('/images/generate', null, { params: { campaign_brief: brief, platform } }),
}
