import Logo from './Logo'
import GoogleSignInButton from './GoogleSignInButton'

export default function LoginCard({ onSignIn, loading }) {
  return (
    <div className="w-full max-w-[400px] text-center rounded-3xl p-8 sm:p-10 bg-white/90 backdrop-blur-xl border border-teal-100/80 shadow-[0_0_0_1px_rgba(13,148,136,0.05),0_20px_50px_-12px_rgba(13,148,136,0.2)]">
      <Logo />
      <p className="text-[0.95rem] text-teal-700/90 mb-8 font-medium tracking-tight">
        Your space to focus. Curated for you.
      </p>
      <GoogleSignInButton onClick={onSignIn} loading={loading} />
    </div>
  )
}
