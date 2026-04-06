import { useEffect, useState } from 'react'
import { api } from '../api'
import type { FeedItem, Category } from '../types'
import ContentCard from '../components/ContentCard'
import CategoryFilter from '../components/CategoryFilter'

export default function Feed() {
  const [items, setItems] = useState<FeedItem[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>()
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getCategories().then(setCategories)
  }, [])

  useEffect(() => {
    setLoading(true)
    api.getFeed({ category: selectedCategory }).then((data) => {
      setItems(data)
      setLoading(false)
    })
  }, [selectedCategory])

  const handleRefresh = async () => {
    setLoading(true)
    await api.refreshCollection()
    const data = await api.getFeed({ category: selectedCategory })
    setItems(data)
    setLoading(false)
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Feed</h1>
        <button onClick={handleRefresh} className="px-3 py-1.5 text-sm bg-gray-800 hover:bg-gray-700 rounded-md">Refresh</button>
      </div>
      <CategoryFilter categories={categories} selected={selectedCategory} onSelect={setSelectedCategory} />
      {loading ? (
        <p className="text-gray-500 mt-8">Loading...</p>
      ) : items.length === 0 ? (
        <p className="text-gray-500 mt-8">No content yet. Try refreshing to collect data.</p>
      ) : (
        <div className="space-y-4 mt-4">
          {items.map((item) => (<ContentCard key={item.id} item={item} />))}
        </div>
      )}
    </div>
  )
}
