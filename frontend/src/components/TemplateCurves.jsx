import React, { useEffect, useRef } from 'react'
import * as echarts from 'echarts'

const TYPE_COLORS = {
  '历史戏': '#ff7043', '家庭戏': '#42a5f5', '公案戏': '#66bb6a', '神话戏': '#ab47bc',
}

export default function TemplateCurves({ data }) {
  const chartRef = useRef(null)
  const instanceRef = useRef(null)

  useEffect(() => {
    if (!data?.narrativeTemplates) return
    const templates = data.narrativeTemplates
    const types = Object.keys(templates)

    if (!instanceRef.current) {
      instanceRef.current = echarts.init(chartRef.current, null, { renderer: 'canvas' })
    }

    const xLabels = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10', 'S11', 'S12']

    const option = {
      tooltip: {
        trigger: 'item',
        formatter: (params) => {
          return `<div style="font-weight:bold;color:${params.color}">${params.seriesName}</div>
                  ${params.name}：${Number(params.value).toFixed(3)}`
        }
      },
      legend: {
        data: types,
        textStyle: { color: '#8899aa', fontSize: 11 },
        top: 0,
        itemWidth: 16,
        itemHeight: 8,
      },
      grid: { left: 55, right: 80, top: 40, bottom: 40 },
      xAxis: {
        type: 'category',
        data: xLabels,
        axisLabel: { color: '#8899aa', fontSize: 9 },
        name: '叙事进度',
        nameTextStyle: { color: '#546e7a', fontSize: 10 },
      },
      yAxis: {
        type: 'value',
        name: '平均张力',
        scale: true, // This allows the Y-axis to adapt automatically instead of starting from 0
        axisLabel: { color: '#8899aa' },
        splitLine: { lineStyle: { color: '#1e2d3d' } },
      },
      series: types.map(t => ({
        name: t,
        type: 'line',
        smooth: true,
        data: templates[t].avg_curve,
        lineStyle: { color: TYPE_COLORS[t] || '#78909c', width: 2.5 },
        itemStyle: { color: TYPE_COLORS[t] },
        symbol: 'circle',
        symbolSize: 4,
        // Remove areaStyle to reduce visual clutter on a single chart
        emphasis: {
          focus: 'series', // Highlights this series and fades others on hover
          lineStyle: { width: 4 }
        },
        markLine: {
          silent: true,
          symbol: 'none',
          label: { show: false },
          data: [{ type: 'max' }],
        },
      })),
    }

    instanceRef.current.setOption(option, true)
  }, [data])

  useEffect(() => {
    const handleResize = () => instanceRef.current?.resize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return <div ref={chartRef} className="chart-container" style={{ minHeight: 300 }} />
}
