####Introduction ####
#title: 'Species Persistence: Data Processing and Visualization'
# author: "NOAA Fisheries' Office of Science and Technology"
# date: "2026-3-6"
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
    # + Established,
    # + Potentially Emerging,
    # + Potentially Disappearing,
    # + Disappeared,
    # + Sporadic

#### Load Packages ####
library(here)
library(dplyr)
library(ggplot2)
library(RColorBrewer)
library(readr)
library(tidyverse)
library(broom)

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
# Absent:	Never/rarely detected.
# Emerged:	Was historically absent/rare, followed by a clear, sustained "break" into consistent presence.
# Disappeared:	Was historically common, followed by a sustained absence.
# Potentially Emerging:	A recent "spike" in detections after a period of absence, but not yet sustained enough to be "Emerged."
# Potentially Disappearing:	A recent "drop" in detections. Still present in the middle of the series, but missing recently.
# Sporadic:	Oscillates in and out without a clear directional trend.

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

#add_trend_category function
add_trend_category <- function(data){
  data %>%
    arrange(Region, SurveyName, Species, Common, Year) %>%
    group_by(Region, SurveyName, Species, Common) %>%
    group_modify(~{
      df <- .x
      n_years <- nrow(df)
      abs_vec <- as.numeric(df$Absence_Presence)

      # 1. Basic Stats
      percent_present <- mean(abs_vec, na.rm = TRUE)

      # 2. Windowed Stats (First 1/3 vs Last 1/3)
      third_n <- max(1, floor(n_years / 3))
      first_third <- abs_vec[1:third_n]
      last_third  <- abs_vec[(n_years - third_n + 1):n_years]

      mean_first <- mean(first_third, na.rm = TRUE)
      mean_last  <- mean(last_third, na.rm = TRUE)

      # 3. Recent Window (Last 5 years)
      last5_idx <- (max(1, n_years - 4)):n_years
      recent_5  <- abs_vec[last5_idx]
      sum_recent_5 <- sum(recent_5, na.rm = TRUE)

      # 4. New logic for the last 10 years
      last10_n <- min(10, n_years)
      last10_idx <- (n_years - last10_n + 1):n_years
      recent_10 <- abs_vec[last10_idx]
      mean_recent_10 <- mean(recent_10, na.rm = TRUE)

      # 3. Recent Window (Last 10 years)
      last10_idx <- (max(1, n_years - 9)):n_years
      recent_10  <- abs_vec[last10_idx]
      sum_recent_10 <- sum(recent_10, na.rm = TRUE)

      # 5. Run Length Encoding (Streaks)
      # Calculates the length of the final 'streak' of 1s or 0s
      runs <- rle(abs_vec)
      last_run_val <- tail(runs$values, 1)
      last_run_len <- tail(runs$lengths, 1)

      # 5. Logic Hierarchy (Established vs. Trending)
      trend_category <- case_when(

        # 1. PERSISTENTLY PRESENT
        # Species that were ALWAYS high (not a new establishment)
        # and any absences are not a recent streak of 3+ absences
        percent_present >= 0.85 & !(last_run_val == 0 & last_run_len >= 3)
        ~"Persistently Present",

        # 2, ABSENT / VAGRANT
        # It was very rarely seen (percent_present <= 0.05)
        # and if caught the hits aren't a recent streak of presences
        percent_present <= 0.05 & !(last_run_val == 1 & last_run_len >= 3) ~ "Absent",

        # 3. ESTABLISHED / SUSTAINED (Emerged + Stabilized)
        # Low start/Sporadic start that is now high and consistent
        #A species that has "stabilized" usually satisfies two conditions:
        #High recent occupancy: They are present in almost all of the most recent years
        #Low early occupancy: They were infrequent or absent in the beginning of the time series.
        (mean_first <= 0.50 & mean_last >= 0.85 & last_run_val == 1 & last_run_len >=5) ~ "Established",

        # 4. POTENTIALLY EMERGING
        # Trend is upward, caught recently, but not 'solid' yet
        (mean_first <= 0.50 & mean_first < mean_last & sum_recent_5 >= 4) ~ "Potentially Emerging",

        # 5. DISSAPPEARED / SUSTAINED ABSENCE
        # high start, but gone now
        (mean_first >= 0.50 & mean_last <= 0.15 & last_run_val == 0 & last_run_len >=5)
        ~ "Dissappeared",

        # 6. POTENTIALLY DISAPPEARING
        (mean_first >= 0.50 & mean_first > mean_last & sum_recent_5 <= 1) ~ "Potentially Disappearing",

        # 7. SPORADIC
        TRUE ~ "Sporadic"
      )

      df$TrendCategory <- trend_category
      return(df)
    }) %>%
    ungroup()
}

# Usage:
# This data frame will be used below in the flagging function
data_for_flag <- add_trend_category(data_cumm_ce) %>%
  mutate(Name = paste(Common, SurveyName, sep = "_"))

# This dataframe will be used for vizualization and plotting to validate trends
data_cat_plot <- add_trend_category(data_cumm_ce) %>%
  mutate(SurveyName = as.character(SurveyName),
         Species = as.character(Species))

# This dataframe will be used for the final data exporting
data_cat <- add_trend_category(data_cumm_ce) %>%
  select(Region, SurveyName, Species, Common, TrendCategory) %>%
  distinct() %>%
  mutate(SurveyName = as.character(SurveyName),
         Species = as.character(Species))

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

#### Visualization and Validation ####
#visualize, check, validate
#PLOT 1: Validation of Trend Categories
# 1. Select one representative species for each category
examples <-  data_cat_plot %>%
  group_by(TrendCategory) %>%
  slice_sample(n = 1) %>%
  pull(Common)

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

####MANAGEMENT COUNCIL JURISDICTION ANALYSIS (for the NEFSC survey data only)####
#The following script does the same analysis as above, but parses the NE Bottom trawl data out into the two different management council jurisdictions.

library(sf)
library(dplyr)

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
# Plot_FMC<- ggplot() +
#   geom_sf(data = EC_Councils, aes(fill = FishRegion), alpha = 0.3) +
#   #geom_point(data = df_NEUS, aes(x=lon, y=lat, color = FishRegion)) +
#   theme_minimal() +
#   labs(title = "Points Labeled by Fishery Management Council Jurisdiction")

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

add_trend_category <- function(data){
  data %>%
    arrange(region, FishRegionsurvey, spp, common, year) %>%
    group_by(region, FishRegionsurvey, spp, common) %>%
    group_modify(~{
      df <- .x
      n_years <- nrow(df)
      abs_vec <- as.numeric(df$Absence_Presence)

      # 1. Basic Stats
      percent_present <- mean(abs_vec, na.rm = TRUE)

      # 2. Windowed Stats (First 1/3 vs Last 1/3)
      third_n <- max(1, floor(n_years / 3))
      first_third <- abs_vec[1:third_n]
      last_third  <- abs_vec[(n_years - third_n + 1):n_years]

      mean_first <- mean(first_third, na.rm = TRUE)
      mean_last  <- mean(last_third, na.rm = TRUE)

      # 3. Recent Window (Last 5 years)
      last5_idx <- (max(1, n_years - 4)):n_years
      recent_5  <- abs_vec[last5_idx]
      sum_recent_5 <- sum(recent_5, na.rm = TRUE)

      # 4. New logic for the last 10 years
      last10_n <- min(10, n_years)
      last10_idx <- (n_years - last10_n + 1):n_years
      recent_10 <- abs_vec[last10_idx]
      mean_recent_10 <- mean(recent_10, na.rm = TRUE)

      # 3. Recent Window (Last 10 years)
      last10_idx <- (max(1, n_years - 9)):n_years
      recent_10  <- abs_vec[last10_idx]
      sum_recent_10 <- sum(recent_10, na.rm = TRUE)

      # 5. Run Length Encoding (Streaks)
      # Calculates the length of the final 'streak' of 1s or 0s
      runs <- rle(abs_vec)
      last_run_val <- tail(runs$values, 1)
      last_run_len <- tail(runs$lengths, 1)

      # 5. Logic Hierarchy (Established vs. Trending)
      trend_category <- case_when(

        # 1. PERSISTENTLY PRESENT
        # Species that were ALWAYS high (not a new establishment)
        # and any absences are not a recent streak of 3+ absences
        percent_present >= 0.85 & !(last_run_val == 0 & last_run_len >= 3)
        ~"Persistently Present",

        # 2, ABSENT / VAGRANT
        # It was very rarely seen (percent_present <= 0.05)
        # and if caught the hits aren't a recent streak of presences
        percent_present <= 0.05 & !(last_run_val == 1 & last_run_len >= 3) ~ "Absent",

        # 3. ESTABLISHED / SUSTAINED (Emerged + Stabilized)
        # Low start/Sporadic start that is now high and consistent
        #A species that has "stabilized" usually satisfies two conditions:
        #High recent occupancy: They are present in almost all of the most recent years
        #Low early occupancy: They were infrequent or absent in the beginning of the time series.
        (mean_first <= 0.50 & mean_last >= 0.85 & last_run_val == 1 & last_run_len >=5) ~ "Established",

        # 4. POTENTIALLY EMERGING
        # Trend is upward, caught recently, but not 'solid' yet
        (mean_first <= 0.50 & mean_first < mean_last & sum_recent_5 >= 4) ~ "Potentially Emerging",

        # 5. DISSAPPEARED / SUSTAINED ABSENCE
        # high start, but gone now
        (mean_first >= 0.50 & mean_last <= 0.15 & last_run_val == 0 & last_run_len >=5)
        ~ "Dissappeared",

        # 6. POTENTIALLY DISAPPEARING
        (mean_first >= 0.50 & mean_first > mean_last & sum_recent_5 <= 1) ~ "Potentially Disappearing",

        # 7. SPORADIC
        TRUE ~ "Sporadic"
      )

      df$TrendCategory <- trend_category
      return(df)
    }) %>%
    ungroup()
}

# Add the trend categories to the dataframe
data_NE_cat <- add_trend_category(data_NE_spatial) %>%
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
                FMC = FishRegion,
                Common = common,
                Species = spp,
                Year = year,
                WTCPUE = FMCwtcpue,
                Prop = prop) %>%
  select(-Totwtcpue, -FishRegionsurvey, -col, -ext)

data_NE_full <- data_NE_full %>%
    mutate(FMC_new = ifelse(data_NE_full$FMC == "New England", "New England",
                       ifelse(data_NE_full$FMC == "NEMA", "Mid-Atlantic",
                              ifelse(data_NE_full$FMC == "South Atlantic", "South Atlantic", NA)))) %>%
    select(-FMC) %>%
    dplyr::rename(FMC = FMC_new)


write.csv(data_NE_full, here::here("data_processing_rcode","output","data_clean","NEFSC_FMC_SpeciesPersistenceIndicatorTrend.csv"))

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
ggplot(plot_data, aes(x = Year, y = paste(FMC, "-", TrendCategory), fill = Absence_Presence)) +
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
  mutate(FMC = factor(FMC,
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


barplot <- ggplot(plot_data_spring, aes(x = Year, y = Prop, fill = FMC)) +
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

