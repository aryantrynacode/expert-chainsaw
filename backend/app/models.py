from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum as sqlEnum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base
import enum

class ReportStatus(enum.Enum):
    PENDING = "pending"
    verified = "verified"
    false_positive = "false_positive"
    drafted = "drafted"
    exported = "exported"

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    scans = relationship("scans", back_populates="owner")

class Scan(Base):
    __tablename__ = "scans"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    urls = Column(JSON, nullable = True)
    scan_results = Column(JSON, nullable = True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="scans")
    findings = relationship("finding", back_populates="scan")

class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    severity = Column(String, nullable=True)
    ai_confidence = Column(Float, nullable=True)

    status = Column(
        sqlEnum(ReportStatus, name="finding_status"),
        default=ReportStatus.PENDING,
        nullable=False
    )

    poc_path = Column(String, nullable=True)  # path to uploaded PoC screenshot/file
    created_at = Column(DateTime, default=datetime.utcnow)

class Export(Base):
    __tablename__ = "exports"
    id = Column(Integer, primary_key=True, index=True)
    finding_id = Column(Integer, ForeignKey("findings.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    format = Column(String)
    path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)