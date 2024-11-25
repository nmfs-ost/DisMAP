##Use this script to update the Filter Table when data is updated, and check if any new species need to be described in the table 
Filter_list<-read.csv("Species_Filter.csv", header=T, sep=",")

#change region name for matching with filter table 
spp_survey$FilterSubRegion<-ifelse(spp_survey$region=="Aleutian Islands","Aleutian Islands",
                                      ifelse(spp_survey$region=="Eastern Bering Sea", "Eastern Bering Sea",
                                             ifelse(spp_survey$region=="Gulf of Alaska", "Gulf of Alaska",
                                                    ifelse(spp_survey$region=="Bering Sea Combined", "Bering Sea Combined",
                                                           ifelse(spp_survey$region=="Northern Bering Sea", "Northern Bering Sea",
                                                                  ifelse(spp_survey$region=="Gulf of Mexico", "Gulf of Mexico",
                                                                         ifelse(spp_survey$region=="West Coast Triennial", "West Coast",
                                                                                ifelse(spp_survey$region=="West Coast Annual", "West Coast",
                                                                                       ifelse(spp_survey$region=="Northeast US Spring", "Northeast",
                                                                                              ifelse(spp_survey$region=="Northeast US Fall", "Northeast",
                                                                                                     ifelse(spp_survey$region=="Southeast US Spring", "Southeast",
                                                                                                            ifelse(spp_survey$region=="Southeast US Summer", "Southeast",
                                                                                                                   ifelse(spp_survey$region=="Southeast US Fall", "Southeast", NA)))))))))))))
spp_survey<- spp_survey%>%
  select(spp, common, FilterSubRegion) %>%
  distinct()%>%
  filter(FilterSubRegion!="Bering Sea Combined")

Filter_updated<-left_join(spp_survey, Filter_list, by=c("spp", "common", "FilterSubRegion"))
write.csv(Filter_updated, "Filter_list_updated.csv")
