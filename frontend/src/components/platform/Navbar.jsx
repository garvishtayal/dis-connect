import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ChevronDown, LogOut, UserPen } from 'lucide-react'
import { signOut } from 'firebase/auth'
import { auth } from '../../lib/firebase'
import { clearSession } from '../../lib/session'
import { useAuthState } from '../../hooks/useAuthState'
import { toast } from 'sonner'
import { getUpgradeFeedback, submitUpgradeFeedback } from '../../api/upgrade'
import { UpgradeModal } from './UpgradeModal'

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
  const [upgradeMode, setUpgradeMode] = useState('form')
  const [feedback, setFeedback] = useState('')
  const [upgradedChoice, setUpgradedChoice] = useState('')
  const [willingToPay, setWillingToPay] = useState('')
  const [isSubmittingUpgrade, setIsSubmittingUpgrade] = useState(false)
  const [isLoadingUpgrade, setIsLoadingUpgrade] = useState(false)
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

  const handleOpenUpgrade = async () => {
    setIsLoadingUpgrade(true)
    try {
      const record = await getUpgradeFeedback()
      if (record?.upgraded) {
        setUpgradeMode('thanks')
      } else {
        setUpgradeMode('form')
      }
      setFeedback(record?.feedback || '')
      setWillingToPay(record?.willing_to_pay || '')
      setUpgradedChoice(record?.upgraded ? 'yes' : '')
    } catch {
      // If no record exists yet, default to fresh form.
      setUpgradeMode('form')
      setFeedback('')
      setWillingToPay('')
      setUpgradedChoice('')
    } finally {
      setIsLoadingUpgrade(false)
      setUpgradeOpen(true)
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
          onClick={handleOpenUpgrade}
          className="absolute left-1/2 -translate-x-1/2 text-sm font-semibold upgrade-shine"
          disabled={isLoadingUpgrade}
        >
          {isLoadingUpgrade ? 'Loading...' : 'Upgrade'}
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
      <UpgradeModal
        open={upgradeOpen}
        mode={upgradeMode}
        feedback={feedback}
        upgradedChoice={upgradedChoice}
        willingToPay={willingToPay}
        isSubmitting={isSubmittingUpgrade}
        onClose={() => setUpgradeOpen(false)}
        onFeedbackChange={setFeedback}
        onUpgradedChoiceChange={setUpgradedChoice}
        onWillingToPayChange={setWillingToPay}
        onSubmit={handleUpgradeSubmit}
      />
    </>
  )
}
