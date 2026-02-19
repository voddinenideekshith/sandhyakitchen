import { useCart } from '../context/CartContext'
import { useState, useEffect } from 'react'
import { createOrder } from '../services/api'

export default function CartPage() {
  const { items, removeFromCart, increaseQuantity, decreaseQuantity, computeTotalPrice, clear } = useCart()
  const [loading, setLoading] = useState(false)
  const [orderId, setOrderId] = useState(null)

  const total = computeTotalPrice()

  const placeOrder = async () => {
    if (items.length === 0) return
    setLoading(true)
    try {
      if (!items[0]?.brand_slug) throw new Error('Missing brand for order')
      const payload = {
        brand_slug: items[0].brand_slug,
        items: items.map((it) => ({ menu_item_id: it.menu_item_id, quantity: it.quantity })),
        customer_name: 'Demo User',
        customer_phone: '0000000000',
        address: 'Demo address',
        payment_method: 'COD',
      }
      const res = await createOrder(payload)
      setOrderId(res.id || res._id || null)
      clear()
    } catch (e) {
      console.error(e)
      alert('Failed to place order: ' + (e.message || String(e)))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">Your Cart</h1>
      {items.length === 0 && <div className="mt-4">Cart is empty</div>}
      <div className="mt-4 space-y-3">
        {items.map((it) => (
          <div key={it.menu_item_id} className="border p-3 flex justify-between items-center">
            <div>
              <div className="font-medium">{it.name}</div>
              <div className="text-sm text-gray-600">Qty: {it.quantity}</div>
            </div>
            <div className="flex items-center space-x-2">
              <button onClick={() => decreaseQuantity(it.menu_item_id, 1)} className="px-2 py-1 border rounded">-</button>
              <div className="px-2">{it.quantity}</div>
              <button onClick={() => increaseQuantity(it.menu_item_id, 1)} className="px-2 py-1 border rounded">+</button>
              <button onClick={() => removeFromCart(it.menu_item_id)} className="text-red-500 px-2">Remove</button>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4">
        <div className="font-semibold">Total: ₹{total}</div>
        <button onClick={placeOrder} disabled={loading || items.length===0} className="mt-2 bg-green-600 text-white px-4 py-2 rounded">
          {loading ? 'Placing...' : 'Place Order'}
        </button>
      </div>

      {orderId && (
        <div className="mt-4 p-3 border rounded bg-green-50">
          Order placed successfully. Order ID: {orderId}
        </div>
      )}
    </div>
  )
}
