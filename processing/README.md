_# Processing Function Documentation
Here is documentation on the functions within this directory on their parameters and usage.

## Endpoint Detection
The purpose of 'endpoint.py' is to take in some circuit image and obtain 
the endpoints of wires. 

```
resize_image(image, path, scale_percent = 25, save_image = 0)

threshold_image(image, path, save_image = 0)

get_contours(image, path, save_image = 0)

get_endpoints(image, path, save_image = 0)

get_centroid_dict(end_points_mask)

get_node_dict(centroids_dictionary, image, contours, width, height)
```


#### `resize_image`
* **Input Args:**
  * `image` - Image to be resized.
  * `path` - Absolute path name to save image to.
  * `scale_percent` - Integer value used to scale input image.
  * `save_image` - Flag setting what images to save to absolute path location.
* **Output Args:**
  * `resized_image` - Scaled image returned.
  * `width` - Width of resized image.
  * `height` - Height of resized image.
* **Description:** Resizes image. If save_image set to 1, saves resized image into absolute path directory. 

#### `threshold_image`
* **Input Args:**
  * `image` - Image to be thresholded and filtered.
  * `path` - Absolute path name to save image to.
  * `save_image` - Flag setting what images to save to absolute path location.
* **Output Args:**
  * `img_filtered` - Thresholded and filtered image.
* **Description:** Takes in image and converts to grayscale image. Noise in image is filtered leaving major image portions with (255, 255, 255) pixel values. If save image set to 1, thresholded image and final filtered image saved to. If save image set to 2, blurred, grayscale, skeleton, and closed image (in addition to thresholded and filtered images) saves to input path.  

#### `get_contours`
* **Inpute Args:**
  * `image` - Image to obtain contours from.
  * `path` - Absolute path name to save image to.
  * `save_image` -  Flag setting what images to save to absolute path location.
* **Output Args:**
  * `out` - Grayscale image with contours of wires saved.
  * `contours` - Contour areas seen within image.
* **Description:** Takes in grayscaled image (thresholded and filtered) and identifies wires within image. Returns image with all contours found and an array of contours found.
