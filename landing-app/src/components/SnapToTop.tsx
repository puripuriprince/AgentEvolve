"use client"
import { useEffect } from "react"

export default function SnapToTop() {
  useEffect(() => {
    try {
      if ('scrollRestoration' in history) {
        // Always take control of scroll position
        history.scrollRestoration = 'manual'
      }
    } catch {}

    const snap = () => {
      const el = document.getElementById('scroll-root')
      if (el) el.scrollTo({ top: 0, left: 0, behavior: 'auto' })
      window.scrollTo({ top: 0, left: 0, behavior: 'auto' })
    }

    // On mount ensure we're at the top (Hero)
    snap()

    // Also ensure on reload/navigation
    window.addEventListener('beforeunload', snap)
    return () => window.removeEventListener('beforeunload', snap)
  }, [])
  return null
}

