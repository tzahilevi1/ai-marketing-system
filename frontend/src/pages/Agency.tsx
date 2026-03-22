import { useState, useEffect, useRef } from 'react'
import { api } from '../api/client'

interface AgentInfo {
  name: string
  role: string
  emoji: string
  active: boolean
}

interface AgencyMessage {
  id: string
  from_agent: string
  to_agent: string
  type: string
  subject: string
  content: string
  priority: string
  timestamp: string
}

const TYPE_CONFIG: Record<string, { color: string; bg: string; icon: string; label: string }> = {
  task:              { color: 'text-blue-700',   bg: 'bg-blue-50 border-blue-200',     icon: '📋', label: 'Task' },
  approval_request:  { color: 'text-amber-700',  bg: 'bg-amber-50 border-amber-200',   icon: '⏳', label: 'Approval' },
  approval_response: { color: 'text-green-700',  bg: 'bg-green-50 border-green-200',   icon: '✅', label: 'Approved' },
  report:            { color: 'text-purple-700', bg: 'bg-purple-50 border-purple-200', icon: '📊', label: 'Report' },
  idea:              { color: 'text-pink-700',   bg: 'bg-pink-50 border-pink-200',     icon: '💡', label: 'Idea' },
  alert:             { color: 'text-red-700',    bg: 'bg-red-50 border-red-200',       icon: '🚨', label: 'Alert' },
  directive:         { color: 'text-indigo-700', bg: 'bg-indigo-50 border-indigo-200', icon: '📣', label: 'Directive' },
}

const PRIORITY_DOT: Record<string, string> = {
  critical: 'bg-red-500',
  high:     'bg-orange-400',
  normal:   'bg-blue-400',
  low:      'bg-gray-300',
}

const AGENT_COLORS: Record<string, string> = {
  ceo:              'from-indigo-500 to-indigo-600',
  project_manager:  'from-blue-500 to-blue-600',
  code_requester:   'from-cyan-500 to-cyan-600',
  code_builder:     'from-teal-500 to-teal-600',
  bug_detector:     'from-rose-500 to-rose-600',
  innovator:        'from-yellow-500 to-orange-500',
  graphic_designer: 'from-fuchsia-500 to-fuchsia-600',
  video_editor:     'from-purple-500 to-purple-600',
  accountant:       'from-emerald-500 to-emerald-600',
  web_developer:    'from-sky-500 to-sky-600',
  ux_expert:        'from-violet-500 to-violet-600',
}

function formatTime(ts: string) {
  try { return new Date(ts).toLocaleTimeString('he-IL', { hour: '2-digit', minute: '2-digit', second: '2-digit' }) }
  catch { return ts }
}

export default function Agency() {
  const [agents, setAgents] = useState<AgentInfo[]>([])
  const [messages, setMessages] = useState<AgencyMessage[]>([])
  const [running, setRunning] = useState(false)
  const [loading, setLoading] = useState(false)
  const [selectedMsg, setSelectedMsg] = useState<AgencyMessage | null>(null)
  const [filter, setFilter] = useState<string>('all')
  const [taskTarget, setTaskTarget] = useState('ceo')
  const [taskSubject, setTaskSubject] = useState('')
  const [taskContent, setTaskContent] = useState('')
  const [sendingTask, setSendingTask] = useState(false)
  const [autoScroll, setAutoScroll] = useState(true)
  const [totalMsgs, setTotalMsgs] = useState(0)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const fetchStatus = async () => {
    try {
      const res = await api.get('/agency/status')
      setRunning(res.data.running)
      setAgents(res.data.agents || [])
      setTotalMsgs(res.data.total_messages || 0)
      setMessages(res.data.message_history || [])
    } catch { /* not started */ }
  }

  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 2500)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (autoScroll) messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, autoScroll])

  const startAgency = async () => {
    setLoading(true)
    try { await api.post('/agency/start'); setRunning(true) } finally { setLoading(false) }
    fetchStatus()
  }

  const stopAgency = async () => {
    await api.post('/agency/stop')
    setRunning(false)
  }

  const sendTask = async () => {
    if (!taskSubject.trim() || !taskContent.trim()) return
    setSendingTask(true)
    try {
      await api.post('/agency/task', { to_agent: taskTarget, subject: taskSubject, content: taskContent })
      setTaskSubject('')
      setTaskContent('')
    } finally { setSendingTask(false) }
  }

  const filtered = filter === 'all'
    ? messages
    : messages.filter(m => m.type === filter || m.from_agent === filter || m.to_agent === filter)

  const typeCounts = messages.reduce((acc, m) => {
    acc[m.type] = (acc[m.type] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const senderCounts = messages.reduce((acc, m) => {
    acc[m.from_agent] = (acc[m.from_agent] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  return (
    <div className="fixed inset-0 bg-gray-950 text-gray-100 flex flex-col" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>

      {/* Top Bar */}
      <div className="bg-gray-900 border-b border-gray-800 px-6 py-3 flex items-center justify-between shrink-0 z-10">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-sm font-bold shadow-lg shadow-blue-500/30">
            AI
          </div>
          <div>
            <h1 className="text-sm font-bold text-white tracking-tight">Agency Control Center</h1>
            <p className="text-xs text-gray-500">{agents.length} agents active &bull; {totalMsgs} messages</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold border transition-all ${
            running
              ? 'bg-green-500/10 text-green-400 border-green-500/30'
              : 'bg-gray-800 text-gray-500 border-gray-700'
          }`}>
            <div className={`w-1.5 h-1.5 rounded-full ${running ? 'bg-green-400 animate-pulse' : 'bg-gray-500'}`} />
            {running ? 'Live' : 'Stopped'}
          </div>
          {!running ? (
            <button onClick={startAgency} disabled={loading}
              className="px-5 py-2 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white text-sm font-semibold rounded-xl transition-all disabled:opacity-50 shadow-lg shadow-blue-500/20">
              {loading ? '⏳ Starting...' : '▶ Start Agency'}
            </button>
          ) : (
            <button onClick={stopAgency}
              className="px-5 py-2 bg-red-600/80 hover:bg-red-600 text-white text-sm font-semibold rounded-xl transition-all">
              ⏹ Stop
            </button>
          )}
        </div>
      </div>

      {/* Main Layout */}
      <div className="flex flex-1 overflow-hidden">

        {/* LEFT: Agents */}
        <div className="w-60 bg-gray-900 border-r border-gray-800 flex flex-col shrink-0">
          <div className="px-4 py-3 border-b border-gray-800">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Agents</p>
          </div>
          <div className="flex-1 overflow-y-auto p-3 space-y-1.5">
            {agents.map(agent => (
              <button key={agent.name}
                onClick={() => setFilter(filter === agent.name ? 'all' : agent.name)}
                className={`w-full flex items-center gap-2.5 p-2.5 rounded-xl text-left transition-all border ${
                  filter === agent.name
                    ? 'bg-gray-700 border-gray-600'
                    : 'bg-transparent border-transparent hover:bg-gray-800'
                }`}>
                <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${AGENT_COLORS[agent.name] || 'from-gray-600 to-gray-700'} flex items-center justify-center text-base shrink-0 shadow`}>
                  {agent.emoji}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-semibold text-gray-200 truncate leading-tight">{agent.role}</p>
                  <p className="text-xs text-gray-600 truncate">{agent.name}</p>
                </div>
                <div className={`w-1.5 h-1.5 rounded-full shrink-0 ${agent.active && running ? 'bg-green-400 animate-pulse' : 'bg-gray-700'}`} />
              </button>
            ))}
          </div>

          {/* Send Task Panel */}
          <div className="p-3 border-t border-gray-800 space-y-2">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Send Task</p>
            <select value={taskTarget} onChange={e => setTaskTarget(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-2 py-1.5 text-xs text-gray-300 focus:outline-none focus:border-blue-500 transition-colors">
              {agents.map(a => <option key={a.name} value={a.name}>{a.emoji} {a.role}</option>)}
            </select>
            <input value={taskSubject} onChange={e => setTaskSubject(e.target.value)}
              placeholder="Subject..."
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-2 py-1.5 text-xs text-gray-300 placeholder-gray-600 focus:outline-none focus:border-blue-500 transition-colors" />
            <textarea value={taskContent} onChange={e => setTaskContent(e.target.value)}
              placeholder="Describe the task..."
              rows={3}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-2 py-1.5 text-xs text-gray-300 placeholder-gray-600 focus:outline-none focus:border-blue-500 transition-colors resize-none" />
            <button onClick={sendTask} disabled={sendingTask || !taskSubject || !taskContent || !running}
              className="w-full py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-30 disabled:cursor-not-allowed text-white text-xs font-semibold rounded-lg transition-all">
              {sendingTask ? 'Sending...' : '⚡ Send Task'}
            </button>
          </div>
        </div>

        {/* CENTER: Message Feed */}
        <div className="flex-1 flex flex-col overflow-hidden">

          {/* Filter Bar */}
          <div className="bg-gray-900/80 backdrop-blur border-b border-gray-800 px-4 py-2 flex items-center gap-1.5 flex-wrap shrink-0">
            <button onClick={() => setFilter('all')}
              className={`px-3 py-1 rounded-full text-xs font-semibold transition-all ${
                filter === 'all' ? 'bg-white text-gray-900' : 'text-gray-500 hover:text-gray-300'
              }`}>
              All ({messages.length})
            </button>
            {Object.entries(TYPE_CONFIG).map(([type, cfg]) => !typeCounts[type] ? null : (
              <button key={type} onClick={() => setFilter(filter === type ? 'all' : type)}
                className={`px-3 py-1 rounded-full text-xs font-semibold transition-all border ${
                  filter === type
                    ? `${cfg.bg} ${cfg.color} border-current`
                    : 'border-gray-700 text-gray-500 hover:text-gray-300 hover:border-gray-600'
                }`}>
                {cfg.icon} {cfg.label} ({typeCounts[type]})
              </button>
            ))}
            <div className="flex-1" />
            <label className="flex items-center gap-1.5 text-xs text-gray-500 cursor-pointer hover:text-gray-300 transition-colors select-none">
              <input type="checkbox" checked={autoScroll} onChange={e => setAutoScroll(e.target.checked)}
                className="w-3 h-3 rounded accent-blue-500" />
              Auto-scroll
            </label>
          </div>

          {/* Messages List */}
          <div className="flex-1 overflow-y-auto p-4 space-y-2">
            {filtered.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full text-gray-700 select-none">
                <div className="text-6xl mb-4">🤖</div>
                <p className="text-sm font-medium">{running ? 'Agents are thinking...' : 'Start the agency to see agents at work'}</p>
              </div>
            )}
            {filtered.map(msg => {
              const cfg = TYPE_CONFIG[msg.type] || { color: 'text-gray-400', bg: 'bg-gray-800 border-gray-700', icon: '💬', label: msg.type }
              const isAlert = msg.type === 'alert'
              const isSelected = selectedMsg?.id === msg.id
              return (
                <div key={msg.id}
                  className={`flex gap-3 cursor-pointer group transition-all duration-150 ${isSelected ? 'scale-[1.005]' : ''}`}
                  onClick={() => setSelectedMsg(isSelected ? null : msg)}>

                  {/* Avatar */}
                  <div className="shrink-0 pt-0.5">
                    <div className={`w-8 h-8 rounded-xl bg-gradient-to-br ${AGENT_COLORS[msg.from_agent] || 'from-gray-600 to-gray-700'} flex items-center justify-center text-sm shadow-md`}>
                      {agents.find(a => a.name === msg.from_agent)?.emoji || '🤖'}
                    </div>
                  </div>

                  {/* Card */}
                  <div className={`flex-1 rounded-2xl border p-3 transition-all duration-150 ${
                    isAlert
                      ? 'bg-red-950/40 border-red-900/60 hover:border-red-800'
                      : isSelected
                      ? 'bg-gray-800 border-gray-600'
                      : 'bg-gray-900 border-gray-800 hover:border-gray-700 hover:bg-gray-800/80'
                  }`}>
                    {/* Header */}
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <span className="text-xs font-bold text-gray-100">{msg.from_agent}</span>
                      <span className="text-gray-700 text-xs">→</span>
                      <span className="text-xs text-gray-500">{msg.to_agent}</span>
                      <div className="flex-1" />
                      <span className={`text-xs px-2 py-0.5 rounded-full border font-semibold ${cfg.bg} ${cfg.color}`}>
                        {cfg.icon} {cfg.label}
                      </span>
                      <div className={`w-1.5 h-1.5 rounded-full ${PRIORITY_DOT[msg.priority] || 'bg-gray-600'}`} title={`Priority: ${msg.priority}`} />
                      <span className="text-xs text-gray-600 tabular-nums">{formatTime(msg.timestamp)}</span>
                    </div>

                    {/* Subject */}
                    <p className={`text-sm font-medium leading-snug ${isAlert ? 'text-red-300' : 'text-gray-100'}`}>
                      {msg.subject}
                    </p>

                    {/* Expanded Content */}
                    {isSelected && msg.content && (
                      <div className="mt-3 pt-3 border-t border-gray-700/60">
                        <div className="max-h-72 overflow-y-auto">
                          <pre className="text-xs text-gray-300 whitespace-pre-wrap font-sans leading-relaxed">
                            {msg.content}
                          </pre>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* RIGHT: Stats */}
        <div className="w-52 bg-gray-900 border-l border-gray-800 flex flex-col shrink-0 overflow-y-auto">
          <div className="px-4 py-3 border-b border-gray-800">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Stats</p>
          </div>
          <div className="p-4 space-y-4">
            {/* Message Types */}
            <div>
              <p className="text-xs font-semibold text-gray-600 mb-2 uppercase tracking-wider">By Type</p>
              <div className="space-y-1.5">
                {Object.entries(TYPE_CONFIG).map(([type, cfg]) => (
                  <div key={type} className="flex items-center justify-between">
                    <span className={`text-xs flex items-center gap-1 ${cfg.color}`}>
                      {cfg.icon} {cfg.label}
                    </span>
                    <span className="text-xs font-bold text-gray-400 tabular-nums">{typeCounts[type] || 0}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Top Senders */}
            <div className="pt-3 border-t border-gray-800">
              <p className="text-xs font-semibold text-gray-600 mb-2 uppercase tracking-wider">Top Senders</p>
              <div className="space-y-1.5">
                {Object.entries(senderCounts)
                  .sort((a, b) => b[1] - a[1])
                  .slice(0, 6)
                  .map(([agent, count]) => (
                    <div key={agent} className="flex items-center gap-1.5">
                      <span className="text-sm">{agents.find(a => a.name === agent)?.emoji || '🤖'}</span>
                      <span className="text-xs text-gray-500 truncate flex-1">{agent}</span>
                      <span className="text-xs font-bold text-gray-300 tabular-nums">{count}</span>
                    </div>
                  ))}
              </div>
            </div>

            {/* Last Alert */}
            <div className="pt-3 border-t border-gray-800">
              <p className="text-xs font-semibold text-gray-600 mb-2 uppercase tracking-wider">Last Alert</p>
              {messages.filter(m => m.type === 'alert').slice(-1).map(m => (
                <div key={m.id} className="bg-red-950/50 border border-red-900/50 rounded-xl p-2.5">
                  <p className="text-xs text-red-300 leading-relaxed line-clamp-3">{m.subject}</p>
                  <p className="text-xs text-gray-600 mt-1">{formatTime(m.timestamp)}</p>
                </div>
              ))}
              {!messages.some(m => m.type === 'alert') && (
                <p className="text-xs text-gray-700">No alerts yet</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
