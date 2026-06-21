import { useState, useEffect } from 'react'
import { DATA_PREFIX } from '../config'

const DATA_FILES = {
  summary: `${DATA_PREFIX}data/summary.json`,
  characterData: `${DATA_PREFIX}data/character_data.json`,
  matrixData: `${DATA_PREFIX}data/matrix_data.json`,
  eraData: `${DATA_PREFIX}data/era_data.json`,
  sankeyData: `${DATA_PREFIX}data/sankey_data.json`,
  overall: `${DATA_PREFIX}data/overall.json`,
}

export function useData() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function loadAll() {
      try {
        const results = {}
        for (const [key, url] of Object.entries(DATA_FILES)) {
          const res = await fetch(url)
          if (!res.ok) throw new Error(`Failed to load ${url}: ${res.status}`)
          results[key] = await res.json()
        }
        setData(results)
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    loadAll()
  }, [])

  return { data, loading, error }
}
