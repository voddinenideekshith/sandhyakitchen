import React from 'react'

export default function DashboardCard({ title, value, loading, accent }) {
  return (
    <div className="bg-white rounded-xl shadow-md p-5 border border-[#EFE8DF]">
      <div className="text-sm text-[#6B6B6B]">{title}</div>
      <div className="mt-3">
        <div className={`text-2xl font-semibold tracking-wide ${accent || 'text-[#1F1F1F]'}`}>{loading ? '—' : value}</div>
      </div>
    </div>
  )
}
