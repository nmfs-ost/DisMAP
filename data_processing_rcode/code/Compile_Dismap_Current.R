## ---- DISMAP 2/20/2025
## updated srcipt to include "expanded survey data" for the new Survey Data Module

## updated thru 2023 survey data for all regions except SEUS and Gmex(which is thru 2022)

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
HQ_PLOTS <- TRUE

# 3. Remove ai,ebs,gmex,goa,neus,seus,wcann,wctri, scot. Keep `dat`. #DEFAULT: FALSE
REMOVE_REGION_DATASETS <- FALSE

# # 4. Create graphs based on the data similar to those shown on the website and outputs them to pdf. #DEFAULT:FALSE
# PLOT_CHARTS <- FALSE

# 5. If you would like to write out the clean data, would you prefer it in Rdata or CSV form?  Note the CSV's are much larger than the Rdata files. #DEFAULT:TRUE, FALSE generates CSV's instead of Rdata.
PREFER_RDATA <- TRUE

# 6. Output the clean full master data frame. #DEFAULT:FALSE
WRITE_MASTER_DAT <- TRUE

# 7. Output the clean trimmed data frame. #DEFAULT:FALSE
WRITE_TRIMMED_DAT <- TRUE

# 7. Generate dat.exploded table. #OPTIONAL, DEFAULT:TRUE
DAT_EXPLODED <- TRUE

# 9. Output the dat.exploded table #DEFAULT:FALSE
WRITE_DAT_EXPLODED <- TRUE


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
  readr::type_convert(col_types = cols(
    lat = col_double(),
    lon = col_double(),
    year = col_integer(),
    wtcpue = col_double(),
    spp = col_character(),
    depth = col_integer(),
    haulid = col_character()
  )) %>%
  dplyr::group_by(region, haulid, stratum, stratumarea, year, lat, lon, depth, spp) %>%
  dplyr::summarise(wtcpue = sum(wtcpue, na.rm = TRUE)) %>%
  dplyr::select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue) %>%
  dplyr::ungroup()

# clean up
rm(haul, catch)

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
    filter(count >= 13)

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
    filter(count >= 12) ## I think this may need to change to 12 years?

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
    filter(count >= 5)

  # how many rows will be lost if only stratum trawled ever year aare kept?
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
  catch_id = col_integer(),
  common_name = col_character(),
  cpue_kg_per_ha_der = col_double(),
  cpue_numbers_per_ha_der = col_double(),
  date_yyyymmdd = col_integer(),
  depth_m = col_double(),
  latitude_dd = col_double(),
  longitude_dd = col_double(),
  pacfin_spid = col_character(),
  partition = col_character(),
  performance = col_character(),
  program = col_character(),
  project = col_character(),
  sampling_end_hhmmss = col_character(),
  sampling_start_hhmmss = col_character(),
  scientific_name = col_character(),
  station_code = col_double(),
  subsample_count = col_integer(),
  subsample_wt_kg = col_double(),
  total_catch_numbers = col_integer(),
  total_catch_wt_kg = col_double(),
  tow_end_timestamp = col_datetime(format = ""),
  tow_start_timestamp = col_datetime(format = ""),
  trawl_id = col_double(),
  vessel = col_character(),
  vessel_id = col_integer(),
  year = col_integer(),
  year_stn_invalid = col_integer()
)) %>%
  select("trawl_id","year","longitude_dd","latitude_dd","depth_m","scientific_name","total_catch_wt_kg","cpue_kg_per_ha_der", "partition", "performance")

wcann_haul <- read_csv(here::here("data_processing_rcode/data", "wcann_haul.csv"), col_types = cols(
  area_swept_ha_der = col_double(),
  date_yyyymmdd = col_integer(),
  depth_hi_prec_m = col_double(),
  invertebrate_weight_kg = col_double(),
  latitude_hi_prec_dd = col_double(),
  longitude_hi_prec_dd = col_double(),
  mean_seafloor_dep_position_type = col_character(),
  midtow_position_type = col_character(),
  nonspecific_organics_weight_kg = col_double(),
  performance = col_character(),
  program = col_character(),
  project = col_character(),
  sample_duration_hr_der = col_double(),
  sampling_end_hhmmss = col_character(),
  sampling_start_hhmmss = col_character(),
  station_code = col_double(),
  tow_end_timestamp = col_datetime(format = ""),
  tow_start_timestamp = col_datetime(format = ""),
  trawl_id = col_double(),
  vertebrate_weight_kg = col_double(),
  vessel = col_character(),
  vessel_id = col_integer(),
  year = col_integer(),
  year_stn_invalid = col_integer()
)) %>%
  select("trawl_id","year","longitude_hi_prec_dd","latitude_hi_prec_dd","depth_hi_prec_m","area_swept_ha_der", "performance")
# It is ok to get warning message that missing column names filled in: 'X1' [1].

wcann <- left_join(wcann_haul, wcann_catch, by = c("trawl_id", "year", "performance")) %>%
  filter(performance !='Unsatisfactory')

wcann <- wcann %>%
  mutate(
    # create haulid
    haulid = trawl_id,
    # Add "strata" (define by lat, lon and depth bands) where needed # no need to use lon grids on west coast (so narrow)
    #stratum = paste(floor(latitude_dd)+0.5, floor(depth_m/100)*100 + 50, sep= "-"),
    # adjust for tow area # kg per hectare (10,000 m2)
    wtcpue = total_catch_wt_kg/area_swept_ha_der
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
  # if want to keep the same footprint as wctri
  # how many rows of data will be lost?
  # nrow(wcann) - nrow(filter(wcann, stratum %in% wctri_fltr$stratum))
  # # percent that will be lost - 61% !
  # print((nrow(wcann) - nrow(filter(wcann, stratum %in% wctri_fltr$stratum)))/nrow(wcann))
  #
  # wcann_fltr <- wcann %>%
  #   filter(stratum %in% wctri_fltr$stratum)

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
    filter(count>=20)

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
  rm(p1, p2)
}

# cleanup
rm(wcann_catch, wcann_haul, wcann_strats)

# Compile GMEX ===========================================================
print("Compile GMEX")
##Read in data
gmex_station <- read_csv(here::here("data_processing_rcode/data", "gmex_STAREC.csv"), col_types = cols(.default = col_character())) %>%
  select('STATIONID', 'CRUISEID', 'CRUISE_NO', 'P_STA_NO', 'TIME_ZN', 'TIME_MIL', 'S_LATD', 'S_LATM', 'S_LOND', 'S_LONM', 'E_LATD', 'E_LATM', 'E_LOND', 'E_LONM', 'STAT_ZONE', 'DEPTH_SSTA', 'MO_DAY_YR', 'VESSEL_SPD', 'COMSTAT')

gmex_station <- type_convert(gmex_station, col_types = cols(
  STATIONID = col_integer(),
  CRUISEID = col_integer(),
  CRUISE_NO = col_integer(),
  P_STA_NO = col_character(),
  TIME_ZN = col_integer(),
  TIME_MIL = col_character(),
  S_LATD = col_integer(),
  S_LATM = col_double(),
  S_LOND = col_integer(),
  S_LONM = col_double(),
  E_LATD = col_integer(),
  E_LATM = col_double(),
  E_LOND = col_integer(),
  E_LONM = col_double(),
  DEPTH_SSTA = col_double(),
  STAT_ZONE = col_double(),
  MO_DAY_YR = col_date(format = "%d/%m/%Y"),
  VESSEL_SPD = col_double(),
  COMSTAT = col_character()
))

names(gmex_station)<-tolower(names(gmex_station))

gmex_tow <-readr::read_delim(here::here("data_processing_rcode/data","gmex_INVREC.csv"),
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

gmex_bio <-readr::read_delim(here::here("data_processing_rcode/data","gmex_BGSREC.csv"),
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

gmex_cruise <-read_csv(here::here("data_processing_rcode/data", "gmex_CRUISES.csv"), col_types = cols(.default = col_character())) %>%
  select(CRUISEID, VESSEL, TITLE)


gmex_cruise <- type_convert(gmex_cruise, col_types = cols(CRUISEID = col_integer(), VESSEL = col_integer(), TITLE = col_character()))
names(gmex_cruise)<-tolower(names(gmex_cruise))

gmex_spp <-read_csv(here::here("data_processing_rcode/data","gmex_BCT_NFR_01182023.csv"))
problems(gmex_spp)
names(gmex_spp)<-tolower(names(gmex_spp))
gmex_spp<- gmex_spp %>%
  dplyr::select(biocode,ciu_biocode,taxon)

##Resolve issues
#Issue 1: Proper way to Merge the Tow (invrec) and bio (bgsrec) tables
# The proper way to link the invrec table to the bgsrec is supposed to use the invrecid
# variable as the primary key. However, the bgsrec table has null invrecid for data collected
# under previous data collection systems. The invrec and bgsrec tables can be linked using
# the vessel, cruise_no and p_sta_no variables as a primary key. Unfortunately, there are
# a series stations where the Oregon II (Vessel 4 Cruise_No = 0284) towed standard
# shrimp trawls (ST) side by side (port/starboard) with experimental trawls (ES). Therefore,
# linking the invrec and bgsrec tabls based on the vessel, cruise_no and p_sta_no variables
# will lead to all catch records for both the shrimp and experimental trawls being linked
# to both trawls. The bgsrec also contains records for catches not associated with invrec table
# records. These are from reef fish cruises. The following codes creates a modified bgsrec table
# that updates the null invrecid for older data and performs some checks.

names(gmex_tow) <- tolower(names(gmex_tow))
names(gmex_bio) <- tolower(names(gmex_bio))
#create bgsrec_invrecid_fix
#get only stationid and invrecid from invrec table
get_stationid_invrecid <- gmex_tow %>%
  dplyr::select(stationid, invrecid) %>%
  rename(inv_invrecid = invrecid)

#extract bgsrec table records with missing invrecid and update based on stationid from get_stationid_invrecid
bgsrec_null_invrecid <- gmex_bio %>%
  dplyr::filter(is.na(invrecid)) %>%
  dplyr::left_join(get_stationid_invrecid, by = 'stationid') %>%
  dplyr::mutate(invrecid = inv_invrecid) %>%
  dplyr::select(-inv_invrecid)

#Extracts any remaining bgsrec table records with null invrecid. These should all be
#associated with reef fish cruises at this point.
bgsrec_null_check1 <- bgsrec_null_invrecid %>%
  dplyr::filter(is.na(invrecid))

#extract bgsrec table records with valid invrecid
bgsrec_with_invrecid <- gmex_bio %>%
  dplyr::filter(!is.na(invrecid))

#Stack bgsrec_null_invrec now updated with valid invrecid and bgsrec_with_invrecid
gmex_bio_mod <- bgsrec_null_invrecid %>%
  dplyr::bind_rows(bgsrec_with_invrecid) %>%
  #Remove null invrecid which should only include those in bgsrec_null_check1
  dplyr::filter(!is.na(invrecid)) %>%
  dplyr::arrange(bgsid)


#Check to make sure only records with invrecs are present - should have 0 rows
bgsrec_null_check2 <- gmex_bio_mod %>% filter(is.na(invrecid))

#drop unwanted data objects
rm(bgsrec_null_invrecid,bgsrec_null_check1,bgsrec_null_check2,bgsrec_with_invrecid,get_stationid_invrecid, gmex_bio)
# garbace collect to free up memory
gc()

#Issues 2: Taxonomic coding
# (2-1) The newbiocodesbig table does not fully contain all code/taxonomic names found in the bgsrec table:
# (2-2) the bgsrec table has a few instances of invalid bio_bgs (biocode) values; and
# (2-3) multiple code/taxonomic combinations may refer to the same organisms under different names. For example,
# 189040204/MONACANTHUS HISPIDUS, 189040305/STEPHANOLEPIS HISPIDA, 189040306/STEPHANOLEPIS HISPIDUS
# and 189040307/STEPHANOLEPIS HISPIDA (current) have all been used to identify Planehead Filefish due to
# changes in taxonomy. The bsgrec file reflects the code/taxonomic use at time of data ingest.
# The provided master biocode table (MBT) will allow translation of the vast majority cases where multiple
# code/taxonomic refer to the same organism. The process relies on the use of the biocode,
# ciu_biocode and taxon variables in the MBT. The MBT biocode variable in numeric form is equivalent to the
# code (character) variable in the newbiocodesbig and bio_bgs (character) variable in the bgsrec tables.
# Similarly the taxon variable in the MBT table is equivalent to taxonomic in the newbiocodesbig table.
# The MBT also has a rb_biocode (replaced by biocode) variable which is the numeric biocode that
# replaces a inactive (inactive = 1 variable) biocode, and allows me to track changes over time.
# Since multiple changes may have occurred, the ciu_biocode (currently in use biocode) value ties multiple records
# that are now inactive to the current active biocode. Inactive biocodes have the variable inactive set to zero.
# Using the example above, the ciu_biocode that ties together records of Planehead Filefish is 189040307.
# The following script updates bgsrec table code to ciu_biocode via the MBT table. The rb_biocode variable is not
# needed for this purpose.

# starting with our gmex_bio_mod from above
gmex_bio_utax1 <- gmex_bio_mod %>%
  #convert bgsrec table bio_bgs varialbe to numeric integer
  dplyr::mutate(bio_bgs = as.integer(bio_bgs)) %>%
  #rename bio_bgs to biocode to allow for easier manipulation with master biocode table (mbt)
  dplyr::rename(biocode = bio_bgs) %>%
  ### take care of Issue 2-2 ###
  # fix invalid zero code and make it the code (999999998) for unidentified specimen
  dplyr::mutate(biocode = ifelse(biocode == 0,999999998,biocode)) %>%
  # fix invalid unidentified fish code 100000001 to proper code
  dplyr::mutate(biocode = ifelse(biocode == 100000001,100000000,biocode)) %>%
  # fix invalid unidentified crustacean code 200000001 to proper code
  dplyr::mutate(biocode = ifelse(biocode == 200000001,200000000,biocode)) %>%
  # fix invalid unidentified crustacean code 300000001  and 300000001 to proper code
  dplyr::mutate(biocode = ifelse(biocode == 300000001,300000000,biocode)) %>%
  dplyr::mutate(biocode = ifelse(biocode == 300000002,300000000,biocode)) %>%
  ### take care of Issue 2-3 ###
  #update older inactive biocodes to those currently in use (ciu_biocode)
  dplyr::left_join(gmex_spp, by = "biocode")

### Issue 3: Problematic Taxa with taxonomic issues or problematic separation in the field###
# Collapse taxa with known identification issues and collapse all sponge to single category
# Note this process needs to be implemented after the ciu_biocode update as the statements
# rely on the ciu_biocode. The statements undergo a review with each updated version of the
# MBT
gmex_bio_utax2 <- gmex_bio_utax1 %>%
  #Take care of squid and species complexes...
  #Update the squid genus Loligo and all species under genus Doryteuthis to the genus Doryteuthis
  mutate(ciu_biocode = ifelse(ciu_biocode %in% c(347020200,347021001,347021002,347021003),347021000,ciu_biocode)) %>%
  mutate(taxon = ifelse(ciu_biocode %in% c(347021000),'DORYTEUTHIS SP',taxon)) %>%
  # #Update batfish species to Halieutichthys
  mutate(ciu_biocode = ifelse(ciu_biocode >= 195050401 & ciu_biocode <= 195050405,195050400,ciu_biocode)) %>%
  mutate(taxon = ifelse(ciu_biocode %in% c(195050400),'HALIEUTICHTHYS SP',taxon)) %>%
  #Update all jellfishy in the genus Aurelia to the genus Aurelia
  mutate(ciu_biocode = ifelse(ciu_biocode >= 618010101 & ciu_biocode <= 618010105,618010100,ciu_biocode)) %>%
  mutate(taxon = ifelse(ciu_biocode %in% c(618010100),'AURELIA',taxon)) %>%
  #Update all lionfishes species to the genus Pterois
  mutate(ciu_biocode = ifelse(ciu_biocode %in% c(168011901,168011902),168011900,ciu_biocode)) %>%
  mutate(taxon = ifelse(ciu_biocode %in% c(168011900),'PTEROIS',taxon)) %>%
  #smoothhounds (Mustelus) Managed as species complex, our ids are OK now but in the past assumptions made %>%
  mutate(ciu_biocode = ifelse(ciu_biocode %in% c(108031101,108031102,108031103,108031104),108031100,ciu_biocode)) %>%
  mutate(taxon = ifelse(ciu_biocode %in% c(108031100),'MUSTELUS SP',taxon)) %>%
  #lump all sponge identifications to Porifera
  mutate(ciu_biocode = ifelse(ciu_biocode >= 613000000 & ciu_biocode < 616000000,613000000,ciu_biocode)) %>%
  mutate(taxon = ifelse(ciu_biocode %in% c(613000000),'PORIFERA',taxon)) %>%
  #handle out of order Porifera  Demospngiae and Agelas and Agelas and Agelasidae in coral numbers
  mutate(ciu_biocode = ifelse(ciu_biocode %in% c(999997000,999997020,617170000,617170100),613000000,ciu_biocode)) %>%
  mutate(taxon = ifelse(ciu_biocode %in% c(613000000),'PORIFERA',taxon)) %>%
  #Collapse all shrimp species in Rimnapenaeus as they are not consistently seperated in the field
  mutate(ciu_biocode = ifelse(ciu_biocode %in% c(228012001,228012002),228012000,ciu_biocode)) %>%
  mutate(taxon = ifelse(ciu_biocode %in% c(228012000),'RIMAPENAEUS',taxon)) %>%
  #Astropecten species have changed, distribution overlap with major east west differences
  mutate(biocode = ifelse(biocode >= 691010101 & biocode <= 691010112,691010100,biocode)) %>%
  mutate(taxon = ifelse(biocode %in% c(691010100),'ASTROPECTEN',taxon))



### PAUSED HERE ####


## Merge the corrected catch/tow/species information from above with cruise information, but only for shrimp trawl tows (ST)
gmex <- left_join(gmex_bio_utax2, gmex_tow, by = c("stationid","vessel", "cruise_no", "p_sta_no", "invrecid")) %>%
  # add station location and related data
  left_join(gmex_station, by = c("cruiseid", "stationid", "cruise_no", "p_sta_no")) %>%
  # add cruise title
  left_join(gmex_cruise, by = c("cruiseid", "vessel")) %>%
  #filter out YOY (denoted by BSGCODE=T) since they are useful for counts by not weights
  filter(bgscode != "T"| is.na(bgscode))

gmex <- gmex %>%
  # Trim to high quality SEAMAP summer trawls, based off the subset used by Jeff Rester's GS_TRAWL_05232011.sas
  filter(grepl("Summer", title) &
           gear_size == 40 &
           mesh_size == 1.63 &
           # OP has no letter value
           !grepl("[A-Z]", op)) %>%
  mutate(
    # Create a unique haulid
    haulid = paste(formatC(vessel, width=3, flag=0), formatC(cruise_no, width=3, flag=0), formatC(p_sta_no, width=5, flag=0, format='d'), sep='-'),
    # Extract year where needed
    year = year(mo_day_yr),
    # Calculate decimal lat and lon, depth in m, where needed
    s_latd = ifelse(s_latd == 0, NA, s_latd),
    s_lond = ifelse(s_lond == 0, NA, s_lond),
    e_latd = ifelse(e_latd == 0, NA, e_latd),
    e_lond = ifelse(e_lond == 0, NA, e_lond),
    lat = rowMeans(cbind(s_latd + s_latm/60, e_latd + e_latm/60), na.rm=T),
    lon = -rowMeans(cbind(s_lond + s_lonm/60, e_lond + e_lonm/60), na.rm=T),
    # Add "strata" (define by STAT_ZONE and depth bands)
    # degree bins, # degree bins, # 100 m bins
    #stratum = paste(STAT_ZONE, floor(depth/100)*100 + 50, sep= "-")
  )

#add stratum code defined by STAT_ZONE and depth bands (note depth in recorded as m, and depth bands based on 0-20 fathoms
# and 21-60 fathoms))
gmex$depth_zone<-ifelse(gmex$depth_ssta<=36.576, "20",
                        ifelse(gmex$depth_ssta>36.576, "60", NA))
gmex<-gmex %>%
  mutate(stratum = paste(stat_zone, depth_zone, sep= "-"))

# # fix speed
# Trim out or fix speed and duration records
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

# while comsat is still present
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
    wtcpue = 10000*select_bgs/(vessel_spd * 1.85200 * 1000 * min_fish / 60 * gear_size * 0.3048)
  ) %>%
  # remove non-fish
  filter(
    spp != '' | !is.na(spp),
    # remove unidentified spp
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
    geom_jitter()

  p2 <- gmex %>%
    select(lat, lon) %>%
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()


  test <- gmex %>%
    filter(year >= 2010, year!=2023) %>% #switched to 2010 and after since 2008-2009 were experimental years
    select(stratum, year) %>%
    distinct() %>%
    group_by(stratum) %>%
    summarise(count = n()) %>%
    filter(count >=10) # removes strata that are poorly sampled through time

  # how many rows will be lost if years where all strata sampled (>2008) are kept?
  test2 <- gmex %>%
    filter(stratum %in% test$stratum)
  nrow(gmex) - nrow(test2)
  # percent that will be lost
  print((nrow(gmex) - nrow(test2))/nrow(gmex))
  # lose % of rows

  gmex_fltr <- gmex %>%
    filter(stratum %in% test$stratum) %>%
    filter(year>=2010, year != 2023)

  #### #filter out the points that are outside of the standard survey extent
  # library(sf)
  # library(sp)
  # shape<-read_sf(dsn="~/transfer/DisMAP project/IDW_survey_shapefiles/GMEX_IDW", layer="GMEX_IDW_Region")
  # plot(shape)
  # points<-gmex_fltr %>%
  #   sf::st_as_sf(coords=c("lon", "lat"))
  # st_crs(points)<-4326
  # shape<-sf::st_transform(shape, CRS("+proj=longlat"))
  # st_crs(shape)<-4326
  #
  # library(tmap)
  # tmap::qtm(points)
  # ponts_in_boundary<-st_intersection(points, shape)
  # tmap::qtm(ponts_in_boundary)
  # gmex_coords <- unlist(st_geometry(ponts_in_boundary)) %>%
  #   matrix(ncol=2,byrow=TRUE) %>%
  #   as_tibble() %>%
  #   setNames(c("lon","lat"))
  # gmex_bind<-bind_cols(ponts_in_boundary, gmex_coords)
  # gmex_fltr<-as.data.frame(gmex_bind) %>%
  #   select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue)
  #
  # plot_new<-gmex_fltr %>%
  #   select(lat, lon)
  # # plot_old<-gmex_fltr %>%
  # #   select(lat, lon)
  # ggplot()+
  #   geom_sf(data=shape, color="red")+
  #   geom_point(data=plot, aes(x = lon, y = lat), color="blue")
  #   # geom_point(data=plot_new, aes(x = lon, y = lat), color="green")

  p3 <- gmex_fltr %>%
    select(stratum, year) %>%
    ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
    geom_jitter()

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
rm(gmex_bio, gmex_cruise, gmex_spp, gmex_station, gmex_tow, problems,gmex_bio_mod, gmex_bio_utax2, gmex_bio_utax1, dups)

# Compile Northeast US ===========================================================
print("Compile NEUS")
## 2023 update, NEFSC gave data set already with the conversions done
#read strata file
neus_strata <- read_csv(here::here("data_processing_rcode/data", "neus_strata.csv"), col_types = cols(.default = col_character())) %>%
  select(stratum, stratum_area) %>%
  mutate(stratum = as.double(stratum)) %>%
  distinct()

#read in catch file, which includes both spring and fall survey. Need to parse them out
neus_catch <- read.csv("data_processing_rcode/data/NEFSC_BTS_ALLCATCHES_May2024.csv", header=T, sep=",")%>%
  filter(!is.na(SCINAME)) %>%
  mutate(SVSPP = as.character(SVSPP))
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
    filter(year != 2017, year >= 1974) %>%
    select(stratum, year) %>%
    distinct() %>%
    group_by(stratum) %>%
    summarise(count = n())%>%
    filter(count >= 46)

  # how many rows will be lost if only stratum trawled fairly consistently (>46 years - so all but 2 of the years) are kept?
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
         wtcpue = EXPCATCHWT)  %>%
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
    filter(year != 2020,year != 2014, year != 1975, year > 1973) %>%
    select(stratum, year) %>%
    distinct() %>%
    group_by(stratum) %>%
    summarise(count = n())%>%
    filter(count >= 44) #note: every year would be 46, but that would lost some key strata in the south

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
seus_catch <- read_csv(here::here("data_processing_rcode/data", "seus_catch.csv"), col_types = cols(.default = col_character())) %>%
  # remove symbols
  mutate_all(list(~str_replace(., "=", ""))) %>%
  mutate_all(list(~str_replace(., '"', ''))) %>%
  mutate_all(list(~str_replace(., '\"', '')))

# The 9 parsing failures are due to the metadata at the end of the file that does not fit into the data columns

# problems should have 0 obs
problems <- problems(seus_catch) %>%
  filter(!is.na(col))
stopifnot(nrow(problems) == 0)

# convert the columns to their correct formats
seus_catch <- type_convert(seus_catch, col_types = cols(
  PROJECTNAME = col_character(),
  PROJECTAGENCY = col_character(),
  DATE = col_character(),
  EVENTNAME = col_character(),
  COLLECTIONNUMBER = col_character(),
  VESSELNAME = col_character(),
  GEARNAME = col_character(),
  GEARCODE = col_character(),
  SPECIESCODE = col_character(),
  MRRI_CODE = col_character(),
  SPECIESSCIENTIFICNAME = col_character(),
  SPECIESCOMMONNAME = col_character(),
  NUMBERTOTAL = col_integer(),
  SPECIESTOTALWEIGHT = col_double(),
  SPECIESSUBWEIGHT = col_double(),
  SPECIESWGTPROCESSED = col_character(),
  WEIGHTMETHODDESC = col_character(),
  ORGWTUNITS = col_character(),
  EFFORT = col_character(),
  CATCHSUBSAMPLED = col_logical(),
  CATCHWEIGHT = col_double(),
  CATCHSUBWEIGHT = col_double(),
  TIMESTART = col_character(),
  DURATION = col_integer(),
  TOWTYPETEXT = col_character(),
  LOCATION = col_character(),
  REGION = col_character(),
  DEPTHZONE = col_character(),
  ACCSPGRIDCODE = col_character(),
  STATIONCODE = col_character(),
  EVENTTYPEDESCRIPTION = col_character(),
  TEMPSURFACE = col_double(),
  TEMPBOTTOM = col_double(),
  SALINITYSURFACE = col_double(),
  SALINITYBOTTOM = col_double(),
  SDO = col_character(),
  BDO = col_character(),
  TEMPAIR = col_double(),
  LATITUDESTART = col_double(),
  LATITUDEEND = col_double(),
  LONGITUDESTART = col_double(),
  LONGITUDEEND = col_double(),
  SPECSTATUSDESCRIPTION = col_character(),
  LASTUPDATED = col_character()
))

seus_haul <- read_csv(here::here("data_processing_rcode/data", "seus_haul.csv"), col_types = cols(.default = col_character())) %>%
  distinct(EVENTNAME, DEPTHSTART)  %>%
  # remove symbols
  mutate_all(list(~str_replace(., "=", ""))) %>%
  mutate_all(list(~str_replace(., '"', ''))) %>%
  mutate_all(list(~str_replace(., '"', '')))

# problems should have 0 obs
problems <- problems(seus_haul) %>%
  filter(!is.na(col))
stopifnot(nrow(problems) == 0)

seus_haul <- type_convert(seus_haul, col_types = cols(
  EVENTNAME = col_character(),
  DEPTHSTART = col_integer()
))

seus <- left_join(seus_catch, seus_haul, by = "EVENTNAME")

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

#Create a 'SEASON' column using 'MONTH' as a criteria
seus <- seus %>%
  mutate(DATE = as.Date(DATE, "%m-%d-%Y"),
         MONTH = month(DATE)) %>%
  # create season column -- FLAG, in 2023 the survey was conducted in two "seasons" see here for details: https://seamap.org/seamap-sa-coastal-trawl/
  mutate(SEASON = NA,
         SEASON = ifelse(MONTH >= 1 & MONTH <= 3, "winter", SEASON),
         SEASON = ifelse(MONTH >= 4 & MONTH <= 6, "spring", SEASON),
         SEASON = ifelse(MONTH >= 7 & MONTH <= 8, "summer", SEASON),
         #September EVENTS were grouped with summer, should be fall because all
         #hauls made in late-September during fall-survey
         SEASON = ifelse(MONTH >= 9 & MONTH <= 12, "fall", SEASON))

# find rows where weight wasn't provided for a species
misswt <- seus %>%
  filter(is.na(SPECIESTOTALWEIGHT)) %>%
  select(SPECIESCODE, SPECIESSCIENTIFICNAME) %>%
  distinct()

# calculate the mean weight for those species
meanwt <- seus %>%
  filter(SPECIESCODE %in% misswt$SPECIESCODE) %>%
  group_by(SPECIESCODE) %>%
  summarise(mean_wt = mean(SPECIESTOTALWEIGHT, na.rm = T))

# rows that need to be changed
change <- seus %>%
  filter(is.na(SPECIESTOTALWEIGHT))

# remove those rows from SEUS
seus <- anti_join(seus, change)

# change the rows
change <- change %>%
  select(-SPECIESTOTALWEIGHT)

# update the column values
change <- left_join(change, meanwt, by = "SPECIESCODE") %>%
  rename(SPECIESTOTALWEIGHT = mean_wt)

# rejoin to the data
seus <- rbind(seus, change)


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

# calculate trawl distance in order to calculate effort
# create a matrix of starting positions
start <- as.matrix(seus[,c("LONGITUDESTART", "LATITUDESTART")], nrow = nrow(seus), ncol = 2)
# create a matrix of ending positions
end <- as.matrix(seus[,c("LONGITUDEEND", "LATITUDEEND")], nrow = nrow(seus), ncol = 2)
# add distance to seus table
seus <- seus %>%
  mutate(distance_m = geosphere::distHaversine(p1 = start, p2 = end),
         distance_km = distance_m / 1000.0,
         distance_mi = distance_m / 1609.344) %>%
  # calculate effort = mean area swept
  # EFFORT = 0 where the boat didn't move, distance_m = 0
  mutate(EFFORT = (13.5 * distance_m)/10000,
         # Create a unique haulid
         haulid = EVENTNAME,
         # Extract year where needed
         year = substr(EVENTNAME, 1,4)
  ) %>%
  rename(
    stratum = STRATA,
    lat = LATITUDESTART,
    lon = LONGITUDESTART,
    depth = DEPTHSTART,
    spp = SPECIESSCIENTIFICNAME,
    stratumarea = STRATAHECTARE)

seus$year <- as.integer(seus$year)

#In seus there are two 'COLLECTIONNUMBERS' per 'EVENTNAME', with no exceptions,
#for each side of the boat;
#EFFORT is always the same for each COLLECTIONNUMBER
# We sum the two tows in seus (port and starboard tows), and this steps deletes any haul id x spp duplicates
seus <- seus %>%
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
  summarise(biomass = sumna(SPECIESTOTALWEIGHT)) %>%
  mutate(wtcpue=biomass/(EFFORT*2)) %>%
  # add temporary region column that will be converted to seasonal
  mutate(region = "Southeast US") %>%
  select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue, SEASON) %>%
  ungroup()

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

  test <- seusSPRING %>%
    select(stratum, year) %>%
    distinct() %>%
    group_by(stratum) %>%
    summarise(count = n()) %>%
    filter(count >= 29) # strata sampled all but a few year!!

  # how many rows will be lost if only stratum trawled ever year are kept?
  test2 <- seusSPRING %>%
    filter(stratum %in% test$stratum)
  nrow(seusSPRING) - nrow(test2)
  # percent that will be lost
  print((nrow(seusSPRING) - nrow(test2))/nrow(seusSPRING))
  # 6% are removed

  seusSPRING_fltr <- seusSPRING %>%
    filter(stratum %in% test$stratum)

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

  test <- seusFALL %>%
    #filter(year != 2018,  year != 2019) %>%
    select(stratum, year) %>%
    distinct() %>%
    group_by(stratum) %>%
    summarise(count = n()) %>%
    filter(count >= 31)

  test2 <- seusFALL %>%
    #filter(year != 2018,  year != 2019) %>%
    filter(stratum %in% test$stratum)
  nrow(seusFALL) - nrow(test2)
  # percent that will be lost
  print((nrow(seusFALL) - nrow(test2))/nrow(seusFALL))
  # 5.1% are removed

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
    rm(temp)
  }
}
#clean up
rm(test, test2, p1, p2, p3, p4)

rm(seus_catch, seus_haul, seus_strata, end, start, meanwt, misswt, biomass, problems, change, seus)

# # COMPILE CANADIAN REGIONS ==================================================
# # Compile Maritimes =========================================================
# spp_files <- as.list(dir(pattern = "_SPP", path = "data", full.names = T))
# mar_spp <- spp_files %>%
#   purrr::map_dfr(~ readr::read_csv(.x, col_types = cols(
#     SPEC = col_character()
#   )))
#
# mar_spp <- mar_spp %>%
#   rename(spp = SPEC,
#          SPEC = CODE) %>%
#   distinct()
#
# mission_files <- as.list(dir(pattern = "_MISSION", path = "data", full.names = T))
# mar_missions <- mission_files %>%
#   purrr::map_dfr(~ readr::read_csv(.x, col_types = cols(
#     .default = col_double(),
#     MISSION = col_character(),
#     VESEL = col_character(),
#     SEASON = col_character()
#   )))
#
# info_files <- as.list(dir(pattern = "_INF", path = "data", full.names = T))
# mar_info <- info_files %>%
#   purrr::map_dfr(~ readr::read_csv(.x, col_types = cols(
#     .default = col_double(),
#     MISSION = col_character(),
#     SDATE = col_character(),
#     GEARDESC = col_character(),
#     STRAT = col_character()
#   )))
#
# catch_files <- as.list(dir(pattern = "_CATCH", path = "data", full.names = T))
# mar_catch <- catch_files %>%
#   purrr::map_dfr(~ readr::read_csv(.x, col_types = cols(
#     .default = col_double(),
#     MISSION = col_character()
#   )))
#
# mar <- left_join(mar_catch, mar_missions, by = "MISSION")
#
# mar <- mar %>%
#   # Create a unique haulid
#   mutate(
#     haulid = paste(formatC(MISSION, width=3, flag=0), formatC(SETNO, width=3, flag=0)))
#
# mar_info <- mar_info %>%
#   # Create a unique haulid
#   mutate(
#     haulid = paste(formatC(MISSION, width=3, flag=0), formatC(SETNO, width=3, flag=0)))
#
# drops <- c("MISSION","SETNO")
# mar_info <- mar_info[ , !(names(mar_info) %in% drops)]
#
# mar <- left_join(mar, mar_info, by = "haulid")
# mar <- left_join(mar, mar_spp, by = "SPEC")
# mar$region <- "Maritimes"
#
# names(mar) <- tolower(names(mar))
#
#
# mar <- mar %>%
#   # convert mission to haul_id
#   rename(wtcpue = totwgt,
#          lat = slat,
#          lon = slong,
#          stratum = strat)
#
# # calculate stratum area for each stratum
# mar <- mar %>%
#   group_by(stratum) %>%
#   filter(stratum != 'NA') %>%
#   mutate(stratumarea = calcarea(lon, lat)) %>%
#   ungroup()
#
#
# # Does the spp column contain any eggs or non-organism notes? #many eggs and unidentified names that need to be removed
# # test <- mar %>%
# #   select(spp) %>%
# #   filter(!is.na(spp)) %>%
# #   distinct() %>%
# #   mutate(spp = as.factor(spp)) %>%
# #   filter(grepl("UNIDENTIFIED", spp) & grepl("", spp))
# #  #filter(grepl("EGG", spp) & grepl("", spp))
# # stopifnot(nrow(test)==0)
#
# # combine the wtcpue for each species by haul
# mar <- mar %>%
#   # remove unidentified spp and non-species
#   filter(spp != "" | !is.na(spp),
#   !grepl("EGG", spp),
#   !grepl("UNIDENTIFIED", spp),
#   !grepl("PURSE", spp),
#   !grepl("UNID. FISH", spp),
#   !grepl("UNID FISH AND INVERTEBRATES", spp),
#   !grepl("UNID REMAINS,DIGESTED", spp),
#   !grepl("UNID FISH AND REMAINS", spp),
#   !grepl("CALAPPA MEGALOPS",spp),
#   !grepl("MARINE INVERTEBRATA", spp),
#   !grepl("EMPTY", spp),
#   !grepl("SHELLS", spp),
#   !grepl("RESERVED", spp),
#   !grepl("SAND TUBE", spp),
#   !grepl("SHARK", spp),
#   !grepl("SHRIMP-LIKE", spp),
#   !grepl("UNKNOWN FISH",spp),
#   !grepl("^MUD$", spp),
#   !grepl("WATER", spp),
#   !grepl("DEBRIS", spp),
#   !grepl("FISH REMAINS", spp),
#   !grepl("POLYCHAETE REMAINS", spp),
#   !grepl("CRUSTACEA LARVAE", spp),
#   !grepl("FOREIGN ARTICLES,GARBAGE", spp),
#   !grepl("NO LONGER USED - PHAKELLIA SPP.", spp),
#   !grepl("PARASITES,ROUND WORMS", spp),
#   !grepl("POLYCHAETA C.,LARGE", spp),
#   !grepl("POLYCHAETA C.,SMALL", spp),
#   !grepl("SEA CORALS", spp),
#   !grepl("STONES AND ROCKS", spp),
#   !grepl("CRAB", spp)) %>%
#   group_by(haulid, stratum, stratumarea, year, season, lat, lon, depth, spp, region) %>%
#   summarise(wtcpue = sumna(wtcpue)) %>%
#   ungroup() %>%
#   # remove extra columns
#   select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue, season)
#
# rm(mar_catch, mar_info, mar_missions, mar_spp, mission_files, info_files, spp_files, catch_files)
#
# #mar$spp <- firstup(mar$spp)
#
# # Maritimes Fall ====
# marFall <- mar %>%
#   ungroup() %>%
#   filter(season == "FALL") %>%
#   select(-season) %>%
#   mutate(region = "Maritimes Fall")
#
#     # # plot the strata by year
#     p1 <- marFall %>%
#       select(stratum, year) %>%
#       ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
#       geom_jitter()
#     p2 <- marFall %>%
#       select(lat, lon) %>%
#       ggplot(aes(x = lon, y = lat)) +
#       geom_jitter()
#     #
#
# # Maritimes Spring ====
# marSpring <- mar %>%
#   ungroup() %>%
#   filter(season == "SPRING") %>%
#   select(-season) %>%
#   mutate(region = "Maritimes Spring")
#
#     # # plot the strata by year
#     p1 <- marSpring %>%
#       select(stratum, year) %>%
#       ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
#       geom_jitter()
#     p2 <- marSpring %>%
#       select(lat, lon) %>%
#       ggplot(aes(x = lon, y = lat)) +
#       geom_jitter()
#     #
#     # grid.arrange(p1, p2, nrow = 2)
#
# # Maritimes Summer ====
# marSummer <- mar %>%
#   ungroup() %>%
#   filter(season == "SUMMER") %>%
#   select(-season) %>%
#   mutate(region = "Maritimes Summer")
#
#     # # plot the strata by year
#     p1 <- marSummer %>%
#       select(stratum, year) %>%
#       ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
#       geom_jitter()
#     p2 <- marSummer %>%
#       select(lat, lon) %>%
#       ggplot(aes(x = lon, y = lat)) +
#       geom_jitter()
#     #
#     # grid.arrange(p1, p2, nrow = 2)
#
# test <- mar %>%
#   filter(region != "4VSW")
# #
# # # plot the strata by year without 4VSW
# p1 <- test %>%
#   select(stratum, year) %>%
#   ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
#   geom_jitter()
# p2 <- mar %>%
#   select(lat, lon) %>%
#   ggplot(aes(x = lon, y = lat)) +
#   geom_jitter()
# #
# # grid.arrange(p1, p2, nrow = 2)
#
# # ONLY consistent methodology and coverage occurred in Summer, so will only use the SUMMER data for furthur analysis
#
# if (HQ_DATA_ONLY == TRUE){
#   # look at the graph and make sure decisions to keep or eliminate data make sense
#
#   # plot the strata by year
#   p1 <- marSummer %>%
#     select(stratum, year) %>%
#     ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
#     geom_jitter()
#   p2 <- marSummer %>%
#     select(lat, lon) %>%
#     ggplot(aes(x = lon, y = lat)) +
#     geom_jitter()
#
#   # find strata sampled every year
#   annual_strata <- marSummer %>%
#     filter(year != 2018) %>%
#     select(stratum, year) %>%
#     distinct() %>%
#     group_by(stratum) %>%
#     summarise(count = n()) %>%
#     filter(count >= 25)
#
#   # find strata sampled every year
#   annual_strata_old <- marSummer %>%
#     select(stratum, year) %>%
#     distinct() %>%
#     group_by(stratum) %>%
#     summarise(count = n())
#
#   sum(length(unique(annual_strata_old$count)) - length(unique(annual_strata$count)))
#   # how many rows will be lost if only stratum trawled ever year are kept?
#   test <- marSummer %>%
#     filter(year!= 2018) %>%
#     filter(stratum %in% annual_strata$stratum)
#   nrow(marSummer) - nrow(test)
#   # percent that will be lost
#   print((nrow(marSummer) - nrow(test))/nrow(marSummer))
#   # 7.6% are removed
#
#   mar_fltr <- marSummer  %>%
#     filter(year != 2018) %>%
#     filter(stratum %in% annual_strata$stratum)
#
#   p3 <- mar_fltr %>%
#     select(stratum, year) %>%
#     ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
#     geom_jitter()
#
#   p4 <- mar_fltr %>%
#     select(lat, lon) %>%
#     ggplot(aes(x = lon, y = lat)) +
#     geom_jitter()
#
#   if (HQ_PLOTS == TRUE){
#     temp <- grid.arrange(p1, p2, p3, p4, nrow = 2)
#     ggsave(plot = temp, filename = here::here("data_processing_rcode/output/plots", "mar_hq_dat_removed.png"))
#   }
# }
#
#
# # Compile Canadian Pacific ---------------------------------------------------
# print("Compile CPAC")
#
# #Queen Charlotte Sound
#
# files <- as.list(dir(pattern = "QCS", path = "data", full.names = T))
#
#
# QCS_catch <- read_csv(here::here("data_processing_rcode/data", "QCS_catch.csv"), col_types = cols(
#   Survey.Year = col_integer(),
#   Trip.identifier = col_integer(),
#   Set.number = col_integer(),
#   ITIS.TSN = col_integer(),
#   Species.code = col_character(),
#   Scientific.name = col_character(),
#   English.common.name = col_character(),
#   French.common.name = col_character(),
#   LSID = col_character(),
#   Catch.weight..kg. = col_double(),
#   Catch.count..pieces. = col_integer()
# )) %>%
#   select(Trip.identifier, Set.number,Survey.Year, ITIS.TSN, Species.code, Scientific.name, English.common.name, Catch.weight..kg.)
#
# QCS_effort <- read_csv(here::here("data_processing_rcode/data", "QCS_effort.csv"), col_types =
#                          cols(
#                            Survey.Year = col_integer(),
#                            Trip.identifier = col_integer(),
#                            Vessel.name = col_character(),
#                            Trip.start.date = col_character(),
#                            Trip.end.date = col_character(),
#                            GMA = col_character(),
#                            PFMA = col_character(),
#                            Set.number = col_integer(),
#                            Set.date = col_character(),
#                            Start.latitude = col_double(),
#                            Start.longitude = col_double(),
#                            End.latitude = col_double(),
#                            End.longitude = col_double(),
#                            Bottom.depth..m. = col_double(),
#                            Tow.duration..min. = col_integer(),
#                            Distance.towed..m. = col_double(),
#                            Vessel.speed..m.min. = col_double(),
#                            Trawl.door.spread..m. = col_double(),
#                            Trawl.mouth.opening.height..m. = col_double()
#                          )) %>%
#   select(Trip.identifier, Set.number,Survey.Year,Trip.start.date,Trip.end.date, GMA, PFMA,Set.date, Start.latitude,Start.longitude, End.latitude, End.longitude, Bottom.depth..m., Tow.duration..min.,Distance.towed..m., Trawl.door.spread..m., Trawl.mouth.opening.height..m. )
#
# QCS <- left_join(QCS_catch, QCS_effort, by = c("Trip.identifier", "Set.number","Survey.Year"))
#
#
#
# QCS <- QCS %>%
#   # Create a unique haulid
#   mutate(
#     haulid = paste(formatC(Trip.identifier, width=3, flag=0), formatC(Set.number, width=3, flag=0), sep= "-"),
#     # Add "strata" (define by lat, lon and depth bands) where needed # degree bins # 100 m bins # no need to use lon grids on west coast (so narrow)
#     stratum = paste(floor(Start.latitude), floor(Start.longitude),floor(Bottom.depth..m./100)*100, sep= "-"),
#     # catch weight (kg.) per tow
#     wtcpue = (Catch.weight..kg.)#/(Distance.towed..m.*Trawl.door.spread..m.)
#   )
#
#
# # Calculate stratum area where needed (use convex hull approach)
# QCS_strats <- QCS  %>%
#   group_by(stratum) %>%
#   summarise(stratumarea = calcarea(Start.longitude, Start.latitude))
#
# QCS <- left_join(QCS, QCS_strats, by = "stratum")
#
# QCS <- QCS %>%
#   rename(
#     lat = Start.latitude,
#     lon = Start.longitude,
#     depth = Bottom.depth..m.,
#     spp = Scientific.name,
#     year = Survey.Year
#   ) %>%
#   # remove unidentified spp and non-species
#   filter(spp != "" | !is.na(spp),
#          !grepl("EGG", spp),
#          !grepl("UNIDENTIFIED", spp),
#          !grepl("PURSE", spp),
#          !grepl("UNID. FISH", spp),
#          !grepl("UNID FISH AND INVERTEBRATES", spp),
#          !grepl("UNID REMAINS,DIGESTED", spp),
#          !grepl("UNID FISH AND REMAINS", spp),
#          !grepl("CALAPPA MEGALOPS",spp),
#          !grepl("MARINE INVERTEBRATA", spp),
#          !grepl("EMPTY", spp),
#          !grepl("SHELLS", spp),
#          !grepl("RESERVED", spp),
#          !grepl("SAND TUBE", spp),
#          !grepl("SHARK", spp),
#          !grepl("SHRIMP-LIKE", spp),
#          !grepl("UNKNOWN FISH",spp),
#          !grepl("^MUD$", spp),
#          !grepl("WATER", spp),
#          !grepl("DEBRIS", spp),
#          !grepl("FISH REMAINS", spp),
#          !grepl("POLYCHAETE REMAINS", spp)) %>%
#   # adjust spp names
#   mutate(spp = ifelse(grepl("LEPIDOPSETTA", spp), "LEPIDOPSETTA SP.", spp),
#          spp = ifelse(grepl("BATHYRAJA", spp), 'BATHYRAJA SP.', spp),
#          spp = ifelse(grepl("SQUALUS", spp), 'SQUALUS SUCKLEYI', spp)) %>%
#   group_by(haulid, stratum, stratumarea, year, lat, lon, depth, spp) %>%
#   summarise(wtcpue = sumna(wtcpue)) %>%
#   # add region column
#   mutate(region = "Queen Charlotte Sound") %>%
#   select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue) %>%
#   ungroup()
#
#
# # combine the wtcpue for each species by haul
# QCS <- QCS %>%
#   group_by(haulid, stratum, stratumarea, year, lat, lon, depth, spp) %>%
#   summarise(wtcpue = sumna(wtcpue)) %>%
#   ungroup() %>%
#   # remove extra columns
#   select(haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue)
#
# #test = setcolorder(scot, c('region', 'haulid', 'year', 'lat', 'lon', 'stratum', 'stratumarea', 'depth', 'spp', 'wtcpue'))
# test <- QCS %>%
#   filter(stratumarea > 0)
#
#
# #West Coast Vancouver Island
#
# WCV_catch <- read_csv(here::here("data_processing_rcode/data", "WCV_catch.csv"), col_types = cols(
#   Survey.Year = col_integer(),
#   Trip.identifier = col_integer(),
#   Set.number = col_integer(),
#   ITIS.TSN = col_integer(),
#   Species.code = col_character(),
#   Scientific.name = col_character(),
#   English.common.name = col_character(),
#   French.common.name = col_character(),
#   LSID = col_character(),
#   Catch.weight..kg. = col_double(),
#   Catch.count..pieces. = col_integer()
# )) %>%
#   select(Trip.identifier, Set.number,Survey.Year, ITIS.TSN, Species.code, Scientific.name, English.common.name, Catch.weight..kg.)
#
# WCV_effort <- read_csv(here::here("data_processing_rcode/data", "WCV_effort.csv"), col_types =
#                          cols(
#                            Survey.Year = col_integer(),
#                            Trip.identifier = col_integer(),
#                            Vessel.name = col_character(),
#                            Trip.start.date = col_character(),
#                            Trip.end.date = col_character(),
#                            GMA = col_character(),
#                            PFMA = col_character(),
#                            Set.number = col_integer(),
#                            Set.date = col_character(),
#                            Start.latitude = col_double(),
#                            Start.longitude = col_double(),
#                            End.latitude = col_double(),
#                            End.longitude = col_double(),
#                            Bottom.depth..m. = col_double(),
#                            Tow.duration..min. = col_integer(),
#                            Distance.towed..m. = col_double(),
#                            Vessel.speed..m.min. = col_double(),
#                            Trawl.door.spread..m. = col_double(),
#                            Trawl.mouth.opening.height..m. = col_double()
#                          )) %>%
#   select(Trip.identifier, Set.number,Survey.Year,Trip.start.date,Trip.end.date, GMA, PFMA,Set.date, Start.latitude,Start.longitude, End.latitude, End.longitude, Bottom.depth..m., Tow.duration..min.,Distance.towed..m., Trawl.door.spread..m., Trawl.mouth.opening.height..m. )
#
#
# WCV <- left_join(WCV_catch, WCV_effort, by = c("Trip.identifier", "Set.number","Survey.Year"))
#
#
#
# WCV <- WCV %>%
#   # Create a unique haulid
#   mutate(
#     haulid = paste(formatC(Trip.identifier, width=3, flag=0), formatC(Set.number, width=3, flag=0), sep= "-"),
#     # Add "strata" (define by lat, lon and depth bands) where needed # degree bins # 100 m bins # no need to use lon grids on west coast (so narrow)
#     stratum = paste(floor(Start.latitude), floor(Start.longitude),floor(Bottom.depth..m./100)*100, sep= "-"),
#     # catch weight (kg.) per tow
#     wtcpue = (Catch.weight..kg.)#/(Distance.towed..m.*Trawl.door.spread..m.)
#   )
#
# # Calculate stratum area where needed (use convex hull approach)
# WCV_strats <- WCV  %>%
#   group_by(stratum) %>%
#   summarise(stratumarea = calcarea(Start.longitude, Start.latitude))
#
# WCV <- left_join(WCV, WCV_strats, by = "stratum")
#
# WCV <- WCV %>%
#   rename(
#     lat = Start.latitude,
#     lon = Start.longitude,
#     depth = Bottom.depth..m.,
#     spp = Scientific.name,
#     year = Survey.Year
#   ) %>%
#   # remove unidentified spp and non-species
#   filter(spp != "" | !is.na(spp),
#          !grepl("EGG", spp),
#          !grepl("UNIDENTIFIED", spp),
#          !grepl("PURSE", spp),
#          !grepl("UNID. FISH", spp),
#          !grepl("UNID FISH AND INVERTEBRATES", spp),
#          !grepl("UNID REMAINS,DIGESTED", spp),
#          !grepl("UNID FISH AND REMAINS", spp),
#          !grepl("CALAPPA MEGALOPS",spp),
#          !grepl("MARINE INVERTEBRATA (NS)", spp),
#          !grepl("EMPTY", spp),
#          !grepl("SHELLS", spp),
#          !grepl("RESERVED", spp),
#          !grepl("SAND TUBE", spp),
#          !grepl("SHARK (NS)", spp),
#          !grepl("SHRIMP-LIKE", spp),
#          !grepl("UNKNOWN FISH",spp),
#          !grepl("^MUD$", spp),
#          !grepl("WATER", spp),
#          !grepl("DEBRIS", spp),
#          !grepl("FISH REMAINS", spp),
#          !grepl("POLYCHAETE REMAINS", spp)) %>%
#   # adjust spp names
#   mutate(spp = ifelse(grepl("LEPIDOPSETTA", spp), "LEPIDOPSETTA SP.", spp),
#          spp = ifelse(grepl("BATHYRAJA", spp), 'BATHYRAJA SP.', spp),
#          spp = ifelse(grepl("SQUALUS", spp), 'SQUALUS SUCKLEYI', spp)) %>%
#   group_by(haulid, stratum, stratumarea, year, lat, lon, depth, spp) %>%
#   summarise(wtcpue = sumna(wtcpue)) %>%
#   # add region column
#   mutate(region = "West Coast Vancouver Island") %>%
#   select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue) %>%
#   ungroup()
#
#
# # combine the wtcpue for each species by haul
# WCV <- WCV %>%
#   group_by(haulid, stratum, stratumarea, year, lat, lon, depth, spp) %>%
#   summarise(wtcpue = sumna(wtcpue)) %>%
#   ungroup() %>%
#   # remove extra columns
#   select(haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue)
#
# #test = setcolorder(scot, c('region', 'haulid', 'year', 'lat', 'lon', 'stratum', 'stratumarea', 'depth', 'spp', 'wtcpue'))
# test <- WCV %>%
#   filter(stratumarea > 0)
#
#
# #West Coast Haida Guai
#
# WCHG_catch <- read_csv(here::here("data_processing_rcode/data", "WCHG_catch.csv"), col_types = cols(
#   Survey.Year = col_integer(),
#   Trip.identifier = col_integer(),
#   Set.number = col_integer(),
#   ITIS.TSN = col_integer(),
#   Species.code = col_character(),
#   Scientific.name = col_character(),
#   English.common.name = col_character(),
#   French.common.name = col_character(),
#   LSID = col_character(),
#   Catch.weight..kg. = col_double(),
#   Catch.count..pieces. = col_integer()
# )) %>%
#   select(Trip.identifier, Set.number,Survey.Year, ITIS.TSN, Species.code, Scientific.name, English.common.name, Catch.weight..kg.)
#
# WCHG_effort <- read_csv(here::here("data_processing_rcode/data", "WCHG_effort.csv"), col_types =
#                           cols(
#                             Survey.Year = col_integer(),
#                             Trip.identifier = col_integer(),
#                             Vessel.name = col_character(),
#                             Trip.start.date = col_character(),
#                             Trip.end.date = col_character(),
#                             GMA = col_character(),
#                             PFMA = col_character(),
#                             Set.number = col_integer(),
#                             Set.date = col_character(),
#                             Start.latitude = col_double(),
#                             Start.longitude = col_double(),
#                             End.latitude = col_double(),
#                             End.longitude = col_double(),
#                             Bottom.depth..m. = col_double(),
#                             Tow.duration..min. = col_integer(),
#                             Distance.towed..m. = col_double(),
#                             Vessel.speed..m.min. = col_double(),
#                             Trawl.door.spread..m. = col_double(),
#                             Trawl.mouth.opening.height..m. = col_double()
#                           )) %>%
#   select(Trip.identifier, Set.number,Survey.Year,Trip.start.date,Trip.end.date, GMA, PFMA,Set.date, Start.latitude,Start.longitude, End.latitude, End.longitude, Bottom.depth..m., Tow.duration..min.,Distance.towed..m., Trawl.door.spread..m., Trawl.mouth.opening.height..m. )
#
#
# WCHG <- left_join(WCHG_catch, WCHG_effort, by = c("Trip.identifier", "Set.number","Survey.Year"))
#
#
#
# WCHG <- WCHG %>%
#   # Create a unique haulid
#   mutate(
#     haulid = paste(formatC(Trip.identifier, width=3, flag=0), formatC(Set.number, width=3, flag=0), sep= "-"),
#     # Add "strata" (define by lat, lon and depth bands) where needed # degree bins # 100 m bins # no need to use lon grids on west coast (so narrow)
#     stratum = paste(floor(Start.latitude), floor(Start.longitude),floor(Bottom.depth..m./100)*100, sep= "-"),
#     # catch weight (kg.) per tow
#     wtcpue = (Catch.weight..kg.)#/(Distance.towed..m.*Trawl.door.spread..m.)
#   )
#
# # Calculate stratum area where needed (use convex hull approach)
# WCHG_strats <- WCHG  %>%
#   group_by(stratum) %>%
#   summarise(stratumarea = calcarea(Start.longitude, Start.latitude))
#
# WCHG <- left_join(WCHG, WCHG_strats, by = "stratum")
#
# WCHG <- WCHG %>%
#   rename(
#     lat = Start.latitude,
#     lon = Start.longitude,
#     depth = Bottom.depth..m.,
#     spp = Scientific.name,
#     year = Survey.Year
#   ) %>%
#   # remove unidentified spp and non-species
#   filter(spp != "" | !is.na(spp),
#          !grepl("EGG", spp),
#          !grepl("UNIDENTIFIED", spp),
#          !grepl("PURSE", spp),
#          !grepl("UNID. FISH", spp),
#          !grepl("UNID FISH AND INVERTEBRATES", spp),
#          !grepl("UNID REMAINS,DIGESTED", spp),
#          !grepl("UNID FISH AND REMAINS", spp),
#          !grepl("CALAPPA MEGALOPS",spp),
#          !grepl("MARINE INVERTEBRATA (NS)", spp),
#          !grepl("EMPTY", spp),
#          !grepl("SHELLS", spp),
#          !grepl("RESERVED", spp),
#          !grepl("SAND TUBE", spp),
#          !grepl("SHARK (NS)", spp),
#          !grepl("SHRIMP-LIKE", spp),
#          !grepl("UNKNOWN FISH",spp),
#          !grepl("^MUD$", spp),
#          !grepl("WATER", spp),
#          !grepl("DEBRIS", spp),
#          !grepl("FISH REMAINS", spp),
#          !grepl("POLYCHAETE REMAINS", spp)) %>%
#   # adjust spp names
#   mutate(spp = ifelse(grepl("LEPIDOPSETTA", spp), "LEPIDOPSETTA SP.", spp),
#          spp = ifelse(grepl("BATHYRAJA", spp), 'BATHYRAJA SP.', spp),
#          spp = ifelse(grepl("SQUALUS", spp), 'SQUALUS SUCKLEYI', spp)) %>%
#   group_by(haulid, stratum, stratumarea, year, lat, lon, depth, spp) %>%
#   summarise(wtcpue = sumna(wtcpue)) %>%
#   # add region column
#   mutate(region = "West Coast Vancouver Island") %>%
#   select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue) %>%
#   ungroup()
#
# # combine the wtcpue for each species by haul
# WCHG <- WCHG %>%
#   group_by(haulid, stratum, stratumarea, year, lat, lon, depth, spp) %>%
#   summarise(wtcpue = sumna(wtcpue)) %>%
#   ungroup() %>%
#   # remove extra columns
#   select(haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue)
#
#
# #Hecate Strait
#
# HS_catch <- read_csv(here::here("data_processing_rcode/data", "HS_catch.csv"), col_types = cols(
#   Survey.Year = col_integer(),
#   Trip.identifier = col_integer(),
#   Set.number = col_integer(),
#   ITIS.TSN = col_integer(),
#   Species.code = col_character(),
#   Scientific.name = col_character(),
#   English.common.name = col_character(),
#   French.common.name = col_character(),
#   LSID = col_character(),
#   Catch.weight..kg. = col_double(),
#   Catch.count..pieces. = col_integer()
# )) %>%
#   select(Trip.identifier, Set.number,Survey.Year, ITIS.TSN, Species.code, Scientific.name, English.common.name, Catch.weight..kg.)
#
# HS_effort <- read_csv(here::here("data_processing_rcode/data", "HS_effort.csv"), col_types =
#                         cols(
#                           Survey.Year = col_integer(),
#                           Trip.identifier = col_integer(),
#                           Vessel.name = col_character(),
#                           Trip.start.date = col_character(),
#                           Trip.end.date = col_character(),
#                           GMA = col_character(),
#                           PFMA = col_character(),
#                           Set.number = col_integer(),
#                           Set.date = col_character(),
#                           Start.latitude = col_double(),
#                           Start.longitude = col_double(),
#                           End.latitude = col_double(),
#                           End.longitude = col_double(),
#                           Bottom.depth..m. = col_double(),
#                           Tow.duration..min. = col_integer(),
#                           Distance.towed..m. = col_double(),
#                           Vessel.speed..m.min. = col_double(),
#                           Trawl.door.spread..m. = col_double(),
#                           Trawl.mouth.opening.height..m. = col_double()
#                         )) %>%
#   select(Trip.identifier, Set.number,Survey.Year,Trip.start.date,Trip.end.date, GMA, PFMA,Set.date, Start.latitude,Start.longitude, End.latitude, End.longitude, Bottom.depth..m., Tow.duration..min.,Distance.towed..m., Trawl.door.spread..m., Trawl.mouth.opening.height..m. )
#
#
# HS <- left_join(HS_catch, HS_effort, by = c("Trip.identifier", "Set.number","Survey.Year"))
#
# HS <- HS %>%
#   # Create a unique haulid
#   mutate(
#     haulid = paste(formatC(Trip.identifier, width=3, flag=0), formatC(Set.number, width=3, flag=0), sep= "-"),
#     # Add "strata" (define by lat, lon and depth bands) where needed # degree bins # 100 m bins # no need to use lon grids on west coast (so narrow)
#     stratum = paste(floor(Start.latitude), floor(Start.longitude),floor(Bottom.depth..m./100)*100, sep= "-"),
#     # catch weight (kg.) per tow
#     wtcpue = (Catch.weight..kg.)#/(Distance.towed..m.*Trawl.door.spread..m.)
#   )
#
# # Calculate stratum area where needed (use convex hull approach)
# HS_strats <- HS  %>%
#   group_by(stratum) %>%
#   summarise(stratumarea = calcarea(Start.longitude,Start.latitude))
#
# HS <- left_join(HS, HS_strats, by = "stratum")
#
# HS <- HS %>%
#   rename(
#     lat = Start.latitude,
#     lon = Start.longitude,
#     depth = Bottom.depth..m.,
#     spp = Scientific.name,
#     year = Survey.Year
#   ) %>%
#   # remove unidentified spp and non-species
#   filter(spp != "" | !is.na(spp),
#          !grepl("EGG", spp),
#          !grepl("UNIDENTIFIED", spp),
#          !grepl("PURSE", spp),
#          !grepl("UNID. FISH", spp),
#          !grepl("UNID FISH AND INVERTEBRATES", spp),
#          !grepl("UNID REMAINS,DIGESTED", spp),
#          !grepl("UNID FISH AND REMAINS", spp),
#          !grepl("CALAPPA MEGALOPS",spp),
#          !grepl("MARINE INVERTEBRATA (NS)", spp),
#          !grepl("EMPTY", spp),
#          !grepl("SHELLS", spp),
#          !grepl("RESERVED", spp),
#          !grepl("SAND TUBE", spp),
#          !grepl("SHARK (NS)", spp),
#          !grepl("SHRIMP-LIKE", spp),
#          !grepl("UNKNOWN FISH",spp),
#          !grepl("^MUD$", spp),
#          !grepl("WATER", spp),
#          !grepl("DEBRIS", spp),
#          !grepl("FISH REMAINS", spp),
#          !grepl("POLYCHAETE REMAINS", spp)) %>%
#   # adjust spp names
#   mutate(spp = ifelse(grepl("LEPIDOPSETTA", spp), "LEPIDOPSETTA SP.", spp),
#          spp = ifelse(grepl("BATHYRAJA", spp), 'BATHYRAJA SP.', spp),
#          spp = ifelse(grepl("SQUALUS", spp), 'SQUALUS SUCKLEYI', spp)) %>%
#   group_by(haulid, stratum, stratumarea, year, lat, lon, depth, spp) %>%
#   summarise(wtcpue = sumna(wtcpue)) %>%
#   # add region column
#   mutate(region = "Hecate Strait") %>%
#   select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue) %>%
#   ungroup()
#
#
# # combine the wtcpue for each species by haul
# HS <- HS %>%
#   group_by(haulid, stratum, stratumarea, year, lat, lon, depth, spp) %>%
#   summarise(wtcpue = sumna(wtcpue)) %>%
#   ungroup() %>%
#   # remove extra columns
#   select(haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue)
#
#
# #Strait of Georgia
#
# SOG_catch <- read_csv(here::here("data_processing_rcode/data", "SOG_catch.csv"), col_types = cols(
#   Survey.Year = col_integer(),
#   Trip.identifier = col_integer(),
#   Set.number = col_integer(),
#   ITIS.TSN = col_integer(),
#   Species.code = col_character(),
#   Scientific.name = col_character(),
#   English.common.name = col_character(),
#   French.common.name = col_character(),
#   LSID = col_character(),
#   Catch.weight..kg. = col_double(),
#   Catch.count..pieces. = col_integer()
# )) %>%
#   select(Trip.identifier, Set.number,Survey.Year, ITIS.TSN, Species.code, Scientific.name, English.common.name, Catch.weight..kg.)
#
# SOG_effort <- read_csv(here::here("data_processing_rcode/data", "SOG_effort.csv"), col_types =
#                          cols(
#                            Survey.Year = col_integer(),
#                            Trip.identifier = col_integer(),
#                            Vessel.name = col_character(),
#                            Trip.start.date = col_character(),
#                            Trip.end.date = col_character(),
#                            GMA = col_character(),
#                            PFMA = col_character(),
#                            Set.number = col_integer(),
#                            Set.date = col_character(),
#                            Start.latitude = col_double(),
#                            Start.longitude = col_double(),
#                            End.latitude = col_double(),
#                            End.longitude = col_double(),
#                            Bottom.depth..m. = col_double(),
#                            Tow.duration..min. = col_integer(),
#                            Distance.towed..m. = col_double(),
#                            Vessel.speed..m.min. = col_double(),
#                            Trawl.door.spread..m. = col_double(),
#                            Trawl.mouth.opening.height..m. = col_double()
#                          )) %>%
#   select(Trip.identifier, Set.number,Survey.Year,Trip.start.date,Trip.end.date, GMA, PFMA,Set.date, Start.latitude,Start.longitude, End.latitude, End.longitude, Bottom.depth..m., Tow.duration..min.,Distance.towed..m., Trawl.door.spread..m., Trawl.mouth.opening.height..m. )
#
#
# SOG <- left_join(SOG_catch, SOG_effort, by = c("Trip.identifier", "Set.number","Survey.Year"))
#
#
#
# SOG <- SOG %>%
#   # Create a unique haulid
#   mutate(
#     haulid = paste(formatC(Trip.identifier, width=3, flag=0), formatC(Set.number, width=3, flag=0), sep= "-"),
#     # Add "strata" (define by lat, lon and depth bands) where needed # degree bins # 100 m bins # no need to use lon grids on west coast (so narrow)
#     stratum = paste(floor(Start.latitude), floor(Start.longitude),floor(Bottom.depth..m./100)*100, sep= "-"),
#     # catch weight (kg.) per tow
#     wtcpue = (Catch.weight..kg.)#/(Distance.towed..m.*Trawl.door.spread..m.)
#   )
#
# # Calculate stratum area where needed (use convex hull approach)
# SOG_strats <- SOG  %>%
#   group_by(stratum) %>%
#   summarise(stratumarea = calcarea(Start.longitude, Start.latitude))
#
# SOG <- left_join(SOG, SOG_strats, by = "stratum")
#
# SOG <- SOG %>%
#   rename(
#     lat = Start.latitude,
#     lon = Start.longitude,
#     depth = Bottom.depth..m.,
#     spp = Scientific.name,
#     year = Survey.Year
#   ) %>%
#   # remove unidentified spp and non-species
#   filter(spp != "" | !is.na(spp),
#          !grepl("EGG", spp),
#          !grepl("UNIDENTIFIED", spp),
#          !grepl("PURSE", spp),
#          !grepl("UNID. FISH", spp),
#          !grepl("UNID FISH AND INVERTEBRATES", spp),
#          !grepl("UNID REMAINS,DIGESTED", spp),
#          !grepl("UNID FISH AND REMAINS", spp),
#          !grepl("CALAPPA MEGALOPS",spp),
#          !grepl("MARINE INVERTEBRATA (NS)", spp),
#          !grepl("EMPTY", spp),
#          !grepl("SHELLS", spp),
#          !grepl("RESERVED", spp),
#          !grepl("SAND TUBE", spp),
#          !grepl("SHARK (NS)", spp),
#          !grepl("SHRIMP-LIKE", spp),
#          !grepl("UNKNOWN FISH",spp),
#          !grepl("^MUD$", spp),
#          !grepl("WATER", spp),
#          !grepl("DEBRIS", spp),
#          !grepl("FISH REMAINS", spp),
#          !grepl("POLYCHAETE REMAINS", spp)) %>%
#   # adjust spp names
#   mutate(spp = ifelse(grepl("LEPIDOPSETTA", spp), "LEPIDOPSETTA SP.", spp),
#          spp = ifelse(grepl("BATHYRAJA", spp), 'BATHYRAJA SP.', spp),
#          spp = ifelse(grepl("SQUALUS", spp), 'SQUALUS SUCKLEYI', spp)) %>%
#   group_by(haulid, stratum, stratumarea, year, lat, lon, depth, spp) %>%
#   summarise(wtcpue = sumna(wtcpue)) %>%
#   # add region column
#   mutate(region = "Strait of Georgia") %>%
#   select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue) %>%
#   ungroup()
#
#
# # combine the wtcpue for each species by haul
# SOG <- SOG %>%
#   group_by(haulid, stratum, stratumarea, year, lat, lon, depth, spp) %>%
#   summarise(wtcpue = sumna(wtcpue)) %>%
#   ungroup() %>%
#   # remove extra columns
#   select(haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue)
#
#
# #combine canadian pacific
# CPAC <- rbind(QCS, WCV, WCHG, HS, SOG)
#
# #test = setcolorder(scot, c('region', 'haulid', 'year', 'lat', 'lon', 'stratum', 'stratumarea', 'depth', 'spp', 'wtcpue'))
# test <- CPAC %>%
#   filter(stratumarea > 0)
#
# #CPAC$year <- as.integer(CPAC$year)
#
#
# # how many rows will be lost if only stratum trawled ever year are kept?
# test2 <- CPAC %>%
#   filter(stratum %in% test$stratum)
# nrow(CPAC) - nrow(test2)
# # percent that will be lost
# print((nrow(CPAC) - nrow(test2))/nrow(CPAC))
# # 0.9% of rows are removed
# test2 <- CPAC %>%
#   filter(stratum %in% test$stratum)
#
#
# CPAC$region <- 'Canadian Pacific'
#
# CPAC <- CPAC %>%
#   select(region, everything())
#
# CPAC$spp <- firstup(CPAC$spp)
#
#
# if (HQ_DATA_ONLY == TRUE){
#   # look at the graph and make sure decisions to keep or eliminate data make sense
#
#   # plot the strata by year
#   p1 <- CPAC %>%
#     select(stratum, year) %>%
#     ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
#     geom_jitter()
#   p2 <- CPAC %>%
#     select(lat, lon) %>%
#     ggplot(aes(x = lon, y = lat)) +
#     geom_jitter()
#
#   CPAC_fltr <- CPAC
#
#   # regroup year bins
#   # update this when adding a new year!
#   # The following line will place data into two year bins
#   # bin names (e.g., 2015) refer to the stated year and the one following (e.g., 2015 = 2015-2016)
#   # This maintains year as a numeric variable and facilitates all other analyses
#   CPAC_fltr$year <- oddtoeven(CPAC_fltr$year)-1
#
#   # Old code to create character bin names
#   # CPAC_fltr$year[CPAC_fltr$year=='2020'] <- '2019'
#   # CPAC_fltr$year[CPAC_fltr$year=='2018'] <- '2017-2018'
#   # CPAC_fltr$year[CPAC_fltr$year=='2016'] <- '2015-2016'
#   # CPAC_fltr$year[CPAC_fltr$year=='2014'] <- '2013-2014'
#   # CPAC_fltryear[CPAC_fltr$year=='2012'] <- '2011-2012'
#   # CPAC_fltr$year[CPAC_fltr$year=='2010'] <- '2009-2010'
#   # CPAC_fltr$year[CPAC_fltr$year=='2008'] <- '2007-2008'
#   # CPAC_fltr$year[CPAC_fltr$year=='2006'] <- '2005-2006'
#   # CPAC_fltr$year[CPAC_fltr$year=='2004'] <- '2003-2004'
#
#   # find strata sampled every year
#   annual_strata <- CPAC_fltr %>%
#     select(stratum, year) %>%
#     distinct() %>%
#     group_by(stratum) %>%
#     summarise(count = n()) %>%
#     filter(count >= 3)
#
#   # find strata sampled every year
#   annual_strata_old <- CPAC %>%
#     #filter(year != 1986, year != 1978) %>%
#     select(stratum, year) %>%
#     distinct() %>%
#     group_by(stratum) %>%
#     summarise(count = n())
#
#
#   # how many rows will be lost if only stratum trawled ever year are kept?
#   test <- CPAC_fltr %>%
#     #filter(year != 1986, year != 1978, year!= 2018) %>%
#     filter(stratum %in% annual_strata$stratum)
#   nrow(CPAC) - nrow(test)
#   # percent that will be lost
#   print((nrow(CPAC) - nrow(test))/nrow(CPAC))
#   # 3.03% are removed
#
#   #how much additional data will be lost if we remove years 2003-2004?
#   test <- CPAC_fltr%>%
#     filter(year != 2003,year != 2019 ) %>%
#     filter(stratum %in% annual_strata$stratum)
#   nrow(CPAC) - nrow(test)
#   # percent that will be lost
#   print((nrow(CPAC) - nrow(test))/nrow(CPAC))
#   # 18.3% are removed
#
#   CPAC_fltr <- CPAC_fltr  %>%
#     filter(year != 2003,year != 2019 )  %>%
#     filter(stratum %in% test$stratum)
#
#   p3 <- CPAC_fltr %>%
#     select(stratum, year) %>%
#     ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
#     geom_jitter()
#
#   p4 <- CPAC_fltr %>%
#     select(lat, lon) %>%
#     ggplot(aes(x = lon, y = lat)) +
#     geom_jitter()
#
#   if (HQ_PLOTS == TRUE){
#     temp <- grid.arrange(p1, p2,p3,p4, nrow = 2)
#     ggsave(plot = temp, filename = here::here("data_processing_rcode/output/plots", "cpac_hq_dat_removed.png"))
#   }
# }
#
#
# rm(SOG, SOG_catch, SOG_effort, SOG_strats, QCS, QCS_catch, QCS_effort, QCS_strats,
#    HS, HS_catch, HS_effort, HS_strats, WCHG, WCHG_catch, WCHG_effort, WCHG_strats,
#    WCV, WCV_catch, WCV_effort, WCV_strats)
#
# # Compile Canadian Gulf of Saint Lawrence South ---------------------------------------------------
# print("Compile GSL South")
#
# #GSL South
#
# GSLsouth <- read_csv(here::here("data_processing_rcode/data", "GSLsouth.csv"))
#
# GSLsouth$haulid <- paste(GSLsouth$year,GSLsouth$month,GSLsouth$day,GSLsouth$start.hour,GSLsouth$start.minute, sep="-")
#
# GSLsouth <- GSLsouth %>%
#   # Create a unique haulid
#   mutate(
#     # Add "strata" (define by lat, lon and depth bands) where needed # degree bins # 100 m bins # no need to use lon grids on west coast (so narrow)
#     stratum = paste(floor(latitude), floor(longitude), sep= "-"),
#     # distance, 1.75 nau mi. (via Daniel Ricard) = 3241 m., trawl door width, 12.497 m. Hurlbut and Clay (1990)
#     # catch weight (kg.) per tow
#     wtcpue = (weight.caught)#/(3241*12.497)
#   )
#
# # Calculate stratum area where needed (use convex hull approach)
# GSLsouth_strats <- GSLsouth  %>%
#   group_by(stratum) %>%
#   summarise(stratumarea = calcarea(longitude, latitude))
#
# GSLsouth <- left_join(GSLsouth, GSLsouth_strats, by = "stratum")
#
# #No depth data available - fill with NA
# GSLsouth$depth <- NA
# #GSLsouth$latin.name <- firstup(GSLsouth$latin.name)
# GSLsouth <- GSLsouth %>%
#   mutate(spp = latin.name,
#          lat = latitude,
#          lon = longitude) %>%
#   # remove unidentified spp and non-species
#   filter(spp != "" | !is.na(spp),
#          !grepl("EGG", spp),
#          !grepl("UNIDENTIFIED", spp),
#          !grepl("PURSE", spp),
#          !grepl("UNID. FISH", spp),
#          !grepl("UNID FISH AND INVERTEBRATES", spp),
#          !grepl("UNID REMAINS,DIGESTED", spp),
#          !grepl("UNID FISH AND REMAINS", spp),
#          !grepl("CALAPPA MEGALOPS",spp),
#          !grepl("MARINE INVERTEBRATA", spp),
#          !grepl("EMPTY", spp),
#          !grepl("SHELLS", spp),
#          !grepl("RESERVED", spp),
#          !grepl("SAND TUBE", spp),
#          !grepl("SHARK (NS)", spp),
#          !grepl("SHRIMP-LIKE", spp),
#          !grepl("UNKNOWN FISH",spp),
#          !grepl("^MUD$", spp),
#          !grepl("WATER", spp),
#          !grepl("DEBRIS", spp),
#          !grepl("FISH REMAINS", spp),
#          !grepl("POLYCHAETE REMAINS", spp),
#          !grepl("CRUSTACEA LARVAE", spp),
#          !grepl("FOREIGN ARTICLES,GARBAGE", spp),
#          !grepl("NO LONGER USED - PHAKELLIA SPP.", spp),
#          !grepl("PARASITES,ROUND WORMS", spp),
#          !grepl("POLYCHAETA C.,LARGE", spp),
#          !grepl("POLYCHAETA C.,SMALL", spp),
#          !grepl("SEA CORALS", spp),
#          !grepl("STONES AND ROCKS", spp),
#          !grepl("CRAB", spp),
#          !grepl("FISH LARVAE, UNID", spp)) %>%
#   group_by(haulid, stratum, stratumarea, year, lat, lon, depth, spp) %>%
#   summarise(wtcpue = sumna(wtcpue)) %>%
#   # add region column
#   mutate(region = "Gulf of St. Lawrence South") %>%
#   select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue) %>%
#   ungroup()
#
#
# if (HQ_DATA_ONLY == TRUE){
#   # look at the graph and make sure decisions to keep or eliminate data make sense
#
#   # plot the strata by year
#   p1 <- GSLsouth %>%
#     select(stratum, year) %>%
#     ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
#     geom_jitter()
#   p2 <- GSLsouth %>%
#     select(lat, lon) %>%
#     ggplot(aes(x = lon, y = lat)) +
#     geom_jitter()
#
#
#   # how many rows will be lost if only stratum trawled ever year are kept?
#   test <- GSLsouth %>%
#     select(stratum, year) %>%
#     distinct() %>%
#     group_by(stratum) %>%
#     summarise(count = n()) %>%
#     filter(count >= 29)
#
#   # how many rows will be lost if only stratum trawled ever year are kept?
#   test2 <- GSLsouth %>%
#     filter(stratum %in% test$stratum)
#   nrow(GSLsouth) - nrow(test2)
#   # percent that will be lost
#   print((nrow(GSLsouth) - nrow(test2))/nrow(GSLsouth))
#   # 1.2% of rows are removed
#
#   # how many rows will be lost if only stratum trawled ever year are kept?
#   # and remove first year with very low coverage
#   test <- GSLsouth %>%
#     filter(year != 1970) %>%
#     select(stratum, year) %>%
#     distinct() %>%
#     group_by(stratum) %>%
#     summarise(count = n()) %>%
#     filter(count > 37)
#
#   # how many rows will be lost if only stratum trawled ever year are kept?
#   test2 <- GSLsouth %>%
#     filter(stratum %in% test$stratum)
#   nrow(GSLsouth) - nrow(test2)
#   # percent that will be lost
#   print((nrow(GSLsouth) - nrow(test2))/nrow(GSLsouth))
#   # 5.6% of rows removed
#
#
#   test3 <- GSLsouth %>%
#     filter(year >= 1985)
#   #filter(year != 1984,year != 1983,year != 1982,year != 1981,year != 1980,year != 1979)
#
#   # how many rows will be lost if only years with all strata are kept?
#   test4 <- GSLsouth %>%
#     filter(year %in% test3$year)
#   nrow(GSLsouth) - nrow(test4)
#   # percent that will be lost
#   print((nrow(GSLsouth) - nrow(test4))/nrow(GSLsouth))
#   # 5.3% of rows are removed
#
#   #how many rows will be lost if both years with low coverage and strata with low coverage are dropped?
#   test5 <- GSLsouth %>%
#     filter(year >= 1985) %>%
#     select(stratum, year) %>%
#     distinct() %>%
#     group_by(stratum) %>%
#     summarise(count = n()) %>%
#     filter(count >= 28)
#
#   test6 <- GSLsouth %>%
#     filter(stratum %in% test5$stratum) %>%
#     filter(year >= 1985)
#
#   nrow(GSLsouth) - nrow(test6)
#   # percent that will be lost
#   print((nrow(GSLsouth) - nrow(test6))/nrow(GSLsouth))
#   # 7.4% of rows are removed
#
#
#
#   # GSLsouth <- GSLsouth  %>%
#   #   #filter(year != 1986, year != 1978, year != 2018) %>%
#   #   filter(stratum %in% test$stratum) %>%
#   #   filter(year >= 1985)
#
#   #Filter spatially and first year with very low coverage
#   GSLsouth_fltr <- GSLsouth %>%
#     filter(year != 1970) %>%
#     filter(stratum %in% test$stratum)
#
#   p3 <- GSLsouth_fltr %>%
#     select(stratum, year) %>%
#     ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
#     geom_jitter()
#
#   p4 <- GSLsouth_fltr %>%
#     select(lat, lon) %>%
#     ggplot(aes(x = lon, y = lat)) +
#     geom_jitter()
#
#   if (HQ_PLOTS == TRUE){
#     temp <- grid.arrange(p1, p2,p3,p4, nrow = 2)
#     ggsave(plot = temp, filename = here::here("data_processing_rcode/output/plots", "GSLsouth_hq_dat_removed.png"))
#   }
# }
#
#
# rm(GSLsouth_strats)
#
# # Compile Canadian Gulf of Saint Lawrence North ---------------------------------------------------
# print("Compile GSL North")
#
# #GSL North Sentinel
#
# GSLnor_sent <- read.csv(here::here("data_processing_rcode/data", "GSLnorth_sentinel.csv"))
#
# #GSL North Gadus
#
# GSLnor_gad <- read.csv(here::here("data_processing_rcode/data", "GSLnorth_gadus.csv"))
#
# #GSL North Hammond
#
# GSLnor_ham <- read.csv(here::here("data_processing_rcode/data", "GSLnorth_hammond.csv"))
#
# #GSL North Needler
#
# GSLnor_need <- read.csv(here::here("data_processing_rcode/data", "GSLnorth_needler.csv"))
#
# #GSL North Teleost
#
# GSLnor_tel <- read.csv(here::here("data_processing_rcode/data", "GSLnorth_teleost.csv"))
#
# #Bind all datasets
#
# GSLnor <- plyr::rbind.fill(GSLnor_sent, GSLnor_gad, GSLnor_ham, GSLnor_need, GSLnor_tel)
# GSLnor$lat <-as.numeric(as.character(GSLnor$Latit_Deb))
# GSLnor$lon <-as.numeric(as.character(GSLnor$Longit_Deb))
# GSLnor$depth <-as.numeric(as.character(GSLnor$Prof_Max))
# GSLnor$Dist_Towed <-as.numeric(GSLnor$Dist_Chalute_Position)
# GSLnor$Pds_Capture <- as.double(GSLnor$Pds_Capture)
# GSLnor$Date <-as.Date(GSLnor$Date_Deb_Trait)
# GSLnor$year <- as.integer(year(GSLnor$Date))
# GSLnor$spp <- trimws(as.character(GSLnor$Nom_Scient_Esp), which = "right")
#
#
# #GSLnor$haulid <- paste(GSLnor$No_Releve,GSLnor$Trait,GSLnor$Date_Deb_Trait,GSLnor$Hre_Deb, sep="-")
#
# GSLnor <- GSLnor[!is.na(GSLnor$lat),]
# GSLnor <- GSLnor[!is.na(GSLnor$depth),]
#
# GSLnor <- GSLnor %>%
#   # Create a unique haulid
#   mutate(
#     haulid = paste(GSLnor$No_Releve,GSLnor$Trait,GSLnor$Date_Deb_Trait,GSLnor$Hre_Deb, sep="-"),
#     # Add "strata" (define by lat, lon and depth bands) where needed # degree bins # 100 m bins # no need to use lon grids on west coast (so narrow)
#     #stratum = paste(floor(lat), floor(lon),floor(depth)*100, sep= "-"),
#     stratum = paste(floor(lat), floor(lon),plyr::round_any(GSLnor$depth, 100), sep= "-"),
#     #weight of catch (kg.) per tow
#     wtcpue = (Pds_Capture)#/(Dist_Towed *12.497)
#   )
#
#
# # Calculate stratum area where needed (use convex hull approach)
# GSLnor_strats <- GSLnor  %>%
#   group_by(stratum) %>%
#   summarise(stratumarea = calcarea(lon,lat)) %>%
#   ungroup()
#
#
# GSLnor <- left_join(GSLnor, GSLnor_strats, by = "stratum")
#
# GSLnor <- GSLnor %>%
#   # remove unidentified spp and non-species
#   filter(spp != "" | !is.na(spp),
#          !grepl("EGG", spp),
#          !grepl("UNIDENTIFIED", spp),
#          !grepl("PURSE", spp),
#          !grepl("UNID. FISH", spp),
#          !grepl("UNID FISH AND INVERTEBRATES", spp),
#          !grepl("UNID REMAINS,DIGESTED", spp),
#          !grepl("UNID FISH AND REMAINS", spp),
#          !grepl("CALAPPA MEGALOPS",spp),
#          !grepl("MARINE INVERTEBRATA (NS)", spp),
#          !grepl("EMPTY", spp),
#          !grepl("SHELLS", spp),
#          !grepl("RESERVED", spp),
#          !grepl("SAND TUBE", spp),
#          !grepl("SHARK (NS)", spp),
#          !grepl("SHRIMP-LIKE", spp),
#          !grepl("UNKNOWN FISH",spp),
#          !grepl("^MUD$", spp),
#          !grepl("WATER", spp),
#          !grepl("INORGANIC DEBRIS", spp),
#          !grepl("FISH REMAINS", spp),
#          !grepl("POLYCHAETA REMAINS", spp)) %>%
#   group_by(haulid, stratum, stratumarea, year, lat, lon, depth, spp) %>%
#   summarise(wtcpue = sumna(wtcpue)) %>%
#   # add region column
#   mutate(region = "Gulf of St. Lawrence North") %>%
#   select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue) %>%
#   ungroup()
#
# if (HQ_DATA_ONLY == TRUE){
#   # look at the graph and make sure decisions to keep or eliminate data make sense
#
#   # plot the strata by year
#   p1 <- GSLnor %>%
#     select(stratum, year) %>%
#     ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
#     geom_jitter()
#   p2 <- GSLnor %>%
#     select(lon, lat) %>%
#     ggplot(aes(x = lon, y = lat)) +
#     geom_jitter()
#
#   test <- GSLnor %>%
#     filter(year != 1979, year != 1980,year != 1981) %>%
#     select(stratum, year) %>%
#     distinct() %>%
#     group_by(stratum) %>%
#     summarise(count = n())  %>%
#     filter(count >= 29)
#
#   # how many rows will be lost if only stratum trawled ever year are kept?
#   test2 <- GSLnor %>%
#     filter(stratum %in% test$stratum)
#   nrow(GSLnor) - nrow(test2)
#   # percent that will be lost
#   print ((nrow(GSLnor) - nrow(test2))/nrow(GSLnor))
#   # 10.5% of rows are removed
#
#   # find strata sampled every year
#   annual_strata <- GSLnor %>%
#     filter(year != 1979, year != 1980,year != 1981) %>%
#     select(stratum, year) %>%
#     distinct() %>%
#     group_by(stratum) %>%
#     summarise(count = n()) %>%
#     filter(count >= 29)
#
#   # find strata sampled every year
#   annual_strata_old <- GSLnor %>%
#     select(stratum, year) %>%
#     distinct() %>%
#     group_by(stratum) %>%
#     summarise(count = n())
#
#   sum(length(unique(annual_strata_old$count)) - length(unique(annual_strata$count)))
#   # how many rows will be lost if only stratum trawled ever year are kept?
#   # test <- GSLnor %>%
#   #   filter(year != 1979, year != 1980,year != 1981) %>%
#   #   select(stratum, year) %>%
#   #   distinct() %>%
#   #   group_by(stratum) %>%
#   #   summarise(count = n()) #%>%
#   #   #filter(count <=34)
#   #
#   # nrow(GSLnor) - nrow(test)
#   # # percent that will be lost
#   # print((nrow(GSLnor) - nrow(test))/nrow(GSLnor))
#   # # 5.6% are removed
#   # #
#
#   GSLnor_fltr <- GSLnor  %>%
#     filter(year != 1979, year != 1980,year != 1981) %>%
#     filter(stratum %in% annual_strata$stratum)
#
#   p3 <- GSLnor_fltr %>%
#     select(stratum, year) %>%
#     ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
#     geom_jitter()
#
#   p4 <- GSLnor_fltr %>%
#     select(lon, lat) %>%
#     ggplot(aes(x = lon, y = lat)) +
#     geom_jitter()
#
#   if (HQ_PLOTS == TRUE){
#     temp <- grid.arrange(p1, p2,p3,p4, nrow = 2)
#     ggsave(plot = temp, filename = here::here("data_processing_rcode/output/plots", "GSLnorth_hq_dat_removed.png"))
#   }
# }
#
# rm(GSLnor_gad, GSLnor_ham, GSLnor_need, GSLnor_sent, GSLnor_tel, GSLnor_strats)




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


tax<- tax  %>%
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
dat <- rbind(ai, ebs, gmex, goa, nbs, neus_fall, neus_spring, seusFALL, seusSPRING, seusSUMMER, wcann, wctri) %>%
  # Remove NA values in wtcpue
  filter(!is.na(wtcpue)) %>%
  # remove any extra white space from around spp and common names
  mutate(spp= str_squish(spp))

#convert all taxa names to first word capitalzied and rest lowercase...
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
not_in_tax<- not_in_tax %>% group_by(spp) %>%
  summarise_all(funs(toString(unique(na.omit(.)))))

#========================== end species name check ===========

# add a case sensitive spp and common name
dat <- left_join(dat, tax, by = c("spp" = "survey_name")) %>%
  select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, valid_name, common, rank, wtcpue) %>%
  distinct()

#check for errors in name matching
if(sum(dat$valid_name == 'NA') > 0 | sum(is.na(dat$valid_name)) > 0){
  warning('>>create_master_table(): Did not match on some taxon [Variable: `tax`] names.')
}

# #if get warning, check for which spp have NA for name and common if check above fails
spp_na<-dat %>%
  filter(is.na(dat$valid_name) & is.na(dat$common)) %>%
  select(c("region", "spp", "valid_name", "common")) %>%
  distinct()

# spp_na_list<-unique(c(as.character(spp_na$spp)))
# spp_na<-as.data.frame(spp_na)
# sppNA_unique<-unique(spp_na[c("spp")])
# write.csv(sppNA_unique, "sppNA_unique.csv")

# #get list of higher order taxon names by region/survey and use to generate the list of higher order names to exclude later on
#   dat_HO_list<-dat %>%
#     filter(grepl("HigherOrder", rank)) %>%
#     select(c("region", "valid_name", "rank")) %>%
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
dat_fltr <- rbind(ai_fltr, ebs_fltr, nbs_fltr, gmex_fltr, goa_fltr, neus_fall_fltr, neus_spring_fltr, seusFALL_fltr, seusSPRING_fltr, seusSUMMER_fltr, wcann_fltr, wctri_fltr) %>%
  # Remove NA values in wtcpue
  filter(!is.na(wtcpue)) %>%
  # remove any extra white space from around spp and common names
  mutate(spp= str_squish(spp))
#convert all taxa names to first word capitalzied and rest lowercase...
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
  filter(is.na(dat_fltr$spp) & is.na(dat_fltr$common))
rm(spp_na)

if(isTRUE(REMOVE_REGION_DATASETS)) {
  rm(ai_fltr, ebs_fltr, gmex_fltr, goa_fltr, neus_fall_fltr, neus_spring_fltr, seusFALL_fltr, seusSPRING_fltr, seusSUMMER_fltr, wcann_fltr, wctri_fltr, tax)
}

if(isTRUE(WRITE_MASTER_DAT)){
  if(isTRUE(PREFER_RDATA)){
    saveRDS(dat_fltr, file = here("data_processing_rcode/output/data_clean", "all-regions-full-fltr_6_7_24.rds"))
  }else{
    write_csv(dat_fltr,file=here("data_processing_rcode/output/data_clean", "all-regions-full-fltr_3_17_23.csv"))
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

spp_addin<-read.csv("data_processing_rcode/data/Add_managed_spp.csv",header=T, sep=",")
spplist<-rbind(spplist, spp_addin) %>%
  distinct()

# Trim dat to these species (for a given region, spp pair in spplist_final, in dat, keep only rows that match that region, spp pairing)
trimmed_dat_fltr_expanded <- dat_fltr %>%
  filter(paste(region, spp) %in% paste(spplist$region, spplist$spp))

# Trim species (for IDW analysis)===========================================================
print("Trim species")

## FILTERED DATA
# Find a standard set of species (present at least 3/4 of the years of the filtered data in a region)
# this result differs from the original code because it does not include any species that have a pres value of 0.  It does, however, include species for which the common name is NA.
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
# retain all spp present at least 3/4 of the available years in a survey
spplist_IDW <- presyrsum %>%
  filter(presyr >= (maxyrs * 3/4)) %>%
  select(region, spp, common)

spp_addin<-read.csv("data_processing_rcode/data/Add_managed_spp.csv",header=T, sep=",")
spplist2<-rbind(spplist_IDW, spp_addin) %>%
  distinct() %>%
  mutate(DistributionProjectName="NMFS/Rutgers IDW Interpolation")
## use this spp list after explode 0 to add a column indicating that these species should be kept for IDW

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

# Dat_exploded -  Add 0's ======================================================
print("Dat exploded")
# these Sys.time() flags are here::here to see how long this section of code takes to run.
Sys.time()
# This takes about 10 minutes
if (DAT_EXPLODED == TRUE){
  dat.exploded <- as.data.table(trimmed_dat_fltr_expanded)[,explode0(.SD), by="region"]
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
dat.exploded<-left_join(dat.exploded, spplist2, by=c("spp","common","region"))

spp_IDW<-dat.exploded %>%
  filter(DistributionProjectName=="NMFS/Rutgers IDW Interpolation") %>%
  select(spp, common) %>%
  distinct()

spp_survey<-dat.exploded %>%
  select(spp, common, region) %>%
  distinct()

#stop and....
## Go to Update_Filter_Table.R
## GO TO create_data_for_map_generation.R now


###################### CAN STOP HERE ##########################################
## CORE Species -- caught every year of survey =======

print("Core species")

## FILTERED DATA
# Find a standard set of species (present at least 3/4 of the years of the filtered data in a region)
# this result differs from the original code because it does not include any species that have a pres value of 0.  It does, however, include speices for which the common name is NA.
presyr <- present_every_year(dat_fltr, region, spp, common, year)

haulsyr<-num_hauls_year(dat_fltr, region, year)

preshaul<-left_join(presyr, haulsyr, by=c("region", "year")) %>%
  mutate(proportion=((pres/hauls)*100))%>%
  filter(proportion>=5)

# years in which spp was present in >= 5% of tows
presyrsum <- num_year_present(preshaul, region, spp, common)

# max num years of survey in each region
maxyrs <- max_year_surv(presyrsum, region)

# merge in max years
presyrsum <- left_join(presyrsum, maxyrs, by = "region")
# write.csv(presyrsum, "presyrsum_11_22_22.csv")
# retain all spp present all years of the available years in a survey
spplist_core <- presyrsum %>%
  filter(presyr >= maxyrs) %>%
  select(region, spp, common)

# Summary information about # of species in this analysis================
#number of unique species across all regions
dfuniq<-unique(spplist[c("spp", "common", "region")]) %>%
  mutate(
    region = ifelse(grepl("West Coast", region), "West Coast", region),
    region = ifelse(grepl("Northeast", region), "Northeast", region),
    region = ifelse(grepl("Southeast", region), "Southeast", region)) %>%
  distinct()

dfuniq_Core<-unique(spplist_core[c("spp", "common")])
length(dfuniq_Core)

#number of unique species caught in each regional survey (expanded data set)
spp_reg_counts<-spplist %>%
  group_by(region)%>%
  summarise(distinct_spp=n_distinct(spp))

#number of unique species within each regional survey (caught 3/4 or years)
spp_reg_counts_quarters<-spplist2 %>%
  group_by(region)%>%
  summarise(spp_3_4years=n_distinct(spp))

#number of unique species CAUGHT ALL YEARS within each region
spp_reg_counts_Core<-spplist_core%>%
  group_by(region)%>%
  summarise(spp_all_yrs=n_distinct(spp))

num_spp_summary<-left_join(spp_reg_counts, spp_reg_counts_quarters, by=c("region"))
num_spp_summary<-left_join(num_spp_summary, spp_reg_counts_Core, by=c("region"))
write.csv(num_spp_summary, file=here("data_processing_rcode/output/data_clean", "summary_unique_spp_table_7_24_24.csv"))
write.csv(spplist_core, file=here("data_processing_rcode/output/data_clean","core_spp_list_7_24_24.csv"))

## compare with the Master Filter Table for the filter functionality on the portal
filter_table<-read.csv("Species_Filter.csv", header=T, sep=",")
spp_to_remove<-anti_join(filter_table, dfuniq, by=c("spp", "FilterSubRegion"="region"))

# write.csv(spp_to_remove, "spp_removed_filter_6_10_24.csv")
#  #remove these species from the filter table
# filter_table_revised<-anti_join(filter_table, spp_to_remove)
#
miss_filter<-anti_join(dfuniq, filter_table, by=c("spp", "region"="FilterSubRegion")) %>%
  rename(FilterSubRegion=region)
#
# Filter_table_updated<-bind_rows(filter_table_revised, miss_filter)
# #write.csv(Filter_table_updated, file=here("data_processing_rcode/output/data_clean", "Final_Filter_Table.csv"))

## Compare old and new filter table to see which species were removed and which were added!
old_table<-read.csv("filter_table_final_5_31_23.csv", header=T, sep=",")
new_table<- read.csv("output/data_clean/Final_Filter_Table.csv", header=T, sep=",")

spp_added<-anti_join(new_table, old_table, by= c("spp", "FilterSubRegion"))
write.csv(spp_added, "spp_added_to_filter_6_10_24.csv")
spp_removed<-anti_join(old_table, new_table, by= c("spp", "FilterSubRegion"))
write.csv(spp_removed, "spp_removed_from_filter_6_10_24.csv")


##GET LIST OF SPECIES AND TAXON REMOVED
# Master "Filtered" dataset
dat_fltr <- rbind(ai_fltr, ebs_fltr, nbs_fltr, gmex_fltr, goa_fltr, neus_fall_fltr, neus_spring_fltr, seusFALL_fltr, seusSPRING_fltr, seusSUMMER_fltr, wcann_fltr, wctri_fltr) %>%
  # Remove NA values in wtcpue
  filter(!is.na(wtcpue)) %>%
  # remove any extra white space from around spp and common names
  mutate(spp= str_squish(spp))
#convert all taxa names to first word capitalzied and rest lowercase...
dat_fltr$spp<-firstup(dat_fltr$spp)
# add a case sensitive spp and common name and filter out Higher Level taxon names, the turtle, bird, and dolphin species, and plants/seaweed species.
dat_fltr <- left_join(dat_fltr, tax, by = c("spp" = "survey_name"))
data_fltr_HOremoved<- dat_fltr %>%
  filter(!grepl("HigherOrder", rank),
         !grepl("remove", rank),
         !grepl("Caretta caretta", valid_name),
         !grepl("Sagmatias obliquidens", valid_name),
         !grepl("Puffinus gravis", valid_name),
         !grepl("Phaeophyceae", class),
         !grepl("Florideophyceae", class),
         !grepl("Ulvophyceae", class)) %>%
  distinct()
removed<-anti_join(dat_fltr, data_fltr_HOremoved, by=c("valid_name", "region")) %>%
  select(valid_name, common)%>%
  distinct()
write.csv(removed, "removed_HO_taxa.csv")

filterd_spp<-anti_join(data_fltr_HOremoved, dfuniq, by=c("valid_name"="spp")) %>%
  select(valid_name, common) %>%
  distinct()
write.csv(filterd_spp, "filter_removed_spp.csv")
