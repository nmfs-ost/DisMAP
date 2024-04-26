# This function can be used to download the most recent survey data files for the AK regions and 
# put them in the data_raw folder.
# The ai_strata.csv, ebs_strata.csv, and goa_strata.csv do not change year to year, and should be retained 
# between updates (do not delete these files)

# Resources --------------------------------------------------------------------

# - https://www.fisheries.noaa.gov/alaska/science-data/groundfish-assessment-program-bottom-trawl-surveys

# Install libraries ------------------------------------------------------------

PKG <- c(
  # Mapping
  "akgfmaps", # devtools::install_github("sean-rohan-noaa/akgfmaps", build_vignettes = TRUE)
  "sf",
  "janitor",
  "readr", 
  "rmarkdown", 
  "tidyr", 
  "dplyr",
  "googledrive",
  "here",
  "magrittr",
  "stringr", 
  "readxl",
  "RODBC", 
  "googledrive",
  "RCurl" # for ftp connection
)

for (p in PKG) {
  if(!require(p,character.only = TRUE)) {  
    install.packages(p, verbose = FALSE)
    require(p,character.only = TRUE)}
}

# Knowns -----------------------------------------------------------------------

data_source <- "gd" # gd = google drive; oracle; api


### Download data from Oracle --------------------------------------------------
# mostly recording this for posterity, in case I need to use it again for google drive loads! - EHM
if (data_source == "oracle") {
  # Log into Oracle
  
  if (file.exists("Z:/Projects/ConnectToOracle.R")) {
    # This has a specific username and password because I DONT want people to have access to this!
    source("Z:/Projects/ConnectToOracle.R")
  } else {
    # For those without a ConnectToOracle file
    library(rstudioapi)
    library(RODBC)
    channel <- odbcConnect(dsn = "AFSC", 
                           uid = rstudioapi::showPrompt(title = "Username", 
                                                        message = "Oracle Username", default = ""), 
                           pwd = rstudioapi::askForPassword("Enter Password"),
                           believeNRows = FALSE)
  }
  
  # Pull data from GAP_PRODUCTS
  
  locations <- c(
    # "GAP_PRODUCTS.METADATA_COLUMN", # metadata
    # "GAP_PRODUCTS.METADATA_TABLE", # metaddata
    "GAP_PRODUCTS.FOSS_CATCH",
    "GAP_PRODUCTS.FOSS_HAUL",
    "GAP_PRODUCTS.FOSS_SPECIES"#,
    # "GAP_PRODUCTS.FOSS_SURVEY_SPECIES"
  )
  
  print(Sys.Date())
  
  error_loading <- c()
  for (i in 1:length(locations)){
    print(locations[i])
    
    a <- RODBC::sqlQuery(channel, paste0("SELECT * FROM ", locations[i], "; "))
    
    if (is.null(nrow(a))) { # if (sum(grepl(pattern = "SQLExecDirect ", x = a))>1) {
      error_loading <- c(error_loading, locations[i])
    } else {
      write.csv(x = a, 
                here::here("data_processing_rcode/data",
                           paste0(tolower(gsub(pattern = '.', 
                                               replacement = "_", 
                                               x = locations[i], 
                                               fixed = TRUE)),
                                  ".csv")))
    }
    remove(a)
  }
  error_loading
}

### Download data from google drive folder -------------------------------------
googledrive::drive_deauth()
googledrive::drive_auth()
2

if (data_source == "gd") { # if you are loading these files from google drive
  
  dir_googledrive <- "https://drive.google.com/drive/folders/1NcDCxolMf-drd01vy0_NIhqD1lf3r_Ud" # downloaded 4/12/2024
  
  # see what files are in this google drive
  temp <- googledrive::drive_ls(path = googledrive::as_id(dir_googledrive))
  # download each of the 3 files in the folder (catch, haul, and species)
  for (i in 1:nrow(temp)) {
    print(temp$name[i]) # for seeing progress
    googledrive::drive_download(
      file = temp$id[i], 
      path = here::here("data_processing_rcode/data/", temp$name[i]), 
      overwrite = TRUE)    
  }
}

### Download data from FOSS API ------------------------------------------------

# !!!! IN DEV !!! #TOLEDO

# if (data_source == "api") {
# ## New Data download function for getting data from the Fisheries one-stop-shop (FOSS): 
# #the API is broken so instead will need to go to FOSS() and manually download the data for each survey and save to local folder. 
# 
# # install.packages(c("httr", "jsonlite"))
# library(httr)
# library(jsonlite)
# library(dplyr)
# 
# # link to the API
# api_link <- "https://apps-st.fisheries.noaa.gov/ods/foss/afsc_groundfish_survey/"
# 
# 
# #EBS
# res <- httr::GET(
#   url = paste0(api_link, '?q={"srvy":"EBS"}'))
# data <- jsonlite::fromJSON(base::rawToChar(res$content))
# 
# as_tibble(data$items) %>% 
#   mutate_if(is.character, type.convert, as.is = TRUE) %>%
#   head(3) %>%
#   dplyr::mutate(across(where(is.numeric), round, 3)) %>%
#   dplyr::select(year, srvy, stratum, species_code, cpue_kgkm2) %>%
#   flextable::flextable() %>%
#   flextable::fit_to_width(max_width = 6) %>% 
#   flextable::theme_zebra() %>%
#   flextable::colformat_num(x = ., j = c("year", "species_code"), big.mark = "") 
# 
# }
