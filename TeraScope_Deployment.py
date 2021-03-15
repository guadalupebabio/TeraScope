# type on terminal: source ~/myEnvs/tera/bin/activate
# to upgarde brix: pip install --upgrade git+https://github.com/CityScope/CS_Brix.git
# pip uninstall cs-brix
# pip install git+git://github.com/CityScope/CS_Brix.git@35e35a8051e118d184749e1feac7878bc75dc305
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
# print(H.update_package())