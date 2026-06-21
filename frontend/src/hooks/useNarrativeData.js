import { useState, useEffect } from 'react'
import { DATA_PREFIX } from '../config'

const DATA_FILES = {
  narrativeSummary: `${DATA_PREFIX}data/narrative_summary.json`,
  narrativeData: `${DATA_PREFIX}data/narrative_data.json`,
  narrativeTypeAgg: `${DATA_PREFIX}data/narrative_type_aggregates.json`,
  narrativeComparison: `${DATA_PREFIX}data/narrative_comparison.json`,
  narrativeTemplates: `${DATA_PREFIX}data/narrative_templates.json`,
}

export function useNarrativeData() {
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
