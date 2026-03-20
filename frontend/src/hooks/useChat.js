import { useMutation } from '@tanstack/react-query'
import { toast } from 'sonner'
import { sendChatMessage } from '../api/chat'

export function useChat(options = {}) {
  return useMutation({
    mutationFn: (message) => sendChatMessage(message),
    onError: (err) => {
      if (err?.status === 429) {
        toast.error('Daily chat limit reached. Try again tomorrow.')
        return
      }
      const msg = err?.message || 'Something went wrong.'
      if (err?.status >= 500) {
        toast.error('Chat failed. Please try again in a moment.')
        return
      }
      toast.error(msg)
    },
    ...options,
  })
}
