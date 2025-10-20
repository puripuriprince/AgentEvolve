import Hero from '@/components/Hero'
import Problem from '@/components/Problem'
import Quote from '@/components/Quote'
import Demo from '@/components/Demo'
import RealWorldAttackDemo from '@/components/RealWorldAttackDemo'
import Team from '@/components/Team'
import AiLabs from '@/components/AiLabs'
import SequentialSection from '@/components/SequentialSection'

export default function Home() {
  return (
    <div id="scroll-root" className="h-screen overflow-y-auto snap-y snap-mandatory">
      <SequentialSection delay={0}>
        <Hero />
      </SequentialSection>
      <SequentialSection delay={0.1}>
        <Problem />
      </SequentialSection>
      {/* Move Quote directly after Problem */}
      <SequentialSection delay={0.2}>
        <Quote />
      </SequentialSection>
      <SequentialSection delay={0.35}>
        <Demo />
      </SequentialSection>
      <SequentialSection delay={0.38}>
        <RealWorldAttackDemo />
      </SequentialSection>
      <SequentialSection delay={0.4}>
        <AiLabs />
      </SequentialSection>
      <SequentialSection delay={0.41}>
        <Team />
      </SequentialSection>
    </div>
  )
}
