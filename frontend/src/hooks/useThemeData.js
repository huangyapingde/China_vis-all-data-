import { useState, useEffect } from 'react'
import { DATA_PREFIX } from '../config'

const DATA_FILES = {
  themeSummary: `${DATA_PREFIX}data/theme_summary.json`,
  themeScriptDist: `${DATA_PREFIX}data/theme_script_distributions.json`,
  themeCooc: `${DATA_PREFIX}data/theme_cooccurrence.json`,
  themeSpace: `${DATA_PREFIX}data/theme_topic_space.json`,
  themeTypeComp: `${DATA_PREFIX}data/theme_type_comparison.json`,
  themeEvolution: `${DATA_PREFIX}data/theme_evolution.json`,
  themeSankey: `${DATA_PREFIX}data/theme_sankey.json`,
  themeLLM: `${DATA_PREFIX}data/theme_llm_labels.json`,
}

export function useThemeData() {
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
