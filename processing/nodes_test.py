import cv2 as cv
import numpy as np
import os
from pylsd import lsd


path = '/mnt/c/Users/antho/Anthony Stuff/UCI Classes/EECS/EECS 159/nodes_out'
image = cv.imread('empty4.jpg')
# Resize image to maintain consistency and reduce noise (Refer to document)
image = cv.resize(image, (750, 1000))

# Thresholding operation
gray =cv.cvtColor(image, cv.COLOR_BGR2GRAY)
img = cv.GaussianBlur(gray, (9,9),0)
thresh = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 7, 5)

# Fill in any large gaps between same wires/nodes
kernel = np.ones((7, 7), np.uint8)
dilation = cv.dilate(thresh, kernel, iterations=5)
erosion = cv.erode(dilation, kernel, iterations=5)

# Fill in any gaps after thresholding and dilation and erosion process
kernel = np.ones((11,11), np.uint8)
closing = cv.morphologyEx(erosion, cv.MORPH_CLOSE, kernel)
# Thinning/Skeletonization Process using Zhang-Suen algorithm
thinned = cv.ximgproc.thinning(closing)
# Thin_cpy = set all 
thin_cpy = thinned.copy()
thin_cpy[thin_cpy != 0] = 1
thin_cpy = np.uint8(thin_cpy)
# Convolve the image with the kernel:
kernel = np.uint8([[1, 1, 1],
              [1, 10, 1],
              [1, 1, 1]])
imgFiltered2 = cv.filter2D(thin_cpy, -1, kernel)
imgFiltered = cv.filter2D(thinned, -1, kernel)

# Find contours of nodes
contours ,hierarchy = cv.findContours(imgFiltered.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
#cv.drawContours(image, contours, -1, (0, 255, 0), 3)

# Creates a black image that is size original resized image
out = np.zeros_like(img)

# Draws contours (large enough) onto black image
for cnt in contours:
    area = cv.contourArea(cnt)
    print(f'Contour area: {area}')
    if area < 80:
        continue
    cv.drawContours(out, [cnt], 0, (255, 255, 255), 3)

cont_thinned = cv.ximgproc.thinning(out, None, 1)

_, binaryImage = cv.threshold(cont_thinned, 128, 10, cv.THRESH_BINARY)
contFiltered = cv.filter2D(binaryImage, -1, kernel)

nodemask = np.where(contFiltered == 110, 255, 0)
nodemask = nodemask.astype(np.uint8)




# Create jpgs showing transformations on orignal input image
cv.imwrite(os.path.join(path, 'node_contours.jpg'), out)
cv.imwrite(os.path.join(path, 'node_dilation.jpg'), dilation)
cv.imwrite(os.path.join(path, 'node_erosion.jpg'), erosion)
cv.imwrite(os.path.join(path, 'node_thresh.jpg'), thresh)
cv.imwrite(os.path.join(path, 'node_thin.jpg'), thinned)
cv.imwrite(os.path.join(path, 'node_close.jpg'), closing)
cv.imwrite(os.path.join(path, 'node_filtered.jpg'), imgFiltered)
cv.imwrite(os.path.join(path, 'node_filtered2.jpg'), imgFiltered2)
cv.imwrite(os.path.join(path, 'node_cont_thinned.jpg'), cont_thinned)
cv.imwrite(os.path.join(path, 'node_mask.jpg'), nodemask)
cv.imwrite(os.path.join(path, 'cont_filtered.jpg'), contFiltered)
