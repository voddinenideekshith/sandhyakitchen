import React, { useEffect, useState, useRef, useMemo } from 'react'
import { useRouter } from 'next/router'
import { setAuthToken, fetchAdminOrders, getAdminStats, updateOrderStatus, fetchBrands } from '../../services/api'
import DashboardCard from '../../components/DashboardCard'
import OrderRow from '../../components/OrderRow'
import StatusBadge from '../../components/StatusBadge'

const POLL_INTERVAL = 10000

function Spinner() {
  return <div className="animate-spin h-6 w-6 border-4 border-blue-500 border-t-transparent rounded-full" />
}

export default function AdminOrders() {
  const router = useRouter()
  const [orders, setOrders] = useState([])
  const [stats, setStats] = useState(null)
  const [brands, setBrands] = useState([])
  const [brandsMap, setBrandsMap] = useState({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [statusFilter, setStatusFilter] = useState('')
  const [brandFilter, setBrandFilter] = useState('')
  const [search, setSearch] = useState('')
  const intervalRef = useRef(null)

  useEffect(() => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('admin_token') : null
    if (!token) {
      router.push('/admin')
      return
    }
    setAuthToken(token)
    loadAll()
    intervalRef.current = setInterval(() => fetchOrders(), POLL_INTERVAL)
    return () => clearInterval(intervalRef.current)
  }, [])

  async function loadAll() {
    setLoading(true)
    setError(null)
    try {
      const [ordersData, statsData, brandsData] = await Promise.all([fetchAdminOrders(), getAdminStats(), fetchBrands()])
      ordersData.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      setOrders(ordersData)
      setStats(statsData)
      setBrands(brandsData)
      const map = {}
      brandsData.forEach((b) => (map[b.id] = b.name))
      setBrandsMap(map)
    } catch (e) {
      setError(e.message || String(e))
    } finally {
      setLoading(false)
    }
  }

  async function fetchOrders() {
    try {
      const ordersData = await fetchAdminOrders()
      ordersData.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      setOrders(ordersData)
    } catch (e) {
      setError(e.message || String(e))
    }
  }

  async function handleChangeStatus(orderId, newStatus) {
    const prev = orders.map((o) => ({ ...o }))
    setOrders((curr) => curr.map((o) => (o.id === orderId ? { ...o, status: newStatus } : o)))
    try {
      await updateOrderStatus(orderId, newStatus)
    } catch (e) {
      setError(e.message || String(e))
      setOrders(prev)
    }
  }

  const filtered = useMemo(() => {
    return orders
      .filter((o) => (statusFilter ? o.status === statusFilter : true))
      .filter((o) => (brandFilter ? String(o.brand_id) === String(brandFilter) : true))
      .filter((o) => (search ? String(o.id).includes(search) : true))
  }, [orders, statusFilter, brandFilter, search])

  const todayStr = new Date().toDateString()
  const todaysRevenue = orders.reduce((acc, o) => (new Date(o.created_at).toDateString() === todayStr ? acc + Number(o.total) : acc), 0)

  return (
    <div className="max-w-6xl mx-auto p-4">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Admin Dashboard — Orders</h1>
        <div className="flex items-center gap-3">
          <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search by order ID" className="border px-3 py-1 rounded-md" />
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="border px-3 py-1 rounded-md">
            <option value="">All statuses</option>
            <option value="pending">pending</option>
            <option value="confirmed">confirmed</option>
            <option value="preparing">preparing</option>
            <option value="ready">ready</option>
            <option value="delivered">delivered</option>
            <option value="cancelled">cancelled</option>
          </select>
          <select value={brandFilter} onChange={(e) => setBrandFilter(e.target.value)} className="border px-3 py-1 rounded-md">
            <option value="">All brands</option>
            {brands.map((b) => (
              <option key={b.id} value={b.id}>{b.name}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="Grid grid-cols-1 sm:grid-cols-4 gap-4 mb-6">
        <DashboardCard title="Total Orders" value={stats ? stats.total_orders : '—'} loading={!stats} />
        <DashboardCard title="Pending Orders" value={stats ? stats.pending_count : '—'} loading={!stats} />
        <DashboardCard title="Revenue Today" value={`₹${todaysRevenue.toFixed(2)}`} loading={!stats} />
        <DashboardCard title="Total Revenue" value={stats ? `₹${Number(stats.total_revenue).toFixed(2)}` : '—'} loading={!stats} />
      </div>

      {loading ? (
        <div className="flex justify-center py-8"><Spinner /></div>
      ) : error ? (
        <div className="text-red-600">{error}</div>
      ) : filtered.length === 0 ? (
        <div className="text-gray-600">No orders found.</div>
      ) : (
        <div className="space-y-3">
          {filtered.map((o) => (
            <OrderRow key={o.id} order={o} brandsMap={brandsMap} onChangeStatus={handleChangeStatus} />
          ))}
        </div>
      )}
    </div>
  )
}
