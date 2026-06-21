import { useState, useEffect } from 'react'
import { DATA_PREFIX } from '../config'

const DATA_FILES = {
  networkSummary: `${DATA_PREFIX}data/network_summary.json`,
  networkComparison: `${DATA_PREFIX}data/network_comparison.json`,
  networkReps: `${DATA_PREFIX}data/network_representatives.json`,
  characterCentrality: `${DATA_PREFIX}data/character_centrality.json`,
  networksAll: `${DATA_PREFIX}data/networks_all.json`,
  networkTypeAgg: `${DATA_PREFIX}data/network_type_aggregates.json`,
}

export function useNetworkData() {
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
