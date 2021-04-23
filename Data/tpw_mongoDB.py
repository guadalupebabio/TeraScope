# API call to MongoDB TPW data

# https://www.mongodb.com/blog/post/getting-started-with-python-and-mongodb
import pymongo

# pprint library is used to make the output look more pretty
from pprint import pprint

username = 'table-creator'
password = ''

def coordinate_format(coordinates):
	'''
	Changes coordinates to city scope format
	'''
	out_coordinates = []
	for c in coordinates:
		out_coordinates.append({"$numberDouble": str(c)})

	return out_coordinates

def get_mongo(settlement_name=None):
	'''
	This function calls the MongoDB server to access The Power of Without database. 
	If settlement name is given, data regarding that specific settlement is returned.
	If settlement name is None, data of all settlements in database is returned. 
	Data returned:
		- settlement name : type str
		- coordinates : type array
		- population : type int
		- accessToEnergy : type str
		- sourceOfEnergy : type str
	'''
	# set MongoDB connection URL 
	tpw_connection_URL = "mongodb+srv://"+username+":"+password+"@cluster0.d6pne.mongodb.net/the_power_of_without?authSource=admin&retryWrites=true&w=majority"
	# tpw_standard_URL = "mongodb://"+username+":"+password+"@cluster0.d6pne.mongodb.net/?authSource=admin"
	# connection_URL = mongodb+srv://cluster0.d6pne.mongodb.net/the_power_of_without"

	# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
	client = pymongo.MongoClient(tpw_connection_URL)

	# CHECK CONNECTION
	db = client.admin
	serverStatusResult=db.command("ServerStatus")
	pprint(serverStatusResult)

	# connect to collection in database [db = client.<collection>]
	# TPW:
	db = client.the_power_of_without

	## GET ALL SETTLEMENT COORDINATES ##
	if settlement_name is None:
		settlements_db = db.settlementdatas.find()
		
		all_settlements_data = {}
		for settlement in settlements_db:
			name = settlement['name']
			## GET SETTLEMENTS COORDINATES ##
			coordinates = settlement['geolocation']['coordinates']
			# fix format of coordinates
			# formatted_coordinates = coordinate_format(settlement_coordinates)
			## GET SETTLEMENTS POPULATION ##
			population = settlement['site']['origin']['population']
			## GET SETTLEMENT ACCESS TO & SOURCE ENERGY ##
			accessToEnergy = settlement['architecture']['infrastructure']['accessToEnergy']
			sourceOfEnergy = settlement['architecture']['infrastructure']['sourceOfEnergy'][0]

			all_settlements_data[name] = {'coordinates': coordinates, 'population': population, 
				'accessToEnergy': accessToEnergy, 'sourceOfEnergy': sourceOfEnergy}
		print(all_settlements_data)
		return all_settlements_data

	## IF SETTLEMENT SPECIFIED ##	
	else:
		try:
			## GET SETTLEMENT COORDINATES ##
			settlement_name_data = db.settlementdatas.find_one({'name': settlement_name})
			# print(settlement_name_data)
			settlement_coordinates = settlement_name_data['geolocation']['coordinates']
			# fix format of coordinates
			# formatted_settlement_coordinates = coordinate_format(settlement_coordinates)
			## GET SETTLEMENT POPULATION ##
			settlement_population = settlement_name_data['site']['origin']['population']

			## GET SETTLEMENT ACCESS TO & SOURCE ENERGY ##
			settlement_accessToEnergy = settlement_name_data['architecture']['infrastructure']['accessToEnergy']
			settlement_sourceOfEnergy = settlement_name_data['architecture']['infrastructure']['sourceOfEnergy'][0]

			one_settlement_data = {'name': settlement_name, 'coordinates': settlement_coordinates, 'population': settlement_population, 
					'accessToEnergy': settlement_accessToEnergy, 'sourceOfEnergy': settlement_sourceOfEnergy}
			print(one_settlement_data)
			return one_settlement_data

		except:
			raise NameError('Settlement is not registered in the database.')

name = 'Lomas del Centinela, Zapopan'
get_mongo(name)

# get_mongo()
# ERROR when connecting to TPW : pymongo.errors.OperationFailure: bad auth : Authentication failed., full error: {'ok': 0, 'errmsg': 'bad auth : Authentication failed.', 'code': 8000, 'codeName': 'AtlasError'}

# https://docs.atlas.mongodb.com/troubleshoot-connection/#std-label-special-pass-characters
# https://docs.atlas.mongodb.com/troubleshoot-connection/#special-characters-in-connection-string-password
# https://docs.mongodb.com/master/reference/connection-string/#connections-standard-connection-string-format
# https://docs.atlas.mongodb.com/configure-api-access/#programmatic-api-keys
# Getting started w python and mongoDB: https://www.mongodb.com/blog/post/getting-started-with-python-and-mongodb