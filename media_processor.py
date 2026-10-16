import cv2
import numpy as np
from PIL import Image

def enhance_image(pil_image):
    """Làm rõ chữ, khử nhiễu và tăng độ tương phản cho ảnh bài tập"""
    open_cv_image = np.array(pil_image.convert('RGB'))
    open_cv_image = open_cv_image[:, :, ::-1].copy() # Convert RGB to BGR

    # 1. Chuyển sang ảnh xám
    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)

    # 2. Tăng độ tương phản bằng CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced_gray = clahe.apply(gray)

    # 3. Khử nhiễu nhẹ
    denoised = cv2.fastNlMeansDenoising(enhanced_gray, h=10)

    # Chuyển lại về dạng PIL Image
    final_img = Image.fromarray(denoised)
    return final_img
