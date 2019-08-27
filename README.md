# Road-Detection
The main goal of this project is to identify roads from satellite imagery employing solely computer vision techniques.
To achieve the desired result we were faced with a few problems. Firstly, the provided images were poorly conditioned and shot in a higher altitude than expected, presenting low quality roads which were most times ocluded by clouds. Secondly, there's a low contrast between the roads and the rest of the background, leading to miss-detections.
Firstly we transformed the image to greyscale, next we increase the image contrast by employing an "adaptative contrast" (CLAHE). Finnaly we applyed a gamma correction, adjusting the image lighting.

With this adjustments the contrast between roads and the background is clearer, which enabled us to separate roads from irrelevant data such as houses and clouds and detecting roads by employing morphology techniques (edge detection).

<p float="left">
  <img src="/img/o3.png" width="400" />
  <img src="/img/s3.png" width="400" />
</p>

<p float="left">
  <img src="/img/o5.png" width="400" /> 
  <img src="/img/s5.png" width="400" />
</p>

<p float="left">
  <img src="/img/o9.png" width="400" />
  <img src="/img/s9.png" width="400" />
</p>

**Software**

*Python*

*OpenCV*

*QGIS*

**References**

http://www.mdpi.com/2072-4292/7/7/8779

http://geopyspark.readthedocs.io/en/latest/index.html

http://www.gdal.org/frmt_sentinel2.html
