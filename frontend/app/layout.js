import './globals.css';
import { Inter } from 'next/font/google';
import Navbar from '@/components/navbar';
import { Providers } from './providers';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'Todo Chatbot',
  description: 'AI-Powered Todo Management System',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-gray-50`}>
        <Providers>
          <div className="min-h-screen bg-gray-50">
            <Navbar />
            <main className="min-h-screen pt-16">
              {children}
            </main>
          </div>
        </Providers>
      </body>
    </html>
  );
}