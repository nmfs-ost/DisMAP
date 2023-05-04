#' ---
#' title: "Download NEUS"
#' ---
#' Download the spring and fall bottom trawl survey files from below links using the WinSCP app and save the zipped file to data_raw folder
#' [Fall]
#' (https://inport.nmfs.noaa.gov/inport/item/22560) -- go to the Distribution 1 and 2 links to get the files (note: only seems to work in internet explorer or Edge)
#' [Distribution 1](ftp://ftp.nefsc.noaa.gov/pub/dropoff/PARR/PEMAD/ESB/22560/)
#' [Distribution 2](ftp://ftp.nefsc.noaa.gov/pub/dropoff/PARR/PEMAD/ESB/SVDBS/)# this doesn't change year to year so don't need to download
#' 
#' [Spring]
#' (https://inport.nmfs.noaa.gov/inport/item/22561).  
#' [Distribution 1](ftp://ftp.nefsc.noaa.gov/pub/dropoff/PARR/PEMAD/ESB/22561)
#' [Distribution 2](ftp://ftp.nefsc.noaa.gov/pub/dropoff/PARR/PEMAD/ESB/SVDBS) ## this is same as Fall so only need to download one of them

## As of 2023 the NEFSC is changing how they host their data, so for now need to reach out directly to: 
## Philip Politis and Catherine Foley to get the data (Jan of each year)

## ----neus----------------------------------------------------------------
unzip(here("data_raw/SVDBS_SupportTables.zip"), exdir = here("data_raw"))
svdbs <- dir(pattern = "SVDBS", path = "data_raw", full.names = T)
svdbs <- svdbs[-c(grep("STRATA|SPECIES|Support", svdbs))]

file.rename(here::here("data_raw", "SVDBS_SVMSTRATA.csv"), here::here("data_raw", "neus_strata.csv"))
file.rename(here::here("data_raw", "SVDBS_SVSPECIES_LIST.csv"), here::here("data_raw", "neus_spp.csv"))


unzip(here("data_raw/22560_NEFSCFallFisheriesIndependentBottomTrawlData.zip"), exdir = here("data_raw"))
unzip(here("data_raw/22561_NEFSCSpringFisheriesIndependentBottomTrawlData.zip"), exdir = here("data_raw"))

#Fall
file.rename(here::here("data_raw","22560_UNION_FSCS_SVSTA.csv"), here::here( "data_raw","neus_fall_svsta.csv"))
file.rename(here::here( "data_raw","22560_UNION_FSCS_SVCAT.csv"), here::here( "data_raw","neus_fall_svcat.csv"))
#Spring
file.rename(here::here( "data_raw","22561_UNION_FSCS_SVSTA.csv"), here::here( "data_raw","neus_spring_svsta.csv"))
file.rename(here::here( "data_raw","22561_UNION_FSCS_SVCAT.csv"), here::here( "data_raw","neus_spring_svcat.csv"))

#Remove unnecessary/duplicate files 
other <- dir(pattern = "FSCS_", path = "data_raw", full.names = T)
file.remove(other)
file.remove(svdbs)

## old code that doesnt work 
# library(here)
# install.packages("RCurl")
# library(RCurl)
# install.packages("curl")
# library(curl)
# ##download the files
# #Fall
# url_fall_1<- "ftp://ftp.nefsc.noaa.gov/pub/dropoff/PARR/PEMAD/ESB/22561"
# url_fall_2<- "ftp://ftp.nefsc.noaa.gov/pub/dropoff/PARR/PEMAD/ESB/SVDBS/"
# 
# fall_filenames_1 <-getURL(url_fall_1, ftp.use.epsv=FALSE, dirlistonly=TRUE)
# fall_filenames_1 <- strsplit(fall_filenames_1, "\r\n")
# fall_filenames_1 <- unlist(fall_filenames_1)
# 
# for (filename in fall_filenames_1) {
#   download.file(paste(url_fall_1, filename, sep=""), paste(getwd(), "/", filename, sep=""))
# }
# 
# options(download.file.method="libcurl", url.method="libcurl")
# source("ftp://ftp.nefsc.noaa.gov/pub/dropoff/PARR/PEMAD/ESB/22561")