#
#This code will generate automatically tables from settlements registered in the PoW website
#
#Input :  Name of the table
# 
#Output : New table with the standard types 
#

import json
import os
import sys
import requests
import brix

import getpass
import pymongo
from pprint import pprint

from brix import Handler
from brix import Grid, edit_types, commit_grid
from shapely.geometry.polygon import Polygon
from shapely.geometry import shape

import os
import sys
sys.path.insert(0,os.path.join(os.path.abspath('../')))
from Data import get_mongo, coordinates_to_polygon #function that get data from Mongo DB

#from Data.api_mongoDB import get_mongo, coordinates_to_polygon #function that get data from Mongo DB

name = 'Samudayik Vikas Samiti, Delhi' #'Lomas del Centinela, Zapopan'
# table_name = input('What is the name of the table you want ot create? (copy paste the same name as appears in the map of informality)')
table_name = name.split()[0].lower() #only takes the first word and makes it lower case

#find if the table exists
if brix.is_table(table_name) == True:    #(table_name) == True :
  print(f'This table already exists, you can see it here: https://cityscope.media.mit.edu/CS_cityscopeJS/?cityscope={table_name}')
else:

    ## MAKE API CALL TO MONGO DB ##
    settlement_data = get_mongo(name)
    settlement_polygon = coordinates_to_polygon(settlement_data['coordinates'])
    
    corner_bbox = settlement_polygon.bounds #lower left corner and upper right corner
    
    ## DEFINE PARAMETS OF THE GRID ##
    #table_name inputed when running this script
    nrows = 20 
    ncols = 20 
    top_left_lat = corner_bbox[3] #42.3664655 
    top_left_lon = corner_bbox[0] #-71.0854323
    rotation = 0
    cell_size = 50 #m2 set as default #modify later
    crs_epsg = '26917' # the previous one: 4326

    ## CREATE GEOGRID ##
    new_grid = Grid(table_name,top_left_lon, top_left_lat, rotation, crs_epsg, cell_size, nrows, ncols)
    grid_geo = new_grid.get_grid_geojson() 
    print('GEOGRID works')

    ## SET INTERACTIVE AREAS ##

    ## EDIT TYPES ##
    types_location = 'type_definitions/lomas_types.json'
    new_types=json.load(open(types_location)) #loads the json with the types

    edit_types(grid_geo, new_types)
    print('EDIT TYPES works')

    ## POST GRID TO CITY IO ##
    commit_grid(table_name,grid_geo)
    print('POST GRID works')

    ## SAVE THE NEW GRID##
    geogrid_out_fname = 'grid_'+ table_name +'.json'
    save_json = input(f'Do you want to save your new table {geogrid_out_fname}? (y/n)')
    if save_json=='y':
      with open(geogrid_out_fname, 'w') as f:
        json.dump(grid_geo, f)
