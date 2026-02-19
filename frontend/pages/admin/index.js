import React, { useEffect, useState } from 'react'
import api, { fetchBrands, fetchMenu, setAuthToken, clearAuthToken } from '../../services/api'

const TOKEN_KEY = 'admin_token'

export default function Admin() {
  const [token, setToken] = useState(() => typeof window !== 'undefined' ? localStorage.getItem(TOKEN_KEY) : null)
  const [loginUser, setLoginUser] = useState('')
  const [loginPass, setLoginPass] = useState('')
  const [brands, setBrands] = useState([])
  const [selectedBrand, setSelectedBrand] = useState(null)
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState(null)
  const [error, setError] = useState(null)

  const [newItem, setNewItem] = useState({ name: '', price: '', category: '', available: true })

  useEffect(() => {
    fetchBrands()
      .then((data) => setBrands(data))
      .catch((err) => setError(err.message || String(err)))
  }, [])

  useEffect(() => {
    if (token) setAuthToken(token)
    else clearAuthToken()
  }, [token])

  useEffect(() => {
    if (selectedBrand) {
      loadMenu(selectedBrand.id)
    }
  }, [selectedBrand])

  async function loadMenu(brandId) {
    setLoading(true)
    setError(null)
    try {
      // If logged-in admin, fetch admin endpoint to include unavailable items
      let data
      if (token) {
        const res = await api.get(`/admin/menu?brand_id=${brandId}`)
        data = { menu: res.data }
      } else {
        data = await fetchMenu(brandId)
      }
      setItems(data.menu.map((it) => ({ ...it, _editing: false })))
    } catch (e) {
      setError(e.message || String(e))
    } finally {
      setLoading(false)
    }
  }

  function setItemField(idx, field, value) {
    setItems((prev) => {
      const copy = [...prev]
      copy[idx] = { ...copy[idx], [field]: value }
      return copy
    })
  }

  async function saveItem(idx) {
    const item = items[idx]
    setError(null)
    setMessage(null)
    try {
      const payload = {
        name: item.name,
        price: parseFloat(item.price),
        category: item.category,
        available: item.available,
      }
      await api.put(`/admin/menu/${item.id}`, payload)
      setMessage('Saved')
      await loadMenu(selectedBrand.id)
    } catch (e) {
      setError(e.message || String(e))
    }
  }

  async function toggleItem(idx) {
    const item = items[idx]
    setError(null)
    setMessage(null)
    try {
      await api.patch(`/admin/menu/${item.id}/toggle`)
      setMessage('Toggled')
      await loadMenu(selectedBrand.id)
    } catch (e) {
      setError(e.message || String(e))
    }
  }

  async function deleteItem(idx) {
    const item = items[idx]
    setError(null)
    setMessage(null)
    if (!confirm(`Delete ${item.name}? This is a soft-delete.`)) return
    try {
      await api.delete(`/admin/menu/${item.id}`)
      setMessage('Deleted')
      await loadMenu(selectedBrand.id)
    } catch (e) {
      setError(e.message || String(e))
    }
  }

  async function createNewItem(e) {
    e.preventDefault()
    setError(null)
    setMessage(null)
    if (!selectedBrand) {
      setError('Select a brand first')
      return
    }
    try {
      const payload = {
        brand_id: selectedBrand.id,
        name: newItem.name,
        price: parseFloat(newItem.price),
        category: newItem.category,
        available: newItem.available,
      }
      await api.post('/admin/menu/', payload)
      setMessage('Created')
      setNewItem({ name: '', price: '', category: '', available: true })
      await loadMenu(selectedBrand.id)
    } catch (e) {
      setError(e.message || String(e))
    }
  }

  async function handleLogin(e) {
    e.preventDefault()
    setError(null)
    setMessage(null)
    try {
      const res = await api.post('/auth/login', { username: loginUser, password: loginPass })
      const tok = res.data?.access_token || res.access_token || res.data
      if (!tok) throw new Error('no token in response')
      setToken(tok)
      localStorage.setItem(TOKEN_KEY, tok)
      setMessage('Logged in')
      // reload items for currently selected brand
      if (selectedBrand) await loadMenu(selectedBrand.id)
    } catch (err) {
      setError(err.message || String(err))
    }
  }

  function handleLogout() {
    setToken(null)
    localStorage.removeItem(TOKEN_KEY)
    clearAuthToken()
    setMessage('Logged out')
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>Admin Panel — Menu Management</h1>

      {!token && (
        <div style={{ marginBottom: 12 }}>
          <h3>Admin Login</h3>
          <form onSubmit={handleLogin}>
            <div>
              <label>Username: </label>
              <input value={loginUser} onChange={(e) => setLoginUser(e.target.value)} />
            </div>
            <div>
              <label>Password: </label>
              <input type="password" value={loginPass} onChange={(e) => setLoginPass(e.target.value)} />
            </div>
            <div>
              <button type="submit">Login</button>
            </div>
          </form>
        </div>
      )}
      {token && (
        <div style={{ marginBottom: 12 }}>
          <strong>Authenticated</strong>
          <button onClick={handleLogout} style={{ marginLeft: 12 }}>Logout</button>
        </div>
      )}

      <div style={{ marginBottom: 12 }}>
        <label>Brand: </label>
        <select onChange={(e) => setSelectedBrand(brands.find((b) => b.id === parseInt(e.target.value)))}>
          <option value="">-- choose brand --</option>
          {brands.map((b) => (
            <option key={b.id} value={b.id}>
              {b.name}
            </option>
          ))}
        </select>
      </div>

      {message && <div style={{ color: 'green' }}>{message}</div>}
      {error && <div style={{ color: 'red' }}>{error}</div>}

      {loading && <div>Loading...</div>}

      {!loading && selectedBrand && (
        <div>
          <h2>Menu Items for {selectedBrand.name}</h2>
          <table border="1" cellPadding="6">
            <thead>
              <tr>
                <th>Name</th>
                <th>Price</th>
                <th>Category</th>
                <th>Available</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map((it, idx) => (
                <tr key={it.id}>
                  <td>
                    <input value={it.name} onChange={(e) => setItemField(idx, 'name', e.target.value)} />
                  </td>
                  <td>
                    <input value={it.price} onChange={(e) => setItemField(idx, 'price', e.target.value)} />
                  </td>
                  <td>
                    <input value={it.category || ''} onChange={(e) => setItemField(idx, 'category', e.target.value)} />
                  </td>
                  <td>{String(it.available)}</td>
                  <td>
                    <button onClick={() => saveItem(idx)}>Save</button>
                    <button onClick={() => toggleItem(idx)} style={{ marginLeft: 6 }}>
                      Toggle
                    </button>
                    <button onClick={() => deleteItem(idx)} style={{ marginLeft: 6 }}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <h3 style={{ marginTop: 20 }}>Add new item</h3>
          <form onSubmit={createNewItem}>
            <div>
              <label>Name: </label>
              <input value={newItem.name} onChange={(e) => setNewItem((s) => ({ ...s, name: e.target.value }))} />
            </div>
            <div>
              <label>Price: </label>
              <input value={newItem.price} onChange={(e) => setNewItem((s) => ({ ...s, price: e.target.value }))} />
            </div>
            <div>
              <label>Category: </label>
              <input value={newItem.category} onChange={(e) => setNewItem((s) => ({ ...s, category: e.target.value }))} />
            </div>
            <div>
              <label>
                <input type="checkbox" checked={newItem.available} onChange={(e) => setNewItem((s) => ({ ...s, available: e.target.checked }))} />{' '}
                Available
              </label>
            </div>
            <div>
              <button type="submit">Create</button>
            </div>
          </form>
        </div>
      )}

      {!selectedBrand && <div>Select a brand to manage its items.</div>}
    </div>
  )
}
