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
from Technologies.power import get_solar_power, get_nuclear_energy #import a function from the file Power_Technologies
pd.options.mode.chained_assignment = None

class Energy_related_Indicators(Indicator):
  '''
  This function comprises any heatmap or indicator related with Energy
  '''
  def setup(self,cellSize=20,latitude=20.770724,longitude=-103.371491,scenario_set=['default']):
    '''
    Common to allsi
    '''
    self.requires_geometry = True
    self.datframe_bysquare = None
    self.wgs84 = 'EPSG:4326'

    self.indicator_type = 'hybrid'    

    self.geogrid_data_df = None
    self.geogrid_data_graph = None

    self.name = 'EnergyIndicators'
    
    self.Cosumption_Person = 10600 #kWh annual average in the U.S by eia

    '''
     Impact_Solar_Panel
    '''
    scenario_set = [0,1,2]
    self.SolarPanelDict = {scenario:get_solar_power(latitude, longitude, cellSize, scenario)["annual_generation_kWh"] for scenario in scenario_set} #this function request the value for PV calling the function #this is how it will look like self.SolarPanelDict   = {0:2500, 1:3000, 3:4000}
    self.current_scenario = scenario_set[0] #choose one scenario

    '''
    Impact_nuclear_reactor
    '''
    self.NuclearReactorDict = get_nuclear_energy(cellSize,scenario_set)["max_annual_generation_kWh"] #this function request the value for PV calling the function #this is how it will look like self.SolarPanelDict   = {0:2500, 1:3000, 3:4000}
    self.cells_with = {} #Create a dictionary
    self.remaining_energy = {} #Create a dictionary
    
  def set_current_scenario(self,geogrid_data):
    '''
    Define Current Scenario from the Grid
    '''
    time_cells = [886, 887, 888, 986, 987, 988, 1086, 1087, 1088] 
    future_cells = set([])
    geogrid_data_df = geogrid_data.as_df()

    ###### Test, assign all the cells the year 2050
    geogrid_data_df.loc[geogrid_data_df['id'].isin(time_cells),'name'] = '2050_Year'
    #######

    for i in time_cells:
      if geogrid_data_df.set_index('id').loc[i]['name'] == '2050_Year':
        future_cells.add(i)

    if len(future_cells) >= 5: #the majority of the cells are future_cells
      self.current_scenario = 1 #2050 scenario
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
  
  def NuclearReactor_Access_POB(self):
    '''
    This function calculate the amount of population that have access with a Nuclear Reactor for each scenario
    '''
    return self.NuclearReactorDict / self.Cosumption_Person

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
    cells_with_SP_energy,remaining_energy_SP = self.propagate_solar_panel() #execute the function #remaining_energy for another heatmap
    cells_with_NR_energy,remaining_energy_NR = self.propagate_nuclear_reactor()

    self.cells_with['cells_with_SP_energy']      = cells_with_SP_energy [['id','Accesibility_Solar_Panel']]
    self.cells_with['cells_with_SP_autonomy']    = cells_with_SP_energy [['id','Autonomy_Solar_Panel']]
    self.cells_with['cells_with_NR_energy']      = cells_with_NR_energy
    self.remaining_energy['remaining_energy_SP'] = remaining_energy_SP
    self.remaining_energy['remaining_energy_NR'] = remaining_energy_NR


  def return_indicator_heatmap(self, geogrid_data):
    energy_access = self.geogrid_data_df[['id','Access_to_Energy']]
    cells_with_SP_energy = self.cells_with['cells_with_SP_energy']
    cells_with_NR_energy = self.cells_with['cells_with_NR_energy']

    # Create a shapefile with points in the center of each cell
    heatmap = geogrid_data.remove_noninteractive().as_df(include_geometries=True) #exclude non interative #if this line is unomented remove include geometies from initialize()
    heatmap.geometry = heatmap.geometry.centroid #each poin of the heatmap is for the centroide of the cells 
    
    # Merge with layers
    heatmap = pd.merge(heatmap,cells_with_SP_energy)
    heatmap = pd.merge(heatmap,cells_with_NR_energy)
    heatmap = pd.merge(heatmap,energy_access)

    # Select relevant collumns
    heatmap = heatmap[['Accesibility_Solar_Panel','Accesibility_nuclear_reactor','Access_to_Energy','geometry']]
    print('Heatmap works!')
    # Convert to json and export
    heatmap = json.loads(heatmap.to_json())
    return heatmap
  
  def return_indicator_numeric(self, geogrid_data):
    radar =[
      {'name': 'Social Wellbeing', 'value': 0.3, 'viz_type': 'radar'}, # WIP
      {'name': 'Environmental Impact', 'value': 0.1, 'viz_type': 'radar'}, #WIP
      {'name': 'Access to Energy', 'value': self.geogrid_data_df['Access_to_Energy'].sum()/len(self.geogrid_data_df['Access_to_Energy']), 'viz_type': 'radar'},
      {'name': 'Autonomy', 'value': (self.geogrid_data_df['POB_W_ELEC_NR'].sum() + self.geogrid_data_df['POB_W_ELEC_SP'].sum() + self.geogrid_data_df['POB_W_ELEC_SP_Autonomy'].sum())/self.geogrid_data_df['POBTOT'].sum(), 'viz_type': 'radar'} 
    ]
    print('Radar works!')
    return radar

  def return_indicator_textual(self,geogrid_data):
    if self.current_scenario == 1:
      scenario_txt = '2050 scenario'
    else:
      scenario_txt = '2021 scenario'
    textual = [{
      'id': 787,
      'info': scenario_txt
    },{
      'id': 9249,
      'info': "This technology has increased the autonomy of Lomas"
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
    geogrid_data_df['Access_to_Energy'] = geogrid_data_df['POB_W_ELEC_percentage'] + geogrid_data_df['Accesibility_Solar_Panel'] + geogrid_data_df['Accesibility_nuclear_reactor']
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

  def propagate_solar_panel(self,energy_name='Power_SolarPanel',quietly=False):
    '''
    This function takes geogrid_data and identifies the cells with Electricty_SolarPanel. Provides enegy to the column POB_WO_ELEC, first to the cells with a solar panel assigned, and then to its neighbors (using brix function ''neighbors = neighbors|set(geogrid_data_graph.neighbors(i))'').
    '''
    geogrid_data_df = self.geogrid_data_df 

    if len(geogrid_data_df[geogrid_data_df['name']==energy_name])==0:
      print(f'WARNING: No {energy_name} found')
    geogrid_data_df.loc[geogrid_data_df['name']==energy_name,'POB_E_SP'] = self.SolarPanel_Access_POB() #assign SolarPanel_Access_POB to all the rows that have solar panels
    geogrid_data_df['POB_E_SP'] = geogrid_data_df['POB_E_SP'].fillna(0)
    # First iteration, give energy to those cells that don't have Energy
    simulated_energy = self.give_energy_cells_neighbors(geogrid_data_df, 'POB_E_SP', 'POB_WO_ELEC', no_iter =1)
    simulated_energy = simulated_energy.rename(columns={
      'free_energy_out_col': 'POB_E_SP',
      'lack_energy_out_col': 'POB_WO_ELEC_SP',
      'tech_energy_col':     'POB_W_ELEC_SP'
    })
    if len(simulated_energy)!=len(geogrid_data_df):
      raise NameError('give_energy_cells_neighbors() returned a dataframe with different cell number')
    geogrid_data_df = geogrid_data_df.drop(['POB_E_SP','POB_WO_ELEC_SP','POB_W_ELEC_SP'],1,errors='ignore')
    geogrid_data_df = pd.merge(geogrid_data_df,simulated_energy)

    # Second iteration, if there is spare energy, use it to gain autonomy in the cells
    if geogrid_data_df['POB_E_SP'].sum() > 0:
      simulated_energy = self.give_energy_cells_neighbors(geogrid_data_df, 'POB_E_SP', 'POB_W_ELEC',no_iter =1)
      simulated_energy = simulated_energy.rename(columns={
        'free_energy_out_col' : 'POB_E_SP_AfterAutonomy', #this will be remaining_energy_SP
        'tech_energy_col'     : 'POB_W_ELEC_SP_Autonomy' #this contributes to autonomy not energy
      }).drop('lack_energy_out_col',1)
      geogrid_data_df = geogrid_data_df.drop(['POB_E_SP_AfterAutonomy','POB_W_ELEC_SP_Autonomy'],1,errors='ignore')
      geogrid_data_df = pd.merge(geogrid_data_df,simulated_energy)
    else:
      geogrid_data_df[['POB_E_SP_AfterAutonomy','POB_W_ELEC_SP_Autonomy']]=0

    geogrid_data_df['Accesibility_Solar_Panel'] = geogrid_data_df['POB_W_ELEC_SP']/geogrid_data_df['POBTOT'] #percentage of people in that cell that recieve energy from a solar panel
    geogrid_data_df['Accesibility_Solar_Panel'] = geogrid_data_df['Accesibility_Solar_Panel'].fillna(0)
    geogrid_data_df['Autonomy_Solar_Panel'] = geogrid_data_df['POB_W_ELEC_SP_Autonomy']/geogrid_data_df['POBTOT'] #percentage of people in that cell that recieve energy from a solar panel
    geogrid_data_df['Autonomy_Solar_Panel'] = geogrid_data_df['Autonomy_Solar_Panel'].fillna(0)
    remaining_energy_SP = geogrid_data_df['POB_E_SP_AfterAutonomy'].sum() 
    out_SP_df = geogrid_data_df[['id','Accesibility_Solar_Panel', 'Autonomy_Solar_Panel']] #reduce the output of the funcion to two columns
    self.geogrid_data_df = geogrid_data_df.copy()
    return out_SP_df ,remaining_energy_SP   

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
  
  def propagate_nuclear_reactor (self,energy_name='Power_NuclearBattery',quietly=False):
    geogrid_data_df = self.geogrid_data_df
    geogrid_data_graph= self.geogrid_data_graph 

    if len(geogrid_data_df[geogrid_data_df['name']==energy_name])==0:
      print(f'WARNING: No {energy_name} found')
    
    geogrid_data_df.loc[geogrid_data_df['name']==energy_name,'POB_E_NR'] = self.NuclearReactor_Access_POB() #assign SolarPanel_Access_POB to all the rows that have solar panels
    geogrid_data_df['POB_E_NR'] = geogrid_data_df['POB_E_NR'].fillna(0)

    simulated_energy = self.give_energy_cells_neighbors(geogrid_data_df, 'POB_E_NR', 'POB_WO_ELEC_SP')
    simulated_energy = simulated_energy.rename(columns={
      'free_energy_out_col': 'POB_E_NR',
      'lack_energy_out_col': 'POB_WO_ELEC_NR',
      'tech_energy_col':     'POB_W_ELEC_NR'
    })
    if len(simulated_energy)!=len(geogrid_data_df):
      raise NameError('give_energy_cells_neighbors() returned a dataframe with different cell number')
    geogrid_data_df = geogrid_data_df.drop(['POB_E_NR','POB_WO_ELEC_NR','POB_W_ELEC_NR'],1,errors='ignore')
    geogrid_data_df = pd.merge(geogrid_data_df,simulated_energy)

    # Second iteration, if there is spare energy, use it to gain autonomy in the cells
    if geogrid_data_df['POB_E_SP'].sum() > 0:
      geogrid_data_df ['POB_W_ELEC_auto_SP'] = geogrid_data_df['POB_W_ELEC'] - geogrid_data_df['POB_W_ELEC_SP_Autonomy'] #POB with energy after the ones that recieved from SP
      simulated_energy = self.give_energy_cells_neighbors(geogrid_data_df, 'POB_E_NR', 'POB_W_ELEC')
      simulated_energy = simulated_energy.rename(columns={
        'free_energy_out_col' : 'POB_E_NR_AfterAutonomy', #this will be remaining_energy_SP
        'tech_energy_col'     : 'POB_W_ELEC_NR_Autonomy' #this contributes to autonomy not energy
      }).drop('lack_energy_out_col',1)
      geogrid_data_df = geogrid_data_df.drop(['POB_E_NR_AfterAutonomy','POB_W_ELEC_NR_Autonomy'],1,errors='ignore')
      geogrid_data_df = pd.merge(geogrid_data_df,simulated_energy)
    else:
      geogrid_data_df[['POB_E_NR_AfterAutonomy','POB_W_ELEC_NR_Autonomy']]=0

    geogrid_data_df['Accesibility_nuclear_reactor'] = geogrid_data_df['POB_W_ELEC_NR']/geogrid_data_df['POBTOT'] #percentage of people in that cell that recieve energy from a Nuclear Reactor
    geogrid_data_df['Accesibility_nuclear_reactor'] = geogrid_data_df['Accesibility_nuclear_reactor'].fillna(0)
    geogrid_data_df['Autonomy_nuclear_reactor'] = geogrid_data_df['POB_W_ELEC_NR_Autonomy']/geogrid_data_df['POBTOT'] #percentage of people in that cell that recieve energy from a solar panel
    geogrid_data_df['Autonomy_nuclear_reactor'] = geogrid_data_df['Autonomy_nuclear_reactor'].fillna(0)
    remaining_energy_NR = geogrid_data_df['POB_E_NR'].sum()
    out_NR_df = geogrid_data_df[['id','Accesibility_nuclear_reactor']] #reduce the output of the funcion to two columns
    self.geogrid_data_df = geogrid_data_df.copy()

    return out_NR_df,remaining_energy_NR  