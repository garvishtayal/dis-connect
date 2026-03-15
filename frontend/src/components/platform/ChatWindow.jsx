import { useState } from 'react'
import { Sparkles } from 'lucide-react'

const INITIAL_MESSAGES = [
  {
    id: '1',
    role: 'advisor',
    content:
      "Hi! I'm here to help you plan and achieve your creative goals on dis-connect. Tell me what you're working towards — I'll give you tailored advice and update your focus as we chat.",
  },
  {
    id: '2',
    role: 'user',
    content: 'I want to build a photography portfolio and start getting clients',
  },
  {
    id: '3',
    role: 'advisor',
    content:
      'Great starting point. For the first 30 days, focus on two things: uploading 10-15 of your strongest images across 2-3 consistent themes, and writing a short bio that names your specialty. Clients scan fast — clarity wins.',
  },
]

export function ChatWindow() {
  const [messages, setMessages] = useState(INITIAL_MESSAGES)
  const [input, setInput] = useState('')

  const handleSend = () => {
    if (!input.trim()) return

    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')

    setTimeout(() => {
      const advisorMessage = {
        id: (Date.now() + 1).toString(),
        role: 'advisor',
        content:
          'I understand. Let me help you refine that goal and create an action plan.',
      }
      setMessages((prev) => [...prev, advisorMessage])
    }, 800)
  }

  return (
    <div className="h-screen bg-white border-l border-gray-100 flex flex-col fixed top-0 right-0 w-[20%]">
      <div className="px-5 pt-5 pb-4 border-b border-gray-100">
        <div className="flex items-center justify-between mb-1">
          <div className="flex items-baseline gap-1">
            <span className="text-[15px] font-normal text-gray-700">Goal</span>
            <span className="text-[15px] font-normal bg-gradient-to-r from-[#0D9488] to-[#14B8A6] bg-clip-text text-transparent">
              advisor
            </span>
          </div>
          <span className="text-[12px] text-gray-400 tracking-wide">
            ● CopilotKit
          </span>
        </div>
        <p className="text-[11px] text-gray-400 leading-tight font-mono">
          chat to plan, refine & grow your creative path
        </p>
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-3">
        {messages.map((message) => (
          <div key={message.id} className="space-y-1">
            <div className="text-[12px] text-gray-400 uppercase tracking-wide">
              {message.role === 'user' ? 'YOU' : 'ADVISOR'}
            </div>
            <div
              className={`rounded-lg p-2 text-[12px] leading-relaxed ${
                message.role === 'user'
                  ? 'bg-gradient-to-br from-[#0D9488] to-[#14B8A6] text-white'
                  : 'bg-gray-50 text-gray-700'
              }`}
            >
              {message.content}
            </div>
          </div>
        ))}
      </div>

      <div className="p-4 border-t border-gray-100">
        <div className="relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type your message..."
            className="w-full px-3 py-2.5 text-[13px] bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:border-[#0D9488]/30 focus:bg-white transition-all placeholder:text-gray-400"
          />
          <button
            type="button"
            onClick={handleSend}
            disabled={!input.trim()}
            className="absolute right-2 top-1/2 -translate-y-1/2 w-6 h-6 rounded bg-gradient-to-br from-[#0D9488] to-[#14B8A6] flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <Sparkles className="w-3 h-3 text-white" />
          </button>
        </div>
        <div className="flex items-center justify-between mt-2">
          <span className="text-[12px] text-gray-400">
            Press <span className="text-[15px]">↵</span> to send
          </span>
        </div>
      </div>
    </div>
  )
}
