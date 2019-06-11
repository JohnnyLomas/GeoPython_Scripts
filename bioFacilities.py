#!/usr/bin/env python3

import geopandas as gpd

# Import file to geopandas
biomass = gpd.read_file("/Users/34North/Desktop/Biomass_Facilities/wood_facility_database-sawmill.shp")

# Create new dataframe with only closed facilities 
biomassClosed = biomass[biomass.Status == 'Closed']

# Filter biomass facilities to exclude faciliites that are now closed 
biomassOperational = biomass[~biomass.Name.isin(biomassClosed.Name) & ~biomass.latitude.isin(biomassClosed.latitude) & ~biomass.longitude.isin(biomassClosed.longitude)]

##### Filter the operational facilities to include only the most recent entries for 
##### a name and a lat/long coordinate

# Create new dataframe to store most recent entries for operational facilities
BioRecentOps = gpd.GeoDataFrame()

# Create object to store a list of unique facility names
names = biomassOperational.Name.unique()

for name in names:
	tempDF = biomassOperational[biomassOperational.Name == name]
	tempDF.sort_values(by = 'Year', ascending = False, inplace = True)
	BioRecentOps = BioRecentOps.append(tempDF.iloc[[0]], ignore_index = True)

print(BioRecentOps.head())

# Write geodataframe to shapefile
BioRecentOps.to_file("WFD_Biomass_Sawmill.shp")