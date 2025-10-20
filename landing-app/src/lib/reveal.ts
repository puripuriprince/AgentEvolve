import type { MotionProps } from "framer-motion"

export type RevealOptions = {
  delay?: number
  distance?: number
  once?: boolean
  amount?: number
  stiffness?: number
  damping?: number
}

export const revealProps = (opts: RevealOptions = {}): MotionProps => {
  const {
    delay = 0,
    distance = 12,
    once = false,
    amount = 0.6,
    stiffness = 220,
    damping = 22,
  } = opts
  return {
    initial: { y: distance, opacity: 0 },
    whileInView: { y: 0, opacity: 1 },
    transition: { type: "spring", stiffness, damping, delay },
    viewport: { once, amount },
  }
}

// Standardized timings across the app
export const timings = {
  headerDelay: 0.06,
  subheaderDelay: 0.14,
  itemStagger: 0.06,
}

export const revealHeader = (opts: Partial<RevealOptions> = {}): MotionProps =>
  revealProps({ delay: timings.headerDelay, distance: 12, stiffness: 220, damping: 22, once: false, amount: 0.6, ...opts })

export const revealSubheader = (opts: Partial<RevealOptions> = {}): MotionProps =>
  revealProps({ delay: timings.subheaderDelay, distance: 12, stiffness: 220, damping: 22, once: false, amount: 0.6, ...opts })

export const revealItem = (opts: Partial<RevealOptions> = {}): MotionProps =>
  revealProps({ delay: 0, distance: 10, stiffness: 180, damping: 26, once: false, amount: 0.6, ...opts })
