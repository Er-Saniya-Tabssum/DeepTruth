import React from 'react'
import type {AnalysisStatus,AnalysisStage} from '../types/api'
const STAGES: {id:AnalysisStage;label:string}[]=[
 {id:'QUEUED',label:'Queued'},
 {id:'PREPROCESSING',label:'Preprocessing'},
 {id:'AI_DETECTION',label:'AI detection'},
 {id:'AUTHENTICITY_ANALYSIS',label:'Authenticity assessment'},
 {id:'FINAL_ASSESSMENT',label:'Final assessment'},
]
export default function AnalysisProgress({status,currentStage,progress}:{status:AnalysisStatus;currentStage?:AnalysisStage|null;progress?:number|null}){
 const idx=STAGES.findIndex(s=>s.id===currentStage)
 return <div className="mt-4"><div className="space-y-3">{STAGES.map((s,i)=>{const done=status==='COMPLETED'||i<idx;const active=s.id===currentStage&&status!=='COMPLETED';return <div key={s.id} className="flex items-center gap-3"><div className={`w-2.5 h-2.5 rounded-full ${done?'bg-emerald-400':active?'bg-cyan-300 animate-pulse':'bg-white/10'}`}/><span className={`text-sm ${active||done?'text-slate-200':'text-slate-600'}`}>{s.label}</span>{active&&<span className="ml-auto text-xs text-cyan-300">Running</span>}</div>})}</div>{progress!=null&&<div className="mt-6"><div className="flex justify-between text-xs text-slate-500 mb-2"><span>Progress</span><span>{progress}%</span></div><div className="h-2 rounded-full bg-white/5 overflow-hidden"><div className="h-full bg-gradient-to-r from-indigo-500 to-cyan-400 rounded-full transition-all" style={{width:`${progress}%`}}/></div></div>}</div>
}
