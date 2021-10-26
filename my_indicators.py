# 
# This script generates the indicators later deployed in TeraScope_Deploymet.py 
# 
# Input:
#   * Data/Databysquare.csv 
# 
# Output:
#   * Energy_related_Indicators (Access_to_Energy, Impact_Solar_Panel, Impact_nuclear_reactor)
#       


import pandas as pd
import numpy as np
import json
from brix import Indicator
from Technologies.power import get_solar_power, get_nuclear_energy, get_hydropower, get_geothermal_energy, get_hydrogen_energy #import a function from the file Power_Technologies
pd.options.mode.chained_assignment = None

class Energy_related_Indicators(Indicator):
  '''
  This function comprises any heatmap or indicator related with Energy
  '''
  def setup(self,cellSize=20,latitude=20.770724,longitude=-103.371491,poopulation = 5000,scenario_set=['default']):
    '''
    Common to all si
    '''
    self.requires_geometry = True
    self.datframe_bysquare = None
    self.wgs84 = 'EPSG:4326'

    #poopulation = 5000 #get it from datframe_bysquare

    self.indicator_type = 'hybrid'    

    self.geogrid_data_df = None
    self.geogrid_data_graph = None

    self.name = 'EnergyIndicators'
    
    self.Cosumption_Person = 10600 #kWh annual average in the U.S by eia
    
    self.technology_properties_lookup = {
      'Power_SolarPanel': {
        'abbreviation': 'SP',
        'propagation_steps': 1
      },
      'Power_NuclearBattery': {
        'abbreviation': 'NB',
        'propagation_steps': None
      },
      'Power_Hydropower': {
        'abbreviation': 'Hp',
        'propagation_steps': None
      },
      'Power_Geothermal': {
        'abbreviation': 'G',
        'propagation_steps': None
      },
      'Power_Hydrogen': {
        'abbreviation': 'Hg',
        'propagation_steps': None
      }
    }
    self.cells_with = {} #Create a dictionary
    self.remaining_energy = {} #Create a dictionary
    
    scenario_set = [0,1,2]
    self.current_scenario = scenario_set[0] #choose one scenario
    '''
     Impact on the technologies
    '''
    #Solar panel
    self.SolarPanelDict = {scenario:get_solar_power(latitude, longitude, cellSize, scenario)["annual_generation_kWh"] for scenario in scenario_set} #this function request the value for PV calling the function #this is how it will look like self.SolarPanelDict   = {0:2500, 1:3000, 3:4000}

    #Nuclear reactor
    self.NuclearBatteryDict = get_nuclear_energy(cellSize,scenario_set)["max_annual_generation_kWh"] #this function request the value for PV calling the function #this is how it will look like self.SolarPanelDict   = {0:2500, 1:3000, 3:4000}

    #Hydropower #set river_size, now is just a placeholder
    self.HydropowerDict = {scenario:get_hydropower(scenario)["annual_generation_kWh"] for scenario in scenario_set} 

    #Geothermal
    self.GeothermalDict = {scenario:get_geothermal_energy(poopulation, scenario)["annual_generation_kWh"] for scenario in scenario_set} 

    #Hydrogen
    self.HydrogenDict = {scenario:get_hydrogen_energy(poopulation, scenario)["annual_generation_kWh"] for scenario in scenario_set} 

  def set_current_scenario(self,geogrid_data):
    '''
    Define Current Scenario from the Grid
    '''
    time_cells = [886, 887, 888, 986, 987, 988, 1086, 1087, 1088] 
    future_cells = set([])
    geogrid_data_df = geogrid_data.as_df()

    for i in time_cells:
      if geogrid_data_df.set_index('id').loc[i]['name'] == '2050_Year':
        future_cells.add(i)

    if len(future_cells) >= 5: #the majority of the cells are future_cells
      self.current_scenario = 2 #2050 scenario
      print('The user has set up the 2050 Scenario, welcome to the Future!!')
    else:
      self.current_scenario = 0 #2021 scenario
      print('The user has selected the 2021 Scenario.')
    
    return self.current_scenario

  def SolarPanel_Access_POB(self):
    '''
    This function calculate the amount of population that have access with each Solar panel created for each scenario
    '''
    return self.SolarPanelDict[self.current_scenario] / self.Cosumption_Person
  
  def NuclearBattery_Access_POB(self):
    '''
    This function calculate the amount of population that have access with a Nuclear Reactor for each scenario
    '''
    return self.NuclearBatteryDict / self.Cosumption_Person
  
  def Hydropower_Access_POB(self):
    '''
    This function calculate the amount of population that have access with Hydropower for each scenario
    '''
    return self.HydropowerDict[self.current_scenario] / self.Cosumption_Person

  def Geothermal_Access_POB(self):
    '''
    This function calculate the amount of population that have access with geothermal for each scenario
    '''
    return self.GeothermalDict[self.current_scenario] / self.Cosumption_Person
  
  def Hydrogen_Access_POB(self):
    '''
    This function calculate the amount of population that have access with Hydrogen for each scenario
    '''
    return self.HydrogenDict[self.current_scenario] / self.Cosumption_Person
  
  def Access_POB(self,energy_name):
    '''
    Calculate the amount of population that have access with given technology for each scenario
    '''
    if energy_name=='Power_SolarPanel':
      return self.SolarPanel_Access_POB()
    elif energy_name=='Power_NuclearBattery':
      return self.NuclearBattery_Access_POB()
    elif energy_name=='Power_Hydropower':
      return self.Hydropower_Access_POB()
    elif energy_name=='Power_Geothermal':
      return self.Geothermal_Access_POB()
    elif energy_name=='Power_Hydrogen':
      return self.Hydrogen_Access_POB()
    else:
      raise NameError('Unknown energy_name')

  def load_module(self):
    datframe_bysquare = pd.read_csv('Data/Databysquare.csv')
    self.datframe_bysquare = datframe_bysquare[['id','POBTOT','POB_WO_ELEC','POB_W_ELEC']]

  def return_indicator(self, geogrid_data):
    # run simulation
    self.run_simulation(geogrid_data)

    # intermediate calculations common to all indicators
    self.calculate_EnergyAccess() 
    # make indicators
    out = {}
    out['heatmap'] = self.return_indicator_heatmap(geogrid_data)
    out['numeric'] = self.return_indicator_numeric(geogrid_data)
    out['textual'] = self.return_indicator_textual(geogrid_data)
    return out

  def run_simulation(self, geogrid_data):
    self.initialize_simulation(geogrid_data)

    #create order of starting_column
    cells_with_SP_energy,remaining_energy_SP = self.propagate_technology('Power_SolarPanel')
    cells_with_NB_energy,remaining_energy_NB = self.propagate_technology('Power_NuclearBattery',starting_column='POB_WO_ELEC_SP')
    cells_with_Hp_energy,remaining_energy_Hp = self.propagate_technology('Power_Hydropower',starting_column='POB_WO_ELEC_NB')
    cells_with_G_energy,remaining_energy_G   = self.propagate_technology('Power_Geothermal',starting_column='POB_WO_ELEC_Hp')
    cells_with_Hg_energy,remaining_energy_Hg = self.propagate_technology('Power_Hydrogen',starting_column='POB_WO_ELEC_G')

    self.cells_with['cells_with_SP_energy']      = cells_with_SP_energy [['id','Accesibility_Power_SolarPanel']]
    self.cells_with['cells_with_NB_energy']      = cells_with_NB_energy [['id','Accesibility_Power_NuclearBattery']]
    self.cells_with['cells_with_Hp_energy']      = cells_with_Hp_energy [['id','Accesibility_Power_Hydropower']]
    self.cells_with['cells_with_G_energy']       = cells_with_G_energy [['id','Accesibility_Power_Geothermal']]
    self.cells_with['cells_with_Hg_energy']      = cells_with_Hg_energy [['id','Accesibility_Power_Hydrogen']]

    self.cells_with['cells_with_SP_autonomy']    = cells_with_SP_energy [['id','Autonomy_Power_SolarPanel']]
    self.cells_with['cells_with_NB_autonomy']    = cells_with_NB_energy [['id','Autonomy_Power_NuclearBattery']]
    self.cells_with['cells_with_Hp_autonomy']    = cells_with_Hp_energy [['id','Autonomy_Power_Hydropower']]
    self.cells_with['cells_with_G_autonomy']     = cells_with_G_energy [['id','Autonomy_Power_Geothermal']]
    self.cells_with['cells_with_Hg_autonomy']    = cells_with_Hg_energy [['id','Autonomy_Power_Hydrogen']]

    self.remaining_energy['remaining_energy_SP'] = remaining_energy_SP
    self.remaining_energy['remaining_energy_NB'] = remaining_energy_NB
    self.remaining_energy['remaining_energy_Hp'] = remaining_energy_Hp
    self.remaining_energy['remaining_energy_G']  = remaining_energy_G
    self.remaining_energy['remaining_energy_Hg'] = remaining_energy_Hg

  def return_indicator_heatmap(self, geogrid_data):
    energy_access = self.geogrid_data_df[['id','Access_to_Energy']]
    cells_with_SP_energy = self.cells_with['cells_with_SP_energy']
    cells_with_NB_energy = self.cells_with['cells_with_NB_energy']
    cells_with_Hp_energy = self.cells_with['cells_with_Hp_energy']
    cells_with_G_energy  = self.cells_with['cells_with_G_energy']
    cells_with_Hg_energy = self.cells_with['cells_with_Hg_energy']

    # Create a shapefile with points in the center of each cell
    heatmap = geogrid_data.remove_noninteractive().as_df(include_geometries=True) #exclude non interative #if this line is unomented remove include geometies from initialize()
    heatmap.geometry = heatmap.geometry.centroid #each poin of the heatmap is for the centroide of the cells 
    
    # Merge with layers
    heatmap = pd.merge(heatmap,cells_with_SP_energy)
    heatmap = pd.merge(heatmap,cells_with_NB_energy)
    heatmap = pd.merge(heatmap,cells_with_Hp_energy)
    heatmap = pd.merge(heatmap,cells_with_G_energy)
    heatmap = pd.merge(heatmap,cells_with_Hg_energy)
    heatmap = pd.merge(heatmap,energy_access)

    # Select relevant collumns
    heatmap = heatmap[['Access_to_Energy','Accesibility_Power_SolarPanel','Accesibility_Power_NuclearBattery','Accesibility_Power_Hydropower','Accesibility_Power_Geothermal','Accesibility_Power_Hydrogen','geometry']]
    #rename heatmap = heatmap.rename(dict)
    print('Heatmap works!')
    # Convert to json and export
    heatmap = json.loads(heatmap.to_json())
    return heatmap
  
  def return_indicator_numeric(self, geogrid_data):
    radar =[
      {'name': 'Social Wellbeing', 'value': 0.3, 'viz_type': 'radar'}, # WIP
      {'name': 'Environmental Impact', 'value': 0.1, 'viz_type': 'radar'}, #WIP
      {'name': 'Access to Energy', 'value': self.geogrid_data_df['Access_to_Energy'].sum()/len(self.geogrid_data_df['Access_to_Energy']), 'viz_type': 'radar'},
      {'name': 'Autonomy', 'value': (self.geogrid_data_df['POB_W_ELEC_NB'].sum() + self.geogrid_data_df['POB_W_ELEC_SP'].sum() + self.geogrid_data_df['POB_W_ELEC_SP_Autonomy'].sum())/self.geogrid_data_df['POBTOT'].sum(), 'viz_type': 'radar'} 
    ]
    print('Radar works!')
    return radar

  def return_indicator_textual(self,geogrid_data):
    if self.current_scenario == 2:
      scenario_txt = '2050 scenario'
    else:
      scenario_txt = '2021 scenario'
    textual = [{
      'id': 787,
      'info': scenario_txt
    },{
      'id': 9249,
      'info': ""
    }]
    print('Textual works!')
    return textual

  def calculate_EnergyAccess(self):
    '''
    Creates a new column in self.geogrid_data_df called 'Access_to_Energy' 
    '''
    geogrid_data_df = self.geogrid_data_df.copy() #working on a local copy
    geogrid_data_df['POB_W_ELEC_percentage'] = geogrid_data_df['POB_W_ELEC']/geogrid_data_df['POBTOT']
    geogrid_data_df['POB_W_ELEC_percentage'] = geogrid_data_df['POB_W_ELEC_percentage'].fillna(0)
    geogrid_data_df['Access_to_Energy'] = geogrid_data_df['POB_W_ELEC_percentage'] + geogrid_data_df['Accesibility_Power_SolarPanel'] + geogrid_data_df['Accesibility_Power_NuclearBattery']
    geogrid_data_df['Access_to_Energy'] = geogrid_data_df['Access_to_Energy'].fillna(0) 

    out_AE_df = geogrid_data_df[['id','Access_to_Energy']]
    self.geogrid_data_df = self.geogrid_data_df.drop('Access_to_Energy',1,errors='ignore')
    self.geogrid_data_df = pd.merge(self.geogrid_data_df,out_AE_df,how='left')

  def initialize_simulation(self, geogrid_data):
    self.set_current_scenario(geogrid_data) #this is the function that identifies what scenario is running
    geogrid_data_df = geogrid_data.remove_noninteractive().as_df() #creates a dataframe
    geogrid_data_df = pd.merge(geogrid_data_df,self.datframe_bysquare,how='left').fillna(0)
    geogrid_data_df.loc[geogrid_data_df['POB_WO_ELEC']<0,'POB_WO_ELEC'] = 0 
    self.geogrid_data_df = geogrid_data_df.copy()
    if self.geogrid_data_graph is None:
      self.geogrid_data_graph = geogrid_data.as_graph() #creates a graph

  def propagate_technology(self,energy_name,starting_column='POB_WO_ELEC',quietly=False):
    '''
    This function takes geogrid_data and identifies the cells with Electricty_SolarPanel. Provides enegy to the column POB_WO_ELEC, first to the cells with a solar panel assigned, and then to its neighbors (using brix function ''neighbors = neighbors|set(geogrid_data_graph.neighbors(i))'').
    '''

    technology_abbrev = self.technology_properties_lookup[energy_name]['abbreviation']
    no_iter = self.technology_properties_lookup[energy_name]['propagation_steps']
    geogrid_data_df = self.geogrid_data_df 

    if len(geogrid_data_df[geogrid_data_df['name']==energy_name])==0:
      print(f'WARNING: No {energy_name} found')
    geogrid_data_df.loc[geogrid_data_df['name']==energy_name,f'POB_E_{technology_abbrev}'] = self.Access_POB(energy_name) #assign SolarPanel_Access_POB to all the rows that have solar panels
    geogrid_data_df[f'POB_E_{technology_abbrev}'] = geogrid_data_df[f'POB_E_{technology_abbrev}'].fillna(0)
    # First iteration, give energy to those cells that don't have Energy
    simulated_energy = self.give_energy_cells_neighbors(geogrid_data_df, f'POB_E_{technology_abbrev}', starting_column, no_iter=no_iter)
    simulated_energy = simulated_energy.rename(columns={
      'free_energy_out_col': f'POB_E_{technology_abbrev}',
      'lack_energy_out_col': f'POB_WO_ELEC_{technology_abbrev}',
      'tech_energy_col':     f'POB_W_ELEC_{technology_abbrev}'
    })
    if len(simulated_energy)!=len(geogrid_data_df):
      raise NameError('give_energy_cells_neighbors() returned a dataframe with different cell number')
    geogrid_data_df = geogrid_data_df.drop([f'POB_E_{technology_abbrev}',f'POB_WO_ELEC_{technology_abbrev}',f'POB_W_ELEC_{technology_abbrev}'],1,errors='ignore')
    geogrid_data_df = pd.merge(geogrid_data_df,simulated_energy)

    # Second iteration, if there is spare energy, use it to gain autonomy in the cells
    if geogrid_data_df[f'POB_E_{technology_abbrev}'].sum() > 0:
      simulated_energy = self.give_energy_cells_neighbors(geogrid_data_df, f'POB_E_{technology_abbrev}', 'POB_W_ELEC',no_iter=no_iter)
      simulated_energy = simulated_energy.rename(columns={
        'free_energy_out_col' : f'POB_E_{technology_abbrev}_AfterAutonomy', #this will be remaining_energy_SP
        'tech_energy_col'     : f'POB_W_ELEC_{technology_abbrev}_Autonomy' #this contributes to autonomy not energy
      }).drop('lack_energy_out_col',1)
      geogrid_data_df = geogrid_data_df.drop([f'POB_E_{technology_abbrev}_AfterAutonomy',f'POB_W_ELEC_{technology_abbrev}_Autonomy'],1,errors='ignore')
      geogrid_data_df = pd.merge(geogrid_data_df,simulated_energy)
    else:
      geogrid_data_df[[f'POB_E_{technology_abbrev}_AfterAutonomy',f'POB_W_ELEC_{technology_abbrev}_Autonomy']]=0

    geogrid_data_df[f'Accesibility_{energy_name}'] = geogrid_data_df[f'POB_W_ELEC_{technology_abbrev}']/geogrid_data_df['POBTOT'] #percentage of people in that cell that recieve energy from a solar panel
    geogrid_data_df[f'Accesibility_{energy_name}'] = geogrid_data_df[f'Accesibility_{energy_name}'].fillna(0)
    geogrid_data_df[f'Autonomy_{energy_name}'] = geogrid_data_df[f'POB_W_ELEC_{technology_abbrev}_Autonomy']/geogrid_data_df['POBTOT'] #percentage of people in that cell that recieve energy from a solar panel
    geogrid_data_df[f'Autonomy_{energy_name}'] = geogrid_data_df[f'Autonomy_{energy_name}'].fillna(0)
    remaining_energy = geogrid_data_df[f'POB_E_{technology_abbrev}_AfterAutonomy'].sum() 
    out_df = geogrid_data_df[['id',f'Accesibility_{energy_name}', f'Autonomy_{energy_name}']] #reduce the output of the funcion to two columns
    self.geogrid_data_df = geogrid_data_df.copy()
    return out_df ,remaining_energy

  def give_energy_cells_neighbors(self, geogrid_data_df_raw, free_energy_col, lack_energy_col, no_iter=None):
    '''
    This function 

    Ensures that all cells with the technology have energy.
    If there is remaining energy, it propagates the energy to all neighbors.

    Parameters
    ----------
    geogrid_data_df_raw : pandas.DataFrame
      Table with 'id', free_energy_col, lack_energy_in_col
    free_energy_col : str
      This is the column with the "free-energy" (free-energy of a cell, is the energy it can give to its neighbors), measures in number of people
    lack_energy_col : str
      This is the number of people missing energy initially in each cell
    no_iter : int, defaults to None
      If provided, it will halt the simulation after no_iter neighbors. 
      Fore example, if no_iter=1, it will only propagate the energy to the first neighbors.
      If no_iter=None, it will stop when energy runs out or when cells run out. 

    Returns
    -------
    simulated_energy : pandas.DataFrame
      Table with four columns:
        id: Id of cell
        free_energy_out_col: Remainin free energy after simulation (this energy is wasted)
        lack_energy_out_col: This is the number people missing energy at the end in each cell
        tech_energy_col: This is the energy provided to each cell by the technology 
    '''
    geogrid_data_graph = self.geogrid_data_graph
    geogrid_data_df    = geogrid_data_df_raw[['id',free_energy_col,lack_energy_col]]

    free_energy_out_col = 'free_energy_out_col'
    lack_energy_out_col = 'lack_energy_out_col' # This is the number people missing energy at the end in each cell
    tech_energy_col     = 'tech_energy_col' # This is the energy provided to each cell by the technology 

    geogrid_data_df[free_energy_out_col] = geogrid_data_df[free_energy_col]

    #################### give energy to cells ####################
    geogrid_data_df[lack_energy_out_col] = geogrid_data_df[lack_energy_col] - geogrid_data_df[free_energy_out_col]
    geogrid_data_df.loc[geogrid_data_df[lack_energy_out_col]<0,lack_energy_out_col] = 0 
    geogrid_data_df[tech_energy_col] = geogrid_data_df[lack_energy_col] - geogrid_data_df[lack_energy_out_col]
    geogrid_data_df[free_energy_out_col] = geogrid_data_df[free_energy_out_col] - geogrid_data_df[tech_energy_col]

    #################### give energy to neighbor cells####################
    cells_with_spare_energy = set(geogrid_data_df[geogrid_data_df[free_energy_out_col]>0]['id']) #get ids for all those cells with a value diffent than 0
    for i in cells_with_spare_energy:
      cell_free_energy = geogrid_data_df[geogrid_data_df['id']==i][free_energy_out_col].sum() #energy to give by cell
      spent_free_energy = 0
      remaining_free_energy = cell_free_energy-spent_free_energy
      
      neighbors = set(geogrid_data_graph.neighbors(i)) #find neighs
      visited_neighbors = set([])
      iter_count = 0
      while (remaining_free_energy>0) and (len(neighbors)>0):
        geogrid_data_df_neighs = geogrid_data_df[geogrid_data_df['id'].isin(neighbors)].sort_values(by=lack_energy_out_col,ascending=False) #local table of neighs. Order from higher to lower necessity
        geogrid_data_df_neighs['CUMSUM'] = geogrid_data_df_neighs[lack_energy_out_col].cumsum() #sum of pob without electrivity to know where i can give energy

        new_energy_ids = set(geogrid_data_df_neighs[geogrid_data_df_neighs['CUMSUM'] <= remaining_free_energy]['id']) #ids of cells i can give energy
        spent_free_energy   = geogrid_data_df[geogrid_data_df['id'].isin(new_energy_ids)][lack_energy_out_col].sum() #how many energy i will speand according to WO_ELEC_after_tech
        geogrid_data_df.loc[geogrid_data_df['id'].isin(new_energy_ids),lack_energy_out_col] = 0 #give them energy and add a 0 to those cells. 
        remaining_free_energy = cell_free_energy-spent_free_energy

        if len(new_energy_ids)!=len(geogrid_data_df_neighs): # Check if all neighbors received energy
          if remaining_free_energy>0:
            new_energy_id = geogrid_data_df_neighs[geogrid_data_df_neighs['CUMSUM'] > remaining_free_energy]['id'].values[0]
            geogrid_data_df.loc[geogrid_data_df['id']==new_energy_id,lack_energy_out_col] += -1*remaining_free_energy
            spent_free_energy = remaining_free_energy
            remaining_free_energy = 0
        else:
          visited_neighbors = visited_neighbors|neighbors
          new_neighbors = set([])
          for j in neighbors:
            new_neighbors = new_neighbors|set(geogrid_data_graph.neighbors(j))
          new_neighbors = new_neighbors.difference(visited_neighbors)
          neighbors = new_neighbors
        if no_iter is not None:
          iter_count+=1
          if iter_count>=no_iter:
            break
      geogrid_data_df.loc[geogrid_data_df['id']==i,free_energy_out_col] = cell_free_energy-spent_free_energy #spare energy to print

    geogrid_data_df[tech_energy_col] = geogrid_data_df[lack_energy_col] - geogrid_data_df[lack_energy_out_col]

    return geogrid_data_df[['id',free_energy_out_col,lack_energy_out_col,tech_energy_col]]
  
