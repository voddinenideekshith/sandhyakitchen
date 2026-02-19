import Link from 'next/link'
import { useCart } from '../context/CartContext'

export default function Header() {
  const { computeTotalQuantity } = useCart()
  const count = computeTotalQuantity()

  return (
    <header className="sticky top-0 z-50 backdrop-blur bg-white/60 border-b border-[#EFE8DF]">
      <div className="max-w-[1200px] mx-auto px-6 py-4 flex items-center justify-between">
        <Link href="/" className="text-2xl font-semibold tracking-wide text-[#1F1F1F]">Sandhya Kitchen</Link>

        <nav className="flex items-center gap-4">
          <Link href="/" className="text-sm text-[#6B6B6B] hover:text-[#1F1F1F] px-4 py-2 rounded-full transition-all duration-200">Home</Link>

          <Link href="/cart" className="relative inline-flex items-center bg-white border border-transparent hover:border-[#EFE8DF] px-4 py-2 rounded-full transition-all duration-200">
            <span className="text-sm text-[#1F1F1F]">Cart</span>
            <span className="ml-3 inline-flex items-center justify-center bg-[#8B5E3C] text-white text-xs font-semibold w-7 h-7 rounded-full">
              {count}
            </span>
          </Link>

          <Link href="/admin" className="text-sm text-[#6B6B6B] hover:text-[#1F1F1F] px-4 py-2 rounded-full transition-all duration-200">Admin</Link>
        </nav>
      </div>
    </header>
  )
}
