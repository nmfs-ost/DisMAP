# This function can be used to download the most recent survey data files for the AK regions and
# put them in the data folder.
# The ai_strata.csv, ebs_strata.csv, and goa_strata.csv do not change year to year, and should be retained
# between updates (do not delete these files)

# Resources --------------------------------------------------------------------

# https://www.fisheries.noaa.gov/alaska/science-data/groundfish-assessment-program-bottom-trawl-surveys
# adatapted from https://afsc-gap-products.github.io/gap_products/content/foss-api-r.html#haul-data
# October 2, 2024 by Emily Markowitz, AFSC

# Install libraries ------------------------------------------------------------

library(dplyr)
library(httr)
library(jsonlite)
options(scipen = 999)

# Download data from FOSS API --------------------------------------------------

## Download Haul Data ----------------------------------------------------------

dat <- data.frame()
for (i in seq(0, 500000, 10000)){
  print(i)
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
                              "?offset=0&limit=10000"))

## convert from JSON format
data <- jsonlite::fromJSON(base::rawToChar(res$content))
catch_spp <- data$items  %>%
  dplyr::select(-links) # necessary for API accounting, but not part of the dataset

write.csv(x = catch_spp,
          here::here("data_processing_rcode/data/AK_gap_products_foss_species.csv"))

## Download Catch Data ---------------------------------------------------------
# catch <- data.frame()
# for (i in seq(0, 1000000, 10000)){
#   ## find how many iterations it takes to cycle through the data
#   print(i)
#   ## query the API link
#   res <- httr::GET(url = paste0("https://apps-st.fisheries.noaa.gov/ods/foss/afsc_groundfish_survey_catch/",
#                                 "?offset=",i,"&limit=10000", '&q={"species_code":{"$lt":32000}}'))
#   ## convert from JSON format
#   data <- jsonlite::fromJSON(base::rawToChar(res$content))
#
#   ## if there are no data, stop the loop
#   if (is.null(nrow(data$items))) {
#     break
#   }
#
#   ## bind sub-pull to dat data.frame
#   catch <- dplyr::bind_rows(dat,
#                             data$items %>%
#                               dplyr::select(-links)) # necessary for API accounting, but not part of the dataset)
# }
# # mostly for testing, but also nice to have it organized
# catch <- catch[order(catch$species_code), ]
# catch <- catch[order(catch$hauljoin), ]
#
# write.csv(x = catch,
#           here::here("data_processing_rcode/data/AK_gap_products_foss_catch.csv"))

catch <- data.frame()
for (i in seq(0, 1000000, 10000)){
  ## find how many iterations it takes to cycle through the data
  print(i)
  ## query the API link
  res <- httr::GET(url = paste0("https://apps-st.fisheries.noaa.gov/ods/foss/afsc_groundfish_survey_catch/",
                                "?offset=",i,"&limit=10000",'&q={"species_code":{"$lt":32000}}'))
  ## convert from JSON format
  data <- jsonlite::fromJSON(base::rawToChar(res$content))

  ## if there are no data, stop the loop
  if (is.null(nrow(data$items))) {
    break
  }

  ## bind sub-pull to dat data.frame
  catch <- dplyr::bind_rows(dat,
                          data$items %>%
                            dplyr::select(-links)) # necessary for API accounting, but not part of the dataset)
}
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
