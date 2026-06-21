import React from 'react'

export default function Sidebar({ task, onTaskChange }) {
  const tasks = [
    { key: 'task1', label: '行当推断与分析', icon: '🎭' },
    { key: 'task2', label: '角色关系网络', icon: '🔗' },
    { key: 'task3', label: '主题建模分析', icon: '📝' },
    { key: 'task4', label: '叙事结构分析', icon: '📈' },
    { key: 'task5', label: '跨维度关联', icon: '🔬' },
  ]

  return (
    <div className="sidebar">
      <div className="sidebar-logo">戏韵万象</div>
      <div className="sidebar-subtitle">京剧可视分析</div>

      <div style={{ marginTop: 20, display: 'flex', flexDirection: 'column', gap: 2 }}>
        {tasks.map(t => (
          <button
            key={t.key}
            className={`sidebar-btn ${task === t.key ? 'active' : ''}`}
            onClick={() => onTaskChange(t.key)}
          >
            <span className="sidebar-btn-icon">{t.icon}</span>
            <span>{t.label}</span>
          </button>
        ))}
      </div>

      <div className="sidebar-footer">
        <div>1473部剧本 · 26877角色</div>
        <div style={{ fontSize: '0.65rem', marginTop: 2 }}>基于Python+React分析平台</div>
      </div>
    </div>
  )
}
