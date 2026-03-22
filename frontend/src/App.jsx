import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'sonner'
import Login from './pages/Login'
import Initial from './pages/Initial'
import Platform from './pages/Platform'
import MobileBlock from './components/layout/MobileBlock'

export default function App() {
  return (
    <MobileBlock>
    <BrowserRouter>
      <Toaster
        position="top-center"
        toastOptions={{
          style: { fontFamily: 'Space Grotesk, system-ui, sans-serif', fontSize: '0.875rem' },
          classNames: { error: 'border-red-100' },
        }}
        richColors
      />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/initial" element={<Initial />} />
        <Route path="/platform" element={<Platform />} />
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
    </MobileBlock>
  )
}
