import { useMutation } from '@tanstack/react-query'
import { toast } from 'sonner'
import { createUser } from '../api/user'

export function useCreateUser() {
  return useMutation({
    mutationFn: ({ initial_prompt }) => createUser(initial_prompt),
    onError: (err) => {
      toast.error(err?.message || 'Something went wrong.')
    },
  })
}
