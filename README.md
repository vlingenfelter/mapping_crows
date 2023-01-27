# Mapping Crows in Oakland, CA

### Recreating my Python Environment

This project makes use of several great Python libraries. To recreate my environment, use conda to create an environment based on `environment.yml` in the project folder. I use conda-forge to download packages. 

## Data 

The preliminary dataset for this project is very large (14,936,795 rows in a single text file). I have this data stored on an external hard drive, which is referenced in the code. It contains all eBird records in the San Francisco Bay Area. To recreate this dataset, one could download a smaller subset from gbif (for example, using the boundaries for Oakland specified later in this document). 

Citation: GBIF.org (21 January 2023) GBIF Occurrence Download  https://doi.org/10.15468/dl.u59qez

### Assets for creating the crow map

There are several hand-drawn svgs in the `./assets` folder. These were created by me in Adobe Illustrator and are pulled into matplotlib as custom markers to generate the crow map. They are all single path SVGs. 

## The Code

This project required data cleaning, some brief data analysis, and then a custom visualization using matplotlib and Adobe Illustrator (or your favorite open source vector-based graphics editor). 

### Data Cleaning

The script to get crow counts is `get_crows.py`. The script to get counts for all birds is `get_all_bird_counts.py`. Each script does the following proceess:
- processes the very large CSV in more manageable (for my personal computer) chunks
- for the crow dataset: filters the data to records within the genus Corvus
- tesselates the data based on the latitude and longitude of each record to an hexagonal grid using Uber's H3 library (at a hexagon size 10, ~15,000 sq m per hexagon)
- counts how many records are tesselated to each hexagon
- clips the data to the following bounding box for the general Oakland area: (-122.355881,37.691211,-122.113884,37.885426)
- saves each chunk as a single CSV for reading and further processing later

At the of this process, the resulting CSVs are recombined and saved in `./data` as single files for the analysis and mapping steps.

To recreate how I ran these files exactly, run the following from the command line:

`python3 <FILENAME>.py > ./outputs/<FILENAME>.txt &`

This runs the file using Python 3, then saves the outputs to the specified file in the outputs folder of this project. The ampersand at the end of the command allows you to continue using the command line. 

### Data analysis & making the map

The final map shows the areas in the greater Oakland area that are in the top percentiles for crow sightings. "Top crow sightings" here is determined by the ratio of crow observances to total bird observances in each hexagon area. I took the top 34% of hexagons, and plotted a crow at the centroid of each hexagon. 

The data is plotted in EPSG:3857 (WGS 84 / Pseudo-Mercator -- Spherical Mercator, Google Maps, OpenStreetMap, Bing, ArcGIS, ESRI). This is so that it lines up well with the tile-basemaps. The custom markers are randomly chosen to make the map look more like a flock of crows flying over the city. I tried randomly varying the size of the markers as well, but found that did not add anything aesthetically. The basemap is added via `contextily` and is Voyager by CartoDB (no labels). 

#### Finishing Touches

To add a better key, title, and to make a more aesthetically pleasing scale bar and north arrow, I pulled the output pdf from the Jupyter notebook into Adobe Illustrator. In Illustartor, I added a north arrow, changed the appearance of the scale bar, and added a caption and citation. I also changed the font of the basemap attribution to match the fonts of the title and text on the map (Arvo). 
