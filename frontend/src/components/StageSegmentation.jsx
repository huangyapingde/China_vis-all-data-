import React, { useEffect, useRef, useState } from 'react'
import * as echarts from 'echarts'

const STAGE_COLORS = {
  opening: '#42a5f5', development: '#ffb74d', climax: '#ef5350', resolution: '#66bb6a',
}
const STAGE_LABELS = {
  opening: '开 端', development: '发 展', climax: '高 潮', resolution: '结 局',
}

export default function StageSegmentation({ data, activeScript }) {
  const chartRef = useRef(null)
  const instanceRef = useRef(null)

  useEffect(() => {
    if (!activeScript || !chartRef.current) return
    const nar = data.narrativeData.narratives.find(n => n.script_id === activeScript)
    if (!nar) return

    if (instanceRef.current) instanceRef.current.dispose()
    instanceRef.current = echarts.init(chartRef.current, null, { renderer: 'canvas' })

    const stages = nar.stages
    const n = stages.length

    // Build stage blocks
    const stageData = []
    let start = 0
    for (let i = 1; i <= n; i++) {
      if (i === n || stages[i] !== stages[start]) {
        stageData.push({
          name: STAGE_LABELS[stages[start]] || stages[start],
          value: i - start,
          itemStyle: { color: STAGE_COLORS[stages[start]] || '#78909c' },
        })
        start = i
      }
    }

    const option = {
      title: {
        text: `${nar.title}`,
        textStyle: { color: '#e0e6ed', fontSize: 13 },
        left: 'center',
        top: 0,
      },
      tooltip: {
        formatter: (params) => {
          return `<strong>${params.name}</strong><br/>场景数: ${params.value}<br/>阶段占比: ${(params.percent).toFixed(1)}%`
        },
      },
      series: [
        {
          type: 'treemap',
          data: stageData,
          width: '90%',
          height: '70%',
          top: 30,
          roam: false,
          label: {
            show: true,
            formatter: '{b}\n{c} 场',
            color: '#fff',
            fontSize: 13,
            fontWeight: 700,
          },
          itemStyle: { borderWidth: 2, borderColor: '#0f1923' },
          levels: [{ colorMappingBy: 'id' }],
        },
      ],
    }

    instanceRef.current.setOption(option, true)
  }, [activeScript, data])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div ref={chartRef} style={{ flex: 1, width: '100%', minHeight: 300 }} />
    </div>
  )
}
