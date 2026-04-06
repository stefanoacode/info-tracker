import type { Category } from '../types'

interface Props {
  categories: Category[]
  selected: string | undefined
  onSelect: (category: string | undefined) => void
}

export default function CategoryFilter({ categories, selected, onSelect }: Props) {
  return (
    <div className="flex gap-2 mb-4">
      <button onClick={() => onSelect(undefined)} className={`px-3 py-1 text-sm rounded-md ${!selected ? 'bg-gray-700 text-white' : 'bg-gray-900 text-gray-400 hover:text-gray-200'}`}>All</button>
      {categories.map((cat) => (
        <button key={cat.id} onClick={() => onSelect(cat.name)} className={`px-3 py-1 text-sm rounded-md ${selected === cat.name ? 'bg-gray-700 text-white' : 'bg-gray-900 text-gray-400 hover:text-gray-200'}`}>{cat.name}</button>
      ))}
    </div>
  )
}
