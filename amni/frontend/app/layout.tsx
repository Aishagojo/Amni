import type { Metadata } from 'next';
import './globals.css';
import './support-scene.css';
export const metadata: Metadata = {
  title: 'AMNI — Tech trouble? Let’s sort it.',
  description: 'A clear home for support cases, infrastructure diagnostics, and team knowledge. Explore the AMNI interactive design preview.',
};
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
