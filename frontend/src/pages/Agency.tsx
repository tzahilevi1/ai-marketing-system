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

const TYPE_COLORS: Record<string, string> = {
  task: 'bg-blue-100 text-blue-700',
  approval_request: 'bg-yellow-100 text-yellow-700',
  approval_response: 'bg-green-100 text-green-700',
  report: 'bg-purple-100 text-purple-700',
  idea: 'bg-pink-100 text-pink-700',
  alert: 'bg-red-100 text-red-700',
  directive: 'bg-indigo-100 text-indigo-700',
}

export default function Agency() {
  const [agents, setAgents] = useState<AgentInfo[]>([])
  const [messages, setMessages] = useState<AgencyMessage[]>([])
  const [running, setRunning] = useState(false)
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const fetchStatus = async () => {
    try {
      const res = await api.get('/agency/status')
      setRunning(res.data.running)
      setAgents(res.data.agents || [])
      setMessages(res.data.message_history || [])
    } catch { /* agency not started yet */ }
  }

  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 3000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const startAgency = async () => {
    setLoading(true)
    await api.post('/agency/start')
    setLoading(false)
    setRunning(true)
    fetchStatus()
  }

  const stopAgency = async () => {
    await api.post('/agency/stop')
    setRunning(false)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AI Agency</h1>
          <p className="text-sm text-gray-500 mt-1">9 autonomous agents managing your marketing</p>
        </div>
        <div className="flex gap-3">
          {!running ? (
            <button onClick={startAgency} disabled={loading} className="bg-green-600 text-white px-5 py-2 rounded-lg text-sm hover:bg-green-700 disabled:opacity-50 font-medium">
              {loading ? 'Starting...' : 'Start Agency'}
            </button>
          ) : (
            <button onClick={stopAgency} className="bg-red-500 text-white px-5 py-2 rounded-lg text-sm hover:bg-red-600 font-medium">
              Stop Agency
            </button>
          )}
        </div>
      </div>

      {/* Agent Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
        {agents.map(agent => (
          <div key={agent.name} className={`bg-white rounded-xl border p-4 text-center transition-all ${agent.active ? 'border-green-200 shadow-sm' : 'border-gray-100 opacity-60'}`}>
            <div className="text-3xl mb-2">{agent.emoji}</div>
            <p className="text-xs font-semibold text-gray-800 leading-tight">{agent.role}</p>
            <div className={`mt-2 inline-block w-2 h-2 rounded-full ${agent.active ? 'bg-green-400' : 'bg-gray-300'}`} />
          </div>
        ))}
      </div>

      {/* Message Feed */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm">
        <div className="p-4 border-b border-gray-50 flex items-center justify-between">
          <h3 className="font-semibold text-gray-900">Agent Communications</h3>
          <span className="text-xs text-gray-400">{messages.length} messages</span>
        </div>
        <div className="h-96 overflow-y-auto p-4 space-y-2">
          {messages.length === 0 ? (
            <p className="text-center text-gray-400 text-sm mt-16">
              {running ? 'Agents are thinking...' : 'Start the agency to see agents communicate in real-time'}
            </p>
          ) : (
            messages.map(msg => (
              <div key={msg.id} className="flex items-start gap-3 text-xs">
                <span className="text-gray-400 shrink-0 w-20 text-right">{new Date(msg.timestamp).toLocaleTimeString()}</span>
                <span className="font-bold text-gray-700 shrink-0 w-24">{msg.from_agent}</span>
                <span className="text-gray-400">→</span>
                <span className="font-medium text-gray-600 shrink-0 w-24">{msg.to_agent}</span>
                <span className={`px-2 py-0.5 rounded-full shrink-0 ${TYPE_COLORS[msg.type] ?? 'bg-gray-100 text-gray-600'}`}>{msg.type}</span>
                <span className="text-gray-700 flex-1 truncate">{msg.subject}</span>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>
    </div>
  )
}
