import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "clinical_records.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patient_cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT NOT NULL,
        patient_name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        eye_examined TEXT,
        exam_timestamp TEXT,
        stage_idx INTEGER,
        stage_name TEXT,
        confidence REAL,
        hba1c REAL,
        urgency_level TEXT,
        doctor_notes TEXT
    )
    """)
    conn.commit()

    # Pre-populate with realistic demo cohort if empty
    cursor.execute("SELECT COUNT(*) FROM patient_cases")
    count = cursor.fetchone()[0]
    if count == 0:
        demo_cases = [
            ("PID-1042", "Rajesh Sharma", 58, "Male", "OD (Right)", "2026-03-24 10:15", 0, "No DR", 98.4, 5.4, "Routine Annual", "Clear fundus. Normal macula and optic disc."),
            ("PID-1088", "Sunita Verma", 62, "Female", "OS (Left)", "2026-03-24 11:30", 1, "Mild Non-Proliferative DR", 92.1, 6.8, "Moderate (6 Months)", "Isolated microaneurysms in temporal quadrant."),
            ("PID-1120", "Mohammed Farooq", 54, "Male", "OD (Right)", "2026-03-25 09:45", 2, "Moderate Non-Proliferative DR", 94.6, 7.9, "High (3 Months)", "Multiple cotton-wool spots and hard exudates."),
            ("PID-1156", "Ananya Deshmukh", 67, "Female", "OS (Left)", "2026-03-25 14:10", 3, "Severe Non-Proliferative DR", 91.8, 9.2, "Urgent (1 Month)", "Venous beading, severe intraretinal microvascular abnormalities."),
            ("PID-1194", "Vikramaditya Rao", 71, "Male", "OD (Right)", "2026-03-26 11:00", 4, "Proliferative DR", 97.2, 10.4, "CRITICAL (Immediate)", "Neovascularization of the disc (NVD), high risk of vitreous hemorrhage."),
            ("PID-1205", "Priya Nair", 49, "Female", "OD (Right)", "2026-03-26 15:20", 0, "No DR", 99.1, 5.2, "Routine Annual", "Healthy retinal vasculature."),
            ("PID-1232", "Harish Patel", 65, "Male", "OS (Left)", "2026-03-27 10:05", 2, "Moderate Non-Proliferative DR", 89.7, 8.1, "High (3 Months)", "Exudates approaching fovea. Advised OCT scan.")
        ]
        cursor.executemany("""
        INSERT INTO patient_cases (patient_id, patient_name, age, gender, eye_examined, exam_timestamp, stage_idx, stage_name, confidence, hba1c, urgency_level, doctor_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, demo_cases)
        conn.commit()
    conn.close()

def save_case(patient_id, patient_name, age, gender, eye_examined, stage_idx, stage_name, confidence, hba1c, urgency_level, doctor_notes):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute("""
    INSERT INTO patient_cases (patient_id, patient_name, age, gender, eye_examined, exam_timestamp, stage_idx, stage_name, confidence, hba1c, urgency_level, doctor_notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (patient_id, patient_name, age, gender, eye_examined, now_str, stage_idx, stage_name, confidence, hba1c, urgency_level, doctor_notes))
    conn.commit()
    case_id = cursor.lastrowid
    conn.close()
    return case_id

def get_all_cases():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, patient_id, patient_name, age, gender, eye_examined, exam_timestamp, stage_idx, stage_name, confidence, hba1c, urgency_level, doctor_notes
    FROM patient_cases
    ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_case_by_id(case_id):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, patient_id, patient_name, age, gender, eye_examined, exam_timestamp, stage_idx, stage_name, confidence, hba1c, urgency_level, doctor_notes
    FROM patient_cases WHERE id = ?
    """, (case_id,))
    row = cursor.fetchone()
    conn.close()
    return row
