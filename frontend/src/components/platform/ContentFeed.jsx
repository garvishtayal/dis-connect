import { useEffect, useRef, useState } from 'react'
import Masonry from 'react-responsive-masonry'
import { Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { ContentCard } from './ContentCard'
import { useContentFeed } from '../../hooks/useContentFeed'

function interleaveContent(items) {
  const images = []
  const shorts = []
  const videos = []

  for (const it of items) {
    if (!it) continue
    if (it.type === 'image') images.push(it)
    else if (it.type === 'short' || it.type === 'reel') shorts.push(it)
    else if (it.type === 'video') videos.push(it)
    else images.push(it) // unknown types fall back to images
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

export function ContentFeed() {
  const [activeItemId, setActiveItemId] = useState(null)
  const bottomSentinelRef = useRef(null)
  const {
    data,
    isLoading,
    isError,
    error,
    isFetchingNextPage,
    fetchNextPage,
    hasNextPage,
  } = useContentFeed({ limit: 40 })

  // Interleave within each page so adding a new page doesn't reshuffle earlier items.
  const mixedContent = (data?.pages ?? []).flatMap((page) =>
    interleaveContent(page?.items ?? []),
  )

  useEffect(() => {
    if (isError && error?.message) {
      toast.error(error.message, { duration: 4000 })
    }
  }, [isError, error?.message])

  useEffect(() => {
    const el = bottomSentinelRef.current
    if (!el) return
    if (!('IntersectionObserver' in window)) return

    const obs = new IntersectionObserver(
      (entries) => {
        const entry = entries[0]
        if (!entry?.isIntersecting) return
        if (!hasNextPage || isFetchingNextPage) return
        fetchNextPage()
      },
      { root: null, threshold: 0.1 },
    )

    obs.observe(el)
    return () => obs.disconnect()
  }, [fetchNextPage, hasNextPage, isFetchingNextPage])

  return (
    <>
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

      <div ref={bottomSentinelRef} className="h-2" />

      {(isLoading || isFetchingNextPage) && (
        <div className="flex justify-center items-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-[#0D9488]" />
        </div>
      )}
    </>
  )
}

