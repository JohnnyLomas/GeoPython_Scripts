#!/usr/bin/env python3

import geopandas
import sys

# Import vector file specified on commmand line 
shp = geopandas.read_file(sys.argv[1])

print(shp.head())

# Print uniques in the attribute column specified on command line
print(shp[sys.argv[2]].unique())