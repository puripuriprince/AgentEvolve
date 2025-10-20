"use client"
import { useEffect } from "react"

export default function BootEffects() {
  useEffect(() => {
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (reduce) {
      document.body.style.setProperty('--gradient-opa', '1')
      return
    }
    let raf: number | null = null
    const start = performance.now()
    const duration = 1400 // ms
    const ease = (t: number) => 1 - Math.pow(1 - t, 3) // easeOutCubic
    const step = (now: number) => {
      const t = Math.min(1, (now - start) / duration)
      const v = ease(t)
      document.body.style.setProperty('--gradient-opa', v.toFixed(3))
      if (t < 1) raf = requestAnimationFrame(step)
    }
    raf = requestAnimationFrame(step)
    return () => { if (raf != null) cancelAnimationFrame(raf) }
  }, [])
  return null
}

