from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .db import Base


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="USER")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    analyses = relationship("Analysis", back_populates="owner")


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String, primary_key=True, default=gen_uuid)
    owner_id = Column(
        String,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    filename = Column(String, nullable=False)
    media_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    storage_path = Column(String, nullable=True)
    status = Column(String, nullable=False, default="QUEUED")
    inference_mode = Column(String, nullable=False, default="REAL")
    model_provider = Column(String, nullable=False, default="PRODUCTION")
    training_consent = Column(Boolean, nullable=True)
    training_status = Column(String, nullable=False, default="NOT_REQUESTED")
    progress = Column(Integer, nullable=True, default=0)
    current_stage = Column(String, nullable=True)
    result = Column(Text, nullable=True)
    error_code = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    owner = relationship("User", back_populates="analyses")
    faces = relationship(
        "DetectedFace",
        back_populates="analysis",
        cascade="all, delete-orphan",
    )
    evidences = relationship(
        "Evidence",
        back_populates="analysis",
        cascade="all, delete-orphan",
    )


class DetectedFace(Base):
    __tablename__ = "detected_faces"

    id = Column(String, primary_key=True, default=gen_uuid)
    analysis_id = Column(
        String,
        ForeignKey("analyses.id"),
        nullable=False,
        index=True,
    )
    bbox_x = Column(Integer, nullable=True)
    bbox_y = Column(Integer, nullable=True)
    bbox_w = Column(Integer, nullable=True)
    bbox_h = Column(Integer, nullable=True)
    identity_name = Column(String, nullable=True)
    identity_confidence = Column(Float, nullable=True)

    analysis = relationship("Analysis", back_populates="faces")


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String, primary_key=True, default=gen_uuid)
    analysis_id = Column(
        String,
        ForeignKey("analyses.id"),
        nullable=False,
        index=True,
    )
    type = Column(String, nullable=False)
    url = Column(String, nullable=False)
    size = Column(Integer, nullable=True)
    media_type = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("Analysis", back_populates="evidences")


class TrackedImage(Base):
    __tablename__ = "tracked_images"

    id = Column(String, primary_key=True, default=gen_uuid)
    analysis_id = Column(
        String,
        ForeignKey("analyses.id"),
        nullable=True,
        index=True,
    )
    source_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TrackingMatch(Base):
    __tablename__ = "tracking_matches"

    id = Column(String, primary_key=True, default=gen_uuid)
    tracked_image_id = Column(
        String,
        ForeignKey("tracked_images.id"),
        nullable=False,
        index=True,
    )
    match_url = Column(String, nullable=False)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class RemovalRequest(Base):
    __tablename__ = "removal_requests"

    id = Column(String, primary_key=True, default=gen_uuid)
    analysis_id = Column(
        String,
        ForeignKey("analyses.id"),
        nullable=True,
        index=True,
    )
    target_url = Column(String, nullable=False)
    platform = Column(String, nullable=True)
    reason = Column(Text, nullable=False)
    contact_email = Column(String, nullable=True)
    status = Column(String, default="SUBMITTED")
    created_at = Column(DateTime, default=datetime.utcnow)


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(String, primary_key=True, default=gen_uuid)
    jti = Column(String, nullable=False, index=True)
    revoked_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

class RemovalJob(Base):
    __tablename__ = "removal_jobs"

    id = Column(String, primary_key=True, default=gen_uuid)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    mode = Column(String, nullable=False)
    source_path = Column(String, nullable=False)
    mask_path = Column(String, nullable=True)
    output_path = Column(String, nullable=True)
    status = Column(String, nullable=False, default="QUEUED")
    model_name = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False, default=0)
    detected_regions = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User")


