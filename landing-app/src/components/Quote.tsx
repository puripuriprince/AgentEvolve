"use client"
import { motion } from 'framer-motion'
import { revealHeader, revealSubheader } from '@/lib/reveal'

export default function Quote() {
  return (
    <section className="mesh-section mesh-b mesh-animated mesh-interactive mesh-hue-soft text-white min-h-screen flex items-center justify-center">
      <div className="mesh-anchor max-w-4xl mx-auto px-6 text-center">
        <motion.blockquote className="text-3xl font-light italic text-white/85 mb-8" {...revealHeader()}>
          "The gap between AI capabilities and security measures is the largest I've seen in my career."
        </motion.blockquote>
        <motion.div className="text-xl font-semibold" {...revealSubheader({ delay: 0.18 })}>Yoshua Bengio</motion.div>
        <motion.div className="text-white/60" {...revealSubheader({ delay: 0.26 })}>Turing Award Winner, AI Pioneer</motion.div>
      </div>
    </section>
  )
}
