import { useMutation } from '@tanstack/react-query'
import { toast } from 'sonner'
import { sendChatMessage } from '../api/chat'

export function useChat(options = {}) {
  return useMutation({
    mutationFn: (message) => sendChatMessage(message),
    onError: (err) => {
      const msg = err?.message || 'Something went wrong.'
      if (msg.toLowerCase().includes('limit')) {
        toast.error('Daily chat limit reached. Try again tomorrow.')
      } else {
        toast.error(msg)
      }
    },
    ...options,
  })
}
