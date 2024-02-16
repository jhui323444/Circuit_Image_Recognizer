import cv2 as cv
import numpy as np
import os
from pylsd import lsd
from endpoint import getContours, resizeImage, thresholdImage, get_node_Dict, \
getCentroidsDict, getEndPoints
image = cv.imread('test_circuit.jpg')
os.chdir("..")
os.chdir("output_images")
path = os.getcwd()

# Resize image to maintain consistency and reduce noise (Refer to document)
image, width, height = resizeImage(image, path, 25)
thresh = thresholdImage(image, path)
mask = getEndPoints(thresh, path)
centroidDict = getCentroidsDict(mask)
out, contours = getContours(thresh, path)
nodeDict, points = get_node_Dict(centroidDict, image, contours, width, height)
print(points)

allh = {}
allv = {}

def calculateLineCoords(horizontal, vertical, x1, y1, x2, y2, mode):
    if mode == 1:
        x = (x1 + x2)/2
        if int(x) not in vertical.keys():
            exists = False
            for xval in vertical.keys():
                if abs(int(x)-xval) <= 15:
                    # Take minimum/,maximum y coords from current line
                    # (either side) and compare to current min/max saved for
                    # x coordinate 
                    vertical[xval][0] = min(vertical[xval][0], \
                                            min(int(y1),int(y2)))
                    vertical[xval][1] = max(vertical[xval][1], \
                                            max(int(y1),int(y2)))
                    exists = True
                    break
            if exists == False:
                vertical[int(x)] = [min(int(y1),int(y2)), \
                                    max(int(y1),int(y2))]
    elif mode == 2:
        y = (y1 + y2)/2
        if int(y) not in horizontal.keys():
            exists = False
            for yval in horizontal.keys():
                if abs(int(y)-yval) <= 15:
                    # Take minimum/,maximum x coords from current line
                    # (either side) and compare to current min/max saved for
                    # y coordinate 
                    horizontal[yval][0] = min(horizontal[yval][0], \
                                                min(int(x1),int(x2)))
                    horizontal[yval][1] = max(horizontal[yval][1], \
                                                max(int(x1),int(x2)))
                    exists = True
                    break
            if exists == False:
                horizontal[int(y)] = [min(int(x1),int(x2)), \
                                        max(int(x1),int(x2))]   
    
def findLines(segments, allv, allh):
    horizontal = {}
    vertical = {}

    for line in segments:
        x1,y1,x2,y2,w = line
        angle = np.abs(np.rad2deg(np.arctan2(y1 - y2, x1 - x2)))

        if(angle < 105 and angle > 75):
            calculateLineCoords(horizontal, vertical, x1, y1, x2, y2, 1)
        else: 
            calculateLineCoords(horizontal, vertical, x1, y1, x2, y2, 2)
        
    allh.update(horizontal)
    allv.update(vertical)


for cnt in contours:
    blank = np.zeros_like(thresh)
    cv.drawContours(blank, [cnt], 0, (255,255,255), -1)
    segments = lsd(blank, scale =.4)
    findLines(segments, allv, allh)
    
# Sort the x and y values 
sortH = list(allh.keys())
sortH.sort()
allh = {i: allh[i] for i in sortH}
print(allh)

sortV = list(allv.keys())
sortV.sort()
allv = {i: allv[i] for i in sortV}
print(allv)

adjustedH = {}
adjustedV = {}
prev = -1
count = 0

# Adjust y values that are close to be same
for key,values in allh.items():
    current = key
    if abs(current - prev) <= 30:
        adjustedH[count] = [values[0], prev, values[1], prev]
        count += 1
        continue
    else:
        adjustedH[count] = [values[0], current, values[1], current]
        count += 1
    
    prev = current

# Adjust x values that are close to be same
count = 0
for key,values in allv.items():
    current = key
    if abs(current - prev) <= 30:
        adjustedV[count] = [prev, values[0], prev, values[1]]
        count += 1
        continue
    else:
        adjustedV[count] = [current, values[0], current, values[1]]
        count += 1
    
    prev = current

# Adjust y values of vertical lines to match horizontal lines
prev = -1 
for keyH, values in adjustedH.items():
    current = values[1]
    if(current == prev): continue
    for key, value in adjustedV.items():
        if((abs(value[1] - current) > 30) and (abs(value[3] - current)  > 30)):
            continue

        if (abs(value[1] - current) <= 30):
            adjustedV[key][1] = current

        if(abs(value[3] - current) <= 30):
            adjustedV[key][3] = current

        prev = current

# Adjust x values of horizontal lines to vertical lines
prev = -1
for values in adjustedV.values():
    current = values[0]
    if(current == prev): continue
    for key, value in adjustedH.items():
        if((abs(value[0] - current) > 30) and (abs(value[2] - current)  > 30)):
            continue

        if (abs(value[0] - current) <= 30):
            adjustedH[key][0] = current
            
        if (abs(value[2] - current) <= 30):
            adjustedH[key][2] = current

        prev = current


for values in adjustedH.values():
    cv.line(image, (values[0], values[1]), \
            (values[2], values[3]), (0, 255, 0), 6)

for values in adjustedV.values():
    cv.line(image, (values[0], values[1]), \
            (values[2], values[3]), (0, 0, 255), 6)

cv.imwrite(os.path.join(path, 'test.jpg'), image)
