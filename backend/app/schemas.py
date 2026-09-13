from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from enum import Enum


# Enums
class AnalysisStatus(str, Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class MediaType(str, Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"


class AnalysisVerdict(str, Enum):
    AUTHENTIC = "AUTHENTIC"
    POTENTIALLY_MANIPULATED = "POTENTIALLY_MANIPULATED"
    AI_GENERATED = "AI_GENERATED"
    FACE_SWAP_DETECTED = "FACE_SWAP_DETECTED"
    INCONCLUSIVE = "INCONCLUSIVE"


class Confidence(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class InferenceMode(str, Enum):
    REAL = "REAL"
    DEMO = "DEMO"


class ModelProvider(str, Enum):
    PRODUCTION = "PRODUCTION"
    MY_MODEL = "MY_MODEL"


# Standard response envelope
class ApiError(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None


class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[ApiError] = None


# Auth
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    created_at: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthResponse(BaseModel):
    user: UserOut
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# Analysis
class AnalysisCreateResponse(BaseModel):
    analysis_id: str
    filename: str
    media_type: MediaType
    file_size: int
    status: AnalysisStatus
    inference_mode: InferenceMode
    model_provider: ModelProvider
    created_at: str


class BBox(BaseModel):
    x: int
    y: int
    width: int
    height: int


class DetectedFace(BaseModel):
    face_id: Optional[str] = None
    bbox: Optional[BBox] = None
    identity_name: Optional[str] = None
    identity_confidence: Optional[float] = None
    identity_distance: Optional[float] = None
    deepfake_probability: Optional[float] = None
    notes: Optional[str] = None


class Artifact(BaseModel):
    type: str
    url: str
    size: Optional[int] = None
    media_type: Optional[MediaType] = None
    created_at: Optional[str] = None


class ForensicEvidence(BaseModel):
    type: str
    severity: str
    title: str
    value: str
    explanation: str


class AnalysisResult(BaseModel):
    verdict: Optional[AnalysisVerdict] = None
    authenticity_score: Optional[float] = None
    ai_probability: Optional[float] = None
    face_swap_probability: Optional[float] = None
    confidence: Optional[Confidence] = None
    faces_detected: Optional[int] = None
    detected_faces: Optional[List[DetectedFace]] = None
    evidence: Optional[List[ForensicEvidence]] = None
    suspicious_regions: Optional[List[BBox]] = None
    frame_results: Optional[Any] = None


class AnalysisDetail(BaseModel):
    analysis_id: str
    filename: str
    media_type: MediaType
    status: AnalysisStatus
    progress: Optional[int] = None
    current_stage: Optional[str] = None
    inference_mode: InferenceMode
    model_provider: ModelProvider
    training_consent: Optional[bool] = None
    training_status: str = "NOT_REQUESTED"
    result: Optional[AnalysisResult] = None
    created_at: str
    completed_at: Optional[str] = None


class AnalysisSummary(BaseModel):
    analysis_id: str
    filename: str
    media_type: MediaType
    status: AnalysisStatus
    verdict: Optional[AnalysisVerdict] = None
    created_at: str
    completed_at: Optional[str] = None


class Pagination(BaseModel):
    page: int
    limit: int
    total: int
    items: List[AnalysisSummary]


class DashboardStats(BaseModel):
    total_analyses: int
    by_status: dict
    by_verdict: dict
    recent_analyses: List[AnalysisSummary]
    storage_used_bytes: int


# Tracking
class TrackedImageOut(BaseModel):
    tracked_id: str
    analysis_id: Optional[str] = None
    source_url: Optional[str] = None
    created_at: Optional[str] = None


class TrackingMatchOut(BaseModel):
    id: str
    match_url: str
    confidence: Optional[float] = None
    created_at: Optional[str] = None


class TrackedImageDetail(BaseModel):
    tracked_id: str
    analysis_id: Optional[str] = None
    source_url: Optional[str] = None
    matches: Optional[List[TrackingMatchOut]] = None


class TrackingAvailable(BaseModel):
    available: bool
    provider: Optional[str] = None
    reason: Optional[str] = None

