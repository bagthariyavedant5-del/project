"""
NETRADEEP - Vitreo-Retinal AI Diagnostic Platform
CS50P Final Project
Author: Vedant Bagthariya
GitHub: vedantbag | edX: vedantbag
Surat, Gujarat, India
"""

import sys
import os
import re

APP_DIR = os.path.join(os.path.dirname(__file__), "app")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

# ---------------------------------------------------------------------------
# ETDRS 5-Stage Classification Reference Table
# ---------------------------------------------------------------------------
STAGES = {
    0: {
        "name": "No Diabetic Retinopathy",
        "short": "No DR",
        "urgency": "Routine Annual",
        "description": "Normal fundus. Healthy optic disc and macula.",
        "symptoms": [],
    },
    1: {
        "name": "Mild Non-Proliferative DR",
        "short": "Mild NPDR",
        "urgency": "Moderate (6 Months)",
        "description": "Presence of microaneurysms only.",
        "symptoms": ["Mild blurred vision (rare)"],
    },
    2: {
        "name": "Moderate Non-Proliferative DR",
        "short": "Moderate NPDR",
        "urgency": "High (3 Months)",
        "description": "Microaneurysms, blot hemorrhages, hard exudates, cotton wool spots.",
        "symptoms": ["Blurred vision", "Dark spots (floaters)"],
    },
    3: {
        "name": "Severe Non-Proliferative DR",
        "short": "Severe NPDR",
        "urgency": "Urgent (1 Month)",
        "description": "4-2-1 Rule: >20 intraretinal hemorrhages in all 4 quadrants.",
        "symptoms": ["Blurred vision", "Dark spots", "Impaired color vision", "Night vision problems"],
    },
    4: {
        "name": "Proliferative Diabetic Retinopathy",
        "short": "PDR",
        "urgency": "CRITICAL (Immediate)",
        "description": "Neovascularization of disc; high risk of vitreous hemorrhage.",
        "symptoms": ["Severe blurred vision", "Vision loss", "Severely impaired night vision", "Dark/empty areas in vision"],
    },
}


def get_stage_info(stage_index):
    """
    Return clinical metadata for a given ETDRS stage index (0-4).

    Args:
        stage_index: Integer 0-4 representing DR severity class.

    Returns:
        dict with keys: name, short, urgency, description, symptoms.

    Raises:
        ValueError: If stage_index is not an integer in range 0-4.
    """
    if not isinstance(stage_index, int) or stage_index not in range(5):
        raise ValueError(
            f"Invalid stage index: {stage_index!r}. Must be an integer 0-4."
        )
    return STAGES[stage_index]


def classify_hba1c(hba1c_value):
    """
    Classify a HbA1c percentage into a glycemic risk category.

    Args:
        hba1c_value: Positive float/int representing HbA1c (e.g. 6.5).

    Returns:
        String: "Normal", "Prediabetic", or "Diabetic".

    Raises:
        ValueError: If value is not a positive number.
    """
    if not isinstance(hba1c_value, (int, float)) or hba1c_value <= 0:
        raise ValueError(
            f"HbA1c must be a positive numeric value, got: {hba1c_value!r}"
        )
    if hba1c_value < 5.7:
        return "Normal"
    elif hba1c_value <= 6.4:
        return "Prediabetic"
    else:
        return "Diabetic"


def format_patient_summary(name, age, stage_index, hba1c):
    """
    Produce a formatted single-line triage summary for a patient.

    Args:
        name:        Patient full name (non-empty string).
        age:         Patient age (positive integer).
        stage_index: ETDRS DR stage 0-4 (integer).
        hba1c:       HbA1c percentage value (positive float/int).

    Returns:
        Formatted summary string.

    Raises:
        ValueError: On any invalid input.
    """
    if not name or not isinstance(name, str):
        raise ValueError("Patient name must be a non-empty string.")
    if not isinstance(age, int) or age <= 0:
        raise ValueError(f"Age must be a positive integer, got: {age!r}")

    stage = get_stage_info(stage_index)
    glycemia = classify_hba1c(hba1c)

    return (
        f"Patient: {name.strip().title()}, Age {age} | "
        f"DR Stage: {stage['short']} | "
        f"Urgency: {stage['urgency']} | "
        f"HbA1c: {hba1c:.1f}% ({glycemia})"
    )


def extract_hba1c_from_text(text):
    """
    Extract the first HbA1c numeric value from raw OCR or clinical text.

    Handles patterns like:
        "HbA1c: 7.4", "HbA1c 8.2", "hba1c=9.0"

    Args:
        text: Raw string (e.g. from OCR of a blood report image).

    Returns:
        Float value if found, else None.
    """
    if not isinstance(text, str):
        return None
    pattern = r"hba1c[^\d]*(\d+\.?\d*)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


def get_symptoms_for_stage(stage_index):
    """
    Return a list of clinical symptoms for a given DR stage index.

    Args:
        stage_index: Integer 0-4.

    Returns:
        List of symptom strings (empty list for stage 0 / No DR).

    Raises:
        ValueError: If stage_index is invalid.
    """
    return get_stage_info(stage_index)["symptoms"]


def main():
    """
    CLI entry point for NETRADEEP triage utilities.

    Usage:
        python project.py stage <0-4>
        python project.py hba1c <value>
        python project.py summary <name> <age> <stage> <hba1c>
    """
    args = sys.argv[1:]

    if not args:
        print("NETRADEEP - Vitreo-Retinal AI Diagnostic Platform")
        print("")
        print("Usage:")
        print("  python project.py stage <0-4>")
        print("  python project.py hba1c <value>")
        print("  python project.py summary <name> <age> <stage> <hba1c>")
        return

    command = args[0].lower()

    if command == "stage":
        if len(args) < 2:
            sys.exit("Error: provide a stage index (0-4).")
        try:
            idx = int(args[1])
            info = get_stage_info(idx)
            print(f"\nStage {idx}: {info['name']}")
            print(f"  Urgency    : {info['urgency']}")
            print(f"  Description: {info['description']}")
            syms = info["symptoms"]
            print(f"  Symptoms   : {', '.join(syms) if syms else 'None (normal)'}")
        except ValueError as e:
            sys.exit(f"Error: {e}")

    elif command == "hba1c":
        if len(args) < 2:
            sys.exit("Error: provide a HbA1c value (e.g. 7.4).")
        try:
            val = float(args[1])
            result = classify_hba1c(val)
            print(f"\nHbA1c {val:.1f}% => {result}")
        except ValueError as e:
            sys.exit(f"Error: {e}")

    elif command == "summary":
        if len(args) < 5:
            sys.exit('Error: provide <name> <age> <stage> <hba1c>. '
                     'Wrap name in quotes if it has spaces.')
        try:
            name = args[1]
            age = int(args[2])
            stage = int(args[3])
            hba1c = float(args[4])
            print("\n" + format_patient_summary(name, age, stage, hba1c))
        except ValueError as e:
            sys.exit(f"Error: {e}")

    else:
        sys.exit(f"Unknown command: {command!r}. Use stage / hba1c / summary.")


if __name__ == "__main__":
    main()
