## ---- DISMAP 5/05/2026
## updated script to include "expanded survey data" for the new Survey Data Module

## updated thru 2025 survey data for all regions

#--------------------------------------------------------------------------------------#
#### LOAD LIBRARIES AND FUNCTIONS ####
#--------------------------------------------------------------------------------------#
## Testing changes ##
# install.packages("devtools")
library(devtools)
# install.packages("readr")
# install.packages("here")
# install.packages("purrr")
# install.packages("stringr")
# install.packages("forcats")
# install.packages("tidyr")
# install.packages("ggplot2")
# install.packages("dplyr")
# install.packages("tibble")
# install.packages("lubridate")
# install.packages("PBSmapping")
# install.packages("data.table")
# install.packages("gridExtra")
# install.packages("questionr")
# install.packages("geosphere")
# install.packages("taxize")
# install.packages("worrms")
# install.packages("rfishbase")


# Load required packages
library(taxize)
library(worrms)
library(rfishbase)
library(lubridate)
library(PBSmapping)
library(gridExtra)
library(questionr)
library(geosphere)
library(here)
library(dplyr)
library(readr) # note need to install from repo to get older version 1.3.1 for it to work properly
library(purrr)
library(forcats)
library(tidyr)
library(tibble)
library(ggplot2)
library(stringr)
library(data.table)


## The data_processing_rcode directory contains three folders (code, data, outputs)
# 1. code - this folder contains all the Rscripts (including this Compile_Dismap_Current.R script) used to download and
# process the data
# 2. data directory - this is the folder containing all raw data files you downloaded using the Rscripts in the code folder
# 3. output directory - folder where the cleaned data will be saved to. This folder includes subfolders for
# data_clean, plots, the data generated for the python scripts by creat_data_for_map_generation.R, and by clean_taxa.R script

# The zip file you downloaded created this directory structure for you.

# a note on species name adjustment ####
# At some point during certain surveys it was realized that what was believed to be one species was actually a different species or more than one species.  Species have been lumped together as a genus in those instances.
# Additionally, species names were verified against WORMs database and standardized across regions (and within surveys)

# Answer the following questions using all caps TRUE or FALSE to direct the actions of the script =====================================

# 1. Some strata and years have very little data, should they be removed and saved as fltr data? #DEFAULT: TRUE.
HQ_DATA_ONLY <- TRUE

# 2. View plots of removed strata for HQ_DATA. #OPTIONAL, DEFAULT:FALSE
# It takes a while to generate these plots.
HQ_PLOTS <- FALSE

# 3. Remove ai,ebs,gmex,goa,neus,seus,wcann,wctri, scot. Keep `dat`. #DEFAULT: FALSE
REMOVE_REGION_DATASETS <- FALSE

# 4. If you would like to write out the clean data, would you prefer it in Rdata or CSV form?  Note the CSV's are much larger than the Rdata files. #DEFAULT:TRUE, FALSE generates CSV's instead of Rdata.
PREFER_RDATA <- TRUE

# 5. Output the clean full master data frame. #DEFAULT:FALSE
WRITE_MASTER_DAT <- FALSE

# 6. Output the clean trimmed data frame. #DEFAULT:FALSE
WRITE_TRIMMED_DAT <- TRUE

# 7. Generate dat.exploded table. #OPTIONAL, DEFAULT:TRUE
DAT_EXPLODED <- TRUE

# 8. Output the dat.exploded table #DEFAULT:FALSE
WRITE_DAT_EXPLODED <- FALSE


# Workspace setup ---------------------------------------------------------
print("Workspace setup")

# This script works best when the repository is downloaded from github,
# especially when that repository is loaded as a project into RStudio.

# The working directory is assumed to be the DisMAP directory of this repository.
# library(tidyverse)# use ggplot2, tibble, readr, dplyr, stringr, purrr


# Functions ===========================================================
print("Functions")

# function to calculate convex hull area in km2
# developed from http://www.nceas.ucsb.edu/files/scicomp/GISSeminar/UseCases/CalculateConvexHull/CalculateConvexHullR.html
calcarea <- function(lon,lat){
  hullpts = chull(x=lon, y=lat) # find indices of vertices
  hullpts = c(hullpts,hullpts[1]) # close the loop
  lonlat <- data.frame(cbind(lon, lat))
  ps = appendPolys(NULL,mat=as.matrix(lonlat[hullpts,]),1,1,FALSE) # create a Polyset object
  attr(ps,"projection") = "LL" # set projection to lat/lon
  psUTM = convUL(ps, km=TRUE) # convert to UTM in km
  polygonArea = calcArea(psUTM,rollup=1)
  return(polygonArea$area)
}

sumna <- function(x){
  #acts like sum(na.rm=T) but returns NA if all are NA
  if(!all(is.na(x))) return(sum(x, na.rm=T))
  if(all(is.na(x))) return(NA)
}

meanna = function(x){
  if(!all(is.na(x))) return(mean(x, na.rm=T))
  if(all(is.na(x))) return(NA)
}

# weighted mean for use with summarize(). values in col 1, weights in col 2
wgtmean = function(x, na.rm=FALSE) {questionr::wtd.mean(x=x[,1], weights=x[,2], na.rm=na.rm)}

wgtse = function(x, na.rm=TRUE){
  if(sum(!is.na(x[,1]) & !is.na(x[,2]))>1){
    if(na.rm){
      return(sqrt(wtd.var(x=x[,1], weights=x[,2], na.rm=TRUE, normwt=TRUE))/sqrt(sum(!is.na(x[,1] & !is.na(x[,2])))))
    } else {
      return(sqrt(wtd.var(x=x[,1], weights=x[,2], na.rm=FALSE, normwt=TRUE))/sqrt(length(x))) # may choke on wtd.var without removing NAs
    }
  } else {
    return(NA) # NA if vector doesn't have at least 2 values
  }
}

se <- function(x) sd(x)/sqrt(length(x)) # assumes no NAs

lunique = function(x) length(unique(x)) # number of unique values in a vector

present_every_year <- function(dat, ...){
  presyr <- dat %>%
    filter(wtcpue > 0) %>%
    group_by(...) %>%
    summarise(pres = n())
  return(presyr)
}

num_hauls_year <- function(dat, ...){
  haulsyr <- dat %>%
    select(c(region, haulid, year)) %>%
    distinct() %>%
    group_by(...) %>%
    summarise(hauls = n())
  return(haulsyr)
}

# num_year_present <- function(presyr, ...){
#   presyrsum <- presyr %>%
#     filter(pres > 0) %>%
#     group_by(...) %>%
#     summarise(presyr = n())
#   return(presyrsum)
# }

num_year_present <- function(haulsyr, ...){
  presyrsum <- haulsyr %>%
    filter(pres > 0) %>%
    group_by(...) %>%
    summarise(presyr = n())
  return(presyrsum)
}

max_year_surv <- function(presyrsum, ...){
  maxyrs <- presyrsum %>%
    group_by(...) %>%
    summarise(maxyrs = max(presyr))
  return(maxyrs)

}

explode0 <- function(x, by=c("region")){
  # x <- copy(x)
  stopifnot(is.data.table(x))

  # print(x[1])

  # x <- as.data.table(x)
  # x <- as.data.table(trimmed_dat)[region=="Scotian Shelf Summer"]
  # setkey(x, sampleid, stratum, year, lat, lon, stratumarea, depth)
  # group the data by these columns
  setorder(x, haulid, stratum, year, lat, lon, stratumarea, depth)

  # pull out all of the unique spp
  u.spp <- x[,as.character(unique(spp))]
  # pull out all of the unique common names
  u.cmmn <- x[,common[!duplicated(as.character(spp))]]

  # pull out these location related columns and sort by haulid and year
  x.loc <- x[,list(haulid, year, stratum, stratumarea, lat, lon, depth)]
  setkey(x.loc, haulid, year)

  # attatch all spp to all locations
  x.skele <- x.loc[,list(spp=u.spp, common=u.cmmn), by=eval(colnames(x.loc))]
  setkey(x.skele, haulid, year, spp)
  x.skele <- unique(x.skele)
  setcolorder(x.skele, c("haulid","year","spp", "common", "stratum", "stratumarea","lat","lon","depth"))

  # pull in multiple observations of the same species
  x.spp.dat <- x[,list(haulid, year, spp, wtcpue)]
  setkey(x.spp.dat, haulid, year, spp)
  x.spp.dat <- unique(x.spp.dat)

  out <- x.spp.dat[x.skele, allow.cartesian = TRUE]

  out$wtcpue[is.na(out$wtcpue)] <- 0

  out
}

#convert factors to numeric

as.numeric.factor <- function(x) {as.numeric(levels(x))[x]}

#Reformat string - first letter uppercase
firstup <- function(x) {
  x <- tolower(x)
  substr(x, 1, 1) <- toupper(substr(x, 1, 1))
  x
}

#add one to odd numbers
oddtoeven <- function(x) {
  ifelse(x %% 2 == 1,x+1,x)
}

#add one to even numbers
eventoodd <- function(x) {
  ifelse(x %% 2 == x+1,1,x)
}

#--------------------------------------------------------------------------------------#
#### PULL IN AND EDIT RAW DATA FILES ####
#--------------------------------------------------------------------------------------#

# Compile AFSC Bottom Trawl Data =====================================================
print("Compile Alaska")

# Load data --------------------------------------------------------------------
catch <- readr::read_csv(file = here::here("data_processing_rcode/data/AK_gap_products_foss_catch.csv"))[,-1] # remove "row number" column
haul <- readr::read_csv(file = here::here("data_processing_rcode/data/AK_gap_products_foss_haul.csv"))[,-1] # remove "row number" column
species <- readr::read_csv(file = here::here("data_processing_rcode/data/AK_gap_products_foss_species.csv"))[,-1] # remove "row number" column

# Wrangle data -----------------------------------------------------------------
ak_full <-
  # join haul and catch data to unique species by survey table
  dplyr::left_join(haul, catch, by="hauljoin") %>%
  # join species data to unique species by survey table
  dplyr::left_join(species, by="species_code") %>%
  # modify zero-filled rows
  dplyr::mutate(
    cpue_kgkm2 = ifelse(is.na(cpue_kgkm2), 0, cpue_kgkm2), # just in case
    cpue_kgha = cpue_kgkm2/100, # Hectares
    cpue_nokm2 = ifelse(is.na(cpue_nokm2), 0, cpue_nokm2), # just in case
    cpue_noha = cpue_nokm2/100, # Hectares
    count = ifelse(is.na(count), 0, count),
    weight_kg = ifelse(is.na(weight_kg), 0, weight_kg), # just in case
    region = dplyr::case_when(
      survey_definition_id == 78 ~ "Bering Sea Slope Survey",
      survey_definition_id == 47 ~ "Gulf of Alaska",
      survey_definition_id == 52 ~ "Aleutian Islands",
      survey_definition_id == 98 ~ "Eastern Bering Sea",
      survey_definition_id == 143 ~ "Northern Bering Sea"
    ))


ak_full<- ak_full %>%
  dplyr::rename(year = year,
                haulid = hauljoin,
                lat = latitude_dd_start,
                lon = longitude_dd_start,
                stratum = stratum,
                depth = depth_m,
                spp = scientific_name,
                common = common_name,
                wtcpue = cpue_kgha) %>%
  dplyr::mutate(
    stratumarea = NA, # removed above because the new data tables dont provide this
    # Calculate a corrected longitude for Aleutians (all in western hemisphere coordinates)
    lon = ifelse(lon > 0, lon - 360, lon),
    # adjust spp names
    # add species names for two rockfish complexes
    spp = ifelse(grepl("rougheye and blackspotted rockfish unid.", common), "Sebastes melanostictus and S. aleutianus", spp),
    spp = ifelse(grepl("dusky and dark rockfishes unid.", common), "Sebastes variabilis and S. ciliatus", spp),
    # catch A. stomias and A. evermanii (grouped together due to identification issues early on in dataset)
    # spp = ifelse(grepl("Atheresthes", spp), "Atheresthes stomias and A. evermanni", spp), #doesn't apply to all regions
    # catch L. polystryxa (valid in 2018), and L. bilineata (valid in 2018)
    spp = ifelse(grepl("Lepidopsetta", spp), "Lepidopsetta sp.", spp),
    # # group together because of identification issues: catch M. jaok (valid in 2018), M. niger (valid in 2018), M. polyacanthocephalus (valid in 2018), M. quadricornis (valid in 2018), M. verrucosus (changed to scorpius), M. scorpioides (valid in 2018), M. scorpius (valid in 2018) (M. scorpius is in the data set but not on the list so it is excluded from the change)
    # spp = ifelse(grepl("Myoxocephalus", spp ) & !grepl("scorpius", spp), "Myoxocephalus sp.", spp),
    # catch B. maculata (valid in 2018), abyssicola (valid in 2018), aleutica (valid in 2018), interrupta (valid in 2018), lindbergi (valid in 2018), mariposa (valid in 2018), minispinosa (valid in 2018), smirnovi (valid in 2018), cf parmifera (Orretal), spinosissima (valid in 2018), taranetzi (valid in 2018), trachura (valid in 2018), violacea (valid in 2018)
    spp = ifelse(grepl("Bathyraja", spp), 'Bathyraja sp.', spp),
    # catch S. melanostictus and S. aleutianus (blackspotted & rougheye), combined into one complex
    spp = ifelse(grepl("Sebastes melanostictus", spp)|grepl("Sebastes aleutianus", spp), "Sebastes melanostictus and S. aleutianus", spp),
    # catch S. variabilis and S. ciliatus (dusky + dark rockfish), combined into one complex
    spp = ifelse(grepl("Sebastes variabilis", spp)|grepl("Sebastes ciliatus", spp), "Sebastes variabilis and S. ciliatus", spp)
    #spp = ifelse(grepl("Hippoglossoides", spp), "Hippoglossoides elassodon and H. robustus", spp) #doesn't apply to all regions
  ) %>%
  # remove rows that are eggs, shells, etc (they will have NA for scientific name)
  dplyr::filter(spp != "" &
                  # remove any additional rows where spp contains the word "egg"
                  !grepl("egg", spp),
                !grepl("Polychaete tubes", spp)) %>%
  mutate(
    across(c(lat, lon, wtcpue), as.numeric),
    across(c(year, depth), as.integer),
    across(c(spp, haulid), as.character)
  ) %>%
  dplyr::group_by(region, haulid, stratum, stratumarea, year, lat, lon, depth, spp) %>%
  dplyr::summarise(wtcpue = sum(wtcpue, na.rm = TRUE)) %>%
  dplyr::select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue) %>%
  dplyr::ungroup()

# clean up
rm(haul, catch, species)

# now that main data set has been compiled and cleaned/standardized, can split out the different surveys
### Aleutian Islands survey -----
ai <- ak_full %>%
  dplyr::filter(region == "Aleutian Islands") %>%
  dplyr::mutate(# catch A. stomias and A. evermanii (grouped together due to identification issues early on in dataset)
    spp = ifelse(grepl("Atheresthes", spp), "Atheresthes stomias and A. evermanni", spp)) %>%
  dplyr::group_by(region, haulid, stratum, stratumarea, year, lat, lon, depth, spp) %>%
  dplyr::summarise(wtcpue = sum(wtcpue, na.rm = TRUE)) %>%
  dplyr::select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue) %>%
  dplyr::ungroup()

if (HQ_DATA_ONLY == TRUE){

  # look at the graph and make sure decisions to keep or eliminate data make sense

  # plot the strata by year

  p1 <- ai %>%
    select(stratum, year) %>%
    ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
    geom_jitter() +
    theme(axis.text.x = element_text(angle = 90, size = rel(0.80)))

  p2 <- ai %>%
    select(lat, lon) %>%
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()

  test <- ai %>%
    select(stratum, year) %>%
    distinct() %>%
    group_by(stratum) %>%
    summarise(count = n()) %>%
    filter(count >= 14) #this ensures that we only use strata that are sampled in all years. Should be updated annually.

  # how many rows will be lost if only stratum trawled ever year are kept?
  test2 <- ai %>%
    filter(stratum %in% test$stratum)
  nrow(ai) - nrow(test2)
  # percent that will be lost
  print((nrow(ai) - nrow(test2))/nrow(ai))
  # 0% of rows are removed (Each strata is sampled each year!)
  ai_fltr <- ai %>%
    filter(stratum %in% test$stratum)

  # plot the results after editing
  p3 <- ai_fltr %>%
    select(stratum, year) %>%
    ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
    geom_jitter() +
    theme(axis.text.x = element_text(angle = 90, size = rel(0.85)))

  p4 <- ai_fltr %>%
    select(lat, lon) %>%
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()

  if (HQ_PLOTS == TRUE){
    temp <- grid.arrange(p1, p2, p3, p4, nrow = 2)
    ggsave(plot = temp, filename = here::here("data_processing_rcode/output/plots", "ai_hq_dat_removed.png"))
    rm(temp)
  }
  rm(test, test2, p1, p2, p3, p4)
}

### Eastern Bering Sea survey -----
ebs <- ak_full %>%
  dplyr::filter(region == "Eastern Bering Sea")%>%
  dplyr::mutate(# catch A. stomias and A. evermanii (grouped together due to idenfication issues early on in dataset)
    spp = ifelse(grepl("Atheresthes", spp), "Atheresthes stomias and A. evermanni", spp),
    spp = ifelse(grepl("Hippoglossoides", spp), "Hippoglossoides elassodon and H. robustus", spp))%>%
  dplyr::group_by(region, haulid, stratum, stratumarea, year, lat, lon, depth, spp) %>%
  dplyr::summarise(wtcpue = sum(wtcpue, na.rm = TRUE)) %>%
  dplyr::select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue) %>%
  dplyr::ungroup()

# ebs<-left_join(ebs, ebs_strata, by=c("stratum"="StratumCode"))%>%
#   select(-stratumarea, -SubareaDescription) %>%
#   rename(stratumarea=Areakm2) %>%
#   dplyr::select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue)

if (HQ_DATA_ONLY == TRUE){
  # look at the graph and make sure decisions to keep or eliminate data make sense

  p1 <- ebs %>%
    select(stratum, year) %>%
    ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
    geom_jitter()  +
    theme(axis.text.y = element_text(size = rel(0.70)))

  p2 <- ebs %>%
    select(lat, lon) %>%
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()

  test <- ebs %>%
    select(stratum, year) %>%
    distinct() %>%
    group_by(year) %>%
    summarise(count = n())  %>%
    filter(count >= 12)

  # how many rows will be lost if only years where all stratum sampled are kept? and start timeseries in 1987
  test2 <- ebs %>%
    filter(year %in% test$year) %>%
    filter(year != 1985)
  nrow(ebs) - nrow(test2)
  # percent that will be lost
  print((nrow(ebs) - nrow(test2))/nrow(ebs))
  # 8% of rows are removed
  ebs_fltr <- ebs %>%
    filter(year %in% test$year)%>%
    filter(year != 1985)

  p3 <- ebs_fltr %>%
    select(stratum, year) %>%
    ggplot(aes(x = as.factor(stratum), y = as.factor(year))) +
    geom_jitter() +
    theme(axis.text.y = element_text(size = rel(0.70)))

  p4 <- ebs_fltr %>%
    select(lat, lon) %>%
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()

  if (HQ_PLOTS == TRUE){
    temp <- grid.arrange(p1, p2, p3, p4, nrow = 2)
    ggsave(plot = temp, filename = here::here("data_processing_rcode/output/plots", "ebs_hq_dat_removed.png"))
    rm(temp)
  }
  rm(test, test2, p1, p2, p3, p4)
}

### Gulf of Alaska survey -----
goa <- ak_full %>%
  dplyr::filter(region == "Gulf of Alaska")

if (HQ_DATA_ONLY == TRUE){
  # look at the graph and make sure decisions to keep or eliminate data make sense

  p1 <- goa %>%
    select(stratum, year) %>%
    ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
    geom_jitter() +
    theme(axis.text.x = element_text(angle = 90, size = rel(0.80)))

  p2 <- goa %>%
    select(lat, lon) %>%
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()

  # for GOA in 2001 missed 27 strata and will be removed, stratum 50 is
  # missing from 3 years but will be kept, 410, 420, 430, 440, 450 are missing
  #from 3 years but will be kept, 510 and higher are missing from 7 or more years
  # of data and will be removed
  test <- goa %>%
    filter(year != 2001) %>%
    select(stratum, year) %>%
    distinct() %>%
    group_by(stratum) %>%
    summarise(count = n())%>%
    filter(count >= 12) #this ensures that we only use strata that are sampled in all but 3 years. Should be updated annually.

  # how many rows will be lost if only stratum trawled ever year and the ones mentioned
  # above are kept?
  test2 <- goa %>%
    filter(stratum %in% test$stratum)
  nrow(goa) - nrow(test2)
  # percent that will be lost
  print ((nrow(goa) - nrow(test2))/nrow(goa))

  goa_fltr <- goa %>%
    filter(stratum %in% test$stratum) %>%
    filter(year != 2001)

  p3 <-  goa_fltr %>%
    select(stratum, year) %>%
    ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
    geom_jitter() +
    theme(axis.text.x = element_text(angle = 90, size = rel(0.80)))

  p4 <- goa_fltr %>%
    select(lat, lon) %>%
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()

  if (HQ_PLOTS == TRUE){
    temp <- grid.arrange(p1, p2, p3, p4, nrow = 2)
    ggsave(plot = temp, filename = here::here("data_processing_rcode/output/plots", "goa_hq_dat_removed.png"))

    rm(temp)
  }
  rm(test, test2, p1, p2, p3, p4)
}

### Northern Bering Sea survey -----
nbs <- ak_full %>%
  dplyr::filter(region == "Northern Bering Sea") %>%
  dplyr::mutate(# catch A. stomias and A. evermanii (grouped together due to idenfication issues early on in dataset)
    spp = ifelse(grepl("Atheresthes", spp), "Atheresthes stomias and A. evermanni", spp),
    spp = ifelse(grepl("Hippoglossoides", spp), "Hippoglossoides elassodon and H. robustus", spp)) %>%
  dplyr::group_by(region, haulid, stratum, stratumarea, year, lat, lon, depth, spp) %>%
  dplyr::summarise(wtcpue = sum(wtcpue, na.rm = TRUE)) %>%
  dplyr::select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue) %>%
  dplyr::ungroup()

if (HQ_DATA_ONLY == TRUE){
  # look at the graph and make sure decisions to keep or eliminate data make sense

  p1 <- nbs %>%
    select(stratum, year) %>%
    ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
    geom_jitter()

  p2 <- nbs %>%
    select(lat, lon) %>%
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()

  test <- nbs %>%
    select(stratum, year) %>%
    distinct() %>%
    group_by(stratum) %>%
    summarise(count = n())%>%
    filter(count >= 6)#this ensures that we only use strata that are sampled in all years. Should be updated annually.

  # how many rows will be lost if only stratum trawled ever year are kept?
  test2 <- nbs %>%
    filter(stratum %in% test$stratum)
  nrow(nbs) - nrow(test2)
  # percent that will be lost
  print ((nrow(nbs) - nrow(test2))/nrow(nbs))

  nbs_fltr <- nbs %>%
    filter(stratum %in% test$stratum)

  p3 <-  nbs_fltr %>%
    select(stratum, year) %>%
    ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
    geom_jitter()

  p4 <- nbs_fltr %>%
    select(lat, lon) %>%
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()

  if (HQ_PLOTS == TRUE){
    temp <- grid.arrange(p1, p2, p3, p4, nrow = 2)
    ggsave(plot = temp, filename = here::here("data_processing_rcode/output/plots", "nbs_hq_dat_removed.png"))

    rm(temp)
  }
  rm(test, test2, p1, p2, p3, p4)
}

# Compile WCTRI ===========================================================
print("Compile WCTRI")

wctri_catch <- read_csv(here::here("data_processing_rcode/data", "wctri_catch.csv"), col_types = cols(
  CRUISEJOIN = col_integer(),
  HAULJOIN = col_integer(),
  CATCHJOIN = col_integer(),
  REGION = col_character(),
  VESSEL = col_integer(),
  CRUISE = col_integer(),
  HAUL = col_integer(),
  SPECIES_CODE = col_integer(),
  WEIGHT = col_double(),
  NUMBER_FISH = col_integer(),
  SUBSAMPLE_CODE = col_character(),
  VOUCHER = col_character(),
  AUDITJOIN = col_integer()
)) %>%
  select(CRUISEJOIN, HAULJOIN, VESSEL, CRUISE, HAUL, SPECIES_CODE, WEIGHT)

wctri_haul <- read_csv(here::here("data_processing_rcode/data", "wctri_haul.csv"), col_types =
                         cols(
                           CRUISEJOIN = col_integer(),
                           HAULJOIN = col_integer(),
                           REGION = col_character(),
                           VESSEL = col_integer(),
                           CRUISE = col_integer(),
                           HAUL = col_integer(),
                           HAUL_TYPE = col_integer(),
                           PERFORMANCE = col_double(),
                           START_TIME = col_character(),
                           DURATION = col_double(),
                           DISTANCE_FISHED = col_double(),
                           NET_WIDTH = col_double(),
                           NET_MEASURED = col_character(),
                           NET_HEIGHT = col_double(),
                           STRATUM = col_integer(),
                           START_LATITUDE = col_double(),
                           END_LATITUDE = col_double(),
                           START_LONGITUDE = col_double(),
                           END_LONGITUDE = col_double(),
                           STATIONID = col_character(),
                           GEAR_DEPTH = col_integer(),
                           BOTTOM_DEPTH = col_integer(),
                           BOTTOM_TYPE = col_integer(),
                           SURFACE_TEMPERATURE = col_double(),
                           GEAR_TEMPERATURE = col_double(),
                           WIRE_LENGTH = col_integer(),
                           GEAR = col_integer(),
                           ACCESSORIES = col_integer(),
                           SUBSAMPLE = col_integer(),
                           AUDITJOIN = col_integer()
                         )) %>%
  select(CRUISEJOIN, HAULJOIN, VESSEL, CRUISE, HAUL, HAUL_TYPE, PERFORMANCE, START_TIME, DURATION, DISTANCE_FISHED, NET_WIDTH, STRATUM, START_LATITUDE, END_LATITUDE, START_LONGITUDE, END_LONGITUDE, STATIONID, BOTTOM_DEPTH)

wctri_species <- read_csv(here::here("data_processing_rcode/data", "wctri_species.csv"), col_types = cols(
  SPECIES_CODE = col_integer(),
  SPECIES_NAME = col_character(),
  COMMON_NAME = col_character(),
  REVISION = col_character(),
  BS = col_character(),
  GOA = col_character(),
  WC = col_character(),
  AUDITJOIN = col_integer()
)) %>%
  select(SPECIES_CODE, SPECIES_NAME, COMMON_NAME)

# Add haul info to catch data
wctri <- left_join(wctri_catch, wctri_haul, by = c("CRUISEJOIN", "HAULJOIN", "VESSEL", "CRUISE", "HAUL"))
#  add species names
wctri <- left_join(wctri, wctri_species, by = "SPECIES_CODE")


wctri <- wctri %>%
  # trim to standard hauls and good performance
  filter(HAUL_TYPE == 3 & PERFORMANCE == 0) %>%
  # Create a unique haulid
  mutate(
    haulid = paste(formatC(VESSEL, width=3, flag=0), formatC(CRUISE, width=3, flag=0), formatC(HAUL, width=3, flag=0), sep='-'),
    # Extract year where needed
    year = substr(CRUISE, 1, 4),
    # Add "strata" (define by lat, lon and depth bands) where needed # degree bins # 100 m bins # no need to use lon grids on west coast (so narrow)
    stratum = paste(floor(START_LATITUDE)+0.5, floor(BOTTOM_DEPTH/100)*100 + 50, sep= "-"),
    # adjust for tow area # weight per hectare (10,000 m2)
    wtcpue = (WEIGHT*10000)/(DISTANCE_FISHED*1000*NET_WIDTH)
  )

# Calculate stratum area where needed (use convex hull approach)
wctri_strats <- wctri %>%
  group_by(stratum) %>% #Should this be "STRATUM"
  summarise(stratumarea = calcarea(START_LONGITUDE, START_LATITUDE))

wctri <- left_join(wctri, wctri_strats, by = "stratum")
wctri <- wctri %>%
  mutate(
    # add species names for two rockfish complexes
    SPECIES_NAME = ifelse(grepl("rougheye and blackspotted rockfish unid.", COMMON_NAME), "Sebastes melanostictus and S. aleutianus", SPECIES_NAME),
    SPECIES_NAME = ifelse(grepl("dusky and dark rockfishes unid.", COMMON_NAME), "Sebastes variabilis and S. ciliatus", SPECIES_NAME))


wctri <- wctri %>%
  rename(
    svvessel = VESSEL,
    lat = START_LATITUDE,
    lon = START_LONGITUDE,
    depth = BOTTOM_DEPTH,
    spp = SPECIES_NAME
  ) %>%
  filter(
    spp != "" &
      !grepl("egg", spp),
    !grepl("Egg", spp),
    !grepl("Empty", spp)
  ) %>%
  # adjust spp names
  mutate(spp = ifelse(grepl("Lepidopsetta", spp), "Lepidopsetta sp.", spp),
         spp = ifelse(grepl("Bathyraja", spp), 'Bathyraja sp.', spp),
         spp = ifelse(grepl("Squalus", spp), 'Squalus suckleyi', spp)) %>%
  group_by(haulid, stratum, stratumarea, year, lat, lon, depth, spp) %>%
  summarise(wtcpue = sumna(wtcpue)) %>%
  # add region column
  mutate(region = "West Coast Triennial") %>%
  select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue) %>%
  ungroup()

if (HQ_DATA_ONLY == TRUE){
  # look at the graph and make sure decisions to keep or eliminate data make sense


  p1 <- wctri %>%
    select(stratum, year) %>%
    ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
    geom_jitter() +
    theme(axis.text.x = element_text(angle = 90, size = rel(0.80)))

  p2 <- wctri %>%
    select(lat, lon) %>%
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()

  test <- wctri %>%
    select(stratum, year) %>%
    distinct() %>%
    group_by(stratum) %>%
    summarise(count = n()) %>%
    filter(count >= 10)

  # how many rows will be lost if only stratum trawled ever year are kept?
  test2 <- wctri %>%
    filter(stratum %in% test$stratum)
  nrow(wctri) - nrow(test2)
  # percent that will be lost
  print((nrow(wctri) - nrow(test2))/nrow(wctri))
  # 23% of rows are removed
  wctri_fltr <- wctri %>%
    filter(stratum %in% test$stratum)

  p3 <- wctri_fltr %>%
    select(stratum, year) %>%
    ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
    geom_jitter() +
    theme(axis.text.x = element_text(angle = 90, size = rel(0.80)))

  p4 <- wctri_fltr %>%
    select(lat, lon) %>%
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()

  if (HQ_PLOTS == TRUE){
    temp <- grid.arrange(p1, p2, p3, p4, nrow = 2)
    ggsave(plot = temp, filename = here::here("data_processing_rcode/output/plots", "wctri_hq_dat_removed.png"))
    rm(temp)
  }
  rm(test, test2, p1, p2, p3, p4)
}

rm(wctri_catch, wctri_haul, wctri_species, wctri_strats)

# Compile WCANN ===========================================================
print("Compile WCANN")
wcann_catch <- read_csv(here::here("data_processing_rcode/data", "wcann_catch.csv"), col_types = cols(
  year = col_integer(),
  trawl_id = col_character(),
  tow = col_double(),
  performance = col_character(),
  project = col_character(),
  partition = col_character(),
  common_name = col_character(),
  scientific_name = col_character(),
  cpue_kg_per_ha_der = col_double(),
  depth_m = col_double()
  ))[,-1] %>% # remove "row number" column
    select ("year", "trawl_id", "tow", "performance", "project", "partition",
                "common_name", "scientific_name", "cpue_kg_per_ha_der", "depth_m") %>%
    filter(performance !='Unsatisfactory',
           project =='Groundfish Slope and Shelf Combination Survey')

wcann_haul <- read_csv(here::here("data_processing_rcode/data", "wcann_haul.csv"), col_types = cols(
  year = col_integer(),
  trawl_id = col_character(),
  tow = col_double(),
  performance = col_character(),
  project = col_character(),
  longitude_dd = col_double(),
  latitude_dd = col_double(),
  depth_hi_prec_m = col_double()
  ))[,-1] %>% # remove "row number" column
select("trawl_id","tow", "year","project", "longitude_dd","latitude_dd","depth_hi_prec_m", "performance") %>%
  filter(performance !='Unsatisfactory',
         project =='Groundfish Slope and Shelf Combination Survey')

wcann <- left_join(wcann_haul, wcann_catch, by = c("year", "trawl_id", "tow")) %>%
  mutate(
    # create haulid
    haulid = trawl_id
  ) %>%
  rename(
    wtcpue = cpue_kg_per_ha_der
  )

wcann$stratum<-ifelse(wcann$latitude_dd <=35.5 & wcann$depth_hi_prec_m<=183, "35.5-183",
                      ifelse(wcann$latitude_dd <= 35.5 & wcann$depth_hi_prec_m <= 549, "35.5-549",
                             ifelse(wcann$latitude_dd <= 35.5 & wcann$depth_hi_prec_m <= 1280, "35.5-1280",
                                    ifelse(wcann$latitude_dd <= 35.5 & wcann$depth_hi_prec_m > 1280, "35.5-2000",
                                           ifelse(wcann$latitude_dd <=40.5 & wcann$depth_hi_prec_m<=183, "40.5-183",
                                                  ifelse(wcann$latitude_dd <= 40.5 & wcann$depth_hi_prec_m<= 549, "40.5-549",
                                                         ifelse(wcann$latitude_dd <= 40.5 & wcann$depth_hi_prec_m <= 1280, "40.5-1280",
                                                                ifelse(wcann$latitude_dd <= 40.5 & wcann$depth_hi_prec_m > 1280, "40.5-2000",
                                                                       ifelse(wcann$latitude_dd <=43.5 & wcann$depth_hi_prec_m<=183, "43.5-183",
                                                                              ifelse(wcann$latitude_dd <= 43.5 & wcann$depth_hi_prec_m <= 549, "43.5-549",
                                                                                     ifelse(wcann$latitude_dd <= 43.5 & wcann$depth_hi_prec_m <= 1280, "43.5-1280",
                                                                                            ifelse(wcann$latitude_dd <= 43.5 & wcann$depth_hi_prec_m > 1280, "43.5-2000",
                                                                                                   # ifelse(wcann$latitude_dd <=47.5 & wcann$depth_m<=183, "47.5-183",
                                                                                                   #        ifelse(wcann$latitude_dd <= 47.5 & wcann$depth_m <= 549, "47.5-549",
                                                                                                   #               ifelse(wcann$latitude_dd <= 47.5 & wcann$depth_m <= 1280, "47.5-1280",
                                                                                                   #                      ifelse(wcann$latitude_dd <= 47.5 & wcann$depth_m > 1280, "47.5-2000",
                                                                                                   ifelse(wcann$latitude_dd <=50.5 & wcann$depth_hi_prec_m<=183, "50.5-183",
                                                                                                          ifelse(wcann$latitude_dd <= 50.5 & wcann$depth_hi_prec_m <= 549, "50.5-549",
                                                                                                                 ifelse(wcann$latitude_dd <= 50.5 & wcann$depth_hi_prec_m <= 1280, "50.5-1280",
                                                                                                                        ifelse(wcann$latitude_dd <= 50.5 & wcann$depth_hi_prec_m > 1280, "50.5-2000",NA))))))))))))))))
wcann_strats <- wcann %>%
  filter(!is.na(wtcpue)) %>%
  group_by(stratum) %>%
  summarise(stratumarea = calcarea(longitude_dd, latitude_dd), na.rm = T)


wcann <- left_join(wcann, wcann_strats, by = "stratum")

wcann <- wcann %>%
  rename(lat = latitude_dd,
         lon = longitude_dd,
         depth = depth_hi_prec_m,
         spp = scientific_name) %>%
  # remove non-fish
  filter(spp != "" &
           !grepl("Egg", partition),
         !grepl("crushed", spp),
         !grepl("empty", spp),
         !grepl("tube worm unident", spp),
         !grepl("unsorted shab", spp),
         !grepl("Gelatinous material unident", spp),
         !grepl("fish unident", spp),
         !grepl("shrimp unident", spp),
         !grepl("unident.", spp)) %>%
  # adjust spp names
  mutate(
    spp = ifelse(grepl("Lepidopsetta", spp), "Lepidopsetta sp.", spp),
    spp = ifelse(grepl("Bathyraja", spp), 'Bathyraja sp.', spp),
    spp = ifelse(grepl("Poromitra", spp), 'Poromitra curilensis', spp)
  ) %>%
  group_by(haulid, stratum, stratumarea, year, lat, lon, depth, spp) %>%
  summarise(wtcpue = sumna(wtcpue)) %>%
  # add region column
  mutate(region = "West Coast Annual") %>%
  select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue) %>%
  ungroup()


if (HQ_DATA_ONLY == TRUE){
  ## Use the full WCANN footprint -- don't match to the WCtri footprint
  p1 <- wcann %>%
    select(stratum, year) %>%
    ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
    geom_jitter()

  p2 <- wcann %>%
    select(lat, lon) %>%
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()

  test <- wcann %>%
    #filter(year != 2019) %>%
    select(stratum, year) %>%
    distinct() %>%
    group_by(stratum) %>%
    summarise(count = n()) %>%
    filter(count>=22) #this ensures that we only use strata that are sampled in all years. Should be updated annually.

  # how many rows will be lost if only stratum trawled ever year are kept?
  test2 <- wcann %>%
    filter(stratum %in% test$stratum)
  nrow(wcann) - nrow(test2)
  # percent that will be lost
  print((nrow(wcann) - nrow(test2))/nrow(wcann))

  wcann_fltr <- wcann %>%
    #filter(year != 2019)%>%
    filter(stratum %in% test$stratum)

  p3 <- wcann_fltr %>%
    select(stratum, year) %>%
    ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
    geom_jitter()

  p4 <- wcann_fltr %>%
    select(lat, lon) %>%
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()

  if (HQ_PLOTS == TRUE){
    temp <- grid.arrange(p1, p2, p3, p4, nrow = 2)
    ggsave(plot = temp, filename = here::here("data_processing_rcode/output/plots", "wcann_hq_dat_removed.png"))
    rm(temp)
  }
  rm(p1, p2, p3, p4, test, test2)
}

# cleanup
rm(wcann_catch, wcann_haul, wcann_strats)

# Compile GMEX ===========================================================
print("Compile GMEX")
##Read in data
gmex_station <- read_csv(here::here("data_processing_rcode/data", "gmex_STAREC_2025.csv"), col_types = cols(.default = col_character())) %>%
  select('STATIONID', 'CRUISEID', 'CRUISE_NO', 'P_STA_NO', 'TIME_ZN', 'TIME_MIL', 'S_LATD', 'S_LATM', 'S_LOND', 'S_LONM', 'E_LATD', 'E_LATM', 'E_LOND', 'E_LONM', 'STAT_ZONE', 'DEPTH_SSTA', 'MO_DAY_YR', 'VESSEL_SPD', 'COMSTAT')

## ISSUE: there are some longitudes that are not accurate (e.g., 913) which are not appearing for past trawls
gmex_station <- type_convert(gmex_station, col_types = cols(
  STATIONID = col_integer(),
  CRUISEID = col_integer(),
  CRUISE_NO = col_integer(),
  P_STA_NO = col_character(),
  TIME_ZN = col_integer(),
  TIME_MIL = col_character(),
  S_LATD = col_double(),
  S_LATM = col_double(),
  S_LOND = col_double(),
  S_LONM = col_double(),
  E_LATD = col_double(),
  E_LATM = col_double(),
  E_LOND = col_double(),
  E_LONM = col_double(),
  DEPTH_SSTA = col_double(),
  STAT_ZONE = col_double(),
  MO_DAY_YR = col_date(format = "%m/%d/%Y"), # note in 2026 this column was reformatted to be mo/day/yr (in previous years it was %d/%mo/%yr)
  VESSEL_SPD = col_double(),
  COMSTAT = col_character()
))

names(gmex_station)<-tolower(names(gmex_station))

gmex_tow <-readr::read_delim(here::here("data_processing_rcode/data","gmex_invrec.csv"),
                             delim = ',', escape_backslash = T, escape_double = F)
gmex_tow<-type_convert(gmex_tow, col_types = cols(
  INVRECID = col_integer(),
  STATIONID = col_integer(),
  CRUISEID = col_integer(),
  VESSEL = col_integer(),
  CRUISE_NO = col_integer(),
  P_STA_NO = col_character(),
  GEAR_SIZE = col_integer(),
  GEAR_TYPE = col_character(),
  MESH_SIZE = col_double(),
  OP = col_character(),
  MIN_FISH = col_integer(),
  WBCOLOR = col_character(),
  BOT_TYPE = col_character(),
  BOT_REG = col_character(),
  TOT_LIVE = col_double(),
  FIN_CATCH = col_double(),
  CRUS_CATCH = col_double(),
  OTHR_CATCH = col_double(),
  T_SAMPLEWT = col_double(),
  T_SELECTWT = col_double(),
  FIN_SMP_WT = col_double(),
  FIN_SEL_WT = col_double(),
  CRU_SMP_WT = col_double(),
  CRU_SEL_WT = col_double(),
  OTH_SMP_WT = col_double(),
  OTH_SEL_WT = col_double(),
  COMBIO = col_character(),
  X28 = col_character()
))

gmex_tow <- gmex_tow %>%
  select('CRUISEID','STATIONID', 'VESSEL', 'CRUISE_NO', 'P_STA_NO', 'INVRECID', 'GEAR_SIZE', 'GEAR_TYPE', 'MESH_SIZE', 'MIN_FISH', 'OP') %>%
  filter(GEAR_TYPE=='ST')
names(gmex_tow) <- tolower(names(gmex_tow))

gmex_bio <-readr::read_delim(here::here("data_processing_rcode/data","gmex_bgsrec.csv"),
                             delim = ',', escape_backslash = T, escape_double = F)

gmex_bio <- type_convert(gmex_bio, cols(
  CRUISEID = col_integer(),
  STATIONID = col_integer(),
  VESSEL = col_integer(),
  CRUISE_NO = col_integer(),
  P_STA_NO = col_character(),
  GENUS_BGS = col_character(),
  SPEC_BGS = col_character(),
  BGSCODE = col_character(),
  BIO_BGS = col_integer(),
  SELECT_BGS = col_double()
))
names(gmex_bio) <- tolower(names(gmex_bio))

gmex_cruise <-read_csv(here::here("data_processing_rcode/data", "gmex_cruises.csv"), col_types = cols(.default = col_character())) %>%
  select(CRUISEID, VESSEL, TITLE)

gmex_cruise <- type_convert(gmex_cruise, col_types = cols(CRUISEID = col_integer(), VESSEL = col_integer(), TITLE = col_character()))
names(gmex_cruise)<-tolower(names(gmex_cruise))

gmex_spp <-read_csv(here::here("data_processing_rcode/data","gmex_BCT_NFR_01182023.csv")) %>%
  mutate_if(is.logical, as.character)
problems(gmex_spp)
names(gmex_spp)<-tolower(names(gmex_spp))

gmex_spp<- gmex_spp %>%
  dplyr::select(biocode,ciu_biocode,taxon)


### Merging gmex_tow and gmex_bio tables ###

# This code updates the null invrecid values in gmex_bio based on stationid from gmex_tow.
# Remaining null values (from reef fish cruises) are removed to create gmex_bio_mod.
# get stationid and invrecid from gmex_tow
get_stationid_invrecid <- gmex_tow %>%
  dplyr::select(stationid, invrecid) %>%
  rename(inv_invrecid = invrecid)

# extract gmex_bio records with missing invrecid and update based on stationid from get_stationid_invrecid
bgsrec_null_invrecid <- gmex_bio %>%
  dplyr::filter(is.na(invrecid)) %>%
  dplyr::left_join(get_stationid_invrecid, by = 'stationid') %>%
  dplyr::mutate(invrecid = inv_invrecid) %>%
  dplyr::select(-inv_invrecid)

# extract gmex_bio records with valid invrecid
bgsrec_with_invrecid <- gmex_bio %>%
  dplyr::filter(!is.na(invrecid))

# stack bgsrec_null_invrec now updated with valid invrecid and bgsrec_with_invrecid
gmex_bio_mod <- bgsrec_null_invrecid %>%
  dplyr::bind_rows(bgsrec_with_invrecid) %>%
  # Remove null invrecids
  dplyr::filter(!is.na(invrecid)) %>%
  dplyr::arrange(bgsid)

# drop unwanted data objects
rm(bgsrec_null_invrecid,bgsrec_with_invrecid,get_stationid_invrecid, gmex_bio)
# garbage collect to free up memory
gc()


### Resolve taxonomic coding ###

# Gmex_bio_mod has a few instances of invalid bio_bgs (biocode) values.
# Also, multiple code/taxonomic combinations may refer to the same organisms under different names.
# Gmex_bio_mod reflects the code/taxonomic use at time of data ingest.
# Gmex_spp will allow translation of cases where multiple code/taxonomic refer to the same organism.
# Since multiple changes may have occurred, the ciu_biocode (currently in use biocode) value ties multiple records
# that are now inactive to the current active biocode. Inactive biocodes have the variable inactive set to zero.

# The following script updates biocode to ciu_biocode in gmex_bio_mod, using gmex_spp to merge.

# starting with our gmex_bio_mod from above
gmex_bio_utax1 <- gmex_bio_mod %>%
  # convert bgsrec table bio_bgs varialbe to numeric integer
  dplyr::mutate(bio_bgs = as.integer(bio_bgs)) %>%
  # rename bio_bgs to biocode to allow for easier manipulation with master biocode table (mbt)
  dplyr::rename(biocode = bio_bgs) %>%
  # fix invalid zero code and make it the code (999999998) for unidentified specimen
  dplyr::mutate(biocode = ifelse(biocode == 0,999999998,biocode)) %>%
  # fix invalid unidentified fish code 100000001 to proper code
  dplyr::mutate(biocode = ifelse(biocode == 100000001,100000000,biocode)) %>%
  # fix invalid unidentified crustacean code 200000001 to proper code
  dplyr::mutate(biocode = ifelse(biocode == 200000001,200000000,biocode)) %>%
  # fix invalid unidentified crustacean code 300000001  and 300000001 to proper code
  dplyr::mutate(biocode = ifelse(biocode == 300000001,300000000,biocode)) %>%
  dplyr::mutate(biocode = ifelse(biocode == 300000002,300000000,biocode)) %>%
  # update older inactive biocodes to those currently in use (ciu_biocode)
  dplyr::left_join(dplyr::select(gmex_spp,biocode,taxon,ciu_biocode), by = "biocode") %>%
  # rename taxon to bgs taxon to keep the original name associated with a biocode
  dplyr::rename(bgs_taxon = taxon) %>%
  # do a left join to bring in taxon associated with ciu_taxon
  dplyr::left_join(dplyr::select(gmex_spp,biocode,taxon), by = c("ciu_biocode" = "biocode"))


# Collapse taxa with known identification issues and collapse all sponges to single category
# These updates undergo a review with each updated version of gmex_spp.

gmex_bio_utax2 <- gmex_bio_utax1 %>%
  # Update the squid genus Loligo and all species under genus Doryteuthis to the genus Doryteuthis
  mutate(ciu_biocode = ifelse(ciu_biocode %in% c(347020200,347021001,347021002,347021003),347021000,ciu_biocode)) %>%
  mutate(taxon = ifelse(ciu_biocode %in% c(347021000),'DORYTEUTHIS SP',taxon)) %>%
  # Update batfish species to Halieutichthys
  mutate(ciu_biocode = ifelse(ciu_biocode >= 195050401 & ciu_biocode <= 195050405,195050400,ciu_biocode)) %>%
  mutate(taxon = ifelse(ciu_biocode %in% c(195050400),'HALIEUTICHTHYS SP',taxon)) %>%
  # Update all jellyfish in the genus Aurelia to the genus Aurelia
  mutate(ciu_biocode = ifelse(ciu_biocode >= 618010101 & ciu_biocode <= 618010105,618010100,ciu_biocode)) %>%
  mutate(taxon = ifelse(ciu_biocode %in% c(618010100),'AURELIA',taxon)) %>%
  # Update all lionfishes species to the genus Pterois
  mutate(ciu_biocode = ifelse(ciu_biocode %in% c(168011901,168011902),168011900,ciu_biocode)) %>%
  mutate(taxon = ifelse(ciu_biocode %in% c(168011900),'PTEROIS',taxon)) %>%
  # Smoothhounds (Mustelus) managed as species complex, our ids are OK now but in the past assumptions made %>%
  mutate(ciu_biocode = ifelse(ciu_biocode %in% c(108031101,108031102,108031103,108031104),108031100,ciu_biocode)) %>%
  mutate(taxon = ifelse(ciu_biocode %in% c(108031100),'MUSTELUS SP',taxon)) %>%
  # Update all sponge identifications to Porifera
  mutate(ciu_biocode = ifelse(ciu_biocode >= 613000000 & ciu_biocode < 616000000,613000000,ciu_biocode)) %>%
  mutate(taxon = ifelse(ciu_biocode %in% c(613000000),'PORIFERA',taxon)) %>%
  # handle out of order Porifera  Demospngiae and Agelas and Agelas and Agelasidae in coral numbers
  mutate(ciu_biocode = ifelse(ciu_biocode %in% c(999997000,999997020,617170000,617170100),613000000,ciu_biocode)) %>%
  mutate(taxon = ifelse(ciu_biocode %in% c(613000000),'PORIFERA',taxon)) %>%
  # Collapse all shrimp species in Rimnapenaeus as they are not consistently separated in the field
  mutate(ciu_biocode = ifelse(ciu_biocode %in% c(228012001,228012002),228012000,ciu_biocode)) %>%
  mutate(taxon = ifelse(ciu_biocode %in% c(228012000),'RIMAPENAEUS',taxon)) %>%
  # Astropecten species have changed, distribution overlap with major east west differences
  mutate(biocode = ifelse(ciu_biocode >= 691010101 & ciu_biocode <= 691010112,691010100,biocode)) %>%
  mutate(taxon = ifelse(ciu_biocode %in% c(691010100),'ASTROPECTEN',taxon))


## Collapse gmex_bio_utax2 to have single entry for each taxa for a distinct invrecid (tow)
gmex_bio_utax3 <- gmex_bio_utax2 %>%
  group_by(cruiseid, stationid, invrecid, ciu_biocode, taxon) %>%
  summarise(record_cnt = n(),
            # Note: Extrapolated counts (cntexp) & weights (select_bgs) of a taxa for a tow is the sum of all records of that taxon.
            tcntexp = sum(cntexp, na.rm=TRUE),
            tselect_bgs = sum(select_bgs,na.rm=TRUE))

## Determine which tows to keep initially from the original gmex_tow object
## Adding additional variable from gmex_station and gmex_cruise
gmex_tow <- gmex_tow %>%
  # add station location and related data dropping duplicated variables cruise_no and p_sta_no
  left_join(select(gmex_station,-c("cruise_no","p_sta_no")), by = c("cruiseid", "stationid")) %>%
  # add cruise title and dropping duplicated variable vessel
  left_join(select(gmex_cruise, -c("vessel")), by = c("cruiseid"))


## filtering gmex_tow
gmex_tow <- gmex_tow %>%
  # Trim to high quality SEAMAP summer trawls
  filter(grepl("Summer", title) &
           # NOTE: gear_size is 42ft (width of trawl net) but recorded as 40ft #
           gear_size == 40 &
           mesh_size == 1.63 &
           ## keeping only null/no operation code or water hauls op = "W"
           ## This also removes op = 9 ("NOS,WTS,OR SPECIES LIST INCOMPLETE") which is undocumented in GSMFC metadata
           (is.na(op) | op == "W")) %>%
  mutate(
    # Create a unique haulid
    haulid = paste(formatC(vessel, width=3, flag=0), formatC(cruise_no, width=3, flag=0), formatC(p_sta_no, width=5, flag=0, format='d'), sep='-'),
    # Extract year where needed
    year = year(mo_day_yr),
    # fix data entry errors for lon (longitudes < - 360 (like -900) don't exist and are due to missing decimal)
    s_lond = ifelse(s_lond > 360, s_lond/10, s_lond),
    e_lond = ifelse(e_lond > 360, e_lond/10, e_lond),
    # # Calculate decimal lat and lon, depth in m, where needed
    s_latd = ifelse(s_latd == 0, NA, s_latd),
    s_lond = ifelse(s_lond == 0, NA, s_lond),
    e_latd = ifelse(e_latd == 0, NA, e_latd),
    e_lond = ifelse(e_lond == 0, NA, e_lond),
    lat = rowMeans(cbind(s_latd + s_latm/60, e_latd + e_latm/60), na.rm=T),
    lon = -rowMeans(cbind(s_lond + s_lonm/60, e_lond + e_lonm/60), na.rm=T),
  ) %>%
  ## filter for target years
  filter(year >= 2010)


## Merge gmex_tow with updated gmex_bio tables (e.g., gmex_bio_utax3) to create gmex object
## Counts and weights collapsed for multiple records for a taxa within an invrecid.
gmex <- gmex_tow %>%
  left_join(gmex_bio_utax3, by = c("cruiseid","stationid","invrecid"))

gmex <- gmex %>%
  dplyr::mutate(uop = op) %>%
  ## Update tow that should have been op coded based on 03/03/2025 download and only years >= 2010
  dplyr::mutate(uop =
                  ifelse(vessel == '95' & cruise_no == '1701' & p_sta_no == '95007' & invrecid == 138972, 'M', uop)) %>%
  dplyr::mutate(uop =
                  ifelse(vessel == '17' & cruise_no == '1503' & p_sta_no == '00030' & invrecid == 139159, 'M', uop)) %>%
  dplyr::mutate(uop =
                  ifelse(vessel == '35' & cruise_no == '1202' & p_sta_no == '35006' & invrecid == 111362, 'T', uop)) %>%
  dplyr::mutate(uop =
                  ifelse(vessel == '17' & cruise_no == '1002' & p_sta_no == '00068' & invrecid == 135137, 'Z', uop)) %>%
  dplyr::mutate(uop =
                  ifelse(vessel == '17' & cruise_no == '1002' & p_sta_no == '00054' & invrecid == 135123, 'X', uop)) %>%
  dplyr::mutate(uop =
                  ifelse(vessel == '35' & cruise_no == '1902' & p_sta_no == '00011' & invrecid == 142353, 'G', uop)) %>%
  dplyr::mutate(uop =
                  ifelse(vessel == '77' & cruise_no == '1002' & p_sta_no == '00007' & invrecid == 135383, 'Z', uop)) %>%
  dplyr::filter(is.na(uop) | uop == "W") %>%
  dplyr::select(-c("uop"))


# add stratum code defined by STAT_ZONE and depth bands (note depth in recorded as m, and depth bands based on 0-20 fathoms
# and 21-60 fathoms))
gmex$depth_zone <- ifelse(gmex$depth_ssta<=36.576, "20",
                        ifelse(gmex$depth_ssta>36.576, "60", NA))

gmex <- gmex %>%
  mutate(stratum = paste(stat_zone, depth_zone, sep= "-"))

## fix speed
# trim out or fix speed and duration records
# trim out tows of 0, >60, or unknown minutes
gmex <- gmex %>%
  filter(min_fish <= 60 & min_fish  > 0 & !is.na(min_fish )) %>%
  # fix typo according to Jeff Rester: 30 = 3
  mutate(vessel_spd = ifelse(vessel_spd == 30, 3, vessel_spd)) %>%
  # trim out vessel speeds 0, unknown, or >5 (need vessel speed to calculate area trawled)
  filter(vessel_spd <= 5 & vessel_spd > 0  & !is.na(vessel_spd))

gmex_strats <- gmex %>%
  group_by(stratum) %>%
  summarise(stratumarea = calcarea(lon, lat))

gmex <- left_join(gmex, gmex_strats, by = "stratum")

# while comstat is still present
# Remove a tow when paired tows exist (same lat/lon/year but different haulid, only Gulf of Mexico)
# identify duplicate tows at same year/lat/lon
dups <- gmex %>%
  group_by(year, lat, lon) %>%
  filter(n() > 1) %>%
  group_by(haulid) %>%
  filter(n() == 1)

# remove the identified tows from the dataset
gmex <- gmex %>%
  filter(!haulid %in% dups$haulid & !grepl("PORT", comstat))

gmex <- gmex %>%
  rename(spp = taxon,
         depth = depth_ssta) %>%
  # adjust for area towed
  mutate(
    # kg per 10000m2. calc area trawled in m2: knots * 1.8 km/hr/knot * 1000 m/km * minutes * 1 hr/60 min * width of gear in feet * 0.3 m/ft # biomass per standard tow
    # gear_size is calculated by multiplying the 42ft net by 0.75 (the estimate of the active-use portion of the net)
    wtcpue = 10000*tselect_bgs/(vessel_spd * 1.85200 * 1000 * min_fish / 60 * 31.5 * 0.3048)
  ) %>%
  # remove unidentified spp
  filter(
    spp != '' | !is.na(spp),
    !spp %in% c('UNID CRUSTA', 'UNID OTHER', 'UNID.FISH', 'CRUSTACEA(INFRAORDER) BRACHYURA', 'MOLLUSCA AND UNID.OTHER #01', 'ALGAE', 'MISCELLANEOUS INVERTEBR', 'OTHER INVERTEBRATES')
  ) %>%
  group_by(haulid, stratum, stratumarea, year, lat, lon, depth, spp) %>%
  summarise(wtcpue = sumna(wtcpue)) %>%
  # add region column
  mutate(region = "Gulf of Mexico") %>%
  select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue) %>%
  ungroup()


if (HQ_DATA_ONLY == TRUE){
  # look at the graph and make sure decisions to keep or eliminate data make sense

  p1 <- gmex %>%
    select(stratum, year) %>%
    ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
    geom_jitter() +
    theme(axis.text.x = element_text(angle = 90, size = rel(0.80)))

  p2 <- gmex %>%
    select(lat, lon) %>%
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()


  test <- gmex %>%
    # filter(year >= 2010, year!=2023) %>% # switched to 2010 and after since 2008-2009 were experimental years
    select(stratum, year) %>%
    distinct() %>%
    group_by(stratum) %>%
    summarise(count = n()) %>%
    filter(count >=11) # Update annually. This removes strata that are poorly sampled through time.

  # how many rows will be lost if years where all strata sampled (>2008) are kept?
  test2 <- gmex %>%
    filter(stratum %in% test$stratum)
  nrow(gmex) - nrow(test2)
  # percent that will be lost
  print((nrow(gmex) - nrow(test2))/nrow(gmex))
  # lose % of rows

  gmex_fltr <- gmex %>%
    filter(stratum %in% test$stratum)
  # %>%
    # filter(year>=2010, year != 2023)


  p3 <- gmex_fltr %>%
    select(stratum, year) %>%
    ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
    geom_jitter() +
    theme(axis.text.x = element_text(angle = 90, size = rel(0.80)))

  p4 <- gmex_fltr %>%
    select(lat, lon) %>%
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()

  if (HQ_PLOTS == TRUE){
    temp <- grid.arrange(p1, p2, p3, p4, nrow = 2)
    ggsave(plot = temp, filename = here::here("data_processing_rcode/output/plots", "gmex_hq_dat_removed.png"))
    rm(temp)
  }
  rm(test, test2, p1, p2, p3, p4)
}
rm(gmex_bio, gmex_cruise, gmex_spp, gmex_station, gmex_tow, problems, gmex_bio_mod, gmex_bio_utax2, gmex_bio_utax1, dups)

# Compile Northeast US ===========================================================
print("Compile NEUS")
## starting in 2023 update, NEFSC gave data set already with the conversions done
#read strata file
neus_strata <- read_csv(here::here("data_processing_rcode/data", "neus_strata.csv"), col_types = cols(.default = col_character())) %>%
  select(stratum, stratum_area) %>%
  mutate(stratum = as.double(stratum)) %>%
  distinct()

#read in catch file, which includes both spring and fall survey thru 2024. Need to parse them out
neus_catch <- read.csv("data_processing_rcode/data/neus_catch.csv", header=T, sep=",")%>%
  filter(!is.na(SCINAME)) %>%
  mutate(SVSPP = as.character(SVSPP))

#read in 2025 data
neus_catch_2025<-read.csv("data_processing_rcode/data/NEFSC_BTS_ALLCATCHES_2025SPR_FALL.csv", header=T, sep=",")%>%
  filter(!is.na(SCINAME)) %>%
  mutate(SVSPP = as.character(SVSPP))

neus_catch<- rbind(neus_catch, neus_catch_2025)

neus_fall_catch<-neus_catch %>%
  filter(SEASON=="FALL")
neus_spring_catch<-neus_catch %>%
  filter(SEASON=="SPRING")

#NEUS fall
neus_fall <- neus_fall_catch %>%
  rename(year = EST_YEAR,
         lat = DECDEG_BEGLAT,
         lon = DECDEG_BEGLON,
         depth = AVGDEPTH,
         stratum = STRATUM,
         haulid = ID,
         spp = SCINAME,
         wtcpue = CALIB_WT)  %>%
  mutate(
    haulid= paste(CRUISE6,"0",stratum,"00",TOW, "0000"),sep="") %>%
  mutate(stratum = as.double(stratum),
         lat = as.double(lat),
         lon = as.double(lon),
         depth = as.double(depth),
         haulid= as.character(haulid),
         wtcpue = as.double(wtcpue),
         year = as.double(year))

# sum different sexes of same spp together
neus_fall <- neus_fall %>%
  group_by(year, lat, lon, depth, haulid, STATION, stratum, spp) %>%
  summarise(wtcpue = sum(wtcpue))
neus_fall <- ungroup(neus_fall)

#join with strata
neus_fall <- left_join(neus_fall, neus_strata, by = "stratum")
neus_fall <- filter(neus_fall, !is.na(stratum_area))
neus_fall <- neus_fall %>%
  rename(stratumarea = stratum_area) %>%
  mutate(stratumarea = as.double(stratumarea)* 3.429904) #convert square nautical miles to square kilometers
neus_fall$region <- "Northeast US Fall"

neus_fall<- neus_fall %>%
  select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue) %>%
  # remove unidentified spp and non-species
  filter(
    !spp %in% c("TRASH SPECIES IN CATCH")) %>%
  filter(
    spp != "" | !is.na(spp),
    haulid !="197512 0 3290 00 1 0000",
    !grepl("EGG", spp),
    !grepl("UNIDENTIFIED", spp),
    !grepl("UNKNOWN", spp),
    !grepl("NO FISH BUT GOOD TOW", spp), ## FLAG. should this tow be kept in somehow?
    !grepl("DELPHINIDAE", spp)) %>%
  # remove any extra white space from around spp names
  mutate(spp = str_trim(spp))


# are there any strata in the data that are not in the strata file?
stopifnot(nrow(filter(neus_fall, is.na(stratumarea))) == 0)

rm(neus_fall_catch)

if (HQ_DATA_ONLY == TRUE){
  # look at the graph and make sure decisions to keep or eliminate data make sense

  p1 <- neus_fall %>%
    select(stratum, year) %>%
    ggplot(aes(x = as.factor(stratum), y = as.factor(year))) +
    geom_jitter()

  p2 <- neus_fall %>%
    select(lat, lon) %>%
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()

  test <- neus_fall %>%
    # filter(year != 2017, year >= 1974) %>%
    select(stratum, year) %>%
    distinct() %>%
    group_by(stratum) %>%
    summarise(count = n())%>%
    filter(count >= 50)

  # how many rows will be lost if only stratum trawled fairly consistently (>48 years - so all but 2 of the years) are kept?
  test2 <- neus_fall %>%
    filter(year != 2017, year > 1973) %>%
    filter(stratum %in% test$stratum)
  nrow(neus_fall) - nrow(test2)
  # percent that will be lost
  print((nrow(neus_fall) - nrow(test2))/nrow(neus_fall))
  # When bad strata are removed after bad years we only lose 34%

  neus_fall_fltr <- neus_fall %>%
    filter(year != 2017, year > 1973) %>%
    filter(stratum %in% test$stratum)

  p3 <- neus_fall_fltr %>%
    select(stratum, year) %>%
    ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
    geom_jitter()

  p4 <- neus_fall_fltr %>%
    select(lat, lon) %>%
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()

  if (HQ_PLOTS == TRUE){
    temp <- grid.arrange(p1, p2, p3, p4, nrow = 2)
    ggsave(plot = temp, filename = here::here("data_processing_rcode/output/plots", "neusF_hq_dat_removed.png"))
    rm(temp)
  }
  rm(test, test2, p1, p2, p3, p4)
}

#NEUS Spring
neus_spring <- neus_spring_catch %>%
  rename(year = EST_YEAR,
         lat = DECDEG_BEGLAT,
         lon = DECDEG_BEGLON,
         depth = AVGDEPTH,
         stratum = STRATUM,
         haulid = ID,
         spp = SCINAME,
         wtcpue = CALIB_WT)  %>%
  mutate(haulid= paste(CRUISE6,"0",stratum,"00",TOW, "0000"),sep="") %>%
  mutate(stratum = as.double(stratum),
         lat = as.double(lat),
         lon = as.double(lon),
         depth = as.double(depth),
         wtcpue = as.double(wtcpue))

# sum different sexes of same spp together
neus_spring <- neus_spring %>%
  group_by(year, lat, lon, depth, haulid, CRUISE6, STATION, stratum, spp) %>%
  summarise(wtcpue = sum(wtcpue))
neus_spring <- ungroup(neus_spring)

#join with strata
neus_spring <- left_join(neus_spring, neus_strata, by = "stratum")
neus_spring <- filter(neus_spring, !is.na(stratum_area))

# are there any strata in the data that are not in the strata file?
stopifnot(nrow(filter(neus_spring, is.na(stratum_area))) == 0)
neus_spring <- neus_spring %>%
  rename(stratumarea = stratum_area) %>%
  mutate(stratumarea = as.double(stratumarea)* 3.429904)#convert square nautical miles to square kilometers

neus_spring$region <- "Northeast US Spring"

neus_spring <- neus_spring %>%
  select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue) %>%
  # remove unidentified spp and non-species
  # remove non-fish
  filter(
    !spp %in% c("TRASH SPECIES IN CATCH")) %>%
  filter(
    spp != "" | !is.na(spp),
    !grepl("EGG", spp),
    !grepl("UNIDENTIFIED", spp),
    !grepl("UNKNOWN", spp),
    !grepl("NO FISH BUT GOOD TOW", spp)) %>%
  # remove any extra white space from around spp names
  mutate(spp = str_trim(spp))

if (HQ_DATA_ONLY == TRUE){
  # look at the graph and make sure decisions to keep or eliminate data make sense

  p1 <-neus_spring %>%
    select(stratum, year) %>%
    ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
    geom_jitter()

  p2 <- neus_spring %>%
    select(lat, lon) %>%
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()

  test <- neus_spring %>%
    filter(year!= 2023, year != 2020, year != 2014, year != 1975, year > 1973) %>%
    select(stratum, year) %>%
    distinct() %>%
    group_by(stratum) %>%
    summarise(count = n())%>%
    filter(count >= 46) #Update annually; note: every year would be 48, but that would lost some key strata in the south

  # how many rows will be lost if only stratum trawled ALMOST ever year are kept?
  test2 <- neus_spring %>%
    filter(year!= 2023, year != 2020,year != 2014, year != 1975, year > 1973) %>%
    filter(stratum %in% test$stratum)
  nrow(neus_spring) - nrow(test2)
  # percent that will be lost
  (nrow(neus_spring) - nrow(test2))/nrow(neus_spring)
  # When bad strata are removed after bad years we only lose 35%

  neus_spring_fltr <- neus_spring %>%
    filter(year!= 2023, year != 2020,year != 2014, year != 1975, year > 1973) %>%
    filter(stratum %in% test$stratum)

  p3 <- neus_spring_fltr %>%
    select(stratum, year) %>%
    ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
    geom_jitter()

  p4 <- neus_spring_fltr %>%
    select(lat, lon) %>%
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()

  if (HQ_PLOTS == TRUE){
    temp <- grid.arrange(p1, p2, p3, p4, nrow = 2)
    ggsave(plot = temp, filename = here::here("data_processing_rcode/output/plots", "neusS_hq_dat_removed.png"))
    rm(temp)
  }
  rm(test, p1, p2, p3, p4)
}

rm(neus_strata)

# Compile SEUS ===========================================================
print("Compile SEUS")
# turns everything into a character so import as character anyway
#starting in 2026 the files were provided in a new format requiring changes to code structure
#install.packages("readxl")
library(readxl)

seus_catch<- read_excel(here::here("data_processing_rcode", "data", "SEAMAP-SA_CTS.xlsx"), sheet = "CTS_AbundBio_1989-2025") %>%
# remove symbols
  mutate_all(list(~str_replace(., "=", ""))) %>%
  mutate_all(list(~str_replace(., '"', ''))) %>%
  mutate_all(list(~str_replace(., '\"', '')))

# convert the columns to their correct formats
seus_catch <- type_convert(seus_catch, col_types = cols(
  PROJECTNAME = col_character(),
  PROJECTAGENCY = col_character(),
  DATE = col_character(),
  EVENTNAME = col_character(),
  #COLLECTIONNUMBER = col_character(),
  VESSELNAME = col_character(),
  GEARNAME = col_character(),
  #GEARCODE = col_character(),
  #SPECIESCODE = col_character(),
  MRRI_CODE = col_character(),
  SPECIESSCIENTIFICNAME = col_character(),
  #SPECIESCOMMONNAME = col_character(),
  NUMBERTOTAL = col_integer(),
  SPECIESTOTALWEIGHT = col_double(),
  #SPECIESSUBWEIGHT = col_double(),
  #SPECIESWGTPROCESSED = col_character(),
  #WEIGHTMETHODDESC = col_character(),
  #ORGWTUNITS = col_character(),
  EFFORT = col_double(),
  #CATCHSUBSAMPLED = col_logical(),
  #CATCHWEIGHT = col_double(),
  #CATCHSUBWEIGHT = col_double(),
  #TIMESTART = col_character(),
  DURATION = col_integer(),
  #TOWTYPETEXT = col_character(),
  #LOCATION = col_character(),
  REGION = col_character(),
  DEPTHZONE = col_character(),
  #ACCSPGRIDCODE = col_character(),
  #STATIONCODE = col_character(),
  #EVENTTYPEDESCRIPTION = col_character(),
  TEMPSURFACE = col_double(),
  TEMPBOTTOM = col_double(),
  SALINITYSURFACE = col_double(),
  SALINITYBOTTOM = col_double(),
  #SDO = col_character(),
  #BDO = col_character(),
  #TEMPAIR = col_double(),
  LATITUDESTART = col_double(),
  LATITUDEEND = col_double(),
  LONGITUDESTART = col_double(),
  LONGITUDEEND = col_double(),
  DEPTHSTART = col_double(),
  DEPTHEND = col_double(),
 # SPECSTATUSDESCRIPTION = col_character(),
 # LASTUPDATED = col_character(),
  SEASON = col_character()
))

seus_haul<- read_excel(here::here("data_processing_rcode", "data", "SEAMAP-SA_CTS.xlsx"), sheet = "CTS_Event_1989-2025") %>%
  # remove symbols
  mutate_all(list(~str_replace(., "=", ""))) %>%
  mutate_all(list(~str_replace(., '"', ''))) %>%
  mutate_all(list(~str_replace(., '\"', '')))

seus_haul <- type_convert(seus_haul, col_types = cols(
  EVENTNAME = col_character(),
  DEPTHSTART = col_integer()
))

##merge catch and haul dataframes
# Find all columns that exist in both datasets, excluding your join key
common_cols <- intersect(names(seus_catch), names(seus_haul))
cols_to_drop <- setdiff(common_cols, "EVENTNAME")

# Join while dropping all of them from the second dataframe
seus <- seus_catch %>%
  left_join(seus_haul %>% select(-all_of(cols_to_drop)), by = "EVENTNAME")

# contains strata areas
seus_strata <- read_csv(here::here("data_processing_rcode/data", "seus_strata.csv"), col_types = cols(
  STRATA = col_integer(),
  STRATAHECTARE = col_double()
))

#Create STRATA column
seus <- seus %>%
  mutate(STRATA = as.numeric(str_sub(STATIONCODE, 1, 2))) %>%
  # Drop OUTER depth zone because it was only sampled for 10 years
  filter(DEPTHZONE != "OUTER")

#add STRATAHECTARE to main file
seus <- left_join(seus, seus_strata, by = "STRATA")


#Survey was changed in 2023 to reflect new months categorized in each season
#We want to preserve the historical season definitions but assign the new definitions for years 2023 and above
#So, here we break dataset in to pre2023 and post2023 to assign seasons and then recombine
seus_pre2023 <- seus %>%
  filter(EVENTNAME < 2023000)

seus_post2023 <- seus %>%
  filter(EVENTNAME >= 2023000)

seus_post2023 <- seus_post2023 %>%
  mutate(SEASON = ifelse(MONTH >= 4 & MONTH <= 6, "spring", SEASON),
         SEASON = ifelse(MONTH >= 8 & MONTH <= 12, "fall", SEASON))

#Create a 'SEASON' column using 'MONTH' as a criteria
seus_pre2023 <- seus_pre2023 %>%
  mutate(SEASON = ifelse(MONTH >= 1 & MONTH <= 3, "winter", SEASON),
         SEASON = ifelse(MONTH >= 4 & MONTH <= 6, "spring", SEASON),
         SEASON = ifelse(MONTH >= 7 & MONTH <= 8, "summer", SEASON),
         #September EVENTS were grouped with summer, should be fall because all
         #hauls made in late-September during fall-survey
         SEASON = ifelse(MONTH >= 9 & MONTH <= 12, "fall", SEASON))

seus <- rbind(seus_post2023, seus_pre2023)

# find rows where weight wasn't provided for a species
## ISSUE: are 0 or very small wgts (e.g., 0.001) when there was 1 or 2 of a species caught, errors?
misswt <- seus %>%
  filter(is.na(SPECIESTOTALWEIGHT)) %>%
  select(MRRI_CODE, SPECIESSCIENTIFICNAME) %>%
  distinct()

    # # calculate the mean weight for those species
    # meanwt <- seus %>%
    #   filter(SPECIESCODE %in% misswt$SPECIESCODE) %>%
    #   group_by(SPECIESCODE) %>%
    #   summarise(mean_wt = mean(SPECIESTOTALWEIGHT, na.rm = T))
    #
    # # rows that need to be changed
    # change <- seus %>%
    #   filter(is.na(SPECIESTOTALWEIGHT))
    #
    # # remove those rows from SEUS
    # seus <- anti_join(seus, change)
    #
    # # change the rows
    # change <- change %>%
    #   select(-SPECIESTOTALWEIGHT)
    #
    # # update the column values
    # change <- left_join(change, meanwt, by = "SPECIESCODE") %>%
    #   rename(SPECIESTOTALWEIGHT = mean_wt)
    #
    # # rejoin to the data
    # seus <- rbind(seus, change)


#Data entry error fixes for lat/lon coordinates
seus <- seus %>%
  mutate(
    # longitudes of less than -360 (like -700), do not exist.  This is a missing decimal.
    LONGITUDESTART = ifelse(LONGITUDESTART < -360, LONGITUDESTART/10, LONGITUDESTART),
    LONGITUDEEND = ifelse(LONGITUDEEND < -360, LONGITUDEEND/10, LONGITUDEEND),
    # latitudes of more than 100 are outside the range of this survey.  This is a missing decimal.
    LATITUDESTART = ifelse(LATITUDESTART > 100, LATITUDESTART/10, LATITUDESTART),
    LATITUDEEND = ifelse(LATITUDEEND  > 100, LATITUDEEND/10, LATITUDEEND)
  )

### In 2026 the data provided provided an Area Swept value (=EFFORT) and also a species total weight that already combined
    # port and starboard samples so the below script is not needed, but may be needed again in the future.
    #NOTE NEEDED IN 2026: In seus there are two 'COLLECTIONNUMBERS' per 'EVENTNAME', with no exceptions,
    #for each side of the boat;
      #EFFORT is always the same for each COLLECTIONNUMBER
      # We sum the two tows in seus (port and starboard tows), and this steps deletes any haul id x spp duplicates
seus <- seus %>%
  rename(
    year = YEAR,
    haulid = EVENTNAME,
    stratum = STRATA,
    lat = LATITUDESTART,
    lon = LONGITUDESTART,
    depth = DEPTHSTART,
    spp = SPECIESSCIENTIFICNAME,
    stratumarea = STRATAHECTARE)

seus<- seus %>%
  group_by(haulid, stratum, stratumarea, year, lat, lon, depth, spp, SEASON, EFFORT) %>%
  # remove non-fish and records with no species or common name
  filter(
    !spp %in% c('MISCELLANEOUS INVERTEBRATES','XANTHIDAE','MICROPANOPE NUTTINGI','ALGAE','DYSPANOPEUS SAYI', 'PSEUDOMEDAEUS AGASSIZII')
  ) %>%
  filter(!is.na(spp)) %>%
  # adjust spp names
  mutate(
    spp = ifelse(grepl("ANCHOA", spp), "ANCHOA", spp),
    spp = ifelse(grepl("LIBINIA", spp), "LIBINIA", spp)
  )  %>%
  #now this accounts for both sides of the boat, and merging within specified gensuses
  #summarise(biomass = sumna(SPECIESTOTALWEIGHT)) %>% #note: add this line back in if total weight not already combined
  mutate(wtcpue=SPECIESTOTALWEIGHT/EFFORT) %>% #Note: make effort *2 if need to combine port and starboard tows in future
  # add temporary region column that will be converted to seasonal
  mutate(region = "Southeast US") %>%
  ungroup() %>%
  select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue, SEASON)

#remove infinite wtcpue values (where effort was 0, causes wtcpue to be inf)
seus <- seus[!is.infinite(seus$wtcpue),]

# now that lines have been removed from the main data set, can split out seasons
# SEUS spring ====
#Separate the the spring season and convert to dataframe
seusSPRING <- seus %>%
  filter(SEASON == "spring") %>%
  select(-SEASON) %>%
  mutate(region = "Southeast US Spring")

if (HQ_DATA_ONLY == TRUE){
  # look at the graph and make sure decisions to keep or eliminate data make sense

  p1 <- seusSPRING %>%
    select(stratum, year) %>%
    ggplot(aes(x = as.factor(stratum), y = as.factor(year))) +
    geom_jitter()

  p2 <- seusSPRING %>%
    select(lat, lon) %>%
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()

  #get # of years
  yrs<-seusSPRING %>%
    select(year) %>%
    distinct()

  test <- seusSPRING %>%
    select(stratum, year) %>%
    filter(year != 1989) %>% #Spring 1989 data are not comparable to the time series (e.g., nocturnal sampling)
    distinct() %>%
    group_by(stratum) %>%
    summarise(count = n()) %>%
    filter(count >= 30) #FLAG: Update annually. strata sampled all but a few year!!

  # how many rows will be lost if only stratum trawled ever year are kept?
  test2 <- seusSPRING %>%
    filter(stratum %in% test$stratum) %>%
    filter(year != 1989)
  nrow(seusSPRING) - nrow(test2)
  # percent that will be lost
  print((nrow(seusSPRING) - nrow(test2))/nrow(seusSPRING))
  # 8.6% are removed

  seusSPRING_fltr <- seusSPRING %>%
    filter(stratum %in% test$stratum)%>%
    filter(year != 1989)

  p3 <- seusSPRING_fltr %>%
    select(stratum, year) %>%
    ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
    geom_jitter()

  p4 <- seusSPRING_fltr %>%
    select(lat, lon) %>%
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()

  if (HQ_PLOTS == TRUE){
    temp <- grid.arrange(p1, p2, p3, p4, nrow = 2)
    ggsave(plot = temp, filename = here::here("data_processing_rcode/output/plots", "seusSPR_hq_dat_removed.png"))
    rm(temp)
  }
  rm(test, p1, p2, p3, p4)
}

# SEUS summer ====
#Separate the summer season and convert to dataframe
##NOTE: summer sampling stopped after 2022
seusSUMMER <- seus %>%
  filter(SEASON == "summer") %>%
  select(-SEASON) %>%
  mutate(region = "Southeast US Summer")

if (HQ_DATA_ONLY == TRUE){
  # look at the graph and make sure decisions to keep or eliminate data make sense

  p1 <- seusSUMMER %>%
    select(stratum, year) %>%
    ggplot(aes(x = as.factor(stratum), y = as.factor(year))) +
    geom_jitter()

  p2 <- seusSUMMER %>%
    select(lat, lon) %>%
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()

  #2021 was poorly sampled, so should be removed from data
  seusSUMMER_fltr <- seusSUMMER %>%
    filter(year!=2021)

  p3 <- seusSUMMER_fltr %>%
    select(stratum, year) %>%
    ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
    geom_jitter()

  p4 <- seusSUMMER_fltr %>%
    select(lat, lon) %>%
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()

  if (HQ_PLOTS == TRUE){
    temp <- grid.arrange(p1, p2, p3, p4, nrow = 2)
    ggsave(plot = temp, filename = here::here("data_processing_rcode/output/plots", "seusSUM_hq_dat_removed.png"))
    rm(temp)
  }
  rm(p1, p2, p3, p4)
}


# SEUS fall ====
seusFALL <- seus %>%
  filter(SEASON == "fall") %>%
  select(-SEASON) %>%
  mutate(region = "Southeast US Fall")

# how many rows will be lost if only stratum trawled ever year are kept?
if (HQ_DATA_ONLY == TRUE){

  p1 <- seusFALL %>%
    select(stratum, year) %>%
    ggplot(aes(x = as.factor(stratum), y = as.factor(year))) +
    geom_jitter()

  p2 <- seusFALL %>%
    select(lat, lon) %>%
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()

  yrs<-seusFALL %>%
    select(year) %>%
    distinct()

  test <- seusFALL %>%
    #filter(year != 2018,  year != 2019) %>%
    select(stratum, year) %>%
    distinct() %>%
    group_by(stratum) %>%
    summarise(count = n()) %>%
    filter(count >= 33) #FLAG: review this annually!

  test2 <- seusFALL %>%
    #filter(year != 2018,  year != 2019) %>%
    filter(stratum %in% test$stratum)
  nrow(seusFALL) - nrow(test2)
  # percent that will be lost
  print((nrow(seusFALL) - nrow(test2))/nrow(seusFALL))
  # 13.1% are removed

  seusFALL_fltr <- seusFALL  %>%
    #filter(year != 2018,  year != 2019) %>%
    filter(stratum %in% test$stratum)

  # plot the results after editing
  p3 <- seusFALL_fltr %>%
    select(stratum, year) %>%
    ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
    geom_jitter()

  p4 <- seusFALL_fltr %>%
    select(lat, lon) %>%
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()


  if (HQ_PLOTS == TRUE){
    temp <- grid.arrange(p1, p2, p3, p4, nrow = 2)
    ggsave(plot = temp, filename = here::here("data_processing_rcode/output/plots", "seusFALL_hq_dat_removed.png"))
    ggsave(plot = p1, filename = here::here("data_processing_rcode/output/plots", "seusFALL2024.png"))
    rm(temp)
  }
}
#clean up
rm(test, test2, p1, p2, p3, p4)

rm(seus_catch, seus_haul, seus_strata)

# Compile BFISH data (Hawaii) =================================================

bfish_catch <- read_csv(here::here("data_processing_rcode/data", "BFISH_DisMAP_2024_update.csv"), col_types = cols(
                          psu = col_character())) %>%
  rename(haulid = psu) %>%
  mutate(stratumarea = NA) %>%
  select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue)

#NOTE: psu is changed to haulid in this dataset to help match the other field names (helpful with compiling)


# Compile TAX ===============================================================
print("Compile TAX")

tax <- read_csv(here::here("data_processing_rcode/spp_taxonomy_mater_key.csv"), col_types = cols(
  survey_name = col_character(),
  accepted_name = col_character(),
  common = col_character(),
  kingdom = col_character(),
  phylum = col_character(),
  class = col_character(),
  order = col_character(),
  family = col_character(),
  genus = col_character(),
  rank = col_character(),
  worms_id = col_character(),
  SpecCode = col_character()))


tax <- tax  %>%
  # remove any extra white space from around spp and common names
  mutate(survey_name= str_squish(survey_name),
         valid_name= str_squish(accepted_name),
         common = str_squish(common)) %>%
  select(c(survey_name, valid_name, common, rank, class, filtercat)) %>%
  distinct()

tax$survey_name<-firstup(tax$survey_name)

if(isTRUE(WRITE_MASTER_DAT)){
  save(ai, ebs, gmex, goa, neus_fall, neus_spring, seusFALL, seusSPRING, seusSUMMER, tax, wcann, wctri, file = here("data_processing_rcode/output/data_clean", "individual-regions.rds"))
}
if(isTRUE(WRITE_MASTER_DAT)){
  save(ai_fltr, ebs_fltr, gmex_fltr, goa_fltr, neus_fall_fltr, neus_spring_fltr, seusFALL_fltr, seusSPRING_fltr, seusSUMMER_fltr, tax, wcann_fltr, wctri_fltr, file = here("data_processing_rcode/output/data_clean", "individual-regions-fltr.rds"))
}


# Master Data Set ===========================================================
print("Join into Master Data Set")
#Full unfiltered data set
#TO DO: Add gmex back in once that part of the code is reviewed
dat <- rbind(ai, ebs, goa, nbs, neus_fall, neus_spring, seusFALL, seusSPRING, seusSUMMER, wcann, wctri) %>%
  # Remove NA values in wtcpue
  filter(!is.na(wtcpue)) %>%
  # remove any extra white space from around spp and common names
  mutate(spp= str_squish(spp))

#convert all taxa names to first word capitalized and rest lowercase...
dat$spp<-firstup(dat$spp)

#========================== start SPECIES CHECK =============
#Species Taxon checkpoint before proceeding!!
# Check if any new species are in survey data sets before proceeding....take the 'dat' file that combines the individual regions but before joined with 'spp_taxonomy' file
dat_spp <- dat %>%
  select(spp,region) %>%
  distinct() %>%
  mutate(spp_id = 1:nrow(.))

# Anti-join this spp list to the taxon column from the tax file to see which spp are not represented there
not_in_tax <- anti_join(dat_spp, tax, by = c("spp" = "survey_name"))
not_in_tax <- not_in_tax %>% group_by(spp) %>%
  summarise_all(funs(toString(unique(na.omit(.))))) #FLAG: Update to replace `funs()`, which has been deprecated

#if not_in_tax > 0 obs print it out to add those species to Tax file
write.csv(not_in_tax, "not_in_tax.csv")

#========================== end species name check ===========

# add a case sensitive spp and common name
dat <- left_join(dat, tax, by = c("spp" = "survey_name")) %>%
  select(region, haulid, year, lat, lon, stratum, stratumarea, depth, valid_name, common, wtcpue) %>%
  distinct() %>%
  rename(spp = valid_name)

#check for errors in name matching
if(sum(dat$spp == 'NA') > 0 | sum(is.na(dat$spp)) > 0){
  warning('>>create_master_table(): Did not match on some taxon [Variable: `tax`] names.')
}

# #if get warning, check for which spp have NA for name and common if check above fails
spp_na<-dat %>%
  filter(is.na(dat$spp) & is.na(dat$common)) %>%
  select(c("region", "spp", "common")) %>%
  distinct()

# spp_na_list<-unique(c(as.character(spp_na$spp)))
# spp_na<-as.data.frame(spp_na)
# sppNA_unique<-unique(spp_na[c("spp")])
# write.csv(sppNA_unique, "sppNA_unique.csv")

# #get list of higher order taxon names by region/survey and use to generate the list of higher order names to exclude later on
#   dat_HO_list<-dat %>%
#     filter(grepl("HigherOrder", rank)) %>%
#     select(c("region", "spp", "rank")) %>%
#     distinct()

if(isTRUE(REMOVE_REGION_DATASETS)) {
  rm(ai, ebs, gmex, goa, neus_fall, neus_spring, seusFALL, seusSPRING, seusSUMMER, wcann, wctri, tax)
}

if(isTRUE(WRITE_MASTER_DAT)){
  if(isTRUE(PREFER_RDATA)){
    saveRDS(dat, file = here("data_processing_rcode/output/data_clean", "all-regions-full.rds"))
  }else{
    write_csv(dat, file =here("data_processing_rcode/output/data_clean", "all-regions-full.csv"))
  }
}


# Master "Filtered" dataset
## TO DO: Add back in gmex_fltr once that region's code has been fixed

dat_fltr <- rbind(ai_fltr, ebs_fltr, nbs_fltr, goa_fltr, neus_fall_fltr, neus_spring_fltr, seusFALL_fltr, seusSPRING_fltr, seusSUMMER_fltr, wcann_fltr, wctri_fltr) %>%
  # Remove NA values in wtcpue
  filter(!is.na(wtcpue)) %>%
  # remove any extra white space from around spp and common names
  mutate(spp= str_squish(spp))
#convert all taxa names to first word capitalized and rest lowercase...
dat_fltr$spp<-firstup(dat_fltr$spp)
# add a case sensitive spp and common name and filter out Higher Level taxon names, the turtle, bird, and dolphin species, and plants/seaweed species.
dat_fltr <- left_join(dat_fltr, tax, by = c("spp" = "survey_name")) %>%
  filter(!grepl("Remove", filtercat),
         !grepl("Caretta caretta", valid_name),
         !grepl("Sagmatias obliquidens", valid_name),
         !grepl("Puffinus gravis", valid_name),
         !grepl("Phaeophyceae", class),
         !grepl("Florideophyceae", class),
         !grepl("Ulvophyceae", class)) %>%
  select(region, haulid, year, lat, lon, stratum, stratumarea, depth, valid_name, common, wtcpue) %>%
  distinct() %>%
  rename(spp = valid_name)

#check for errors in name matching
if(sum(dat_fltr$spp == 'NA') > 0 | sum(is.na(dat_fltr$spp)) > 0){
  warning('>>create_master_table(): Did not match on some taxon [Variable: `tax`] names.')
}
#if get warning, check for which spp have NA for name and common if check above fails
spp_na<-dat_fltr %>%
  filter(is.na(dat_fltr$spp) & is.na(dat_fltr$common)) %>%
  select(c("region", "spp", "common")) %>%
  distinct()
# rm(spp_na)

#This code chunk is for Appendix II in the Tech report (the species removed from dataset by taxon check and filtering)
filtered_spp <- anti_join(dat, dat_fltr, by = c("region", "spp")) %>%
  select(region, spp, common) %>%
  distinct()
# write.csv(filtered_spp, "filter_removed_spp.csv")

if(isTRUE(REMOVE_REGION_DATASETS)) {
  rm(ai_fltr, ebs_fltr, gmex_fltr, goa_fltr, neus_fall_fltr, neus_spring_fltr, seusFALL_fltr, seusSPRING_fltr, seusSUMMER_fltr, wcann_fltr, wctri_fltr, tax)
}

if(isTRUE(WRITE_MASTER_DAT)){
  if(isTRUE(PREFER_RDATA)){
    saveRDS(dat_fltr, file = here("data_processing_rcode/output/data_clean", "all-regions-full-fltr.rds"))
  }else{
    write_csv(dat_fltr,file=here("data_processing_rcode/output/data_clean", "all-regions-full-fltr.csv"))
  }
}


# Expanded Survey Dataset=================================================
print ("Expanded dataset")
presyr <- present_every_year(dat_fltr, region, spp, common, year)

haulsyr<-num_hauls_year(dat_fltr, region, year)

preshaul<-left_join(presyr, haulsyr, by=c("region", "year")) %>%
  mutate(proportion=((pres/hauls)*100)) %>%
  filter(proportion>=5)

# years in which spp was present in >= 5% of tows
presyrsum <- num_year_present(preshaul, region, spp, common)

# max num years of survey in each region
maxyrs <- max_year_surv(presyrsum, region)

# merge in max years
presyrsum <- left_join(presyrsum, maxyrs, by = "region")
# write.csv(presyrsum, "presyrsum_11_22_22.csv")
# retain all spp present at >5% of tows in at least 2 of the available years in a survey
spplist <- presyrsum %>%
  filter(presyr >= 2) %>%
  select(region, spp, common)

# these species were removed based on the 3/4 years criteria above but we have decided to add them back in based on commercial/recreational importance
spp_addin<-read.csv("data_processing_rcode/data/Add_managed_spp.csv",header=T, sep=",")
spplist<-rbind(spplist, spp_addin) %>%
  distinct()

# Trim dat to these species (for a given region, spp pair in spplist, in dat_fltr, keep only rows that match that region, spp pairing)
trimmed_dat_fltr_expanded <- dat_fltr %>%
  filter(paste(region, spp) %in% paste(spplist$region, spplist$spp))


#add an EBS+NBS combined region =========================
#select years from compiled EBS that match the NBS survey years
years<-c(2010, 2017, 2019, 2021, 2022, 2023)
enbs_trimmed<- trimmed_dat_fltr_expanded  %>% filter(region %in% c("Eastern Bering Sea", "Northern Bering Sea"),
                                                     year %in% years) %>%
  mutate(region="Eastern and Northern Bering Sea")

p1 <- enbs_trimmed %>%
  select(stratum, year) %>%
  ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
  geom_jitter()

p2 <- enbs_trimmed %>%
  select(lat, lon) %>%
  ggplot(aes(x = lon, y = lat)) +
  geom_jitter()

trimmed_dat_fltr_expanded <-rbind(trimmed_dat_fltr_expanded, enbs_trimmed)

if(isTRUE(WRITE_TRIMMED_DAT)){
  if(isTRUE(PREFER_RDATA)){
    saveRDS(trimmed_dat_fltr_expanded, file = here("data_processing_rcode/output/data_clean", "all-regions-trimmed-fltr.rds"))
  }else{
    write_csv(trimmed_dat_fltr_expanded, "data_processing_rcode/data_clean/all-regions-trimmed-fltr.csv")
  }
}

# Trim species (for IDW analysis)===========================================================
print("Trim species")

## FILTERED DATA
# Find a standard set of species (present at least 3/4 of the years of the filtered data in a region)
presyr <- present_every_year(trimmed_dat_fltr_expanded, region, spp, common, year)

haulsyr<-num_hauls_year(trimmed_dat_fltr_expanded, region, year)

preshaul<-left_join(presyr, haulsyr, by=c("region", "year")) %>%
  mutate(proportion=((pres/hauls)*100)) %>%
  filter(proportion>=5)

# years in which spp was present in >= 5% of tows
presyrsum <- num_year_present(preshaul, region, spp, common)

# max num years of survey in each region
maxyrs <- max_year_surv(presyrsum, region)

# merge in max years
presyrsum <- left_join(presyrsum, maxyrs, by = "region")
# write.csv(presyrsum, "presyrsum_11_22_22.csv")
# retain all spp present at least 3/4 of the available years in a survey
spplist_IDW <- presyrsum %>%
  filter(presyr >= (maxyrs * 3/4)) %>%
  select(region, spp, common)

# these species were removed based on the 3/4 years criteria above but we have decided to add them back in based on commercial/recreational importance
spp_addin<-read.csv("data_processing_rcode/data/Add_managed_spp.csv",header=T, sep=",")

spplist_IDW_2<-rbind(spplist_IDW, spp_addin) %>%
  distinct() %>%
  mutate(DistributionProjectName="NMFS/Rutgers IDW Interpolation")
## use this spp list after explode 0 to add a column indicating that these species should be kept for IDW


# Dat_exploded -  Add 0's ======================================================
print("Dat exploded")
# these Sys.time() flags are here::here to see how long this section of code takes to run.
Sys.time()
# This takes about 10 minutes
if (DAT_EXPLODED == TRUE){
  dat.exploded <- as.data.table(trimmed_dat_fltr_expanded)[,explode0(.SD), by="region"]
  saveRDS(dat.exploded, here::here("data_processing_rcode/output/data_clean", "alldata_withzeros.rds"))

  dat_expl_spl <- split(dat.exploded, dat.exploded$region, drop = FALSE)

  if(isTRUE(WRITE_DAT_EXPLODED)){
    if(isTRUE(PREFER_RDATA)){
      lapply(dat_expl_spl, function(x) saveRDS(x, here::here("data_processing_rcode/output/data_clean", paste0('dat_exploded', x$region[1], '.rds'))))
    }else{
      lapply(dat_expl_spl, function(x) write_csv(x, gzfile(here::here("data_processing_rcode/output/data_clean", paste0('dat_exploded', x$region[1], '.csv.gz')))))
    }
  }

}
Sys.time()

#clean up
rm(dat_expl_spl)

## Add the DistributionProjectName column to dat.exploded
#use the spplist2 to indicate which species should be kept for IDW as opposed to which are for both IDW and expanded survey module
dat.exploded<-left_join(dat.exploded, spplist_IDW_2, by=c("spp","common","region"))


## CORE Species -- caught every year of survey =======

print("Core species")

## FILTERED DATA
# Find a standard set of species (present ALL of the years of the filtered data in a region)
presyr <- present_every_year(trimmed_dat_fltr_expanded, region, spp, common, year)

haulsyr<-num_hauls_year(trimmed_dat_fltr_expanded, region, year)

preshaul<-left_join(presyr, haulsyr, by=c("region", "year")) %>%
  mutate(proportion=((pres/hauls)*100))%>%
  filter(proportion>=5)

# years in which spp was present in >= 5% of tows
presyrsum <- num_year_present(preshaul, region, spp, common)

# max num years of survey in each region
maxyrs <- max_year_surv(presyrsum, region)

# merge in max years
presyrsum <- left_join(presyrsum, maxyrs, by = "region")
# retain all spp present all years of the available years in a survey
spplist_core <- presyrsum %>%
  filter(presyr >= maxyrs) %>%
  select(region, spp, common)

## Add column indicating if a species is a core species
#Go to the next section first to create spplist_core
spplist_core$CoreSpecies <- rep("Yes", times = nrow(spplist_core))
dat.exploded <- left_join(dat.exploded, spplist_core, by = c("region", "spp", "common"))
dat.exploded$CoreSpecies[is.na(dat.exploded$CoreSpecies)] <- "No"

#stop and....
## GO TO create_data_for_map_generation.R now
# Update Filter table

###################### CAN STOP HERE ##########################################

# Summary information about # of species in this analysis================

#Species available in the Persistence Module
spp_survey<-dat.exploded %>%
  select(spp, common) %>%
  distinct()

##This creates a df for Appendix I of tech report (list of all species in all the modules)
spp__techreport <- dat.exploded %>%
  group_by(spp, common) %>%
  summarise(regions = paste(unique(region), collapse = ", "),
            .groups = "drop")
write.csv(spp__techreport, "SppList_AppendixI.csv")

#Species available in the Single Species Shift Module
spp_IDW<-dat.exploded %>%
  filter(DistributionProjectName=="NMFS/Rutgers IDW Interpolation") %>%
  select(spp, common) %>%
  distinct()

#Species available in the Regional Summary module
spp_core<-dat.exploded %>%
  filter(CoreSpecies =="Yes")%>%
  select(spp, common) %>%
  distinct()

#number of unique species across all regions
# number of unique species in the species persistence module (5% of tows in a year in at <= 2 of  survey years)
spp_pers <- trimmed_dat_fltr_expanded %>%
  select(region, spp, common) %>%
  distinct() %>%
  group_by(region) %>%
  summarise(spp_pers = n())

#number of unique species within each regional survey (caught 3/4 or years)
spp_reg_counts_IDW<-spplist_IDW_2 %>%
  group_by(region)%>%
  summarise(spp_3_4years=n_distinct(spp))

#number of unique species CAUGHT ALL YEARS within each region
spp_reg_counts_Core<-spplist_core%>%
  group_by(region)%>%
  summarise(spp_all_yrs=n_distinct(spp))

num_spp_summary<-left_join(spp_pers, spp_reg_counts_IDW, by=c("region"))
num_spp_summary<-left_join(num_spp_summary, spp_reg_counts_Core, by=c("region"))
write.csv(num_spp_summary, file=here("data_processing_rcode/output/data_clean", "summary_unique_spp_table_1_16_26.csv"))
# write.csv(spplist_core, file=here("data_processing_rcode/output/data_clean","core_spp_list_7_10_25.csv"))

