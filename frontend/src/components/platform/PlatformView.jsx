import { Navbar } from './Navbar'
import { ContentFeed } from './ContentFeed'
import { ChatWindow } from './ChatWindow'

/**
 * Main platform layout: navbar, content feed (left), chat window (right).
 * No API calls — uses mock data and local chat state.
 */
export function PlatformView() {
  return (
    <div className="min-h-screen bg-white">
      <Navbar />

      <div className="flex">
        <main className="w-[80%] pt-20 pb-12 px-8">
          <ContentFeed />
        </main>

        <ChatWindow />
      </div>
    </div>
  )
}
