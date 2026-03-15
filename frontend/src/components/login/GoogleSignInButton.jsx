import { Loader2 } from 'lucide-react'
import GoogleLogo from './GoogleLogo'

const buttonClass =
  'w-full inline-flex items-center justify-center gap-3 py-3.5 px-6 text-[0.95rem] font-semibold rounded-xl border cursor-pointer bg-white text-gray-800 border-gray-200 shadow-sm transition hover:bg-gray-50 hover:border-gray-300 hover:shadow-md active:scale-[0.99] disabled:opacity-85 disabled:cursor-not-allowed disabled:hover:scale-100'

export default function GoogleSignInButton({ loading, onClick, disabled }) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled ?? loading}
      className={buttonClass}
    >
      {loading ? (
        <Loader2 size={20} className="animate-spin text-[#0D9488]" />
      ) : (
        <GoogleLogo />
      )}
      <span>{loading ? 'Signing in…' : 'Continue with Google'}</span>
    </button>
  )
}
