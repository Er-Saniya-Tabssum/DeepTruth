import React, {useCallback, useRef, useState} from 'react'

interface MediaDropzoneProps {
  accept: string[]
  maxSizeBytes: number
  disabled?: boolean
  onFileSelected: (file: File | null) => void
}

export default function MediaDropzone({accept, maxSizeBytes, disabled=false, onFileSelected}: MediaDropzoneProps){
  const [isDrag, setIsDrag] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement | null>(null)

  const onFiles = useCallback((files: FileList | null) => {
    setError(null)
    if(!files || files.length===0){ onFileSelected(null); return }
    const f = files[0]
    const ext = (f.name.split('.').pop() || '').toLowerCase()
    const mime = f.type
    // basic accept check
    const allowedExt = accept.map(a => a.replace('.', '').toLowerCase())
    if(!allowedExt.includes(ext) && !accept.includes(mime)){
      setError('Unsupported file type.')
      onFileSelected(null)
      return
    }
    if(f.size === 0){ setError('The selected file is empty.'); onFileSelected(null); return }
    if(f.size > maxSizeBytes){ setError('File is too large.'); onFileSelected(null); return }
    onFileSelected(f)
  },[accept,maxSizeBytes,onFileSelected])

  const handleDrop = useCallback((e: React.DragEvent)=>{
    e.preventDefault(); e.stopPropagation(); setIsDrag(false)
    onFiles(e.dataTransfer.files)
  },[onFiles])

  const handleDragOver = useCallback((e: React.DragEvent)=>{
    e.preventDefault(); e.stopPropagation(); setIsDrag(true)
  },[])

  const handleDragLeave = useCallback((e: React.DragEvent)=>{
    e.preventDefault(); e.stopPropagation(); setIsDrag(false)
  },[])

  const handleClick = () => { if(disabled) return; inputRef.current?.click() }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>)=>{
    onFiles(e.target.files)
  }

  return (
    <div>
      <div
        role="button"
        tabIndex={0}
        onKeyDown={(e)=>{ if(e.key==='Enter' || e.key===' ') handleClick() }}
        onClick={handleClick}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        aria-disabled={disabled}
        className={["border-dashed border-2 rounded p-8 text-center", isDrag? 'border-cyan-400 bg-cyan-400/5':'border-white/10 bg-white/[.02]', disabled? 'opacity-50 pointer-events-none':''].join(' ')}
      >
        <input ref={inputRef} type="file" accept={accept.join(",")} className="hidden" onChange={handleChange} aria-hidden multiple={false} />
        <div className="max-w-md mx-auto">
          <p className="text-lg font-medium">Drag & drop your image or video here</p>
          <p className="text-sm text-slate-500 mt-2">Or click to choose a file</p>
          <p className="text-xs text-slate-600 mt-4">Supported: {accept.join(', ')} • Max size: {(maxSizeBytes/1024/1024).toFixed(1)} MB</p>
        </div>
      </div>
      {error && <div className="text-sm text-rose-300 mt-2">{error}</div>}
    </div>
  )
}
