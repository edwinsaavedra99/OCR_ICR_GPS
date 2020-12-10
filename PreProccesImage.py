import sys
import numpy as np
from cv2 import *
import time
import os
import threading
#import pytesseract
import imutils

#direccion donde esta tesseract
#pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\tesseract'



def preProces(img_path):
    # Read image using opencv
    img = cv2.imread(img_path)
    # Extract the file name without the file extension
    file_name = os.path.basename(img_path).split('.')[0]
    file_name = file_name.split()[0]
    # Create a directory for outputs
    output_path = os.path.join('out', "ocr")
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    # Rescale the image, if needed.
    img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    # Converting to gray scale
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Removing Shadows
    rgb_planes = cv2.split(img)
    result_planes = []
    result_norm_planes = []
    for plane in rgb_planes:
        dilated_img = cv2.dilate(plane, np.ones((7, 7), np.uint8))
        bg_img = cv2.medianBlur(dilated_img, 21)
        diff_img = 255 - cv2.absdiff(plane, bg_img)
        result_planes.append(diff_img)
    img = cv2.merge(result_planes)

    # Apply dilation and erosion to remove some noise
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)  # increases the white region in the image
    img = cv2.erode(img, kernel, iterations=1)  # erodes away the boundaries of foreground object

    # Apply blur to smooth out the edges
    # img = cv2.GaussianBlur(img, (5, 5), 0)

    # Apply threshold to get image with only b&w (binarization)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # Save the filtered image in the output directory
    save_path = os.path.join(output_path, file_name + ".png")
    cv2.imwrite(save_path, img)
    # read
    img = cv2.imread('out/ocr/0.png', cv2.IMREAD_GRAYSCALE)

    # increase contrast
    pxmin = np.min(img)
    pxmax = np.max(img)
    imgContrast = (img - pxmin) / (pxmax - pxmin) * 255

    # increase line width
    kernel = np.ones((3, 3), np.uint8)
    imgMorph = cv2.erode(imgContrast, kernel, iterations=1)

    # write
    cv2.imwrite('out/ocr/0.png', imgMorph)
    # Recognize text with tesseract for python
    #result = pytesseract.image_to_string(img, lang="eng")
    #return result

    #aqui va la direccion de la imagen a imprimir
    #s = get_string("direccion de la imagen")
    #t = s.split(sep='\n')
    #for s in t:
    #    print(s)


preProces('data_in/0.png')