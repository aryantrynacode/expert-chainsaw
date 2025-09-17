from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from PIL import Image as PILImage
import io
import os

def generate_pdf_bytes(finding: dict, poc_path: str | None = None) -> bytes:
    """
    Create a PDF bytes from finding dict and optional poc image path
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph(f"<b>{finding.get('title','Vulnerability Report')}</b>", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Severity:</b> {finding.get('severity')}", styles["Normal"]))
    story.append(Paragraph(f"<b>AI Confidence:</b> {finding.get('ai_confidence')}", styles["Normal"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Description</b>", styles["Heading3"]))
    story.append(Paragraph(finding.get("description","N/A"), styles["Normal"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Location</b>", styles["Heading4"]))
    story.append(Paragraph(str(finding.get("location","-")), styles["Normal"]))
    story.append(Spacer(1, 12))
    if poc_path and os.path.exists(poc_path):
        # convert image to JPG if needed and embed
        try:
            im = PILImage.open(poc_path)
            # scale image to fit
            max_w = 6.5*inch
            width, height = im.size
            ratio = min(max_w/width, 1.0)
            display_w = width * ratio
            display_h = height * ratio
            # Save to BytesIO as JPEG
            img_buffer = io.BytesIO()
            im.save(img_buffer, format="JPEG")
            img_buffer.seek(0)
            story.append(Paragraph("<b>PoC Screenshot</b>", styles["Heading4"]))
            story.append(Image(img_buffer, width=display_w, height=display_h))
            story.append(Spacer(1,12))
        except Exception:
            story.append(Paragraph("Could not embed PoC image.", styles["Normal"]))
    doc.build(story)
    buffer.seek(0)
    return buffer.read()

