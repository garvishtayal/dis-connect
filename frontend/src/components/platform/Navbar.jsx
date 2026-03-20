import { useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { Link, useNavigate } from 'react-router-dom'
import { ChevronDown, LogOut, UserPen } from 'lucide-react'
import { signOut } from 'firebase/auth'
import { auth } from '../../lib/firebase'
import { clearSession } from '../../lib/session'
import { useAuthState } from '../../hooks/useAuthState'
import { toast } from 'sonner'
import { submitUpgradeFeedback } from '../../api/upgrade'

function Avatar({ src, alt }) {
  return (
    <img
      src={src}
      alt={alt}
      className="w-7 h-7 rounded-full object-cover bg-gray-100"
      referrerPolicy="no-referrer"
    />
  )
}

export function Navbar() {
  const navigate = useNavigate()
  const { user, loading } = useAuthState()
  const [open, setOpen] = useState(false)
  const [upgradeOpen, setUpgradeOpen] = useState(false)
  const [feedback, setFeedback] = useState('')
  const [upgradedChoice, setUpgradedChoice] = useState('')
  const [willingToPay, setWillingToPay] = useState('')
  const [isSubmittingUpgrade, setIsSubmittingUpgrade] = useState(false)
  const wrapRef = useRef(null)

  useEffect(() => {
    if (!open) return
    const onDown = (e) => {
      const el = wrapRef.current
      if (!el) return
      if (el.contains(e.target)) return
      setOpen(false)
    }

    document.addEventListener('mousedown', onDown)
    return () => document.removeEventListener('mousedown', onDown)
  }, [open])

  const handleLogout = async () => {
    try {
      await signOut(auth)
      clearSession()
      navigate('/login', { replace: true })
    } catch {
      toast.error('Logout failed. Please try again.', { duration: 4000 })
    } finally {
      setOpen(false)
    }
  }

  const handleUpgradeSubmit = async () => {
    if (!upgradedChoice) {
      toast.error('Please choose if you want to upgrade.')
      return
    }
    if (!willingToPay) {
      toast.error('Please choose how much you are comfortable paying.')
      return
    }
    setIsSubmittingUpgrade(true)
    try {
      await submitUpgradeFeedback({
        upgraded: upgradedChoice === 'yes',
        feedback,
        willing_to_pay: willingToPay,
      })
      toast.success('Thanks. Your upgrade preference is saved.', { duration: 3000 })
      setUpgradeOpen(false)
      setFeedback('')
      setUpgradedChoice('')
      setWillingToPay('')
    } catch (err) {
      toast.error(err?.message || 'Could not save upgrade details.', { duration: 4000 })
    } finally {
      setIsSubmittingUpgrade(false)
    }
  }

  return (
    <>
      <nav className="fixed top-0 left-0 w-[80%] z-50 bg-white/100 backdrop-blur-xl border-b border-gray-100">
      <div className="flex items-center justify-between h-14 px-6">
        <Link to="/platform" className="flex items-center group">
          <img
            src="/logo-dis-connect-small.png"
            alt="Dis-Connect Logo"
            className="w-[120px] object-contain"
          />
        </Link>

        <button
          type="button"
          onClick={() => setUpgradeOpen(true)}
          className="absolute left-1/2 -translate-x-1/2 text-sm font-semibold upgrade-shine"
        >
          Upgrade
        </button>

        <div ref={wrapRef} className="relative">
          {user ? (
            <>
              <button
                type="button"
                onClick={() => setOpen((v) => !v)}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-gray-50 transition-all cursor-pointer"
              >
                {user.photoURL ? (
                  <Avatar src={user.photoURL} alt="User avatar" />
                ) : (
                  <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#0D9488] to-[#14B8A6]" />
                )}
                <ChevronDown className="w-3.5 h-3.5 text-gray-700" />
              </button>

              {open && (
                <div className="absolute right-0 mt-2 w-56 rounded-2xl border border-gray-100 bg-white/95 backdrop-blur-xl shadow-[0_12px_40px_-20px_rgba(13,148,136,0.35)] overflow-hidden">
                  <div className="px-4 py-3 bg-gradient-to-br from-teal-50 to-emerald-50 border-b border-gray-100">
                    <div className="flex items-center gap-3">
                      {user.photoURL ? (
                        <Avatar src={user.photoURL} alt="User avatar" />
                      ) : (
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#0D9488] to-[#14B8A6]" />
                      )}
                      <div className="min-w-0">
                        <div className="text-sm font-semibold text-gray-900 truncate">
                          {user.displayName || 'User'}
                        </div>
                        <div className="text-xs text-gray-600 truncate">
                          {user.email || ''}
                        </div>
                      </div>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      setOpen(false)
                      navigate('/initial', { replace: true })
                    }}
                    className="w-full text-left px-4 py-3 text-sm hover:bg-gray-50 transition-colors cursor-pointer flex items-center gap-2"
                  >
                    <UserPen className="w-4 h-4 text-gray-700" />
                    Update profile
                  </button>
                  <div className="h-px bg-gray-100" />
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="w-full text-left px-4 py-3 text-sm hover:bg-gray-50 transition-colors cursor-pointer flex items-center gap-2"
                  >
                    <LogOut className="w-4 h-4 text-gray-700" />
                    Logout
                  </button>
                </div>
              )}
            </>
          ) : (
            null
          )}
          {loading && (
            <div className="w-[110px] h-[34px] rounded-lg bg-gray-100 animate-pulse" />
          )}
        </div>
      </div>

      </nav>
      {upgradeOpen && typeof document !== 'undefined'
        ? createPortal(
            <div className="fixed inset-0 z-[120] bg-white/90 backdrop-blur-md">
              <div className="absolute inset-0 bg-gradient-to-br from-white via-emerald-50/70 to-teal-100/70" />
              <div className="relative h-full w-full flex items-center justify-center p-6 overflow-y-auto">
                <div className="w-full max-w-2xl rounded-3xl border border-emerald-100 bg-white/95 shadow-[0_30px_90px_-35px_rgba(13,148,136,0.45)] p-8">
                  <div className="mb-6">
                    <h2 className="text-2xl font-bold text-gray-900">Upgrade Experience</h2>
                    <p className="text-sm text-gray-600 mt-2">
                      Quick check-in: how did you like the product, and do you want to use it more?
                    </p>
                  </div>

                  <label className="block text-sm font-medium text-gray-800 mb-2">
                    How are you liking dis-connect so far?
                  </label>
                  <textarea
                    value={feedback}
                    onChange={(e) => setFeedback(e.target.value)}
                    rows={5}
                    placeholder="Share what worked for you and what could be better..."
                    className="w-full rounded-2xl border border-gray-200 bg-white px-4 py-3 text-sm resize-none overflow-y-auto focus:outline-none focus:ring-1 focus:ring-black/15 focus:border-black/20"
                  />

                  <div className="mt-6">
                    <p className="text-sm font-medium text-gray-800 mb-3">
                      Are you willing to upgrade?
                    </p>
                    <div className="flex gap-3">
                      {['yes', 'no'].map((opt) => (
                        <button
                          key={opt}
                          type="button"
                          onClick={() => setUpgradedChoice(opt)}
                          className={`px-4 py-2 rounded-xl text-sm font-medium border transition-all ${
                            upgradedChoice === opt
                              ? 'bg-gradient-to-r from-[#0D9488] to-[#14B8A6] text-white border-transparent shadow'
                              : 'bg-white text-gray-700 border-gray-200 hover:border-emerald-300'
                          }`}
                        >
                          {opt === 'yes' ? 'Yes' : 'No'}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="mt-6">
                    <p className="text-sm font-medium text-gray-800 mb-3">
                      If yes, how much are you comfortable paying per month?
                    </p>
                    <div className="flex flex-wrap gap-3">
                      {[
                        '$4 / month',
                        '$8 / month',
                        '$12 / month',
                        'Not willing to pay right now',
                      ].map((opt) => (
                        <button
                          key={opt}
                          type="button"
                          onClick={() => setWillingToPay(opt)}
                          className={`px-4 py-2 rounded-xl text-sm font-medium border transition-all ${
                            willingToPay === opt
                              ? 'bg-gradient-to-r from-[#0D9488] to-[#14B8A6] text-white border-transparent shadow'
                              : 'bg-white text-gray-700 border-gray-200 hover:border-emerald-300'
                          }`}
                        >
                          {opt}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="mt-8 flex items-center justify-end gap-3">
                    <button
                      type="button"
                      onClick={() => setUpgradeOpen(false)}
                      className="px-4 py-2 rounded-xl text-sm border border-gray-200 text-gray-700 hover:bg-gray-50"
                      disabled={isSubmittingUpgrade}
                    >
                      Close
                    </button>
                    <button
                      type="button"
                      onClick={handleUpgradeSubmit}
                      disabled={isSubmittingUpgrade}
                      className="px-5 py-2 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-[#0D9488] to-[#14B8A6] disabled:opacity-60"
                    >
                      {isSubmittingUpgrade ? 'Saving...' : 'Submit'}
                    </button>
                  </div>
                </div>
              </div>
            </div>,
            document.body,
          )
        : null}
    </>
  )
}
