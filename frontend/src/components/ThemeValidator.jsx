import React, { useState, useMemo } from 'react';

export default function ThemeValidator({ data }) {
  const [selectedThemes, setSelectedThemes] = useState([]);

  const { allThemes, filteredScripts } = useMemo(() => {
    if (!data?.themeLLM) return { allThemes: [], filteredScripts: [] };
    
    const themeSet = new Set();
    data.themeLLM.forEach(r => {
      (r.llm_themes || []).forEach(t => themeSet.add(t));
    });
    const themes = Array.from(themeSet).sort();

    const scripts = selectedThemes.length === 0 
      ? data.themeLLM 
      : data.themeLLM.filter(r => 
          selectedThemes.every(st => (r.llm_themes || []).includes(st))
        );
      
    return { allThemes: themes, filteredScripts: scripts };
  }, [data, selectedThemes]);

  return (
    <>
      <div className="card span-4" style={{ display: 'flex', flexDirection: 'column', maxHeight: 450 }}>
        <div className="card-header"><h3>主题字典筛选</h3></div>
        <div style={{ flex: 1, display: 'flex', flexWrap: 'wrap', alignContent: 'flex-start', gap: 8, overflowY: 'auto', paddingRight: 4 }}>
          {allThemes.map(t => {
            const isSelected = selectedThemes.includes(t);
            return (
              <button 
                key={t}
                onClick={() => {
                  if (isSelected) {
                    setSelectedThemes(selectedThemes.filter(st => st !== t));
                  } else {
                    setSelectedThemes([...selectedThemes, t]);
                  }
                }}
                style={{
                  padding: '6px 12px', borderRadius: 16, border: 'none', cursor: 'pointer',
                  background: isSelected ? '#4fc3f7' : 'rgba(255,255,255,0.05)',
                  color: isSelected ? '#000' : '#8899aa',
                  fontSize: '0.8rem', fontWeight: isSelected ? 'bold' : 'normal',
                  transition: 'all 0.2s',
                  flex: '1 1 auto', textAlign: 'center', whiteSpace: 'nowrap'
                }}>
                {t}
              </button>
            )
          })}
        </div>
      </div>

      <div className="card span-8" style={{ display: 'flex', flexDirection: 'column', maxHeight: 450 }}>
        <div className="card-header">
          <h3>剧本识别结果 <span style={{ color: '#4fc3f7', fontSize: '0.8rem', fontWeight: 'normal' }}>({filteredScripts.length} 部剧本)</span></h3>
        </div>
        <div style={{ flex: 1, overflowY: 'auto', paddingRight: 4 }}>
          <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
            <thead style={{ position: 'sticky', top: 0, background: '#111820', zIndex: 1 }}>
              <tr style={{ borderBottom: '1px solid #2a3a4a' }}>
                <th style={{ padding: '8px 4px', width: '25%', color: '#8899aa', fontSize: '0.8rem' }}>剧本</th>
                <th style={{ padding: '8px 4px', color: '#8899aa', fontSize: '0.8rem' }}>识别结果</th>
              </tr>
            </thead>
            <tbody>
              {filteredScripts.map((r, i) => (
                <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.02)' }}>
                  <td style={{ padding: '10px 4px', fontSize: '0.8rem', color: '#e0e6ed', verticalAlign: 'top' }}>
                    {r.title}
                  </td>
                  <td style={{ padding: '10px 4px' }}>
                    {(r.llm_themes || []).map(t => {
                      const isFocus = selectedThemes.includes(t);
                      return (
                        <span key={t} style={{
                          padding: '3px 8px', borderRadius: 4, marginRight: 6,
                          background: isFocus ? 'rgba(79,195,247,0.2)' : 'rgba(255,255,255,0.05)', 
                          color: isFocus ? '#4fc3f7' : '#8899aa',
                          border: isFocus ? '1px solid rgba(79,195,247,0.5)' : '1px solid transparent',
                          fontSize: '0.75rem', display: 'inline-block', marginBottom: 4,
                        }}>{t}</span>
                      )
                    })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  )
}
