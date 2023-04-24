import pandas as pd
import numpy as np
import geopandas as gpd
import os
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

gdf_road = gpd.read_file('../Shapefile/road_ptt.shp')
gdf_grid = gpd.read_file('../Shapefile/PTT_Grid.shp')
gdf_grid.to_crs('EPSG:4326', inplace = True)
gdf_grid['Id'] = np.arange(0,gdf_grid.shape[0],1)
ptt = gpd.read_file('../Shapefile/prov_ปทุมธานี.shp')
ptt.to_crs('EPSG:4326', inplace = True)

pointid = gpd.read_file('../Shapefile/point_ptt.shp')
pointid['start'] = np.nan
pointid['Latitude'] = pointid['geometry'].y
pointid['Longigude'] = pointid['geometry'].x
pointid['start'] = pointid['Longigude'].astype(str) + ',' + pointid['Latitude'].astype(str)
pointid['Id'] = np.arange(0,pointid.shape[0],1)
pointid['Latitude'] = pointid['Latitude'].astype(str).str[:9]
pointid['Longigude'] = pointid['Longigude'].astype(str).str[:9]
pointid.rename(columns = {'Id':'id'}, inplace=True)

for data in os.listdir('../Data_Jas/'):
    if data.endswith('.xlsx'):
        df = pd.read_excel(rf'../Data_Jas/{data}', skipfooter=2)
        a = str(data)
        b = a.split('_')
        c = f'{b[3]}-{b[4]}-{b[5]}_{b[6][:2]}:00'
        e = f'{b[3]}{b[4]}{b[5]}_{b[6][:2]}00'
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
            # if (i == 'CO(g/hr)') |(i == 'HC(g/hr)') |(i == 'NOx(g/hr)') |(i == 'PM(g/hr)'):
            if i in ['CO(g/hr)', 'HC(g/hr)', 'NOx(g/hr)', 'PM(g/hr)', 'PM25(g/hr)', 'PM10(g/hr)', 'BC(g/hr)',
            'OC(g/hr)', 'NH3(g/hr)', 'CH4(g/hr)', 'VOC(g/hr)', 'SO2(g/hr)','CO2(g/hr)', 'N2O(g/hr)']:
                df1[i] = df[i]
                df_gdf = gpd.GeoDataFrame(df1, 
                                    geometry = gpd.points_from_xy(df1['Longigude'], df1['Latitude']))
                ESRI_WKT = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]'
                d = i.split('(')[0]
                # df_gdf.to_file(filename = rf'{main}\point_result\{d}_{c}.shp', driver = 'ESRI Shapefile',crs = ESRI_WKT)
                df_gdf.drop(columns=['Latitude', 'Longigude',  'geometry'], inplace = True)
                df2 = pd.merge(gdf_road, df_gdf, left_on = 'id', right_on = 'id', how = 'left')
                # df2.to_file(filename = rf'{main}\line_result\{d}_{c}.shp', driver = 'ESRI Shapefile',crs = ESRI_WKT)
                
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
                # df7.to_file(filename = rf'{main}\grid_result\{d}_{c}.shp', driver = 'ESRI Shapefile',crs = ESRI_WKT)
                
                # =============================================================================
                # Plotting figure                
                # =============================================================================
                fig, ax = plt.subplots(figsize=(30,20), dpi=200)
                plt.rcParams['font.size'] = '24'
                
                # if d == 'CO':
                #     vmax = 3600
                # elif d == 'HC':
                #     vmax = 650
                # elif d == 'NOx':
                #     vmax = 950
                # elif d == 'PM':
                #     vmax = 100
                # else:
                #     vmax = 0
                
                df7.plot(column=i,
                            ax=ax,
                            # vmax=vmax,
                            legend=True,
                            legend_kwds={
                            "shrink":.73
                        })#, cmap='YlOrRd'
                
                gdf_grid.plot(ax=ax, color='none', edgecolor='whitesmoke')
                ptt.plot(ax=ax, color='none', edgecolor='red')
                ax.set_title(f'{d}_{c}(g/hr)');
                ax.set_xlim([100.325, 100.96])
                ax.set_ylim([13.91, 14.29])
                fig.savefig(f'../Traffic_figure/{d}_{e}.png', bbox_inches = 'tight')
                #version1