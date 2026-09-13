from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch
import io
import json
import os


def safe_text(val):
    if val is None:
        return "Not available"
    if isinstance(val, (int, float)):
        return str(val)
    return str(val)


def generate_report_pdf_bytes(analysis, evidences, faces):
    """
    Build a PDF bytes for a given analysis record.
    - analysis: models.Analysis instance
    - evidences: list of Evidence ORM objects
    - faces: list of DetectedFace ORM objects
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    elements = []

    # Cover
    title = Paragraph("<b>DEEPTRUTH</b>", styles['Title'])
    subtitle = Paragraph("AI MEDIA FORENSIC ANALYSIS REPORT", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 6))
    elements.append(subtitle)
    elements.append(Spacer(1, 12))

    generated = safe_text(getattr(analysis, 'created_at', None))
    elements.append(Paragraph(f"Analysis ID: {analysis.id}", styles['Normal']))
    elements.append(Paragraph(f"Generated: {generated}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Summary Section
    elements.append(Paragraph('<b>1. Analysis Summary</b>', styles['Heading2']))
    try:
        result = json.loads(analysis.result) if analysis.result else {}
    except Exception:
        result = {}
    verdict = result.get('verdict') if result else None
    confidence = result.get('confidence') if result else None

    summary_table_data = [
        ['Analysis ID', safe_text(analysis.id)],
        ['Filename', safe_text(analysis.filename)],
        ['Media Type', safe_text(analysis.media_type)],
        ['Analysis Date', safe_text(analysis.created_at.isoformat() if analysis.created_at else None)],
        ['Status', safe_text(analysis.status)],
        ['Verdict', safe_text(verdict)],
        ['Confidence', safe_text(confidence)],
    ]
    t = Table(summary_table_data, hAlign='LEFT', colWidths=[150, 350])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.whitesmoke), ('VALIGN',(0,0),(-1,-1),'TOP'), ('INNERGRID', (0,0), (-1,-1), 0.25, colors.grey), ('BOX', (0,0), (-1,-1), 0.25, colors.grey)]))
    elements.append(t)
    elements.append(Spacer(1, 12))

    # Media Information
    elements.append(Paragraph('<b>2. Media Information</b>', styles['Heading2']))
    media_table = []
    media_table.append(['Filename', safe_text(analysis.filename)])
    media_table.append(['File Type', safe_text(analysis.media_type)])
    media_table.append(['File Size (bytes)', safe_text(analysis.file_size)])

    # If evidences contain dimensions/duration in metadata, include if present
    # We intentionally do not attempt to probe files for metadata here.
    mt = Table(media_table, colWidths=[150, 350], hAlign='LEFT')
    mt.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'), ('INNERGRID', (0,0), (-1,-1), 0.25, colors.grey), ('BOX', (0,0), (-1,-1), 0.25, colors.grey)]))
    elements.append(mt)
    elements.append(Spacer(1, 12))

    # Forensic Assessment
    elements.append(Paragraph('<b>3. Forensic Assessment</b>', styles['Heading2']))
    assessment = []
    assessment.append(['Verdict', safe_text(verdict)])
    # If there are numeric scores present in result, include them
    for k in ('authenticity_score', 'ai_probability', 'face_swap_probability'):
        if result and k in result:
            assessment.append([k.replace('_',' ').title(), safe_text(result.get(k))])
    at = Table(assessment, colWidths=[200,300], hAlign='LEFT')
    at.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'), ('INNERGRID', (0,0), (-1,-1), 0.25, colors.grey), ('BOX', (0,0), (-1,-1), 0.25, colors.grey)]))
    elements.append(at)
    elements.append(Spacer(1,12))

    # Detected Faces
    elements.append(Paragraph('<b>4. Detected Faces</b>', styles['Heading2']))
    if faces and len(faces)>0:
        faces_data = [['Face #', 'BBox (x,y,w,h)', 'Identity', 'Confidence']]
        for idx, f in enumerate(faces, start=1):
            bbox = 'Not available'
            try:
                bx = (f.bbox_x, f.bbox_y, f.bbox_w, f.bbox_h)
                bbox = ','.join([safe_text(x) for x in bx])
            except Exception:
                bbox = 'Not available'
            faces_data.append([str(idx), bbox, safe_text(getattr(f, 'identity_name', None)), safe_text(getattr(f, 'identity_confidence', None))])
        ft = Table(faces_data, colWidths=[50,200,150,100])
        ft.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.whitesmoke), ('INNERGRID',(0,0),(-1,-1),0.25,colors.grey), ('BOX',(0,0),(-1,-1),0.25,colors.grey)]))
        elements.append(ft)
    else:
        elements.append(Paragraph('No detected face data available', styles['Normal']))
    elements.append(Spacer(1,12))

    # Evidence
    elements.append(Paragraph('<b>5. Forensic Evidence</b>', styles['Heading2']))
    structured_evidence = result.get('evidence') if isinstance(result, dict) else None
    if structured_evidence:
        ev_data = [['Severity', 'Type', 'Finding', 'Explanation']]
        for item in structured_evidence:
            ev_data.append([
                safe_text(item.get('severity')),
                safe_text(item.get('type')),
                safe_text(item.get('title')) + ': ' + safe_text(item.get('value')),
                safe_text(item.get('explanation')),
            ])
        et = Table(ev_data, colWidths=[65,90,145,250], repeatRows=1)
        et.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.whitesmoke), ('VALIGN',(0,0),(-1,-1),'TOP'), ('INNERGRID',(0,0),(-1,-1),0.25,colors.grey), ('BOX',(0,0),(-1,-1),0.25,colors.grey)]))
        elements.append(et)
    elif evidences:
        ev_data = [['Type','Explanation']]
        for e in evidences:
            ev_data.append([safe_text(e.type), safe_text(e.url)])
        et = Table(ev_data, colWidths=[120,430], repeatRows=1)
        et.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.whitesmoke), ('VALIGN',(0,0),(-1,-1),'TOP'), ('INNERGRID',(0,0),(-1,-1),0.25,colors.grey), ('BOX',(0,0),(-1,-1),0.25,colors.grey)]))
        elements.append(et)
    else:
        elements.append(Paragraph('No forensic evidence available', styles['Normal']))
    elements.append(Spacer(1,12))

    # Suspicious Regions
    elements.append(Paragraph('<b>6. Suspicious Regions</b>', styles['Heading2']))
    # We read suspicious_regions from result if present
    if result and result.get('suspicious_regions'):
        sr = result.get('suspicious_regions')
        sr_data = [['Region #','x','y','width','height']]
        for idx, r in enumerate(sr, start=1):
            sr_data.append([str(idx), safe_text(r.get('x')), safe_text(r.get('y')), safe_text(r.get('width')), safe_text(r.get('height'))])
        srt = Table(sr_data, colWidths=[60,100,100,100,100])
        srt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.whitesmoke), ('INNERGRID',(0,0),(-1,-1),0.25,colors.grey), ('BOX',(0,0),(-1,-1),0.25,colors.grey)]))
        elements.append(srt)
    else:
        elements.append(Paragraph('No suspicious region data available', styles['Normal']))
    elements.append(Spacer(1,12))

    # Video/frame results
    elements.append(Paragraph('<b>7. Video Frame Results</b>', styles['Heading2']))
    if result and result.get('frame_results'):
        fr = result.get('frame_results')
        # If frame_results is a list of dicts, attempt to show a few rows
        if isinstance(fr, list):
            fr_data = [['Frame','Timestamp','Finding']]
            for idx, f in enumerate(fr[:50], start=1):
                ts = safe_text(f.get('timestamp') if isinstance(f, dict) else None)
                finding = safe_text(f.get('finding') if isinstance(f, dict) else None)
                fr_data.append([safe_text(f.get('frame') if isinstance(f, dict) else idx), ts, finding])
            frt = Table(fr_data, colWidths=[60,120,420])
            frt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.whitesmoke), ('INNERGRID',(0,0),(-1,-1),0.25,colors.grey), ('BOX',(0,0),(-1,-1),0.25,colors.grey)]))
            elements.append(fr_t:=frt)
        else:
            elements.append(Paragraph('Frame-level results present but not in table format. Refer to JSON result.', styles['Normal']))
    else:
        elements.append(Paragraph('No frame-level results available', styles['Normal']))
    elements.append(Spacer(1,12))

    # Model / Inference
    elements.append(Paragraph('<b>8. Model / Inference Information</b>', styles['Heading2']))
    meta = result.get('model_metadata') if result else None
    if meta:
        md = []
        for k in ('model_name','version','framework','inference_mode','device','processing_time'):
            if k in meta:
                md.append([k.replace('_',' ').title(), safe_text(meta.get(k))])
        mdt = Table(md, colWidths=[200,300])
        mdt.setStyle(TableStyle([('INNERGRID',(0,0),(-1,-1),0.25,colors.grey), ('BOX',(0,0),(-1,-1),0.25,colors.grey)]))
        elements.append(mdt)
    else:
        elements.append(Paragraph('No model metadata available', styles['Normal']))
    elements.append(Spacer(1,12))

    # Limitations
    elements.append(Paragraph('<b>9. Limitations</b>', styles['Heading2']))
    limitations_text = (
        'This report reflects the output of the configured DeepTruth inference pipeline. ' 
        'Absence of detected manipulation indicators does not constitute proof of authenticity. ' 
        'The analysis uses persisted results and did not re-run any model during report generation.'
    )
    elements.append(Paragraph(limitations_text, styles['Normal']))
    elements.append(Spacer(1,12))

    # Footer/meta
    elements.append(Paragraph('<b>10. Report Metadata</b>', styles['Heading2']))
    elements.append(Paragraph(f'Generated At: {safe_text(analysis.created_at.isoformat() if analysis.created_at else None)}', styles['Normal']))
    # Compose
    doc.build(elements)
    buffer.seek(0)
    return buffer.read()
