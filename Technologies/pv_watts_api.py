import requests
import json


def pv_watts_get(sys_cap, lat, lon, array_type, time_frame='monthly', mod_type=1, losses=14.08, tilt=20, azimuth=180):
	'''
	requests GET API call to PV watts 
	parameters:
		api_key : str : my_api_key
		sys_cap : float : name plate capacity (kW), range 0.05-500000
		lat : float : latitude of location to use, range -90 to 90
		lon : float : longitude of location to use, range -180 to 180
		array_type : int : array type (0, 1, 2, 3, 4)
			0 = fixed - open rack (ground)
			1 = fixed - roof mounted (household roof)
			2 = 1-Axis
			3 = 1-Axis Backtracking
			4 = 2-Axis
		time_frame : str : granularity of the output response, monthly or hourly
		module_type : int : module type 
			0 = standard, crystalline silicon, 15% nominal efficiency, glass 
			1 = premium, crystalline silicon, 19% nominal  efficiency, glass with anti-reflective coating
			2 = thin film, thin film, 10% glass
		losses : float : percent system losses, range -5 to 99 
		tilt : float : tilt angle (degrees), range 0 to 90
		azimuth : float : azimuth angle (degrees), <360
		address : string : required if lat, lon are not specified

	returns json:
		ac_monthly : list : monthly AC system output (kWhac)
		poa_monthly : list : monthly plane of array irradiance values. (kWh/m2)
		dc_monthly : list : Monthly DC array output. (kWhdc)
		solrad_monthly : list : Monthly solar radiation values. (kWh/m2/day)
		ac_annual : float : Annual AC system output. (kWhac)
		solrad_annual : float : Annual solar radiation values. (kWh/m2/day)
		capacity_factor : float : The ratio of the system's predicted electrical output in 
			the first year of operation to the nameplate output, which is equivalent to the 
			quantity of energy the system would generate if it operated at its nameplate 
			capacity for every hour of the year. (AC-to-DC)

	API details: https://developer.nrel.gov/docs/solar/pvwatts/v6/#examples
	'''
	print('---------------------------------')
	print('Calling PV Watts')
	print('---------------------------------')
	# url creation for API get request
	nrel_url = "https://developer.nrel.gov"
	pvwatts_url = "/api/pvwatts/v6.json?"
	my_api_key = 'HL6NnxupaYwtWc2K8oJfwYkrsoJGRvGAaz2sfdBz'

	params = {
		"api_key": my_api_key, "system_capacity": sys_cap, 
	    "module_type": mod_type, "losses": losses, "array_type": array_type, 
	    "tilt": tilt, "azimuth": azimuth, "lat": lat, "lon":lon
	}

	# create url string with all desginated parameters
	url = nrel_url + pvwatts_url
	for key, value in params.items(): 
		url += key + "=" + str(value) + '&'

	# remove last '&'
	url = url[:-1]
	print('URL :', url)

	headers = {
	    'content-type': "application/x-www-form-urlencoded",
	    'cache-control': "no-cache"
	}

	# GET request to url 
	response = requests.request("GET", url, headers=headers)

	return response.json()

def get_solar_power_gen(lat, lon, area):
	'''
	this function will be called directly from Terascope Tool; will call the pv_watts_get function to get necessary solar data.
	paramters:
		lat : float : latitude of location to use, range -90 to 90
		lon : float : longitude of location to use, range -180 to 180
		area : float : area of covered space in terascope tool (m^2)
			- only 50% of the area will be assumed for solar power system installation
	returns:
		power generated with the following degrees of efficiency
			- today: 15%
			- next 10 yrs: 30%
			- next 50 yrs: 95%
	methods:
		lambda = power generated = (efficiency used in pv_watts) * (solar radition) * (some other factors)
		power generated w/increased efficiency = (lambda / (efficiency used in pv_watts)) * (increased efficiency) 
											   = (solar radition) * (some other factors) * (increased efficiency)
	'''

	# panel type = 210 W/m^2
	# divide by 1000 to convert to kW
	sys_cap = area*0.5*210/1000 

	# pv watts data of roof mounted system
	pv_watts_data = dict(pv_watts_get(sys_cap, lat, lon, array_type=1))
	print('---------------------------------')
	print('PV Watts Data')
	print('---------------------------------')
	print(pv_watts_data)
	
	# effiency used in PV watts 
	mod_types = {0: 0.15, 1: 0.19, 2: 0.1}
	current_eff = mod_types[int(pv_watts_data["inputs"]["module_type"])]
	print(current_eff)
	
	# 15% efficiency, generation (kWhac)
	annual_pv_gen_today = pv_watts_data["outputs"]["ac_annual"]
	monthly_pv_gen_today = pv_watts_data["outputs"]["ac_monthly"]

	# 30% efficiency, 10+ yrs from today, generation (kWhac)
	future10_eff = 0.3
	annual_pv_gen_future10 = round((pv_watts_data["outputs"]["ac_annual"]/current_eff)*future10_eff,2)
	monthly_pv_gen_future10 = [round((i/current_eff)*future10_eff,2) for i in pv_watts_data["outputs"]["ac_monthly"]]

	# 95% efficiency, 50+ yrs from today, generation (kWhac)
	future50_eff = 0.95
	annual_pv_gen_future50 = round((pv_watts_data["outputs"]["ac_annual"]/current_eff)*future50_eff,2)
	monthly_pv_gen_future50 = [round((i/current_eff)*future50_eff,2) for i in pv_watts_data["outputs"]["ac_monthly"]]

	results = {
		"system_capacity_kW":sys_cap, "lat": lat, "lon": lon,
		"today":{"annual_pv_gen_today":annual_pv_gen_today, "monthly_pv_gen_today":monthly_pv_gen_today}, 
		"future 10 years": {"annual_pv_gen_future10":annual_pv_gen_future10, "monthly_pv_gen_future10":monthly_pv_gen_future10}, 
		"future 50 years":{"annual_pv_gen_future50":annual_pv_gen_future50, "monthly_pv_gen_future50":monthly_pv_gen_future50}
		}

	print('---------------------------------')
	print('Solar Generation Results (kWhac)')
	print('---------------------------------')
	print(results)
	return results


#########################################################################
## EXAMPLE GET_SOLAR_POWER_GEN
#########################################################################
# area = 187900 # this is area of Jalisco /1000; area of Jalisco = 187.9 million m^2
# lat = 20.65
# lon = -103.26

# pv_generation = get_solar_power_gen(lat, lon, area)

###############################
# OUTPUT
###############################
# {'system_capacity_kW': 19729.5, 'lat': 20.65, 'lon': -103.26, 
# 	'today': 
		# {'annual_pv_gen_today': 35,569,416.0, 
		# 'monthly_pv_gen_today': [2908829.0, 2885999.25, 3518535.25, 3312188.25, 3169752.75, 2696853.0, 2736674.5, 2892661.5, 2708767.5, 3031611.25, 2907324.5, 2800213.5]}, 
# 	'future 10 years': 
		# {'annual_pv_gen_future10': 56,162,235.79, 
		# 'monthly_pv_gen_future10': [4592887.89, 4556840.92, 5555581.97, 5229770.92, 5004872.76, 4258188.95, 4321065.0, 4567360.26, 4277001.32, 4786754.61, 4590512.37, 4421389.74]}, 
# 	'future 50 years': 
		# {'annual_pv_gen_future50': 177,847,080.0, 
		# 'monthly_pv_gen_future50': [14544145.0, 14429996.25, 17592676.25, 16560941.25, 15848763.75, 13484265.0, 13683372.5, 14463307.5, 13543837.5, 15158056.25, 14536622.5, 14001067.5]}}


#########################################################################
## EXAMPLE PV_WATTS_GET
#########################################################################
# system_cap = 10
# array_type = 1
# lat = 20.65
# lon = -103.26

# pv_watts_data = pv_watts_get(system_cap, lat, lon, array_type)
# print(pv_watts_data)

###############################
# OUTPUT
###############################
# {
# 	"inputs":
# 	{
# 		"system_capacity":"10","module_type":"1","losses":"14.08","array_type":"1","tilt":"20","azimuth":"180","lat":"20.65","lon":"-103.26"},
# 	"errors":[],"warnings":[],"version":"1.0.2","ssc_info":
# 	{
# 		"version":45,"build":"Linux 64 bit GNU/C++ Jul  7 2015 14:24:09"},
# 	"station_info":
# 	{
# 		"lat":20.64999961853027,"lon":-103.2600021362305,"elev":1549.119995117188,"tz":-6.0,"location":"None","city":"","state":"Jalisco",
# 		"solar_resource_file":"W10326N2065.csv","distance":0},
# 	"outputs":
# 	{
# 		"ac_monthly":[1474.355102539062,1462.783935546875,1783.388549804688,1678.7998046875,1606.605224609375,1366.913696289062,1387.097900390625,
# 		1466.161010742188,1372.953491210938,1536.587890625,1473.593872070312,1419.303588867188],

# 		"poa_monthly":[196.4875793457031,197.8671112060547,243.4680023193359,227.9575347900391,223.7420806884766,187.5926361083984,186.331787109375,
# 		196.415283203125,183.4392852783203,207.0892028808594,197.8186950683594,190.9305877685547],

# 		"solrad_monthly":[6.338308811187744,7.0666823387146,7.853806495666504,7.598584651947021,7.217486381530762,6.253087997436523,6.010702610015869,
# 		6.335977077484131,6.11464262008667,6.680296897888184,6.593956470489502,6.159051418304443],

# 		"dc_monthly":[1534.945068359375,1523.952758789062,1861.529296875,1748.985229492188,1674.874633789062,1426.199951171875,1446.7060546875,
# 		1528.437255859375,1431.57470703125,1600.340942382812,1534.7978515625,1478.1357421875],

# 		"ac_annual":18028.54296875,

# 		"solrad_annual":6.685214996337891,

# 		"capacity_factor":20.58053016662598
# 	}
# }
