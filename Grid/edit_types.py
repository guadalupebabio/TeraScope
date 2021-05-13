#
#Update the types of technologies I have in my table
#
#if it doesn't run try with the colab: https://colab.research.google.com/drive/1W81SI2i92brySznKS8_iEZBggr76BW1w?usp=sharing
# 
#error http://cityio.media.mit.edu/api/table/lomas/GEOGRID/properties/types are not updated!

import json
import requests
import shapely
from shapely.geometry.polygon import Polygon
from shapely.geometry import shape
from brix import Handler

table_name='lomas'
H = Handler(table_name,quietly=False)

#Polygon importred from PoW web
lat_point_list = [20.764781341419358, 20.76303528674933, 20.763215914030038, 20.762031797925214, 20.76134942171894,20.76124907201699,20.761430386498358,20.75675402210621, 20.756071622073794, 20.75657338710328, 20.756891146354917, 20.75557076509179, 20.757716955908744, 20.758852159932292, 20.7593438806329, 20.761691654649997, 20.76670887497622, 20.769215940307845, 20.769356147330143, 20.770700755657085, 20.771041923030506, 20.76811216984444, 20.765182062242182]
lon_point_list = [-103.36270688388338,-103.36274981993364,-103.3615690785509,-103.36227752338053,-103.36176229077716,-103.36077476162069,-103.35710590345617,-103.35873747336686,-103.35841545298975, -103.36019729907642,-103.36146340784991,-103.36176355384579,-103.36681530234735,-103.36631873727687,-103.36723112834531,-103.36669703771352,-103.37101723758293,-103.36673933187646,-103.36523770894898,-103.36399256349084,-103.36373494718914,-103.3603015332957,-103.36216925148294]
polygon_geom = Polygon(zip(lon_point_list, lat_point_list))

default_type = 'No_Technology'
timing_now_type = '2021'
timing_future_type = '2025'
new_types=json.load(open('type_definitions/lomas_types.json'))
print(new_types)

default_color_hex = new_types[default_type]['color'].lstrip('#')
default_color_rgb = list(int(default_color_hex[i:i+2], 16) for i in (0, 2, 4)) #doesn't work

#Assign the property 'Street_NoInteractive' to those cells outside the polygon
geogrid = H.get_GEOGRID()
geogrid['properties']['types']=new_types

time_cells = [886, 887, 888, 986, 987, 988, 1086, 1087, 1088] #cells that will edit the timing
for cell in geogrid['features']:
  cell_shape = shape(cell['geometry'])
  if not cell_shape.centroid.within(polygon_geom):
    if cell['properties']['id'] not in time_cells:
      cell['properties']['name']='Street_NoInteractive'
      cell['properties']['color'] = [0,0,0,0]
      cell['properties'].pop('interactive',None)
    else: #time_cells
      cell['properties']['name']= default_type #timing_now_type
      cell['properties']['color'] = default_color_hex
      cell['properties']['interactive'] = 'Web'
  else:
    cell['properties']['name'] = default_type
    cell['properties']['color'] = default_color_hex
    cell['properties']['interactive'] = 'Web'

# Save the geogrid created
geogrid_out_fname = 'grid_lomas.json'
overwrite = input(f'Overwrite {geogrid_out_fname}? (y/n)')
if overwrite=='y':
  with open(geogrid_out_fname, 'w') as f:
    json.dump(geogrid, f)

r = requests.post(H.cityIO_GEOGRID_post_url, data=json.dumps(geogrid), headers=Handler.cityio_post_headers)
print(r.url)
if r.status_code == 413:
  raise NameError('Package too large, exit status {r.status_code}')
print(r)

H.reset_geogrid_data()
