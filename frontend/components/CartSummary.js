import React from 'react'
import Link from 'next/link'
import { useCart } from '../context/CartContext'

export default function CartSummary() {
  const { computeTotalQuantity, computeTotalPrice } = useCart()
  const qty = computeTotalQuantity()
  const total = computeTotalPrice()

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white/80 backdrop-blur border-t border-[#EFE8DF] z-50 md:hidden">
      <div className="max-w-[1200px] mx-auto px-6 py-3 flex items-center justify-between">
        <div>
          <div className="text-sm text-[#6B6B6B]">{qty} items</div>
          <div className="text-lg font-semibold text-[#1F1F1F]">₹{Number(total).toFixed(2)}</div>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/cart" className="bg-[#8B5E3C] hover:bg-[#6F472C] text-white px-4 py-2 rounded-full transition-all duration-200">View Cart</Link>
        </div>
      </div>
    </div>
  )
}
