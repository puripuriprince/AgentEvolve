'use client'
import { useEffect, useMemo, useRef, useState, type SVGProps } from 'react'
import { motion } from 'framer-motion'
import { revealItem, timings } from '@/lib/reveal'

type Lab = {
  name: string
  slug: string
}

// Map display names to Simple Icons slugs (ordered)
const labs: Lab[] = [
  { name: 'OpenAI', slug: 'openai' },
  { name: 'Google', slug: 'google' },
  { name: 'Anthropic', slug: 'anthropic' },
  { name: 'Microsoft', slug: 'microsoft' },
  { name: 'Meta', slug: 'meta' },
  { name: 'Amazon', slug: 'amazon' },
  { name: 'DeepSeek', slug: 'deepseek' },
  { name: 'Perplexity', slug: 'perplexity' },
  { name: 'xAI', slug: 'x' },
]

function iconUrl(slug: string, size = 40) {
  // Enforce monochrome white icons
  // https://cdn.simpleicons.org/:icon_slug/:color
  return `https://cdn.simpleicons.org/${slug}/fff?viewbox=auto&size=${size}`
}

function lobeIconWhite(slug: string) {
  // LobeHub WEBP (dark) provides white icons for dark backgrounds
  return `https://unpkg.com/@lobehub/icons-static-webp@latest/dark/${slug}.webp`
}

function lobeIconWhiteMirror(slug: string) {
  // Mirror for LobeHub WEBP (dark) via npmmirror
  return `https://registry.npmmirror.com/@lobehub/icons-static-webp/latest/files/dark/${slug}.webp`
}

function lobeIconSvg(slug: string) {
  // Fallback to SVG variant if WEBP missing
  return `https://unpkg.com/@lobehub/icons-static-svg@latest/icons/${slug}.svg`
}

function iconSources(slug: string) {
  const sources: string[] = []
  const seen = new Set<string>()
  const add = (url: string) => {
    if (!seen.has(url)) {
      seen.add(url)
      sources.push(url)
    }
  }
  const lowerSlug = slug.trim().toLowerCase()

  // Build candidate LobeHub slugs (ordered) based on provider slug
  const lobeCandidates: Record<string, string[]> = {
    openai: ['openai'], // models: chatgpt, gpt-4, gpt-4o
    google: ['google'], // models: gemini
    anthropic: ['anthropic'], // models: claude
    microsoft: ['microsoft', 'azure', 'copilot'], // include copilot for reliability
    meta: ['meta', 'metaai'], // include metaai for reliability
    amazon: ['aws', 'amazon'],
    deepseek: ['deepseek'], // models: deepseek
    perplexity: ['perplexity'], // models: perplexity
    x: ['x', 'xai'],
    xai: ['xai', 'x'],
  }

  const candidates = new Set<string>()
  if (lobeCandidates[lowerSlug]) for (const id of lobeCandidates[lowerSlug]) candidates.add(id)
  // Always try the slug itself as a candidate as well
  candidates.add(lowerSlug)

  for (const id of candidates) {
    // Prefer LobeHub via npm mirror first, then unpkg, then SVG
    add(lobeIconWhiteMirror(id))
    add(lobeIconWhite(id))
    add(lobeIconSvg(id))
  }

  // Then fall back to Simple Icons (white)
  add(iconUrl(lowerSlug, 40))

  // Final invalid URL to force placeholder instead of alt text
  add('data:image/svg+xml;base64,PGh0bWw+PC9odG1sPg==')

  return sources
}

function LabLogo({ name, slug, delay = 0 }: Lab & { delay?: number }) {
  const [srcIndex, setSrcIndex] = useState(0)
  const [failed, setFailed] = useState(false)
  const sources = useMemo(() => iconSources(slug), [slug])
  const [resolvedSrc, setResolvedSrc] = useState<string | null>(null)
  const isLobe = resolvedSrc?.includes('@lobehub/')
  const imgClass = `h-10 w-auto opacity-80 hover:opacity-100 transition-opacity${isLobe ? ' transform scale-110' : ''}`
  
  useEffect(() => {
    // Concurrently try all sources (except invalid data URI); choose the first successful
    let done = false
    let errors = 0
    const imgs: HTMLImageElement[] = []
    setResolvedSrc(null)
    setFailed(false)
    const urls = sources.filter(u => !u.startsWith('data:'))
    if (urls.length === 0) {
      setFailed(true)
      return
    }
    urls.forEach((url) => {
      const img = new Image()
      imgs.push(img)
      img.decoding = 'async'
      try { img.fetchPriority = 'high' as any } catch {}
      img.onload = () => {
        if (!done) {
          done = true
          setResolvedSrc(url)
        }
      }
      img.onerror = () => {
        errors += 1
        if (errors >= urls.length && !done) {
          setFailed(true)
        }
      }
      img.src = url
    })
    return () => {
      // Best-effort cleanup: prevent handlers from firing
      imgs.forEach((im) => {
        im.onload = null
        im.onerror = null
      })
    }
  }, [sources])
  return (
    <div className="relative h-10 w-20 flex items-center justify-center">
      {!failed && resolvedSrc ? (
        <motion.img
          {...revealItem({ delay })}
          key={resolvedSrc}
          src={resolvedSrc}
          alt={`${name} logo`}
          title={name}
          loading="eager"
          fetchPriority="high"
          decoding="sync"
          className={imgClass}
        />
      ) : (
        <div
          className="h-10 w-10 flex items-center justify-center rounded bg-white/10 text-white/80"
          title={`${name} logo unavailable`}
          aria-label={`${name} logo unavailable`}
        >
          <BrokenImageIcon className="h-5 w-5" />
        </div>
      )}
    </div>
  )
}

function BrokenImageIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
      <path d="M3 14l4-4 4 4 4-4 6 6" />
    </svg>
  )
}

function SmallCheckIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M20 6L9 17l-5-5" />
    </svg>
  )
}

function SmallCopyIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
    </svg>
  )
}

export default function AiLabs() {
  const prompt = 'Copy this prompt to try the simulation with your provider.'
  const [copiedLab, setCopiedLab] = useState<string | null>(null)
  const resetTimerRef = useRef<number | null>(null)

  useEffect(() => () => {
    if (resetTimerRef.current) {
      window.clearTimeout(resetTimerRef.current)
      resetTimerRef.current = null
    }
  }, [])

  const uniqueLabs = useMemo(() => {
    const map = new Map<string, Lab>()
    for (const l of labs) {
      const key = l.name.trim().toLowerCase()
      if (!map.has(key)) map.set(key, l)
    }
    return Array.from(map.values())
  }, [])

  return (
    <section id="ai-labs" className="mesh-section mesh-b mesh-animated mesh-interactive mesh-hue-soft text-white min-h-screen flex items-center justify-center">
      <div className="mesh-anchor max-w-6xl mx-auto px-6">
        <h3 className="text-center text-2xl font-semibold mb-8">Think Your AI Provider Is Secure? Test It.</h3>

        {(() => {
          const total = uniqueLabs.length
          const topCount = Math.floor(total / 2)
          const top = uniqueLabs.slice(0, topCount)
          const bottom = uniqueLabs.slice(topCount)

          const renderItem = (lab: Lab, idx: number, baseDelay = 0) => (
            <div key={lab.name} className="flex flex-col items-center gap-3">
              <LabLogo name={lab.name} slug={lab.slug} delay={baseDelay + idx * timings.itemStagger} />
              {/* Keep label visually centered under logo; position icon absolutely so it doesn't shift centering */}
              <div className="relative text-sm text-white/90">
                <span className="block text-center px-5">{lab.name}</span>
                {copiedLab === lab.name ? (
                  <span className="absolute right-0 top-1/2 -translate-y-1/2 text-white h-4 w-4 flex items-center justify-center leading-none pointer-events-none">
                    <SmallCheckIcon className="h-3 w-3" />
                  </span>
                ) : (
                  <button
                    type="button"
                    aria-label={`Copy prompt for ${lab.name}`}
                    className="absolute right-0 top-1/2 -translate-y-1/2 h-4 w-4 p-0 text-white flex items-center justify-center leading-none"
                    onClick={async () => {
                      try {
                        await navigator.clipboard.writeText(prompt)
                        setCopiedLab(lab.name)
                        if (resetTimerRef.current) window.clearTimeout(resetTimerRef.current)
                        resetTimerRef.current = window.setTimeout(() => setCopiedLab(null), 2000)
                      } catch {
                        // ignore
                      }
                    }}
                  >
                    <SmallCopyIcon className="h-3 w-3" />
                  </button>
                )}
              </div>
            </div>
          )

          return (
            <div className="space-y-10">
              <div className="flex flex-row justify-center gap-10 flex-nowrap">
                {top.map((lab, i) => renderItem(lab, i, 0))}
              </div>
              {bottom.length > 0 && (
                <div className="flex flex-row justify-center gap-10 flex-nowrap">
                  {bottom.map((lab, i) => renderItem(lab, i, top.length * timings.itemStagger))}
                </div>
              )}
            </div>
          )
        })()}
      </div>
    </section>
  )
}
