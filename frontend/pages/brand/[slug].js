import { useRouter } from 'next/router'
import { useEffect, useState, useMemo } from 'react'
import { fetchMenu, fetchBrands } from '../../services/api'
import MenuItem from '../../components/MenuItem'
import { useCart } from '../../context/CartContext'
import SearchBar from '../../components/SearchBar'
import CartSummary from '../../components/CartSummary'

function LoadingGrid() {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="animate-pulse bg-gray-100 h-40 rounded-lg" />
      ))}
    </div>
  )
}

export default function BrandMenu() {
  const router = useRouter()
  const { slug } = router.query
  const [menu, setMenu] = useState([])
  const [brand, setBrand] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [query, setQuery] = useState('')
  const { addToCart } = useCart()

  useEffect(() => {
    if (!slug) return
    let mounted = true
    const load = async () => {
      setLoading(true)
      setError(null)
      try {
        const brands = await fetchBrands()
        if (!mounted) return
        const toSlug = (name) => name.toLowerCase().replace(/\s+/g, '-')
        const matched = brands.find((b) => toSlug(b.name) === slug)
        if (!matched) {
          setError(`Brand not found for slug "${slug}"`)
          setBrand(null)
          setMenu([])
          return
        }
        setBrand(matched)
        const data = await fetchMenu(matched.id)
        if (!mounted) return
        setMenu(data.menu || [])
      } catch (err) {
        setError(err?.message || JSON.stringify(err))
        setBrand(null)
        setMenu([])
      } finally {
        if (mounted) setLoading(false)
      }
    }

    load()
    return () => { mounted = false }
  }, [slug])

  const filtered = useMemo(() => {
    if (!query) return menu
    const q = query.toLowerCase()
    return menu.filter((m) => m.name.toLowerCase().includes(q) || (m.category || '').toLowerCase().includes(q))
  }, [menu, query])

  const grouped = useMemo(() => {
    const map = {}
    filtered.forEach((m) => {
      const cat = m.category || 'Other'
      if (!map[cat]) map[cat] = []
      map[cat].push(m)
    })
    return map
  }, [filtered])

  return (
    <div className="max-w-5xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-3">{brand?.name || 'Menu'}</h1>

      <div className="mb-4">
        <SearchBar value={query} onChange={setQuery} />
      </div>

      {loading && <LoadingGrid />}
      {!loading && error && <div className="text-red-600">Error loading menu: {error}</div>}

      {!loading && !error && Object.keys(grouped).length === 0 && (
        <div className="py-12 text-center text-gray-600">No items found for this menu.</div>
      )}

      {!loading && !error && (
        <div className="space-y-6">
          {Object.keys(grouped).map((cat) => (
            <div key={cat}>
              <h2 className="text-xl font-semibold mb-3">{cat}</h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                {grouped[cat].map((it) => (
                  <MenuItem key={it.id} item={it} brandSlug={brand?.slug} onAdd={(payload) => addToCart(payload)} />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      <CartSummary />
    </div>
  )
}
