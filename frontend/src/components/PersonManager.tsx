import { useState } from 'react'
import { api } from '../api'
import type { Person, Category } from '../types'

interface Props {
  people: Person[]
  categories: Category[]
  onUpdate: () => void
}

export default function PersonManager({ people, categories, onUpdate }: Props) {
  const [showForm, setShowForm] = useState(false)
  const [name, setName] = useState('')
  const [bio, setBio] = useState('')
  const [categoryName, setCategoryName] = useState('')
  const [handles, setHandles] = useState<Record<string, string>>({ x: '', youtube: '', substack: '', reddit: '' })

  const handleAdd = async () => {
    if (!name || !categoryName) return
    const platform_handles: Record<string, string> = {}
    for (const [k, v] of Object.entries(handles)) {
      if (v.trim()) platform_handles[k] = v.trim()
    }
    await api.addPerson({ name, bio, category_name: categoryName, platform_handles })
    setName('')
    setBio('')
    setHandles({ x: '', youtube: '', substack: '', reddit: '' })
    setShowForm(false)
    onUpdate()
  }

  const handleDelete = async (id: number) => {
    await api.deletePerson(id)
    onUpdate()
  }

  return (
    <div className="mt-4">
      <button onClick={() => setShowForm(!showForm)} className="px-3 py-1.5 text-sm bg-blue-600 hover:bg-blue-500 rounded-md mb-4">{showForm ? 'Cancel' : '+ Add Person'}</button>
      {showForm && (
        <div className="bg-gray-900 rounded-lg p-4 border border-gray-800 mb-4 space-y-3">
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Name" className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm" />
          <input value={bio} onChange={(e) => setBio(e.target.value)} placeholder="Bio (optional)" className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm" />
          <select value={categoryName} onChange={(e) => setCategoryName(e.target.value)} className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm">
            <option value="">Select category</option>
            {categories.map((c) => (<option key={c.id} value={c.name}>{c.name}</option>))}
          </select>
          <div className="grid grid-cols-2 gap-2">
            {Object.keys(handles).map((platform) => (
              <input key={platform} value={handles[platform]} onChange={(e) => setHandles({ ...handles, [platform]: e.target.value })} placeholder={`${platform} handle`} className="bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm" />
            ))}
          </div>
          <button onClick={handleAdd} className="px-3 py-1.5 text-sm bg-green-600 hover:bg-green-500 rounded-md">Save</button>
        </div>
      )}
      <div className="space-y-2">
        {people.map((p) => (
          <div key={p.id} className="flex items-center justify-between bg-gray-900 rounded-lg px-4 py-3 border border-gray-800">
            <div>
              <span className="font-medium text-white">{p.name}</span>
              <span className="text-xs text-gray-500 ml-2">{p.category_name}</span>
              {p.bio && <p className="text-xs text-gray-400 mt-0.5">{p.bio}</p>}
              <div className="flex gap-2 mt-1">
                {Object.entries(p.platform_handles).map(([platform, handle]) => (
                  <span key={platform} className="text-xs text-gray-500">{platform}: {handle}</span>
                ))}
              </div>
            </div>
            <button onClick={() => handleDelete(p.id)} className="text-xs text-red-400 hover:text-red-300">Remove</button>
          </div>
        ))}
      </div>
    </div>
  )
}
