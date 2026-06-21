import React, { useEffect, useRef, useState } from 'react'
import * as echarts from 'echarts'

const THEME_COLORS = [
  '#ff7043', '#42a5f5', '#66bb6a', '#ab47bc', '#ffca28',
  '#ef5350', '#26c6da', '#8d6e63', '#7986cb', '#4db6ac',
  '#f48fb1', '#a1887f', '#90a4ae', '#ce93d8', '#81c784',
]

export default function TopicTimeline({ data }) {
  const chartRef = useRef(null)
  const instanceRef = useRef(null)
  const [activeScript, setActiveScript] = useState(null)
  const [scripts, setScripts] = useState([])
  const [selectedCategory, setSelectedCategory] = useState('全部')

  // On mount, pick first script
  useEffect(() => {
    if (!data?.themeEvolution) return
    const evo = data.themeEvolution
    const ids = Object.keys(evo)
    setScripts(ids)
    if (ids.length > 0) {
      setActiveScript(ids[0])
    }
  }, [data])

  // Render chart when activeScript or chartRef changes
  useEffect(() => {
    if (!activeScript || !chartRef.current) return
    const evo = data?.themeEvolution
    if (!evo || !evo[activeScript]) return

    const script = evo[activeScript]
    const { timeline, title, type } = script
    if (!timeline || timeline.length === 0) return

    // Dispose old instance if exists
    if (instanceRef.current) {
      instanceRef.current.dispose()
    }

    instanceRef.current = echarts.init(chartRef.current, null, { renderer: 'canvas' })

    // Collect all themes across scenes
    const themeSet = new Set()
    timeline.forEach(sc => {
      sc.top_themes?.forEach(t => themeSet.add(t.theme))
    })
    const allThemes = [...themeSet].slice(0, 8)

    const option = {
      title: {
        text: `${title} (${type})`,
        textStyle: { color: '#e0e6ed', fontSize: 13 },
        left: 'center',
        top: 0,
      },
      tooltip: {
        trigger: 'axis',
        formatter: (params) => {
          let html = `<strong>Scene ${params[0].name}</strong><br/>`
          params.sort((a, b) => b.value - a.value).forEach(p => {
            if (p.value > 0) {
              html += `${p.marker}${p.seriesName}: ${(p.value * 100).toFixed(1)}%<br/>`
            }
          })
          return html
        },
      },
      grid: { left: 40, right: 10, top: 40, bottom: 40, containLabel: true },
      xAxis: {
        type: 'category',
        data: timeline.map(t => `S${t.scene_id}`),
        axisLabel: { color: '#8899aa', fontSize: 9, interval: 0, rotate: 45 },
        name: '场次推进',
        nameTextStyle: { color: '#546e7a', fontSize: 10 },
      },
      yAxis: {
        type: 'value',
        name: '主题强度',
        max: 1,
        axisLabel: { color: '#8899aa' },
        splitLine: { lineStyle: { color: '#1e2d3d' } },
      },
      series: allThemes.map((theme, i) => ({
        name: theme,
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 4,
        color: THEME_COLORS[i % THEME_COLORS.length],
        lineStyle: { width: 2 },
        areaStyle: { opacity: 0.05 },
        data: timeline.map(sc => {
          const hit = sc.top_themes?.find(t => t.theme === theme)
          return hit ? hit.strength : 0
        }),
      })),
    }

    instanceRef.current.setOption(option, true)
  }, [activeScript, data])

  // Resize handler
  useEffect(() => {
    const handleResize = () => instanceRef.current?.resize()
    window.addEventListener('resize', handleResize)
    return () => {
      window.removeEventListener('resize', handleResize)
      instanceRef.current?.dispose()
    }
  }, [])

  if (scripts.length === 0) {
    return <div style={{ color: '#546e7a', padding: 20, textAlign: 'center' }}>暂无演化数据</div>
  }

  const evo = data?.themeEvolution
  const categories = ['全部', ...new Set(scripts.map(id => evo?.[id]?.type).filter(Boolean))]

  const filteredScripts = selectedCategory === '全部'
    ? scripts
    : scripts.filter(id => evo?.[id]?.type === selectedCategory)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* 下拉选择栏 */}
      <div style={{ display: 'flex', gap: 16, marginBottom: 12, borderBottom: '1px solid #1e2d3d', paddingBottom: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ color: '#8899aa', fontSize: '0.75rem' }}>题材筛选:</span>
          <select
            value={selectedCategory}
            onChange={(e) => {
              const cat = e.target.value
              setSelectedCategory(cat)
              const newScripts = cat === '全部' ? scripts : scripts.filter(id => evo?.[id]?.type === cat)
              if (newScripts.length > 0) setActiveScript(newScripts[0])
            }}
            style={{
              padding: '4px 8px', borderRadius: 4, background: '#1a2634', color: '#e0e6ed',
              border: '1px solid #2a3a4a', fontSize: '0.75rem', outline: 'none', cursor: 'pointer'
            }}
          >
            {categories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
          </select>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ color: '#8899aa', fontSize: '0.75rem' }}>具体剧本:</span>
          <select
            value={activeScript || ''}
            onChange={(e) => setActiveScript(e.target.value)}
            style={{
              padding: '4px 8px', borderRadius: 4, background: '#1a2634', color: '#e0e6ed',
              border: '1px solid #2a3a4a', fontSize: '0.75rem', outline: 'none', maxWidth: 220, cursor: 'pointer'
            }}
          >
            {filteredScripts.map(sid => (
              <option key={sid} value={sid}>{evo?.[sid]?.title || sid}</option>
            ))}
          </select>
        </div>
      </div>
      <div ref={chartRef} style={{ flex: 1, width: '100%', minHeight: 300 }} />
    </div>
  )
}
