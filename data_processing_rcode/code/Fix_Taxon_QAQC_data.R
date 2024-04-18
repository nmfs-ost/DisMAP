# clean Taxon QAQC Sheet ===============================================================
print("Clean & Compile TAX")
source("clean_taxa.R")

#load in existing full cleaned Taxa list 
full_tax<-read.csv("taxa_analysis/Taxa_clean_to_Compare.csv", sep=",", header=T)

# Get WoRM's id for sourcing
wrm <- gnr_datasources() %>% 
  filter(title == "World Register of Marine Species") %>% 
  pull(id)

#Full unfiltered data set
dat <- rbind(ai, ebs, gmex, goa, nbs, neus_fall, neus_spring, seusFALL, seusSPRING, seusSUMMER, wcann, wctri) %>% 
  # Remove NA values in wtcpue
  filter(!is.na(wtcpue)) %>%
  # remove any extra white space from around spp names
  mutate(spp= str_squish(spp))

### Automatic cleaning
dat<- dat %>% 
  mutate(
    taxa2 = str_squish(spp),
    taxa2 = str_remove_all(taxa2," spp\\.| sp\\.| spp|"),
    taxa2 = str_to_sentence(str_to_lower(taxa2)))

# Set Survey code
All_srvy_code <- "All-svry"

clean_auto <- clean_taxa(unique(dat$taxa2),
                         input_survey = All_srvy_code,
                         save = T, output="add", fishbase=T)

Flags<-anti_join(clean_auto, full_tax, by=c("taxa"))
#28 entries that dont match. But that is ok. If more than 28 unmatches in future then check-spp list

##merge new and old tax check to see what matches and doesnt match ...
taxa_2<- taxa_2 %>% 
  mutate(
    survey_name = str_squish(survey_name),
    survey_name = str_remove_all(survey_name," spp\\.| sp\\.| spp|"),
    survey_name = str_to_sentence(str_to_lower(survey_name)))

merge_tax<-left_join(taxa_2, clean_auto, by=c("survey_name"="query", "valid_name"="taxa"))
merge_tax_v2<-left_join(clean_auto, taxa_2, by=c("query"="survey_name", "taxa"="valid_name"))

write.csv(merge_tax, "tax_clean_9_29_23.csv")
write.csv(merge_tax_v2, "clean_auto_check.csv")

missing<-read.csv("missing_taxa_check.csv", sep=",", header=T) %>%
  select(survey_name, valid_name, common)

missing_merge<-left_join(missing, clean_auto, by=c("valid_name"="taxa"))
write.csv(missing_merge, "add_missing_cleaned.csv")

missing_merge_v2<-left_join(missing, clean_auto, by=c("survey_name"="query"))

remaining<-read.csv("remaining_missing_spp.csv", sep=",", header=T)
remaining_merge<-left_join(remaining, clean_auto, by=c("survey_name"="query"))
write.csv(remaining_merge, "remaining_worms_matches.csv")
