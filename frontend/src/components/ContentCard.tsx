import type { FeedItem } from '../types'

const platformColors: Record<string, string> = {
  x: 'text-blue-400',
  youtube: 'text-red-400',
  substack: 'text-orange-400',
  reddit: 'text-yellow-400',
}

export default function ContentCard({ item }: { item: FeedItem }) {
  return (
    <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="font-medium text-white">{item.person_name}</span>
          <span className="text-xs text-gray-500">{item.category_name}</span>
          <span className={`text-xs ${platformColors[item.source_platform] || 'text-gray-400'}`}>{item.source_platform}</span>
        </div>
        {item.published_at && (<span className="text-xs text-gray-500">{new Date(item.published_at).toLocaleDateString()}</span>)}
      </div>
      {item.so_what && (<p className="text-sm font-medium text-gray-200 mb-2">{item.so_what}</p>)}
      {item.ai_summary && (<p className="text-sm text-gray-400 mb-3 whitespace-pre-line">{item.ai_summary}</p>)}
      <div className="flex items-center justify-between">
        <div className="flex gap-1.5">
          {item.topics.map((topic) => (<span key={topic} className="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded">{topic}</span>))}
        </div>
        <a href={item.original_url} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-400 hover:text-blue-300">Source</a>
      </div>
    </div>
  )
}
