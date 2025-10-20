"use client"
import { motion } from 'framer-motion'
import { revealProps } from '@/lib/reveal'
export default function Problem() {
  const stats = [
    { value: "85%", label: "Enterprises deploy AI" },
    { value: "10%", label: "Have adequate security" },
    { value: "$93.75B", label: "AI Security market by 2030" },
    { value: "65%", label: "Average jailbreak success rate" },
    { value: "86%", label: "Faced AI security incidents in 2024" },
  ]

  return (
    <section className="mesh-section mesh-b mesh-animated mesh-interactive mesh-hue-soft text-white min-h-screen flex items-center justify-center">
      <div className="mesh-anchor max-w-6xl mx-auto px-4 text-center">
        <h2 className="text-4xl font-bold text-center mb-16 dark:text-white">The Growing AI Security Crisis</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8">
          {stats.map((stat, index) => (
            <motion.div key={index} className="text-center max-w-[14rem] mx-auto" {...revealProps({ delay: index * 0.05 })}>
              <div className="text-3xl font-bold text-blue-600 dark:text-blue-400 mb-2">{stat.value}</div>
              <div className="text-gray-600 dark:text-gray-300">{stat.label}</div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
