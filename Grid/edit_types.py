#
#Update the types of technologies I have in my table
#
#if it doesn't run try with the colab: https://colab.research.google.com/drive/1W81SI2i92brySznKS8_iEZBggr76BW1w?usp=sharing
# 

import urllib
import json
import requests

table_name='lomas'

get_url='https://cityio.media.mit.edu/api/table/'+table_name
post_url='https://cityio.media.mit.edu/api/table/update/'+table_name

with urllib.request.urlopen(get_url+'/GEOGRID') as url:
  geogrid=json.loads(url.read().decode())
geogrid['properties'].keys()
geogrid['properties']['types']

new_types=json.load(open('type_definitions/lomas_types.json'))
geogrid['properties']['types']=new_types

r = requests.post(post_url+'/GEOGRID', data = json.dumps(geogrid))
r