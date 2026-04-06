export interface Category {
  id: number
  name: string
  description: string | null
  is_custom: boolean
  sort_order: number
}

export interface Person {
  id: number
  name: string
  bio: string | null
  avatar_url: string | null
  category_name: string
  platform_handles: Record<string, string>
  is_custom: boolean
}

export interface FeedItem {
  id: number
  person_name: string
  person_id: number
  category_name: string
  source_platform: string
  original_url: string
  ai_summary: string | null
  so_what: string | null
  topics: string[]
  published_at: string | null
  collected_at: string
  is_read: boolean
}

export interface Trend {
  id: number
  topic: string
  description: string
  related_content_ids: number[]
  detected_at: string
  time_range: string
  sentiment_score: number
  momentum_score: number
}

export interface Digest {
  items: DigestItem[]
  count: number
}

export interface DigestItem {
  person_name: string
  category_name: string
  source_platform: string
  original_url: string
  so_what: string | null
  ai_summary: string | null
  topics: string[]
  published_at: string | null
}
