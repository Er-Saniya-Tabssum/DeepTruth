import React,{useEffect,useState} from 'react'
import {Link} from 'react-router-dom'
import {api} from '../lib/api'
const badge=(v:string)=>v==='AI_GENERATED'?'text-rose-300 bg-rose-500/10':v==='AUTHENTIC'?'text-emerald-300 bg-emerald-500/10':'text-amber-300 bg-amber-500/10'
export default function HistoryPage(){
 const [items,setItems]=useState<any[]>([]),[loading,setLoading]=useState(true)
 const load=()=>api.analysis.history().then(r=>setItems(r.items||[])).finally(()=>setLoading(false))
 useEffect(()=>{load()},[])
 return <div className="max-w-6xl mx-auto px-5 py-8"><div className="flex justify-between items-end"><div><div className="text-xs uppercase tracking-[.2em] text-cyan-300">Evidence log</div><h1 className="mt-2 text-4xl font-bold text-white">Analysis history</h1><p className="mt-2 text-slate-400">Every completed scan stays linked to your account.</p></div><Link to="/analyze" className="px-4 py-2.5 rounded-xl bg-indigo-500 text-white font-semibold">New scan</Link></div>
 <div className="card rounded-2xl mt-8 overflow-hidden">{loading?<div className="p-10 text-slate-500">Loading history…</div>:items.length===0?<div className="p-12 text-center text-slate-500">No analyses yet. Start your first scan.</div>:<div className="divide-y divide-white/5">{items.map(it=><Link to={`/results/${it.analysis_id}`} key={it.analysis_id} className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-5 hover:bg-white/[.03]"><div><div className="font-medium text-slate-200">{it.filename}</div><div className="text-xs text-slate-600 mt-1">{it.media_type} • {new Date(it.created_at).toLocaleString()}</div></div><div className="flex items-center gap-3"><span className={`px-2.5 py-1 rounded-full text-xs ${badge(it.verdict||'')}`}>{it.verdict||it.status}</span><span className="text-slate-600">→</span></div></Link>)}</div>}</div></div>
}
