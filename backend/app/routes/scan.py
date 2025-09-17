# app/routes/scan.py
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas
from ..services import scanner, analyzer
from typing import List

router = APIRouter(prefix="/scan", tags=["scan"])

@router.post("/submit", response_model=schemas.ScanOut)
def submit_scan(payload: schemas.ScanCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # create a scan record with queued results
    scan_results = {url: {"status": "queued", "analysis": None} for url in payload.urls}
    scan = models.Scan(user_id=None, urls=payload.urls, scan_results=scan_results)
    db.add(scan)
    db.commit()
    db.refresh(scan)

    # run passive scans in background
    def run_scans(scan_id: int, urls: List[str]):
        db2 = next(get_db())
        try:
            results = scanner.passive_scan_urls(urls)
            # update scan record
            s = db2.query(models.Scan).filter(models.Scan.id == scan_id).first()
            s.scan_results = results
            db2.add(s)
            db2.commit()
        finally:
            db2.close()

    background_tasks.add_task(run_scans, scan.id, payload.urls)
    return scan

@router.get("/{scan_id}", response_model=schemas.ScanOut)
def get_scan(scan_id: int, db: Session = Depends(get_db)):
    s = db.query(models.Scan).filter(models.Scan.id == scan_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Scan not found")
    return s

@router.post("/{scan_id}/run_analysis")
def run_analysis(scan_id: int, db: Session = Depends(get_db)):
    s = db.query(models.Scan).filter(models.Scan.id == scan_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Scan not found")
    scan_data = s.scan_results or {}
    analysis = analyzer.analyze_scan(scan_data)
    # Create findings entries for each suspicious url
    created = []
    for url, a in analysis.items():
        title = a.get("title", f"Finding for {url}")
        description = a.get("description", "")
        location = a.get("location", url)
        severity = a.get("severity", "Low")
        confidence = float(a.get("ai_confidence", 0.0))
        finding = models.Finding(scan_id=s.id, title=title, description=description, location=location, severity=severity, ai_confidence=confidence)
        db.add(finding)
        db.commit()
        db.refresh(finding)
        created.append({"finding_id": finding.id, "url": url})
    return {"created": created}