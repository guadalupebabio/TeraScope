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
from brix import Grid_maker, normalize_table_name
from shapely.geometry.polygon import Polygon
from shapely.geometry import shape
from vincenty import vincenty

import os
import sys
sys.path.insert(0,os.path.join(os.path.abspath('../')))
from Data import get_mongo, coordinates_to_polygon #function that get data from Mongo DB

#from Data.api_mongoDB import get_mongo, coordinates_to_polygon #function that get data from Mongo DB

name = 'Lomas del Centinela, Zapopan' #'Lomas del Centinela, Zapopan'
# table_name = input('What is the name of the table you want ot create? (copy paste the same name as appears in the map of informality)')
table_name = brix.normalize_table_name(name)
print(f'table_name:{table_name}')

#find if the table exists
if brix.is_table(table_name) == True:   
  print(f'This table already exists, you can see it here: https://cityscope.media.mit.edu/CS_cityscopeJS/?cityscope={table_name}')
  new_table = input(f'Do you still want to create the table: {table_name}? (y/n)').lower() 

if  brix.is_table(table_name) == False or new_table == 'y': 

  ## MAKE API CALL TO MONGO DB ##
  settlement_data = get_mongo(name)
  settlement_polygon = coordinates_to_polygon(settlement_data['coordinates'])
  
  corner_bbox = settlement_polygon.bounds #lower left corner and upper right corner
  
  ## DEFINE PARAMETS OF THE GRID ##
  top_left_lat = corner_bbox[3] ## #42.3664655 
  top_left_lon = corner_bbox[0] ## #-71.0854323
  top_left = (top_left_lat,top_left_lon)

  top_right_lat = corner_bbox[3]
  top_right_lon = corner_bbox[2]
  top_right = (top_right_lat,top_right_lon)

  bottom_left_lat = corner_bbox[1]
  bottom_left_lon = corner_bbox[0]
  bottom_left = (bottom_left_lat,bottom_left_lon)

  dist_horizontal = vincenty(top_left, top_right)*1000 #in m
  dist_vertical = vincenty(top_left, bottom_left)*1000 #in m

  if dist_horizontal > dist_vertical:
    ncols = 20 ##
    cell_side = round(dist_horizontal / ncols)
    cell_size = cell_side #m ##
    nrows = round(dist_vertical / cell_side) ##

  else:
    nrows = 20 ##
    cell_side = round(dist_vertical / nrows)
    cell_size = cell_side #m ##
    ncols = round(dist_horizontal / cell_side) ##

  rotation = 0
  crs_epsg = '26917' # the previous one: 4326

  ## CREATE GEOGRID ##
  new_grid = Grid_maker(table_name, top_left_lat, top_left_lon, rotation=rotation, cell_size=cell_size, nrows=nrows, ncols=ncols)
  grid_geo = new_grid.get_grid_geojson() 
  print('GEOGRID works')

  ## EDIT TYPES ##
  types_location = 'type_definitions/lomas_types.json'
  new_types=json.load(open(types_location)) #loads the json with the types
  new_grid.edit_types(new_types)
  print('EDIT TYPES works')

  ## SET INTERACTIVE AREAS ##
  default_type = 'No_Technology'
  default_color_hex = new_types[default_type]['color'].lstrip('#')

  for cell in grid_geo['features']:
    cell_shape = shape(cell['geometry'])
    if not cell_shape.centroid.within(settlement_polygon):
      cell['properties']['name']='Street_NoInteractive'
      cell['properties']['color'] = [0,0,0,0]
      cell['properties'].pop('interactive',None)
    else:
      cell['properties']['name'] = default_type
      #cell['properties']['color'] = default_color_hex
      cell['properties']['interactive'] = 'Web'

  ## POST GRID TO CITY IO ##
  new_grid.commit_grid()
  print('POST GRID works')

  ## CHANGE OPACITY ## #not working
  H = Handler(table_name)
  H.set_opacity({'Street_NoInteractive':0}, default_alpha = 0.7)

  H.reset_geogrid_data()

  ## SAVE THE NEW GRID##
  geogrid_out_fname = 'grid_'+ table_name +'.json'
  save_json = input(f'Do you want to save your new table {geogrid_out_fname}? (y/n)')
  if save_json=='y':
    with open(geogrid_out_fname, 'w') as f:
      json.dump(grid_geo, f)
