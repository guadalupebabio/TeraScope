#
#This code will generate automatically tables from settlements registered in the PoW website
#
#Input :  Name of the table
# 
#Output : New table with the standard types 
#
import geopandas as gpd

table_name ='lomas' #name by default
table_name = input('What is the name of the table you want ot create? (copy paste the same name as appears in the map of informality)')
#find if the table exists
if table_name in #how is called? :
  print(f'This table already exists, you can see it here: https://cityscope.media.mit.edu/CS_cityscopeJS/?cityscope={table_name}')
else:
  #table_name inputed when running this script
  rows = 20 #modify later
  columns = 20 #modify later
  latitude = 42.3664655
  longitude = -71.0854323
  cellSize = 50 #m2

  #Import from data base
  lat_point_list = [20.764781341419358, 20.76303528674933, 20.763215914030038, 20.762031797925214, 20.76134942171894,20.76124907201699,20.761430386498358,20.75675402210621, 20.756071622073794, 20.75657338710328, 20.756891146354917, 20.75557076509179, 20.757716955908744, 20.758852159932292, 20.7593438806329, 20.761691654649997, 20.76670887497622, 20.769215940307845, 20.769356147330143, 20.770700755657085, 20.771041923030506, 20.76811216984444, 20.765182062242182]
  lon_point_list = [-103.36270688388338,-103.36274981993364,-103.3615690785509,-103.36227752338053,-103.36176229077716,-103.36077476162069,-103.35710590345617,-103.35873747336686,-103.35841545298975, -103.36019729907642,-103.36146340784991,-103.36176355384579,-103.36681530234735,-103.36631873727687,-103.36723112834531,-103.36669703771352,-103.37101723758293,-103.36673933187646,-103.36523770894898,-103.36399256349084,-103.36373494718914,-103.3603015332957,-103.36216925148294]

  polygon_geom = Polygon(zip(lon_point_list, lat_point_list))
  crs = {'init': 'epsg:4326'}
  polygon = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[polygon_geom]) 

  #create bounding box
  columns = bb_width/raiz of cellSize
  rows = bb_height/raiz of cellSize
  #determine highest left corner
  left_corner = 
  latitude = left_corner_lat
  longitude = left_corner_lon

  #copy paset edit_types.py