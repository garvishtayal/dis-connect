import { useState } from 'react'
import { Heart, Share2, MoreHorizontal, Play, Bookmark } from 'lucide-react'

export function ContentCard({ item }) {
  const [isLiked, setIsLiked] = useState(false)
  const [isHovered, setIsHovered] = useState(false)
  const [isSaved, setIsSaved] = useState(false)

  return (
    <div className="group">
      <div
        className="relative rounded-2xl overflow-hidden bg-gray-50 cursor-pointer shadow-sm hover:shadow-xl transition-all duration-300"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        <div className="relative">
          {item.type === 'image' && (
            <img
              src={item.url}
              alt={item.title}
              className="w-full h-auto object-cover"
              loading="lazy"
            />
          )}

          {(item.type === 'video' || item.type === 'reel') && (
            <div className="relative">
              <img
                src={item.url}
                alt={item.title}
                className="w-full h-auto object-cover"
                loading="lazy"
              />
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-14 h-14 rounded-full bg-white/95 backdrop-blur-sm flex items-center justify-center shadow-lg">
                  <Play className="w-6 h-6 text-[#0D9488] ml-0.5" fill="#0D9488" />
                </div>
              </div>
              {item.type === 'reel' && (
                <div className="absolute top-3 left-3 px-3 py-1 rounded-full bg-gradient-to-r from-[#0D9488] to-[#14B8A6] text-white text-xs font-medium shadow-lg">
                  Reel
                </div>
              )}
            </div>
          )}

          <div
            className={`absolute inset-0 bg-gradient-to-t from-black/70 via-black/10 to-transparent transition-opacity duration-200 ${
              isHovered ? 'opacity-100' : 'opacity-0'
            }`}
          >
            <div className="absolute top-3 right-3 flex gap-2">
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation()
                  setIsSaved(!isSaved)
                }}
                className={`w-10 h-10 rounded-full backdrop-blur-md flex items-center justify-center transition-all ${
                  isSaved
                    ? 'bg-gradient-to-br from-[#0D9488] to-[#14B8A6] text-white'
                    : 'bg-white/95 text-gray-800 hover:bg-white'
                }`}
              >
                <Bookmark className={`w-5 h-5 ${isSaved ? 'fill-white' : ''}`} />
              </button>
              <button
                type="button"
                className="w-10 h-10 rounded-full bg-white/95 backdrop-blur-md flex items-center justify-center hover:bg-white transition-all"
              >
                <Share2 className="w-5 h-5 text-gray-800" />
              </button>
              <button
                type="button"
                className="w-10 h-10 rounded-full bg-white/95 backdrop-blur-md flex items-center justify-center hover:bg-white transition-all"
              >
                <MoreHorizontal className="w-5 h-5 text-gray-800" />
              </button>
            </div>

            <div className="absolute bottom-0 left-0 right-0 p-4">
              <div className="flex items-center justify-between mb-2">
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation()
                    setIsLiked(!isLiked)
                  }}
                  className="flex items-center gap-2 hover:scale-105 transition-transform"
                >
                  <Heart
                    className={`w-5 h-5 ${
                      isLiked ? 'fill-red-500 text-red-500' : 'text-white'
                    }`}
                  />
                  <span className="text-sm text-white font-medium">
                    {isLiked ? item.likes + 1 : item.likes}
                  </span>
                </button>
              </div>
              {(item.type === 'video' || item.type === 'reel') && (
                <>
                  <h3 className="text-white font-semibold mb-1 line-clamp-2">
                    {item.title}
                  </h3>
                  <p className="text-white/90 text-sm">{item.author}</p>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {(item.type === 'video' || item.type === 'reel') && (
        <div className="mt-3 px-1">
          <p className="text-gray-800 text-sm font-medium line-clamp-2 leading-relaxed">
            {item.title}
          </p>
        </div>
      )}
    </div>
  )
}
