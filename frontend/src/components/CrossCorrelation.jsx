import React, { useMemo } from 'react'
import ReactEChartsCore from 'echarts-for-react'

const CAT_COLORS = {
  '网络': '#4fc3f7',
  '主题': '#81c784',
  '叙事': '#ffb74d',
}

export default function CrossCorrelation({ data }) {
  const { summary } = data || {}
  const matrix = summary?.correlation_matrix || {}
  const dimNames = summary?.dimension_names || []
  const dimCats = summary?.dimension_categories || []

  const option = useMemo(() => {
    const n = dimNames.length
    if (n === 0) return {}

    // Build heatmap data
    const heatData = []
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        heatData.push([j, i, matrix[dimNames[i]]?.[dimNames[j]] || 0])
      }
    }

    return {
      tooltip: {
        position: 'top',
        formatter: (p) => {
          const x = dimNames[p.value[0]]
          const y = dimNames[p.value[1]]
          return `<strong>${y} × ${x}</strong><br/>相关系数: <strong>${p.value[2].toFixed(4)}</strong>`
        },
      },
      grid: { left: 140, right: 30, top: 30, bottom: 100 },
      xAxis: {
        type: 'category',
        data: dimNames,
        splitArea: { show: true },
        axisLabel: { rotate: 45, fontSize: 10, color: '#8899aa', interval: 0 },
        axisLine: { show: false },
      },
      yAxis: {
        type: 'category',
        data: [...dimNames].reverse(),
        splitArea: { show: true },
        axisLabel: { fontSize: 10, color: '#8899aa' },
        axisLine: { show: false },
      },
      visualMap: {
        min: -1,
        max: 1,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: 0,
        inRange: {
          color: ['#d32f2f', '#ff8a80', '#f5f5f5', '#81d4fa', '#1565c0'],
        },
        textStyle: { color: '#8899aa' },
      },
      series: [{
        type: 'heatmap',
        data: heatData,
        label: {
          show: true,
          fontSize: 9,
          color: '#e0e6ed',
          formatter: (p) => p.value[2].toFixed(2),
        },
        emphasis: {
          itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' },
        },
      }],
    }
  }, [matrix, dimNames])

  return (
    <div>
      <ReactEChartsCore option={option} style={{ height: 560 }} notMerge />
      <div style={{ display: 'flex', gap: 16, justifyContent: 'center', marginTop: 8 }}>
        {Object.entries(CAT_COLORS).map(([cat, color]) => (
          <span key={cat} style={{ fontSize: '0.75rem', color: '#8899aa' }}>
            <span style={{ display: 'inline-block', width: 10, height: 10, borderRadius: 2, background: color, marginRight: 4 }} />
            {cat}
          </span>
        ))}
      </div>
    </div>
  )
}
