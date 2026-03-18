import { useState } from 'react'
import { analyticsApi } from '../../api/client'

interface Message {
  role: 'user' | 'assistant'
  text: string
}

export default function NLQAChat() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', text: 'Ask me anything about your marketing performance! e.g. "Why did our CPA increase last week?"' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const ask = async () => {
    if (!input.trim()) return
    const question = input.trim()
    setInput('')
    setMessages(m => [...m, { role: 'user', text: question }])
    setLoading(true)
    try {
      const res = await analyticsApi.ask(question)
      setMessages(m => [...m, { role: 'assistant', text: res.data.answer }])
    } catch {
      setMessages(m => [...m, { role: 'assistant', text: 'Sorry, I could not process your question right now.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm flex flex-col h-96">
      <div className="p-4 border-b border-gray-50">
        <h3 className="text-sm font-semibold text-gray-900">Ask Claude About Your Data</h3>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-xs text-sm px-3 py-2 rounded-xl ${m.role === 'user' ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-800'}`}>
              {m.text}
            </div>
          </div>
        ))}
        {loading && <div className="text-xs text-gray-400 animate-pulse">Claude is thinking...</div>}
      </div>
      <div className="p-4 border-t border-gray-50 flex gap-2">
        <input
          className="flex-1 border rounded-lg px-3 py-2 text-sm"
          placeholder="Ask about your campaigns..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && ask()}
        />
        <button onClick={ask} disabled={loading} className="bg-primary-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-primary-700 disabled:opacity-50">
          Ask
        </button>
      </div>
    </div>
  )
}
