'use client'
import { useEffect } from 'react'

export default function ContentWrapObserver() {
  useEffect(() => {
    const sections = Array.from(
      document.querySelectorAll<HTMLElement>('.mesh-section')
    )
    if (sections.length === 0) return

    let rafId: number | null = null

    const update = () => {
      sections.forEach(section => {
        const anchor = section.querySelector<HTMLElement>('.mesh-anchor')
        if (!anchor) return
        const s = section.getBoundingClientRect()
        const a = anchor.getBoundingClientRect()
        if (s.width === 0 || s.height === 0) return

        // Center of anchor within section (percent)
        const cx = ((a.left - s.left) + a.width / 2) / s.width * 100
        const cy = ((a.top - s.top) + a.height / 2) / s.height * 100

        // Ellipse radii relative to section size
        const styles = getComputedStyle(section)
        const spreadXRaw = parseFloat(styles.getPropertyValue('--wrap-spread-x'))
        const spreadYRaw = parseFloat(styles.getPropertyValue('--wrap-spread-y'))
        const spreadX = isFinite(spreadXRaw) ? Math.min(4, Math.max(0.5, spreadXRaw)) : 1.8
        const spreadY = isFinite(spreadYRaw) ? Math.min(4, Math.max(0.5, spreadYRaw)) : 1.6

        const baseX = (a.width / s.width) * 100
        const baseY = (a.height / s.height) * 100
        const rx = Math.min(300, Math.max(40, baseX * spreadX))
        const ry = Math.min(260, Math.max(40, baseY * spreadY))

        section.style.setProperty('--wrap-x', `${cx}%`)
        section.style.setProperty('--wrap-y', `${cy}%`)
        section.style.setProperty('--wrap-rx', `${rx}%`)
        section.style.setProperty('--wrap-ry', `${ry}%`)
      })
    }

    const schedule = () => {
      if (rafId != null) return
      rafId = window.requestAnimationFrame(() => {
        rafId = null
        update()
      })
    }

    update()
    window.addEventListener('resize', schedule)
    window.addEventListener('scroll', schedule, { passive: true })
    window.addEventListener('orientationchange', schedule)
    return () => {
      if (rafId != null) window.cancelAnimationFrame(rafId)
      window.removeEventListener('resize', schedule)
      window.removeEventListener('scroll', schedule)
      window.removeEventListener('orientationchange', schedule)
    }
  }, [])

  return null
}
