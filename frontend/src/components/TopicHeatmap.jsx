import React, { useEffect, useRef } from 'react'
import * as echarts from 'echarts'

export default function TopicHeatmap({ data, selectedType }) {
  const chartRef = useRef(null)
  const instanceRef = useRef(null)

  useEffect(() => {
    if (!data?.themeTypeComp?.matrix) return
    const { types, themes, matrix } = data.themeTypeComp

    // Show selected type or all
    const displayTypes = selectedType ? [selectedType] : types

    // Build heatmap data
    const heatData = []
    const displayThemes = themes.slice(0, 12)
    let maxVal = 0

    displayTypes.forEach((t, ti) => {
      displayThemes.forEach((th, ci) => {
        const v = (matrix[t]?.[th] || 0) * 100
        heatData.push([ci, ti, v])
        if (v > maxVal) maxVal = v
      })
    })

    if (!instanceRef.current) {
      instanceRef.current = echarts.init(chartRef.current, null, { renderer: 'canvas' })
    }

    const option = {
      tooltip: {
        formatter: (params) => {
          const theme = displayThemes[params.value[0]]
          const type = displayTypes[params.value[1]]
          return `<strong>${type}</strong> × <strong>${theme}</strong><br/>强度: ${params.value[2].toFixed(1)}%`
        },
      },
      grid: { left: 80, right: 60, top: 10, bottom: 70 },
      xAxis: {
        type: 'category',
        data: displayThemes,
        axisLabel: { color: '#8899aa', fontSize: 10, rotate: 30 },
        axisLine: { lineStyle: { color: '#2a3a4a' } },
      },
      yAxis: {
        type: 'category',
        data: displayTypes,
        axisLabel: { color: '#8899aa', fontSize: 11 },
        axisLine: { lineStyle: { color: '#2a3a4a' } },
      },
      visualMap: {
        min: 0,
        max: Math.max(maxVal, 1),
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: 0,
        textStyle: { color: '#8899aa' },
        inRange: { color: ['#0d1b2a', '#0d47a1', '#1976d2', '#42a5f5', '#bbdefb'] },
      },
      series: [{
        type: 'heatmap',
        data: heatData,
        label: {
          show: true,
          color: '#e0e6ed',
          fontSize: 9,
          formatter: p => p.value[2] > 1 ? p.value[2].toFixed(0) : '',
        },
      }],
    }

    instanceRef.current.setOption(option, true)
  }, [data, selectedType])

  useEffect(() => {
    const handleResize = () => instanceRef.current?.resize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return <div ref={chartRef} className="chart-container" />
}
