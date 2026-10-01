# NETRADEEP — Vitreo-Retinal AI Diagnostic Platform

#### Video Demo: <https://youtu.be/YtFL3EkdlII?si=BDl7kbuEouSoVvy9>

#### Description:

## Overview

NETRADEEP (Neural Triage for Retinal Analysis and Diabetic Eye Evaluation Platform) is a full-stack, production-grade Clinical Decision Support System (CDSS) designed to automate the detection and staging of Diabetic Retinopathy (DR) using deep learning. The system integrates a fine-tuned MobileNetV2 convolutional neural network, Grad-CAM explainability heatmaps, an SQLite-backed Electronic Health Record (EHR) engine, HbA1c blood report OCR parsing, and a real-time web portal accessible on desktop and mobile.

Diabetic Retinopathy is the leading cause of preventable blindness in working-age adults worldwide. In India and many low-resource settings, access to vitreo-retinal specialists is critically limited, especially at the Primary Health Center (PHC) level. NETRADEEP bridges this diagnostic gap by enabling any trained health worker to upload a retinal fundus photograph and receive an instant, explainable, clinically-staged diagnosis in under 1.2 seconds — all from a browser on any device.

## Project Structure and Files

### `project.py` (Root)
This is the mandatory CS50P entry point file. It contains `main()` and five top-level qualifying functions. Rather than duplicating the Streamlit UI logic (which requires a browser and heavy dependencies), `project.py` exposes a clean, standalone command-line interface for NETRADEEP's core clinical utility functions — the same underlying logic that powers the web platform. Functions include:

- **`get_stage_info(stage_index)`**: Given an integer 0–4, returns a dictionary containing the full clinical metadata for that ETDRS Diabetic Retinopathy stage — the formal name, short label, urgency level, pathological description, and associated symptoms. Raises a `ValueError` for any invalid index. This is the foundational lookup table for all staging logic in the system.

- **`classify_hba1c(hba1c_value)`**: Takes a HbA1c percentage value (a standard blood marker for long-term glycemic control) and returns one of three risk classifications: `"Normal"` (< 5.7%), `"Prediabetic"` (5.7–6.4%), or `"Diabetic"` (≥ 6.5%). Raises `ValueError` for non-positive or non-numeric inputs. This function is critical because HbA1c is a primary correlate of DR severity.

- **`format_patient_summary(name, age, stage_index, hba1c)`**: Combines patient demographic data, DR stage, and glycemic status into a single, formatted triage summary string. This is the output that would appear at the top of a clinical triage queue entry. Validates all inputs and raises `ValueError` on bad data. The name is automatically title-cased.

- **`extract_hba1c_from_text(text)`**: Uses regular expressions to extract the first numeric HbA1c value from an arbitrary clinical text string (e.g., raw OCR output from a scanned blood report image). Returns a float if found, or `None` otherwise. This enables the blood report OCR feature of the full platform.

- **`get_symptoms_for_stage(stage_index)`**: Returns the list of clinical symptoms associated with a given DR stage. Stage 0 (No DR) returns an empty list; proliferative stages return increasingly severe symptom lists. This drives the symptom panel in the diagnostic report generator.

The `main()` function provides a three-command CLI: `stage`, `hba1c`, and `summary`, allowing the platform's core logic to be exercised from the terminal without any heavy dependencies.

### `test_project.py` (Root)
Contains 36 pytest unit tests covering all five qualifying functions. Tests verify correct output for valid inputs, correct classification boundaries (especially the prediabetic threshold at 5.7% and diabetic at 6.5%), proper `ValueError` raising on invalid or edge-case inputs (negative values, wrong types, out-of-range indices), and regex extraction from multiline OCR text. All 36 tests pass (`pytest test_project.py -v`).

### `app/app.py`
The original Streamlit-based diagnostic front-end. Contains the full UI for image upload, CLAHE preprocessing, model inference, Grad-CAM visualization, EHR case saving, cohort analytics, and medical report generation. This is the rich interactive application used in actual clinical demonstrations.

### `app/server.py`
A Flask-based production web server that provides the same diagnostic capabilities as the Streamlit app through a session-authenticated web portal. Supports two roles: Admin (PIN 1396, full analytics dashboard) and User (mobile-optimized diagnostic interface). Exposed publicly via Cloudflare Tunnel for tele-medicine access.

### `app/database.py`
Manages the SQLite Electronic Health Record database (`clinical_records.db`). Implements `init_db()`, `save_case()`, `get_all_cases()`, and `get_case_by_id()`. Pre-populates with a realistic seven-patient demo cohort covering all five ETDRS severity classes.

### `app/gradcam.py`
Implements Gradient-weighted Class Activation Mapping (Grad-CAM) using `tf-keras-vis`. The `generate_gradcam_heatmap()` function extracts saliency maps from the final convolutional layer of the MobileNetV2 model, and `overlay_heatmap()` superimposes them onto the original fundus image using selectable colormaps (`jet`, `inferno`, `plasma`, `viridis`).

### `app/report_generator.py`
Generates complete, printable HTML medical discharge reports with doctor signature blocks, urgency banners, glycemic summaries, treatment recommendations per ETDRS stage, and patient demographic tables.

### `app/blood_report.py`
Uses `pytesseract` to perform OCR on scanned blood report images and extract HbA1c values via regex matching. Returns a formatted risk assessment string.

### `app/symptoms.py`
Legacy module that maps DR stage indices to symptom lists. The same logic is now embedded directly in `project.py`'s `STAGES` dictionary for the CS50P submission.

### `requirements.txt`
Lists all pip-installable dependencies: `tensorflow`, `streamlit`, `flask`, `opencv-python`, `numpy`, `pillow`, `pytesseract`, `tf-keras-vis`, `pandas`, `scikit-learn`, `matplotlib`, and `pytest`.

## Design Decisions

### Why a CLI entry point rather than just the Streamlit app?
CS50P requires a `project.py` with a `main()` function that runs standalone and has top-level functions testable with `pytest`. The Streamlit app starts a server and renders a browser UI — it cannot be meaningfully unit-tested with pytest. The design decision was to extract the core algorithmic logic (staging, HbA1c classification, text parsing, report formatting) into pure functions in `project.py` that are framework-agnostic, deterministic, and thus fully testable. The full web app remains in `app/` for practical clinical use.

### Why MobileNetV2 and not a larger model?
The system must run on standard laptops in rural PHC settings without GPU infrastructure. MobileNetV2 offers an excellent accuracy-to-latency trade-off (>91% validation accuracy on the 5-class APTOS/IDRiD dataset) while completing inference in under 1.2 seconds on a CPU. Larger models like ResNet50 or InceptionV3 would be clinically impractical in this context.

### Why SQLite instead of a cloud database?
Clinical patient data is highly sensitive. Storing it locally in an SQLite database avoids third-party data handling and compliance risks (HIPAA, DISHA) while keeping the system fully functional offline — critical for field deployment in areas with unreliable internet connectivity.

### Why Grad-CAM for explainability?
Clinicians cannot adopt "black box" AI decisions for medical triage. Grad-CAM produces class-discriminative saliency maps that highlight exactly which retinal regions (microaneurysms, hemorrhages, neovascularization sites) influenced the model's decision. This transforms the AI output from a bare label into a clinical teaching tool and builds physician trust.

## Team

| Member | Role |
|---|---|
| **Vedant Bagthariya** | Team Lead, AI Architecture, Model Training |
| **Rajdeepsinh Parmar** | Full-Stack Engineering, EHR Database |
| **Avanish Shiyal** | Computer Vision, Grad-CAM, Report Generator |

## How to Run

```bash
# CLI usage (no dependencies beyond Python stdlib + project.py)
python project.py stage 3
python project.py hba1c 7.4
python project.py summary "Vedant Bagthariya" 22 2 6.8

# Run all unit tests
pytest test_project.py -v

# Full Streamlit web app
cd pwp_project
streamlit run app/app.py

# Install all dependencies
pip install -r requirements.txt
```
