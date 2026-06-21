import React from 'react'
import CrossCorrelation from './CrossCorrelation'
import CrossScatterMatrix from './CrossScatterMatrix'
import CrossParallel from './CrossParallel'
import CrossPattern from './CrossPattern'

export default function CrossOverview({ data, tab }) {
  if (!data) return null

  const summary = data.summary || {}
  const scripts = data.scripts || []
  const patterns = data.patterns || []
  const clusters = data.clusters || []

  return (
    <div className="dashboard">
      {tab === 'cross-overview' && (
        <>
          {/* Summary Cards */}
          <div className="card span-12" style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
            {[
              { label: '关联分析剧本', value: summary.total_scripts, sub: '878部具全维度数据', color: '#4fc3f7' },
              { label: '发现关联模式', value: patterns.length, sub: '典型跨维规律', color: '#81c784' },
              { label: '识别结构类型', value: clusters.length, sub: '四类典型叙事结构', color: '#ffb74d' },
              { label: '分析维度', value: summary.dimension_names?.length || 0, sub: '网络+主题+叙事', color: '#ba68c8' },
            ].map((card, i) => (
              <div key={i} style={{
                flex: 1, minWidth: 140,
                padding: '16px 20px', borderRadius: 8,
                background: 'linear-gradient(135deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01))',
                border: '1px solid #2a3a4a',
                borderTop: `3px solid ${card.color}`,
              }}>
                <div style={{ fontSize: '1.8rem', fontWeight: 700, color: card.color }}>{card.value}</div>
                <div style={{ fontSize: '0.8rem', color: '#e0e6ed', marginTop: 2 }}>{card.label}</div>
                <div style={{ fontSize: '0.68rem', color: '#546e7a', marginTop: 4 }}>{card.sub}</div>
              </div>
            ))}
          </div>

          {/* Correlation Heatmap - large */}
          <div className="card span-12">
            <div className="card-header">
              <div>
                <h3>跨维度关联矩阵</h3>
                <div className="subtitle">Pearson相关系数 · 蓝色=正相关 红色=负相关 颜色越深=关联越强</div>
              </div>
            </div>
            <CrossCorrelation data={data} />
          </div>

          {/* Pattern Discovery */}
          <div className="card span-12">
            <div className="card-header">
              <div>
                <h3>典型关联模式发现</h3>
                <div className="subtitle">基于规则挖掘的跨维度协同规律</div>
              </div>
            </div>
            <CrossPattern data={data} />
          </div>
        </>
      )}

      {tab === 'cross-matrix' && (
        <div className="card span-12">
          <div className="card-header">
            <div>
              <h3>多维散点矩阵 (Pairwise Scatter Matrix)</h3>
              <div className="subtitle">每个散点代表一部剧本 · 颜色按剧种区分 · 对角为维度标签</div>
            </div>
          </div>
          <CrossScatterMatrix data={data} />
        </div>
      )}

      {tab === 'cross-parallel' && (
        <div className="card span-12">
          <div className="card-header">
            <div>
              <h3>平行坐标探索 (Parallel Coordinates)</h3>
              <div className="subtitle">每条折线=一部剧本 · 颜色=聚类归属 · 可拖动筛选</div>
            </div>
          </div>
          <CrossParallel data={data} />
        </div>
      )}

      {tab === 'cross-pattern' && (
        <div className="card span-12">
          <div className="card-header">
            <div>
              <h3>结构类型与模式深度分析</h3>
              <div className="subtitle">聚类轮廓 · 剧种对比 · 结构-主题交叉分析</div>
            </div>
          </div>
          <CrossPattern data={data} />
        </div>
      )}
    </div>
  )
}
