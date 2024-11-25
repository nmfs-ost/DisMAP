##Use this script to update the Filter Table when data is updated, and check if any new species need to be described in the table 
Filter_list<-read.csv("Species_Filter.csv", header=T, sep=",")

#change region name for matching with filter table 
spp_survey2<-spp_survey
spp_survey2$FilterSubRegion<-ifelse(spp_survey2$region=="Aleutian Islands","Aleutian Islands",
                                      ifelse(spp_survey2$region=="Eastern Bering Sea", "Eastern Bering Sea",
                                             ifelse(spp_survey2$region=="Gulf of Alaska", "Gulf of Alaska",
                                                    ifelse(spp_survey2$region=="Bering Sea Combined", "Bering Sea Combined",
                                                           ifelse(spp_survey2$region=="Northern Bering Sea", "Northern Bering Sea",
                                                                  ifelse(spp_survey2$region=="Gulf of Mexico", "Gulf of Mexico",
                                                                         ifelse(spp_survey2$region=="West Coast Triennial", "West Coast",
                                                                                ifelse(spp_survey2$region=="West Coast Annual", "West Coast",
                                                                                       ifelse(spp_survey2$region=="Northeast US Spring", "Northeast",
                                                                                              ifelse(spp_survey2$region=="Northeast US Fall", "Northeast",
                                                                                                     ifelse(spp_survey2$region=="Southeast US Spring", "Southeast",
                                                                                                            ifelse(spp_survey2$region=="Southeast US Summer", "Southeast",
                                                                                                                   ifelse(spp_survey2$region=="Southeast US Fall", "Southeast", NA)))))))))))))
spp_survey2<- spp_survey2 %>%
  select(spp, common, FilterSubRegion) %>%
  distinct()%>%
  filter(FilterSubRegion!="Bering Sea Combined")

Filter_updated<-left_join(spp_survey2, Filter_list, by=c("spp", "common", "FilterSubRegion")) 
Filter_updated$DistributionProjectName<-ifelse(!is.na(Filter_updated$FilterRegion), "NMFS/Rutgers IDW Interpolation", "Not for IDW")
write.csv(Filter_updated, "Filter_list_Expanded_Survey.csv")


