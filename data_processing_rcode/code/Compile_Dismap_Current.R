## ---- DISMAP 04/18/2024 --- NOTE: need to double check SEUS and WCANN information (get different files depending on where on FRAM download the data from;
# also look at FishGLOB code for some standard column names, and how they handled it... ) 

## updated thru 2023 survey data for all regions except SEUS (which is thru 2022)
## added bottom temperature and SST to the files for all regions (note: West Coast raw data doesn't include these variables)

#--------------------------------------------------------------------------------------#
#### LOAD LIBRARIES AND FUNCTIONS ####
#--------------------------------------------------------------------------------------#

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


# If running from R instead of RStudio, please set the working directory to the folder containing this script before running this script.
# This script is designed to run within the following directory structure:
# Directory 1 contains:
# 1. compile_Dismap_Current.R script - this script
# 2. data_raw directory - folder containing all raw data files
# 3. data_clean directory - folder where the cleaned data will be saved to 
# 4. 'plots' folder where to store the plots generated with HQ_DATA_ONLY == TRUE
# 4. Additional R scripts used to download data, create data for mapping, and cleaning taxa 

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

# 4. Create graphs based on the data similar to those shown on the website and outputs them to pdf. #DEFAULT:FALSE
PLOT_CHARTS <- FALSE
# This used to be called OPTIONAL_PLOT_CHARTS, do I need to change it back?

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
#developed from http://www.nceas.ucsb.edu/files/scicomp/GISSeminar/UseCases/CalculateConvexHull/CalculateConvexHullR.html
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
  
  # print(x[1]) #enable below line 204 to run a test of the function 
  # x <- as.data.table(x)
   # x <- as.data.table(trimmed_dat_fltr)[region=="Aleutian Islands"]
  # setkey(x, sampleid, stratum, year, lat, lon, stratumarea, depth)
  
  # group the data by these columns
  setorder(x, haulid,  stratum, year, datetime, lat, lon, stratumarea, depth, sbt,
           sst, vesselID, haul_dist, haul_dur, area_swept)
  
  # pull out all of the unique spp
  u.spp <- x[,as.character(unique(spp))]
  # pull out all of the unique common names
  u.cmmn <- x[,common[!duplicated(as.character(spp))]]
  #pull out all of the unique kingdom through to genus names and worms_id
  u.king<-x[,kingdom[!duplicated(as.character(spp))]]
  u.phy<-x[,phylum[!duplicated(as.character(spp))]]
  u.class<-x[,class[!duplicated(as.character(spp))]]
  u.order<-x[,order[!duplicated(as.character(spp))]]
  u.fam<-x[,family[!duplicated(as.character(spp))]]
  u.gen<-x[,genus[!duplicated(as.character(spp))]]
  u.worm<-x[,worms_id[!duplicated(as.character(spp))]]
  
  # pull out these location related columns and sort by haulid and year
  x.loc <- x[,list(haulid, year, datetime, stratum, stratumarea, lat, lon, depth, 
                   sbt, sst, vesselID, haul_dist, haul_dur, area_swept)]
  setkey(x.loc, haulid, year)
  
  # attatch all spp to all locations
  x.skele <- x.loc[,list(spp=u.spp, common=u.cmmn, kingdom=u.king, phylum=u.phy, class=u.class,
                         order=u.order, family=u.fam, genus=u.gen, worms_id=u.worm), by=eval(colnames(x.loc))]
  setkey(x.skele, haulid, year, spp)
  x.skele <- unique(x.skele)
  setcolorder(x.skele, c("haulid","year", "spp", "common", "stratum", "stratumarea","lat","lon","depth", "sbt",
                         "sst", "vesselID", "haul_dist", "haul_dur", "area_swept", "kingdom", "phylum",
                         "class", "order", "family", "genus", "worms_id"))
  
   # pull in multiple observations of the same species 
  x.spp.dat <- x[,list(haulid, year, spp, num, numcpue, wgt, wtcpue)]
  setkey(x.spp.dat, haulid, year, spp)
  x.spp.dat <- unique(x.spp.dat)
  
  out <- x.spp.dat[x.skele, allow.cartesian = TRUE]
  
  out$wtcpue[is.na(out$wtcpue)] <- 0
  out$wgt[is.na(out$wgt)]<-0
  out$num[is.na(out$num)]<-0
  out$numcpue[is.na(out$numcpue)]<-0
 
  out$num<-ifelse(out$num == 0 & out$wgt>0, NA, out$num)
  out$numcpue<-ifelse(out$numcpue == 0 & out$wgt>0, NA, out$numcpue)
  
  out<-out[, c(1,2,27,9:19,3, 8, 4:7, 20:26)]
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

#--------------------------------------------------------------------------------------#
# Compile AI =====================================================
print("Compile AI")

# read in AI survey data file 
ai_data <- read_csv(here::here("data_raw", "ai1991_2021.csv"))  %>% 
  # remove any extra white space from around spp and common names
  mutate(Stratum=as.integer(Stratum),
         `Common Name` = str_trim(`Common Name`), 
         `Scientific Name` = str_trim(`Scientific Name`)) 

ai_strata <- read_csv(here::here("data_raw", "ai_strata.csv"), col_types = cols(NPFMCArea = col_character(),
                                                                                SubareaDescription = col_character(),
                                                                                StratumCode = col_integer(),
                                                                                DepthIntervalm = col_character(),
                                                                                Areakm2 = col_integer()
))  %>% 
  select(StratumCode, Areakm2) %>% 
  rename(Stratum = StratumCode)


ai <- left_join(ai_data, ai_strata, by = "Stratum") %>%
  # rename columns
  rename(year = Year, 
         datetime = `Date Time`,
         lat = `Latitude Dd`, 
         lon = `Longitude Dd`,
         sbt=`Bottom Temperature C`,
         sst=`Surface Temperature C`,
         depth = `Depth M`, 
         spp = `Scientific Name`,
         common =`Common Name`,
         stratum = Stratum,
         stratumarea = Areakm2,
         vesselID = `Vessel Id`,
         haul_dist = `Distance Fished Km`, #units Km
         haul_dur = `Duration Hr`, #units in hours
         area_swept = `Area Swept Ha`, #units in Ha
         num = `Count`,
         numcpue = `Cpue Noha`,
         wgt = `Weight Kg`,
         wtcpue = `Cpue Kgha`) #units = kg/hectare ( hectare = 0.01 km)
# are there any strata in the data that are not in the strata file?
stopifnot(nrow(filter(ai, is.na(stratumarea))) == 0)

# the following chunk of code reformats and fixes this region's data
ai <- ai %>% 
  mutate(
    # add species names for two rockfish complexes
    spp = ifelse(grepl("Rougheye and Blackspotted Rockfish Unid.", common), "Sebastes melanostictus and S. aleutianus", spp),
    spp = ifelse(grepl("Dusky and Dark Rockfishes Unid.", common), "Sebastes variabilis and S. ciliatus", spp), 
    # Create a unique haulid
    haulid = paste(formatC(vesselID, width=3, flag=0), Cruise, formatC(Haul, width=3, flag=0), sep='-'), 
    # change -9999 wtcpue to NA
    wtcpue = ifelse(wtcpue == "-9999", NA, wtcpue)) %>% 
  # remove rows that are eggs
  filter(spp != "" &
           # remove all spp that contain the word "egg"
           !grepl("egg", spp),
         !grepl("Polychaete tubes", spp)) %>% 
  # adjust spp names
  mutate(
    # catch A. stomias and A. evermanii (as of 2018 both spp appear as "valid" so not sure why they are being changed)
    spp = ifelse(grepl("Atheresthes", spp), "Atheresthes stomias and A. evermanni", spp), 
    # catch L. polystryxa (valid in 2018), and L. bilineata (valid in 2018)
    spp = ifelse(grepl("Lepidopsetta", spp), "Lepidopsetta sp.", spp),
    # catch M. jaok (valid in 2018), M. niger (valid in 2018), M. polyacanthocephalus (valid in 2018), M. quadricornis (valid in 2018), M. verrucosus (changed to scorpius), M. scorpioides (valid in 2018), M. scorpius (valid in 2018) (M. scorpius is in the data set but not on the list so it is excluded from the change)
    #spp = ifelse(grepl("Myoxocephalus", spp ) & !grepl("scorpius", spp), "Myoxocephalus sp.", spp),
    # catch B. maculata (valid in 2018), abyssicola (valid in 2018), aleutica (valid in 2018), interrupta (valid in 2018), lindbergi (valid in 2018), mariposa (valid in 2018), minispinosa (valid in 2018), parmifera (valid in 2018), smirnovi (valid in 2018), cf parmifera (Orretal), spinosissima (valid in 2018), taranetzi (valid in 2018), trachura (valid in 2018), violacea (valid in 2018)
    # B. panthera is not on the list of spp to change
    spp = ifelse(grepl("Bathyraja", spp), 'Bathyraja sp.', spp),
    # catch S. melanostictus and S. aleutianus (blackspotted & rougheye), combined into one complex
    spp = ifelse(grepl("Sebastes melanostictus", spp)|grepl("Sebastes aleutianus", spp), "Sebastes melanostictus and S. aleutianus", spp),
    # catch S. variabilis and S. ciliatus (dusky + dark rockfish), combined into one complex
    spp = ifelse(grepl("Sebastes variabilis", spp)|grepl("Sebastes ciliatus", spp), "Sebastes variabilis and S. ciliatus", spp)
  ) %>% 
  select(haulid, year, datetime, lat, lon, stratum, stratumarea, vesselID, haul_dist, haul_dur, area_swept, sbt, sst, depth, spp, num, numcpue, wgt, wtcpue) %>% 
  type_convert(col_types = cols(
    lat = col_double(),
    lon = col_double(),
    year = col_integer(),
    wtcpue = col_double(),
    spp = col_character(),
    sbt = col_double(),
    sst = col_double(), 
    depth = col_integer(),
    haulid = col_character()
  )) %>% 
  group_by(haulid, year, datetime, lat, lon, stratum, stratumarea, vesselID, haul_dist, haul_dur, area_swept, sbt, sst, depth, spp) %>% 
  summarise(wtcpue = sumna(wtcpue),
            numcpue=sumna(numcpue),
            num = sumna(num),
            wgt = sumna(wgt)) %>% 
  # Calculate a corrected longitude for Aleutians (all in western hemisphere coordinates)
  ungroup() %>% 
  mutate(lon = ifelse(lon > 0, lon - 360, lon), 
         region = "Aleutian Islands") %>% 
  select(region, haulid, year, datetime, lat, lon, stratum, stratumarea, vesselID, haul_dist, haul_dur, area_swept, sbt, sst, depth, spp, num, numcpue, wgt, wtcpue)

if (HQ_DATA_ONLY == TRUE){
  
  # look at the graph and make sure decisions to keep or eliminate data make sense
  
  # plot the strata by year
  
  p1 <- ai %>% 
    select(stratum, year) %>% 
    ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
    geom_jitter()
  
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
    geom_jitter()
  
  p4 <- ai_fltr %>%
    select(lat, lon) %>% 
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()
  
  if (HQ_PLOTS == TRUE){
    temp <- grid.arrange(p1, p2, p3, p4, nrow = 2)
    ggsave(plot = temp, filename = here::here("plots", "ai_hq_dat_removed.png"))
    rm(temp)
  }
  rm(test, test2, p1, p2, p3, p4)
}# clean up
rm(ai_data, ai_strata)

#--------------------------------------------------------------------------------------#
# Compile EBS ============================================================
print("Compile EBS")
files <- as.list(dir(pattern = "ebs", path = "data_raw", full.names = T))

# exclude the strata file
files <- files[-grep("strata", files)]

# combine all of the data files into one table
ebs_data <- files %>% 
  # read in all of the csv's in the files list
  map_dfr(read_csv) %>%
  # remove any data rows that have headers as data rows
  filter(!is.na(`Latitude Dd`)) %>% 
  # remove any extra white space from around spp and common names
  mutate(Stratum=as.integer(Stratum),
         `Common Name` = str_trim(`Common Name`), 
         `Scientific Name` = str_trim(`Scientific Name`)) 

# import the strata data
ebs_strata <- read_csv(here::here("data_raw", "ebs_strata.csv"), col_types = cols(
  SubareaDescription = col_character(),
  StratumCode = col_integer(),
  Areakm2 = col_integer()
)) %>% 
  select(StratumCode, Areakm2) %>% 
  rename(Stratum = StratumCode)

ebs <- left_join(ebs_data, ebs_strata, by = "Stratum")%>%
  # rename columns
  rename(year = Year, 
         datetime = `Date Time`,
         lat = `Latitude Dd`, 
         lon = `Longitude Dd`,
         sbt=`Bottom Temperature C`,
         sst=`Surface Temperature C`,
         depth = `Depth M`, 
         spp = `Scientific Name`,
         common =`Common Name`,
         stratum = Stratum,
         stratumarea = Areakm2,
         vesselID = `Vessel Id`,
         haul_dist = `Distance Fished Km`, #units Km
         haul_dur = `Duration Hr`, #units in hours
         area_swept = `Area Swept Ha`, #units in Ha
         num = `Count`,
         numcpue = `Cpue Noha`,
         wgt = `Weight Kg`,
         wtcpue = `Cpue Kgha`) #units = kg/hectare ( hectare = 0.01 km)
# are there any strata in the data that are not in the strata file?
stopifnot(nrow(filter(ai, is.na(stratumarea))) == 0)

ebs <- ebs %>% 
  mutate(
    # add species names for two rockfish complexes
    spp = ifelse(grepl("Rougheye and Blackspotted Rockfish Unid.", common), "Sebastes melanostictus and S. aleutianus", spp),
    spp = ifelse(grepl("Dusky and Dark Rockfishes Unid.", common), "Sebastes variabilis and S. ciliatus", spp), 
    # Create a unique haulid
    haulid = paste(formatC(vesselID, width=3, flag=0), Cruise, formatC(Haul, width=3, flag=0), sep='-'), 
    # convert -9999 to NA 
    wtcpue = ifelse(wtcpue == "-9999", NA, wtcpue)) %>%  
  # remove eggs
  filter(spp != '' &
           !grepl("egg", spp),
         !grepl("Polychaete tubes", spp)) %>% 
  # adjust spp names
  mutate(spp = ifelse(grepl("Atheresthes", spp), "Atheresthes stomias and A. evermanni", spp), 
         spp = ifelse(grepl("Lepidopsetta", spp), "Lepidopsetta sp.", spp),
         # spp = ifelse(grepl("Myoxocephalus", spp), "Myoxocephalus sp.", spp),
         spp = ifelse(grepl("Bathyraja", spp), 'Bathyraja sp.', spp), 
         spp = ifelse(grepl("Hippoglossoides", spp), "Hippoglossoides elassodon and H. robustus", spp),
         spp = ifelse(grepl("Sebastes melanostictus", spp)|grepl("Sebastes aleutianus", spp), "Sebastes melanostictus and S. aleutianus", spp),
         spp = ifelse(grepl("Sebastes variabilis", spp)|grepl("Sebastes ciliatus", spp), "Sebastes variabilis and S. ciliatus", spp)) %>%
  # change from all character to fitting column types
  select(haulid, year, datetime, lat, lon, stratum, stratumarea, vesselID, haul_dist, haul_dur, area_swept, sbt, sst, depth, spp, num, numcpue, wgt, wtcpue) %>% 
  type_convert(col_types = cols(
    lat = col_double(),
    lon = col_double(),
    year = col_integer(),
    wtcpue = col_double(),
    spp = col_character(),
    sbt = col_double(),
    sst = col_double(), 
    depth = col_integer(),
    haulid = col_character()
  )) %>% 
  group_by(haulid, year, datetime, lat, lon, stratum, stratumarea, vesselID, haul_dist, haul_dur, area_swept, sbt, sst, depth, spp,) %>% 
  summarise(wtcpue = sumna(wtcpue),
            numcpue=sumna(numcpue),
            num = sumna(num),
            wgt = sumna(wgt)) %>% 
  ungroup() %>% 
  mutate(region = "Eastern Bering Sea") %>% 
  select(region, haulid, year, datetime, lat, lon, stratum, stratumarea, vesselID, haul_dist, haul_dur, area_swept, sbt, sst, depth, spp, num, numcpue, wgt, wtcpue)


if (HQ_DATA_ONLY == TRUE){
  # look at the graph and make sure decisions to keep or eliminate data make sense
  
  p1 <- ebs %>% 
    select(stratum, year) %>% 
    ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
    geom_jitter()
  
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
  
  # how many rows will be lost if only years where all stratum sampled are kept?
  test2 <- ebs %>% 
    filter(year %in% test$year)
  nrow(ebs) - nrow(test2)
  # percent that will be lost
  print((nrow(ebs) - nrow(test2))/nrow(ebs))
  # 8% of rows are removed
  ebs_fltr <- ebs %>% 
    filter(year %in% test$year) 
  
  p3 <- ebs_fltr %>% 
    select(stratum, year) %>% 
    ggplot(aes(x = as.factor(stratum), y = as.factor(year))) +
    geom_jitter()
  
  p4 <- ebs_fltr %>%
    select(lat, lon) %>% 
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()
  
  if (HQ_PLOTS == TRUE){
    temp <- grid.arrange(p1, p2, p3, p4, nrow = 2)
    ggsave(plot = temp, filename = here::here("plots", "ebs_hq_dat_removed.png"))
    rm(temp)
  }
  rm(test, test2, p1, p2, p3, p4)
}
# clean up
rm(files, ebs_data, ebs_strata)


#--------------------------------------------------------------------------------------#
# Compile GOA =============================================================
print("Compile GOA")

files <- as.list(dir(pattern = "goa", path = "data_raw", full.names = T))

# exclude the 2 strata files; the 1 and 2 elements
files <- files[-grep("strata", files)]

# combine all of the data files into one table
goa_data <- files %>% 
  # read in all of the csv's in the files list
  purrr::map_dfr(read_csv) %>%
  # remove any data rows that have headers as data rows
  filter(!is.na(`Latitude Dd`)) %>%  
  # remove any extra white space from around spp and common names
  mutate(Stratum=as.integer(Stratum),
         `Common Name` = str_trim(`Common Name`), 
         `Scientific Name` = str_trim(`Scientific Name`)) 

#read in the goa strata data
goa_strata <- read_csv(here::here("data_raw", "goa_strata.csv"), col_types = cols(
  SubareaDescription = col_character(),
  StratumCode = col_integer(),
  Areakm2 = col_integer()
)) %>% 
  select(StratumCode, Areakm2) %>% 
  rename(Stratum = StratumCode)

goa <- left_join(goa_data, goa_strata, by = "Stratum") %>%
  # rename columns
  rename(year = Year, 
         datetime = `Date Time`,
         lat = `Latitude Dd`, 
         lon = `Longitude Dd`,
         sbt=`Bottom Temperature C`,
         sst=`Surface Temperature C`,
         depth = `Depth M`, 
         spp = `Scientific Name`,
         common =`Common Name`,
         stratum = Stratum,
         stratumarea = Areakm2,
         vesselID = `Vessel Id`,
         haul_dist = `Distance Fished Km`, #units Km
         haul_dur = `Duration Hr`, #units in hours
         area_swept = `Area Swept Ha`, #units in Ha
         num = `Count`,
         numcpue = `Cpue Noha`,
         wgt = `Weight Kg`,
         wtcpue = `Cpue Kgha`) #units = kg/hectare ( hectare = 0.01 km)
# are there any strata in the data that are not in the strata file?
stopifnot(nrow(filter(ai, is.na(stratumarea))) == 0)

goa <- goa %>%
  mutate(
    # add species names for two rockfish complexes
    spp = ifelse(grepl("Rougheye and Blackspotted Rockfish Unid.", common), "Sebastes melanostictus and S. aleutianus", spp),
    spp = ifelse(grepl("Dusky and Dark Rockfishes Unid.", common), "Sebastes variabilis and S. ciliatus", spp), 
    # Create a unique haulid
    haulid = paste(formatC(vesselID, width=3, flag=0), Cruise, formatC(Haul, width=3, flag=0), sep='-'),    
    wtcpue = ifelse(wtcpue == "-9999", NA, wtcpue)) %>% 
  # remove non-fish
  filter(
    spp != '' & 
      !grepl("egg", spp),
    !grepl("Polychaete tubes", spp)) %>% 
  # adjust spp names
  mutate(
    spp = ifelse(grepl("Lepidopsetta", spp), "Lepidopsetta sp.", spp),
    #spp = ifelse(grepl("Myoxocephalus", spp), "Myoxocephalus sp.", spp),
    spp = ifelse(grepl("Bathyraja", spp) & !grepl("panthera", spp),'Bathyraja sp.', spp), 
    spp = ifelse(grepl("Sebastes melanostictus", spp)|grepl("Sebastes aleutianus", spp), "Sebastes melanostictus and S. aleutianus", spp),
    spp = ifelse(grepl("Sebastes variabilis", spp)|grepl("Sebastes ciliatus", spp), "Sebastes variabilis and S. ciliatus", spp)) %>%
  # change from all character to fitting column types
  select(haulid, year, datetime, lat, lon, stratum, stratumarea, vesselID, haul_dist, haul_dur, area_swept, sbt, sst, depth, spp, num, numcpue, wgt, wtcpue) %>% 
  type_convert(col_types = cols(
    lat = col_double(),
    lon = col_double(),
    year = col_integer(),
    wtcpue = col_double(),
    spp = col_character(),
    sbt = col_double(),
    sst = col_double(), 
    depth = col_integer(),
    haulid = col_character()
  )) %>% 
  group_by(haulid, year, datetime, lat, lon, stratum, stratumarea, vesselID, haul_dist, haul_dur, area_swept, sbt, sst, depth, spp,) %>% 
  summarise(wtcpue = sumna(wtcpue),
            numcpue=sumna(numcpue),
            num = sumna(num),
            wgt = sumna(wgt)) %>% 
  ungroup() %>% 
  mutate(region = "Gulf of Alaska") %>% 
  select(region, haulid, year, datetime, lat, lon, stratum, stratumarea, vesselID, haul_dist, haul_dur, area_swept, sbt, sst, depth, spp, num, numcpue, wgt, wtcpue)


if (HQ_DATA_ONLY == TRUE){
  # look at the graph and make sure decisions to keep or eliminate data make sense
  
  p1 <- goa %>% 
    select(stratum, year) %>% 
    ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
    geom_jitter()
  
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
    filter(count >= 11)  
  
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
    geom_jitter()
  
  p4 <- goa_fltr %>%
    select(lat, lon) %>% 
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()
  
  if (HQ_PLOTS == TRUE){
    temp <- grid.arrange(p1, p2, p3, p4, nrow = 2)
    ggsave(plot = temp, filename = here::here("plots", "goa_hq_dat_removed.png"))
    
    rm(temp)
  }
  rm(test, test2, p1, p2, p3, p4)
}
rm(files, goa_data, goa_strata)

#--------------------------------------------------------------------------------------#
# Compile NBS =============================================================
print("Compile NBS")
#Note: there is no strata file for this survey. But the info in there is not used anyways
nbs_data <- read_csv(here::here("data_raw", "nbs_survey.csv")) %>%
  # remove any extra white space from around spp and common names
  mutate(Stratum=as.integer(Stratum),
         `Common Name` = str_trim(`Common Name`), 
         `Scientific Name` = str_trim(`Scientific Name`)) %>%
  # rename columns
  rename(year = Year, 
         datetime = `Date Time`,
         lat = `Latitude Dd`, 
         lon = `Longitude Dd`,
         sbt=`Bottom Temperature C`,
         sst=`Surface Temperature C`,
         depth = `Depth M`, 
         spp = `Scientific Name`,
         common =`Common Name`,
         stratum = Stratum,
         vesselID = `Vessel Id`,
         haul_dist = `Distance Fished Km`, #units Km
         haul_dur = `Duration Hr`, #units in hours
         area_swept = `Area Swept Ha`, #units in Ha
         num = `Count`,
         numcpue = `Cpue Noha`,
         wgt = `Weight Kg`,
         wtcpue = `Cpue Kgha`) #units = kg/hectare ( hectare = 0.01 km)

nbs <- nbs_data %>%
  mutate(
    # add species names for two rockfish complexes
    spp = ifelse(grepl("Rougheye and Blackspotted Rockfish Unid.", common), "Sebastes melanostictus and S. aleutianus", spp),
    spp = ifelse(grepl("Dusky and Dark Rockfishes Unid.", common), "Sebastes variabilis and S. ciliatus", spp), 
    # Create a unique haulid
    stratumarea=NA,
    haulid = paste(formatC(vesselID, width=3, flag=0), Cruise, formatC(Haul, width=3, flag=0), sep='-'),    
    wtcpue = ifelse(wtcpue == "-9999", NA, wtcpue)) %>% 
  # remove non-fish
  filter(
    spp != '' & 
      !grepl("egg", spp),
    !grepl("Polychaete tubes", spp)) %>% 
  # adjust spp names
  mutate(spp = ifelse(grepl("Atheresthes", spp), "Atheresthes stomias and A. evermanni", spp), 
         spp = ifelse(grepl("Lepidopsetta", spp), "Lepidopsetta sp.", spp),
         # spp = ifelse(grepl("Myoxocephalus", spp), "Myoxocephalus sp.", spp),
         spp = ifelse(grepl("Bathyraja", spp), 'Bathyraja sp.', spp), 
         spp = ifelse(grepl("Hippoglossoides", spp), "Hippoglossoides elassodon and H. robustus", spp),
         spp = ifelse(grepl("Sebastes melanostictus", spp)|grepl("Sebastes aleutianus", spp), "Sebastes melanostictus and S. aleutianus", spp),
         spp = ifelse(grepl("Sebastes variabilis", spp)|grepl("Sebastes ciliatus", spp), "Sebastes variabilis and S. ciliatus", spp)) %>%
  # change from all character to fitting column types
  select(haulid, year, datetime, lat, lon, stratum, stratumarea, vesselID, haul_dist, haul_dur, area_swept, sbt, sst, depth, spp, num, numcpue, wgt, wtcpue) %>% 
  type_convert(col_types = cols(
    lat = col_double(),
    lon = col_double(),
    year = col_integer(),
    wtcpue = col_double(),
    spp = col_character(),
    sbt = col_double(),
    sst = col_double(), 
    depth = col_integer(),
    haulid = col_character()
  )) %>% 
  group_by(haulid, year, datetime, lat, lon, stratum, stratumarea, vesselID, haul_dist, haul_dur, area_swept, sbt, sst, depth, spp,) %>% 
  summarise(wtcpue = sumna(wtcpue),
            numcpue=sumna(numcpue),
            num = sumna(num),
            wgt = sumna(wgt)) %>% 
  ungroup() %>% 
  mutate(region = "Northern Bering Sea") %>% 
  select(region, haulid, year, datetime, lat, lon, stratum, stratumarea, vesselID, haul_dist, haul_dur, area_swept, sbt, sst, depth, spp, num, numcpue, wgt, wtcpue)


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
    ggsave(plot = temp, filename = here::here("plots", "nbs_hq_dat_removed.png"))
    
    rm(temp)
  }
  rm(test, test2, p1, p2, p3, p4)
}
rm(files, nbs_data, nbs_strata)

#--------------------------------------------------------------------------------------#
# # Compile BSSS ================================
# #(Data will not update because the survey is no longer running since 2016)
# print("Compile BSSS")
# #Note: there is no strata file for this survey. But the info in there is not used anyways
# bsss_data <- read_csv(here::here("data_raw", "EBSS_data.csv")) %>%
#   select(Year, Cruise, Haul, `Vessel Id`, `Latitude Dd`, `Longitude Dd`, Stratum, `Cpue Kgha`,`Depth M`, `Scientific Name`, `Common Name`) %>% 
#   # remove any extra white space from around spp and common names
#   mutate(Stratum=as.integer(Stratum),
#          `Common Name` = str_trim(`Common Name`), 
#          `Scientific Name` = str_trim(`Scientific Name`)) %>%
#   # rename columns
#   rename(year = Year, 
#          lat = `Latitude Dd`, 
#          lon = `Longitude Dd`, 
#          depth = `Depth M`, 
#          spp = `Scientific Name`,
#          common =`Common Name`,
#          stratum = Stratum,
#          vesselID = `Vessel Id`,
#          wtcpue = `Cpue Kgha`)
# 
# bsss <- bsss_data %>%
#   mutate(
#     # add species names for two rockfish complexes
#     spp = ifelse(grepl("Rougheye and Blackspotted Rockfish Unid.", common), "Sebastes melanostictus and S. aleutianus", spp),
#     spp = ifelse(grepl("Dusky and Dark Rockfishes Unid.", common), "Sebastes variabilis and S. ciliatus", spp), 
#     # Create a unique haulid
#     stratumarea=NA,
#     haulid = paste(formatC(vesselID, width=3, flag=0), Cruise, formatC(Haul, width=3, flag=0), sep='-'),    
#     wtcpue = ifelse(wtcpue == "-9999", NA, wtcpue)) %>% 
#   # remove non-fish
#   filter(
#     spp != '' & 
#       !grepl("egg", spp),
#     !grepl("Polychaete tubes", spp)) %>% 
#   # adjust spp names
#   mutate(spp = ifelse(grepl("Atheresthes", spp), "Atheresthes stomias and A. evermanni", spp), 
#          spp = ifelse(grepl("Lepidopsetta", spp), "Lepidopsetta sp.", spp),
#          # spp = ifelse(grepl("Myoxocephalus", spp), "Myoxocephalus sp.", spp),
#          spp = ifelse(grepl("Bathyraja", spp), 'Bathyraja sp.', spp), 
#          spp = ifelse(grepl("Hippoglossoides", spp), "Hippoglossoides elassodon and H. robustus", spp),
#          spp = ifelse(grepl("Sebastes melanostictus", spp)|grepl("Sebastes aleutianus", spp), "Sebastes melanostictus and S. aleutianus", spp),
#          spp = ifelse(grepl("Sebastes variabilis", spp)|grepl("Sebastes ciliatus", spp), "Sebastes variabilis and S. ciliatus", spp)) %>%
#   # change from all character to fitting column types
#   type_convert(col_types = cols(
#     lat = col_double(),
#     lon = col_double(),
#     year = col_integer(),
#     wtcpue = col_double(),
#     spp = col_character(),
#     depth = col_integer(),
#     haulid = col_character(),
#     startumarea=col_character()
#   ))  %>% 
#   group_by(haulid, stratum, stratumarea, year, lat, lon, depth, spp) %>% 
#   summarise(wtcpue = sumna(wtcpue)) %>% 
#   mutate(region = "Bering Sea Slope Survey") %>% 
#   select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue) %>% 
#   ungroup()
# 
# if (HQ_DATA_ONLY == TRUE){
#   # look at the graph and make sure decisions to keep or eliminate data make sense
#   
#   p1 <- bsss %>% 
#     select(stratum, year) %>% 
#     ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
#     geom_jitter()
#   
#   p2 <- bsss %>%
#     select(lat, lon) %>% 
#     ggplot(aes(x = lon, y = lat)) +
#     geom_jitter()
#   
#   test <- bsss %>%
#     select(stratum, year) %>% 
#     distinct() %>% 
#     group_by(stratum) %>% 
#     summarise(count = n())%>%
#     filter(count >= 5)  
#   
#   # how many rows will be lost if only stratum trawled ever year aare kept?
#   test2 <- bsss %>% 
#     filter(stratum %in% test$stratum)
#   nrow(bsss) - nrow(test2)
#   # percent that will be lost
#   print ((nrow(bsss) - nrow(test2))/nrow(bsss))
#   
#   bsss_fltr <- bsss %>% 
#     filter(stratum %in% test$stratum)
#   
#   p3 <-  bsss_fltr %>% 
#     select(stratum, year) %>% 
#     ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
#     geom_jitter()
#   
#   p4 <- bsss_fltr %>%
#     select(lat, lon) %>% 
#     ggplot(aes(x = lon, y = lat)) +
#     geom_jitter()
#   
#   if (HQ_PLOTS == TRUE){
#     temp <- grid.arrange(p1, p2, p3, p4, nrow = 2)
#     ggsave(plot = temp, filename = here::here("plots", "bsss_hq_dat_removed.png"))
#     
#     rm(temp)
#   }
#   rm(test, test2, p1, p2, p3, p4)
# }
# rm(files, bsss_data, bsss_strata)


#--------------------------------------------------------------------------------------#
# Compile WCTRI ===========================================================
print("Compile WCTRI")

wctri_catch <- read_csv(here::here("data_raw", "wctri_catch.csv"), col_types = cols(
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
)) 

wctri_haul <- read_csv(here::here("data_raw", "wctri_haul.csv"), col_types = 
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
                         )) 

wctri_species <- read_csv(here::here("data_raw", "wctri_species.csv"), col_types = cols(
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
    area_swept = 100*(DISTANCE_FISHED*(NET_WIDTH/1000)), #area swept in ha
    numcpue = NUMBER_FISH/area_swept,
    wtcpue = WEIGHT/area_swept
  )

# Calculate stratum area where needed (use convex hull approach)
wctri_strats <- wctri %>% 
  group_by(stratum) %>% 
  summarise(stratumarea = calcarea(START_LONGITUDE, START_LATITUDE))

wctri <- left_join(wctri, wctri_strats, by = "stratum")
wctri <- wctri %>%
  mutate(
    # add species names for two rockfish complexes
    SPECIES_NAME = ifelse(grepl("rougheye and blackspotted rockfish unid.", COMMON_NAME), "Sebastes melanostictus and S. aleutianus", SPECIES_NAME),
    SPECIES_NAME = ifelse(grepl("dusky and dark rockfishes unid.", COMMON_NAME), "Sebastes variabilis and S. ciliatus", SPECIES_NAME)) 


wctri <- wctri %>% 
  rename(
    datetime=START_TIME,
    lat = START_LATITUDE, 
    lon = START_LONGITUDE,
    sst = SURFACE_TEMPERATURE,
    depth = BOTTOM_DEPTH, 
    spp = SPECIES_NAME,
    vesselID = VESSEL,
    haul_dist=DISTANCE_FISHED,
    haul_dur=DURATION,
    num=NUMBER_FISH,
    wgt=WEIGHT
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
         spp = ifelse(grepl("Squalus", spp), 'Squalus suckleyi', spp),
         sbt=NA) %>%
  group_by(haulid, year, datetime, lat, lon, stratum, stratumarea, vesselID, haul_dist, haul_dur, area_swept, sbt, sst, depth, spp) %>% 
  summarise(wtcpue = sumna(wtcpue),
            numcpue=sumna(numcpue),
            num = sumna(num),
            wgt = sumna(wgt)) %>% 
  # add region column
  mutate(region = "West Coast Triennial") %>% 
  select(region, haulid, year, datetime, lat, lon, stratum, stratumarea, vesselID, haul_dist, haul_dur, area_swept, sbt, sst, depth, spp, num, numcpue, wgt, wtcpue) %>% 
  ungroup()

if (HQ_DATA_ONLY == TRUE){
  # look at the graph and make sure decisions to keep or eliminate data make sense
  
  
  p1 <- wctri %>% 
    select(stratum, year) %>% 
    ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
    geom_jitter()
  
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
    geom_jitter()
  
  p4 <- wctri_fltr %>%
    select(lat, lon) %>% 
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()
  
  if (HQ_PLOTS == TRUE){
    temp <- grid.arrange(p1, p2, p3, p4, nrow = 2)
    ggsave(plot = temp, filename = here::here("plots", "wctri_hq_dat_removed.png"))
    rm(temp)
  }
  rm(test, test2, p1, p2, p3, p4)
}

rm(wctri_catch, wctri_haul, wctri_species, wctri_strats)

#--------------------------------------------------------------------------------------#
# Compile WCANN ===========================================================
print("Compile WCANN")
wcann_catch <- read_csv(here::here("data_raw", "wcann_catch.csv"), col_types = cols(
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
)) 

wcann_haul <- read_csv(here::here("data_raw", "wcann_haul.csv"), col_types = cols(
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
))


wcann <- left_join(wcann_haul, wcann_catch, by = c(
  "trawl_id", "year", "date_yyyymmdd", "station_code",
  "performance","program","project","sampling_end_hhmmss",
  "sampling_start_hhmmss","tow_end_timestamp","tow_start_timestamp",
  "vessel","vessel_id","year_stn_invalid")) %>%
  filter(performance !='Unsatisfactory')

wcann <- wcann %>% 
  mutate(
    # create haulid
    haulid = trawl_id,
    # adjust for tow area # kg per hectare (10,000 m2)	
    wtcpue = total_catch_wt_kg/area_swept_ha_der,
    numcpue = total_catch_numbers/area_swept_ha_der
  )
#add stratum based on lat and depth intervals
wcann$stratum<-ifelse(wcann$latitude_dd <=35.5 & wcann$depth_m<=183, "35.5-183", 
                      ifelse(wcann$latitude_dd <= 35.5 & wcann$depth_m <= 549, "35.5-549",
                             ifelse(wcann$latitude_dd <= 35.5 & wcann$depth_m <= 1280, "35.5-1280",
                                    ifelse(wcann$latitude_dd <= 35.5 & wcann$depth_m > 1280, "35.5-2000",
                                           ifelse(wcann$latitude_dd <=40.5 & wcann$depth_m<=183, "40.5-183", 
                                                  ifelse(wcann$latitude_dd <= 40.5 & wcann$depth_m <= 549, "40.5-549",
                                                         ifelse(wcann$latitude_dd <= 40.5 & wcann$depth_m <= 1280, "40.5-1280",
                                                                ifelse(wcann$latitude_dd <= 40.5 & wcann$depth_m > 1280, "40.5-2000",
                                                                       ifelse(wcann$latitude_dd <=43.5 & wcann$depth_m<=183, "43.5-183", 
                                                                              ifelse(wcann$latitude_dd <= 43.5 & wcann$depth_m <= 549, "43.5-549",
                                                                                     ifelse(wcann$latitude_dd <= 43.5 & wcann$depth_m <= 1280, "43.5-1280",
                                                                                            ifelse(wcann$latitude_dd <= 43.5 & wcann$depth_m > 1280, "43.5-2000",
                                                                                                   # ifelse(wcann$latitude_dd <=47.5 & wcann$depth_m<=183, "47.5-183", 
                                                                                                   #        ifelse(wcann$latitude_dd <= 47.5 & wcann$depth_m <= 549, "47.5-549",
                                                                                                   #               ifelse(wcann$latitude_dd <= 47.5 & wcann$depth_m <= 1280, "47.5-1280",
                                                                                                   #                      ifelse(wcann$latitude_dd <= 47.5 & wcann$depth_m > 1280, "47.5-2000",
                                                                                                   ifelse(wcann$latitude_dd <=50.5 & wcann$depth_m<=183, "50.5-183", 
                                                                                                          ifelse(wcann$latitude_dd <= 50.5 & wcann$depth_m <= 549, "50.5-549",
                                                                                                                 ifelse(wcann$latitude_dd <= 50.5 & wcann$depth_m <= 1280, "50.5-1280",
                                                                                                                        ifelse(wcann$latitude_dd <= 50.5 & wcann$depth_m > 1280, "50.5-2000",NA))))))))))))))))
wcann_strats <- wcann %>%
  filter(!is.na(wtcpue)) %>% 
  group_by(stratum) %>% 
  summarise(stratumarea = calcarea(longitude_dd, latitude_dd), na.rm = T)


wcann <- left_join(wcann, wcann_strats, by = "stratum")

wcann <- wcann %>% 
  rename(lat = latitude_dd, 
         lon = longitude_dd,
         depth = depth_m, 
         num = total_catch_numbers,
         wgt = total_catch_wt_kg,
         haul_dur = sample_duration_hr_der,
         area_swept = area_swept_ha_der,
         vesselID = vessel_id,
         datetime = date_yyyymmdd,
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
    spp = ifelse(grepl("Poromitra", spp), 'Poromitra curilensis', spp),
    sbt=NA,
    sst=NA,
    haul_dist=NA
  ) %>%
  group_by(haulid, year, datetime, lat, lon, stratum, stratumarea, vesselID, haul_dist, haul_dur, area_swept, sbt, sst, depth, spp) %>% 
  summarise(wtcpue = sumna(wtcpue),
            numcpue=sumna(numcpue),
            num = sumna(num),
            wgt = sumna(wgt)) %>% 
  # add region column
  mutate(region = "West Coast Annual") %>% 
  select(region, haulid, year, datetime, lat, lon, stratum, stratumarea, vesselID, haul_dist, haul_dur, area_swept, sbt, sst, depth, spp, num, numcpue, wgt, wtcpue) %>% 
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
    filter(count>=19)
  
  # how many rows will be lost if only stratum trawled ever year are kept?
  test2 <- wcann %>% 
    filter(stratum %in% test$stratum)
  nrow(wcann) - nrow(test2)
  # percent that will be lost
  print((nrow(wcann) - nrow(test2))/nrow(wcann))
  # 23% of rows are removed
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
    ggsave(plot = temp, filename = here::here("plots", "wcann_hq_dat_removed.png"))
    rm(temp)
  }
  rm(p1, p2)
}

# cleanup
rm(wcann_catch, wcann_haul, wcann_strats)

#--------------------------------------------------------------------------------------#
# Compile GMEX ===========================================================
print("Compile GMEX")

gmex_station_raw <- read_lines(here::here("data_raw", "gmex_STAREC.csv"))
# remove oddly quoted characters
# #gmex_station_clean <- str_replace_all(gmex_station_raw, "\\\\\\\"", "\\\"\\\"")
gmex_station_clean <- str_replace_all(gmex_station_raw, "\\\\\"", "")
write_lines(gmex_station_clean, file = "gmex_station_raw.txt")

gmex_station <- read_csv(file = "gmex_station_raw.txt", 
                         col_types = cols(.default = col_character())) %>% 
  #output of new names...49 means The message is telling you that some of 
  #the columns have no names and it's giving them one
  select('STATIONID', 'CRUISEID', 'CRUISE_NO', 'P_STA_NO', 'TIME_ZN',
         'TIME_MIL', 'S_LATD', 'S_LATM', 'S_LOND', 'S_LONM', 'E_LATD',
         'E_LATM', 'E_LOND', 'E_LONM', 'STAT_ZONE', 'DEPTH_SSTA', 'MO_DAY_YR',
         'VESSEL_SPD', 'COMSTAT','TEMP_SSURF','TEMP_BOT')

#delete this file we temporarily made
file.remove("gmex_station_raw.txt")

problems <- problems(gmex_station) %>% 
  filter(!is.na(col))

stopifnot(nrow(problems) == 0)

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
  MO_DAY_YR = col_character(),
  VESSEL_SPD = col_double(),
  COMSTAT = col_character()
))


gmex_tow <-read_csv(here::here("data_raw", "gmex_INVREC.csv"), col_types = cols(
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
  COMBIO = col_character()
))

gmex_tow <- gmex_tow %>%
  select('STATIONID', 'CRUISE_NO', 'P_STA_NO', 'INVRECID', 'GEAR_SIZE', 'GEAR_TYPE', 'MESH_SIZE', 'MIN_FISH', 'OP') %>%
  filter(GEAR_TYPE=='ST')

problems <- problems(gmex_tow) %>% 
  filter(!is.na(col)) 
#stopifnot(nrow(problems) == 2)
# 2 problems are that there are weird delimiters in the note column COMBIO, ignoring for now.

gmex_spp <-read_csv(here::here("data_raw","gmex_NEWBIOCODESBIG.csv"), col_types = cols(
  Key1 = col_integer(),
  TAXONOMIC = col_character(),
  CODE = col_integer(),
  TAXONSIZECODE = col_character(),
  isactive = col_integer(),
  common_name = col_character(),
  tsn = col_integer(),
  tsn_accepted = col_integer()
)) %>% 
  select(-tsn_accepted)

# problems should be 0 obs
problems <- problems(gmex_spp) %>% 
  filter(!is.na(col))
stopifnot(nrow(problems) == 0)

gmex_cruise <-read_csv(here::here("data_raw", "gmex_CRUISES.csv"), col_types = cols(.default = col_character())) %>% 
  select(CRUISEID, VESSEL, TITLE)

# problems should be 0 obs
problems <- problems(gmex_cruise) %>% 
  filter(!is.na(col))
stopifnot(nrow(problems) == 0)
gmex_cruise <- type_convert(gmex_cruise, col_types = cols(CRUISEID = col_integer(), VESSEL = col_integer(), TITLE = col_character()))

gmex_bio <-read_csv(here::here("data_raw", "gmex_BGSREC.csv"), col_types = cols(.default = col_character())) %>% 
  select('CRUISEID', 'STATIONID', 'VESSEL', 'CRUISE_NO', 'P_STA_NO',
         'GENUS_BGS','CNT','CNTEXP', 'SPEC_BGS', 'BGSCODE', 'BIO_BGS', 'SELECT_BGS') %>%
  # trim out young of year records (only useful for count data) and those with UNKNOWN species
  filter(BGSCODE != "T" | is.na(BGSCODE),
         GENUS_BGS != "UNKNOWN" | is.na(GENUS_BGS))  %>%
  # remove the few rows that are still duplicates
  distinct()

# problems should be 0 obs
problems <- problems(gmex_bio) %>% 
  filter(!is.na(col))
stopifnot(nrow(problems) == 0)

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

# make two combined records where 2 different species share the same species code
newspp <- tibble(
  Key1 = c(503,5770), 
  TAXONOMIC = c('ANTHIAS TENUIS AND WOODSI', 'MOLLUSCA AND UNID.OTHER #01'), 
  CODE = c(170026003, 300000000), 
  TAXONSIZECODE = NA, 
  isactive = -1, 
  common_name = c('threadnose and swallowtail bass', 'molluscs or unknown'), 
  tsn = NA) 

# remove the duplicates that were just combined  
gmex_spp <- gmex_spp %>% 
  distinct(CODE, .keep_all = T)
# add the combined records on to the end. trim out extra columns from gmexspp
gmex_spp <- rbind(gmex_spp, newspp) %>% 
  select(CODE, TAXONOMIC) %>% 
  rename(BIO_BGS = CODE)

# merge tow information with catch data, but only for shrimp trawl tows (ST)
gmex <- left_join(gmex_bio, gmex_tow, by = c("STATIONID", "CRUISE_NO", "P_STA_NO")) %>% 
  # add station location and related data
  left_join(gmex_station, by = c("CRUISEID", "STATIONID", "CRUISE_NO", "P_STA_NO")) %>% 
  # add scientific name
  left_join(gmex_spp, by = "BIO_BGS") %>% 
  # add cruise title
  left_join(gmex_cruise, by = c("CRUISEID", "VESSEL"))

gmex <- gmex %>% 
  # Trim to high quality SEAMAP summer trawls, based off the subset used by Jeff Rester's GS_TRAWL_05232011.sas
  filter(grepl("Summer", TITLE) & 
           GEAR_SIZE == 40 & 
           MESH_SIZE == 1.63 &
           # OP has no letter value
           !grepl("[A-Z]", OP)) %>% 
  mutate(
    # Create a unique haulid
    haulid = paste(formatC(VESSEL, width=3, flag=0), formatC(CRUISE_NO, width=3, flag=0), formatC(P_STA_NO, width=5, flag=0, format='d'), sep='-'), 
    # Extract year where needed
    year = year(MO_DAY_YR),
    # Calculate decimal lat and lon, depth in m, where needed
    S_LATD = ifelse(S_LATD == 0, NA, S_LATD), 
    S_LOND = ifelse(S_LOND == 0, NA, S_LOND), 
    E_LATD = ifelse(E_LATD == 0, NA, E_LATD), 
    E_LOND = ifelse(E_LOND == 0, NA, E_LOND),
    lat = rowMeans(cbind(S_LATD + S_LATM/60, E_LATD + E_LATM/60), na.rm=T), 
    lon = -rowMeans(cbind(S_LOND + S_LONM/60, E_LOND + E_LONM/60), na.rm=T), 
    # Add "strata" (define by STAT_ZONE and depth bands)
    # degree bins, # degree bins, # 100 m bins
    #stratum = paste(STAT_ZONE, floor(depth/100)*100 + 50, sep= "-")
  )

#add stratum code defined by STAT_ZONE and depth bands (note depth in recorded as m, and depth bands based on 0-20 fathoms
# and 21-60 fathoms))
gmex$depth_zone<-ifelse(gmex$DEPTH_SSTA<=36.576, "20", 
                        ifelse(gmex$DEPTH_SSTA>36.576, "60", NA))
gmex<-gmex %>%
  mutate(stratum = paste(STAT_ZONE, depth_zone, sep= "-"))
# fix speed
# Trim out or fix speed and duration records
# trim out tows of 0, >60, or unknown minutes
gmex <- gmex %>% 
  filter(MIN_FISH <= 60 & MIN_FISH > 0 & !is.na(MIN_FISH)) %>% 
  # fix typo according to Jeff Rester: 30 = 3	
  mutate(VESSEL_SPD = ifelse(VESSEL_SPD == 30, 3, VESSEL_SPD)) %>% 
  # trim out vessel speeds 0, unknown, or >5 (need vessel speed to calculate area trawled)
  filter(VESSEL_SPD <= 5 & VESSEL_SPD > 0  & !is.na(VESSEL_SPD))

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
  filter(!haulid %in% dups$haulid & !grepl("PORT", COMSTAT))

gmex <- gmex %>% 
  rename(spp = TAXONOMIC,
         depth = DEPTH_SSTA,
         num=CNTEXP,
         wgt=SELECT_BGS,
         sbt = TEMP_BOT,
         sst = TEMP_SSURF,
         datetime=MO_DAY_YR,
         vesselID=VESSEL) %>% 
  # adjust for area towed
  mutate(
    # kg per 10000m2. calc area trawled in ha: knots * 1.8 km/hr/knot * minutes * 1 hr/60 min * width of gear in feet * 0.0003048 km/ft # biomass per standard to
    area_swept = (((VESSEL_SPD *1.852)*(MIN_FISH/60))*(GEAR_SIZE*0.0003048) * 100),
    wtcpue= wgt/area_swept,
    numcpue = num/area_swept,
    haul_dist = (VESSEL_SPD *1.852)*(MIN_FISH/60),
    haul_dur=MIN_FISH/60) %>% 
  # remove non-fish
  filter(
    spp != '' | !is.na(spp),
    # remove unidentified spp
    !spp %in% c('UNID CRUSTA', 'UNID OTHER', 'UNID.FISH', 'CRUSTACEA(INFRAORDER) BRACHYURA', 'MOLLUSCA AND UNID.OTHER #01', 'ALGAE', 'MISCELLANEOUS INVERTEBR', 'OTHER INVERTEBRATES')
  ) %>%
  # adjust spp names
  mutate(
    spp = ifelse(GENUS_BGS == 'PELAGIA' & SPEC_BGS == 'NOCTUL', 'PELAGIA NOCTILUCA', spp),
    BIO_BGS = ifelse(spp == "PELAGIA NOCTILUCA", 618030201, BIO_BGS),
    spp = ifelse(GENUS_BGS == 'MURICAN' & SPEC_BGS == 'FULVEN', 'MURICANTHUS FULVESCENS', spp),
    BIO_BGS = ifelse(spp == "MURICANTHUS FULVESCENS", 308011501, BIO_BGS),
    spp = ifelse(grepl("APLYSIA", spp), "APLYSIA", spp),
    spp = ifelse(grepl("AURELIA", spp), "AURELIA", spp),
    spp = ifelse(grepl("BOTHUS", spp), "BOTHUS", spp),
    spp = ifelse(grepl("CLYPEASTER", spp), "CLYPEASTER", spp),
    spp = ifelse(grepl("CONUS", spp), "CONUS", spp),
    spp = ifelse(grepl("CYNOSCION", spp), "CYNOSCION", spp),
    spp = ifelse(grepl("ECHINASTER", spp), "ECHINASTER", spp),
    spp = ifelse(grepl("OPISTOGNATHUS", spp), "OPISTOGNATHUS", spp),
    spp = ifelse(grepl("OPSANUS", spp), "OPSANUS", spp),
    spp = ifelse(grepl("ROSSIA", spp), "ROSSIA", spp),
    spp = ifelse(grepl("SOLENOCERA", spp), "SOLENOCERA", spp),
    spp = ifelse(grepl("TRACHYPENEUS", spp), "TRACHYPENEUS", spp)
  ) %>%
  group_by(haulid, year, datetime, lat, lon, stratum, stratumarea, vesselID, haul_dist, haul_dur, area_swept, sbt, sst, depth, spp) %>%
  summarise(wtcpue = sumna(wtcpue),
            numcpue=sumna(numcpue),
            num = sumna(num),
            wgt = sumna(wgt)) %>%
  # add region column
  mutate(region = "Gulf of Mexico") %>%
  select(region, haulid, year, datetime, lat, lon, stratum, stratumarea, vesselID, haul_dist, haul_dur, area_swept, sbt, sst, depth, spp, num, numcpue, wgt, wtcpue) %>%
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
    filter(year >= 2008, year !=2022) %>% 
    select(stratum, year) %>% 
    distinct() %>% 
    group_by(stratum) %>% 
    summarise(count = n()) %>%
    filter(count >=12)
  
  # how many rows will be lost if years where all strata sampled (>2008) are kept?
  test2 <- gmex %>% 
    filter(stratum %in% test$stratum)
  nrow(gmex) - nrow(test2)
  # percent that will be lost
  print((nrow(gmex) - nrow(test2))/nrow(gmex))
  # lose % of rows
  
  gmex_fltr <- gmex %>%
    filter(stratum %in% test$stratum) %>%
    filter(year>=2008, year!=2022) 
  
  p3 <- gmex_fltr %>% 
    select(stratum, year) %>% 
    ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
    geom_jitter()
  
  p4 <- gmex_fltr%>%
    select(lat, lon) %>% 
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()
  
  if (HQ_PLOTS == TRUE){
    temp <- grid.arrange(p1, p2, p3, p4, nrow = 2)
    ggsave(plot = temp, filename = here::here("plots", "gmex_hq_dat_removed.png"))
    rm(temp)
  }
  rm(test, test2, p1, p2, p3, p4)
}
rm(gmex_bio, gmex_cruise, gmex_spp, gmex_station, gmex_tow, newspp, problems, gmex_station_raw, gmex_station_clean, gmex_strats, dups)

#--------------------------------------------------------------------------------------#
# Compile Northeast US ===========================================================
print("Compile NEUS")
## 2023 update, NEFSC gave data set already with the conversions done 
#read strata file
neus_strata <- read_csv(here::here("data_raw", "neus_strata.csv"), col_types = cols(.default = col_character())) %>%
  select(stratum, stratum_area) %>% 
  mutate(stratum = as.double(stratum)) %>%
  distinct()

#read in catch file, which includes both spring and fall survey. Need to parse them out
neus_catch <- read.csv("data_raw/NEFSC_BTS_ALLCATCHES.csv", header=T, sep=",")%>%
  filter(!is.na(SCINAME)) %>%
  mutate(SVSPP = as.character(SVSPP)) %>%
  rename(year = EST_YEAR,
         lat = DECDEG_BEGLAT, 
         lon = DECDEG_BEGLON, 
         depth = AVGDEPTH,
         stratum = STRATUM,
         haulid = ID,
         spp = SCINAME,
         wtcpue = CALIB_WT,
         numcpue=CALIB_NUM,
         vesselID=SVVESSEL)  %>%
  mutate(
    haulid= paste(CRUISE6,"0",stratum,"00",TOW, "0000")) %>%
  mutate(stratum = as.double(stratum),
         lat = as.double(lat),
         lon = as.double(lon),
         depth = as.double(depth),
         haulid= as.character(haulid),
         wtcpue = as.double(wtcpue),
         year = as.double(year)) %>%
  mutate(sbt = NA,
         sst= NA,
         haul_dist=NA,
         haul_dur=NA,
         area_swept=NA,
         num=NA,
         wgt=NA,
         datetime=NA)%>%
  select(SEASON, haulid, year, datetime, lat, lon, stratum, vesselID, haul_dist, haul_dur, area_swept, sbt, sst, depth, spp, num, numcpue, wgt, wtcpue)

neus_fall_catch<-neus_catch %>%
  filter(SEASON=="FALL")
neus_spring_catch<-neus_catch %>%
  filter(SEASON=="SPRING")

#NEUS fall
# sum different sexes of same spp together
neus_fall <- neus_fall_catch %>% 
  group_by(haulid, year, datetime, lat, lon, stratum, vesselID, haul_dist, haul_dur, area_swept, sbt, sst, depth, spp)%>%
  summarise(wtcpue = sumna(wtcpue),
            numcpue=sumna(numcpue),
            num = sumna(num),
            wgt = sumna(wgt))
neus_fall <- ungroup(neus_fall)

#join with strata
neus_fall <- left_join(neus_fall, neus_strata, by = "stratum")
neus_fall <- filter(neus_fall, !is.na(stratum_area))
neus_fall <- neus_fall %>%
  rename(stratumarea = stratum_area) %>%
  mutate(stratumarea = as.double(stratumarea)* 3.429904) #convert square nautical miles to square kilometers
neus_fall$region <- "Northeast US Fall"

neus_fall<- neus_fall %>%
  select(region, haulid, year, datetime, lat, lon, stratum, stratumarea, vesselID, haul_dist, haul_dur, area_swept, sbt, sst, depth, spp, num, numcpue, wgt, wtcpue) %>%
  # remove unidentified spp and non-species
  filter(
    !spp %in% c("TRASH SPECIES IN CATCH")) %>%
  filter(
    spp != "" | !is.na(spp), 
    haulid !="197512 0 3290 00 1 0000",
    !grepl("EGG", spp), 
    !grepl("UNIDENTIFIED", spp),
    !grepl("UNKNOWN", spp),
    !grepl("NO FISH BUT GOOD TOW", spp),
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
    summarise(count = n()) %>%
    filter(count >= 47)
  
  # how many rows will be lost if only stratum trawled ever year are kept (47 years)?
  test2 <- neus_fall %>% 
    filter(year != 2017, year > 1973) %>% 
    filter(stratum %in% test$stratum)
  nrow(neus_fall) - nrow(test2)
  # percent that will be lost
  print((nrow(neus_fall) - nrow(test2))/nrow(neus_fall))
  # When bad strata are removed after bad years we only lose 38%
  
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
    ggsave(plot = temp, filename = here::here("plots", "neusF_hq_dat_removed.png"))
    rm(temp)
  }
  rm(test, test2, p1, p2, p3, p4)
}

#NEUS Spring
neus_spring <- neus_spring_catch %>% group_by(haulid, year, datetime, lat, lon, stratum, vesselID, haul_dist, haul_dur, area_swept, sbt, sst, depth, spp)%>%
  summarise(wtcpue = sumna(wtcpue),
            numcpue=sumna(numcpue),
            num = sumna(num),
            wgt = sumna(wgt))
neus_spring<- ungroup(neus_spring)

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
  select(region, haulid, year, datetime, lat, lon, stratum, stratumarea, vesselID, haul_dist, haul_dur, area_swept, sbt, sst, depth, spp, num, numcpue, wgt, wtcpue) %>%
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
    filter(year != 2020,year != 2014, year != 1975, year > 1973) %>%
    filter(stratum %in% test$stratum)
  nrow(neus_spring) - nrow(test2)
  # percent that will be lost
  (nrow(neus_spring) - nrow(test2))/nrow(neus_spring)
  # When bad strata are removed after bad years we only lose 35%
  
  neus_spring_fltr <- neus_spring %>%
    filter(year != 2020,year != 2014, year != 1975, year > 1973) %>% 
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
    ggsave(plot = temp, filename = here::here("plots", "neusS_hq_dat_removed.png"))
    rm(temp)
  }
  rm(test, p1, p2, p3, p4)
}

rm(neus_strata)

#--------------------------------------------------------------------------------------#
# Compile SEUS ===========================================================
print("Compile SEUS")
# turns everything into a character so import as character anyway
seus_catch <- read_csv(here::here("data_raw", "seus_catch.csv"), col_types = cols(.default = col_character())) %>% 
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

seus_haul <- read_csv(here::here("data_raw", "seus_haul.csv"), col_types = cols(.default = col_character())) %>% 
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
seus_strata <- read_csv(here::here("data_raw", "seus_strata.csv"), col_types = cols(
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
  # create season column
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
  mutate(distance_m = geosphere::distHaversine(p1 = start, p2 = end))
seus<-seus %>%
  mutate(
    distance_km = distance_m / 1000.0, 
    distance_mi = distance_m / 1609.344) %>% 
  # calculate effort = mean area swept
  # EFFORT = 0 where the boat didn't move, distance_m = 0
  mutate(EFFORT = (13.5 * distance_m)/10000, ## in hectares
         # Create a unique haulid
         haulid = EVENTNAME, 
         # Extract year where needed
         year = substr(EVENTNAME, 1,4),
         DURATION=DURATION/60) %>% 
  rename(
    stratum = STRATA, 
    datetime=DATE,
    lat = LATITUDESTART, 
    lon = LONGITUDESTART, 
    sbt = TEMPBOTTOM,
    sst = TEMPSURFACE,
    depth = DEPTHSTART, 
    spp = SPECIESSCIENTIFICNAME, 
    stratumarea = STRATAHECTARE,
    haul_dist=distance_km, 
    haul_dur=DURATION,
    area_swept=EFFORT,
    vesselID=VESSELNAME)

seus$year <- as.integer(seus$year)
seus$datetime<-as.character(seus$datetime)
# seus<-seus %>% 
#   select(SEASON, haulid, year, datetime, lat, lon, stratum, stratumarea, vesselID, haul_dist, 
#                   haul_dur, area_swept, sbt, sst, depth, spp, NUMBERTOTAL, SPECIESTOTALWEIGHT)

#In seus there are two 'COLLECTIONNUMBERS' per 'EVENTNAME', with no exceptions; EFFORT is always the same for each COLLECTIONNUMBER
# We sum the two tows in seus
seus <- seus %>% 
  group_by(haulid, SEASON, year, datetime, lat, lon, stratum, stratumarea, vesselID, haul_dist, 
           haul_dur, area_swept, sbt, sst, depth, spp) %>% 
  # adjust spp names (we want to sum over these genuses)
  mutate(
    spp = ifelse(grepl("ANCHOA", spp), "ANCHOA", spp), 
    spp = ifelse(grepl("LIBINIA", spp), "LIBINIA", spp)) %>%
  #now this accounts for both sides of the boat, and merging within specified genuses
  summarise(wgt = sum(SPECIESTOTALWEIGHT),
            num = sum(NUMBERTOTAL)) %>% 
  mutate(wtcpue = wgt/(area_swept*2),
         numcpue = num/(area_swept*2)) ##multiply by 2 because there are two tows, one on each side of the boat.  

seus <- seus %>% 
  # remove non-fish
  filter(
    !spp %in% c('MISCELLANEOUS INVERTEBRATES','XANTHIDAE','MICROPANOPE NUTTINGI','ALGAE','DYSPANOPEUS SAYI', 'PSEUDOMEDAEUS AGASSIZII')
  ) %>% 
  # add temporary region column that will be converted to seasonal
  mutate(region = "Southeast US") %>% 
  select(region, SEASON, haulid, year, datetime, lat, lon, stratum, stratumarea, vesselID, haul_dist, 
         haul_dur, area_swept, sbt, sst, depth, spp, num, numcpue, wgt, wtcpue) %>% 
  ungroup()

#remove infinite wtcpue values (where effort was 0, causes wtcpue to be inf)
seus <- seus[!is.infinite(seus$wtcpue),]

#check for duplicates
count_seus <- seus %>%
  group_by(haulid, spp) %>%
  mutate(count = n())

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
    filter(count >= 29)
  
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
    ggsave(plot = temp, filename = here::here("plots", "seusSPR_hq_dat_removed.png"))
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
  #no need to filter, but rename dataset for consistency
  seusSUMMER_fltr <- seusSUMMER
  p1 <- seusSUMMER_fltr %>% 
    select(stratum, year) %>% 
    ggplot(aes(x = as.factor(stratum), y = as.factor(year))) +
    geom_jitter()
  
  p2 <- seusSUMMER_fltr %>%
    select(lat, lon) %>% 
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()
  
  if (HQ_PLOTS == TRUE){
    temp <- grid.arrange(p1, p2, nrow = 2)
    ggsave(plot = temp, filename = here::here("plots", "seusSUM_hq_dat_removed.png"))
    rm(temp)
  }
  rm(p1, p2)
}
# no missing data

# SEUS fall ====
seusFALL <- seus %>% 
  filter(SEASON == "fall") %>% 
  select(-SEASON) %>% 
  mutate(region = "Southeast US Fall")


# how many rows will be lost if only stratum trawled ever year are kept?
if (HQ_DATA_ONLY == TRUE){
  test <- seusFALL %>%
    filter(year != 2018,  year != 2019) %>%
    select(stratum, year) %>%
    distinct() %>%
    group_by(stratum) %>%
    summarise(count = n()) %>%
    filter(count >= 27)
  
  test2 <- seusFALL %>% 
    filter(year != 2018,  year != 2019) %>%
    filter(stratum %in% test$stratum)
  nrow(seusFALL) - nrow(test2)
  # percent that will be lost
  print((nrow(seusFALL) - nrow(test2))/nrow(seusFALL))
  # 5.1% are removed
  
  p1 <- seusFALL %>% 
    select(stratum, year) %>% 
    ggplot(aes(x = as.factor(stratum), y = as.factor(year))) +
    geom_jitter()
  
  p2 <- seusFALL %>%
    select(lat, lon) %>% 
    ggplot(aes(x = lon, y = lat)) +
    geom_jitter()
  
  seusFALL_fltr <- seusFALL  %>%
    filter(year != 2018,  year != 2019) %>%
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
    ggsave(plot = temp, filename = here::here("plots", "seusFALL_hq_dat_removed.png"))
    rm(temp)
  }
}
#clean up
rm(test, test2, p1, p2, p3, p4)

rm(seus_catch, seus_haul, seus_strata, end, start, meanwt, misswt, biomass, problems, change, seus)

#--------------------------------------------------------------------------------------#
# # COMPILE CANADIAN REGIONS ==================================================
# # Compile Maritimes =========================================================
# spp_files <- as.list(dir(pattern = "_SPP", path = "data_raw", full.names = T))
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
# mission_files <- as.list(dir(pattern = "_MISSION", path = "data_raw", full.names = T))
# mar_missions <- mission_files %>% 
#   purrr::map_dfr(~ readr::read_csv(.x, col_types = cols(
#     .default = col_double(),
#     MISSION = col_character(),
#     VESEL = col_character(),
#     SEASON = col_character()
#   )))
# 
# info_files <- as.list(dir(pattern = "_INF", path = "data_raw", full.names = T))
# mar_info <- info_files %>% 
#   purrr::map_dfr(~ readr::read_csv(.x, col_types = cols(
#     .default = col_double(),
#     MISSION = col_character(),
#     SDATE = col_character(),
#     GEARDESC = col_character(),
#     STRAT = col_character() 
#   )))
# 
# catch_files <- as.list(dir(pattern = "_CATCH", path = "data_raw", full.names = T))
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
#     ggsave(plot = temp, filename = here::here("plots", "mar_hq_dat_removed.png"))
#   }
# }
# 
# 
# # Compile Canadian Pacific ---------------------------------------------------
# print("Compile CPAC")
# 
# #Queen Charlotte Sound
# 
# files <- as.list(dir(pattern = "QCS", path = "data_raw", full.names = T))
# 
# 
# QCS_catch <- read_csv(here::here("data_raw", "QCS_catch.csv"), col_types = cols(
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
# QCS_effort <- read_csv(here::here("data_raw", "QCS_effort.csv"), col_types = 
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
# WCV_catch <- read_csv(here::here("data_raw", "WCV_catch.csv"), col_types = cols(
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
# WCV_effort <- read_csv(here::here("data_raw", "WCV_effort.csv"), col_types = 
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
# WCHG_catch <- read_csv(here::here("data_raw", "WCHG_catch.csv"), col_types = cols(
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
# WCHG_effort <- read_csv(here::here("data_raw", "WCHG_effort.csv"), col_types = 
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
# HS_catch <- read_csv(here::here("data_raw", "HS_catch.csv"), col_types = cols(
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
# HS_effort <- read_csv(here::here("data_raw", "HS_effort.csv"), col_types = 
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
# SOG_catch <- read_csv(here::here("data_raw", "SOG_catch.csv"), col_types = cols(
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
# SOG_effort <- read_csv(here::here("data_raw", "SOG_effort.csv"), col_types = 
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
#     ggsave(plot = temp, filename = here::here("plots", "cpac_hq_dat_removed.png"))
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
# GSLsouth <- read_csv(here::here("data_raw", "GSLsouth.csv"))
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
#     ggsave(plot = temp, filename = here::here("plots", "GSLsouth_hq_dat_removed.png"))
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
# GSLnor_sent <- read.csv(here::here("data_raw", "GSLnorth_sentinel.csv"))
# 
# #GSL North Gadus
# 
# GSLnor_gad <- read.csv(here::here("data_raw", "GSLnorth_gadus.csv"))
# 
# #GSL North Hammond
# 
# GSLnor_ham <- read.csv(here::here("data_raw", "GSLnorth_hammond.csv"))
# 
# #GSL North Needler
# 
# GSLnor_need <- read.csv(here::here("data_raw", "GSLnorth_needler.csv"))
# 
# #GSL North Teleost
# 
# GSLnor_tel <- read.csv(here::here("data_raw", "GSLnorth_teleost.csv"))
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
#     ggsave(plot = temp, filename = here::here("plots", "GSLnorth_hq_dat_removed.png"))
#   }
# }
# 
# rm(GSLnor_gad, GSLnor_ham, GSLnor_need, GSLnor_sent, GSLnor_tel, GSLnor_strats)





#--------------------------------------------------------------------------------------#
#### MERGE DATA FILES AND CHECK SPECIES TAXONOMY ####
#--------------------------------------------------------------------------------------#
#MERGE DATASETS 
# Create Master (unfilterd) Data Set ===========================================================
print("Join into Master Data Set")
dat <- rbind(ai, ebs, gmex, goa, nbs, neus_fall, neus_spring, seusFALL, seusSPRING, seusSUMMER, wcann, wctri) %>% 
  # Remove NA values in wtcpue
  filter(!is.na(wtcpue)) %>%
  # remove any extra white space from around spp names
  mutate(spp = str_squish(spp),
         spp = str_remove_all(spp," spp\\.| sp\\.| spp|"),
         spp = str_to_sentence(str_to_lower(spp)))

# Master "Filtered" dataset
print("Join Master Filtered Data Set")
dat_fltr <- rbind(ai_fltr, ebs_fltr, nbs_fltr, gmex_fltr, goa_fltr, neus_fall_fltr, neus_spring_fltr, seusFALL_fltr, seusSPRING_fltr, seusSUMMER_fltr, wcann_fltr, wctri_fltr) %>% 
  # Remove NA values in wtcpue
  filter(!is.na(wtcpue)) %>%
  # remove any extra white space from around spp names
  mutate(spp = str_squish(spp),
         spp = str_remove_all(spp," spp\\.| sp\\.| spp|"),
         spp = str_to_sentence(str_to_lower(spp)))

#START SPECIES CHECK----------------------------------------------------
#Load in Clean Species Taxon data
tax<-read.csv("tax_clean_9_29_23.csv", sep=",", header=T) %>%
      mutate(survey_name= str_squish(survey_name),
             accepted_name= str_squish(accepted_name),
             common = str_squish(common))
#
# Check if any new species are in survey data sets before proceeding....take the 'dat' file that combines the individual regions but before joined with 'spp_taxonomy' file
dat_spp <- dat %>% 
  select(spp) %>% 
  distinct() %>% 
  mutate(spp_id = 1:nrow(.))

# Anti-join this spp list to the survey_name column from the tax file to see which spp are not represented there
not_in_tax <- anti_join(dat_spp, tax, by = c("spp" = "survey_name")) 
if(nrow(not_in_tax)!=0){
  warning('Potential new names: Check list')
}

#Conduct auto-cleaning of taxa names and compare to previous cleaned file. 
    print("Clean & Compile TAX")
    source("clean_taxa.R")
    
    # Get WoRM's id for sourcing
    wrm <- gnr_datasources() %>% 
      filter(title == "World Register of Marine Species") %>% 
      pull(id)
    
    # Set Survey code
    All_srvy_code <- "All-svry"
    
    clean_auto <- clean_taxa(unique(dat$spp),
                             input_survey = All_srvy_code,
                             save = T, output="add", fishbase=T)
    Flags<-anti_join(clean_auto, full_tax, by=c("taxa")) #28 entries that don't match. But that is ok. If more than 28 nonmatches in future then check-spp list
    if(nrow(Flags)!=28){
      warning('Potential new names: Check Flags list')
    }
#END SPECIES CHECK ---------------------------------------------------
    
#--------------------------------------------------------------------------------------#
#### INTEGRATE CLEAN TAXA into SURVEY data ####
#--------------------------------------------------------------------------------------#
#Full unfiltered dataset
dat <- left_join(dat, tax, by = c("spp" = "survey_name")) %>% 
  rename(survey_name=spp) %>%
      filter(grepl("Species", rank),
             !grepl("Caretta caretta", accepted_name),
             !grepl("Sagmatias obliquidens", accepted_name),
             !grepl("Puffinus gravis", accepted_name),
             !grepl("Phaeophyceae", class),
             !grepl("Florideophyceae", class),
             !grepl("Ulvophyceae", class)) %>%
      distinct()
dat<-dat %>%
  rename(spp=accepted_name)

#check for errors in name matching
if(sum(dat$spp == 'NA') > 0 | sum(is.na(dat$spp)) > 0){
  warning('>>create_master_table(): Did not match on some taxon [Variable: `tax`] names.')
}

# #if get warning, check for which spp have NA for name and common if check above fails
spp_na<-dat %>%
  filter(is.na(dat$accepted_name) & is.na(dat$common)) %>%
  select(c("region", "survey_name", "accepted_name", "common")) %>% 
  distinct()


if(isTRUE(REMOVE_REGION_DATASETS)) {
  rm(ai, ebs, gmex, goa, neus_fall, neus_spring, seusFALL, seusSPRING, seusSUMMER, wcann, wctri, tax)
}

if(isTRUE(WRITE_MASTER_DAT)){
  if(isTRUE(PREFER_RDATA)){
    saveRDS(dat, file = here("data_clean", "all-regions-full.rds"))
  }else{
    write_csv(dat, file =here("data_clean", "all-regions-full.csv"))
  }
}


# "Filtered" dataset
dat_fltr <- left_join(dat_fltr, tax, by = c("spp" = "survey_name")) %>% 
  rename(survey_name=spp,
         spp=accepted_name) %>%
  filter(grepl("Species", rank),
         !grepl("Caretta caretta", spp),
         !grepl("Sagmatias obliquidens", spp),
         !grepl("Puffinus gravis", spp),
         !grepl("Phaeophyceae", class),
         !grepl("Florideophyceae", class),
         !grepl("Ulvophyceae", class)) %>%
  distinct()

#check for errors in name matching
if(sum(dat_fltr$spp == 'NA') > 0 | sum(is.na(dat_fltr$spp)) > 0){
  warning('>>create_master_table(): Did not match on some taxon [Variable: `tax`] names.')
}
#if get warning, check for which spp have NA for name and common if check above fails
spp_na<-dat_fltr %>%
  filter(is.na(dat_fltr$spp) & is.na(dat_fltr$common))
# rm(spp_na)

if(isTRUE(REMOVE_REGION_DATASETS)) {
  rm(ai_fltr, ebs_fltr, gmex_fltr, goa_fltr, neus_fall_fltr, neus_spring_fltr, seusFALL_fltr, seusSPRING_fltr, seusSUMMER_fltr, wcann_fltr, wctri_fltr, tax)
}

if(isTRUE(WRITE_MASTER_DAT)){
  if(isTRUE(PREFER_RDATA)){
    saveRDS(dat_fltr, file = here("data_clean", "all-regions-full-fltr_3_17_23.rds"))
  }else{
    write_csv(dat_fltr,file=here("data_clean", "all-regions-full-fltr_3_17_23.csv"))
  }
}

#--------------------------------------------------------------------------------------#
#### TRIM SPECIES IN FILTERED DATASET TO PERSISTENT SPECIES ####
#--------------------------------------------------------------------------------------#
print("Trim species")

## FILTERED DATA
# Find a standard set of species (present at least 3/4 of the years of the filtered data in a region)
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
spplist <- presyrsum %>% 
  filter(presyr >= (maxyrs * 3/4)) %>% 
  select(region, spp, common)

spp_addin<-read.csv("Add_managed_spp.csv",header=T, sep=",")
spplist<-rbind(spplist, spp_addin) 

# Trim dat_fltr to these species (for a given region, spp pair in spplist, in dat_fltr, keep only rows that match that region, spp pairing)
trimmed_dat_fltr <- dat_fltr %>% 
  filter(paste(region, spp) %in% paste(spplist$region, spplist$spp))

#add an EBS+NBS combined region =========================
#select years from compiled EBS that match the NBS survey years
years<-c(2010, 2017, 2019, 2021, 2022)
enbs_trimmed<-trimmed_dat_fltr %>% filter(region %in% c("Eastern Bering Sea", "Northern Bering Sea"),
                                          year %in% years) %>%
  mutate(region="Bering Sea Combined")

p1 <- enbs_trimmed %>% 
  select(stratum, year) %>% 
  ggplot(aes(x = as.factor(stratum), y = as.factor(year)))   +
  geom_jitter()

p2 <- enbs_trimmed %>%
  select(lat, lon) %>% 
  ggplot(aes(x = lon, y = lat)) +
  geom_jitter()

trimmed_dat_fltr<-rbind(trimmed_dat_fltr, enbs_trimmed)

trimmed_dat_fltr_spp<-trimmed_dat_fltr %>% 
  select(spp, common, region) %>%
  distinct()
write.csv(trimmed_dat_fltr_spp, "trimmed_species_region_list.csv")

trimmed_dat_fltr_sppUnique<-trimmed_dat_fltr %>% 
  select(spp, common) %>%
  distinct()
write.csv(trimmed_dat_fltr_sppUnique, "trimmed_Unique_species_list.csv")

if(isTRUE(WRITE_TRIMMED_DAT)){
  if(isTRUE(PREFER_RDATA)){
    saveRDS(trimmed_dat_fltr, file = here("data_clean", "all-regions-trimmed-fltr.rds"))
  }else{
    write_csv(trimmed_dat_fltr, "data_clean/all-regions-trimmed-fltr.csv")
  }
}

# Dat_exploded -  Add 0's ======================================================
print("Dat exploded") 
# these Sys.time() flags are here::here to see how long this section of code takes to run.
Sys.time()
# This takes about 10 minutes
if (DAT_EXPLODED == TRUE){
  dat.exploded <- as.data.table(trimmed_dat_fltr)[,explode0(.SD), by="region"]
  dat_expl_spl <- split(dat.exploded, dat.exploded$region, drop = FALSE)
  
  if(isTRUE(WRITE_DAT_EXPLODED)){
    if(isTRUE(PREFER_RDATA)){
      lapply(dat_expl_spl, function(x) saveRDS(x, here::here("data_clean", paste0('dat_exploded_obis', x$region[1], '.rds')))) 
    }else{
      lapply(dat_expl_spl, function(x) write_csv(x, gzfile(here::here("data_clean", paste0('dat_exploded_obis', x$region[1], '.csv.gz')))))
    }
  }
  
}
Sys.time()

#clean up
rm(dat_expl_spl)



------------------------------------------------------------------------------------------------------------------------------------------
###################### CAN STOP HERE ##########################################
CORE Species -- caught every year of survey =======

print("Core species")

## FILTERED DATA
# Find a standard set of species (present at least 3/4 of the years of the filtered data in a region)
# this result differs from the original code because it does not include any species that have a pres value of 0.  It does, however, include speices for which the common name is NA.
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
# retain all spp present all years of the available years in a survey
spplist_core <- presyrsum %>% 
  filter(presyr >= maxyrs) %>% 
  select(region, spp, common)

# #remove flagged spp (load in Exclude species files )
# setwd("~/transfer/DisMAP project/DisMAP_processing_code/spp_QAQC/exclude_spp")
# ai_ex<-read.csv("ai_excludespp.csv")
# goa_ex<-read.csv("goa_excludespp.csv")
# ebs_ex<-read.csv("ebs_excludespp.csv")
# wctri_ex<-read.csv("wctri_excludespp.csv")
# wcann_ex<-read.csv("wcann_excludespp.csv")
# gmex_ex<-read.csv("gmex_excludespp.csv")
# SEUSs_ex<-read.csv("seusSPRING_excludespp.csv")
# SEUSf_ex<-read.csv("seusFALL_excludespp.csv")
# SUESsu_ex<-read.csv("seusSUMMER_excludespp.csv")
# NEUSs_ex<-read.csv("neusS_excludespp.csv")
# NEUSf_ex<-read.csv("neusF_excludespp.csv")
# addsppex<-read.csv("sppList_add_exclude_12_21_22.csv")
# names(gmex_ex) <- names(ai_ex) 
# 
# excludespp_list<-rbind(ai_ex, goa_ex, ebs_ex, wctri_ex, wcann_ex, 
#                        SEUSs_ex, SEUSf_ex,SUESsu_ex, NEUSs_ex, NEUSf_ex, gmex_ex, addsppex) %>%
#   mutate(test.spp = str_trim(test.spp)) %>%
#   select(test.spp, region, exclude) %>%
#   distinct()
# names(excludespp_list)[1] <- "spp"
# 
# spplist_exclude <- left_join(spplist, excludespp_list, by=c('region','spp'))
# spplist_exclude$exclude <- ifelse(is.na(spplist_exclude$exclude),FALSE,spplist_exclude$exclude)
# 
# spplist_final_Core <- filter(spplist_exclude, exclude == FALSE)
# spplist_remove_1<-filter(spplist_exclude, exclude == TRUE)
# 
# spplist_final_Core<-spplist_final_Core[c(1,2,3)]

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
#number of unique species within each region 
spp_reg_counts<-spplist%>%
  group_by(region)%>%
  summarise(distinct_spp=n_distinct(spp))

#number of unique species CAUGHT ALL YEARS within each region 
spp_reg_counts_Core<-spplist_core%>%
  group_by(region)%>%
  summarise(spp_all_yrs=n_distinct(spp))

num_spp_summary<-left_join(spp_reg_counts, spp_reg_counts_Core, by=c("region"))
write.csv(num_spp_summary, "summary_unique_spp_table.csv")
write.csv(spplist_core, "core_spp_list.csv")

filter_table<-read.csv("filter_table_final.csv", header=T, sep=",")
missing_spp<-anti_join(filter_table, dfuniq, by=c("spp", "FilterSubRegion"="region"))
#filter_table_final<-anti_join(filter_table_3_17, missing_spp, by=c("spp", "common", "FilterSubRegion"))
# write.csv(missing_spp, "missing_NE_spp_3_17_23.csv")
# write.csv(filter_table_final, "filter_table_final.csv")   
miss_filter<-anti_join(dfuniq, filter_table, by=c("spp", "region"="FilterSubRegion"))
write.csv(miss_filter, "add_to_filter.csv")

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