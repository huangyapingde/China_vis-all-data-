import React, { useState } from 'react'
import { useData } from './hooks/useData'
import { useNetworkData } from './hooks/useNetworkData'
import { useThemeData } from './hooks/useThemeData'
import { useNarrativeData } from './hooks/useNarrativeData'
import Sidebar from './components/Sidebar'
import SummaryCards from './components/SummaryCards'
import SankeyChart from './components/SankeyChart'
import StackedBarChart from './components/StackedBarChart'
import HeatmapChart from './components/HeatmapChart'
import TimeSeriesChart from './components/TimeSeriesChart'
import ScatterChart from './components/ScatterChart'
import PMITable from './components/PMITable'
import PurityEntropyChart from './components/PurityEntropyChart'
import BubbleChart from './components/BubbleChart'
import ForceGraph from './components/ForceGraph'
import NetworkComparison from './components/NetworkComparison'
import RadarChart from './components/RadarChart'
import CommunityGraph from './components/CommunityGraph'
import CentralityTable from './components/CentralityTable'
import TopicSpaceChart from './components/TopicSpaceChart'
import TopicHeatmap from './components/TopicHeatmap'
import TopicNetwork from './components/TopicNetwork'
import TopicTimeline from './components/TopicTimeline'
import TopicCombinations from './components/TopicCombinations'
import TopicTypeBar from './components/TopicTypeBar'
import NarrativeCurve from './components/NarrativeCurve'
import StageSegmentation from './components/StageSegmentation'
import StructureComparison from './components/StructureComparison'
import ClimaxDistribution from './components/ClimaxDistribution'
import NarrativeClustering from './components/NarrativeClustering'
import TemplateCurves from './components/TemplateCurves'

export default function App() {
  const [task, setTask] = useState('task1')
  const [tab, setTab] = useState('overview')
  const [selectedNode, setSelectedNode] = useState(null)
  const [networkType, setNetworkType] = useState('历史戏')
  const [themeType, setThemeType] = useState(null)
  const [narrativeActiveScript, setNarrativeActiveScript] = useState(null)

  const { data, loading, error } = useData()
  const { data: netData, loading: netLoading, error: netError } = useNetworkData()
  const { data: themeData, loading: themeLoading, error: themeError } = useThemeData()
  const { data: narData, loading: narLoading, error: narError } = useNarrativeData()

  const allLoading = loading || netLoading || themeLoading || narLoading
  const allError = error || netError || themeError || narError

  const handleTaskChange = (newTask) => {
    setTask(newTask)
    setSelectedNode(null)
    if (newTask === 'task1') setTab('overview')
    else if (newTask === 'task2') setTab('network-overview')
    else if (newTask === 'task3') setTab('theme-overview')
    else if (newTask === 'task4') setTab('narrative-overview')
  }

  const handleTabChange = (newTab) => {
    setTab(newTab)
    setSelectedNode(null)
  }

  if (allLoading) {
    return (
      <div className="app">
        <Sidebar task={task} tab={tab} onTaskChange={handleTaskChange} onTabChange={handleTabChange} />
        <div style={{ marginLeft: 220, display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
          <div className="loading" style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', marginBottom: 8 }}>🎭</div>
            加载数据中...
          </div>
        </div>
      </div>
    )
  }

  if (allError) {
    return (
      <div className="app">
        <Sidebar task={task} tab={tab} onTaskChange={handleTaskChange} onTabChange={handleTabChange} />
        <div style={{ marginLeft: 220, display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', color: '#e57373' }}>
          加载失败: {allError}
        </div>
      </div>
    )
  }

  const sidebarEl = <Sidebar task={task} tab={tab} onTaskChange={handleTaskChange} onTabChange={handleTabChange} summaryData={data?.summary} />

  // ── Task 1: Hangdang Analysis ──
  if (task === 'task1') {
    return (
      <div className="app">
        {sidebarEl}
        <div style={{ marginLeft: 220 }}>
          <header className="header">
            <div>
              <h1>任务一：行当推断与分析</h1>
              <div style={{ fontSize: '0.75rem', color: '#8899aa', marginTop: 4 }}>
                角色特征 → 行当归属 → 历史变化规律 · 基于 {data?.summary?.unique_scripts || 1473} 部京剧剧本
              </div>
            </div>
            <div className="header-stats">
              <div>剧本 <strong>{data?.summary?.unique_scripts}</strong></div>
              <div>角色 <strong>{data?.summary?.total_characters}</strong></div>
              <div>行当标注+预测 <strong>6,004</strong></div>
            </div>
          </header>

          <div className="dashboard">
            {tab === 'overview' && (
              <>
                <SummaryCards data={data} />

                <div className="card span-8">
                  <div className="card-header">
                    <div>
                      <h3>图1: 角色类型 → 行当 映射桑基图</h3>
                      <div className="subtitle">角色类型与四大行当的流向关系 (点击节点筛选)</div>
                    </div>
                  </div>
                  <SankeyChart data={data} onSelect={setSelectedNode} />
                </div>

                <div className="card span-4">
                  <div className="card-header">
                    <div><h3>行当分布概览</h3></div>
                  </div>
                  <PurityEntropyChart data={data} />
                  <div className="tooltip-info" style={{ marginTop: 8 }}>
                    纯度: 行当是否集中表达特定角色类型<br/>熵: 行当的多样化程度
                  </div>
                </div>

                <div className="card span-8">
                  <div className="card-header">
                    <div>
                      <h3>图4: 角色特征聚类散点图</h3>
                      <div className="subtitle">基于行为特征(权力/情感/互动)的2D投影 · 颜色=行当标签</div>
                    </div>
                  </div>
                  <ScatterChart data={data} />
                </div>

                <div className="card span-4">
                  <div className="card-header">
                    <div><h3>PMI 关联强度 TOP15</h3></div>
                  </div>
                  <PMITable data={data} />
                </div>

                <div className="card span-12">
                  <div className="card-header">
                    <div>
                      <h3>图2: 各卷行当分布堆叠图</h3>
                      <div className="subtitle">不同剧本卷/时期的行当构成对比</div>
                    </div>
                  </div>
                  <StackedBarChart data={data} />
                </div>
              </>
            )}

            {tab === 'detail' && (
              <>
                <div className="card span-8">
                  <div className="card-header">
                    <div><h3>图3: 角色类型 × 行当 热力图</h3></div>
                  </div>
                  <HeatmapChart data={data} />
                </div>
                <div className="card span-4">
                  <div className="card-header"><h3>角色-行当偏好度 PMI</h3></div>
                  <PMITable data={data} />
                </div>
                <div className="card span-6">
                  <div className="card-header"><h3>各行当纯度与熵</h3></div>
                  <PurityEntropyChart data={data} />
                </div>
                <div className="card span-6">
                  <div className="card-header"><h3>角色-行当气泡图 (D3)</h3></div>
                  <div className="chart-container"><BubbleChart data={data} /></div>
                </div>
              </>
            )}

            {tab === 'era' && (
              <>
                <div className="card span-8">
                  <div className="card-header">
                    <div><h3>图5: 行当占比随时间变化曲线</h3></div>
                  </div>
                  <TimeSeriesChart data={data} />
                </div>
                <div className="card span-4">
                  <div className="card-header"><h3>关键趋势发现</h3></div>
                  <div style={{ fontSize: '0.8rem', color: '#8899aa', lineHeight: 1.8 }}>
                    <ul style={{ listStyle: 'none', padding: 0 }}>
                      <li style={{ marginBottom: 12 }}>
                        <strong style={{ color: '#e0e6ed' }}>1. 行当结构稳定性</strong><br/>
                        四大行当在各卷中保持相对稳定的比例分布。
                      </li>
                      <li style={{ marginBottom: 12 }}>
                        <strong style={{ color: '#e0e6ed' }}>2. 生行为主</strong><br/>
                        生行在所有卷中占比最高，与京剧历史传承一致。
                      </li>
                      <li style={{ marginBottom: 12 }}>
                        <strong style={{ color: '#e0e6ed' }}>3. 纯度差异</strong><br/>
                        {Object.entries(data?.matrixData?.purity || {}).sort((a, b) => b[1] - a[1]).map(([hd, p], i) => (
                          <span key={hd} style={{ display: 'block', fontSize: '0.75rem' }}>
                            {hd}: {(p * 100).toFixed(0)}% 集中于特定角色类型
                          </span>
                        ))}
                      </li>
                    </ul>
                  </div>
                </div>
                <div className="card span-8">
                  <div className="card-header"><h3>各卷行当堆叠图</h3></div>
                  <StackedBarChart data={data} />
                </div>
                <div className="card span-4">
                  <div className="card-header"><h3>各卷数据明细</h3></div>
                  <div style={{ maxHeight: 380, overflowY: 'auto' }}>
                    <table>
                      <thead><tr><th>卷</th><th>角色数</th><th>生%</th><th>旦%</th><th>净%</th><th>丑%</th></tr></thead>
                      <tbody>
                        {(data?.eraData?.time_series || []).map(row => (
                          <tr key={row.era}>
                            <td>{row.era}</td><td>{row.total}</td>
                            <td>{((row['生'] || 0) * 100).toFixed(1)}</td>
                            <td>{((row['旦'] || 0) * 100).toFixed(1)}</td>
                            <td>{((row['净'] || 0) * 100).toFixed(1)}</td>
                            <td>{((row['丑'] || 0) * 100).toFixed(1)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    )
  }

  // ── Task 2: Network Analysis ──
  const typeDistribution = netData?.networkSummary?.type_distribution || {}
  const typeAggregates = netData?.networkSummary?.type_aggregates || {}

  if (task === 'task2') {
    return (
    <div className="app">
      {sidebarEl}
      <div style={{ marginLeft: 220 }}>
        <header className="header">
          <div>
            <h1>任务二：角色关系网络分析</h1>
            <div style={{ fontSize: '0.75rem', color: '#8899aa', marginTop: 4 }}>
              三层网络 (共现/对话/权力) · 四类剧种对比 · 社区发现
            </div>
          </div>
          <div className="header-stats">
            <div>剧本 <strong>{netData?.networkSummary?.total_scripts}</strong></div>
            <div>剧种 <strong>{Object.keys(typeDistribution).length}</strong></div>
            <div>角色中心性库 <strong>{Object.keys(netData?.characterCentrality?.characters || {}).length}</strong></div>
          </div>
        </header>

        <div className="dashboard">
          {tab === 'network-overview' && (
            <>
              {/* Type distribution cards */}
              <div className="card span-12" style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
                {Object.entries(typeDistribution).map(([t, count]) => (
                  <div key={t} style={{
                    flex: 1, minWidth: 120, padding: '16px', borderRadius: 8,
                    background: 'rgba(255,255,255,0.03)', border: '1px solid #2a3a4a',
                    textAlign: 'center', cursor: 'pointer',
                    borderColor: networkType === t ? '#4fc3f7' : '#2a3a4a',
                  }} onClick={() => setNetworkType(t)}>
                    <div style={{ fontSize: '1.6rem', fontWeight: 700, color: '#4fc3f7' }}>{count}</div>
                    <div style={{ fontSize: '0.8rem', color: '#8899aa' }}>{t}</div>
                    <div style={{ fontSize: '0.7rem', color: '#546e7a', marginTop: 4 }}>
                      密度: {typeAggregates[t]?.cooc_density?.toFixed(3) || '-'}
                    </div>
                    <div style={{ fontSize: '0.7rem', color: '#546e7a' }}>
                      权力密度: {typeAggregates[t]?.power_density?.toFixed(3) || '-'}
                    </div>
                  </div>
                ))}
              </div>

              {/* Network Summary Cards */}
              <div className="card span-4">
                <div className="card-header"><h3>三层网络结构</h3></div>
                <div style={{ fontSize: '0.75rem', color: '#8899aa', lineHeight: 1.8 }}>
                  <div style={{ marginBottom: 10, padding: '8px 10px', background: 'rgba(79,195,247,0.08)', borderRadius: 4 }}>
                    <strong style={{ color: '#4fc3f7' }}>Layer 1: 共现网络</strong><br/>
                    同一场景出现 → 连边<br/>
                    <span style={{ color: '#546e7a' }}>反映角色阵营/场景归属</span>
                  </div>
                  <div style={{ marginBottom: 10, padding: '8px 10px', background: 'rgba(240,98,146,0.08)', borderRadius: 4 }}>
                    <strong style={{ color: '#f06292' }}>Layer 2: 对话网络</strong><br/>
                    台词接续 → 有向边<br/>
                    <span style={{ color: '#546e7a' }}>反映叙事控制权</span>
                  </div>
                  <div style={{ padding: '8px 10px', background: 'rgba(255,183,77,0.08)', borderRadius: 4 }}>
                    <strong style={{ color: '#ffb74d' }}>Layer 3: 权力网络</strong><br/>
                    命令-服从 → 支配边<br/>
                    <span style={{ color: '#546e7a' }}>反映权力结构</span>
                  </div>
                </div>
              </div>

              {/* Density comparison */}
              <div className="card span-8">
                <div className="card-header"><h3>剧种 × 三层网络密度对比</h3></div>
                <NetworkComparison data={netData} />
              </div>

              {/* Key findings */}
              <div className="card span-4">
                <div className="card-header"><h3>关键发现</h3></div>
                <div style={{ fontSize: '0.8rem', color: '#8899aa', lineHeight: 1.8 }}>
                  <ul style={{ listStyle: 'none', padding: 0 }}>
                    <li style={{ marginBottom: 12 }}>
                      <strong style={{ color: '#ff7043' }}>历史戏：星型结构</strong><br/>
                      密度: {typeAggregates['历史戏']?.cooc_density?.toFixed(3) || '-'} · 权力密度最高 ({typeAggregates['历史戏']?.power_density?.toFixed(3) || '-'})
                      <br/>核心角色高度中心化，权力网络明显
                    </li>
                    <li style={{ marginBottom: 12 }}>
                      <strong style={{ color: '#42a5f5' }}>家庭戏：多中心分散</strong><br/>
                      密度: {typeAggregates['家庭戏']?.cooc_density?.toFixed(3) || '-'} · 权力密度最低 ({typeAggregates['家庭戏']?.power_density?.toFixed(3) || '-'})
                      <br/>情感连接强，权力关系弱
                    </li>
                    <li style={{ marginBottom: 12 }}>
                      <strong style={{ color: '#66bb6a' }}>公案戏：高密度交互</strong><br/>
                      密度: {typeAggregates['公案戏']?.cooc_density?.toFixed(3) || '-'} · 对话密度最高 ({typeAggregates['公案戏']?.dial_density?.toFixed(3) || '-'})
                      <br/>多角色交叉互动，对话网络复杂
                    </li>
                  </ul>
                </div>
              </div>

              {/* Centrality overview */}
              <div className="card span-8">
                <div className="card-header"><h3>角色影响力雷达图 (PageRank Top 8)</h3></div>
                <div className="chart-container"><RadarChart data={netData} /></div>
              </div>
            </>
          )}

          {tab === 'network-graph' && (
            <>
              <div className="card span-8">
                <div className="card-header">
                  <div>
                    <h3>角色关系网络图 (力导向布局)</h3>
                    <div className="subtitle">节点大小=度中心性 · 颜色=社区归属 · 边粗=互动频率</div>
                  </div>
                  <div style={{ display: 'flex', gap: 6 }}>
                    {Object.keys(typeDistribution).map(t => (
                      <button key={t} onClick={() => setNetworkType(t)} style={{
                        padding: '4px 12px', borderRadius: 4, border: '1px solid #2a3a4a',
                        background: networkType === t ? 'rgba(79,195,247,0.15)' : 'transparent',
                        color: networkType === t ? '#4fc3f7' : '#8899aa',
                        cursor: 'pointer', fontSize: '0.75rem',
                      }}>{t}</button>
                    ))}
                  </div>
                </div>
                <div className="chart-container tall">
                  <ForceGraph data={netData} selectedType={networkType} />
                </div>
              </div>

              <div className="card span-4">
                <div className="card-header"><h3>社区结构</h3></div>
                <CommunityGraph data={netData} selectedType={networkType} />
                <div className="tooltip-info">
                  社区检测算法: Louvain / 贪婪模块度<br/>
                  不同颜色代表不同的角色阵营/群体
                </div>
              </div>
            </>
          )}

          {tab === 'network-comparison' && (
            <>
              <div className="card span-8">
                <div className="card-header">
                  <div>
                    <h3>剧种结构对比：多层网络指标</h3>
                    <div className="subtitle">共现/对话/权力三层网络 × 四类剧种</div>
                  </div>
                </div>
                <NetworkComparison data={netData} />
              </div>

              <div className="card span-4">
                <div className="card-header"><h3>分析结论</h3></div>
                <div style={{ fontSize: '0.8rem', color: '#8899aa', lineHeight: 1.8 }}>
                  <ul style={{ listStyle: 'none', padding: 0 }}>
                    {[
                      { t: '历史戏', color: '#ff7043', desc: '权力集中，星型网络，核心角色主导叙事' },
                      { t: '家庭戏', color: '#42a5f5', desc: '多中心分散，情感连接为主，权力弱化' },
                      { t: '公案戏', color: '#66bb6a', desc: '高密度交互，角色交叉对话复杂' },
                      { t: '神话戏', color: '#ab47bc', desc: '角色少但高度互联，神仙妖怪关系紧密' },
                    ].map(item => (
                      <li key={item.t} style={{ marginBottom: 12, padding: '8px 10px', background: 'rgba(255,255,255,0.02)', borderRadius: 4 }}>
                        <strong style={{ color: item.color }}>{item.t}</strong><br/>
                        <span style={{ fontSize: '0.75rem' }}>{item.desc}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Layer comparison table */}
              <div className="card span-6">
                <div className="card-header"><h3>各剧种三层网络密度</h3></div>
                <table>
                  <thead><tr><th>剧种</th><th>共现密度</th><th>对话密度</th><th>权力密度</th></tr></thead>
                  <tbody>
                    {Object.entries(typeAggregates).map(([t, agg]) => (
                      <tr key={t}>
                        <td><strong>{t}</strong></td>
                        <td>{(agg.cooc_density * 100).toFixed(1)}%</td>
                        <td>{(agg.dial_density * 100).toFixed(1)}%</td>
                        <td>{(agg.power_density * 100).toFixed(1)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Community comparison */}
              <div className="card span-6">
                <div className="card-header"><h3>社区结构对比 (各剧种代表剧本)</h3></div>
                <CommunityGraph data={netData} selectedType={networkType} />
              </div>
            </>
          )}

          {tab === 'network-characters' && (
            <>
              <div className="card span-8">
                <div className="card-header"><h3>角色影响力雷达图</h3></div>
                <div className="chart-container"><RadarChart data={netData} /></div>
              </div>

              <div className="card span-4">
                <div className="card-header"><h3>使用方法</h3></div>
                <div style={{ fontSize: '0.8rem', color: '#8899aa', lineHeight: 1.8 }}>
                  <p>雷达图展示跨剧本角色中心性的四个维度：</p>
                  <ul style={{ paddingLeft: 16 }}>
                    <li><strong>出场次数</strong>：角色在多少剧本中出现</li>
                    <li><strong>平均度</strong>：平均连接数 (社交枢纽)</li>
                    <li><strong>PageRank</strong>：网络影响力 (权力中心)</li>
                    <li><strong>中间中心性</strong>：信息桥梁作用</li>
                  </ul>
                  <p style={{ marginTop: 8, color: '#546e7a', fontSize: '0.7rem' }}>
                    点击图表中的角色名查看详情
                  </p>
                </div>
              </div>

              <div className="card span-12">
                <div className="card-header"><h3>角色中心性排名 (跨剧本聚合)</h3></div>
                <CentralityTable data={netData} />
              </div>
            </>
          )}
        </div>
      </div>
    </div>

    )
  }

  // ── Task 3: Theme Analysis ──
  if (task === 'task3') {
    return (
      <div className="app">
        {sidebarEl}
        <div style={{ marginLeft: 220 }}>
          <header className="header">
            <div>
              <h1>任务三：主题建模与分析</h1>
              <div style={{ fontSize: '0.75rem', color: '#8899aa', marginTop: 4 }}>
                剧本主题提取 · 主题组合模式 · 跨剧种对比 · 场景演化分析
              </div>
            </div>
            <div className="header-stats">
              <div>剧本 <strong>{themeData?.themeSummary?.total_scripts}</strong></div>
              <div>台词 <strong>{themeData?.themeSummary?.total_utterances}</strong></div>
              <div>主题类别 <strong>{themeData?.themeSummary?.theme_count}</strong></div>
            </div>
          </header>

          <div className="dashboard">
            {tab === 'theme-overview' && (
              <>
                {/* Summary & Key Findings */}
                <div className="card span-4">
                  <div className="card-header"><h3>主题建模方法</h3></div>
                  <div style={{ fontSize: '0.75rem', color: '#8899aa', lineHeight: 1.8 }}>
                    <div style={{ marginBottom: 10, padding: '8px 10px', background: 'rgba(79,195,247,0.08)', borderRadius: 4 }}>
                      <strong style={{ color: '#4fc3f7' }}>Step 1: 关键词词典</strong><br/>
                      15类京剧主题 × 精选关键词库<br/>
                      <span style={{ color: '#546e7a' }}>覆盖战争、智谋、忠诚、家庭等核心主题</span>
                    </div>
                    <div style={{ marginBottom: 10, padding: '8px 10px', background: 'rgba(129,199,132,0.08)', borderRadius: 4 }}>
                      <strong style={{ color: '#81c784' }}>Step 2: TF-IDF + PCA</strong><br/>
                      84,803条台词 → 主题向量空间<br/>
                      <span style={{ color: '#546e7a' }}>PCA降维可视化</span>
                    </div>
                    <div style={{ padding: '8px 10px', background: 'rgba(255,183,77,0.08)', borderRadius: 4 }}>
                      <strong style={{ color: '#ffb74d' }}>Step 3: LLM验证</strong><br/>
                      Qwen2.5:7b 批量标注主题<br/>
                      <span style={{ color: '#546e7a' }}>验证关键词分类结果</span>
                    </div>
                  </div>
                </div>

                {/* Type × Theme bar */}
                <div className="card span-8">
                  <div className="card-header">
                    <div>
                      <h3>剧种 × 主题强度对比</h3>
                      <div className="subtitle">不同剧种的主题构成差异</div>
                    </div>
                  </div>
                  <TopicTypeBar data={themeData} />
                </div>

                {/* Key Findings */}
                <div className="card span-4">
                  <div className="card-header"><h3>核心发现</h3></div>
                  <div style={{ fontSize: '0.8rem', color: '#8899aa', lineHeight: 1.8 }}>
                    <ul style={{ listStyle: 'none', padding: 0 }}>
                      <li style={{ marginBottom: 12 }}>
                        <strong style={{ color: '#ff7043' }}>历史戏：二元主题结构</strong><br/>
                        战争军事 + 智谋策略 为主导组合<br/>
                        君臣关系与权力斗争并存
                      </li>
                      <li style={{ marginBottom: 12 }}>
                        <strong style={{ color: '#42a5f5' }}>家庭戏：情感单核结构</strong><br/>
                        家庭伦理 + 爱情情感 为核心<br/>
                        忠孝节义主题突出
                      </li>
                      <li style={{ marginBottom: 12 }}>
                        <strong style={{ color: '#66bb6a' }}>公案戏：多主题冲突</strong><br/>
                        正义审判 + 权力斗争 + 悲情苦难<br/>
                        主题组合复杂度最高
                      </li>
                    </ul>
                  </div>
                </div>

                {/* Topic Combinations */}
                <div className="card span-8">
                  <div className="card-header">
                    <h3>主题组合模式 & 关联规则</h3>
                  </div>
                  <TopicCombinations data={themeData} />
                </div>
              </>
            )}

            {tab === 'theme-space' && (
              <>
                <div className="card span-8">
                  <div className="card-header">
                    <div>
                      <h3>主题空间分布图 (PCA降维)</h3>
                      <div className="subtitle">每个点=一个剧本，颜色=剧种，位置基于主题分布相似度</div>
                    </div>
                  </div>
                  <TopicSpaceChart data={themeData} />
                </div>
                <div className="card span-4">
                  <div className="card-header"><h3>解读</h3></div>
                  <div style={{ fontSize: '0.8rem', color: '#8899aa', lineHeight: 1.8 }}>
                    <p>PCA将15维主题向量投影到2D空间：</p>
                    <ul style={{ paddingLeft: 16, marginTop: 8 }}>
                      <li><strong>距离近</strong> = 主题构成相似</li>
                      <li><strong>同色聚集</strong> = 同剧种主题结构趋同</li>
                      <li><strong>跨色混杂</strong> = 不同剧种也有主题重叠</li>
                    </ul>
                    <p style={{ marginTop: 12, fontSize: '0.7rem', color: '#546e7a' }}>
                      主题不是独立存在的，而是以"组合结构"的形式呈现。
                      历史戏=二元结构，家庭戏=单核结构。
                    </p>
                  </div>
                </div>

                {/* Heatmap */}
                <div className="card span-8">
                  <div className="card-header">
                    <div><h3>剧种 × 主题 热力图</h3></div>
                    <div style={{ display: 'flex', gap: 4 }}>
                      {['历史戏', '家庭戏', '公案戏', '神话戏'].map(t => (
                        <button key={t} onClick={() => setThemeType(themeType === t ? null : t)} style={{
                          padding: '3px 8px', borderRadius: 4, border: '1px solid #2a3a4a',
                          background: themeType === t ? 'rgba(79,195,247,0.15)' : 'transparent',
                          color: themeType === t ? '#4fc3f7' : '#8899aa',
                          cursor: 'pointer', fontSize: '0.7rem',
                        }}>{t}</button>
                      ))}
                    </div>
                  </div>
                  <TopicHeatmap data={themeData} selectedType={themeType} />
                </div>

                <div className="card span-4">
                  <div className="card-header"><h3>主题多样性分析</h3></div>
                  <div style={{ fontSize: '0.8rem', color: '#8899aa', lineHeight: 1.8 }}>
                    {(() => {
                      const types = themeData?.themeTypeComp?.types || []
                      const matrix = themeData?.themeTypeComp?.matrix || {}
                      return types.map(t => {
                        const dist = matrix[t] || {}
                        const entropy = -Object.values(dist)
                          .filter(v => v > 0)
                          .reduce((sum, v) => sum + v * Math.log2(v), 0)
                        return (
                          <div key={t} style={{ marginBottom: 10, padding: '8px 10px', background: 'rgba(255,255,255,0.02)', borderRadius: 4 }}>
                            <strong>{t}</strong><br/>
                            <span style={{ fontSize: '0.72rem' }}>熵: {entropy.toFixed(3)}</span><br/>
                            <span style={{ fontSize: '0.7rem', color: '#546e7a' }}>
                              {entropy > 2.2 ? '主题多样，多线叙事' :
                               entropy > 1.8 ? '主题适中，主次分明' : '主题集中，单线叙事'}
                            </span>
                          </div>
                        )
                      })
                    })()}
                  </div>
                </div>
              </>
            )}

            {tab === 'theme-network' && (
              <>
                <div className="card span-8">
                  <div className="card-header">
                    <div>
                      <h3>主题共现网络图</h3>
                      <div className="subtitle">节点=主题，边=共现关系，标注=PMI值，节点大小=出现频率</div>
                    </div>
                  </div>
                  <TopicNetwork data={themeData} />
                </div>

                <div className="card span-4">
                  <div className="card-header"><h3>主题组合规律</h3></div>
                  <TopicCombinations data={themeData} />
                </div>
              </>
            )}

            {tab === 'theme-evolution' && (
              <>
                <div className="card span-8">
                  <div className="card-header">
                    <div>
                      <h3>主题随场景演化曲线</h3>
                      <div className="subtitle">选择剧本查看主题强度的场景变化</div>
                    </div>
                  </div>
                  <div className="chart-container tall">
                    <TopicTimeline data={themeData} />
                  </div>
                </div>

                <div className="card span-4">
                  <div className="card-header"><h3>关于主题演化</h3></div>
                  <div style={{ fontSize: '0.8rem', color: '#8899aa', lineHeight: 1.8 }}>
                    <p>每条曲线代表一个主题在剧本各场景中的强度变化：</p>
                    <ul style={{ paddingLeft: 16, marginTop: 8 }}>
                      <li><strong>上升趋势</strong>：主题逐渐成为主线</li>
                      <li><strong>下降趋势</strong>：主题退出叙事</li>
                      <li><strong>多峰结构</strong>：主题在多个场景重现</li>
                      <li><strong>交叉点</strong>：主题转换/叙事转折</li>
                    </ul>
                    <p style={{ marginTop: 12, fontSize: '0.72rem', color: '#546e7a' }}>
                      主题不是静态分类，而是随叙事动态演化的过程。
                      主题曲线揭示了剧本的内在叙事结构。
                    </p>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    )
  }  // end task3

  // ── Task 4: Narrative Structure Analysis ──
  if (task === 'task4') {
    return (
      <div className="app">
        {sidebarEl}
        <div style={{ marginLeft: 220 }}>
          <header className="header">
            <div>
              <h1>任务四：叙事结构分析</h1>
              <div style={{ fontSize: '0.75rem', color: '#8899aa', marginTop: 4 }}>
                起承转合 · 叙事曲线 · 高潮检测 · 四阶段分割 · 跨剧种对比
              </div>
              <div style={{ fontSize: '0.7rem', color: '#546e7a', marginTop: 4 }}>
                * 注：本页面统计的 <strong>{narData?.narrativeSummary?.total_scripts || 934}</strong> 部“有效样本”，是指成功通过算法提取出高潮峰值和完整叙事结构的剧本（已过滤掉文本过短或场景过少的剧本）。
              </div>
            </div>
            <div className="header-stats">
              <div title="成功提取叙事结构的剧本数">有效样本 <strong>{narData?.narrativeSummary?.total_scripts}</strong></div>
              <div>单峰 <strong>{narData?.narrativeSummary?.structure_distribution?.single_peak}</strong></div>
              <div>多峰 <strong>{(narData?.narrativeSummary?.structure_distribution?.dual_peak || 0) + (narData?.narrativeSummary?.structure_distribution?.multi_peak || 0)}</strong></div>
            </div>
          </header>

          <div className="dashboard">
            {tab === 'narrative-overview' && (
              <>
                <div className="card span-4">
                  <div className="card-header"><h3>叙事结构分析流程</h3></div>
                  <div style={{ fontSize: '0.75rem', color: '#8899aa', lineHeight: 1.8 }}>
                    <div style={{ marginBottom: 10, padding: '8px 10px', background: 'rgba(79,195,247,0.08)', borderRadius: 4 }}>
                      <strong style={{ color: '#4fc3f7' }}>Step 1: Scene特征提取</strong><br/>
                      情绪强度 · 冲突强度 · 事件密度 · 角色活跃度
                    </div>
                    <div style={{ marginBottom: 10, padding: '8px 10px', background: 'rgba(239,83,80,0.08)', borderRadius: 4 }}>
                      <strong style={{ color: '#ef5350' }}>Step 2: 峰值检测</strong><br/>
                      高斯平滑 + SciPy峰值检测 → 识别叙事高潮
                    </div>
                    <div style={{ marginBottom: 10, padding: '8px 10px', background: 'rgba(255,183,77,0.08)', borderRadius: 4 }}>
                      <strong style={{ color: '#ffb74d' }}>Step 3: 四阶段分割</strong><br/>
                      开端 → 发展 → 高潮 → 结局
                    </div>
                    <div style={{ padding: '8px 10px', background: 'rgba(129,199,132,0.08)', borderRadius: 4 }}>
                      <strong style={{ color: '#81c784' }}>Step 4: 叙事模式分类</strong><br/>
                      单峰/双峰/多峰 · 早期/中期/晚期高潮
                    </div>
                  </div>
                </div>

                <div className="card span-8">
                  <div className="card-header">
                    <h3>不同剧种叙事模板曲线</h3>
                    <div className="subtitle">12点归一化张力曲线 (高斯平滑后取均值)</div>
                  </div>
                  <TemplateCurves data={narData} />
                </div>

                <div className="card span-12">
                  <div className="card-header"><h3>关键发现</h3></div>
                  <div style={{ fontSize: '0.8rem', color: '#8899aa', lineHeight: 1.8 }}>
                    <ul style={{ listStyle: 'none', padding: 0, display: 'flex', gap: 16 }}>
                      <li style={{ flex: 1, padding: '12px', background: 'rgba(255,255,255,0.02)', borderRadius: 4 }}>
                        <strong style={{ color: '#ff7043' }}>历史戏：线性冲突驱动</strong><br/>
                        单峰结构占 92.5%<br/>
                        高潮集中在中后期<br/>
                        快速推进的线性叙事
                      </li>
                      <li style={{ flex: 1, padding: '12px', background: 'rgba(255,255,255,0.02)', borderRadius: 4 }}>
                        <strong style={{ color: '#42a5f5' }}>家庭戏：情绪驱动型</strong><br/>
                        多峰结构占比最高 (10.5%)<br/>
                        情绪波动大<br/>
                        情节起伏较多
                      </li>
                      <li style={{ flex: 1, padding: '12px', background: 'rgba(255,255,255,0.02)', borderRadius: 4 }}>
                        <strong style={{ color: '#66bb6a' }}>公案戏：阶段型结构</strong><br/>
                        双峰+多峰结构共占 21%<br/>
                        调查→冲突→判决<br/>
                        节奏分段明显
                      </li>
                    </ul>
                  </div>
                </div>
              </>
            )}

            {tab === 'narrative-curve' && (
              <>
                <div className="card span-8">
                  <div className="card-header">
                    <div>
                      <h3>叙事曲线图 (四线叠加)</h3>
                      <div className="subtitle">叙事张力 · 冲突强度 · 事件密度 · 情绪强度 随场景变化</div>
                    </div>
                  </div>
                  <div className="chart-container tall">
                    <NarrativeCurve data={narData} onScriptChange={setNarrativeActiveScript} />
                  </div>
                </div>

                <div className="card span-4">
                  <div className="card-header">
                    <div>
                      <h3>四阶段分割 (Treemap)</h3>
                      <div className="subtitle">开端/发展/高潮/结局 场景占比</div>
                    </div>
                  </div>
                  <div className="chart-container">
                    <StageSegmentation data={narData} activeScript={narrativeActiveScript} />
                  </div>
                </div>

                <div className="card span-12">
                  <div style={{ fontSize: '0.75rem', color: '#546e7a', lineHeight: 1.8, padding: 8 }}>
                    <strong>解读：</strong>
                    蓝色区域 = 开端(Setup) · 橙色区域 = 发展(Development) · 红色区域 = 高潮(Climax) · 绿色区域 = 结局(Resolution)
                    <br/>红色图钉标记 = 检测到的最高潮场景。虚线曲线分别展示冲突强度和事件密度的平滑趋势。
                  </div>
                </div>
              </>
            )}

            {tab === 'narrative-comparison' && (
              <>
                <div className="card span-6">
                  <div className="card-header"><h3>叙事结构类型对比</h3></div>
                  <StructureComparison data={narData} />
                </div>

                <div className="card span-6">
                  <div className="card-header"><h3>高潮位置分布</h3></div>
                  <ClimaxDistribution data={narData} />
                </div>

                <div className="card span-12">
                  <div className="card-header"><h3>叙事节奏指标</h3></div>
                  {(() => {
                    const agg = narData?.narrativeTypeAgg || {}
                    return (
                      <table style={{ width: '100%', textAlign: 'left' }}>
                        <thead>
                          <tr><th>剧种</th><th>平均高潮位置</th><th>张力幅度</th><th>节奏波动</th></tr>
                        </thead>
                        <tbody>
                          {Object.entries(agg).map(([t, a]) => (
                            <tr key={t}>
                              <td><strong>{t}</strong></td>
                              <td>{(a.avg_climax_position * 100).toFixed(1)}%</td>
                              <td>{a.avg_tension_range?.toFixed(3)}</td>
                              <td>{a.avg_tension_std?.toFixed(3)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    )
                  })()}
                </div>
              </>
            )}

            {tab === 'narrative-clustering' && (
              <>
                <div className="card span-8">
                  <div className="card-header">
                    <div>
                      <h3>叙事结构聚类图 (PCA降维)</h3>
                      <div className="subtitle">
                        每个点=剧本 · 颜色=剧种 · 形状=结构类型 (圆形=单峰, 菱形=双峰, 三角=多峰)
                      </div>
                    </div>
                  </div>
                  <NarrativeClustering data={narData} />
                </div>

                <div className="card span-4">
                  <div className="card-header"><h3>聚类解读</h3></div>
                  <div style={{ fontSize: '0.8rem', color: '#8899aa', lineHeight: 1.8 }}>
                    <p>基于6维叙事特征向量的PCA投影：</p>
                    <ul style={{ paddingLeft: 16, marginTop: 8 }}>
                      <li><strong>圆形(单峰)</strong>：标准戏剧结构，线性叙事</li>
                      <li><strong>菱形(双峰)</strong>：双高潮结构，多线叙事</li>
                      <li><strong>三角(多峰)</strong>：复杂结构，多段式叙事</li>
                    </ul>
                    <p style={{ marginTop: 12, fontSize: '0.72rem', color: '#546e7a' }}>
                      历史戏倾向于单峰线性结构，家庭戏和公案戏结构更复杂。
                    </p>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    )
  }

  // Default fallback (should not reach)
  return null
}
