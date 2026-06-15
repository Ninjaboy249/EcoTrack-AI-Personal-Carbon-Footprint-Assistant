import React, { useEffect, useMemo, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, BarChart, Bar, Legend } from 'recharts'

type Entry = {
  transport: number
  electricity: number
  food: number
  shopping: number
  totalCO2: number
  createdAt?: string
  _id?: string
}

export default function App() {
  const [entries, setEntries] = useState<Entry[]>([])
  const [form, setForm] = useState({ transport: 0, electricity: 0, food: 0, shopping: 0 })
  const [loading, setLoading] = useState(false)

  const apiBase = (() => {
    if (typeof window !== 'undefined' && window.location.hostname === 'localhost' && window.location.port === '5173') return 'http://localhost:4000'
    return ''
  })()

  const load = async () => {
    try {
      const r = await fetch(`${apiBase}/api/entries`)
      const data = await r.json()
      setEntries(data.entries || [])
    } catch (e) {
      setEntries([])
    }
  }

  useEffect(() => {
    load()
  }, [])

  const submit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    setLoading(true)
    try {
      await fetch(`${apiBase}/api/calculate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      await load()
    } finally {
      setLoading(false)
    }
  }

  const chartData = useMemo(() => {
    return entries
      .slice()
      .reverse()
      .map((en) => ({
        date: en.createdAt ? new Date(en.createdAt).toLocaleDateString() : '',
        total: Number(en.totalCO2 || 0),
        transport: en.transport || 0,
        electricity: en.electricity || 0,
        food: en.food || 0,
        shopping: en.shopping || 0,
      }))
  }, [entries])

  const latest = entries[0]

  return (
    <div className="app-shell">
      <h1 className="text-2xl font-semibold mb-4">EcoTrack AI</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card md:col-span-1">
          <h2 className="text-lg font-medium mb-2">Add entry</h2>
          <form onSubmit={submit} className="space-y-2">
            <div className="form-row">
            <div>
              <label className="small">Transport (km): <span className="font-semibold">{form.transport}</span></label>
              <input className="w-full mt-1" type="range" min="0" max="500" step="1" value={form.transport} onChange={(e) => setForm({ ...form, transport: Number(e.target.value) })} />
            </div>
            <div>
              <label className="small">Electricity (kWh): <span className="font-semibold">{form.electricity}</span></label>
              <input className="w-full mt-1" type="range" min="0" max="200" step="0.1" value={form.electricity} onChange={(e) => setForm({ ...form, electricity: Number(e.target.value) })} />
            </div>
          </div>
          <div className="form-row">
            <div>
              <label className="small">Food (units): <span className="font-semibold">{form.food}</span></label>
              <input className="w-full mt-1" type="range" min="0" max="10" step="0.1" value={form.food} onChange={(e) => setForm({ ...form, food: Number(e.target.value) })} />
            </div>
            <div>
              <label className="small">Shopping (units): <span className="font-semibold">{form.shopping}</span></label>
              <input className="w-full mt-1" type="range" min="0" max="20" step="0.1" value={form.shopping} onChange={(e) => setForm({ ...form, shopping: Number(e.target.value) })} />
            </div>
            </div>
          <div className="flex items-center gap-2">
            <button className="bg-green-600 text-white px-4 py-2 rounded" disabled={loading} type="submit">{loading ? 'Saving...' : 'Calculate & Save'}</button>
            <button type="button" className="px-3 py-2 border rounded" onClick={load}>Refresh</button>
            <button type="button" className="px-3 py-2 border rounded" onClick={async () => { setLoading(true); try { await fetch(`${apiBase}/api/calculate`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ transport: 10, electricity: 5, food: 2, shopping: 1 }) }); await load(); } finally { setLoading(false); } }}>Seed sample</button>
          </div>
        </form>

        {latest ? (
          <div className="mt-4 small">
            <div className="font-medium">Latest: {new Date(latest.createdAt || '').toLocaleString()}</div>
            <div>Total: <strong>{latest.totalCO2.toFixed(2)} kg CO₂</strong></div>
            <div className="text-sm text-gray-500">T:{latest.transport} E:{latest.electricity} F:{latest.food} S:{latest.shopping}</div>
          </div>
        ) : (
          <div className="mt-4 small">No entries yet.</div>
        )}
        </div>

        <div className="card md:col-span-2">
          <h2 className="text-lg font-medium mb-2">Trends</h2>
          <div style={{ width: '100%', height: 240 }}>
            {chartData.length === 0 ? (
              <div className="flex items-center justify-center h-full text-gray-500">No data yet. Use the form or click "Seed sample" to add an entry.</div>
            ) : (
              <ResponsiveContainer>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="total" stroke="#10b981" dot={false} name="Total CO₂" />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>

          <h3 className="mt-4">Category breakdown (latest)</h3>
          <div style={{ width: '100%', height: 160 }}>
            {latest ? (
              <ResponsiveContainer>
                <BarChart data={[{ name: 'Latest', Transport: latest.transport, Electricity: latest.electricity, Food: latest.food, Shopping: latest.shopping }]}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="Transport" stackId="a" fill="#2563eb" />
                  <Bar dataKey="Electricity" stackId="a" fill="#f59e0b" />
                  <Bar dataKey="Food" stackId="a" fill="#ef4444" />
                  <Bar dataKey="Shopping" stackId="a" fill="#7c3aed" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">No data to display</div>
            )}
          </div>
        </div>
      </div>

      <div className="card mt-4">
        <h2 className="text-lg font-medium mb-2">Recent entries</h2>
        <ul className="space-y-2">
          {entries.map((en) => (
            <li key={en._id} className="p-2 border rounded flex justify-between items-center">
              <div>
                <div className="font-medium">{new Date(en.createdAt || '').toLocaleString()}</div>
                <div className="small">T:{en.transport} E:{en.electricity} F:{en.food} S:{en.shopping}</div>
              </div>
              <div className="text-right">
                <div className="font-semibold">{en.totalCO2.toFixed(2)} kg CO₂</div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
