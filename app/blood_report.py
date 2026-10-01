import pytesseract
from PIL import Image
import re

def extract_text(image):
    # Depending on OS, you might need to specify tesseract_cmd
    # pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    try:
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        return ""

def analyze_blood_report(image):
    text = extract_text(image)
    if not text:
        return "Could not read text from image. Ensure Tesseract OCR is installed."
    
    # Simple regex to find HbA1c value
    hba1c_pattern = r'HbA1c.*?(\d+\.\d+)'
    match = re.search(hba1c_pattern, text, re.IGNORECASE)
    
    if match:
        try:
            val = float(match.group(1))
            if val < 5.7:
                risk = "Normal"
            elif 5.7 <= val <= 6.4:
                risk = "Prediabetic"
            else:
                risk = "Diabetic"
            return f"Detected HbA1c: {val}% -> Risk Level: **{risk}**"
        except ValueError:
            pass
            
    return "Could not confidently detect HbA1c in the report. Please verify manually."
