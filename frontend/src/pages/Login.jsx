import { useNavigate } from 'react-router-dom'
import Footer from '../components/layout/Footer'
import LoginCard from '../components/login/LoginCard'
import { useSignInWithGoogle, useRedirectResult } from '../hooks/useSignInWithGoogle'
import { saveSession } from '../lib/session'
import { withGuestOnly } from '../hocs/withGuestOnly'

function Login() {
  const navigate = useNavigate()
  const { mutate, isPending, reset } = useSignInWithGoogle()

  const handleSuccess = (data) => {
    saveSession(data)
    navigate(data?.onboarding_completed ? '/platform' : '/initial', { replace: true })
  }

  useRedirectResult(handleSuccess)

  const handleSignIn = () => {
    reset()
    mutate(undefined, { onSuccess: handleSuccess })
  }

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-teal-50 via-emerald-50/30 to-white relative overflow-hidden">
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-teal-200/20 rounded-full blur-3xl -translate-y-1/2" />
      <div className="absolute bottom-1/3 right-0 w-80 h-80 bg-emerald-200/25 rounded-full blur-3xl translate-x-1/3" />
      <main className="flex-1 flex items-center justify-center p-6 relative z-10">
        <LoginCard onSignIn={handleSignIn} loading={isPending} />
      </main>
      <Footer />
    </div>
  )
}

export default withGuestOnly(Login)
