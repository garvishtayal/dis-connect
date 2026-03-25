import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import Footer from '../components/layout/Footer'
import { withOnboardingPendingRequired } from '../hocs/withOnboardingPendingRequired'
import { useCreateUser } from '../hooks/useCreateUser'
import { saveSession, setOnboardingDone } from '../lib/session'

const PROMPT_TO_COPY = `I'm building a personalized content feed for someone and need a short profile to tailor it. Please answer these questions about me in a concise paragraph (4–6 sentences max):

1. What's my name?
2. What are my main goals right now — personally or professionally?
3. What do I genuinely care about or find meaningful?
4. What kind of person do I want to become?
5. What topics, hobbies, or areas do I enjoy consuming content about?

Write it in third person, as if describing me to someone who's curating content for me. Be specific, not generic.

talk about what his human characteristic is, pull from older chat not just latest things, his true self

`

function InitialPage() {
  const navigate = useNavigate()
  const [pastedResponse, setPastedResponse] = useState('')
  const [copied, setCopied] = useState(false)
  const { mutate: submitOnboarding, isPending } = useCreateUser()

  const handleCopyPrompt = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(PROMPT_TO_COPY)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      setPastedResponse(PROMPT_TO_COPY)
    }
  }, [])

  const handleSubmit = () => {
    const trimmed = pastedResponse?.trim()
    if (!trimmed) return
    submitOnboarding(
      { initial_prompt: trimmed },
      {
        onSuccess: (data) => {
          if (data?.onboarding_completed) setOnboardingDone()
          if (data) saveSession({ ...data, onboarding_completed: true })
          navigate('/platform', { replace: true })
        },
      }
    )
  }

  return (
    <div className="min-h-screen flex flex-col bg-white text-zinc-800">
      <main className="flex-1 flex flex-col items-center px-4 py-10 sm:py-14">
        <p className="text-sm font-medium text-zinc-500 uppercase tracking-widest mb-2">
          One-time setup
        </p>
        <h1 className="text-2xl sm:text-3xl font-semibold text-zinc-900 tracking-tight mb-3 text-center">
          Tell us about you
        </h1>
        <p className="text-zinc-600 text-center max-w-lg mb-10 text-sm sm:text-base">
          Copy the prompt below into your favourite LLM (ChatGPT, Claude, etc.), then paste the response here. We use it to tailor your feed and chats.
        </p>

        <div className="w-full max-w-4xl flex flex-col lg:flex-row gap-6 lg:gap-8 flex-1">
          <section className="flex-1 min-h-[200px] lg:min-h-[280px] rounded-2xl border border-zinc-200 bg-zinc-50/80 p-5 sm:p-6 flex flex-col">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-medium text-zinc-500 uppercase tracking-wider">
                Copy this prompt
              </span>
              <button
                type="button"
                onClick={handleCopyPrompt}
                className="text-xs font-medium text-emerald-600 hover:text-emerald-500 transition-colors cursor-pointer"
              >
                {copied ? 'Copied' : 'Copy'}
              </button>
            </div>
            <div className="flex-1 rounded-xl bg-white border border-zinc-200 p-4 text-zinc-700 text-sm leading-relaxed select-all">
              {PROMPT_TO_COPY}
            </div>
          </section>

          <section className="flex-1 min-h-[200px] lg:min-h-[280px] rounded-2xl border border-zinc-200 bg-zinc-50/80 p-5 sm:p-6 flex flex-col">
            <label htmlFor="paste-response" className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-3 block">
              Paste your LLM response here
            </label>
            <textarea
              id="paste-response"
              value={pastedResponse}
              onChange={(e) => setPastedResponse(e.target.value)}
              placeholder="Paste the response from your LLM…"
              className="flex-1 min-h-[140px] w-full rounded-xl bg-white border border-zinc-200 p-4 text-zinc-700 text-sm leading-relaxed placeholder:text-zinc-400 resize-none focus:outline-none focus:border-zinc-400 focus:ring-1 focus:ring-zinc-300/50 transition-colors"
              disabled={isPending}
            />
          </section>
        </div>

        <div className="mt-8 w-full max-w-4xl flex justify-end">
          <button
            type="button"
            onClick={handleSubmit}
            disabled={!pastedResponse?.trim() || isPending}
            className="px-6 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 disabled:pointer-events-none text-white font-medium text-sm transition-colors"
          >
            {isPending ? 'Saving…' : 'Continue'}
          </button>
        </div>
      </main>
      <Footer />
    </div>
  )
}

export default withOnboardingPendingRequired(InitialPage)
