import requests
import json


def pv_watts_get(sys_cap, lat, lon, array_type, time_frame='monthly', mod_type=0, losses=14.08, tilt=20, azimuth=180):
	'''
	requests GET API call to PV watts 
	returns json file of energy generation (monthly, hourly) in recent year
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
		module_type : int : module type (0 = standard, 1 = premium, 2 = thin film)
		losses : float : percent system losses, range -5 to 99 
		
		tilt : float : tilt angle (degrees), range 0 to 90
		azimuth : float : azimuth angle (degrees), <360
		address : string : required if lat, lon are not specified
	API details: https://developer.nrel.gov/docs/solar/pvwatts/v6/#examples
	'''
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
	print('URL', url)

	headers = {
	    'content-type': "application/x-www-form-urlencoded",
	    'cache-control': "no-cache"
	}

	# GET request to url 
	response = requests.request("GET", url, headers=headers)

	return response.text


#########################################################################
## EXAMPLE
#########################################################################
# system_cap = 10
# array_type = 0
# lat = 20.65
# lon = -103.26

# pv_watts_data = pv_watts_get(system_cap, lat, lon, array_type)
# print(pv_watts_data)
