## The code below shows how to download the various data products available for DisMAP through 
#the ESRI and fisheries map server API. 
#This data includes: 
#   - indicators table which includes information on the COG lat, depth, lon of each species
#   - interpolated biomass raster layers 
#   - survey points 

## IMPORTANT INSTRUCTIONS####
## The data URLs referenced in this code can be found in the DisMAP inPort records under the Distribution information: 
## Check the inport page for DisMAP for the most up-to-date URLS for each data product: https://www.fisheries.noaa.gov/inport/item/66799
   #look under "Child Items", the numbers at the end of the title indicate the date of the layer in Year-Month-Day format. Click on the data set of interest
    # and use that URL in the steps below (examples for an earlier dataset are provided below)
# for the indicators table: https://services2.arcgis.com/C8EMgrsFcRFL6LrL/arcgis/rest/services/Indicators_20220516/FeatureServer
# for the survey data: https://www.fisheries.noaa.gov/inport/item/67366
# for the interpolated biomass layers: https://www.fisheries.noaa.gov/inport/item/67368

## Please see our technical report for more details on how the analysis and data found in the DisMAP portal
#  https://apps-st.fisheries.noaa.gov/dismap/DisMAP.html   

#load required packages 
library(jsonlite)
library(dplyr)
library(raster)
library(rgdal)
library(sp)
library(ggplot2)
library(rasterVis)
library(httr)
library(gganimate)
library(maps)
#install.packages("ggthemes")
library(ggthemes)
library(gifski)
#install.packages("gapminder")
library(gapminder)
library(dplyr)
require(viridis)
#install.packages("mapdata")
library(mapdata)
#install.packages("cmocean")
library(cmocean)
#install.packages("tidyverse")
library(tidyverse)
#install.packages("exactextractr")
library(exactextractr)
library(sf)


#### 1. Querying the INDICATORS TABLE ####
#Query the Distribution indicators table (switch out common name with desired species common name, and Region
# with desired region for the selected species (or remove the Region portion if want all regions for
# a given species))
###Available Regions include: "Aleutian Islands", "Eastern Bering Sea", "Gulf of Alaska", "West Coast Triennial",
#                           "West Coast Annual", "Gulf of Mexico", "Northeast US Spring", "Northeast US Fall",
#                           "Southeast US Fall", "Southeats US Spring", "Southeast US Summer", "Northern Bering Sea", "Eastern and Northern Bering Sea"

## Example for American Lobster in Northeast US Spring
url <- parse_url("https://services2.arcgis.com/C8EMgrsFcRFL6LrL/ArcGIS/rest/services")
url$path <- paste(url$path, "Indicators_20220516/FeatureServer/3/query", sep = "/")
url$query <- list(where = "CommonName = 'American lobster' AND OARegion='Northeast US Spring'",
                  outFields = "*",
                  f = "geojson")
request <- build_url(url)

ALob_metrics <- st_read(request)
ALob_COG<-as.data.frame(ALob_metrics)
ALob_COG<-ALob_COG %>%
  rename(lon=CenterOfGravityLongitude,
         lat=CenterOfGravityLatitude)
write.csv(ALob_COG, "ALob_COG_change.csv")

COG_change<-ggplot() + 
  geom_point(data=ALob_COG, aes(x=lon, y=lat, col=Year)) +
  theme_classic() +  labs(y="", x="") + 
  theme( panel.border = element_rect(colour = "black", fill=NA, size=1)) + #makes a box
  annotation_map(map_data("world"), colour = "black", fill="grey50")+
  coord_quickmap(xlim=c(-80,-65),ylim=c(33,45)) +  #Sets aspect ratio
  scale_x_continuous(expand = c(0, 0)) +  scale_y_continuous(expand = c(0, 0))


#### 2. Downloading INTERPOLATED BIOMASS RASTERS ####
  ## Example for Summer Flounder in NEUS Spring
  #Get the sliceIDs that correspond to Summer Flounder in NEUS Spring. There will be a unique slice ID for each species-year pair within each region
  ##Note that the URLs may change with data updates (mainly just the #s at the end that indicate the date, e.g., the 20220516 would change to reflect new date)
  # make sure to double check the URLs for the data layer you want by going to the InPort page, clicking on Fish and Invertebrate Interpolated Biomass Distribution 
    #surfaces for the data release date you want, and then scrolling down to the Distribution section and checking the URL for the region of interest. Swap out that 
    #URL for everything before the /slices in the below, and /exportImage in the next step ... 
    SumFl_slices <- "https://maps.fisheries.noaa.gov/image/rest/services/DisMAP/Northeast_US_Spring_20220516/ImageServer/slices?multidimensionalDefinition=%5B%7B%22variableName%22%3A+%22Paralichthys+dentatus%22%7D%5D&f=pjson"
    header_type <- "applcation/json"
    response<-GET(SumFl_slices)
    text_json <- content(response, type = 'text', encoding = "UTF-8")
    jfile <- fromJSON( text_json)
    df <- as.data.frame(jfile)
    
  #now to use the exportImage function of ESRI API to export the raster images for Summer Flounder based on the slice #s in df
    #and save the rasters in folder on your local computer 
    ##loop through the sliceIDs (can see the slice in the file "df")
    ## replace the #s with the first and last slice ID that can be found in the 'df' generaged in previous step 
    for (i in c(2112:2155)){ 
        print(paste0("Downloading raster image for slice ", i))
          
        url<-httr::parse_url("https://maps.fisheries.noaa.gov/image/rest/services/DisMAP/Northeast_US_Spring_20220516/ImageServer/exportImage")
        
        query_arg <- list(imageSR = "4326",
                          format = "tiff",
                          pixelType = "F32",
                          #noData = "3.4e38",
                          noDataInterpretation = "esriNoDataMatchAny",
                          interpolation = "+RSP_BilinearInterpolation",
                          sliceID = i,
                          f = "json")
       
        bbox_arg <- list(bbox = paste(    #note that the bounding box will be different for each region! 
          min(7808000),
          min(3950000),
          max(8228000),
          max(5212000),
          sep = ","
        ))
        
        res <- httr::GET(url, query = c(bbox_arg, query_arg))
        
        tmpfile <-tempfile()
        content <-httr::content(res, type = "application/json")
        
        httr::RETRY("GET", content$href, 
                    httr::progress(), 
                    httr::write_disk(tmpfile),
                    times = 10, pause_cap = 10)
        r <-raster(tmpfile)
        
        #save raster
        fname<-paste0("SummerFlounder","_", i)
        writeRaster(r, paste0("SummerFlounder_NE_spring", "/", fname), overwrite=TRUE)
      }
      
      ## load in the saved rasters into R...
        dir<-"" #NOTE: here will need to add in your dir, which is the local directory that points to where raster data is stored 
   
        files_SumFl_NEspring<-list.files(paste0(dir, '/SummerFlounder_NE_Spring'), full.names=TRUE, pattern=".grd")
        years<-seq(1974, 2019)
        yearsEx<-years[years!=1975]
        yearsEx<-yearsEx[yearsEx!=2014]
        output <- as.data.frame(matrix(NA, nrow=160000*44,ncol=4)) #160000 non-NA grid cells in raster (use:  rNA <- !is.na(SmFl)), 44 is the # of years
        colnames(output) <- c("lon","lat","year","wtcpue")
        
        #----Loop through the slices----
        #s is the year, so loop through the 44 years
        for (s in 1:44){
          SmFl <- raster(files_SumFl_NEspring[s])
          plot(SmFl)
         ###Extract data for each 'slice' (which corresponds to each year)
          print("Extracting Data")
          ei <- 160000*s #end location in output grid to index to
          se <- ei - (160000-1) #start location in output grid to index to
          output$lat[se:ei] <- rasterToPoints(SmFl)[,2]
          output$lon[se:ei] <- rasterToPoints(SmFl)[,1]
          output$year[se:ei] <- rep(yearsEx[s],160000)
          output$wtcpue[se:ei] <- rasterToPoints(SmFl)[,3] 
        }
       
        #NOTE: need to mutate data frame so that values of 3.4e+38 which is what is given to "no data" is switched to NA, 
        #and add a new column where wtcpue values are cube-rooted. The cube-root provides for better visualizations
      SmFl_Spring_data<-output %>%
        mutate(
          wtcpue = ifelse(wtcpue>3000, NA, wtcpue),
          #wtcpue = ifelse(wtcpue == 0, NA, wtcpue),
          cuberoot_wtcpue = (wtcpue)^(1/3))
          #can also chose to make 0's NA as well. This is what we did for DisMAP, so only areas of positive predicted biomass are shown 
          # as colors in the distribution map. We felt this makes it easier to see some of the trends. 
      
      write.csv(SmFl_Spring_data, "SummerFlounder_NEUS_spring_data.csv")
     
      ### Example of how to make animated GIFs of the distribution 
     SmFl_NEUS_spring <- ggplot(data = SmFl_Spring_data, aes(x=lon,y=lat))+
        geom_tile(aes(fill=cuberoot_wtcpue))+
        theme_classic() +  labs(y="", x="") + 
        theme(legend.position="right",legend.title = element_blank())+
        theme( panel.border = element_rect(colour = "black", fill=NA, size=1)) + #makes a box
        scale_fill_gradientn(colours = cmocean("matter")(256),limits = c(0, max(SmFl_Spring_data$cuberoot_wtcpue))) +
        annotation_map(map_data("world"), colour = "black", fill="grey50")+
        coord_quickmap(xlim=c(-78,-65),ylim=c(34,48)) +  #Sets aspect ratio
        scale_x_continuous(expand = c(0, 0)) +  scale_y_continuous(expand = c(0, 0))+
        transition_time(year)+
        ease_aes("linear") +
        labs(title="Summer Flounder NEUS Spring {frame_time}") #takes some time 
      
      SmFl_annimated <- gganimate::animate(SmFl_NEUS_spring,nframes = 44, fps=2, renderer = gifski_renderer())#renders in 
      anim_save('SmFl_NEUS_spring.gif', SmFl_annimated)
      

#### 3. Survey points ####
      url <- parse_url("https://services2.arcgis.com/C8EMgrsFcRFL6LrL/ArcGIS/rest/services")
      url$path <- paste(url$path, "Eastern_Bering_Sea_Survey_Locations_20220516/FeatureServer/1/query", sep = "/")
      url$query <- list(where = "OARegion='Eastern Bering Sea'",
                        outFields = "*",
                        f = "geojson")
      request <- build_url(url)
      
      selected_regions <- st_read(request)
      selected_regions<-as.data.frame(selected_regions)