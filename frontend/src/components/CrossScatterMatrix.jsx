import React, { useMemo } from 'react'
import ReactEChartsCore from 'echarts-for-react'

const TYPE_COLORS = {
  '历史戏': '#ff7043',
  '家庭戏': '#42a5f5',
  '公案戏': '#66bb6a',
  '神话戏': '#ab47bc',
}

export default function CrossScatterMatrix({ data }) {
  const scripts = data?.scripts || []

  // Pick key dimensions for scatter matrix
  const dims = [
    { key: 'cooc_centralization', label: '中心化程度', cat: '网络' },
    { key: 'power_density', label: '权力密度', cat: '网络' },
    { key: 'cooc_modularity', label: '模块度', cat: '网络' },
    { key: 'theme_entropy', label: '主题熵', cat: '主题' },
    { key: 'climax_position', label: '高潮位置', cat: '叙事' },
    { key: 'tension_std', label: '张力波动', cat: '叙事' },
  ]

  const option = useMemo(() => {
    const n = dims.length
    if (n === 0 || scripts.length === 0) return {}

    const grid = []
    const xAxes = []
    const yAxes = []
    const series = []

    // Collect types for color mapping
    const types = [...new Set(scripts.map(s => s.type || '其他'))]

    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        if (i === j) continue // skip diagonal
        const idx = i * (n - 1) + (j < i ? j : j - 1)

        grid.push({
          left: `${j * 15 + 3}%`,
          top: `${i * 15 + 3}%`,
          width: '13%',
          height: '13%',
          show: true,
          backgroundColor: 'rgba(255,255,255,0.02)',
          borderColor: '#1a2634',
          borderWidth: 1,
        })

        xAxes.push({
          type: 'value',
          gridIndex: idx,
          show: j === 0,
          axisLabel: { fontSize: 8, color: '#8899aa' },
          splitLine: { show: false },
          name: j === 0 ? dims[i].label : '',
          nameLocation: 'center',
          nameGap: 20,
          nameTextStyle: { fontSize: 9, color: '#8899aa' },
        })

        yAxes.push({
          type: 'value',
          gridIndex: idx,
          show: i === 0,
          axisLabel: { fontSize: 8, color: '#8899aa' },
          splitLine: { show: false },
          name: i === 0 ? dims[j].label : '',
          nameLocation: 'center',
          nameGap: 20,
          nameTextStyle: { fontSize: 9, color: '#8899aa' },
        })

        const scatterData = scripts.map(s => ({
          value: [s[dims[j].key] || 0, s[dims[i].key] || 0],
          itemStyle: { color: TYPE_COLORS[s.type] || '#546e7a' },
        }))

        series.push({
          type: 'scatter',
          xAxisIndex: idx,
          yAxisIndex: idx,
          data: scatterData,
          symbolSize: 3,
          animation: false,
          emphasis: {
            scale: 2,
            label: {
              show: true,
              formatter: (p) => scripts[p.dataIndex]?.title || '',
              fontSize: 10,
            },
          },
        })
      }
    }

    // Add diagonal labels
    for (let i = 0; i < n; i++) {
      grid.push({
        left: `${i * 15 + 3}%`,
        top: `${i * 15 + 3}%`,
        width: '13%',
        height: '13%',
        show: true,
        backgroundColor: 'rgba(255,255,255,0.01)',
        borderColor: '#1a2634',
        borderWidth: 1,
      })
      series.push({
        type: 'scatter',
        xAxisIndex: n * (n - 1) + i,
        yAxisIndex: n * (n - 1) + i,
        data: [],
        label: {
          show: true,
          position: 'center',
          fontSize: 11,
          color: '#8899aa',
          fontWeight: 600,
          formatter: dims[i].label,
        },
      })
      xAxes.push({ type: 'value', gridIndex: n * (n - 1) + i, show: false })
      yAxes.push({ type: 'value', gridIndex: n * (n - 1) + i, show: false })
    }

    return {
      tooltip: {
        formatter: (p) => {
          const s = scripts[p.dataIndex]
          if (!s) return ''
          return `<strong>${s.title}</strong> (${s.type})<br/>
            ${dims[p.seriesIndex % n]?.label || ''}: ${p.value[1].toFixed(3)}<br/>
            ${dims[Math.floor(p.seriesIndex / n)]?.label || ''}: ${p.value[0].toFixed(3)}`
        },
      },
      grid,
      xAxis: xAxes,
      yAxis: yAxes,
      series,
      legend: {
        data: Object.entries(TYPE_COLORS).map(([name, color]) => ({ name, itemStyle: { color } })),
        top: 0,
        left: 'center',
        textStyle: { color: '#8899aa', fontSize: 11 },
        itemWidth: 12,
        itemHeight: 8,
      },
    }
  }, [scripts])

  return (
    <div>
      <ReactEChartsCore option={option} style={{ height: 650 }} notMerge />
      <div style={{ fontSize: '0.75rem', color: '#546e7a', textAlign: 'center', marginTop: 4 }}>
        对角标签 = 维度名称 · 每个散点 = 一个剧本 · 颜色 = 剧种 · 悬停查看详情
      </div>
    </div>
  )
}
