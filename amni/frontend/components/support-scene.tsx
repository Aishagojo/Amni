import { ArrowUpRight, Check, Network, ShieldCheck, Terminal } from 'lucide-react';

export function SupportScene({ onCase, onGuide }: { onCase: () => void; onGuide: () => void }) {
  return <div className="support-scene" aria-label="Illustration of connected support cases and diagnostics">
    <div className="scene-orbit orbit-one"/><div className="scene-orbit orbit-two"/>
    <svg className="scene-wires" viewBox="0 0 600 490" fill="none" aria-hidden="true">
      <path d="M100 120H210Q235 120 235 145V205M495 120H405Q375 120 375 150V205M110 360H200Q235 360 235 330V290M505 370H420Q375 370 375 335V290" stroke="#4bb99e" strokeWidth="2" strokeDasharray="6 7"/>
      <circle cx="100" cy="120" r="5" fill="#ffe163"/><circle cx="495" cy="120" r="5" fill="#c3afff"/><circle cx="110" cy="360" r="5" fill="#c3afff"/><circle cx="505" cy="370" r="5" fill="#ffe163"/>
    </svg>
    <span className="scene-spark spark-one">✳</span><span className="scene-spark spark-two">✦</span>
    <div className="scene-label"><span/> MISSION CONTROL, MINUS THE CHAOS</div>
    <div className="support-bot" aria-hidden="true">
      <div className="bot-antenna"><i/></div>
      <div className="bot-head"><span className="bot-brow">AMNI / SUPPORT UNIT</span><div className="bot-screen"><div className="bot-eye"/><div className="bot-eye"/><span className="bot-smile"/><span className="bot-cheek cheek-left"/><span className="bot-cheek cheek-right"/></div><span className="bot-ear ear-left"/><span className="bot-ear ear-right"/></div>
      <div className="bot-base"><div className="bot-lights"><i/><i/><i/></div><span>READY TO HELP</span><ShieldCheck size={20}/></div>
      <div className="bot-base base-bottom"><div className="bot-vent"/><div className="bot-vent"/><div className="bot-vent"/><span className="bot-power"/></div>
      <div className="bot-foot foot-left"/><div className="bot-foot foot-right"/>
    </div>
    <button className="scene-ticket ticket-case" onClick={onCase}><span className="ticket-top"><span className="ticket-tag">CASE #1042</span><ArrowUpRight size={18}/></span><strong>Houston, we have<br/>a connection issue.</strong><span className="ticket-footer"><span className="ticket-dot"/> Let’s investigate <Network size={15}/></span></button>
    <div className="scene-ticket ticket-terminal"><div className="ticket-terminal-bar"><Terminal size={14}/><span>diagnostics.sh</span><span>•••</span></div><p><span>$</span> check connectivity</p><div><Check size={13}/> DNS resolved</div><div><Check size={13}/> TLS verified</div><div className="terminal-cursor">_</div></div>
    <button className="scene-ticket ticket-guide" onClick={onGuide}><span className="guide-sticker">AHA!</span><span><strong>There’s a guide for that.</strong><small>One less mystery. One useful answer.</small></span><ArrowUpRight size={19}/></button>
    <div className="scene-security"><ShieldCheck size={19}/><span>Good support starts<br/><strong>with good context.</strong></span></div>
    <span className="scene-caption">A little personality. A lot of problem-solving.</span>
  </div>;
}
