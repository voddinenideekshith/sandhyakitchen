import { useEffect, useState } from 'react'
import Link from 'next/link'
import { fetchBrands } from '../services/api'

export default function Home() {
  const [brands, setBrands] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let mounted = true
    setLoading(true)
    fetchBrands()
      .then((data) => { if (mounted) setBrands(data) })
      .catch((err) => { if (mounted) setError(err.message || String(err)) })
      .finally(() => { if (mounted) setLoading(false) })
    return () => { mounted = false }
  }, [])

  if (loading) return <div className="p-8">Loading brands...</div>
  if (error) return <div className="p-8 text-red-600">Error loading brands: {error}</div>

  return (
    <div>
      <h1 className="text-3xl font-semibold mb-6 tracking-wide">Choose a Brand</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {brands.map((b) => (
          <Link key={b.slug} href={`/brand/${b.slug}`} className="block bg-white rounded-2xl p-6 shadow-md border border-[#EFE8DF] hover:shadow-lg hover:-translate-y-1 transform transition-all duration-200">
            <h2 className="font-semibold text-lg text-[#1F1F1F] mb-2">{b.name}</h2>
            <p className="text-sm text-[#6B6B6B]">{b.description}</p>
          </Link>
        ))}
      </div>
    </div>
  )
}
