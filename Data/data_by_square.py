# 
# This script generates the Databysquare.csv file
# 
# Input:
#   * Manzanas.shp: This file comes from https://www.inegi.org.mx/contenidos/masiva/indicadores/inv/14_Manzanas_INV2016_shp.zip
# 
# Output:
#   * Databysquare
# 

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from brix import Handler
import os

local_projection="EPSG:3621" #https://spatialreference.org/ref/epsg/3621/ 
wgs84="EPSG:4326"
######################## This part takes care of loading the Shapefile with the data by manzanas ########################

def load_shapefile_wrapper(local_projection):
  '''
  This function loads the shapefile and takes care of any missing values.
  '''
  shapefile = gpd.read_file("/content/drive/MyDrive/Colab Notebooks/new_manzanas/new_manzanas.shp")
  na_values = ['N.D.','*']
  str_cols = ['PROOCUP_C','ACESOPER_C','ACESOAUT_C','RECUCALL_C','SENALIZA_C','ALUMPUB_C','TELPUB_C','BANQUETA_C','GUARNICI_C','ARBOLES_C','RAMPAS_C','PUESSEMI_C','PUESAMBU_C']
  str_cols+= ['NOM_MUN','NOM_ENT','NOM_LOC','AGEB']
  for col in shapefile.drop(['geometry','CVEGEO'],1).columns:
    if col not in str_cols:
      shapefile.loc[shapefile[col].isin(na_values),col] = np.nan
      shapefile[col] = shapefile[col].astype(float)
  shapefile = shapefile.to_crs(local_projection)
  shapefile['AREA'] = shapefile.geometry.area #gets the area of each manzana
  return shapefile

shapefile = load_shapefile_wrapper(local_projection)

#Impute missing values for VIVTOT, VPH_C_ELEC, POBTOT
for colname in ['VIVTOT','VPH_C_ELEC','POBTOT']:
  density = (shapefile[~shapefile[colname].isna()][colname].sum()/shapefile[~shapefile[colname].isna()]['AREA'].sum())
  shapefile.loc[shapefile[colname].isna(),colname] = shapefile[shapefile[colname].isna()]['AREA']*density

#New variables density_POB_BY_VIV, VIV_W_ELEC, POB_W_ELEC
density_POB_BY_VIV = (shapefile['POBTOT']/shapefile['VIVTOT'])
shapefile['VIV_WO_ELEC'] = (shapefile['VIVTOT']-shapefile['VPH_C_ELEC'])
shapefile['POB_WO_ELEC'] = (shapefile['VIV_WO_ELEC'] * density_POB_BY_VIV)

shapefile[['CVEGEO',"VIVTOT",'VIV_WO_ELEC','POBTOT','POB_WO_ELEC','geometry']] #columns of the shapefile that I am interested on

######################## This part takes care of loading the geogrid from the table: lomas ########################

H = Handler('lomas', quietly=False)

#make sure table is connected
geogrid_data = H.get_geogrid_data(include_geometries=True,as_df=True,exclude_noninteractive=True)
geogrid_data = geogrid_data.set_crs(crs=wgs84)
geogrid_data = geogrid_data.to_crs(local_projection)

######################## join the two GeoDataFrames ########################
data_join = gpd.sjoin(geogrid_data[['id','geometry']], shapefile[['CVEGEO',"VIVTOT",'VIV_WO_ELEC','POBTOT','POB_WO_ELEC','geometry']], op='intersects') #geopandas.sjoin(left_df, right_df, how='inner', op='intersects', lsuffix='left', rsuffix='right')
data_join = pd.merge(data_join,shapefile[['CVEGEO','geometry']].rename(columns={'geometry':'shapefile_geometry'}))
data_join['intersected_area'] = [g1.intersection(g2).area for g1,g2 in data_join[['geometry','shapefile_geometry']].values]
data_join['area'] = [g.area for g in data_join['shapefile_geometry']] # area of block (shapefile)
data_join['fraction'] = data_join['intersected_area']/data_join['area'] # area of the intersection manzana with square
for colname in ["VIVTOT",'VIV_WO_ELEC','POBTOT','POB_WO_ELEC']:
  data_join[colname] = (data_join['fraction']*data_join[colname])

######################## create the Dataframe to be exported and add everything inside the same id ########################
datframe_bysquare = data_join.groupby('id').sum()[["VIVTOT",'POBTOT','POB_WO_ELEC']].reset_index()
datframe_bysquare[['POB_W_ELEC_NuclearBattery','POB_W_ELEC_SolarPanel']] = 0  #Columns to add so I can use when calculating accesibility
datframe_bysquare['POB_W_ELEC'] = datframe_bysquare['POBTOT']-datframe_bysquare['POB_WO_ELEC'] #create new column for POB_W_ELEC

out_directory = "Data" #review directory
if not os.path.exists(out_directory):
  os.makedirs(out_directory)
outpath = os.path.join(out_directory, 'Databysquare.csv')
datframe_bysquare.to_csv(outpath) 
