import React, { useMemo } from 'react'
import ReactEChartsCore from 'echarts-for-react'

export default function CrossPattern({ data }) {
  const clusters = data?.clusters || []
  const patterns = data?.patterns || []
  const scripts = data?.scripts || []
  const typeAggs = data?.type_aggregates || {}

  // ── Cluster radar chart ──
  const radarOption = useMemo(() => {
    if (clusters.length === 0) return {}

    const indicators = [
      { name: '角色数', max: 25 },
      { name: '中心化', max: 1 },
      { name: '模块度', max: 0.5 },
      { name: '主题熵', max: 4 },
      { name: '张力波动', max: 0.4 },
      { name: '高潮位置', max: 1 },
    ]

    const indicatorKeys = [
      'avg_character_count', 'avg_centralization',
      'avg_modularity', 'avg_entropy',
      'avg_tension_std', 'avg_climax',
    ]

    return {
      radar: {
        indicators,
        radius: '65%',
        center: ['50%', '55%'],
        name: { textStyle: { color: '#8899aa', fontSize: 10 } },
        splitArea: {
          areaStyle: { color: ['rgba(79,195,247,0.02)', 'rgba(79,195,247,0.05)'] },
        },
        axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
      },
      series: [{
        type: 'radar',
        data: clusters.map(c => ({
          name: c.name,
          value: indicatorKeys.map(k => c.centroid?.[k] || 0),
          itemStyle: { color: c.color },
          lineStyle: { color: c.color, width: 2 },
          areaStyle: { color: c.color, opacity: 0.1 },
        })),
        symbol: 'none',
        animation: false,
      }],
      legend: {
        data: clusters.map(c => ({ name: c.name, itemStyle: { color: c.color } })),
        top: 0,
        left: 'center',
        textStyle: { color: '#8899aa', fontSize: 11 },
      },
    }
  }, [clusters])

  // ── Structure × Theme cross tab ──
  const stCross = data?.structure_theme_cross || {}
  const themeNames = [...new Set(Object.values(stCross).flatMap(d => Object.keys(d)))]
  const structTypes = Object.keys(stCross)

  const barOption = useMemo(() => {
    if (structTypes.length === 0) return {}
    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        formatter: (ps) => `<strong>${ps[0].axisValue}</strong><br/>${ps.map(p =>
          `${p.marker} ${p.seriesName}: ${p.value}部`
        ).join('<br/>')}`,
      },
      grid: { left: 100, right: 30, top: 10, bottom: 40 },
      xAxis: {
        type: 'value',
        axisLabel: { color: '#8899aa', fontSize: 10 },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
      },
      yAxis: {
        type: 'category',
        data: structTypes.map(t => ({
          single_peak: '单峰', dual_peak: '双峰', multi_peak: '多峰'
        }[t] || t)),
        axisLabel: { color: '#e0e6ed', fontSize: 11, fontWeight: 600 },
      },
      series: themeNames.map((th, i) => ({
        name: th,
        type: 'bar',
        stack: 'total',
        barWidth: '70%',
        data: structTypes.map(st => stCross[st]?.[th] || 0),
        itemStyle: { color: `hsl(${i * 25 + 10}, 65%, 55%)` },
        label: { show: false },
      })),
      legend: {
        data: themeNames.map((n, i) => ({ name: n, itemStyle: { color: `hsl(${i * 25 + 10}, 65%, 55%)` } })),
        top: 0,
        left: 'center',
        textStyle: { color: '#8899aa', fontSize: 9 },
        itemWidth: 10,
        itemHeight: 8,
      },
    }
  }, [stCross, themeNames, structTypes])

  // ── Type aggregate comparison ──
  const typeCompOption = useMemo(() => {
    const entries = Object.entries(typeAggs)
    if (entries.length === 0) return {}

    const metrics = [
      { key: 'avg_cooc_density', label: '共现密度', max: 1 },
      { key: 'avg_cooc_clustering', label: '聚集系数', max: 1 },
      { key: 'avg_cooc_modularity', label: '模块度', max: 0.3 },
      { key: 'avg_power_density', label: '权力密度', max: 0.2 },
      { key: 'avg_theme_entropy', label: '主题熵', max: 3 },
    ]

    return {
      radar: {
        indicator: metrics.map(m => ({ name: m.label, max: m.max })),
        radius: '65%',
        center: ['50%', '55%'],
        name: { textStyle: { color: '#8899aa', fontSize: 10 } },
        splitArea: { areaStyle: { color: ['rgba(129,199,132,0.02)', 'rgba(129,199,132,0.05)'] } },
        axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
      },
      series: [{
        type: 'radar',
        data: entries.map(([name, agg]) => ({
          name,
          value: metrics.map(m => agg[m.key] || 0),
          itemStyle: { color: TYPE_COLORS[name] || '#546e7a' },
          lineStyle: { color: TYPE_COLORS[name] || '#546e7a', width: 2 },
          areaStyle: { color: TYPE_COLORS[name] || '#546e7a', opacity: 0.1 },
        })),
        symbol: 'none',
        animation: false,
      }],
      legend: {
        data: entries.map(([name]) => ({ name, itemStyle: { color: TYPE_COLORS[name] || '#546e7a' } })),
        top: 0,
        left: 'center',
        textStyle: { color: '#8899aa', fontSize: 11 },
      },
    }
  }, [typeAggs])

  return (
    <div>
      {/* Pattern Discovery Cards */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          {patterns.map((p, i) => (
            <div key={i} style={{
              flex: '1 1 200px', minWidth: 200,
              padding: '14px 16px', borderRadius: 8,
              background: 'rgba(255,255,255,0.02)',
              border: '1px solid #2a3a4a',
            }}>
              <div style={{ fontSize: '0.75rem', color: '#4fc3f7', fontWeight: 600, marginBottom: 6 }}>
                P{i + 1}: {p.name}
              </div>
              <div style={{ fontSize: '0.72rem', color: '#8899aa', lineHeight: 1.6 }}>
                {p.description}
              </div>
              <div style={{
                marginTop: 8, fontSize: '0.68rem', color: '#546e7a',
                background: 'rgba(79,195,247,0.06)', padding: '4px 8px', borderRadius: 4,
              }}>
                支持度: {p.support}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Cluster Radar + Structure × Theme in two columns */}
      <div style={{ display: 'flex', gap: 16, marginBottom: 16 }}>
        <div style={{ flex: 1 }}>
          <div className="card-header"><h3>四类典型结构雷达对比</h3></div>
          <ReactEChartsCore option={radarOption} style={{ height: 340 }} notMerge />
        </div>
        <div style={{ flex: 1 }}>
          <div className="card-header"><h3>剧种多维特征雷达</h3></div>
          <ReactEChartsCore option={typeCompOption} style={{ height: 340 }} notMerge />
        </div>
      </div>

      {/* Structure × Theme */}
      <div style={{ marginBottom: 16 }}>
        <div className="card-header">
          <h3>叙事结构 × 主导主题 交叉分布</h3>
          <div className="subtitle">不同叙事结构下剧本的主导主题分布</div>
        </div>
        <ReactEChartsCore option={barOption} style={{ height: 280 }} notMerge />
      </div>

      {/* Cluster Representatives */}
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
        {clusters.map(c => (
          <div key={c.name} style={{
            flex: '1 1 220px', minWidth: 200,
            padding: '14px 16px', borderRadius: 8,
            background: 'rgba(255,255,255,0.02)',
            border: '1px solid #2a3a4a',
            borderTop: `3px solid ${c.color}`,
          }}>
            <div style={{ fontSize: '0.8rem', fontWeight: 600, color: c.color, marginBottom: 4 }}>
              {c.name}
              <span style={{ fontSize: '0.68rem', color: '#546e7a', marginLeft: 6 }}>
                ({c.size}部)
              </span>
            </div>
            <div style={{ fontSize: '0.7rem', color: '#8899aa', marginBottom: 8, lineHeight: 1.5 }}>
              {c.description}
            </div>
            <div style={{ fontSize: '0.68rem', color: '#546e7a' }}>
              代表剧本:
            </div>
            {(c.representatives || []).slice(0, 4).map(r => (
              <div key={r.script_id} style={{
                fontSize: '0.68rem', color: '#8899aa', padding: '2px 0',
                borderBottom: '1px solid rgba(255,255,255,0.04)',
              }}>
                {r.title} <span style={{ color: '#546e7a' }}>({r.type})</span>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}

const TYPE_COLORS = {
  '历史戏': '#ff7043',
  '家庭戏': '#42a5f5',
  '公案戏': '#66bb6a',
  '神话戏': '#ab47bc',
}
