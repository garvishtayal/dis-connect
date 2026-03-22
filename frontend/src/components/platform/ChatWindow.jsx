import { useEffect, useRef, useState } from 'react'
import { Sparkles } from 'lucide-react'
import { useChat } from '../../hooks/useChat'
import { useAuthState } from '../../hooks/useAuthState'
import { getStoredUserId } from '../../lib/session'

const INTRO_DISPLAY =
  "Hi! I'm here to help you plan and achieve your creative goals on dis-connect. Tell me what you're working towards — I'll give you tailored advice and update your focus as we chat."

// Prompt sent to backend on behalf of the user (we display a nicer message immediately).
const INTRO_PROMPT = 'hi give intro msg..'
const FEED_REFRESH_MAX_TRIES = 1
const FEED_REFRESH_WAIT_MS = 25000

function SkeletonBubble() {
  return (
    <div className="space-y-2">
      <div className="h-3 w-3/4 bg-gray-200 rounded animate-pulse" />
      <div className="h-3 w-1/2 bg-gray-200 rounded animate-pulse" />
    </div>
  )
}

function requestFeedRefreshOnce() {
  const requestId = `${Date.now()}-${Math.random().toString(16).slice(2)}`
  return new Promise((resolve) => {
    const timeoutId = setTimeout(() => {
      window.removeEventListener('content:refresh:done', onDone)
      resolve(false)
    }, FEED_REFRESH_WAIT_MS)

    const onDone = (event) => {
      const detail = event?.detail || {}
      if (detail.requestId !== requestId) return
      clearTimeout(timeoutId)
      window.removeEventListener('content:refresh:done', onDone)
      resolve(Boolean(detail.ok && detail.count > 0))
    }

    window.addEventListener('content:refresh:done', onDone)
    window.dispatchEvent(new CustomEvent('content:refresh', { detail: { requestId } }))
  })
}

export function ChatWindow() {
  const { user, loading: authLoading } = useAuthState()
  const storedUserId = getStoredUserId()

  const chatMutation = useChat()
  const isChatPending = chatMutation.isPending

  const [messages, setMessages] = useState(() => [
    {
      id: 'intro-advisor',
      role: 'advisor',
      content: '',
      isSkeleton: true,
    },
  ])
  const [input, setInput] = useState('')
  const [isUpdatingFeed, setIsUpdatingFeed] = useState(false)
  const [updatingDots, setUpdatingDots] = useState('')

  const canChat = Boolean(user && storedUserId && !authLoading)
  const disableInput = authLoading || !canChat || isChatPending || isUpdatingFeed

  const textareaRef = useRef(null)
  useEffect(() => {
    if (!isUpdatingFeed) return

    const frames = ['', '.', '..', '...']
    let idx = 0
    const t = setInterval(() => {
      idx = (idx + 1) % frames.length
      setUpdatingDots(frames[idx])
    }, 220)

    return () => clearInterval(t)
  }, [isUpdatingFeed])

  const scrollRef = useRef(null)
  useEffect(() => {
    scrollRef.current?.scrollTo?.({ top: scrollRef.current.scrollHeight })
  }, [messages, isUpdatingFeed])

  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`
  }, [input])

  const didBootstrapIntro = useRef(false)
  useEffect(() => {
    if (!canChat) return
    if (didBootstrapIntro.current) return
    didBootstrapIntro.current = true

    chatMutation.mutate(INTRO_PROMPT, {
      onSuccess: (data) => {
        const nextText = data?.chat_response || INTRO_DISPLAY
        setMessages((prev) =>
          prev.map((m) =>
            m.id === 'intro-advisor' ? { ...m, content: nextText, isSkeleton: false } : m,
          ),
        )
      },
      onError: () => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === 'intro-advisor' ? { ...m, content: INTRO_DISPLAY, isSkeleton: false } : m,
          ),
        )
      },
    })
  }, [canChat, chatMutation])

  const handleSend = () => {
    if (!input.trim()) return
    if (!canChat) return
    if (isChatPending || isUpdatingFeed) return

    const userText = input.trim()
    setInput('')

    const userMsgId = Date.now().toString()
    const advisorSkeletonId = (Date.now() + 1).toString()

    setMessages((prev) => [
      ...prev,
      { id: userMsgId, role: 'user', content: userText, isSkeleton: false },
      { id: advisorSkeletonId, role: 'advisor', content: '', isSkeleton: true },
    ])

    chatMutation.mutate(userText, {
      onSuccess: async (data) => {
        const advisorText = data?.chat_response || ''
        const needsNewContent = Boolean(data?.needs_new_content)

        setMessages((prev) =>
          prev.map((m) =>
            m.id === advisorSkeletonId ? { ...m, content: advisorText, isSkeleton: false } : m,
          ),
        )

        if (!needsNewContent) return

        // Show minimal loading in chat, then refresh the feed.
        const feedMsgId = (Date.now() + 2).toString()
        setIsUpdatingFeed(true)
        setMessages((prev) => [
          ...prev,
          {
            id: feedMsgId,
            role: 'advisor',
            kind: 'updating_feed',
            content: '',
            isSkeleton: false,
            hideRoleLabel: true,
          },
        ])

        try {
          let gotContent = false
          let attempts = 0
          while (!gotContent && attempts < FEED_REFRESH_MAX_TRIES) {
            attempts += 1
            // Keep chat blocked and keep trying until feed gets fresh items.
            gotContent = await requestFeedRefreshOnce()
          }
        } finally {
          setMessages((prev) => prev.filter((m) => m.id !== feedMsgId))
          setIsUpdatingFeed(false)
        }
      },
    })
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
          <span className="text-[12px] text-gray-400 tracking-wide">● Advisor</span>
        </div>
        <p className="text-[11px] text-gray-400 leading-tight font-mono">
          chat to plan, refine & grow your creative path
        </p>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto px-5 py-4 space-y-3">
        {messages.map((message) => (
          <div key={message.id} className="space-y-1">
            {!message.hideRoleLabel && (
              <div className="text-[12px] text-gray-400 uppercase tracking-wide">
                {message.role === 'user' ? 'YOU' : 'ADVISOR'}
              </div>
            )}
            <div
              className={`rounded-lg p-2 text-[12px] leading-relaxed ${
                message.role === 'user'
                  ? 'bg-gradient-to-br from-[#0D9488] to-[#14B8A6] text-white'
                  : message.kind === 'updating_feed'
                    ? 'bg-gray-50 text-gray-600 font-mono'
                    : 'bg-gray-50 text-gray-700'
              }`}
            >
              {message.isSkeleton ? (
                <SkeletonBubble />
              ) : message.kind === 'updating_feed' ? (
                <div className="whitespace-nowrap overflow-hidden text-ellipsis">
                  Generating new content{updatingDots}
                </div>
              ) : (
                message.content
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="p-4 border-t border-gray-100">
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                // GPT-style: Shift+Enter => new line (even if input is empty).
                if (e.shiftKey) return

                // Enter => send
                e.preventDefault()
                handleSend()
              }
            }}
            placeholder={disableInput ? '...' : 'Type your message...'}
            disabled={disableInput}
            rows={1}
            className="w-full px-3 py-2.5 text-[13px] bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:border-[#0D9488]/30 focus:bg-white transition-all placeholder:text-gray-400 disabled:opacity-70 disabled:cursor-not-allowed resize-none overflow-hidden leading-relaxed min-h-[44px] max-h-[160px]"
          />
          <button
            type="button"
            onClick={handleSend}
            disabled={!input.trim() || disableInput}
            className="absolute right-2 bottom-2 w-6 h-6 rounded bg-gradient-to-br from-[#0D9488] to-[#14B8A6] flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <Sparkles className="w-3 h-3 text-white" />
          </button>
        </div>
        <div className="flex items-center justify-between mt-2">
          <span className="text-[12px] text-gray-400">
            Press <span className="text-[15px]">↵</span> to send. <span className="font-mono">Shift+↵</span> for new line.
          </span>
        </div>
      </div>
    </div>
  )
}
