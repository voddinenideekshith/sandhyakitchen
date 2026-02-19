import axios from 'axios'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
	baseURL: API_BASE,
	timeout: 15000,
})

// Response interceptor: unwrap data or throw
let authToken = null

// Request interceptor: ensure Authorization header is attached from localStorage when available
api.interceptors.request.use((cfg) => {
	try {
 		const t = localStorage.getItem('admin_token')
 		if (t) cfg.headers = cfg.headers || {}, (cfg.headers['Authorization'] = `Bearer ${t}`)
 	} catch (e) {}
	return cfg
})

api.interceptors.response.use(
	(res) => res,
	(err) => {
		if (err.response && err.response.status === 401) {
			console.warn('Token expired or invalid. Logging out...')
			clearAuthToken()
			window.location.reload()
		}
		if (err.response) {
			// server responded with non-2xx
			const message = err.response.data?.detail || err.response.data || err.message
			return Promise.reject(new Error(message))
		}
		return Promise.reject(err)
	}
)

export async function fetchBrands() {
	const res = await api.get('/brands/')
	return res.data
}

// Login helper: returns token and sets it in localStorage + axios headers
export async function login(username, password) {
	const res = await api.post('/auth/login', { username, password })
	const token = res.data?.access_token
	if (token) setAuthToken(token)
	return res.data
}

export async function fetchMenu(brandId) {
	const res = await api.get(`/menu/${brandId}`)
	return res.data
}

export async function createOrder(payload) {
	const res = await api.post('/orders/', payload)
	return res.data
}

// Admin orders APIs
export async function fetchAdminOrders() {
	const res = await api.get('/admin/orders')
	return res.data
}

// Backwards/alternate names required by caller
export const getAdminOrders = fetchAdminOrders

export async function updateOrderStatus(orderId, status) {
	const res = await api.patch(`/admin/orders/${orderId}/status`, { status })
	return res.data
}

export async function fetchAdminStats() {
	// Try new endpoint first, fall back to existing orders stats endpoint
	try {
		const res = await api.get('/admin/stats')
		return res.data
	} catch (e) {
		const res = await api.get('/admin/orders/stats')
		return res.data
	}
}

export const getAdminStats = fetchAdminStats

// Auth helpers for frontend admin
export function setAuthToken(token) {
	authToken = token
	if (token) {
		api.defaults.headers.common['Authorization'] = `Bearer ${token}`
		try {
			localStorage.setItem('admin_token', token)
		} catch (e) {}
	}
}

export function clearAuthToken() {
	authToken = null
	delete api.defaults.headers.common['Authorization']
	try {
		localStorage.removeItem('admin_token')
	} catch (e) {}
}

export default api
