import { Infinity, Sparkles, LogIn } from "lucide-react";
import { Link } from "react-router";

export function Navbar() {
  return (
    <nav className="fixed top-0 left-0 w-[80%] z-50 bg-white/100 backdrop-blur-xl border-b border-gray-100">
      <div className="flex items-center justify-between h-14 px-6">
        {/* Left - Logo */}
        <Link to="/" className="flex items-center group">
          <img
            src="https://i.ibb.co/99SGjPd8/Gemini-Generated-Image-150iyg150iyg150i.png"
            alt="Dis-Connect Logo"
            className="w-[120px] object-contain"
          />
        </Link>

        {/* Center - Upgrade */}
        <button className="absolute left-1/2 -translate-x-1/2 text-sm font-semibold upgrade-shine">
          Upgrade
        </button>

        {/* Right - Firebase Login */}
        <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gradient-to-br from-[#0D9488] to-[#14B8A6] text-white hover:shadow-lg transition-all">
          <LogIn className="w-3.5 h-3.5" />
          <span className="text-[10px] font-medium">
            Sign In
          </span>
        </button>
      </div>
    </nav>
  );
}