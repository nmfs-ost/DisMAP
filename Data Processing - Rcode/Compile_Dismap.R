## ---- DISMAP 5/12/22
### This code has been modified for purposes for developing the data for DisMAP from code orignially 
  # developed by the OceanAdapt team lead by Malin Pinsky at Rutgers University in partnership with NOAA Fisheries 

# This code requires the following versions of packages. These versions are based on the last successful date that the script ran.  This will install these versions on your machine, proceed with caution.  The dates on the following lines can be updated if the script successfully runs with different versions on a subsequent date.
library(devtools)
# install_version("readr", repos = "https://mran.revolutionanalytics.com/snapshot/2019-12-05/") # 1.3.1
# install_version("purrr", repos = "https://mran.revolutionanalytics.com/snapshot/2019-12-05/") # 0.3.3
# install_version("stringr", repos = "https://mran.revolutionanalytics.com/snapshot/2019-12-05/") # 1.4.0
# install_version("forcats", repos = "https://mran.revolutionanalytics.com/snapshot/2019-12-05/") # 0.4.0
# install_version("tidyr", repos = "https://mran.revolutionanalytics.com/snapshot/2019-12-05/") # 1.0.0
# install_version("ggplot2", repos = "https://mran.revolutionanalytics.com/snapshot/2019-12-05/") # 3.2.1
# install_version("dplyr", repos = "https://mran.revolutionanalytics.com/snapshot/2020-07-01/") # 0.8.3 or 1.0.0
# # note: dplyr 0.8.3 (12/5/19) would not install in R v3.5.2 during last test so v1.0.0 (7/1/20) was used
# install_version("tibble", repos = "https://mran.revolutionanalytics.com/snapshot/2020-07-01/") # 2.1.3 or 3.0.1
# # note: used v3.0.1 (7/1/20) during test to match dplyr (instead of v2.1.3 from 12/5/19)
# install_version("lubridate", repos = "https://mran.revolutionanalytics.com/snapshot/2019-12-05/") # 1.7.4
# install_version("PBSmapping", repos = "https://mran.revolutionanalytics.com/snapshot/2019-12-05/") # 2.72.1
# install_version("data.table", repos = "https://mran.revolutionanalytics.com/snapshot/2019-12-05/") # 1.12.6
# install_version("gridExtra", repos = "https://mran.revolutionanalytics.com/snapshot/2019-12-05/") # 2.3
# install_version("questionr", repos = "https://mran.revolutionanalytics.com/snapshot/2019-12-05/") # 0.7.0
# install_version("geosphere", repos = "https://mran.revolutionanalytics.com/snapshot/2019-12-05/") # 1.5-10
# install_version("here", repos = "https://mran.revolutionanalytics.com/snapshot/2019-12-05/") # 0.1

# Load required packages 
 library(lubridate)
 library(PBSmapping) 
 library(gridExtra) 
 library(questionr) 
 library(geosphere)
 library(here)
 library(dplyr)
 library(readr)
 library(purrr)
 library(forcats)
 library(tidyr)
 library(tibble)
 library(ggplot2)
 library(stringr)
 library(data.table) 

# If running from R instead of RStudio, please set the working directory to the folder containing this script before running this script.
# This script is designed to run within the following directory structure:
# Directory contains:
# 1. compile.R script - this script
# 2. data_raw - folder that the raw data will be placed into after running the "Download_x.R" scripts for each region
# 3. spp_QAQC - folder with species taxon and exclusions information 
# 4. Survey Evaluation Plots - folder where plots generated in this scrip to evaluate survey coverage and to aid in decisions to trim the data will be saved 
# 4. data_clean - folder where the cleaned/processed data will be saved to 

# The zip file you downloaded created this directory structure for you.

# a note on species name adjustment #### 
# At some point during certain surveys it was realized that what was believed to be one species was actually a different species or more than one species.  Species have been lumped together as a genus in those instances.

# Answer the following questions using all caps TRUE or FALSE to direct the actions of the script =====================================

# 1. Some strata and years have very little data, should they be removed and saved as fltr data? #DEFAULT: TRUE. 
HQ_DATA_ONLY <- TRUE

# 2. View plots of removed strata for HQ_DATA. #OPTIONAL, DEFAULT:FALSE
# It takes a while to generate these plots.
HQ_PLOTS <- TRUE

# 3. Remove ai,ebs,gmex,goa,neus,seus,wcann,wctri, scot. Keep `dat`. #DEFAULT: FALSE 
REMOVE_REGION_DATASETS <- FALSE

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

# The working directory is assumed to be the "DisMAP - Data Processing-Rcode" directory of this repository.
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

lunique = function(x) length(unique(x)) # number of unique values in a vector

present_every_year <- function(dat, ...){
  presyr <- dat %>% 
    filter(wtcpue > 0) %>% 
    group_by(...) %>% 
    summarise(pres = n())
  return(presyr)
}

num_year_present <- function(presyr, ...){
  presyrsum <- presyr %>% 
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
  # setkey(x, haulid, stratum, year, lat, lon, stratumarea, depth)
  # group the data by these columns
  setorder(x, haulid, stratum, year, lat, lon, stratumarea, depth)
  
  # pull out all of the unique spp
  u.spp <- x[,as.character(unique(spp))]
  # pull out all of the unique common names
  u.cmmn <- x[,common[!duplicated(as.character(spp))]]
  
  # pull out these location related columns and sort by haul_id and year
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


# Compile AI =====================================================
print("Compile AI")

## Special fix
#there is a comment that contains a comma in the 2014-2018 file that causes the delimiters to read incorrectly.  Fix that here::here:
temp <- read_lines(here::here("data_raw", "ai2014_2018.csv"))
# replace the string that causes the problem
temp_fixed <- str_replace_all(temp, "Stone et al., 2011", "Stone et al. 2011")
# read the result in as a csv
temp_csv <- read_csv(temp_fixed)
## End special fix

files <- as.list(dir(pattern = "ai", path = "data_raw", full.names = T))

# exclude the strata file and the raw 2014-2016 data file which has been fixed in temp_csv
files <- files[-c(grep("strata", files),grep("2014", files))]

# combine all of the data files into one table
ai_data <- files %>% 
  # read in all of the csv's in the files list
  purrr::map_dfr(read_csv) %>%
  # add in the data fixed above
  rbind(temp_csv) %>% 
  # remove any data rows that have headers as data rows
  filter(LATITUDE != "LATITUDE", !is.na(LATITUDE)) %>% 
  mutate(stratum = as.integer(STRATUM)) %>% 
  # remove unused columns
  select(-STATION, -DATETIME, -NUMCPUE, -SID, -BOT_TEMP, -SURF_TEMP, -STRATUM) %>% 
  # remove any extra white space from around spp and common names
  mutate(COMMON = str_trim(COMMON), 
         SCIENTIFIC = str_trim(SCIENTIFIC))

# The warning of 13 parsing failures is pointing to a row in the middle of the data set that contains headers instead of the numbers expected, this row is removed by the filter above.

ai_strata <- read_csv(here::here("data_raw", "ai_strata.csv"), col_types = cols(NPFMCArea = col_character(),
                                                                                SubareaDescription = col_character(),
                                                                                StratumCode = col_integer(),
                                                                                DepthIntervalm = col_character(),
                                                                                Areakm2 = col_integer()
))  %>% 
  select(StratumCode, Areakm2) %>% 
  mutate(stratum = StratumCode)


ai <- left_join(ai_data, ai_strata, by = "stratum")

ai<- ai %>%
  mutate(
    # add species names for two rockfish complexes
    SCIENTIFIC = ifelse(grepl("rougheye and blackspotted rockfish unid.", COMMON), "Sebastes melanostictus and S. aleutianus", SCIENTIFIC),
    SCIENTIFIC = ifelse(grepl("dusky and dark rockfishes unid.", COMMON), "Sebastes variabilis and S. ciliatus", SCIENTIFIC)) 

# are there any strata in the data that are not in the strata file?
stopifnot(nrow(filter(ai, is.na(Areakm2))) == 0)

# the following chunk of code reformats and fixes this region's data
ai <- ai %>% 
  mutate(
    # Create a unique haulid
    haulid = paste(formatC(VESSEL, width=3, flag=0), CRUISE, formatC(HAUL, width=3, flag=0), sep='-'), 
    # change -9999 wtcpue to NA
    wtcpue = ifelse(WTCPUE == "-9999", NA, WTCPUE)) %>% 
  # rename columns
  rename(year = YEAR, 
         lat = LATITUDE, 
         lon = LONGITUDE, 
         depth = BOT_DEPTH, 
         spp = SCIENTIFIC,
         stratumarea = Areakm2) %>% 
  # remove rows that are eggs
  filter(spp != "" &
           # remove all spp that contain the word "egg"
           !grepl("egg", spp)) %>% 
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
  select(haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue) %>% 
  type_convert(col_types = cols(
    lat = col_double(),
    lon = col_double(),
    year = col_integer(),
    wtcpue = col_double(),
    spp = col_character(),
    depth = col_integer(),
    haulid = col_character()
  )) %>% 
  group_by(haulid, stratum, stratumarea, year, lat, lon, depth, spp) %>% 
  summarise(wtcpue = sumna(wtcpue)) %>% 
  # Calculate a corrected longitude for Aleutians (all in western hemisphere coordinates)
  ungroup() %>% 
  mutate(lon = ifelse(lon > 0, lon - 360, lon), 
         region = "Aleutian Islands") %>% 
  select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue)

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
  
  # how many rows will be lost if only stratum trawled at least X # of years are kept?
  test2 <- ai %>% 
    filter(stratum %in% test$stratum)
  nrow(ai) - nrow(test2)
  # percent that will be lost
  print((nrow(ai) - nrow(test2))/nrow(ai))
  # 0% of rows are removed
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
    ggsave(plot = temp, filename = here::here("Survey_Evaluation_Plots", "ai_hq_dat_removed.png"))
    rm(temp)
  }
  rm(test, test2, p1, p2, p3, p4)
}# clean up
rm(ai_data, ai_strata, files, temp_fixed, temp_csv)

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
  filter(LATITUDE != "LATITUDE", !is.na(LATITUDE)) %>% 
  mutate(stratum = as.integer(STRATUM))  %>% 
  # remove unused columns
  select(-STATION, -DATETIME, -NUMCPUE, -SID, -BOT_TEMP, -SURF_TEMP, -STRATUM) %>% 
  # remove any extra white space from around spp and common names
  mutate(COMMON = str_trim(COMMON), 
         SCIENTIFIC = str_trim(SCIENTIFIC))

# import the strata data
ebs_strata <- read_csv(here::here("data_raw", "ebs_strata.csv"), col_types = cols(
  SubareaDescription = col_character(),
  StratumCode = col_integer(),
  Areakm2 = col_integer()
)) %>% 
  select(StratumCode, Areakm2) %>% 
  rename(stratum = StratumCode)

ebs <- left_join(ebs_data, ebs_strata, by = "stratum")

# are there any strata in the data that are not in the strata file?
stopifnot(nrow(filter(ebs, is.na(Areakm2))) == 0)

ebs<-ebs%>%
  mutate(
    # add species names for two rockfish complexes
    SCIENTIFIC = ifelse(grepl("rougheye and blackspotted rockfish unid.", COMMON), "Sebastes melanostictus and S. aleutianus", SCIENTIFIC),
    SCIENTIFIC = ifelse(grepl("dusky and dark rockfishes unid.", COMMON), "Sebastes variabilis and S. ciliatus", SCIENTIFIC)) 


ebs <- ebs %>% 
  mutate(
    # Create a unique haulid
    haulid = paste(formatC(VESSEL, width=3, flag=0), CRUISE, formatC(HAUL, width=3, flag=0), sep='-'), 
    # convert -9999 to NA 
    wtcpue = ifelse(WTCPUE == "-9999", NA, WTCPUE)) %>%  
  # rename columns
  rename(year = YEAR, 
         lat = LATITUDE, 
         lon = LONGITUDE, 
         depth = BOT_DEPTH, 
         spp = SCIENTIFIC, 
         stratumarea = Areakm2) %>% 
  # remove eggs
  filter(spp != '' &
           !grepl("egg", spp)) %>% 
  # adjust spp names
  mutate(spp = ifelse(grepl("Atheresthes", spp), "Atheresthes stomias and A. evermanni", spp), 
         spp = ifelse(grepl("Lepidopsetta", spp), "Lepidopsetta sp.", spp),
        # spp = ifelse(grepl("Myoxocephalus", spp), "Myoxocephalus sp.", spp),
         spp = ifelse(grepl("Bathyraja", spp), 'Bathyraja sp.', spp), 
         spp = ifelse(grepl("Hippoglossoides", spp), "Hippoglossoides elassodon and H. robustus", spp),
         spp = ifelse(grepl("Sebastes melanostictus", spp)|grepl("Sebastes aleutianus", spp), "Sebastes melanostictus and S. aleutianus", spp),
         spp = ifelse(grepl("Sebastes variabilis", spp)|grepl("Sebastes ciliatus", spp), "Sebastes variabilis and S. ciliatus", spp)) %>%
  # change from all character to fitting column types
  type_convert(col_types = cols(
    lat = col_double(),
    lon = col_double(),
    STATION = col_character(),
    year = col_integer(),
    DATETIME = col_character(),
    wtcpue = col_double(),
    NUMCPUE = col_double(),
    COMMON = col_character(),
    spp = col_character(),
    SID = col_integer(),
    depth = col_integer(),
    BOT_TEMP = col_double(),
    SURF_TEMP = col_double(),
    VESSEL = col_integer(),
    CRUISE = col_integer(),
    HAUL = col_integer(),
    haulid = col_character()
  ))  %>%  
  group_by(haulid, stratum, stratumarea, year, lat, lon, depth, spp) %>% 
  summarise(wtcpue = sumna(wtcpue)) %>% 
  # add region column
  mutate(region = "Eastern Bering Sea") %>% 
  select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue) %>% 
  ungroup()

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
    group_by(stratum) %>% 
    summarise(count = n())  %>% 
    filter(count >= 36)
  
  # how many rows will be lost if only stratum trawled ever year are kept?
  test2 <- ebs %>% 
    filter(stratum %in% test$stratum)
  nrow(ebs) - nrow(test2)
  # percent that will be lost
  print((nrow(ebs) - nrow(test2))/nrow(ebs))
  # 4.7% of rows are removed
  ebs_fltr <- ebs %>% 
    filter(stratum %in% test$stratum)
  
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
    ggsave(plot = temp, filename = here::here("Survey_Evaluation_Plots", "ebs_hq_dat_removed.png"))
    rm(temp)
  }
  rm(test, test2, p1, p2, p3, p4)
}
# clean up
rm(files, ebs_data, ebs_strata)


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
  filter(LATITUDE != "LATITUDE", !is.na(LATITUDE)) %>% 
  mutate(stratum = as.integer(STRATUM)) %>% 
  # remove unused columns
  select(-STATION, -DATETIME, -NUMCPUE, -SID, -BOT_TEMP, -SURF_TEMP, -STRATUM) %>%
# remove any extra white space from around spp and common names
  mutate(COMMON = str_trim(COMMON), 
       SCIENTIFIC = str_trim(SCIENTIFIC))
# import the strata data
files <- as.list(dir(pattern = "goa_strata", path = "data_raw", full.names = T))

goa_strata <- files %>% 
  # read in all of the csv's in the files list
  purrr::map_dfr(read_csv) %>% 
  select(StratumCode, Areakm2) %>% 
  distinct() %>% 
  rename(stratum = StratumCode)

goa <- left_join(goa_data, goa_strata, by = "stratum")

# are there any strata in the data that are not in the strata file?
stopifnot(nrow(filter(goa, is.na(Areakm2))) == 0)

goa <- goa %>%
  mutate(
    # add species names for two rockfish complexes
    SCIENTIFIC = ifelse(grepl("rougheye and blackspotted rockfish unid.", COMMON), "Sebastes melanostictus and S. aleutianus", SCIENTIFIC),
    SCIENTIFIC = ifelse(grepl("dusky and dark rockfishes unid.", COMMON), "Sebastes variabilis and S. ciliatus", SCIENTIFIC)) 

goa <- goa %>%
  mutate(
    # Create a unique haulid
    haulid = paste(formatC(VESSEL, width=3, flag=0), CRUISE, formatC(HAUL, width=3, flag=0), sep='-'),    
    wtcpue = ifelse(WTCPUE == "-9999", NA, WTCPUE)) %>% 
  rename(year = YEAR, 
         lat = LATITUDE, 
         lon = LONGITUDE, 
         depth = BOT_DEPTH, 
         spp = SCIENTIFIC, 
         stratumarea = Areakm2) %>% 
  # remove non-fish
  filter(
    spp != '' & 
      !grepl("egg", spp)) %>% 
  # adjust spp names
  mutate(
    spp = ifelse(grepl("Lepidopsetta", spp), "Lepidopsetta sp.", spp),
   #spp = ifelse(grepl("Myoxocephalus", spp), "Myoxocephalus sp.", spp),
    spp = ifelse(grepl("Bathyraja", spp) & !grepl("panthera", spp),'Bathyraja sp.', spp), 
    spp = ifelse(grepl("Sebastes melanostictus", spp)|grepl("Sebastes aleutianus", spp), "Sebastes melanostictus and S. aleutianus", spp),
    spp = ifelse(grepl("Sebastes variabilis", spp)|grepl("Sebastes ciliatus", spp), "Sebastes variabilis and S. ciliatus", spp)) %>%
  type_convert(col_types = cols(
    lat = col_double(),
    lon = col_double(),
    STATION = col_character(),
    year = col_integer(),
    DATETIME = col_character(),
    wtcpue = col_double(),
    NUMCPUE = col_double(),
    COMMON = col_character(),
    spp = col_character(),
    SID = col_integer(),
    depth = col_integer(),
    BOT_TEMP = col_double(),
    SURF_TEMP = col_double(),
    VESSEL = col_integer(),
    CRUISE = col_integer(),
    HAUL = col_integer(),
    haulid = col_character()
  ))  %>% 
  group_by(haulid, stratum, stratumarea, year, lat, lon, depth, spp) %>% 
  summarise(wtcpue = sumna(wtcpue)) %>% 
  mutate(region = "Gulf of Alaska") %>% 
  select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, wtcpue) %>% 
  ungroup()

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
  
  # for GOA in 2018, 2001 missed 27 strata and will be removed, stratum 50 is
  # missing from 3 years but will be kept, 410, 420, 430, 440, 450 are missing 
  #from 3 years but will be kept, 510 and higher are missing from 7 or more years
  # of data and will be removed
  test <- goa %>%
    filter(year != 2001) %>% 
    select(stratum, year) %>% 
    distinct() %>% 
    group_by(stratum) %>% 
    summarise(count = n())  %>%
    filter(count >= 14)
  
  # how many rows will be lost if only stratum trawled ever year are kept?
  test2 <- goa %>% 
    filter(stratum %in% test$stratum)
  nrow(goa) - nrow(test2)
  # percent that will be lost
  print ((nrow(goa) - nrow(test2))/nrow(goa))
  # 4% of rows are removed
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
    ggsave(plot = temp, filename = here::here("Survey_Evaluation_Plots", "goa_hq_dat_removed.png"))
    
    rm(temp)
  }
  rm(test, test2, p1, p2, p3, p4)
}
rm(files, goa_data, goa_strata)


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
)) %>% 
  select(CRUISEJOIN, HAULJOIN, VESSEL, CRUISE, HAUL, SPECIES_CODE, WEIGHT)

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
                         )) %>% 
  select(CRUISEJOIN, HAULJOIN, VESSEL, CRUISE, HAUL, HAUL_TYPE, PERFORMANCE, START_TIME, DURATION, DISTANCE_FISHED, NET_WIDTH, STRATUM, START_LATITUDE, END_LATITUDE, START_LONGITUDE, END_LONGITUDE, STATIONID, BOTTOM_DEPTH)

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
    wtcpue = (WEIGHT*10000)/(DISTANCE_FISHED*1000*NET_WIDTH)
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
    svvessel = VESSEL,
    lat = START_LATITUDE, 
    lon = START_LONGITUDE,
    depth = BOTTOM_DEPTH, 
    spp = SPECIES_NAME
  ) %>% 
  filter(
    spp != "" & 
      !grepl("egg", spp)
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
    ggsave(plot = temp, filename = here::here("Survey_Evaluation_Plots", "wctri_hq_dat_removed.png"))
    rm(temp)
  }
  rm(test, test2, p1, p2, p3, p4)
}

rm(wctri_catch, wctri_haul, wctri_species, wctri_strats)

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
)) %>% 
  select("trawl_id","year","longitude_dd","latitude_dd","depth_m","scientific_name","total_catch_wt_kg","cpue_kg_per_ha_der", "partition")

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
)) %>% 
  select("trawl_id","year","longitude_hi_prec_dd","latitude_hi_prec_dd","depth_hi_prec_m","area_swept_ha_der")
# It is ok to get warning message that missing column names filled in: 'X1' [1].

wcann <- left_join(wcann_haul, wcann_catch, by = c("trawl_id", "year"))
wcann <- wcann %>% 
  mutate(
    # create haulid
    haulid = trawl_id,
    # Add "strata" (define by lat, lon and depth bands) where needed # no need to use lon grids on west coast (so narrow)
    stratum = paste(floor(latitude_dd)+0.5, floor(depth_m/100)*100 + 50, sep= "-"), 
    # adjust for tow area # kg per hectare (10,000 m2)	
    wtcpue = total_catch_wt_kg/area_swept_ha_der 
  )

wcann_strats <- wcann %>% 
  filter(!is.na(longitude_dd)) %>% 
  group_by(stratum) %>% 
  summarise(stratumarea = calcarea(longitude_dd, latitude_dd), na.rm = T)

wcann <- left_join(wcann, wcann_strats, by = "stratum")

wcann <- wcann %>% 
  rename(lat = latitude_dd, 
         lon = longitude_dd, 
         depth = depth_m, 
         spp = scientific_name) %>% 
  # remove non-fish
  filter(!grepl("Egg", partition), 
         !grepl("crushed", spp)) %>% 
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
    filter(year != 2019) %>% 
    select(stratum, year) %>% 
    distinct() %>% 
    group_by(stratum) %>% 
    summarise(count = n()) %>%
    filter(count >= 14)
  
  # how many rows will be lost if only stratum trawled ever year are kept?
  test2 <- wcann %>% 
    filter(stratum %in% test$stratum)
  nrow(wcann) - nrow(test2)
  # percent that will be lost
  print((nrow(wcann) - nrow(test2))/nrow(wcann))
  # 23% of rows are removed
  wcann_fltr <- wcann %>% 
    filter(year != 2019)%>% 
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
    ggsave(plot = temp, filename = here::here("Survey_Evaluation_Plots", "wcann_hq_dat_removed.png"))
    rm(temp)
  }
  rm(p1, p2)
}

# cleanup
rm(wcann_catch, wcann_haul, wcann_strats)

# Compile GMEX ===========================================================
print("Compile GMEX")

gmex_station_raw <- read_lines(here::here("data_raw", "gmex_STAREC.csv"))
# remove oddly quoted characters
#gmex_station_clean <- str_replace_all(gmex_station_raw, "\\\\\\\"", "\\\"\\\"")
gmex_station_clean <- str_replace_all(gmex_station_raw, "\\\\\"", "")
#gmex_station_clean <- gsub('\"', "", gmex_station_clean)

gmex_station <- read_csv(gmex_station_clean, col_types = cols(.default = col_character())) %>% 
  select('STATIONID', 'CRUISEID', 'CRUISE_NO', 'P_STA_NO', 'TIME_ZN', 'TIME_MIL', 'S_LATD', 'S_LATM', 'S_LOND', 'S_LONM', 'E_LATD', 'E_LATM', 'E_LOND', 'E_LONM', 'DEPTH_SSTA', 'MO_DAY_YR', 'VESSEL_SPD', 'COMSTAT')

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
  MO_DAY_YR = col_date(format = ""),
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
  COMBIO = col_character(),
  X28 = col_character()
))

gmex_tow <- gmex_tow %>%
  select('STATIONID', 'CRUISE_NO', 'P_STA_NO', 'INVRECID', 'GEAR_SIZE', 'GEAR_TYPE', 'MESH_SIZE', 'MIN_FISH', 'OP') %>%
  filter(GEAR_TYPE=='ST')

problems <- problems(gmex_tow) %>% 
  filter(!is.na(col)) 
stopifnot(nrow(problems) == 2)
# 2 problems are that there are weird delimiters in the note column COMBIO, ignoring for now.

gmex_spp <-read_csv(here::here("data_raw","gmex_NEWBIOCODESBIG.csv"), col_types = cols(
  Key1 = col_integer(),
  TAXONOMIC = col_character(),
  CODE = col_integer(),
  TAXONSIZECODE = col_character(),
  isactive = col_integer(),
  common_name = col_character(),
  tsn = col_integer(),
  tsn_accepted = col_integer(),
  X9 = col_character()
)) %>% 
  select(-X9, -tsn_accepted)

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

gmex_bio <-read_csv(unz(here::here("data_raw", "gmex_BGSREC.csv.zip"), "gmex_BGSREC.csv"), col_types = cols(.default = col_character())) %>% 
  select('CRUISEID', 'STATIONID', 'VESSEL', 'CRUISE_NO', 'P_STA_NO', 'GENUS_BGS', 'SPEC_BGS', 'BGSCODE', 'BIO_BGS', 'SELECT_BGS') %>%
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
    # convert fathoms to meters
    depth = DEPTH_SSTA * 1.8288, 
    # Add "strata" (define by lat, lon and depth bands) where needed
    # degree bins, # degree bins, # 100 m bins
    stratum = paste(floor(lat)+0.5, floor(lon)+0.5, floor(depth/100)*100 + 50, sep= "-")
  )

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
  rename(spp = TAXONOMIC) %>% 
  # adjust for area towed
  mutate(
    # kg per 10000m2. calc area trawled in m2: knots * 1.8 km/hr/knot * 1000 m/km * minutes * 1 hr/60 min * width of gear in feet * 0.3 m/ft # biomass per standard tow
    wtcpue = 10000*SELECT_BGS/(VESSEL_SPD * 1.85200 * 1000 * MIN_FISH / 60 * GEAR_SIZE * 0.3048) 
  ) %>% 
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
    filter(year >= 2008) %>% 
    select(stratum, year) %>% 
    distinct() %>% 
    group_by(stratum) %>% 
    summarise(count = n()) %>%
    filter(count >= 11) 
  
  # how many rows will be lost if years where all strata sampled (>2008) are kept?
  test2 <- gmex %>% 
    filter(stratum %in% test$stratum)
  nrow(gmex) - nrow(test2)
  # percent that will be lost
  print((nrow(gmex) - nrow(test2))/nrow(gmex))
  # lose % of rows
  
  gmex_fltr <- gmex %>%
    filter(stratum %in% test$stratum) %>%
    filter(year >=2008) 
  
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
    ggsave(plot = temp, filename = here::here("Survey_Evaluation_Plots", "gmex_hq_dat_removed.png"))
    rm(temp)
  }
     rm(test, test2, p1, p2, p3, p4)
}
rm(gmex_bio, gmex_cruise, gmex_spp, gmex_station, gmex_tow, newspp, problems, gmex_station_raw, gmex_station_clean, gmex_strats, dups)

# Compile Northeast US ===========================================================
print("Compile NEUS")

#load conversion factors
NEFSC_conv <- read_csv(here::here("data_raw", "NEFSC_conversion_factors.csv"), col_types = "_ddddddd")
NEFSC_conv <- data.table::as.data.table(NEFSC_conv)
#Bigelow >2008 Vessel Conversion
#Use Bigelow conversions for Pisces as well (PC)
#Tables 56-58 from Miller et al. 2010 Biomass estimators
big_fall <- data.table::data.table(svspp = c('012', '022', '024', '027', '028', 
                                            '031', '033', '034', '073', '076', 
                                            '106', '107', '109', '121', '135', 
                                            '136', '141', '143', '145', '149', 
                                            '155', '164', '171', '181', '193', 
                                            '197', '502', '512', '015', '023', '026', 
                                            '032', '072', '074', '077', '078', 
                                            '102', '103', '104', '105', '108', 
                                            '131', '163', '301', '313', '401', 
                                            '503'),
                                  season = c(rep('fall', 47)),
                                  rhoW = c(1.082, 3.661, 6.189, 4.45, 3.626, 1.403, 1.1, 2.12,
                                           1.58, 2.088, 2.086, 3.257, 12.199, 0.868, 0.665, 1.125,
                                           2.827, 1.347, 1.994, 1.535, 1.191, 1.354, 3.259, 0.22,
                                           3.912, 8.062, 1.409, 2.075, 1.21,
                                           2.174, 8.814, 1.95, 4.349, 1.489, 3, 2.405, 1.692,
                                           2.141, 2.151, 2.402, 1.901, 1.808, 2.771, 1.375, 2.479,
                                           3.151, 1.186))

big_spring <- data.table::data.table(svspp = c('012', '022', '024', '027', '028', 
                                            '031', '033', '034', '073', '076', 
                                            '106', '107', '109', '121', '135', 
                                            '136', '141', '143', '145', '149', 
                                            '155', '164', '171', '181', '193', 
                                            '197', '502', '512', '015', '023', 
                                            '026', '032', '072', '074', '077', 
                                            '078', '102', '103', '104', '105', 
                                            '108', '131', '163', '301', '313', 
                                            '401', '503'),
                                  season = c(rep('spring', 47)),
                                  rhoW = c(1.082, 3.661, 6.189, 4.45, 3.626, 1.403, 1.1, 2.12,
                                           1.58, 2.088, 2.086, 3.257, 12.199, 0.868, 0.665, 1.125,
                                           2.827, 1.347, 1.994, 1.535, 1.191, 1.354, 3.259, 0.22,
                                           3.912, 8.062, 1.409, 2.075, 1.166, 3.718, 2.786, 5.394,
                                           4.591, 0.878, 3.712, 3.483, 2.092, 3.066, 3.05, 2.244,
                                           3.069, 2.356, 2.986, 1.272, 3.864, 1.85, 2.861))


#read strata file
neus_strata <- read_csv(here::here("data_raw", "neus_strata.csv"), col_types = cols(.default = col_character())) %>%
  select(stratum, stratum_area) %>% 
  mutate(stratum = as.double(stratum)) %>%
  distinct()
#read and clean spp file
neus_spp_raw <- read_lines(here::here("data_raw", "neus_spp.csv"))
neus_spp_raw <- str_replace_all(neus_spp_raw, 'SQUID, CUTTLEFISH, AND OCTOPOD UNCL', 'Squid/Cuttlefish/Octopod (unclear)')
neus_spp_raw <- str_replace_all(neus_spp_raw, 'SEA STAR, BRITTLE STAR, AND BASKETSTAR UNCL', 'Sea Star/Brittle Star/Basket Star (unclear)')
neus_spp_raw <- str_replace_all(neus_spp_raw, 'MOON SNAIL, SHARK EYE, AND BABY-EAR UNCL', 'Moon Snail/shark eye/baby-ear (unclear)')
neus_spp_raw <- str_replace_all(neus_spp_raw, 'MOON SNAIL, SHARK EYE, AND BABY-EAR UNCL', 'Moon Snail/shark eye/baby-ear (unclear)')
neus_spp_clean <- str_replace_all(neus_spp_raw, 'SHRIMP \\(PINK,BROWN,WHITE\\)', 'Shrimp \\(pink/brown/white\\)')
neus_spp<- read_csv(neus_spp_clean, col_types = cols(.default = col_character()))

rm(neus_spp_clean, neus_spp_raw)
  

#NEUS Fall
neus_catch_raw <- read_lines(here::here("data_raw", "neus_fall_svcat.csv"))
# remove comma
neus_catch_raw <- str_replace_all(neus_catch_raw, 'SQUID, CUTTLEFISH, AND OCTOPOD UNCL', 'Squid/Cuttlefish/Octopod (unclear)')
neus_catch_raw <- str_replace_all(neus_catch_raw, 'SEA STAR, BRITTLE STAR, AND BASKETSTAR UNCL', 'Sea Star/Brittle Star/Basket Star (unclear)')
neus_catch_raw <- str_replace_all(neus_catch_raw, 'MOON SNAIL, SHARK EYE, AND BABY-EAR UNCL', 'Moon Snail/shark eye/baby-ear (unclear)')
neus_catch_raw <- str_replace_all(neus_catch_raw, 'MOON SNAIL, SHARK EYE, AND BABY-EAR UNCL', 'Moon Snail/shark eye/baby-ear (unclear)')
neus_catch_clean <- str_replace_all(neus_catch_raw, 'SHRIMP \\(PINK,BROWN,WHITE\\)', 'Shrimp \\(pink/brown/white\\)')
neus_fall_catch <- read_csv(neus_catch_clean, col_types = cols(.default = col_character())) %>% 
  select('CRUISE6','STRATUM','TOW','STATION','ID','LOGGED_SPECIES_NAME','SVSPP','CATCHSEX','EXPCATCHNUM','EXPCATCHWT')

neus_fall_haul <- read_csv(here::here("data_raw", "neus_fall_svsta.csv"), col_types = cols(.default = col_character())) %>% 
  select("CRUISE6","STRATUM", "ID", "AREA","EST_YEAR","AVGDEPTH", "DECDEG_BEGLAT","DECDEG_BEGLON", "SVVESSEL")
drops <- c("CRUISE6","STRATUM")
neus_fall <- left_join(neus_fall_catch, neus_fall_haul[ , !(names(neus_fall_haul) %in% drops)], by = "ID")
neus_fall <- left_join(neus_fall, neus_spp, by = "SVSPP")

neus_fall <- neus_fall %>%
  rename(year = EST_YEAR,
         lat = DECDEG_BEGLAT, 
         lon = DECDEG_BEGLON, 
         depth = AVGDEPTH,
         stratum = STRATUM,
         haulid = ID,
         spp = SCINAME,
         wtcpue = EXPCATCHWT) 
neus_fall <- neus_fall %>%
  mutate(stratum = as.double(stratum),
         lat = as.double(lat),
         lon = as.double(lon),
         depth = as.double(depth),
         wtcpue = as.double(wtcpue),
         year = as.double(year),
         SVSPP = as.double(SVSPP))


#apply fall conversion factors
setDT(neus_fall)

dcf.spp <- NEFSC_conv[DCF_WT > 0, SVSPP]

#test for changes due to conversion with "before" and "after"
#before <- neus_fall[year < 1985 & SVSPP %in% dcf.spp, .(mean_wtcpue=mean(wtcpue)), by=SVSPP][order(SVSPP)]

for(i in 1:length(dcf.spp)){
  neus_fall[year < 1985 & SVSPP == dcf.spp[i], wtcpue := wtcpue * NEFSC_conv[SVSPP == dcf.spp[i], DCF_WT]]
}

#after <- neus_fall[year < 1985 & SVSPP %in% dcf.spp, .(mean_wtcpue=mean(wtcpue)), by=SVSPP][order(SVSPP)]

#before <- neus_fall[SVVESSEL == 'DE' & SVSPP %in% vcf.spp, .(mean_wtcpue=mean(wtcpue)), by=SVSPP][order(SVSPP)]

vcf.spp <- NEFSC_conv[VCF_WT > 0, SVSPP]
for(i in 1:length(dcf.spp)){
  neus_fall[SVVESSEL == 'DE' & SVSPP == vcf.spp[i], wtcpue := wtcpue* NEFSC_conv[SVSPP == vcf.spp[i], VCF_WT]]
}

#after<- neus_fall[SVVESSEL == 'DE' & SVSPP %in% vcf.spp, .(mean_wtcpue=mean(wtcpue)), by=SVSPP][order(SVSPP)]

spp_fall <- big_fall[season == 'fall', svspp]

#before <- neus_fall[SVVESSEL %in% c('HB', 'PC') & SVSPP %in% spp_fall, .(mean_wtcpue=mean(wtcpue)), by=SVSPP][order(SVSPP)]
for(i in 1:length(big_fall$svspp)){
  neus_fall[SVVESSEL %in% c('HB', 'PC') & SVSPP == spp_fall[i], wtcpue := wtcpue / big_fall[i, rhoW]]
}  

#after <- neus_fall[SVVESSEL %in% c('HB', 'PC')  & SVSPP %in% spp_fall, .(mean_wtcpue=mean(wtcpue)), by=SVSPP][order(SVSPP)]

neus_fall <- as.data.frame(neus_fall)
  
# sum different sexes of same spp together
neus_fall <- neus_fall %>% 
  group_by(year, lat, lon, depth, haulid, CRUISE6, STATION, stratum, spp) %>% 
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
  # remove non-fish
    filter(
      !spp %in% c("TRASH SPECIES IN CATCH")) %>%
    filter(
      spp != "" | !is.na(spp), 
      !grepl("EGG", spp), 
      !grepl("UNIDENTIFIED", spp),
      !grepl("UNKNOWN", spp)) %>%
  # remove any extra white space from around spp names
    mutate(spp = str_trim(spp))

# are there any strata in the data that are not in the strata file?
stopifnot(nrow(filter(neus_fall, is.na(stratumarea))) == 0)

rm(neus_catch_clean, neus_catch_raw, neus_fall_catch, neus_fall_haul)


#NEUS Spring
neus_catch_raw <- read_lines(here::here("data_raw", "neus_spring_svcat.csv"))
# remove comma
neus_catch_raw <- str_replace_all(neus_catch_raw, 'SQUID, CUTTLEFISH, AND OCTOPOD UNCL', 'Squid/Cuttlefish/Octopod (unclear)')
neus_catch_raw <- str_replace_all(neus_catch_raw, 'SEA STAR, BRITTLE STAR, AND BASKETSTAR UNCL', 'Sea Star/Brittle Star/Basket Star (unclear)')
neus_catch_raw <- str_replace_all(neus_catch_raw, 'MOON SNAIL, SHARK EYE, AND BABY-EAR UNCL', 'Moon Snail/shark eye/baby-ear (unclear)')
neus_catch_raw <- str_replace_all(neus_catch_raw, 'MOON SNAIL, SHARK EYE, AND BABY-EAR UNCL', 'Moon Snail/shark eye/baby-ear (unclear)')
neus_catch_clean <- str_replace_all(neus_catch_raw, 'SHRIMP \\(PINK,BROWN,WHITE\\)', 'Shrimp \\(pink/brown/white\\)')
neus_spring_catch <- read_csv(neus_catch_clean, col_types = cols(.default = col_character())) %>% 
  select('CRUISE6','STRATUM','TOW','STATION','ID','LOGGED_SPECIES_NAME','SVSPP','CATCHSEX','EXPCATCHNUM','EXPCATCHWT')
rm(neus_catch_clean, neus_catch_raw)

neus_spring_haul <- read_csv(here::here("data_raw", "neus_spring_svsta.csv"), col_types = cols(.default = col_character())) %>% 
  select("CRUISE6","STRATUM", "ID", "AREA","EST_YEAR","AVGDEPTH", "DECDEG_BEGLAT","DECDEG_BEGLON", "SVVESSEL")
drops <- c("CRUISE6","STRATUM")
neus_spring <- left_join(neus_spring_catch, neus_spring_haul[ , !(names(neus_spring_haul) %in% drops)], by = "ID")
neus_spring <- left_join(neus_spring, neus_spp, by = "SVSPP")


rm(neus_spring_catch, neus_spring_haul)
neus_spring <- neus_spring %>%
  rename(year = EST_YEAR,
         lat = DECDEG_BEGLAT, 
         lon = DECDEG_BEGLON, 
         depth = AVGDEPTH,
         stratum = STRATUM,
         haulid = ID,
         spp = SCINAME,
         wtcpue = EXPCATCHWT) 
neus_spring <- neus_spring %>%
  mutate(stratum = as.double(stratum),
         lat = as.double(lat),
         lon = as.double(lon),
         depth = as.double(depth),
         wtcpue = as.double(wtcpue))


#apply spring conversion factors
setDT(neus_spring)

dcf.spp <- NEFSC_conv[DCF_WT > 0, SVSPP]

for(i in 1:length(dcf.spp)){
  neus_spring[year < 1985 & SVSPP == dcf.spp[i], 
              wtcpue := wtcpue * NEFSC_conv[SVSPP == dcf.spp[i], DCF_WT]]
}

gcf.spp <- NEFSC_conv[GCF_WT > 0, SVSPP]
for(i in 1:length(gcf.spp)){
  neus_spring[year > 1972 & year < 1982 & SVSPP == gcf.spp[i],
              wtcpue := wtcpue / NEFSC_conv[SVSPP == gcf.spp[i], GCF_WT]]
}

vcf.spp <- NEFSC_conv[VCF_WT > 0, SVSPP]
for(i in 1:length(dcf.spp)){
  neus_spring[SVVESSEL == 'DE' & SVSPP == vcf.spp[i], wtcpue := wtcpue* NEFSC_conv[SVSPP == vcf.spp[i], VCF_WT]]
}

spp_spring <- big_spring[season == 'spring', svspp]
#before <- neus_spring[SVVESSEL %in% c('HB', 'PC') & SVSPP %in% spp_spring, .(mean_wtcpue=mean(wtcpue)), by=SVSPP][order(SVSPP)]
for(i in 1:length(big_spring$svspp)){
  neus_spring[SVVESSEL %in% c('HB', 'PC') & SVSPP == spp_spring[i], wtcpue := wtcpue / big_spring[i, rhoW]]
}  

#after <- neus_spring[SVVESSEL %in% c('HB', 'PC')  & SVSPP %in% spp_spring, .(mean_wtcpue=mean(wtcpue)), by=SVSPP][order(SVSPP)]


neus_spring <- as.data.frame(neus_spring)

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
    !grepl("UNKNOWN", spp)) %>%
  # remove any extra white space from around spp names
  mutate(spp = str_trim(spp))

# are there any strata in the data that are not in the strata file?
stopifnot(nrow(filter(neus_fall, is.na(stratumarea))) == 0)

# NEUS Fall ====

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
    filter(year != 2017, year >= 1972) %>% 
    select(stratum, year) %>% 
    distinct() %>% 
    group_by(stratum) %>% 
    summarise(count = n()) %>%
    filter(count >= 45)
  
  # how many rows will be lost if only stratum trawled ever year are kept?
  test2 <- neus_fall %>% 
    filter(year != 2017, year > 1973) %>% 
    filter(stratum %in% test$stratum)
  nrow(neus_fall) - nrow(test2)
  # percent that will be lost
  print((nrow(neus_fall) - nrow(test2))/nrow(neus_fall))
  # 60% is too much, by removing bad years we get rid of 9%, which is not so bad.
  # When bad strata are removed after bad years we only lose 37%
  
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
    ggsave(plot = temp, filename = here::here("Survey_Evaluation_Plots", "neusF_hq_dat_removed.png"))
    rm(temp)
  }
  rm(test, test2, p1, p2, p3, p4)
}
#NEUS Spring ===========
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
    filter(year > 1973) %>% 
    select(stratum, year) %>% 
    distinct() %>% 
    group_by(stratum) %>% 
    summarise(count = n()) %>%
    filter(count >= 45)
  
  # how many rows will be lost if only stratum trawled ever year are kept?
  test2 <- neus_spring %>% 
    filter(stratum %in% test$stratum)
  nrow(neus_spring) - nrow(test2)
  # percent that will be lost
  (nrow(neus_spring) - nrow(test2))/nrow(neus_spring)
  #23%
  
  test <- neus_spring %>% 
    filter(year != 2020,year != 2014, year != 1975, year > 1973) %>%
    select(stratum, year) %>% 
    distinct() %>% 
    group_by(stratum) %>% 
    summarise(count = n()) %>%
    filter(count >= 42)
  
  # how many rows will be lost if only stratum trawled ever year are kept?
  test2 <- neus_spring %>% 
    filter(stratum %in% test$stratum)
  nrow(neus_spring) - nrow(test2)
  # percent that will be lost
  (nrow(neus_spring) - nrow(test2))/nrow(neus_spring)
  # When bad strata are removed after bad years we only lose 20.1%
  
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
    ggsave(plot = temp, filename = here::here("Survey_Evaluation_Plots", "neusS_hq_dat_removed.png"))
    rm(temp)
  }
  rm(test, p1, p2, p3, p4)
}

rm(neus_spp, neus_strata, big_fall, big_spring, NEFSC_conv)

# Compile SEUS ===========================================================
print("Compile SEUS")
# turns everything into a character so import as character anyway
seus_catch <- read_csv(unz(here::here("data_raw", "seus_catch.csv.zip"), "seus_catch.csv"), col_types = cols(.default = col_character())) %>% 
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

#In seus there are two 'COLLECTIONNUMBERS' per 'EVENTNAME', with no exceptions; EFFORT is always the same for each COLLECTIONNUMBER
# We sum the two tows in seus
biomass <- seus %>% 
  group_by(haulid, stratum, stratumarea, year, lat, lon, depth, SEASON, spp, EFFORT) %>% 
  summarise(biomass = sum(SPECIESTOTALWEIGHT)) %>% 
  mutate(wtcpue = biomass/(EFFORT*2))

seus <- left_join(seus, biomass, by = c("haulid", "stratum", "stratumarea", "year", "lat", "lon", "depth", "SEASON", "spp", "EFFORT"))
# double check that column numbers haven't changed by more than 2.  

seus <- seus %>% 
  # remove non-fish
  filter(
    !spp %in% c('MISCELLANEOUS INVERTEBRATES','XANTHIDAE','MICROPANOPE NUTTINGI','ALGAE','DYSPANOPEUS SAYI', 'PSEUDOMEDAEUS AGASSIZII')
  ) %>% 
  # adjust spp names
  mutate(
    spp = ifelse(grepl("ANCHOA", spp), "ANCHOA", spp), 
    spp = ifelse(grepl("LIBINIA", spp), "LIBINIA", spp)
  )  %>% 
  group_by(haulid, stratum, stratumarea, year, lat, lon, depth, spp, SEASON) %>% 
  summarise(wtcpue = sumna(wtcpue)) %>% 
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
    ggsave(plot = temp, filename = here::here("Survey_Evaluation_Plots", "seusSPR_hq_dat_removed.png"))
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
    ggsave(plot = temp, filename = here::here("Survey_Evaluation_Plots", "seusSUM_hq_dat_removed.png"))
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
  ggsave(plot = temp, filename = here::here("Survey_Evaluation_Plots", "seusFALL_hq_dat_removed.png"))
  rm(temp)
}
}
#clean up
rm(test, test2, p1, p2, p3, p4)

rm(seus_catch, seus_haul, seus_strata, end, start, meanwt, misswt, biomass, problems, change, seus)


# Compile TAX ===========================================================
print("Compile TAX")
tax <- read_csv(here::here("spp_QAQC", "spptaxonomy_updated_5_12_22.csv"), col_types = cols(
  taxon = col_character(),
  species = col_character(),
  genus = col_character(),
  family = col_character(),
  order = col_character(),
  class = col_character(),
  superclass = col_character(),
  subphylum = col_character(),
  phylum = col_character(),
  kingdom = col_character(),
  name = col_character(),
  common = col_character()
)) %>% 
  select(taxon, name, common)


# if(isTRUE(WRITE_MASTER_DAT)){
#   save(ai, CPAC, ebs, gmex, goa, GSLnor, GSLsouth, mar, neus_fall, neus_spring, seusFALL, seusSPRING, seusSUMMER, tax, wcann, wctri, file = here::here("data_clean", "individual-regions.rds"))
# }
# if(isTRUE(WRITE_MASTER_DAT)){
#   save(ai_fltr, CPAC_fltr, ebs_fltr, gmex_fltr, goa_fltr, GSLnor_fltr, GSLsouth_fltr, mar_fltr, neus_fall_fltr, neus_spring_fltr, seusFALL_fltr, seusSPRING_fltr, seusSUMMER_fltr, tax, wcann_fltr, wctri_fltr, file = here::here("data_clean", "individual-regions-fltr.rds"))
# }

if(isTRUE(WRITE_MASTER_DAT)){
  save(ai, ebs, gmex, goa, neus_fall, neus_spring, seusFALL, seusSPRING, seusSUMMER, tax, wcann, wctri, file = here("data_clean", "individual-regions.rda"))
}
if(isTRUE(WRITE_MASTER_DAT)){
   save(ai_fltr, ebs_fltr, gmex_fltr, goa_fltr, neus_fall_fltr, neus_spring_fltr, seusFALL_fltr, seusSPRING_fltr, seusSUMMER_fltr, tax, wcann_fltr, wctri_fltr, file = here("data_clean", "individual-regions-fltr.rda"))
}


# Master Data Set ===========================================================
print("Join into Master Data Set")

#Full unfiltered data set
dat <- rbind(ai, ebs, gmex, goa, neus_fall, neus_spring, seusFALL, seusSPRING, seusSUMMER, wcann, wctri) %>% 
  # Remove NA values in wtcpue
  filter(!is.na(wtcpue))

# add a case sensitive spp and common name
dat <- left_join(dat, tax, by = c("spp" = "taxon")) %>% 
  select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, name, common, wtcpue) %>% 
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
# 
# if(isTRUE(WRITE_MASTER_DAT)){
#   if(isTRUE(PREFER_RDATA)){
#     saveRDS(dat, file = gzfile(here::here("data_clean", "all-regions-full.rds.gz")))
#   }else{
#     write_csv(dat, gzfile(here::here("data_clean", "all-regions-full.csv.gz")))
#   }
# }

# Master "Filtered" dataset
dat_fltr <- rbind(ai_fltr, ebs_fltr, gmex_fltr, goa_fltr, neus_fall_fltr, neus_spring_fltr, seusFALL_fltr, seusSPRING_fltr, seusSUMMER_fltr, wcann_fltr, wctri_fltr) %>% 
  # Remove NA values in wtcpue
  filter(!is.na(wtcpue))

# add a case sensitive spp and common name
dat_fltr <- left_join(dat_fltr, tax, by = c("spp" = "taxon")) %>% 
  select(region, haulid, year, lat, lon, stratum, stratumarea, depth, spp, name, common, wtcpue) %>%
  distinct()
  # rename(spp = name) %>%
  # filter(!is.na(spp))

#check for errors in name matching
if(sum(dat_fltr$name == 'NA') > 0 | sum(is.na(dat_fltr$name)) > 0){
  warning('>>create_master_table(): Did not match on some taxon [Variable: `tax`] names.')
}
##note still some naming issues, primarily in the Gulf of Mexico!

  # #check for which spp have NA for name and common if check above fails
  spp_na<-dat_fltr %>%
    filter(is.na(dat_fltr$name) & is.na(dat_fltr$common))
  spp_na_list<-unique(c(as.character(spp_na$spp)))
  spp_na<-as.data.frame(spp_na)
  sppNA_unique<-unique(spp_na[c("spp")])
  write.csv(sppNA_unique, "sppNA_unique.csv")

  if(isTRUE(REMOVE_REGION_DATASETS)) {
  rm(ai_fltr, ebs_fltr, gmex_fltr, goa_fltr, neus_fall_fltr, neus_spring_fltr, seusFALL_fltr, seusSPRING_fltr, seusSUMMER_fltr, wcann_fltr, wctri_fltr, tax)
}

if(isTRUE(WRITE_MASTER_DAT)){
  if(isTRUE(PREFER_RDATA)){
    saveRDS(dat_fltr, file = here("data_clean", "all-regions-full-fltr_5_12_22.rds"))
  }else{
    write_csv(dat_fltr,file=here("data_clean", "all-regions-full-fltr_5_12_22.csv"))
  }
}

# if(isTRUE(WRITE_MASTER_DAT)){
#   if(isTRUE(PREFER_RDATA)){
#     saveRDS(dat_fltr, file = gzfile(here::here("data_clean", "all-regions-full-fltr.rds.gz")))
#   }else{
#     write_csv(dat_fltr, gzfile(here::here("data_clean", "all-regions-full-fltr.csv.gz")))
#   }
# }


##FEEL FREE TO ADD, MODIFY, OR DELETE ANYTHING BELOW THIS LINE
# Trim species ===========================================================
print("Trim species")

## FILTERED DATA
# Find a standard set of species (present at least 3/4 of the years of the filtered data in a region)
presyr <- present_every_year(dat_fltr, region, spp, name, common, year) 

# years in which spp was present
presyrsum <- num_year_present(presyr, region, spp, name, common)

# max num years of survey in each region
maxyrs <- max_year_surv(presyrsum, region)

# merge in max years
presyrsum <- left_join(presyrsum, maxyrs, by = "region")
  #write.csv(presyrsum, "presyrsum_5_12_22.csv")

# retain all spp present at least 3/4 of the available years in a survey
spplist <- presyrsum %>% 
  filter(presyr >= (maxyrs * 3/4)) %>% 
  select(region, spp, name, common)
#write.csv(spplist, "spplist_3quaters_years_5_12_22.csv")

#remove flagged spp (load in Exclude species files )
ai_ex<-read.csv(here::here("spp_QAQC", "exclude_spp", "ai_excludespp.csv"))
goa_ex<-read.csv(here::here("spp_QAQC", "exclude_spp","goa_excludespp.csv"))
ebs_ex<-read.csv(here::here("spp_QAQC", "exclude_spp","ebs_excludespp.csv"))
wctri_ex<-read.csv(here::here("spp_QAQC", "exclude_spp","wctri_excludespp.csv"))
wcann_ex<-read.csv(here::here("spp_QAQC", "exclude_spp","wcann_excludespp.csv"))
gmex_ex<-read.csv(here::here("spp_QAQC", "exclude_spp","gmex_excludespp.csv"))
SEUSs_ex<-read.csv(here::here("spp_QAQC", "exclude_spp","seusSPRING_excludespp.csv"))
SEUSf_ex<-read.csv(here::here("spp_QAQC", "exclude_spp","seusFALL_excludespp.csv"))
SUESsu_ex<-read.csv(here::here("spp_QAQC", "exclude_spp","seusSUMMER_excludespp.csv"))
NEUSs_ex<-read.csv(here::here("spp_QAQC", "exclude_spp","neusS_excludespp.csv"))
NEUSf_ex<-read.csv(here::here("spp_QAQC", "exclude_spp","neusF_excludespp.csv"))

names(gmex_ex) <- names(ai_ex) 

excludespp_list<-rbind(ai_ex, goa_ex, ebs_ex, wctri_ex, wcann_ex, 
                       SEUSs_ex, SEUSf_ex,SUESsu_ex, NEUSs_ex, NEUSf_ex, gmex_ex)

names(excludespp_list)[1] <- "spp"
spplist_exclude <- left_join(spplist, excludespp_list, by=c('region','spp'))
spplist_exclude$exclude <- ifelse(is.na(spplist_exclude$exclude),FALSE,spplist_exclude$exclude)

spplist_final <- filter(spplist_exclude, exclude == FALSE)

##here is where the additional species to exclude are added in
addsppex<-read.csv(here::here("spp_QAQC", "exclude_spp", "sppList_add_exclude_3_5_22.csv"))
names(addsppex)[2]<- "name"
spplist_FinalExclude<- left_join(spplist_final, addsppex, by=c('region','name'))
spplist_FinalExclude$remove <- ifelse(is.na(spplist_FinalExclude$remove),FALSE,spplist_FinalExclude$remove)
spplist_finalFinal <- filter(spplist_FinalExclude, remove == FALSE)
  ##what species were removed in the end
  spplist_remove_1<-filter(spplist_exclude, exclude == TRUE)
  sppList_removed<-filter(spplist_FinalExclude, remove == TRUE)
  sppList_removed_full<-rbind(spplist_remove_1, sppList_removed)
  #write.csv(sppList_removed, "sppList_REMOVED_5_12_22.csv")

spplist_finalFinal<-spplist_finalFinal[c(1,3,4)]
names(spplist_finalFinal)[2]<-"name"
names(spplist_finalFinal)[3]<-"common"
#write.csv(spplist_finalFinal, "sppList_Final_5_12_22.csv")

# Trim dat to these species (for a given region, spp pair in spplist_finalFinal, in dat, keep only rows that match that region, spp pairing)
trimmed_dat_fltr <- dat_fltr %>% 
  filter(paste(region, name) %in% paste(spplist_finalFinal$region, spplist_finalFinal$name))

trimmed_dat_fltr<-trimmed_dat_fltr[-c(9)]
names(trimmed_dat_fltr)[9]<-"spp"

if(isTRUE(WRITE_TRIMMED_DAT)){
  if(isTRUE(PREFER_RDATA)){
    saveRDS(trimmed_dat_fltr, file = here("data_clean", "all-regions-trimmed-fltr.rds"))
  }else{
    write_csv(trimmed_dat_fltr, file=here("data_clean", "all-regions-trimmed-fltr.csv.gz"))
  }
}

# are there any spp in trimmed_dat that are not in the taxonomy file?
# test <- anti_join(select(trimmed_dat_fltr, spp, common), spplist_finalFinal, by = "spp") %>% 
#   distinct()

# if test contains more than 0 obs, use the add-spp-to-taxonomy.R script to add new taxa to the spptaxonomy.csv and go back to "Compile Tax".
rm(test)


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
      lapply(dat_expl_spl, function(x) saveRDS(x, here::here("data_clean", paste0('dat_exploded', x$region[1], '.rds')))) 
    }else{
      lapply(dat_expl_spl, function(x) write_csv(x, gzfile(here::here("data_clean", paste0('dat_exploded', x$region[1], '.csv.gz')))))
    }
  }
  
}
Sys.time()

#clean up
rm(dat_expl_spl)

### STOP HERE - at this point the data has been saved in "data_clean" and ready to move to the Python script =========

## The below code is not necessary for DisMAP, but can be used to get a list of the CORE Species -- 
### that are caught every year of survey
# Trim species ===========================================================
print("Trim species")

## FILTERED DATA
# Find a standard set of species (present every year of the filtered data in a region)
presyr <- present_every_year(dat_fltr, region, spp, name, common, year) 

# years in which spp was present
presyrsum <- num_year_present(presyr, region, spp, name, common)

# max num years of survey in each region
maxyrs <- max_year_surv(presyrsum, region)

# merge in max years
presyrsum <- left_join(presyrsum, maxyrs, by = "region")

# retain all spp present all years of the available years in a survey
spplist <- presyrsum %>% 
  filter(presyr >= maxyrs) %>% 
  select(region, spp, name, common)

#remove flagged spp (load in Exclude species files )
ai_ex<-read.csv(here::here("spp_QAQC", "exclude_spp", "ai_excludespp.csv"))
goa_ex<-read.csv(here::here("spp_QAQC", "exclude_spp","goa_excludespp.csv"))
ebs_ex<-read.csv(here::here("spp_QAQC", "exclude_spp","ebs_excludespp.csv"))
wctri_ex<-read.csv(here::here("spp_QAQC", "exclude_spp","wctri_excludespp.csv"))
wcann_ex<-read.csv(here::here("spp_QAQC", "exclude_spp","wcann_excludespp.csv"))
gmex_ex<-read.csv(here::here("spp_QAQC", "exclude_spp","gmex_excludespp.csv"))
SEUSs_ex<-read.csv(here::here("spp_QAQC", "exclude_spp","seusSPRING_excludespp.csv"))
SEUSf_ex<-read.csv(here::here("spp_QAQC", "exclude_spp","seusFALL_excludespp.csv"))
SUESsu_ex<-read.csv(here::here("spp_QAQC", "exclude_spp","seusSUMMER_excludespp.csv"))
NEUSs_ex<-read.csv(here::here("spp_QAQC", "exclude_spp","neusS_excludespp.csv"))
NEUSf_ex<-read.csv(here::here("spp_QAQC", "exclude_spp","neusF_excludespp.csv"))

names(gmex_ex) <- names(ai_ex) 

excludespp_list<-rbind(ai_ex, goa_ex, ebs_ex, wctri_ex, wcann_ex, 
                       SEUSs_ex, SEUSf_ex,SUESsu_ex, NEUSs_ex, NEUSf_ex, gmex_ex)

names(excludespp_list)[1] <- "spp"
spplist_exclude <- left_join(spplist, excludespp_list, by=c('region','spp'))
spplist_exclude$exclude <- ifelse(is.na(spplist_exclude$exclude),FALSE,spplist_exclude$exclude)

spplist_final <- filter(spplist_exclude, exclude == FALSE)
spplist_remove_1<-filter(spplist_exclude, exclude == TRUE)

##here is where the additional species to exclude.... (come up with a better system for this in future)
addsppex<-read.csv(here::here("spp_QAQC", "exclude_spp", "sppList_add_exclude_3_5_22.csv"))
names(addsppex)[2]<- "name"
spplist_FinalExclude<- left_join(spplist_final, addsppex, by=c('region','name'))
spplist_FinalExclude$remove <- ifelse(is.na(spplist_FinalExclude$remove),FALSE,spplist_FinalExclude$remove)
spplist_Core <- filter(spplist_FinalExclude, remove == FALSE)

spplist_Core<-spplist_Core[c(1,3,4)]
names(spplist_Core)[2]<-"name"
names(spplist_Core)[3]<-"common"

# Summary information about # of species in this analysis================
#number of unique species across all regions
dfuniq<-unique(spplist_finalFinal[c("name", "common")])
write.csv(dfuniq, "unique_sppList_5_12_22.csv")

dfuniq_all<-unique(spplist_Core$name)
length(dfuniq_all)
#number fo unique species within each region 
spp_reg_counts<-spplist_finalFinal%>%
  group_by(region)%>%
  summarise(distinct_spp=n_distinct(name))

#number of unique species CAUGHT ALL YEARS within each region 
spp_reg_counts_ALL<-spplist_Core%>%
  group_by(region)%>%
  summarise(spp_all_yrs=n_distinct(name))

num_spp_summary<-left_join(spp_reg_counts, spp_reg_counts_ALL, by=c("region"))
write.csv(num_spp_summary, "summary_unique_spp.csv")
write.csv(spplist_Core, "core_spp_list.csv")

