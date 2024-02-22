# Processing Function Documentation
Below is documentation on the functions within this directory on their parameters and usage. 

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
  * `save_image` - Flag setting what images to save to absolute path location. Set to 0 by default. If save_image set to 1, saves resized image into absolute path directory.
* **Output Args:**
  * `resized_image` - Scaled image returned.
  * `width` - Width of resized image.
  * `height` - Height of resized image. 
* **Description:** Resizes image. 

#### `threshold_image`
* **Input Args:**
  * `image` - Image to be thresholded and filtered.
  * `path` - Absolute path name to save image to.
  * `save_image` - Flag setting what images to save to absolute path location. Set to 0 by default. If save_image set to 1, thresholded image and final filtered image saved to absolute path. If save _image set to 2, blurred, grayscale, skeleton, and closed image (in addition to thresholded and filtered images) saves to absolute path.
* **Output Args:**
  * `img_filtered` - Thresholded and filtered image.
* **Description:** Takes in image and converts to grayscale image. Noise in image is filtered leaving major image portions with (255, 255, 255) RGB pixel values.   

#### `get_contours`
* **Inpute Args:**
  * `image` - Grayscale image to obtain contours from.
  * `path` - Absolute path name to save image to.
  * `save_image` -  Flag setting what images to save to absolute path location. Set to 0 by default. If save_image set to 1, image with found contours above set area threshold saved to absolute path.   
* **Output Args:**
  * `out` - Grayscale image with contours of wires saved.
  * `contours` - Detected contours in image. 
* **Description:** Takes in grayscaled image (thresholded and filtered) and identifies wires within image. Returns image with all contours found and array of contours found.

#### `get_end_points`
* **Input Args:**
  * `image` - Grayscale image to obtain endpoints of wires. Main input is filtered grayscale image.
  * `path` - Absolute path name to save image to.
  * `save_image` - Flag setting what images to save to absolute path location. Set to 0 by default.If save_image set to 1, thinned and filtered contour images saved to absolute path.
* **Output Args:**
  * `end_points_mask` - Grayscale 8 bit unsigned integer image with only identified endpoints within image with (255, 255, 255) RGB pixel values.
* **Description:** Generates a bit mask with only the endpoints of wires in image from filtered image.

#### `get_centroids_dict`
* **Input Args:**
  * `end_points_mask` - Grayscale 8 bit unsigned integer image with only identified endpoints within image with (255, 255, 255) RGB pixel values.
* **Output Args:**
  * `centroids_dict` - Dictionary with all found centroids in image.
* **Description:** - Generates dictionary containing all centroids found in image based on all end points in input mask.

#### `get_node_dict`
* **Input Args:**
  * `centroids_dict` - Dictionary with all found centroids in image.
  * `image` - Resized image from resize_image.
  * `contours` - Detected contours in image.
  * `width` - Width of resized image.
  * `height` - Height of resized image.
  * `save_image` - Flag setting what images to save to absolute path location. Set to 0 by default. If save_image set to 1, image with endpoints found highlighted on input image saved to absolute path.
* **Output Args:**
  * `node_dict` - Dictionary with all identified circuit nodes. The keys are the point number. Values are the node the point belongs to.
  * `points` - Dictionary with all endpoints identified. The keys are the point number. Values are the (x,y) coordinates of point in resized image.
* **Description:** Generates a dictionary with all points in nodes and another dictionary with endpoint coordinates.

### Running the File on Its Own
You may change the testing image to whatever you want. Make sure the image is within the same directory as the `endpoint.py` file.
