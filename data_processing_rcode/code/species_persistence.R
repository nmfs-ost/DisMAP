
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
# library(stringr)
# library(data.table)
# library(taxize)
# library(worrms)
# library(rfishbase)
# library(lubridate)
# library(PBSmapping)
# library(gridExtra)
# library(questionr)
# library(geosphere)

# Read in data from Compile_Dismap_Current.r
## Note: I am using example data from last year for now##

goa_ex <- readr::read_csv(file = here::here("data_processing_rcode/output/python/example_GOA_survey.csv"))[,-1] # remove "row number" column

#This step seems unecessary#
# goa_ex <- goa_ex %>%
#   type_convert(goa_ex, col_types = cols(
#     region = col_character(),
#     haulid = col_integer(),
#     year = col_double(),
#     spp = col_character(),
#     wtcpue = col_double(),
#     common = col_character(),
#     stratum = col_integer(),
#     stratumarea = col_integer(),
#     lat = col_double(),
#     lon = col_double(),
#     depth = col_double(),
#     DistributionProjectName = col_character(),
#   ))

goa_ex$year <- as.character(goa_ex$year)

goa_wide <- goa_ex %>%
  group_by(region, year, spp) %>%
  summarise(wtcpue = sum(wtcpue)) %>%
  pivot_wider(names_from = year, values_from = wtcpue, names_prefix = "yr") %>%
  mutate(
    yrs1993_90 = yr1993 - yr1990,
    yrs1996_93 = yr1996 - yr1993,
    yrs1999_96 = yr1999 - yr1996,
    yrs2003_99 = yr2003 - yr1999,
    yrs2005_03 = yr2005 - yr2003,
    yrs2007_05 = yr2007 - yr2005,
    yrs2009_07 = yr2009 - yr2007,
    yrs2011_09 = yr2011 - yr2009,
    yrs2013_11 = yr2013 - yr2011,
    yrs2015_13 = yr2015 - yr2013,
    yrs2017_15 = yr2017 - yr2015,
    yrs2019_17 = yr2019 - yr2017,
    yrs2021_19 = yr2021 - yr2019,
    yrs2023_21 = yr2023 - yr2021
  ) %>%
  ungroup() %>%
  select(region, spp, yrs1993_90:yrs2023_21) %>%
  mutate(total_change_wtcpue = yrs1993_90 + yrs1996_93 + yrs1999_96 + yrs2003_99 + yrs2005_03 + yrs2007_05 +
                                   yrs2009_07 + yrs2011_09 + yrs2013_11 + yrs2015_13 + yrs2017_15 + yrs2019_17 +
                                   yrs2021_19 + yrs2023_21) # this is a separate table

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
