export function AmniMark({ className = '' }: { className?: string }) {
  return <svg className={className} viewBox="0 0 48 48" fill="none" aria-hidden="true"><path d="M5 36 18 8h11l-9 20-4 8H5Z" fill="currentColor"/><path d="m29 8 14 28H32L19 8h10Z" fill="#159a81"/><path d="m19 27 6 6 13-14" stroke="#ffde59" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round"/></svg>;
}
export function Brand({ light = false }: { light?: boolean }) {
  return <a className={`brand ${light ? 'brand-light' : ''}`} href="#home" aria-label="AMNI home"><span className="brand-mark"><AmniMark/></span>amni</a>;
}
