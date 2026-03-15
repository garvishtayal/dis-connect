export default function Footer({ variant = 'light' }) {
  const isDark = variant === 'dark'
  return (
    <footer
      className={`w-full mt-auto flex-shrink-0 overflow-hidden ${isDark ? 'bg-zinc-950 border-t border-zinc-800/80' : 'bg-[#f7f7f7]'}`}
    >
      <iframe
        title="Dino game"
        src="/dino-game.html"
        className="block w-full h-[280px] border-0 overflow-hidden"
      />
    </footer>
  )
}
