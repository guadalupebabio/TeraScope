# type on terminal: source ~/myEnvs/tera/bin/activate
#
# Desinstall and install Brix: Bash reinstall_brix.sh
#
# This script integrates the indicators and any modification of the grid
# 

from brix import Handler

from my_indicators import Energy_related_Indicators #Access_to_Sanitation, etc
from my_gridmodification import collapse_technology

H = Handler('lomas', quietly=False)

# Another way to make: '**{k:H.get_table_properties()[k] for k in ['cellSize','latitude','longitude']}'
# props = H.get_table_properties()
# Energy = Energy_related_Indicators(
#         longitude=props['longitude'],
#         cellSize =props['cellSize'],
#         latitude =props['latitude']
# )
Energy = Energy_related_Indicators(
        **{k:H.get_table_properties()[k] for k in ['cellSize','latitude','longitude']}
)
#Sanitation = Access_to_Sanitation()

H.add_geogrid_data_update_function(collapse_technology)
H.add_indicators([
        Energy #, 
        #Sanitation, ect
])
H.listen()
# print(H.update_package())
