from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas
from ..services import analyzer
from ..config import settings

router = APIRouter(prefix="/chatbot", tags=["chatbot"])

@router.post("/refine/{finding_id}")
def refine_report(finding_id: int, payload: schemas.ChatbotMessage, db: Session = Depends(get_db)):
    f = db.query(models.Finding).filter(models.Finding.id == finding_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Finding not found")
    # Combine existing finding + user prompt/context and ask the analyzer (LLM) to refine the text
    scan_data = {f.location: {"title": f.title, "description": f.description}}
    # pass extra_text as the prompt content to the analyzer; analyzer will call OpenAI if available
    result = analyzer.analyze_scan(scan_data, extra_text=payload.prompt)
    # result is mapping URL -> analysis; pick relevant entry
    analysis_entry = result.get(f.location) or (next(iter(result.values())) if isinstance(result, dict) else {})
    # Update finding with refined fields (if present)
    f.title = analysis_entry.get("title", f.title)
    f.description = analysis_entry.get("description", f.description)
    f.severity = analysis_entry.get("severity", f.severity)
    f.ai_confidence = float(analysis_entry.get("ai_confidence", f.ai_confidence or 0.0))
    db.add(f)
    db.commit()
    db.refresh(f)
    return {"refined": {"title": f.title, "description": f.description, "severity": f.severity, "ai_confidence": f.ai_confidence}}