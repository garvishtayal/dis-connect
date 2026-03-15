import { Navbar } from "../components/Navbar";
import { ManifestModal } from "../components/ManifestModal";
import { useState } from "react";
import { Sparkles, User, Settings } from "lucide-react";

export function Profile() {
  const [isManifestOpen, setIsManifestOpen] = useState(false);

  return (
    <>
      <div className="min-h-screen bg-white">
        <Navbar />
        <main className="pt-24 pb-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto">
            {/* Profile Header */}
            <div className="flex items-center gap-6 mb-8">
              <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-[#0D9488] to-[#14B8A6] flex items-center justify-center shadow-lg">
                <User className="w-12 h-12 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-1">Your Profile</h1>
                <p className="text-gray-600">Manage your preferences and settings</p>
              </div>
            </div>

            {/* Settings Cards */}
            <div className="grid gap-4">
              {/* Manifest Card */}
              <div className="bg-white border border-gray-200 rounded-2xl p-6 hover:border-[#0D9488]/30 transition-all">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-xl bg-[#0D9488]/10 flex items-center justify-center flex-shrink-0">
                      <Sparkles className="w-6 h-6 text-[#0D9488]" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg text-gray-900 mb-1">Your Manifest</h3>
                      <p className="text-gray-600 text-sm mb-4">
                        Personalize your dis-connect experience with AI. Share your goals, interests, and preferences to get content tailored just for you.
                      </p>
                      <button
                        onClick={() => setIsManifestOpen(true)}
                        className="px-4 py-2 rounded-xl bg-gradient-to-br from-[#0D9488] to-[#14B8A6] text-white hover:shadow-lg transition-all font-medium"
                      >
                        Update Manifest
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Account Settings Card */}
              <div className="bg-white border border-gray-200 rounded-2xl p-6 hover:border-[#0D9488]/30 transition-all">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl bg-[#0D9488]/10 flex items-center justify-center flex-shrink-0">
                    <Settings className="w-6 h-6 text-[#0D9488]" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg text-gray-900 mb-1">Account Settings</h3>
                    <p className="text-gray-600 text-sm">
                      Manage your account preferences and privacy settings.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>

      <ManifestModal isOpen={isManifestOpen} onClose={() => setIsManifestOpen(false)} />
    </>
  );
}