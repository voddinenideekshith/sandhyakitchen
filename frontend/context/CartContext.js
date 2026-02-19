import { createContext, useContext, useEffect, useState } from 'react'

const CartContext = createContext()

export function useCart() {
  return useContext(CartContext)
}

export function CartProvider({ children }) {
  const [items, setItems] = useState(() => {
    try {
      const raw = localStorage.getItem('cart')
      return raw ? JSON.parse(raw) : []
    } catch (e) {
      return []
    }
  })

  useEffect(() => {
    try {
      localStorage.setItem('cart', JSON.stringify(items))
    } catch (e) {}
  }, [items])

  const addToCart = (item) => {
    // item must include: menu_item_id, name, price, brand_slug, quantity
    setItems((prev) => {
      const idx = prev.findIndex((p) => p.menu_item_id === item.menu_item_id)
      if (idx >= 0) {
        const copy = prev.map((p, i) => (i === idx ? { ...p, quantity: p.quantity + (item.quantity || 1) } : p))
        return copy
      }
      return [...prev, { menu_item_id: item.menu_item_id, name: item.name, price: item.price, brand_slug: item.brand_slug, quantity: item.quantity || 1 }]
    })
  }

  const increaseQuantity = (menu_item_id, delta = 1) => {
    setItems((prev) => prev.map((p) => (p.menu_item_id === menu_item_id ? { ...p, quantity: p.quantity + delta } : p)))
  }

  const decreaseQuantity = (menu_item_id, delta = 1) => {
    setItems((prev) => {
      const copy = prev.map((p) => (p.menu_item_id === menu_item_id ? { ...p, quantity: p.quantity - delta } : p))
      return copy.filter((p) => p.quantity > 0)
    })
  }

  const removeFromCart = (menu_item_id) => {
    setItems((prev) => prev.filter((p) => p.menu_item_id !== menu_item_id))
  }

  const computeTotalQuantity = () => items.reduce((s, it) => s + (it.quantity || 0), 0)

  const computeTotalPrice = () => items.reduce((s, it) => s + (it.price || 0) * (it.quantity || 0), 0)

  const clear = () => setItems([])

  return (
    <CartContext.Provider value={{ items, addToCart, increaseQuantity, decreaseQuantity, removeFromCart, computeTotalQuantity, computeTotalPrice, clear }}>
      {children}
    </CartContext.Provider>
  )
}
