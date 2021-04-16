# API call to MongoDB TPW data

# https://www.mongodb.com/blog/post/getting-started-with-python-and-mongodb
import pymongo

# pprint library is used to make the output look more pretty
from pprint import pprint

username = 'acfiallo'
password = "MAS%21ELO%21UROP%212021"
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
db = client.settlementdatas

## GET ALL SETTLEMENT COORDINATES ##
settlements_data = db.settlementdatas.find()
settlement_coord_data = {}
for settlement in settlements_data:
	name = settlement['name']
	coordinates = settlement['geolocation']['coordinates']
	settlement_coord_data[name] = coordinates
print(settlement_coord_data)

## GET SPECIFIC SETTLEMENT COORDINATES ##
settlement_name = ""
settlements_data = db.settlementdatas.find_one({'name': settlement_name})
settlement_coordinates = settlements_data['geolocation']['coordinates']

# ERROR when connecting to TPW : pymongo.errors.OperationFailure: bad auth : Authentication failed., full error: {'ok': 0, 'errmsg': 'bad auth : Authentication failed.', 'code': 8000, 'codeName': 'AtlasError'}