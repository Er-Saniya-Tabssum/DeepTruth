import React, {useEffect, useRef, useState} from 'react'
import {api} from '../lib/api'

type Mode = 'text' | 'object'

export default function RemovePage(){
  const [file,setFile]=useState<File|null>(null)
  const [mode,setMode]=useState<Mode>('text')
  const [busy,setBusy]=useState(false)
  const [error,setError]=useState('')
  const [result,setResult]=useState<{job_id:string;model:string;region_count?:number;cleaned_url:string}|null>(null)
  const [cleanedPreview,setCleanedPreview]=useState('')
  const [preview,setPreview]=useState('')
  const canvasRef=useRef<HTMLCanvasElement|null>(null)
  const imageRef=useRef<HTMLImageElement|null>(null)
  const drawing=useRef(false)

  useEffect(()=>{
    if(!file){setPreview('');return}
    const url=URL.createObjectURL(file); setPreview(url)
    return ()=>URL.revokeObjectURL(url)
  },[file])

  const clearMask=()=>{
    const c=canvasRef.current
    if(!c)return
    const ctx=c.getContext('2d'); if(ctx)ctx.clearRect(0,0,c.width,c.height)
  }

  const syncCanvas=()=>{
    const img=imageRef.current, c=canvasRef.current
    if(!img||!c)return
    c.width=img.naturalWidth; c.height=img.naturalHeight
    c.style.width=`${img.clientWidth}px`; c.style.height=`${img.clientHeight}px`
  }

  const paint=(e:React.PointerEvent<HTMLCanvasElement>)=>{
    const c=canvasRef.current; if(!c)return
    const rect=c.getBoundingClientRect();
    const x=(e.clientX-rect.left)*(c.width/rect.width)
    const y=(e.clientY-rect.top)*(c.height/rect.height)
    const ctx=c.getContext('2d'); if(!ctx)return
    ctx.fillStyle='white'; ctx.beginPath(); ctx.arc(x,y,Math.max(18,c.width/80),0,Math.PI*2); ctx.fill()
  }

  const run=async()=>{
    if(!file)return
    setBusy(true); setError(''); setResult(null); setCleanedPreview('')
    try{
      const form=new FormData(); form.append('file',file)
      if(mode==='text'){
        const data=await api.removal.removeText(form)
        setResult(data)
        const blob=await api.downloadRemoval(data.job_id); setCleanedPreview(URL.createObjectURL(blob))
      }else{
        const c=canvasRef.current
        if(!c) throw new Error('Mask canvas is not ready.')
        const hasMask=c.getContext('2d')?.getImageData(0,0,c.width,c.height).data.some((v,i)=>i%4===3&&v>0)
        if(!hasMask) throw new Error('Paint over the object you want to remove first.')
        const maskBlob=await new Promise<Blob|null>(resolve=>c.toBlob(resolve,'image/png'))
        if(!maskBlob) throw new Error('Could not create the removal mask.')
        form.append('mask',maskBlob,'mask.png')
        const data=await api.removal.removeObject(form); setResult(data)
        const cleanedBlob=await api.downloadRemoval(data.job_id); setCleanedPreview(URL.createObjectURL(cleanedBlob))
      }
    }catch(e){setError(e instanceof Error?e.message:'Removal failed.')}
    finally{setBusy(false)}
  }

  const cleanedSrc=cleanedPreview

  return <div className="max-w-7xl mx-auto px-5 py-8">
    <div className="max-w-3xl">
      <div className="text-xs uppercase tracking-[.2em] text-cyan-300">AI cleanup lab</div>
      <h1 className="mt-2 text-4xl font-bold text-white">Remove text & unwanted objects</h1>
      <p className="mt-2 text-slate-400">Use pretrained CPU-friendly models. No local model training or high-end GPU is required.</p>
    </div>

    <div className="grid lg:grid-cols-[.8fr_1.2fr] gap-5 mt-8">
      <div className="card rounded-2xl p-6">
        <div className="grid grid-cols-2 gap-2 mb-5">
          <button onClick={()=>setMode('text')} className={`rounded-xl px-4 py-3 text-sm font-semibold ${mode==='text'?'bg-cyan-400 text-slate-950':'bg-white/5 text-slate-300'}`}>Auto text</button>
          <button onClick={()=>setMode('object')} className={`rounded-xl px-4 py-3 text-sm font-semibold ${mode==='object'?'bg-cyan-400 text-slate-950':'bg-white/5 text-slate-300'}`}>Brush object</button>
        </div>
        <label className="block border border-dashed border-white/15 rounded-2xl p-6 text-center cursor-pointer hover:border-cyan-400/50">
          <input type="file" accept=".jpg,.jpeg,.png,.webp" className="hidden" onChange={e=>{setFile(e.target.files?.[0]||null);setResult(null);clearMask()}}/>
          <div className="text-white font-semibold">{file?file.name:'Choose an image'}</div>
          <div className="text-sm text-slate-500 mt-1">JPG, PNG or WEBP • up to 20 MB</div>
        </label>
        {file&&<button onClick={run} disabled={busy} className="mt-4 w-full py-3 rounded-xl bg-indigo-500 hover:bg-indigo-400 disabled:opacity-40 text-white font-semibold">{busy?'Running pretrained models…':mode==='text'?'Detect & remove text':'Remove painted object'}</button>}
        {mode==='object'&&<button onClick={clearMask} className="mt-2 w-full py-3 rounded-xl bg-white/5 text-slate-300">Clear brush mask</button>}
        <div className="mt-6 rounded-xl border border-white/10 bg-white/[.03] p-4 text-xs text-slate-500 leading-5">
          <b className="text-slate-300">Models:</b> PP-OCRv5 mobile text detector + LaMa inpainting. Text removal is automatic; object removal uses your brush mask so we don't pretend a generic detector can identify every object reliably.
        </div>
        {error&&<div className="mt-4 rounded-xl bg-rose-500/10 border border-rose-500/20 p-4 text-sm text-rose-300">{error}</div>}
      </div>

      <div className="card rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4"><h2 className="font-semibold text-white">Before / after</h2>{result&&<span className="text-xs text-emerald-300">Completed</span>}</div>
        {!file?<div className="h-96 grid place-items-center text-slate-600">Select an image to begin.</div>:<div className="grid md:grid-cols-2 gap-4">
          <div><div className="text-xs text-slate-500 mb-2">ORIGINAL {mode==='object'&&'• PAINT WHITE OVER THE OBJECT'}</div><div className="relative rounded-xl overflow-hidden bg-black/20"><img ref={imageRef} src={preview} onLoad={syncCanvas} className="w-full max-h-[520px] object-contain"/><canvas ref={canvasRef} onPointerDown={e=>{drawing.current=true;e.currentTarget.setPointerCapture(e.pointerId);paint(e)}} onPointerMove={e=>drawing.current&&paint(e)} onPointerUp={()=>drawing.current=false} onPointerCancel={()=>drawing.current=false} className={`absolute inset-0 w-full h-full ${mode==='object'?'cursor-crosshair':'pointer-events-none'}`} /></div></div>
          <div><div className="text-xs text-slate-500 mb-2">CLEANED</div>{result?<img src={cleanedSrc} className="w-full max-h-[520px] object-contain rounded-xl bg-black/20"/>:<div className="h-80 rounded-xl bg-white/[.02] border border-white/5 grid place-items-center text-slate-600">Run the cleanup to see the result.</div>}</div>
        </div>}
        {result&&<div className="mt-5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 p-4 text-sm text-slate-300"><div className="font-semibold text-emerald-300">{result.model}</div>{result.region_count!=null&&<div className="mt-1">Detected text regions removed: {result.region_count}</div>}<a href={cleanedSrc} target="_blank" rel="noreferrer" className="inline-block mt-3 text-cyan-300 hover:text-cyan-200">Open cleaned image →</a></div>}
      </div>
    </div>
  </div>
}
