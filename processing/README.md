# Processing Function Documentation
Here is documentation on the functions within this directory on their parameters and usage.

## Endpoint Detection
The purpose of 'endpoint.py' is to take in some circuit image and obtain 
the endpoints of wires. 

```
resize_image(image, path, scale_percent=25)

threshold_image(image, path)

get_contours(image, path)

get_endpoints(image, path)

get_centroid_dict(endPointsMask)

get_node_dict(centroids_dictionary, image, contours, width, height)
```


#### `resizeImage`
* **Input Args:** image, path, scale_percent
* **Output Args:** resized_image, width, height
* **Description:** Resizes some input image to whatever percent and returns modified image. The default percent is 25 to reduce noise when converting image to grayscale. The modified image is saved into the provided master path name.

#### `thresholdImage`
