import React, { useEffect, useRef } from 'react'
import * as echarts from 'echarts'

const TYPE_COLORS = {
  '历史戏': '#ff7043', '家庭戏': '#42a5f5',
  '公案戏': '#66bb6a', '神话戏': '#ab47bc', '其他': '#78909c',
}

export default function TopicSpaceChart({ data }) {
  const chartRef = useRef(null)
  const instanceRef = useRef(null)

  useEffect(() => {
    if (!data?.themeSpace?.points || data.themeSpace.points.length === 0) return
    const points = data.themeSpace.points

    if (!instanceRef.current) {
      instanceRef.current = echarts.init(chartRef.current, null, { renderer: 'canvas' })
    }

    const types = [...new Set(points.map(p => p.type).filter(Boolean))]

    const series = types.map(t => ({
      name: t,
      type: 'scatter',
      data: points.filter(p => p.type === t).map(p => ({
        value: [p.x, p.y, p.title, p.top_themes?.join('+'), p.entropy],
      })),
      symbolSize: 8,
      itemStyle: { color: TYPE_COLORS[t] || '#78909c', opacity: 0.7 },
      emphasis: { itemStyle: { opacity: 1, borderColor: '#fff', borderWidth: 1 } },
    }))

    const option = {
      tooltip: {
        formatter: (params) => {
          const [, , title, themes, entropy] = params.value
          return `<strong>${title}</strong><br/>主题: ${themes || '-'}<br/>熵: ${entropy?.toFixed(3)}`
        },
      },
      legend: {
        data: types,
        textStyle: { color: '#8899aa', fontSize: 10 },
        top: 0,
      },
      grid: { left: 40, right: 40, top: 50, bottom: 30 },
      xAxis: {
        type: 'value',
        name: 'PC1',
        nameTextStyle: { color: '#8899aa', fontSize: 10 },
        axisLabel: { show: false },
        splitLine: { lineStyle: { color: '#1e2d3d' } },
      },
      yAxis: {
        type: 'value',
        name: 'PC2',
        nameTextStyle: { color: '#8899aa', fontSize: 10 },
        axisLabel: { show: false },
        splitLine: { lineStyle: { color: '#1e2d3d' } },
      },
      series,
    }

    instanceRef.current.setOption(option, true)
  }, [data])

  useEffect(() => {
    const handleResize = () => instanceRef.current?.resize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return <div ref={chartRef} className="chart-container" />
}
