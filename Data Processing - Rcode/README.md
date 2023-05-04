# DisMAP

We follow these steps to update the DisMAP data annually.
---
## Prepare data_raw/ directory for new data files ###
Make sure there is a data_raw directory within the DisMAP directory.

---
## Acquire new data.  ###
Run the download_x.R scripts found in the "R" directory within the DisMAP directory.  Some notes:
1. For regions in Alaska, you can download the data via the API from the Fisheries One Stop Shop at https://www.fisheries.noaa.gov/foss/f?p=215:28:15463939570639::::: 

2. WCTRI is no longer active and so the wctri files in the data_raw directory remain the current files to use each year.  Do not delete them.

3. For Gulf of Mexico (GMEX), you have to visit the website in the script and download the files to the Downloads folder manually, the script will copy them over to the correct location once they have been downloaded.

4. For Northeast US (NEUS), you have to reach out directly to the survey folks (Philip Politis)

5. For Southeast US (SEUS), you have to visit the website in the script and download the files to the Downloads folder manually, the script will copy them over to the correct location once they have been downloaded.

6. For Hawai'i you have to reach out to Ben Richards. 

---
## Run compile.R script ###
   1. Make sure the directory is set to the folder containing [compile.R](https://github.com/mpinsky/OceanAdapt/blob/master/compile.R), which should be the top level
   2. Run the script. It will access the raw files, making specific corrections/ standardizations to data format and content, and calculating statistics etc.
   3. After running Compile_Dismap.R, run the create_data_for_map_generation.R to get the data in the needed file format for use in the Python script and genarte the interpolated biomass and indicators (as described below)
---
