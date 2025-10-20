"use client"
import { useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { revealHeader, revealItem } from '@/lib/reveal'

type Member = {
  name: string
  role: string
  credentials: string
  linkedin: string
  image?: string
}

function TeamAvatar({ name, image }: { name: string; image?: string }) {
  const initials = useMemo(() => {
    const parts = name.trim().split(/\s+/)
    const [a, b] = [parts[0] ?? '', parts[1] ?? '']
    const chars = `${a.charAt(0) || ''}${b.charAt(0) || ''}`.toUpperCase()
    return chars || '##'
  }, [name])

  const candidates = useMemo(() => {
    if (image) return [image]
    const parts = name.trim().split(/\s+/)
    const first = (parts[0] || '').toLowerCase().replace(/[^a-z0-9_-]/g, '')
    const full = name.toLowerCase().replace(/\s+/g, '').replace(/[^a-z0-9_-]/g, '')
    const exts = ['jpg', 'jpeg', 'png', 'webp', 'avif']
    const list: string[] = []
    for (const base of [first, full]) {
      if (!base) continue
      for (const ext of exts) {
        // Prefer organized under public/data
        list.push(`/data/images/team/${base}.${ext}`)
        // Fallbacks for compatibility
        list.push(`/images/team/${base}.${ext}`)
        list.push(`/${base}.${ext}`)
      }
    }
    return list
  }, [name, image])

  const [idx, setIdx] = useState(0)
  const src = candidates[idx]

  if (!src) {
    return (
      <div className="w-32 h-32 bg-gray-300 dark:bg-gray-700 rounded-full mx-auto mb-6 flex items-center justify-center">
        <span className="text-3xl font-semibold">{initials}</span>
      </div>
    )
  }

  return (
    <motion.img
      {...revealItem({ delay: 0 })}
      src={src}
      alt={`${name} portrait`}
      className="w-32 h-32 rounded-full object-cover mx-auto mb-6"
      loading="eager"
      fetchPriority="high"
      decoding="sync"
      onError={() => setIdx((i) => i + 1)}
    />
  )
}

export default function Team() {
  const team: Member[] = [
    {
      name: 'Arnaud Denis-Remillard',
      role: 'CTO & Co-Founder',
      credentials: 'GDSC Lead | Adversarial ML research | 2nd Place, HEC 54h Startup Hackathon',
      linkedin: 'https://www.linkedin.com/in/arnaud-denis-remillard-25b3a8296/',
      image: '/data/images/team/arnaud.jpg',
    },
    {
      name: 'Lucas Miranda',
      role: 'CEO & Co-Founder',
      credentials: 'Jailbreak research: synthetic datasets for LLM alignment | Quant Dev (EMJ Capital) | 9x hackathon winner',
      linkedin: 'https://www.linkedin.com/in/cielofinsoen/',
    },
    {
      name: 'Henrique Jongh',
      role: 'COO',
      credentials: 'PhD (McGill, UFRGS) | Research: autonomous LLM agents & computer vision | Former CTO, PrintUp 3D (decade+)',
      linkedin: 'https://www.linkedin.com/in/henrique-jongh/',
      image: '/data/images/team/henrique.jpg',
    },
  ]

  return (
    <section className="mesh-section mesh-a mesh-animated mesh-interactive mesh-hue-soft text-white min-h-screen flex items-center justify-center">
      <div className="mesh-anchor max-w-6xl mx-auto px-6 text-center">
        <motion.h2 className="text-4xl font-bold text-center mb-16 dark:text-white" {...revealHeader()}>
          Our Team
        </motion.h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-x-12 gap-y-14 items-stretch">
          {team.map((member, index) => (
            <div key={index} className="text-center flex flex-col items-center h-full">
              <TeamAvatar name={member.name} image={member.image} />
              <h3 className="text-xl font-semibold mb-2 dark:text-white">{member.name}</h3>
              <p className="text-blue-600 dark:text-blue-400 mb-2">{member.role}</p>
              <p className="text-gray-600 dark:text-gray-300 text-sm mb-4">{member.credentials}</p>
              <a href={member.linkedin} className="self-center mt-auto text-blue-500 dark:text-blue-400 hover:underline">LinkedIn</a>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
