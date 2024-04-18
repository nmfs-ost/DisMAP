# The Distribution Mapping and Analysis Portal (DisMAP) 

The NOAA Fisheries Distribution Mapping and Analysis Portal (DisMAP) provides easy access to information to track and understand distributions of marine fish and macroinvertebrate species in the U.S. Marine Ecosystems. The portal currently provides access to distribution information for over 400 species collected in fishery-independent bottom trawl surveys conducted by NOAA Fisheries or its partners. The portal provides information on three key indicators used to track and explore shifts in species distributions:
  * Distribution of biomass in space and time (i.e., distribution surface)
  * Center of biomass
  * Range limits

This repository provides the data processing and analysis code used to develop the spatial distribution and indicators presented in the portal. For more information and to launch the portal visit: https://apps-st.fisheries.noaa.gov/dismap/index.html. 

Explanation of Folders:
1. Data Processing - Rcode
This folder holds all the R scripts needed to download and process the regional bottom trawl survey data. Openining up the DisMAP_Project Rproject file will open all necessary Rscripts to run the analysis and set up the appropriate directory structure. You will need to follow the instructions in each of the "download_x.R" scripts for each to download the raw survey data. Once the data is downloaded and in the "data_raw" folder, you may run the Compile_Dismap.R script to process and clean the data. After running Compile_Dismap.R, run the create_data_for_map_generation.R to get the data in the needed file format for use in the Python script and genarte the interpolated biomass and indicators (as described below)

2. ArcGIS Analysis - Python
This folder houses the scripts for generating the interpolated biomass and calculating the distribution indicators (latitude, depth, range limits, etc). 

3. DisMAP_Data_Download_API Rscript, runs through examples of how to access the various products (e.g., Distribution metrics (COG), Interpolated Biomass layers, and survey points) via the Map Services and API. 

