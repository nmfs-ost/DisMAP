Species Quality Analysis/Quality Control (spp_QAQC)
-------------------------------
This folder contains taxonomic information and is used to update the trimmed datasets in the Compile_Dismap.R script with correct species scientific and common names, and to remove species which are of higher order or inappropriately sampled by the trawl survey gear. 

## spptaxonomy_updated_5_12_22.csv ##
This file contains the most recent scientific and common names for the species caught in the bottom trawl surveys. 

## exclude_spp ##
Contains a list of taxa, annotated with notes from the regional contacts and a TRUE/FALSE column for exclusion. Taxa with "TRUE" in this column will be excluded from the data analysis in compile.R.

