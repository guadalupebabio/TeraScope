# 
# This script runs the script power to get the values for each technology
# 

from power import get_solar_power, get_nuclear_energy, get_hydropower, get_geothermal_energy, get_hydrogen_energy #import functions from the file Power_Technologies

def get_technologies_values(cellSize=20,latitude=20.770724,longitude=-103.371491,poopulation = 5000):

    wgs84 = 'EPSG:4326'
    
    Cosumption_Person = 10600 #kWh annual average in the U.S by eia
    
    scenario_set = [0,1,2]

    #Solar panel
    SolarPanelDict = {scenario:get_solar_power(latitude, longitude, cellSize, scenario)for scenario in scenario_set} #this function request the value for PV calling the function #this is how it will look like self.SolarPanelDict   = {0:2500, 1:3000, 3:4000}

    #Nuclear reactor
    NuclearBatteryDict = {scenario:get_nuclear_energy(cellSize,scenario_set)for scenario in scenario_set} #this function request the value for PV calling the function #this is how it will look like self.SolarPanelDict   = {0:2500, 1:3000, 3:4000}

    #Hydropower #set river_size, now is just a placeholder
    HydropowerDict = {scenario:get_hydropower(scenario)for scenario in scenario_set}

    #Geothermal
    GeothermalDict = {scenario:get_geothermal_energy(poopulation, scenario)for scenario in scenario_set}

    #Hydrogen
    HydrogenDict = {scenario:get_hydrogen_energy(poopulation, scenario)for scenario in scenario_set}

    return SolarPanelDict, NuclearBatteryDict, HydropowerDict, GeothermalDict, HydrogenDict

sp, nb, hp, gt, hg = get_technologies_values()

# print(f'solar panel: {sp}')
# print(f'Nuclear reactor: {nb}')
# print(f'Hydropower: {hp}')
# print(f'Geothermal: {gt}')
print(f'Hydrogen: {hg}')
