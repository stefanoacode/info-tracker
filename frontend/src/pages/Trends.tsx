import { useEffect, useState } from 'react'
import { api } from '../api'
import type { Trend } from '../types'
import TrendChart from '../components/TrendChart'

export default function Trends() {
  const [trends, setTrends] = useState<Trend[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getTrends().then((data) => {
      setTrends(data)
      setLoading(false)
    })
  }, [])

  if (loading) return <p className="text-gray-500">Loading trends...</p>

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Trending Topics</h1>
      {trends.length === 0 ? (
        <p className="text-gray-500">No trends detected yet. Check back after more content is collected.</p>
      ) : (
        <>
          <TrendChart trends={trends} />
          <div className="space-y-4 mt-8">
            {trends.map((trend) => (
              <div key={trend.id} className="bg-gray-900 rounded-lg p-4 border border-gray-800">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-white">{trend.topic}</h3>
                  <div className="flex gap-3 text-xs text-gray-400">
                    <span>Momentum: {(trend.momentum_score * 100).toFixed(0)}%</span>
                    <span>Sentiment: {trend.sentiment_score > 0 ? '+' : ''}{trend.sentiment_score.toFixed(1)}</span>
                  </div>
                </div>
                <p className="text-sm text-gray-300">{trend.description}</p>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
