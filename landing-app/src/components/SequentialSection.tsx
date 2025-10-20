'use client'
import { useInView } from 'framer-motion'
import { useRef, type CSSProperties } from 'react'

export default function SequentialSection({
  children,
  delay = 0,
  className = '',
  fade = false,
}: {
  children: React.ReactNode
  delay?: number
  className?: string
  fade?: boolean
}) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-100px' })

  const fadeStyle = fade
    ? ({
        WebkitMaskImage: 'linear-gradient(to bottom, black 92%, transparent 100%)',
        maskImage: 'linear-gradient(to bottom, black 92%, transparent 100%)',
      } as CSSProperties)
    : undefined

  return (
    <div ref={ref} className={`w-full min-h-screen snap-center snap-always ${className}`} style={fadeStyle}>
      {children}
    </div>
  )
}
