import React, { useState } from 'react'
import { useData } from './hooks/useData'
import { useNetworkData } from './hooks/useNetworkData'
import { useThemeData } from './hooks/useThemeData'
import { useNarrativeData } from './hooks/useNarrativeData'
import { useCrossAnalysis } from './hooks/useCrossAnalysis'
import Sidebar from './components/Sidebar'
import SankeyChart from './components/SankeyChart'
import ScatterChart from './components/ScatterChart'
import PMITable from './components/PMITable'
import TimeSeriesChart from './components/TimeSeriesChart'
import ForceGraph from './components/ForceGraph'
import NetworkComparison from './components/NetworkComparison'
import RadarChart from './components/RadarChart'
import CentralityTable from './components/CentralityTable'
import TopicTypeBar from './components/TopicTypeBar'
import TopicSpaceChart from './components/TopicSpaceChart'
import TopicNetwork from './components/TopicNetwork'
import TopicTimeline from './components/TopicTimeline'
import NarrativeCurve from './components/NarrativeCurve'
import StructureComparison from './components/StructureComparison'
import ClimaxDistribution from './components/ClimaxDistribution'
import TemplateCurves from './components/TemplateCurves'
import CrossCorrelation from './components/CrossCorrelation'
import CrossParallel from './components/CrossParallel'
import CrossPattern from './components/CrossPattern'

export default function App() {
  const [task, setTask] = useState('task1')
  const [networkType, setNetworkType] = useState('历史戏')

  const { data, loading, error } = useData()
  const { data: netData, loading: netLoading, error: netError } = useNetworkData()
  const { data: themeData, loading: themeLoading, error: themeError } = useThemeData()
  const { data: narData, loading: narLoading, error: narError } = useNarrativeData()
  const { data: crossData, loading: crossLoading, error: crossError } = useCrossAnalysis()

  const allLoading = loading || netLoading || themeLoading || narLoading || crossLoading
  const allError = error || netError || themeError || narError || crossError

  if (allLoading) {
    return (
      <div className="app">
        <Sidebar task={task} onTaskChange={setTask} />
        <div className="main-area"><div className="loading">🎭 加载数据中...</div></div>
      </div>
    )
  }

  if (allError) {
    return (
      <div className="app">
        <Sidebar task={task} onTaskChange={setTask} />
        <div className="main-area"><div className="loading" style={{ color: '#e53935' }}>加载失败: {allError}</div></div>
      </div>
    )
  }

  const typeDist = netData?.networkSummary?.type_distribution || {}
  const HD = data?.matrixData
  const hdList = HD?.purity ? Object.entries(HD.purity).sort((a, b) => b[1] - a[1]) : []

  return (
    <div className="app">
      <Sidebar task={task} onTaskChange={setTask} />
      <div className="main-area">

        {task === 'task1' && (
          <>
            <div className="academic-header">
              <h1>任务一：行当推断与分析</h1>
              <div className="academic-subtitle">基于角色特征的行当归属推断及时期演变规律</div>
              <div className="academic-meta">
                <span>剧本 {data?.summary?.unique_scripts} 部</span>
                <span>角色 {data?.summary?.total_characters} 个</span>
                <span>行当 {data?.summary?.hangdang_main_distribution ? Object.keys(data.summary.hangdang_main_distribution).length : 4} 类</span>
              </div>
            </div>
            <div className="panel-grid">
              <div className="panel-card span-6">
                <div className="fig-header">图1 角色类型→行当映射桑基图</div>
                <div className="fig-caption">彩带粗细代表有多少角色"流"向该行当，一眼看出角色类型与行当的对应关系</div>
                <SankeyChart data={data} />
                <div className="fig-analysis"><strong>核心发现：</strong>武将、奸臣与净行绑定极强；后妃、女将几乎全部归于旦行。行当本质是一套"角色类型化"的编码系统。</div>
              </div>
              <div className="panel-card span-3">
                <div className="fig-header">图2 行当-角色PMI关联TOP15</div>
                <div className="fig-caption">PMI值越高说明这对组合越不寻常、越有标志性</div>
                <PMITable data={data} />
              </div>
              <div className="panel-card span-3">
                <div className="fig-header">图3 各行当纯度与熵</div>
                <div className="fig-caption">纯度=专一程度，熵=多样化程度</div>
                <div style={{ fontSize: '0.88rem', lineHeight: 2.4, padding: '8px 4px' }}>
                  {hdList.map(([hd, p]) => (
                    <div key={hd} style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 6, padding: '4px 8px', borderRadius: 4, background: 'rgba(0,0,0,0.02)' }}>
                      <span className={`hangdang-tag hangdang-${hd}`}>{hd}</span>
                      <span>纯度 <strong>{(p * 100).toFixed(1)}%</strong></span>
                      <span style={{ color: '#5a6b7d' }}>熵 <strong>{HD?.entropy?.[hd]?.toFixed(3)}</strong></span>
                    </div>
                  ))}
                </div>
                <div className="fig-analysis"><strong>解读：</strong>丑行纯度最高(26.3%)，扮演角色最集中；生旦熵值最高，承担的角色类型最广泛。</div>
              </div>
              <div className="panel-card span-6">
                <div className="fig-header">图4 角色特征聚类散点图</div>
                <div className="fig-caption">基于权力/情感/交互行为特征的2D投影，颜色=行当标签</div>
                <ScatterChart data={data} />
                <div className="fig-analysis"><strong>核心发现：</strong>不同行当在特征空间中呈现聚类趋势，证明凭行为特征可推断行当归属。</div>
              </div>
              <div className="panel-card span-6">
                <div className="fig-header">图5 各时期行当占比变化</div>
                <div className="fig-caption">不同剧本卷/时期四大行当构成的演变趋势</div>
                <TimeSeriesChart data={data} />
                <div className="fig-analysis"><strong>解读：</strong>四大行当比例在各卷间保持稳定——生行约40%，旦净丑各约20%，行当结构是京剧的"深层语法"。</div>
              </div>
            </div>
          </>
        )}

        {task === 'task2' && (
          <>
            <div className="academic-header">
              <h1>任务二：角色关系网络分析</h1>
              <div className="academic-subtitle">三层网络（共现/对话/权力）构建与剧种结构比较</div>
              <div className="academic-meta">
                <span>构建网络 {netData?.networkSummary?.total_scripts} 个</span>
                <span>剧种类别 {Object.keys(typeDist).length} 类</span>
                <span>中心角色 {Object.keys(netData?.characterCentrality?.characters || {}).length} 个</span>
              </div>
            </div>
            <div className="panel-grid">
              <div className="panel-card span-3">
                <div className="fig-header">图1 剧种网络密度对比</div>
                <div className="fig-caption">密度越高说明角色之间联系越紧密</div>
                <NetworkComparison data={netData} />
                <div className="fig-analysis"><strong>解读：</strong>神话戏密度最高(0.925)，公案戏对话密度最高——审案场景台词交锋密集。</div>
              </div>
              <div className="panel-card span-5">
                <div className="fig-header">图2 角色关系网络图（力导向）</div>
                <div className="fig-caption">节点大小=度中心性，颜色=社区归属，边粗=互动频率</div>
                <div style={{ display: 'flex', gap: 4, marginBottom: 6, flexWrap: 'wrap' }}>
                  {Object.keys(typeDist).map(t => (
                    <button key={t} onClick={() => setNetworkType(t)}
                      style={{ padding: '3px 12px', borderRadius: 4, border: '1px solid #dce1e8',
                        background: networkType === t ? 'rgba(25,118,210,0.1)' : 'transparent',
                        color: networkType === t ? '#1976d2' : '#5a6b7d',
                        cursor: 'pointer', fontSize: '0.75rem' }}>{t}</button>
                  ))}
                </div>
                <ForceGraph data={netData} selectedType={networkType} />
                <div className="fig-analysis"><strong>核心发现：</strong>历史戏呈星型结构(众星捧月)，家庭戏呈多小团体分散结构，公案戏呈三方对峙结构。</div>
              </div>
              <div className="panel-card span-4">
                <div className="fig-header">图3 角色影响力雷达图</div>
                <div className="fig-caption">从出场次数、社交广度、传播影响力、桥梁作用四维度看角色分量</div>
                <RadarChart data={netData} />
              </div>
              <div className="panel-card span-12">
                <div className="fig-header">图4 角色中心性排名（跨剧本聚合）</div>
                <div className="fig-caption">综合度中心性、PageRank、中介中心性的跨剧本排名</div>
                <CentralityTable data={netData} />
              </div>
            </div>
          </>
        )}

        {task === 'task3' && (
          <>
            <div className="academic-header">
              <h1>任务三：主题建模与分析</h1>
              <div className="academic-subtitle">15类主题关键词词典 + TF-IDF 提取，跨剧种比较</div>
              <div className="academic-meta">
                <span>剧本 {themeData?.themeSummary?.total_scripts} 部</span>
                <span>台词 {themeData?.themeSummary?.total_utterances} 条</span>
                <span>主题 {themeData?.themeSummary?.theme_count} 类</span>
              </div>
            </div>
            <div className="panel-grid">
              <div className="panel-card span-6">
                <div className="fig-header">图1 剧种×主题强度对比</div>
                <div className="fig-caption">不同剧种在15类主题上的分布差异，柱子越高该主题越突出</div>
                <TopicTypeBar data={themeData} />
                <div className="fig-analysis"><strong>核心发现：</strong>历史戏=战争+智谋二元结构；家庭戏=伦理+情感单核；公案戏=正义+权力+悲情复合体。</div>
              </div>
              <div className="panel-card span-6">
                <div className="fig-header">图2 主题空间分布（PCA降维）</div>
                <div className="fig-caption">每点=一部剧本，颜色=剧种，位置基于主题分布相似度</div>
                <TopicSpaceChart data={themeData} />
              </div>
              <div className="panel-card span-5">
                <div className="fig-header">图3 主题共现网络</div>
                <div className="fig-caption">节点=主题，边=共现关系，标注=PMI值</div>
                <TopicNetwork data={themeData} />
                <div className="fig-analysis"><strong>解读：</strong>"战争+智谋""忠诚+君臣""家庭+爱情"是京剧最稳定的主题搭配组合。</div>
              </div>
              <div className="panel-card span-7">
                <div className="fig-header">图4 主题随场景演化曲线</div>
                <div className="fig-caption">选择剧本查看各主题强度随剧情推进的动态变化</div>
                <TopicTimeline data={themeData} />
              </div>
            </div>
          </>
        )}

        {task === 'task4' && (
          <>
            <div className="academic-header">
              <h1>任务四：叙事结构分析</h1>
              <div className="academic-subtitle">情感/冲突/事件密度特征提取，高潮检测与四阶段分割</div>
              <div className="academic-meta">
                <span>分析剧本 {narData?.narrativeSummary?.total_scripts} 部</span>
                <span>单峰 {narData?.narrativeSummary?.structure_distribution?.single_peak || 0}</span>
                <span>多峰 {(narData?.narrativeSummary?.structure_distribution?.dual_peak || 0) + (narData?.narrativeSummary?.structure_distribution?.multi_peak || 0)}</span>
              </div>
            </div>
            <div className="panel-grid">
              <div className="panel-card span-6">
                <div className="fig-header">图1 不同剧种叙事模板曲线</div>
                <div className="fig-caption">12点归一化张力曲线（高斯平滑后取均值）</div>
                <TemplateCurves data={narData} />
                <div className="fig-analysis"><strong>核心发现：</strong>历史戏呈渐进式上升曲线，高潮位于中后段；家庭戏曲线波动最剧烈；公案戏呈三段式节奏。</div>
              </div>
              <div className="panel-card span-3">
                <div className="fig-header">图2 叙事结构类型分布</div>
                <div className="fig-caption">单峰/双峰/多峰结构占比</div>
                <StructureComparison data={narData} />
                <div className="fig-analysis"><strong>解读：</strong>87%剧本采用单峰结构，符合"起承转合"经典叙事逻辑。</div>
              </div>
              <div className="panel-card span-3">
                <div className="fig-header">图3 高潮位置分布</div>
                <div className="fig-caption">戏曲家们最喜欢把"戏眼"放在哪里？</div>
                <ClimaxDistribution data={narData} />
              </div>
              <div className="panel-card span-12">
                <div className="fig-header">图4 叙事曲线图（四线叠加）</div>
                <div className="fig-caption">张力·冲突·事件·情绪 四线随场景变化趋势，红色图钉=高潮位置</div>
                <NarrativeCurve data={narData} />
              </div>
            </div>
          </>
        )}

        {task === 'task5' && (
          <>
            <div className="academic-header">
              <h1>任务五：跨维度关联分析</h1>
              <div className="academic-subtitle">角色关系 × 主题表达 × 叙事方式的关联机制与协同演化规律</div>
              <div className="academic-meta">
                <span>关联剧本 {crossData?.summary?.total_scripts} 部</span>
                <span>分析维度 {crossData?.summary?.dimension_names?.length} 个</span>
                <span>发现模式 {crossData?.patterns?.length} 条</span>
              </div>
            </div>
            <div className="panel-grid">
              <div className="panel-card span-7">
                <div className="fig-header">图1 跨维度关联矩阵</div>
                <div className="fig-caption">网络/主题/叙事三维度 Pearson 相关系数，蓝色=正相关 红色=负相关</div>
                <CrossCorrelation data={crossData} />
                <div className="fig-analysis"><strong>核心发现：</strong>权力密度与中心化正相关；模块度与主题熵正相关（社区分化越明显，主题越多样）。揭示"人物配置-主题选择-节奏安排"的系统性耦合。</div>
              </div>
              <div className="panel-card span-5">
                <div className="fig-header">图2 平行坐标探索</div>
                <div className="fig-caption">每条折线=一部剧本，颜色=聚类归属，9个维度联合观察</div>
                <CrossParallel data={crossData} />
              </div>
              <div className="panel-card span-12">
                <div className="fig-header">图3 典型关联模式与结构类型</div>
                <div className="fig-caption">自动挖掘的跨维度协同规律 + 四类典型结构聚类对比</div>
                <CrossPattern data={crossData} />
              </div>
            </div>
          </>
        )}

      </div>
    </div>
  )
}
