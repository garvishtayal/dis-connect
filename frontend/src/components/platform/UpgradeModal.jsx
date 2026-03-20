import { createPortal } from 'react-dom'

export function UpgradeModal({
  open,
  mode,
  feedback,
  upgradedChoice,
  willingToPay,
  isSubmitting,
  onClose,
  onFeedbackChange,
  onUpgradedChoiceChange,
  onWillingToPayChange,
  onSubmit,
}) {
  if (!open || typeof document === 'undefined') return null

  return createPortal(
    <div className="fixed inset-0 z-[120] bg-white/90 backdrop-blur-md">
      <div className="absolute inset-0 bg-gradient-to-br from-white via-emerald-50/70 to-teal-100/70" />
      <div className="relative h-full w-full flex items-center justify-center p-6 overflow-y-auto">
        <div className="w-full max-w-2xl rounded-3xl border border-emerald-100 bg-white/95 shadow-[0_30px_90px_-35px_rgba(13,148,136,0.45)] p-8">
          {mode === 'thanks' ? (
            <>
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Thank You</h2>
                <p className="text-sm text-gray-700 mt-3 leading-relaxed">
                  Thanks for sharing your interest in upgrading. We are finalizing
                  the upgrade plans, and we will reach out as soon as details are
                  confirmed to share the next steps.
                </p>
              </div>
              <div className="mt-8 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2 rounded-xl text-sm border border-gray-200 text-gray-700 hover:bg-gray-50"
                >
                  Close
                </button>
              </div>
            </>
          ) : (
            <>
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
                onChange={(e) => onFeedbackChange(e.target.value)}
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
                      onClick={() => onUpgradedChoiceChange(opt)}
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
                      onClick={() => onWillingToPayChange(opt)}
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
                  onClick={onClose}
                  className="px-4 py-2 rounded-xl text-sm border border-gray-200 text-gray-700 hover:bg-gray-50"
                  disabled={isSubmitting}
                >
                  Close
                </button>
                <button
                  type="button"
                  onClick={onSubmit}
                  disabled={isSubmitting}
                  className="px-5 py-2 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-[#0D9488] to-[#14B8A6] disabled:opacity-60"
                >
                  {isSubmitting ? 'Saving...' : 'Submit'}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>,
    document.body,
  )
}
