# 
# This script modifies the grid of the table
#
#if it doesn't run try with the colab: https://colab.research.google.com/drive/1W81SI2i92brySznKS8_iEZBggr76BW1w?usp=sharing
# 

import urllib
import urllib.request
import json
import requests

table_name='lomas'
ids=json.load(open('ids_non_interactive.json'))

get_url='https://cityio.media.mit.edu/api/table/'+table_name
post_url='https://cityio.media.mit.edu/api/table/update/'+table_name

id_list=[ids[id] for id in ids]

with urllib.request.urlopen(get_url+'/GEOGRIDDATA') as url:
  geogriddata=json.loads(url.read().decode())  


for i_c, cell in enumerate(geogriddata):
  if i_c in id_list:
    # geogriddata[i_c]['interactive']=False #make interactive False
    geogriddata[i_c]['color']=[0,0,0,0] #change the color to transparent [0,0,0,0]

r = requests.post(post_url+'/GEOGRIDDATA', data = json.dumps(geogriddata))
r
