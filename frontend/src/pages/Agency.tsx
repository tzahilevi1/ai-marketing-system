import { useState, useEffect, useRef, useCallback } from 'react'
import { api } from '../api/client'

interface AgentInfo { name: string; role: string; emoji: string; active: boolean }
interface AgencyMessage {
  id: string; from_agent: string; to_agent: string; type: string
  subject: string; content: string; priority: string; timestamp: string
}

const TYPE_META: Record<string, { label: string; icon: string; accent: string; glow: string; pill: string }> = {
  task:              { label: 'Task',     icon: '⚡', accent: '#3b82f6', glow: '59,130,246',  pill: 'bg-blue-500/15 text-blue-300 ring-1 ring-blue-500/30' },
  approval_request:  { label: 'Approval', icon: '🔐', accent: '#f59e0b', glow: '245,158,11',  pill: 'bg-amber-500/15 text-amber-300 ring-1 ring-amber-500/30' },
  approval_response: { label: 'Approved', icon: '✅', accent: '#10b981', glow: '16,185,129',  pill: 'bg-emerald-500/15 text-emerald-300 ring-1 ring-emerald-500/30' },
  report:            { label: 'Report',   icon: '📊', accent: '#a855f7', glow: '168,85,247',  pill: 'bg-purple-500/15 text-purple-300 ring-1 ring-purple-500/30' },
  idea:              { label: 'Idea',     icon: '💡', accent: '#ec4899', glow: '236,72,153',  pill: 'bg-pink-500/15 text-pink-300 ring-1 ring-pink-500/30' },
  alert:             { label: 'Alert',    icon: '🚨', accent: '#ef4444', glow: '239,68,68',   pill: 'bg-red-500/15 text-red-300 ring-1 ring-red-500/30' },
  directive:         { label: 'Directive',icon: '📣', accent: '#6366f1', glow: '99,102,241',  pill: 'bg-indigo-500/15 text-indigo-300 ring-1 ring-indigo-500/30' },
}

const AGENT_GRADIENT: Record<string, [string, string]> = {
  ceo:                ['#6366f1','#818cf8'],
  project_manager:    ['#3b82f6','#60a5fa'],
  code_requester:     ['#06b6d4','#22d3ee'],
  code_builder:       ['#14b8a6','#2dd4bf'],
  bug_detector:       ['#f43f5e','#fb7185'],
  innovator:          ['#f59e0b','#fbbf24'],
  graphic_designer:   ['#d946ef','#e879f9'],
  video_editor:       ['#8b5cf6','#a78bfa'],
  accountant:         ['#10b981','#34d399'],
  web_developer:      ['#0ea5e9','#38bdf8'],
  ux_expert:          ['#7c3aed','#9c40f7'],
  campaign_manager:   ['#f97316','#ef4444'],
  analytics_director: ['#16a34a','#22c55e'],
}

const DEPT: Record<string, string> = {
  ceo: 'Leadership', project_manager: 'Leadership', accountant: 'Leadership',
  code_requester: 'Engineering', code_builder: 'Engineering', bug_detector: 'Engineering',
  web_developer: 'Engineering', ux_expert: 'Design',
  graphic_designer: 'Design', video_editor: 'Design', innovator: 'Strategy',
  campaign_manager: 'Marketing', analytics_director: 'Marketing',
}

function fmt(ts: string) {
  try { return new Date(ts).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }) }
  catch { return ts }
}

function Avatar({ name, emoji, size = 36 }: { name: string; emoji: string; size?: number }) {
  const [a, b] = AGENT_GRADIENT[name] || ['#4b5563','#6b7280']
  return (
    <div style={{
      width: size, height: size, borderRadius: size * 0.3,
      background: `linear-gradient(135deg, ${a}, ${b})`,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontSize: size * 0.44, flexShrink: 0,
      boxShadow: `0 0 ${size * 0.4}px ${a}40`,
    }}>{emoji}</div>
  )
}

function PulsingDot({ active }: { active: boolean }) {
  return (
    <span style={{ position: 'relative', display: 'inline-flex', width: 8, height: 8 }}>
      {active && <span style={{
        position: 'absolute', inset: 0, borderRadius: '50%',
        background: '#22c55e', opacity: 0.6,
        animation: 'ping 1.4s cubic-bezier(0,0,0.2,1) infinite',
      }} />}
      <span style={{
        borderRadius: '50%', width: 8, height: 8,
        background: active ? '#22c55e' : '#374151', display: 'block'
      }} />
    </span>
  )
}

export default function Agency() {
  const [agents, setAgents] = useState<AgentInfo[]>([])
  const [messages, setMessages] = useState<AgencyMessage[]>([])
  const [running, setRunning] = useState(false)
  const [loading, setLoading] = useState(false)
  const [selectedMsg, setSelectedMsg] = useState<AgencyMessage | null>(null)
  const [filterType, setFilterType] = useState('all')
  const [filterAgent, setFilterAgent] = useState('all')
  const [taskTarget, setTaskTarget] = useState('ceo')
  const [taskSubject, setTaskSubject] = useState('')
  const [taskContent, setTaskContent] = useState('')
  const [sendingTask, setSendingTask] = useState(false)
  const [autoScroll, setAutoScroll] = useState(true)
  const [totalMsgs, setTotalMsgs] = useState(0)
  const [showTaskPanel, setShowTaskPanel] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  const fetchStatus = useCallback(async () => {
    try {
      const res = await api.get('/agency/status')
      setRunning(res.data.running)
      setAgents(res.data.agents || [])
      setTotalMsgs(res.data.total_messages || 0)
      setMessages(res.data.message_history || [])
    } catch { /* silent */ }
  }, [])

  useEffect(() => { fetchStatus(); const t = setInterval(fetchStatus, 2500); return () => clearInterval(t) }, [fetchStatus])
  useEffect(() => { if (autoScroll && !selectedMsg) bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, autoScroll, selectedMsg])

  const startAgency = async () => { setLoading(true); try { await api.post('/agency/start'); setRunning(true) } finally { setLoading(false) }; fetchStatus() }
  const stopAgency = async () => { await api.post('/agency/stop'); setRunning(false) }
  const sendTask = async () => {
    if (!taskSubject.trim() || !taskContent.trim()) return
    setSendingTask(true)
    try { await api.post('/agency/task', { to_agent: taskTarget, subject: taskSubject, content: taskContent }); setTaskSubject(''); setTaskContent(''); setShowTaskPanel(false) }
    finally { setSendingTask(false) }
  }

  const filtered = messages.filter(m =>
    (filterType === 'all' || m.type === filterType) &&
    (filterAgent === 'all' || m.from_agent === filterAgent || m.to_agent === filterAgent)
  )

  const typeCounts = messages.reduce((a, m) => ({ ...a, [m.type]: (a[m.type] || 0) + 1 }), {} as Record<string, number>)
  const senderCounts = messages.reduce((a, m) => ({ ...a, [m.from_agent]: (a[m.from_agent] || 0) + 1 }), {} as Record<string, number>)
  const maxCount = Math.max(...Object.values(senderCounts), 1)

  const deptGroups = agents.reduce((acc, a) => {
    const d = DEPT[a.name] || 'Other'
    if (!acc[d]) acc[d] = []
    acc[d].push(a)
    return acc
  }, {} as Record<string, AgentInfo[]>)

  const lastAlert = messages.filter(m => m.type === 'alert').slice(-1)[0]

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        @keyframes ping { 75%,100% { transform: scale(2); opacity: 0; } }
        @keyframes slideUp { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:translateY(0); } }
        @keyframes fadeIn { from { opacity:0; } to { opacity:1; } }
        @keyframes shimmer { 0%{background-position:-200% 0} 100%{background-position:200% 0} }
        .msg-card { animation: slideUp 0.2s ease-out; }
        .sidebar-scroll::-webkit-scrollbar { width: 4px; }
        .sidebar-scroll::-webkit-scrollbar-track { background: transparent; }
        .sidebar-scroll::-webkit-scrollbar-thumb { background: #1f2937; border-radius: 4px; }
        .feed-scroll::-webkit-scrollbar { width: 6px; }
        .feed-scroll::-webkit-scrollbar-track { background: transparent; }
        .feed-scroll::-webkit-scrollbar-thumb { background: #1e2433; border-radius: 6px; }
        .feed-scroll::-webkit-scrollbar-thumb:hover { background: #2d3748; }
      `}</style>

      <div style={{ position: 'fixed', inset: 0, background: '#080b12', fontFamily: "'Inter', system-ui, sans-serif", color: '#e2e8f0', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

        {/* ── TOP NAV ── */}
        <header style={{ height: 56, background: 'rgba(10,13,22,0.95)', backdropFilter: 'blur(20px)', borderBottom: '1px solid rgba(255,255,255,0.06)', display: 'flex', alignItems: 'center', paddingInline: 24, gap: 16, flexShrink: 0, zIndex: 50 }}>
          {/* Brand */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 32, height: 32, borderRadius: 10, background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 15, boxShadow: '0 0 20px #6366f140' }}>⚡</div>
            <div>
              <div style={{ fontSize: 13, fontWeight: 700, letterSpacing: '-0.3px', color: '#f1f5f9' }}>AI Agency</div>
              <div style={{ fontSize: 10, color: '#475569', fontWeight: 500 }}>Autonomous Marketing Intelligence</div>
            </div>
          </div>

          <div style={{ flex: 1 }} />

          {/* Stats pills */}
          <div style={{ display: 'flex', gap: 8 }}>
            <div style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 20, padding: '4px 12px', fontSize: 11, color: '#94a3b8', fontWeight: 500 }}>
              <span style={{ color: '#f1f5f9', fontWeight: 700 }}>{agents.length}</span> Agents
            </div>
            <div style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 20, padding: '4px 12px', fontSize: 11, color: '#94a3b8', fontWeight: 500 }}>
              <span style={{ color: '#f1f5f9', fontWeight: 700 }}>{totalMsgs}</span> Messages
            </div>
          </div>

          {/* Status */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, background: running ? 'rgba(34,197,94,0.1)' : 'rgba(255,255,255,0.04)', border: `1px solid ${running ? 'rgba(34,197,94,0.3)' : 'rgba(255,255,255,0.08)'}`, borderRadius: 20, padding: '5px 12px', fontSize: 11, fontWeight: 600, color: running ? '#86efac' : '#64748b' }}>
            <PulsingDot active={running} />
            {running ? 'Live' : 'Offline'}
          </div>

          {/* Actions */}
          {!running ? (
            <button onClick={startAgency} disabled={loading} style={{ height: 34, padding: '0 18px', background: 'linear-gradient(135deg, #4f46e5, #7c3aed)', border: 'none', borderRadius: 10, fontSize: 12, fontWeight: 700, color: '#fff', cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.6 : 1, boxShadow: '0 0 24px #4f46e550', letterSpacing: '0.2px' }}>
              {loading ? '...' : '▶ Launch Agency'}
            </button>
          ) : (
            <button onClick={stopAgency} style={{ height: 34, padding: '0 18px', background: 'rgba(239,68,68,0.15)', border: '1px solid rgba(239,68,68,0.35)', borderRadius: 10, fontSize: 12, fontWeight: 700, color: '#fca5a5', cursor: 'pointer' }}>
              ⏹ Stop
            </button>
          )}
        </header>

        {/* ── BODY ── */}
        <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>

          {/* ── LEFT SIDEBAR ── */}
          <aside style={{ width: 220, background: 'rgba(10,13,22,0.8)', borderRight: '1px solid rgba(255,255,255,0.05)', display: 'flex', flexDirection: 'column', flexShrink: 0 }}>
            <div className="sidebar-scroll" style={{ flex: 1, overflowY: 'auto', padding: '8px 8px 0' }}>
              {Object.entries(deptGroups).map(([dept, deptAgents]) => (
                <div key={dept} style={{ marginBottom: 4 }}>
                  <div style={{ fontSize: 9, fontWeight: 700, color: '#334155', letterSpacing: '0.8px', textTransform: 'uppercase', padding: '8px 8px 4px' }}>{dept}</div>
                  {deptAgents.map(agent => {
                    const isActive = filterAgent === agent.name
                    const msgCount = senderCounts[agent.name] || 0
                    return (
                      <button key={agent.name} onClick={() => setFilterAgent(isActive ? 'all' : agent.name)} style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 8, padding: '7px 8px', borderRadius: 10, border: 'none', background: isActive ? 'rgba(99,102,241,0.12)' : 'transparent', cursor: 'pointer', transition: 'all 0.15s', outline: isActive ? '1px solid rgba(99,102,241,0.3)' : 'none', textAlign: 'left' }}
                        onMouseEnter={e => { if (!isActive) e.currentTarget.style.background = 'rgba(255,255,255,0.04)' }}
                        onMouseLeave={e => { if (!isActive) e.currentTarget.style.background = 'transparent' }}>
                        <Avatar name={agent.name} emoji={agent.emoji} size={30} />
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ fontSize: 11, fontWeight: 600, color: isActive ? '#c7d2fe' : '#cbd5e1', lineHeight: 1.3, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{agent.role.split('/')[0].trim()}</div>
                          {msgCount > 0 && <div style={{ fontSize: 9, color: '#475569', fontWeight: 500 }}>{msgCount} msg{msgCount !== 1 ? 's' : ''}</div>}
                        </div>
                        <PulsingDot active={agent.active && running} />
                      </button>
                    )
                  })}
                </div>
              ))}
              <div style={{ height: 8 }} />
            </div>

            {/* Send task button */}
            <div style={{ padding: 10, borderTop: '1px solid rgba(255,255,255,0.05)' }}>
              <button onClick={() => setShowTaskPanel(!showTaskPanel)} style={{ width: '100%', height: 36, background: showTaskPanel ? 'rgba(99,102,241,0.2)' : 'rgba(255,255,255,0.05)', border: `1px solid ${showTaskPanel ? 'rgba(99,102,241,0.4)' : 'rgba(255,255,255,0.08)'}`, borderRadius: 10, fontSize: 11, fontWeight: 700, color: showTaskPanel ? '#a5b4fc' : '#94a3b8', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, transition: 'all 0.2s' }}>
                ✉ Send Task
              </button>
            </div>
          </aside>

          {/* ── CENTER: FEED ── */}
          <main style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', minWidth: 0 }}>

            {/* Filter bar */}
            <div style={{ height: 44, background: 'rgba(10,13,22,0.6)', backdropFilter: 'blur(10px)', borderBottom: '1px solid rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', paddingInline: 16, gap: 6, flexShrink: 0, overflowX: 'auto' }}>
              {(['all', ...Object.keys(TYPE_META)] as string[]).map(type => {
                const meta = TYPE_META[type]
                const cnt = type === 'all' ? messages.length : (typeCounts[type] || 0)
                if (type !== 'all' && cnt === 0) return null
                const isActive = filterType === type
                return (
                  <button key={type} onClick={() => setFilterType(isActive ? 'all' : type)} style={{ height: 26, padding: '0 10px', borderRadius: 20, border: 'none', fontSize: 10, fontWeight: 700, cursor: 'pointer', whiteSpace: 'nowrap', transition: 'all 0.15s', background: isActive ? (meta ? meta.accent : '#f1f5f9') : 'rgba(255,255,255,0.05)', color: isActive ? '#fff' : '#64748b', boxShadow: isActive && meta ? `0 0 12px ${meta.accent}50` : 'none' }}>
                    {meta ? `${meta.icon} ${meta.label}` : 'All'} · {cnt}
                  </button>
                )
              })}
              <div style={{ flex: 1 }} />
              <label style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 10, color: '#475569', cursor: 'pointer', userSelect: 'none', whiteSpace: 'nowrap' }}>
                <input type="checkbox" checked={autoScroll} onChange={e => setAutoScroll(e.target.checked)} style={{ accentColor: '#6366f1', width: 11, height: 11 }} />
                Auto-scroll
              </label>
            </div>

            {/* Messages */}
            <div className="feed-scroll" style={{ flex: 1, overflowY: 'auto', padding: 16, display: 'flex', flexDirection: 'column', gap: 8 }}>
              {filtered.length === 0 ? (
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#1e2a3a', gap: 12 }}>
                  <div style={{ fontSize: 64 }}>🤖</div>
                  <div style={{ fontSize: 13, fontWeight: 600 }}>{running ? 'Agents are thinking...' : 'Launch the agency to see agents collaborate'}</div>
                  <div style={{ fontSize: 11, color: '#0f172a' }}>Messages will appear here in real-time</div>
                </div>
              ) : filtered.map(msg => {
                const meta = TYPE_META[msg.type] || TYPE_META.task
                const agentInfo = agents.find(a => a.name === msg.from_agent)
                const isSelected = selectedMsg?.id === msg.id
                const isAlert = msg.type === 'alert'

                return (
                  <div key={msg.id} className="msg-card" onClick={() => setSelectedMsg(isSelected ? null : msg)} style={{ display: 'flex', gap: 10, cursor: 'pointer' }}>
                    <Avatar name={msg.from_agent} emoji={agentInfo?.emoji || '🤖'} size={34} />
                    <div style={{ flex: 1, minWidth: 0, background: isAlert ? 'rgba(239,68,68,0.07)' : isSelected ? 'rgba(99,102,241,0.08)' : 'rgba(255,255,255,0.03)', border: `1px solid ${isAlert ? 'rgba(239,68,68,0.25)' : isSelected ? 'rgba(99,102,241,0.3)' : 'rgba(255,255,255,0.07)'}`, borderRadius: 14, padding: '10px 14px', transition: 'all 0.15s', boxShadow: isSelected ? `0 0 0 1px rgba(99,102,241,0.2)` : 'none' }}
                      onMouseEnter={e => { if (!isSelected) e.currentTarget.style.background = 'rgba(255,255,255,0.05)'; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.12)' }}
                      onMouseLeave={e => { if (!isSelected) { e.currentTarget.style.background = isAlert ? 'rgba(239,68,68,0.07)' : 'rgba(255,255,255,0.03)'; e.currentTarget.style.borderColor = isAlert ? 'rgba(239,68,68,0.25)' : 'rgba(255,255,255,0.07)' } }}>
                      {/* Row 1 */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 5 }}>
                        <span style={{ fontSize: 11, fontWeight: 700, color: '#e2e8f0' }}>{msg.from_agent}</span>
                        <span style={{ fontSize: 10, color: '#334155' }}>→</span>
                        <span style={{ fontSize: 10, color: '#475569', fontWeight: 500 }}>{msg.to_agent === 'broadcast' ? '🌐 all' : msg.to_agent}</span>
                        <div style={{ flex: 1 }} />
                        <span className={meta.pill} style={{ fontSize: 9, fontWeight: 700, borderRadius: 20, padding: '2px 7px', letterSpacing: '0.3px' }}>{meta.icon} {meta.label}</span>
                        <span style={{ fontSize: 9, color: '#334155', fontWeight: 600, fontVariantNumeric: 'tabular-nums' }}>{fmt(msg.timestamp)}</span>
                      </div>
                      {/* Subject */}
                      <div style={{ fontSize: 12, fontWeight: 600, color: isAlert ? '#fca5a5' : '#f1f5f9', lineHeight: 1.4, marginBottom: isSelected ? 0 : undefined }}>{msg.subject}</div>
                      {/* Expanded content */}
                      {isSelected && msg.content && (
                        <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid rgba(255,255,255,0.07)', maxHeight: 320, overflowY: 'auto', animation: 'fadeIn 0.2s ease' }}>
                          <pre style={{ fontSize: 11, color: '#94a3b8', lineHeight: 1.7, whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>{msg.content}</pre>
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
              <div ref={bottomRef} />
            </div>
          </main>

          {/* ── RIGHT PANEL: STATS ── */}
          <aside style={{ width: 220, background: 'rgba(10,13,22,0.8)', borderLeft: '1px solid rgba(255,255,255,0.05)', display: 'flex', flexDirection: 'column', overflowY: 'auto', flexShrink: 0 }} className="sidebar-scroll">
            <div style={{ padding: '12px 14px 6px', fontSize: 9, fontWeight: 700, color: '#1e293b', letterSpacing: '1px', textTransform: 'uppercase' }}>Overview</div>

            {/* KPI row */}
            <div style={{ padding: '0 10px 10px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6 }}>
              {[
                { label: 'Total', value: totalMsgs, color: '#6366f1' },
                { label: 'Alerts', value: typeCounts['alert'] || 0, color: '#ef4444' },
                { label: 'Tasks', value: typeCounts['task'] || 0, color: '#3b82f6' },
                { label: 'Reports', value: typeCounts['report'] || 0, color: '#a855f7' },
              ].map(k => (
                <div key={k.label} style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 10, padding: '8px 10px' }}>
                  <div style={{ fontSize: 18, fontWeight: 800, color: k.color, lineHeight: 1 }}>{k.value}</div>
                  <div style={{ fontSize: 9, color: '#475569', fontWeight: 600, marginTop: 2 }}>{k.label}</div>
                </div>
              ))}
            </div>

            {/* Activity bar */}
            <div style={{ padding: '0 14px 14px' }}>
              <div style={{ fontSize: 9, fontWeight: 700, color: '#1e293b', letterSpacing: '0.8px', textTransform: 'uppercase', marginBottom: 8 }}>Activity</div>
              {Object.entries(TYPE_META).map(([type, meta]) => {
                const cnt = typeCounts[type] || 0
                const pct = messages.length ? (cnt / messages.length) * 100 : 0
                return (
                  <div key={type} style={{ marginBottom: 6 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
                      <span style={{ fontSize: 10, color: '#64748b', fontWeight: 500 }}>{meta.icon} {meta.label}</span>
                      <span style={{ fontSize: 10, color: '#475569', fontWeight: 700 }}>{cnt}</span>
                    </div>
                    <div style={{ height: 3, background: 'rgba(255,255,255,0.05)', borderRadius: 3, overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${pct}%`, background: meta.accent, borderRadius: 3, transition: 'width 0.5s ease', boxShadow: `0 0 6px ${meta.accent}80` }} />
                    </div>
                  </div>
                )
              })}
            </div>

            {/* Top agents */}
            <div style={{ padding: '0 14px 14px', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: 12 }}>
              <div style={{ fontSize: 9, fontWeight: 700, color: '#1e293b', letterSpacing: '0.8px', textTransform: 'uppercase', marginBottom: 8 }}>Most Active</div>
              {Object.entries(senderCounts).sort((a, b) => b[1] - a[1]).slice(0, 6).map(([name, cnt]) => {
                const agent = agents.find(a => a.name === name)
                const [g1] = AGENT_GRADIENT[name] || ['#4b5563','#6b7280']
                return (
                  <div key={name} style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 7 }}>
                    <Avatar name={name} emoji={agent?.emoji || '🤖'} size={22} />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 10, color: '#94a3b8', fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{name}</div>
                      <div style={{ height: 2, background: 'rgba(255,255,255,0.05)', borderRadius: 2, marginTop: 3 }}>
                        <div style={{ height: '100%', width: `${(cnt / maxCount) * 100}%`, background: g1, borderRadius: 2, transition: 'width 0.5s ease' }} />
                      </div>
                    </div>
                    <span style={{ fontSize: 10, color: '#475569', fontWeight: 800, minWidth: 18, textAlign: 'right' }}>{cnt}</span>
                  </div>
                )
              })}
            </div>

            {/* Last alert */}
            {lastAlert && (
              <div style={{ margin: '0 10px 14px', background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 12, padding: 10 }}>
                <div style={{ fontSize: 9, fontWeight: 700, color: '#ef4444', letterSpacing: '0.6px', textTransform: 'uppercase', marginBottom: 5 }}>🚨 Last Alert</div>
                <div style={{ fontSize: 10, color: '#fca5a5', lineHeight: 1.5, display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>{lastAlert.subject}</div>
                <div style={{ fontSize: 9, color: '#7f1d1d', marginTop: 4, fontWeight: 600 }}>{fmt(lastAlert.timestamp)}</div>
              </div>
            )}
          </aside>
        </div>

        {/* ── SEND TASK MODAL ── */}
        {showTaskPanel && (
          <div onClick={() => setShowTaskPanel(false)} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(8px)', zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', animation: 'fadeIn 0.15s ease' }}>
            <div onClick={e => e.stopPropagation()} style={{ width: 440, background: '#0d1117', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 20, padding: 24, boxShadow: '0 24px 80px rgba(0,0,0,0.6)', animation: 'slideUp 0.2s ease' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
                <div>
                  <div style={{ fontSize: 16, fontWeight: 800, color: '#f1f5f9' }}>Send Task</div>
                  <div style={{ fontSize: 11, color: '#475569', marginTop: 2 }}>Assign a task to any agent</div>
                </div>
                <button onClick={() => setShowTaskPanel(false)} style={{ width: 28, height: 28, borderRadius: 8, border: '1px solid rgba(255,255,255,0.08)', background: 'rgba(255,255,255,0.04)', color: '#64748b', fontSize: 16, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>×</button>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                <div>
                  <label style={{ fontSize: 10, fontWeight: 700, color: '#475569', textTransform: 'uppercase', letterSpacing: '0.6px', display: 'block', marginBottom: 6 }}>Assign To</label>
                  <select value={taskTarget} onChange={e => setTaskTarget(e.target.value)} style={{ width: '100%', background: '#111827', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 10, padding: '10px 12px', fontSize: 12, color: '#e2e8f0', outline: 'none', cursor: 'pointer' }}>
                    {agents.map(a => <option key={a.name} value={a.name}>{a.emoji} {a.role}</option>)}
                  </select>
                </div>
                <div>
                  <label style={{ fontSize: 10, fontWeight: 700, color: '#475569', textTransform: 'uppercase', letterSpacing: '0.6px', display: 'block', marginBottom: 6 }}>Subject</label>
                  <input value={taskSubject} onChange={e => setTaskSubject(e.target.value)} placeholder="Brief task title..." style={{ width: '100%', background: '#111827', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 10, padding: '10px 12px', fontSize: 12, color: '#e2e8f0', outline: 'none', fontFamily: 'inherit' }} onFocus={e => e.target.style.borderColor = '#4f46e5'} onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.08)'} />
                </div>
                <div>
                  <label style={{ fontSize: 10, fontWeight: 700, color: '#475569', textTransform: 'uppercase', letterSpacing: '0.6px', display: 'block', marginBottom: 6 }}>Instructions</label>
                  <textarea value={taskContent} onChange={e => setTaskContent(e.target.value)} placeholder="Describe what you need the agent to do..." rows={4} style={{ width: '100%', background: '#111827', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 10, padding: '10px 12px', fontSize: 12, color: '#e2e8f0', outline: 'none', resize: 'none', fontFamily: 'inherit', lineHeight: 1.6 }} onFocus={e => e.target.style.borderColor = '#4f46e5'} onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.08)'} />
                </div>
                <button onClick={sendTask} disabled={sendingTask || !taskSubject || !taskContent || !running} style={{ height: 44, background: (!taskSubject || !taskContent || !running) ? 'rgba(255,255,255,0.04)' : 'linear-gradient(135deg, #4f46e5, #7c3aed)', border: 'none', borderRadius: 12, fontSize: 13, fontWeight: 700, color: (!taskSubject || !taskContent || !running) ? '#334155' : '#fff', cursor: (!taskSubject || !taskContent || !running) ? 'not-allowed' : 'pointer', transition: 'all 0.2s', boxShadow: (taskSubject && taskContent && running) ? '0 0 24px #4f46e560' : 'none' }}>
                  {sendingTask ? 'Sending...' : '⚡ Dispatch Task'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  )
}
