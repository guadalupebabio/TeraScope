# type on terminal: source ~/myEnvs/tera/bin/activate
# to upgarde brix: pip install --upgrade git+https://github.com/CityScope/CS_Brix.git
# pip uninstall cs-brix
# To install a commit: pip install git+git://github.com/CityScope/CS_Brix.git@0aa8917d44c38a54b421569c75d9716134d548c8
#
# To install a branch: pip install git+https://github.com/CityScope/CS_Brix.git@hybrid_indicators
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
# #Sanitation = Access_to_Sanitation()

H.add_geogrid_data_update_function(collapse_technology)
H.add_indicators([
        Energy #, 
        #Sanitation, ect
])
# H.listen()
# print(H.update_package())
