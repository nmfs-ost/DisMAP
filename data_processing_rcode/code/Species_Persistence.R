####Introduction ####
#title: 'Species Persistence: Data Processing and Visualization'
# author: "NOAA Fisheries' Office of Science and Technology"
# date: "2026-5-28"
# The goals for this analysis are four-fold:
#
#   * Visualize changes in observed biomass for a particular species, from year to year
# * Categorize survey abundance as being:
#   + absent,
# + rare,
# + less common,
# + common,
# + abundant,
# + or highly abundant
# * Measure overall prevalence pattern of a particular species, across all survey years
# * Categorize trend as:
    # + Persistently Present,
    # + Persistently Absent,
    # + Stabilized Presence,
    # + Stabilized Absence,
    # + Re-emergence,
    # + Newly Emerging,
    # + Disappearing,
    # + Sporadic - Primarily Absent,
    # + Sporadic - Primarily Present

#### Load Packages ####
library(here)
library(dplyr)
library(ggplot2)
library(RColorBrewer)
library(readr)
library(tidyverse)
library(broom)
library(trend)

#### DATA PROCESSING/WRANGLING ####
### Run `Compile_Dismap_Current.R` first before this analysis ###

#read in data
data <- data.frame(base::readRDS(file = here::here("data_processing_rcode/output/data_clean/alldata_withzeros.rds"))) %>%
  select(region, haulid, year, spp, common, wtcpue, stratum, stratumarea, lat, lon, depth)

bfish <- read_csv(here::here("data_processing_rcode/data", "BFISH_DisMAP_2024_update.csv")) %>%
  mutate(haulid = psu,
         stratumarea = NA,
         region = case_when(region == "Hawaii" ~ "Hawai'i Islands")) %>%
  select(region, haulid, year, spp, common, wtcpue, stratum, stratumarea, lat, lon, depth)

data <- rbind(data, bfish)
rm(bfish)

# need to edit naming for regions versus surveys
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
                                                                                                   ifelse(data$region == "Hawai'i Islands", "Bottomfish Fishery-Independent Survey in Hawaii (BFISH)",
                                                                                                          ifelse(data$region == "Eastern and Northern Bering Sea", NA, NA))))))))))))))

data <- data %>%
  filter(!is.na(survey)) %>%
  mutate(region_old = region) %>%
  select(-region)

data$region <- ifelse(data$region_old == "Aleutian Islands", "Aleutian Islands",
                             ifelse(data$region_old == "Eastern Bering Sea", "Eastern Bering Sea",
                                    ifelse(data$region_old == "Northern Bering Sea", "Northern Bering Sea",
                                           ifelse(data$region_old == "Gulf of Alaska", "Gulf of Alaska",
                                                  ifelse(data$region_old == "Gulf of Mexico", "Gulf of Mexico",
                                                         ifelse(data$region_old == "Northeast US Fall", "Northeast US",
                                                                ifelse(data$region_old == "Northeast US Spring", "Northeast US",
                                                                       ifelse(data$region_old == "Southeast US Fall", "Southeast US",
                                                                              ifelse(data$region_old == "Southeast US Spring", "Southeast US",
                                                                                     ifelse(data$region_old == "Southeast US Summer", "Southeast US",
                                                                                            ifelse(data$region_old == "West Coast Annual", "West Coast",
                                                                                                   ifelse(data$region_old == "Hawai'i Islands", "Hawai'i Islands",
                                                                                                          ifelse(data$region_old == "West Coast Triennial", "West Coast", NA)))))))))))))
data<- data %>%
  select(-region_old)

#### PERCENTILES: BIOMASS & HAUL  ####
#### Biomass percentile ####
# This section captures the data by calculating percentile/rank of biomass of a specific species, compared to all the species biomass in that survey region and survey year.
# We calculate total biomass for each species in each year for each survey. Then we remove zero biomass records because these values would skew percentile calculations in the following step.
#These will be added back in after the percentile calculations.

data_sum <- data %>%
  select(region, survey, spp, year, common, wtcpue) %>%
  group_by(region, survey, year, spp, common) %>%
  summarise(wtcpue = sum(wtcpue))

data_sum_zeros <- data_sum %>%
  filter(wtcpue == 0)

data_sum_nozeros <- data_sum %>%
  filter(wtcpue > 0)

#Using the `cume_dist()` function here (as opposed to the `percent_rank()` function) to
# rank biomass values as percentiles because this method will not produce a percentile of
# zero. Percentiles are calculated for a particular species, in comparison to all the biomass
# values for all species in a survey/survey region, across all survey years.

data_rank_nozeros <- data_sum_nozeros %>%
  group_by(region, survey) %>%
  mutate(percentile = cume_dist(wtcpue))

#Then, we bring the zero biomass rows back in after the percentiles are calculated and `rbind`
# them to the data set with percentiles calculated. Species that have zero biomass in a survey
# region for a survey year will have a percentile value of zero. Any species that has a survey
# biomass > 0 for a survey year will have a ranked percentile value, in comparison to all the
# biomass values in that survey region across all survey years.

data_rank <- rbind(data_rank_nozeros, data_sum_zeros) %>%
  dplyr::rename(Region = region,
                SurveyName = survey,
                Common = common,
                Species = spp,
                Year = year,
                WTCPUE = wtcpue,
                Percentile = percentile) %>%
  mutate(Percentile = ifelse(is.na(Percentile), 0, Percentile))

### Bin the percentile values as:
#"Absent" (biomass and percentile of 0),
#"Rare" (< 10th percentile),
#"Less Common" (10th - 25th percentile),
#"Common" (25th - 75th percentile),
#"Abundant" (75th - 90th percentile), or
#"Highly Abundant" (> 90th percentile).

data_rank$Bin <- ifelse(data_rank$Percentile == 0.0, "Absent",
                        ifelse(data_rank$Percentile > 0.0 & data_rank$Percentile <= 0.10, "Rare",
                               ifelse(data_rank$Percentile > 0.10 & data_rank$Percentile <= 0.25, "Less Common",
                                      ifelse(data_rank$Percentile > 0.25 & data_rank$Percentile <= 0.75, "Common",
                                             ifelse(data_rank$Percentile > 0.75 & data_rank$Percentile <= 0.90, "Abundant",
                                                    ifelse(data_rank$Percentile > 0.90, "Highly Abundant", NA))))))

data_rank$Absence_Presence <- ifelse(data_rank$WTCPUE == 0, "0",
                                     ifelse(data_rank$WTCPUE > 0, "1", "NA")) #Absence is 0 and Presence is 1

#### Proportion of hauls Percentiles ####
# This section will calculate the number of hauls that a species is present in, per survey and per year.
# Measuring the presence in hauls will capture the prevalence of that species in the survey (i.e., how
# prominent is this species in the survey?), over time. We calculate the number of hauls total (in each
#survey and survey year) and the number of hauls for which a particular species was caught. We then also
#calculate the proportion of total hauls each species was caught in (for each survey and survey year).
haulsyr_max <- data %>%
  select(survey, haulid, year) %>%
  distinct() %>%
  group_by(survey, year) %>%
  summarise(maxhauls = n())

haulsyr <- data %>%
  filter(wtcpue > 0) %>%
  select(survey, year, haulid, spp) %>%
  distinct() %>%
  group_by(survey, year, spp) %>%
  summarise(haulspres = n())


data_haul <- left_join(haulsyr, haulsyr_max, by = c("survey", "year")) %>%
  mutate(
    haul_perc = haulspres/maxhauls
  ) %>%
  rename(
    SurveyName = survey,
    Year = year,
    Species = spp,
    HaulPresence = haulspres,
    HaulProportion = haul_perc
  ) %>%
  select(-maxhauls)

#### Combine Haul props table with Biomass percentile table and add Haul prop bins ####
data_full <- data_rank %>%
  left_join(data_haul, by = c("SurveyName", "Year", "Species")) %>%
  mutate(HaulPresence = ifelse(is.na(HaulPresence), 0, HaulPresence)) %>%
  mutate(HaulProportion = ifelse(is.na(HaulProportion), 0, HaulProportion))



data_full$HaulBin <- ifelse(data_full$HaulProportion == 0.0, "Absent",
                            ifelse(data_full$HaulProportion > 0.0 & data_full$HaulProportion <= 0.10, "Rare",
                                   ifelse(data_full$HaulProportion > 0.10 & data_full$HaulProportion <= 0.25, "Less Common",
                                          ifelse(data_full$HaulProportion > 0.25 & data_full$HaulProportion <= 0.75, "Common",
                                                 ifelse(data_full$HaulProportion > 0.75 & data_full$HaulProportion <= 0.90, "Abundant",
                                                        ifelse(data_full$HaulProportion > 0.90, "Highly Abundant", NA))))))

data_full$HaulBin <- factor(data_full$HaulBin, levels = c("Absent", "Rare", "Less Common", "Common", "Abundant", "Highly Abundant"))

####Export data as csv####
data_percentiles_export<- data_full %>%
  select (Region, SurveyName, Year, Species, Common, WTCPUE, Bin, HaulProportion, HaulBin)

write.csv(data_percentiles_export, here::here("data_processing_rcode","output","data_clean","SpeciesPersistenceIndicatorPercentileBin.csv"))


#### TREND ASSESSMENT ####
# This section:
#   - 1) evaluates the trend categories based on observation (presence versus absence) in survey catch,
# - 2) measures increasing versus decreasing trends in levels of haul frequency and biomass,
# - 3) conducts a ground-truthing exercise to examine trends of a set of focal species,
# - 4) applies a flagging function to trends that require further review, and
# - 5) compiles all information for data export

#### Directional Trend Analysis: Increasing or Decreasing Trend analysis ####
# 1. Define a function to identify the trend direction and significance
get_trend_status <- function(data) {
  # 1. Remove NAs for the calculation
  clean_vec <- na.omit(data)

  # 2. Check for minimum data points (need at least 5 for MK test)
  if(length(clean_vec) < 5) return("Incomplete Data")

  # 3. Check if the values are constant (e.g., all 0 or all 1)
  # If the difference between max and min is ~0, it's stable/zero
  if(max(clean_vec) - min(clean_vec) < 1e-9) return("Stable (Zero/Constant)")

  # 4. Run the test now that we know there is variation
  test <- trend::mk.test(clean_vec)
  p <- test$p.value
  s <- test$estimates[1]

  if (p < 0.05) {
    if (s > 0) return("Increasing")
    else return("Decreasing")
  } else {
    return("Stable")
  }
}

#Proportion in Hauls trend
data_trend_haul <- data_full %>%
  select(Region, SurveyName, Year, Species, Common, HaulProportion)

data_trend_haul <- data_trend_haul %>%
  group_by(SurveyName, Species) %>%
  mutate(Haul_Inc_Dec = get_trend_status(HaulProportion)) %>%
  ungroup() %>%
  select(Region, SurveyName, Species, Common, Haul_Inc_Dec) %>%
  distinct()

#Biomass Trends
data_trend_wtcpue <- data_full %>%
  select(Region, SurveyName, Year, Species, Common, WTCPUE)

data_trend_wtcpue <- data_trend_wtcpue %>%
  group_by(SurveyName, Species) %>%
  mutate(Bio_Inc_Dec = get_trend_status(WTCPUE)) %>%
  ungroup() %>%
  select(Region, SurveyName, Species, Common, Bio_Inc_Dec) %>%
  distinct()

#### Trend Categorization ####
##Category definitions
# Persistently Present:	High occupancy throughout, with no major gaps in the recent window.
# Persistently Absent:	Never/rarely detected.
# Sustained Presence: Was historically absent/rare (or recently absent), followed by a clear, sustained "break" into consistent presence.
# Newly Emerging:	A recent "spike" in detections after a period of absence, but not yet sustained enough to be "Emerged."
# Re-emerging: currently becoming more present, but has history of disappearing for stretches
# Stabilzed Absence:	Was historically common, followed by a sustained absence.
# Disappearing:	A recent "drop" in detections. Still present in the middle of the series, but missing recently.
# Relapsing disappearance: Species is currently becoming more consistently absent, but has a history of fluctuating blocks of absences and presences
# Sporadic – Primarily Present:	Species is observed in over half of surveys but observations in surveys are inconsistent, and recent history shows no clear pattern
# Sporadic – Primarily Absent:	Species is observed in less than half of surveys and observations in surveys are inconsistent, and recent history shows no clear pattern

data_cumm <- data %>%
  select(region, survey, spp, year, common, wtcpue) %>%
  group_by(region, survey, year, spp, common) %>%
  summarise(wtcpue = sum(wtcpue)) %>%
  dplyr::rename(Region = region,
                SurveyName = survey,
                Common = common,
                Species = spp,
                Year = year,
                WTCPUE = wtcpue) %>%
  mutate(Absence_Presence = ifelse(WTCPUE == 0, "0",
                ifelse(WTCPUE > 0, "1", "NA"))) %>%  #Absence is 0 and Presence is 1
  select(-WTCPUE)

data_cumm$Absence_Presence <- as.numeric(data_cumm$Absence_Presence)

#first we identify instances in which a species shifts from being present in a survey one year to being absent in a survey the following year, and vice versa.
holding <- data.frame(SurveyName = character(), Species = character(), Year = numeric(), Diff = numeric(), stringsAsFactors = FALSE)
surveys <- unique(data_cumm$SurveyName)

for(v in surveys) {
  firstfilt <- data_cumm %>%
    filter(SurveyName == v)
  spps <- unique(firstfilt$Species)

  for (p in spps) {
    myfilt <- firstfilt %>%
      filter(Species == p)
    years <- c(myfilt$Year)
    years <- years[order(years)]

    for (i in 1:(length(years)-1)) {
      var_1 <- myfilt %>%
        filter(Year == years[i])
      var_2 <- myfilt %>%
        filter(Year == years[i+1])
      Diff <- var_2$Absence_Presence[1] - var_1$Absence_Presence[1]
      temp <- data.frame(SurveyName = v, Species = p, Year = years[i+1], Diff = Diff, stringsAsFactors = FALSE)
      holding <- rbind(holding, temp)
    }
  }
}

# Creating a species list will allow for joining in the common names at the end of the next chunk
spp_list <- distinct(data_cumm %>%
                       ungroup() %>%
                       select(SurveyName, Species, Common))

# Identifying when species goes from absent to present in survey
data_ce_col <- holding %>%
  filter(Diff == 1) %>%
  group_by(SurveyName, Species) %>%
  summarise(col = n())

# Identifying when species goes from present to absent in survey
data_ce_ext <- holding %>%
  filter(Diff == -1) %>%
  group_by(SurveyName, Species) %>%
  summarise(ext = n())

# Identifying when species remains as either absent or present in survey
data_ce_stable <- holding %>%
  filter(Diff == 0) %>%
  group_by(SurveyName, Species) %>%
  summarise(stable = n())

# merging three objects above
data_ce <- data_ce_stable %>%
  full_join(data_ce_col, by = c("SurveyName", "Species")) %>%
  full_join(data_ce_ext, by = c("SurveyName", "Species")) %>%
  replace(is.na(.), 0) %>%
  select(-stable) %>%
  left_join(spp_list, by = c("SurveyName", "Species")) %>%
  select(SurveyName, Species, Common, col, ext)

#adding colonization and extinction event columns to data frame to use in trend categorization
data_cumm_ce <- data_cumm %>%
  left_join(data_ce, by = c("SurveyName", "Species", "Common"))

# Stock Categorization Using Block Comparison
#
#' @param data A data.frame containing columns: Region, SurveyName, Species, Year, Absence_Presence
#' @return A data.frame with a single `TrendCategory` column broadcasted across all rows per group.

add_block_trend_categories <- function(data) {

  message("Processing data... Executing simplified block comparison strategy.")

  data_processed <- data %>%
    # 1. Sort precisely to ensure the final elements represent the modern era
    arrange(Region, SurveyName, Species, Year) %>%
    group_by(Region, SurveyName, Species) %>%

    # 2. Use nest/map or summarize to handle the complex group-level logic safely
    mutate(
      TrendCategory = {
        # Clean the vector for this specific group
        clean_pres <- Absence_Presence[!is.na(Absence_Presence)]
        n_total    <- length(clean_pres)
        p_total    <- sum(clean_pres == 1) / n_total

        # Isolate the last 3 years: Calculate the final run properties
        series_rle      <- rle(clean_pres)
        last_run_value  <- tail(series_rle$values, 1)
        last_run_length <- tail(series_rle$lengths, 1)
        ends_in_3_presences <- (last_run_value == 1 & last_run_length >= 3)
        ends_in_3_absences <- (last_run_value == 0 & last_run_length >= 3)

        # Apply the classification logic based on time-series length
        if (n_total >= 10) {

          # Isolate the final 5 elements (Modern Block) and the 5 elements prior (Historical Block)
          last_5_block <- tail(clean_pres, 5)
          prev_5_block <- head(tail(clean_pres, 10), 5)

          last_5_sum <- sum(last_5_block)
          prev_5_sum <- sum(prev_5_block)

          # Isolate first third, middle third, last third of time series
          indices      <- seq_along(clean_pres)
          splits       <- cut(indices, breaks = 3, labels = FALSE)

          first_third  <- clean_pres[splits == 1]
          p_first <- mean(first_third)
          middle_third <- clean_pres[splits == 2]
          p_middle <- mean(middle_third)
          last_third   <- clean_pres[splits == 3]
          p_last <- mean(last_third)

          # Isolate the Deep History ----
          # Everything BEFORE the last 10 years
          historical_series <- head(clean_pres, n_total - 10)

          # Calculate Run Length Encoding for the historical series
          hist_rle <- rle(historical_series)

          # --- CHRONOLOGICAL CHECK ---
          # 1. Find indices where a presence run lasted 4 or more years
          valid_pres_indices <- which(hist_rle$values == 1 & hist_rle$lengths >= 4)

          # 2. Check if ANY qualifying presence run is followed later by a >4 year absence run
          has_valid_reemergence_history <- FALSE

          if (length(valid_pres_indices) > 0) {
            # Find the very first time it successfully "emerged"
            first_emergence_idx <- min(valid_pres_indices)
            # Look at all RLE runs *after* that first emergence
            if (first_emergence_idx < length(hist_rle$values)) {
              subsequent_values <- hist_rle$values[(first_emergence_idx + 1):length(hist_rle$values)]
              subsequent_lengths <- hist_rle$lengths[(first_emergence_idx + 1):length(hist_rle$lengths)]
              # Did it disappear for AT LEAST than 4 years (i.e., >= 4 years)?
              has_valid_reemergence_history <- any(subsequent_values == 0 & subsequent_lengths >= 4)
            }
          }

          # # 1. Create our two distinct time series
          # historical_series <- head(clean_pres, n_total - 10) # For finding the anchor
          # forward_series    <- head(clean_pres, n_total - 5)  # For looking forward
          #
          # hist_rle    <- rle(historical_series)
          # forward_rle <- rle(forward_series)
          #
          # # --- CHRONOLOGICAL RE-EMERGENCE CHECK ---
          # valid_pres_indices <- which(hist_rle$values == 1 & hist_rle$lengths >= 4)
          # has_valid_reemergence_history <- FALSE
          #
          # if (length(valid_pres_indices) > 0) {
          #   first_emergence_idx <- min(valid_pres_indices)
          #
          #   # Calculate exactly how many absolute years into the data this historic run ended
          #   years_until_end_of_run <- sum(hist_rle$lengths[1:first_emergence_idx])
          #
          #   # Find which run index in the FORWARD RLE corresponds to that same absolute year
          #   forward_run_ends <- cumsum(forward_rle$lengths)
          #   forward_idx      <- which(forward_run_ends >= years_until_end_of_run)[1]
          #
          #   # Look at all forward RLE runs AFTER that matching index
          #   if (!is.na(forward_idx) && forward_idx < length(forward_rle$values)) {
          #     subsequent_values  <- forward_rle$values[(forward_idx + 1):length(forward_rle$values)]
          #     subsequent_lengths <- forward_rle$lengths[(forward_idx + 1):length(forward_rle$lengths)]
          #
          #     has_valid_reemergence_history <- any(subsequent_values == 0 & subsequent_lengths >= 4)
          #   }
          # }

          # 2. Find where a historic disappearance lasted 4 or more years
          valid_abs_indices <- which(hist_rle$values == 0 & hist_rle$lengths >= 4)
          has_valid_redisappearance_history <- FALSE

          if (length(valid_abs_indices) > 0) {
            first_disappearance_idx <- min(valid_abs_indices)
            # Look for a temporary >= 4 year recovery AFTER that initial disappearance
            if (first_disappearance_idx < length(hist_rle$values)) {
              post_disc_values  <- hist_rle$values[(first_disappearance_idx + 1):length(hist_rle$values)]
              post_disc_lengths <- hist_rle$lengths[(first_disappearance_idx + 1):length(hist_rle$lengths)]
              has_valid_redisappearance_history <- any(post_disc_values == 1 & post_disc_lengths >= 4)
            }
          }

          # # 1. Find where a historic disappearance lasted 4 or more years in the deep history
          # valid_abs_indices <- which(hist_rle$values == 0 & hist_rle$lengths >= 4)
          # has_valid_redisappearance_history <- FALSE
          #
          # if (length(valid_abs_indices) > 0) {
          #   first_disappearance_idx <- min(valid_abs_indices)
          #
          #   # Calculate exactly how many absolute years into the data this historic absence run ended
          #   years_until_end_of_abs_run <- sum(hist_rle$lengths[1:first_disappearance_idx])
          #
          #   # Find which run index in the FORWARD RLE corresponds to that same absolute year
          #   forward_run_ends <- cumsum(forward_rle$lengths)
          #   forward_idx      <- which(forward_run_ends >= years_until_end_of_abs_run)[1]
          #
          #   # Look for a temporary >= 4 year recovery AFTER that initial disappearance, up to the 5-year cutoff
          #   if (!is.na(forward_idx) && forward_idx < length(forward_rle$values)) {
          #     post_disc_values  <- forward_rle$values[(forward_idx + 1):length(forward_rle$values)]
          #     post_disc_lengths <- forward_rle$lengths[(forward_idx + 1):length(forward_rle$lengths)]
          #
          #     # Did it reappear (value == 1) for AT LEAST 4 years before the 5-year cutoff?
          #     has_valid_redisappearance_history <- any(post_disc_values == 1 & post_disc_lengths >= 4)
          #   }
          # }

          # Find the maximum consecutive run of 1s (presences) in history
          presence_runs <- hist_rle$lengths[hist_rle$values == 1]
          max_pres_run  <- if(length(presence_runs) > 0) max(presence_runs) else 0

          absence_runs <- hist_rle$lengths[hist_rle$values == 0]
          max_abs_run  <- if(length(absence_runs) > 0) max(absence_runs) else 0

          # ---------------------------------------------

          # Assign Categories based on direct block contrast
          if (p_total >= 0.75 & p_first >=0.75 & p_middle >=0.75 & p_last >= 0.75 & prev_5_sum >= 3 & !ends_in_3_absences){
            "Persistently Present"
          } else if (p_total <= 0.15 & p_first <= 0.15 & p_middle <= 0.15 & p_last <= 0.15 & prev_5_sum <= 2 & !ends_in_3_presences) {
            "Persistently Absent"
          } else if (prev_5_sum == 5 & last_5_sum == 5 & !(max_pres_run >= 4 & max_abs_run < 3)) {
            "Stabilized Presence"
          } else if (prev_5_sum == 0 & last_5_sum == 0 & !(max_abs_run >= 4 & max_pres_run < 3)) {
            "Stabilized Absence"
          } else if (prev_5_sum <= last_5_sum & last_5_sum >= 4) {
            # SUB-CRITERIA 1: separate re-emergence from new arrival
            if (has_valid_reemergence_history) {
              "Re-Emerging"
            } else if (max_pres_run >= 4 & max_abs_run <= 3 & p_total >= 0.5) {
              "Sporadic - Primarily Present"
            } else {
              "Emerging"
            }

          } else if (prev_5_sum >= last_5_sum & last_5_sum <= 1) {
            # SUB-CRITERIA 2
            if (has_valid_redisappearance_history) {
              "Relapsing Disappearance"
            } else if (max_abs_run >= 4 & max_pres_run <= 3 & p_total <= 0.5) {
              "Transient - Primarily Absent"
            } else {
              "Disappearing"
            }

          } else if (prev_5_sum <=1 & ends_in_3_presences){
            "Emerging"
          } else if (prev_5_sum >= 4 & ends_in_3_absences){
            "Disappearing"
          } else if (p_total >= 0.5) {
            "Sporadic - Primarily Present"
          } else {
            "Transient - Primarily Absent"
          }

        } else {
          # Short time-series fallback branch (n < 10)
          if (p_total >= 0.80) {
            "Persistently Present"
          } else if (p_total <= 0.20) {
            "Persistently Absent"
          } else if (ends_in_3_presences){
            "Emerging"
          } else if (ends_in_3_absences) {
            "Dissappearing"
          } else if (p_total >= 0.5) {
            "Sporadic - Primarily Present"
          } else {
            "Transient - Primarily Absent"
          }
        }
      }
    ) %>%
    ungroup()

  return(data_processed)
}

# Usage:
# This data frame will be used below in the flagging function
data_for_flag <- add_block_trend_categories(data_cumm_ce) %>%
  mutate(Name = paste(Common, SurveyName, sep = "_"))

# This dataframe will be used for vizualization and plotting to validate trends
data_cat_plot <- add_block_trend_categories(data_cumm_ce) %>%
  mutate(SurveyName = as.character(SurveyName),
         Species = as.character(Species))

# This dataframe will be used for the final data exporting
data_cat <- add_block_trend_categories(data_cumm_ce) %>%
  select(Region, SurveyName, Species, Common, TrendCategory) %>%
  distinct() %>%
  mutate(SurveyName = as.character(SurveyName),
         Species = as.character(Species))

#### Visualization and Validation ####
#visualize, check, validate
#PLOT 1: Validation of Trend Categories
# 1. Select one representative species for each category
examples <-  data_cat_plot %>%
  group_by(TrendCategory) %>%
  slice_sample(n = 1) %>%
  pull(Common)
#examples<- c("Barndoor skate")
# 2. Filter data for these specific examples
plot_data <- data_cat_plot %>%
  filter(Common %in% examples) %>%
  mutate(Absence_Presence = factor (Absence_Presence, levels = c(0,1)))

# 3. Create the Validation Plot
ggplot(plot_data, aes(x = Year, y = Common, fill = Absence_Presence)) +
  geom_tile(color = "white", linewidth = 0.2) + # Adds a small border between tiles
  facet_wrap(~TrendCategory, scales = "free_y", ncol = 1) + # Group by TrendCategory
  scale_fill_manual(
    values = c("0" = "#f8d7da", "1" = "#004085"), # Light red vs Deep blue
    labels = c("Absent", "Present"),
    name = "Status"
  ) +
  theme_minimal() +
  labs(
    title = "Species Trend Validation: Occupancy Barcodes",
    subtitle = "Visualizing the 'Sustained' vs 'Sporadic' patterns",
    x = "Year",
    y = "Species Common Name"
  ) +
  theme(
    strip.text = element_text(face = "bold", size = 10),
    panel.grid = element_blank(), # Remove grid lines for a cleaner tile look
    axis.text.y = element_text(size = 8)
  )

#### Flagging function ####
#adds a flag for species trends that are under review.

## flag species function
flag_spp <- function(data, survey){

  cat("taxonomy check for survey: ", survey, sep="\n")

  #select region (survey column)
  data_survey <- data %>%
    dplyr::mutate(SurveyName = forcats::as_factor(SurveyName)) %>%
    dplyr::filter(SurveyName == survey)


  #get grouped species names per year
  df <- data_survey %>%
    dplyr::select(Species, Year, Absence_Presence) %>%
    dplyr::group_by(Species) %>%
    dplyr::distinct()

  #make species x year matrix
  years <- unique(df$Year)
  df2 <- data.frame(matrix(ncol = length(years)+1, nrow = length(df$Species)))
  x <- c('spp', unique(df$Year))
  colnames(df2) <- x
  df2$spp <- df$Species

  #fill up matrix with FALSE/TRUE depending on species presence/absence
  n <- 2
  for (y in years) {
    df2[, n] <- sapply(df2$spp, function(spp_name) {
      any(df$Species == spp_name & df$Year == y & df$Absence_Presence == 1)
    })
    n <- n + 1
  }

  #summarize
  df2 <- df2 %>%
    dplyr::group_by(spp) %>%
    dplyr::summarize_all(any)

  #create new dataframe
  df3 <- data.frame(matrix(ncol = 3, nrow = length(df2$spp)))
  colnames(df3) <- c('spp', 'rlmax', 'PresToAbs')

  #fill up the dataframe
  for (n in 1:length(df2$spp)){

    #Compute the lengths and values of runs of equal values in a vector
    r <- rle(df2[n,])

    sp <- c(df2[n,1])

    rlmax <- max(r$lengths)

    df3[n,1] <- sp
    df3[n,2] <- rlmax #maximum run length
    df3[n,3] <- length(r$values) #total nb of runs

  }

  #get species with maximum run length lower than 95% of the years (56)
  #and that occurred in less than 4 runs
  x <- round(0.95*length(years))
  df3 <- df3[df3$rlmax < x,]
  df3 <- df3[df3$PresToAbs < 4,]

  testdf <- data.frame(spp = df3$spp)

  if (dim(testdf)[1] > 0) {

    #write df of species flagged
    survey_clean <- gsub("[/\\]", "_", survey)  # Replace slashes/backslashes with underscore
    write.csv(df3, file = here::here("data_processing_rcode", "output", "flags", paste0(survey_clean, "_flags.csv")), row.names = FALSE)

    #create absence dataframe for plotting
    allyears <- min(years):max(years)
    abs <- data.frame("accepted_name" = rep(df3$spp, each = length(allyears)),
                      "year" = rep(allyears, length(df3$spp)))

    #get presence dataframe for plotting
    pres <- subset(data_survey, Species %in% testdf$spp) %>%
      dplyr::select(Species, Year)

  }else{

    print("----- No species flagged for this region")
  }
}

##Compilation of flagged species
survey_list <- unique(data_for_flag$SurveyName)

for (i in survey_list) {
  flag_spp(data_for_flag, survey = i)
}

#bringing csv files back into combine them into one df
folder_path <- here::here("data_processing_rcode", "output", "flags")

files <- list.files(path = folder_path, pattern = "\\.csv$", full.names = TRUE)
# files_clean <- paste0(list.files(path = folder_path, pattern = "\\.csv$", full.names = FALSE))

df_list <- list()

for (n in seq_along(files)){
  #read in csv
  temp_df <- read_csv(files[n])
  # Get the file name without path and extension
  name <- tools::file_path_sans_ext(basename(files[n]))
  # Remove the string "flag" at the end, if present
  name <- sub("_flags$", "", name)
  # Add the source column as the first column
  temp_df <- cbind(survey = name, temp_df)
  # Store in list
  df_list[[n]] <- temp_df
}

flags_combo <- do.call(rbind, df_list) %>%
  rename(SurveyName = survey,
         Species = spp) %>%
  mutate(SurveyName = gsub("_", "/", SurveyName))

flags_combo$Notes <- c(rep("Preliminary trend - under review", nrow(flags_combo)))

#### Combine trends, flags and category datasets ####
data_trend_cat<- data_cat %>%
  full_join(data_trend_wtcpue, by = c("Region", "SurveyName", "Species", "Common")) %>%
  full_join(data_trend_haul, by = c("Region", "SurveyName", "Species", "Common")) %>%
  left_join(flags_combo, by = c("SurveyName", "Species")) %>%
  select(Region, SurveyName, Species, Common, TrendCategory, Notes, Haul_Inc_Dec, Bio_Inc_Dec)

#### Export Data ####
data_trend_export<-data_trend_cat
write.csv(data_trend_export, here::here("data_processing_rcode","output","data_clean","SpeciesPersistenceIndicatorTrendCategories.csv"))


####MANAGEMENT COUNCIL JURISDICTION ANALYSIS (for the NEFSC survey data only)####
#The following script does the same analysis as above, but parses the NE Bottom trawl data out into the three different management council jurisdictions.
library(sf)

####Load spatial polygons ####
# 1. Load multi-polygon shapefile
boundaries <- st_read(here::here("data_processing_rcode/data/fishery_management_council_regions_20210609", "20210609_fishery_management_council_regions.shp"))
boundaries_exploded<-st_cast(boundaries, "POLYGON")
selected_boundaries<-boundaries_exploded %>%
  filter(FishRegion %in% c("New England", "NEMA", "South Atlantic"))
# Apply the fix duplicate vertices issues
map_cleaned <- st_make_valid(selected_boundaries)
# Casts each individual Polygon back into its own Multipolygon wrapper
EC_Councils <- st_cast(map_cleaned, "MULTIPOLYGON")

# 2. Convert your dataframe to a spatial object
# We'll create a copy so we don't overwrite the original 'df' immediately
pts_sf <- st_as_sf(data, coords = c("lon", "lat"), crs = 4326, remove=FALSE)

# 3. Align the Coordinate Reference Systems (Crucial!)
EC_Councils <- st_transform(EC_Councils, st_crs(pts_sf))

# 4. Perform a Left Spatial Join
# 'left = TRUE' ensures we keep ALL points, even those that fall outside both polygons
df_labeled_sf <- st_join(pts_sf, EC_Councils, join = st_intersects, left = TRUE)
df_labeled_sf_NEUS <- df_labeled_sf %>%
  filter(region=="Northeast US")

# 5. Clean up and return to a standard dataframe
df_NEUS <- df_labeled_sf_NEUS %>%
  st_drop_geometry() %>%
  select(region, survey, haulid, year, spp, common, wtcpue, stratum, stratumarea, lat, lon, depth, FishRegion) %>%
  #filter(!is.na(FishRegion)) %>%
  unite("FishRegionsurvey", FishRegion, survey, sep=" ", remove=FALSE)

# # 6. Visualize to make sure the points are labeled correctly
Plot_FMC<- ggplot() +
  geom_sf(data = EC_Councils, aes(fill = FishRegion), alpha = 0.3) +
  geom_point(data = df_NEUS, aes(x=lon, y=lat, color = FishRegion)) +
  theme_minimal() +
  labs(title = "Points Labeled by Fishery Management Council Jurisdiction")

install.packages("maps")
library(maps)

# 1. Grab US state boundaries and convert them to an 'sf' object
us_states <- sf::st_as_sf(maps::map("state", plot = FALSE, fill = TRUE))

# 2. Build your updated plot
Plot_FMC <- ggplot() +
  # Basemap: Grayscale states
  geom_sf(data = us_states, fill = "gray95", color = "gray80") +

  # Your original layers
  geom_sf(data = EC_Councils, aes(fill = FishRegion), alpha = 0.4) +
  geom_point(data = df_NEUS, aes(x = lon, y = lat, color = FishRegion), size = 2) +

  # Crucial: Zoom the map specifically to the East Coast
  # (Adjust these coordinates if your data extends further north or south)
  coord_sf(xlim = c(-82, -65), ylim = c(30, 46), expand = FALSE) +

  theme_minimal() +
  labs(
    title = "Points Labeled by Fishery Management Council Jurisdiction",
    x = "Longitude",
    y = "Latitude"
  )

# Display the plot
print(Plot_FMC)

#### Proportion of total biomass by species in each Council region ####
data_sum_NEUSregions <- df_NEUS %>%
  select(region, survey, year, spp, common, wtcpue, FishRegion, FishRegionsurvey) %>%
  group_by(region, survey, year, spp, common, FishRegion, FishRegionsurvey) %>%
  summarise(FMCwtcpue = sum(wtcpue))

data_sum_Total <- df_NEUS %>%
  select(region, survey, year, spp, common, wtcpue) %>%
  group_by(region, survey, year, spp, common) %>%
  summarise(Totwtcpue = sum(wtcpue))

data_sum_All <- left_join(data_sum_NEUSregions, data_sum_Total, by=c("region", "survey", "year", "spp", "common"))%>%
  filter(!is.na(FishRegion)) %>%
  mutate(prop=if_else(Totwtcpue ==0, 0, FMCwtcpue/Totwtcpue)) %>%
  mutate(Absence_Presence = ifelse(FMCwtcpue == 0, "0",
                                   ifelse(FMCwtcpue > 0, "1", "NA")))

data_sum_All$Absence_Presence <- as.numeric(data_sum_All$Absence_Presence)

#### Trend Categories by species, FMC region, and survey ####
data_cumm <- data_sum_All %>%
  select(region, survey, year, spp, common, FishRegion, FishRegionsurvey, Absence_Presence)

holding <- data.frame(FishRegionsurvey = character(), spp = character(), year = numeric(), Diff = numeric(), stringsAsFactors = FALSE)
FMCsurveys <- unique(data_cumm$FishRegionsurvey)

for(v in FMCsurveys) {

  firstfilt <- data_sum_All %>%
    filter(FishRegionsurvey == v)

  spps <- unique(firstfilt$spp)

  for (p in spps) {

    myfilt <- firstfilt %>%
      filter(spp == p)

    years <- c(myfilt$year)
    years <- years[order(years)]


    for (i in 1:(length(years)-1)) {

      var_1 <- myfilt %>%
        filter(year == years[i])

      var_2 <- myfilt %>%
        filter(year == years[i+1])

      Diff <- var_2$Absence_Presence[1] - var_1$Absence_Presence[1]

      temp <- data.frame(FishRegionsurvey = v, spp = p, year = years[i+1], Diff = Diff, stringsAsFactors = FALSE)

      holding <- rbind(holding, temp)

    }
  }
}

# Creating a species list will allow for joining in the common names at the end of the next chunk
spp_list_NEspatial <- distinct(data_sum_All %>%
                       ungroup() %>%
                       select(FishRegionsurvey, spp, common))

# Identifying when species goes from absent to present in survey
data_ce_col <- holding %>%
  filter(Diff == 1) %>%
  group_by(FishRegionsurvey, spp) %>%
  summarise(col = n())

# Identifying when species goes from present to absent in survey
data_ce_ext <- holding %>%
  filter(Diff == -1) %>%
  group_by(FishRegionsurvey, spp) %>%
  summarise(ext = n())

# Identifying when species remains as either absent or present in survey
data_ce_stable <- holding %>%
  filter(Diff == 0) %>%
  group_by(FishRegionsurvey, spp) %>%
  summarise(stable = n())

# merging three objects above
data_ce <- data_ce_stable %>%
  full_join(data_ce_col, by = c("FishRegionsurvey", "spp")) %>%
  full_join(data_ce_ext, by = c("FishRegionsurvey", "spp")) %>%
  replace(is.na(.), 0) %>%
  select(-stable) %>%
  left_join(spp_list_NEspatial, by = c("FishRegionsurvey", "spp")) %>%
  select(FishRegionsurvey, spp, common, col, ext)

#adding colonization and extinction event columns to data frame to use in trend categorization
data_NE_spatial <- data_sum_All %>%
  left_join(data_ce, by = c("FishRegionsurvey", "spp", "common"))

## Add the Category flags
add_block_trend_categories <- function(data) {

  message("Processing data... Executing simplified block comparison strategy.")

  data_processed <- data %>%
    # 1. Sort precisely to ensure the final elements represent the modern era
    arrange(region, FishRegionsurvey, spp, common, year) %>%
    group_by(region, FishRegionsurvey, spp, common) %>%

    # 2. Use nest/map or summarize to handle the complex group-level logic safely
    mutate(
      TrendCategory = {
        # Clean the vector for this specific group
        clean_pres <- Absence_Presence[!is.na(Absence_Presence)]
        n_total    <- length(clean_pres)
        p_total    <- sum(clean_pres == 1) / n_total

        # Isolate the last 3 years: Calculate the final run properties
        series_rle      <- rle(clean_pres)
        last_run_value  <- tail(series_rle$values, 1)
        last_run_length <- tail(series_rle$lengths, 1)
        ends_in_3_presences <- (last_run_value == 1 & last_run_length >= 3)
        ends_in_3_absences <- (last_run_value == 0 & last_run_length >= 3)

        # Apply the classification logic based on time-series length
        if (n_total >= 10) {

          # Isolate the final 5 elements (Modern Block) and the 5 elements prior (Historical Block)
          last_5_block <- tail(clean_pres, 5)
          prev_5_block <- head(tail(clean_pres, 10), 5)

          last_5_sum <- sum(last_5_block)
          prev_5_sum <- sum(prev_5_block)

          # Isolate first third, middle third, last third of time series
          indices      <- seq_along(clean_pres)
          splits       <- cut(indices, breaks = 3, labels = FALSE)

          first_third  <- clean_pres[splits == 1]
          p_first <- mean(first_third)
          middle_third <- clean_pres[splits == 2]
          p_middle <- mean(middle_third)
          last_third   <- clean_pres[splits == 3]
          p_last <- mean(last_third)

          # Isolate the Deep History ----
          # Everything BEFORE the last 10 years
          historical_series <- head(clean_pres, n_total - 10)

          # Calculate Run Length Encoding for the historical series
          hist_rle <- rle(historical_series)

          # --- CHRONOLOGICAL CHECK ---
          # 1. Find indices where a presence run lasted 4 or more years
          valid_pres_indices <- which(hist_rle$values == 1 & hist_rle$lengths >= 4)

          # 2. Check if ANY qualifying presence run is followed later by a >4 year absence run
          has_valid_reemergence_history <- FALSE

          if (length(valid_pres_indices) > 0) {
            # Find the very first time it successfully "emerged"
            first_emergence_idx <- min(valid_pres_indices)
            # Look at all RLE runs *after* that first emergence
            if (first_emergence_idx < length(hist_rle$values)) {
              subsequent_values <- hist_rle$values[(first_emergence_idx + 1):length(hist_rle$values)]
              subsequent_lengths <- hist_rle$lengths[(first_emergence_idx + 1):length(hist_rle$lengths)]
              # Did it disappear for AT LEAST than 4 years (i.e., >= 4 years)?
              has_valid_reemergence_history <- any(subsequent_values == 0 & subsequent_lengths >= 4)
            }
          }

          # # 1. Create our two distinct time series
          # historical_series <- head(clean_pres, n_total - 10) # For finding the anchor
          # forward_series    <- head(clean_pres, n_total - 5)  # For looking forward
          #
          # hist_rle    <- rle(historical_series)
          # forward_rle <- rle(forward_series)
          #
          # # --- CHRONOLOGICAL RE-EMERGENCE CHECK ---
          # valid_pres_indices <- which(hist_rle$values == 1 & hist_rle$lengths >= 4)
          # has_valid_reemergence_history <- FALSE
          #
          # if (length(valid_pres_indices) > 0) {
          #   first_emergence_idx <- min(valid_pres_indices)
          #
          #   # Calculate exactly how many absolute years into the data this historic run ended
          #   years_until_end_of_run <- sum(hist_rle$lengths[1:first_emergence_idx])
          #
          #   # Find which run index in the FORWARD RLE corresponds to that same absolute year
          #   forward_run_ends <- cumsum(forward_rle$lengths)
          #   forward_idx      <- which(forward_run_ends >= years_until_end_of_run)[1]
          #
          #   # Look at all forward RLE runs AFTER that matching index
          #   if (!is.na(forward_idx) && forward_idx < length(forward_rle$values)) {
          #     subsequent_values  <- forward_rle$values[(forward_idx + 1):length(forward_rle$values)]
          #     subsequent_lengths <- forward_rle$lengths[(forward_idx + 1):length(forward_rle$lengths)]
          #
          #     has_valid_reemergence_history <- any(subsequent_values == 0 & subsequent_lengths >= 4)
          #   }
          # }

          # 2. Find where a historic disappearance lasted 4 or more years
          valid_abs_indices <- which(hist_rle$values == 0 & hist_rle$lengths >= 4)
          has_valid_redisappearance_history <- FALSE

          if (length(valid_abs_indices) > 0) {
            first_disappearance_idx <- min(valid_abs_indices)
            # Look for a temporary >= 4 year recovery AFTER that initial disappearance
            if (first_disappearance_idx < length(hist_rle$values)) {
              post_disc_values  <- hist_rle$values[(first_disappearance_idx + 1):length(hist_rle$values)]
              post_disc_lengths <- hist_rle$lengths[(first_disappearance_idx + 1):length(hist_rle$lengths)]
              has_valid_redisappearance_history <- any(post_disc_values == 1 & post_disc_lengths >= 4)
            }
          }

          # # 1. Find where a historic disappearance lasted 4 or more years in the deep history
          # valid_abs_indices <- which(hist_rle$values == 0 & hist_rle$lengths >= 4)
          # has_valid_redisappearance_history <- FALSE
          #
          # if (length(valid_abs_indices) > 0) {
          #   first_disappearance_idx <- min(valid_abs_indices)
          #
          #   # Calculate exactly how many absolute years into the data this historic absence run ended
          #   years_until_end_of_abs_run <- sum(hist_rle$lengths[1:first_disappearance_idx])
          #
          #   # Find which run index in the FORWARD RLE corresponds to that same absolute year
          #   forward_run_ends <- cumsum(forward_rle$lengths)
          #   forward_idx      <- which(forward_run_ends >= years_until_end_of_abs_run)[1]
          #
          #   # Look for a temporary >= 4 year recovery AFTER that initial disappearance, up to the 5-year cutoff
          #   if (!is.na(forward_idx) && forward_idx < length(forward_rle$values)) {
          #     post_disc_values  <- forward_rle$values[(forward_idx + 1):length(forward_rle$values)]
          #     post_disc_lengths <- forward_rle$lengths[(forward_idx + 1):length(forward_rle$lengths)]
          #
          #     # Did it reappear (value == 1) for AT LEAST 4 years before the 5-year cutoff?
          #     has_valid_redisappearance_history <- any(post_disc_values == 1 & post_disc_lengths >= 4)
          #   }
          # }

          # Find the maximum consecutive run of 1s (presences) in history
          presence_runs <- hist_rle$lengths[hist_rle$values == 1]
          max_pres_run  <- if(length(presence_runs) > 0) max(presence_runs) else 0

          absence_runs <- hist_rle$lengths[hist_rle$values == 0]
          max_abs_run  <- if(length(absence_runs) > 0) max(absence_runs) else 0

          # ---------------------------------------------

          # Assign Categories based on direct block contrast
          if (p_total >= 0.75 & p_first >=0.75 & p_middle >=0.75 & p_last >= 0.75 & prev_5_sum >= 3 & !ends_in_3_absences){
            "Persistently Present"
          } else if (p_total <= 0.15 & p_first <= 0.15 & p_middle <= 0.15 & p_last <= 0.15 & prev_5_sum <= 2 & !ends_in_3_presences) {
            "Persistently Absent"
          } else if (prev_5_sum == 5 & last_5_sum == 5 & !(max_pres_run >= 4 & max_abs_run < 3)) {
            "Stabilized Presence"
          } else if (prev_5_sum == 0 & last_5_sum == 0 & !(max_abs_run >= 4 & max_pres_run < 3)) {
            "Stabilized Absence"
          } else if (prev_5_sum <= last_5_sum & last_5_sum >= 4) {
            # SUB-CRITERIA 1: separate re-emergence from new arrival
            if (has_valid_reemergence_history) {
              "Re-Emerging"
            } else if (max_pres_run >= 4 & max_abs_run <= 3 & p_total >= 0.5) {
              "Sporadic - Primarily Present"
            } else {
              "Emerging"
            }

          } else if (prev_5_sum >= last_5_sum & last_5_sum <= 1) {
            # SUB-CRITERIA 2
            if (has_valid_redisappearance_history) {
              "Relapsing Disappearance"
            } else if (max_abs_run >= 4 & max_pres_run <= 3 & p_total <= 0.5) {
              "Transient - Primarily Absent"
            } else {
              "Disappearing"
            }

          } else if (prev_5_sum <=1 & ends_in_3_presences){
            "Emerging"
          } else if (prev_5_sum >= 4 & ends_in_3_absences){
            "Disappearing"
          } else if (p_total >= 0.5) {
            "Sporadic - Primarily Present"
          } else {
            "Transient - Primarily Absent"
          }

        } else {
          # Short time-series fallback branch (n < 10)
          if (p_total >= 0.80) {
            "Persistently Present"
          } else if (p_total <= 0.20) {
            "Persistently Absent"
          } else if (ends_in_3_presences){
            "Emerging"
          } else if (ends_in_3_absences) {
            "Dissappearing"
          } else if (p_total >= 0.5) {
            "Sporadic - Primarily Present"
          } else {
            "Transient - Primarily Absent"
          }
        }
      }
    ) %>%
    ungroup()

  return(data_processed)
}

# Add the trend categories to the dataframe
data_NE_cat <- add_block_trend_categories(data_NE_spatial) %>%
  select(-col, -ext) %>%
  distinct() %>%
  mutate(FishRegionsurvey = as.character(FishRegionsurvey),
         spp = as.character(spp))

#### Increasing vs. decreasing vs. stable trends in proportion biomass####
#This section is caculates trend in proportion within each FMC and adds to dataframe
# 2. Apply to the dataframe and create a new column
data_NE_trend <- data_NE_spatial %>%
  group_by(spp, FishRegionsurvey) %>%
  mutate(Prop_inc_dec = get_trend_status(prop)) %>%
  ungroup()

#### Data Export NE anaylsis ####
data_NE_full<- data_NE_trend %>%
  full_join(data_NE_cat) %>%
  dplyr::rename(Region = region,
                SurveyName = survey,
                SpatialName = FishRegion,
                Common = common,
                Species = spp,
                Year = year,
                WTCPUE = FMCwtcpue,
                Prop = prop) %>%
  mutate(SpatialGroup = "Northeast FMC") %>%
  select(-Totwtcpue, -FishRegionsurvey, -col, -ext)

data_NE_full <- data_NE_full %>%
    mutate(FMC_new = ifelse(data_NE_full$SpatialName == "New England", "New England",
                       ifelse(data_NE_full$SpatialName == "NEMA", "Mid-Atlantic",
                              ifelse(data_NE_full$SpatialName == "South Atlantic", "South Atlantic", NA)))) %>%
    select(-SpatialName) %>%
    dplyr::rename(SpatialName = FMC_new)


write.csv(data_NE_full, here::here("data_processing_rcode","output","data_clean","SpatialGroup_SpeciesPersistenceIndicator.csv"))

#### Visualizations and Validation ####
#visualize, check, validate
#PLOT 1: Validation of Trend Categories
# 1. Select one representative species for each category
examples <- data_NE_full %>%
  group_by(TrendCategory) %>%
  slice_sample(n = 1) %>%
  pull(Common)

# 2. Filter data for these specific examples
plot_data <- data_NE_full %>%
  filter(Common %in% examples) %>%
  mutate(Absence_Presence = factor (Absence_Presence, levels = c(0,1)))

# 3. Create the Validation Plot
ggplot(plot_data, aes(x = Year, y = Common, fill = Absence_Presence)) +
  geom_tile(color = "white", linewidth = 0.2) + # Adds a small border between tiles
  facet_wrap(~TrendCategory, scales = "free_y", ncol = 1) + # Group by TrendCategory
  scale_fill_manual(
    values = c("0" = "#f8d7da", "1" = "#004085"), # Light red vs Deep blue
    labels = c("Absent", "Present"),
    name = "Status"
  ) +
  theme_minimal() +
  labs(
    title = "Species Trend Validation: Occupancy Barcodes",
    subtitle = "Visualizing the 'Sustained' vs 'Sporadic' patterns",
    x = "Year",
    y = "Species Common Name"
  ) +
  theme(
    strip.text = element_text(face = "bold", size = 10),
    panel.grid = element_blank(), # Remove grid lines for a cleaner tile look
    axis.text.y = element_text(size = 8)
  )

## PLOT 2: Looking Across surveys for individual species view
# 1. Select the species you want to investigate
# You can change these names to the specific fish you are interested in
selected_spp <- c("Centropristis striata")

plot_data <- data_NE_full %>%
  filter(Species %in% selected_spp) %>%
  # Ensure the status is a factor for the discrete color scale
  mutate(Absence_Presence = factor(Absence_Presence, levels = c(0, 1))) %>%
  filter(SurveyName == "NEFSC Spring Bottom Trawl")

# 2. Create the Plot
ggplot(plot_data, aes(x = Year, y = paste(SpatialName, "-", TrendCategory), fill = Absence_Presence)) +
  geom_tile(color = "white", linewidth = 0.1) +
  # Facet by species name, allowing each species to have its own block
  facet_wrap(~Common, ncol = 1, scales = "free_y") +
  # This function wraps labels that exceed 20 characters
  scale_y_discrete(labels = scales::label_wrap(20)) +
  scale_fill_manual(
    values = c("0" = "#f8d7da", "1" = "#004085"), # Light red (absent) vs Deep blue (present)
    labels = c("Absent", "Present"),
    name = "Status"
  ) +
  theme_minimal() +
  labs(
    title = "Regional Occupancy Barcodes by Species",
    subtitle = "Comparing presence/absence patterns across different fish surveys",
    x = "Year",
    y = "Fishery Management Council"
  ) +
  theme(
    # Make the species headers bold and distinct
    strip.text = element_text(face = "bold", size = 12, color = "darkslategrey"),
    # Clean up the background
    panel.grid = element_blank(),
    # Adjust survey labels to be readable
    axis.text.y = element_text(size = 8),
    legend.position = "bottom",
    # Add spacing between the species facets
    panel.spacing = unit(1, "lines")
  )

## PLOT 3: Plot barplot with table showing trends
##selected subset of species
selected_spp <- c("Centropristis striata")
plot_data_spring <- data_NE_full %>%
  filter(Species %in% selected_spp) %>%
  # Ensure the status is a factor for the discrete color scale
  mutate(FMC = factor(SpatialName,
                      levels = c("New England", "Mid-Atlantic", "South Atlantic"))) %>%
  filter(SurveyName=="NEFSC Spring Bottom Trawl")

# Convert year to numeric
plot_data_spring$Year <- as.numeric(as.character(plot_data_spring$Year))

## create a summary table for the trends info
library(ggpubr) # Great for arranging tables and plots

# 1. Create the summary table data
summary_tab <- plot_data_spring %>%
  distinct(FMC, TrendCategory, Prop_inc_dec)

# 2. Turn that data into a clean-looking table object
table_plot <- ggtexttable(summary_tab, rows = NULL, theme = ttheme("default"))

##plot the data
color_palette <- scale_fill_manual(
  name = "Jurisdiction", # Legend title
  values = c("#275F6E","#3B8EA5","#D1E3F0")) # Example colors: Blue, Dark Blue, Off-White


barplot <- ggplot(plot_data_spring, aes(x = Year, y = Prop, fill = SpatialName)) +
  geom_bar(stat = "identity", position = "stack", width = 1) +
  # Color palette and legend
  color_palette +
  # Add the trend labels
  # geom_text(data = trend_labels,
  #           aes(x = mid_year, y = 0.5, label = label_text), # y=0.5 places it in the middle height
  #           color = "white",
  #           fontface = "bold",
  #           size = 3,
  #           inherit.aes = FALSE) + # Important: prevents geom_text from looking for 'fill'
  facet_wrap(~ Species, ncol = 2) +
  labs(title = "Biomass Proportions with Significant Trends (p < 0.05)",
       x = "Year", y = "Proportion") +
  theme(
    strip.text = element_text(hjust = 0), # Align species titles left
    legend.position = "bottom",
    axis.text.x = element_text(angle = 0)
  )

final_output <- ggarrange(barplot, table_plot, ncol=1, heights=c(2,1))


################## STOP HERE #########################################

#### COMBINED FULL DATASETS ####
#Adding the NE data to the data_percentiles_export
data_percentiles_Full <- data_percentiles_export %>%
  mutate(Prop = 1,
         SpatialGroup = "Survey wide",
         SpatialName = SurveyName) %>%
  mutate(Absence_Presence = ifelse(WTCPUE == 0, "0",
                                   ifelse(WTCPUE > 0, "1", "NA")))
data_percentiles_Full$Absence_Presence <- as.numeric(data_percentiles_Full$Absence_Presence)

data_NE_prop<- data_NE_full %>%
  select(Region, SurveyName, FMC, Species, Common, Year, Absence_Presence, WTCPUE, Prop) %>%
  dplyr::rename(SpatialName = FMC) %>%
  mutate(SpatialGroup = "Northeast FMC")

data_percentiles_spatialgroup <- bind_rows(data_percentiles_Full, data_NE_prop)

#Adding the NE data to the data_trend_export
data_trend_full <- data_trend_export %>%
  mutate(SpatialGroup = "Survey wide",
         SpatialName = SurveyName)

data_NE_trend<- data_NE_full %>%
  select(Region, SurveyName, FMC, Species, Common, TrendCategory, Prop_inc_dec) %>%
  dplyr::rename(SpatialName = FMC) %>%
  mutate(SpatialGroup = "Northeast FMC") %>%
  distinct()

data_trend_spatialgroup <- bind_rows(data_trend_full, data_NE_trend)

#### Data Export ####
#export percentiles data (used for chicklets graph)
write.csv(data_percentiles_spatialgroup, here::here("data_processing_rcode","output","data_clean","SpeciesPersistenceIndicatorPercentileBin_SpatialGroup.csv"))

#export the trend data (used for category and direction indicators)
write.csv(data_trend_spatialgroup, here::here("data_processing_rcode","output","data_clean","SpeciesPersistenceIndicatorTrendCategories_SpatialGroup.csv"))

