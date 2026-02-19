import { useCart } from '../context/CartContext'
import { useState, useEffect } from 'react'

export default function MenuItem({ item, brandSlug }) {
  const { items, addToCart, increaseQuantity, decreaseQuantity } = useCart()
  const inCart = items.find((c) => c.menu_item_id === item.id)
  const [anim, setAnim] = useState(false)

  useEffect(() => {
    if (inCart) {
      setAnim(true)
      const t = setTimeout(() => setAnim(false), 300)
      return () => clearTimeout(t)
    }
  }, [inCart?.quantity])

  const handleAdd = () => {
    if (!item.available) return
    addToCart({ menu_item_id: item.id, name: item.name, price: Number(item.price), brand_slug: brandSlug || null, quantity: 1 })
  }

  const handleInc = () => increaseQuantity(item.id, 1)
  const handleDec = () => decreaseQuantity(item.id, 1)

  return (
    <div className={`bg-white rounded-2xl p-5 shadow-md border border-[#EFE8DF] h-full flex flex-col justify-between transition-transform duration-200 ease-in-out hover:shadow-lg hover:-translate-y-1 hover:scale-105 ${!item.available ? 'opacity-60 pointer-events-none' : ''}`}>
      <div>
        <div className="flex items-start justify-between">
          <div className="text-lg font-semibold tracking-wide text-[#1F1F1F]">{item.name}</div>
          <div className="text-sm text-[#6B6B6B] font-semibold">₹{Number(item.price).toFixed(2)}</div>
        </div>

        <div className="text-sm text-[#6B6B6B] mb-3 mt-1">{item.category}</div>
        {item.description && <div className="text-sm text-[#6B6B6B] mt-2">{item.description}</div>}
      </div>

      <div className="mt-4 flex items-center justify-between">
        {!inCart ? (
          <button onClick={handleAdd} className="bg-[#8B5E3C] hover:bg-[#6F472C] text-white px-4 py-2 rounded-full shadow-sm transition-all duration-200">Add</button>
        ) : (
          <div className="flex items-center gap-2 bg-gray-50 px-2 py-1 rounded-full">
            <button onClick={handleDec} className="w-8 h-8 rounded-full bg-white border flex items-center justify-center">-</button>
            <div className={`w-8 text-center font-semibold transition-transform ${anim ? 'scale-110' : ''}`}>{inCart.quantity}</div>
            <button onClick={handleInc} className="w-8 h-8 rounded-full bg-white border flex items-center justify-center">+</button>
          </div>
        )}

        {!item.available && <div className="text-sm text-[#B85A4A] italic">Unavailable</div>}
      </div>
    </div>
  )
}
