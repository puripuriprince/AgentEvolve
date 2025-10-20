"use client"
import { useEffect, useRef } from 'react'
import { useInView } from 'framer-motion'
import { motion } from 'framer-motion'
import { revealHeader, revealItem } from '@/lib/reveal'

export default function RealWorldAttackDemo() {
  const sectionRef = useRef<HTMLElement | null>(null)
  const inView = useInView(sectionRef, { amount: 0.4 })
  const leftRef = useRef<HTMLVideoElement | null>(null)
  const rightRef = useRef<HTMLVideoElement | null>(null)
  const delayRef = useRef<number | null>(null)

  useEffect(() => {
    const play = async () => {
      try {
        // Play right immediately (times are reset on leave)
        if (rightRef.current) {
          await rightRef.current.play()
        }

        // Delay left by 0s (immediate); adjust as needed
        if (delayRef.current != null) window.clearTimeout(delayRef.current)
        delayRef.current = window.setTimeout(() => {
          leftRef.current?.play().catch(() => {})
        }, 0.0)
      } catch {
        // Autoplay might be blocked if not muted; we ensure muted=true
      }
    }

    const pause = () => {
      if (delayRef.current != null) {
        window.clearTimeout(delayRef.current)
        delayRef.current = null
      }
      // Pause and reset to 0 so on next entry we start fresh
      if (leftRef.current) { leftRef.current.pause(); leftRef.current.currentTime = 0 }
      if (rightRef.current) { rightRef.current.pause(); rightRef.current.currentTime = 0 }
    }

    if (inView) {
      play()
    } else {
      pause()
    }
    return () => {
      if (delayRef.current != null) {
        window.clearTimeout(delayRef.current)
        delayRef.current = null
      }
    }
  }, [inView])

  return (
    <section id="real-world-attack-demo" ref={sectionRef} className="mesh-section mesh-c mesh-animated mesh-interactive mesh-hue-soft text-white min-h-screen flex items-center justify-center">
      <div className="mesh-anchor max-w-6xl mx-auto px-6">
        <motion.h2 className="text-4xl font-bold text-center mb-8 dark:text-white" {...revealHeader()}>
          Real-World Attack Demo
        </motion.h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
          <motion.div className="w-full rounded-3xl p-2 bg-white/5 border border-white/10 overflow-hidden" {...revealItem({ delay: 0 })}>
            <video
              ref={leftRef}
              className="w-full h-auto rounded-2xl bg-black crop-edge"
              src="/data/videos/attempt1.mp4"
              muted
              playsInline
              preload="auto"
              autoPlay
            />
          </motion.div>
          <motion.div className="w-full rounded-3xl p-2 bg-white/5 border border-white/10 overflow-hidden" {...revealItem({ delay: 0.05 })}>
            <video
              ref={rightRef}
              className="w-full h-auto rounded-2xl bg-black crop-edge"
              src="/data/videos/attempt2.mp4"
              muted
              playsInline
              preload="auto"
              autoPlay
            />
          </motion.div>
        </div>
      </div>
    </section>
  )
}
