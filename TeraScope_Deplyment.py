import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import shapely
import gdal
import pyproj
import folium
import numpy as np
from brix import Handler
import pygeos
import rtree 
import os

from my_indicators import Access_to_Energy,SolarPanel_Impact
from my_gridmodification import collapse_technology

Energy = Access_to_Energy()
#Sanitation = Access_to_Sanitation()

H = Handler('lomas', quietly=False)
H.add_geogrid_data_update_function(collapse_technology)
H.add_indicators([
        Energy,
        Sanitation
])
H.listen()