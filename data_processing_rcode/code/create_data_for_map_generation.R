
OUTPUT_CSV_DIRECTORY = "~/transfer/DisMAP project/DisMAP/data_processing_rcode/output/python"

# dat.exploded should have already be created

print ("[Local]: CSV Tables are being prepped.")
ai_csv = dat.exploded[dat.exploded$region %in% c('Aleutian Islands'),]
ebs_csv = dat.exploded[dat.exploded$region %in% c('Eastern Bering Sea'),]
goa_csv = dat.exploded[dat.exploded$region %in% c('Gulf of Alaska'),]
nbs_csv = dat.exploded[dat.exploded$region %in% c('Northern Bering Sea'),]
enbs_csv = dat.exploded[dat.exploded$region %in% c('Bering Sea Combined'),]

neusS_csv = dat.exploded[dat.exploded$region %in% c('Northeast US Spring'),]
neusf_csv = dat.exploded[dat.exploded$region %in% c('Northeast US Fall'),]

wctri_csv = dat.exploded[dat.exploded$region %in% c('West Coast Triennial'),]
wcann_csv = dat.exploded[dat.exploded$region %in% c('West Coast Annual'),]

gmex_csv = dat.exploded[dat.exploded$region %in% c('Gulf of Mexico'),]

seus_spr_csv = dat.exploded[dat.exploded$region %in% c('Southeast US Spring'),]
seus_sum_csv = dat.exploded[dat.exploded$region %in% c('Southeast US Summer'),]
seus_fal_csv = dat.exploded[dat.exploded$region %in% c('Southeast US Fall'),]

print ("[Local]: CSV Tables prepped.")
write.csv(ai_csv, file.path(OUTPUT_CSV_DIRECTORY, "AI_survey.csv")) 
print ("[Local]: ai_csv.csv output successfully")
write.csv(ebs_csv, file.path(OUTPUT_CSV_DIRECTORY, "EBS_survey.csv"))
print ("[Local]: ebs_csv.csv output successfully") 
write.csv(goa_csv, file.path(OUTPUT_CSV_DIRECTORY, "GOA_survey.csv")) 
print ("[Local]: goa_csv.csv output successfully")
write.csv(nbs_csv, file.path(OUTPUT_CSV_DIRECTORY, "NBS_survey.csv")) 
print ("[Local]: nbs_csv.csv output successfully")
write.csv(enbs_csv, file.path(OUTPUT_CSV_DIRECTORY, "ENBS_survey.csv")) 
print ("[Local]: enbs_csv.csv output successfully")

write.csv(neusS_csv, file.path(OUTPUT_CSV_DIRECTORY, "NEUS_SPR_survey.csv")) 
print ("[Local]: neus_csv.csv output successfully")
write.csv(neusf_csv, file.path(OUTPUT_CSV_DIRECTORY, "NEUS_FAL_survey.csv")) 
print ("[Local]: neusf_csv.csv output successfully")

write.csv(wctri_csv, file.path(OUTPUT_CSV_DIRECTORY, "WC_TRI_survey.csv")) 
print ("[Local]: wctri_csv.csv output successfully")
write.csv(wcann_csv, file.path(OUTPUT_CSV_DIRECTORY, "WC_ANN_survey.csv")) 
print ("[Local]: wcann_csv.csv output successfully")

write.csv(gmex_csv, file.path(OUTPUT_CSV_DIRECTORY, "GMEX_survey.csv")) 
print ("[Local]: gmex_csv.csv output successfully")

write.csv(seus_spr_csv, file.path(OUTPUT_CSV_DIRECTORY, "SEUS_SPR_survey.csv")) 
print ("[Local]: seus_spr_csv.csv output successfully")
write.csv(seus_sum_csv, file.path(OUTPUT_CSV_DIRECTORY, "SEUS_SUM_survey.csv")) 
print ("[Local]: seus_sum_csv.csv output successfully")
write.csv(seus_fal_csv, file.path(OUTPUT_CSV_DIRECTORY, "SEUS_FAL_survey.csv")) 
print ("[Local]: seus_fal_csv.csv output successfully")

## Old script for generated the data for IDW... the new script has file name change b/c its the expanded survey data
# write.csv(ai_csv, file.path(OUTPUT_CSV_DIRECTORY, "AI_IDW.csv")) 
# print ("[Local]: ai_csv.csv output successfully")
# write.csv(ebs_csv, file.path(OUTPUT_CSV_DIRECTORY, "EBS_IDW.csv"))
# print ("[Local]: ebs_csv.csv output successfully") 
# write.csv(goa_csv, file.path(OUTPUT_CSV_DIRECTORY, "GOA_IDW.csv")) 
# print ("[Local]: goa_csv.csv output successfully")
# write.csv(nbs_csv, file.path(OUTPUT_CSV_DIRECTORY, "NBS_IDW.csv")) 
# print ("[Local]: nbs_csv.csv output successfully")
# write.csv(enbs_csv, file.path(OUTPUT_CSV_DIRECTORY, "ENBS_IDW.csv")) 
# print ("[Local]: enbs_csv.csv output successfully")
# 
# write.csv(neusS_csv, file.path(OUTPUT_CSV_DIRECTORY, "NEUS_SPR_IDW.csv")) 
# print ("[Local]: neus_csv.csv output successfully")
# write.csv(neusf_csv, file.path(OUTPUT_CSV_DIRECTORY, "NEUS_FAL_IDW.csv")) 
# print ("[Local]: neusf_csv.csv output successfully")
# 
# write.csv(wctri_csv, file.path(OUTPUT_CSV_DIRECTORY, "WC_TRI_IDW.csv")) 
# print ("[Local]: wctri_csv.csv output successfully")
# write.csv(wcann_csv, file.path(OUTPUT_CSV_DIRECTORY, "WC_ANN_IDW.csv")) 
# print ("[Local]: wcann_csv.csv output successfully")
# 
# write.csv(gmex_csv, file.path(OUTPUT_CSV_DIRECTORY, "GMEX_IDW.csv")) 
# print ("[Local]: gmex_csv.csv output successfully")
# 
# write.csv(seus_spr_csv, file.path(OUTPUT_CSV_DIRECTORY, "SEUS_SPR_IDW.csv")) 
# print ("[Local]: seus_spr_csv.csv output successfully")
# write.csv(seus_sum_csv, file.path(OUTPUT_CSV_DIRECTORY, "SEUS_SUM_IDW.csv")) 
# print ("[Local]: seus_sum_csv.csv output successfully")
# write.csv(seus_fal_csv, file.path(OUTPUT_CSV_DIRECTORY, "SEUS_FAL_IDW.csv")) 
# print ("[Local]: seus_fal_csv.csv output successfully")