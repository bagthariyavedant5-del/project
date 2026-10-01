import base64
from io import BytesIO
from PIL import Image

def image_to_base64(img):
    buffered = BytesIO()
    if isinstance(img, Image.Image):
        img.save(buffered, format="JPEG")
    else:
        pil_img = Image.fromarray(img)
        pil_img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

def generate_medical_report_html(patient_data, fundus_img, cam_img=None, enhanced_img=None):
    fundus_b64 = image_to_base64(fundus_img) if fundus_img is not None else ""
    cam_b64 = image_to_base64(cam_img) if cam_img is not None else ""
    enhanced_b64 = image_to_base64(enhanced_img) if enhanced_img is not None else ""

    stage_color = {
        0: "#059669", # Emerald
        1: "#0891b2", # Cyan
        2: "#d97706", # Amber
        3: "#ea580c", # Orange
        4: "#dc2626"  # Red
    }.get(patient_data.get("stage_idx", 0), "#0891b2")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>NETRADEEP Diagnostic Pathology Report - {patient_data.get('patient_id', 'REF-001')}</title>
<style>
    @media print {{
        body {{ margin: 0; padding: 15px; font-size: 11pt; background: #fff !important; color: #000 !important; }}
        .no-print {{ display: none !important; }}
        .report-card {{ border: 1px solid #ccc !important; box-shadow: none !important; }}
    }}
    body {{
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        background: #f0fdfa;
        margin: 0;
        padding: 40px 20px;
        color: #0f172a;
    }}
    .report-container {{
        max-width: 900px;
        margin: 0 auto;
        background: #ffffff;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(8, 145, 178, 0.1);
        padding: 40px 48px;
        border-top: 8px solid #0891b2;
        border-left: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
    }}
    .header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 20px;
        margin-bottom: 25px;
    }}
    .institute-title {{
        font-size: 24px;
        font-weight: 800;
        color: #0891b2;
        letter-spacing: -0.5px;
    }}
    .institute-sub {{
        font-size: 13px;
        color: #64748b;
        margin-top: 4px;
    }}
    .badge {{
        background: #ecfeff;
        border: 1px solid #a5f3fc;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 700;
        color: #0e7490;
    }}
    .patient-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        background: #f8fafc;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 28px;
    }}
    .patient-field label {{
        display: block;
        font-size: 11px;
        text-transform: uppercase;
        color: #64748b;
        font-weight: 700;
        margin-bottom: 4px;
    }}
    .patient-field span {{
        font-size: 15px;
        font-weight: 600;
        color: #0f172a;
    }}
    .diag-box {{
        background: #f8fafc;
        border: 1px solid {stage_color};
        border-left: 6px solid {stage_color};
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 28px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .diag-stage {{
        font-size: 20px;
        font-weight: 800;
        color: #0f172a;
    }}
    .diag-conf {{
        font-size: 13px;
        color: #475569;
        margin-top: 4px;
    }}
    .urgency-badge {{
        background: {stage_color};
        color: #ffffff;
        padding: 8px 18px;
        border-radius: 30px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }}
    .image-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin-bottom: 28px;
    }}
    .image-card {{
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        overflow: hidden;
        text-align: center;
        background: #000;
    }}
    .image-card img {{
        width: 100%;
        height: 180px;
        object-fit: cover;
        display: block;
    }}
    .image-card .caption {{
        background: #f8fafc;
        padding: 8px;
        font-size: 12px;
        font-weight: 600;
        color: #475569;
        border-top: 1px solid #e2e8f0;
    }}
    .section-title {{
        font-size: 15px;
        font-weight: 700;
        color: #0891b2;
        margin-bottom: 12px;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .clinical-findings {{
        font-size: 13.5px;
        line-height: 1.6;
        color: #334155;
        margin-bottom: 25px;
        background: #f8fafc;
        padding: 16px 20px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
    }}
    .team-badge {{
        font-size: 12px;
        color: #64748b;
        background: #f1f5f9;
        padding: 10px 16px;
        border-radius: 8px;
        margin-top: 20px;
        text-align: center;
    }}
    .signatures {{
        display: flex;
        justify-content: space-between;
        margin-top: 35px;
        border-top: 2px dashed #cbd5e1;
        padding-top: 20px;
    }}
    .sig-block {{
        width: 260px;
        text-align: center;
    }}
    .sig-line {{
        border-bottom: 1px solid #0f172a;
        height: 35px;
        margin-bottom: 6px;
    }}
    .sig-name {{
        font-size: 13px;
        font-weight: 700;
        color: #0f172a;
    }}
    .sig-title {{
        font-size: 11px;
        color: #64748b;
    }}
    .btn-bar {{
        text-align: center;
        margin-top: 25px;
    }}
    .print-btn {{
        background: #0891b2;
        color: #ffffff;
        border: none;
        padding: 12px 32px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 4px 14px rgba(8, 145, 178, 0.3);
    }}
    .print-btn:hover {{
        background: #0e7490;
    }}
</style>
</head>
<body>

<div class="report-container">
    <div class="header">
        <div>
            <div class="institute-title">NETRADEEP™ Vitreo-Retinal Diagnostic Institute</div>
            <div class="institute-sub">Center for Advanced Tele-Ophthalmology & Deep Learning Diagnostics</div>
        </div>
        <div class="badge">
            CASE ID: {patient_data.get('patient_id', 'REF-001')}
        </div>
    </div>

    <div class="patient-grid">
        <div class="patient-field">
            <label>Patient Name</label>
            <span>{patient_data.get('patient_name', 'Anonymous Patient')}</span>
        </div>
        <div class="patient-field">
            <label>Age / Gender</label>
            <span>{patient_data.get('age', '--')} yrs / {patient_data.get('gender', '--')}</span>
        </div>
        <div class="patient-field">
            <label>Examined Eye</label>
            <span>{patient_data.get('eye_examined', 'OD (Right)')}</span>
        </div>
        <div class="patient-field">
            <label>Date of Examination</label>
            <span>{patient_data.get('exam_timestamp', 'Current Session')}</span>
        </div>
    </div>

    <div class="diag-box">
        <div>
            <div class="diag-stage">ETDRS Staging: {patient_data.get('stage_name', 'Pending')}</div>
            <div class="diag-conf">MobileNetV2 Deep Learning Confidence: <strong>{patient_data.get('confidence', 0):.2f}%</strong> | Glycemic Index (HbA1c): <strong>{patient_data.get('hba1c', 'N/A')}%</strong></div>
        </div>
        <div class="urgency-badge">
            {patient_data.get('urgency_level', 'Routine Review')}
        </div>
    </div>

    <div class="section-title">Tri-Modal Imaging & Explainable AI (XAI) Saliency</div>
    <div class="image-grid">
        <div class="image-card">
            <img src="data:image/jpeg;base64,{fundus_b64}" alt="Fundus Scan">
            <div class="caption">1. High-Resolution Fundus Retinograph</div>
        </div>
        <div class="image-card">
            <img src="data:image/jpeg;base64,{enhanced_b64}" alt="CLAHE Vessels">
            <div class="caption">2. CLAHE Optical Micro-Vessel Filter</div>
        </div>
        <div class="image-card">
            <img src="data:image/jpeg;base64,{cam_b64}" alt="Grad-CAM Heatmap">
            <div class="caption">3. Grad-CAM XAI Lesion Saliency</div>
        </div>
    </div>

    <div class="section-title">Clinical Pathological Assessment & Recommendations</div>
    <div class="clinical-findings">
        <p><strong>Pathological Observations:</strong> {patient_data.get('doctor_notes', 'Comprehensive retinal vascular evaluation performed by Netradeep neural network.')}</p>
        <p><strong>Clinical Follow-up Protocol:</strong> {patient_data.get('urgency_level', 'Routine examination')} follow-up scheduled. Glycemic targets should be strictly maintained under HbA1c &lt; 7.0%. Regular blood pressure and lipid profile monitoring indicated.</p>
    </div>

    <div class="signatures">
        <div class="sig-block">
            <div class="sig-line"></div>
            <div class="sig-name">Vedant Bagthariya</div>
            <div class="sig-title">Team Leader & Lead AI Architect | NETRADEEP™</div>
        </div>
        <div class="sig-block">
            <div class="sig-line"></div>
            <div class="sig-name">Dr. R. K. Mukherjee, MD (Ophthal)</div>
            <div class="sig-title">Senior Vitreo-Retinal Consultant</div>
        </div>
    </div>

    <div class="team-badge">
        <strong>Clinical Engineering Directorate:</strong> Vedant Bagthariya (Team Lead & Chief AI Architect) • Rajdeepsinh Parmar (Systems Engineer) • Avanish Shiyal (Computer Vision Specialist) | NETRADEEP Diagnostic Platform
    </div>

    <div class="btn-bar no-print">
        <button class="print-btn" onclick="window.print()">PRINT / SAVE ACCREDITED CLINICAL REPORT (PDF)</button>
    </div>
</div>

</body>
</html>"""
    return html
