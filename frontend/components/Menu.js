export default function Menu({ items = [] }) {
  return (
    <div className="grid grid-cols-1 gap-2">
      {items.map((it) => (
        <div key={it.id} className="p-2 border rounded">
          <div className="font-medium">{it.name} — ₹{it.price}</div>
          <div className="text-sm text-gray-600">{it.description}</div>
        </div>
      ))}
    </div>
  )
}
