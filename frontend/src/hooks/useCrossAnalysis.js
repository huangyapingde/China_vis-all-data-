import { useState, useEffect } from 'react'
import { DATA_PREFIX } from '../config'

const DATA_FILE = `${DATA_PREFIX}data/cross_analysis.json`

export function useCrossAnalysis() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch(DATA_FILE)
        if (!res.ok) throw new Error(`Failed to load ${DATA_FILE}: ${res.status}`)
        const json = await res.json()
        setData(json)
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  return { data, loading, error }
}
