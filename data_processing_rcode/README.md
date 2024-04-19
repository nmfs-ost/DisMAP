Compiling and process/cleaning the Survey Data for DisMAP! 

This folder sets up the directory structure needed to run the data processing steps. 

All R scripts used in this data processing are found in the "code" folder. This includes:
1. "download_x.R" scripts - follow the instructions in each script to download or otherwise obtain the survey data
2. "Compile_Dismap_Current.R" - this script will compile and clean the regional survey data into standardized formats, and reivew/check for taxonomic naming issues. 
3. clean_taxa.R - contains the code for the function used to obtain clean taxa names. Use of this code will only be needed occasionally when taxonomic naming errors are flagged in the Compile code 
5. create_data_for_map_generation.R - run this after Compile script to get the data in the needed file format for use in the Python script and generate the interpolated biomass rasters and calculate the indicators. 
4. DisMAP_data_download_API.R - this code runs through example scripts of how to download the data presented on the DisMAP site using API to connect to our [Inport records](https://www.fisheries.noaa.gov/inport/item/66799)


<img src="https://raw.githubusercontent.com/nmfs-general-modeling-tools/nmfspalette/main/man/figures/noaa-fisheries-rgb-2line-horizontal-small.png" alt="NOAA Fisheries" height="75"/>

[U.S. Department of Commerce](https://www.commerce.gov/) \| [National
Oceanographic and Atmospheric Administration](https://www.noaa.gov) \|
[NOAA Fisheries](https://www.fisheries.noaa.gov/)

