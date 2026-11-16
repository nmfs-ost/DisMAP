# WCANN download ----

# ## Try pulling the data using the nwfscsurvey R package
##note: this pulls a lot of data and takes a long time to process.
# library(nwfscSurvey)
#
# #catch data
# nw_catch<-pull_catch(survey="NWFSC.Combo", years=c(2003,2025))
# write.csv(nw_catch, here::here("data_processing_rcode", "data", "wcann_catch.csv"))
#
# #haul data
# nw_haul<-pull_haul(survey="NWFSC.Combo", years=c(2003,2025))
# write.csv(nw_haul, here::here("data_processing_rcode", "data", "wcann_haul.csv"))


## Downloading the data from the updated FRAM site using API
# info about West Coast api: https://www.nwfsc.noaa.gov/data/api/v1/source
library(readr)
library(jsonlite)
library(here)
library(httr)

# wcann_save_loc <- "data"
save_date <- Sys.Date()
catch_file_name <- paste("wcann", "catch.csv", sep="_")
haul_file_name <- paste("wcann", "haul.csv", sep="_")

#download catch data
url_catch <- "https://www.webapps.nwfsc.noaa.gov/trips/api/v1/source/trawl.catch_fact/selection.json"
header_type <- "applcation/json"
response<-GET(url_catch)
text_json <- content(response, type = 'text', encoding = "UTF-8")
jfile <- fromJSON( text_json)
data_catch <- as.data.frame(jfile)

#download haul data
url_haul <- "https://www.webapps.nwfsc.noaa.gov/trips/api/v1/source/trawl.operation_haul_fact/selection.json"
data_haul <- jsonlite::fromJSON(url_haul)


write.csv(data_catch, here::here("data_processing_rcode", "data", catch_file_name))
write.csv(data_haul, here::here("data_processing_rcode", "data", haul_file_name))
### NOTE: the above urls download files with different columns then if go directly to the FRAM site and click on the CSV next to the table type. This way has more column names, including Temperature

