import React, { useEffect, useRef } from 'react'
import * as echarts from 'echarts'

const TYPE_COLORS = {
  '历史戏': '#ff7043', '家庭戏': '#42a5f5', '公案戏': '#66bb6a', '神话戏': '#ab47bc',
}

export default function ClimaxDistribution({ data }) {
  const chartRef = useRef(null)
  const instanceRef = useRef(null)

  useEffect(() => {
    if (!data?.narrativeData?.narratives) return
    const nars = data.narrativeData.narratives

    if (!instanceRef.current) {
      instanceRef.current = echarts.init(chartRef.current, null, { renderer: 'canvas' })
    }

    const types = [...new Set(nars.map(n => n.type).filter(Boolean))]

    const option = {
      tooltip: {
        trigger: 'item',
        formatter: (params) => {
          const d = params.value
          return `<strong>${d[2]} (${d[3]})</strong><br/>高潮位置: ${(d[0] * 100).toFixed(0)}%<br/>张力幅度: ${d[1].toFixed(2)}`
        },
      },
      legend: {
        data: types,
        textStyle: { color: '#8899aa', fontSize: 10 },
        top: 0,
      },
      grid: { left: 55, right: 20, top: 30, bottom: 40 },
      xAxis: {
        type: 'value',
        name: '高潮位置 (0%=开场, 100%=结局)',
        nameLocation: 'middle',
        nameGap: 25,
        nameTextStyle: { color: '#8899aa', fontSize: 10 },
        axisLabel: { color: '#8899aa', formatter: v => `${(v * 100).toFixed(0)}%` },
        splitLine: { lineStyle: { color: '#1e2d3d' } },
        min: 0, max: 1,
      },
      yAxis: {
        type: 'value',
        name: '张力幅度',
        axisLabel: { color: '#8899aa' },
        splitLine: { lineStyle: { color: '#1e2d3d' } },
      },
      series: types.map(t => ({
        name: t,
        type: 'scatter',
        data: nars.filter(n => n.type === t).map(n => [
          n.climax_position, n.tension_range, n.title, n.structure_type,
        ]),
        symbolSize: 7,
        itemStyle: { color: TYPE_COLORS[t] || '#78909c', opacity: 0.6 },
        emphasis: { itemStyle: { opacity: 1 } },
      })),
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
