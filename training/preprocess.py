import cv2
import numpy as np

def preprocess_image(img):
    # Resize to standard size
    img = cv2.resize(img, (224, 224))
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0)
    enhanced = clahe.apply(gray)
    
    # Merge back to 3 channels since MobileNetV2 expects 3 channels
    img = cv2.merge((enhanced, enhanced, enhanced))
    
    # Normalize pixel values
    img = img / 255.0
    
    return img
