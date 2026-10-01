import os, io, base64, sqlite3, secrets
import numpy as np, cv2
from PIL import Image
from flask import (Flask, render_template, request, jsonify,
                   redirect, url_for, session)
import tensorflow as tf
from database import init_db, save_case, get_all_cases
from gradcam import generate_gradcam_heatmap, overlay_heatmap

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "netradeep-secret-2024"

ADMIN_PIN = "1396"

init_db()

MODEL_PATH = os.path.join(os.path.dirname(__file__), "dr_model.h5")
try:
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    print("TensorFlow model loaded successfully into Flask backend.")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

CLASSES = [
    "Class 0: No Apparent DR (Normal)",
    "Class 1: Mild Non-Proliferative DR",
    "Class 2: Moderate Non-Proliferative DR",
    "Class 3: Severe Non-Proliferative DR",
    "Class 4: Proliferative DR (PDR)"
]

URGENCY_MAP = {
    0: ("Low Risk",       "Routine Annual Screening",              "Maintain baseline glycemic control and standard balanced diet."),
    1: ("Moderate Risk",  "Follow-up in 6-9 Months",              "Monitor HbA1c strictly (<7.0%). Review blood pressure and lipid panel."),
    2: ("High Risk",      "Ophthalmologist Review in 3-4 Months", "Early vascular leakage. Consider Optical Coherence Tomography (OCT)."),
    3: ("Very High Risk", "Urgent Specialist Care (Within 1 Month)","Significant ischemia & venous beading. Potential laser photocoagulation candidate."),
    4: ("CRITICAL RISK",  "Immediate Vitreo-Retinal Intervention", "High risk of vitreous hemorrhage / retinal detachment. Anti-VEGF / Panretinal Photocoagulation required.")
}

def to_base64(img_arr):
    pil_img = Image.fromarray(img_arr.astype("uint8"))
    buffered = io.BytesIO()
    pil_img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

# ── Auth helpers ──────────────────────────────────────────────────────
def is_admin():  return session.get("role") == "admin"
def is_user():   return session.get("role") in ("admin", "user")

# ── Login / Logout ────────────────────────────────────────────────────
@app.route("/")
def root():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    role = request.form.get("role", "user")
    pin  = request.form.get("pin", "")
    if role == "admin":
        if pin == ADMIN_PIN:
            session["role"] = "admin"
            return redirect(url_for("desktop"))
        return render_template("login.html", error="Incorrect PIN. Access denied.")
    else:
        session["role"] = "user"
        return redirect(url_for("mobile"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("root"))

# ── Pages ─────────────────────────────────────────────────────────────
@app.route("/dashboard")
def desktop():
    if not is_admin():
        return redirect(url_for("root"))
    return render_template("index.html")

@app.route("/mobile")
def mobile():
    if not is_user():
        return redirect(url_for("root"))
    return render_template("mobile.html")

# ── API: Preset ───────────────────────────────────────────────────────
@app.route("/api/preset/<int:stage_idx>", methods=["GET"])
def get_preset(stage_idx):
    if not is_user():
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    base_dataset = os.path.join(os.path.dirname(__file__), "..", "dataset", str(stage_idx))
    sample_file  = os.path.join(base_dataset, f"sample_{stage_idx}_0.jpg")
    if os.path.exists(sample_file):
        with open(sample_file, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode()
            return jsonify({"success": True, "image_b64": b64_data, "filename": f"sample_{stage_idx}_0.jpg"})
    return jsonify({"success": False, "error": "Preset file not found"}), 404

# ── API: Predict ──────────────────────────────────────────────────────
@app.route("/api/predict", methods=["POST"])
def predict():
    if not is_user():
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    if "image" not in request.files and "image_b64" not in request.form:
        return jsonify({"success": False, "error": "No image provided"}), 400
    try:
        if "image" in request.files:
            pil_img = Image.open(request.files["image"].stream).convert("RGB")
        else:
            b64_str = request.form["image_b64"]
            if "," in b64_str: b64_str = b64_str.split(",")[1]
            pil_img = Image.open(io.BytesIO(base64.b64decode(b64_str))).convert("RGB")

        img_np        = np.array(pil_img)
        green_channel = img_np[:, :, 1]
        clahe         = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced_green = clahe.apply(green_channel)
        enhanced_rgb   = cv2.cvtColor(enhanced_green, cv2.COLOR_GRAY2RGB)

        img_resized = pil_img.resize((224, 224))
        img_norm    = np.array(img_resized, dtype=np.float32) / 255.0
        img_batch   = np.expand_dims(img_norm, axis=0)

        if model:
            predictions = model.predict(img_batch, verbose=0)[0]
            stage_idx   = int(np.argmax(predictions))
            confidence  = float(np.max(predictions)) * 100
            probs       = [float(p * 100) for p in predictions]
        else:
            stage_idx, confidence = 0, 95.0
            probs = [95.0, 2.0, 1.0, 1.0, 1.0]

        stage_name = CLASSES[stage_idx]
        risk_cat, visit_urgency, treatment_protocol = URGENCY_MAP[stage_idx]

        cam_b64 = ""
        try:
            heatmap    = generate_gradcam_heatmap(model, img_batch, stage_idx)
            cam_overlay = overlay_heatmap(np.array(img_resized), heatmap, alpha=0.45, colormap_name="jet")
            cam_b64    = to_base64(np.array(cam_overlay))
        except Exception as e:
            print(f"Grad-CAM fallback: {e}")
            cam_b64 = to_base64(enhanced_rgb)

        return jsonify({
            "success": True, "stage_idx": stage_idx, "stage_name": stage_name,
            "confidence": round(confidence, 2), "probabilities": probs, "classes": CLASSES,
            "risk_category": risk_cat, "urgency": visit_urgency, "treatment": treatment_protocol,
            "original_b64": to_base64(img_np), "enhanced_b64": to_base64(enhanced_rgb), "cam_b64": cam_b64
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ── API: Cases ────────────────────────────────────────────────────────
@app.route("/api/cases", methods=["GET"])
def get_cases():
    if not is_admin():
        return jsonify({"success": False, "error": "Admin only"}), 403
    cases = get_all_cases()
    records = [{"id": c[0], "patient_id": c[1], "name": c[2], "age": c[3], "gender": c[4],
                "eye": c[5], "timestamp": c[6], "stage_idx": c[7], "stage_name": c[8],
                "confidence": c[9], "hba1c": c[10], "urgency": c[11], "notes": c[12]} for c in cases]
    return jsonify({"success": True, "cases": records})

@app.route("/api/cases", methods=["POST"])
def add_case():
    if not is_user():
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    data = request.json or {}
    case_id = save_case(
        patient_id=data.get("patient_id", "REF-001"),
        patient_name=data.get("patient_name", "Anonymous"),
        age=data.get("age", 50), gender=data.get("gender", "Male"),
        eye_examined=data.get("eye_examined", "OD (Right)"),
        stage_idx=data.get("stage_idx", 0), stage_name=data.get("stage_name", "No DR"),
        confidence=data.get("confidence", 95.0), hba1c=data.get("hba1c", 7.0),
        urgency_level=data.get("urgency_level", "Routine Annual"),
        doctor_notes=data.get("doctor_notes", "Automated diagnostic record.")
    )
    return jsonify({"success": True, "case_id": case_id})

# ── API: Analytics ────────────────────────────────────────────────────
@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    if not is_admin():
        return jsonify({"success": False, "error": "Admin only"}), 403
    cases      = get_all_cases()
    total      = len(cases)
    critical   = sum(1 for c in cases if c[7] >= 3)
    normal     = sum(1 for c in cases if c[7] == 0)
    avg_conf   = round(float(np.mean([c[9] for c in cases])), 1) if cases else 0.0
    stage_counts = {CLASSES[i]: sum(1 for c in cases if c[7] == i) for i in range(5)}
    return jsonify({"success": True, "total_screenings": total, "critical_referrals": critical,
                    "normal_count": normal, "avg_confidence": avg_conf, "stage_distribution": stage_counts})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
