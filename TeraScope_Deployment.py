# type on terminal: source ~/myEnvs/tera/bin/activate
#
# This script integrates the indicators and any modification of the grid
# 

from brix import Handler

from my_indicators import Energy_related_Indicators #Access_to_Sanitation, etc
from my_gridmodification import collapse_technology

Energy = Energy_related_Indicators()
# #Sanitation = Access_to_Sanitation()

H = Handler('lomas', quietly=False)
H.add_geogrid_data_update_function(collapse_technology)
H.add_indicators([
        Energy #, 
        #Sanitation, ect
])
H.listen()