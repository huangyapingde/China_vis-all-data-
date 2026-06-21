import React, { useEffect, useRef, useState } from 'react'
import * as echarts from 'echarts'

const STAGE_COLORS = {
  opening: 'rgba(79,195,247,0.15)',
  development: 'rgba(255,183,77,0.15)',
  climax: 'rgba(239,83,80,0.2)',
  resolution: 'rgba(129,199,132,0.15)',
}
const STAGE_LABELS = {
  opening: '开端', development: '发展', climax: '高潮', resolution: '结局',
}

export default function NarrativeCurve({ data, onScriptChange }) {
  const chartRef = useRef(null)
  const instanceRef = useRef(null)
  const [activeScript, setActiveScript] = useState(null)
  const [scripts, setScripts] = useState([])
  const [selectedCategory, setSelectedCategory] = useState('全部')

  const handleScriptChange = (id) => {
    setActiveScript(id)
    if (onScriptChange) onScriptChange(id)
  }

  useEffect(() => {
    if (!data?.narrativeData?.narratives) return
    const nars = data.narrativeData.narratives
    setScripts(nars)
    if (nars.length > 0) handleScriptChange(nars[0].script_id)
  }, [data])

  useEffect(() => {
    if (!activeScript || !chartRef.current) return

    const nar = data.narrativeData.narratives.find(n => n.script_id === activeScript)
    if (!nar) return

    if (instanceRef.current) instanceRef.current.dispose()
    instanceRef.current = echarts.init(chartRef.current, null, { renderer: 'canvas' })

    const curve = nar.narrative_curve
    const stages = nar.stages
    const xData = nar.scenes.map((_, i) => `S${i + 1}`)

    // Mark stage bands
    const markAreas = []
    let stageStart = 0
    for (let i = 1; i <= stages.length; i++) {
      if (i === stages.length || stages[i] !== stages[stageStart]) {
        const stage = stages[stageStart]
        markAreas.push([
          { xAxis: `S${stageStart + 1}`, itemStyle: { color: STAGE_COLORS[stage] } },
          { xAxis: `S${i}` },
        ])
        stageStart = i
      }
    }

    const option = {
      title: {
        text: `${nar.title} (${nar.type})`,
        subtext: `${STAGE_LABELS[nar.structure_type]} · 高潮位置: ${(nar.climax_position * 100).toFixed(0)}%`,
        textStyle: { color: '#e0e6ed', fontSize: 13 },
        subtextStyle: { color: '#546e7a', fontSize: 11 },
        left: 'center',
        top: 0,
      },
      tooltip: { trigger: 'axis' },
      legend: {
        data: ['叙事张力', '冲突强度', '事件密度', '情绪强度'],
        textStyle: { color: '#8899aa', fontSize: 10 },
        top: 40,
      },
      grid: { left: 55, right: 65, top: 80, bottom: 50 },
      xAxis: {
        type: 'category',
        data: xData,
        axisLabel: { color: '#8899aa', fontSize: 9 },
        name: '场景推进',
        nameTextStyle: { color: '#546e7a', fontSize: 10 },
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: '#8899aa' },
        splitLine: { lineStyle: { color: '#1e2d3d' } },
      },
      series: [
        {
          name: '叙事张力', type: 'line',
          data: curve.tension,
          lineStyle: { color: '#ff7043', width: 2.5 },
          itemStyle: { color: '#ff7043' },
          symbol: 'circle', symbolSize: 4,
          markArea: { silent: true, data: markAreas },
          markPoint: {
            data: [{
              type: 'max', name: '高潮', symbol: 'pin', symbolSize: 30,
              itemStyle: { color: '#ef5350' }, label: { color: '#fff', fontSize: 10 }
            }],
          },
        },
        {
          name: '冲突强度', type: 'line',
          data: curve.conflict_smooth,
          lineStyle: { color: '#ef5350', width: 1.5, type: 'dashed' },
          symbol: 'none',
        },
        {
          name: '事件密度', type: 'line',
          data: curve.event_smooth,
          lineStyle: { color: '#42a5f5', width: 1.5, type: 'dashed' },
          symbol: 'none',
        },
        {
          name: '情绪强度', type: 'line',
          data: curve.emotion,
          lineStyle: { color: '#ab47bc', width: 1.5, type: 'dotted' },
          symbol: 'none',
        },
      ],
    }

    instanceRef.current.setOption(option, true)
  }, [activeScript, data])

  useEffect(() => {
    const handleResize = () => instanceRef.current?.resize()
    window.addEventListener('resize', handleResize)
    return () => {
      window.removeEventListener('resize', handleResize)
      instanceRef.current?.dispose()
    }
  }, [])

  if (scripts.length === 0) return <div style={{ color: '#546e7a', padding: 20, textAlign: 'center' }}>暂无数据</div>

  const categories = ['全部', ...new Set(scripts.map(s => s.type).filter(Boolean))]
  const filteredScripts = selectedCategory === '全部'
    ? scripts
    : scripts.filter(s => s.type === selectedCategory)

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
              const newScripts = cat === '全部' ? scripts : scripts.filter(s => s.type === cat)
              if (newScripts.length > 0) handleScriptChange(newScripts[0].script_id)
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
            onChange={(e) => handleScriptChange(e.target.value)}
            style={{
              padding: '4px 8px', borderRadius: 4, background: '#1a2634', color: '#e0e6ed',
              border: '1px solid #2a3a4a', fontSize: '0.75rem', outline: 'none', maxWidth: 220, cursor: 'pointer'
            }}
          >
            {filteredScripts.map(s => (
              <option key={s.script_id} value={s.script_id}>{s.title || s.script_id}</option>
            ))}
          </select>
        </div>
      </div>
      <div ref={chartRef} style={{ flex: 1, width: '100%', minHeight: 350 }} />
    </div>
  )
}
