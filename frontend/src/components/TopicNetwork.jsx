import React, { useEffect, useRef } from 'react'
import * as echarts from 'echarts'

export default function TopicNetwork({ data }) {
  const chartRef = useRef(null)
  const instanceRef = useRef(null)

  useEffect(() => {
    if (!data?.themeCooc?.top_pairs) return
    const { top_pairs, topic_totals } = data.themeCooc

    // Build graph data from top co-occurring pairs
    const themeSet = new Set()
    top_pairs.slice(0, 20).forEach(p => {
      themeSet.add(p.theme1)
      themeSet.add(p.theme2)
    })

    const nodes = [...themeSet].map(name => {
      const size = Math.max(45, Math.sqrt(topic_totals[name] || 1) * 3.5)
      return {
        name,
        symbolSize: size,
        category: 0,
        label: {
          fontSize: Math.max(10, size / 4.5)
        }
      }
    })

    const nodeIdx = {}
    nodes.forEach((n, i) => { nodeIdx[n.name] = i })

    const edges = top_pairs.slice(0, 20).map(p => ({
      source: nodeIdx[p.theme1],
      target: nodeIdx[p.theme2],
      sourceName: p.theme1,
      targetName: p.theme2,
      value: p.count,
      label: { show: true, formatter: `${p.pmi.toFixed(3)}`, fontSize: 9, color: '#8899aa' },
      lineStyle: { width: Math.max(1.5, p.pmi * 40) },
    }))

    if (!instanceRef.current) {
      instanceRef.current = echarts.init(chartRef.current, null, { renderer: 'canvas' })
    }

    const option = {
      tooltip: {
        formatter: (params) => {
          if (params.dataType === 'edge') {
            return `${params.data.sourceName} ↔ ${params.data.targetName}<br/>PMI: ${params.data.label?.formatter}`
          }
          return `${params.name}<br/>出现次数: ${topic_totals[params.name] || '-'}`
        },
      },
      series: [{
        type: 'graph',
        layout: 'force',
        roam: true,
        draggable: true,
        force: { repulsion: 1200, edgeLength: [150, 350], gravity: 0.08 },
        data: nodes,
        edges: edges,
        label: { show: true, position: 'inside', fontSize: 11, color: '#e0e6ed', fontWeight: 'bold' },
        lineStyle: { color: 'rgba(255,255,255,0.4)', curveness: 0.2 },
        emphasis: { focus: 'adjacency', lineStyle: { width: 5, color: '#ffb74d' } },
      }],
    }

    instanceRef.current.setOption(option, true)
  }, [data])

  useEffect(() => {
    const handleResize = () => instanceRef.current?.resize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return <div ref={chartRef} className="chart-container tall" />
}
