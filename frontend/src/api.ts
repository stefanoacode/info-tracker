import type { Category, Person, FeedItem, Trend, Digest } from './types'

const BASE = '/api'

async function fetchJSON<T>(url: string): Promise<T> {
  const resp = await fetch(`${BASE}${url}`)
  if (!resp.ok) throw new Error(`API error: ${resp.status}`)
  return resp.json()
}

export const api = {
  getCategories: () => fetchJSON<Category[]>('/categories'),
  getPeople: (category?: string) =>
    fetchJSON<Person[]>(category ? `/people?category=${category}` : '/people'),
  addPerson: async (data: { name: string; bio?: string; category_name: string; platform_handles: Record<string, string> }) => {
    const resp = await fetch(`${BASE}/people`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!resp.ok) throw new Error(`API error: ${resp.status}`)
    return resp.json() as Promise<Person>
  },
  deletePerson: async (id: number) => {
    await fetch(`${BASE}/people/${id}`, { method: 'DELETE' })
  },
  getFeed: (params?: { category?: string; platform?: string; limit?: number; offset?: number }) => {
    const qs = new URLSearchParams()
    if (params?.category) qs.set('category', params.category)
    if (params?.platform) qs.set('platform', params.platform)
    if (params?.limit) qs.set('limit', String(params.limit))
    if (params?.offset) qs.set('offset', String(params.offset))
    const query = qs.toString()
    return fetchJSON<FeedItem[]>(`/feed${query ? `?${query}` : ''}`)
  },
  getTrends: (timeRange?: string) =>
    fetchJSON<Trend[]>(timeRange ? `/trends?time_range=${timeRange}` : '/trends'),
  getDigest: (category?: string) =>
    fetchJSON<Digest>(category ? `/digest?category=${category}` : '/digest'),
  refreshCollection: async () => {
    const resp = await fetch(`${BASE}/collect/refresh`, { method: 'POST' })
    return resp.json()
  },
}
