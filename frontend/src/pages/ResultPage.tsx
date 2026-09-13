import React,{useEffect,useState} from 'react'
import {useNavigate,useParams} from 'react-router-dom'
import {api} from '../lib/api'

function verdictStyle(v?:string|null){
 return v==='AI_GENERATED'?'bg-rose-500/10 border-rose-500/20 text-rose-200':v==='AUTHENTIC'?'bg-emerald-500/10 border-emerald-500/20 text-emerald-200':'bg-amber-500/10 border-amber-500/20 text-amber-200'
}
function pct(value?:number|null){return `${Math.round((value??0)*100)}%`}
function severityClass(s?:string){return s==='HIGH'?'text-rose-300 bg-rose-500/10 border-rose-500/20':s==='MEDIUM'?'text-amber-300 bg-amber-500/10 border-amber-500/20':'text-cyan-300 bg-cyan-500/10 border-cyan-500/20'}

export default function ResultPage(){
 const {analysisId}=useParams(); const nav=useNavigate();
 const [data,setData]=useState<any>(null),[loading,setLoading]=useState(true),[reporting,setReporting]=useState(false),[error,setError]=useState('')
 useEffect(()=>{
  if(!analysisId)return
  api.analysis.get(analysisId).then(setData).catch(e=>setError(e.message)).finally(()=>setLoading(false))
 },[analysisId])
 const download=async()=>{
  if(!analysisId)return; setReporting(true)
  try{const blob=await api.downloadReport(analysisId);const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=`deeptruth-report-${analysisId}.pdf`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
  catch(e){setError(e instanceof Error?e.message:'Could not generate report.')} finally{setReporting(false)}
 }
 if(loading)return <div className="max-w-6xl mx-auto p-8 text-slate-500">Loading forensic result…</div>
 if(error||!data)return <div className="max-w-6xl mx-auto p-8 text-rose-300">{error||'Result not found.'}</div>
 const r=data.result||{}
 const ai=Math.round((r.ai_probability??0)*100), auth=Math.round((r.authenticity_score??0)*100)
 const evidence=r.evidence||[]
 const metadata=r.media_metadata||{}
 const model=r.model_metadata||{}
 return <div className="max-w-7xl mx-auto px-5 py-8 pb-16">
  <button onClick={()=>nav('/history')} className="text-sm text-slate-500 hover:text-white">← Back to history</button>
  <div className="flex flex-col md:flex-row md:items-end justify-between gap-5 mt-5">
   <div><div className="text-xs uppercase tracking-[.2em] text-cyan-300">Forensic assessment</div><h1 className="mt-2 text-4xl font-bold text-white break-all">{data.filename}</h1><p className="mt-2 text-slate-500">{new Date(data.created_at).toLocaleString()} • {data.media_type} • {data.status}</p></div>
   <button onClick={download} className="px-4 py-2.5 rounded-xl bg-white text-slate-950 font-semibold">{reporting?'Generating…':'Download PDF report'}</button>
  </div>

  <div className={`mt-8 rounded-2xl border p-7 ${verdictStyle(r.verdict)}`}>
   <div className="text-xs uppercase tracking-[.18em] opacity-70">Overall assessment</div>
   <div className="mt-2 text-3xl md:text-4xl font-black">{(r.verdict||'INCONCLUSIVE').split('_').join(' ')}</div>
   <div className="mt-2 text-sm opacity-70">Confidence: {r.confidence||'N/A'} • {model.model_name||'configured detector'} • {model.device||'CPU'}</div>
   <div className="mt-6 max-w-2xl text-sm leading-6 opacity-80">DeepTruth reports probabilistic model signals. A high score is not proof of synthetic media, and a low score is not proof of authenticity. Review the evidence below before making consequential decisions.</div>
  </div>

  <div className="grid md:grid-cols-3 gap-4 mt-5">
   {[['AI probability',pct(r.ai_probability),ai>=75?'rose':ai>=55?'amber':'cyan'],['Authenticity score',pct(r.authenticity_score),auth>=75?'emerald':auth>=55?'amber':'cyan'],['Faces detected',r.faces_detected??'—','cyan']].map(([label,value,tone])=><div className="card rounded-2xl p-5" key={label as string}><div className="text-sm text-slate-500">{label}</div><div className="mt-2 text-3xl font-bold text-white">{value}</div><div className="mt-4 h-2 rounded-full bg-white/5 overflow-hidden"><div className="h-full bg-cyan-400 rounded-full" style={{width:`${label==='AI probability'?Math.max(3,ai):label==='Authenticity score'?Math.max(3,auth):Math.min(100,(r.faces_detected||0)*20)}%`}}/></div></div>)}
  </div>

  <div className="grid lg:grid-cols-[1.2fr_.8fr] gap-5 mt-5">
   <div className="card rounded-2xl p-6"><div className="flex items-center justify-between"><div><h2 className="font-semibold text-white">Forensic evidence</h2><p className="text-sm text-slate-500 mt-1">Signals used to form the assessment</p></div><span className="text-xs text-slate-600">{evidence.length} signals</span></div>
    <div className="mt-5 space-y-3">{evidence.map((e:any,i:number)=><div key={`${e.type}-${i}`} className="rounded-xl border border-white/8 bg-white/[.025] p-4"><div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2"><div className="font-medium text-slate-200">{e.title}</div><span className={`self-start text-[11px] uppercase tracking-wider border rounded-full px-2 py-1 ${severityClass(e.severity)}`}>{e.severity}</span></div><div className="mt-2 text-lg font-semibold text-white">{e.value}</div><p className="mt-1 text-sm leading-5 text-slate-500">{e.explanation}</p></div>)}{!evidence.length&&<div className="text-sm text-slate-600">No structured evidence was returned by the model pipeline.</div>}</div>
   </div>
   <div className="card rounded-2xl p-6"><h2 className="font-semibold text-white">Media fingerprint</h2><div className="mt-4 space-y-3 text-sm">
    {[['Dimensions',metadata.width&&metadata.height?`${metadata.width} × ${metadata.height}`:'Not available'],['Format',metadata.format||'Not available'],['EXIF',metadata.exif_present?'Present':'Not present'],['SHA-256',metadata.sha256?`${metadata.sha256.slice(0,16)}…`:'Not available']].map(([k,v])=><div key={k} className="flex justify-between gap-4 border-b border-white/5 pb-3"><span className="text-slate-500">{k}</span><span className="text-slate-200 text-right break-all">{v}</span></div>)}
   </div></div>
  </div>

  <div className="grid lg:grid-cols-2 gap-5 mt-5">
   <div className="card rounded-2xl p-6"><h2 className="font-semibold text-white">Model output</h2><div className="mt-5 space-y-3">{(r.raw_predictions||[]).map((p:any)=><div key={p.label}><div className="flex justify-between text-sm mb-1"><span className="text-slate-300">{p.label}</span><span className="text-cyan-300">{Math.round(p.score*100)}%</span></div><div className="h-2 rounded-full bg-white/5 overflow-hidden"><div className="h-full bg-cyan-400 rounded-full" style={{width:`${Math.round(p.score*100)}%`}}/></div></div>)}{r.frame_results?.length>0&&<div className="text-sm text-slate-500 pt-2">Video frames sampled: {r.frame_results.length}</div>}</div><div className="mt-6 text-xs text-slate-600">{model.framework||'Hugging Face Transformers'} • revision {model.version||'default'} • {model.processing_time??'—'}s</div></div>
   <div className="card rounded-2xl p-6"><h2 className="font-semibold text-white">Limitations & review guidance</h2><ul className="mt-4 space-y-3 text-sm text-slate-400">{(r.limitations||[]).map((x:string)=><li key={x} className="flex gap-2"><span className="text-cyan-300">•</span>{x}</li>)}</ul></div>
  </div>

  <div className="card rounded-2xl p-6 mt-5"><h2 className="font-semibold text-white">Detected faces</h2>{r.detected_faces?.length?<div className="mt-4 grid sm:grid-cols-2 gap-3">{r.detected_faces.map((f:any)=><div key={f.face_id} className="rounded-xl bg-white/[.03] p-4 text-sm text-slate-400">Face {f.face_id?.split('-')[1]||'1'} • bbox {f.bbox?.x},{f.bbox?.y},{f.bbox?.width}×{f.bbox?.height}<div className="mt-2 text-xs text-slate-600">{f.notes}</div></div>)}</div>:<p className="mt-3 text-sm text-slate-600">No faces were detected.</p>}</div>
 </div>
}
