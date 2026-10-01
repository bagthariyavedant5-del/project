"""
test_project.py  — CS50P Final Project Tests
Tests for NETRADEEP's core utility functions in project.py

Run with:  pytest test_project.py -v
"""

import pytest
from project import (
    get_stage_info,
    classify_hba1c,
    format_patient_summary,
    extract_hba1c_from_text,
    get_symptoms_for_stage,
)


# ---------------------------------------------------------------------------
# Tests for get_stage_info
# ---------------------------------------------------------------------------

def test_get_stage_info_valid():
    """Valid indices 0-4 must return correct stage metadata dicts."""
    for i in range(5):
        info = get_stage_info(i)
        assert isinstance(info, dict)
        assert "name" in info
        assert "short" in info
        assert "urgency" in info
        assert "symptoms" in info

def test_get_stage_info_stage_zero():
    info = get_stage_info(0)
    assert info["short"] == "No DR"
    assert info["symptoms"] == []

def test_get_stage_info_stage_four():
    info = get_stage_info(4)
    assert info["short"] == "PDR"
    assert "CRITICAL" in info["urgency"]

def test_get_stage_info_invalid_negative():
    with pytest.raises(ValueError):
        get_stage_info(-1)

def test_get_stage_info_invalid_out_of_range():
    with pytest.raises(ValueError):
        get_stage_info(5)

def test_get_stage_info_invalid_string():
    with pytest.raises(ValueError):
        get_stage_info("2")

def test_get_stage_info_invalid_float():
    with pytest.raises(ValueError):
        get_stage_info(2.0)


# ---------------------------------------------------------------------------
# Tests for classify_hba1c
# ---------------------------------------------------------------------------

def test_classify_hba1c_normal():
    assert classify_hba1c(5.0) == "Normal"
    assert classify_hba1c(4.2) == "Normal"
    assert classify_hba1c(5.6) == "Normal"

def test_classify_hba1c_prediabetic():
    assert classify_hba1c(5.7) == "Prediabetic"
    assert classify_hba1c(6.0) == "Prediabetic"
    assert classify_hba1c(6.4) == "Prediabetic"

def test_classify_hba1c_diabetic():
    assert classify_hba1c(6.5) == "Diabetic"
    assert classify_hba1c(8.0) == "Diabetic"
    assert classify_hba1c(12.3) == "Diabetic"

def test_classify_hba1c_invalid_zero():
    with pytest.raises(ValueError):
        classify_hba1c(0)

def test_classify_hba1c_invalid_negative():
    with pytest.raises(ValueError):
        classify_hba1c(-1.0)

def test_classify_hba1c_invalid_string():
    with pytest.raises(ValueError):
        classify_hba1c("7.4")

def test_classify_hba1c_integer_input():
    """Integer inputs should also work (e.g. hba1c of 7)."""
    assert classify_hba1c(7) == "Diabetic"
    assert classify_hba1c(5) == "Normal"


# ---------------------------------------------------------------------------
# Tests for format_patient_summary
# ---------------------------------------------------------------------------

def test_format_patient_summary_basic():
    result = format_patient_summary("Vedant Bagthariya", 22, 0, 5.2)
    assert "Vedant Bagthariya" in result
    assert "Age 22" in result
    assert "No DR" in result
    assert "Normal" in result

def test_format_patient_summary_title_case():
    result = format_patient_summary("vedant bagthariya", 22, 0, 5.2)
    assert "Vedant Bagthariya" in result

def test_format_patient_summary_diabetic_stage():
    result = format_patient_summary("Rajesh Sharma", 58, 4, 10.4)
    assert "PDR" in result
    assert "Diabetic" in result
    assert "CRITICAL" in result

def test_format_patient_summary_prediabetic():
    result = format_patient_summary("Sunita Verma", 62, 1, 6.2)
    assert "Mild NPDR" in result
    assert "Prediabetic" in result

def test_format_patient_summary_invalid_name_empty():
    with pytest.raises(ValueError):
        format_patient_summary("", 30, 2, 7.0)

def test_format_patient_summary_invalid_name_type():
    with pytest.raises(ValueError):
        format_patient_summary(123, 30, 2, 7.0)

def test_format_patient_summary_invalid_age_zero():
    with pytest.raises(ValueError):
        format_patient_summary("Ananya", 0, 2, 7.0)

def test_format_patient_summary_invalid_age_negative():
    with pytest.raises(ValueError):
        format_patient_summary("Ananya", -5, 2, 7.0)

def test_format_patient_summary_invalid_stage():
    with pytest.raises(ValueError):
        format_patient_summary("Ananya", 45, 9, 7.0)


# ---------------------------------------------------------------------------
# Tests for extract_hba1c_from_text
# ---------------------------------------------------------------------------

def test_extract_hba1c_from_text_basic():
    assert extract_hba1c_from_text("HbA1c: 7.4") == 7.4

def test_extract_hba1c_from_text_case_insensitive():
    assert extract_hba1c_from_text("hba1c 6.2") == 6.2
    assert extract_hba1c_from_text("HBA1C 9.0") == 9.0

def test_extract_hba1c_from_text_with_equals():
    assert extract_hba1c_from_text("HbA1c=8.1") == 8.1

def test_extract_hba1c_from_text_not_found():
    assert extract_hba1c_from_text("Blood Glucose: 120 mg/dL") is None

def test_extract_hba1c_from_text_empty_string():
    assert extract_hba1c_from_text("") is None

def test_extract_hba1c_from_text_invalid_type():
    assert extract_hba1c_from_text(None) is None
    assert extract_hba1c_from_text(123) is None

def test_extract_hba1c_from_text_integer_value():
    assert extract_hba1c_from_text("HbA1c: 8") == 8.0

def test_extract_hba1c_from_text_multiline():
    text = "Patient Report\nFasting Glucose: 130\nHbA1c: 9.3\nLDL: 140"
    assert extract_hba1c_from_text(text) == 9.3


# ---------------------------------------------------------------------------
# Tests for get_symptoms_for_stage
# ---------------------------------------------------------------------------

def test_get_symptoms_for_stage_zero():
    assert get_symptoms_for_stage(0) == []

def test_get_symptoms_for_stage_one():
    syms = get_symptoms_for_stage(1)
    assert isinstance(syms, list)
    assert len(syms) >= 1

def test_get_symptoms_for_stage_four():
    syms = get_symptoms_for_stage(4)
    assert len(syms) >= 3
    assert any("vision" in s.lower() for s in syms)

def test_get_symptoms_for_stage_invalid():
    with pytest.raises(ValueError):
        get_symptoms_for_stage(10)

def test_get_symptoms_severity_increases():
    """More advanced stages should have more symptoms."""
    for i in range(1, 5):
        assert len(get_symptoms_for_stage(i)) >= len(get_symptoms_for_stage(0))
