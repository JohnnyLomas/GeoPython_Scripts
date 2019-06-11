#!/usr/bin/env python3

###############################################################################################################

'''
Author: Johnny Lomas
Company: 34North

This script extract all the bands in a multiband geotiff, reprojects them into EPSG:3857, and writes each band
to its own single-band Gtiff file. The script was written for and tested on IFTDSS fire modeling outputs and
the tag/description updating functions are specific to IFTDSS output keywords.  
See the link for details:

https://iftdss.firenet.gov/landing_page/

Usage:

./extractBands.py yourFile.tif 
'''

###############################################################################################################
import rasterio
import sys
import string
from rasterio.warp import calculate_default_transform, reproject, Resampling

# Save the console arguments for input
inFile = sys.argv[1]

# Set projection to reproject to
dst_crs = 'EPSG:32610'

# Make new file name for output files
tempName = "reproj_" + inFile

# Open geotiff raster data from IFTDSS to reproject and extract bands
with rasterio.open(inFile) as raster:
	
	# Get raster data for use in reprojection
	transform, width, height = calculate_default_transform(raster.crs, dst_crs, raster.width, raster.height, *raster.bounds)
	kwargs = raster.meta.copy()
	kwargs.update({
		'crs': dst_crs,
		'transform': transform,
		'width': width,
		'height': height
		})

	

	# Open a new geotiff file to write to using the metadata from the original raster
	with rasterio.open(tempName, 'w', **kwargs) as dst:
		
		# Iteratively reproject the bands in the original raster
		for i in range(1, raster.count + 1):
			
			reproject(
				source=rasterio.band(raster, i),
				destination=rasterio.band(dst, i),
				src_transform=raster.transform,
				src_crs=raster.crs,
				dst_transform=transform,
				dst_crs=dst_crs,
				resampling=Resampling.nearest)
		
		# Update band descriptions and tags with layer names and units. File writes at the end of the with statment
		for i in range(1, dst.count +1):
			dst.set_band_description(i, raster.tags(i)["Layer"].strip() + ", " + raster.tags(i)["Units"].strip())
			dst.update_tags(i, Units = raster.tags(i)["Units"].strip(), Layer = raster.tags(i)["Layer"].strip())

	

	# Re-open the newly projected multiband tiff
	with rasterio.open(tempName, 'r') as reprj:

		# Iterate throught the bands and save as a separate GTiff
		for i in range(1, reprj.count + 1):
	
			# Contruct output filename
			outName1 = str(raster.tags(i)['Layer'])
			outName = outName1.strip()
			outName = "reproj_" + outName.replace(" ", "_") + ".tif"
			print(outName)
		
			# Collect metadata from reprojected tiff
			profile = reprj.profile
			
			# Update meta data
			profile['count'] = 1
			profile["Description"] = raster.tags(i)["Layer"].strip() + ", " + raster.tags(i)["Units"].strip()
			
			# Write the single band to a new Gtiff with updated tags 
			with rasterio.open(outName, 'w', **profile) as single:
				single.update_tags(1, Units = raster.tags(i)["Units"].strip(), Layer = raster.tags(i)["Layer"].strip())
				single.write(reprj.read(i), 1)
		

	
		
		
		
