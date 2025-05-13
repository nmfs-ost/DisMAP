
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
data_orig <- data.frame(base::readRDS(file = here::here("data_processing_rcode/output/data_clean/alldata_withzeros.rds")))

## creating a dataset for last year ##

bfish <- read_csv(here::here("data_processing_rcode/data", "BFISH_DisMAP_2024_update_v2.csv")) %>%
  select(region, haulid, year, spp, wtcpue, stratum, stratumarea, lat, lon, depth)
ai <- read_csv(here::here("data_processing_rcode","output","python", "AI_survey.csv")) %>%
  select(region, haulid, year, spp, wtcpue, stratum, stratumarea, lat, lon, depth)
ebs <- read_csv(here::here("data_processing_rcode","output","python", "EBS_survey.csv")) %>%
  select(region, haulid, year, spp, wtcpue, stratum, stratumarea, lat, lon, depth)
gmex <- read_csv(here::here("data_processing_rcode","output","python", "GMEX_survey.csv")) %>%
  select(region, haulid, year, spp, wtcpue, stratum, stratumarea, lat, lon, depth)
goa <- read_csv(here::here("data_processing_rcode","output","python", "GOA_survey.csv")) %>%
  select(region, haulid, year, spp, wtcpue, stratum, stratumarea, lat, lon, depth)
nbs <- read_csv(here::here("data_processing_rcode","output","python", "NBS_survey.csv")) %>%
  select(region, haulid, year, spp, wtcpue, stratum, stratumarea, lat, lon, depth)
neus_fall <- read_csv(here::here("data_processing_rcode","output","python", "NEUS_FAL_survey.csv")) %>%
  select(region, haulid, year, spp, wtcpue, stratum, stratumarea, lat, lon, depth)
neus_spri <- read_csv(here::here("data_processing_rcode","output","python", "NEUS_SPR_survey.csv")) %>%
  select(region, haulid, year, spp, wtcpue, stratum, stratumarea, lat, lon, depth)
seus_fall <- read_csv(here::here("data_processing_rcode","output","python", "SEUS_FAL_survey.csv")) %>%
  select(region, haulid, year, spp, wtcpue, stratum, stratumarea, lat, lon, depth)
seus_spri <- read_csv(here::here("data_processing_rcode","output","python", "SEUS_SPR_survey.csv")) %>%
  select(region, haulid, year, spp, wtcpue, stratum, stratumarea, lat, lon, depth)
seus_sum <- read_csv(here::here("data_processing_rcode","output","python", "SEUS_SUM_survey.csv")) %>%
  select(region, haulid, year, spp, wtcpue, stratum, stratumarea, lat, lon, depth)
wc_ann <- read_csv(here::here("data_processing_rcode","output","python", "WC_ANN_survey.csv")) %>%
  select(region, haulid, year, spp, wtcpue, stratum, stratumarea, lat, lon, depth)
wc_tri <- read_csv(here::here("data_processing_rcode","output","python", "WC_TRI_survey.csv")) %>%
  select(region, haulid, year, spp, wtcpue, stratum, stratumarea, lat, lon, depth)

data <- rbind(bfish, ai, ebs, gmex, goa, nbs, neus_fall, neus_spri, seus_fall, seus_spri, seus_sum, wc_ann, wc_tri)

## done ##


data$survey <- ifelse(data$region == "Aleutian Islands", "Aleutian Islands Bottom Trawl Survey",
                         ifelse(data$region == "Eastern Bering Sea", "Eastern Bering Sea Crab/Groundfish Bottom Trawl Survey",
                                ifelse(data$region == "Northern Bering Sea", "Northern Bering Sea Crab/Groundfish Survey - Eastern Bering Sea Shelf Survey Extension",
                                       ifelse(data$region == "Gulf of Alaska", "Gulf of Alaska Bottom Trawl Survey",
                                              ifelse(data$region == "Gulf of Mexico", "Gulf of Mexico Summer Shrimp/Groundfish Survey",
                                                     ifelse(data$region == "Northeast US Fall", "NEFSC Fall Bottom Trawl",
                                                            ifelse(data$region == "Northeast US Spring", "NEFSC Spring Bottom Trawl",
                                                                   ifelse(data$region == "Southeast US Fall", "SEAMAP Fall Coastal Trawl Survey",
                                                                          ifelse(data$region == "Southeast US Spring", "SEAMAP Spring Coastal Trawl Survey",
                                                                                 ifelse(data$region == "Southeast US Summer", "SEAMAP Summer Coastal Trawl Survey",
                                                                                        ifelse(data$region == "West Coast Annual", "West Coast Bottom Trawl Annual",
                                                                                               ifelse(data$region == "West Coast Triennial", "West Coast Bottom Trawl Triennial",
                                                                                                      ifelse(data$region == "Hawaii", "Bottomfish Fishery-Independent Survey in Hawaii (BFISH)",
                                                                                                             ifelse(data$region == "Eastern and Northern Bering Sea", NA, NA))))))))))))))

data_update <- data %>%
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
                                                                                                   ifelse(data_update$region_old == "Hawaii", "Hawai'i Islands",
                                                                                                          ifelse(data_update$region_old == "West Coast Triennial", "West Coast", NA)))))))))))))


#### Calculate percentile for each spp, year, and survey####
data_rank <- data_update %>%
  select(region, survey, spp, year,
         # common,
         wtcpue) %>%
  group_by(region, survey, year, spp) %>%
  summarise(wtcpue = sum(wtcpue)) %>%
  group_by(region, survey, spp) %>%
  mutate(percentile = percent_rank(wtcpue)) %>%
  # select(-wtcpue) %>%
  dplyr::rename(Region = region,
                SurveyName = survey,
                Species = spp,
                Year = year,
                WTCPUE = wtcpue,
                Percentile = percentile)

#### Calculate cumulative biomass gain or loss across all survey years####

data_wtcpue <- data_update %>%
  select(region, survey, year, spp,
         # common,
         wtcpue) %>%
  group_by(region, survey, year, spp) %>%
  summarise(wtcpue = sum(wtcpue))


# loop through to find the gain or loss in biomass from year to year
holding <- data.frame(survey = character(), spp = character(), Diff = numeric(), stringsAsFactors = FALSE)


surveys <- unique(data_wtcpue$survey)

for(v in surveys) {

  firstfilt <- data_wtcpue %>%
    filter(survey == v)

  spps <- unique(firstfilt$spp)

  for (p in spps) {

    myfilt <- firstfilt %>%
      filter(spp == p)

    years <- c(myfilt$year)


    for (i in 1:(length(years)-1)) {

      wt_1 <- myfilt %>%
        filter(year == years[i])

      wt_2 <- myfilt %>%
        filter(year == years[i+1])

      diff <- wt_2$wtcpue[1] - wt_1$wtcpue[1]

      #this step (below) might be redundant
      survey <- paste(v)
      spp <- paste(p)
      Diff <- diff

      temp <- data.frame(survey = survey, spp = spp, Diff = Diff, stringsAsFactors = FALSE)

      holding <- rbind(holding, temp)

    }
  }
}


netwtcpue <- holding %>%
  group_by(survey, spp) %>%
  summarise(net_wtcpue = sum(Diff))

netwtcpue$region <- ifelse(netwtcpue$survey == "Aleutian Islands Bottom Trawl Survey", "Aleutian Islands",
                             ifelse(netwtcpue$survey == "Eastern Bering Sea Crab/Groundfish Bottom Trawl Survey", "Eastern Bering Sea",
                                    ifelse(netwtcpue$survey == "Northern Bering Sea Crab/Groundfish Survey - Eastern Bering Sea Shelf Survey Extension", "Northern Bering Sea",
                                           ifelse(netwtcpue$survey == "Gulf of Alaska Bottom Trawl Survey", "Gulf of Alaska",
                                                  ifelse(netwtcpue$survey == "Gulf of Mexico Summer Shrimp/Groundfish Survey", "Gulf of Mexico",
                                                         ifelse(netwtcpue$survey == "NEFSC Fall Bottom Trawl", "Northeast US",
                                                                ifelse(netwtcpue$survey == "NEFSC Spring Bottom Trawl", "Northeast US",
                                                                       ifelse(netwtcpue$survey == "SEAMAP Fall Coastal Trawl Survey", "Southeast US",
                                                                              ifelse(netwtcpue$survey == "SEAMAP Spring Coastal Trawl Survey", "Southeast US",
                                                                                     ifelse(netwtcpue$survey == "SEAMAP Summer Coastal Trawl Survey", "Southeast US",
                                                                                            ifelse(netwtcpue$survey == "West Coast Bottom Trawl Annual", "West Coast",
                                                                                                   ifelse(netwtcpue$survey == "Bottomfish Fishery-Independent Survey in Hawaii (BFISH)", "Hawai'i Islands",
                                                                                                          ifelse(netwtcpue$survey == "West Coast Bottom Trawl Triennial", "West Coast", NA)))))))))))))


netwtcpue <- netwtcpue %>%
  select(region, survey, spp, net_wtcpue) %>%
  dplyr::rename(Region = region,
                SurveyName = survey,
                Species = spp,
                NetWTCPUE = net_wtcpue)


## Add presence absence (1/0) ??

#### Writing csv files for development team ####

# write.csv(data_rank, here::here("data_processing_rcode","output","data_clean","SpeciesPersistenceIndicatorPercentile_withWTCPUE.csv"), row.names = FALSE)
# write.csv(netwtcpue, here::here("data_processing_rcode","output","data_clean","SpeciesPersistenceIndicatorNetWTCPUE.csv"), row.names = FALSE)


#### Visualizations ####

# an example of filtering for a species and visualizing - redo this
data_filt1 <- data_rank %>%
  filter(Species == "Sebastes aurora" | (SurveyName== "West Coast Bottom Trawl Annual" & Species == "Sebastes melanostictus and S. aleutianus"))

data_filt2 <- data_rank %>%
  filter(SurveyName== "West Coast Bottom Trawl Annual" & Species == "Sebastes melanostictus and S. aleutianus")

data_filt3 <- data_rank %>%
  filter(Species == "Sebastes aurora")

data_filt4 <- data_rank %>%
  filter(SurveyName== "Aleutian Islands Bottom Trawl Survey" & Species == "Aplidium soldatovi")

plot1 <- ggplot(data, aes(Year, Species)) +
  geom_tile(aes(fill= Percentile)) +
  theme(axis.text.x = element_text(angle = 60, size = rel(0.80))) +
  scale_colour_brewer(palette = "Spectral")

plot2 <- ggplot(data_filt1, aes(Year, Species)) +
  scale_colour_brewer(palette = "Spectral") +
  geom_tile(aes(fill= Percentile)) +
  theme(axis.text.x = element_text(angle = 60, size = rel(0.80))) +
  theme_minimal()

plot3 <- ggplot(data_filt1, aes(Year, Species)) +
  scale_colour_brewer(palette = "Spectral") +
  geom_tile(aes(fill= WTCPUE)) +
  theme(axis.text.x = element_text(angle = 60, size = rel(0.80))) +
  theme_minimal()

plot4 <- ggplot(data_filt2, aes(Year, Species)) +
  scale_colour_brewer(palette = "Spectral") +
  geom_tile(aes(fill= WTCPUE)) +
  theme(axis.text.x = element_text(angle = 60, size = rel(0.80))) +
  theme_minimal()

plot5 <- ggplot(data_filt4, aes(Year, Species)) +
  scale_colour_brewer(palette = "Spectral") +
  geom_tile(aes(fill= Percentile)) +
  theme(axis.text.x = element_text(angle = 60, size = rel(0.80))) +
  theme_minimal()
