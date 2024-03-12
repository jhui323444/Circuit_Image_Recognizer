# imports:
import cv2
import numpy as np
import os
from collections import defaultdict




def resize_image(image, path, scale_percent = 25, save_image = 0):
    # Resize image:
    if image is None:
        raise Exception("RESIZE_IMAGE ERROR: Valid image not found.")
    
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)

    # New dimensions:
    dim = (width, height)

    # resize image
    resized_image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    if save_image == 1:
        cv2.imwrite(os.path.join(path, "resized.jpg"), resized_image)
    return resized_image, width, height


def threshold_image(image, path, save_image = 0):
    # Color conversion
    if image is None:
        raise Exception("THRESHOLD_IMAGE ERROR: Valid image not found.")
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9,9),0)
    if save_image == 2:
        cv2.imwrite(os.path.join(path, "blur.jpg") , blur)

    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
                                    cv2.THRESH_BINARY_INV, 7, 5)
    if save_image == 1 or save_image == 2:
        cv2.imwrite(os.path.join(path, "thresh.jpg") , thresh)

    # Fill in any large gaps between same wires/nodes
    kernel = np.ones((7, 7), np.uint8)
    dilation = cv2.dilate(thresh, kernel, iterations=5)
    erosion = cv2.erode(dilation, kernel, iterations=5)
    kernel = np.ones((11,11),np.uint8)
    closing = cv2.morphologyEx(erosion, cv2.MORPH_CLOSE, kernel)
    skeleton = cv2.ximgproc.thinning(closing, None, 1)

    if save_image == 2:
        cv2.imwrite(os.path.join(path, "skel_ZS.jpg") , skeleton)
        cv2.imwrite(os.path.join(path, "gray.jpg"), gray)
        cv2.imwrite(os.path.join(path, "close.jpg"), closing)
    # Set the end-points kernel:
    kernel = np.uint8([[1, 1, 1],
                [1, 10, 1],
                [1, 1, 1]])
    # Convolve the image with the kernel:
    img_filtered = cv2.filter2D(skeleton, -1, kernel)
    if save_image == 1 or save_image == 2:        
        cv2.imwrite(os.path.join(path,"filtered.jpg"), img_filtered)
    return img_filtered


def get_contours(image, path, save_image = 0):
    if image is None:
        raise Exception("GET_CONTOURS ERROR: Valid image not found. ")
        # Find contours of nodes
    contours ,hierarchy = cv2.findContours(image, \
                                        cv2.RETR_EXTERNAL, \
                                        cv2.CHAIN_APPROX_SIMPLE)

    # Creates a black image that is size original resized image
    out = np.zeros_like(image)

    # Draws contours (large enough) onto black image
    for cnt in contours:
        area = cv2.contourArea(cnt)
        #print(f'Contour area: {area}')
        if area < 80:
            continue
        cv2.drawContours(out, [cnt], 0, (255, 255, 255), -1)
    
    if save_image == 1: 
        cv2.imwrite(os.path.join(path,"contours.jpg"), out)
    
    return out, contours

# Take in filtered image and find endpoints
def get_end_points(image, path, save_image = 0):
    out, contours = get_contours(image, path)
    cont_thinned = cv2.ximgproc.thinning(out, None, 1)
    kernel = np.uint8([[1, 1, 1],
                [1, 10, 1],
                [1, 1, 1]])
    _, binary_image = cv2.threshold(cont_thinned, 128, 10, cv2.THRESH_BINARY)
    cont_filtered = cv2.filter2D(binary_image, -1, kernel)
    
    if save_image == 1:
        cv2.imwrite(os.path.join(path,"cont_thinned.jpg"), cont_thinned)
        cv2.imwrite(os.path.join(path,"cont_filtered.jpg"), cont_filtered)

    # Extract only the end-points pixels, those with
    # an intensity value of 110:
    end_points_mask = np.where(cont_filtered == 110, 255, 0)
    end_points_mask = end_points_mask.astype(np.uint8)
    
    return end_points_mask


def get_centroids_dict(end_points_mask):
    # RGB copy of this:
    rgb_mask = end_points_mask.copy()
    rgb_mask = cv2.cvtColor(rgb_mask, cv2.COLOR_GRAY2BGR)

    # Create a copy of the mask for points processing:
    groups_mask = end_points_mask.copy()

    # Set kernel (structuring element) size:
    kernel_size = 3
    # Set operation iterations:
    op_iterations = 3
    # Get the structuring element:
    max_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, \
                                          (kernel_size, kernel_size))
    # Perform dilate:
    groups_x     = cv2.morphologyEx(groups_mask, cv2.MORPH_DILATE, max_kernel, \
                            None, None, op_iterations, cv2.BORDER_REFLECT101)

    # Set the centroids Dictionary:
    centroids_dict = {}

    # Get centroids on the end points mask:
    total_components, output, stats, centroids = \
        cv2.connectedComponentsWithStats(end_points_mask, connectivity=8)

    # Count the blob labels with this:
    label_counter = 1

    # Loop through the centroids, skipping the background (0):
    for c in range(1, len(centroids), 1):

        # Get the current centroids:
        cx = int(centroids[c][0])
        cy = int(centroids[c][1])

        # Get the pixel value on the groups mask:
        pixel_value = groups_mask[cy, cx]

        # If new value (255) there's no entry in the dictionary
        # Process a new key and value:
        if pixel_value == 255:

            # New key and values-> Centroid and Point Count:
            centroids_dict[label_counter] = (cx, cy, 1)

            # Flood fill at centroid:
            cv2.floodFill(groups_mask, mask=None, \
                        seedPoint=(cx, cy), newVal=label_counter)
            label_counter += 1

        # Else, the label already exists and we must accumulate the
        # centroid and its count:
        else:

            # Get Value:
            (accum_cx, accum_cy, blob_count) = centroids_dict[pixel_value]

            # Accumulate value:
            accum_cx = accum_cx + cx
            accum_cy = accum_cy + cy
            blob_count += 1

            # Update dictionary entry:
            centroids_dict[pixel_value] = (accum_cx, accum_cy, blob_count)

            # Loop trough the dictionary and get the final centroid values:

    return centroids_dict


# takes in centroids dict, contours, and resized image
def get_node_dict(centroids_dict, image, contours, \
                  width, height, save_image = 0):
    node_dict = {}
    points = {}
    ends_counter = 0
    for k in centroids_dict:
        # Get the value of the current key:
        (cx, cy, count) = centroids_dict[k]
        # Process combined points:
        if count != 1:
            cx = int(cx/count)
            cy = int(cy/count)
        # Draw circle at the centroid
        cv2.circle(image, (cx, cy), 8, (0, 0, 255), -1)


        # Check which node the endpoint belongs to 
        contour_counter = 0
        check_contour = np.zeros((height, width), dtype=np.uint8)

        for c in contours:
            if cv2.contourArea(c) > 80:
                cv2.drawContours(check_contour, [c], 0, (255, 255, 255), 3)
            color = check_contour[cy, cx]
            #print(color)

            # If pixel at node end is white after drawing a contour, 
            # then point belongs to that node
            if color == 255:
                node_dict[ends_counter] = contour_counter
                points[ends_counter] = (cx, cy)
                ends_counter += 1
                break

            contour_counter += 1
    if save_image == 1:
        cv2.imwrite(os.path.join(path, "Final Centroids.jpg"), resized_image)
    return node_dict, points


if __name__ == '__main__':
    # Reading an image in default mode:
    image = cv2.imread("")

    os.chdir("..")
    os.chdir("output_images")
    path = os.getcwd()
    print(path)
    resized_image, width, height = resize_image(image, path)
    img_filtered = threshold_image(resized_image, path)
    end_points_mask = get_end_points(img_filtered, path)
    centroids_dict = get_centroids_dict(end_points_mask)
    out, contours = get_contours(img_filtered, path , 1)
    node_dict, points = get_node_dict(centroids_dict, resized_image, \
                                   contours, width, height, 1)

    
    if not cv2.imwrite(os.path.join(path, "test.jpg"), resized_image):
        raise Exception("No image loaded.")
    #print(centroids_dictionary)
    #print(node_dict)

