#!/usr/bin/env python3

################################################################################################################
'''
This script and the functions defined here automate the geographic analysis of polygons within Butte County, 
California. The script is written to run entirely within its own directory along with the shapefiles
and GeoTiffs it depends on. It generates the following metrics wit respect to the input polygon:

- Total area in acres
- Fire hazard severity acreage by class
- Direct protection area acreage
- Total parcel count
- Total Owner count
- Average parcel size
- Total acreage of the top 6 landowners
- Total estimated structure count
- General plan land designation acreage
- Vegetation according to FRAP surface fuels acreage
- Names of critical infrastructure in the polygon

Input shapefiles must contain a single polygon of interest to report your statistics accurately. The raster
calculation is based on a hard-coded pixel size of 30.00025 meters-squared. 

Usage: ./zonalAnalysis inputShapefile.shp

Author: Johnny Lomas
Company: 34North
Date: 6/6/19
'''
################################################################################################################

import geopandas as gpd
import rasterio as rio
import rasterio.mask
import sys
import pprint
import shapely 
import pycrs
import numpy
import pandas as pd
import matplotlib.pyplot as plt

################################################ FUNCTION DEFINITIONS ###########################################

def totalArea(inputPoly):
	''' 
	Calculates the total area in acres of the 
	user input polygon.
	'''
	
	# Calculate a new column to store the area of the polygon in acres
	inputPoly["acres"] = inputPoly['geometry'].area/4046.856

	# Return the total area of the polygon
	area = inputPoly["acres"][0]
	
	return {"Total_Area": {"Acreage": area}}


def hazardClass(inputPoly):
	'''
	Function caluclates the area in the input polygon
	in acres for each Cal Fire hazard class. This function 
	relies on the Butte County LRA FHZ layer. Returns a dict
	of real numbers.
	'''
	
	#Load the shapefile containing fire hazard class
	fhz = gpd.read_file("ButteCounty_LRA_FHZ_prj32610.shp")

	# Clip the firehazard class to the extent of the input polygon
	fhz_intersect = gpd.overlay(fhz, inputPoly, how='intersection')

	# Compute a colume for acreage in the new layer
	fhz_intersect['acres'] = fhz_intersect['geometry'].area/4046.856

	# Compute FHZ statistics from clipped layer
	nonWildland = fhz_intersect[fhz_intersect["HAZ_CODE"] < 0]["acres"].sum()
	moderate = fhz_intersect[fhz_intersect["HAZ_CODE"] == 1]["acres"].sum()
	high = fhz_intersect[fhz_intersect["HAZ_CODE"] ==2]["acres"].sum()
	veryHigh = fhz_intersect[fhz_intersect["HAZ_CODE"] == 3]["acres"].sum()

	# Return the statistics in a dictionary
	return {"Fire Hazard Severity": {"Non-Wildland": nonWildland, "Moderate": moderate, "High": high, "Very_High": veryHigh}}


def directProtection(inputPoly):
	'''
	Function calculates the area in the input polygon
	in acres for each direct protection area designation.
	The function relies on the DPA layer.
	'''

	#Load the shapefile containing direct protection areas
	dpa = gpd.read_file("direcrprotectionarea_17_prj32610.shp")

	# Clip the direct protection areas to the extent of the input polygon
	dpa_intersect = gpd.overlay(dpa, inputPoly, how='intersection')

	# Compute a colume for acreage in the new layer
	dpa_intersect['acres'] = dpa_intersect['geometry'].area/4046.856

	# Compute DPA acreages for each agency
	local = dpa_intersect[dpa_intersect["DPA_GROUP"] == "LOCAL"]["acres"].sum()
	state = dpa_intersect[dpa_intersect["DPA_GROUP"] == "STATE"]["acres"].sum()
	federal = dpa_intersect[dpa_intersect["DPA_GROUP"] == "FEDERAL"]["acres"].sum()

	# Return the statistics in a dictionary
	return {"Direct Protection Areas": {"Local": local, "State": state, "federal": federal}}
	


def parcels(inputPoly):
	'''
	Function calculates the total number of parcels within
	the input polygon, the top 6 land owners, and the 
	total number of owners. It relies on the parcels layer 
	provided by the county.
	'''

	#Load the shapefile containing parcels
	parcels = gpd.read_file("Parcel_with_lotsize_improvevalue_32610.shp")

	# Clip the parcels to the extent of the input polygon
	par_intersect = gpd.overlay(parcels, inputPoly, how='intersection')

	# Count the total number rows
	totalParcels = par_intersect.count()["APN"]

	# Compute average parcel size
	avgParcel = par_intersect["ACRES"].mean()

	# Dissolve the clipped layer on owner and count the number of rows to get the number of owners
	par_dissolve = par_intersect[["geometry", "Owner", "ACRES"]]
	par_dissolve = par_dissolve.dissolve(by = "Owner", aggfunc = "sum")
	totalOwners = par_dissolve.count()["geometry"]

	# Sort the dissolved parcel layer by acreage at record the top 6 owners
	par_dissolve.sort_values(by = "ACRES", ascending = False, inplace = True)
	top6OwnersAcres = list(par_dissolve["ACRES"][0:6])
	top6OwnersNames = list(par_dissolve[0:6].index)
	
	# Initialize empty list to store parcel counts
	top6OwnersParcels = []

	# Iterate through top 6 owners and get the number of parcels they own
	for person in top6OwnersNames:
		par = par_intersect[par_intersect["Owner"] == person]
		top6OwnersParcels.append(par.count()["geometry"])

	return {"Parcel Analysis": {"Total_Parcels": totalParcels, 
								"Total_Owners": totalOwners, 
								"Top_6_Owners": [top6OwnersAcres, top6OwnersNames, top6OwnersParcels],
								"Average Parcel Size": avgParcel}}


def totalStructures(inputPoly):
	'''
	Function returns the number of estimated structures 
	that are within the boundary of the input polygon.
	It relies on the structures layer created from the 
	parcels by Brendan Palmieri.
	'''

	# Load the shapefile containing the estimated structure locations (points)
	structures = gpd.read_file("structures_parcel_IV10000_prj32610.shp")

	'''
	# Plot for debugging purposes
	fig, ax = plt.subplots()

	inputPoly.plot(ax=ax, facecolor = 'gray')

	structures.plot(ax=ax, color = 'blue', markersize =0.5)
	plt.tight_layout()
	plt.show()'''
	
	# Generate a boolean series denoting whether or not a structure is in the input polygon
	mask = structures.within(inputPoly.loc[0, 'geometry'])

	# Count the number of True values in the boolean series
	struct = mask.loc[mask == True].count()

	# Return the count
	return {"Estimated Structures": {"Count": struct}}

def generalPlan(inputPoly):
	'''
	Function returns the acreage of each General Plan land
	designation within the input polygon. It relies on the 
	General Plan layer provided by Butte County.
	'''

	#Load the shapefile containing direct protection areas
	gpa = gpd.read_file("General_Plan_prj32610.shp")

	# Clip the direct protection areas to the extent of the input polygon
	gpa_intersect = gpd.overlay(gpa, inputPoly, how='intersection')

	# Compute a colume for acreage in the new layer
	gpa_intersect['acres'] = gpa_intersect['geometry'].area/4046.856

	# Dissolve on GP just in case clipping splits a polygon
	gpa_dissolve = gpa_intersect.dissolve(by = "GP_Type", aggfunc = 'sum')

	# Sort the table for prettier printing
	gpa_dissolve.sort_values(by = "acres", ascending = False, inplace = True)
	
	# Grab designations and acreage from dataframe
	acre = list(gpa_dissolve.iloc[:,-1])
	des = list(gpa_dissolve.index)
	
	# Return the statistics
	return {"General Plan": {"Designation": des, "Acreage": acre}}

def vegetationAnalysis(inputPoly):
	'''
	Returns the acreage of each FRAP vegetation model present
	within the input polygon. Relies on the FRAP surface fuels
	raster layer. The code for the models is below:

	-⁠ ['#FFF286', 1, Grass]
    -⁠ ['#F1DE3A', 2, Pine/⁠Grass]
    -⁠ ['#E4C176', 3, Tall Grass]
    -⁠ ['#C44F3B', 4, Tall Chaparral]
    -⁠ ['#D993CC', 5, Brush]
    -⁠ ['#CA2084', 6, Dormant Brush]
    -⁠ ['#C4863B', 7, Southern Rough]
    -⁠ ['#3A68C1', 8, Hardwood/⁠ Lodgepole Pine]
    -⁠ ['#66CE77', 9, Mixed Conifer Light]
    -⁠ ['#237E32', 10, Mixed Conifer Medium]
    -⁠ ['#C16C05', 11, Light Logging Slash]
    -⁠ ['#8B520D', 12, Medium Logging Slash]
    -⁠ ['#451A85', 28, Urban Fuel]
    -⁠ ['#A3ACA5', 97, Agricultural Lands]
    -⁠ ['#2CC1D7', 98, Water]
    -⁠ ['#696969', 99, Barren/⁠Rock/⁠Other]
	'''

	# Reproject input layer to be 3310 because the frap raster is in 3310...
	input3310 = inputPoly.copy()
	input3310 = input3310.to_crs({"init": "epsg:3310"})

	# Get the polygon's geometry from the input file to overlay on the FRAP data
	poly = input3310["geometry"]

	# Import the raster layer with rasterio, clip by mask extent, and update the metadata 
	with rio.open("frap_fuel_butte.tif") as src:
		out_img, out_transform = rasterio.mask.mask(src, poly, crop=True)

		out_meta = src.meta.copy()

		out_meta.update({"driver": "GTiff", "height": out_img.shape[1], "width": out_img.shape[2], "transform": out_transform})

	# Write the clipped raster to a new file 
	with rasterio.open("clipped_frap.tif", "w", **out_meta) as dest:
		dest.write(out_img)

	
	# Open the newly clipped raster
	with rio.open("clipped_frap.tif") as frap_clipped:
		# Read raster into numpy array
		raster = frap_clipped.read()

		# This step is probably redundant
		values = raster[:,:,:]

		# Get the unique values and calculate their frequencies
		uniques, counts = numpy.unique(values, return_counts=True)

		# Format uniqes and counts into data frame
		raster_counts = pd.DataFrame(counts, index = uniques, columns = ['Count'])

		# Convert frequencies to acreage based on pixel size
		raster_counts['acres'] = raster_counts['Count']*(900.015013545*0.000247105)
		
		# remove first row which contains no-data values
		raster_counts = raster_counts.iloc[1:-1]
		
	# Return the vegetation acreage	
	return raster_counts["acres"]
	

def criticalInfrastructure(inputPoly):
	'''
	Returns a list of the critical infrastructure within the 
	input polygon. Relies on the critical infrastructure layer.
	'''

	# Load the shapefile containing the critical facilities
	cf = gpd.read_file("Critical_Facilities_Butte_County_prj32610.shp")

	# Generate a boolean series denoting whether or not a facility is in the input polygon
	mask = cf.within(inputPoly.loc[0, 'geometry'])

	# Count the number of True values in the boolean series
	facil = mask.loc[mask == True].count()

	# Select facilities from the original file and generate new dataframe
	cf_clip = cf.loc[mask]

	# Get facilitiy names as a list
	names = list(cf_clip["Name"])

	# Return the facilities
	return {"Critical_Facilities": {"Count": facil, "Facilities": names}}

def SRA(inputPoly):
	'''
	Function calculates the area in the input polygon
	in acres for each state responsibility designation.
	The function relies on the SRA16 layer.
	'''

	#Load the shapefile containing direct protection areas
	sra = gpd.read_file("SRA16_Butte_32610.shp")

	# Clip the direct protection areas to the extent of the input polygon
	sra_intersect = gpd.overlay(sra, inputPoly, how='intersection')

	# Compute a colume for acreage in the new layer
	sra_intersect['acres'] = sra_intersect['geometry'].area/4046.856

	# Compute DPA acreages for each agency
	lra = sra_intersect[sra_intersect["SRA"] == "LRA"]["acres"].sum()
	Sra = sra_intersect[sra_intersect["SRA"] == "SRA"]["acres"].sum()
	fra = sra_intersect[sra_intersect["SRA"] == "FRA"]["acres"].sum()

	# Return the statistics in a dictionary
	return {"State Responsibility Area": {"Local": lra, "State": Sra, "federal": fra}}


############################# BEGIN THE MAIN SCRIPT ###################################################

def main():
	'''Main script uses the above functions to print a report 
		to a text file containing each statistic generated with
		respect to the input polygon.
	'''
	
	# Load the shapefile specified on the command line
	inputPoly = gpd.read_file(sys.argv[1])

	# Make sure projection is 32610
	inputPoly.to_crs({'init': 'epsg:32610'})

	# Run the statistic generating functions and print
	#pprint.pprint(totalArea(inputPoly))
	#pprint.pprint(hazardClass(inputPoly))
	#pprint.pprint(directProtection(inputPoly))
	#pprint.pprint(parcels(inputPoly))
	#pprint.pprint(totalStructures(inputPoly))
	#pprint.pprint(generalPlan(inputPoly))
	#print("FRAP fuel models (Acres)\n")
	#pprint.pprint(vegetationAnalysis(inputPoly))
	#pprint.pprint(criticalInfrastructure(inputPoly))
	pprint.pprint(SRA(inputPoly))



main()