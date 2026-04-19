# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        dev_create_indicators_table_worker
# Purpose:
#
# Author:      john.f.kennedy
#
# Created:     09/03/2024
# Copyright:   (c) john.f.kennedy 2024
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os
import sys
import traceback
import inspect

import arcpy # third-parties second

def printRowContent(region_indicators):
    try:
        arcpy.AddMessage("Print records in the Region Indicators table")

        fields = [f.name for f in arcpy.ListFields(region_indicators) if f.type not in ['Geometry', 'OID']]
        with arcpy.da.SearchCursor(region_indicators, fields) as cursor:
        #with arcpy.da.SearchCursor(region_indicators, fields, "CoreSpecies = 'No'") as cursor:
            for row in cursor:
                #arcpy.AddMessage(', '.join((row)))

                DatasetCode                = row[0]
                Region                     = row[1]
                Season                     = row[2]
                DateCode                   = row[3]
                Species                    = row[4]
                CommonName                 = row[5]
                CoreSpecies                = row[6]
                Year                       = row[7]
                #DistributionProjectName    = row[8]
                DistributionProjectCode    = row[9]
                SummaryProduct             = row[10]
                CenterOfGravityLatitude    = '' if row[11] is None else f'{row[11]:.1f}'
                MinimumLatitude            = '' if row[12] is None else f'{row[12]:.1f}'
                MaximumLatitude            = '' if row[13] is None else f'{row[13]:.1f}'
                OffsetLatitude             = '' if row[14] is None else f'{row[14]:.1f}'
                CenterOfGravityLatitudeSE  = '' if row[15] is None else f'{row[15]:.1f}'
                CenterOfGravityLongitude   = '' if row[16] is None else f'{row[16]:.1f}'
                MinimumLongitude           = '' if row[17] is None else f'{row[17]:.1f}'
                MaximumLongitude           = '' if row[18] is None else f'{row[18]:.1f}'
                OffsetLongitude            = '' if row[19] is None else f'{row[19]:.1f}'
                CenterOfGravityLongitudeSE = '' if row[20] is None else f'{row[20]:.1f}'
                CenterOfGravityDepth       = '' if row[21] is None else f'{row[21]:.1f}'
                MinimumDepth               = '' if row[22] is None else f'{row[22]:.1f}'
                MaximumDepth               = '' if row[23] is None else f'{row[23]:.1f}'
                OffsetDepth                = '' if row[24] is None else f'{row[24]:.1f}'
                CenterOfGravityDepthSE     = '' if row[25] is None else f'{row[25]:.1f}'

                #arcpy.AddMessage(DatasetCode, Region, Season, DateCode, Species, CommonName, CoreSpecies, Year, DistributionProjectName, DistributionProjectCode, SummaryProduct, CenterOfGravityLatitude, MinimumLatitude, MaximumLatitude, OffsetLatitude, CenterOfGravityLatitudeSE, CenterOfGravityLongitude, MinimumLongitude, MaximumLongitude, OffsetLongitude, CenterOfGravityLongitudeSE, CenterOfGravityDepth, MinimumDepth, MaximumDepth, OffsetDepth, CenterOfGravityDepthSE)
                arcpy.AddMessage(f"{DatasetCode}, {Region}, {Season}, {DateCode}, {Species}, {CommonName}, {CoreSpecies}, {Year}, {DistributionProjectCode}, {SummaryProduct}, {CenterOfGravityLatitude}, {MinimumLatitude}, {MaximumLatitude}, {OffsetLatitude}, {CenterOfGravityLatitudeSE}, {CenterOfGravityLongitude}, {MinimumLongitude}, {MaximumLongitude}, {OffsetLongitude}, {CenterOfGravityLongitudeSE}, {CenterOfGravityDepth}, {MinimumDepth}, {MaximumDepth}, {OffsetDepth}, {CenterOfGravityDepthSE}")

                del DatasetCode, Region, Season, DateCode, Species, CommonName
                #del DistributionProjectName
                del CoreSpecies, Year
                del DistributionProjectCode, SummaryProduct, CenterOfGravityLatitude
                del MinimumLatitude, MaximumLatitude, OffsetLatitude
                del CenterOfGravityLatitudeSE, CenterOfGravityLongitude
                del MinimumLongitude, MaximumLongitude, OffsetLongitude
                del CenterOfGravityLongitudeSE, CenterOfGravityDepth, MinimumDepth
                del MaximumDepth, OffsetDepth, CenterOfGravityDepthSE

                del row
            del cursor
        del fields

    except KeyboardInterrupt:
        sys.exit()
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(f"Caught an arcpy.ExecuteWarning error in the '{inspect.stack()[0][3]}' function.")
        arcpy.AddWarning(arcpy.GetMessages(1))
        traceback.print_exc()
        sys.exit()
    except arcpy.ExecuteError:
        arcpy.AddError(f"Caught an arcpy.ExecuteError error in the '{inspect.stack()[0][3]}' function.")
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
        sys.exit()
    except SystemExit as se:
        arcpy.AddError(f"Caught an SystemExit error: {se} in the '{inspect.stack()[0][3]}' function.")
        sys.exit()
    except Exception as e:
        arcpy.AddError(f"Caught an Exception error: {e} in the '{inspect.stack()[0][3]}' function.")
        traceback.print_exc()
        sys.exit()
    except:  # noqa: E722
        arcpy.AddError(f"Caught an except error in the '{inspect.stack()[0][3]}' function.")
        traceback.print_exc()
        sys.exit()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk:
            arcpy.AddMessage(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function at line number {inspect.stack()[0][2]}\n\t##--> '{', '.join(rk)}' <--##")
        del rk
        return True
    finally:
        pass

def worker(region_gdb=""):
    try:
        # Test if passed workspace exists, if not sys.exit()
        if not arcpy.Exists(rf"{region_gdb}"):
            arcpy.AddError(f"{os.path.basename(region_gdb)} is missing!!")
            arcpy.AddError(f"Function: '{inspect.stack()[0][3]}', Line Number: {inspect.stack()[0][2]}")
            sys.exit()
        else:
            pass

        import numpy as np
        import math

        import dismap_tools

        np.seterr(divide='ignore', invalid='ignore')

        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        table_name        = os.path.basename(region_gdb).replace(".gdb","")
        scratch_folder    = os.path.dirname(region_gdb)
        project_folder    = os.path.dirname(scratch_folder)
        csv_data_folder   = rf"{project_folder}\CSV_Data"
        image_folder      = rf"{project_folder}\Images"
        scratch_workspace = rf"{scratch_folder}\{table_name}\scratch.gdb"

        arcpy.AddMessage(f"Table Name: {table_name}\nProject Folder: {os.path.basename(project_folder)}\nScratch Folder: {os.path.basename(scratch_folder)}\n")

        arcpy.env.workspace                = region_gdb
        arcpy.env.scratchWorkspace         = scratch_workspace
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"
        #arcpy.env.compression               = "LZ77"
        #arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"
        #arcpy.env.pyramid                   = "PYRAMIDS -1 BILINEAR LZ77 NO_SKIP"
        arcpy.env.resamplingMethod         = "BILINEAR"
        arcpy.env.rasterStatistics         = "STATISTICS 1 1"
        #arcpy.env.buildStatsAndRATForTempRaster = True

        arcpy.management.CreateTable(region_gdb, f"{table_name}_Indicators", "", "", "")
        arcpy.AddMessage("\tCreate Table: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

        dismap_tools.add_fields(csv_data_folder, os.path.join(region_gdb, f"{table_name}_Indicators"))
        #dismap_tools.import_metadata(rf"{region_gdb}\{table_name}_Indicators")

        del csv_data_folder

        arcpy.AddMessage(f"Generating {table_name} Indicators Table")

        # "DatasetCode", "CSVFile", "TransformUnit", "TableName", "GeographicArea",
        # "CellSize", "PointFeatureType", "FeatureClassName", "Region", "Season",
        # "DateCode", "Status", "DistributionProjectCode", "DistributionProjectName",
        # "SummaryProduct", "FilterRegion", "FilterSubRegion", "FeatureServiceName",
        # "FeatureServiceTitle", "MosaicName", "MosaicTitle", "ImageServiceName",
        # "ImageServiceTitle"

        arcpy.AddMessage(f"\tGet list of vaules for the {table_name} Indicators table from the Datasets table")

        fields = ["DatasetCode", "TableName", "CellSize", "Region", "Season",
                  "DateCode", "DistributionProjectCode", "DistributionProjectName",
                  "SummaryProduct",]
        region_list = [row for row in arcpy.da.SearchCursor(rf"{region_gdb}\Datasets", fields, where_clause = f"TableName = '{table_name}'")][0]
        del fields

        # Assigning variables from items in the chosen table list
        # ['AI_IDW', 'AI_IDW_Region', 'AI', 'Aleutian Islands', None, 'IDW']
        datasetcode             = region_list[0]
        table_name              = region_list[1]
        cellsize                = region_list[2]
        region                  = region_list[3]
        season                  = region_list[4]
        datecode                = region_list[5]
        distributionprojectcode = region_list[6]
        distributionprojectname = region_list[7]
        summaryproduct          = region_list[8]
        del region_list

        # Convert the Month Day Year date code to YYYYMMDD
        #datecode = dismap.date_code(datecode)
        #arcpy.AddMessage(datecode)
        #arcpy.AddMessage(dismap.date_code(datecode))

        arcpy.env.cellSize = cellsize
        del cellsize

        # Region Raster Mask
        datasetcode_raster_mask = os.path.join(region_gdb, f"{table_name}_Raster_Mask")

        # we need to set the mask and extent of the environment, or the raster and items may not come out correctly.
        arcpy.env.extent     = arcpy.Describe(datasetcode_raster_mask).extent
        arcpy.env.mask       = datasetcode_raster_mask
        arcpy.env.snapRaster = datasetcode_raster_mask
        del datasetcode_raster_mask

        # Region Indicators
        region_indicators = rf"{region_gdb}\{table_name}_Indicators"

        # Region Bathymetry
        region_bathymetry = rf"{region_gdb}\{table_name}_Bathymetry"

        # Region Latitude
        region_latitude = rf"{region_gdb}\{table_name}_Latitude"

        # Region Longitude
        region_longitude = rf"{region_gdb}\{table_name}_Longitude"

        layerspeciesyearimagename = rf"{region_gdb}\{table_name}_LayerSpeciesYearImageName"

        input_rasters = {}

        arcpy.AddMessage("\tCreate a list of input biomass raster path locations")

        #fields = "DatasetCode;Region;Season;Species;CommonName;SpeciesCommonName;CoreSpecies;Year;StdTime;Variable;Value;Dimensions"
        #fields = fields.split(";")
        fields = ['ImageName', 'Variable', 'Species', 'CommonName', 'CoreSpecies', 'Year']

        #arcpy.AddMessage(fields)
        #fields = [f.name for f in arcpy.ListFields(datasetcode_tmp) if f.type not in ['Geometry', 'OID']]
        with arcpy.da.SearchCursor(layerspeciesyearimagename, fields, where_clause = f"DatasetCode = '{datasetcode}'") as cursor:
            for row in cursor:
                image_name, variable, species, commonname, corespecies, year = row[0], row[1], row[2], row[3], row[4], row[5]
                #if variable not in variables: variables.append(variable)
                #arcpy.AddMessage(variable, image_name)
                #variable = f"_{variable}" if "Species Richness" in variable else variable
                if "Species Richness" not in variable:
                    #arcpy.AddMessage(variable, year)
                    input_raster_path = rf"{image_folder}\{table_name}\{variable}\{image_name}.tif"
                    #arcpy.AddMessage(input_raster_path)
                    #input_rasters[variable, year] = [image_name, variable, species, commonname, corespecies, year, input_raster_path]
                    #input_rasters[variable][year] = [image_name, variable, species, commonname, corespecies, year, input_raster_path]
                    #input_rasters[variable] = {year : image_name}
                    if variable not in input_rasters:
                        input_rasters[variable] = {year : [image_name, variable, species, commonname, corespecies, year, input_raster_path]}
                    else:
                        value = input_rasters[variable]
                        if year not in value:
                            value[year] = [image_name, variable, species, commonname, corespecies, year, input_raster_path]
                            input_rasters[variable] = value
                        del value

                    del input_raster_path

                del row, image_name, variable, species, commonname, corespecies, year
            del cursor

        #arcpy.AddMessage(variables)
        del fields
        #del variables
        del layerspeciesyearimagename
        del image_folder

        # Start with empty row_values list of list
        row_values = []

        arcpy.AddMessage("Interate over the species names")

        for variable in sorted(input_rasters):

            first_year = 9999

            raster_years = input_rasters[variable]

            for raster_year in sorted(raster_years):

                image_name, variable, species, commonname, corespecies, year, input_raster_path = raster_years[raster_year]

                PrintRecord = False
                if PrintRecord:
                    arcpy.AddMessage(f"\t> Image Name: {image_name}")
                    arcpy.AddMessage(f"\t\t> Variable:      {variable}")
                    arcpy.AddMessage(f"\t\t> Species:       {species}")
                    arcpy.AddMessage(f"\t\t> Common Name:   {commonname}")
                    arcpy.AddMessage(f"\t\t> Core Species:  {corespecies}")
                    arcpy.AddMessage(f"\t\t> Year:          {year}")
                    arcpy.AddMessage(f"\t\t> Output Raster: {os.path.basename(input_raster_path)}")
                del PrintRecord

                arcpy.AddMessage(f"Processing {image_name} Biomass Raster for year: {raster_year}")

                # Get maximumBiomass value to filter out "zero" rasters
                maximumBiomass = float(arcpy.management.GetRasterProperties(input_raster_path, "MAXIMUM").getOutput(0))

                arcpy.AddMessage(f"\t> Biomass Raster Maximum: {maximumBiomass}")

                # arcpy.AddMessage(variable, corespecies, first_year, year)

                # If maximumBiomass greater than zero, then process raster
                if maximumBiomass > 0.0:
                    # Test is for first year

                    first_year = year if year < first_year else first_year
                    #arcpy.AddMessage(f"\t{first_year}, {year} {first_year == year}")

                    arcpy.AddMessage("\t> Calculating biomassArray")

                    biomassArray = arcpy.RasterToNumPyArray(input_raster_path, nodata_to_value=np.nan)
                    biomassArray[biomassArray <= 0.0] = np.nan

                    #sumWtCpue = sum of all wtcpue values (get this from input_raster_path stats??)
                    sumBiomassArray = np.nansum(biomassArray)

                    arcpy.AddMessage(f"\t> sumBiomassArray: {sumBiomassArray}")

                    arcpy.AddMessage(f"\t> biomassArray non-nan count: {np.count_nonzero(~np.isnan(biomassArray))}")

                    # ###--->>> Biomass End

                    arcpy.AddMessage("\t> Calculating latitudeArray")

                    # ###--->>> Latitude Start
                    #CenterOfGravityLatitude    = None
                    #MinimumLatitude            = None
                    #MaximumLatitude            = None
                    #OffsetLatitude             = None
                    #CenterOfGravityLatitudeSE  = None

                    # Latitude
                    latitudeArray = arcpy.RasterToNumPyArray(region_latitude, nodata_to_value=np.nan)
                    #arcpy.AddMessage(latitudeArray.shape)
                    latitudeArray[np.isnan(biomassArray)] = np.nan
                    #arcpy.AddMessage(latitudeArray.shape)

                    #arcpy.AddMessage(f"\t\t> latitudeArray non-nan count: {np.count_nonzero(~np.isnan(latitudeArray)):,d}")

                    #arcpy.AddMessage(f"\t\t> Latitude Min: {np.nanmin(latitudeArray)}")

                    #arcpy.AddMessage(f"\t\t> Latitude Max: {np.nanmax(latitudeArray)}")

                    # make the biomass and latitude arrays one dimensional

                    flatBiomassArray = biomassArray.flatten()

                    flatLatitudeArray = latitudeArray.flatten()

                    # latsInds is an array of indexes representing the sort

                    latsInds = flatLatitudeArray.argsort()

                    # sort biomass and latitude arrays by lat sorted index

                    sortedBiomassArray = flatBiomassArray[latsInds]
                    sortedLatitudeArray = flatLatitudeArray[latsInds]

                    # calculate the cumulative sum of the sorted biomass values

                    sortedBiomassArrayCumSum = np.nancumsum(sortedBiomassArray)

                    # quantile is cumulative sum value divided by total biomass

                    sortedBiomassArrayQuantile = sortedBiomassArrayCumSum / np.nansum(flatBiomassArray)

                    # find the difference between 0.95 and each cumulative sum value ... asbolute value gives the closest distance

                    diffArray = np.abs(sortedBiomassArrayQuantile - 0.95)

                    # find the index of the smallest difference

                    minIndex = diffArray.argmin()

                    # get the lat at that index

                    #maxLat = sortedLatitudeArray[minIndex]
                    MaximumLatitude = sortedLatitudeArray[minIndex]

                    # do the same for 0.05

                    diffArray = np.abs(sortedBiomassArrayQuantile - 0.05)

                    minIndex = diffArray.argmin()

                    #minLat = sortedLatitudeArray[minIndex]
                    MinimumLatitude = sortedLatitudeArray[minIndex]

                    del sortedBiomassArrayCumSum, sortedBiomassArrayQuantile
                    del diffArray, minIndex
                    del sortedLatitudeArray, sortedBiomassArray, flatBiomassArray
                    del latsInds, flatLatitudeArray

                    weightedLatitudeArray = np.multiply(biomassArray, latitudeArray)

                    sumWeightedLatitudeArray = np.nansum(weightedLatitudeArray)

                    #arcpy.AddMessage("\t\t> Sum Weighted Latitude: {sumWeightedLatitudeArray}")

                    CenterOfGravityLatitude = sumWeightedLatitudeArray / sumBiomassArray

                    if year == first_year:
                        first_year_offset_latitude = CenterOfGravityLatitude

                    OffsetLatitude = CenterOfGravityLatitude - first_year_offset_latitude

                    weightedLatitudeArrayVariance = np.nanvar(weightedLatitudeArray)
                    weightedLatitudeArrayCount = np.count_nonzero(~np.isnan(weightedLatitudeArray))

                    CenterOfGravityLatitudeSE = math.sqrt(weightedLatitudeArrayVariance) / math.sqrt(weightedLatitudeArrayCount)

                    del weightedLatitudeArrayVariance, weightedLatitudeArrayCount

                    #arcpy.AddMessage(f"\t\t> Center of Gravity Latitude: {round(CenterOfGravityLatitude,6)}"
                    arcpy.AddMessage(f"\t\t> Center of Gravity Latitude: {CenterOfGravityLatitude}")
                    arcpy.AddMessage(f"\t\t> Minimum Latitude (5th Percentile): {MinimumLatitude}")
                    arcpy.AddMessage(f"\t\t> Maximum Latitude (95th Percentile): {MaximumLatitude}")
                    arcpy.AddMessage(f"\t\t> Offset Latitude: {OffsetLatitude}")
                    arcpy.AddMessage(f"\t\t> Center of Gravity Latitude Standard Error: {CenterOfGravityLatitudeSE}")

                    del latitudeArray, weightedLatitudeArray, sumWeightedLatitudeArray

                    # ###--->>> Latitude End

                    arcpy.AddMessage("\t> Calculating longitudeArray")

                    # ###--->>> Longitude Start
                    #CenterOfGravityLongitude   = None
                    #MinimumLongitude           = None
                    #MaximumLongitude           = None
                    #OffsetLongitude            = None
                    #CenterOfGravityLongitudeSE = None

                    # For issue of international date line
                    # Added/Modified by JFK June 15, 2022
                    longitudeArray = arcpy.RasterToNumPyArray(region_longitude, nodata_to_value=np.nan)

                    longitudeArray = np.mod(longitudeArray, 360.0)

                    longitudeArray[np.isnan(biomassArray)] = np.nan

                    # make the biomass and latitude arrays one dimensional

                    flatBiomassArray = biomassArray.flatten()

                    flatLongitudeArray = longitudeArray.flatten()

                    # longsInds is an array of indexes representing the sort

                    longsInds = flatLongitudeArray.argsort()

                    # sort biomass and latitude arrays by long sorted index

                    sortedBiomassArray = flatBiomassArray[longsInds]
                    sortedLongitudeArray = flatLongitudeArray[longsInds]

                    # calculate the cumulative sum of the sorted biomass values

                    sortedBiomassArrayCumSum = np.nancumsum(sortedBiomassArray)

                    # quantile is cumulative sum value divided by total biomass

                    sortedBiomassArrayQuantile = sortedBiomassArrayCumSum / np.nansum(flatBiomassArray)

                    # find the difference between 0.95 and each cumulative sum value ... asbolute value gives the closest distance

                    diffArray = np.abs(sortedBiomassArrayQuantile - 0.95)

                    # find the index of the smallest difference

                    minIndex = diffArray.argmin()

                    # get the lat at that index

                    MaximumLongitude = sortedLongitudeArray[minIndex]

                    # do the same for 0.05

                    diffArray = np.abs(sortedBiomassArrayQuantile - 0.05)

                    minIndex = diffArray.argmin()

                    MinimumLongitude = sortedLongitudeArray[minIndex]

                    del sortedBiomassArrayCumSum, sortedBiomassArrayQuantile, diffArray, minIndex
                    del sortedLongitudeArray, sortedBiomassArray, flatBiomassArray
                    del longsInds, flatLongitudeArray

                    weightedLongitudeArray = np.multiply(biomassArray, longitudeArray)

                    sumWeightedLongitudeArray = np.nansum(weightedLongitudeArray)

                    CenterOfGravityLongitude = sumWeightedLongitudeArray / sumBiomassArray

                    if year == first_year:
                       first_year_offset_longitude = CenterOfGravityLongitude

                    OffsetLongitude = CenterOfGravityLongitude - first_year_offset_longitude

                    weightedLongitudeArrayVariance = np.nanvar(weightedLongitudeArray)
                    weightedLongitudeArrayCount = np.count_nonzero(~np.isnan(weightedLongitudeArray))

                    CenterOfGravityLongitudeSE = math.sqrt(weightedLongitudeArrayVariance) / math.sqrt(weightedLongitudeArrayCount)

                    del weightedLongitudeArrayVariance, weightedLongitudeArrayCount

                    # Convert 360 back to 180
                    # Added/Modified by JFK June 15, 2022
                    CenterOfGravityLongitude = np.mod(CenterOfGravityLongitude - 180.0, 360.0) - 180.0
                    MinimumLongitude = np.mod(MinimumLongitude - 180.0, 360.0) - 180.0
                    MaximumLongitude = np.mod(MaximumLongitude - 180.0, 360.0) - 180.0

                    #arcpy.AddMessage(f"\t\t> Sum Weighted Longitude: {0}".format(sumWeightedLongitudeArray))

                    #arcpy.AddMessage(f"\t\t> Center of Gravity Longitude: {round(CenterOfGravityLongitude,6)}"
                    arcpy.AddMessage(f"\t\t> Center of Gravity Longitude: {CenterOfGravityLongitude}")

                    #arcpy.AddMessage(F"\t\t> Center of Gravity Longitude: {np.mod(CenterOfGravityLongitude - 180.0, 360.0) -180.0}")

                    arcpy.AddMessage(f"\t\t> Minimum Longitude (5th Percentile): {MinimumLongitude}")
                    arcpy.AddMessage(f"\t\t> Maximum Longitude (95th Percentile): {MaximumLongitude}")
                    arcpy.AddMessage(f"\t\t> Offset Longitude: {OffsetLongitude}")
                    arcpy.AddMessage(f"\t\t> Center of Gravity Longitude Standard Error: {CenterOfGravityLongitudeSE}")

                    del longitudeArray, weightedLongitudeArray, sumWeightedLongitudeArray

                    # ###--->>> Longitude End

                    arcpy.AddMessage("\t> Calculating bathymetryArray")

                    # ###--->>> Center of Gravity Depth (Bathymetry) Start

                    #CenterOfGravityDepth       = None
                    #MinimumDepth               = None
                    #MaximumDepth               = None
                    #OffsetDepth                = None
                    #CenterOfGravityDepthSE     = None

                    # Bathymetry
                    bathymetryArray = arcpy.RasterToNumPyArray(region_bathymetry, nodata_to_value=np.nan)
                    # If biomass cells are Null, make bathymetry cells Null as well
                    bathymetryArray[np.isnan(biomassArray)] = np.nan
                    # For bathymetry values zero are larger, make zero
                    bathymetryArray[bathymetryArray >= 0.0] = 0.0

                    #arcpy.AddMessage("\t\t> bathymetryArray non-nan count: {0}".format(np.count_nonzero(~np.isnan(bathymetryArray)))
                    #arcpy.AddMessage("\t\t> Bathymetry Min: {0}".format(np.nanmin(bathymetryArray))
                    #arcpy.AddMessage("\t\t> Bathymetry Max: {0}".format(np.nanmax(bathymetryArray))
                    # make the biomass and latitude arrays one dimensional

                    flatBiomassArray = biomassArray.flatten()

                    flatBathymetryArray = bathymetryArray.flatten()

                    # bathyInds is an array of indexes representing the sort

                    bathyInds = flatBathymetryArray.argsort()

                    # sort biomass and latitude arrays by lat sorted index

                    sortedBiomassArray = flatBiomassArray[bathyInds]
                    sortedBathymetryArray = flatBathymetryArray[bathyInds]

                    # calculate the cumulative sum of the sorted biomass values

                    sortedBiomassArrayCumSum = np.nancumsum(sortedBiomassArray)

                    # quantile is cumulative sum value divided by total biomass

                    sortedBiomassArrayQuantile = sortedBiomassArrayCumSum/np.nansum(flatBiomassArray)

                    # find the difference between 0.95 and each cumulative sum
                    # value ... asbolute value gives the closest distance

                    diffArray = np.abs(sortedBiomassArrayQuantile - 0.95)

                    # find the index of the smallest difference

                    minIndex = diffArray.argmin()

                    # get the lat at that index

                    #maxLat = sortedBathymetryArray[minIndex]
                    MaximumDepth = sortedBathymetryArray[minIndex]

                    # do the same for 0.05

                    diffArray = np.abs(sortedBiomassArrayQuantile - 0.05)

                    minIndex = diffArray.argmin()

                    #minLat = sortedBathymetryArray[minIndex]
                    MinimumDepth = sortedBathymetryArray[minIndex]

                    del sortedBiomassArrayCumSum, sortedBiomassArrayQuantile, diffArray, minIndex
                    del sortedBathymetryArray, sortedBiomassArray, flatBiomassArray
                    del bathyInds, flatBathymetryArray

                    weightedBathymetryArray = np.multiply(biomassArray, bathymetryArray)

                    sumWeightedBathymetryArray = np.nansum(weightedBathymetryArray)

                    arcpy.AddMessage(f"\t\t> Sum Weighted Bathymetry: {sumWeightedBathymetryArray}")

                    CenterOfGravityDepth = sumWeightedBathymetryArray / sumBiomassArray

                    if year == first_year:
                        first_year_offset_depth = CenterOfGravityDepth

                    OffsetDepth = CenterOfGravityDepth - first_year_offset_depth

                    weightedBathymetryArrayVariance = np.nanvar(weightedBathymetryArray)
                    weightedBathymetryArrayCount = np.count_nonzero(~np.isnan(weightedBathymetryArray))

                    CenterOfGravityDepthSE = math.sqrt(weightedBathymetryArrayVariance) / math.sqrt(weightedBathymetryArrayCount)

                    del weightedBathymetryArrayVariance, weightedBathymetryArrayCount

                    arcpy.AddMessage("\t\t> Center of Gravity Depth: {0}".format(CenterOfGravityDepth))

                    arcpy.AddMessage("\t\t> Minimum Depth (5th Percentile): {0}".format(MinimumDepth))

                    arcpy.AddMessage("\t\t> Maximum Depth (95th Percentile): {0}".format(MaximumDepth))

                    arcpy.AddMessage("\t\t> Offset Depth: {0}".format(OffsetDepth))

                    arcpy.AddMessage("\t\t> Center of Gravity Depth Standard Error: {0}".format(CenterOfGravityDepthSE))

                    del bathymetryArray, weightedBathymetryArray
                    del sumWeightedBathymetryArray

                    # ###--->>> Center of Gravity Depth (Bathymetry) End

                    # Clean Up
                    del biomassArray, sumBiomassArray

                elif maximumBiomass == 0.0:
                    CenterOfGravityLatitude    = None
                    MinimumLatitude            = None
                    MaximumLatitude            = None
                    OffsetLatitude             = None
                    CenterOfGravityLatitudeSE  = None
                    CenterOfGravityLongitude   = None
                    MinimumLongitude           = None
                    MaximumLongitude           = None
                    OffsetLongitude            = None
                    CenterOfGravityLongitudeSE = None
                    CenterOfGravityDepth       = None
                    MinimumDepth               = None
                    MaximumDepth               = None
                    OffsetDepth                = None
                    CenterOfGravityDepthSE     = None

                else:
                    arcpy.AddMessage('Something wrong with biomass raster')


                arcpy.AddMessage("\t> Assigning variables to row values")

                # Clean-up
                del maximumBiomass

                # Standard for all records
                DatasetCode             = datasetcode
                Region                  = region
                Season                  = season
                DateCode                = datecode
                Species                 = species
                CommonName              = commonname
                CoreSpecies             = corespecies
                Year                    = year
                DistributionProjectName = distributionprojectname
                DistributionProjectCode = distributionprojectcode
                SummaryProduct          = summaryproduct

                row = [
                       DatasetCode,
                       Region,
                       Season,
                       DateCode,
                       Species,
                       CommonName,
                       CoreSpecies,
                       Year,
                       DistributionProjectName,
                       DistributionProjectCode,
                       SummaryProduct,
                       CenterOfGravityLatitude,
                       MinimumLatitude,
                       MaximumLatitude,
                       OffsetLatitude,
                       CenterOfGravityLatitudeSE,
                       CenterOfGravityLongitude,
                       MinimumLongitude,
                       MaximumLongitude,
                       OffsetLongitude,
                       CenterOfGravityLongitudeSE,
                       CenterOfGravityDepth,
                       MinimumDepth,
                       MaximumDepth,
                       OffsetDepth,
                       CenterOfGravityDepthSE,
                      ]

                del DatasetCode, Region, Season, DateCode, Species, CommonName
                del CoreSpecies, Year, DistributionProjectName
                del DistributionProjectCode, SummaryProduct, CenterOfGravityLatitude
                del MinimumLatitude, MaximumLatitude, OffsetLatitude
                del CenterOfGravityLatitudeSE, CenterOfGravityLongitude
                del MinimumLongitude, MaximumLongitude, OffsetLongitude
                del CenterOfGravityLongitudeSE, CenterOfGravityDepth, MinimumDepth
                del MaximumDepth, OffsetDepth, CenterOfGravityDepthSE

                # Append to list
                row_values.append(row)
                del row

                del image_name, variable, species, commonname, corespecies, year, input_raster_path
                del raster_year

            del raster_years
            del first_year

            if "first_year_offset_latitude"  in locals():
                del first_year_offset_latitude
            if "first_year_offset_longitude" in locals():
                del first_year_offset_longitude
            if "first_year_offset_depth"     in locals():
                del first_year_offset_depth

        del region_bathymetry, region_latitude, region_longitude, input_rasters

        arcpy.AddMessage("Inserting records into the table")

        # This gets a list of fields in the table
        fields = [f.name for f in arcpy.ListFields(region_indicators) if f.type not in ['Geometry', 'OID']]

        # Open an InsertCursor
        cursor = arcpy.da.InsertCursor(region_indicators, fields)
        del fields

        # Insert new rows into the table
        for row in row_values:
            try:
                row = [None if x != x else x for x in row]
                cursor.insertRow(row)
            except:  # noqa: E722
                # Get the traceback object
                tb = sys.exc_info()[2]
                tbinfo = traceback.format_tb(tb)[0]
                # Concatenate information together concerning the error into a message string
                pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
                sys.exit()(pymsg)
            finally:
                del row

        # Delete cursor object
        del cursor

        # Delete
        del row_values

        getcount = arcpy.management.GetCount(region_indicators)[0]
        arcpy.AddMessage(f'\n> "{os.path.basename(region_indicators)}" has {getcount} records\n')
        del getcount

        PrintRowContent = False
        if PrintRowContent:
            printRowContent(region_indicators)
        del PrintRowContent

        del region_indicators

        arcpy.management.Delete(rf"{region_gdb}\Datasets")
        arcpy.management.Delete(rf"{region_gdb}\{table_name}_Bathymetry")
        arcpy.management.Delete(rf"{region_gdb}\{table_name}_Latitude")
        arcpy.management.Delete(rf"{region_gdb}\{table_name}_Longitude")
        arcpy.management.Delete(rf"{region_gdb}\{table_name}_Raster_Mask")
        arcpy.management.Delete(rf"{region_gdb}\{table_name}_LayerSpeciesYearImageName")

        # Values from Datasets table
        del datasetcode, region, season, datecode, distributionprojectcode
        del distributionprojectname, summaryproduct
        # Declared Variables assigned based on the passed paramater
        del table_name, scratch_folder, project_folder, scratch_workspace
        # Imported modules
        del np, math, dismap_tools
        # Passed paramater
        del region_gdb

    except KeyboardInterrupt:
        sys.exit()
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(f"Caught an arcpy.ExecuteWarning error in the '{inspect.stack()[0][3]}' function.")
        arcpy.AddWarning(arcpy.GetMessages(1))
        traceback.print_exc()
        sys.exit()
    except arcpy.ExecuteError:
        arcpy.AddError(f"Caught an arcpy.ExecuteError error in the '{inspect.stack()[0][3]}' function.")
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
        sys.exit()
    except SystemExit as se:
        arcpy.AddError(f"Caught an SystemExit error: {se} in the '{inspect.stack()[0][3]}' function.")
        sys.exit()
    except Exception as e:
        arcpy.AddError(f"Caught an Exception error: {e} in the '{inspect.stack()[0][3]}' function.")
        traceback.print_exc()
        sys.exit()
    except:  # noqa: E722
        arcpy.AddError(f"Caught an except error in the '{inspect.stack()[0][3]}' function.")
        traceback.print_exc()
        sys.exit()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk:
            arcpy.AddMessage(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function at line number {inspect.stack()[0][2]}\n\t##--> '{', '.join(rk)}' <--##")
        del rk
        return True
    finally:
        pass

def preprocessing(project_gdb="", table_names="", clear_folder=True):
    try:
        import dismap_tools

        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(1) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        # Set basic arcpy.env variables
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        # Set varaibales
        project_folder = os.path.dirname(project_gdb)
        scratch_folder = rf"{project_folder}\Scratch"
        scratch_workspace = os.path.join(project_folder, "Scratch\\scratch.gdb")

        # Clear Scratch Folder
        #ClearScratchFolder = True
        #if ClearScratchFolder:
        if clear_folder:
            dismap_tools.clear_folder(folder=rf"{os.path.dirname(project_gdb)}\Scratch")
        else:
            pass
        #del ClearScratchFolder
        del clear_folder

        arcpy.env.workspace        = project_gdb
        arcpy.env.scratchWorkspace = scratch_workspace
        del project_folder, scratch_workspace

        if not table_names:
            table_names = [row[0] for row in arcpy.da.SearchCursor(os.path.join(project_gdb, "Datasets"),
                                                                   "TableName",
                                                                   where_clause = "TableName LIKE '%_IDW'")]
        else:
            pass

        for table_name in table_names:
            arcpy.AddMessage(f"Pre-Processing: {table_name}")

            region_gdb = os.path.join(scratch_folder, f"{table_name}.gdb")
            region_scratch_workspace = os.path.join(scratch_folder, f"{table_name}", "scratch.gdb")

            # Create Scratch Workspace for Region
            if not arcpy.Exists(region_scratch_workspace):
                os.makedirs(os.path.join(scratch_folder,  table_name))
                if not arcpy.Exists(region_scratch_workspace):
                    arcpy.AddMessage(f"Create File GDB: '{table_name}'")
                    arcpy.management.CreateFileGDB(os.path.join(scratch_folder, f"{table_name}"), "scratch")
                    arcpy.AddMessage("\tCreate File GDB: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
            del region_scratch_workspace
            # # # CreateFileGDB
            arcpy.AddMessage(f"Creating File GDB: '{table_name}'")
            arcpy.management.CreateFileGDB(rf"{scratch_folder}", f"{table_name}")
            arcpy.AddMessage("\tCreate File GDB: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
            # # # CreateFileGDB
            # # # Datasets
            # Process: Make Table View (Make Table View) (management)
            datasets = rf'{project_gdb}\Datasets'
            arcpy.AddMessage(f"'{os.path.basename(datasets)}' has {arcpy.management.GetCount(datasets)[0]} records")
            arcpy.management.Copy(datasets, rf"{region_gdb}\Datasets")
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
            # # # Datasets

            # # # LayerSpeciesYearImageName
            LayerSpeciesYearImageName = rf"{project_gdb}\{table_name}_LayerSpeciesYearImageName"
            arcpy.AddMessage(f"The table '{table_name}_LayerSpeciesYearImageName' has {arcpy.management.GetCount(LayerSpeciesYearImageName)[0]} records")
            arcpy.management.Copy(rf"{project_gdb}\{table_name}_LayerSpeciesYearImageName", rf"{region_gdb}\{table_name}_LayerSpeciesYearImageName")
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
            del LayerSpeciesYearImageName
            # # # LayerSpeciesYearImageName

            # # # Raster_Mask
            arcpy.AddMessage(f"Copy Raster Mask for '{table_name}'")
            arcpy.management.Copy(rf"{project_gdb}\{table_name}_Raster_Mask", rf"{region_gdb}\{table_name}_Raster_Mask")
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
            # # # Raster_Mask

            # # # Bathymetry
            arcpy.AddMessage(f"Copy Bathymetry for '{table_name}'")
            arcpy.management.Copy(rf"{project_gdb}\{table_name}_Bathymetry", rf"{region_gdb}\{table_name}_Bathymetry")
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
            # # # Bathymetry

            # # # Latitude
            arcpy.AddMessage(f"Copy Latitude for '{table_name}'")
            arcpy.management.Copy(rf"{project_gdb}\{table_name}_Latitude", rf"{region_gdb}\{table_name}_Latitude")
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
            # # # Latitude

            # # # Longitude
            arcpy.AddMessage(f"Copy Longitude for '{table_name}'")
            arcpy.management.Copy(rf"{project_gdb}\{table_name}_Longitude", rf"{region_gdb}\{table_name}_Longitude")
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
            # # # Longitude

            # Declared Variables
            del table_name
            del datasets

        # Declared Variables
        del scratch_folder, region_gdb
        # Imports
        del dismap_tools
        # Function Parameters
        del project_gdb, table_names

    except KeyboardInterrupt:
        sys.exit()
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(f"Caught an arcpy.ExecuteWarning error in the '{inspect.stack()[0][3]}' function.")
        arcpy.AddWarning(arcpy.GetMessages(1))
        traceback.print_exc()
        sys.exit()
    except arcpy.ExecuteError:
        arcpy.AddError(f"Caught an arcpy.ExecuteError error in the '{inspect.stack()[0][3]}' function.")
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
        sys.exit()
    except SystemExit as se:
        arcpy.AddError(f"Caught an SystemExit error: {se} in the '{inspect.stack()[0][3]}' function.")
        sys.exit()
    except Exception as e:
        arcpy.AddError(f"Caught an Exception error: {e} in the '{inspect.stack()[0][3]}' function.")
        traceback.print_exc()
        sys.exit()
    except:  # noqa: E722
        arcpy.AddError(f"Caught an except error in the '{inspect.stack()[0][3]}' function.")
        traceback.print_exc()
        sys.exit()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk:
            arcpy.AddMessage(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function at line number {inspect.stack()[0][2]}\n\t##--> '{', '.join(rk)}' <--##")
        del rk
        return True
    finally:
        pass

def script_tool(project_gdb=""):
    try:
        # Imports
        import dismap_tools
        from time import gmtime, localtime, strftime, time
        # Set a start time so that we can see how log things take
        start_time = time()
        arcpy.AddMessage(f"{'-' * 80}")
        arcpy.AddMessage(f"Python Script:  {os.path.basename(__file__)}")
        arcpy.AddMessage(f"Location:       .. {'/'.join(__file__.split(os.sep)[-4:])}")
        arcpy.AddMessage(f"Python Version: {sys.version}")
        arcpy.AddMessage(f"Environment:    {os.path.basename(sys.exec_prefix)}")
        arcpy.AddMessage(f"Start Time:     {strftime('%a %b %d %I:%M %p', localtime(start_time))}")
        arcpy.AddMessage(f"{'-' * 80}\n")



        ##        # Set worker parameters
        ##        #table_name = "AI_IDW"
        ##        table_name = "HI_IDW"
        ##        #table_name = "NBS_IDW"
        ##        #table_name = "ENBS_IDW"

        table_names = ["HI_IDW",]

        #preprocessing(project_gdb=project_gdb, table_names=table_names, clear_folder=True)

        for table_name in table_names:
            region_gdb = rf"{os.path.dirname(project_gdb)}\Scratch\{table_name}.gdb"
            try:
                pass
                worker(region_gdb=region_gdb)
            except SystemExit:
                arcpy.AddError(arcpy.GetMessages(2))
                traceback.print_exc()
                sys.exit()
            del table_name, region_gdb
        del table_names

        # Declared Varaiables
        # Imports
        del dismap_tools
        # Function Parameters
        del project_gdb

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        hours, rem = divmod(end_time-start_time, 3600)
        minutes, seconds = divmod(rem, 60)
        arcpy.AddMessage(f"\n{'-' * 80}")
        arcpy.AddMessage(f"Python script: {os.path.basename(__file__)}")
        arcpy.AddMessage(f"Start Time:    {strftime('%a %b %d %I:%M %p', localtime(start_time))}")
        arcpy.AddMessage(f"End Time:      {strftime('%a %b %d %I:%M %p', localtime(end_time))}")
        arcpy.AddMessage(f"Elapsed Time   {int(hours):0>2}:{int(minutes):0>2}:{seconds:05.2f} (H:M:S)")
        arcpy.AddMessage(f"{'-' * 80}")
        del hours, rem, minutes, seconds
        del elapse_time, end_time, start_time
        del gmtime, localtime, strftime, time

    except KeyboardInterrupt:
        sys.exit()
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(f"Caught an arcpy.ExecuteWarning error in the '{inspect.stack()[0][3]}' function.")
        arcpy.AddWarning(arcpy.GetMessages(1))
        traceback.print_exc()
        sys.exit()
    except arcpy.ExecuteError:
        arcpy.AddError(f"Caught an arcpy.ExecuteError error in the '{inspect.stack()[0][3]}' function.")
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
        sys.exit()
    except SystemExit as se:
        arcpy.AddError(f"Caught an SystemExit error: {se} in the '{inspect.stack()[0][3]}' function.")
        sys.exit()
    except Exception as e:
        arcpy.AddError(f"Caught an Exception error: {e} in the '{inspect.stack()[0][3]}' function.")
        traceback.print_exc()
        sys.exit()
    except:  # noqa: E722
        arcpy.AddError(f"Caught an except error in the '{inspect.stack()[0][3]}' function.")
        traceback.print_exc()
        sys.exit()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk:
            arcpy.AddMessage(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function at line number {inspect.stack()[0][2]}\n\t##--> '{', '.join(rk)}' <--##")
        del rk
        return True
    finally:
        pass

if __name__ == '__main__':
    try:
        project_gdb = arcpy.GetParameterAsText(0)
        if not project_gdb:
            project_gdb = os.path.join(os.path.expanduser('~'), "Documents\\ArcGIS\\Projects\\DisMAP\\ArcGIS-Analysis-Python\\February 1 2026\\February 1 2026.gdb")
        else:
            pass
        script_tool(project_gdb)
        arcpy.SetParameterAsText(1, "Result")
        del project_gdb
    except:  # noqa: E722
        traceback.print_exc()
    else:
        pass
    finally:
        pass