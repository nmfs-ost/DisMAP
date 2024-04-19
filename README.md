# [The Distribution Mapping and Analysis Portal (DisMAP)](https://github.com/nmfs-fish-tools/DisMAP) 

> This code is always in development. Find code used for various reports in the code [releases](https://github.com/nmfs-fish-tools/DisMAP/releases).

The NOAA Fisheries Distribution Mapping and Analysis Portal (DisMAP) provides easy access to information to track and understand distributions of marine fish and macroinvertebrate species in the U.S. Marine Ecosystems. The portal currently provides access to distribution information for over 400 species collected in fishery-independent bottom trawl surveys conducted by NOAA Fisheries or its partners. The portal provides information on three key indicators used to track and explore shifts in species distributions:
  * Distribution of biomass in space and time (i.e., distribution surface)
  * Center of biomass
  * Range limits

This repository provides the data processing and analysis code used to develop the spatial distribution and indicators presented in the portal. For more information and to launch the portal visit: https://apps-st.fisheries.noaa.gov/dismap/index.html. 

Explanation of Folders:
1. data_processing_rcode
This folder holds all the R scripts needed to download and process the regional bottom trawl survey data. Opening up the DisMAP_Project Rproject file will open all necessary Rscripts to run the analysis and set up the appropriate directory structure. You will need to follow the instructions in each of the "download_x.R" scripts for each to download or obtain from a regional POC the raw survey data. Once the data is downloaded and in the "data" folder, you may run the Compile_Dismap_Current.R script to process and clean the data. After running Compile_Dismap_Current.R, run the create_data_for_map_generation.R to get the data in the needed file format for use in the Python script and generte the interpolated biomass and indicators (as described below)

2. ArcGIS Analysis - Python
This folder houses the scripts for generating the interpolated biomass and calculating the distribution indicators (latitude, depth, range limits, etc). 

## Suggestions and Comments

If you see that the data, product, or metadata can be improved, you are
invited to create a [pull
request](https://github.com/nmfs-fish-tools/DisMAP/pulls)
or [submit an issue to the code’s
repository](https://github.com/nmfs-fish-tools/DisMAP/issues).

## NOAA README

This repository is a scientific product and is not official
communication of the National Oceanic and Atmospheric Administration, or
the United States Department of Commerce. All NOAA GitHub project code
is provided on an ‘as is’ basis and the user assumes responsibility for
its use. Any claims against the Department of Commerce or Department of
Commerce bureaus stemming from the use of this GitHub project will be
governed by all applicable Federal law. Any reference to specific
commercial products, processes, or services by service mark, trademark,
manufacturer, or otherwise, does not constitute or imply their
endorsement, recommendation or favoring by the Department of Commerce.
The Department of Commerce seal and logo, or the seal and logo of a DOC
bureau, shall not be used in any manner to imply endorsement of any
commercial product or activity by DOC or the United States Government.

## NOAA License

Software code created by U.S. Government employees is not subject to
copyright in the United States (17 U.S.C. §105). The United
States/Department of Commerce reserve all rights to seek and obtain
copyright protection in countries other than the United States for
Software authored in its entirety by the Department of Commerce. To this
end, the Department of Commerce hereby grants to Recipient a
royalty-free, nonexclusive license to use, copy, and create derivative
works of the Software outside of the United States.

<img src="https://raw.githubusercontent.com/nmfs-general-modeling-tools/nmfspalette/main/man/figures/noaa-fisheries-rgb-2line-horizontal-small.png" alt="NOAA Fisheries" height="75"/>

[U.S. Department of Commerce](https://www.commerce.gov/) \| [National
Oceanographic and Atmospheric Administration](https://www.noaa.gov) \|
[NOAA Fisheries](https://www.fisheries.noaa.gov/)

