import { useEffect, useState } from 'react'
import { api } from '../api'
import type { Person, Category } from '../types'
import PersonManager from '../components/PersonManager'
import CategoryFilter from '../components/CategoryFilter'

export default function People() {
  const [people, setPeople] = useState<Person[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>()

  const loadPeople = () => { api.getPeople(selectedCategory).then(setPeople) }

  useEffect(() => { api.getCategories().then(setCategories) }, [])
  useEffect(() => { loadPeople() }, [selectedCategory])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">People</h1>
      <CategoryFilter categories={categories} selected={selectedCategory} onSelect={setSelectedCategory} />
      <PersonManager people={people} categories={categories} onUpdate={loadPeople} />
    </div>
  )
}
