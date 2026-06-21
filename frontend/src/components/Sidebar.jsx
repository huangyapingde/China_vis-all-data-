import React from 'react'

const sidebarStyle = {
  position: 'fixed',
  left: 0,
  top: 0,
  bottom: 0,
  width: 220,
  background: '#0d1b2a',
  borderRight: '1px solid #2a3a4a',
  zIndex: 200,
  display: 'flex',
  flexDirection: 'column',
  overflowY: 'auto',
}

const logoStyle = {
  padding: '20px 16px',
  borderBottom: '1px solid #2a3a4a',
  fontSize: '1rem',
  fontWeight: 700,
  color: '#e0e6ed',
  letterSpacing: '1px',
}

const navItemStyle = (active) => ({
  display: 'flex',
  alignItems: 'center',
  gap: 10,
  padding: '12px 16px',
  background: active ? 'rgba(79,195,247,0.1)' : 'transparent',
  borderLeftWidth: '3px',
  borderLeftStyle: 'solid',
  borderLeftColor: active ? '#4fc3f7' : 'transparent',
  borderTop: 'none',
  borderRight: 'none',
  borderBottom: 'none',
  color: active ? '#e0e6ed' : '#8899aa',
  cursor: 'pointer',
  fontSize: '0.85rem',
  fontWeight: active ? 600 : 400,
  transition: 'all 0.15s',
  width: '100%',
  textAlign: 'left',
})

const sectionTitleStyle = {
  padding: '16px 16px 6px',
  fontSize: '0.65rem',
  fontWeight: 700,
  color: '#546e7a',
  textTransform: 'uppercase',
  letterSpacing: '1.5px',
}

export default function Sidebar({ task, tab, onTaskChange, onTabChange, summaryData }) {
  return (
    <div style={sidebarStyle}>
      <div style={logoStyle}>
        🎭 京剧行当<br/>分析仪表盘
      </div>

      {/* Task 1 */}
      <div style={sectionTitleStyle}>任务一：行当推断与分析</div>
      {[
        { key: 'overview', icon: '📊', label: '概览总览' },
        { key: 'detail', icon: '🔍', label: '行当-角色关联' },
        { key: 'era', icon: '📈', label: '时期变迁' },
      ].map(t => (
        <button
          key={t.key}
          style={navItemStyle(task === 'task1' && tab === t.key)}
          onClick={() => { onTaskChange('task1'); onTabChange(t.key) }}
        >
          <span>{t.icon}</span>
          <span>{t.label}</span>
        </button>
      ))}

      {/* Task 2 */}
      <div style={sectionTitleStyle}>任务二：角色关系网络分析</div>
      {[
        { key: 'network-overview', icon: '🔗', label: '网络总览' },
        { key: 'network-graph', icon: '🕸️', label: '关系网络图' },
        { key: 'network-comparison', icon: '📊', label: '剧种结构对比' },
        { key: 'network-characters', icon: '👤', label: '角色中心性排名' },
      ].map(t => (
        <button
          key={t.key}
          style={navItemStyle(task === 'task2' && tab === t.key)}
          onClick={() => { onTaskChange('task2'); onTabChange(t.key) }}
        >
          <span>{t.icon}</span>
          <span>{t.label}</span>
        </button>
      ))}

      {/* Task 3 */}
      <div style={sectionTitleStyle}>任务三：主题建模与分析</div>
      {[
        { key: 'theme-overview', icon: '📝', label: '主题总览' },
        { key: 'theme-space', icon: '🌌', label: '主题空间分布' },
        { key: 'theme-network', icon: '🔗', label: '主题关联网络' },
        { key: 'theme-evolution', icon: '⏳', label: '主题演化曲线' },
      ].map(t => (
        <button
          key={t.key}
          style={navItemStyle(task === 'task3' && tab === t.key)}
          onClick={() => { onTaskChange('task3'); onTabChange(t.key) }}
        >
          <span>{t.icon}</span>
          <span>{t.label}</span>
        </button>
      ))}

      {/* Task 4 */}
      <div style={sectionTitleStyle}>任务四：叙事结构分析</div>
      {[
        { key: 'narrative-overview', icon: '📖', label: '叙事总览' },
        { key: 'narrative-curve', icon: '📈', label: '叙事曲线' },
        { key: 'narrative-comparison', icon: '📊', label: '结构对比' },
        { key: 'narrative-clustering', icon: '🌌', label: '叙事聚类' },
      ].map(t => (
        <button
          key={t.key}
          style={navItemStyle(task === 'task4' && tab === t.key)}
          onClick={() => { onTaskChange('task4'); onTabChange(t.key) }}
        >
          <span>{t.icon}</span>
          <span>{t.label}</span>
        </button>
      ))}

      {/* Legend */}
      <div style={{ marginTop: 'auto', padding: '16px', borderTop: '1px solid #2a3a4a', fontSize: '0.7rem', color: '#546e7a' }}>
        <div>
          {summaryData 
            ? `${summaryData.unique_scripts}部剧本 · ${summaryData.total_characters}角色` 
            : '数据加载中...'}
        </div>
        <div style={{ marginTop: 4 }}>四层网络 · 十五类主题 · 四阶段叙事</div>
      </div>
    </div>
  )
}
