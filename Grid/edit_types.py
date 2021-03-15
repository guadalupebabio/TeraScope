#
#Update the types of technologies I have in my table
#
#if it doesn't run try with the colab: https://colab.research.google.com/drive/1W81SI2i92brySznKS8_iEZBggr76BW1w?usp=sharing
# 

import json
import requests
from brix import Handler

table_name='lomas'
H = Handler(table_name,quietly=False)

default_type = 'No_Technology'
new_types=json.load(open('type_definitions/lomas_types.json'))
default_color_hex = new_types[default_type]['color'].lstrip('#')
default_color_rgb = list(int(default_color_hex[i:i+2], 16) for i in (0, 2, 4))

geogrid = H.get_GEOGRID()
geogrid['properties']['types']=new_types
for cell in geogrid['features']:
  if cell['properties']['name']!='Street_NoInteractive':
    cell['properties']['name'] = default_type
    cell['properties']['color'] = default_color_rgb
  else:
    cell['properties']['color'] = [0,0,0,0]

geogrid_out_fname = 'grid_lomas.json'
overwrite = input(f'Overwrite {geogrid_out_fname}? (y/n)')
if overwrite=='y':
  with open(geogrid_out_fname, 'w') as f:
    json.dump(geogrid, f)

r = requests.post(H.cityIO_post_url+'/GEOGRID', data = json.dumps(geogrid))
print(r)

H.reset_geogrid_data()
