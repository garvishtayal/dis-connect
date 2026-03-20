import { useInfiniteQuery } from '@tanstack/react-query'
import { toast } from 'sonner'
import { fetchContent } from '../api/content'
import { getStoredUserId } from '../lib/session'
import { useAuthState } from './useAuthState'

export function useContentFeed({ limit = 20 } = {}) {
  const userId = getStoredUserId()
  const { user, loading } = useAuthState()

  return useInfiniteQuery({
    queryKey: ['content', userId, limit],
    enabled: Boolean(userId && user && !loading),
    initialPageParam: 0,
    queryFn: async ({ pageParam }) => {
      return fetchContent({ userId, limit, offset: pageParam })
    },
    getNextPageParam: (lastPage, pages) => {
      const items = lastPage?.items ?? []
      if (items.length < limit) return undefined
      return pages.length * limit
    },
    onError: (err) => {
      const msg = err?.message || 'Failed to fetch content.'
      if (msg.toLowerCase().includes('limit')) {
        toast.error('Daily content limit reached. Try again tomorrow.')
      } else {
        toast.error(msg)
      }
    },
  })
}

