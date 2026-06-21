import React, { useMemo } from 'react'
import ReactEChartsCore from 'echarts-for-react'

export default function CrossParallel({ data }) {
  const scripts = data?.scripts || []
  const clusters = data?.clusters || []

  const clusterColorMap = useMemo(() => {
    const map = {}
    clusters.forEach(c => {
      c.representatives?.forEach(r => { map[r.script_id] = c.color })
    })
    return map
  }, [clusters])

  const option = useMemo(() => {
    if (scripts.length === 0) return {}

    const dims = [
      { key: 'cooc_centralization', label: '中心化', min: 0, max: 1 },
      { key: 'power_density', label: '权力密度', min: 0, max: 0.5 },
      { key: 'cooc_modularity', label: '模块度', min: 0, max: 1 },
      { key: 'cooc_clustering', label: '聚集系数', min: 0, max: 1 },
      { key: 'theme_entropy', label: '主题熵', min: 0, max: 4 },
      { key: 'theme_count', label: '主题数', min: 0, max: 15 },
      { key: 'climax_position', label: '高潮位置', min: 0, max: 1 },
      { key: 'tension_std', label: '张力波动', min: 0, max: 0.5 },
      { key: 'character_count', label: '角色数', min: 0, max: 30 },
    ]

    // Assign colors by cluster membership
    const scriptClusters = {}
    clusters.forEach(c => {
      c.representatives?.forEach(r => {
        scriptClusters[r.script_id] = c.color
      })
    })

    // Sample data (limit for performance)
    const maxPoints = 300
    const step = Math.max(1, Math.floor(scripts.length / maxPoints))
    const sampled = scripts.filter((_, i) => i % step === 0)

    const lineData = sampled.map(s => {
      const color = scriptClusters[s.script_id] || '#546e7a'
      return {
        value: dims.map(d => s[d.key] || 0),
        lineStyle: { color, width: 1, opacity: 0.4 },
        itemStyle: { color },
        _title: s.title,
        _type: s.type,
      }
    })

    return {
      tooltip: {
        formatter: (p) => {
          const d = p.data
          if (!d || !d._title) return ''
          return `<strong>${d._title}</strong> (${d._type})<br/>` +
            dims.map((dim, i) => `${dim.label}: ${d.value[i]?.toFixed(3)}`).join('<br/>')
        },
      },
      parallel: {
        left: '5%',
        right: '8%',
        bottom: '5%',
        top: '5%',
        parallelAxisDefault: {
          type: 'value',
          nameTextStyle: { color: '#8899aa', fontSize: 11 },
          axisLabel: { color: '#546e7a', fontSize: 9 },
          splitLine: { show: false },
          nameLocation: 'end',
        },
      },
      parallelAxis: dims.map(d => ({
        dim: dims.indexOf(d),
        name: d.label,
        min: d.min,
        max: d.max,
      })),
      series: [{
        type: 'parallel',
        lineStyle: { width: 1, opacity: 0.35 },
        data: lineData,
        emphasis: {
          lineStyle: { width: 3, opacity: 0.9 },
        },
      }],
      legend: {
        data: clusters.map(c => ({
          name: c.name,
          itemStyle: { color: c.color },
        })),
        top: 0,
        left: 'center',
        textStyle: { color: '#8899aa', fontSize: 11 },
      },
    }
  }, [scripts, clusters])

  return (
    <div>
      <ReactEChartsCore option={option} style={{ height: 500 }} notMerge />
      <div style={{ fontSize: '0.75rem', color: '#546e7a', textAlign: 'center', marginTop: 4 }}>
        每条折线 = 一个剧本 · 颜色 = 聚类归属 · 悬停查看剧本详情
      </div>
    </div>
  )
}
