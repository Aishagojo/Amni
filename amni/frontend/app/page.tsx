'use client';

import { useEffect, useRef, useState } from 'react';
import { ArrowUpRight, ArrowRight, Check, CheckCheck, ChevronDown, Code2, FileText, Globe2, Layers3, LifeBuoy, Menu, MessageSquare, Network, Plus, Search, Send, Server, ShieldCheck, Terminal, X, Zap } from 'lucide-react';
import { Brand } from '@/components/brand';
import { SupportScene } from '@/components/support-scene';
import { guides, initialCases, type SupportCase } from '@/lib/demo';

type Modal = { type: 'create' } | { type: 'case'; id: string } | { type: 'guide'; index: number } | { type: 'architecture' } | null;
const filters = ['All cases', 'Open', 'In progress', 'Resolved'];
const categories = ['All topics', 'Networking', 'Linux & Docker', 'Security'];

export default function Home() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [cases, setCases] = useState<SupportCase[]>(initialCases);
  const [filter, setFilter] = useState('All cases');
  const [query, setQuery] = useState('');
  const [topic, setTopic] = useState('All topics');
  const [modal, setModal] = useState<Modal>(null);
  const [toast, setToast] = useState('');
  const [storageReady, setStorageReady] = useState(false);
  const [storageAvailable, setStorageAvailable] = useState(true);
  const [diagnostic, setDiagnostic] = useState(false);
  const [diagnosticRunning, setDiagnosticRunning] = useState(false);
  const dialog = useRef<HTMLDialogElement>(null);
  const lastFocus = useRef<HTMLElement | null>(null);

  useEffect(() => {
    try {
      const saved = JSON.parse(localStorage.getItem('amni-demo-cases') || 'null');
      if (Array.isArray(saved) && saved.every(item => item && typeof item.id === 'string' && typeof item.title === 'string' && typeof item.category === 'string' && typeof item.description === 'string' && typeof item.owner === 'string' && ['High', 'Medium', 'Low'].includes(item.priority) && ['Open', 'In progress', 'Resolved'].includes(item.status))) setCases(saved);
    } catch { setStorageAvailable(false); }
    setStorageReady(true);
  }, []);
  useEffect(() => {
    if (storageReady) try { localStorage.setItem('amni-demo-cases', JSON.stringify(cases)); } catch { setStorageAvailable(false); }
  }, [cases, storageReady]);
  useEffect(() => {
    if (modal) {
      if (!dialog.current?.open) {
        lastFocus.current = document.activeElement as HTMLElement;
        dialog.current?.showModal();
      }
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
      dialog.current?.close();
      lastFocus.current?.focus();
    }
  }, [modal]);
  useEffect(() => {
    if (!toast) return;
    const timeout = setTimeout(() => setToast(''), 5000);
    return () => clearTimeout(timeout);
  }, [toast]);
  useEffect(() => {
    if (!diagnosticRunning) return;
    const timeout = setTimeout(() => { setDiagnosticRunning(false); setDiagnostic(true); }, 1200);
    return () => clearTimeout(timeout);
  }, [diagnosticRunning]);
  const selected = modal?.type === 'case' ? cases.find(item => item.id === modal.id) : null;
  const visibleCases = cases.filter(item => (filter === 'All cases' || item.status === filter) && `${item.id} ${item.title} ${item.category}`.toLowerCase().includes(query.toLowerCase()));

  function createCase(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const title = String(form.get('title') || '').trim();
    const description = String(form.get('description') || '').trim();
    if (!title || !description) { setToast('Please enter a case title and description.'); return; }
    const id = `AMN-${Math.max(1042, ...cases.map(item => Number(item.id.split('-')[1]) || 0)) + 1}`;
    setCases(previous => [{ id, title, category: String(form.get('category')), priority: String(form.get('priority')), status: 'Open', owner: 'You', description }, ...previous]);
    setFilter('All cases'); setQuery(''); setModal(null);
    setToast(`${id} created in your demo workspace.`);
  }

  return <>
    <div className="announcement"><span className="announcement-badge">MEET YOUR NEW SUPPORT WORKSPACE</span> Technical support with a human side. <a href="#workspace">Take it for a spin <ArrowRight size={14}/></a></div>
    <header className="header">
      <div className="container nav-inner"><Brand/>
        <nav className={menuOpen ? 'navigation open' : 'navigation'} aria-label="Main navigation">
          <a href="#solutions" onClick={() => setMenuOpen(false)}>Platform <ChevronDown size={13}/></a>
          <a href="#workflow" onClick={() => setMenuOpen(false)}>How it works</a>
          <a href="#knowledge" onClick={() => setMenuOpen(false)}>Resources</a>
        </nav>
        <div className="nav-actions"><a className="nav-login" href="#workspace">View demo <ArrowUpRight size={14}/></a><button className="button button-dark button-small" onClick={() => setModal({ type: 'create' })}>Open a case <Plus size={15}/></button><button className="menu-button" aria-label="Toggle navigation" aria-expanded={menuOpen} onClick={() => setMenuOpen(!menuOpen)}>{menuOpen ? <X/> : <Menu/>}</button></div>
      </div>
    </header>
    <main>
      <section className="hero" id="home">
        <div className="container hero-grid">
          <div className="hero-copy">
            <div className="eyebrow"><span className="status-dot"/> FOR THE PEOPLE WHO FIX THINGS</div>
            <h1>Tech trouble?<br/>Let’s <span>sort it.</span><span className="heading-star" aria-hidden="true">✳</span></h1>
            <p className="hero-description">The case. The clues. The “aha!” moment. Bring them together in one support workspace built for people, servers, and everything in between.</p>
            <div className="hero-actions"><a className="button button-green" href="#workspace">Jump into the workspace <ArrowUpRight size={18}/></a><a className="text-link" href="#workflow"><span className="play-icon">▶</span> See how it works</a></div>
            <div className="hero-notes"><span><Check size={14}/> Built for technical teams</span><span><Check size={14}/> Made to keep you moving</span></div>
          </div>
          <SupportScene onCase={() => setModal({ type: 'case', id: 'AMN-1042' })} onGuide={() => setModal({ type: 'guide', index: 0 })}/>
        </div>
        <div className="container stack-strip"><span>UNDER THE HOOD<br/><strong>A SERIOUS STACK.</strong></span><div><Code2/> Next.js</div><div><Zap/> FastAPI</div><div><Layers3/> Docker</div><div><Server/> PostgreSQL</div><div><Globe2/> AWS-ready</div></div>
      </section>

      <section className="section solutions container" id="solutions">
        <div className="section-header"><div><div className="eyebrow">THREE GOOD REASONS TO STAY HERE.</div><h2>Less juggling. More fixing.</h2></div><p>Cases, clues, and collective know-how.<br/>All within arm’s reach.</p></div>
        <div className="solution-grid">
          <a href="#workspace" className="solution-card"><span className="feature-icon green-icon"><MessageSquare size={23}/></span><span className="feature-number">01 / THE INBOX</span><h3>Give the chaos a home.</h3><p>Keep the context, priority, and next step together. Make your queue easier to act on.</p><span className="feature-link">Explore case management <ArrowUpRight size={16}/></span></a>
          <a href="#solutions" className="solution-card"><span className="feature-icon blue-icon"><Terminal size={23}/></span><span className="feature-number">02 / THE TOOLKIT</span><h3>Follow the breadcrumbs.</h3><p>Start with Linux, DNS, TLS, and connectivity checks. Turn symptoms into a useful next step.</p><span className="feature-link">Explore diagnostics <ArrowUpRight size={16}/></span></a>
          <a href="#knowledge" className="solution-card"><span className="feature-icon orange-icon"><FileText size={23}/></span><span className="feature-number">03 / THE BRAIN</span><h3>Good answers travel.</h3><p>Find a guide before opening a case. Keep practical answers close to the people who need them.</p><span className="feature-link">Browse the knowledge base <ArrowUpRight size={16}/></span></a>
        </div>
      </section>

      <section className="workspace-section" id="workspace"><div className="container">
        <div className="section-header"><div><div className="eyebrow"><span className="status-dot"/> ROLL UP YOUR SLEEVES</div><h2>Fresh cases. Clear next steps.</h2></div><button className="button button-dark" onClick={() => setModal({ type: 'create' })}><Plus size={16}/> New case</button></div>
        <div className="workspace-panel"><div className="workspace-toolbar"><div className="case-tabs" role="group" aria-label="Filter cases by status">{filters.map(label => <button key={label} className={filter === label ? 'active' : ''} aria-pressed={filter === label} onClick={() => setFilter(label)}>{label}<span>{label === 'All cases' ? cases.length : cases.filter(c => c.status === label).length}</span></button>)}</div><label className="search"><Search size={16}/><input placeholder="Search cases…" aria-label="Search cases" value={query} onChange={e => setQuery(e.target.value)}/></label></div>
          <div className="case-table"><div className="table-head"><span>CASE / SUBJECT</span><span>PRIORITY</span><span>STATUS</span><span>ASSIGNED TO</span><span/></div>{visibleCases.length ? visibleCases.map(item => <button className="case-row" key={item.id} onClick={() => setModal({ type: 'case', id: item.id })}><span className="case-subject"><span className="case-id">{item.id}</span><strong>{item.title}</strong><small>{item.category}</small></span><span className={`priority priority-${item.priority.toLowerCase()}`}><i/>{item.priority}</span><span className={`status status-${item.status.toLowerCase().replace(' ', '-')}`}>{item.status === 'Resolved' ? <Check size={12}/> : <span/>}{item.status}</span><span className="case-owner"><span className="avatar">{item.owner.split(' ').map(n => n[0]).join('')}</span>{item.owner}</span><ArrowUpRight size={16}/></button>) : <div className="empty-state"><Search size={25}/><h3>No cases found</h3><p>Try a different search or status.</p><button className="text-link" onClick={() => { setQuery(''); setFilter('All cases'); }}>Clear filters</button></div>}</div>
          <div className="workspace-foot"><span><span className="status-dot"/> Interactive demo</span><span>{storageAvailable ? 'Changes are saved in this browser.' : 'Changes are available for this session.'} No live services connected.</span></div>
        </div>
      </div></section>

      <section className="section container workflow" id="workflow"><div className="workflow-intro"><div className="eyebrow">NO DETOURS REQUIRED</div><h2>From “uh-oh”<br/>to “we got this.”</h2><p>Keep the whole support story in one place, from the first report to the useful answer.</p><a className="text-link" href="#workspace">Give the demo a try <ArrowRight size={17}/></a></div><div className="steps">{[{n:'01',title:'Bring the context.',text:'Open a case with the issue, its priority, and the details your team needs.'},{n:'02',title:'Find the next step.',text:'Follow a diagnostic checklist and share findings where the work happens.'},{n:'03',title:'Close the loop.',text:'Resolve the case and turn what you learned into a guide for next time.'}].map(step => <div className="step" key={step.n}><span>{step.n}</span><div><h3>{step.title}</h3><p>{step.text}</p></div><ArrowDown/></div>)}</div></section>


      <section className="section container knowledge" id="knowledge"><div className="section-header"><div><div className="eyebrow">LESS “ANY IDEAS?” MORE “FOUND IT.”</div><h2>Someone’s been here before.</h2></div><span className="resource-note"><FileText size={15}/> The knowledge base</span></div><div className="topic-filters" role="group" aria-label="Knowledge base topics">{categories.map(label => <button key={label} aria-pressed={topic === label} className={topic === label ? 'active' : ''} onClick={() => setTopic(label)}>{label === 'All topics' ? <Layers3 size={14}/> : label === 'Networking' ? <Network size={14}/> : label === 'Security' ? <ShieldCheck size={14}/> : <Terminal size={14}/>} {label}</button>)}</div><div className="guide-grid">{guides.map((guide, index) => (topic === 'All topics' || topic === guide.category) && <button className="guide-card" key={guide.title} onClick={() => setModal({ type: 'guide', index })}><span className={`guide-art guide-art-${index}`} aria-hidden="true">{index === 0 ? <Network size={65} strokeWidth={1.15}/> : index === 1 ? <Terminal size={65} strokeWidth={1.15}/> : <ShieldCheck size={65} strokeWidth={1.15}/>}<span className="art-label">{index === 0 ? 'DNS / CONNECTIVITY' : index === 1 ? 'LOGS / CONTAINERS' : 'TLS / HTTPS'}</span><ArrowUpRight size={21}/></span><span className="guide-meta">{guide.category}<span>{guide.time}</span></span><h3>{guide.title}</h3><span className="guide-read">Read the guide <ArrowRight size={15}/></span></button>)}</div></section>

      <section className="container closing"><div className="closing-symbol"><ShieldCheck size={42} strokeWidth={1.6}/></div><div><div className="eyebrow">YOUR NEXT “AHA!” STARTS HERE</div><h2>Big on context. Low on chaos.</h2><p>Your cases, your context, your next step. Together.</p></div><button className="button button-green" onClick={() => setModal({ type: 'create' })}>Open your first demo case <ArrowUpRight size={17}/></button></section>
    </main>
    <footer className="container footer"><div><Brand/><p>For humans.<br/>And the systems they look after.</p></div><div className="footer-links"><a href="#solutions">Platform</a><a href="#workspace">Workspace demo</a><a href="#knowledge">Knowledge base</a></div><div className="footer-meta"><span>AMNI · Design preview</span><span><ShieldCheck size={13}/> Built with care. Designed for clarity.</span></div></footer>

    <dialog ref={dialog} className="modal" onCancel={() => setModal(null)} onClick={e => { if (e.target === e.currentTarget) setModal(null); }} aria-labelledby="modal-title"><button className="modal-close" aria-label="Close dialog" onClick={() => setModal(null)}><X size={20}/></button>
      {modal?.type === 'create' && <><div className="eyebrow">YOUR DEMO WORKSPACE</div><h2 id="modal-title">Let’s get it sorted.</h2><p className="modal-description">Add a sample case. It stays in this browser; it isn’t sent to a support team.</p><form onSubmit={createCase}><label>Case title<input name="title" placeholder="What do you need help with?" maxLength={120} required autoFocus/></label><div className="form-row"><label>Category<select name="category"><option>Networking</option><option>Linux & Docker</option><option>Security</option><option>Knowledge base</option></select></label><label>Priority<select name="priority"><option>Medium</option><option>High</option><option>Low</option></select></label></div><label>Description<textarea name="description" placeholder="What happened? What have you tried?" maxLength={3000} rows={4} required/></label><button className="button button-green" type="submit">Create demo case <Send size={16}/></button></form></>}
      {selected && <><div className="eyebrow">{selected.id} / {selected.category}</div><h2 id="modal-title">{selected.title}</h2><div className="case-detail-meta"><span className={`status status-${selected.status.toLowerCase().replace(' ', '-')}`}>{selected.status}</span><span>{selected.priority} priority</span><span>{selected.owner}</span></div><p className="case-description">{selected.description}</p><div className="case-timeline"><h3>Case activity</h3><p><MessageSquare size={16}/><span>Case recorded in the demo workspace.</span></p>{selected.status !== 'Open' && <p><Terminal size={16}/><span>Investigation started. Check logs and connectivity.</span></p>}{selected.status === 'Resolved' && <p><CheckCheck size={16}/><span>Case marked as resolved.</span></p>}</div><button className="button button-green" onClick={() => { const next = selected.status === 'Open' ? 'In progress' : selected.status === 'In progress' ? 'Resolved' : 'Open'; setCases(previous => previous.map(c => c.id === selected.id ? { ...c, status: next } : c)); setToast(`${selected.id} updated to ${next.toLowerCase()}.`); }}>{selected.status === 'Open' ? 'Start investigation' : selected.status === 'In progress' ? 'Mark as resolved' : 'Reopen case'} <ArrowRight size={16}/></button><p className="modal-footnote">Sample workflow · no WebSocket connection</p></>}
      {modal?.type === 'guide' && <><div className="eyebrow">{guides[modal.index].category} / {guides[modal.index].time}</div><h2 id="modal-title">{guides[modal.index].title}</h2><p className="guide-body">{guides[modal.index].body}</p><div className="guide-help"><LifeBuoy size={23}/><div><h3>Still need a hand?</h3><p>Bring what you found into a case.</p></div></div><button className="button button-green" onClick={() => setModal({ type: 'create' })}>Create a demo case <Plus size={16}/></button></>}
    </dialog>
    <div className={toast ? 'toast visible' : 'toast'} role="status" aria-live="polite"><Check size={17}/>{toast}</div>
  </>;
}
function ArrowDown() { return <span className="step-check"><Check size={15}/></span>; }
