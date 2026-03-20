import { useState } from 'react'
import { Share2 } from 'lucide-react'
import { toast } from 'sonner'

function getYoutubeVideoId(url) {
  if (!url) return null

  // Shorts: https://www.youtube.com/shorts/{id}
  const shortsMatch = url.match(/youtube\.com\/shorts\/([^?&#/]+)/)
  if (shortsMatch?.[1]) return shortsMatch[1]

  // Watch: https://www.youtube.com/watch?v={id}
  const watchMatch = url.match(/[?&]v=([^?&#/]+)/)
  if (watchMatch?.[1]) return watchMatch[1]

  // youtu.be/{id}
  const shortLinkMatch = url.match(/youtu\.be\/([^?&#/]+)/)
  if (shortLinkMatch?.[1]) return shortLinkMatch[1]

  // Embed: https://www.youtube.com/embed/{id}
  const embedMatch = url.match(/youtube\.com\/embed\/([^?&#/]+)/)
  if (embedMatch?.[1]) return embedMatch[1]

  return null
}

function getYoutubeEmbedUrl(url) {
  const id = getYoutubeVideoId(url)
  if (!id) return null
  return `https://www.youtube.com/embed/${id}`
}

function YoutubeEmbed({ url, variant, title, active, onActivate }) {
  const embedUrl = getYoutubeEmbedUrl(url)
  if (!embedUrl) {
    return (
      <div className="w-full bg-gray-100 text-gray-600 text-sm p-6">
        Unable to embed this YouTube item.
      </div>
    )
  }

  const videoId = getYoutubeVideoId(url)
  const iframeSrc = `${embedUrl}?autoplay=1&playsinline=1`

  // Aspect ratio via padding-top (no Tailwind aspect plugin required).
  const paddingTop = variant === 'short' ? '177.78%' : '56.25%' // 9:16 vs 16:9

  return (
    <div className="relative w-full overflow-hidden" style={{ paddingTop }}>
      {active ? (
        <iframe
          className="absolute inset-0 w-full h-full"
          src={iframeSrc}
          title={title || 'YouTube'}
          loading="lazy"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
          allowFullScreen
          frameBorder="0"
          referrerPolicy="strict-origin-when-cross-origin"
        />
      ) : (
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation()
            onActivate?.()
          }}
          className="absolute inset-0 w-full h-full cursor-pointer"
          aria-label="Load YouTube video"
        >
          {videoId && (
            <img
              src={`https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`}
              onError={(e) => {
                // Fallback when maxres isn't available.
                e.currentTarget.src = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`
              }}
              alt={title || 'YouTube video'}
              className="w-full h-full object-cover"
              loading="lazy"
            />
          )}
          <div className="absolute inset-0 bg-black/10" />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-14 h-14 rounded-full bg-white/95 backdrop-blur-sm flex items-center justify-center shadow-lg">
              <span className="text-[#0D9488] text-2xl leading-none">▶</span>
            </div>
          </div>
        </button>
      )}
    </div>
  )
}

function isImageUrl(url) {
  return Boolean(
    url?.match(/\.(jpe?g|png|gif|webp|bmp|svg)(\?.*)?(#.*)?$/i)
  )
}

function getPinterestPinId(url) {
  if (!url) return null
  // Example: https://www.pinterest.com/pin/PIN_ID/
  const match = url.match(/pinterest\.com\/pin\/([^/?#]+)/i)
  return match?.[1] || null
}

function PinterestEmbed({ url, title }) {
  const pinId = getPinterestPinId(url)
  if (!pinId) {
    return (
      <div className="w-full bg-gray-100 text-gray-600 text-sm p-6">
        Unable to embed this Pinterest item.
      </div>
    )
  }

  // Pinterest embeds often vary; this keeps Masonry layout stable.
  const paddingTop = '120%' // approx vertical card

  return (
    <div className="relative w-full overflow-hidden" style={{ paddingTop }}>
      <iframe
        className="absolute inset-0 w-full h-full"
        src={`https://assets.pinterest.com/ext/embed.html?id=${pinId}`}
        title={title || 'Pinterest'}
        loading="lazy"
        frameBorder="0"
        scrolling="no"
        allow="autoplay; encrypted-media"
        referrerPolicy="strict-origin-when-cross-origin"
      />
    </div>
  )
}

export function ContentCard({ item, activeItemId, onActivate }) {
  const [isHovered, setIsHovered] = useState(false)

  const type = item?.type
  const isImage = type === 'image'
  const isShort = type === 'short' || type === 'reel'
  const isVideo = type === 'video'

  const showHoverUI = isImage
  const isActiveVideo = (isShort || isVideo) && activeItemId === item?.id

  async function copyImageUrl() {
    const url = item?.url
    if (!url) {
      toast.error('No image URL to copy.')
      return
    }

    try {
      await navigator.clipboard.writeText(url)
      toast.success('Image URL copied.', { duration: 2500 })
    } catch {
      toast.error('Copy failed. Please try again.', { duration: 2500 })
    }
  }

  return (
    <div className="group">
      <div
        className={`relative rounded-2xl overflow-hidden bg-gray-50 cursor-pointer shadow-sm ${
          showHoverUI ? 'hover:shadow-xl' : ''
        } transition-all duration-300`}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        <div className="relative">
          {isImage && (
            <>
              {isImageUrl(item?.url) ? (
                // Force a consistent portrait card height for direct image URLs.
                // Without this, wide/short images create very small cards in Masonry.
                <div
                  className="relative w-full overflow-hidden"
                  style={{ paddingTop: '120%' }}
                >
                  <img
                    src={item?.url}
                    alt={item?.title || 'Pinterest image'}
                    className="absolute inset-0 w-full h-full object-cover"
                    loading="lazy"
                  />
                </div>
              ) : (
                <PinterestEmbed url={item?.url} title={item?.title} />
              )}
            </>
          )}

          {(isShort || isVideo) && (
            <div className="relative">
              <YoutubeEmbed
                url={item?.url}
                variant={isShort ? 'short' : 'video'}
                title={item?.title}
                active={isActiveVideo}
                onActivate={() => onActivate?.(item?.id)}
              />

              {isShort && (
                <div className="absolute top-3 left-3 px-3 py-1 rounded-full bg-gradient-to-r from-[#0D9488] to-[#14B8A6] text-white text-xs font-medium shadow-lg">
                  Reel
                </div>
              )}
            </div>
          )}

          <div
            className={`absolute inset-0 bg-gradient-to-t from-black/70 via-black/10 to-transparent transition-opacity duration-200 ${
              showHoverUI && isHovered ? 'opacity-100' : 'opacity-0'
            } pointer-events-none`}
          >
            <div className="absolute top-3 right-3 flex gap-2">
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation()
                  void copyImageUrl()
                }}
                className="w-10 h-10 rounded-full bg-white/95 backdrop-blur-md flex items-center justify-center hover:bg-white transition-all pointer-events-auto"
              >
                <Share2 className="w-5 h-5 text-gray-800" />
              </button>
            </div>

            <div className="absolute bottom-0 left-0 right-0 p-4">
              <h3 className="text-white font-semibold mb-1 line-clamp-2">
                {item?.title}
              </h3>
            </div>
          </div>
        </div>
      </div>

      {(isShort || isVideo) && (
        <div className="mt-3 px-1">
          <p className="text-gray-800 text-sm font-medium line-clamp-2 leading-relaxed">
            {item?.title}
          </p>
        </div>
      )}
    </div>
  )
}
