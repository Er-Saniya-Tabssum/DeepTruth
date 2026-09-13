import React from 'react'

type Props = {
  value?: string | null
  kind?: 'status' | 'verdict' | 'confidence'
}

const STATUS_MAP: Record<string, string> = {
  QUEUED: 'bg-gray-100 text-gray-800',
  PROCESSING: 'bg-yellow-100 text-yellow-800',
  COMPLETED: 'bg-green-100 text-green-800',
  FAILED: 'bg-red-100 text-red-800',
}

const VERDICT_MAP: Record<string, string> = {
  AUTHENTIC: 'bg-green-100 text-green-800',
  POTENTIALLY_MANIPULATED: 'bg-yellow-100 text-yellow-800',
  AI_GENERATED: 'bg-red-100 text-red-800',
  FACE_SWAP_DETECTED: 'bg-red-100 text-red-800',
  INCONCLUSIVE: 'bg-gray-100 text-gray-800',
}

const CONFIDENCE_MAP: Record<string, string> = {
  LOW: 'bg-red-50 text-red-700',
  MEDIUM: 'bg-yellow-50 text-yellow-700',
  HIGH: 'bg-green-50 text-green-700',
}

export default function Badge({ value, kind = 'status' }: Props) {
  const v = value || ''
  let cls = 'bg-gray-100 text-gray-800'
  if (kind === 'status') cls = STATUS_MAP[v] ?? cls
  if (kind === 'verdict') cls = VERDICT_MAP[v] ?? cls
  if (kind === 'confidence') cls = CONFIDENCE_MAP[v] ?? cls

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-sm font-medium ${cls}`}>{value ?? 'N/A'}</span>
  )
}
