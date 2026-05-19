## Run this code following the Compile_Dismap_Current.R script ##
### This will update the Species Filter table ###

# Each year, read in the previous year's Species Filter to work off of
species_filter_old <- read_csv(here::here("data_processing_rcode", "Species_Filter.csv")) %>%
  select(-DistributionProjectName)

### ### Hawaii ### ###
# Hawaii has different processing so it should be removed and then re-attachced at the end of the Species Filter processing each year
## Update if there are changes. This is accurate as of August 2025
hawaii <- species_filter_old %>%
  filter(FilterSubRegion == "Hawai'i Islands")

hawaii$DistributionProjectName <- rep("NMFS/Rutgers IDW Interpolation", length.out = nrow(hawaii))
### ### ### ### ###

# We will use the `dat.exploded` to identify the species that need to be included in this year's Species Filter
data <- dat.exploded %>%
  select(region, spp, common, DistributionProjectName) %>%
  distinct() %>%
  rename(Region = region,
         Species = spp,
         CommonName = common)

# Add Region column so that this df can join to last year's Species Filter
data$FilterSubRegion <- ifelse(data$Region == "Aleutian Islands", "Aleutian Islands",
                               ifelse(data$Region == "Eastern Bering Sea", "Eastern Bering Sea",
                                      ifelse(data$Region == "Northern Bering Sea", "Northern Bering Sea",
                                             ifelse(data$Region == "Gulf of Mexico", "Gulf of Mexico",
                                                    ifelse(data$Region == "Gulf of Alaska", "Gulf of Alaska",
                                                           ifelse(data$Region == "Northeast US Fall", "Northeast US",
                                                                  ifelse(data$Region == "Northeast US Spring", "Northeast US",
                                                                         ifelse(data$Region == "Southeast US Fall", "Southeast US",
                                                                                ifelse(data$Region == "Southeast US Spring", "Southeast US",
                                                                                       ifelse(data$Region == "Southeast US Summer", "Southeast US",
                                                                                              ifelse(data$Region == "West Coast Annual", "West Coast",
                                                                                                     ifelse(data$Region == "West Coast Triennial", "West Coast",
                                                                                                            ifelse(data$Region == "Eastern and Northern Bering Sea", "Eastern and Northern Bering Sea", NA)))))))))))))

data <- data %>%
  select(-Region) %>%
  distinct() %>%
  replace_na(list(DistributionProjectName = "Not for IDW"))

### quick checks ###
#There might be some repeats here (e.g., a row w/IDW and without)
to_add <- data %>%
  anti_join(species_filter_old, by = c("FilterSubRegion", "Species", "CommonName"))

to_remove <- species_filter_old %>%
  anti_join(data, by = c("FilterSubRegion", "Species", "CommonName"))
###############


#To avoid duplicate relationships in the join #
## In cases that there is a row that For IDW and a row that is not for IDW (ex. if its IDW for one season of a particular region but not the other),
## this code will prioritize the row that lists it's for IDW over the row that says it isn't for IDW
data_priority <- data %>%
  mutate(
    priority = case_when(
      DistributionProjectName == "NMFS/Rutgers IDW Interpolation" ~ 1,
      DistributionProjectName == "Not for IDW" ~ 2,
      TRUE ~ 3 # For any other possible values, lowest priority
    )
  ) %>%
  group_by(FilterSubRegion, Species, CommonName) %>%
  slice_min(order_by = priority, n = 1, with_ties = FALSE) %>%
  ungroup() %>%
  select(-priority)


species_filter_new <- species_filter_old %>%
  right_join(data_priority, by = c("FilterSubRegion", "Species", "CommonName")) %>%
  rbind(hawaii)

write.csv(species_filter_new, file=here("data_processing_rcode", "Species_Filter.csv"))
## Write the csv^ and then check for any NA entries (taxon and FMP info)! ##
### These are new species and need to be filled in manually ###


#### END #####

### ENBS section ###
enbs <- data %>%
  filter(FilterSubRegion == "Eastern and Northern Bering Sea") %>%
  select(-FilterSubRegion)

filt_ak <- species_filter_old %>%
  filter(FilterSubRegion == "Eastern Bering Sea" | FilterSubRegion == "Northern Bering Sea") %>%
  select(-FilterSubRegion)

enbs_join <- enbs %>%
  left_join(filt_ak, by = c("Species", "CommonName"))
# write.csv(enbs_join, "enbs_join.csv")
