import h3
import os
import glob
import pandas as pd
from shapely.geometry import Polygon, Point
import geopandas as gpd

keep_columns = [
    'individualCount',
    'eventDate',
    'year', 'month', 'day', 'county', 'genus',
    'locality', 'decimalLatitude', 'decimalLongitude', 'species',
]

def add_geometry(row):
    points = h3.h3_to_geo_boundary(row, True)
    return Polygon(points)

oak_west, oak_south, oak_east, oak_north = -122.355881,37.691211,-122.113884,37.885426

# iterator for looping through the big csv
# this one is ~15 GB, too big for me to process in one shot with my personal computer
dfReader = pd.read_csv('/Volumes/blackSSD/witch_data/birds/dl.u59qez/occurrence.txt', 
                 sep='\t', usecols=keep_columns, chunksize=50000)

# function to get h3 hexagons for each occurrence of specified genus
# saves a file to specified location
# returns the total number of rows in the saved csv
def get_genus_h3(df, i, save_path, genus):
    file_name = f'{save_path}/{genus}_{i}.csv'

    df = df.dropna().copy() # get rid of rows where there isn't an individual count
    new_df = df[df['genus'] == genus].copy() # get the rows that are crow sightings specifically 

    # tessellate the crow data 
    new_df['h3_10'] = [h3.geo_to_h3(lat, lng, 10) for lat,lng 
                          in zip(new_df['decimalLatitude'], new_df['decimalLongitude'])]
    
    counts = pd.DataFrame(new_df.groupby('h3_10')['individualCount'].sum()).reset_index()
    counts['geometry'] = counts['h3_10'].apply(add_geometry)
    counts = gpd.GeoDataFrame(counts)
    counts = counts.set_crs(epsg=4326)
    
    counts = counts.cx[oak_west:oak_east, oak_south:oak_north].copy()
    counts.drop(columns=['geometry'])
    
    counts.to_csv(file_name)
    
    return new_df['individualCount'].sum()

# paths to save the csvs
crow_path = '/Volumes/blackSSD/oakland_data/crows/'

# keeping a count so I can know how big the resulting CSVs will end up being 
# (if I merge the little ones into a single big one)
crows_count = 0

# loop through the iterator -- I have a print statement that helps me keep faith that the program is running
# much like a child, I need to see immedate results
for i,df in enumerate(dfReader):
    # crows and ravens are in genus Corvus and European/American magpies are genus Pica
    crows = get_genus_h3(df, i, crow_path, 'Corvus')
    
    # update the total counter
    crows_count += crows
    
    # print so I know something is happening.. pleas sir I must see progress pls sir
    if (((i+1) % 5) == 0):
        print(f'{i}: {crows_count} crows', flush=True)
    
print('DONE WITH THE BIG CSV!!, on to saving.', flush=True)
print(f'{crows_count} crow occurrences', flush=True)

# get the files we saved and recombine them into a single CSV
files = os.listdir(crow_path)
dfs = [None] * len(files) # as much as possible, do not grow lists dynamically!! 

# get each file and add it to the list
for i,f in enumerate(files):
    dfs[i] = pd.read_csv(f'{crow_path}/{f}')
    
df = pd.concat(dfs) # merge these into a single data frame

del dfs # delete the list as we no longer need it

# clean up the column names
df = df.drop(columns=['Unnamed: 0'])

# group by the hexagons and get a count per hexagon
# this will significantly shrink the size of the file by combining records at the same hexagon
bird_counts = df.groupby('h3_10')['individualCount'].sum().reset_index()
bird_counts = bird_counts.rename(columns={'individualCount':'crows'})

# save this file in the local project
bird_counts.to_csv('./data/crow_counts.csv')

# finally, remove the temporary CSV files
for f in files:
    os.remove(f)
    
print('CROW DATA PROCESSED! YIPEE!', flush=True)
