import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from '../lib/api'
import type { AnalysisDetail, AnalysisStatus } from '../types/api'

type JobState = 'IDLE'|'SELECTED'|'UPLOADING'|'QUEUED'|'PROCESSING'|'COMPLETED'|'FAILED'

export function useAnalysisJob(){
  const [file, setFile] = useState<File | null>(null)
  const [state, setState] = useState<JobState>('IDLE')
  const [analysis, setAnalysis] = useState<AnalysisDetail | null>(null)
  const [error, setError] = useState<string | null>(null)
  const pollRef = useRef<number | null>(null)

  // recovery: persist current analysis id in sessionStorage
  useEffect(()=>{
    const stored = sessionStorage.getItem('dt_current_analysis')
    if(stored){
      // try to load status
      ;(async ()=>{
        try{
          const res = await api.analysis.get(stored)
          setAnalysis(res)
          if(res.status === 'COMPLETED') setState('COMPLETED')
          else if(res.status === 'FAILED') setState('FAILED')
          else { setState(res.status === 'QUEUED' ? 'QUEUED' : 'PROCESSING'); startPolling(res.analysis_id) }
        }catch(e){ sessionStorage.removeItem('dt_current_analysis') }
      })()
    }
  },[])

  const selectFile = useCallback((f: File | null)=>{
    setFile(f)
    setError(null)
    setAnalysis(null)
    setState(f? 'SELECTED':'IDLE')
  },[])

  const uploadAndStart = useCallback(async (modelProvider: 'PRODUCTION' | 'MY_MODEL' = 'PRODUCTION')=>{
    if(!file) return
    if(state === 'UPLOADING' || state === 'QUEUED' || state === 'PROCESSING') return
    setState('UPLOADING')
    setError(null)
    try{
      const form = new FormData()
      form.append('file', file)
      form.append('model_provider', modelProvider)
      const res = await api.analysis.upload(form)
      const analysisId = res.analysis_id
      // persist for recovery
      sessionStorage.setItem('dt_current_analysis', analysisId)
      // start run
      await api.analysis.run(analysisId)
      setState('QUEUED')
      // start polling
      startPolling(analysisId)
    }catch(err:any){
      setError(err.message || 'Upload failed')
      setState('FAILED')
    }
  },[file,state])

  const startPolling = useCallback((analysisId:string)=>{
    // clear existing poll
    if(pollRef.current) window.clearInterval(pollRef.current)
    const poll = async ()=>{
      try{
        const res = await api.analysis.get(analysisId)
        setAnalysis(res)
        const s = res.status as AnalysisStatus
        if(s === 'COMPLETED'){
          setState('COMPLETED')
          sessionStorage.removeItem('dt_current_analysis')
          if(pollRef.current){ window.clearInterval(pollRef.current); pollRef.current = null }
        }else if(s === 'FAILED'){
          setState('FAILED')
          sessionStorage.removeItem('dt_current_analysis')
          if(pollRef.current){ window.clearInterval(pollRef.current); pollRef.current = null }
        }else{
          setState(s === 'QUEUED' ? 'QUEUED' : 'PROCESSING')
        }
      }catch(e:any){
        // network error â€” do not mark as failed immediately
        setError('Unable to reach the server. Will retry.');
      }
    }
    // initial immediate poll
    poll()
    const id = window.setInterval(poll, 2000)
    pollRef.current = id
  },[])

  useEffect(()=>{
    return ()=>{ if(pollRef.current) window.clearInterval(pollRef.current) }
  },[])

  const cancel = useCallback(()=>{
    setFile(null); setAnalysis(null); setState('IDLE'); setError(null); sessionStorage.removeItem('dt_current_analysis')
    if(pollRef.current){ window.clearInterval(pollRef.current); pollRef.current = null }
  },[])

  return { file, selectFile, uploadAndStart, state, analysis, error, cancel }
}

