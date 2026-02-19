import React, { useState } from 'react'
import StatusBadge from './StatusBadge'

const STATUS_OPTIONS = ['pending', 'confirmed', 'preparing', 'ready', 'delivered', 'cancelled']

export default function OrderRow({ order, brandsMap, onChangeStatus }) {
  const [open, setOpen] = useState(false)
  const [localStatus, setLocalStatus] = useState(order.status)

  async function handleStatusChange(e) {
    const s = e.target.value
    setLocalStatus(s)
    await onChangeStatus(order.id, s)
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-[#EFE8DF] overflow-hidden">
      <div className="p-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button onClick={() => setOpen((v) => !v)} className="text-sm text-[#6B6B6B]">{open ? '▾' : '▸'}</button>
          <div>
            <div className="font-semibold text-[#1F1F1F]">Order #{order.id}</div>
            <div className="text-sm text-[#6B6B6B]">{brandsMap[order.brand_id] || `#${order.brand_id}`}</div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-sm text-[#6B6B6B]">₹{Number(order.total).toFixed(2)}</div>
          <div>
            <select value={localStatus} onChange={handleStatusChange} className="px-3 py-1 border border-[#EFE8DF] rounded-full text-sm">
              {STATUS_OPTIONS.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
          <div>
            <StatusBadge status={localStatus} />
          </div>
        </div>
      </div>

      {open && (
        <div className="p-4 border-t bg-[#FBF9F7]">
          <div className="mb-2 font-semibold">Items</div>
          <ul className="list-disc pl-5">
            {order.items.map((it) => (
              <li key={it.id} className="mb-1 text-sm text-[#6B6B6B]">
                {it.quantity} × {it.name || `Item ${it.menu_item_id}`} — ₹{Number(it.price).toFixed(2)}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
