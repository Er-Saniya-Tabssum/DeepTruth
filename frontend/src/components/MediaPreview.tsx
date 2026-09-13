import React, {useEffect, useState} from 'react'

interface MediaPreviewProps {
  file: File | null
}

export default function MediaPreview({file}: MediaPreviewProps){
  const [url, setUrl] = useState<string | null>(null)
  const [duration, setDuration] = useState<number | null>(null)

  useEffect(()=>{
    if(!file){ setUrl(null); return }
    const objectUrl = URL.createObjectURL(file)
    setUrl(objectUrl)
    return ()=>{ URL.revokeObjectURL(objectUrl); setUrl(null) }
  },[file])

  useEffect(()=>{
    if(!url) return
    if(!file) return
    if(file.type.startsWith('video/')){
      const video = document.createElement('video')
      video.preload = 'metadata'
      video.src = url
      const handler = ()=>{ setDuration(video.duration); URL.revokeObjectURL(video.src) }
      video.addEventListener('loadedmetadata', handler)
      return ()=>{ video.removeEventListener('loadedmetadata', handler) }
    }
  },[url,file])

  if(!file) return null

  return (
    <div className="mt-4 bg-white p-4 rounded shadow">
      <div className="flex items-start gap-4">
        <div className="w-48 h-48 bg-gray-100 flex items-center justify-center overflow-hidden rounded">
          {file.type.startsWith('image/') && url && <img src={url} alt={file.name} className="object-contain w-full h-full" />}
          {file.type.startsWith('video/') && url && (
            <video src={url} controls className="w-full h-full object-contain" />
          )}
        </div>
        <div className="flex-1">
          <div className="text-sm text-gray-700"><strong>{file.name}</strong></div>
          <div className="text-xs text-gray-500">{(file.size/1024/1024).toFixed(2)} MB • {file.type || 'Unknown'}</div>
          {duration && <div className="text-xs text-gray-500">Duration: {Math.round(duration)}s</div>}
        </div>
      </div>
    </div>
  )
}
