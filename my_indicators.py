# 
# This script generates the indicators later deployed in TeraScope_Deploymet.py Hi
# 
# Input:
#   * Data/Databysquare.csv 
# 
# Output:
#   * Energy_related_Indicators (Access_to_Energy, Impact_Solar_Panel, Impact_Nuclear_Battery)
#       
#get_solar_power_gen(lat, lon, area, scenario)

import pandas as pd
import numpy as np
import json
from brix import Indicator

class Energy_related_Indicators(Indicator):
  '''
  This function comprises any heatmap or indicator related with Energy
  '''
  def setup(self,cellSize=20,latitude=20.770724,longitude=-103.371491,scenario_set=[0]):
    '''
    Common to all
    '''
    self.requires_geometry = True
    self.datframe_bysquare = None
    self.wgs84 = 'EPSG:4326'

    self.indicator_type = 'hybrid'    

    self.geogrid_data_df = None
    self.geogrid_data_graph = None
    
    self.Cosumption_Person = 5000 #kW that a person uses



    '''
    Impact_Solar_Panel
    '''

    self.SolarPanelDict = {scenario:get_solar_power_gen(latitude, longitude, cellSize, scenario) for scenario in scenario_set} #va a correr para los escenarios que le de
    #self.SolarPanelDict   = {0:2500, 1:3000, 3:4000}
    self.current_scenario = scenario_set[0]

    self.SolarPanel = 25000 #Energy released by that tech
    self.SolarPanel_Access_POB = self.SolarPanel / self.Cosumption_Person #number of people that have access to energy with one solar pannel (one square)
    '''
    Impact_Nuclear_Battery
    '''
    self.NuclearBattery = 500000 #Energy released by that tech
    self.NuclearBattery_Access_POB = self.NuclearBattery / self.Cosumption_Person #number of people that have access to energy with one nuclear battery (one square)

def SolarPanel_Access_POB(self):
  return self.SolarPanelDict[self.current_scenario] / self.Cosumption_Person

  def load_module(self):
    datframe_bysquare = pd.read_csv('Data/Databysquare.csv')
    self.datframe_bysquare = datframe_bysquare[['id','POBTOT','POB_WO_ELEC','POB_W_ELEC']]


  def return_indicator_asdf(self, geogrid_data):
    self.initialize_simulation(geogrid_data)
    
    cells_with_SP_energy,remaining_energy_SP = self.propagate_solar_panel() #execute the function #remaining_energy for another heatmap
    cells_with_NB_energy,remaining_energy_NB = self.propagate_nuclear_battery()
    energy_access = self.return_EnergyAccess()
    

    # Create a shapefile with points in the center of each cell
    heatmap = geogrid_data.remove_noninteractive().as_df(include_geometries=True) #exclude non interative
    heatmap.geometry = heatmap.geometry.centroid #each poin of the heatmap is for the centroide of the cells 

    # Merge with layers
    heatmap = pd.merge(heatmap,cells_with_SP_energy)
    heatmap = pd.merge(heatmap,cells_with_NB_energy)
    heatmap = pd.merge(heatmap,energy_access)

    # Select relevant collumns
    heatmap = heatmap[['Accesibility_Solar_Panel','Accesibility_Nuclear_Battery','Access_to_Energy','geometry']]
    return heatmap 
  
  def return_indicator_heatmap(self, geogrid_data):
    heatmap = self.return_indicator_asdf(geogrid_data)
    # Convert to json and export
    heatmap = json.loads(heatmap.to_json())

    return heatmap
  
  def return_indicator_numeric(self, geogrid_data):
    radar =[
      {'name': 'Social Wellbeing', 'value': 0.3, 'viz_type': 'radar'}, # WIP
      {'name': 'Environmental Impact', 'value': 0.1, 'viz_type': 'radar'}, #WIP
      {'name': 'Access to Energy', 'value': self.geogrid_data_df['Access_to_Energy'].sum()/len(self.geogrid_data_df['Access_to_Energy']), 'viz_type': 'radar'}, 
      {'name': 'Autonomy', 'value': (self.geogrid_data_df['POB_W_ELEC_NB'].sum() + self.geogrid_data_df['POB_W_ELEC_OUT'].sum())/self.geogrid_data_df['POBTOT'].sum(), 'viz_type': 'radar'} 
    ]

    return radar

  def return_EnergyAccess(self):
    geogrid_data_df = self.geogrid_data_df
    geogrid_data_df['POB_W_ELEC_percentage'] = geogrid_data_df['POB_W_ELEC']/geogrid_data_df['POBTOT']
    geogrid_data_df['Access_to_Energy'] = geogrid_data_df['POB_W_ELEC_percentage'] + geogrid_data_df['Accesibility_Solar_Panel'] +geogrid_data_df['Accesibility_Nuclear_Battery']
    geogrid_data_df['Access_to_Energy'] = geogrid_data_df['Access_to_Energy'].fillna(0) #this shouldn't be 0, delete this line when Cris fix it
    out_AE_df = geogrid_data_df[['id','Access_to_Energy']]
    return out_AE_df

  def initialize_simulation(self, geogrid_data):
    geogrid_data_df = geogrid_data.remove_noninteractive().as_df() #creates a dataframe
    geogrid_data_df = pd.merge(geogrid_data_df,self.datframe_bysquare,how='left').fillna(0)
    # self.current_scenario = geogrid_data.current_scenario() # This is not yet implemented, and it depends on Ariel's good grace
    self.current_scenario = 0
    self.geogrid_data_df = geogrid_data_df.copy()
    if self.geogrid_data_graph is None:
      self.geogrid_data_graph = geogrid_data.as_graph() #creates a graph

  def propagate_solar_panel(self,energy_name='Electricity_SolarPanel',quietly=False):
    '''
    This function takes geogrid_data and identifies the cells with Electricty_SolarPanel. Provides enegy to the column POB_WO_ELEC, first to the cells with a solar panel assigned, and then to its neighbors (using brix function ''neighbors = neighbors|set(geogrid_data_graph.neighbors(i))'').
    '''
    geogrid_data_df = self.geogrid_data_df.copy()
    geogrid_data_graph = self.geogrid_data_graph
    if len(geogrid_data_df[geogrid_data_df['name']==energy_name])==0:
      print(f'WARNING: No {energy_name} found')

    geogrid_data_df.loc[geogrid_data_df['name']==energy_name,'POB_E_SP'] = self.SolarPanel_Access_POB() #assign SolarPanel_Access_POB to all the rows that have solar panels
     #it merges both df keeping the lenght of the left one, it assigns 0 to the element  Na
    
    #################### give energy to cells ####################
    geogrid_data_df['POB_WO_ELEC_OUT'] = geogrid_data_df['POB_WO_ELEC'] - geogrid_data_df['POB_E_SP'] 
    geogrid_data_df.loc[geogrid_data_df['POB_WO_ELEC_OUT']<0,'POB_WO_ELEC_OUT'] = 0 
    geogrid_data_df['POB_W_ELEC_OUT']  = geogrid_data_df['POB_WO_ELEC'] - geogrid_data_df['POB_WO_ELEC_OUT']
    geogrid_data_df['SP_energy_for_neigh'] = geogrid_data_df['POB_E_SP'] - geogrid_data_df['POB_W_ELEC_OUT'] #all the energy not used because it has extra will be for the neighbors
    #################### give energy to neighbor cells####################
    cells_with_spare_energy = set(geogrid_data_df[geogrid_data_df.SP_energy_for_neigh>0]['id']) #get ids for all those cells with a value diffent than 0
    for i in cells_with_spare_energy: 
      SP_energy_for_neigh = geogrid_data_df[geogrid_data_df['id']==i]['SP_energy_for_neigh'].sum() #energy to give by cell
      neighbors = set(geogrid_data_graph.neighbors(i)) #find neighs
      geogrid_data_df_neighs = geogrid_data_df[geogrid_data_df['id'].isin(neighbors)&(geogrid_data_df['POB_WO_ELEC_OUT']>0)].sort_values(by='POB_WO_ELEC_OUT',ascending=False) #local table of neighs. Order from higher to lower necessity
      geogrid_data_df_neighs['POB_WO_ELEC_OUT_CUMSUM'] = geogrid_data_df_neighs['POB_WO_ELEC_OUT'].cumsum() #sum of pob without electrivity to know where i can give energy

      new_energy_ids = set(geogrid_data_df_neighs[geogrid_data_df_neighs['POB_WO_ELEC_OUT_CUMSUM'] <= SP_energy_for_neigh]['id']) #ids of cells i can give energy
      spent_energy = geogrid_data_df[geogrid_data_df['id'].isin(new_energy_ids)]['POB_WO_ELEC_OUT'].sum() #how many energy i will speand according to POB_WO_ELEC_OUT
      geogrid_data_df.loc[geogrid_data_df['id'].isin(new_energy_ids),'POB_WO_ELEC_OUT'] = 0 #give them energy and add a 0 to those cells. 
      
      if len(new_energy_ids)!=len(geogrid_data_df_neighs): #check if all energy is spent
        remaining_energy_SP = SP_energy_for_neigh-spent_energy
        if remaining_energy_SP>0:
          new_energy_id = geogrid_data_df_neighs[geogrid_data_df_neighs['POB_WO_ELEC_OUT_CUMSUM'] > SP_energy_for_neigh]['id'].values[0]
          geogrid_data_df.loc[geogrid_data_df['id']==new_energy_id,'POB_WO_ELEC_OUT'] += -1*remaining_energy_SP
          spent_energy = SP_energy_for_neigh
      geogrid_data_df['POB_W_ELEC_OUT']  = geogrid_data_df['POB_WO_ELEC'] - geogrid_data_df['POB_WO_ELEC_OUT']
      geogrid_data_df.loc[geogrid_data_df['id']==i,'SP_energy_for_neigh'] = SP_energy_for_neigh-spent_energy #spare energy to print

    geogrid_data_df['Accesibility_Solar_Panel'] = geogrid_data_df['POB_W_ELEC_OUT']/geogrid_data_df['POBTOT'] #percentage of people in that cell that recieve energy from a solar panel
    geogrid_data_df['Accesibility_Solar_Panel'] = geogrid_data_df['Accesibility_Solar_Panel'].fillna(0)
    remaining_energy_SP = geogrid_data_df['SP_energy_for_neigh'].sum() #so far a print but will be another indicator
    out_SP_df = geogrid_data_df[['id','Accesibility_Solar_Panel']] #reduce the output of the funcion to two columns
    self.geogrid_data_df = geogrid_data_df.copy()
    return out_SP_df,remaining_energy_SP  
  
  def propagate_nuclear_battery (self,energy_name='Electricity_NuclearBattery',quietly=False):
    geogrid_data_df = self.geogrid_data_df
    geogrid_data_graph= self.geogrid_data_graph 

    if len(geogrid_data_df[geogrid_data_df['name']==energy_name])==0:
      print(f'WARNING: No {energy_name} found')

    geogrid_data_df['POB_WO_ELEC_OUT'] = 0 #creates a new column
    geogrid_data_df['POB_W_ELEC_OUT'] = geogrid_data_df['POB_W_ELEC_OUT'].fillna(0) #all the people that got energy from the solar panel
    geogrid_data_df['POB_WO_ELEC_OUT'] = geogrid_data_df['POB_WO_ELEC'] -geogrid_data_df['POB_W_ELEC_OUT']  #population that still needs energy
    geogrid_data_df['POB_W_ELEC_NB'] = 0 #initialize the column 'POB_W_ELEC_NB' with 0 values

    ########## Set the starting point for giving energy to neighbors
    nuclearbattery_cells = geogrid_data_df[geogrid_data_df.name.isin([energy_name])]
    cells_with_energy = set(nuclearbattery_cells['id']) 

    ########## Amount of energy to give to neighbors
    nuclear_battery_num = len(cells_with_energy) #number of nuclear batteries I have in my grid
    POB_E_NB = nuclear_battery_num * self.NuclearBattery_Access_POB #amount of people i can give energy to 

    # if not quietly:
      # print(f'BEFORE WHILE: cells_with_energy {cells_with_energy}, POB_E_NB {POB_E_NB}')

    ########## GOAL: Find the set of cells that I need to give energy to (neighbors of neighbors) while having energy_remaining
    new_energy_ids = set([''])
    while len(new_energy_ids)>0:
      neighbors = set([]) 
      for i in cells_with_energy: #start from the first nuclear battery item 
        neighbors = neighbors|set(geogrid_data_graph.neighbors(i))
      neighbors = neighbors.difference(cells_with_energy) #this removes duplicates
      df_neighbors = geogrid_data_df[geogrid_data_df['id'].isin(neighbors)]
      df_neighbors = df_neighbors[df_neighbors['POB_WO_ELEC_OUT']>0] #remove those who don't need energy
      #find out if we still have energy after giving to the current cells
      if df_neighbors['POB_WO_ELEC_OUT'].sum()<POB_E_NB: 
        new_energy_ids = neighbors #if yes, find new neighbors
      else:
        df_neighbors['POB_WO_ELEC_SUM'] = df_neighbors['POB_WO_ELEC_OUT'].cumsum() #new column with cumulative sum
        new_energy_ids = set(df_neighbors[df_neighbors['POB_WO_ELEC_SUM']<=POB_E_NB]['id']) #take ids of those who have less or equal values of POB_E_NB 
      cells_with_energy = cells_with_energy|new_energy_ids #join the two sets
      POB_E_NB += -df_neighbors[df_neighbors['id'].isin(new_energy_ids)]['POB_WO_ELEC_OUT'].sum()
    # cells_with_energy is the set of cells I need to give enery to
    # POB_E_NB is very close to zero, and is equivalent to the remaining energy

    # Goal: give energy to all cells in cells_with_energy
    geogrid_data_df.loc[geogrid_data_df['id'].isin(cells_with_energy),'POB_W_ELEC_NB'] = geogrid_data_df[geogrid_data_df['id'].isin(cells_with_energy)]['POB_WO_ELEC_OUT']#df_neighbors[df_neighbors['id'].isin(cells_with_energy),'POB_WO_ELEC_OUT'] #give the energy from WO to NB in the cells identifyed
    geogrid_data_df.loc[geogrid_data_df['id'].isin(cells_with_energy),'POB_WO_ELEC_OUT'] = 0 #those cells that recieved energy convert 'POB_WO_ELEC_OUT' to 0

    if not quietly:
      print('geogrid_data_df[POB_WO_ELEC_OUT]:, before we give this to POB_W_ELEC_NB')
      print(geogrid_data_df['POB_W_ELEC_NB'].sum())

    self.geogrid_data_df = geogrid_data_df

    remaining_energy_NB = POB_E_NB
    geogrid_data_df['Accesibility_Nuclear_Battery'] = geogrid_data_df['POB_W_ELEC_NB']/geogrid_data_df['POBTOT'] #percentage of people in that cell that recieve energy from a Nuclear Battery
    geogrid_data_df['Accesibility_Nuclear_Battery'] = geogrid_data_df['Accesibility_Nuclear_Battery'].fillna(0)
    out_NB_df = geogrid_data_df[['id','Accesibility_Nuclear_Battery']] #reduce the output of the funcion to two columns

    return out_NB_df,remaining_energy_NB  

