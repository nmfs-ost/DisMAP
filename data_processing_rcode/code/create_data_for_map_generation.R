
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

write.csv(ai_csv, file.path(OUTPUT_CSV_DIRECTORY, "ai_csv.csv")) 
print ("[Local]: ai_csv.csv output successfully")
write.csv(ebs_csv, file.path(OUTPUT_CSV_DIRECTORY, "ebs_csv.csv"))
print ("[Local]: ebs_csv.csv output successfully") 
write.csv(goa_csv, file.path(OUTPUT_CSV_DIRECTORY, "goa_csv.csv")) 
print ("[Local]: goa_csv.csv output successfully")
write.csv(nbs_csv, file.path(OUTPUT_CSV_DIRECTORY, "nbs_csv.csv")) 
print ("[Local]: nbs_csv.csv output successfully")
write.csv(enbs_csv, file.path(OUTPUT_CSV_DIRECTORY, "enbs_csv.csv")) 
print ("[Local]: enbs_csv.csv output successfully")

write.csv(neusS_csv, file.path(OUTPUT_CSV_DIRECTORY, "neusS_csv.csv")) 
print ("[Local]: neus_csv.csv output successfully")
write.csv(neusf_csv, file.path(OUTPUT_CSV_DIRECTORY, "neusf_csv.csv")) 
print ("[Local]: neusf_csv.csv output successfully")

write.csv(wctri_csv, file.path(OUTPUT_CSV_DIRECTORY, "wctri_csv.csv")) 
print ("[Local]: wctri_csv.csv output successfully")
write.csv(wcann_csv, file.path(OUTPUT_CSV_DIRECTORY, "wcann_csv.csv")) 
print ("[Local]: wcann_csv.csv output successfully")

write.csv(gmex_csv, file.path(OUTPUT_CSV_DIRECTORY, "gmex_csv.csv")) 
print ("[Local]: gmex_csv.csv output successfully")

write.csv(seus_spr_csv, file.path(OUTPUT_CSV_DIRECTORY, "seus_spr_csv.csv")) 
print ("[Local]: seus_spr_csv.csv output successfully")
write.csv(seus_sum_csv, file.path(OUTPUT_CSV_DIRECTORY, "seus_sum_csv.csv")) 
print ("[Local]: seus_sum_csv.csv output successfully")
write.csv(seus_fal_csv, file.path(OUTPUT_CSV_DIRECTORY, "seus_fal_csv.csv")) 
print ("[Local]: seus_fal_csv.csv output successfully")