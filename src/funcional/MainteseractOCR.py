import cv2
import numpy as np
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

img = cv2.imread("../data/testOCR.png")

text = pytesseract.image_to_string(img)
print(text)

cv2.imshow("Img",img)
cv2.waitKey(0)