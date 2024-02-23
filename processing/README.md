# Processing Function Documentation
Below is documentation on the functions within this directory on their parameters and usage. 

## Endpoint Detection
'endpoint.py' takes in some circuit image and obtains the endpoints of wires. 

#### Summary
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
  * `save_image` - Flag setting what images to save to absolute path location. Set to 0 by default. If `save_image` set to 1, thresholded image and final filtered image saved to absolute path. If `save _image` set to 2, blurred, grayscale, skeleton, and closed image (in addition to thresholded and filtered images) saves to absolute path.
* **Output Args:**
  * `img_filtered` - Thresholded and filtered image.
* **Description:** Takes in image and converts to grayscale image. Noise in image is filtered leaving major image portions with (255, 255, 255) RGB pixel values.   

#### `get_contours`
* **Inpute Args:**
  * `image` - Grayscale image to obtain contours from.
  * `path` - Absolute path name to save image to.
  * `save_image` -  Flag setting what images to save to absolute path location. Set to 0 by default. If `save_image` set to 1, image with found contours above set area threshold saved to absolute path.   
* **Output Args:**
  * `out` - Grayscale image with contours of wires saved.
  * `contours` - Detected contours in image. 
* **Description:** Takes in grayscaled image (thresholded and filtered) and identifies wires within image. Returns image with all contours found and array of contours found.

#### `get_end_points`
* **Input Args:**
  * `image` - Grayscale image to obtain endpoints of wires. Main input is filtered grayscale image.
  * `path` - Absolute path name to save image to.
  * `save_image` - Flag setting what images to save to absolute path location. Set to 0 by default.If `save_image` set to 1, thinned and filtered contour images saved to absolute path.
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
  * `save_image` - Flag setting what images to save to absolute path location. Set to 0 by default. If `save_image` set to 1, image with endpoints found highlighted on input image saved to absolute path.
* **Output Args:**
  * `node_dict` - Dictionary with all identified circuit nodes. The keys are the point number. Values are the node the point belongs to.
  * `points` - Dictionary with all endpoints identified. The keys are the point number. Values are the (x,y) coordinates of point in resized image.
* **Description:** Generates a dictionary with all points in nodes and another dictionary with endpoint coordinates.

### Running the File on Its Own
You may change the testing image to whatever you want. Make sure the image is within the same directory as the `endpoint.py` file.

## Line Detection
`line_detection.py` identifies wires within an input circuit image, straightens them, and draws them within input image after adjusting them with respect to each other.

#### Summary
```
calculate_line_coords(horizontal, vertical, x1, y1, x2, y2, mode)

find_lines(segments, allv, allh)

adjust_line_coordinates(line_dict_1, line_dict_2, coord1, coord2)

generate_lines(image, thresholded, contours, path)
```

#### `calculate_line_coords`
* **Input Args:**
  * `direction` - Dictionary for horizontal or vertical lines.
  * `x1` - First x coordinate of line segment.
  * `y1` - First y coordinate of line segment.
  * `x2` - Second x coordinate of line segment.
  * `y2` - Second y coordinate of line segment.
  * `mode` - Sets mode for line maximum line coordinate calculation. If mode set to 1, calculate for vertical lines. If mode set to 2, calculate for horizontal lines. Ensure input direction dictionary is correct.
* **Output Args:** None
* **Description:** Adds (horizontal or vertical) line into input dictionary. If dictionary has line with (x/y) coordinate of same range as line segment provided in coordinates, expand the line if coordinates exist past current line size. If not, skip coordinate adjustment. Dictionary is in format (key = found line number, value = [x1, y1, x2, y2]).

#### `find_lines`
* **Input Args:**
  * `segments` - Line segments found in image
  * `allv` - Dictionary to hold all vertical lines found
  * `allh` - Dictionary to hold all horizontal lines found
* **Output Args:** None
* **Description:** Identifies line segment angle and finds largest total line that accounts for portion of the wire.

#### `adjust_line_coordinates`
* **Input Args:**
  * `line_dict_1` - First input dictionary containing found lines
  * `line_dict_2` - Second input dictionary containing found lines
  * `coord1` - First varying coordinate in line format (x1, y1, x2, y2)
  * `coord2` - Second varying coordinate in line format
 * **Output Args:** None
 * **Description:** Adjusts line coordinates in dictionary `line_dict_2` to match coordinates in `line_dict_1`. `coord1` and `coord2` are the same within `line_dict_1` and compare to every same list index within `line_dict_2` in certain threshold (25 pixels on either side by default) and sets equal. This move lines so lines properly connect.

#### `generate_lines`
* **Input Args:**
  * `image` - Adjusted input image.
  * `thresholded` - Thresholded and filtered version of image with components removed.
  * `contours` - Contour found in image.
  * `path` - Absolute path name for image save location.
  * `mode` - Flag to set debug and saving of image. Set to 0 by default. If `mode` set to 1, function prints found horizontal and vertical line, and all adjusted lines coordinates, .
* **Output Args:** None
* **Description** Generates and draws all lines onto input image and saves into `path` directory.
