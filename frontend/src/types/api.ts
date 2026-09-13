// TypeScript types mirroring backend Pydantic models (subset)

export type AnalysisStatus = 'QUEUED' | 'PROCESSING' | 'COMPLETED' | 'FAILED'
export type AnalysisStage = 'QUEUED' | 'UPLOADING' | 'PREPROCESSING' | 'FACE_DETECTION' | 'AI_DETECTION' | 'AUTHENTICITY_ANALYSIS' | 'FACE_SWAP_ANALYSIS' | 'EVIDENCE_EXTRACTION' | 'FINAL_ASSESSMENT' | 'FAILED'
export type MediaType = 'IMAGE' | 'VIDEO'
export type AnalysisVerdict = 'AUTHENTIC' | 'POTENTIALLY_MANIPULATED' | 'AI_GENERATED' | 'FACE_SWAP_DETECTED' | 'INCONCLUSIVE'
export type Confidence = 'LOW' | 'MEDIUM' | 'HIGH'
export type InferenceMode = 'REAL' | 'DEMO'
export type ModelProvider = 'PRODUCTION' | 'MY_MODEL'

export interface User {
  id: string
  name: string
  email: string
  created_at: string
}

export interface Artifact {
  type: string
  url: string
  size?: number
  media_type?: MediaType
  created_at?: string
}

export interface DetectedFace {
  face_id?: string | null
  bbox?: { x:number, y:number, width:number, height:number } | null
  identity_name?: string | null
  identity_confidence?: number | null
  identity_distance?: number | null
  deepfake_probability?: number | null
  notes?: string | null
}

export interface ForensicEvidence {
  type: string
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'INFO' | string
  title: string
  value: string
  explanation: string
}

export interface AnalysisResult {
  verdict?: AnalysisVerdict | null
  authenticity_score?: number | null
  ai_probability?: number | null
  face_swap_probability?: number | null
  confidence?: Confidence | null
  faces_detected?: number | null
  detected_faces?: DetectedFace[] | null
  evidence?: ForensicEvidence[] | null
  suspicious_regions?: {x:number,y:number,width:number,height:number}[] | null
  frame_results?: any | null
  media_metadata?: { width?: number; height?: number; format?: string; exif_present?: boolean; sha256?: string } | null
  model_metadata?: { model_name?: string; version?: string; framework?: string; inference_mode?: string; device?: string; processing_time?: number } | null
  raw_predictions?: { label: string; score: number }[] | null
  limitations?: string[] | null
}

export interface AnalysisDetail {
  analysis_id: string
  filename: string
  media_type: MediaType
  status: AnalysisStatus
  progress?: number | null
  current_stage?: string | null
  inference_mode: InferenceMode
  model_provider: ModelProvider
  training_consent?: boolean | null
  training_status?: string
  result?: AnalysisResult | null
  created_at: string
  completed_at?: string | null
}

