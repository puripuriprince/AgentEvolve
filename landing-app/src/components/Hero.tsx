"use client"
import { motion } from "framer-motion"
import { revealHeader, revealSubheader } from "@/lib/reveal"

export default function Hero() {
  return (
    <section className="mesh-section mesh-a mesh-animated mesh-interactive mesh-hue-soft text-white min-h-screen flex items-center justify-center">
      <div className="mesh-anchor text-center max-w-4xl mx-auto px-6">
        <motion.h1
          className="text-5xl sm:text-6xl font-bold mb-6 tracking-tight"
          {...revealHeader()}
          viewport={{ once: false, amount: 0.6 }}
        >
          They Said Their AI Was Secure. Then We Tested It.
        </motion.h1>
        <motion.p
          className="text-xl sm:text-2xl mb-8 text-blue-100/90"
          {...revealSubheader()}
          viewport={{ once: false, amount: 0.6 }}
        >
          See exactly where your defenses break before attackers do.
        </motion.p>

        <motion.div
          className="mt-4 flex flex-col sm:flex-row items-center justify-center gap-4"
          {...revealSubheader({ delay: 0.22 })}
          viewport={{ once: false, amount: 0.6 }}
        >
          <a
            href="#ai-labs"
            onClick={(e) => {
              e.preventDefault()
              const el = document.getElementById('ai-labs')
              if (!el) return
              const snapParent = el.closest('.snap-center') as HTMLElement | null
              ;(snapParent ?? el).scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'nearest' })
            }}
            className="inline-flex items-center justify-center rounded-md bg-white text-black px-5 py-3 font-semibold hover:bg-white/90 transition"
          >
            Break Your AI Now
          </a>
          <a
            href="#real-world-attack-demo"
            onClick={(e) => {
              e.preventDefault()
              const el = document.getElementById('real-world-attack-demo')
              if (!el) return
              const snapParent = el.closest('.snap-center') as HTMLElement | null
              ;(snapParent ?? el).scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'nearest' })
            }}
            className="inline-flex items-center justify-center rounded-md border border-white/25 text-white px-5 py-3 font-semibold hover:bg-white/10 transition"
          >
            Watch Real-World Attack Demo
          </a>
        </motion.div>
      </div>
    </section>
  )
}
