'use client'
import { useEffect, useMemo, useRef, useState } from 'react'
import Papa from 'papaparse'
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ZAxis, ReferenceLine } from 'recharts'
import { revealHeader, revealItem } from '@/lib/reveal'
import { motion, useInView } from 'framer-motion'

interface Iteration {
  iteration: number
  prompt: string
  success: number
  confidence: number
  vulnerability_type: string
  response_time_ms: number
}

export default function Demo() {
  const [iterations, setIterations] = useState<Iteration[]>([])
  const [isDark, setIsDark] = useState(false)
  const [graphSteps, setGraphSteps] = useState(0)

  const TOTAL_DURATION_MS = 5000

  // Observe when the section is in view to trigger animation on scroll
  const sectionRef = useRef<HTMLElement | null>(null)
  const isInView = useInView(sectionRef, { amount: 0.3 })
  const graphTimerRef = useRef<number | undefined>(undefined)
  const stopGraph = () => {
    if (graphTimerRef.current !== undefined) {
      window.clearInterval(graphTimerRef.current)
      graphTimerRef.current = undefined
    }
  }

  const [dataReady, setDataReady] = useState(false)

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleSchemeChange = (event: MediaQueryListEvent) => setIsDark(event.matches)
    setIsDark(mediaQuery.matches)
    mediaQuery.addEventListener('change', handleSchemeChange)

    fetch('/data/datasets/demo_iterations.csv')
      .then(response => response.text())
      .then(csv => {
        Papa.parse<Iteration>(csv, {
          header: true,
          dynamicTyping: true,
          skipEmptyLines: true,
          complete: (results) => {
            const parsed = (results.data as Iteration[])
              .filter(row => row && typeof row.iteration === 'number' && !Number.isNaN(row.iteration))
              .map(row => ({
                ...row,
                iteration: Number(row.iteration),
                success: Number(row.success),
                confidence: Number(row.confidence),
                response_time_ms: Number(row.response_time_ms)
              }))
              .sort((a, b) => a.iteration - b.iteration)
            
            stopGraph()
            setGraphSteps(0)
            setIterations(parsed)
            setDataReady(true)

            if (parsed.length === 0) {
              return
            }

            // Animation now starts when in view; handled in another effect
          }
        })
      })

  return () => {
      // No external timeline to stop anymore
      stopGraph()
      mediaQuery.removeEventListener('change', handleSchemeChange)
    }
  }, [])

  // Start/stop animations when section is in view, replay on each entry
  useEffect(() => {
    if (!dataReady || iterations.length === 0) return

    // Reset on leave to ensure fresh animation on next entry
    if (!isInView) {
      stopGraph()
      setGraphSteps(0)
      return
    }

    // Animate on entry from the reset state
    stopGraph()
    setGraphSteps(1)

    if (iterations.length > 1) {
      const perStep = Math.max(16, Math.floor(TOTAL_DURATION_MS / iterations.length))
      graphTimerRef.current = window.setInterval(() => {
        setGraphSteps(prev => {
          if (prev >= iterations.length) {
            stopGraph()
            return prev
          }
          const next = Math.min(prev + 1, iterations.length)
          if (next >= iterations.length) stopGraph()
          return next
        })
      }, perStep)
    }

    return () => {
      stopGraph()
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isInView, dataReady, iterations.length])

  // Use actual CSV data with confidence converted to percentage
  const graphDataAll = useMemo(() => {
    return iterations.map(it => ({
      iteration: it.iteration,
      confidence: Math.round(it.confidence * 100),
      success: it.success,
      size: 20 + Math.round((it.confidence * 100) / 100 * 15)
    }))
  }, [iterations])

  const graphData = useMemo(() => {
    return graphDataAll.slice(0, graphSteps)
  }, [graphDataAll, graphSteps])

  // Gauge should mirror the graph's data (use the latest confidence value)
  const displayedSteps = graphData.length
  // Gauge reflects the latest generation's confidence (%) directly from CSV
  const asr = displayedSteps > 0 ? graphData[displayedSteps - 1].confidence : 0
  // Report total attacks analyzed = attempts per generation * generations shown
  const ATTEMPTS_PER_ITERATION = 10
  const totalAttempts = displayedSteps * ATTEMPTS_PER_ITERATION

  const baseBlue = isDark ? '#93c5fd' : '#60a5fa'
  const hexToRgba = (hex: string, alpha: number) => {
    const h = hex.replace('#', '')
    const bigint = parseInt(h, 16)
    const r = (bigint >> 16) & 255
    const g = (bigint >> 8) & 255
    const b = bigint & 255
    return `rgba(${r}, ${g}, ${b}, ${alpha})`
  }

  const CustomTooltip = ({ active, payload, isDark }: any) => {
    if (!active || !payload || payload.length === 0) return null
    const p = payload[0]?.payload as { iteration: number; confidence: number }
    if (!p) return null
    return (
      <div
        style={{
          backgroundColor: isDark ? '#1f2937' : '#fff',
          border: `1px solid ${isDark ? '#374151' : '#e5e7eb'}`,
          color: isDark ? '#fff' : '#000',
          padding: '8px 10px',
          borderRadius: 8,
        }}
      >
        <div>Generation: {p.iteration}</div>
        <div>Succesful Attacks: {Math.round(p.confidence)}%</div>
      </div>
    )
  }

  const HitDot = (props: any) => {
    const { cx, cy, size, fill } = props
    const s = typeof size === 'number' ? size : 24
    // Reduce to original perceived size (slightly smaller than sqrt mapping)
    const visibleR = Math.max(2, Math.sqrt(s) * 0.7)
    // Modest invisible hit radius for easier hover without changing visual size
    const hitR = Math.max(10, visibleR + 6)
    return (
      <g>
        <circle cx={cx} cy={cy} r={hitR} fill="transparent" pointerEvents="all" />
        <circle cx={cx} cy={cy} r={visibleR} fill={fill} style={{ transition: 'fill 180ms ease-out' }} />
      </g>
    )
  }

  return (
    <section ref={sectionRef} className="mesh-section mesh-c mesh-animated mesh-interactive mesh-hue-soft text-white min-h-screen flex items-center justify-center">
      <div className="mesh-anchor max-w-6xl mx-auto px-4 text-center">
        <motion.h2 className="text-4xl font-bold text-center mb-12 dark:text-white" {...revealHeader()}>
          Prompt Evolution
        </motion.h2>

        {/* ASR Meter and Graph Side by Side */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 mb-12">
          {/* ASR Meter */}
          <motion.div className="text-center lg:col-span-1" {...revealItem({ delay: 0 })}>
            <div className="text-2xl font-semibold mb-4 dark:text-white">Attack Success Rate</div>
            <div className="relative w-32 h-32 mx-auto">
              <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 36 36">
                <path
                  d="m18,2.0845 a 15.9155,15.9155 0 0,1 0,31.831 a 15.9155,15.9155 0 0,1 0,-31.831"
                  fill="none"
                  stroke={isDark ? "#374151" : "#eee"}
                  strokeWidth="2"
                />
                <motion.path
                  d="m18,2.0845 a 15.9155,15.9155 0 0,1 0,31.831 a 15.9155,15.9155 0 0,1 0,-31.831"
                  fill="none"
                  stroke="#3b82f6"
                  strokeWidth="2"
                  strokeDasharray="100"
                  initial={{ strokeDashoffset: 100 }}
                  animate={{ strokeDashoffset: 100 - asr }}
                  transition={{ duration: 0.5 }}
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-2xl font-bold dark:text-white">{Math.round(asr)}%</span>
              </div>
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400 mt-2">
              {totalAttempts} attacks attempted
            </div>
          </motion.div>

          {/* Animated Graph */}
          <motion.div className="lg:col-span-3" {...revealItem({ delay: 0.05 })}>
            <div className="text-xl font-semibold mb-4 text-center dark:text-white">Confidence Progression</div>
            <ResponsiveContainer width="100%" height={240}>
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 80 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={isDark ? "#374151" : "#e5e7eb"} />
                <XAxis
                  type="number"
                  dataKey="iteration"
                  stroke={isDark ? "#9ca3af" : "#6b7280"}
                  domain={[1, iterations.length || 16]}
                  label={{ value: 'Generation', position: 'insideBottom', offset: -10, fill: isDark ? "#9ca3af" : "#6b7280" }}
                />
                <YAxis
                  type="number"
                  dataKey="confidence"
                  stroke={isDark ? "#9ca3af" : "#6b7280"}
                  domain={[0, 100]}
                  label={{ 
                    value: 'Confidence %', 
                    angle: -90, 
                    position: 'insideLeft',
                    offset: -5,
                    style: { textAnchor: 'middle' },
                    fill: isDark ? "#9ca3af" : "#6b7280" 
                  }}
                />
                <ZAxis type="number" dataKey="size" range={[12, 36]} />
                <ReferenceLine y={50} stroke={isDark ? "#4b5563" : "#d1d5db"} strokeDasharray="4 4" />
                <Tooltip
                  cursor={{ strokeDasharray: '4 4' }}
                  content={<CustomTooltip isDark={isDark} />}
                  wrapperStyle={{ transition: 'none' }}
                />
                <Scatter
                  data={graphData}
                  isAnimationActive={false}
                  line
                  stroke={baseBlue}
                  shape={HitDot}
                >
                  {graphData.map((point, index) => {
                    const t = graphData.length > 0 ? index / graphData.length : 0
                    const alpha = 0.25 + 0.65 * t
                    const color = baseBlue
                    return (
                      <Cell key={`point-${point.iteration}-${index}`} fill={hexToRgba(color, alpha)} />
                    )
                  })}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
          </motion.div>
        </div>

        {/* Removed iteration list to keep only graphs */}
      </div>
    </section>
  )
}
