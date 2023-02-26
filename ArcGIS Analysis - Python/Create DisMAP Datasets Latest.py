# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      jfken
#
# Created:     23/03/2021
# Copyright:   (c) jfken 2021
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from __future__ import print_function
import os
import arcpy
from arcpy import metadata as md
import pandas as pd
import numpy as np
import scipy
from scipy import stats
from time import time, localtime, strftime, sleep, gmtime
from datetime import date
import shutil
from math import copysign
import math

# Get the name of the running fuction
import inspect
function_name = lambda: inspect.stack()[1][3]

######################################
# Functions specific to this program
######################################

def addMetadata(item):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        #arcpy.AddMessage(function)

        # Get the target item's Metadata object
        md = arcpy.metadata.Metadata(item)
        md.synchronize('ACCESSED', 1)
        md.save()
        md.reload()

        # Delete all geoprocessing history and any enclosed files from the item's metadata
        if not md.isReadOnly:
            md.deleteContent('GPHISTORY')
            md.deleteContent('ENCLOSED_FILES')
            md.save()

        del md, item

        localKeys =  [key for key in locals().keys() if "function" not in key]

        if localKeys:
            msg = "Local Keys in {0}(): {1}".format(function, u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys, function

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo

def analyzeMosaicDataset():
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        #arcpy.AddMessage(function)

        # Set a start time so that we can see how log things take
        start_time = time()

        arcpy.env.overwriteOutput = True
        arcpy.env.scratchWorkspace = ScratchGDB
        arcpy.env.workspace = ProjectGDB

        for table_name in table_names:
            # Assigning variables from items in the chosen table list
            #region_shape = table_name[0]
            #region_boundary = table_name[1]
            region_abb = table_name[2]
            region = table_name[3]
            #csv_file = table_name[4]
            #region_georef = table_name[5]
            #region_contours = table_name[6]

            # For benchmarking.
            log_file = os.path.join(LOG_DIRECTORY, region + ".log")

            # Write a message to the log file
            msg = "#-> STARTING {0} ON {1}".format(function, strftime("%a %b %d %I:%M:%S %p", localtime()))
            logFile(log_file, msg)
            del msg

            msg = ">-> Region (abb): {0}\n\t Region:  {1}".format(region_abb, region)
            logFile(log_file, msg)

            # Define region_mosaic
            region_mosaic = os.path.join(ProjectGDB, region_abb)

            msg = ">-> arcpy.management.AnalyzeMosaicDataset for {0}".format(region)
            logFile(log_file, msg); del msg

            with arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB):
                arcpy.management.AnalyzeMosaicDataset(region_mosaic,
                                                      '',
                                                      "FOOTPRINT;FUNCTION;RASTER;PATHS;SOURCE_VALIDITY;STALE;STATISTICS;PERFORMANCE;INFORMATION"
                                                     )
            msg = arcpy.GetMessages()
            msg = ">->-> {0}".format(msg.replace('\n', '\n>->-> '))
            logFile(log_file, msg); del msg

        # Cleanup
        del log_file
        del table_name, region_abb, region, region_mosaic

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = u"#-> Elapsed Time for {0} {1} (H:M:S)\n".format(function, strftime("%H:%M:%S", gmtime(elapse_time)))
        print(msg)
        del msg, start_time, end_time, elapse_time

        localKeys =  [key for key in locals().keys() if "function" not in key]

        if localKeys:
            msg = "Local Keys in {0}(): {1}".format(function, u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys, function

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo

def buildMultidimensionalInfo():
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        #arcpy.AddMessage(function)

        # Set a start time so that we can see how log things take
        start_time = time()

        arcpy.env.overwriteOutput = True
        arcpy.env.scratchWorkspace = ScratchGDB
        arcpy.env.workspace = ProjectGDB

        for table_name in table_names:
            # Assigning variables from items in the chosen table list
            #region_shape = table_name[0]
            #region_boundary = table_name[1]
            region_abb = table_name[2]
            region = table_name[3]
            #csv_file = table_name[4]
            #region_georef = table_name[5]
            #region_contours = table_name[6]

            # For benchmarking.
            log_file = os.path.join(LOG_DIRECTORY, region + ".log")

            # Write a message to the log file
            msg = "#-> STARTING {0} ON {1}".format(function, strftime("%a %b %d %I:%M:%S %p", localtime()))
            logFile(log_file, msg)
            del msg

            msg = ">-> Region (abb): {0}\n\t Region:  {1}".format(region_abb, region)
            logFile(log_file, msg)

            # Define region_mosaic
            region_mosaic = os.path.join(ProjectGDB, region_abb)

            msg = "\t\t Adding Multidimensional Information to the regional Mosaic Dataset"
            logFile(log_file, msg); del msg

            try:
                print(">-> arcpy.md.BuildMultidimensionalInfo DELETE_MULTIDIMENSIONAL_INFO")

                arcpy.md.BuildMultidimensionalInfo(region_mosaic, '', None, None, "DELETE_MULTIDIMENSIONAL_INFO")
                msg = arcpy.GetMessages()
                msg = ">->-> {0}".format(msg.replace('\n', '\n>->-> '))
                logFile(log_file, msg); del msg

            except:
                pass

            arcpy.md.BuildMultidimensionalInfo(region_mosaic, "Variable", "StdTime # #", None, "NO_DELETE_MULTIDIMENSIONAL_INFO")

            msg = arcpy.GetMessages()
            msg = ">->-> {0}".format(msg.replace('\n', '\n>->-> '))
            logFile(log_file, msg); del msg

        # Cleanup
        del log_file
        del table_name, region_abb, region, region_mosaic

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = u"#-> Elapsed Time for {0} {1} (H:M:S)\n".format(function, strftime("%H:%M:%S", gmtime(elapse_time)))
        print(msg)
        del msg, start_time, end_time, elapse_time

        localKeys =  [key for key in locals().keys() if "function" not in key]

        if localKeys:
            msg = "Local Keys in {0}(): {1}".format(function, u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys, function

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo

def createDisMapRegions():
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        # Set the workspace to the ProjectGDB
        tmp_workspace = arcpy.env.workspace
        arcpy.env.workspace = ProjectGDB

        # Set the scratch workspace to the ScratchGDB
        tmp_scratchWorkspace = arcpy.env.scratchWorkspace
        arcpy.env.scratchWorkspace = ScratchGDB

# ###--->>> DisMAP Regions
        dismap_regions = os.path.join(ProjectGDB, u"DisMAP_Regions")
        if not arcpy.Exists(dismap_regions) or ReplaceDisMapRegions:
            arcpy.management.CreateFeatureclass(out_path = ProjectGDB,
                                                out_name = "DisMAP_Regions",
                                                geometry_type="POLYLINE",
                                                template="",
                                                has_m="DISABLED",
                                                has_z="DISABLED",
                                                spatial_reference="PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]];-20037700 -30241100 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision",
                                                config_keyword="",
                                                spatial_grid_1="0",
                                                spatial_grid_2="0",
                                                spatial_grid_3="0")
            arcpy.management.AddField(in_table = dismap_regions,
                                      field_name="OARegion",
                                      field_type="TEXT",
                                      field_precision="",
                                      field_scale="",
                                      field_length="50",
                                      field_alias="OA Region",
                                      field_is_nullable="NULLABLE",
                                      field_is_required="NON_REQUIRED",
                                      field_domain="")
        for table_name in table_names:
            region_abb = table_name[2]

            region_shape = os.path.join(ProjectGDB, region_abb+"_Shape")
            region_shape_line = os.path.join(ProjectGDB, region_abb+"_Shape_Line")

            if arcpy.Exists(region_shape):

                msg = "> arcpy.management.FeatureToLine"
                print(msg)
                # Process: arcpy.management.FeatureToLine
                arcpy.management.FeatureToLine(in_features = region_shape, out_feature_class = region_shape_line, cluster_tolerance="", attributes="ATTRIBUTES")

                msg = "> arcpy.management.DeleteField"
                print(msg)
                # Process: arcpy.management.DeleteField
                fields = [f.name for f in arcpy.ListFields(region_shape_line, "*") if not f.required and u'OARegion' not in f.name]
                arcpy.management.DeleteField(region_shape_line, fields)
                del fields

                msg = "> arcpy.management.Append"
                print(msg)
                # Process: arcpy.management.Append
                arcpy.management.Append(inputs = region_shape_line,
                                        target = dismap_regions,
                                        schema_type="TEST",
                                        field_mapping="",
                                        subtype="")

        msg = "> arcpy.management.DeleteIdentical"
        print(msg)
        # Process: arcpy.management.DeleteIdentical
        arcpy.management.DeleteIdentical(in_dataset = dismap_regions,
                                         fields = "Shape;Shape_Length;OARegion",
                                         xy_tolerance="",
                                         z_tolerance="0")

        #
        addMetadata(dismap_regions)

        del dismap_regions, table_name, region_abb, region_shape, region_shape_line, msg

        # Set the workspace to the tmp_workspace
        arcpy.env.workspace = tmp_workspace
        # Set the scratch workspace to the tmp_scratchWorkspace
        arcpy.env.scratchWorkspace = tmp_scratchWorkspace
        del tmp_workspace, tmp_scratchWorkspace

        localKeys =  [key for key in locals().keys() if "function" not in key]

        if localKeys:
            msg = "Local Keys in {0}(): {1}".format(function, u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys, function

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo

def createCoreSpeciesRichnessRasters():
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        #arcpy.AddMessage(function)

        # Set a start time so that we can see how log things take
        start_time = time()

        #ProjectFolder = r'C:\Users\john.f.kennedy\Documents\GitHub\DisMap\Test'
        #ProjectGDB = os.path.join(ProjectFolder, u'DisMap.gdb')
        #ScratchGDB = os.path.join(ProjectFolder, r'scratch\scratch.gdb')
        #ANALYSIS_DIRECTORY = os.path.join(ProjectFolder, "Analysis_Folder")
        #MOSAIC_DIRECTORY = os.path.join(ProjectFolder, "Raster_Folder")
        arcpy.env.overwriteOutput = True
        arcpy.env.scratchWorkspace = ScratchGDB
        arcpy.env.rasterStatistics = u'STATISTICS 1 1'
        arcpy.env.buildStatsAndRATForTempRaster = True

        tmp_workspace = arcpy.env.workspace

        arcpy.env.workspace = ScratchGDB
        # This removes the saved rasters in the ScratchGDB
        for raster in arcpy.ListRasters("*"): arcpy.management.Delete(raster)
        arcpy.management.Compact(ScratchGDB)
        #del raster

        arcpy.env.workspace = ScratchFolder
        # This removes the saved rasters in the ScratchGDB
        for raster in [r for r in arcpy.ListRasters("*")]: arcpy.management.Delete(raster)
        #del raster

        arcpy.env.workspace = tmp_workspace
        del tmp_workspace

        for table_name in table_names:
            # Assigning variables from items in the chosen table list
            #region_shape = table_name[0]
            #region_boundary = table_name[1]
            region_abb = table_name[2]
            region = table_name[3]
            csv_file = table_name[4]
            region_georef = table_name[5]
            #region_contours = table_name[6]
            cell_size = table_name[7]

            # Set the output coordinate system to what is available for us.
            region_sr = srs[region_georef]
            arcpy.env.outputCoordinateSystem = region_sr

            #region_shape = os.path.join(ProjectGDB, region_abb+"_Shape")
            region_snap_raster = os.path.join(ProjectGDB, region_abb+"_Snap_Raster")
            region_raster_mask = os.path.join(ProjectGDB, region_abb+"_Raster_Mask")

            arcpy.env.snapRaster = region_snap_raster
            # we need to set the mask and extent of the environment, or the raster and items may not come out correctly.
            arcpy.env.extent = arcpy.Describe(region_snap_raster).extent
            arcpy.env.mask = region_raster_mask

            # These are used later to set the rows and columns for a zero numpy array
            rowCount = int(arcpy.management.GetRasterProperties(region_snap_raster, "ROWCOUNT" ).getOutput(0))
            columnCount = int(arcpy.management.GetRasterProperties(region_snap_raster, "COLUMNCOUNT" ).getOutput(0))

            # For benchmarking.
            log_file = os.path.join(LOG_DIRECTORY, region + ".log")
            # Start with removing the log file if it exists
            #if os.path.isfile(log_file):
            #    os.remove(log_file)

            # Write a message to the log file
            msg = "#-> STARTING {0} ON {1}".format(function, strftime("%a %b %d %I:%M:%S %p", localtime()))
            logFile(log_file, msg)
            del msg

            msg = ">-> Region (abb): {0}\n\t Region:  {1}".format(region_abb, region)
            logFile(log_file, msg)

            # Region richness raster
            # Set region_year_richness_path
            region_year_richness_path = os.path.join(ANALYSIS_DIRECTORY, region_abb, "Core Species Richness")

            if not os.path.isdir(region_year_richness_path):
                os.makedirs(region_year_richness_path)

            if ReplaceRegionYearRichness:
                tmp_workspace = arcpy.env.workspace
                arcpy.env.workspace = region_year_richness_path
                rs = arcpy.ListRasters("*Core_Species_Richness*")
                for r in rs: arcpy.management.Delete(r); del r
                del rs
                arcpy.env.workspace = tmp_workspace
                del tmp_workspace

            # Define region_mosaic
            region_mosaic = os.path.join(ProjectGDB, region_abb)
            # Make region_mosaic_layer
            region_mosaic_layer = arcpy.management.MakeMosaicLayer(region_mosaic, "region_mosaic_layer")

            # Get a unique list of years from the region_mosaic_layer
            years = unique_years(region_mosaic_layer)
            #years = unique_years(region_mosaic)

            if arcpy.Exists("region_mosaic_layer"): arcpy.management.Delete("region_mosaic_layer")
            del region_mosaic_layer

            # Test if we are filtering on years. If so, a new year list is
            # created with the selected years remaining in the list
            if FilterYears:
                # Get a shorter list
                years = [y for y in years if y in selected_years]
            else:
                pass

            for year in years:

                region_year_base_name = "{0}_{1}_".format(region_abb, year)

                region_year_richness = os.path.join(region_year_richness_path, "{0}Core_Species_Richness.tif".format(region_year_base_name))

                if not os.path.isfile(region_year_richness) or ReplaceRegionYearRichness:

                    msg = ">->-> Year: {0}".format(year)
                    logFile(log_file, msg)

                    # Set workspace
                    arcpy.env.workspace = ScratchFolder

                    msg = ">->->-> arcpy.management.ExportMosaicDatasetItems"
                    logFile(log_file, msg)

                    # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
                    # The following inputs are layers or table views: "region_mosaic_layer"

                    arcpy.management.ExportMosaicDatasetItems(#in_mosaic_dataset = "region_mosaic_layer",
                                                              in_mosaic_dataset = region_mosaic,
                                                              out_folder = ScratchFolder,
                                                              out_base_name = region_year_base_name,
                                                              where_clause = "Year = {0} AND CoreSpecies = 'Yes' AND Variable NOT IN ('Species Richness', 'Core Species Richness')".format(year),
                                                              format = "TIFF",
                                                              nodata_value = "-3.40282346639e+38", #-3.402823e+38
                                                              clip_type = "NONE",
                                                              template_dataset = "DEFAULT",
                                                              cell_size = "{0} {0}".format(cell_size))

                    msg = arcpy.GetMessages()
                    msg = ">->->-> {0}\n".format(msg.replace('\n', '\n>->->-> '))
                    logFile(log_file, msg)

                    # Get a list of rasters that are exported from the arcpy.management.ExportMosaicDatasetItems tool
                    # These, for some reason, have TIF as an extension
                    rasters = [r for r in arcpy.ListRasters("{0}*.TIF".format(region_year_base_name)) if "Richness" not in r]
                    for raster in rasters: arcpy.management.CalculateStatistics(raster)
                    del raster
                    #print(rasters)

                    #richnessArray = np.zeros((rowCount, columnCount), dtype=int, order='C')
                    #richnessArray = np.zeros((rowCount, columnCount), dtype=float, order='C')
                    #richnessArray = np.zeros((rowCount, columnCount), dtype=np.int32, order='C')
                    richnessArray = np.zeros((rowCount, columnCount), dtype='float32', order='C')

                    msg = ">->->-> Processing rasters"
                    logFile(log_file, msg)
                    # For each raster exported, create the Con mask
                    for raster in rasters:
                        #arcpy.management.CalculateStatistics(raster)
                        msg = ">->->->-> Processing {0} raster".format(raster)
                        logFile(log_file, msg)

                        # Get Raster Maximum to test of zero rasters
                        #rasterMaximum = float(arcpy.management.GetRasterProperties(raster,"MAXIMUM").getOutput(0))

                        # If Raster Maximum greater than zero, then proceed
                        #if rasterMaximum > 0.0:

                        rasterArray = arcpy.RasterToNumPyArray(raster, nodata_to_value=np.nan)
                        #rasterArray = rasterArray.astype('float32')
                        rasterArray[rasterArray < 0.0] = np.nan

    ##                    maximumRasterArray = np.nanmax(rasterArray)
    ##                    minimumRasterArray = np.nanmin(rasterArray)
    ##
    ##                    msg = ">->->->-> Maximum Biomass Array:         {0}".format(maximumRasterArray)
    ##                    print(msg)
    ##                    del msg
    ##
    ##                    msg = ">->->->-> Minimum Biomass Array:         {0}".format(minimumRasterArray)
    ##                    print(msg)
    ##                    del msg

                        rasterArray[rasterArray > 0.0] = 1.0

    ##                    maximumRasterArray = np.nanmax(rasterArray)
    ##                    minimumRasterArray = np.nanmin(rasterArray)
    ##
    ##                    msg = ">->->->-> Maximum Biomass Array:         {0}".format(maximumRasterArray)
    ##                    print(msg)
    ##                    del msg
    ##
    ##                    msg = ">->->->-> Minimum Biomass Array:         {0}".format(minimumRasterArray)
    ##                    print(msg)
    ##                    del msg

                        #add rasterArray to richnessArray
                        richnessArray = np.add(richnessArray, rasterArray)
                        # Can also use: richnessArray + rasterArray
                        del rasterArray
                    # cleanup
                    # del rasterMaximum

                    #richnessArray[richnessArray <= 0] = np.nan

                    msg = ">->->-> Creating Richness Raster"
                    logFile(log_file, msg)

                    # Create Raster from Array
                    snapRaster = arcpy.Raster(region_snap_raster)
                    lowerLeft = arcpy.Point(snapRaster.extent.XMin, snapRaster.extent.YMin)
                    del snapRaster

                    # Cast array as float32
                    richnessArray = richnessArray.astype('float32')

                    # Convert Array to Raster
                    richnessArrayRaster = arcpy.NumPyArrayToRaster(richnessArray, lowerLeft, cell_size, cell_size, -3.40282346639e+38) #-3.40282346639e+38
                    richnessArrayRaster.save(region_year_richness)
                    del richnessArray, richnessArrayRaster, lowerLeft
                    del rasters

                    arcpy.management.CalculateStatistics(region_year_richness)

                    # Add metadata
                    region_year_richness_md = md.Metadata(region_year_richness)
                    region_year_richness_md.synchronize('ACCESSED', 1)
                    region_year_richness_md.title = "{0} {1}".format(region.replace('-',' to '), DateCode)
                    region_year_richness_md.tags = "{0}, {1}, Core Species Richness".format(geographic_regions[region_abb], year)
                    region_year_richness_md.save()
                    del region_year_richness_md

                    # ###--->>>

                    tmp_workspace = arcpy.env.workspace
                    arcpy.env.workspace = ScratchFolder
                    msg = ">->->-> arcpy.management.Delete in ScratchFolder"
                    logFile(log_file, msg)
                    # This removes the saved rasters in the ScratchFolder
                    #for raster in [r for r in arcpy.ListRasters("*") if "Richness" not in r]: arcpy.management.Delete(raster)
                    for raster in arcpy.ListRasters("*"): arcpy.management.Delete(raster)
                    del raster
                    arcpy.env.workspace = tmp_workspace
                    del tmp_workspace

            # ###--->>>

            # Loading images into the Mosaic.
            msg = '>->->-> Loading the {} Mosaic. This may take a while... Please wait...'.format(region)
            logFile(log_file, msg)

            arcpy.management.AddRastersToMosaicDataset(in_mosaic_dataset = region_mosaic,
                                                       raster_type = "Raster Dataset",
                                                       input_path = region_year_richness_path,
                                                       #input_path = region_year_richness,
                                                       update_cellsize_ranges = "UPDATE_CELL_SIZES",
                                                       #update_cellsize_ranges = "NO_CELL_SIZES",
                                                       update_boundary = "UPDATE_BOUNDARY",
                                                       #update_boundary = "NO_BOUNDARY",
                                                       update_overviews = "NO_OVERVIEWS",
                                                       maximum_pyramid_levels = "",
                                                       maximum_cell_size = "0",
                                                       minimum_dimension = "1500",
                                                       spatial_reference = region_sr,
                                                       #filter = "*Richness.tif",
                                                       filter = "*Core_Species_Richness.tif",
                                                       sub_folder = "NO_SUBFOLDERS",
                                                       #duplicate_items_action = "OVERWRITE_DUPLICATES",
                                                       duplicate_items_action = "EXCLUDE_DUPLICATES",
                                                       build_pyramids = "NO_PYRAMIDS",
                                                       calculate_statistics = "CALCULATE_STATISTICS",
                                                       #calculate_statistics = "NO_STATISTICS",
                                                       build_thumbnails = "BUILD_THUMBNAILS",
                                                       #build_thumbnails = "NO_THUMBNAILS",
                                                       operation_description = "",
                                                       #force_spatial_reference = "NO_FORCE_SPATIAL_REFERENCE",
                                                       force_spatial_reference = "FORCE_SPATIAL_REFERENCE",
                                                       estimate_statistics = "ESTIMATE_STATISTICS",
                                                       #estimate_statistics = "NO_STATISTICS",
                                                       )

            del region_year_richness, region_year_richness_path

            msg = ">->->-> Calculating new values for the new fields in the regional Mosaic Dataset"
            logFile(log_file, msg)

            msg = ">->->-> arcpy.management.MakeTableView Variable_View"
            logFile(log_file, msg)
            # For Multidimensional data (https://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/wkfl-create-a-multidimensional-mosaic-dataset-from-a-set-of-time-series-images.htm)
            # Make table view for calculations
            #arcpy.management.MakeTableView(in_table=region_richness_mosaic, out_view="Variable_View", where_clause="Variable IS NULL", workspace="", )
            arcpy.management.MakeTableView(in_table=region_mosaic, out_view="Variable_View", where_clause="Variable IS NULL OR Variable = 'Core Species Richness'", workspace="", )

            msg = ">->->-> arcpy.management.CalculateField Region"
            logFile(log_file, msg)
            # Process: Calculate Region Field
            arcpy.management.CalculateField("Variable_View", "OARegion", "'{0}'".format(region.replace("'","''")), "PYTHON", "")

            msg = ">->->-> arcpy.management.CalculateField CoreSpecies"
            logFile(log_file, msg)
            # Process: Calculate Region Field
            arcpy.management.CalculateField("Variable_View", "CoreSpecies", "'Yes'", "PYTHON", "")

            msg = ">->->-> arcpy.management.CalculateField Year"
            logFile(log_file, msg)
            # Process: Calculate Year Field
            arcpy.management.CalculateField("Variable_View", "Year", expression="MakeInt( !Name!)", expression_type="PYTHON", code_block="def MakeInt(name):   return int(name[-21:-17]) if 'Core' not in name else int(name[-26:-22])")

            msg = ">->->-> arcpy.management.CalculateField Variable"
            logFile(log_file, msg)
            # Process: Calculate Species Field
            arcpy.management.CalculateField("Variable_View", "Variable", "'Core Species Richness'", "PYTHON", "")

            codeBlock = """def getDate(region, year):
                              from datetime import datetime
                              import pytz
                              regionDateDict = {# Region : Month, Day, Time Zone
                                                'Aleutian Islands'   : [1, 1, 0, 0, 0, 'US/Alaska'],
                                                'Eastern Bering Sea' : [1, 1, 0, 0, 0, 'US/Alaska'],
                                                'Gulf of Alaska' : [1, 1, 0, 0, 0, 'US/Alaska'],
                                                'Gulf of Mexico' : [1, 1, 0, 0, 0, 'US/Central'],
                                                'Hawaii Islands' : [1, 1, 0, 0, 0, 'US/Hawaii'],
                                                "Hawai'i Islands" : [1, 1, 0, 0, 0, 'US/Hawaii'],
                                                'Hawaii' : [1, 1, 0, 0, 0, 'US/Hawaii'],
                                                'Northeast US Fall' : [1, 1, 0, 0, 0, 'US/Eastern'],
                                                'Northeast US Spring' : [1, 1, 0, 0, 0, 'US/Eastern'],
                                                'Southeast US Spring' : [1, 1, 0, 0, 0, 'US/Eastern'],
                                                'Southeast US Summer' : [1, 1, 0, 0, 0, 'US/Eastern'],
                                                'Southeast US Fall' : [1, 1, 0, 0, 0, 'US/Eastern'],
                                                'West Coast Annual' : [1, 1, 0, 0, 0, 'US/Pacific'],
                                                'West Coast Triennial' : [1, 1, 0, 0, 0, 'US/Pacific'],
                                                'West Coast Annual 2003-Present' : [1, 1, 0, 0, 0, 'US/Pacific'],
                                                'West Coast Triennial 1977-2004' : [1, 1, 0, 0, 0, 'US/Pacific'],
                                                'West Coast Annual (2003-Present)' : [1, 1, 0, 0, 0, 'US/Pacific'],
                                                'West Coast Triennial (1977-2004)' : [1, 1, 0, 0, 0, 'US/Pacific'],}
                              month, day, hour, min, sec, timeZone = regionDateDict[region]
                              fmt = "%m/%d/%Y %H:%M:%S"
                              local = pytz.timezone(timeZone)
                              naive = datetime.strptime("{0}/{1}/{2} {3}:{4}:{5}".format(month, day, year, hour, min, sec), fmt)
                              #local_dt = local.localize(naive, is_dst=True)
                              local_dt = local.localize(naive, is_dst=False)
                              utc_dt = local_dt.astimezone(pytz.utc)
                              #return utc_dt.strftime(fmt)
                              return utc_dt"""

            msg = ">->->-> arcpy.management.CalculateField StdTime"
            logFile(log_file, msg)
            arcpy.management.CalculateField("Variable_View", "StdTime", expression="getDate( !OARegion!, !Year! )", expression_type="PYTHON", code_block=codeBlock)
            del codeBlock

            msg = ">->->-> arcpy.management.CalculateField Dimensions"
            logFile(log_file, msg); del msg

            arcpy.management.CalculateField(in_table="Variable_View", field="Dimensions", expression="'StdTime'", expression_type="PYTHON", code_block="")

            arcpy.management.Delete("Variable_View")

            # Cleanup
            del region_mosaic, region_abb
            del region_georef, year, years
            del table_name, csv_file, region_year_base_name
            del region, region_sr
            del rowCount, columnCount
            del region_snap_raster, region_raster_mask, cell_size

        # Cleanup
        del log_file

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = u"#-> Elapsed Time for {0} {1} (H:M:S)\n".format(function, strftime("%H:%M:%S", gmtime(elapse_time)))
        print(msg)
        del msg, start_time, end_time, elapse_time

        localKeys =  [key for key in locals().keys() if "function" not in key]

        if localKeys:
            msg = "Local Keys in {0}(): {1}".format(function, u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys, function

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo

def createCloudRasterFormatExport():
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        #arcpy.AddMessage(function)

        # Set a start time so that we can see how log things take
        start_time = time()

        arcpy.env.overwriteOutput = True
        arcpy.env.scratchWorkspace = ScratchGDB
        arcpy.env.workspace = ProjectGDB
        arcpy.env.overwriteOutput = True

        for table_name in table_names:
            # Assigning variables from items in the chosen table list
            #region_shape = table_name[0]
            #region_boundary = table_name[1]
            region_abb = table_name[2]
            region = table_name[3]
            #csv_file = table_name[4]
            #region_georef = table_name[5]
            #region_contours = table_name[6]
            cell_size = table_name[7]
            arcpy.env.cellSize = cell_size

            # For benchmarking.
            log_file = os.path.join(LOG_DIRECTORY, region + ".log")

            # Write a message to the log file
            msg = "#-> STARTING {0} ON {1}".format(function, strftime("%a %b %d %I:%M:%S %p", localtime()))
            logFile(log_file, msg); del msg

            msg = ">-> Region (abb): {0}\n\t Region:  {1}".format(region_abb, region)
            logFile(log_file, msg); del msg

            # Define region_mosaic
            region_mosaic = os.path.join(ProjectGDB, region_abb)

            ###--->>> Copying the regional Mosaic Dataset to create a Cloud Raster Format Dataset
            msg = "\t\t Copying the regional Mosaic Dataset to create a Cloud Raster Format Dataset"
            logFile(log_file, msg); del msg

            # Copy Raster to CRF
            #crf = os.path.join( MOSAIC_DIRECTORY, "{0} {1}.crf".format(region.replace('-',' to '), DateCode))
            crf = os.path.join( MOSAIC_DIRECTORY, "{0} {1}.crf".format(region_abb, DateCode))
            #print(crf)
            #print(region_mosaic)

            arcpy.management.CopyRaster(region_mosaic,
                                        crf,
                                        '',
                                        None,
                                        "3.4e+38",
                                        "NONE",
                                        "NONE",
                                        '',
                                        "NONE",
                                        "NONE",
                                        "CRF",
                                        "NONE",
                                        "ALL_SLICES",
                                        "NO_TRANSPOSE")

            msg = arcpy.GetMessages()
            msg = ">->-> {0}".format(msg.replace('\n', '\n>->-> '))
            logFile(log_file, msg); del msg

            msg = "\t\t arcpy.management.CalculateStatistics"
            logFile(log_file, msg); del msg

            arcpy.management.CalculateStatistics(crf, 1, 1, [], "OVERWRITE")

            msg = arcpy.GetMessages()
            msg = ">->-> {0}".format(msg.replace('\n', '\n>->-> '))
            logFile(log_file, msg); del msg

            # Add some metadata
            years_md = unique_years(region_mosaic)

            crf_md = md.Metadata(crf)
            crf_md.synchronize('ACCESSED', 1)
            crf_md.title = "{0} {1}".format(region.replace('-',' to '), DateCode)
            crf_md.tags = "{0}, {1} to {2}".format(geographic_regions[region_abb], min(years_md), max(years_md))
            crf_md.save()
            del crf_md, years_md

            del crf
            del table_name, region_abb, region, region_mosaic, cell_size

        # Cleanup
        del log_file

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = u"#-> Elapsed Time for {0} {1} (H:M:S)\n".format(function, strftime("%H:%M:%S", gmtime(elapse_time)))
        print(msg)
        del msg, start_time, end_time, elapse_time

        localKeys =  [key for key in locals().keys() if key not in ['function']]

        if localKeys:
            msg = "#-> Local Keys in function {0}: {1}".format(function, u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys, function

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo

def createIndicatorsTable():
    try:
        temp_workspace = arcpy.env.workspace

        # Set a start time so that we can see how log things take
        start_time = time()

##        - getting the test CenterOfGravityLat and CenterOfGravityDepth into the Indicators table
##        - working on new procedures for calculating CenterOfGravityLat and CenterOfGravityDepth:
##           - ensuring that the interpolated biomass, latitude, and depth rasters all share the same grid (via a snap raster??)
##           - develop latitude raster
##           - develop depth raster
##           - pseudo code for CenterOfGravityLat
##             for each region
##                 for each season
##                     for each species
##                         for each year
##                             sumWtCpue = sum of all wtcpue values (get this from raster stats??)
##                             weightedLat = wtcpue raster * latitude raster
##                             sumWeightedLat = sum of all weightedLat values
##                             CenterOfGravityLatitude = sumWeightedLat/sumWtCpue
##
##        - pseudo code for CenterOfGravityDepth
##
##             same as CenterOfGravityLat except you'll be weighting depth by wtcpue

        # This is s dictionary that maps 'season' codes used as part of the CSV
        # file names. An R script, created by OceanAdap (ref?), parses a data-
        # table to create a set of CSV files that indivdually  contains data
        # for a region/season
        DisMapSeasonCodeDict = {"F" : "Fall",
                                "S" : "Spring",
                                "SPR" : "Spring",
                                "SUM" : "Summer",
                                "FALL" : "Fall",
                                "ANN" : "Annual",
                                "TRI" : "Triennial",
                                "Spring" : "Spring",
                                "Summer" : "Summer",
                                "Fall" : "Fall",
                                "Winter" : "Winter",
                                "Annual" : "Annual",
                                "Triennial" : "Triennial",
                                None : None,
                                '' : ''}

        # Create an empty list to gather tuples
        # row_values = []

        indicators_template = os.path.join(ProjectGDB, u"Indicators_Template")
        indicators = os.path.join(ProjectGDB, u"Indicators")

        if not arcpy.Exists(indicators) or ReplaceIndicatorTable:
            arcpy.management.Delete(indicators)
            arcpy.management.CreateTable(ProjectGDB, u"Indicators", indicators_template, "" ,"")
            msg = arcpy.GetMessages()
            msg = ">->->-> {0}".format(msg.replace('\n', '\n>->->-> '))
            #logFile(log_file, msg)
            print(msg)

        # Start looping over the table_name array as we go region by region.
        for table_name in table_names:
            # Assigning variables from items in the chosen table list
            # region_shape = table_name[0]
            # region_boundary = table_name[1]
            region_abb = table_name[2]
            region = table_name[3]
            csv_file = table_name[4]
            region_georef = table_name[5]
            # region_contours = table_name[6]

            del table_name

            # Start with empty row_values list of list
            #row_values = []

            # Make Geodatabase friendly name
            region_name = region.replace('(','').replace(')','').replace('-','_to_').replace(' ', '_').replace("'", "")

            # List of varaibles for the table
            # OARegionCode = region_abb
            OARegion = region[:region.find("(")].strip() if "(" in region else region
            #Species = ''
            #CommonName = ''
            DisMapRegionCode = region.replace('(','').replace(')','').replace('-','_to_').replace(' ', '_').replace("'", "").lower()
            #RegionText = region
            OASeasonCode = region_abb[region_abb.find('_')+1:] if '_' in region_abb else None
            DisMapSeasonCode = DisMapSeasonCodeDict[OASeasonCode]

##            Region
##            DisMapRegionCode
##            DisMapSeasonCode
##            Species
##            CommonName
##            Year
##            CenterOfGravityLatitude
##            MinimumLatitude
##            MaximumLatitude
##            CenterOfGravityLatitudeStandardError
##            CenterOfGravityLongitude
##            MinimumLongitude
##            MaximumLongitude
##            CenterOfGravityLongitudeStandardError
##            CenterOfGravityDepth
##            MinimumDepth
##            MaximumDepth
##            CenterOfGravityDepthStandardError
##            EffectiveAreaOccupied
##            CoreHabitatArea

            # Clean up
            del OASeasonCode

            # For benchmarking.
            #log_file = os.path.join(LOG_DIRECTORY, region + ".log")
            log_file = os.path.abspath(os.path.join(LOG_DIRECTORY, region + ".log"))

            if os.path.isfile(log_file):
                print(log_file)
                #os.makedirs(log_file)
            # Start with removing the log file if it exists
            #if os.path.isfile(log_file):
            #    os.remove(log_file)

            # Write a message to the log file
            msg = "STARTING REGION {} ON {}".format(region, strftime("%a %b %d %I:%M:%S %p", localtime()))
            logFile(log_file, msg)

            # Set the output coordinate system to what is available for us.
            region_sr = srs[region_georef]
            arcpy.env.outputCoordinateSystem = region_sr
            #del region_sr

            # region abbreviated path
            region_abb_folder = os.path.join(ANALYSIS_DIRECTORY, region_abb)

            # Region Indicators
            region_indicators = os.path.join(ProjectGDB, "{0}_Indicators".format(region_abb))

            # Region Bathymetry
            region_bathymetry = os.path.join(ProjectGDB, "{0}_Bathymetry".format(region_abb))

            # Region Latitude
            region_latitude = os.path.join(ProjectGDB, "{0}_Latitude".format(region_abb))

            # Region Longitude
            region_longitude = os.path.join(ProjectGDB, "{0}_Longitude".format(region_abb))

            # Region Snap Raster
            region_snap_raster = os.path.join(ProjectGDB, "{0}_Snap_Raster".format(region_abb))

            # Region Snap Raster
            region_raster_mask = os.path.join(ProjectGDB, "{0}_Raster_Mask".format(region_abb))

            #arcpy.env.scratchWorkspace = ScratchGDB
            arcpy.env.overwriteOutput = True
            arcpy.env.snapRaster = region_snap_raster
            arcpy.env.extent = arcpy.Describe(region_snap_raster).extent
            arcpy.env.mask = region_raster_mask

            # Tests if the abbreviated region folder exists and if it is in
            # selected regions
            if os.path.isdir(region_abb_folder):
                # msg = ">-> Region (abb): {0}\n\t Region:  {1}\n\t CSV File: {2}\n\t Geo Reference: {3}"\
                #      .format(region_abb, region, csv_file, region_sr)
                msg = ">-> Region (abb): {0}\n\t Region:  {1}\n\t CSV File: {2}"\
                     .format(region_abb, region, csv_file)
                logFile(log_file, msg)
                # List of folders in the region dictory
                species_folders = [d for d in os.listdir(region_abb_folder) if \
                               os.path.isdir(os.path.join(region_abb_folder, d))]
                if species_folders:
                    msg = '>-> There are {0} species folders for the {1} region folder.'.format(len(species_folders), region)
                    logFile(log_file, msg)
                    if FilterSpecies:
                        # Convert the selected species list to matcv the species
                        # folder name by removing haphens and periods
                        selected_species_keys = [ss.replace(".","").replace("-"," ").replace("(","").replace(")","").replace("/","and") for ss in selected_species.keys()]

                        # Find the intersection between the list of specie folders and the filtered list
                        selected_species_folders = list(set(species_folders) & set(selected_species_keys))
                        del selected_species_keys
                        # Sort the list
                        selected_species_folders.sort()
                        if selected_species_folders:
                            # Replace the list
                            species_folders = selected_species_folders[:]
                            msg = '>-> There are {0} selected species in the {1} region folder to process.'.format(len(species_folders), region)
                            logFile(log_file, msg)
                        else:
                            msg = '>-> There are no selected species in the {0} region folder to process.'.format(region)
                            logFile(log_file, msg)
                            msg = '>-> Need to change the selected species list for this region.'
                            logFile(log_file, msg)
                            return
                        del selected_species_folders

                    # Get a disctionary of species and common names from the
                    # CVS Table in the Project GDB
                    csv_file_table = os.path.join(ProjectGDB, csv_file)
                    # Dictionary of species and common names that are in the tables
                    species_common_name_dict = unique_fish_dict(csv_file_table)
                    #print( species_common_name_dict )
                    #print("Is the")

                    # Clean up
                    del csv_file_table
                else:
                    msg = '>-> There are no species folders in the region ({0}) folder.'.format(region)
                    logFile(log_file, msg)
                    msg = '>-> Need to run generateRasters to create images.'
                    logFile(log_file, msg)
                    return
            else:
                msg = '>-> The folder for this region ({0}) is missing from the Analysis Folder and needs to be created.'.format(region)
                logFile(log_file, msg)
                return

            # Cleanup
            del region_georef

            # Creating the region indicator table to be used. We output this to the file system in the appropriate folder.
            msg = '> Creating the {} Indicators Table. This may take a while... Please wait...'.format(region)
            logFile(log_file, msg)

            if not arcpy.Exists( region_indicators ) or ReplaceRegionIndicatorTable:
                # If ReplaceRegionIndicatorTable is True:
                if ReplaceRegionIndicatorTable and arcpy.Exists(region_indicators):
                    msg = '>-> Removing the {0} Region Indicators Table'.format(region)
                    logFile(log_file, msg)

                    # Geoprocessing tools return a result object of the derived
                    # output dataset.
                    result = arcpy.management.Delete(region_indicators)
                    msg = arcpy.GetMessages()
                    msg = ">->-> {0}\n".format(msg.replace('\n', '\n>->-> '))
                    logFile(log_file, msg)
                    del msg
                    del result

                else:
                    msg = ">-> Replace Indicator Datasets set to True, but {0} Indicator Dataset is missing".format(region)
                    logFile(log_file, msg)

                indicators_view = arcpy.management.MakeTableView(indicators, 'Indicators_View', "OARegion = '{0}'".format(region.replace("'", "''")))
                arcpy.management.DeleteRows('Indicators_View')
                msg = arcpy.GetMessages()
                msg = ">->-> {0}\n".format(msg.replace('\n', '\n>->-> '))
                logFile(log_file, msg)
                result = arcpy.management.Delete('Indicators_View')
                msg = arcpy.GetMessages()
                msg = ">->-> {0}\n".format(msg.replace('\n', '\n>->-> '))
                logFile(log_file, msg)
                del indicators_view
                del result

                msg = '>-> Creating the {} Indicator Table'.format(region)
                logFile(log_file, msg)

                # Set local variables
                out_path = ProjectGDB
                out_name = "{0}_Indicators".format(region_abb)
                template = indicators_template
                config_keyword = ""

                # Execute CreateTable
                arcpy.management.CreateTable(out_path, out_name, template, config_keyword)
                msg = arcpy.GetMessages()
                msg = ">->-> {0}".format(msg.replace('\n', '\n>->->-> '))
                logFile(log_file, msg)

                del out_path, out_name, template, config_keyword

                # Loading images into the Mosaic.
                # msg = '> Loading the {} Indicator Dataset. This may take a while... Please wait...'.format(region)
                # logFile(log_file, msg)

                # Start with empty row_values list of list
                row_values = []

                # Loop through dictionary
                for Species in species_common_name_dict:
                    # Speices folders do not include the '.' that can be a part
                    # of the name, so remove
                    species_folder = Species.replace(".","").replace("-"," ").replace("(","").replace(")","").replace("/","and")
                    # The common name is the value in the dictionary
                    CommonName = species_common_name_dict[Species][0]
                    #print(CommonName)
                    CoreSpecies = species_common_name_dict[Species][1]
                    #print(CoreSpecies)
                    # Create an item for multidimensional variable list
                    #speciesCommonName = "'{0}' '{1}' #".format(species, common)
                    # print("\t\t '{0}'".format(speciesCommonName))
                    # 'Centropristis striata' 'Centropristis striata' #
                    # Append that item to speciesCommonNameRegionList
                    #speciesCommonNameRegionList.append(speciesCommonName)
                    #del speciesCommonName

                    # Test of the speices folder name from the dictionary is in
                    # the list of folders in the region folder. The species
                    # folder may not have been created, so need to test
                    # if species_folder in species_folders first, then as a filter see
                    # if species is in a shorter list. Will need to change this later

                    # This test is species is in selected species
                    if species_folder in species_folders: # and species_folder in selected_species.keys():

                        # Test if there a corresponding folder in RASTER DIRECTORY, if
                        # not create the folder
                        #out_species_folder = os.path.join(MOSAIC_DIRECTORY, region_abb, species_folder)
                        # Make the speices folder in the raster directory if missing
                        #if not os.path.isdir(out_species_folder):
                        #    os.makedirs(out_species_folder)
                        msg = ">->-> Species: {0}, Common Name: {1}".format(Species, CommonName)
                        logFile(log_file, msg)

                        input_folder = os.path.join(region_abb_folder, species_folder)

                        msg = ">->-> Processing Biomass Rasters"
                        logFile(log_file, msg)

                        arcpy.env.workspace = input_folder
                        biomassRasters = arcpy.ListRasters("*.tif")
                        #print(biomassRasters)
                        #print(selected_years)
                        # Test if we are filtering on years. If so, a new year list is
                        # created with the selected years remaining in the list
                        if FilterYears:
                            # Get a shorter list
                            #biomassRasters = [r for r in biomassRasters if int(r.replace(".tif", "")) in selected_years]
                            biomassRasters = [r for r in biomassRasters if int(r[-8:-4]) in selected_years]
                        else:
                            pass
                        #print(biomassRasters)

                        # ###--->>> This is to get a median biomass value for all years
                        biomassBigArray = np.array([])
                        for biomassRaster in sorted(biomassRasters):
                            # Get maximumBiomass value to filter out "zero" rasters
                            maximumBiomass = float(arcpy.management.GetRasterProperties(biomassRaster,"MAXIMUM").getOutput(0))
                            # If maximumBiomass greater than zero, then process raster
                            if maximumBiomass > 0.0:
                                # Use Raster To NumPy Array
                                biomassArray = arcpy.RasterToNumPyArray(biomassRaster, nodata_to_value=np.nan)
                                # Set zero and smaller values to NaN
                                biomassArray[biomassArray <= 0.0] = np.nan
                                # make the biomass arrays one dimensional
                                flatBiomassArray = biomassArray.flatten()
                                # Remove NaN values from flatten (1-D) array
                                flatBiomassArray = flatBiomassArray[~np.isnan(flatBiomassArray)]
                                # Append Yearly Flatten Biomass Array to the big array (for all years)
                                biomassBigArray = np.append(biomassBigArray, flatBiomassArray)
                        # After processing all years, get the median value
                        medianBiomass  = np.median(flatBiomassArray)
                        # Cleanup
                        del biomassBigArray, maximumBiomass, biomassArray, flatBiomassArray
                        # ###--->>> This is to get a median biomass value for all years

                        first_year = 9999
                        # Process rasters
                        for biomassRaster in sorted(biomassRasters):
                            # Get year from raster name
                            Year = int(biomassRaster[-8:-4])

                            msg = ">->->-> Processing {0} Biomass Raster".format(biomassRaster)
                            logFile(log_file, msg)

                            # Get maximumBiomass value to filter out "zero" rasters
                            maximumBiomass = float(arcpy.management.GetRasterProperties(biomassRaster,"MAXIMUM").getOutput(0))

                            msg = ">->->->-> Biomass Raster Maximum: {0}".format(maximumBiomass)
                            logFile(log_file, msg)
                            del msg

                            # If maximumBiomass greater than zero, then process raster
                            if maximumBiomass > 0.0:
                                msg = ">->->->-> Calculating indicators"
                                logFile(log_file, msg)

                                # Test is for first year
                                if Year < first_year:
                                    first_year = Year

                            # ###--->>> Biomass Start

                                #biomassArray = arcpy.RasterToNumPyArray(masked_biomass_raster, nodata_to_value=np.nan)
                                biomassArray = arcpy.RasterToNumPyArray(biomassRaster, nodata_to_value=np.nan)
                                biomassArray[biomassArray <= 0.0] = np.nan
                                #biomassArray[biomassArray <= 0.001] = np.nan

                                #arcpy.management.Delete(masked_biomass_raster)
                                #del masked_biomass_raster

                                #sumWtCpue = sum of all wtcpue values (get this from biomassRaster stats??)
                                sumBiomassArray = np.nansum(biomassArray)

                                #msg = ">->->->-> sumBiomassArray: {0}".format(sumBiomassArray)
                                #logFile(log_file, msg)
                                #del msg

                                #msg = ">->->->-> biomassArray non-nan count: {0}".format(np.count_nonzero(~np.isnan(biomassArray)))
                                #logFile(log_file, msg)
                                #del msg
                            # ###--->>> Biomass End

                            # ###--->>> Latitude Start
                                #latitudeArray = arcpy.RasterToNumPyArray(masked_latitude_raster, nodata_to_value = np.nan)
                                #arcpy.management.Delete(masked_latitude_raster)
                                #del masked_latitude_raster

                                # Latitude
                                latitudeArray = arcpy.RasterToNumPyArray(region_latitude, nodata_to_value=np.nan)
                                #print(latitudeArray.shape)
                                latitudeArray[np.isnan(biomassArray)] = np.nan
                                #print(latitudeArray.shape)

                            ##    msg = ">->->->-> latitudeArray non-nan count: {0}".format(np.count_nonzero(~np.isnan(latitudeArray)))
                            ##    logFile(log_file, msg)
                            ##    del msg

                            ##    msg = ">->->->-> Latitude Min: {0}".format(np.nanmin(latitudeArray))
                            ##    logFile(log_file, msg)
                            ##    del msg
                            ##    msg = ">->->->-> Latitude Max: {0}".format(np.nanmax(latitudeArray))
                            ##    logFile(log_file, msg)
                            ##    del msg

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

                                del sortedBiomassArrayCumSum, sortedBiomassArrayQuantile, diffArray, minIndex
                                del sortedLatitudeArray, sortedBiomassArray, flatBiomassArray
                                del latsInds, flatLatitudeArray

                                weightedLatitudeArray = np.multiply(biomassArray, latitudeArray)

                                sumWeightedLatitudeArray = np.nansum(weightedLatitudeArray)

                                #msg = ">->->->-> Sum Weighted Latitude: {0}".format(sumWeightedLatitudeArray)
                                #logFile(log_file, msg)
                                #del msg

                                #CenterOfGravityLatitude = round(sumWeightedLatitudeArray / sumBiomassArray, 6)
                                CenterOfGravityLatitude = sumWeightedLatitudeArray / sumBiomassArray

                                if Year == first_year:
                                    first_year_offset_latitude = CenterOfGravityLatitude

                                OffsetLatitude = CenterOfGravityLatitude - first_year_offset_latitude

                                # cog_se<-(sqrt(wtd.var(BioComb$NEUS_F_Latitude, w=BioComb$X1972)))/sqrt(length(BioComb$NEUS_F_Latitude))
                                # cog_se<-(sqrt(wtd.var(BioComb$NEUS_F_Latitude, w=BioComb$NEUS_F_Centropristis_striata_1972)))/sqrt(length(BioComb$NEUS_F_Latitude))
                                # cog st err is 0.00395

                                weightedLatitudeArrayVariance = np.nanvar(weightedLatitudeArray)
                                weightedLatitudeArrayCount = np.count_nonzero(~np.isnan(weightedLatitudeArray))

                                CenterOfGravityLatitudeStandardError = math.sqrt(weightedLatitudeArrayVariance) / math.sqrt(weightedLatitudeArrayCount)

                                del weightedLatitudeArrayVariance, weightedLatitudeArrayCount

                                #msg = ">->->->-> Center of Gravity Latitude: {0}".format(round(CenterOfGravityLatitude,6))
                                msg = ">->->->-> Center of Gravity Latitude: {0}".format(CenterOfGravityLatitude)
                                logFile(log_file, msg)
                                del msg

                                msg = ">->->->-> Minimum Latitude (5th Percentile): {0}".format(MinimumLatitude)
                                logFile(log_file, msg)
                                del msg

                                msg = ">->->->-> Maximum Latitude (95th Percentile): {0}".format(MaximumLatitude)
                                logFile(log_file, msg)
                                del msg

                                msg = ">->->->-> Offset Latitude: {0}".format(OffsetLatitude)
                                logFile(log_file, msg)
                                del msg

                                msg = ">->->->-> Center of Gravity Latitude Standard Error: {0}".format(CenterOfGravityLatitudeStandardError)
                                logFile(log_file, msg)
                                del msg

                                del latitudeArray, weightedLatitudeArray, sumWeightedLatitudeArray

                            # ###--->>> Latitude End

                            # ###--->>> Longitude Start
                                #longitudeArray = arcpy.RasterToNumPyArray(masked_longitude_raster, nodata_to_value = np.nan)
                                #arcpy.management.Delete(masked_longitude_raster)
                                #del masked_longitude_raster

                                # Longitude
                                # Doesn't work for International Date Line
                                #longitudeArray = arcpy.RasterToNumPyArray(region_longitude, nodata_to_value=np.nan)
                                #longitudeArray[np.isnan(biomassArray)] = np.nan

                                # For issue of international date line
                                # Added/Modified by JFK June 15, 2022
                                longitudeArray = arcpy.RasterToNumPyArray(region_longitude, nodata_to_value=np.nan)
                                longitudeArray = np.mod(longitudeArray, 360.0)
                                longitudeArray[np.isnan(biomassArray)] = np.nan

                                #msg = ">->->->-> longitudeArray non-nan count: {0}".format(np.count_nonzero(~np.isnan(longitudeArray)))
                                #logFile(log_file, msg)
                                #del msg

                                #msg = ">->->->-> Longitude Min: {0}".format(np.nanmin(longitudeArray))
                                #logFile(log_file, msg)
                                #del msg
                                #msg = ">->->->-> Longitude Max: {0}".format(np.nanmax(longitudeArray))
                                #logFile(log_file, msg)
                                #del msg

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

                                #maxLat = sortedLongitudeArray[minIndex]
                                MaximumLongitude = sortedLongitudeArray[minIndex]

                                # do the same for 0.05

                                diffArray = np.abs(sortedBiomassArrayQuantile - 0.05)

                                minIndex = diffArray.argmin()

                                #minLat = sortedLongitudeArray[minIndex]
                                MinimumLongitude = sortedLongitudeArray[minIndex]

                                del sortedBiomassArrayCumSum, sortedBiomassArrayQuantile, diffArray, minIndex
                                del sortedLongitudeArray, sortedBiomassArray, flatBiomassArray
                                del longsInds, flatLongitudeArray

                                weightedLongitudeArray = np.multiply(biomassArray, longitudeArray)

                                sumWeightedLongitudeArray = np.nansum(weightedLongitudeArray)

                                #CenterOfGravityLongitude = round(sumWeightedLongitudeArray / sumBiomassArray, 6)
                                CenterOfGravityLongitude = sumWeightedLongitudeArray / sumBiomassArray

                                if Year == first_year:
                                    first_year_offset_longitude = CenterOfGravityLongitude

                                OffsetLongitude = CenterOfGravityLongitude - first_year_offset_longitude

                                # cog_se<-(sqrt(wtd.var(BioComb$NEUS_F_Latitude, w=BioComb$X1972)))/sqrt(length(BioComb$NEUS_F_Latitude))
                                # cog_se<-(sqrt(wtd.var(BioComb$NEUS_F_Latitude, w=BioComb$NEUS_F_Centropristis_striata_1972)))/sqrt(length(BioComb$NEUS_F_Latitude))
                                # cog st err is 0.00395

                                weightedLongitudeArrayVariance = np.nanvar(weightedLongitudeArray)
                                weightedLongitudeArrayCount = np.count_nonzero(~np.isnan(weightedLongitudeArray))

                                CenterOfGravityLongitudeStandardError = math.sqrt(weightedLongitudeArrayVariance) / math.sqrt(weightedLongitudeArrayCount)

                                del weightedLongitudeArrayVariance, weightedLongitudeArrayCount

                                # Convert 360 back to 180
                                # Added/Modified by JFK June 15, 2022
                                CenterOfGravityLongitude = np.mod(CenterOfGravityLongitude - 180.0, 360.0) - 180.0
                                MinimumLongitude = np.mod(MinimumLongitude - 180.0, 360.0) - 180.0
                                MaximumLongitude = np.mod(MaximumLongitude - 180.0, 360.0) - 180.0

                                #msg = ">->->->-> Sum Weighted Longitude: {0}".format(sumWeightedLongitudeArray)
                                #logFile(log_file, msg)
                                #del msg

                                #msg = ">->->->-> Center of Gravity Longitude: {0}".format(round(CenterOfGravityLongitude,6))
                                msg = ">->->->-> Center of Gravity Longitude: {0}".format(CenterOfGravityLongitude)
                                logFile(log_file, msg)
                                del msg

                                #msg = ">->->->-> Center of Gravity Longitude: {0}".format(np.mod(CenterOfGravityLongitude - 180.0, 360.0) -180.0)
                                #logFile(log_file, msg)
                                #del msg

                                msg = ">->->->-> Minimum Longitude (5th Percentile): {0}".format(MinimumLongitude)
                                logFile(log_file, msg)
                                del msg

                                msg = ">->->->-> Maximum Longitude (95th Percentile): {0}".format(MaximumLongitude)
                                logFile(log_file, msg)
                                del msg

                                msg = ">->->->-> Offset Longitude: {0}".format(OffsetLongitude)
                                logFile(log_file, msg)
                                del msg

                                msg = ">->->->-> Center of Gravity Longitude Standard Error: {0}".format(CenterOfGravityLongitudeStandardError)
                                logFile(log_file, msg)
                                del msg

                                del longitudeArray, weightedLongitudeArray, sumWeightedLongitudeArray

                            # ###--->>> Center of Gravity Depth Start
                                # ###--->>> Bathymetry (Depth)
                                #bathymetryArray = arcpy.RasterToNumPyArray(masked_bathymetry_raster, nodata_to_value = np.nan)
                                #arcpy.management.Delete(masked_bathymetry_raster)
                                #del masked_bathymetry_raster

                                # Bathymetry
                                bathymetryArray = arcpy.RasterToNumPyArray(region_bathymetry, nodata_to_value=np.nan)
                                # If biomass cells are Null, make bathymetry cells Null as well
                                bathymetryArray[np.isnan(biomassArray)] = np.nan
                                # For bathymetry values zero are larger, make zero
                                bathymetryArray[bathymetryArray >= 0.0] = 0.0

                                #msg = ">->->->-> bathymetryArray non-nan count: {0}".format(np.count_nonzero(~np.isnan(bathymetryArray)))
                                #logFile(log_file, msg)
                                #del msg

                                #msg = ">->->->-> Bathymetry Min: {0}".format(np.nanmin(bathymetryArray))
                                #logFile(log_file, msg)
                                #del msg
                                #msg = ">->->->-> Bathymetry Max: {0}".format(np.nanmax(bathymetryArray))
                                #logFile(log_file, msg)
                                #del msg

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

                                # find the difference between 0.95 and each cumulative sum value ... asbolute value gives the closest distance

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

                                #msg = ">->->->-> Sum Weighted Bathymetry: {0}".format(sumWeightedBathymetryArray)
                                #logFile(log_file, msg)
                                #del msg

                                #CenterOfGravityDepth = round(sumWeightedBathymetryArray / sumBiomassArray, 6)
                                CenterOfGravityDepth = sumWeightedBathymetryArray / sumBiomassArray

                                if Year == first_year:
                                    first_year_offset_depth = CenterOfGravityDepth

                                OffsetDepth = CenterOfGravityDepth - first_year_offset_depth

                                # cog_se<-(sqrt(wtd.var(BioComb$NEUS_F_Latitude, w=BioComb$X1972)))/sqrt(length(BioComb$NEUS_F_Latitude))
                                # cog_se<-(sqrt(wtd.var(BioComb$NEUS_F_Latitude, w=BioComb$NEUS_F_Centropristis_striata_1972)))/sqrt(length(BioComb$NEUS_F_Latitude))
                                # cog st err is 0.00395

                                weightedBathymetryArrayVariance = np.nanvar(weightedBathymetryArray)
                                weightedBathymetryArrayCount = np.count_nonzero(~np.isnan(weightedBathymetryArray))

                                CenterOfGravityDepthStandardError = math.sqrt(weightedBathymetryArrayVariance) / math.sqrt(weightedBathymetryArrayCount)

                                del weightedBathymetryArrayVariance, weightedBathymetryArrayCount

                                #msg = ">->->->-> Center of Gravity Depth: {0}".format(round(CenterOfGravityDepth,6))
                                msg = ">->->->-> Center of Gravity Depth: {0}".format(CenterOfGravityDepth)
                                logFile(log_file, msg)
                                del msg

                                msg = ">->->->-> Minimum Depth (5th Percentile): {0}".format(MinimumDepth)
                                logFile(log_file, msg)
                                del msg

                                msg = ">->->->-> Maximum Depth (95th Percentile): {0}".format(MaximumDepth)
                                logFile(log_file, msg)
                                del msg

                                msg = ">->->->-> Offset Depth: {0}".format(OffsetDepth)
                                logFile(log_file, msg)
                                del msg

                                msg = ">->->->-> Center of Gravity Depth Standard Error: {0}".format(CenterOfGravityDepthStandardError)
                                logFile(log_file, msg)
                                del msg

                                del bathymetryArray, weightedBathymetryArray, sumWeightedBathymetryArray

                            # ###--->>> Center of Gravity Depth End

                            # ###--->>> Effective Area Occupied Start

                                # biomassSquaredArray = biomassArray * biomassArray (use numpy.multiply?)
                                biomassSquaredArray = np.multiply(biomassArray, biomassArray)

                                # sumBiomassSquared = sum of biomassSquaredArray (use numpy.sum?)
                                sumBiomassSquared = np.nansum(biomassSquaredArray)

                                # Clean-up
                                del biomassSquaredArray

                                #msg = ">->->->-> Sum (total) Biomass: {0} WTCPUE".format(sumBiomassArray)
                                #logFile(log_file, msg)
                                #del msg

                                #msg = ">->->->-> Sum of Biomass Squared Array: {0}".format(sumBiomassSquared)
                                #logFile(log_file, msg)
                                #del msg

                                # ###--->>> Effective Area Occupied
                                #EffectiveAreaOccupied = (sumBiomassArray * sumBiomassArray) / sumBiomassSquared

                                #msg = ">->->->-> Effective Area Occupied: {0}".format(EffectiveAreaOccupied)
                                #logFile(log_file, msg)
                                #del msg

                                # Clean-up
                                del sumBiomassSquared

                            # ###--->>> Effective Area Occupied End

                            # ###--->>> Core Habitat Area Start
                                #msg = ">->->->-> biomassArray min: {0}".format(np.nanmin(biomassArray))
                                #logFile(log_file, msg)
                                #del msg
                                #msg = ">->->->-> biomassArray max: {0}".format(np.nanmax(biomassArray))
                                #logFile(log_file, msg)
                                #del msg
                                #msg = ">->->->-> biomassArray mean: {0}".format(np.nanmean(biomassArray))
                                #logFile(log_file, msg)
                                #del msg

                                # cellArea = 2000 x 2000 (... or 2 x 2 to for square km)
                                #cellArea = cell_size * cell_size
                                #cell_size = 2000
                                #cellArea = cell_size/1000 * cell_size/1000

                                # medianBiomass = median of biomassArray (use numpy.median?)
                                # medianBiomass = np.nanmedian(biomassArray)

                                # biomassGTMedianArray = only those biomassArray values GT medianBiomass (not sure how)
                                biomassGTMedianArray = np.copy(biomassArray)
                                biomassGTMedianArray[biomassArray < medianBiomass] = np.nan

                                # countValues = count of non-null values in biomassGTMedianArray
                                countValues = np.count_nonzero(~np.isnan(biomassGTMedianArray))

                                # CoreHabitatArea = countValues * cellArea
                                #CoreHabitatArea = countValues * cellArea

                                #msg = ">->->->-> Cell Area: {0} sqr km".format(cellArea)
                                #logFile(log_file, msg)
                                #del msg
                                #msg = ">->->->-> Median Biomass: {0}".format(medianBiomass)
                                #logFile(log_file, msg)
                                #del msg
                                #msg = ">->->->-> Count Values: {0}".format(countValues)
                                #logFile(log_file, msg)
                                #del msg
                                #msg = ">->->->-> Core Habitat Area: {0} sqr km".format(CoreHabitatArea)
                                #logFile(log_file, msg)
                                #del msg

                                #del cellArea
                                del biomassGTMedianArray
                                del countValues, biomassRaster, biomassArray, sumBiomassArray
                            # ###--->>> Core Habitat Area End


                            elif maximumBiomass == 0.0:
                               CenterOfGravityLatitude = None
                               MinimumLatitude = None
                               MaximumLatitude = None
                               OffsetLatitude = None
                               CenterOfGravityLatitudeStandardError = None
                               CenterOfGravityLongitude = None
                               MinimumLongitude = None
                               MaximumLongitude = None
                               OffsetLongitude = None
                               CenterOfGravityLongitudeStandardError = None
                               CenterOfGravityDepth = None
                               MinimumDepth = None
                               MaximumDepth = None
                               OffsetDepth = None
                               CenterOfGravityDepthStandardError = None
                               #EffectiveAreaOccupied = None
                               #CoreHabitatArea = None
                               del biomassRaster
                            else:
                                print('Something wrong with biomass raster')

                            row = [OARegion,
                                   DisMapRegionCode,
                                   DisMapSeasonCode,
                                   Species,
                                   CommonName,
                                   CoreSpecies,
                                   Year,
                                   CenterOfGravityLatitude,
                                   MinimumLatitude,
                                   MaximumLatitude,
                                   OffsetLatitude,
                                   CenterOfGravityLatitudeStandardError,
                                   CenterOfGravityLongitude,
                                   MinimumLongitude,
                                   MaximumLongitude,
                                   OffsetLongitude,
                                   CenterOfGravityLongitudeStandardError,
                                   CenterOfGravityDepth,
                                   MinimumDepth,
                                   MaximumDepth,
                                   OffsetDepth,
                                   CenterOfGravityDepthStandardError,
                                   #EffectiveAreaOccupied,
                                   #CoreHabitatArea
                                   ]

                            # Append to list
                            row_values.append(row)
                            del row

                            # Clean-up
                            del maximumBiomass
                            del Year, CenterOfGravityLatitude, MinimumLatitude, MaximumLatitude
                            del CenterOfGravityLatitudeStandardError, CenterOfGravityLongitude
                            del MinimumLongitude, MaximumLongitude
                            del CenterOfGravityLongitudeStandardError, CenterOfGravityDepth
                            del MinimumDepth, MaximumDepth, CenterOfGravityDepthStandardError
                            #del EffectiveAreaOccupied, CoreHabitatArea
                            del OffsetLatitude, OffsetLongitude, OffsetDepth
                            #del Species, CommonName, CoreSpecies

                        del medianBiomass
                        del first_year
                        del first_year_offset_latitude, first_year_offset_longitude, first_year_offset_depth
                    else:
                        pass # Passng for the moment to limit print output
                        #msg = "###--->>> Species: {0} does not have a folder, Common Name: {1}".format(Species, CommonName)
                        #logFile(log_file, msg)
                        #del msg

                    del Species, CommonName, CoreSpecies

                msg = ">->->-> Inserting records into the table"
                print(msg)
                del msg

                for row_value in row_values:
                    #print(row_value)
                    print("Region: {0}".format(row_value[0]))
                    print("DisMapRegionCode: {0}".format(row_value[1]))
                    print("DisMapSeasonCode: {0}".format(row_value[2]))
                    print("Species: {0}".format(row_value[3]))
                    print("CommonName: {0}".format(row_value[4]))
                    print("CoreSpecies: {0}".format(row_value[5]))
                    print("Year: {0}".format(row_value[6]))
                    print("\tCenterOfGravityLatitude: {0}".format(row_value[7]))
                    print("\tMinimumLatitude: {0}".format(row_value[8]))
                    print("\tMaximumLatitude: {0}".format(row_value[9]))
                    print("\tOffsetLatitude: {0}".format(row_value[10]))
                    print("\tCenterOfGravityLatitudeStandardError: {0}".format(row_value[11]))
                    print("\tCenterOfGravityLongitude: {0}".format(row_value[12]))
                    print("\tMinimumLongitude: {0}".format(row_value[13]))
                    print("\tMaximumLongitude: {0}".format(row_value[14]))
                    print("\tOffsetLongitude: {0}".format(row_value[15]))
                    print("\tCenterOfGravityLongitudeStandardError: {0}".format(row_value[16]))
                    print("\tCenterOfGravityDepth: {0}".format(row_value[17]))
                    print("\tMinimumDepth: {0}".format(row_value[18]))
                    print("\tMaximumDepth: {0}".format(row_value[19]))
                    print("\tOffsetDepth: {0}".format(row_value[20]))
                    print("\tCenterOfGravityDepthStandardError: {0}".format(row_value[21]))
                    #print("\tEffectiveAreaOccupied: {0}".format(row_value[22]))
                    #print("\tCoreHabitatArea: {0}".format(row_value[23]))
                if row_value: del row_value

                # This gets a list of fields in the table
                fields = [f.name for f in arcpy.ListFields(region_indicators) if f.name != 'OBJECTID']
                #print(fields)

                # Open an InsertCursor
                cursor = arcpy.da.InsertCursor(region_indicators, fields)

                # Insert new rows into the table
                for row in row_values:
                    try:
                        row = [None if x != x else x for x in row]
                        cursor.insertRow(row)
                        del row
                    except:
                        #print(fields)
                        print("Row: {0}".format(row))

                #print(row_values)
                # Delete cursor object
                del cursor
                del row_values

                # Remove Identical Records
                arcpy.management.DeleteIdentical(in_dataset=region_indicators, fields=fields, xy_tolerance="", z_tolerance="0")
                msg = arcpy.GetMessages()
                msg = ">-> {0}\n".format(msg.replace('\n', '\n>-> '))
                logFile(log_file, msg); del msg

                del fields

                # Make XY Event  Layer
                my_events = arcpy.management.MakeXYEventLayer(region_indicators, "CenterOfGravityLongitude", "CenterOfGravityLatitude", "my_events","#","#")

                # Make it a feature class and output it to the local hard disk drive (for usage and debugging purposes)
                arcpy.FeatureClassToFeatureClass_conversion(in_features=my_events, out_path=ProjectGDB, out_name= "{0}_Indicators_COG".format(region_abb),
                                                            where_clause='',
                                                            field_mapping='',
                                                            #field_mapping="""Field1 "Field1" true true false 50 Text 0 0 ,First,#,my_events,Field1,-1,-1;region "region" true true false 50 Text 0 0 ,First,#,my_events,region,-1,-1;haulid "haulid" true true false 255 Text 0 0 ,First,#,my_events,haulid,-1,-1;year "year" true true false 4 Long 0 0 ,First,#,my_events,year,-1,-1;spp "spp" true true false 50 Text 0 0 ,First,#,my_events,spp,-1,-1;wtcpue "wtcpue" true true false 8 Double 10 20 ,First,#,my_events,wtcpue,-1,-1;common "common" true true false 50 Text 0 0 ,First,#,my_events,common,-1,-1;lat "lat" true true false 8 Double 10 20 ,First,#,my_events,lat,-1,-1;stratum "stratum" true true false 50 Text 0 0 ,First,#,my_events,stratum,-1,-1;stratumare "stratumare" true true false 50 Text 0 0 ,First,#,my_events,stratumarea,-1,-1;lon "lon" true true false 8 Double 10 20 ,First,#,my_events,lon,-1,-1;depth "depth" true true false 50 Text 0 0 ,First,#,my_events,depth,-1,-1""",
                                                            config_keyword="")
                #arcpy.conversion.FeatureClassToFeatureClass("neusf_csv_XYTableToPoint", r"C:\Users\jfken\Documents\GitHub\DisMap\Default.gdb", "neusf_csv_XY", '', 'csv_id "csv_id" true true false 4 Long 0 0,First,#,neusf_csv_XYTableToPoint,csv_id,-1,-1;region "region" true true false 34 Text 0 0,First,#,neusf_csv_XYTableToPoint,region,0,34;haulid "haulid" true true false 30 Text 0 0,First,#,neusf_csv_XYTableToPoint,haulid,0,30;year "year" true true false 4 Long 0 0,First,#,neusf_csv_XYTableToPoint,year,-1,-1;spp "spp" true true false 64 Text 0 0,First,#,neusf_csv_XYTableToPoint,spp,0,64;wtcpue "wtcpue" true true false 8 Double 0 0,First,#,neusf_csv_XYTableToPoint,wtcpue,-1,-1;wtc_cube "wtc_cube" true true false 8 Double 0 0,First,#,neusf_csv_XYTableToPoint,wtc_cube,-1,-1;common "common" true true false 64 Text 0 0,First,#,neusf_csv_XYTableToPoint,common,0,64;stratum "stratum" true true false 4 Long 0 0,First,#,neusf_csv_XYTableToPoint,stratum,-1,-1;stratumarea "stratumarea" true true false 8 Double 0 0,First,#,neusf_csv_XYTableToPoint,stratumarea,-1,-1;lat "lat" true true false 8 Double 0 0,First,#,neusf_csv_XYTableToPoint,lat,-1,-1;lon "lon" true true false 8 Double 0 0,First,#,neusf_csv_XYTableToPoint,lon,-1,-1;depth "depth" true true false 8 Double 0 0,First,#,neusf_csv_XYTableToPoint,depth,-1,-1', '')

                # Clear the XY Event Layer from memory.
                arcpy.management.Delete("my_events")
                del my_events

                # Append Region Indicators to Indicators Table
                arcpy.management.Append(inputs=region_indicators, target=indicators, schema_type="TEST", field_mapping="", subtype="")

                # Add some metadata
                years_md = unique_years(region_indicators)

                region_indicators_md = md.Metadata(region_indicators)
                region_indicators_md.synchronize('ACCESSED', 1)
                region_indicators_md.title = "{0} Indicators {1}".format(region.replace('-',' to '), DateCode)
                region_indicators_md.tags = "{0}, {1} to {2}".format(geographic_regions[region_abb], min(years_md), max(years_md))
                region_indicators_md.save()
                del region_indicators_md, years_md

                del input_folder, biomassRasters, species_folder

            else:
                print("Region {0} Indicator Table exists or ReplaceIndicatorTable is set to False".format(region_abb))

            # Clean up
            del csv_file, region_name
            del region_abb_folder, region_sr, region_abb
            del OARegion #, Species, CommonName, CoreSpecies
            del DisMapRegionCode, DisMapSeasonCode
            del region_indicators, region_bathymetry, region_latitude
            del region_longitude, region_raster_mask, species_folders
            del species_common_name_dict
            #del medianBiomass

            #Final benchmark for the region.
            msg = "ENDING REGION {} COMPLETED ON {}".format(region, strftime("%a %b %d %I:%M:%S %p", localtime()))
            logFile(log_file, msg)
            del msg
            del region

        # This gets a list of fields in the table
        fields = [f.name for f in arcpy.ListFields(indicators) if f.name != 'OBJECTID']

        # Remove Identical Records
        arcpy.management.DeleteIdentical(in_dataset=indicators, fields=fields, xy_tolerance="", z_tolerance="0")
        msg = arcpy.GetMessages()
        msg = ">-> {0}\n".format(msg.replace('\n', '\n>-> '))
        logFile(log_file, msg); del msg


        msg = '>-> Adding field index in the Indicators Table'
        logFile(log_file, msg)

        try:
            arcpy.RemoveIndex_management(indicators, ["IndicatorsTableSpeciesIndex"])
        except:
            pass

        # Add Attribute Index
        arcpy.management.AddIndex(indicators, ['Species', 'CommonName', 'SpeciesCommonName', 'Year'], "IndicatorsTableSpeciesIndex", "NON_UNIQUE", "NON_ASCENDING")

        msg = arcpy.GetMessages()
        msg = ">->->-> {0}".format(msg.replace('\n', '\n>->->-> '))
        logFile(log_file, msg); del msg



        #geographic_regions[region_abb]
        indicators_md = md.Metadata(indicators)
        indicators_md.synchronize('ACCESSED', 1)
        indicators_md.title = "Indicators {0}".format(DateCode)
        #indicators_md.tags = "{0}, {1} to {2}".format(geographic_regions[region_abb], min(years), max(years))
        indicators_md.save()
        del indicators_md

        del indicators, indicators_template, region_snap_raster
        del DisMapSeasonCodeDict, fields

        arcpy.env.workspace = temp_workspace
        del temp_workspace

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = u"Elapsed Time {0} (H:M:S)\n".format(strftime("%H:%M:%S", gmtime(elapse_time)))
        logFile(log_file, msg)
        del msg, start_time, end_time, elapse_time, log_file

        localKeys =  [key for key in locals().keys()]

        if localKeys:
            msg = "Local Keys in createIndicatorsTable(): {0}".format(u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo

def createSpeciesRichnessRasters():
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        # Set a start time so that we can see how log things take
        start_time = time()

        arcpy.env.overwriteOutput = True

        arcpy.env.rasterStatistics = u'STATISTICS 1 1'
        arcpy.env.buildStatsAndRATForTempRaster = True

        # Clean Scatch workspace -- Start
        tmp_workspace = arcpy.env.workspace
        arcpy.env.workspace = ScratchGDB
        # This removes the saved rasters in the ScratchGDB
        for raster in arcpy.ListRasters("*"): arcpy.management.Delete(raster)
        arcpy.management.Compact(ScratchGDB)
        #del raster
        arcpy.env.workspace = ScratchFolder
        # This removes the saved rasters in the ScratchGDB
        for raster in [r for r in arcpy.ListRasters("*")]: arcpy.management.Delete(raster)
        #del raster

        arcpy.env.workspace = tmp_workspace
        del tmp_workspace
        # Clean Scatch workspace -- End

##        # Set the workspace to the ProjectGDB
##        tmp_workspace = arcpy.env.workspace
##        arcpy.env.workspace = ProjectGDB
##
##        # Set the scratch workspace to the ScratchGDB
##        tmp_scratchWorkspace = arcpy.env.scratchWorkspace
##        arcpy.env.scratchWorkspace = ScratchGDB


        for table_name in table_names:
            # Assigning variables from items in the chosen table list
            #region_shape = table_name[0]
            #region_boundary = table_name[1]
            region_abb = table_name[2]
            region = table_name[3]
            csv_file = table_name[4]
            region_georef = table_name[5]
            #region_contours = table_name[6]
            cell_size = table_name[7]

            # Set the output coordinate system to what is available for us.
            region_sr = srs[region_georef]
            arcpy.env.outputCoordinateSystem = region_sr

            #region_shape = os.path.join(ProjectGDB, region_abb+"_Shape")
            region_snap_raster = os.path.join(ProjectGDB, region_abb+"_Snap_Raster")
            region_raster_mask = os.path.join(ProjectGDB, region_abb+"_Raster_Mask")

            arcpy.env.snapRaster = region_snap_raster
            # we need to set the mask and extent of the environment, or the raster and items may not come out correctly.
            arcpy.env.extent = arcpy.Describe(region_snap_raster).extent
            arcpy.env.mask = region_raster_mask

            # These are used later to set the rows and columns for a zero numpy array
            rowCount = int(arcpy.management.GetRasterProperties(region_snap_raster, "ROWCOUNT" ).getOutput(0))
            columnCount = int(arcpy.management.GetRasterProperties(region_snap_raster, "COLUMNCOUNT" ).getOutput(0))

            # For benchmarking.
            log_file = os.path.join(LOG_DIRECTORY, region + ".log")
            # Start with removing the log file if it exists
            #if os.path.isfile(log_file):
            #    os.remove(log_file)

            # Write a message to the log file
            msg = "#-> STARTING {0} ON {1}".format(function, strftime("%a %b %d %I:%M:%S %p", localtime()))
            logFile(log_file, msg)
            del msg

            msg = ">-> Region (abb): {0}\n\t Region:  {1}".format(region_abb, region)
            logFile(log_file, msg)

            region_year_richness_path = os.path.join(ANALYSIS_DIRECTORY, region_abb)

            if ReplaceRegionYearRichness:
                tmp_workspace = arcpy.env.workspace
                arcpy.env.workspace = region_year_richness_path
                rs = arcpy.ListRasters("*Richness*")
                for r in rs: arcpy.management.Delete(r); del r
                del rs
                arcpy.env.workspace = tmp_workspace
                del tmp_workspace

            # Region richness raster
            # Set region_year_richness_path
            region_year_richness_path = os.path.join(ANALYSIS_DIRECTORY, region_abb, "Species Richness")

            if not os.path.isdir(region_year_richness_path):
                os.makedirs(region_year_richness_path)

            if ReplaceRegionYearRichness:
                tmp_workspace = arcpy.env.workspace
                arcpy.env.workspace = region_year_richness_path
                rs = arcpy.ListRasters("*Richness*")
                for r in rs: arcpy.management.Delete(r); del r
                del rs
                arcpy.env.workspace = tmp_workspace
                del tmp_workspace

            # Define region_mosaic
            region_mosaic = os.path.join(ProjectGDB, region_abb)
            # Make region_mosaic_layer
            region_mosaic_layer = arcpy.management.MakeMosaicLayer(region_mosaic, "region_mosaic_layer")

            # Get a unique list of years from the region_mosaic_layer
            years = unique_years(region_mosaic_layer)
            #years = unique_years(region_mosaic)

            if arcpy.Exists("region_mosaic_layer"): arcpy.management.Delete("region_mosaic_layer")
            del region_mosaic_layer

            # Test if we are filtering on years. If so, a new year list is
            # created with the selected years remaining in the list
            if FilterYears:
                # Get a shorter list
                years = [y for y in years if y in selected_years]
            else:
                pass

            for year in years:

                region_year_base_name = "{0}_{1}_".format(region_abb, year)

                region_year_richness = os.path.join(region_year_richness_path, "{0}Species_Richness.tif".format(region_year_base_name))

                if not os.path.isfile(region_year_richness) or ReplaceRegionYearRichness:

                    msg = ">->-> Year: {0}".format(year)
                    logFile(log_file, msg)

                    # Set workspace
                    arcpy.env.workspace = ScratchFolder

                    msg = ">->->-> arcpy.management.ExportMosaicDatasetItems"
                    logFile(log_file, msg)

                    # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
                    # The following inputs are layers or table views: "region_mosaic_layer"

                    arcpy.management.ExportMosaicDatasetItems(#in_mosaic_dataset = "region_mosaic_layer",
                                                              in_mosaic_dataset = region_mosaic,
                                                              out_folder = ScratchFolder,
                                                              out_base_name = region_year_base_name,
                                                              where_clause = "Year = {0} AND Variable NOT IN ('Species Richness', 'Core Species Richness')".format(year),
                                                              format = "TIFF",
                                                              nodata_value = "-3.40282346639e+38", #-3.402823e+38
                                                              clip_type = "NONE",
                                                              template_dataset = "DEFAULT",
                                                              cell_size = "{0} {0}".format(cell_size))

                    msg = arcpy.GetMessages()
                    msg = ">->->-> {0}\n".format(msg.replace('\n', '\n>->->-> '))
                    logFile(log_file, msg)

                    # Get a list of rasters that are exported from the arcpy.management.ExportMosaicDatasetItems tool
                    # These, for some reason, have TIF as an extension
                    rasters = [r for r in arcpy.ListRasters("{0}*.TIF".format(region_year_base_name)) if "Richness" not in r]
                    for raster in rasters: arcpy.management.CalculateStatistics(raster)
                    del raster
                    #print(rasters)

                    #richnessArray = np.zeros((rowCount, columnCount), dtype=int, order='C')
                    #richnessArray = np.zeros((rowCount, columnCount), dtype=float, order='C')
                    #richnessArray = np.zeros((rowCount, columnCount), dtype=np.int32, order='C')
                    richnessArray = np.zeros((rowCount, columnCount), dtype='float32', order='C')

                    msg = ">->->-> Processing rasters"
                    logFile(log_file, msg)
                    # For each raster exported, create the Con mask
                    for raster in rasters:
                        #arcpy.management.CalculateStatistics(raster)
                        msg = ">->->->-> Processing {0} raster".format(raster)
                        logFile(log_file, msg)

                        # Get Raster Maximum to test of zero rasters
                        #rasterMaximum = float(arcpy.management.GetRasterProperties(raster,"MAXIMUM").getOutput(0))

                        # If Raster Maximum greater than zero, then proceed
                        #if rasterMaximum > 0.0:

                        rasterArray = arcpy.RasterToNumPyArray(raster, nodata_to_value=np.nan)
                        #rasterArray = rasterArray.astype('float32')
                        rasterArray[rasterArray < 0.0] = np.nan

    ##                    maximumRasterArray = np.nanmax(rasterArray)
    ##                    minimumRasterArray = np.nanmin(rasterArray)
    ##
    ##                    msg = ">->->->-> Maximum Biomass Array:         {0}".format(maximumRasterArray)
    ##                    print(msg)
    ##                    del msg
    ##
    ##                    msg = ">->->->-> Minimum Biomass Array:         {0}".format(minimumRasterArray)
    ##                    print(msg)
    ##                    del msg

                        rasterArray[rasterArray > 0.0] = 1.0

    ##                    maximumRasterArray = np.nanmax(rasterArray)
    ##                    minimumRasterArray = np.nanmin(rasterArray)
    ##
    ##                    msg = ">->->->-> Maximum Biomass Array:         {0}".format(maximumRasterArray)
    ##                    print(msg)
    ##                    del msg
    ##
    ##                    msg = ">->->->-> Minimum Biomass Array:         {0}".format(minimumRasterArray)
    ##                    print(msg)
    ##                    del msg

                        #add rasterArray to richnessArray
                        richnessArray = np.add(richnessArray, rasterArray)
                        # Can also use: richnessArray + rasterArray
                        del rasterArray
                    # cleanup
                    # del rasterMaximum

                    #richnessArray[richnessArray <= 0] = np.nan

                    msg = ">->->-> Creating Richness Raster"
                    logFile(log_file, msg)

                    # Create Raster from Array
                    snapRaster = arcpy.Raster(region_snap_raster)
                    lowerLeft = arcpy.Point(snapRaster.extent.XMin, snapRaster.extent.YMin)
                    del snapRaster

                    # Cast array as float32
                    richnessArray = richnessArray.astype('float32')

                    # Convert Array to Raster
                    richnessArrayRaster = arcpy.NumPyArrayToRaster(richnessArray, lowerLeft, cell_size, cell_size, -3.40282346639e+38) #-3.40282346639e+38
                    richnessArrayRaster.save(region_year_richness)
                    del richnessArray, richnessArrayRaster, lowerLeft
                    del rasters

                    arcpy.management.CalculateStatistics(region_year_richness)

                    # Add metadata
                    region_year_richness_md = md.Metadata(region_year_richness)
                    region_year_richness_md.synchronize('ACCESSED', 1)
                    region_year_richness_md.title = "{0} {1}".format(region.replace('-',' to '), DateCode)
                    region_year_richness_md.tags = "{0}, {1}, Species Richness".format(geographic_regions[region_abb], year)
                    region_year_richness_md.save()
                    del region_year_richness_md

                    # ###--->>>

                    tmp_workspace = arcpy.env.workspace
                    arcpy.env.workspace = ScratchFolder
                    msg = ">->->-> arcpy.management.Delete in ScratchFolder"
                    logFile(log_file, msg)
                    # This removes the saved rasters in the ScratchFolder
                    #for raster in [r for r in arcpy.ListRasters("*") if "Richness" not in r]: arcpy.management.Delete(raster)
                    for raster in arcpy.ListRasters("*"): arcpy.management.Delete(raster)
                    del raster
                    arcpy.env.workspace = tmp_workspace
                    del tmp_workspace

            # ###--->>>

            # Loading images into the Mosaic.
            msg = '>->->-> Loading the {} Mosaic. This may take a while... Please wait...'.format(region)
            logFile(log_file, msg)

            arcpy.management.AddRastersToMosaicDataset(in_mosaic_dataset = region_mosaic,
                                                       raster_type = "Raster Dataset",
                                                       input_path = region_year_richness_path,
                                                       update_cellsize_ranges = "UPDATE_CELL_SIZES",
                                                       #update_cellsize_ranges = "NO_CELL_SIZES",
                                                       update_boundary = "UPDATE_BOUNDARY",
                                                       #update_boundary = "NO_BOUNDARY",
                                                       update_overviews = "NO_OVERVIEWS",
                                                       maximum_pyramid_levels = "",
                                                       maximum_cell_size = "0",
                                                       minimum_dimension = "1500",
                                                       spatial_reference = region_sr,
                                                       #filter = "*Richness.tif",
                                                       filter = "*Richness.tif",
                                                       sub_folder = "NO_SUBFOLDERS",
                                                       #duplicate_items_action = "OVERWRITE_DUPLICATES",
                                                       duplicate_items_action = "EXCLUDE_DUPLICATES",
                                                       build_pyramids = "NO_PYRAMIDS",
                                                       calculate_statistics = "CALCULATE_STATISTICS",
                                                       #calculate_statistics = "NO_STATISTICS",
                                                       build_thumbnails = "BUILD_THUMBNAILS",
                                                       #build_thumbnails = "NO_THUMBNAILS",
                                                       operation_description = "",
                                                       #force_spatial_reference = "NO_FORCE_SPATIAL_REFERENCE",
                                                       force_spatial_reference = "FORCE_SPATIAL_REFERENCE",
                                                       estimate_statistics = "ESTIMATE_STATISTICS",
                                                       #estimate_statistics = "NO_STATISTICS",
                                                       )

            del region_year_richness, region_year_richness_path

            msg = ">->->-> Calculating new values for the new fields in the regional Mosaic Dataset"
            logFile(log_file, msg)

            msg = ">->->-> arcpy.management.MakeTableView Variable_View"
            logFile(log_file, msg)
            # For Multidimensional data (https://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/wkfl-create-a-multidimensional-mosaic-dataset-from-a-set-of-time-series-images.htm)
            # Make table view for calculations
            #arcpy.management.MakeTableView(in_table=region_richness_mosaic, out_view="Variable_View", where_clause="Variable IS NULL", workspace="", )
            arcpy.management.MakeTableView(in_table=region_mosaic, out_view="Variable_View", where_clause="Variable IS NULL OR Variable = 'Species Richness'", workspace="", )

            msg = ">->->-> arcpy.management.CalculateField Region"
            logFile(log_file, msg)
            # Process: Calculate Region Field
            arcpy.management.CalculateField("Variable_View", "OARegion", "'{0}'".format(region.replace("'","''")), "PYTHON", "")

            msg = ">->->-> arcpy.management.CalculateField CoreSpecies"
            logFile(log_file, msg)
            # Process: Calculate Region Field
            arcpy.management.CalculateField("Variable_View", "CoreSpecies", "'No'", "PYTHON", "")

            msg = ">->->-> arcpy.management.CalculateField Year"
            logFile(log_file, msg)
            # Process: Calculate Year Field
            arcpy.management.CalculateField("Variable_View", "Year", expression="MakeInt( !Name!)", expression_type="PYTHON", code_block="def MakeInt(name):   return int(name[-21:-17]) if 'Core' not in name else int(name[-26:-22])")

            msg = ">->->-> arcpy.management.CalculateField Variable"
            logFile(log_file, msg)
            # Process: Calculate Species Field
            arcpy.management.CalculateField("Variable_View", "Variable", "'Species Richness'", "PYTHON", "")

            codeBlock = """def getDate(region, year):
                              from datetime import datetime
                              import pytz
                              regionDateDict = {# Region : Month, Day, Time Zone
                                                'Aleutian Islands'   : [1, 1, 0, 0, 0, 'US/Alaska'],
                                                'Eastern Bering Sea' : [1, 1, 0, 0, 0, 'US/Alaska'],
                                                'Gulf of Alaska' : [1, 1, 0, 0, 0, 'US/Alaska'],
                                                'Gulf of Mexico' : [1, 1, 0, 0, 0, 'US/Central'],
                                                'Hawaii Islands' : [1, 1, 0, 0, 0, 'US/Hawaii'],
                                                "Hawai'i Islands" : [1, 1, 0, 0, 0, 'US/Hawaii'],
                                                'Hawaii' : [1, 1, 0, 0, 0, 'US/Hawaii'],
                                                'Northeast US Fall' : [1, 1, 0, 0, 0, 'US/Eastern'],
                                                'Northeast US Spring' : [1, 1, 0, 0, 0, 'US/Eastern'],
                                                'Southeast US Spring' : [1, 1, 0, 0, 0, 'US/Eastern'],
                                                'Southeast US Summer' : [1, 1, 0, 0, 0, 'US/Eastern'],
                                                'Southeast US Fall' : [1, 1, 0, 0, 0, 'US/Eastern'],
                                                'West Coast Annual' : [1, 1, 0, 0, 0, 'US/Pacific'],
                                                'West Coast Triennial' : [1, 1, 0, 0, 0, 'US/Pacific'],
                                                'West Coast Annual 2003-Present' : [1, 1, 0, 0, 0, 'US/Pacific'],
                                                'West Coast Triennial 1977-2004' : [1, 1, 0, 0, 0, 'US/Pacific'],
                                                'West Coast Annual (2003-Present)' : [1, 1, 0, 0, 0, 'US/Pacific'],
                                                'West Coast Triennial (1977-2004)' : [1, 1, 0, 0, 0, 'US/Pacific'],}
                              month, day, hour, min, sec, timeZone = regionDateDict[region]
                              fmt = "%m/%d/%Y %H:%M:%S"
                              local = pytz.timezone(timeZone)
                              naive = datetime.strptime("{0}/{1}/{2} {3}:{4}:{5}".format(month, day, year, hour, min, sec), fmt)
                              #local_dt = local.localize(naive, is_dst=True)
                              local_dt = local.localize(naive, is_dst=False)
                              utc_dt = local_dt.astimezone(pytz.utc)
                              #return utc_dt.strftime(fmt)
                              return utc_dt"""

            msg = ">->->-> arcpy.management.CalculateField StdTime"
            logFile(log_file, msg)

            arcpy.management.CalculateField("Variable_View", "StdTime", expression="getDate( !OARegion!, !Year! )", expression_type="PYTHON", code_block=codeBlock)
            del codeBlock

            msg = ">->->-> arcpy.management.CalculateField Dimensions"
            logFile(log_file, msg); del msg

            arcpy.management.CalculateField(in_table="Variable_View", field="Dimensions", expression="'StdTime'", expression_type="PYTHON", code_block="")

            arcpy.management.Delete("Variable_View")

            # Cleanup
            del region_mosaic, region_abb
            del region_georef, year, years
            del table_name, csv_file, region_year_base_name
            del region, region_sr
            del rowCount, columnCount
            del region_snap_raster, region_raster_mask, cell_size

        # Cleanup
        del log_file

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = u"#-> Elapsed Time for {0} {1} (H:M:S)\n".format(function, strftime("%H:%M:%S", gmtime(elapse_time)))
        print(msg)
        del msg, start_time, end_time, elapse_time

        localKeys =  [key for key in locals().keys() if "function" not in key]

        if localKeys:
            msg = "Local Keys in {0}(): {1}".format(function, u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys, function

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo

def createSnapRasterBathymetryLatitudeLongitude():
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        # Set the workspace to the ProjectGDB
        tmp_workspace = arcpy.env.workspace
        arcpy.env.workspace = ProjectGDB

        # Set the scratch workspace to the ScratchGDB
        tmp_scratchWorkspace = arcpy.env.scratchWorkspace
        arcpy.env.scratchWorkspace = ScratchGDB

        # Set a start time so that we can see how log things take
        start_time = time()

##        arcpy.ClearEnvironment("XYTolerance")
##        arcpy.ClearEnvironment("cellAlignment")
##        arcpy.ClearEnvironment("cellSize")
##        arcpy.ClearEnvironment("cellSizeProjectionMethod")
##        arcpy.ClearEnvironment("extent")
##        arcpy.ClearEnvironment("mask")
##        arcpy.ClearEnvironment("outputCoordinateSystem")
##        arcpy.ClearEnvironment("resamplingMethod")
##        arcpy.ClearEnvironment("snapRaster")
##        environments = arcpy.ListEnvironments()
##        # Sort the environment names
##        environments.sort()
##        for environment in environments:
##            # Format and print each environment and its current setting.
##            # (The environments are accessed by key from arcpy.env.)
##            print("{0:<30}: {1}".format(environment, arcpy.env[environment]))
##            del environment
##        del environments

# ###--->>> For loop through regions
        # Start looping over the table_name array as we go region by region.
        for table_name in table_names:
# ###--->>> Variables from list of lists
            # Assigning variables from items in the chosen table list
            region_shape = table_name[0]
            region_boundary = table_name[1]
            region_abb = table_name[2]
            region = table_name[3]
            # csv_file = table_name[4]
            region_georef = table_name[5]
            # region_contours = table_name[6]
            cell_size = table_name[7]
            del table_name
# ###--->>> Variables from list of lists

            # Set the output coordinate system to what is available for us.
            region_sr = srs[region_georef]


##            environments = arcpy.ListEnvironments()
##            # Sort the environment names
##            environments.sort()
##            for environment in environments:
##                # Format and print each environment and its current setting.
##                # (The environments are accessed by key from arcpy.env.)
##                print("{0:<30}: {1}".format(environment, arcpy.env[environment]))
##                del environment
##            del environments
            arcpy.ClearEnvironment("XYTolerance")
            arcpy.ClearEnvironment("cellAlignment")
            arcpy.ClearEnvironment("cellSize")
            arcpy.ClearEnvironment("cellSizeProjectionMethod")
            arcpy.ClearEnvironment("extent")
            arcpy.ClearEnvironment("mask")
            arcpy.ClearEnvironment("outputCoordinateSystem")
            arcpy.ClearEnvironment("resamplingMethod")
            arcpy.ClearEnvironment("snapRaster")

# ###--->>> ArcPy Envs
            arcpy.env.outputCoordinateSystem = region_sr
            #del region_sr
            arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"
            # Set the XYTolerance to 0.02 Meters
            arcpy.env.XYTolerance = "0.02 Meters"

            # Set the cell alignment environment using a keyword.
            arcpy.env.cellAlignment = "ALIGN_WITH_PROCESSING_EXTENT"
            arcpy.env.cellSize = cell_size

            # For benchmarking.
            log_file = os.path.join(LOG_DIRECTORY, region + ".log")
            # Start with removing the log file if it exists
            #if os.path.isfile(log_file):
            #    os.remove(log_file)
# ###--->>>
            # Write a message to the log file
            msg = "STARTING REGION {} ON {}".format(region, strftime("%a %b %d %I:%M:%S %p", localtime()))
            logFile(log_file, msg)

            if not os.path.exists( MAP_DIRECTORY+"\\"+region_abb ): os.makedirs( MAP_DIRECTORY+"\\"+region_abb )

            # The shapefile used to create the extent and mask for the environment variable
            my_shape = arcpy.management.MakeFeatureLayer(MAP_DIRECTORY+"\\"+region_abb+"\\" + region_shape + ".shp", "my_shape")
            #extent = arcpy.Describe(my_shape).extent
            #print("XMin: {0}, Old_X_Max: {1}, YMin: {2}, YMax: {3}\n".format(extent.XMin, extent.XMax, extent.YMin, extent.YMax))
            #del extent

# ###--->>>
            # Additional variables
            region_shape = os.path.join(ProjectGDB, region_abb+"_Shape")
            region_shape_line = os.path.join(ProjectGDB, region_abb+"_Shape_Line")
            #region_envelope = os.path.join(ProjectGDB, region_abb+"_Envelope")
            region_fish_net = os.path.join(ProjectGDB, region_abb+"_Fish_Net")
            #region_fish_net_bathy = os.path.join(ProjectGDB, region_abb+"_Fish_Net_Bathy")
            region_fish_net_label = os.path.join(ProjectGDB, region_abb+"_Fish_Net_Label")
            region_snap_raster = os.path.join(ProjectGDB, region_abb+"_Snap_Raster")
            region_raster_mask = os.path.join(ProjectGDB, region_abb+"_Raster_Mask")
            region_bathymetry = os.path.join(ProjectGDB, region_abb+"_Bathymetry")
            region_bathymetry_sample = os.path.join(ProjectGDB, region_abb+"_Bathymetry_Sample")
            region_lat_long = os.path.join(ProjectGDB, region_abb+"_Lat_Long")
            region_latitude = os.path.join(ProjectGDB, region_abb+"_Latitude")
            region_longitude = os.path.join(ProjectGDB, region_abb+"_Longitude")

# ###--->>> Cleanup Datasets to start fresh
            arcpy.management.Delete(region_shape)
            arcpy.management.Delete(region_fish_net)
            #arcpy.management.Delete(region_fish_net_bathy)
            arcpy.management.Delete(region_fish_net_label)
            arcpy.management.Delete(region_snap_raster)
            arcpy.management.Delete(region_raster_mask)
            arcpy.management.Delete(region_bathymetry)
            arcpy.management.Delete(region_bathymetry_sample)
            arcpy.management.Delete(region_lat_long)
            arcpy.management.Delete(region_latitude)
            arcpy.management.Delete(region_longitude)

# ###--->>> Source Bathymetry
            #etopo1 = os.path.join(BASE_DIRECTORY, r"ETOPO1.gdb\etopo1_bed_g_f4")
            #etopo1 = os.path.join(BASE_DIRECTORY, r"ETOPO1.gdb\etopo1_bed_g_f4_bathymetry")
            bathymetry = os.path.join(BASE_DIRECTORY, r"{0}\{1}_Bathymetry".format(BathymetryGDB, region_abb))

            msg = "> arcpy.management.Project"
            logFile(log_file, msg)
            # Project Data
            #arcpy.management.Project(my_shape, region_shape, region_sr, "WGS_1984_(ITRF08)_To_NAD_1983_2011", preserve_shape = "PRESERVE_SHAPE")
            arcpy.management.Project(my_shape, region_shape, region_sr, "", preserve_shape = "PRESERVE_SHAPE")

            fields = [f.name for f in arcpy.ListFields(region_shape)]
            if "Id" not in fields:
                msg = "> arcpy.management.AddField"
                logFile(log_file, msg)
                arcpy.management.AddField(region_shape, "Id", "LONG","","","","Id","NULLABLE","NON_REQUIRED")

            if "OARegion" not in fields:
                msg = '> Adding the "OARegion" field to the {} Shape'.format(region)
                logFile(log_file, msg)

                # Process: Add Region Field
                arcpy.management.AddField(region_shape, "OARegion", "TEXT", "", "", "50", "OA Region", "NULLABLE", "NON_REQUIRED", "")

            del fields

            msg = "> arcpy.management.CalculateField"
            logFile(log_file, msg)
            # Set ID field value
            arcpy.management.CalculateField(region_shape, "Id", 1, "PYTHON")

            msg = "> arcpy.management.CalculateField"
            logFile(log_file, msg)
            # Process: Calculate Region Field
            arcpy.management.CalculateField(region_shape, "OARegion", "'{0}'".format(region), "PYTHON", "")

            # Get Extent
            extent = arcpy.Describe(region_shape).extent
            Old_X_Min, Old_Y_Min, Old_X_Max, Old_Y_Max = extent.XMin, extent.YMin, extent.XMax, extent.YMax
            print("Old_X_Min: {0}, Old_Y_Min: {1}, Old_X_Max: {2}, Old_Y_Max: {3}\n".format(Old_X_Min, Old_Y_Min, Old_X_Max, Old_Y_Max))

            arcpy.management.Delete("my_shape")
            del my_shape
            del region_sr

            sign = lambda x : copysign(1, x)

            New_X_Min = (cell_size * round(abs(Old_X_Min)/cell_size) - cell_size * sign(Old_X_Min)) * sign(Old_X_Min)
            New_Y_Min = (cell_size * round(abs(Old_Y_Min)/cell_size) - cell_size * sign(Old_Y_Min)) * sign(Old_Y_Min)
            New_X_Max = (cell_size * round(abs(Old_X_Max)/cell_size) + cell_size * sign(Old_X_Max)) * sign(Old_X_Max)
            New_Y_Max = (cell_size * round(abs(Old_Y_Max)/cell_size) + cell_size * sign(Old_Y_Max)) * sign(Old_Y_Max)

            print("New_X_Min: {}, New_Y_Min: {}, New_X_Max: {}, New_Y_Max: {}".format(New_X_Min, New_Y_Min, New_X_Max, New_Y_Max))

            print("New_X_Min < Old_X_Min: {0}".format(New_X_Min < Old_X_Min))
            print("New_Y_Min < Old_Y_Min: {0}".format(New_Y_Min < Old_Y_Min))
            print("New_X_Max > Old_X_Max: {0}".format(New_X_Max > Old_X_Max))
            print("New_Y_Max > Old_Y_Max: {0}".format(New_Y_Max > Old_Y_Max))

            del extent, sign
            del Old_X_Min, Old_Y_Min, Old_X_Max, Old_Y_Max

            #arcpy.env.extent = arcpy.Extent(New_X_Min, New_Y_Min, New_X_Max, New_Y_Max)
            region_extent = "{0} {1} {2} {3}".format(New_X_Min, New_Y_Min, New_X_Max, New_Y_Max)
            arcpy.env.extent = region_extent

            # Create Region Snap Raster from new extent
            feature_info = [[[New_X_Min, New_Y_Min], [New_X_Min, New_Y_Max], [New_X_Max, New_Y_Max], [New_X_Max, New_Y_Min],]]

            snap_feature_class = os.path.join(ProjectGDB, "snap_feature_class")

            # A list that will hold each of the Polygon objects
            features = []

            # Create Polygon objects based an the array of points
            for feature in feature_info:
                array = arcpy.Array([arcpy.Point(*coords) for coords in feature])

                # Add the first coordinate pair to the end to close polygon
                array.append(array[0])
                features.append(arcpy.Polygon(array))
            del feature, feature_info, array

            # Persist a copy of the geometry objects using CopyFeatures
            arcpy.management.CopyFeatures(features, snap_feature_class)
            arcpy.management.Delete(features); del features

            arcpy.conversion.PolygonToRaster(in_features=snap_feature_class, value_field="OBJECTID", out_rasterdataset=region_snap_raster, cell_assignment="CELL_CENTER", priority_field="NONE", cellsize=cell_size)
            arcpy.management.Delete(snap_feature_class); del snap_feature_class
            arcpy.env.snapRaster = region_snap_raster

            # CreateFishnet(out_feature_class, origin_coord, y_axis_coord, cell_width, cell_height, number_rows, number_columns, {corner_coord}, {labels}, {template}, {geometry_type})
            #outFeatureClass = region_fish_net
            # Set the origin of the fishnet
            originCoordinate = '{0} {1}'.format(New_X_Min, New_Y_Min)
            # Set the orientation
            yAxisCoordinate = '{0} {1}'.format(New_X_Min, New_Y_Min+cell_size)
            # Enter 0 for width and height - these values will be calcualted by the tool
            cellSizeWidth = '{0}'.format(cell_size)
            cellSizeHeight = '{0}'.format(cell_size)
            # Number of rows and columns together with origin and opposite corner
            # determine the size of each cell
            numRows =  ''
            numColumns = ''
            oppositeCoorner = '{0} {1}'.format(New_X_Max, New_Y_Max)
            # Create a point label feature class
            labels = 'LABELS'
            # Extent is set by origin and opposite corner - no need to use a template fc
            templateExtent = "{0} {1} {2} {3}".format(New_X_Min, New_Y_Min, New_X_Max, New_Y_Max)
            # Each output cell will be a polygon
            geometryType = 'POLYGON'
            #Coordinate_System = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
            msg = "> arcpy.management.CreateFishnet with {0} by {1} cells".format(cellSizeWidth, cellSizeHeight)
            logFile(log_file, msg)
            arcpy.management.CreateFishnet(region_fish_net, originCoordinate, yAxisCoordinate, cellSizeWidth, cellSizeHeight, numRows, numColumns, oppositeCoorner, labels, templateExtent, geometryType)

            # Get Extent
            extent = arcpy.Describe(region_fish_net).extent
            New_X_Min, New_Y_Min, New_X_Max, New_Y_Max = extent.XMin, extent.YMin, extent.XMax, extent.YMax
            print("New_X_Min: {0}, New_Y_Min: {1}, New_X_Max: {2}, New_Y_Max: {3}\n".format(New_X_Min, New_Y_Min, New_X_Max, New_Y_Max))
            del extent, New_X_Min, New_Y_Min, New_X_Max, New_Y_Max

            #del outFeatureClass
            del originCoordinate, yAxisCoordinate
            del cellSizeWidth, cellSizeHeight, numRows, numColumns
            del oppositeCoorner, labels, templateExtent, geometryType
            #del Coordinate_System

            msg = "> arcpy.management.AddField"
            logFile(log_file, msg)
            # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
            # The following inputs are layers or table views: "NEUS_F_Fish_Net"
            arcpy.management.AddField(in_table=region_fish_net, field_name="Value", field_type="SHORT", field_precision="", field_scale="", field_length="", field_alias="Value", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")

            msg = "> arcpy.management.CalculateField"
            logFile(log_file, msg)
            # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
            # The following inputs are layers or table views: "NEUS_F_Fish_Net"
            arcpy.management.CalculateField(in_table=region_fish_net, field="Value", expression="1", expression_type="PYTHON", code_block="")

            #print(region_extent)
            #arcpy.env.extent = region_extent
            #print(cell_size)
            #msg = "> PolygonToRaster_conversion to create Snap Raster"
            #logFile(log_file, msg)
            #arcpy.env.outputCoordinateSystem = arcpy.Describe(region_fish_net).spatialReference
            # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
            # The following inputs are layers or table views: "NEUS_F_Fish_Net"
            #arcpy.PolygonToRaster_conversion(in_features=region_fish_net, value_field="Value", out_rasterdataset=region_snap_raster, cell_assignment="CELL_CENTER", priority_field="Value", cellsize = cell_size)

            # Get Extent
            extent = arcpy.Describe(region_fish_net).extent
            New_X_Min, New_Y_Min, New_X_Max, New_Y_Max = extent.XMin, extent.YMin, extent.XMax, extent.YMax
            print("New_X_Min: {0}, New_Y_Min: {1}, New_X_Max: {2}, New_Y_Max: {3}\n".format(New_X_Min, New_Y_Min, New_X_Max, New_Y_Max))
            del extent, New_X_Min, New_Y_Min, New_X_Max, New_Y_Max

            arcpy.env.extent = arcpy.Describe(region_snap_raster).extent
            arcpy.env.snapRaster = region_snap_raster

# ###--->>> Select by location and trim
            msg = "> arcpy.management.MakeFeatureLayer"
            logFile(log_file, msg)
            region_fish_net_layer = arcpy.management.MakeFeatureLayer(region_fish_net, "{0}_Fish_Net_Layer".format(region_abb))

            msg = "> arcpy.management.SelectLayerByLocation"
            logFile(log_file, msg)
            arcpy.management.SelectLayerByLocation(region_fish_net_layer, "WITHIN_A_DISTANCE", region_shape, 25000, "NEW_SELECTION", "INVERT")

            msg = "> arcpy.management.DeleteFeatures"
            logFile(log_file, msg)
            arcpy.management.DeleteFeatures(region_fish_net_layer)

            #msg = "> arcpy.management.SelectLayerByAttribute"
            #logFile(log_file, msg)
            #arcpy.management.SelectLayerByAttribute(region_fish_net_layer, "CLEAR_SELECTION")

            msg = "> arcpy.management.MakeFeatureLayer"
            logFile(log_file, msg)
            region_fish_net_label_layer = arcpy.management.MakeFeatureLayer(region_fish_net_label, "{0}_Fish_Net_Label_Layer".format(region_abb))

            msg = "> arcpy.management.SelectLayerByLocation"
            logFile(log_file, msg)
            arcpy.management.SelectLayerByLocation(region_fish_net_label_layer, "INTERSECT", region_fish_net_layer, 0, "NEW_SELECTION", "INVERT")

            msg = "> arcpy.management.DeleteFeatures"
            logFile(log_file, msg)
            arcpy.management.DeleteFeatures(region_fish_net_label_layer)

            msg = "> arcpy.management.Delete"
            logFile(log_file, msg)
            arcpy.management.Delete("{0}_Fish_Net_Layer".format(region_abb))
            arcpy.management.Delete("{0}_Fish_Net_Label_Layer".format(region_abb))
            del region_fish_net_layer, region_fish_net_label_layer

# ###--->>> Select by location and trim

            msg = "> FeatureToRaster_conversion to create Raster Mask"
            logFile(log_file, msg)
            # Change mask to the region shape to create the raster mask
            #region_shape_buffer = os.path.join(ProjectGDB, '{0}_Buffers'.format(region_abb))
            #arcpy.analysis.Buffer(region_shape, region_shape_buffer, cell_size)
            #arcpy.env.mask = region_shape_buffer
            arcpy.env.mask = region_shape
            arcpy.conversion.FeatureToRaster(region_shape, "Id", region_raster_mask, cell_size)
            #arcpy.conversion.FeatureToRaster(region_shape_buffer,"Id", region_raster_mask, cell_size)
            #arcpy.management.Delete(region_shape_buffer)
            #del region_shape_buffer

            # Get Extent
            extent = arcpy.Describe(region_fish_net).extent
            New_X_Min, New_Y_Min, New_X_Max, New_Y_Max = extent.XMin, extent.YMin, extent.XMax, extent.YMax
            print("New_X_Min: {0}, New_Y_Min: {1}, New_X_Max: {2}, New_Y_Max: {3}\n".format(New_X_Min, New_Y_Min, New_X_Max, New_Y_Max))
            del extent, New_X_Min, New_Y_Min, New_X_Max, New_Y_Max
            #del region_raster_mask

            msg = "> arcpy.management.DeleteField Value"
            logFile(log_file, msg)
            # Execute DeleteField
            arcpy.management.DeleteField(region_fish_net, ['Value'])

            msg = "> arcpy.management.Rename"
            logFile(log_file, msg)
            #
            arcpy.management.Rename(region_fish_net_label, region_lat_long)

            Coordinate_System = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
            msg = "> arcpy.management.AddGeometryAttributes"
            logFile(log_file, msg)
            # Process: Add Geometry Attributes
            arcpy.management.AddGeometryAttributes(region_lat_long, "POINT_X_Y_Z_M", "", "", Coordinate_System)
            del Coordinate_System

            msg = "> arcpy.management.AlterField POINT_X to Longitude"
            logFile(log_file, msg)
            #
            arcpy.management.AlterField(region_lat_long, "POINT_X", "Longitude", "Longitude")

            msg = "> arcpy.management.AlterField POINT_Y to Latitude"
            logFile(log_file, msg)
            #
            arcpy.management.AlterField(region_lat_long, "POINT_Y", "Latitude", "Latitude")

            msg = "> PointToRaster_conversion"
            logFile(log_file, msg)
            # Process: Point to Raster Longitude
            arcpy.conversion.PointToRaster(region_lat_long, "Longitude", region_longitude, "MOST_FREQUENT", "NONE", cell_size)

            #getRowColumnCount(region_longitude)

            msg = "> PointToRaster_conversion"
            logFile(log_file, msg)
            # Process: Point to Raster Latitude
            arcpy.conversion.PointToRaster(region_lat_long, "Latitude", region_latitude, "MOST_FREQUENT", "NONE", cell_size)

            # Get Extent
            extent = arcpy.Describe(region_fish_net).extent
            New_X_Min, New_Y_Min, New_X_Max, New_Y_Max = extent.XMin, extent.YMin, extent.XMax, extent.YMax
            print("New_X_Min: {0}, New_Y_Min: {1}, New_X_Max: {2}, New_Y_Max: {3}\n".format(New_X_Min, New_Y_Min, New_X_Max, New_Y_Max))
            del extent, New_X_Min, New_Y_Min, New_X_Max, New_Y_Max

            msg = "> arcpy.management.AddField GRID_ID"
            logFile(log_file, msg)
            # Add Field to Feature class
            arcpy.management.AddField(in_table=region_lat_long, field_name="GRID_ID", field_type="LONG", field_precision="", field_scale="", field_length="", field_alias="GRID ID", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")

            msg = "> arcpy.management.CalculateField GRID_ID"
            logFile(log_file, msg)
            # arcpy.management.CalculateField
            arcpy.management.CalculateField(in_table=region_lat_long, field="GRID_ID", expression='!OID!', expression_type="PYTHON", code_block="")

            msg = "> arcpy.management.AddIndex GRID_ID"
            logFile(log_file, msg)
            # Add Attribute Index
            arcpy.management.AddIndex(region_lat_long, ['GRID_ID',], "{0}_Lat_Lon_GRID_ID_Index".format(region_abb), "UNIQUE", "ASCENDING")

            msg = "> arcpy.management.AddField GRID_ID"
            logFile(log_file, msg)
            # Add Field to Feature class
            arcpy.management.AddField(in_table=region_fish_net, field_name="GRID_ID", field_type="LONG", field_precision="", field_scale="", field_length="", field_alias="GRID ID", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")

            msg = "> arcpy.management.CalculateField GRID_ID"
            logFile(log_file, msg)
            # arcpy.management.CalculateField
            arcpy.management.CalculateField(in_table=region_fish_net, field="GRID_ID", expression='!OID!', expression_type="PYTHON", code_block="")

            msg = "> arcpy.management.AddIndex GRID_ID"
            logFile(log_file, msg)
            # Add Attribute Index
            arcpy.management.AddIndex(region_lat_long, ['GRID_ID',], "{0}_Fishnet_GRID_ID_Index".format(region_abb), "UNIQUE", "ASCENDING")

            arcpy.env.mask = region_snap_raster
            arcpy.env.extent = arcpy.Describe(region_snap_raster).extent
            arcpy.env.snapRaster = region_snap_raster
            tmp_cell_size = arcpy.env.cellSize
            arcpy.env.cellSize = "MINOF"

            msg = "> arcpy.sa.Sample region_bathymetry"
            logFile(log_file, msg)
            # Sample_sa region_bathymetry
            #arcpy.sa.Sample(etopo1, region_lat_long, region_bathymetry_sample, "NEAREST", "GRID_ID", "CURRENT_SLICE", None, '', None, None, "ROW_WISE", "TABLE")
            arcpy.sa.Sample(bathymetry, region_lat_long, region_bathymetry_sample, "NEAREST", "GRID_ID", "CURRENT_SLICE", None, '', None, None, "ROW_WISE", "TABLE")

            arcpy.env.cellSize = tmp_cell_size
            del tmp_cell_size

            bathymetry_field = [f.name for f in arcpy.ListFields(region_bathymetry_sample) if "bathymetry" in f.name.lower()][0]
            #print(bathymetry_field)

            msg = "> arcpy.management.AddIndex GRID_ID"
            logFile(log_file, msg)
            # Add Attribute Index
            arcpy.management.AddIndex(region_bathymetry_sample, ["{0}_Lat_Long".format(region_abb),], "{0}_Lat_Lon_Batymetry_Index".format(region_abb), "UNIQUE", "ASCENDING")

            msg = '> arcpy.management.JoinField region_lat_long'
            logFile(log_file, msg)
            arcpy.management.JoinField(region_lat_long, "GRID_ID", region_bathymetry_sample, "{0}_Lat_Long".format(region_abb), bathymetry_field)

            msg = "> arcpy.management.AlterField region_lat_long"
            logFile(log_file, msg)
            #arcpy.management.AlterField(region_lat_long, bathymetry_field, "Etopo1_Depth", "ETOPO1 Depth")
            arcpy.management.AlterField(in_table=region_lat_long, field=bathymetry_field, new_field_name="Bathymetry", new_field_alias="Bathymetry")

            msg = '> arcpy.management.JoinField region_fish_net'
            logFile(log_file, msg)
            arcpy.management.JoinField(region_fish_net, "GRID_ID", region_bathymetry_sample, "{0}_Lat_Long".format(region_abb), bathymetry_field)

            msg = "> arcpy.management.AlterField region_fish_net"
            logFile(log_file, msg)
            arcpy.management.AlterField(region_fish_net, bathymetry_field, "Bathymetry", "Bathymetry")

            del bathymetry_field

            msg = "> arcpy.management.Delete region_bathymetry_sample"
            logFile(log_file, msg)
            # Cleanup
            arcpy.management.Delete(in_data=region_bathymetry_sample, data_type="")

            tmp_cell_size = arcpy.env.cellSize
            arcpy.env.cellSize = "MINOF"

            msg = "> ZonalStatisticsAsTable"
            logFile(log_file, msg)
            arcpy.sa.ZonalStatisticsAsTable(region_fish_net, "GRID_ID", bathymetry, region_fish_net+"_Zonal_Stats", "DATA", "ALL")
            #arcpy.env.cellSize = tmp_cell_size; del tmp_cell_size
            #arcpy.env.resamplingMethod = tmp_resamplingMethod; del tmp_resamplingMethod

            arcpy.env.cellSize = tmp_cell_size; del tmp_cell_size

            msg = "> arcpy.management.JoinField"
            logFile(log_file, msg)
            arcpy.management.JoinField(in_data=region_fish_net, in_field="GRID_ID", join_table=region_fish_net+"_Zonal_Stats", join_field="GRID_ID", fields="COUNT;AREA;MIN;MAX;RANGE;MEAN;STD;SUM;VARIETY;MAJORITY;MINORITY;MEDIAN")

            msg = "> arcpy.management.Delete"
            logFile(log_file, msg)
            # Cleanup
            arcpy.management.Delete(in_data=region_fish_net+"_Zonal_Stats", data_type="")

            msg = "> FeatureToRaster_conversion to create Bathymetry Temp"
            logFile(log_file, msg); del msg
            # Change mask to the region shape to create the raster mask
            arcpy.env.mask = region_shape
            #arcpy.env.mask = region_shape_buffer
            arcpy.conversion.FeatureToRaster(region_fish_net, "MEDIAN", region_bathymetry+"_tmp", cell_size)
            #arcpy.conversion.FeatureToRaster(region_fish_net, "MEAN", region_bathymetry+"_tmp", cell_size)

            msg = "> FeatureToRaster_conversion to create Bathymetry"
            logFile(log_file, msg); del msg
            region_bathymetry_tmp = arcpy.sa.Times(region_bathymetry+"_tmp", 1.0)
            region_bathymetry_tmp.save(region_bathymetry)
            arcpy.management.Delete(region_bathymetry+"_tmp")
            del region_bathymetry_tmp

            addMetadata(region_bathymetry)
            addMetadata(region_fish_net)
            addMetadata(region_lat_long)
            addMetadata(region_latitude)
            addMetadata(region_longitude)
            addMetadata(region_raster_mask)
            addMetadata(region_shape)
            addMetadata(region_shape_line)
            addMetadata(region_snap_raster)

            del region_shape, region_shape_line, region_boundary, region_abb, region_georef
            del region_snap_raster, region_bathymetry, region_bathymetry_sample
            del region_lat_long, region_latitude, region_longitude, bathymetry
            del region_fish_net, region_fish_net_label, region_extent, region_raster_mask

            #del region_fish_net_bathy

            #environments = arcpy.ListEnvironments()
            # Sort the environment names
            #environments.sort()
            #for environment in environments:
            #    # Format and print each environment and its current setting.
            #    # (The environments are accessed by key from arcpy.env.)
            #    print("{0:<30}: {1}".format(environment, arcpy.env[environment]))
            #del environment, environments

            arcpy.ResetEnvironments()
            #arcpy.ClearEnvironment("XYTolerance")
            #arcpy.ClearEnvironment("cellAlignment")
            #arcpy.ClearEnvironment("cellSize")
            #arcpy.ClearEnvironment("cellSizeProjectionMethod")
            #arcpy.ClearEnvironment("extent")
            #arcpy.ClearEnvironment("mask")
            #arcpy.ClearEnvironment("outputCoordinateSystem")
            #arcpy.ClearEnvironment("resamplingMethod")
            #arcpy.ClearEnvironment("snapRaster")

            #Final benchmark for the region.
            msg = "ENDING REGION {} COMPLETED ON {}".format(region, strftime("%a %b %d %I:%M:%S %p", localtime()))
            logFile(log_file, msg)
            del msg

            del region

##            environments = arcpy.ListEnvironments()
##            # Sort the environment names
##            environments.sort()
##            for environment in environments:
##                # Format and print each environment and its current setting.
##                # (The environments are accessed by key from arcpy.env.)
##                print("{0:<30}: {1}".format(environment, arcpy.env[environment]))
##            del environment, environments

        #del dismap_regions
        del cell_size

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = u"Elapsed Time {0} (H:M:S)\n".format(strftime("%H:%M:%S", gmtime(elapse_time)))
        logFile(log_file, msg)
        del msg, start_time, end_time, elapse_time, log_file

        # Set the workspace to the tmp_workspace
        arcpy.env.workspace = tmp_workspace
        # Set the scratch workspace to the tmp_scratchWorkspace
        arcpy.env.scratchWorkspace = tmp_scratchWorkspace
        del tmp_workspace, tmp_scratchWorkspace

        localKeys =  [key for key in locals().keys() if "function" not in key]

        if localKeys:
            msg = "Local Keys in {0}(): {1}".format(function, u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys, function

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo





def createTemplateTables():
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        #arcpy.AddMessage(function)

        # If the ProjectGDB is missing, create the folder
        if not arcpy.Exists(ProjectGDB):
            print("The ProjectGDB is the output location for data")
            print("\t missing and will be created")
            arcpy.management.CreateFileGDB(BASE_DIRECTORY, ProjectName + " " + SoftwareEnvironmentLevel)

        # If the ScratchFolder is missing, create the folder
        if not os.path.exists( ScratchFolder ) and not os.path.isdir( ScratchFolder ):
            print("The ScratchFolder is the output location for scratch data")
            print("\t missing and will be created")
            os.makedirs( ScratchFolder )

        # Set the workspace to the ProjectGDB
        tmp_workspace = arcpy.env.workspace
        arcpy.env.workspace = ProjectGDB

        # Set the scratch workspace to the ScratchGDB
        tmp_scratchWorkspace = arcpy.env.scratchWorkspace
        arcpy.env.scratchWorkspace = ScratchGDB

        # Table Field dictionary
        # geomTypes: "Polygon", "PolyLine", "Point", "Table"
        tb_dict = {
                   "DataSeries_Template" : {"Table" : {1 : {"OARegionCode" : {"type" : "TEXT",
                                                                              "precision" : "",
                                                                              "scale" : "",
                                                                              "length" : 10,
                                                                              "aliasName" : "OA Region Code"}},
                                                       2 : {"OARegion" : {"type" : "TEXT",
                                                                          "precision" : "",
                                                                          "scale" : "",
                                                                          "length" : 50,
                                                                          "aliasName" : "OA Region"}},
                                                       3 : {"DisMapRegionCode" : {"type" : "TEXT",
                                                                                  "precision" : "",
                                                                                  "scale" : "",
                                                                                  "length" : 50,
                                                                                   "aliasName" : "DisMAP Region Code"}},
                                                       4 : {"RegionText" : {"type" : "TEXT",
                                                                            "precision" : "",
                                                                            "scale" : "",
                                                                            "length" : 50,
                                                                            "aliasName" : "Region Text"}},
                                                       5 : {"OASeasonCode" : {"type" : "TEXT",
                                                                              "precision" : "",
                                                                              "scale" : "",
                                                                              "length" : 10,
                                                                              "aliasName" : "Season Code"}},
                                                       6 : {"DisMapSeasonCode": {"type" : "TEXT",
                                                                                 "precision" : "",
                                                                                 "scale" : "",
                                                                                 "length" : 10,
                                                                                 "aliasName" : "DisMAP Season Code"}},
                                                       7 : {"ServiceName": {"type" : "TEXT",
                                                                            "precision" : "",
                                                                            "scale" : "",
                                                                            "length" : 50,
                                                                            "aliasName" : "Service Name"}}
                                                      }},
                   "RegionSpeciesYearImageName_Template" : {"Table" : {1 : {"OARegion" : {"type" : "TEXT",
                                                                                          "precision" : "",
                                                                                          "scale" : "",
                                                                                          "length" : 50,
                                                                                          "aliasName" : "OA Region"}},
                                                                       2 : {"Species" : {"type" : "TEXT",
                                                                                         "precision" : "",
                                                                                         "scale" : "",
                                                                                         "length" : 50,
                                                                                         "aliasName" : "Species"}},
                                                                       3 : {"CommonName" : {"type" : "TEXT",
                                                                                            "precision" : "",
                                                                                            "scale" : "",
                                                                                            "length" : 50,
                                                                                             "aliasName" : "Common Name"}},
                                                                       4 : {"SpeciesCommonName" : {"type" : "TEXT",
                                                                                                   "precision" : "",
                                                                                                   "scale" : "",
                                                                                                   "length" : 100,
                                                                                                   "aliasName" : "Species (Common Name)"}},
                                                                       5 : {"CoreSpecies" : {"type" : "TEXT",
                                                                                             "precision" : "",
                                                                                             "scale" : "",
                                                                                             "length" : 5,
                                                                                             "aliasName" : "Core Species"}},
                                                                       6 : {"Year" : {"type" : "SHORT",
                                                                                      "precision" : "",
                                                                                      "scale" : "",
                                                                                      "length" : 4,
                                                                                      "aliasName" : "Year"}},
                                                                       7 : {"StdTime" : {"type" : "DATE",
                                                                                         "precision" : "",
                                                                                         "scale" : "",
                                                                                         "length" : "",
                                                                                         "aliasName" : "StdTime"}},
                                                                       8 : {"Variable" : {"type" : "TEXT",
                                                                                           "precision" : "",
                                                                                           "scale" : "",
                                                                                           "length" : 50,
                                                                                           "aliasName" : "Variable"}},
                                                                       9 : {"Dimensions" : {"type" : "TEXT",
                                                                                           "precision" : "",
                                                                                           "scale" : "",
                                                                                           "length" : 10,
                                                                                           "aliasName" : "Dimensions"}},
                                                                      10 : {"ImageName" : {"type" : "TEXT",
                                                                                           "precision" : "",
                                                                                           "scale" : "",
                                                                                           "length" : 200,
                                                                                           "aliasName" : "Image Name"}},
                                                                       }},
                   "SpeciesRegionSeason_Template" : {"Table" : {1 : {"OARegion" : {"type" : "TEXT",
                                                                                   "precision" : "",
                                                                                   "scale" : "",
                                                                                   "length" : 50,
                                                                                   "aliasName" : "OA Region"}},
                                                                2 : {"Species" : {"type" : "TEXT",
                                                                                  "precision" : "",
                                                                                  "scale" : "",
                                                                                  "length" : 50,
                                                                                  "aliasName" : "Species"}},
                                                                3 : {"CommonName" : {"type" : "TEXT",
                                                                                      "precision" : "",
                                                                                      "scale" : "",
                                                                                      "length" : 50,
                                                                                       "aliasName" : "Common Name"}},
                                                                4 : {"SpeciesCommonName" : {"type" : "TEXT",
                                                                                            "precision" : "",
                                                                                            "scale" : "",
                                                                                            "length" : 100,
                                                                                            "aliasName" : "Species (Common Name)"}},
                                                                5 : {"CommonNameSpecies" : {"type" : "TEXT",
                                                                                            "precision" : "",
                                                                                            "scale" : "",
                                                                                            "length" : 100,
                                                                                            "aliasName" : "Common Name (Species)"}},
                                                                6 : {"CoreSpecies" : {"type" : "TEXT",
                                                                                      "precision" : "",
                                                                                      "scale" : "",
                                                                                      "length" : 5,
                                                                                      "aliasName" : "Core Species"}},
                                                                7 : {"DisMapRegionCode": {"type" : "TEXT",
                                                                                          "precision" : "",
                                                                                          "scale" : "",
                                                                                          "length" : 50,
                                                                                          "aliasName" : "DisMAP Region Code"}},
                                                                8 : {"DisMapSeasonCode": {"type" : "TEXT",
                                                                                          "precision" : "",
                                                                                          "scale" : "",
                                                                                          "length" : 10,
                                                                                          "aliasName" : "DisMAP Season Code"}}
                                                               }},
                   "Indicators_Template" : {"Table" : {1 : {"OARegion" : {"type" : "TEXT",
                                                                          "precision" : "",
                                                                          "scale" : "",
                                                                          "length" : 50,
                                                                          "aliasName" : "OA Region Code"}},
                                                       2 : {"DisMapRegionCode": {"type" : "TEXT",
                                                                                 "precision" : "",
                                                                                 "scale" : "",
                                                                                 "length" : 50,
                                                                                 "aliasName" : "DisMAP Region Code"}},
                                                       3 : {"DisMapSeasonCode": {"type" : "TEXT",
                                                                                 "precision" : "",
                                                                                 "scale" : "",
                                                                                 "length" : 10,
                                                                                 "aliasName" : "DisMAP Season Code"}},
                                                       4 : {"Species" : {"type" : "TEXT",
                                                                         "precision" : "",
                                                                         "scale" : "",
                                                                         "length" : 50,
                                                                         "aliasName" : "Species"}},
                                                       5 : {"CommonName" : {"type" : "TEXT",
                                                                            "precision" : "",
                                                                            "scale" : "",
                                                                            "length" : 50,
                                                                            "aliasName" : "Common Name"}},
                                                       6 : {"CoreSpecies" : {"type" : "TEXT",
                                                                             "precision" : "",
                                                                             "scale" : "",
                                                                             "length" : 5,
                                                                             "aliasName" : "Core Species"}},
                                                       7 : {"Year" : {"type" : "SHORT",
                                                                      "precision" : "",
                                                                      "scale" : "",
                                                                      "length" : 4,
                                                                      "aliasName" : "Year"}},
                                                       8 : {"CenterOfGravityLatitude" : {"type" : "DOUBLE",
                                                                                         "precision" : "",
                                                                                         "scale" : "",
                                                                                         "length" : "",
                                                                                         "aliasName" : "Center of Gravity Latitude"}},
                                                       9 : {"MinimumLatitude" : {"type" : "DOUBLE",
                                                                                 "precision" : "",
                                                                                 "scale" : "",
                                                                                 "length" : "",
                                                                                 "aliasName" : "Minimum Latitude"}},
                                                      10 : {"MaximumLatitude" : {"type" : "DOUBLE",
                                                                                 "precision" : "",
                                                                                 "scale" : "",
                                                                                 "length" : "",
                                                                                 "aliasName" : "Maximum Latitude"}},
                                                      11 : {"OffsetLatitude" : {"type" : "DOUBLE",
                                                                                "precision" : "",
                                                                                "scale" : "",
                                                                                "length" : "",
                                                                                "aliasName" : "Offset Latitude"}},
                                                      12 : {"CenterOfGravityLatitudeStandardError" : {"type" : "DOUBLE",
                                                                                                      "precision" : "",
                                                                                                      "scale" : "",
                                                                                                      "length" : "",
                                                                                                      "aliasName" : "Center of Gravity Latitude Standard Error"}},
                                                      13 : {"CenterOfGravityLongitude" : {"type" : "DOUBLE",
                                                                                          "precision" : "",
                                                                                          "scale" : "",
                                                                                          "length" : "",
                                                                                          "aliasName" : "Center of Gravity Longitude"}},
                                                      14 : {"MinimumLongitude" : {"type" : "DOUBLE",
                                                                                 "precision" : "",
                                                                                 "scale" : "",
                                                                                 "length" : "",
                                                                                 "aliasName" : "Minimum Longitude"}},
                                                      15 : {"MaximumLongitude" : {"type" : "DOUBLE",
                                                                                 "precision" : "",
                                                                                 "scale" : "",
                                                                                 "length" : "",
                                                                                 "aliasName" : "Maximum Longitude"}},
                                                      16 : {"OffsetLongitude" : {"type" : "DOUBLE",
                                                                                 "precision" : "",
                                                                                 "scale" : "",
                                                                                 "length" : "",
                                                                                 "aliasName" : "Offset Longitude"}},
                                                      17 : {"CenterOfGravityLongitudeStandardError" : {"type" : "DOUBLE",
                                                                                                      "precision" : "",
                                                                                                      "scale" : "",
                                                                                                      "length" : "",
                                                                                                      "aliasName" : "Center of Gravity Longitude Standard Error"}},
                                                      18 : {"CenterOfGravityDepth" : {"type" : "DOUBLE",
                                                                                      "precision" : "",
                                                                                      "scale" : "",
                                                                                      "length" : "",
                                                                                      "aliasName" : "Center of Gravity Depth"}},
                                                      19 : {"MinimumDepth" : {"type" : "DOUBLE",
                                                                              "precision" : "",
                                                                              "scale" : "",
                                                                              "length" : "",
                                                                              "aliasName" : "Minimum Depth"}},
                                                      20 : {"MaximumDepth" : {"type" : "DOUBLE",
                                                                              "precision" : "",
                                                                              "scale" : "",
                                                                              "length" : "",
                                                                              "aliasName" : "Maximum Depth"}},
                                                      21 : {"OffsetDepth" : {"type" : "DOUBLE",
                                                                              "precision" : "",
                                                                              "scale" : "",
                                                                              "length" : "",
                                                                              "aliasName" : "Offset Depth"}},
                                                      22 : {"CenterOfGravityDepthStandardError" : {"type" : "DOUBLE",
                                                                                                   "precision" : "",
                                                                                                   "scale" : "",
                                                                                                   "length" : "",
                                                                                                   "aliasName" : "Center of Gravity Depth Standard Error"}},
                                                      }},
                  }

        # Filter the table dictionary, if needed. Needs a list of table to filter
        # for. Source https://blog.finxter.com/how-to-filter-a-dictionary-in-python/
        if FilterTables:
            tb_dict = {k:v for (k,v) in tb_dict.items() if k in selected_tables}

        for tb in tb_dict:
            msg = "Dataet: {0}".format(tb)
            arcpy.AddMessage(msg)

            geomTypes = tb_dict[tb]
            for geomType in geomTypes:
                msg = "\t Geometry Type: {0}".format(geomType)
                arcpy.AddMessage(msg)
                if not arcpy.Exists(tb) or ReplaceTables:
                    if arcpy.Exists(tb) and ReplaceTables:
                        arcpy.management.Delete(tb)
                    else:
                        msg = ">-> ReplaceTables set to True, but {0} dataset is missing".format(tb)
                        arcpy.AddMessage(msg)

                    if "Table" in geomType:
                        # Create table
                        arcpy.management.CreateTable(ProjectGDB, tb)
                        msg = arcpy.GetMessages()
                        arcpy.AddMessage("\t\t {0}\n".format(msg.replace('\n', '\n\t\t ')))

                    else:
                        # Create feature classes
                        arcpy.management.CreateFeatureclass(ProjectGDB, tb, "{0}".format(geomType.upper()), spatial_reference = sp_ref)
                        msg = arcpy.GetMessages()
                        arcpy.AddMessage("\t\t {0}\n".format(msg.replace('\n', '\n\t\t ')))

                    ids = geomTypes[geomType]
                    for id in ids:
                        msg = "\t\t ID: {0}".format(id)
                        arcpy.AddMessage(msg)

                        # Get fields from dictionary
                        fields = ids[id]
                        for field in fields:
                            msg = "\t\t\t Field: {0}".format(field)
                            arcpy.AddMessage(msg)

                            fieldName = field
                            items = fields[field]
                            fieldtype = items["type"]
                            msg = "\t\t\t\t fieldtype: {0}".format(fieldtype)
                            arcpy.AddMessage(msg)

                            fieldprecision = items["precision"]
                            msg = "\t\t\t\t fieldprecision: {0}".format(fieldprecision)
                            arcpy.AddMessage(msg)

                            fieldscale = items["scale"]
                            msg = "\t\t\t\t fieldscale: {0}".format(fieldscale)
                            arcpy.AddMessage(msg)


                            fieldlength = items["length"]
                            msg = "\t\t\t\t fieldlength: {0}".format(fieldlength)
                            arcpy.AddMessage(msg)

                            fieldAliasName = items["aliasName"]
                            msg = "\t\t\t\t fieldAliasName: {0}".format(fieldAliasName)
                            arcpy.AddMessage(msg)

                            # Add Field
                            arcpy.management.AddField(tb, fieldName, fieldtype, fieldprecision, fieldscale, fieldlength, fieldAliasName)
                            msg = arcpy.GetMessages()
                            arcpy.AddMessage("\t\t\t\t {0}\n".format(msg.replace('\n', '\n\t\t\t\t ')))
                            #print("\t\t\t\t {0}\n".format(msg.replace('\n', '\n\t\t\t\t ')))
                            del field, fieldName, items, fieldtype
                            del fieldprecision, fieldscale, fieldlength
                            del fieldAliasName
                        del id, fields
                    del ids
            # Add Metadata
            addMetadata(tb)
        #
        del tb_dict, tb, msg, geomTypes, geomType

        # Set the workspace to the tmp_workspace
        arcpy.env.workspace = tmp_workspace
        # Set the scratch workspace to the tmp_scratchWorkspace
        arcpy.env.scratchWorkspace = tmp_scratchWorkspace
        del tmp_workspace, tmp_scratchWorkspace

        localKeys =  [key for key in locals().keys() if "function" not in key]

        if localKeys:
            msg = "Local Keys in {0}(): {1}".format(function, u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys, function

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo

def functionName():
    #print(inspect.stack()[0][0].f_code.co_name)
    #print(inspect.stack()[0][3])
    #print(inspect.currentframe().f_code.co_name)
    #print(sys._getframe().f_code.co_name)
    print(function_name())
    print(inspect.stack()[0].function)
    print("%s/%s" %(sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name))

# Output a message if level is under or equal to the DEBUG_LEVEL
def DEBUG_OUTPUT(level, message):
    if level <= DEBUG_LEVEL:
        print("[DEBUG LEVEL ("+ str(level) + " / " + str(DEBUG_LEVEL) +")] " + message )


def logFile(log_file, msg):
    try:
        print(msg)
        my_log = open(log_file, "a+")
        my_log.write(msg + '\n')
        my_log.close
        del my_log
    except:
        print("Log Folder may be missing. Set ProjectSetup to True.")

def generateMosaics():
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        #arcpy.AddMessage(function)

        # Set a start time so that we can see how log things take
        start_time = time()

        arcpy.env.overwriteOutput = True
        arcpy.env.scratchWorkspace = ScratchGDB
        arcpy.env.rasterStatistics = u'STATISTICS 1 1'
        arcpy.env.buildStatsAndRATForTempRaster = True

        tmp_workspace = arcpy.env.workspace

        arcpy.env.workspace = ScratchGDB
        #print(ScratchGDB)
        # This removes the saved rasters in the ScratchGDB
        scratch_rasters = arcpy.ListRasters("*")
        if scratch_rasters:
            for raster in scratch_rasters: arcpy.management.Delete(raster)
            arcpy.management.Compact(ScratchGDB)
        del scratch_rasters

        arcpy.env.workspace = ScratchFolder
        scratch_rasters = arcpy.ListRasters("*")
        if scratch_rasters:
            # This removes the saved rasters in the ScratchGDB
            for raster in [r for r in arcpy.ListRasters("*")]: arcpy.management.Delete(raster)
        del scratch_rasters

        arcpy.env.workspace = tmp_workspace
        del tmp_workspace


        region_species_image_name = os.path.join(ProjectGDB, 'RegionSpeciesYearImageName')

        # Start looping over the table_name array as we go region by region.
        for table_name in table_names:
            # Assigning variables from items in the chosen table list
            # region_shape = table_name[0]
            # region_boundary = table_name[1]
            region_abb = table_name[2]
            region = table_name[3]
            csv_file = table_name[4]
            region_georef = table_name[5]
            # region_contours = table_name[6]
            cell_size = table_name[7]

            del table_name

            # Make Geodatabase friendly name
            region_name = region.replace('(','').replace(')','').replace('-','_to_').replace(' ', '_').replace("'", "")

            # For benchmarking.
            log_file = os.path.join(LOG_DIRECTORY, region + ".log")
            # Start with removing the log file if it exists
            #if os.path.isfile(log_file):
            #    os.remove(log_file)

            # Write a message to the log file
            msg = "STARTING REGION {} ON {}".format(region, strftime("%a %b %d %I:%M:%S %p", localtime()))
            logFile(log_file, msg)

            # Set the output coordinate system to what is available for us.
            #region_sr = arcpy.SpatialReference(srs[region_georef][0])
            region_sr = srs[region_georef]
            arcpy.env.outputCoordinateSystem = region_sr
            #del region_sr

            # region abbreviated path
            region_abb_folder = os.path.join(ANALYSIS_DIRECTORY, region_abb)

            # Tests if the abbreviated region folder exists and if it is in
            # selected regions
            if os.path.isdir(region_abb_folder):
                msg = ">-> Region (abb): {0}\n\t Region:  {1}\n\t CSV File: {2}"\
                     .format(region_abb, region, csv_file)
                logFile(log_file, msg)
                # List of folders in the region dictory
                species_folders = [d for d in os.listdir(region_abb_folder) if \
                               os.path.isdir(os.path.join(region_abb_folder, d)) and d not in ['Core Species Richness', 'Species Richness']]
                if species_folders:
                    msg = '>-> There are {0} species folders for the {1} region folder.'.format(len(species_folders), region)
                    logFile(log_file, msg)
                    if FilterSpecies:
                        # Convert the selected species list to matcv the species
                        # folder name by removing haphens and periods
                        #selected_species_keys = [ss.replace("'","").replace(".","") for ss in selected_species.keys()]
                        selected_species_keys = [ss.replace(".","").replace("-"," ").replace("(","").replace(")","").replace("/","and") for ss in selected_species.keys()]
                        # Find the intersection between the list of specie folders and the filtered list
                        selected_species_folders = list(set(species_folders) & set(selected_species_keys))
                        del selected_species_keys
                        # Sort the list
                        selected_species_folders.sort()
                        if selected_species_folders:
                            # Replace the list
                            species_folders = selected_species_folders[:]
                            msg = '>-> There are {0} selected species in the {1} region folder to process.'.format(len(species_folders), region)
                            logFile(log_file, msg)
                        else:
                            msg = '>-> There are no selected species in the {0} region folder to process.'.format(region)
                            logFile(log_file, msg)
                            msg = '>-> Need to change the selected species list for this region.'
                            logFile(log_file, msg)
                            return
                        del selected_species_folders

                    # Get a disctionary of species and common names from the
                    # CVS Table in the Project GDB
                    csv_file_table = os.path.join(ProjectGDB, csv_file)
                    # Dictionary of species and common names that are in the tables
                    species_common_name_dict = unique_fish_dict(csv_file_table)
                    #print( species_common_name_dict )
                    #print("Is the")

                    # Clean up
                    del csv_file_table
                else:
                    msg = '>-> There are no species folders in the region ({0}) folder.'.format(region)
                    logFile(log_file, msg)
                    msg = '>-> Need to run generateRasters to create images.'
                    logFile(log_file, msg)
                    return
            else:
                msg = '>-> The folder for this region ({0}) is missing from the Analysis Folder and needs to be created.'.format(region)
                logFile(log_file, msg)
                return

            # Cleanup
            del region_georef

            # Creating the region_mosaic to be used. We output this to the file system in the appropriate folder.
            msg = '> Creating the {} Mosaic. This may take a while... Please wait...'.format(region)
            logFile(log_file, msg)

            #
            region_mosaic = os.path.join(ProjectGDB, region_abb)
            #result = arcpy.management.Delete(region_mosaic)
            #print(result)

            if not arcpy.Exists( region_mosaic ) or ReplaceMosaicDatasets:
                msg = '>-> Creating the {} Mosaic'.format(region)
                logFile(log_file, msg)

                arcpy.management.CreateMosaicDataset(in_workspace = ProjectGDB,
                                                     in_mosaicdataset_name = region_abb,
                                                     coordinate_system = region_sr,
                                                     num_bands = "1",
                                                     pixel_type = "32_BIT_FLOAT",
                                                     product_definition = "",
                                                     product_band_definitions="")

                msg = arcpy.GetMessages()
                msg = ">->-> {0}\n".format(msg.replace('\n', '\n>->-> '))
                logFile(log_file, msg)
                del msg

            # Loading images into the Mosaic.
            msg = '> Loading the {} Mosaic. This may take a while... Please wait...'.format(region)
            logFile(log_file, msg)

            total_count = len(species_folders)
            count = 0
            # Loop through dictionary
            for species in species_common_name_dict:
                # Speices folders do not include the '.' that can be a part
                # of the name, so remove
                #species_folder = species.replace('.','')
                species_folder = species.replace(".","").replace("-"," ").replace("(","").replace(")","").replace("/","and")
                #selected_species_keys = [ss.replace(".","").replace("-"," ").replace("(","").replace(")","").replace("/","and") for ss in selected_species.keys()]
                # The common name is the value in the dictionary
                common = species_common_name_dict[species][0]
                core_species = species_common_name_dict[species][1]
                #common, core_species = species_common_name_dict[species]

                #msg = ">-> Species: {0}, Common Name: {1}".format(species, common)
                #logFile(log_file, msg)

                # Test of the speices folder name from the dictionary is in
                # the list of folders in the region folder. The species
                # folder may not have been created, so need to test
                # if species_folder in species_folders first, then as a filter see
                # if species is in a shorter list. Will need to change this later


                # This test is species is in selected species
                if species_folder in species_folders: # and species_folder in selected_species.keys():
                    count += 1
                    # Test if there a corresponding folder in RASTER DIRECTORY, if
                    # not create the folder
                    #out_species_folder = os.path.join(MOSAIC_DIRECTORY, region_abb, species_folder)
                    # Make the speices folder in the raster directory if missing
                    #if not os.path.isdir(out_species_folder):
                    #    os.makedirs(out_species_folder)

                    msg = ">-> Species: {0}, Common Name: {1}".format(species, common)
                    logFile(log_file, msg)

                    input_folder = os.path.join(region_abb_folder, species_folder)

                    msg = ">-> Adding Rasters to the {0} Mosaic Dataset".format(region)
                    logFile(log_file, msg)

                    # Process: Add Rasters To Mosaic Dataset
                    arcpy.management.AddRastersToMosaicDataset(in_mosaic_dataset = region_mosaic,
                                                               raster_type = "Raster Dataset",
                                                               input_path = input_folder,
                                                               update_cellsize_ranges = "UPDATE_CELL_SIZES",
                                                               #update_cellsize_ranges = "NO_CELL_SIZES",
                                                               update_boundary = "UPDATE_BOUNDARY",
                                                               #update_boundary = "NO_BOUNDARY",
                                                               update_overviews = "NO_OVERVIEWS",
                                                               maximum_pyramid_levels = "",
                                                               maximum_cell_size = "0",
                                                               minimum_dimension = "1500",
                                                               spatial_reference = region_sr,
                                                               filter = "*.tif",
                                                               sub_folder = "NO_SUBFOLDERS",
                                                               #duplicate_items_action = "OVERWRITE_DUPLICATES",
                                                               duplicate_items_action = "EXCLUDE_DUPLICATES",
                                                               build_pyramids = "NO_PYRAMIDS",
                                                               calculate_statistics = "CALCULATE_STATISTICS",
                                                               #calculate_statistics = "NO_STATISTICS",
                                                               build_thumbnails = "BUILD_THUMBNAILS",
                                                               #build_thumbnails = "NO_THUMBNAILS",
                                                               operation_description = "DisMAP",
                                                               #force_spatial_reference = "NO_FORCE_SPATIAL_REFERENCE",
                                                               force_spatial_reference = "FORCE_SPATIAL_REFERENCE",
                                                               estimate_statistics = "ESTIMATE_STATISTICS",
                                                               #estimate_statistics = "NO_STATISTICS",
                                                               )
                    msg = arcpy.GetMessages()
                    msg = ">->-> {0}\n".format(msg.replace('\n', '\n>->-> '))
                    logFile(log_file, msg)
                    del msg

                    # Cleanup
                    del input_folder

                else:
                    if not os.path.isdir(os.path.join(region_abb_folder, species_folder)):
                        msg = "###--->>> Species: {0} ({1}) does not have a folder.".format(species, common)
                        logFile(log_file, msg)
                        del msg
                    elif os.path.isdir(os.path.join(region_abb_folder, species_folder)):
                        msg = "###--->>> Species: {0} ({1}) is not part of the selected species list.".format(species, common)
                        logFile(log_file, msg)
                        del msg
                    else:
                        msg = "###--->>> Something is wrong."
                        logFile(log_file, msg)
                        del msg

                # Cleanup
                del species, species_folder, common, core_species

            msg = ">-> arcpy.management.JoinField region_mosaic with region_species_image_name"
            logFile(log_file, msg); del msg

            arcpy.management.JoinField(in_data = region_mosaic, in_field="Name", join_table = region_species_image_name, join_field="ImageName", fields="OARegion;Species;CommonName;SpeciesCommonName;CoreSpecies;Year;StdTime;Variable;Dimensions")

            msg = '>-> Adding field index in the {0} Feature Class'.format(region)
            logFile(log_file, msg)

            try:
                arcpy.RemoveIndex_management(region_mosaic, ["{0}_MosaicSpeciesIndex".format(region_abb)])
            except:
                pass

            # Add Attribute Index
            arcpy.management.AddIndex(region_mosaic, ['Species', 'CommonName', 'SpeciesCommonName', 'Year'], "{0}_MosaicSpeciesIndex".format(region_abb), "NON_UNIQUE", "NON_ASCENDING")

            msg = arcpy.GetMessages()
            msg = ">->->-> {0}".format(msg.replace('\n', '\n>->->-> '))
            logFile(log_file, msg); del msg

            # Add metadata
            years_md = unique_years(region_mosaic)

            region_mosaic_md = md.Metadata(region_mosaic)
            region_mosaic_md.synchronize('ACCESSED', 1)
            region_mosaic_md.title = "{0} {1}".format(region.replace('-',' to '), DateCode)
            region_mosaic_md.tags = "{0}, {1} to {2}".format(geographic_regions[region_abb], min(years_md), max(years_md))
            region_mosaic_md.save()
            del region_mosaic_md, years_md

            # Cleanup
            del region_mosaic
            del species_common_name_dict, species_folders
            del csv_file, region_name
            del region_abb_folder
            del region_sr, region_abb, cell_size

            #Final benchmark for the region.
            msg = "ENDING REGION {} COMPLETED ON {}".format(region, strftime("%a %b %d %I:%M:%S %p", localtime()))
            logFile(log_file, msg)
            del msg
            del region

        #arcpy.env.workspace = tmp_workspace
        #del tmp_workspace
        del total_count, count, region_species_image_name

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = u"Elapsed Time {0} (H:M:S)\n".format(strftime("%H:%M:%S", gmtime(elapse_time)))
        logFile(log_file, msg)
        del msg, start_time, end_time, elapse_time, log_file

        localKeys =  [key for key in locals().keys()]

        if localKeys:
            msg = "Local Keys in generateMosaics(): {0}".format(u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo

def generatePointFeatureClasses():
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        # Set the workspace to the ProjectGDB
        tmp_workspace = arcpy.env.workspace
        arcpy.env.workspace = ProjectGDB

        # Set the scratch workspace to the ScratchGDB
        tmp_scratchWorkspace = arcpy.env.scratchWorkspace
        arcpy.env.scratchWorkspace = ScratchGDB

        # Start looping over the table_name array as we go region by region.
        for table_name in table_names:
            # Assigning variables from items in the chosen table list
            region_shape = table_name[0]
            region_boundary = table_name[1]
            region_abb = table_name[2]
            region = table_name[3]
            csv_file = table_name[4]
            region_georef = table_name[5]
            region_contours = table_name[6]

            # Make Geodatabase friendly name
            region_name = region.replace('(','').replace(')','').replace('-','_to_').replace(' ', '_').replace("'", "")

            # For benchmarking.
            log_file = os.path.join(LOG_DIRECTORY, region + ".log")
            # Start with removing the log file if it exists
            #if os.path.isfile(log_file):
            #    os.remove(log_file)

            # Set a start time so that we can see how log things take
            start_time = time()

            # Write a message to the log file
            msg = "STARTING REGION {0} ON {1}".format(region, strftime("%a %b %d %I:%M:%S %p", localtime()))
            logFile(log_file, msg)

            # THIS WILL ACTUALLY DELETE FROM THE PHYSICAL HARD DISK DRIVE since it is pointing to a specific location.
            # arcpy.management.Delete(MAP_DIRECTORY+region_abb+"\\" + region_abb + "_Layer.shp")

            # Generate the shapefile to be used. We output this to the file system in the appropriate folder.
            msg = '> Generating {0} Feature Class. This may take a while... Please wait...'.format(region)
            logFile(log_file, msg)

            # Set the output coordinate system to what is available for us.
            #region_sr = arcpy.SpatialReference(srs[region_georef][0])
            region_sr = srs[region_georef]
            arcpy.env.outputCoordinateSystem = region_sr
            del region_sr

            # Input Feature class
            in_fc = os.path.join(ProjectGDB, "{0}_Survey_Locations".format(region_name))
            if not arcpy.Exists(in_fc) or ReplaceFeatureClass:
                #print(in_fc)
                if ReplaceFeatureClass and arcpy.Exists(in_fc):
                    msg = '>-> Removing the {0} Feature Class'.format(region)
                    logFile(log_file, msg)

                    # Geoprocessing tools return a result object of the derived
                    # output dataset.
                    result = arcpy.management.Delete(in_fc)
                    del result

                    # A print statement will display the string
                    # representation of the output.
                    #print(result)

                    # A result object can be indexed to get the output value.
                    # Note: a result object also has a getOutput() method that
                    # can be used for the same purpose.
                    #result_value = result[0]
                    #print(result_value)
                else:
                    msg = ">-> ReplaceFeatureClass set to True, but {0} Feature Class is missing".format(region)
                    logFile(log_file, msg)

                msg = '>-> Creating the {} Feature Class'.format(region)
                logFile(log_file, msg)

                #my_unique_fish = unique_fish( in_fc )

                # Test if we are filtering on species. If so, a new species list is
                # created with the selected species remaining in the list
                #if FilterSpecies:
                #    # Get a shorter list
                #    my_unique_fish = [f for f in my_unique_fish if f in selected_species.keys()]
                #else:
                #    pass

                in_table = os.path.join(ProjectGDB, csv_file)
                # Make XY Event  Layer
                my_events = arcpy.management.MakeXYEventLayer(in_table,"Longitude","Latitude","my_events","#","#")
                del in_table

                # Make it a feature class and output it to the local hard disk drive (for usage and debugging purposes)
                #tmp_fc_name = region_name + '_tmp'
                #tmp_fc = os.path.join(DefaultGDB, tmp_fc_name)
                arcpy.FeatureClassToFeatureClass_conversion(in_features=my_events, out_path=ProjectGDB, out_name= "{0}_Survey_Locations".format(region_name),
                                                            where_clause='',
                                                            field_mapping='',
                                                            #field_mapping="""Field1 "Field1" true true false 50 Text 0 0 ,First,#,my_events,Field1,-1,-1;region "region" true true false 50 Text 0 0 ,First,#,my_events,region,-1,-1;haulid "haulid" true true false 255 Text 0 0 ,First,#,my_events,haulid,-1,-1;year "year" true true false 4 Long 0 0 ,First,#,my_events,year,-1,-1;spp "spp" true true false 50 Text 0 0 ,First,#,my_events,spp,-1,-1;wtcpue "wtcpue" true true false 8 Double 10 20 ,First,#,my_events,wtcpue,-1,-1;common "common" true true false 50 Text 0 0 ,First,#,my_events,common,-1,-1;lat "lat" true true false 8 Double 10 20 ,First,#,my_events,lat,-1,-1;stratum "stratum" true true false 50 Text 0 0 ,First,#,my_events,stratum,-1,-1;stratumare "stratumare" true true false 50 Text 0 0 ,First,#,my_events,stratumarea,-1,-1;lon "lon" true true false 8 Double 10 20 ,First,#,my_events,lon,-1,-1;depth "depth" true true false 50 Text 0 0 ,First,#,my_events,depth,-1,-1""",
                                                            config_keyword="")
                #arcpy.conversion.FeatureClassToFeatureClass("neusf_csv_XYTableToPoint", r"C:\Users\jfken\Documents\GitHub\DisMap\Default.gdb", "neusf_csv_XY", '', 'csv_id "csv_id" true true false 4 Long 0 0,First,#,neusf_csv_XYTableToPoint,csv_id,-1,-1;region "region" true true false 34 Text 0 0,First,#,neusf_csv_XYTableToPoint,region,0,34;haulid "haulid" true true false 30 Text 0 0,First,#,neusf_csv_XYTableToPoint,haulid,0,30;year "year" true true false 4 Long 0 0,First,#,neusf_csv_XYTableToPoint,year,-1,-1;spp "spp" true true false 64 Text 0 0,First,#,neusf_csv_XYTableToPoint,spp,0,64;wtcpue "wtcpue" true true false 8 Double 0 0,First,#,neusf_csv_XYTableToPoint,wtcpue,-1,-1;wtc_cube "wtc_cube" true true false 8 Double 0 0,First,#,neusf_csv_XYTableToPoint,wtc_cube,-1,-1;common "common" true true false 64 Text 0 0,First,#,neusf_csv_XYTableToPoint,common,0,64;stratum "stratum" true true false 4 Long 0 0,First,#,neusf_csv_XYTableToPoint,stratum,-1,-1;stratumarea "stratumarea" true true false 8 Double 0 0,First,#,neusf_csv_XYTableToPoint,stratumarea,-1,-1;lat "lat" true true false 8 Double 0 0,First,#,neusf_csv_XYTableToPoint,lat,-1,-1;lon "lon" true true false 8 Double 0 0,First,#,neusf_csv_XYTableToPoint,lon,-1,-1;depth "depth" true true false 8 Double 0 0,First,#,neusf_csv_XYTableToPoint,depth,-1,-1', '')

                # Clear the XY Event Layer from memory.
                arcpy.management.Delete("my_events")
                del my_events

                msg = '>-> Adding field index in the {0} Feature Class'.format(region)
                logFile(log_file, msg)

                # Add Attribute Index
                arcpy.management.AddIndex(in_fc, ['Species', 'CommonName', 'SpeciesCommonName', 'Year'], "{0}_SurveyLocationsSpeciesIndex".format(region_name), "NON_UNIQUE", "NON_ASCENDING")

                result = arcpy.management.GetCount(in_fc)
                msg = '>-> {} has {} records'.format("{0}_Survey_Locations".format(region_name), result[0])
                logFile(log_file, msg)
                del result

                #
                addMetadata(in_fc)
                del in_fc

                msg = '> Generating {0} Feature Class completed ON {1}'.format(region, strftime("%a %b %d %I:%M:%S %p", localtime()))
                logFile(log_file, msg)

            else:
                msg = '>-> {0} Feature Class Exists'.format(region)
                logFile(log_file, msg)

            #Final benchmark for the region.
            msg = "ENDING REGION {} COMPLETED ON {}".format(region, strftime("%a %b %d %I:%M:%S %p", localtime()))
            logFile(log_file, msg)

            # Elapsed time
            end_time = time()
            elapse_time =  end_time - start_time
            msg = u"Elapsed Time {0} (H:M:S)\n".format(strftime("%H:%M:%S", gmtime(elapse_time)))
            logFile(log_file, msg)

        # Clean up
        del msg, table_name, region_abb, region, csv_file, region_georef
        del log_file, start_time, end_time, elapse_time
        del region_shape, region_boundary, region_contours, region_name

        # Set the workspace to the tmp_workspace
        arcpy.env.workspace = tmp_workspace
        # Set the scratch workspace to the tmp_scratchWorkspace
        arcpy.env.scratchWorkspace = tmp_scratchWorkspace
        del tmp_workspace, tmp_scratchWorkspace

        localKeys =  [key for key in locals().keys() if "function" not in key]

        if localKeys:
            msg = "Local Keys in {0}(): {1}".format(function, u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys, function

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo

def generateRasters():
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        # Set the workspace to the ProjectGDB
        tmp_workspace = arcpy.env.workspace
        arcpy.env.workspace = ProjectGDB

        # Set the scratch workspace to the ScratchGDB
        tmp_scratchWorkspace = arcpy.env.scratchWorkspace
        #print(os.path.abspath(ScratchGDB))
        #arcpy.env.scratchWorkspace = os.path.abspath(ScratchGDB)
        arcpy.env.scratchWorkspace = os.path.abspath(r'{0}'.format(ScratchGDB))
        print(arcpy.env.scratchWorkspace)
        print(arcpy.env.scratchGDB)
        print(arcpy.env.scratchFolder)

##        # If the scratch workspace is missing, referencing the env will create the workspace
##        msg = arcpy.env.scratchWorkspace
##        arcpy.AddMessage(msg)
##        msg = arcpy.env.scratchGDB
##        arcpy.AddMessage(msg)
##        msg = arcpy.env.scratchFolder
##        arcpy.AddMessage(msg)
##        del msg

        arcpy.env.overwriteOutput = True
        # Set the compression environment to LZ77
        arcpy.env.compression = "LZ77"

        # Start looping over the table_name array as we go region by region.
        for table_name in table_names:
            # Assigning variables from items in the chosen table list
            region_shape = table_name[0]
            region_boundary = table_name[1]
            region_abb = table_name[2]
            region = table_name[3]
            csv_file = table_name[4]
            region_georef = table_name[5]
            region_contours = table_name[6]
            cell_size = table_name[7]

            region_shape = os.path.join(ProjectGDB, region_abb+"_Shape")
            region_snap_raster = os.path.join(ProjectGDB, region_abb+"_Snap_Raster")
            region_raster_mask = os.path.join(ProjectGDB, region_abb+"_Raster_Mask")

            arcpy.env.snapRaster = region_snap_raster
            # we need to set the mask and extent of the environment, or the raster and items may not come out correctly.
            arcpy.env.extent = arcpy.Describe(region_snap_raster).extent
            arcpy.env.mask = region_raster_mask

            # Make Geodatabase friendly name
            region_name = region.replace('(','').replace(')','').replace('-','_to_').replace(' ', '_').replace("'", "")

            # For benchmarking.
            log_file = os.path.join(LOG_DIRECTORY, region + ".log")
            # Start with removing the log file if it exists
            #if os.path.isfile(log_file):
            #    os.remove(log_file)

            # Set a start time so that we can see how log things take
            start_time = time()

            # Write a message to the log file
            msg = "STARTING REGION {} ON {}".format(region, strftime("%a %b %d %I:%M:%S %p", localtime()))
            logFile(log_file, msg)


            # Generate the shapefile to be used. We output this to the file system in the appropriate folder.
            msg = '> Generating {} Rasters. This may take a while... Please wait...'.format(region)
            logFile(log_file, msg)

            # Prepare the points layer
            in_fc = os.path.join(ProjectGDB, "{0}_Survey_Locations".format(region_name))
            my_points = arcpy.management.MakeFeatureLayer(in_fc, "my_points")
            del in_fc

            # Add the YearWeights feild
            fields =  [f.name for f in arcpy.ListFields(my_points)]
            if "YearWeights" not in fields:
                # Add the YearWeights field to the feature class. This is used for the IDW modeling later
                arcpy.management.AddField(my_points, "YearWeights", "SHORT",field_alias = "Year Weights")
            del fields

            # The shapefile used to create the extent and mask for the environment variable
            #my_shape = arcpy.management.MakeFeatureLayer(MAP_DIRECTORY+"\\"+region_abb+"\\" + region_shape + ".shp", "my_shape")
            #my_shape = arcpy.management.MakeFeatureLayer(region_shape, "my_shape")

            # Set the output coordinate system to what is available for us.
            region_sr = srs[region_georef]
            arcpy.env.outputCoordinateSystem = region_sr
            arcpy.env.cartographicCoordinateSystem = region_sr
            del region_sr

            result = arcpy.management.GetCount(my_points)
            msg = '>-> {} has {} records'.format(region, result[0])
            logFile(log_file, msg)
            del result

            my_unique_fish = unique_fish( my_points )
            #print(my_unique_fish)
            #print(list(selected_species.keys()))

            # Test if we are filtering on species. If so, a new species list is
            # created with the selected species remaining in the list
            if FilterSpecies:
                # Get a shorter list
                my_unique_fish = [f for f in my_unique_fish if f in list(selected_species.keys())]
                print(my_unique_fish)
            else:
                print("Something wrong")

            # Finally we will start looping of the uniquely identified fish in this csv.
            for this_fish in my_unique_fish:
                # We prepare a place so that we can place fish data relevant to the fish species we're looking at.
                #print(this_fish)
                my_fish_dir = this_fish.replace("'","")
                #print(my_fish_dir)
                my_fish_dir = my_fish_dir.replace(".","")
                #print(my_fish_dir)
                my_fish_dir = my_fish_dir.replace("/","and")
                #print(my_fish_dir)
                my_fish_dir = my_fish_dir.replace("(","")
                #print(my_fish_dir)
                my_fish_dir = my_fish_dir.replace(")","")
                #print(my_fish_dir)
                my_fish_dir = my_fish_dir.replace("-"," ")
                #print(my_fish_dir)
                # To remove double spaces
                my_fish_dir = " ".join(my_fish_dir.split())

                msg = ">-> Creating Raster Files in directory {}".format(my_fish_dir)
                logFile(log_file, msg)

                # Create a special folder for them
                fish_dir = os.path.join(ANALYSIS_DIRECTORY, region_abb, my_fish_dir)
                if not os.path.exists( fish_dir  ) and not os.path.isdir( fish_dir ):
                    os.makedirs( ANALYSIS_DIRECTORY + "\\" + region_abb + "\\" + my_fish_dir )

                #
                arcpy.env.workspace = fish_dir

                # if not os.path.exists( PICTURE_FOLDER + "\\" + region_abb + "\\" + my_fish_dir ) and not os.path.isdir( PICTURE_FOLDER + "\\" + region_abb + "\\" + my_fish_dir ):
                #     os.makedirs( PICTURE_FOLDER + "\\" + region_abb + "\\" + my_fish_dir )

                # We are pretty much going to set min to 0, max to STD(OVER YEARS)*2+AVG(OVER YEARS), and the other two shouldn't matter, but we'll set those anyways.
                select_by_fish_no_years(my_points, this_fish.replace("'","''") )

                # Get all of the unique years
                my_unique_years = unique_year( my_points, this_fish.replace("'","''") )

                #print("\n####################\n")
                #print(my_unique_years)
                #print("\n####################\n")

                # Test if we are filtering on years. If so, a new year list is
                # created with the selected years remaining in the list
                if FilterYears:
                    # Get a shorter list
                    my_unique_years = [y for y in my_unique_years if y in selected_years]
                else:
                    pass

                # Note: in the previous script there was an attemp to find the
                # earliest year of data, but that doesn't make since as the
                # unique year list is ordered.
                # set the year to the future, where no data should exist.
                # We will update this variable as we loop over the uniquely
                # identified years for later.
                # year_smallest = date.today().year + 100
                # Since the goal is to get the first (or smallest) year in the list
                # year_smallest = min(my_unique_years)

                #print("Year smallest in the future: {}".format(year_smallest))
                for this_year in my_unique_years:
                    msg =  ">-> Creating Raster File {}.tif".format(str(this_year))
                    logFile(log_file, msg)

                    # select the fish species data by the year provided.
                    select_by_fish(my_points, this_fish.replace("'","''"), str(this_year))

                    # Calculate YearWeights=3-(abs(Tc-Ti))
                    # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
                    # The following inputs are layers or table views: "my_points"
                    arcpy.management.CalculateField(in_table=my_points, field="YearWeights", expression="3 - (abs({0} - !Year!))".format(int(this_year)), expression_type="PYTHON", code_block="")

                    # Get the count of records for selected species
                    result = arcpy.management.GetCount(my_points)
                    msg = ">->-> {} has {} records for {} and year {}".format(region, result[0], this_fish, this_year)
                    logFile(log_file, msg)
                    del result

                    #Get a count of all the points and store it.
                    # result = arcpy.management.GetCount(my_points)
                    # count = int(result.getOutput(0))
                    # del result

                    # Generate the interpolated Raster file and store it on the local hard drive. Can now be used in other ArcGIS Documents
                    # Please make sure when importing, that you are projecting it on the map propertly.

                    # Replace a layer/table view name with a path to a dataset
                    # (which can be a layer file) or create the layer/table view
                    # within the script
                    # The following inputs are layers or table views:
                    # "AI_Layer", "AI_Boundary"
                    #arcpy.gp.Idw_sa(my_points, "wtc_cube", ANALYSIS_DIRECTORY + "\\" + region_abb + "\\" + my_fish_dir + "\\" + str(this_year) + ".tif", "#", "1", "VARIABLE 15 200000", my_bounds)

                    #my_fish_raster = os.path.join(ANALYSIS_DIRECTORY, region_abb, my_fish_dir, str(this_year) + ".tif")
                    # No special character used, replace spaces, '.', '-' with '_' (underscores)
                    fish_year_raster = "{0}_{1}_{2}".format(region_abb, my_fish_dir.replace(" ","_"), str(this_year))
                    #                .replace(".","").replace("-"," ").replace("(","").replace(")","").replace("/","and").replace(" ","_")

                    my_fish_raster = os.path.join(ANALYSIS_DIRECTORY, region_abb, my_fish_dir, fish_year_raster+".tif")
                    if not os.path.isfile(my_fish_raster) or ReplaceRaster:
                        if os.path.isfile(my_fish_raster) and ReplaceRaster:
                            msg = '>->->-> Removing the {0} image'.format(fish_year_raster)
                            logFile(log_file, msg)

                            # Geoprocessing tools return a result object of the derived
                            # output dataset.
                            result = arcpy.management.Delete(my_fish_raster)
                            msg = arcpy.GetMessages()
                            msg = ">->->-> {0}".format(msg.replace('\n', '\n>->->-> '))
                            logFile(log_file, msg); del msg, result

                        else:
                            msg = ">->->-> ReplaceRaster set to True, but {0} image is missing".format(fish_year_raster)
                            logFile(log_file, msg)


                        # Check out Spatial Analyst
                        # arcpy.CheckOutExtension("Spatial")

                        # Check Out GeoStats Extension
                        arcpy.CheckOutExtension("GeoStats")

                        msg =  ">->-> Creating Raster File {} for {}".format(fish_year_raster, this_fish)
                        logFile(log_file, msg)

                        #arcpy.gp.Idw_sa(my_points, "WTCPUECubeRoot", my_fish_raster, "#", "1", "VARIABLE 15 200000", my_bounds)
                        # idw_field is either 'WTCPUECubeRoot' or 'WTCPUE'
                        #idw_field = 'WTCPUE'
                        #out_idw = arcpy.sa.Idw(my_points, idw_field, "#", "1", "VARIABLE 15 200000", my_bounds)
                        # Execute IDW
                        #out_idw = arcpy.sa.Idw(my_points, 'WTCPUECubeRoot', "#", "1", "VARIABLE 15 200000", my_bounds)
                        #out_idw = arcpy.sa.Idw(my_points, 'WTCPUE', "#", "1", "VARIABLE 15 200000", my_bounds)

                        # idw_field is either 'WTCPUECubeRoot' or 'WTCPUE'
                        #idw_field = 'WTCPUE'
                        # out_idw = arcpy.sa.Idw(my_points, idw_field, "#", "1", "VARIABLE 15 200000", my_bounds)
                        # out_idw = arcpy.sa.Idw(my_points, idw_field, "#", "1", "VARIABLE 15 200000")

                        tmp_raster = os.path.join(ScratchGDB, "tmp_{0}".format(fish_year_raster))
                        #tmp_raster_power = os.path.join(ScratchGDB, "tmp_power_{0}".format(str(this_year)))
                        tmp_raster = os.path.join(ScratchFolder, f"tmp_{fish_year_raster}.tif")

                        if arcpy.Exists(tmp_raster):
                            arcpy.management.Delete(tmp_raster)


                        tmp_cellSize = arcpy.env.cellSize
                        arcpy.env.cellSize = cell_size
                        # https://www.esri.com/arcgis-blog/products/product/mapping/choosing-an-appropriate-cell-size-when-interpolating-raster-data/
                        # https://www.sciencedirect.com/science/article/pii/S0098300405002657?via%3Dihub
                        # Set local variables
                        inPointFeatures = my_points
                        zField = idw_field
                        outLayer = "outIDW"
                        outRaster = tmp_raster
                        # 100000m or 10km
                        cellSize = cell_size
                        power = 2
                        weightField = "YearWeights"

                        # Set variables for search neighborhood
                        majSemiaxis = 200000
                        minSemiaxis = 200000
                        angle = 0
                        maxNeighbors = 15
                        minNeighbors = 10
                        sectorType = "ONE_SECTOR"
                        searchNeighbourhood = arcpy.SearchNeighborhoodStandard(majSemiaxis, minSemiaxis,
                                                                               angle, maxNeighbors,
                                                                               minNeighbors, sectorType)

                        del majSemiaxis, minSemiaxis, angle, maxNeighbors, minNeighbors, sectorType
                        #del cell_size

                        # Check out the ArcGIS Geostatistical Analyst extension license
                        arcpy.CheckOutExtension("GeoStats")

                        # Execute IDW
                        arcpy.IDW_ga(inPointFeatures, zField, outLayer, outRaster, cellSize, power, searchNeighbourhood, weightField)

                        # Execute CrossValidation
                        #cvResult = arcpy.CrossValidation_ga(outLayer)
                        #print("Count = {}".format(str(cvResult.count)))
                        #print("Mean Error = {}".format(str(cvResult.meanError)))
                        #print("Root Mean Square Error = {}".format(str(cvResult.rootMeanSquare)))
                        #print("Average Standard = {}".format(str(cvResult.averageStandard)))
                        #print("Mean Standardized = {}".format(str(cvResult.meanStandardized)))
                        #print("Root Mean Square Error Standardized = {}".format(str(cvResult.rootMeanSquareStandardized)))
                        #del cvResult

                        del zField, cellSize, power, searchNeighbourhood, weightField

                        # environments = arcpy.ListEnvironments()
                        # Sort the environment names
                        # environments.sort()
                        # for environment in environments:
                        #     # Format and print each environment and its current setting.
                        #     # (The environments are accessed by key from arcpy.env.)
                        #     print("{0:<30}: {1}".format(environment, arcpy.env[environment]))
                        #     del environment
                        # del environments

                        #out_idw.save(tmp_raster)
                        #arcpy.management.Delete(out_idw)
                        #del out_idw
                        # Execute Power
                        if idw_field == 'WTCPUECubeRoot':
                            out_cube = arcpy.sa.Power(outRaster, 3)
                            #out_cube.save(tmp_raster_power)
                            out_cube.save(my_fish_raster)
                            #arcpy.management.Delete(out_cube)
                            del out_cube

                        arcpy.env.cellSize = tmp_cellSize
                        del tmp_cellSize

                        #arcpy.management.Delete(out_idw)
                        #del out_idw

                        arcpy.management.Delete(tmp_raster)
                        #arcpy.management.Delete(tmp_raster_power)
                        arcpy.management.Delete(outLayer)
                        del tmp_raster, outRaster, outLayer, inPointFeatures

                        # Add Metadata
                        addMetadata(my_fish_raster)

##                        # Add some metadata
##                        years_md = unique_years(region_mosaic)
##
##                        crf_md = md.Metadata(crf)
##                        crf_md.synchronize('ACCESSED', 1)
##                        crf_md.title = "{0} {1}".format(region.replace('-',' to '), DateCode)
##                        crf_md.tags = "{0}, {1} to {2}".format(geographic_regions[region_abb], min(years_md), max(years_md))
##                        crf_md.save()
##                        del crf_md, years_md


                        # Check In Spatial Extension
                        # arcpy.CheckInExtension("Spatial")

                        # Check In GeoStats Extension
                        arcpy.CheckInExtension("GeoStats")

                        # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
                        # The following inputs are layers or table views: "Aleutian_Islands"
                        arcpy.management.CalculateField(in_table=my_points, field="YearWeights", expression="None", expression_type="PYTHON", code_block="")

                    else:
                        msg =  ">->-> Raster File {}.tif for {} exists".format(fish_year_raster, this_fish)
                        logFile(log_file, msg)

                    del this_year, fish_year_raster, my_fish_raster

                del this_fish, my_fish_dir

            # Delete my points
            arcpy.management.Delete("my_points")

            # Clean up
            #del csv_file, my_points, my_shape, my_bounds, my_unique_fish
            del csv_file, my_points, my_unique_fish

            #Final benchmark for the region.
            msg = "ENDING REGION {} COMPLETED ON {}".format(region, strftime("%a %b %d %I:%M:%S %p", localtime()))
            logFile(log_file, msg)

            del region

            # Elapsed time
            end_time = time()
            elapse_time =  end_time - start_time
            msg = u"Elapsed Time {0} (H:M:S)\n".format(strftime("%H:%M:%S", gmtime(elapse_time)))
            logFile(log_file, msg)
            del msg, start_time, end_time, elapse_time

        #Clean up
        del table_name, region_shape, region_boundary, region_abb
        del region_georef, region_contours, region_name, log_file
        del fish_dir, my_unique_years, region_snap_raster, region_raster_mask
        del cell_size

        # Set the workspace to the tmp_workspace
        arcpy.env.workspace = tmp_workspace
        # Set the scratch workspace to the tmp_scratchWorkspace
        arcpy.env.scratchWorkspace = tmp_scratchWorkspace
        del tmp_workspace, tmp_scratchWorkspace

        localKeys =  [key for key in locals().keys() if "function" not in key]

        if localKeys:
            msg = "Local Keys in {0}(): {1}".format(function, u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys, function

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo

def generateTables():
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        # arcpy.AddMessage(function)

        # Set the workspace to the ProjectGDB
        tmp_workspace = arcpy.env.workspace
        arcpy.env.workspace = ProjectGDB

        # Set the scratch workspace to the ScratchGDB
        tmp_scratchWorkspace = arcpy.env.scratchWorkspace
        arcpy.env.scratchWorkspace = ScratchGDB

        # Start looping over the table_name array as we go region by region.
        for table_name in table_names:
            # Assigning variables from items in the chosen table list
            region_shape = table_name[0]
            region_boundary = table_name[1]
            region_abb = table_name[2]
            region = table_name[3]
            csv_file = table_name[4]
            region_georef = table_name[5]
            region_contours = table_name[6]

            # Make Geodatabase friendly name
            region_name = region.replace('(','').replace(')','').replace('-','_to_').replace(' ', '_').replace("'", "")

            # For benchmarking.
            log_file = os.path.join(LOG_DIRECTORY, region + ".log")
            # Start with removing the log file if it exists
            #if os.path.isfile(log_file):
            #    os.remove(log_file)

            # Set a start time so that we can see how log things take
            start_time = time()

            # Write a message to the log file
            msg = "STARTING REGION {0} ON {1}".format(region, strftime("%a %b %d %I:%M:%S %p", localtime()))
            logFile(log_file, msg)

            # Generate the shapefile to be used. We output this to the file system in the appropriate folder.
            msg = '> Generating {0} Table.'.format(region)
            logFile(log_file, msg)

            # out_table = os.path.join(DefaultGDB, csv_file)
            out_table = os.path.join(ProjectGDB, csv_file)
            #print(out_table)
            #if arcpy.Exists(out_table):
            #    arcpy.management.Delete(out_table)
            if not arcpy.Exists(out_table) or ReplaceTable:
                if ReplaceTable and arcpy.Exists(out_table):
                    msg = '>-> Removing the {0} CSV Table'.format(region)
                    logFile(log_file, msg)

                    # Geoprocessing tools return a result object of the derived
                    # output dataset.
                    #result = arcpy.management.Delete(out_table)
                    #arcpy.management.Delete(out_table)
                    tbs = arcpy.ListTables("{}*".format(csv_file))
                    # print (tbs)
                    for tb in tbs:
                        arcpy.management.Delete(tb)
                    del tb, tbs

                    # A print statement will display the string
                    # representation of the output.
                    #print(result)

                    # A result object can be indexed to get the output value.
                    # Note: a result object also has a getOutput() method that
                    # can be used for the same purpose.
                    #result_value = result[0]
                    #print(result_value)
                else:
                    msg = ">-> ReplaceTable set to True, but {0} CSV Table missing".format(region)
                    logFile(log_file, msg)

                msg = '>-> Processing the {0} CSV Table'.format(region)
                logFile(log_file, msg)

                input_csv_file = os.path.join(CSV_DIRECTORY, csv_file + ".csv")
                # https://pandas.pydata.org/pandas-docs/stable/getting_started/intro_tutorials/09_timeseries.html?highlight=datetime
                # https://www.tutorialsandyou.com/python/numpy-data-types-66.html
                #df = pd.read_csv('my_file.tsv', sep='\t', header=0)  ## not setting the index_col
                #df.set_index(['0'], inplace=True)

                df = pd.read_csv(input_csv_file,
                                 index_col = 0,
                                 encoding="utf-8",
                                 #encoding = "ISO-8859-1",
                                 #engine='python',
                                 delimiter = ',',
                                 #dtype = None,
                                 dtype = {
                                          "region" : str,
                                          "haulid" : str,
                                          "year" : 'uint16',
                                          # 'TrawlDate' : 'uint16',
                                          # 'SurfaceTemperature' : float,
                                          # 'BottomTemperature' : float,
                                          "spp" : str,
                                          "wtcpue" : float,
                                          "common" : str,
                                          "stratum" : str,
                                          "stratumarea" : float,
                                          "lat" : float,
                                          "lon" : float,
                                          "depth" : float,
                                          },
                                 )
                del input_csv_file

                # TODO: add new fields:
                # new fields:
                #   sea surface temperature (float), 'SurfaceTemperature'
                #   bottom temperature (float), 'BottomTemperature'
                #   Date of Trawl (Date) (Day-MO-Year of the trawl) 'TrawlDate'

                msg = '>->-> Defining the column name.'
                logFile(log_file, msg)

                # The original column names from the CSV files are not very
                # reader friendly, so we are making some changes here
                #df.columns = [u'OARegion', u'HUALID', u'Year', u'Species', u'WTCPUE', u'CommonName', u'Stratum', u'StratumArea', u'Latitude', u'Longitude', u'Depth']
                df.columns = ['OARegion', 'HUALID', 'Year', 'Species', 'WTCPUE', 'CommonName', 'Stratum', 'StratumArea', 'Latitude', 'Longitude', 'Depth']

                # Test if we are filtering on species. If so, a new species list is
                # created with the selected species remaining in the list
                if FilterSpecies and ReplaceTable:
                    msg = '>->-> Filtering table on selected species for {0} Table'.format(region)
                    logFile(log_file, msg)
                    # Filter data frame
                    df = df.loc[df['Species'].isin(selected_species.keys())]
                else:
                    msg = '>->-> No species filtering of selected species for {0} Table'.format(region)
                    logFile(log_file, msg)

                ###-->> Species and CommonName
                msg = '>->->  Setting Nulls in Species and CommonName to empty strings.'
                logFile(log_file, msg)
                # Replace NaN with an empty string. When pandas reads a cell
                # with missing data, it asigns that cell with a Null or nan
                # value. So, we are changing that value to an empty string of ''.
                # Seems to be realivent for Species and CommonName only
                df.Species    = df.Species.fillna('')
                df.CommonName = df.CommonName.fillna('')
                df.Species    = df.Species.replace('Na', '')
                df.CommonName = df.CommonName.replace('Na', '')
                #msg = '>->->  Droping row where Species have an empty string.'
                #logFile(log_file, msg)
                # Drop rows based on a condition. Rows without a species name are not of use
                #df = df[df.Species != '']

                #-->> SpeciesCommonName
                msg = '>->->  Adding SpeciesCommonName and setting it to "Species (CommonName)".'
                logFile(log_file, msg)
                # Insert column
                df.insert(df.columns.get_loc('CommonName')+1, 'SpeciesCommonName', df['Species'] + ' (' + df['CommonName'] + ')')

                #-->> CommonNameSpecies
                msg = '>->->  Adding CommonNameSpecies and setting it to "CommonName (Species)".'
                logFile(log_file, msg)
                # Insert column
                df.insert(df.columns.get_loc('SpeciesCommonName')+1, 'CommonNameSpecies', df['CommonName'] + ' (' + df['Species'] + ')')

                #-->> CoreSpecies
                msg = '>->->  Adding CoreSpecies and setting it to "No".'
                logFile(log_file, msg)
                # Insert column
                df.insert(df.columns.get_loc('CommonNameSpecies')+1, 'CoreSpecies', "No")

                # ###-->> Depth
                # msg = '>->->  Setting the Depth to float16.'
                # logFile(log_file, msg)
                # # The Depth column in the CSV files contain a mix of integer and
                # # double. This converts all to float values to be consistant
                # #df.Depth = df.Depth.astype(np.float16) # or np.float32 or np.float64
                # df.Depth = df.Depth.astype(float)

                ###-->> WTCPUE
                msg = '>->->  Replacing Infinity values with Nulls.'
                logFile(log_file, msg)
                # Replace Inf with Nulls
                # For some cell values in the 'WTCPUE' column, there is an Inf
                # value representing an infinit
                df.replace([np.inf, -np.inf], np.nan, inplace=True)

                ###-->> WTCPUECubeRoot
                msg = '>->->  Adding the WTCPUECubeRoot column and calculating values.'
                logFile(log_file, msg)
                # Insert a column to the right of a column and then do a calculation
                df.insert(df.columns.get_loc('WTCPUE')+1, 'WTCPUECubeRoot', df['WTCPUE'].pow((1.0/3.0)))

                msg = '>-> Creating the {0} Geodatabase Table'.format(region)
                logFile(log_file, msg)

                # ###--->>> Numpy Datatypes
                # https://pro.arcgis.com/en/pro-app/latest/arcpy/get-started/working-with-numpy-in-arcgis.htm

                #OARegion_Max: 20
                #HUALID_Max: 15
                #Species_Max: 23
                #CommonName_Max: 18
                #Stratum_Max: 14

##                # This works in Python 3.x unicode issue
##                # names = df.dtypes.index.tolist()
##                # Consider using import platform and platform.python_version()
##                # to get Python version number i.e. '2.7.18'
##                # This works for Python 2.7.x non-unicode issue
##                names = [str(n) for n in df.dtypes.index.tolist()]
##                names = ', '.join(names)
##                formats = '<i4, S50, S20, S50, S50, <i4, <f8, <f8, S25, <f8, <f8, <f8, <f8'
##                # This step takes the pandas dataframe and converts it to a numpy
##                # array so that the array can be converted to a ArcGIS table
##                # CSVFILEID, OARegion, HUALID, Year, Species, WTCPUE, WTCPUECubeRoot, CommonName, Stratum, StratumArea, Latitude, Longitude, Depth
##                CSVFILEID, Integer, 4 <i4
##                Region, String, 20 S50 ##
##                HUALID, String, 14 S20
##                Species, String, 23 S50
##                CommonName, String, 15 S50
##                Year, Integer, 4 <i4
##                WTCPUE, Double, 8 <f8
##                WTCPUECubeRoot, Double, 8 <f8
##                Stratum, String, 8 S25
##                StratumArea, Double, 8 <f8
##                Depth, Double, 8 <f8
##                Latitude, Double, 8 <f8
##                Longitude, Double, 8 <f8
##                '<i4, S50,  S20, S50, S50, <i4, <f8, <f8, S25, <f8, <f8, <f8, <f8'
##
### #                'S10,S8,S4,<f8,<f8,S5,S5,<i4,S5'
##
##                array = np.array(np.rec.fromrecords(df.values, names = names, formats = formats))
##                #array = np.array(np.rec.fromrecords(recs, ,
##                del formats
##
##                array.dtype.names = tuple(names)

                #print('DataFrame\n----------\n', df.head(10))
                #print('\nDataFrame datatypes :\n', df.dtypes)
                #columns = [str(c) for c in df.dtypes.index.tolist()]
                column_names = list(df.columns)
                #print(column_names)
                # https://www.tutorialsandyou.com/python/numpy-data-types-66.html
                # column_formats = [u'S50', u'S20', 'u2', u'S50', 'f4', 'f4', u'S50', u'S100', u'S25', 'f4', 'f4', 'f4', 'f4']
                #column_formats = ['S50', 'S20', '<i4', 'S50', '<f8', '<f8', 'S50', 'S100', 'S100', 'S5', 'S25', '<f8', '<f8', '<f8', '<f8']
                column_formats = ['S50', 'S20', '<i4', 'S50', '<f8', '<f8', 'U50', 'U100', 'U100', 'S5', 'S25', '<f8', '<f8', '<f8', '<f8']
                dtypes = list(zip(column_names, column_formats))

                df['CommonName'] = df['CommonName'].astype('unicode')

                #print(df)
                try:
                    array = np.array(np.rec.fromrecords(df.values), dtype = dtypes)
                except:
                    import sys, traceback
                    # Get the traceback object
                    tb = sys.exc_info()[2]
                    #tb = sys.exc_info()
                    tbinfo = traceback.format_tb(tb)[0]
                    # Concatenate information together concerning the error into a message string
                    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
                    print(pymsg)
                    del pymsg, tb, tbinfo

                del df, column_names, column_formats, dtypes

                # Temporary table
                tmp_table = out_table + '_tmp'
                if arcpy.Exists(tmp_table):
                    arcpy.management.Delete(tmp_table)

                try:
                    arcpy.da.NumPyArrayToTable(array, tmp_table)
                    del array
                    #print(column_names)
                    #arcpy.da.NumPyArrayToTable(records, tmp_table, column_names)

                except IOError:
                    print("Something went wrong: IOError")
                except:
                    import sys, traceback
                    # Get the traceback object
                    tb = sys.exc_info()[2]
                    #tb = sys.exc_info()
                    tbinfo = traceback.format_tb(tb)[0]
                    # Concatenate information together concerning the error into a message string
                    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
                    print(pymsg)
                    del pymsg, tb, tbinfo

                #del array

                if region_abb in ['WC_ANN', 'WC_TRI',]:
                    msg = '>-> Updating the Region Field for {0}'.format(region)
                    logFile(log_file, msg)

                    arcpy.management.CalculateField(in_table=tmp_table, field="OARegion", expression="'{0}'".format(region), expression_type="PYTHON", code_block="")


                msg = '>-> Adding the StdTime column to the {0} Table and calculating the datetime value'.format(region)
                logFile(log_file, msg)

            # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
            # The following inputs are layers or table views: "NEUS_S_Layer"
            #
            # https://community.esri.com/t5/arcgis-online-questions/arcgis-online-utc-time-zone-converting-to-local-timezone/m-p/188515
            # https://desktop.arcgis.com/en/arcmap/latest/tools/data-management-toolbox/convert-timezone.htm
            # https://support.esri.com/en/technical-article/000015224
            # https://community.esri.com/t5/arcgis-online-blog/mastering-the-space-time-continuum-2-0-more-about-date-fields/ba-p/891203?searchId=e9792f70-29cb-43d4-a2f5-289e42701d7a&searchIndex=4&sr=search
            # https://community.esri.com/t5/arcgis-online-blog/golden-rules-to-mastering-space-and-time-on-the-web/ba-p/891069?searchId=2e78f04a-625c-4456-9dd7-27362e4136c9&searchIndex=0&sr=search
            # https://stackoverflow.com/questions/36623786/in-python-how-do-i-create-a-timezone-aware-datetime-from-a-date-and-time
            # http://pytz.sourceforge.net/

                arcpy.management.AddField(in_table=tmp_table, field_name="StdTime", field_type="DATE", field_precision="", field_scale="", field_length="", field_alias="StdTime", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")

                # The following calculates the time stamp for the feature class
                codeBlock = """def getDate(region, year):
                                  from datetime import datetime
                                  import pytz
                                  regionDateDict = {# Region : Month, Day, Hour, Minute, Second, Time Zone
                                                    'Aleutian Islands'   : [1, 1, 0, 0, 0, 'US/Alaska'],
                                                    'Eastern Bering Sea' : [1, 1, 0, 0, 0, 'US/Alaska'],
                                                    'Gulf of Alaska' : [1, 1, 0, 0, 0, 'US/Alaska'],
                                                    'Gulf of Mexico' : [1, 1, 0, 0, 0, 'US/Central'],
                                                    'Hawaii Islands' : [1, 1, 0, 0, 0, 'US/Hawaii'],
                                                    "Hawai'i Islands" : [1, 1, 0, 0, 0, 'US/Hawaii'],
                                                    'Hawaii' : [1, 1, 0, 0, 0, 'US/Hawaii'],
                                                    'Northeast US Fall' : [1, 1, 0, 0, 0, 'US/Eastern'],
                                                    'Northeast US Spring' : [1, 1, 0, 0, 0, 'US/Eastern'],
                                                    'Southeast US Spring' : [1, 1, 0, 0, 0, 'US/Eastern'],
                                                    'Southeast US Summer' : [1, 1, 0, 0, 0, 'US/Eastern'],
                                                    'Southeast US Fall' : [1, 1, 0, 0, 0, 'US/Eastern'],
                                                    'West Coast Annual' : [1, 1, 0, 0, 0, 'US/Pacific'],
                                                    'West Coast Triennial' : [1, 1, 0, 0, 0, 'US/Pacific'],
                                                    'West Coast Annual 2003-Present' : [1, 1, 0, 0, 0, 'US/Pacific'],
                                                    'West Coast Triennial 1977-2004' : [1, 1, 0, 0, 0, 'US/Pacific'],
                                                    'West Coast Annual (2003-Present)' : [1, 1, 0, 0, 0, 'US/Pacific'],
                                                    'West Coast Triennial (1977-2004)' : [1, 1, 0, 0, 0, 'US/Pacific'],}
                                  month, day, hour, min, sec, timeZone = regionDateDict[region]
                                  fmt = "%m/%d/%Y %H:%M:%S"
                                  local = pytz.timezone(timeZone)
                                  naive = datetime.strptime("{0}/{1}/{2} {3}:{4}:{5}".format(month, day, year, hour, min, sec), fmt)
                                  #local_dt = local.localize(naive, is_dst=True)
                                  local_dt = local.localize(naive, is_dst=False)
                                  utc_dt = local_dt.astimezone(pytz.utc)
                                  #return utc_dt.strftime(fmt)
                                  return utc_dt"""

                arcpy.management.CalculateField(tmp_table, "StdTime", expression="getDate( !OARegion!, !Year! )", expression_type="PYTHON", code_block=codeBlock)
                del codeBlock

                # new_field_order = ["field2", "field3", "field1"]
                # reorder_fields(in_fc, out_fc, new_field_order)

                # A new order of fields that put like things together
                # new_field_order = ['OBJECTID', 'CSVFILEID', 'OARegion', 'HUALID', 'Species', 'CommonName', 'Year', 'WTCPUE', 'WTCPUECubeRoot', 'Stratum', 'StratumArea', 'Depth', 'Latitude', 'Longitude', 'StdTime']
                # new_field_order = ['OBJECTID', 'CSVFILEID', 'OARegion', 'HUALID', 'Species', 'CommonName', 'SpeciesCommonName', 'CommonNameSpecies', 'Year', 'WTCPUE', 'WTCPUECubeRoot', 'Stratum', 'StratumArea', 'Depth', 'Latitude', 'Longitude', 'StdTime']
                # Drops'CSVFILEID',
                new_field_order = ['OBJECTID', 'OARegion', 'HUALID', 'Species', 'CommonName', 'SpeciesCommonName', 'CommonNameSpecies', 'CoreSpecies', 'Year', 'StdTime', 'WTCPUE', 'WTCPUECubeRoot', 'Stratum', 'StratumArea', 'Depth', 'Latitude', 'Longitude',]


                # Sends the input feature class to the field reorder function
                msg = '>-> Reordering the fields in the {0} Table'.format(region)
                logFile(log_file, msg)
                #
                reorder_fields(tmp_table, out_table, new_field_order)

                # Cleanup
                del new_field_order

                # Remove the temporary feature class
                arcpy.management.Delete(tmp_table)
                del tmp_table

                print("Table: {0}".format(csv_file))
                all_years = unique_values(csv_file, "Year")
                #print(all_years)
                min_year = min(all_years)
                max_year = max(all_years)
                print("\t Years: {0}".format(', '.join([str(y) for y in all_years])))
                print("\t Min Year: {0}".format(min_year))
                print("\t Max Year: {0}".format(max_year))

                #species = unique_values(csv_file, "Species")

                species_lyr = arcpy.management.MakeTableView(csv_file, '{0} Table View'.format(csv_file))

                species = unique_values(species_lyr, "Species")

                for specie in species:
                    print("\t Species: {0}".format(specie))
                    #specie_lyr = arcpy.management.MakeTableView(csv_file, '{0} Table View'.format(csv_file), "Species = '{0}'".format(specie))

                    # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
                    # The following inputs are layers or table views: "ai_csv"
                    arcpy.management.SelectLayerByAttribute(in_layer_or_view=species_lyr, selection_type="NEW_SELECTION", where_clause="Species = '{0}' AND WTCPUE > 0.0".format(specie))

                    all_specie_years = unique_values(species_lyr, "Year")
                    #print("\t\t Years: {0}".format(', '.join([str(y) for y in all_specie_years])))

                    arcpy.management.SelectLayerByAttribute(in_layer_or_view=species_lyr, selection_type="NEW_SELECTION", where_clause="Species = '{0}'".format(specie))

                    if all_years == all_specie_years:
                        print("\t\t Match for: {0}".format(specie))
                        arcpy.management.CalculateField(in_table=species_lyr, field="CoreSpecies", expression="'Yes'", expression_type="PYTHON", code_block="")
                    else:
                        print("\t\t @@@@ No Match for: {0} @@@@".format(specie))
                        arcpy.management.CalculateField(in_table=species_lyr, field="CoreSpecies", expression="'No'", expression_type="PYTHON", code_block="")

                    arcpy.management.SelectLayerByAttribute(species_lyr, "CLEAR_SELECTION")
                    #arcpy.management.Delete("Species = '{0}'".format(specie))
                    #del specie_lyr
                    del specie, all_specie_years

                arcpy.management.Delete('{0} Table View'.format(csv_file))
                del species_lyr

                del all_years, min_year, max_year, species

                # field_alias = {'CSVFILEID' : '',
                #                'OARegion' : '',
                #                'HUALID' : '',
                #                'Species' : '',
                #                'CommonName' : '',
                #                'Year' : '',
                #                'WTCPUE' : '',
                #                'WTCPUECubeRoot' : '',
                #                'Stratum' : '',
                #                'StratumArea' : '',
                #                'Depth' : '',
                #                'Latitude' : '',
                #                'Longitude' : ''
                #                'StdTime' : ''}

                msg = '>-> Updating the field alias in the {0} Table'.format(region)
                logFile(log_file, msg)

                fields = arcpy.ListFields(out_table)
                for field in fields:
                    if '_' in field.aliasName:
                        arcpy.management.AlterField(out_table, field.name, new_field_alias = field.aliasName.replace('_', ' '))
                del field, fields

                addMetadata(out_table)

                msg = '> Generating {0} Table complete ON {1}'.format(region, strftime("%a %b %d %I:%M:%S %p", localtime()))
                logFile(log_file, msg)

            elif arcpy.Exists(out_table):
                msg = '>-> {0} CSV Table Exists'.format(region)
                logFile(log_file, msg)
            else:
                msg = '>-> Nothing to do {0} CSV Table'.format(region)
                logFile(log_file, msg)

            # Cleanup

            del out_table

            #Final benchmark for the region.
            msg = "ENDING REGION {} COMPLETED ON {}".format(region, strftime("%a %b %d %I:%M:%S %p", localtime()))
            logFile(log_file, msg)

            # Elapsed time
            end_time = time()
            elapse_time =  end_time - start_time
            msg = u"Elapsed Time {0} (H:M:S)\n".format(strftime("%H:%M:%S", gmtime(elapse_time)))
            logFile(log_file, msg)

        # Clean up
        del msg, table_name, region_abb, region, csv_file, region_georef
        del log_file, start_time, end_time, elapse_time
        del region_shape, region_boundary, region_contours, region_name

        # Set the workspace to the tmp_workspace
        arcpy.env.workspace = tmp_workspace
        # Set the scratch workspace to the tmp_scratchWorkspace
        arcpy.env.scratchWorkspace = tmp_scratchWorkspace
        del tmp_workspace, tmp_scratchWorkspace

        localKeys =  [key for key in locals().keys() if "function" not in key]

        if localKeys:
            msg = "Local Keys in {0}(): {1}".format(function, u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys, function

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo

def getRowColumnCount(raster):
    rowCount    = arcpy.management.GetRasterProperties(raster, "ROWCOUNT" ).getOutput(0)
    columnCount = arcpy.management.GetRasterProperties(raster, "COLUMNCOUNT" ).getOutput(0)
    CELLSIZEX   = arcpy.management.GetRasterProperties(raster, "CELLSIZEX" ).getOutput(0)
    CELLSIZEY   = arcpy.management.GetRasterProperties(raster, "CELLSIZEY" ).getOutput(0)
    TOP         = arcpy.management.GetRasterProperties(raster, "TOP" ).getOutput(0)
    LEFT        = arcpy.management.GetRasterProperties(raster, "LEFT" ).getOutput(0)
    RIGHT       = arcpy.management.GetRasterProperties(raster, "RIGHT" ).getOutput(0)
    BOTTOM      = arcpy.management.GetRasterProperties(raster, "BOTTOM" ).getOutput(0)

    print("\t {0}".format(raster))
    print("\t\t Rows: {0}, Columns: {1}".format(rowCount, columnCount))
    print("\t\t Cell Size X: {0}, Cell Size Y: {1}".format(CELLSIZEX, CELLSIZEY))
    print("\t\t X Min: {0}, Y Min: {1}, X Max: {2}, Y Max: {3}".format(LEFT, BOTTOM, TOP, RIGHT))
    del raster, rowCount, columnCount, CELLSIZEX, CELLSIZEY, LEFT, BOTTOM, TOP, RIGHT

def getRowColumnCountReport():
    try:
        # Start looping over the table_name array as we go region by region.
        for table_name in table_names:
            region_abb = table_name[2]
            region = table_name[3]

            wildcard = "{0}*".format(region_abb)
            rasters = arcpy.ListRasters(wildcard)
            rasters.append(', '.join(arcpy.ListDatasets(wildcard, "Mosaics")))
            #mosaics = arcpy.ListDatasets(wildcard, "Mosaics")
            #print(rasters)
            #print(mosaics)
            print(region)
            for raster in rasters:
                getRowColumnCount(raster)
                del raster

            del table_name, region_abb, region, rasters, wildcard

        localKeys =  [key for key in locals().keys()]

        if localKeys:
            msg = "Local Keys in getRowColumnCountReport(): {0}".format(u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo


def getDepthSummaryStatisticsReport():
    try:
        # Start looping over the table_name array as we go region by region.
        for table_name in table_names:
            region_abb = table_name[2]
            region = table_name[3]
            csv_file = table_name[4]

            # Make Geodatabase friendly name
            region_name = region.replace('(','').replace(')','').replace('-','_to_').replace(' ', '_').replace("'", "")

            del table_name, region_abb, region

        localKeys =  [key for key in locals().keys()]

        if localKeys:
            msg = "Local Keys in getDepthSummaryStatisticsReport(): {0}".format(u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo

def importEPU():
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        #arcpy.AddMessage(function)

        # Set a start time so that we can see how log things take
        start_time = time()

        arcpy.env.overwriteOutput = True
        arcpy.env.scratchWorkspace = ScratchGDB
        arcpy.env.workspace = ProjectGDB

        # Write a message to the log file
        msg = "#-> STARTING {0} ON {1}".format(function, strftime("%a %b %d %I:%M:%S %p", localtime()))
        print(msg); del msg

        epu_shape_path = os.path.join(MAP_DIRECTORY, 'EPU_shape', 'EPU_NOESTUARIES')

        arcpy.management.CopyFeatures(epu_shape_path, 'EPU_NOESTUARIES')

        #arcpy.management.DeleteField('EPU_NOESTUARIES', )

        # Cleanup
        del epu_shape_path

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = u"#-> Elapsed Time for {0} {1} (H:M:S)\n".format(function, strftime("%H:%M:%S", gmtime(elapse_time)))
        print(msg)
        del msg, start_time, end_time, elapse_time

        localKeys =  [key for key in locals().keys() if "function" not in key]

        if localKeys:
            msg = "Local Keys in {0}(): {1}".format(function, u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys, function

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo

def main():
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        arcpy.AddMessage(function)

        localKeys =  [key for key in locals().keys() if "function" not in key]

        if localKeys:
            msg = "Local Keys in {0}(): {1}".format(function, u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys, function

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        msgs = "Arcpy Errors:\n" + arcpy.GetMessages(2) + "\n"
        arcpy.AddError(pymsg)
        arcpy.AddError(msgs)
        arcpy.AddMessage(pymsg)
        arcpy.AddMessage(msgs)
        del tb, tbinfo, pymsg, msgs

def populateRegionSpeciesYearImageName():
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        #arcpy.AddMessage(function)

        # Set the workspace to the ProjectGDB
        tmp_workspace = arcpy.env.workspace
        arcpy.env.workspace = ProjectGDB

        # Set the scratch workspace to the ScratchGDB
        tmp_scratchWorkspace = arcpy.env.scratchWorkspace
        arcpy.env.scratchWorkspace = ScratchGDB

        # From: Data Dictionary
        # OARegion    (e.g. West Coast Triennial)
        # Species    Some scientific name
        # Common_Name    Common Name of the species
        # SpeciesCommonName    Centropristis striata (black sea bass)
        # DisMapRegionCode    GOM
        # DisMapSeasonCode    NULL

        arcpy.env.workspace = ProjectGDB
        region_species_image_name_template = os.path.join(ProjectGDB, 'RegionSpeciesYearImageName_Template')
        region_species_image_name = os.path.join(ProjectGDB, 'RegionSpeciesYearImageName')

        if PopulateRegionSpeciesYearImageName:
            arcpy.management.Delete(region_species_image_name)
            arcpy.management.CreateTable(ProjectGDB, 'RegionSpeciesYearImageName', region_species_image_name_template)

        # This gets a list of fields in the table
        fields = [f.name for f in arcpy.ListFields(region_species_image_name) if f.name != 'OBJECTID']
        msg = "\t {0}\n\t Fields: {1}\n".format( region_species_image_name, ', '.join(fields))
        print(msg)
        del msg
        del fields

        for table_name in table_names:
            # Assigning variables from items in the chosen table list
            #region_shape = table_name[0]
            #region_boundary = table_name[1]
            region_abb = table_name[2]
            region = table_name[3]
            csv_file = table_name[4]
            #region_georef = table_name[5]
            #region_contours = table_name[6]

            # Get a record count to see if data is present; we don't want to add data
            tb_count = int(arcpy.management.GetCount(csv_file)[0])
            msg = '\t {} has {} records\n'.format(csv_file, tb_count)
            print(msg)
            del msg

            #region_abb = tb[:tb.find('_csv')].upper()

            # Execute Statistics to get unique set of records
            tb_tmp = csv_file+"_tmp"
            statsFields = [["Species", "COUNT"]]
            caseFields = ["OARegion", "Species", "CommonName", "SpeciesCommonName", "CoreSpecies", "Year", "StdTime"]
            stat_tb = arcpy.Statistics_analysis(csv_file, tb_tmp, statsFields, caseFields)
            del statsFields, caseFields

            # Get a record count to see if data is present; we don't want to add data
            stat_tb_count = int(arcpy.management.GetCount(stat_tb)[0])
            msg = '\t\t {} has {} records\n'.format(tb_tmp, stat_tb_count)
            print(msg)
            del msg

            msg = '\t\t Add Variable Field to {} RegionSpeciesYearImageName table\n'.format(tb_tmp)
            print(msg)
            del msg

            arcpy.management.AddField(in_table=tb_tmp, field_name="Variable", field_type="TEXT", field_precision="", field_scale="", field_length="50", field_alias="Variable", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")

            msg = '\t\t Calculate Variable Field to {} RegionSpeciesYearImageName table\n'.format(tb_tmp)
            print(msg)
            del msg

            #arcpy.management.CalculateField(in_table=tb_tmp, field="Variable", expression='!Species!', expression_type="PYTHON", code_block="")
            arcpy.management.CalculateField(in_table=tb_tmp, field="Variable", expression='" ".join(!Species!.replace(".","").replace("-"," ").replace("(","").replace(")","").replace("/","and").split())', expression_type="PYTHON", code_block="")

            msg = '\t\t Add Dimensions Field to {} RegionSpeciesYearImageName table\n'.format(tb_tmp)
            print(msg)
            del msg

            arcpy.management.AddField(in_table=tb_tmp, field_name="Dimensions", field_type="TEXT", field_precision="", field_scale="", field_length="10", field_alias="Dimensions", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")

            msg = '\t\t Calculate Dimensions Field to {} RegionSpeciesYearImageName table\n'.format(tb_tmp)
            print(msg)
            del msg

            arcpy.management.CalculateField(in_table=tb_tmp, field="Dimensions", expression="'StdTime'", expression_type="PYTHON", code_block="")

            msg = '\t\t Add ImageName Field to {} RegionSpeciesYearImageName table\n'.format(tb_tmp)
            print(msg)
            del msg

            arcpy.management.AddField(in_table=tb_tmp, field_name="ImageName", field_type="TEXT", field_precision="", field_scale="", field_length="100", field_alias="Image Name", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")

            msg = '\t\t Calculate ImageName Field to {} RegionSpeciesYearImageName table\n'.format(tb_tmp)
            print(msg)
            del msg

            codeBlock = """def imageName(region, species, year):
                               return "{0}_{1}_{2}".format(region, species.replace(".","").replace("-"," ").replace("(","").replace(")","").replace("/","and").replace(" ","_"), str(year))
                         """

            arcpy.management.CalculateField(in_table=tb_tmp, field="ImageName", expression='imageName("{0}", !Species!, !Year!)'.format(region_abb), expression_type="PYTHON", code_block=codeBlock)
            del codeBlock

            #msg = '\t\t Joining {} to DataSeries table\n'.format(tb_tmp)
            #print(msg)
            #del msg

            # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
            # The following inputs are layers or table views: "ebs_csv_tmp", "DataSeries"
            #arcpy.management.JoinField(in_data = tb_tmp, in_field = "OARegion", join_table = "DataSeries", join_field = "OARegion", fields = "OARegion;DisMapRegionCode;DisMapSeasonCode")
            #msg = arcpy.GetMessages()
            #print("\t\t {0}\n".format(msg.replace('\n', '\n\t\t ')))
            #del msg

            msg = '\t\t Append {} to RegionSpeciesYearImageName table\n'.format(tb_tmp)
            print(msg); del msg

            #
            arcpy.management.Append(inputs = tb_tmp, target="RegionSpeciesYearImageName", schema_type="NO_TEST", field_mapping="", subtype="")
            msg = arcpy.GetMessages()
            print("\t\t {0}\n".format(msg.replace('\n', '\n\t\t '))); del msg

            # Remove temporary table
            arcpy.management.Delete(stat_tb)

            msg = arcpy.GetMessages()
            print("\t\t {0}\n".format(msg.replace('\n', '\n\t\t '))); del msg

            del tb_tmp, stat_tb, tb_count, stat_tb_count
        #

        #
        addMetadata(region_species_image_name)

        #
        msg = '\t\t arcpy.analysis.Statistics RegionSpeciesYearImageName table\n'
        print(msg);del msg

        arcpy.analysis.Statistics(in_table="RegionSpeciesYearImageName", out_table="_Species", statistics_fields="Species COUNT", case_field="Species")
        msg = arcpy.GetMessages()
        print("\t\t {0}\n".format(msg.replace('\n', '\n\t\t '))); del msg

        arcpy.management.DeleteField(in_table="_Species", drop_field="FREQUENCY;COUNT_Species")

        arcpy.TableToTable_conversion(in_rows="_Species", out_path=BASE_DIRECTORY, out_name=f"Species{SoftwareEnvironmentLevel}.csv", where_clause="", field_mapping='', config_keyword="")

        msg = '\t\t arcpy.analysis.Statistics RegionSpeciesYearImageName table\n'
        print(msg);del msg

        arcpy.analysis.Statistics(in_table="RegionSpeciesYearImageName", out_table="_CoreSpecies", statistics_fields="Species COUNT", case_field="OARegion;Species;CoreSpecies")
        msg = arcpy.GetMessages()
        print("\t\t {0}\n".format(msg.replace('\n', '\n\t\t '))); del msg

        arcpy.management.DeleteField(in_table="_CoreSpecies", drop_field="FREQUENCY;COUNT_Species")

        arcpy.TableToTable_conversion(in_rows="_CoreSpecies", out_path=BASE_DIRECTORY, out_name=f"CoreSpecies{SoftwareEnvironmentLevel}.csv", where_clause="", field_mapping='', config_keyword="")

        del region_species_image_name, region_species_image_name_template
        del region_abb, table_name, region, csv_file

        # Set the workspace to the tmp_workspace
        arcpy.env.workspace = tmp_workspace
        # Set the scratch workspace to the tmp_scratchWorkspace
        arcpy.env.scratchWorkspace = tmp_scratchWorkspace
        del tmp_workspace, tmp_scratchWorkspace

        localKeys =  [key for key in locals().keys() if "function" not in key]

        if localKeys:
            msg = "Local Keys in {0}(): {1}".format(function, u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys, function

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo

def projectSetup():
    import sys, platform
    try:
        function = function_name()
        # Get ArcGIS Product Information
        # print(arcpy.GetInstallInfo()['Version'])
        # ## Use the dictionary iteritems to iterate through
        # ##   the key/value pairs from GetInstallInfo
        # #d = arcpy.GetInstallInfo()
        # #for key, value in list(d.items()):
        # #    # Print a formatted string of the install key and its value
        # #    #
        # #    print("{:<13} : {}".format(key, value))

        ProductName = arcpy.GetInstallInfo()['ProductName']
        ProductVersion = arcpy.GetInstallInfo()['Version']
        # Now we need to test what license level
        if ProductName == "ArcGISPro":
            # Get the Product License Level
            ProductLicenseLevel = arcpy.GetInstallInfo()['LicenseLevel']
            #if not ProductLicenseLevel in ['Advanced', '']
            #if ProductLicenseLevel in []

        elif ProductName == "Desktop":
            # Testing Product License Level
            #print("Advanced: {}".format(arcpy.CheckProduct("arcinfo")))
            #print("Standard: {}".format(arcpy.CheckProduct("arceditor")))

            if arcpy.CheckProduct("arcinfo") == "Available":
                ProductLicenseLevel = "Advanced"
            elif arcpy.CheckProduct("arceditor") == "Available":
                ProductLicenseLevel = "Standard"
            elif arcpy.CheckProduct("arcview") == "Available":
                ProductLicenseLevel = "Basic"
            else:
                pass
        else:
            #print("")
            pass

        # This prints out a list of items related to this project.
        print("Project related items")
        # Print out the variables that are set
        print('\t Project Folder:       {0}'.format(BASE_DIRECTORY))
        print('\t Fish Data Folder:     {0}'.format(CSV_DIRECTORY))
        print('\t Map Folder:           {0}'.format(MAP_DIRECTORY))
        print('\t Analysis Folder:      {0}'.format(ANALYSIS_DIRECTORY))
        #print('\t Picture Folder:       {0}'.format(PICTURE_FOLDER))
        print('\t Mosaic Folder:        {0}'.format(MOSAIC_DIRECTORY))
        print('\t Log Folder:           {0}'.format(LOG_DIRECTORY))
        print('\t ArcGIS Pro Project:   {0}'.format(ProjectGIS))
        print('\t Python Executing:     {0}'.format(sys.executable))
        print('\t Python Version:       {0}'.format(sys.version))
        print('\t Python Version:       {0}'.format(platform.python_version()))
        print('\t Platform:             {0} {1} ( Linux and Mac OSX not tested. )'.format(platform.system(), platform.release()))
        print('\t ArcGIS Product:       {0} {1}'.format(ProductName, ProductVersion))
        print('\t ArcGIS License Level: {0}'.format(ProductLicenseLevel))

        # If the Base_Folder is missing, create the folder
        if not os.path.exists( BASE_DIRECTORY ) and not os.path.isdir( BASE_DIRECTORY ):
            print("The Base Folder is the output location for project folders")
            print("\t missing and will be created")
            os.makedirs( BASE_DIRECTORY )

        # If the ProjectGDB is missing, create the folder
        if not arcpy.Exists(ProjectGDB):
            print("The ProjectGDB is the output location for data")
            print("\t missing and will be created")
            arcpy.management.CreateFileGDB(BASE_DIRECTORY, ProjectName + " " + SoftwareEnvironmentLevel)

        # If the BathymetryGDB is missing, create the folder
        if not arcpy.Exists(BathymetryGDB):
            print("The BathymetryGDB is the output location for data")
            print("\t missing and will be created")
            arcpy.management.CreateFileGDB(BASE_DIRECTORY, "Bathymetry")

        # If the ScratchFolder is missing, create the folder
        if not os.path.exists( ScratchFolder ) and not os.path.isdir( ScratchFolder ):
            print("The ScratchFolder is the output location for scratch data")
            print("\t missing and will be created")
            os.makedirs( ScratchFolder )
            #if not arcpy.Exists(ScratchGDB):
            #    arcpy.management.CreateFileGDB(ScratchFolder, "sratch")

            arcpy.env.scratchWorkspace = ScratchGDB
            msg = arcpy.env.scratchWorkspace
            arcpy.AddMessage(msg)
            # If the scratch workspace is missing, referencing the env will create the workspace
            msg = arcpy.env.scratchGDB
            arcpy.AddMessage(msg)
            msg = arcpy.env.scratchFolder
            arcpy.AddMessage(msg)
            del msg

        # Test if a folder exists, if not then create what is missing
        # If the Analysis_Folder is missing, create the folder
        if not os.path.exists( ANALYSIS_DIRECTORY ) and not os.path.isdir( ANALYSIS_DIRECTORY ):
            print("The Analysis Folder is the output location for raster images")
            print("\t missing and will be created")
            os.makedirs( ANALYSIS_DIRECTORY )

        # Test if a folder exists, if not then create what is missing
        # If the Fish Data is missing, create the folder
        if not os.path.exists( CSV_DIRECTORY ) and not os.path.isdir( CSV_DIRECTORY ):
            print("The Fish Data Folder is missing and will be created")
            print("\t This folder contains the CSV files needed to run this script")
            print("\t The R script in the Project folder need to be executed to")
            print("\t the CSV files.")
            os.makedirs( CSV_DIRECTORY )

        # If the Map_Shapefiles is missing, create the folder
        if not os.path.exists( MAP_DIRECTORY ) and not os.path.isdir( MAP_DIRECTORY ):
            print("The Map Folder contains source data needed for this script.")
            print("\t Source data was provided in the original download file")
            os.makedirs( MAP_DIRECTORY )

        # If Raster_Folder is missing, create the folder
        if not os.path.exists( MOSAIC_DIRECTORY ) and not os.path.isdir( MOSAIC_DIRECTORY ):
            print("The Mosaic Folder is the output location for raster mosaics")
            print("\t created using this script")
            os.makedirs( MOSAIC_DIRECTORY )

        # If EXPORT_METADATA_DIRECTORY is missing, create the folder
        if not os.path.exists( EXPORT_METADATA_DIRECTORY ) and not os.path.isdir( EXPORT_METADATA_DIRECTORY ):
            print("The EXPORT_METADATA_DIRECTORY Folder is the output location for export metadata")
            print("\t created using this script")
            os.makedirs( EXPORT_METADATA_DIRECTORY )

        # If ARCGIS_METADATA_DIRECTORY is missing, create the folder
        if not os.path.exists( ARCGIS_METADATA_DIRECTORY ) and not os.path.isdir( ARCGIS_METADATA_DIRECTORY ):
            print("The ARCGIS_METADATA_DIRECTORY Folder is the output location for ArcGIS metadata")
            print("\t created using this script")
            os.makedirs( ARCGIS_METADATA_DIRECTORY )

        # If INPORT_METADATA_DIRECTORY is missing, create the folder
        if not os.path.exists( INPORT_METADATA_DIRECTORY ) and not os.path.isdir( INPORT_METADATA_DIRECTORY ):
            print("The INPORT_METADATA_DIRECTORY Folder is the output location for InPort metadata")
            print("\t created using this script")
            os.makedirs( INPORT_METADATA_DIRECTORY )

        # If Raster_Folder is missing, create the folder
        if not os.path.exists( LOG_DIRECTORY ) and not os.path.isdir( LOG_DIRECTORY ):
            print("The Log Folder is the output location for log files")
            print("\t created using this script")
            os.makedirs( LOG_DIRECTORY )

        elif ClearLogDirectory:
            for filename in os.listdir(LOG_DIRECTORY):
                file_path = os.path.join(LOG_DIRECTORY, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))
                del filename, file_path

        # Now we need to test if there is an ArGIS Pro project
        if ProductName == "ArcGISPro":
            print("Testing ArcGISPro")
            try:
                #template_project = os.path.join(os.path.dirname(ProjectGIS), "DisMAP Project Template", "DisMAP Project Template.aprx")
                template_project = os.path.join(os.path.dirname(BASE_DIRECTORY), "DisMAP Project Template", "DisMAP Project Template.aprx")
                #print(template_project)
                aprx = arcpy.mp.ArcGISProject(template_project)

                # print( aprx.defaultGeodatabase )
                # print( aprx.defaultToolbox )
                # print( aprx.homeFolder )
                # Create the scratch File Geodatabase
                #if not os.path.exists( DefaultGDB ) and not os.path.isdir( DefaultGDB ):
                #    arcpy.management.CreateFileGDB(BASE_DIRECTORY, "Default")
                #else:
                #    print("\t Default.gdb Exists")
                #if not os.path.exists( ProjectGDB ) and not os.path.isdir( ProjectGDB ):
                #    arcpy.management.CreateFileGDB(BASE_DIRECTORY, ProjectName)
                #else:
                #    print("\t {0}.gdb Exists".format(ProjectName))
                # Set Enviroment Variables
                #arcpy.EnvManager(scratchWorkspace = ScratchGDB, workspace = ProjectGDB)

                if not os.path.exists( ProjectGIS ) or ReplaceProject:
                    aprx.defaultGeodatabase = ProjectGDB
                    aprx.homeFolder = BASE_DIRECTORY
                    #aprx.defaultToolbox = ProjectToolBox
                    aprx.saveACopy(ProjectGIS)

                del aprx, template_project

            except IOError:
                print('\nThere was an error opening the ArcGIS Pro Project: {0}!'.format(ProjectName))
                print('\t Step #1 Start a new ArcGIS Pro session')
                print('\t Step #2 Select the Catalog Blank Template')
                print('\t Step #3 Enter {0} for the name of the project'.format(ProjectName))
                print('\t Step #4 Use the Folder icon to navigate to the Project Folder:\n\t\t{0}'.format(BASE_DIRECTORY))
                print('\t Step #5 Uncheck "Create a new folder for this project')
                print('\t Step #6 Click OK to continue. Once the new Project is created,')
                print('\t\t exit ArcGIS Pro and return to run this script again')
                return
        elif ProductName == "Desktop":
            #print("Testing Desktop")
            print("This script requires ArcGIS Pro")
        else:
            print("ArcGIS Needs to be installed and available for use")
            return

        #This program cannot run without having the Spatial Extension.
        #If it doesn't exist or cannot be checked out, we will exit the program.
        try:
            if not arcpy.CheckExtension("Spatial") == "Available":
                print("WARNING!! The SPATIAL EXTENSION is required to successfully run this script")
                # Raise IOError to exit script
                raise IOError
        except IOError:
            return

        del sys, platform
        del ProductName, ProductVersion, ProductLicenseLevel

        localKeys =  [key for key in locals().keys() if "function" not in key]

        if localKeys:
            msg = "Local Keys in {0}(): {1}".format(function, u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys, function

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo

def queryTable():
    try:
        OARegionMax = 0
        HUALIDMax = 0
        SpeciesMax = 0
        CommonNameMax = 0
        SpeciesCommonNameMax = 0
        StratumMax = 0

        # Get a list of tables
        msg = 'Get a list of tables'
        print(msg)
        del msg

        # Creating the list of tables
        tbs = arcpy.ListTables("*_csv")

        # Loop through the list of tables
        for tb in tbs:
            #msg = "\t Table: {}".format(tb)
            #print(msg)
            #del msg

            # Get list of fields in the table
            #fields = arcpy.ListFields(tb, field_type = "String")
            fields = arcpy.ListFields(tb)

            # Loop through fields
            for field in fields:
##                print("\t\t Field:       {0}".format(field.name))
##                print("\t\t Alias:       {0}".format(field.aliasName))
##                print("\t\t Type:        {0}".format(field.type))
##                print("\t\t Length:        {0}".format(field.length)
##                print("\t\t Is Editable: {0}".format(field.editable))
##                print("\t\t Required:    {0}".format(field.required))
##                print("\t\t Scale:       {0}".format(field.scale))
##                print("\t\t Precision:   {0}".format(field.precision))

                fieldName = field.name
                fieldAliasName = field.aliasName
                fieldType = field.type
                fieldLength = field.length
                fieldEditable = field.editable
                fieldRequired = field.required
                fieldScale = field.scale
                fieldPrecision = field.precision


##                print("\t\t Field:       {0}".format(fieldName))
##                print("\t\t Alias:       {0}".format(fieldAliasName))
##                print("\t\t Type:        {0}".format(fieldType))
##                print("\t\t Type:        {0}".format(fieldLength))
##                print("\t\t Is Editable: {0}".format(fieldEditable))
##                print("\t\t Required:    {0}".format(fieldRequired))
##                print("\t\t Scale:       {0}".format(fieldScale))
##                print("\t\t Precision:   {0}".format(fieldPrecision))


##                msg = "\t\t {}, {}, {}, {}, {}, {}".format(fieldName, fieldAliasName, fieldType, fieldEditable, fieldRequired, fieldScale, fieldPrecision)
##                print(msg)
##                del msg

##                msg = "\t\t {}, {}, {}, {}, {}".format(tb, fieldName,  fieldType, fieldLength, fieldScale, fieldPrecision)
##                print(msg)
##                del msg

                msg = "{}, {}, {}, {}".format(tb, fieldName, fieldType, fieldLength)
                print(msg)
                del msg

                #
                if fieldName == 'OARegion':
                    OARegionMax = fieldLength if fieldLength > OARegionMax else OARegionMax

                if fieldName == 'HUAL_ID':
                    HUALIDMax = fieldLength if fieldLength > HUALIDMax else HUALIDMax

                if fieldName == 'Species':
                    SpeciesMax = fieldLength if fieldLength > SpeciesMax else SpeciesMax

                if fieldName == 'CommonName':
                    CommonNameMax = fieldLength if fieldLength > CommonNameMax else CommonNameMax

                if fieldName == 'SpeciesCommonName':
                    SpeciesCommonNameMax = fieldLength if fieldLength > SpeciesCommonNameMax else SpeciesCommonNameMax

                if fieldName == 'Stratum':
                    StratumMax = fieldLength if fieldLength > StratumMax else StratumMax

                del field, fieldName, fieldAliasName, fieldType, fieldLength
                del fieldEditable, fieldRequired, fieldScale, fieldPrecision

            del fields

##        # Get a record count to see if data is present; we don't want to add data
##        count = int(arcpy.management.GetCount(gdb_tb)[0])
##        msg = '{} has {} records'.format(gdb_tb, count)
##        print(msg)
##        del msg

        print()
        print("OARegionMax: {}".format(OARegionMax))
        print("HUALIDMax: {}".format(HUALIDMax))
        print("SpeciesMax: {}".format(SpeciesMax))
        print("CommonNameMax: {}".format(CommonNameMax))
        print("SpeciesCommonNameMax: {}".format(SpeciesCommonNameMax))
        print("StratumMax: {}".format(StratumMax))

        del OARegionMax, HUALIDMax, SpeciesMax,CommonNameMax, StratumMax, SpeciesCommonNameMax

        # Cleanup
        del tb, tbs

        localKeys =  [key for key in locals().keys()]

        if localKeys:
            msg = "Local Keys in queryTable(): {0}".format(u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo

def queryYears():
    try:
        # Start looping over the table_name array as we go region by region.
        for table_name in table_names:
            # Assigning variables from items in the chosen table list
            region_abb = table_name[2]
            region = table_name[3]

            # Make Geodatabase friendly name
            region_name = region.replace('(','').replace(')','').replace('-','_to_').replace(' ', '_').replace("'", "")

            # Generate the shapefile to be used. We output this to the file system in the appropriate folder.
            msg = '> Query years for the {} region:'.format(region)
            print(msg)
            del msg

            # Prepare the points layer
            in_fc = os.path.join(ProjectGDB, region_name)
            my_points = arcpy.management.MakeFeatureLayer(in_fc, "my_points")
            del in_fc

            result = arcpy.management.GetCount(my_points)
            msg = '>-> {} has {} records'.format(region, result[0])
            print(msg)
            del msg, result

            my_unique_fish = unique_fish( my_points )

            # Test if we are filtering on species. If so, a new species list is
            # created with the selected species remaining in the list
            if FilterSpecies:
                # Get a shorter list
                my_unique_fish = [f for f in my_unique_fish if f in selected_species.keys()]
            else:
                pass

            # Finally we will start looping of the uniquely identified fish in this csv.
            for this_fish in my_unique_fish:
                # We prepare a place so that we can place fish data relevant to the fish species we're looking at.
                my_fish_dir = this_fish.replace("'","")
                my_fish_dir = my_fish_dir.replace(".","")
                my_fish_dir = my_fish_dir.replace("/","and")

                # We are pretty much going to set min to 0, max to STD(OVER YEARS)*2+AVG(OVER YEARS), and the other two shouldn't matter, but we'll set those anyways.
                select_by_fish_no_years(my_points, this_fish.replace("'","''") )

                # Get all of the unique years
                my_unique_years = unique_year( my_points, this_fish.replace("'","''") )
                print("{0}".format(this_fish))
                print(my_unique_years)
                print("")


            # Delete my points
            arcpy.management.Delete("my_points")

            # Clean up
            del my_points, region

        #Clean up
        del table_name, region_abb, region_name
        del my_unique_years, my_unique_fish, this_fish, my_fish_dir

        localKeys =  [key for key in locals().keys()]

        if localKeys:
            msg = "Local Keys in queryYears(): {0}".format(u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo

def reorder_fields(table, out_table, field_order, add_missing=True):
    try:
        # From http://joshwerts.com/blog/2014/04/17/arcpy-reorder-fields/
        """
        Reorders fields in input featureclass/table
        :table:         input table (fc, table, layer, etc)
        :out_table:     output table (fc, table, layer, etc)
        :field_order:   order of fields (objectid, shape not necessary)
        :add_missing:   add missing fields to end if True (leave out if False)
        -> path to output table
        """
        existing_fields = arcpy.ListFields(table)
        existing_field_names = [field.name for field in existing_fields]

        existing_mapping = arcpy.FieldMappings()
        existing_mapping.addTable(table)

        new_mapping = arcpy.FieldMappings()

        def add_mapping(field_name):
            mapping_index = existing_mapping.findFieldMapIndex(field_name)

            # required fields (OBJECTID, etc) will not be in existing mappings
            # they are added automatically
            if mapping_index != -1:
                field_map = existing_mapping.fieldMappings[mapping_index]
                new_mapping.addFieldMap(field_map)

        # add user fields from field_order
        for field_name in field_order:
            if field_name not in existing_field_names:
                raise Exception("Field: {0} not in {1}".format(field_name, table))

            add_mapping(field_name)

        # add missing fields at end
        if add_missing:
            missing_fields = [f for f in existing_field_names if f not in field_order]
            for field_name in missing_fields:
                add_mapping(field_name)

        # use merge with single input just to use new field_mappings
        arcpy.management.Merge(table, out_table, new_mapping)
        return out_table
        ##Usage:
        ##
        ##new_field_order = ["field2", "field3", "field1"]
        ##reorder_fields(in_fc, out_fc, new_field_order)

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo

# #
# Function: select_by_fish
#       Selects the rows of fish species data in a 5 year span for use by the
#       Inverse Distance Weighted (IDW) function.
# @param string table: The name of the layer that contains the fish information
# @param string which_fish: The scientific name (Species) of the fish species to look at
# @param string base_year: The origin year (as a string) to get a five year range
#       (-2 to +2) of data for this fish.
# @return integer 1: returns 1 on complete
# #
def select_by_fish(table, which_fish, base_year):
    # This clears the selection just incase it is not empty, even though
    # "NEW_SELECTION" should theroetically take care of this
    # base_year should already be converted to string using str()
    #DEBUG_OUTPUT(3, "Selecing from table `"+ table.name +"`")
    DEBUG_OUTPUT(3, "Selecing from table `"+ str(table) +"`")
    DEBUG_OUTPUT(3, "With Statement:`\"Species\"='"+ which_fish +"' AND \"Year\" >= ("+base_year+"-2 ) AND \"Year\" <= (" + base_year+ "+2)`" )

    arcpy.management.SelectLayerByAttribute( table, "CLEAR_SELECTION" )
    arcpy.management.SelectLayerByAttribute( table, "NEW_SELECTION", "\"Species\"='"+ which_fish +"' AND \"Year\" >= ("+base_year+"-2 ) AND \"Year\" <= ("+base_year+"+2 ) " )
    return 1

##
# Function: select_by_fish_no_years
#       Does same thing as @function select_by_fish, just all of the years worth of data.
# @param string table: The name of the layer that contains the fish information
# @param string which_fish: The scientific name (Species) of the fish species to look at
# @return boolean True: returns True on complete.
##
def select_by_fish_no_years(table, which_fish):
    #DEBUG_OUTPUT(3, "Selecing from table `"+ table.name +"`")
    DEBUG_OUTPUT(3, "Selecing from table `"+ str(table) +"`")
    DEBUG_OUTPUT(3, "With Statement:`\"Species\"='"+ which_fish + "'`" )

    arcpy.management.SelectLayerByAttribute( table, "CLEAR_SELECTION" )
    arcpy.management.SelectLayerByAttribute( table, "NEW_SELECTION", "\"Species\"='"+ which_fish +"'" )
    return 1

def setMosaicDatasetProperties():
    try:
        # https://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/wkfl-create-a-multidimensional-mosaic-dataset-from-a-set-of-time-series-images.htm

        # Uses the inspect module and a lamda to find name of this function
        function = function_name()
        #arcpy.AddMessage(function)

        # Set a start time so that we can see how log things take
        start_time = time()

        arcpy.env.overwriteOutput = True
        arcpy.env.scratchWorkspace = ScratchGDB
        arcpy.env.workspace = ProjectGDB

        for table_name in table_names:
            # Assigning variables from items in the chosen table list
            #region_shape = table_name[0]
            #region_boundary = table_name[1]
            region_abb = table_name[2]
            region = table_name[3]
            #csv_file = table_name[4]
            #region_georef = table_name[5]
            #region_contours = table_name[6]

            # For benchmarking.
            log_file = os.path.join(LOG_DIRECTORY, region + ".log")

            # Write a message to the log file
            msg = "#-> STARTING {0} ON {1}".format(function, strftime("%a %b %d %I:%M:%S %p", localtime()))
            logFile(log_file, msg)
            del msg

            msg = ">-> Region (abb): {0}\n\t Region:  {1}".format(region_abb, region)
            logFile(log_file, msg)

            # Define region_mosaic
            region_mosaic = os.path.join(ProjectGDB, region_abb)

            ###--->>> SetMosaicDatasetProperties
            msg = "\t\t Set Mosaic Dataset Properties"
            logFile(log_file, msg)

            arcpy.management.SetMosaicDatasetProperties(region_mosaic,
                                                        4100,
                                                        15000,
                                                        "None;JPEG;LZ77;LERC",
                                                        "LZ77",
                                                        75,
                                                        0.01,
                                                        "BILINEAR",
                                                        "NOT_CLIP",
                                                        "FOOTPRINTS_MAY_CONTAIN_NODATA",
                                                        "CLIP",
                                                        "NOT_APPLY",
                                                        "Basic",
                                                        "Basic",
                                                        "NorthWest;Center;LockRaster;ByAttribute;Nadir;Viewpoint;Seamline;None",
                                                        "NorthWest",
                                                        '',
                                                        '',
                                                        "ASCENDING",
                                                        "FIRST",
                                                        10,
                                                        600,
                                                        300,
                                                        20,
                                                        0.8,
                                                        "0 0",
                                                        "Basic",
                                                        "Name;MinPS;MaxPS;LowPS;HighPS;Tag;GroupName;ProductName;CenterX;CenterY;ZOrder;Shape_Length;Shape_Area;OARegion;Species;CommonName;SpeciesCommonName;CoreSpecies;Year;Variable;StdTime;Thumbnail;Dimensions",
                                                        "DISABLED",
                                                        '',
                                                        '',
                                                        '',
                                                        None,
                                                        20,
                                                        1000,
                                                        "GENERIC",
                                                        1,
                                                        #"None;'{0}'".format(variables),
                                                        "None",
                                                        "None",
                                                        None,
                                                        '',
                                                        "NONE",
                                                        None)

        del table_name, region_abb, region, region_mosaic
        # Cleanup
        del log_file

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = u"#-> Elapsed Time for {0} {1} (H:M:S)\n".format(function, strftime("%H:%M:%S", gmtime(elapse_time)))
        print(msg)
        del msg, start_time, end_time, elapse_time

        localKeys =  [key for key in locals().keys() if "function" not in key]

        if localKeys:
            msg = "Local Keys in {0}(): {1}".format(function, u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys, function

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo

def tableAndFieldReport(workspace, wildcard, datatype, type):
    try:
        # Uses the inspect module and a lamda to find name of this function
        function = function_name()

        arcpy.env.workspace = workspace

        # Get a list of tables
        msg = f"Workspace: {workspace}"
        print(msg); del msg


        # Get a list of tables
        msg = 'Get a list of Datasets'
        print(msg); del msg

##        items = {
##                 #'ai_csv' : "CSV Table",
##                 #'DataSeries' : "Table",
##                 #'SpeciesRegionSeason' : "Table",
##                 'Indicators' : "Table",
##                 #'DisMAP_Regions' : "Feature Class",
##                 #'Aleutian_Islands_Survey_Locations' : "Feature Class",
##                 #'AI_Shape' : "Feature Class",
##                 #'AI' : "Mosaic",
##                 }

##        items = []
##
##        # Creating the list of tables
##        #tbs = [t for t in arcpy.ListTables("*") if not 'Template' in t]
##        tbs = ['ai_csv', 'DataSeries', 'SpeciesRegionSeason', 'Indicators',]
##        print(tbs)
##        items.extend(tbs)
##
##        #fcs = arcpy.ListFeatureClasses("*")
##        fcs = ['DisMap_Regions', 'Aleutian_Islands_Survey_Locations']
##        print(fcs)
##        items.extend(fcs)
##
##        #dss = arcpy.ListDatasets("*", "Mosaic")
##        dss = ['AI',]
##        print(dss)
##        items.extend(dss)

        fieldNames = []

        arcGISfields = ['Shape',
                        'Shape_Length',
                        'Tag',
                        'HighPS',
                        'ZOrder',
                        'CenterX',
                        'Name',
                        'CenterY',
                        'ProductName',
                        'Raster',
                        'UriHash',
                        'MinPS',
                        'ServiceName',
                        'TypeID',
                        'OBJECTID',
                        'MaxPS',
                        'Uri',
                        'LowPS',
                        'Shape_Area',
                        'Thumbnail',
                        'ItemTS',
                        'GroupName',
                        'Category',
                       ]

        dataSets = []

        walk = arcpy.da.Walk(workspace, topdown=True, datatype=datatype, type=type)

        for dirpath, dirnames, filenames in walk:
            for filename in filenames:
                if wildcard.lower() in filename.lower():
                    #dataSets.append(os.path.join(dirpath, filename))
                    dataSets.append(filename)

        for dataSet in dataSets:
            # Describe dataset
            desc = arcpy.Describe(dataSet)
            # Print selected dataset and describe object properties
            msg = "Data Set: {0} Data Type: {1}".format(desc.name, desc.dataType)
            print(msg); del msg
            del desc

            # Get list of fields in the table
            fields = arcpy.ListFields(dataSet)

            # Loop through fields
            for field in fields:
                fieldName = field.name
                fieldAliasName = field.aliasName
                fieldType = field.type
                fieldLength = field.length
                fieldEditable = field.editable
                fieldRequired = field.required
                fieldScale = field.scale
                fieldPrecision = field.precision

                fieldNames.append(fieldName)

                state = "Esri" if field.name in arcGISfields else "DisMAP"

                print("\t Field:       {0} ({1})".format(fieldName, state))
                print("\t Alias:       {0}".format(fieldAliasName))
                print("\t Type:        {0}".format(fieldType))
                print("\t Length:      {0}".format(fieldLength))
                print("\t Editable:    {0}".format(fieldEditable))
                print("\t Required:    {0}".format(fieldRequired))
                print("\t Scale:       {0}".format(fieldScale))
                print("\t Precision:   {0}".format(fieldPrecision))
                print("")

                # This is for printing a list of attributes for the XML metadata file
                # print('\t\t\t\t<attrlabl Sync="TRUE">{0}</attrlabl>'.format(fieldName))
                # print('\t\t\t\t<attalias Sync="TRUE">{0}</attalias>'.format(fieldAliasName))
                # print('\t\t\t\t<attrtype Sync="TRUE">{0}</attrtype>'.format(fieldType))
                # print('\t\t\t\t<attwidth Sync="TRUE">{0}</attwidth>'.format(fieldLength))
                # print('\t\t\t\t<atprecis Sync="TRUE">{0}</atprecis>'.format(fieldPrecision))
                # print('\t\t\t\t<attscale Sync="TRUE">0</attscale>')
                # print('\t\t\t\t<attrdef>{0}</attrdef>'.format(fieldAliasName))
                # print('\t\t\t\t<attrdefs>{0}</attrdefs>'.format(state))
                # print('')

                del field, fieldName, fieldAliasName, fieldType
                del fieldLength, fieldEditable, fieldRequired, fieldScale
                del fieldPrecision, state

            del dataSet, fields

        del workspace, wildcard, fieldNames, arcGISfields, dataSets
        del walk, dirpath, dirnames, filenames, filename, datatype, type


##        # Loop through the list of tables
##        for item in items:
##            msg = "Item: {0} ({1})".format(item, items[item])
##            print(msg); del msg
##
##            # Get list of fields in the table
##            #fields = arcpy.ListFields(tb, field_type = "String")
##            fields = arcpy.ListFields(item)

##            # Loop through fields
##            for field in fields:
##                fieldName = field.name
##                fieldAliasName = field.aliasName
##                fieldType = field.type
##                fieldLength = field.length
##                fieldEditable = field.editable
##                fieldRequired = field.required
##                fieldScale = field.scale
##                fieldPrecision = field.precision
##
##                fieldNames.append(fieldName)
##
##                state = "Esri" if field.name in arcGISfields else "DisMAP"
##
##                print("\t Field:       {0} ({1})".format(fieldName, state))
##                print("\t Alias:       {0}".format(fieldAliasName))
##                print("\t Type:        {0}".format(fieldType))
##                print("\t Length:      {0}".format(fieldLength))
##                print("\t Editable:    {0}".format(fieldEditable))
##                print("\t Required:    {0}".format(fieldRequired))
##                print("\t Scale:       {0}".format(fieldScale))
##                print("\t Precision:   {0}".format(fieldPrecision))
##                print("")
##
##                print('\t\t\t\t<attrlabl Sync="TRUE">{0}</attrlabl>'.format(fieldName))
##                print('\t\t\t\t<attalias Sync="TRUE">{0}</attalias>'.format(fieldAliasName))
##                print('\t\t\t\t<attrtype Sync="TRUE">{0}</attrtype>'.format(fieldType))
##                print('\t\t\t\t<attwidth Sync="TRUE">{0}</attwidth>'.format(fieldLength))
##                print('\t\t\t\t<atprecis Sync="TRUE">{0}</atprecis>'.format(fieldPrecision))
##                print('\t\t\t\t<attscale Sync="TRUE">0</attscale>')
##                print('\t\t\t\t<attrdef>{0}</attrdef>'.format(fieldAliasName))
##                print('\t\t\t\t<attrdefs>{0}</attrdefs>'.format(state))
##                print('')

##                msg = "\t\t {}, {}, {}, {}, {}, {}".format(fieldName, fieldAliasName, fieldType, fieldEditable, fieldRequired, fieldScale, fieldPrecision)
##                print(msg)
##                del msg

##                msg = "\t\t {}, {}, {}, {}, {}".format(tb, fieldName,  fieldType, fieldLength, fieldScale, fieldPrecision)
##                print(msg)
##                del msg

##                msg = "{}, {}, {}, {}".format(tb, fieldName, fieldType, fieldLength)
##                print(msg)
##                del msg

##                del field, fieldName, fieldAliasName, fieldType, fieldLength
##                del fieldEditable, fieldRequired, fieldScale, fieldPrecision
##                del state

         #   del fields

        #fieldNames = list(set(fieldNames))
        #print(fieldNames)

        #del fieldNames

        # Cleanup
        #del item, items, arcGISfields
        #del tbs, fcs, dss

        localKeys =  [key for key in locals().keys() if "function" not in key]

        if localKeys:
            msg = "Local Keys in {0}(): {1}".format(function, u", ".join(localKeys))
            print(msg)
            del msg
        del localKeys, function

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo

# #
# Function: unique_field
#       Generic function to return all the unique values within a specified field
# @param string table: The name of the layer that contains the field to be searched
# @param string field: which field to look
# @return array: a sorted array of unique values.
# #
def unique_field(table,field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})

# #
# Function: unique_fish
#       Gets the unique fish species within a dataset
# @param string table: The name of the layer that contains the fish information
# @return array: a sorted array of unique fish species.
# #
def unique_fish(table):
    arcpy.management.SelectLayerByAttribute( table, "CLEAR_SELECTION" )
    with arcpy.da.SearchCursor(table, ["Species"]) as cursor:
        return sorted({row[0] for row in cursor})

# #
# Function: unique_fish_dict
#       Gets the unique fish species and common name within a dataset
# @param string table: The name of the layer that contains the fish information
# @return array: a sorted array of unique fish species and common name.
# #
def unique_fish_dict(table):
    arcpy.management.SelectLayerByAttribute( table, "CLEAR_SELECTION" )
    with arcpy.da.SearchCursor(table, ["Species", "CommonName", "CoreSpecies"]) as cursor:
        return {row[0] : [row[1], row[2]] for row in cursor if row[0] not in ['NA', '']}

# #
# Function: unique_year
#       Gets the unique years (that have data) for a fish species
# @param string table: The name of the layer that contains the fish information
# @param string which_fish: The scientific name (Species) of the fish species to look at
# @return array: a sorted year array so we can go in order.
# #
def unique_year(table, which_fish):
    arcpy.management.SelectLayerByAttribute( table, "CLEAR_SELECTION" )
    with arcpy.da.SearchCursor(table, ["Year"], "\"Species\"='"+ which_fish +"'") as cursor:
        return sorted({row[0] for row in cursor})

# #
# Function: unique_years
#       Gets the unique years in a table
# @param string table: The name of the layer
# @return array: a sorted year array so we can go in order.
# #
def unique_years(table):
    #print("in table function")
    arcpy.management.SelectLayerByAttribute( table, "CLEAR_SELECTION" )
    #msg = arcpy.GetMessages()
    #msg = ">->->-> {0}".format(msg.replace('\n', '\n>->->-> '))
    #print(msg)
    #arcpy.management.SelectLayerByAttribute( table, "NEW_SELECTION", "Year IS NOT NULL AND Variable NOT IN ('Species Richness')")
    arcpy.management.SelectLayerByAttribute( table, "NEW_SELECTION", "Year IS NOT NULL")
    #msg = arcpy.GetMessages()
    #msg = ">->->-> {0}".format(msg.replace('\n', '\n>->->-> '))
    #print(msg)
    #with arcpy.da.SearchCursor(table, ["year"]) as cursor:
    with arcpy.da.SearchCursor(table, ["Year"]) as cursor:
        #for row in cursor: print(row[0])
        return sorted({row[0] for row in cursor})

def unique_values(table, field):  ##uses list comprehension
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})





##def createIndicatorsTableDev():
##    try:
##        # Get the current workspace and save it to temp_workspace
##        temp_workspace = arcpy.env.workspace
##
##        temp_indicators = "temp_indicators"
##        csv_file = "by_species"
##
##
##        # Set a start time so that we can see how log things take
##        start_time = time()
##
##        # Write a message to the log file
##        msg = "STARTING ON {0}".format(strftime("%a %b %d %I:%M:%S %p", localtime()))
##        print(msg)
##
##        # Generate the shapefile to be used. We output this to the file system in the appropriate folder.
##        msg = '> Generating {0} Table.'.format(temp_indicators)
##        print(msg)
##
##        # out_table = os.path.join(DefaultGDB, csv_file)
##        out_table = os.path.join(ProjectGDB, csv_file)
##        #print(out_table)
##        #if arcpy.Exists(out_table):
##        #    arcpy.management.Delete(out_table)
##
##        input_csv_file = os.path.join(CSV_DIRECTORY, csv_file + ".csv")
##        del csv_file
##
##        msg = '>-> Processing the {0} CSV Table'.format(temp_indicators)
##        print(msg)
##
##        # https://pandas.pydata.org/pandas-docs/stable/getting_started/intro_tutorials/09_timeseries.html?highlight=datetime
##        df = pd.read_csv(input_csv_file)
##        del input_csv_file
##        #df = pd.read_csv(input_csv_file, parse_dates[u'year'])
##        #df.columns = [u'csv_id', u'region', u'haulid', u'year', u'spp', u'wtcpue', u'common', u'stratum', u'stratumarea', u'lat', u'lon', u'depth']
##        msg = '>->-> Defining the column name.'
##        print(msg)
##
##        #print('DataFrame\n----------\n', df.head(10))
##        #print('\nDataFrame datatypes :\n', df.dtypes)
##        #columns = [str(c) for c in df.dtypes.index.tolist()]
##
##        #
##        # df.columns = [u'CSVFILEID', u'OARegion', u'HUALID', u'Year', u'Species', u'WTCPUE', u'CommonName', u'Stratum', u'StratumArea', u'Latitude', u'Longitude', u'Depth']
##        #            ['region',   'spp',      'year', 'lat',                  'depth',                 'lon',  'lat_se',  'depth_se',  'lon_se']
##        df.columns = [u'OARegion', u'Species', u'CommonName', u'Year', u'CenterOfGravityLatitude', u'CenterOfGravityDepth', u'CenterOfGravityLongitude', u'CenterOfGravityLatitudeStandardError', u'CenterOfGravityDepthStandardError', u'CenterOfGravityLongitudeStandardError']
##        column_names = list(df.columns)
##        column_formats = ['S50', 'S50', 'S50', '<i4', '<f8', '<f8', '<f8', '<f8', '<f8', '<f8',]
##        #df.Species = df.Species.fillna('')
##        df = df[df['Species'].notna()]
##        df.CommonName = df.CommonName.fillna('')
##
##        #print(column_names)
##        #print(column_formats)
##        dtypes = list(zip(column_names, column_formats))
##        #print(dtypes)
##        #print(df.columns)
##
##        try:
##            if ProductName == "Desktop":
##                array = np.array(np.rec.fromrecords(df.values, names = column_names, formats = column_formats))
##            elif ProductName == "ArcGISPro":
##                array = np.array(np.rec.fromrecords(df.values), dtype = dtypes)
##            else:
##                pass
##        except:
##            import sys, traceback
##            # Get the traceback object
##            tb = sys.exc_info()[2]
##            #tb = sys.exc_info()
##            tbinfo = traceback.format_tb(tb)[0]
##            # Concatenate information together concerning the error into a message string
##            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
##            print(pymsg)
##            del pymsg, tb, tbinfo
##
##        del df, column_names, column_formats, dtypes
##
##        # Temporary table
##        tmp_table = out_table + '_tmp'
##        if arcpy.Exists(tmp_table):
##            arcpy.management.Delete(tmp_table)
##
##        try:
##            arcpy.da.NumPyArrayToTable(array, tmp_table)
##        except IOError:
##            print("Something went wrong")
##        except:
##            print("Something went wrong")
##        del array, out_table
##
##        indicators = os.path.join(ProjectGDB, u"Indicators")
##        indicators_dev = os.path.join(ProjectGDB, u"IndicatorsDev")
##
##        # Execute CreateTable
##        arcpy.management.CreateTable(ProjectGDB, u"IndicatorsDev", indicators, config_keyword = "")
##
##        arcpy.management.Append(inputs=tmp_table, target=indicators_dev, schema_type="NO_TEST", field_mapping="", subtype="")
##
##        codeBlock="""def x(region):
##                       if 'Fall' in region:
##                          return 'Fall'
##                       elif 'Spring' in region:
##                          return 'Spring'
##                       elif 'Summer' in region:
##                          return 'Summer'
##                       else:
##                          return ''"""
##        del tmp_table
##
##        arcpy.management.CalculateField(in_table=indicators_dev, field="DisMapSeasonCode", expression="x( !OARegion! )", expression_type="PYTHON", code_block = codeBlock)
##        del codeBlock
##
##        arcpy.management.CalculateField(in_table=indicators_dev, field="DisMapRegionCode", expression="!OARegion!.replace(' ', '_').lower()", expression_type="PYTHON", code_block="")
##
##        del indicators, indicators_dev
##
##        #Final benchmark for the region.
##        msg = "ENDING REGION {} COMPLETED ON {}".format(temp_indicators, strftime("%a %b %d %I:%M:%S %p", localtime()))
##        print(msg)
##        del temp_indicators
##
##        # Elapsed time
##        end_time = time()
##        elapse_time =  end_time - start_time
##        msg = u"Elapsed Time {0} (H:M:S)\n".format(strftime("%H:%M:%S", gmtime(elapse_time)))
##        print(msg)
##
##        arcpy.env.workspace = temp_workspace
##        del temp_workspace, start_time, msg, end_time, elapse_time
##
##        localKeys =  [key for key in locals().keys()]
##
##        if localKeys:
##            msg = "Local Keys in createIndicatorsTableDev(): {0}".format(u", ".join(localKeys))
##            print(msg)
##            del msg
##        del localKeys
##
##    except:
##        import sys, traceback
##        # Get the traceback object
##        tb = sys.exc_info()[2]
##        tbinfo = traceback.format_tb(tb)[0]
##        # Concatenate information together concerning the error into a message string
##        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
##        print(pymsg)
##        del pymsg, tb, tbinfo









if __name__ == '__main__':
    try:
        arcpy.ResetEnvironments()

        # Set a start time so that we can see how log things take
        start_time = time()

        # Write a message to the log file
        msg = "STARTING PROGRAM ON {}".format(strftime("%a %b %d %I:%M:%S %p", localtime()))
        print(msg)

        # This is a list of local and global variables that are exclude from
        # lists of variables
        exclude_keys = ['arcgis', 'arcpy', 'date', 'datetime', 'exclude_keys', 'main', 'math',
                        'numpy', 'np', 'os', 'pd', 'sys', 'time', 'localtime',
                        'strftime', 'sleep', 'gmtime', 'shutil', 'scipy',
                        'stats', 'copysign', "logging", "MakeInt", "getDate",
                        "removeSpaces"]

        # Use all of the cores on the machine.
        arcpy.env.parallelProcessingFactor = "100%"
        ##!!WARNING!!:::::::SET THE OVERWRITE TO ON - ANY ITEMS THAT GET SAVED WILL BE OVERWRITTEN
        arcpy.env.overwriteOutput = True
        arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"
        #
        arcpy.env.pyramid = "PYRAMIDS -1 CUBIC DEFAULT 75 NO_SKIP"
        arcpy.env.cellSizeProjectionMethod = "PRESERVE_RESOLUTION"
        # Use the minimum value of the data at the coincident location.
        arcpy.env.coincidentPoints = "INCLUDE_ALL"
        # Set the resampling method environment to bilinear interpolation
        # Options: "NEAREST", "BILINEAR", "CUBIC"
        arcpy.env.resamplingMethod = "NEAREST"
        #arcpy.env.resamplingMethod = "BILINEAR"
        # Set the raster statistics
        arcpy.env.rasterStatistics = "STATISTICS 1 1"
        # Statistics using a skip factor of 100 for x and y, and
        # ignore values of 0 and 255
        #arcpy.env.rasterStatistics = 'STATISTICS 100 100 (0 255)'
        # Set the cell size environment using a number. In this case 10,000 m
        cell_size = 2000
        arcpy.env.cellSize = cell_size
        arcpy.env.outputZFlag = "Disabled"
        arcpy.env.outputMFlag = "Disabled"
        # Set the compression environment to LZ77
        arcpy.env.compression = "LZ77"

        arcpy.SetLogMetadata(False)

        DEBUG_LEVEL = 0
        # 0: No Debugging Ouput
        # 1: Some probably important stuff
        # 2: mostly important stuff
        # 3: Probably literally everything, as verbose as necessary.


        # ###--->>> Declaring folder paths
        # Project Folders:
        # DisMap Folder
        #   ArcGIS_Analysis_Files
        #       Analysis_Folder <<-- created in OAGenerateRasterFiles.py
        #       Fish Data <<-- Needs to be present and have data created from R script
        #       Map_Shapefiles <<--- Only folder present in the zip file from OceanAdapt
        #       Map_Picture_Collection <<-- created in OAGenerateRasterFiles.py
        #       Raster_Folder <<-- created in ST6OAGenerateRasterFiles.py
        #       Log_Folder <<-- created to centrailize log files
        #   OceanAdapt
        #       (Various sub-folders)
        #

        # Project related items

        # December 1 2022
        Version = "December 1 2022"
        DateCode = "20221201"

        # October 1 2022
        #Version = "October 1 2022"
        #DateCode = "20221001"

        # Agust 9 2022
        # Version = "August 9 2022"
        # DateCode = "20220809"

        # Agust 2 2022
        #Version = "August 2 2022"
        #DateCode = "20220802"

        # July 17 2022
        #Version = "July 17 2022"
        #DateCode = "20220717"

        # May 16 2022
        #Version = "May 16 2022"
        #DateCode = "20220516"

        # March 7 2022
        #Version = "March 7 2022"
        #DateCode = "20220307"

        # March 1 2022
        #Version = "March 1 2022"
        #DateCode = "20220301"

        # February 1 2022
        #Version = "February 1 2022"
        #DateCode = "20220201"

        # March 1 2021
        #Version = "March 1 2021"
        #DateCode = "20210301"

        ProjectName = "DisMAP {0}".format(Version)

        # ###--->>> Software Environment Level
        #SoftwareEnvironmentLevel = ""
        SoftwareEnvironmentLevel = "Dev" # Local laptop
        SoftwareEnvironmentLevel = "Test" # Local laptop and Windows Instance
        #SoftwareEnvironmentLevel = "Prod" # Windows Instance

        # The directory this script is in.
        # cwd = os.getcwd()
        # The directory this script is in (ArcGIS_Analysis_Files).
        # or os.path.dirname(sys.argv[0])
        BASE_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
        BASE_DIRECTORY = os.path.join(BASE_DIRECTORY, Version)
        # print('BASE_DIRECTORY: ', BASE_DIRECTORY)
        # print(os.path.realpath(__file__))
        # Raster Files will go here.
        ANALYSIS_DIRECTORY = os.path.join(BASE_DIRECTORY, "Analysis Folder {0} {1}".format(Version, SoftwareEnvironmentLevel))
        # print('ANALYSIS_DIRECTORY: ', ANALYSIS_DIRECTORY)
        # CSV files will be read from
        CSV_DIRECTORY = os.path.join(BASE_DIRECTORY, "Fish Data {0}".format(Version))
        # print('CSV_DIRECTORY: ', CSV_DIRECTORY)
        # This directory contains important files for geoprocessing,
        # also the output directory for the feature classes created from the
        # CSV files
        MAP_DIRECTORY = os.path.join(BASE_DIRECTORY, "Map Shapefiles {0}".format(Version))
        # print('MAP_DIRECTORY: ', MAP_DIRECTORY)
        # Output the pictures to the Picture Folder.
        #PICTURE_FOLDER = os.path.join(BASE_DIRECTORY, "Map Picture Collection {0}".format(Version))
        # print('PICTURE_FOLDER: ', PICTURE_FOLDER)
        #Geodatabase Raster Files will go here.
        MOSAIC_DIRECTORY = os.path.join(BASE_DIRECTORY, "Mosaic Folder {0} {1}".format(Version, SoftwareEnvironmentLevel))
        # print('MOSAIC_DIRECTORY: ', MOSAIC_DIRECTORY)

        ProjectGIS = os.path.join(BASE_DIRECTORY, "{0}.aprx".format(ProjectName + " " + SoftwareEnvironmentLevel))
        ProjectToolBox = os.path.join(BASE_DIRECTORY, "{0}.tbx".format(ProjectName + " " + SoftwareEnvironmentLevel))
        #DefaultGDB = os.path.join(BASE_DIRECTORY, "Default.gdb")
        ProjectGDB = os.path.join(BASE_DIRECTORY, "{0}.gdb".format(ProjectName + " " + SoftwareEnvironmentLevel))
        BathymetryGDB = os.path.join(BASE_DIRECTORY, "Bathymetry.gdb")
        ScratchGDB = os.path.join(BASE_DIRECTORY, "Scratch {0} {1}".format(Version, SoftwareEnvironmentLevel), "scratch.gdb")
        ScratchFolder = os.path.join(BASE_DIRECTORY, "Scratch {0} {1}".format(Version, SoftwareEnvironmentLevel))

        # Log files will go here.
        LOG_DIRECTORY = os.path.join(BASE_DIRECTORY, "Log Folder {0}".format(Version))

        EXPORT_METADATA_DIRECTORY = os.path.join(BASE_DIRECTORY, "Export Metadata")
        ARCGIS_METADATA_DIRECTORY = os.path.join(BASE_DIRECTORY, "ArcGIS Metadata")
        INPORT_METADATA_DIRECTORY = os.path.join(BASE_DIRECTORY, "InPort Metadata")

##        # Set the workspace to the ProjectGDB
##        tmp_workspace = arcpy.env.workspace
##        arcpy.env.workspace = ProjectGDB
##
##        # Set the scratch workspace to the ScratchGDB
##        tmp_scratchWorkspace = arcpy.env.scratchWorkspace
##        arcpy.env.scratchWorkspace = ScratchGDB

##        # Set the workspace to the ProjectGDB
##        tmp_workspace = arcpy.env.workspace
##        arcpy.env.workspace = ProjectGDB
##
##        #if not os.path.isdir(ScratchFolder):
##        #    #shutil.rmtree(ScratchFolder)
##        #    arcpy.management.CreateFileGDB(ScratchGDB)
##        # Scratch workspace
##        tmp_scratchWorkspace = arcpy.env.scratchWorkspace
##        arcpy.env.scratchWorkspace = ScratchGDB
##        # If the scratch workspace is missing, referencing the env will create the workspace
##        msg = arcpy.env.scratchFolder
##        arcpy.AddMessage(msg)
##        msg = arcpy.env.scratchGDB
##        arcpy.AddMessage(msg)
##        del msg

        # ###--->>>

        # ###--->>> Declaring Table Names
        # The table_names variable includes the following information:
        #        table_names[0]: The region shape that gets used for the mask and extent of the environment variable, and the output coordinate system
        #        table_names[1]: The boundary shape file ( a single Polyline ) that gets used by arcpy.gp.Idw_sa
        #        table_names[2]: The abbreviation of the region (for file/folder structure)
        #        table_names[3]: The actual name of the region
        #        table_names[4]: The CSV file that contains this region's data
        #        table_names[5]: ??? The PRJ datum used by the region shapefile (table_names[0]). These are included within the ArcGIS installation. Please see
        #                            https://desktop.arcgis.com/en/arcmap/10.5/map/projections/pdf/projected_coordinate_systems.pdf
        #                            for valid Projection Names or inside arcgis itself.
        #                            The variable itself does not appear to be used, it's just there for my reference.
        #        table_names[6]: A shapefile containing contour lines for outputting pictures.

        # In order to automate generating raster files and pictures for the Ocean Adapt website, This array of information was used to allow controlled and regulated so all regions are treated the exact same way.
        table_names = [
                       [ 'AI_Shape', 'AI_Boundary','AI', 'Aleutian Islands', 'ai_csv', 'NAD_1983_2011_UTM_Zone_1N', 'contour_ai', 2000],
                       [ 'EBS_Shape', 'EBS_Boundary','EBS', 'Eastern Bering Sea', 'ebs_csv', 'NAD_1983_2011_UTM_Zone_3N', 'contour_ebs', 2000],
                       [ 'GOA_Shape', 'GOA_Boundary','GOA', 'Gulf of Alaska', 'goa_csv', 'NAD_1983_2011_UTM_Zone_5N', 'contour_goa', 2000],

                       [ 'GOM_Shape', 'GOM_Boundary','GOM', 'Gulf of Mexico', 'gmex_csv', 'NAD_1983_2011_UTM_Zone_15N', 'contour_gom', 2000],

                       #[ 'HI_Shape', 'HI_Boundary','HI', 'Hawaii Islands', 'hi_csv', 'WGS_1984_UTM_Zone_4N', 'contour_hi', 500],
                       [ 'HI_Shape', 'HI_Boundary','HI', "Hawai'i Islands", 'hi_csv', 'WGS_1984_UTM_Zone_4N', 'contour_hi', 500],

                       [ 'NEUS_Fall_Shape', 'NEUS_Fall_Boundary','NEUS_F', 'Northeast US Fall', 'neusf_csv', 'NAD_1983_2011_UTM_Zone_18N', 'contour_neus', 2000],
                       [ 'NEUS_Spring_Shape', 'NEUS_Spring_Boundary','NEUS_S', 'Northeast US Spring', 'neus_csv', 'NAD_1983_2011_UTM_Zone_18N', 'contour_neus', 2000],

                       [ 'SEUS_Shape', 'SEUS_Boundary','SEUS_SPR', 'Southeast US Spring', 'seus_spr_csv', 'NAD_1983_2011_UTM_Zone_17N', 'contour_seus', 2000],
                       [ 'SEUS_Shape', 'SEUS_Boundary','SEUS_SUM', 'Southeast US Summer', 'seus_sum_csv', 'NAD_1983_2011_UTM_Zone_17N', 'contour_seus', 2000],
                       [ 'SEUS_Shape', 'SEUS_Boundary','SEUS_FALL', 'Southeast US Fall', 'seus_fal_csv', 'NAD_1983_2011_UTM_Zone_17N', 'contour_seus', 2000],

                       [ 'WC_Ann_Shape', 'WC_Ann_Boundary','WC_ANN', 'West Coast Annual 2003-Present', 'wcann_csv', 'NAD_1983_2011_UTM_Zone_10N', 'contour_wc', 2000],
                       [ 'WC_Tri_Shape', 'WC_Tri_Boundary','WC_TRI', 'West Coast Triennial 1977-2004', 'wctri_csv', 'NAD_1983_2011_UTM_Zone_10N', 'contour_wc', 2000]
                      ]

        # ###--->>> Spatial Reference Dictionary
        srs = {u'NAD_1983_2011_UTM_Zone_1N'  : 'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]', # Aleutian Islands
               u'NAD_1983_2011_UTM_Zone_3N'  : 'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]', # Eastern Bering Sea
               u'NAD_1983_2011_UTM_Zone_5N'  : 'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]', # Gulf of Alaska
               u'NAD_1983_2011_UTM_Zone_10N' : 'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]', # West Coast
               #u'WGS_1984_UTM_Zone_4N'       : 'PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]', # Hawaii
               u'WGS_1984_UTM_Zone_4N'       : "PROJCS['WGS_1984_UTM_Zone_4N',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-159.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]];-5120900 -9998100 450445547.391054;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision", # Hawaii
               u'NAD_1983_2011_UTM_Zone_15N' : 'PROJCS["WGS_1984_Albers_NMSDD",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",180.0],PARAMETER["standard_parallel_1",-2.0],PARAMETER["standard_parallel_2",49.0],PARAMETER["latitude_of_origin",25.5],UNIT["Meter",1.0]]', # Gulf of Mexico
               u'NAD_1983_2011_UTM_Zone_17N' : 'PROJCS["WGS_1984_Albers_NMSDD",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",180.0],PARAMETER["standard_parallel_1",-2.0],PARAMETER["standard_parallel_2",49.0],PARAMETER["latitude_of_origin",25.5],UNIT["Meter",1.0]]', # Southeast US
               u'NAD_1983_2011_UTM_Zone_18N' : 'PROJCS["WGS_1984_Albers_NMSDD",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",180.0],PARAMETER["standard_parallel_1",-2.0],PARAMETER["standard_parallel_2",49.0],PARAMETER["latitude_of_origin",25.5],UNIT["Meter",1.0]]', # Northeast US
              }

##        # ###--->>> Spatial Reference Dictionary
##        srs = {u'NAD_1983_2011_UTM_Zone_1N'  : [102048, 'WGS_1984_(ITRF08)_To_NAD_1983_2011'], # Aleutian Islands
##               u'NAD_1983_2011_UTM_Zone_3N'  : [102050, 'WGS_1984_(ITRF08)_To_NAD_1983_2011'], # Eastern Bering Sea
##               u'NAD_1983_2011_UTM_Zone_5N'  : [102052, 'WGS_1984_(ITRF08)_To_NAD_1983_2011'], # Gulf of Alaska
##               u'NAD_1983_2011_UTM_Zone_10N' : [102057, 'WGS_1984_(ITRF08)_To_NAD_1983_2011'], # West Coast
##               u'NAD_1983_2011_UTM_Zone_15N' : [102384, 'WGS_1984_(ITRF08)_To_NAD_1983_2011'], # Gulf of Mexico
##               u'NAD_1983_2011_UTM_Zone_17N' : [102386, 'WGS_1984_(ITRF08)_To_NAD_1983_2011'], # Southeast US
##               u'NAD_1983_2011_UTM_Zone_18N' : [102387, 'WGS_1984_(ITRF08)_To_NAD_1983_2011'], # Northeast US
##               u'WGS_1984_Web_Mercator_Auxiliary_Sphere' : [102100, ''], # World
##              }
##
##        East Coast
##        Spatial Reference: PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]
##
##        Gulf of Mexico
##        Spatial Reference: PROJCS["WGS_1984_Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-78.0],PARAMETER["standard_parallel_1",27.33333333333333],PARAMETER["standard_parallel_2",40.66666666666666],PARAMETER["latitude_of_origin",34.0],UNIT["Meter",1.0]]
##
##        West Coast
##        Spatial Reference: PROJCS["WGS_1984_Albers_NMSDD",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",180.0],PARAMETER["standard_parallel_1",-2.0],PARAMETER["standard_parallel_2",49.0],PARAMETER["latitude_of_origin",25.5],UNIT["Meter",1.0]]
##
##        Gulf of Alaska
##        Spatial Reference: PROJCS["WGS_1984_Albers_NMSDD",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",180.0],PARAMETER["standard_parallel_1",-2.0],PARAMETER["standard_parallel_2",49.0],PARAMETER["latitude_of_origin",25.5],UNIT["Meter",1.0]]
##
##        Hawaii
##        Spatial Reference: PROJCS["WGS_1984_Albers_NMSDD",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",180.0],PARAMETER["standard_parallel_1",-2.0],PARAMETER["standard_parallel_2",49.0],PARAMETER["latitude_of_origin",25.5],UNIT["Meter",1.0]]


        geographic_regions = {
                            'AI'        : 'Aleutian Islands',
                            'EBS'       : 'Eastern Bering Sea, Bering Sea',
                            'GOA'       : 'Gulf of Alaska',
                            'GOM'       : 'Gulf of Mexico',
                            'GMEX'      : 'Gulf of Mexico',
                            #'HI'        : 'Hawaii Islands',
                            'HI'        : "Hawai'i Islands",
                            'NEUS_F'    : 'Northeast US, East Coast',
                            'NEUSF'     : 'Northeast US, East Coast',
                            'NEUS_S'    : 'Northeast US, East Coast',
                            'NEUS'      : 'Northeast US, East Coast',
                            'SEUS_SPR'  : 'Southeast US, East Coast',
                            'SEUS_SUM'  : 'Southeast US, East Coast',
                            'SEUS_FALL' : 'Southeast US, East Coast',
                            'SEUS_FAL'  : 'Southeast US, East Coast',
                            'WC_ANN'    : 'West Coast',
                            'WCANN'     : 'West Coast',
                            'WC_TRI'    : 'West Coast',
                            'WCTRI'     : 'West Coast',
                            'Aleutian_Islands'    : 'Aleutian Islands',
                            'Eastern_Bering_Sea'  : 'Eastern Bering Sea, Bering Sea',
                            'Gulf_of_Alaska'      : 'Gulf of Alaska',
                            'Gulf_of_Mexico'      : 'Gulf of Mexico',
                            #'Hawaii_Islands'    : 'Hawaii Islands',
                            'Hawaii_Islands'    : "Hawai'i Islands",
                            #'Northeast_US_Fall'   : 'Northeast US, East Coast',
                            'Northeast_US'   : 'Northeast US, East Coast',
                            #'Northeast_US_Spring' : 'Northeast US, East Coast',
                            'Southeast_US'        : 'Southeast US, East Coast',
                            #'Southeast_US_Summer' : 'Southeast US, East Coast',
                            'West_Coast'          : 'West Coast',

                          }
        # Set to True if we want to filter on certian one or more regions, else
        # False to process all regions
        FilterRegions = False

        if not FilterRegions:
            # ###--->>> Use a list to filter on regions.
            selected_regions = ['AI', 'EBS', 'GOA', 'GOM', 'HI', 'NEUS_F', 'NEUS_S', 'SEUS_FALL', 'SEUS_SPR', 'SEUS_SUM', 'WC_ANN', 'WC_TRI',]
        else:
            # Below are lists used to test different regions
            selected_regions = ['HI',]

        # Test if we are filtering on regions. If so, a new table_names list is
        # created with the selected regions remaining in the list
        if FilterRegions:
            # New table_names list of lists #-> https://stackoverflow.com/questions/21507319/python-list-comprehension-list-of-lists
            table_names = [[r for r in group] for group in table_names if group[2] in selected_regions]
        else:
            pass

        # Set to True if we want to filter on certian species, else False to
        # process all species
        if SoftwareEnvironmentLevel in  ["Dev", "Test"]:
            FilterSpecies = True
            if SoftwareEnvironmentLevel == "Dev":
                # TODO: Consider using sets instead
                selected_species = {
                                    # 'AI', 'Aleutian Islands'
                                    # 'EBS', 'Eastern Bering Sea'
                                    # 'GOA', 'Gulf of Alaska'
                                    # 'WC_ANN', 'West Coast Annual (2003-present)'
                                    # 'WC_TRI', 'West Coast Triennial (1977-2004)',
                                    'Acesta sphoni' : 'Limid clam sp.',
                                    'Anthopleura xanthogrammica' : 'Giant green anemone',
                                    'Citharichthys sordidus' : 'Pacific sanddab',
                                    'Doryteuthis (Loligo) opalescens' : 'California market squid',
                                    'Gadus chalcogrammus' : 'Walleye Pollock',
                                    # 'GOM', 'Gulf of Mexico'
                                    'Lutjanus campechanus' : 'red snapper',
                                    # 'HI', 'Hawaii'
                                    'Etelis coruscans' : 'Onaga',
                                    'Hyporthodus quernus' : 'HapuÊ»upuÊ»u',
                                    # 'NEUS_F', 'Northeast US Fall'
                                    # 'NEUS_S', 'Northeast US Spring'
                                    # 'SEUS_SPR', 'Southeast US Spring'
                                    # 'SEUS_SUM', 'Southeast US Summer'
                                    # 'SEUS_FALL', 'Southeast US Fall'
                                    'Centropristis striata' : 'black sea bass',
                                   }
            if SoftwareEnvironmentLevel == "Test":
                # TODO: Consider using sets instead
                selected_species = {
                                    # 'AI', 'Aleutian Islands'
                                    # 'EBS', 'Eastern Bering Sea'
                                    # 'GOA', 'Gulf of Alaska'
                                    # 'WC_ANN', 'West Coast Annual (2003-present)'
                                    # 'WC_TRI', 'West Coast Triennial (1977-2004)',
                                    'Acesta sphoni' : 'Limid clam sp.',
                                    'Anthopleura xanthogrammica' : 'Giant green anemone',
                                    'Calinaticina oldroydii' : "Oldroyd's Fragile Moon Snail",
                                    'Citharichthys sordidus' : 'Pacific sanddab',
                                    'Doryteuthis (Loligo) opalescens' : 'California market squid',
                                    'Gadus chalcogrammus' : 'Walleye Pollock',
                                    'Gadus macrocephalus' : 'Pacific Cod',
                                    'Hippoglossus stenolepis' : 'Pacific Halibut',
                                    'Limanda aspera' : 'yellowfin sole',
                                    # 'GOM', 'Gulf of Mexico'
                                    'Ancylopsetta dilecta' : 'three-eye flounder',
                                    'Ancylopsetta ommata': 'ocellated flounder',
                                    'Chicoreus florifer-dilectus' : '',
                                    'Lutjanus campechanus' : 'red snapper',
                                    'Scomberomorus maculatus' : 'Spanish Mackerel',
                                    # 'HI', 'Hawaii'
                                    'Aphareus rutilans' : 'Lehi',
                                    'Etelis carbunculus' : 'Ehu',
                                    'Etelis coruscans' : 'Onaga',
                                    'Hyporthodus quernus' : 'HapuÊ»upuÊ»u',
                                    'Pristipomoides filamentosus' : 'Opakapaka',
                                    'Pristipomoides sieboldii' : 'Kalekale',
                                    'Pristipomoides zonatus' : 'Gindai',
                                    # 'NEUS_F', 'Northeast US Fall'
                                    # 'NEUS_S', 'Northeast US Spring'
                                    'Centropristis striata' : 'black sea bass',
                                    'Geryon (Chaceon) quinquedens' : 'Red Deep Sea Crab',
                                    'Homarus americanus' : 'American Lobster',
                                    # 'SEUS_SPR', 'Southeast US Spring'
                                    # 'SEUS_SUM', 'Southeast US Summer'
                                    # 'SEUS_FALL', 'Southeast US Fall'
                                    'Brevoortia tyrannus' : 'Atlantic menhaden',
                                    'Micropogonias undulatus' : 'Atlantic croaker',
                                    'Rachycentron canadum' : 'Cobia',
                                   }
        else:
            FilterSpecies = False
            selected_species = {}


##    Ancylopsetta dilecta
##    Ancylopsetta ommata
##    Brevoortia tyrannus
##    Calinaticina oldroydii
##    Centropristis striata
##    Chicoreus florifer-dilectus
##    Gadus chalcogrammus
##    Gadus macrocephalus
##    Geryon (Chaceon) quinquedens
##    Hippoglossus stenolepis
##    Homarus americanus
##    Limanda aspera
##    Lutjanus campechanus
##    Micropogonias undulatus
##    Rachycentron canadum
##    Scomberomorus maculatus

# 'Ammodytes sp.', 'Aphroditidae spp.', 'Calinaticina oldroydii', 'Gadus chalcogrammus', 'Gadus macrocephalus', 'Hippoglossus stenolepis', 'Ancylopsetta dilecta', 'Ancylopsetta ommata', 'Lutjanus campechanus', 'Scomberomorus maculatus', 'Centropristis striata', 'Geryon quinquedens', 'Homarus americanus', 'Myctophidae spp.', 'Brevoortia tyrannus', 'Micropogonias undulatus','Rachycentron'

        # Set to True if we want to filter on certian years, else False to
        # process all years
        FilterYears = False
        #selected_years = [2008, 2009]
        year_min = 1983
        year_max = 1987
        selected_years = [yr for yr in range(year_min, year_max+1)]
        del year_min, year_max

        # TODO: Explain how to use the True/False filters

        # Main function (doesn't do anything yet)
        # main()

        # If ClearLogDirectory True or False
        ClearLogDirectory = True

    # ###--->>> Step #1
    # ###--->>> Project Setup Start
        # Project Setup True or False
        ProjectSetup = False
        ReplaceProject = False
        # Project Setup -- Needs to run first to create folders and stuff
        if ProjectSetup:
            projectSetup()
        del ProjectSetup, ReplaceProject, projectSetup
    # ###--->>> Project Setup End

    # ###--->>> Step #2
    # ###--->>> importEPU Start
        ImportEPU = False

        if ImportEPU:
            importEPU()

        del ImportEPU, importEPU

    # ###--->>> importEPU End

    # ###--->>> Step #3
    # ###--->>> Tables Start
        # Create Tables: True or False
        CreateTemplateTables = False
        # Replace Tables: True or False
        ReplaceTables = True
        # Filter out tables to process: True or False
        FilterTables = False

        # Selected tables to process, instead of processing all tables
        # selected_tables = ["DataSeries_Template", "SpeciesRegionSeason_Template", "Indicators_Template", "AreaAnalysis_Template", "Areas_Template",]
        #selected_tables = ["Indicators_Template"]
        # selected_tables = ["Indicators_Template", "AreaAnalysis_Template", "Areas_Template",]
        # selected_tables = ["DataSeries_Template",]
        selected_tables = ["Indicators_Template", "RegionSpeciesYearImageName_Template"]

        # Create empty tables, if CreateTemplateTables is set to True
        if CreateTemplateTables:
            createTemplateTables()

        del createTemplateTables, CreateTemplateTables, ReplaceTables, FilterTables, selected_tables

    # ###--->>> Tables End

    # ###--->>> Step #4
    # ###--->>> Import CSV Tables Start
        # Generate Tables True or False
        GenerateTables = True
        # Tables
        # Set ReplaceTable to True or False
        ReplaceTable = True
        # Generate Tables -- Needs to run next so that
        # Feature classes can be created in the following step.
        if GenerateTables:
            generateTables()
        del GenerateTables
    # ###--->>> Import CSV Tables End

    # ###--->>> Step #5
    # ###--->>> Populate Region Species Year Image Name Table Start

        # Populate Species Region Season Table
        PopulateRegionSpeciesYearImageName = False

        if PopulateRegionSpeciesYearImageName:
            populateRegionSpeciesYearImageName()

        del populateRegionSpeciesYearImageName
        del PopulateRegionSpeciesYearImageName

    # ###--->>> Populate Region Species Year Image Name Table End

    # ###--->>> Step #6
    # ###--->>> Generate Point Feature Classes Start
        # Generate Point Feature Classes True or False
        GeneratePointFeatureClasses = False
        # Feature Classes
        # Set ReplaceFeatureClass to True or False
        ReplaceFeatureClass = True
        # Generate Point Feature Classes -- Needs to run next so that
        # Rasters can be created for the following step.
        if GeneratePointFeatureClasses:
            generatePointFeatureClasses()

    # ###--->>>  Generate Point Feature Classes End

    # ###--->>> Step #7
    # ###--->>> Create Snap Raster, Bathymetry, Latitude, Longitude Start
    # #### Need to create  bathy first

        CreateSnapRasterBathymetryLatitudeLongitude = False

        if CreateSnapRasterBathymetryLatitudeLongitude:
            createSnapRasterBathymetryLatitudeLongitude()

        del CreateSnapRasterBathymetryLatitudeLongitude, createSnapRasterBathymetryLatitudeLongitude

        GetRowColumnCountReport = False
        if GetRowColumnCountReport:
            getRowColumnCountReport()
        del GetRowColumnCountReport, getRowColumnCountReport

    # ###--->>> Create Snap Raster, Bathymetry, Latitude, Longitude End

    # ###--->>> Step #8
    # ###--->>> Create DisMAP Regions Start

        # Remember to select all regions
        CreateDisMapRegions = False
        if CreateDisMapRegions:
            createDisMapRegions()
        del CreateDisMapRegions, createDisMapRegions

    # ###--->>> Create DisMAP Regions End

    # ###--->>> Step #9
    # ###--->>> Rasters Start

        # Generate Rasters True or False
        GenerateRasters = False
        # Rasters
        # Change idw_field
        # idw_field = "WTCPUE" or "WTCPUECubeRoot"
        idw_field = "WTCPUECubeRoot"

        # Set ReplaceRaster to True or False
        ReplaceRaster = True

        # Set ReplaceLayer to True or False
        #ReplaceLayer = True

        # Generate Rasters -- Needs to run next so that Mosaics can be
        # created for the following step.
        if GenerateRasters:
            generateRasters()
        #del ReplaceLayer

    # ###--->>> Rasters End

    # ###--->>> Step #10
    # ###--->>> Indicators Table Start

        # Populate Indicators Table True or False
        CreateIndicatorsTable = False

        # Replace Region Indicator Datasets True or False
        ReplaceRegionIndicatorTable = True

        # Replace Indicator Datasets True or False
        ReplaceIndicatorTable = False

        if CreateIndicatorsTable:
            createIndicatorsTable()

        del CreateIndicatorsTable, ReplaceIndicatorTable, createIndicatorsTable
        del ReplaceRegionIndicatorTable

    # ###--->>> Indicators Table End

##        # ###--->>> Create sample Indicators Dev table Start
##        # Create Center of Gravity True or False
##        # PopulateIndicatorsTableDev = False
##        # if PopulateIndicatorsTableDev:
##        #     createIndicatorsTableDev()
##        # del createIndicatorsTableDev, PopulateIndicatorsTableDev
##        # ###--->>> Create sample Indicators Dev table Start
##
##
##        # Testing, Testing . . . anyone there?
##        # queryTable()
##        # del queryTable
##
##    # ###--->>> Tables End

    # ###--->>> Step #11
    # ###--->>> Mosaics Start

        # Generate Mosaics or False
        GenerateMosaics = False

        # Overwrite Mosaic Datasets
        ReplaceMosaicDatasets = True

        # Generate Mosaics -- Needs to run next so that ??? can be
        # created for the following step.
        if GenerateMosaics:
            generateMosaics()

        del GenerateMosaics, ReplaceMosaicDatasets, generateMosaics

    # ###--->>> Mosaics End

    # ###--->>>
        #queryYears()
        #del queryYears
    # ###--->>>

    # ###--->>> Step #12
    # ###--->>> Richness Start

        # CreateRichnessRasters = True or False
        CreateRichnessRasters = False
        CreateCoreSpeciesRichnessRasters = False

        # Replace Region Year Richness = True or False
        ReplaceRegionYearRichness = True

        # Replace the Richness Mosaic = True or False
        # #ReplaceRichnessMosaic = False

        if CreateRichnessRasters:
            createSpeciesRichnessRasters()

        if CreateCoreSpeciesRichnessRasters:
            createCoreSpeciesRichnessRasters()

        del CreateRichnessRasters, createSpeciesRichnessRasters, createCoreSpeciesRichnessRasters

    # ###--->>> Richness End

    # ###--->>> Step #13
    # ###--->>>  Set Mosaic Dataset Properties Start

        SetMosaicDatasetProperties = False

        if SetMosaicDatasetProperties:
            setMosaicDatasetProperties()

        del SetMosaicDatasetProperties, setMosaicDatasetProperties

    # ###--->>> CreateCloudRasterFormatExport End

    # ###--->>> Step #14
    # ###--->>> BuildMultidimensionalInfo Start

        BuildMultidimensionalInfo = False

        if BuildMultidimensionalInfo:
            buildMultidimensionalInfo()

        del buildMultidimensionalInfo, BuildMultidimensionalInfo

    # ###--->>> BuildMultidimensionalInfo End

    # ###--->>> Step #15
    # ###--->>> AnalyzeMosaicDataset Start

        AnalyzeMosaicDataset = False

        if AnalyzeMosaicDataset:
            analyzeMosaicDataset()

        del AnalyzeMosaicDataset, analyzeMosaicDataset

    # ###--->>> AnalyzeMosaicDataset End

    # ###--->>> Step #16
    # ###--->>> CreateCloudRasterFormatExport Start

        CreateCloudRasterFormatExport = False

        if CreateCloudRasterFormatExport:
            createCloudRasterFormatExport()

        del CreateCloudRasterFormatExport, createCloudRasterFormatExport

    # ###--->>> CreateCloudRasterFormatExport End

    # ###--->>> Step #17
    # ###--->>> Table and Field Report Start

        TableAndFieldReport = False
        ws = ProjectGDB
        wc = "HI_CSV"
        #wc = ""
        # dt = ["Any",]
        #dt = ["Any",]
        dt = ["Table", "FeatureClass"]
        t = ["Any",]
        #t = ["Polygon",]

        if TableAndFieldReport:
            tableAndFieldReport(ws, wc, dt, t)

        del tableAndFieldReport, TableAndFieldReport, ws, wc, dt, t

    # ###--->>> Table and Field Report End

    # ###--->>> Step #18
    # ###--->>> Compact Project GDB Start

        CompactProjectGDB = True

        if CompactProjectGDB:

            print(">-> arcpy.management.Compact")
            arcpy.management.Compact(ProjectGDB)
            msg = arcpy.GetMessages()
            msg = ">->-> {0}".format(msg.replace('\n', '\n>->-> '))
            print(msg); del msg

        del CompactProjectGDB

    # ###--->>> Compact Project GDB End

    # ###--->>> Clean up

        del table_names, srs
        del selected_regions, ProjectName, ProjectGIS, ProjectGDB, ProjectToolBox
        #del DefaultGDB
        del BASE_DIRECTORY, ANALYSIS_DIRECTORY, CSV_DIRECTORY, MAP_DIRECTORY
        del EXPORT_METADATA_DIRECTORY, ARCGIS_METADATA_DIRECTORY, INPORT_METADATA_DIRECTORY
        del MOSAIC_DIRECTORY, LOG_DIRECTORY, logFile
        del DEBUG_OUTPUT, unique_field, unique_fish, unique_year, selected_species
        del select_by_fish, select_by_fish_no_years, DEBUG_LEVEL
        del FilterRegions, FilterSpecies, FilterYears, selected_years
        del ClearLogDirectory
        del print_function, reorder_fields, generateRasters
        del generatePointFeatureClasses, ReplaceTable, ReplaceFeatureClass
        del ReplaceRaster, generateTables
        del unique_fish_dict
        del idw_field, cell_size
        del GeneratePointFeatureClasses, GenerateRasters
        del queryTable
        del queryYears, ScratchGDB, ScratchFolder
        del getRowColumnCount
        del unique_years
        del ReplaceRegionYearRichness
        del SoftwareEnvironmentLevel
        del getDepthSummaryStatisticsReport
        del BathymetryGDB
        del unique_values, CreateCoreSpeciesRichnessRasters
        del Version, DateCode
        del md
        del geographic_regions
        #del generateMaps
        #del convertRastersToPoints
        del inspect, functionName, function_name
        del addMetadata

        #arcpy.env.workspace = tmp_workspace; del tmp_workspace

        #arcpy.env.scratchWorkspace = tmp_scratchWorkspace; del tmp_scratchWorkspace


        arcpy.ResetEnvironments()

        #Final benchmark for the region.
        msg = "PROGRAM COMPLETED ON {}".format(strftime("%a %b %d %I:%M:%S %p", localtime()))
        print(msg)

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        msg = u"Elapsed Time {0} (H:M:S)\n".format(strftime("%H:%M:%S", gmtime(elapse_time)))
        print(msg)
        del msg, start_time, end_time, elapse_time

        globalKeys = [key for key in globals().keys() if not key.startswith('__') and key not in exclude_keys]

        if globalKeys:
            #msg = "Global Keys: {0}".format(u", ".join(globalKeys))
            msg = "Global Keys: {0}".format(u', '.join('"{0}"'.format(gk) for gk in globalKeys))
            print(msg)
            #print(globalKeys)
            del msg
        del globalKeys

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)
        del pymsg, tb, tbinfo
