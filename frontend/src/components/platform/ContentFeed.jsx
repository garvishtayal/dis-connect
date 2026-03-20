import { useEffect, useState } from 'react'
import Masonry from 'react-responsive-masonry'
import { Loader2 } from 'lucide-react'
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
  const {
    data,
    isLoading,
    isFetchingNextPage,
    fetchNextPage,
    hasNextPage,
  } = useContentFeed({ limit: 40 })

  const content = data?.pages?.flatMap((page) => page?.items ?? []) ?? []
  const mixedContent = interleaveContent(content)

  useEffect(() => {
    const handleScroll = () => {
      if (!hasNextPage || isFetchingNextPage) return

      const scrolledToBottom =
        window.innerHeight + window.scrollY >=
        document.documentElement.scrollHeight - 1000

      if (scrolledToBottom) fetchNextPage()
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
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
      {(isLoading || isFetchingNextPage) && (
        <div className="flex justify-center items-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-[#0D9488]" />
        </div>
      )}
    </>
  )
}

