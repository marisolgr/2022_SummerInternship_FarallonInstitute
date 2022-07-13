# Chlorine Project
Author: Austin
Date: 13 July 2022
Description: This function will plot a 300km-diameter graph of chlorophyll levels around certain seabird sites globally.

Methods:
 - Image Mask Method: Using the PIL (Pillow) library, an image mask is used to show a 300km range around a site. This method is more efficient, but significantly limits editing graphing features, and is generally a cheaper shortcut for performance.
 - NAN Method: Using only the inbuilt math libraries, calculate the angular distance between the site and every point within 300km (Every longitude/latitude degree is approx. 60 nautical miles measured from the equator) and only render points within the desired range. This method is significantly more resource intensive, but allows for free editing of the graphing features.