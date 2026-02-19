import Head from 'next/head'
import '../styles/globals.css'
import { CartProvider } from '../context/CartContext'
import Header from '../components/Header'

export default function MyApp({ Component, pageProps }) {
  return (
    <CartProvider>
      <Head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-[#FAF7F2] to-[#F1E9DF] text-[#1F1F1F]">
        <Header />
        <main className="max-w-[1200px] mx-auto px-6 py-10">
          <Component {...pageProps} />
        </main>
      </div>
    </CartProvider>
  )
}
