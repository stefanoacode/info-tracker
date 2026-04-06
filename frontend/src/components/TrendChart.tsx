import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import type { Trend } from '../types'

export default function TrendChart({ trends }: { trends: Trend[] }) {
  const data = trends.map((t) => ({
    name: t.topic,
    momentum: Math.round(t.momentum_score * 100),
    sentiment: Math.round((t.sentiment_score + 1) * 50),
  }))

  return (
    <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
      <h3 className="text-sm font-medium text-gray-400 mb-4">Topic Momentum</h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data}>
          <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 12 }} />
          <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} />
          <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: 8 }} labelStyle={{ color: '#f3f4f6' }} />
          <Bar dataKey="momentum" fill="#3b82f6" name="Momentum %" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
