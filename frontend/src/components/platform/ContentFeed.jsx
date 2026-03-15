import { useEffect, useState } from 'react'
import Masonry from 'react-responsive-masonry'
import { Loader2 } from 'lucide-react'
import { ContentCard } from './ContentCard'

const MOCK_IMAGES = [
  'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/03d1f9fc0c176dcf42a97f3535e35d1c8af06664.jpg',
  'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/cd195f0ed52e960fa13ae405db7e5d075d827e50.jpg',
  'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/47cce5ce9760e90d5871d7070a52ac1685da5a90.jpg',
  'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/6b28bb51160eecad22bd994eb4febe44e3ed1a6a.jpg',
  'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/20f8876b59ad586862fcc7a2510d5e4f87b90133.jpg',
  'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/708aebd8b4ca2b7d91d85fc2af6f2f87f03b7762.jpg',
  'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/81db53675b6df3abe7501fbf43068fb40df35c74.jpg',
  'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/f5755863a42197b45f7de5661078699062665e2e.jpg',
  'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/c1a07e7742761990cba88346dc3768ec9d59e6af.jpg',
]

const MOCK_TITLES = [
  'Milan Coat Street Aura',
  'Night Coder MacBook Glow',
  'No Pants Milan Rebels',
  'Dual Mac Aesthetic Desk',
  'Knitted Milan Fringe King',
  'Green Terminal Hacker',
  'Modern Code Masterpiece',
  'Khaki Harness Warriors',
  'Sunset Beach Peace Man',
]

const MOCK_AUTHORS = [
  'Alex Chen',
  'Maria Garcia',
  'James Wilson',
  'Sophia Lee',
  'David Park',
  'Emma Johnson',
  'Lucas Brown',
  'Olivia Davis',
  'Noah Martinez',
]

const TYPES = ['image', 'image', 'image', 'video', 'reel']

function generateMockContent() {
  return MOCK_IMAGES.map((url, index) => ({
    id: `content-${index}`,
    type: TYPES[index % TYPES.length],
    url,
    title: MOCK_TITLES[index % MOCK_TITLES.length],
    author: MOCK_AUTHORS[index % MOCK_AUTHORS.length],
    likes: Math.floor(Math.random() * 1000) + 100,
  }))
}

export function ContentFeed() {
  const [content, setContent] = useState([])
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(false)

  const loadMoreContent = () => {
    if (loading) return
    setLoading(true)
    // Simulate API latency
    setTimeout(() => {
      const newContent = generateMockContent().map((item, index) => ({
        ...item,
        id: `content-${page}-${index}`,
      }))
      setContent((prev) => [...prev, ...newContent])
      setPage((prev) => prev + 1)
      setLoading(false)
    }, 600)
  }

  useEffect(() => {
    loadMoreContent()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    const handleScroll = () => {
      if (
        window.innerHeight + window.scrollY >=
          document.documentElement.scrollHeight - 1000 &&
        !loading
      ) {
        loadMoreContent()
      }
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [loading])

  return (
    <>
      <Masonry columnsCount={5} gutter="16px">
        {content.map((item) => (
          <ContentCard key={item.id} item={item} />
        ))}
      </Masonry>
      {loading && (
        <div className="flex justify-center items-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-[#0D9488]" />
        </div>
      )}
    </>
  )
}

