#' ---
#' title: "Download NEUS"
#' ---
#' Download the spring and fall bottom trawl survey files from 
#' [Fall]
#' (https://inport.nmfs.noaa.gov/inport/item/22560) -- go to the Distribution 1 and 2 links to get the files (note: only seems to work in internet explorer or Edge)
#' [Distribution 1](ftp://ftp.nefsc.noaa.gov/pub/dropoff/PARR/PEMAD/ESB/22560/)
#' [Distribution 2](ftp://ftp.nefsc.noaa.gov/pub/dropoff/PARR/PEMAD/ESB/SVDBS/)
#' 
#' [Spring]
#' (https://inport.nmfs.noaa.gov/inport/item/22561).  
#' [Distribution 1](ftp://ftp.nefsc.noaa.gov/pub/dropoff/PARR/PEMAD/ESB/22561)
#' [Distribution 2](ftp://ftp.nefsc.noaa.gov/pub/dropoff/PARR/PEMAD/ESB/SVDBS) ## this is same as Fall so only need to download one of them

library(here)

## ----neus----------------------------------------------------------------
unzip(here::here("/data_raw/SVDBS_SupportTables.zip"), exdir = here::here("data_raw"))
svdbs <- dir(pattern = "SVDBS", path = "data_raw", full.names = T)
svdbs <- svdbs[-c(grep("STRATA|SPECIES", svdbs))]
file.remove(svdbs)
file.rename(here::here("data_raw", "SVDBS_SVMSTRATA.csv"), here::here("data_raw", "neus_strata.csv"))
file.rename(here::here("data_raw", "SVDBS_SVSPECIES_LIST.csv"), here::here("data_raw", "neus_spp.csv"))

unzip(here("/data_raw/22560_FSCSTables.zip"), exdir = here::here("data_raw"))
unzip("22561_FSCSTables.zip", exdir = here::here("data_raw"))

file.rename(here::here("data_raw","22560_UNION_FSCS_SVSTA.csv"), here::here( "data_raw","neus_fall_svsta.csv"), overwrite = T)
file.rename(here::here( "data_raw","22560_UNION_FSCS_SVCAT.csv"), here::here( "data_raw","neus_fall_svcat.csv"), overwrite = T)

file.rename(here::here( "data_raw","22561_UNION_FSCS_SVSTA.csv"), here::here( "data_raw","neus_spring_svsta.csv"), overwrite = T)
file.rename(here::here( "data_raw","22561_UNION_FSCS_SVCAT.csv"), here::here( "data_raw","neus_spring_svcat.csv"), overwrite = T)

other <- dir(pattern = "FSCS", path = "data_raw", full.names = T)
file.remove(other)