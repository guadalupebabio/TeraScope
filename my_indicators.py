from brix import Indicator
import pandas as pd
import numpy as np



class Access_to_Energy(Indicator):
  '''
  Percentage of population with access to Energy
  '''
  def setup(self):
    '''
    Here you will define the properties of your indicator.
    '''
    self.indicator_type = 'heatmap'
    self.requires_geometry = True
    self.datframe_bysquare = None
    self.name = 'Access_to_Energy' #Name of the indicator to be visualized in the interface
    self.wgs84 = 'EPSG:4326'

    self.name = 'SolarPanel_Impact'
    self.Cosumption_Person = 5000 #kW that a person uses
    self.SolarPanel = 25000 #Energy released by that tech
    self.SolarPanel_Access_POB = self.SolarPanel / self.Cosumption_Person #people with access to energy with the solar pannel


  def load_module(self):
    datframe_bysquare = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/new_Databysquare/new_Databysquare.csv')
    self.datframe_bysquare = datframe_bysquare[['id','POB_WO_ELEC']]

  def return_indicator(self,geogrid_data):
    self.return_SolarPanel(geogrid_data)
    self.return_EnergyAccess(geogrid_data)

  def return_EnergyAccess(self,geogrid_data):
    #electricity_cells = [cell for cell in geogrid_data if cell['name'].split('_')[0]=='Electricity']
    features = []
    for cell in geogrid_data:
      cell_value = self.datframe_bysquare[self.datframe_bysquare['id']==cell['id']]
      if len(cell_value)>0:
        feature = {}
        lat,lon = zip(*cell['geometry']['coordinates'][0])
        lat,lon = np.mean(lat),np.mean(lon)
        feature['geometry'] = {'coordinates': [lat,lon],'type': 'Point'}
        feature['properties'] = {self.name:cell_value['POB_W_ELEC'].values[0]}
        features.append(feature)
    out = {'type':'FeatureCollection','features':features}
    return out

  def return_SolarPanel(self, geogrid_data):
    '''
    This is the main course of your indicator.
    This function takes in `geogrid_data` and returns the value of your indicator.
    The library is flexible enough to handle indicators that return a number or a dictionary.
    '''
    cells_with_energy = self.propagate_solar_panel(geogrid_data,self.SolarPanel_Access_POB)
    return cells_with_energy

  def propagate_solar_panel(self,geogrid_data,SolarPanel_Access_POB,energy_name='Electricty_SolarPanel',quietly=True):
    '''
    This function takes geogrid_data and identifies the cells with Electricty_SolarPanel. Provides enegy to the column POB_WO_ELEC, first to the cells with a solar panel assigned, and then to its neighbors (using brix function ''neighbors = neighbors|set(geogrid_data_graph.neighbors(i))'').
    '''
    geogrid_data_df = geogrid_data.as_df()
    geogrid_data_graph = geogrid_data.as_graph()
    solarpanel_cells = geogrid_data_df[geogrid_data_df.name.isin([energy_name])] 
    energy_available = len(solarpanel_cells)*SolarPanel_Access_POB #in people
    energy_remaining = energy_available
    cells_with_energy = set(solarpanel_cells['id'])
    energy_remaining+= -self.datframe_bysquare[self.datframe_bysquare['id'].isin(cells_with_energy)]['POB_WO_ELEC'].sum()
    if not quietly:
      print(len(cells_with_energy),energy_remaining)

    new_energy_ids = set([''])
    while len(new_energy_ids)>0:
      neighbors = set([])
      for i in cells_with_energy:
        neighbors = neighbors|set(geogrid_data_graph.neighbors(i))
      neighbors = neighbors.difference(cells_with_energy)
      df_neighbors = self.datframe_bysquare[self.datframe_bysquare['id'].isin(neighbors)]
      df_neighbors = df_neighbors[df_neighbors['POB_WO_ELEC']>0]
      if df_neighbors['POB_WO_ELEC'].sum()<energy_remaining:
        new_energy_ids = neighbors
      else:
        df_neighbors['POB_WO_ELEC_SUM'] = df_neighbors['POB_WO_ELEC'].cumsum()
        new_energy_ids = set(df_neighbors[df_neighbors['POB_WO_ELEC_SUM']<=energy_remaining]['id'])
      cells_with_energy = cells_with_energy|new_energy_ids
      energy_remaining += -df_neighbors[df_neighbors['id'].isin(new_energy_ids)]['POB_WO_ELEC'].sum()
      if not quietly:
        print(len(cells_with_energy),energy_remaining,len(new_energy_ids),new_energy_ids)
  

class SolarPanel_Impact(Indicator):
  '''
  Percentage of population with access to Energy
  '''
  def setup(self):
    '''
    Here you will define the properties of your indicator.
    '''
    self.name = 'SolarPanel_Impact'
    self.Cosumption_Person = 5000 #kW that a person uses
    self.SolarPanel = 25000 #Energy released by that tech
    self.SolarPanel_Access_POB = self.SolarPanel / self.Cosumption_Person #people with access to energy with the solar pannel

  def load_module(self):
    '''
    This function is not strictly necessary, but we recommend that you define it if you want to load something from memory. It will make your code more readable.
    '''
    datframe_bysquare = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/new_Databysquare/new_Databysquare.csv')
    self.datframe_bysquare = datframe_bysquare[['id','POB_WO_ELEC']]

  def return_SolarPanel(self, geogrid_data):
    '''
    This is the main course of your indicator.
    This function takes in `geogrid_data` and returns the value of your indicator.
    The library is flexible enough to handle indicators that return a number or a dictionary.
    '''
    cells_with_energy = self.propagate_solar_panel(geogrid_data,self.SolarPanel_Access_POB)
    return cells_with_energy
          
  def propagate_solar_panel(self,geogrid_data,SolarPanel_Access_POB,energy_name='Electricty_SolarPanel',quietly=True):
    '''
    This function takes geogrid_data and identifies the cells with Electricty_SolarPanel. Provides enegy to the column POB_WO_ELEC, first to the cells with a solar panel assigned, and then to its neighbors (using brix function ''neighbors = neighbors|set(geogrid_data_graph.neighbors(i))'').
    '''
    geogrid_data_df = geogrid_data.as_df()
    geogrid_data_graph = geogrid_data.as_graph()
    solarpanel_cells = geogrid_data_df[geogrid_data_df.name.isin([energy_name])] 
    energy_available = len(solarpanel_cells)*SolarPanel_Access_POB #in people
    energy_remaining = energy_available
    cells_with_energy = set(solarpanel_cells['id'])
    energy_remaining+= -self.datframe_bysquare[self.datframe_bysquare['id'].isin(cells_with_energy)]['POB_WO_ELEC'].sum()
    if not quietly:
      print(len(cells_with_energy),energy_remaining)

    new_energy_ids = set([''])
    while len(new_energy_ids)>0:
      neighbors = set([])
      for i in cells_with_energy:
        neighbors = neighbors|set(geogrid_data_graph.neighbors(i))
      neighbors = neighbors.difference(cells_with_energy)
      df_neighbors = self.datframe_bysquare[self.datframe_bysquare['id'].isin(neighbors)]
      df_neighbors = df_neighbors[df_neighbors['POB_WO_ELEC']>0]
      if df_neighbors['POB_WO_ELEC'].sum()<energy_remaining:
        new_energy_ids = neighbors
      else:
        df_neighbors['POB_WO_ELEC_SUM'] = df_neighbors['POB_WO_ELEC'].cumsum()
        new_energy_ids = set(df_neighbors[df_neighbors['POB_WO_ELEC_SUM']<=energy_remaining]['id'])
      cells_with_energy = cells_with_energy|new_energy_ids
      energy_remaining += -df_neighbors[df_neighbors['id'].isin(new_energy_ids)]['POB_WO_ELEC'].sum()
      if not quietly:
        print(len(cells_with_energy),energy_remaining,len(new_energy_ids),new_energy_ids)