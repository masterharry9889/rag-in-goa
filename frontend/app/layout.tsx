import { Inter } from 'next/font/google';
import FloatingDock from '@/components/FloatingDock';
import './globals.css';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });

export const metadata = {
  title: 'Voice.AI | Next Generation RAG',
  description: 'Lightning fast voice-enabled retrieval-augmented generation',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-[#0f1115] text-white antialiased selection:bg-brand-main/30`}>
        {children}
        <FloatingDock />
      </body>
    </html>
  )
}
