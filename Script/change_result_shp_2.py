import pandas as pd
import numpy as np
import geopandas as gpd
import os
import matplotlib.pyplot as plt

main = r'F:\lampang_2'
gdf_road = gpd.read_file(rf'{main}\shapefile\Road_Lampang.shp')
gdf_road.drop(columns= ['lane'], inplace = True)
gdf_grid = gpd.read_file(rf'{main}\shapefile\Grid_lampang.shp')
gdf_grid.to_crs('EPSG:4326', inplace = True)

pointid = pd.read_excel(rf'{main}\shapefile\excel_points_1.xlsx')
pointid.drop(columns = ['lane', 'end'], inplace= True)
pointid['Latitude'] = pointid['start'].str.split(',', expand=True)[1].str[:9]
pointid['Longigude'] = pointid['start'].str.split(',', expand=True)[0].str[:9]

lam = gpd.read_file(rf'{main}\shapefile\Lampang.shp')
lam.to_crs('EPSG:4326', inplace = True)

for data in os.listdir(rf'{main}\result_beat_new'):
    if data.endswith('.xlsx'):
        df = pd.read_excel(rf'{main}\result_beat_new\{data}', skipfooter=2)
        a = str(data)
        b = a.split('_')
        c = b[2]+b[3]+b[4]+b[5][:4]
        # =============================================================================
        # Removing Unnamed columns
        # =============================================================================
        for i in df.columns:
              
            if 'Unnamed' in i:
                df.drop(columns = i, inplace=True)
            else:
                continue

        # =============================================================================
        # Arrange of columns name
        # =============================================================================
        df['Origin'] = df['Origin'].str.replace(" ","")
        df['Origin'] = df['Origin'].str.replace("\t","")
        df['Origin'] = df['Origin'].str.replace("(","")
        df['Destination'] = df['Destination'].str.replace(" ","")
        df['Destination'] = df['Destination'].str.replace("\t","")
        df['Destination'] = df['Destination'].str.replace("(","")
        df['Latitude_use'] = df['Origin'].str.split(',', expand=True)[0]
        df['Longigude_use'] = df['Origin'].str.split(',', expand=True)[1]
        df['Latitude_1'] = df['Origin'].str.split(',', expand=True)[0].str[:9]
        df['Longigude_1'] = df['Origin'].str.split(',', expand=True)[1].str[:9]
        df = pd.merge(df, pointid, left_on = ['Latitude_1', 'Longigude_1'],
                      right_on = ['Latitude', 'Longigude'], how = 'right')
        
        for i in df.columns:
            df1 = df[['Latitude_use','Longigude_use', 'id']]
            df1.rename(columns= {'Latitude_use':'Latitude', 'Longigude_use':'Longigude'}, inplace= True)
            if (i == 'CO(g/hr)') |(i == 'HC(g/hr)') |(i == 'NOx(g/hr)') |(i == 'PM(g/hr)'):
                df1[i] = df[i]
                df_gdf = gpd.GeoDataFrame(df1, 
                                   geometry = gpd.points_from_xy(df1['Longigude'], df1['Latitude']))
                ESRI_WKT = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]'
                d = i.split('(')[0]
                df_gdf.to_file(filename = rf'{main}\point_result\{d}_{c}.shp', driver = 'ESRI Shapefile',crs = ESRI_WKT)
                df_gdf.drop(columns=['Latitude', 'Longigude',  'geometry'], inplace = True)
                df2 = pd.merge(gdf_road, df_gdf, left_on = 'id', right_on = 'id', how = 'left')
                df2.to_file(filename = rf'{main}\line_result\{d}_{c}.shp', driver = 'ESRI Shapefile',crs = ESRI_WKT)
                
                df3 = gpd.sjoin(gdf_grid, df2)
                df4 = df3.groupby('index_right').count()
                df4.drop(columns=['Id', 'geometry', i], inplace = True)
                df4.rename(columns={'id':'count'}, inplace = True)
                df5 = pd.merge(df3, df4, left_on= 'index_right', right_index=True, how='left')
                df5[i] = df5[i]/df5['count']
                df6 = df5.groupby(df5.index).sum()
                df6.drop(columns = ['Id', 'index_right', 'id',  'count'], inplace = True)
                df7 = pd.merge(gdf_grid, df6, left_index = True, right_index = True, how = 'left')
                df7.drop(columns = ['Id'], inplace=True)
                df7.to_file(filename = rf'{main}\grid_result\{d}_{c}.shp', driver = 'ESRI Shapefile',crs = ESRI_WKT)
                
                # =============================================================================
                # Plotting figure                
                # =============================================================================
                fig, ax = plt.subplots(figsize=(30,20), dpi=200)
                plt.rcParams['font.size'] = '24'
                
                if d == 'CO':
                    vmax = 3600
                elif d == 'HC':
                    vmax = 650
                elif d == 'NOx':
                    vmax = 950
                elif d == 'PM':
                    vmax = 100
                else:
                    vmax = 0
                
                df7.plot(column=i,
                           ax=ax,
                           vmax=vmax,
                           legend=True)#, cmap='YlOrRd'
                
                gdf_grid.plot(ax=ax, color='none', edgecolor='whitesmoke')
                lam.plot(ax=ax, color='none', edgecolor='red')
                ax.set_title(f'{d}_{c[:8]}_{c[-4:-2]}:{c[-2:]}(g/hr)');
                ax.set_xlim([99.30, 99.78])
                ax.set_ylim([18.18, 18.62])
                fig.savefig(rf'{main}\figure_result_new\{d}_{c}.png', bbox_inches = 'tight')
                
        print(f'==========================Finish on {c}==========================')


                
            
    
    
    
    
    
    
    
    