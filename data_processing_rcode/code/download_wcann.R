# WCANN download ----
# info about West Coast api: https://www.nwfsc.noaa.gov/data/api/v1/source
library(readr)
library(jsonlite)
library(here)
library(httr)

wcann_save_loc <- "data"
save_date <- Sys.Date()
catch_file_name <- paste("wcann", "catch.csv", sep="_")
haul_file_name <- paste("wcann", "haul.csv", sep="_")

# url_catch <- "https://www.webapps.nwfsc.noaa.gov/data/api/v1/source/trawl.catch_fact/selection.json?filters=project=Groundfish%20Slope%20and%20Shelf%20Combination%20Survey,date_dim$year>=2003" #updated URL in March 2021
# data_catch <- jsonlite::fromJSON(url_catch)

url_catch <- "https://www.webapps.nwfsc.noaa.gov/data/api/v1/source/trawl.catch_fact/selection.json?filters=project=Groundfish%20Slope%20and%20Shelf%20Combination%20Survey,date_dim$year>=2003"
header_type <- "applcation/json"
response<-GET(url_catch)
text_json <- content(response, type = 'text', encoding = "UTF-8")
jfile <- fromJSON( text_json)
data_catch <- as.data.frame(jfile)

url_haul <- "https://www.webapps.nwfsc.noaa.gov/data/api/v1/source/trawl.operation_haul_fact/selection.json?filters=project=Groundfish%20Slope%20and%20Shelf%20Combination%20Survey,date_dim$year>=2003" #updated URL in March 2021
data_haul <- jsonlite::fromJSON(url_haul)


write.csv(data_catch, here::here(wcann_save_loc, catch_file_name))
write.csv(data_haul, here::here(wcann_save_loc, haul_file_name))
### NOTE: the above urls download files with different columns then if go directly to the FRAM site and click on the CSV next to the table type. This way has more column names, including Temperature 


