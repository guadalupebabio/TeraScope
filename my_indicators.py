# 
# This script generates the indicators later deployed in TeraScope_Deploymet.py
# 
# Input:
#   * Data/Databysquare.csv 
# 
# Output:
#   * Energy_related_Indicators (Access_to_Energy, Impact_Solar_Panel, Impact_Nuclear_Battery)
#       

import pandas as pd
import numpy as np
import json
from brix import Indicator

class Energy_related_Indicators(Indicator):
  '''
  This function comprises any heatmap or indicator related with Energy
  '''
  def setup(self):
    '''
    Common to all
    '''
    self.requires_geometry = True
    self.datframe_bysquare = None
    self.wgs84 = 'EPSG:4326'

    self.indicator_type = 'heatmap' #cjeck if we can delete this one    

    '''
    Impact_Solar_Panel
    '''
    self.Cosumption_Person = 5000 #kW that a person uses
    self.SolarPanel = 25000 #Energy released by that tech
    self.SolarPanel_Access_POB = self.SolarPanel / self.Cosumption_Person #number of people that have access to energy with one solar pannel (one square)

    self.geogrid_data_df = None
    self.geogrid_data_graph = None

  def load_module(self):
    datframe_bysquare = pd.read_csv('Data/Databysquare.csv')
    self.datframe_bysquare_E = datframe_bysquare[['id','POB_W_ELEC']] #data for 
    self.datframe_bysquare_SP = datframe_bysquare[['id','POBTOT','POB_WO_ELEC']]


  def return_indicator(self, geogrid_data):
    '''
    This is the main course of your indicator.
    This function takes in `geogrid_data` and returns the value of your indicator.
    '''
    self.initialize_simulation(geogrid_data)
    
    cells_with_SP_energy,remaining_energy = self.propagate_solar_panel() #execute the function #remaining_energy for another heatmap
    cells_with_NB_energy = self.propagate_nuclear_battery()
    energy_access = self.return_EnergyAccess()
    

    # Create a shapefile with points in the center of each cell
    heatmap = geogrid_data.remove_noninteractive().as_df(include_geometries=True) #exclude non interative
    heatmap.geometry = heatmap.geometry.centroid #each poin of the heatmap is for the centroide of the cells 

    # Merge with layers
    heatmap = pd.merge(heatmap,cells_with_SP_energy)
    heatmap = pd.merge(heatmap,energy_access)

    # Select relevant collumns
    heatmap = heatmap[['Accesibility_Solar_Panel','Access_to_Energy','geometry']]

    # Convert to json and export
    heatmap = json.loads(heatmap.to_json())
    return heatmap 

  def return_EnergyAccess(self):
    out = self.datframe_bysquare_E[['id','POB_W_ELEC']].rename(columns={'POB_W_ELEC':'Access_to_Energy'})
    return out

  def initialize_simulation(self, geogrid_data):
    self.geogrid_data_df = geogrid_data.as_df() #creates a dataframe
    if self.geogrid_data_graph is None:
      self.geogrid_data_graph = geogrid_data.as_graph() #creates a graph

  def propagate_solar_panel(self,energy_name='Electricty_SolarPanel',quietly=False):
    '''
    This function takes geogrid_data and identifies the cells with Electricty_SolarPanel. Provides enegy to the column POB_WO_ELEC, first to the cells with a solar panel assigned, and then to its neighbors (using brix function ''neighbors = neighbors|set(geogrid_data_graph.neighbors(i))'').
    '''
    geogrid_data_df = self.geogrid_data_df
    geogrid_data_graph = self.geogrid_data_graph
    geogrid_data_df.loc[geogrid_data_df['name']==energy_name,'POB_E_SP'] = self.SolarPanel_Access_POB #assign SolarPanel_Access_POB to all the rows that have solar panels
    geogrid_data_df = pd.merge(geogrid_data_df,self.datframe_bysquare_SP,how='left').fillna(0) #it merges both df keeping the lenght of the left one, it assigns 0 to the element  Na
    
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
        remaining_energy = SP_energy_for_neigh-spent_energy
        if remaining_energy>0:
          new_energy_id = geogrid_data_df_neighs[geogrid_data_df_neighs['POB_WO_ELEC_OUT_CUMSUM'] > SP_energy_for_neigh]['id'].values[0]
          geogrid_data_df.loc[geogrid_data_df['id']==new_energy_id,'POB_WO_ELEC_OUT'] += -1*remaining_energy
          spent_energy = SP_energy_for_neigh
      geogrid_data_df['POB_W_ELEC_OUT']  = geogrid_data_df['POB_WO_ELEC'] - geogrid_data_df['POB_WO_ELEC_OUT']
      geogrid_data_df.loc[geogrid_data_df['id']==i,'SP_energy_for_neigh'] = SP_energy_for_neigh-spent_energy #spare energy to print

    geogrid_data_df['Accesibility_Solar_Panel'] = geogrid_data_df['POB_W_ELEC_OUT']/geogrid_data_df['POBTOT'] #percentage of people in that cell that recieve energy from a solar panel
    geogrid_data_df['Accesibility_Solar_Panel'] = geogrid_data_df['Accesibility_Solar_Panel'].fillna(0)
    self.geogrid_data_df = geogrid_data_df
    remaining_energy = geogrid_data_df['SP_energy_for_neigh'].sum() #so far a print but will be another indicator
    out_df = geogrid_data_df[['id','Accesibility_Solar_Panel']] #reduce the output of the funcion to two columns
    return out_df,remaining_energy  
  
  def propagate_nuclear_battery (self,energy_name='Electricity_NuclearBatter',quietly=False):

    #has info from POB_WO_ELEC_OUT esta es a la que le tengo que dar!
  