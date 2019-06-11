#!/usr/bin/env python3

import geopandas as gpd
import shapely

# Roads to extract from the TIGER/LINE shapefile
routes = ["Oroville Bangor Hwy",
 "Oroville Quincy Hwy",
 "Oro Quincy Hwy",
 "Oro Bangor Hwy",
 "Oroville-Bangor Hwy",
 "Oroville-Quincy Hwy",
 "Olive Hwy",
 "Simmons Rd",
 "Northfork Rd",
 "Bell Ranch Rd",
 "Encina Grande Rd",
 "Bloomer Hill Rd",
 "Bald Rock Rd",
 "Zink Rd",
 "Rockerfeller Rd",
 "Bean Creek Rd",
 "Stephens Ridge Rd",
 "Deer Creek Hwy",
 "Honey Run Rd",
 "Centerville Rd",
 "Durham-Pentz Rd",
 "Williams Rd",
 "Clark Rd",
 "Cassandra Dr",
 "Wheelock Rd",
 "Mesilla Valley Rd",
 "Pentz Rd",
 "Cohasset Rd",
 "Vilas Rd",
 "Richardson Springs Rd",
 "Forbestown Rd",
 "Lumpkin Rd",
 "Robinson Mill Rd",
 "La Porte Rd",
 "New York Flat Rd",
 "Challenge Cut Off Rd",
 "Miners Ranch Rd",
 "Nopel Avenue",
 "Forest Ranch Rd",
 "Garland Rd",
 "Schott Rd",
 "Crown Point Rd",
 "Wilder Dr",
 "Humboldt Rd",
 "Skyway",
 "Skyway Rd",
 "Scout Rd",
 "Clark Rd",
 "Hoffman Rd",
 "Concow Rd",
 "Rim Rd",
 "Jordan Hill Rd",
 "Deadwood Rd",
 "Pinkston Canyon Rd",
 "Andy Mountain Rd",
 "Dark Canyon Rd",
 "Big Bend Rd",
 "Four Trees Rd",
 "Pulga Rd",
 "Granite Ridge Rd",
 "Nelson Bar Rd",
 "Yankee Hill Rd",
 "Cherokee Rd",
 "Los Verjeles Rd",
 "Cox Ln",
 "Palermo Rd",
 "Upper Palermo Rd",
 "Lincoln Blvd",
 "Ophir Rd",
 "Lone Tree Rd",
 "Lower Wyandotte Rd",
 "Foothill Blvd",
 "Mt Ida Rd",
 "Oakvale Ave",
 "Glen Dr",
 "Canyon Dr",
 "Oro Dam Blvd E",
 "Oroville Dam Blvd E",
 "Royal Oaks Dr",
 "Kelly Ridge Rd",
 "Butte Creek Flat Rd",
 "Bull Hill Rd",
 "State Hwy 70"]

# Load the shapefile as a geodataframe
tigerlines = gpd.read_file("tl_2018_06007_roads.shp")

# Create new geodataframe to store Ingress/Egress routes from TIGER/LINE data
evac = gpd.GeoDataFrame()

# Iterate through TIGER/LINE data to pull out the needed routes
for index, road in tigerlines.iterrows():
	if road['FULLNAME'] in routes:
		evac = evac.append(road)

# Check to see if any Ingress/Egress routes listed above were missed in the iteration
# Not confident this works.....
print(evac[~evac.FULLNAME.isin(routes)])
print(evac.head())
# Write evac geodataframe to shape file
#evac.to_file("tl_2018_Egress.shp")

