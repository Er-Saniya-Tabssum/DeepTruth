import React, {useState} from 'react'
import {api} from '../lib/api'

interface Props { analysisId: string }

export default function AnalysisActions({analysisId}:Props){
  const [loading, setLoading] = useState(false)

  const downloadReport = async ()=>{
    setLoading(true)
    try{
      const blob = await api.downloadReport(analysisId)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `deeptruth-analysis-${analysisId}.pdf`
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
    }catch(e){ alert(e instanceof Error ? e.message : 'Failed to download report') }
    finally{ setLoading(false) }
  }

  const deleteAnalysis = async ()=>{
    if(!confirm('Delete analysis? This cannot be undone.')) return
    setLoading(true)
    try{
      await api.analysis.delete(analysisId)
      window.location.href = '/history'
    }catch(e){ alert(e instanceof Error ? e.message : 'Failed to delete analysis') }
    finally{ setLoading(false) }
  }

  return (
    <div className="flex flex-wrap gap-2">
      <button onClick={downloadReport} className="bg-blue-600 text-white px-3 py-2 rounded" disabled={loading}>Download Report</button>
      <button onClick={()=>{ window.location.href = '/analyze' }} className="bg-gray-200 px-3 py-2 rounded">Analyze Another</button>
      <button onClick={deleteAnalysis} className="bg-red-600 text-white px-3 py-2 rounded" disabled={loading}>Delete</button>
    </div>
  )
}
