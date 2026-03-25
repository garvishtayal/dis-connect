import { useInfiniteQuery } from '@tanstack/react-query'
import { fetchContent } from '../api/content'
import { getStoredUserId } from '../lib/session'
import { useAuthState } from './useAuthState'

export function useContentFeed({ limit = 100 } = {}) {
  const userId = getStoredUserId()
  const { user, loading } = useAuthState()

  return useInfiniteQuery({
    queryKey: ['content', userId, limit],
    enabled: Boolean(userId && user && !loading),
    initialPageParam: 0,
    queryFn: async ({ pageParam }) => {
      try {
        return await fetchContent({ userId, limit, offset: pageParam })
      } catch (err) {
        const msg = err?.message || 'Failed to fetch content.'
        throw new Error(msg)
      }
    },
    getNextPageParam: (lastPage, pages) => {
      const items = lastPage?.items ?? []
      if (items.length < limit) return undefined
      return pages.length * limit
    },
  })
}

