export default function MobileBlock({ children }) {
  return (
    <>
      <div className="md:hidden min-h-screen flex flex-col items-center justify-center text-center px-6 bg-gradient-to-br from-teal-50 via-emerald-50/30 to-white">
        <img
          src="https://media.giphy.com/media/26ufdipQqU2lhNA4g/giphy.gif"
          alt="really?"
          className="w-[220px] h-[220px] object-cover rounded-2xl shadow-[0_20px_60px_-30px_rgba(13,148,136,0.45)]"
          loading="lazy"
        />
        <h3 className="mt-6 text-xl font-semibold text-gray-900 tracking-tight">
          Not built for thumbs.
        </h3>
        <p className="mt-3 text-sm text-gray-500 max-w-xs leading-relaxed">
          dis·connect is a desktop experience.<br />
          Close this, grab a laptop, and come back like the legend you are.
        </p>
      </div>

      <div className="hidden md:block">
        {children}
      </div>
    </>
  )
}
