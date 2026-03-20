import { useEffect, useState } from 'react'
import Masonry from 'react-responsive-masonry'
import { Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { ContentCard } from './ContentCard'
import { fetchContent } from '../../api/content'
import { getStoredUserId } from '../../lib/session'
import { useAuthState } from '../../hooks/useAuthState'

function interleaveContent(items) {
  if (!Array.isArray(items)) return []
  const images = []
  const shorts = []
  const videos = []

  for (const it of items) {
    if (!it) continue
    if (it.type === 'image') images.push(it)
    else if (it.type === 'short' || it.type === 'reel') shorts.push(it)
    else if (it.type === 'video') videos.push(it)
    else images.push(it)
  }

  const result = []
  let i = 0
  while (i < images.length || i < shorts.length || i < videos.length) {
    if (i < images.length) result.push(images[i])
    if (i < shorts.length) result.push(shorts[i])
    if (i < videos.length) result.push(videos[i])
    i += 1
  }

  return result
}

const MAX_RETRIES = 1

export function ContentFeed() {
  const [activeItemId, setActiveItemId] = useState(null)
  const [items, setItems] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [isFetchingMore, setIsFetchingMore] = useState(false)
  const [hasMore, setHasMore] = useState(true)
  const [errorCount, setErrorCount] = useState(0)
  const { user, loading: isAuthLoading } = useAuthState()
  const userId = getStoredUserId()
  const limit = 40

  async function loadContent(append, force = false) {
    if (!userId || !user) return { ok: false, count: 0 }
    if (append && !hasMore) return { ok: false, count: 0 }
    if (!force && errorCount >= MAX_RETRIES) return { ok: false, count: 0 }

    const setFlag = append ? setIsFetchingMore : setIsLoading
    setFlag(true)
    try {
      const res = await fetchContent({ userId, limit, offset: 0 })
      const batch = Array.isArray(res)
        ? res
        : Array.isArray(res?.items)
          ? res.items
          : []

      setItems((prev) => {
        if (!append) return batch

        const seen = new Set(prev.map((it) => it?.id || it?.url).filter(Boolean))
        const fresh = batch.filter((it) => {
          const key = it?.id || it?.url
          if (!key || seen.has(key)) return false
          seen.add(key)
          return true
        })

        if (fresh.length === 0) {
          setHasMore(false)
          return prev
        }
        return [...prev, ...fresh]
      })

      setErrorCount(0)
      if (batch.length === 0) setHasMore(false)
      return { ok: true, count: batch.length }
    } catch (err) {
      setErrorCount((n) => n + 1)
      toast.error(err?.message || 'Failed to fetch content.', { duration: 4000 })
      return { ok: false, count: 0 }
    } finally {
      setFlag(false)
    }
  }

  useEffect(() => {
    if (isAuthLoading || !userId || !user) return
    if (items.length > 0) return
    void loadContent(false)
  }, [isAuthLoading, userId, user])

  useEffect(() => {
    const handleRefreshFeed = async (event) => {
      const requestId = event?.detail?.requestId || null
      setHasMore(true)
      setErrorCount(0)
      const result = await loadContent(false, true)
      window.dispatchEvent(
        new CustomEvent('content:refresh:done', {
          detail: {
            requestId,
            ok: Boolean(result?.ok),
            count: Number(result?.count || 0),
          },
        }),
      )
    }
    window.addEventListener('content:refresh', handleRefreshFeed)
    return () => window.removeEventListener('content:refresh', handleRefreshFeed)
  }, [userId, user])

  useEffect(() => {
    const handleScroll = () => {
      if (!hasMore || isFetchingMore || isLoading) return
      if (errorCount >= MAX_RETRIES) return

      const scrolledToBottom =
        window.innerHeight + window.scrollY >=
        document.documentElement.scrollHeight - 1000

      if (scrolledToBottom) void loadContent(true)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [hasMore, isFetchingMore, isLoading, errorCount])

  const mixedContent = interleaveContent(items)

  return (
    <>
      {!isLoading && !isFetchingMore && mixedContent.length === 0 && (
        <div className="w-full min-h-[65vh] flex flex-col items-center justify-center text-center px-6">
          <img
            src="https://media.giphy.com/media/l0HlBO7eyXzSZkJri/giphy.gif"
            alt="No content animation"
            className="w-[260px] h-[260px] object-cover rounded-2xl shadow-[0_20px_60px_-30px_rgba(13,148,136,0.45)]"
            loading="lazy"
          />
          <h3 className="mt-5 text-xl font-semibold text-gray-900">
            Nothing to scroll... yet.
          </h3>
          <p className="mt-2 text-sm text-gray-600 max-w-md">
            Content generation took a nap. Try again in a bit and we will bring fresh vibes.
          </p>
        </div>
      )}

      <Masonry columnsCount={5} gutter="16px">
        {mixedContent.map((item) => (
          <ContentCard
            key={item.id}
            item={item}
            activeItemId={activeItemId}
            onActivate={setActiveItemId}
          />
        ))}
      </Masonry>

      {(isLoading || isFetchingMore) && (
        <div className="flex justify-center items-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-[#0D9488]" />
        </div>
      )}
    </>
  )
}
