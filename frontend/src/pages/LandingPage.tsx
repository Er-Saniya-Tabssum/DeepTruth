import React from 'react'
import { Link } from 'react-router-dom'

export default function LandingPage(){
  return <div className="min-h-screen grid-bg">
    <header className="max-w-7xl mx-auto px-5 py-6 flex justify-between items-center">
      <div className="flex items-center gap-3"><div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-cyan-400 grid place-items-center font-black">D</div><span className="font-bold text-white text-lg">DeepTruth</span></div>
      <div className="flex gap-2"><Link to="/login" className="px-4 py-2 rounded-lg text-slate-300 hover:bg-white/5">Sign in</Link><Link to="/register" className="px-4 py-2 rounded-lg bg-white text-slate-950 font-semibold">Get started</Link></div>
    </header>
    <section className="max-w-6xl mx-auto px-5 pt-16 pb-24 text-center">
      <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full glass text-xs text-cyan-200 mb-7"><span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"/> Real ML inference • Private analysis workspace</div>
      <h1 className="text-5xl md:text-7xl font-black tracking-tight text-white leading-[1.02]">Know what you're<br/><span className="text-gradient">looking at.</span></h1>
      <p className="max-w-2xl mx-auto mt-7 text-lg text-slate-400 leading-8">DeepTruth analyzes images and sampled video frames with a pretrained vision model to estimate whether media is authentic or AI-generated.</p>
      <div className="mt-9 flex justify-center gap-3"><Link to="/register" className="px-6 py-3 rounded-xl bg-indigo-500 hover:bg-indigo-400 text-white font-semibold shadow-lg shadow-indigo-500/20">Analyze media</Link><a href="#how" className="px-6 py-3 rounded-xl glass text-slate-200">How it works</a></div>
      <div id="how" className="grid md:grid-cols-3 gap-4 mt-20 text-left">
        {[['01','Upload','Drop an image or video. Files stay tied to your account.'],['02','Detect','A real pretrained vision classifier scores AI-generation probability.'],['03','Explain','Review confidence, sampled frames, faces and a downloadable report.']].map(([n,t,d])=><div key={n} className="card rounded-2xl p-6"><div className="text-xs text-indigo-300 font-bold">{n}</div><h3 className="mt-5 text-xl font-semibold text-white">{t}</h3><p className="mt-2 text-sm leading-6 text-slate-400">{d}</p></div>)}
      </div>
    </section>
    <footer className="border-t border-white/10 py-8 text-center text-xs text-slate-600">DeepTruth • AI media forensics workspace</footer>
  </div>
}
