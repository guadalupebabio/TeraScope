# TeraScope
TeraScope, an open-source module within the [CityScope] (https://github.com/CityScope) project that will allow local stakeholders to evaluate a range of possible technologies to better meet the unique needs of informal communities, without access to conventional infrastructure. 


# Activate the enviroment
on terminal: source ~/myEnvs/tera/bin/activate
What is an enviroment?  A virtual environment is a Python tool for dependency management and project isolation. It allows third party libraries to be installed locally in an isolated directory for a particular project.
How? [Here] (https://uoa-eresearch.github.io/eresearch-cookbook/recipe/2014/11/26/python-virtual-env/) 

# To run the code: python TeraScope_Deployment

# To create a table on the CityScope
-Opt 1: On the editor, https://cityscope.media.mit.edu/CS_cityscopeJS/#/editor (if you delete a type after you download without ‘recreate’ a new grid, it will crash)
-Opt 2: The script Grid/generate_a_new_tables.py created automatically a table from the settlements registered in the PoW website

# Edit table
The script Grid/edit_types.py edits the technologies with the types defined on lomas_types.json and modifies the layout of grid automatically. **Useful to add transparency to the types


# Quick Tricks
To Desinstall and install Brix: Bash reinstall_brix.sh
List installed packages: pip list
Upgrade package: pip install --upgrade PackageName
show: ls
open folder: cd
go back folder: cd -


# Explanation by file

/Data
api_mongoDB.py executed the API call to MongoDB to download TPW data
data_by_square.py tranforms geolocated data into the correspondant one of a square of the grid. In this case generates: Databysquare.csv
Databysquare.csv data that will be used for the simulation
manzanas.txt link to the folder that containf shp files

/Grid
type_definitions types that will be used in the simulation
edit_color.py change the color of the grid
edit_types.py edit types
generate_a_new_table.py create a table from the Monog DB
grid_lomas.json saves a copy of the table in case there are changes on CityIo
ids_non_interactive.json all the ids that shouldn't be interactive in lomas table

/Technologies
get_power.py This script runs power.py for every possible scenario
power.py This script calculates the energy generated by each technologies related to Power

informality_indicator.py calculares the value for the indicator, ideally it would be added to the setup function in my_indicators, so only would have to calculate the additional values inputed. Due to the time ocnstrain it will calculate everything for this iteration

my_gridmodification.py Defines the function that will take care of populating the impact of certain technologies across neighboring cells

TeraScope_Deployment.py runs the table
