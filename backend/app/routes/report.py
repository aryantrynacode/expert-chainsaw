# app/routes/report.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Response
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas
from ..services.exporter import generate_pdf_bytes
import os
import shutil

router = APIRouter(prefix="/report", tags=["report"])

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/{finding_id}/upload_poc")
def upload_poc(finding_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    finding = db.query(models.Finding).filter(models.Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    filename = f"poc_{finding_id}_{file.filename}"
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    finding.poc_path = path
    db.add(finding)
    db.commit()
    db.refresh(finding)
    return {"message": "uploaded", "path": path}

@router.get("/findings/{finding_id}", response_model=schemas.FindingOut)
def get_finding(finding_id: int, db: Session = Depends(get_db)):
    f = db.query(models.Finding).filter(models.Finding.id == finding_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Finding not found")
    return f

@router.get("/export/{finding_id}/pdf")
def export_pdf(finding_id: int, db: Session = Depends(get_db)):
    f = db.query(models.Finding).filter(models.Finding.id == finding_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Finding not found")
    finding_dict = {
        "title": f.title,
        "description": f.description,
        "location": f.location,
        "severity": f.severity,
        "ai_confidence": f.ai_confidence
    }
    pdf_bytes = generate_pdf_bytes(finding_dict, f.poc_path)
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=finding_{finding_id}.pdf"})
