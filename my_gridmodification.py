def collapse_technology(geogrid_data):
  default_type = 'No_Technology'
  focus_type = 'Power_NuclearReactor'
  geogrid_data = geogrid_data.remove_noninteractive().as_df(include_geometries=True) 
  
  NuclearBattery_cells = geogrid_data[geogrid_data.name.isin([focus_type])] #the split doen't work
  if len(NuclearBattery_cells)>1:
    keep_ids = []
    patches = NuclearBattery_cells.unary_union
    if patches.geom_type == 'Polygon':
        patches = [patches]
    for tech_patch in patches:
      NuclearBattery_centroid = tech_patch.centroid
      keep_id = geogrid_data[geogrid_data.geometry.contains(NuclearBattery_centroid)]['id'].values
      if len(keep_id)!=0:
        keep_id = keep_id[0]
      else:
        raise NameError('Centroid is not inside any interactive cell.')
        # This means that there is not cell that contains the centroid (i.e. the centroid fell in a non-interaactive cell)
        pass 
      keep_ids.append(keep_id)
    geogrid_data.loc[geogrid_data['name']==focus_type,'name'] = default_type
    geogrid_data.loc[geogrid_data['id'].isin(keep_ids),'name'] = focus_type
  geogrid_data = geogrid_data[['color','height','id','name','interactive']]
  geogrid_data = [dict(row) for index,row in geogrid_data.iterrows()]
  return geogrid_data
