import { X, Copy, Check, Sparkles } from "lucide-react";
import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";

interface ManifestModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const LLM_PROMPT = `I want to share my personal manifest with you. Please analyze and understand the following about me:

1. MY GOALS & ASPIRATIONS:
   - What I want to achieve in life
   - My short-term and long-term goals
   - What success means to me

2. MY INTERESTS & PASSIONS:
   - Topics and subjects that fascinate me
   - Hobbies and activities I love
   - What I enjoy learning about

3. MY VALUES & BELIEFS:
   - What principles guide my decisions
   - What matters most to me
   - How I want to impact the world

4. MY CURRENT JOURNEY:
   - Where I am right now in life
   - Challenges I'm facing
   - What I'm working on

5. MY INSPIRATION PREFERENCES:
   - Types of content that motivate me
   - Aesthetic preferences
   - Content formats I enjoy (images, videos, quotes, etc.)

Please provide a comprehensive manifest about me based on our conversation. Format it as a structured JSON that I can paste into dis-connect platform to get personalized content recommendations.`;

export function ManifestModal({ isOpen, onClose }: ManifestModalProps) {
  const [copied, setCopied] = useState(false);
  const [manifestText, setManifestText] = useState("");
  const [showSuccess, setShowSuccess] = useState(false);

  const handleCopyPrompt = () => {
    navigator.clipboard.writeText(LLM_PROMPT);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSaveManifest = () => {
    if (manifestText.trim()) {
      // In a real app, this would save to backend/Supabase
      localStorage.setItem("user-manifest", manifestText);
      setShowSuccess(true);
      setTimeout(() => {
        setShowSuccess(false);
        onClose();
      }, 1500);
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="bg-white rounded-3xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden"
        >
          {/* Header */}
          <div className="bg-gradient-to-br from-[#0D9488] to-[#14B8A6] p-6 text-white relative">
            <button
              onClick={onClose}
              className="absolute top-4 right-4 p-2 rounded-full bg-white/20 hover:bg-white/30 transition-all"
            >
              <X className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-3">
              <Sparkles className="w-8 h-8" />
              <div>
                <h2 className="text-2xl font-bold">Create Your Manifest</h2>
                <p className="text-white/90 text-sm mt-1">
                  Personalize your dis-connect experience with AI
                </p>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
            {/* Step 1 */}
            <div className="mb-8">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-8 h-8 rounded-full bg-[#0D9488]/10 text-[#0D9488] flex items-center justify-center font-semibold">
                  1
                </div>
                <h3 className="font-semibold text-lg">Copy the Prompt</h3>
              </div>
              <div className="bg-gray-50 rounded-xl p-4 relative border border-gray-200">
                <pre className="text-sm text-gray-700 whitespace-pre-wrap font-mono max-h-48 overflow-y-auto">
                  {LLM_PROMPT}
                </pre>
                <button
                  onClick={handleCopyPrompt}
                  className="absolute top-4 right-4 flex items-center gap-2 px-3 py-2 bg-white rounded-lg shadow-md hover:shadow-lg transition-all border border-gray-200"
                >
                  {copied ? (
                    <>
                      <Check className="w-4 h-4 text-green-600" />
                      <span className="text-sm text-green-600">Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4 text-gray-600" />
                      <span className="text-sm text-gray-600">Copy</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Step 2 */}
            <div className="mb-8">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-8 h-8 rounded-full bg-[#0D9488]/10 text-[#0D9488] flex items-center justify-center font-semibold">
                  2
                </div>
                <h3 className="font-semibold text-lg">Chat with Your Favorite LLM</h3>
              </div>
              <p className="text-gray-600 text-sm ml-10">
                Paste this prompt into ChatGPT, Claude, Gemini, or any other LLM. Have a
                conversation about yourself, your goals, and your interests. The AI will help you
                create a personalized manifest.
              </p>
            </div>

            {/* Step 3 */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <div className="w-8 h-8 rounded-full bg-[#0D9488]/10 text-[#0D9488] flex items-center justify-center font-semibold">
                  3
                </div>
                <h3 className="font-semibold text-lg">Paste Your Manifest</h3>
              </div>
              <textarea
                value={manifestText}
                onChange={(e) => setManifestText(e.target.value)}
                placeholder="Paste the manifest generated by your LLM here..."
                className="w-full ml-10 p-4 border-2 border-gray-200 rounded-xl focus:border-[#0D9488]/30 focus:outline-none transition-all min-h-[150px] resize-y"
              />
            </div>
          </div>

          {/* Footer */}
          <div className="p-6 bg-gray-50 border-t border-gray-200 flex justify-end gap-3">
            <button
              onClick={onClose}
              className="px-6 py-2 rounded-xl border-2 border-gray-300 hover:bg-gray-100 transition-all"
            >
              Cancel
            </button>
            <button
              onClick={handleSaveManifest}
              disabled={!manifestText.trim()}
              className="px-6 py-2 rounded-xl bg-gradient-to-br from-[#0D9488] to-[#14B8A6] text-white hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Save Manifest
            </button>
          </div>

          {/* Success Overlay */}
          <AnimatePresence>
            {showSuccess && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 bg-white/95 backdrop-blur-sm flex items-center justify-center"
              >
                <div className="text-center">
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="w-20 h-20 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4"
                  >
                    <Check className="w-10 h-10 text-green-600" />
                  </motion.div>
                  <h3 className="text-2xl font-bold text-gray-800">Manifest Saved!</h3>
                  <p className="text-gray-600 mt-2">
                    Your personalized experience is ready
                  </p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}