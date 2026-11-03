'use client';
import { Brand } from '@/components/brand';
import { SupportScene } from '@/components/support-scene';
export default function Home() { const explore = () => document.getElementById('workspace')?.scrollIntoView(); return <main className="container section"><Brand/><h1>Tech trouble? Let's sort it.</h1><div style={{background:'#062d2b',borderRadius:20,padding:20}}><SupportScene onCase={explore} onGuide={explore}/></div><section id="workspace"><h2>Support workspace</h2><p>Case-management tools are the next milestone.</p></section></main>; }
