# imports:
import cv2
import numpy as np
import os
from collections import defaultdict
# image path

# Reading an image in default mode:
inputImage = cv2.imread("empty2.jpg")
path = '/mnt/c/Users/antho/Anthony Stuff/UCI Classes/EECS/EECS 159/output_images'

scalePercent = 50  
width = int(inputImage.shape[1] * scalePercent / 100)
height = int(inputImage.shape[0] * scalePercent / 100)


def resizeImage(image, path):
    # Resize image:
    scalePercent = 50  # percent of original size
    width = int(inputImage.shape[1] * scalePercent / 100)
    height = int(inputImage.shape[0] * scalePercent / 100)

    # New dimensions:
    dim = (width, height)

    # resize image
    resizedImage = cv2.resize(inputImage, dim, interpolation=cv2.INTER_AREA)
    return resizedImage

def thresholdImage(resizedImage, path):
    # Color conversion
    grayscaleImage = cv2.cvtColor(resizedImage, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(grayscaleImage, (9,9),0)
    cv2.imwrite(os.path.join(path, "blur.jpg") , blur)

    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
                                    cv2.THRESH_BINARY_INV, 7, 5)
    cv2.imwrite(os.path.join(path, "thresh.jpg") , thresh)

    # Fill in any large gaps between same wires/nodes
    kernel = np.ones((7, 7), np.uint8)
    dilation = cv2.dilate(thresh, kernel, iterations=5)
    erosion = cv2.erode(dilation, kernel, iterations=5)

    # This section might not be needed?
    kernel = np.ones((11,11),np.uint8)
    closing = cv2.morphologyEx(erosion, cv2.MORPH_CLOSE, kernel)

    skeleton = cv2.ximgproc.thinning(closing, None, 1)

    # Threshold the image so that white pixels get a value of 0 and
    # black pixels a value of 10:

    cv2.imwrite(os.path.join(path, "skel_ZS.jpg") , skeleton)
    cv2.imwrite(os.path.join(path, "gray3.jpg"), grayscaleImage)
    cv2.imwrite(os.path.join(path, "close.jpg"), closing)
    # Set the end-points kernel:
    kernel = np.uint8([[1, 1, 1],
                [1, 10, 1],
                [1, 1, 1]])

    # Convolve the image with the kernel:
    imgFiltered = cv2.filter2D(skeleton, -1, kernel)
    cv2.imwrite(os.path.join(path,"filtered.jpg"), imgFiltered)
    return imgFiltered


def getContours(imgFiltered):
        # Find contours of nodes
    contours ,hierarchy = cv2.findContours(imgFiltered, \
                                        cv2.RETR_EXTERNAL, \
                                        cv2.CHAIN_APPROX_SIMPLE)
    #cv.drawContours(image, contours, -1, (0, 255, 0), 3)

    # Creates a black image that is size original resized image
    out = np.zeros_like(imgFiltered)

    # Draws contours (large enough) onto black image
    for cnt in contours:
        area = cv2.contourArea(cnt)
        print(f'Contour area: {area}')
        if area < 80:
            continue
        cv2.drawContours(out, [cnt], 0, (255, 255, 255), 3)
    cv2.imwrite(os.path.join(path,"contours.jpg"), out)
    return out, contours
# Take in filtered image and find endpoints
def getEndPoints(imgFiltered, path):
    out, contours = getContours(imgFiltered)
    cont_thinned = cv2.ximgproc.thinning(out, None, 1)
    kernel = np.uint8([[1, 1, 1],
                [1, 10, 1],
                [1, 1, 1]])
    _, binaryImage = cv2.threshold(cont_thinned, 128, 10, cv2.THRESH_BINARY)
    contFiltered = cv2.filter2D(binaryImage, -1, kernel)
    cv2.imwrite(os.path.join(path,"cont_thinned.jpg"), cont_thinned)
    cv2.imwrite(os.path.join(path,"cont_filtered.jpg"), contFiltered)

    # Extract only the end-points pixels, those with
    # an intensity value of 110:
    endPointsMask = np.where(contFiltered == 110, 255, 0)
    cv2.imwrite(os.path.join(path, "endmask.jpg"), endPointsMask)
    # The above operation converted the image to 32-bit float,
    # convert back to 8-bit uint
    endPointsMask = endPointsMask.astype(np.uint8)
    return endPointsMask

def getCentroidsDict(endPointsMask):
    # RGB copy of this:
    rgbMask = endPointsMask.copy()
    rgbMask = cv2.cvtColor(rgbMask, cv2.COLOR_GRAY2BGR)

    # Create a copy of the mask for points processing:
    groupsMask = endPointsMask.copy()

    # Set kernel (structuring element) size:
    kernelSize = 3
    # Set operation iterations:
    opIterations = 3
    # Get the structuring element:
    maxKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernelSize, kernelSize))
    # Perform dilate:
    groupsMask = cv2.morphologyEx(groupsMask, cv2.MORPH_DILATE, maxKernel, \
                                None, None, opIterations, cv2.BORDER_REFLECT101)

    # Set the centroids Dictionary:
    centroidsDictionary = {}

    # Get centroids on the end points mask:
    totalComponents, output, stats, centroids = \
        cv2.connectedComponentsWithStats(endPointsMask, connectivity=8)

    # Count the blob labels with this:
    labelCounter = 1

    # Loop through the centroids, skipping the background (0):
    for c in range(1, len(centroids), 1):

        # Get the current centroids:
        cx = int(centroids[c][0])
        cy = int(centroids[c][1])

        # Get the pixel value on the groups mask:
        pixelValue = groupsMask[cy, cx]

        # If new value (255) there's no entry in the dictionary
        # Process a new key and value:
        if pixelValue == 255:

            # New key and values-> Centroid and Point Count:
            centroidsDictionary[labelCounter] = (cx, cy, 1)

            # Flood fill at centroid:
            cv2.floodFill(groupsMask, mask=None, \
                        seedPoint=(cx, cy), newVal=labelCounter)
            labelCounter += 1

        # Else, the label already exists and we must accumulate the
        # centroid and its count:
        else:

            # Get Value:
            (accumCx, accumCy, blobCount) = centroidsDictionary[pixelValue]

            # Accumulate value:
            accumCx = accumCx + cx
            accumCy = accumCy + cy
            blobCount += 1

            # Update dictionary entry:
            centroidsDictionary[pixelValue] = (accumCx, accumCy, blobCount)

            # Loop trough the dictionary and get the final centroid values:

    return centroidsDictionary

# takes in centroids dict, contours, and resized image
def get_node_Dict(centroidsDictionary, image, contours):
    nodeDictionary = {}
    endsCounter = 0
    for k in centroidsDictionary:
        # Get the value of the current key:
        (cx, cy, count) = centroidsDictionary[k]
        # Process combined points:
        if count != 1:
            cx = int(cx/count)
            cy = int(cy/count)
        # Draw circle at the centroid
        cv2.circle(image, (cx, cy), 8, (0, 0, 255), -1)
        #cv2.circle(out, (cx, cy), 1, (0, 0, 255), -1)


        # Check which node the endpoint belongs to 
        contourCounter = 0
        checkContour = np.zeros((height, width), dtype=np.uint8)

        for c in contours:
            if cv2.contourArea(c) > 80:
                cv2.drawContours(checkContour, [c], 0, (255, 255, 255), 3)
            color = checkContour[cy, cx]
            print(color)

            # If pixel at node end is white after drawing a contour, then point belongs to that node
            if color == 255:
                print(f'YES! WOOOOOO: {contourCounter}; x:{cx} y:{cy}')
                nodeDictionary[endsCounter] = contourCounter
                endsCounter += 1
                break

            contourCounter += 1

    return nodeDictionary

resizedImage = resizeImage(inputImage, path)
imgFiltered = thresholdImage(resizedImage, path)
endPointsMask = getEndPoints(imgFiltered, path)
centroidsDictionary = getCentroidsDict(endPointsMask)
out, contours = getContours(imgFiltered)
nodeDictionary = get_node_Dict(centroidsDictionary, resizedImage, contours)

#cv2.imwrite(os.path.join(path, "Centroids and Contour.jpg"), out)

cv2.imwrite(os.path.join(path, "Final Centroids.jpg"), resizedImage)

print(f'H: {height}, W: {width}')
print(centroidsDictionary)
print(nodeDictionary)

connectivityMap = {}
for key, value in nodeDictionary.items():
    connectivityMap.setdefault(value, set()).add(key)

print(connectivityMap)

