import cv2 as cv
import numpy as np
import os
from pylsd import lsd



def calculate_line_coords(direction, x1, y1, x2, y2, mode):
    if mode == 1:
        x = (x1 + x2)/2
        if int(x) not in direction.keys():
            exists = False
            for xval in direction.keys():
                if abs(int(x)-xval) <= 25:
                    
                    direction[xval][0] = min(direction[xval][0], \
                                            min(int(y1),int(y2)))
                    direction[xval][1] = max(direction[xval][1], \
                                            max(int(y1),int(y2)))
                    exists = True
                    break
            if exists == False:
                direction[int(x)] = [min(int(y1),int(y2)), \
                                    max(int(y1),int(y2))]
    elif mode == 2:
        y = (y1 + y2)/2
        if int(y) not in direction.keys():
            exists = False
            for yval in direction.keys():
                if abs(int(y)-yval) <= 25:
                    # Take minimum/,maximum x coords from current line
                    # (either side) and compare to current min/max saved for
                    # y coordinate 
                    direction[yval][0] = min(direction[yval][0], \
                                                min(int(x1),int(x2)))
                    direction[yval][1] = max(direction[yval][1], \
                                                max(int(x1),int(x2)))
                    exists = True
                    break
            if exists == False:
                direction[int(y)] = [min(int(x1),int(x2)), \
                                        max(int(x1),int(x2))]   
    
def find_lines(segments, allv, allh):
    horizontal = {}
    vertical = {}

    for line in segments:
        x1,y1,x2,y2,w = line
        angle = np.abs(np.rad2deg(np.arctan2(y1 - y2, x1 - x2)))

        if(angle < 105 and angle > 75):
            calculate_line_coords(vertical, x1, y1, x2, y2, 1)
        else: 
            calculate_line_coords(horizontal, x1, y1, x2, y2, 2)
            
    allh.update(horizontal)
    allv.update(vertical)


def adjust_line_coordinates(line_dict_1, line_dict_2, coord1, coord2):
    prev = -1
    for values in line_dict_1.values():
        current = values[coord1]

        if(current == prev): continue

        for key, value in line_dict_2.items():
            if((abs(value[coord1] - current) > 25) and \
               (abs(value[coord2] - current)  > 25)):
                continue

            if (abs(value[coord1] - current) <= 25):
                line_dict_2[key][coord1] = current

            if(abs(value[coord2] - current) <= 25):
                line_dict_2[key][coord2] = current

            prev = current

def generate_lines(thresholded, contours, mode = 0):
    if contours is None:
        raise Exception("GENERATE_LINES ERROR: No lines found.")
    
    if thresholded is None:
        raise Exception("GENERATE_LINES ERROR: No image found. ")
    allh = {}
    allv = {}
    
    
    for cnt in contours:
        blank = np.zeros_like(thresholded)
        cv.drawContours(blank, [cnt], 0, (255,255,255), -1)
        segments = lsd(blank, scale =.7)
        find_lines(segments, allv, allh)
    
    
    # Sort the x and y values 
    sort_h = list(allh.keys())
    sort_h.sort()
    allh = {i: allh[i] for i in sort_h}
    
    
    sort_v = list(allv.keys())
    sort_v.sort()
    allv = {i: allv[i] for i in sort_v}
        

    adjusted_h = {}
    adjusted_v = {}
    prev = -1
    count = 0
    # Adjust y values that are close to be same
    for key,values in allh.items():
        current = key
        if abs(current - prev) <= 25:
            adjusted_h[count] = [values[0], prev, values[1], prev]
            count += 1
            continue
        else:
            adjusted_h[count] = [values[0], current, values[1], current]
            count += 1
        
        prev = current
    # Adjust x values that are close to be same
    count = 0
    for key,values in allv.items():
        current = key
        if abs(current - prev) <= 25:
            adjusted_v[count] = [prev, values[0], prev, values[1]]
            count += 1
            continue
        else:
            adjusted_v[count] = [current, values[0], current, values[1]]
            count += 1
        
        prev = current
    
    adjust_line_coordinates(adjusted_h, adjusted_v, 1, 3)
    adjust_line_coordinates(adjusted_v, adjusted_h, 0, 2)

    for coords in adjusted_h.values():
        
        for count, coord in enumerate(coords):
            mod = coord % 4
            coords[count] -= mod


    for coords in adjusted_v.values():
        for count, coord in enumerate(coords):
            mod = coord % 4
            coords[count] -= mod

    if mode == 1:
        print(f'Found horizontal lines: {allh}')
        print(f'Found vertical lines: {allv}')

        print(f'Adjusted horizontal lines: {adjusted_h}')
        print(f'Adjusted vertical lines: {adjusted_v}')
    

    return adjusted_h, adjusted_v

def draw_lines(image, horizontal, vertical, path):
    for values in horizontal.values():
        cv.line(image, (values[0], values[1]), \
                (values[2], values[3]), (0, 255, 0), 6)

    for values in vertical.values():
        cv.line(image, (values[0], values[1]), \
                (values[2], values[3]), (0, 0, 255), 6)
    cv.imwrite(os.path.join(path, 'test.jpg'), image)
    return image


if __name__ == '__main__':
    from endpoint import get_contours, resize_image, threshold_image, \
        get_node_dict, get_centroids_dict, get_end_points
    image = cv.imread('empty4.jpg')

    os.chdir("..")
    os.chdir("output_images")
    path = os.getcwd()

    # Resize image to maintain consistency and reduce noise (Refer to document)
    image, width, height = resize_image(image, path)
    thresh = threshold_image(image, path)
    mask = get_end_points(thresh, path)
    centroid_dict = get_centroids_dict(mask)
    out, contours = get_contours(thresh, path)
    nodeDict, points = get_node_dict(centroid_dict, image, \
                                     contours, width, height)
    print(points)

    horizontal, vertical = generate_lines(thresh, contours, 1)
    lines = draw_lines(image, horizontal, vertical, path)
    cv.imwrite(os.path.join(path, "lines.jpg"), lines)

    #print(horizontal) 
    #print(vertical)
