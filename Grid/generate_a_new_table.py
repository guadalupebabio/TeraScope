#
#This code will generate automatically tables from settlements registered in the PoW website
#
#Input :  Name of the table
# 
#Output : New table with the standard types 
#
# Forked from @doorleyr https://github.com/CityScope/CS_Grid_Maker/blob/master/examples/corktown_grid.py
#

import geopandas as gpd
import math 
import json
import os
import sys
import requests
import pymongo
from shapely.geometry.polygon import Polygon

table_name ='lomas' #name by default
table_name = input('What is the name of the table you want ot create? (copy paste the same name as appears in the map of informality)')


def find_if_table_exist(table_name):
    x = requests.get('http://cityio.media.mit.edu/api/tables/list')
    
    list_of_table=x.content.decode('utf-8')
    list_to_json = json.loads(list_of_table)
    
    for this_table in list_to_json:
        clean_table_name = this_table.replace('https://cityio.media.mit.edu/api/table/', '')
        if clean_table_name ==table_name:
            return True
    return False

#find if the table exists
if find_if_table_exist(table_name) == True:
  print(f'This table already exists, you can see it here: https://cityscope.media.mit.edu/CS_cityscopeJS/?cityscope={table_name}')
else:
  #table_name inputed when running this script
  rows = 20 #modify later
  columns = 20 #modify later
  latitude = 42.3664655
  longitude = -71.0854323
  rotation = 0
  cellSize = 50 #m2 set as default
  crs_epsg = 4326

  #API call to MongoDB TPW data
  username = "table-creator"
  password = getpass.getpass()
  tpw_connection_URL = f'mongodb+srv://{username}:{password}@cluster0.d6pne.mongodb.net/the_power_of_without?retryWrites=true&w=majority'
  client = pymongo.MongoClient(tpw_connection_URL) # connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
  # CHECK CONNECTION
  db = client.admin
  serverStatusResult=db.command("ServerStatus")
  print(serverStatusResult)
  ## GET ALL SETTLEMENT COORDINATES ##
  settlements_data = db.settlementdatas.find()
  settlement_coord_data = {}
  for settlement in settlements_data:
    name = settlement['name']
    coordinates = settlement['geolocation']['coordinates']
    settlement_coord_data[name] = coordinate
  ## GET SPECIFIC SETTLEMENT COORDINATES ##
  settlements_data = db.settlementdatas.find_one({'name': table_name})
  settlement_coordinates = settlements_data['geolocation']['coordinates']

  #Import from data base
  lat_point_list = [20.764781341419358, 20.76303528674933, 20.763215914030038, 20.762031797925214, 20.76134942171894,20.76124907201699,20.761430386498358,20.75675402210621, 20.756071622073794, 20.75657338710328, 20.756891146354917, 20.75557076509179, 20.757716955908744, 20.758852159932292, 20.7593438806329, 20.761691654649997, 20.76670887497622, 20.769215940307845, 20.769356147330143, 20.770700755657085, 20.771041923030506, 20.76811216984444, 20.765182062242182]
  lon_point_list = [-103.36270688388338,-103.36274981993364,-103.3615690785509,-103.36227752338053,-103.36176229077716,-103.36077476162069,-103.35710590345617,-103.35873747336686,-103.35841545298975, -103.36019729907642,-103.36146340784991,-103.36176355384579,-103.36681530234735,-103.36631873727687,-103.36723112834531,-103.36669703771352,-103.37101723758293,-103.36673933187646,-103.36523770894898,-103.36399256349084,-103.36373494718914,-103.3603015332957,-103.36216925148294]

  polygon_geom = Polygon(zip(lon_point_list, lat_point_list))
  crs = {'init': 'epsg:4326'} #this should work for most of the tables
  polygon = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[polygon_geom]) 

  bbox = polygon.bounds #creates the bounding box
  bb_width = #horizontal lenghth 
  bb_height = #vertical lenghth 
  columns = int(bb_width / math.sqrt(cellSize))
  rows = bb_height / math.sqrt(cellSize)

  #determine highest left corner
  bb_corners = list(bbox.exterior.coords)
  top_left_corner = bb_corners [1]
  top_left_lat,top_left_lon = top_left_corner

  new_grid = Grid(top_left_lon, top_left_lat, rotation,crs_epsg, cell_size, rows, columns) #creates a geogrid
  #new_grid.add_tui_interactive_cells(tui_top_left_row_index, tui_top_left_col_index,tui_num_interactive_rows, tui_num_interactive_cols) #what does it make?
  
  #load default types to the new table
  default_types=json.load(open('type_definitions/lomas_types.json'))
  geogrid['properties']['types']=default_types

  #Define the interactive part of the table
  default_type = 'No_Technology'
  for cell in geogrid['features']:
  cell_shape = shape(cell['geometry'])
  if not cell_shape.centroid.within(polygon_geom):
    cell['properties']['name']='Street_NoInteractive'
    cell['properties']['color'] = [0,0,0,0]
    cell['properties'].pop('interactive',None)
  else:
    cell['properties']['name'] = default_type
    cell['properties']['color'] = default_color_rgb
    cell['properties']['interactive'] = 'Web'

  #Initialized Geogriddata
  geogriddata=[]


  #Post to CityIO
  output_url='https://cityio.media.mit.edu/api/table/update/{}'.format(table_name)
  r = requests.post(output_url+'/GEOGRID', data = json.dumps(grid_geo))
  print('Geogrid:')
  print(r)

  #resetea geogrid data


#missing: bb_width, create a new table, make api call
#ronan already did it https://github.com/CityScope/CS_Grid_Maker/blob/master/examples/corktown_grid.py