import { useQuery } from '@tanstack/react-query'
import { analyticsApi } from '../api/client'

export function useMetrics() {
  return useQuery({
    queryKey: ['metrics'],
    queryFn: () => analyticsApi.metrics().then(r => r.data),
    refetchInterval: 60000,
  })
}

export function useInsights() {
  return useQuery({
    queryKey: ['insights'],
    queryFn: () => analyticsApi.insights().then(r => r.data),
  })
}
