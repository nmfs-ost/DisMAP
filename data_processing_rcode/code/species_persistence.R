
# This script will process cleaned survey data to evaluate species persistence as
# change in biomass of each species in a survey region



# Load required packages
library(devtools)
library(here)
library(dplyr)
library(readr) # note need to install from repo to get older version 1.3.1 for it to work properly
# library(purrr)
library(forcats)
library(tidyr)
library(tibble)
library(ggplot2)
library(RColorBrewer)


# Read in data from Compile_Dismap_Current.r
## Note: I am using example data from last year for now##
data_ex <- data.frame(base::readRDS(file = here::here("data_processing_rcode/output/data_clean/alldata_withzeros.rds")))

# This version does not include data from Hawai'i Islands, but this should be added in
data_ex$survey <- ifelse(data_ex$region == "Aleutian Islands", "Aleutian Islands Bottom Trawl Survey",
                         ifelse(data_ex$region == "Eastern Bering Sea", "Eastern Bering Sea Crab/Groundfish Bottom Trawl Survey",
                                ifelse(data_ex$region == "Northern Bering Sea", "Northern Bering Sea Crab/Groundfish Survey - Eastern Bering Sea Shelf Survey Extension",
                                       ifelse(data_ex$region == "Gulf of Alaska", "Gulf of Alaska Bottom Trawl Survey",
                                              ifelse(data_ex$region == "Gulf of Mexico", "Gulf of Mexico Summer Shrimp/Groundfish Survey",
                                                     ifelse(data_ex$region == "Northeast US Fall", "NEFSC Fall Bottom Trawl",
                                                            ifelse(data_ex$region == "Northeast US Spring", "NEFSC Spring Bottom Trawl",
                                                                   ifelse(data_ex$region == "Southeast US Fall", "SEAMAP Fall Coastal Trawl Survey",
                                                                          ifelse(data_ex$region == "Southeast US Spring", "SEAMAP Spring Coastal Trawl Survey",
                                                                                 ifelse(data_ex$region == "Southeast US Summer", "SEAMAP Summer Coastal Trawl Survey",
                                                                                        ifelse(data_ex$region == "West Coast Annual", "West Coast Bottom Trawl Annual",
                                                                                               ifelse(data_ex$region == "West Coast Triennial", "West Coast Bottom Trawl Triennial",
                                                                                                      ifelse(data_ex$region == "Eastern and Northern Bering Sea", NA, NA)))))))))))))

data_update <- data_ex %>%
  filter(!is.na(survey)) %>%
  mutate(region_old = region) %>%
  select(-region)

data_update$region <- ifelse(data_update$region_old == "Aleutian Islands", "Aleutian Islands",
                             ifelse(data_update$region_old == "Eastern Bering Sea", "Eastern Bering Sea",
                                    ifelse(data_update$region_old == "Northern Bering Sea", "Northern Bering Sea",
                                           ifelse(data_update$region_old == "Gulf of Alaska", "Gulf of Alaska",
                                                  ifelse(data_update$region_old == "Gulf of Mexico", "Gulf of Mexico",
                                                         ifelse(data_update$region_old == "Northeast US Fall", "Northeast US",
                                                                ifelse(data_update$region_old == "Northeast US Spring", "Northeast US",
                                                                       ifelse(data_update$region_old == "Southeast US Fall", "Southeast US",
                                                                              ifelse(data_update$region_old == "Southeast US Spring", "Southeast US",
                                                                                     ifelse(data_update$region_old == "Southeast US Summer", "Southeast US",
                                                                                            ifelse(data_update$region_old == "West Coast Annual", "West Coast",
                                                                                                   ifelse(data_update$region_old == "West Coast Triennial", "West Coast", NA))))))))))))


# caculate percentile for each
data_rank <- data_update %>%
  select(region, survey, year, spp, common, wtcpue) %>%
  group_by(region, survey, year, spp) %>%
  summarise(wtcpue = sum(wtcpue)) %>%
  group_by(region, survey, spp) %>%
  mutate(percentile = percent_rank(wtcpue)) %>%
  select(-wtcpue)

##### PAUSED HERE #####

  # pivot_wider(names_from = year, values_from = wtcpue, names_prefix = "yr") %>%
  # mutate(
  #   yrs1993_yr90 = yr1993 - yr1990,
  #   yrs1996_yr93 = yr1996 - yr1993,
  #   yrs1999_yr96 = yr1999 - yr1996,
  #   yrs2003_yr99 = yr2003 - yr1999,
  #   yrs2005_yr03 = yr2005 - yr2003,
  #   yrs2007_yr05 = yr2007 - yr2005,
  #   yrs2009_yr07 = yr2009 - yr2007,
  #   yrs2011_yr09 = yr2011 - yr2009,
  #   yrs2013_yr11 = yr2013 - yr2011,
  #   yrs2015_yr13 = yr2015 - yr2013,
  #   yrs2017_yr15 = yr2017 - yr2015,
  #   yrs2019_yr17 = yr2019 - yr2017,
  #   yrs2021_yr19 = yr2021 - yr2019,
  #   yrs2023_yr21 = yr2023 - yr2021
  # ) %>%
  # ungroup() %>%
  # select(region, spp, yrs1993_90:yrs2023_21) %>%
  # mutate(total_change_wtcpue = yrs1993_90 + yrs1996_93 + yrs1999_96 + yrs2003_99 + yrs2005_03 + yrs2007_05 +
  #                                  yrs2009_07 + yrs2011_09 + yrs2013_11 + yrs2015_13 + yrs2017_15 + yrs2019_17 +
  #                                  yrs2021_19 + yrs2023_21) # this is a separate table

## Add presence absence (1/0), actual biomass, percentile for just that year

goa_long <- goa_wide %>%
  pivot_longer(yrs1993_90:total_change_wtcpue, names_to = "year_diff", values_to = "wtcpue_diff")

#an example of filtering for a species and visualizing
goa_filt <- goa_long %>%
  filter(spp== "Aphrocallistes vastus")

plot1 <- ggplot(goa_filt, aes(year_diff, spp)) +
  geom_tile(aes(fill= wtcpue_diff)) +
  theme(axis.text.x = element_text(angle = 60, size = rel(0.80))) +
  scale_colour_brewer(palette = "Spectral")
