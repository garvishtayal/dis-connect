import { useEffect, useState } from "react";
import Masonry from "react-responsive-masonry";
import { Navbar } from "../components/Navbar";
import {
  ContentCard,
  ContentItem,
} from "../components/ContentCard";
import { ChatWindow } from "../components/ChatWindow";
import { Loader2 } from "lucide-react";

// Mock data with real Unsplash images
const generateMockContent = (): ContentItem[] => {
const images = [
  // 1 Milan men's fashion week coat style
  "https://pplx-res.cloudinary.com/image/upload/pplx_search_images/03d1f9fc0c176dcf42a97f3535e35d1c8af06664.jpg",
  
  // 2 man coding MacBook modern office night
  "https://pplx-res.cloudinary.com/image/upload/pplx_search_images/cd195f0ed52e960fa13ae405db7e5d075d827e50.jpg",
  
  // 3 Milan street style no pants coats
  "https://pplx-res.cloudinary.com/image/upload/pplx_search_images/47cce5ce9760e90d5871d7070a52ac1685da5a90.jpg",
  
  // 4 aesthetic dual MacBook coding setup
  "https://pplx-res.cloudinary.com/image/upload/pplx_search_images/6b28bb51160eecad22bd994eb4febe44e3ed1a6a.jpg",
  
  // 5 Milan knitted beanie fringed sweater man
  "https://pplx-res.cloudinary.com/image/upload/pplx_search_images/20f8876b59ad586862fcc7a2510d5e4f87b90133.jpg",
  
  // 6 green terminal code dual monitor MacBook
  "https://pplx-res.cloudinary.com/image/upload/pplx_search_images/708aebd8b4ca2b7d91d85fc2af6f2f87f03b7762.jpg",
  
  // 7 modern coding desk MacBook notebook
  "https://pplx-res.cloudinary.com/image/upload/pplx_search_images/81db53675b6df3abe7501fbf43068fb40df35c74.jpg",
  
  // 8 khaki harness street style men fashion
  "https://pplx-res.cloudinary.com/image/upload/pplx_search_images/f5755863a42197b45f7de5661078699062665e2e.jpg",
  
  // 9 male Italian aura beach sunset prayer
  "https://pplx-res.cloudinary.com/image/upload/pplx_search_images/c1a07e7742761990cba88346dc3768ec9d59e6af.jpg",
  
  // 10 Milan gray turtleneck white pants boots
  "https://pplx-res.cloudinary.com/image/upload/pplx_search_images/03d1f9fc0c176dcf42a97f3535e35d1c8af06664.jpg",
  
  // 11 coder LG monitor MacBook mechanical keyboard
  "https://pplx-res.cloudinary.com/image/upload/pplx_search_images/6b28bb51160eecad22bd994eb4febe44e3ed1a6a.jpg",
  
  // 12 Milan wide black pants fringed sweater
  "https://pplx-res.cloudinary.com/image/upload/pplx_search_images/20f8876b59ad586862fcc7a2510d5e4f87b90133.jpg"
];


const titles = [
  // 1-12 Pinterest aesthetic male fashion Italy peace UFC coding vibes
  "Milan Coat Street Aura",
  "Night Coder MacBook Glow", 
  "No Pants Milan Rebels",
  "Dual Mac Aesthetic Desk",
  "Knitted Milan Fringe King",
  "Green Terminal Hacker",
  "Modern Code Masterpiece",
  "Khaki Harness Warriors",
  "Sunset Beach Peace Man",
  "Turtleneck Milan Elegance",
  "Mac LG Setup Legend",
  "Fringe Sweater Milan Mood"
];

  const authors = [
    "Alex Chen",
    "Maria Garcia",
    "James Wilson",
    "Sophia Lee",
    "David Park",
    "Emma Johnson",
    "Lucas Brown",
    "Olivia Davis",
    "Noah Martinez",
    "Ava Taylor",
    "Ethan Anderson",
    "Mia Thomas",
  ];

  const types: ("image" | "video" | "reel")[] = [
    "image",
    "image",
    "image",
    "video",
    "reel",
  ];

  return images.map((url, index) => ({
    id: `content-${index}`,
    type: types[index % types.length],
    url,
    title: titles[index],
    author: authors[index],
    likes: Math.floor(Math.random() * 1000) + 100,
  }));
};

export function Home() {
  const [content, setContent] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);

  useEffect(() => {
    loadMoreContent();
  }, []);

  useEffect(() => {
    const handleScroll = () => {
      if (
        window.innerHeight + window.scrollY >=
          document.documentElement.scrollHeight - 1000 &&
        !loading
      ) {
        loadMoreContent();
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () =>
      window.removeEventListener("scroll", handleScroll);
  }, [loading]);

  const loadMoreContent = () => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      const newContent = generateMockContent().map(
        (item, index) => ({
          ...item,
          id: `content-${page}-${index}`,
        }),
      );
      setContent((prev) => [...prev, ...newContent]);
      setPage((prev) => prev + 1);
      setLoading(false);
    }, 800);
  };

  return (
    <div className="min-h-screen bg-white">
      <Navbar />

      <div className="flex">
        {/* Content Feed - 70% */}
        <main className="w-[80%] pt-20 pb-12 px-8">
          {/* Masonry Grid */}
          <Masonry columnsCount={5} gutter="16px">
            {content.map((item) => (
              <ContentCard key={item.id} item={item} />
            ))}
          </Masonry>

          {/* Loading Indicator */}
          {loading && (
            <div className="flex justify-center items-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-[#0D9488]" />
            </div>
          )}
        </main>

        {/* Chat Window - 30% (Fixed to right) */}
        <ChatWindow />
      </div>
    </div>
  );
}