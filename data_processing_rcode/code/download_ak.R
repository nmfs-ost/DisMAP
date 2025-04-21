# This function can be used to download the most recent survey data files for the AK regions and
# put them in the data folder.
# The ai_strata.csv, ebs_strata.csv, and goa_strata.csv do not change year to year, and should be retained
# between updates (do not delete these files)

# Resources --------------------------------------------------------------------

# https://www.fisheries.noaa.gov/alaska/science-data/groundfish-assessment-program-bottom-trawl-surveys
# adatapted from https://afsc-gap-products.github.io/gap_products/content/foss-api-r.html#haul-data
# Last updated by April 21, 2025 by Emily Markowitz, AFSC

# Install libraries ------------------------------------------------------------

library(dplyr)
library(httr)
library(jsonlite)
options(scipen = 999)

# Download data from FOSS API --------------------------------------------------

## Download Haul Data ----------------------------------------------------------

dat <- data.frame()
for (i in seq(0, 500000, 10000)){
  # print(i)
  ## query the API link
  res <- httr::GET(url = paste0('https://apps-st.fisheries.noaa.gov/ods/foss/afsc_groundfish_survey_haul/',
                                "?offset=",i,"&limit=10000"))
  ## convert from JSON format
  data <- jsonlite::fromJSON(base::rawToChar(res$content))

  ## if there are no data, stop the loop
  if (is.null(nrow(data$items))) {
    break
  }

  ## bind sub-pull to dat data.frame
  dat <- dplyr::bind_rows(dat,
                          data$items %>%
                            dplyr::select(-links)) # necessary for API accounting, but not part of the dataset)
}
haul <- dat %>%
  dplyr::mutate(date_time = as.POSIXct(date_time,
                                       format = "%Y-%m-%dT%H:%M:%S",
                                       tz = Sys.timezone()))

# mostly for testing, but also nice to have it organized
haul <- haul[order(haul$hauljoin), ]

write.csv(x = haul,
          here::here("data_processing_rcode/data/AK_gap_products_foss_haul.csv"))

## Download Species Data -------------------------------------------------------

res <- httr::GET(url = paste0('https://apps-st.fisheries.noaa.gov/ods/foss/afsc_groundfish_survey_species/',
                              "?offset=0&limit=10000")) # , '&q={"species_code":{"$lt":32000}}'))

## convert from JSON format
data <- jsonlite::fromJSON(base::rawToChar(res$content))
catch_spp <- data$items  %>%
  dplyr::select(-links) # necessary for API accounting, but not part of the dataset

catch_spp <- catch_spp %>%
  dplyr::filter(species_code < 32000)

write.csv(x = catch_spp,
          here::here("data_processing_rcode/data/AK_gap_products_foss_species.csv"))

## Download Catch Data ---------------------------------------------------------
# pull only the data in the catch_spp list (which currently includes species codes below 32000)

dat <- data.frame()
for (ii in 1:nrow(catch_spp)) {
for (i in seq(0, 1000000, 10000)){
  ## find how many iterations it takes to cycle through the data
  print(i)
  ## query the API link
  res <- httr::GET(url = paste0("https://apps-st.fisheries.noaa.gov/ods/foss/afsc_groundfish_survey_catch/",
                                "?offset=",i,"&limit=10000", '&q={"species_code":',catch_spp$species_code[ii],'}')) # '&q={"species_code":{"$lt":32000}}'
  ## convert from JSON format
  data <- jsonlite::fromJSON(base::rawToChar(res$content))

  ## if there are no data, stop the loop
  if (is.null(nrow(data$items))) {
    break
  }

  ## bind sub-pull to dat data.frame
  dat <- dplyr::bind_rows(dat,
                          data$items %>%
                            dplyr::select(-links)) # necessary for API accounting, but not part of the dataset)
}
}
catch <- unique(dat)

############ Testing # As of April 21, 2025

dim(catch)
# 438608      7
summary(catch)
# hauljoin        species_code     cpue_kgkm2        cpue_nokm2          count           weight_kg         taxon_confidence  
# Min.   : -23911   Min.   :    1   Min.   :      0   Min.   :     14   Min.   :    1.0   Min.   :    0.001   Length:438608     
# 1st Qu.: -14310   1st Qu.:10130   1st Qu.:     25   1st Qu.:     64   1st Qu.:    2.0   1st Qu.:    0.872   Class :character  
# Median :  -4750   Median :20510   Median :    171   Median :    243   Median :    9.0   Median :    5.900   Mode  :character  
# Mean   : 284057   Mean   :16337   Mean   :   2236   Mean   :   4437   Mean   :  154.4   Mean   :   71.638                     
# 3rd Qu.: 802455   3rd Qu.:21740   3rd Qu.:    897   3rd Qu.:   1307   3rd Qu.:   46.0   3rd Qu.:   31.320                     
# Max.   :1225635   Max.   :30600   Max.   :3226235   Max.   :4481702   Max.   :47118.0   Max.   :18187.700                     
#                                   NA's   :943       NA's   :943                 

### Download Catch Data - Alt --------------------------------------------------
# pull all data and crop to the species codes less than 32000

dat <- data.frame()
  for (i in seq(0, 1000000, 10000)){
    ## find how many iterations it takes to cycle through the data
    print(i)
    ## query the API link
    res <- httr::GET(url = paste0("https://apps-st.fisheries.noaa.gov/ods/foss/afsc_groundfish_survey_catch/",
                                  "?offset=",i,"&limit=10000")) # '&q={"species_code":{"$lt":32000}}'
    ## convert from JSON format
    data <- jsonlite::fromJSON(base::rawToChar(res$content))

    ## if there are no data, stop the loop
    if (is.null(nrow(data$items))) {
      break
    }

    ## bind sub-pull to dat data.frame
    dat <- dplyr::bind_rows(dat,
                            data$items %>%
                              dplyr::select(-links)) # necessary for API accounting, but not part of the dataset)
  }



catch <- dat %>%
  dplyr::filter(species_code < 32000) %>%
  unique()

############ Testing # As of April 21, 2025
# all data
dim(dat)
# 891144      7
summary(dat)
# hauljoin        species_code     cpue_kgkm2        cpue_nokm2           count            weight_kg         taxon_confidence
# Min.   : -23911   Min.   :    1   Min.   :      0   Min.   :      13   Min.   :     1.0   Min.   :    0.001   Length:891144
# 1st Qu.: -14439   1st Qu.:20510   1st Qu.:      6   1st Qu.:      58   1st Qu.:     2.0   1st Qu.:    0.199   Class :character
# Median :  -5267   Median :40500   Median :     49   Median :     214   Median :     8.0   Median :    1.814   Mode  :character
# Mean   : 280338   Mean   :45195   Mean   :   1250   Mean   :    4605   Mean   :   180.5   Mean   :   41.720
# 3rd Qu.: 802426   3rd Qu.:71800   3rd Qu.:    372   3rd Qu.:    1137   3rd Qu.:    43.0   3rd Qu.:   13.780
# Max.   :1225635   Max.   :99999   Max.   :3226235   Max.   :21780780   Max.   :867119.0   Max.   :18187.700
#                                   NA's   :87811      NA's   :87811

############ Testing
# data cropped to species codes of interest
dim(catch)
# 438608      7
summary(catch)
# hauljoin        species_code     cpue_kgkm2        cpue_nokm2          count           weight_kg         taxon_confidence
# Min.   : -23911   Min.   :    1   Min.   :      0   Min.   :     14   Min.   :    1.0   Min.   :    0.001   Length:438608
# 1st Qu.: -14310   1st Qu.:10130   1st Qu.:     25   1st Qu.:     64   1st Qu.:    2.0   1st Qu.:    0.872   Class :character
# Median :  -4750   Median :20510   Median :    171   Median :    243   Median :    9.0   Median :    5.900   Mode  :character
# Mean   : 284057   Mean   :16337   Mean   :   2236   Mean   :   4437   Mean   :  154.4   Mean   :   71.638
# 3rd Qu.: 802455   3rd Qu.:21740   3rd Qu.:    897   3rd Qu.:   1307   3rd Qu.:   46.0   3rd Qu.:   31.320
# Max.   :1225635   Max.   :30600   Max.   :3226235   Max.   :4481702   Max.   :47118.0   Max.   :18187.700
#                                   NA's   :943       NA's   :943

# mostly for testing, but also nice to have it organized
catch <- catch[order(catch$species_code), ]
catch <- catch[order(catch$hauljoin), ]

write.csv(x = catch,
          here::here("data_processing_rcode/data/AK_gap_products_foss_catch.csv"))

# # Zero-Filled Data -----------------------------------------------------------
#
# dat <- dplyr::full_join(
#   haul,
#   catch) %>%
#   dplyr::full_join(
#    catch_spp)  %>%
#   # modify zero-filled rows
#   dplyr::mutate(
#     cpue_kgkm2 = ifelse(is.na(cpue_kgkm2), 0, cpue_kgkm2),
#     cpue_nokm2 = ifelse(is.na(cpue_nokm2), 0, cpue_nokm2),
#     count = ifelse(is.na(count), 0, count),
#     weight_kg = ifelse(is.na(weight_kg), 0, weight_kg))
