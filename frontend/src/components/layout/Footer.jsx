export default function Footer({ variant = 'light' }) {
  const isDark = variant === 'dark'
  return (
    <footer
      className={`w-full mt-auto flex-shrink-0 overflow-hidden ${isDark ? 'bg-zinc-950 border-t border-zinc-800/80' : 'bg-[#f7f7f7]'}`}
    >
      <div className="relative">
        <iframe
          title="Dino game"
          src="/dino-game.html"
          className="block w-full h-[280px] border-0 overflow-hidden"
        />
        <p className={`absolute bottom-3 left-1/2 -translate-x-1/2 text-[10px] font-light tracking-[0.22em] uppercase select-none pointer-events-none ${isDark ? 'text-zinc-400' : 'text-gray-400'}`}>
          press space to jump
        </p>
      </div>
    </footer>
  )
}
