import React from 'react'

const MAP = {
  pending: 'bg-[#FBF3E9] text-[#8B5E3C]',
  confirmed: 'bg-[#F3ECE8] text-[#6F472C]',
  preparing: 'bg-[#F7F5F3] text-[#8B5E3C]',
  ready: 'bg-[#F1F6F3] text-[#2E6B5A]',
  delivered: 'bg-[#EFF7EF] text-[#2F6B3F]',
  cancelled: 'bg-[#FDECEA] text-[#B85A4A]',
}

export default function StatusBadge({ status }) {
  const cls = MAP[status] || 'bg-[#F4F2F0] text-[#6B6B6B]'
  return <span className={`px-3 py-1 rounded-full text-sm font-semibold ${cls}`}>{status}</span>
}
