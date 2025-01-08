# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        create_region_fishnets_worker.py
# Purpose:
#
# Author:      john.f.kennedy
#
# Created:     25/02/2024
# Copyright:   (c) john.f.kennedy 2024
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os, sys # built-ins first
import traceback
import importlib
import inspect

import arcpy # third-parties second

sys.path.append(os.path.dirname(__file__))

def line_info(msg):
    f = inspect.currentframe()
    i = inspect.getframeinfo(f.f_back)
    return f"Script: {os.path.basename(i.filename)}\n\tNear Line: {i.lineno}\n\tFunction: {i.function}\n\tMessage: {msg}"

def worker(region_gdb=""):
    try:
        # Test if passed workspace exists, if not raise SystemExit
        if not arcpy.Exists(rf"{region_gdb}"):
            raise SystemExit(line_info(f"{os.path.basename(region_gdb)} is missing!!"))

        import dismap
        importlib.reload(dismap)
        from dismap import check_transformation

        # Reset environment settings to default settings.
        arcpy.ResetEnvironments()

        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(1) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        table_name      = os.path.basename(region_gdb).replace(".gdb","")
        scratch_folder  = os.path.dirname(region_gdb)
        project_folder  = os.path.dirname(scratch_folder)
        scratch_workspace = rf"{scratch_folder}\{table_name}\scratch.gdb"

        arcpy.AddMessage(f"Table Name: {table_name}\nProject Folder: {project_folder}\nScratch Folder: {scratch_folder}\n")

        del scratch_folder, project_folder

        arcpy.env.workspace                 = region_gdb
        arcpy.env.scratchWorkspace          = scratch_workspace
        arcpy.env.overwriteOutput           = True
        arcpy.env.parallelProcessingFactor  = "100%"
        arcpy.env.compression               = "LZ77"
        #arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"
        arcpy.env.pyramid                   = "PYRAMIDS -1 BILINEAR DEFAULT 75 NO_SKIP NO_SIPS"
        arcpy.env.resamplingMethod          = "BILINEAR"
        arcpy.env.rasterStatistics          = 'STATISTICS 1 1'
        #arcpy.env.XYTolerance               = "0.1 Meters"
        #arcpy.env.XYResolution              = "0.01 Meters"

        # DatasetCode, CSVFile, TransformUnit, TableName, GeographicArea, CellSize,
        # PointFeatureType, FeatureClassName, Region, Season, DateCode, Status,
        # DistributionProjectCode, DistributionProjectName, SummaryProduct,
        # FilterRegion, FilterSubRegion, FeatureServiceName, FeatureServiceTitle,
        # MosaicName, MosaicTitle, ImageServiceName, ImageServiceTitle

        fields = ["TableName", "CellSize",]
        region_list = [row for row in arcpy.da.SearchCursor(rf"{region_gdb}\Datasets", fields, where_clause = f"TableName = '{table_name}'")][0]
        del fields

        # Assigning variables from items in the chosen table list
        # ['AI_IDW', 'AI_IDW_Region', 'AI', 'Aleutian Islands', None, 'IDW']
        table_name      = region_list[0]
        cell_size       = region_list[1]
        del region_list

        process_region       = rf"{region_gdb}\{table_name}_Region"
        region_raster_mask   = rf"{table_name}_Raster_Mask"
        region_extent_points = rf"{table_name}_Extent_Points"
        region_fishnet       = rf"{table_name}_Fishnet"
        region_lat_long      = rf"{table_name}_Lat_Long"
        region_latitude      = rf"{table_name}_Latitude"
        region_longitude     = rf"{table_name}_Longitude"
        region_name          = rf"{table_name}_Region"

        arcpy.AddMessage(f"Region: {region_name}")
        arcpy.AddMessage(f"Region GDB: {arcpy.env.workspace}")
        arcpy.AddMessage(f"Region GDB: {arcpy.env.scratchWorkspace}")

        psr = arcpy.Describe(process_region).spatialReference
        arcpy.env.outputCoordinateSystem = psr
        arcpy.AddMessage(f"\t\tSpatial Reference: {psr.name}")
        # Set coordinate system of the output fishnet
        # 4326 - World Geodetic System 1984 (WGS 84) and 3857 - Web Mercator
        # Spatial Reference factory code of 4326 is : GCS_WGS_1984
        # Spatial Reference factory code of 5714 is : Mean Sea Level (Height)
        # sr = arcpy.SpatialReference(4326, 5714)
        #gsr = arcpy.SpatialReference(4326, 5714)
        gsr = arcpy.SpatialReference(4326)

##        arcpy.AddMessage("process_region")
##        arcpy.AddMessage(f"Spatial Reference: {str(arcpy.Describe(process_region).spatialReference.name)}")
##        arcpy.AddMessage(f"Extent:            {str(arcpy.Describe(process_region).extent).replace(' NaN', '')}")
##        arcpy.AddMessage(f"Output Coordinate System:   {arcpy.env.outputCoordinateSystem.name}")
##        arcpy.AddMessage(f"Geographic Transformations: {arcpy.env.geographicTransformations}")

        # Creating Raster Mask
        arcpy.AddMessage(f"Creating Raster Mask: {table_name}_Raster_Mask")

        cell_size = [row[0] for row in arcpy.da.SearchCursor(rf"{region_gdb}\Datasets", "CellSize", where_clause = f"GeographicArea = '{region_name}'")][0]

        arcpy.management.CalculateField(rf"{process_region}", "ID", 1)
        arcpy.AddMessage("\tCalculate Field 'ID' for {0}:\n\t\t{1}\n".format(f"{region_name}", arcpy.GetMessages(0).replace("\n", "\n\t\t")))

        arcpy.conversion.FeatureToRaster(rf"{process_region}", "ID", rf"{region_gdb}\{region_raster_mask}", cell_size)
        arcpy.AddMessage("\tFeature To Raster for {0}:\n\t\t{1}\n".format(f"{region_name}", arcpy.GetMessages(0).replace("\n", "\n\t\t")))

        arcpy.management.DeleteField(rf"{process_region}", "ID")
        arcpy.AddMessage("\tDelete Field 'ID' field in {0}:\n\t\t{1}\n".format(f"{region_name}", arcpy.GetMessages(0).replace("\n", "\n\t\t")))

        #del edit

        # Creating Extent Points
        arcpy.AddMessage(f"Creating Extent Points: {region_extent_points}")

        extent   = arcpy.Describe(process_region).extent
        X_Min, Y_Min, X_Max, Y_Max = extent.XMin, extent.YMin, extent.XMax, extent.YMax
        del extent

        arcpy.AddMessage(f"\t{region_name} Extent:\n\t\tX_Min: {X_Min}\n\t\tY_Min: {Y_Min}\n\t\tX_Max: {X_Max}\n\t\tY_Max: {Y_Max}\n")

        # A list of coordinate pairs
        pointList = [[X_Min, Y_Min], [X_Min, Y_Max], [X_Max, Y_Max]]
        # Create an empty Point object
        point = arcpy.Point()
        # A list to hold the PointGeometry objects
        pointGeometryList = []
        # For each coordinate pair, populate the Point object and create a new
        # PointGeometry object
        for pt in pointList:
            point.X = pt[0]
            point.Y = pt[1]
            pointGeometry = arcpy.PointGeometry(point, arcpy.Describe(process_region).spatialReference)
            pointGeometryList.append(pointGeometry)
            del pt, pointGeometry
        # Delete after last use
        del pointList, point

        # Create a copy of the PointGeometry objects, by using pointGeometryList as
        # input to the CopyFeatures tool.
        arcpy.management.CopyFeatures(pointGeometryList, rf"{region_gdb}\{region_extent_points}")
        arcpy.AddMessage("\tCopy Features to {0}:\n\t\t{1}\n".format(region_extent_points, arcpy.GetMessages(0).replace("\n", "\n\t\t")))

        del pointGeometryList

 #        arcpy.AddMessage("tmp_region_extent_points")
 #        tmp_region_extent_points = rf"{region_gdb}\{region_extent_points}"
 #        arcpy.AddMessage(f"Spatial Reference: {str(arcpy.Describe(tmp_region_extent_points).spatialReference.name)}")
 #        arcpy.AddMessage(f"Extent:            {str(arcpy.Describe(tmp_region_extent_points).extent).replace(' NaN', '')}")
 #        arcpy.AddMessage(f"Output Coordinate System:   {arcpy.env.outputCoordinateSystem.name}")
 #        arcpy.AddMessage(f"Geographic Transformations: {arcpy.env.geographicTransformations}")
 #        del tmp_region_extent_points

        with arcpy.EnvManager(outputCoordinateSystem = psr):
            arcpy.management.AddXY(in_features = rf"{region_gdb}\{region_extent_points}")
            arcpy.AddMessage("\tAdd XY:\n\t\t{0}\n".format(arcpy.GetMessages(0).replace("\n", "\n\t\t")))

        arcpy.management.AlterField(
                                    in_table          = rf"{region_gdb}\{region_extent_points}",
                                    field             = "POINT_X",
                                    new_field_name    = "Easting",
                                    new_field_alias   = "Easting",
                                    field_type        = "",
                                    field_length      = None,
                                    field_is_nullable = "NULLABLE",
                                    clear_field_alias = "DO_NOT_CLEAR"
                                   )
        arcpy.AddMessage("\tAlter Field:\n\t\t{0}\n".format(arcpy.GetMessages(0).replace("\n", "\n\t\t")))

        arcpy.management.AlterField(
                                    in_table          = rf"{region_gdb}\{region_extent_points}",
                                    field             = "POINT_Y",
                                    new_field_name    = "Northing",
                                    new_field_alias   = "Northing",
                                    field_type        = "",
                                    field_length      = None,
                                    field_is_nullable = "NULLABLE",
                                    clear_field_alias = "DO_NOT_CLEAR"
                                   )
        arcpy.AddMessage("\tAlter Field:\n\t\t{0}\n".format(arcpy.GetMessages(0).replace("\n", "\n\t\t")))

        tmp_outputCoordinateSystem = arcpy.env.outputCoordinateSystem
        arcpy.env.outputCoordinateSystem = gsr

        with arcpy.EnvManager(outputCoordinateSystem = gsr, geographicTransformations = check_transformation(rf"{region_gdb}\{region_extent_points}", gsr)):
            arcpy.management.AddXY(in_features = rf"{region_gdb}\{region_extent_points}")
            arcpy.AddMessage("\tAdd XY:\n\t\t{0}\n".format(arcpy.GetMessages(0).replace("\n", "\n\t\t")))

        arcpy.env.outputCoordinateSystem = tmp_outputCoordinateSystem
        del tmp_outputCoordinateSystem

        arcpy.management.AlterField(
                                    in_table          = rf"{region_gdb}\{region_extent_points}",
                                    field             = "POINT_X",
                                    new_field_name    = "Longitude",
                                    new_field_alias   = "Longitude",
                                    field_type        = "",
                                    field_length      = None,
                                    field_is_nullable = "NULLABLE",
                                    clear_field_alias = "DO_NOT_CLEAR"
                                   )
        arcpy.AddMessage("\tAlter Field:\n\t\t{0}\n".format(arcpy.GetMessages(0).replace("\n", "\n\t\t")))

        arcpy.management.AlterField(
                                    in_table          = rf"{region_gdb}\{region_extent_points}",
                                    field             = "POINT_Y",
                                    new_field_name    = "Latitude",
                                    new_field_alias   = "Latitude",
                                    field_type        = "",
                                    field_length      = None,
                                    field_is_nullable = "NULLABLE",
                                    clear_field_alias = "DO_NOT_CLEAR"
                                   )
        arcpy.AddMessage("\tAlter Field:\n\t\t{0}\n".format(arcpy.GetMessages(0).replace("\n", "\n\t\t")))

        # Creating Fishnet
        arcpy.AddMessage(f"Creating Fishnet: {region_fishnet}")
        arcpy.AddMessage(f"\tCreate Fishnet for {region_name} with {cell_size} by {cell_size} cells")
        arcpy.management.CreateFishnet(
                                       os.path.join(rf"{region_gdb}\{region_fishnet}"),
                                       f"{X_Min} {Y_Min}",
                                       f"{X_Min} {Y_Max}",
                                       cell_size,
                                       cell_size,
                                       None,
                                       None,
                                       f"{X_Max} {Y_Max}",
                                       "NO_LABELS",
                                       "DEFAULT",
                                       "POLYGON"
                                      )
        arcpy.AddMessage("\tCreate Fishnet for {0}:\n\t\t{1}\n".format(f"{region_name}", arcpy.GetMessages(0).replace("\n", "\n\t\t")))

        del X_Min, Y_Min, X_Max, Y_Max

        arcpy.management.MakeFeatureLayer(rf"{region_gdb}\{region_fishnet}", f"{region_name}_Fishnet_Layer")
        arcpy.AddMessage("\tMake Feature Layer for {0}:\n\t\t{1}\n".format(f"{region_fishnet}", arcpy.GetMessages(0).replace("\n", "\n\t\t")))
        arcpy.AddMessage(f"\t\tRecord Count: {int(arcpy.management.GetCount(f'{region_name}_Fishnet_Layer')[0]):,d}")

        arcpy.management.SelectLayerByLocation(f"{region_name}_Fishnet_Layer", "WITHIN_A_DISTANCE", process_region, 2 * int(cell_size), "NEW_SELECTION", "INVERT")
        arcpy.AddMessage("\tSelect Layer By Location:\n\t\t{0}\n".format(arcpy.GetMessages(0).replace("\n", "\n\t\t")))
        arcpy.AddMessage(f"\t\tRecord Count: {int(arcpy.management.GetCount(f'{region_name}_Fishnet_Layer')[0]):,d}")

        arcpy.management.DeleteFeatures(f"{region_name}_Fishnet_Layer")
        arcpy.AddMessage("\tDelete Features:\n\t\t{0}\n".format(arcpy.GetMessages(0).replace("\n", "\n\t\t")))

        arcpy.management.Delete(f"{region_name}_Fishnet_Layer")
        arcpy.AddMessage("\tDelete {0}:\n\t\t{1}\n".format(f"{region_name}_Fishnet_Layer", arcpy.GetMessages(0).replace("\n", "\n\t\t")))

        # Creating Lat-Long
        arcpy.AddMessage(f"Creating Lat-Long: {region_lat_long}")
        arcpy.management.FeatureToPoint(rf"{region_gdb}\{region_fishnet}", rf"{region_gdb}\{region_lat_long}", "CENTROID")
        arcpy.AddMessage("\tFeature To Point:\n\t\t{0}\n".format(arcpy.GetMessages(0).replace("\n", "\n\t\t")))

        # Execute DeleteField
        arcpy.management.DeleteField(rf"{region_gdb}\{region_lat_long}", ['ORIG_FID'])
        arcpy.AddMessage("\tDelete Field:\n\t\t{0}\n".format(arcpy.GetMessages(0).replace("\n", "\n\t\t")))

        with arcpy.EnvManager(outputCoordinateSystem = psr):
            arcpy.management.AddXY(in_features=rf"{region_gdb}\{region_lat_long}")
            arcpy.AddMessage("\tAdd XY:\n\t\t{0}\n".format(arcpy.GetMessages(0).replace("\n", "\n\t\t")))

            arcpy.management.AlterField(
                                        in_table          = rf"{region_gdb}\{region_lat_long}",
                                        field             = "POINT_X",
                                        new_field_name    = "Easting",
                                        new_field_alias   = "Easting",
                                        field_type        = "",
                                        field_length      = None,
                                        field_is_nullable = "NULLABLE",
                                        clear_field_alias = "DO_NOT_CLEAR"
                                       )
            arcpy.AddMessage("\tAlter Field:\n\t\t{0}\n".format(arcpy.GetMessages(0).replace("\n", "\n\t\t")))

            arcpy.management.AlterField(
                                        in_table          = rf"{region_gdb}\{region_lat_long}",
                                        field             = "POINT_Y",
                                        new_field_name    = "Northing",
                                        new_field_alias   = "Northing",
                                        field_type        = "",
                                        field_length      = None,
                                        field_is_nullable = "NULLABLE",
                                        clear_field_alias = "DO_NOT_CLEAR"
                                       )
            arcpy.AddMessage("\tAlter Field:\n\t\t{0}\n".format(arcpy.GetMessages(0).replace("\n", "\n\t\t")))

        with arcpy.EnvManager(outputCoordinateSystem = gsr, geographicTransformations = check_transformation(rf"{region_gdb}\{region_extent_points}", gsr)):
            arcpy.management.AddXY(in_features=rf"{region_gdb}\{region_lat_long}")
            arcpy.AddMessage("\tAdd XY:\n\t\t{0}\n".format(arcpy.GetMessages(0).replace("\n", "\n\t\t")))

            arcpy.management.AlterField(
                                        in_table          = rf"{region_gdb}\{region_lat_long}",
                                        field             = "POINT_X",
                                        new_field_name    = "Longitude",
                                        new_field_alias   = "Longitude",
                                        field_type        = "",
                                        field_length      = None,
                                        field_is_nullable = "NULLABLE",
                                        clear_field_alias = "DO_NOT_CLEAR"
                                       )
            arcpy.AddMessage("\tAlter Field:\n\t\t{0}\n".format(arcpy.GetMessages(0).replace("\n", "\n\t\t")))

            arcpy.management.AlterField(
                                        in_table          = rf"{region_gdb}\{region_lat_long}",
                                        field             = "POINT_Y",
                                        new_field_name    = "Latitude",
                                        new_field_alias   = "Latitude",
                                        field_type        = "",
                                        field_length      = None,
                                        field_is_nullable = "NULLABLE",
                                        clear_field_alias = "DO_NOT_CLEAR"
                                       )
            arcpy.AddMessage("\tAlter Field:\n\t\t{0}\n".format(arcpy.GetMessages(0).replace("\n", "\n\t\t")))

 #        arcpy.management.CalculateFields(
 #                                         in_table        = rf"{region_gdb}\{region_lat_long}",
 #                                         expression_type = "PYTHON3",
 #                                         fields          = "Easting 'round(!Easting!, 8)' #;Northing 'round(!Northing!, 8)' #;Longitude 'round(!Longitude!, 8)' #;Latitude 'round(!Latitude!, 8)' #",
 #                                         code_block      = "",
 #                                         enforce_domains = "NO_ENFORCE_DOMAINS"
 #                                        )
 #        arcpy.AddMessage("\tCalculate Fields:\n\t\t{0}\n".format(arcpy.GetMessages(0).replace("\n", "\n\t\t")))

        arcpy.AddMessage(f"Generating {table_name} Latitude and Longitude Rasters")

 #        arcpy.env.cellSize   = cell_size
 #        arcpy.env.extent     = arcpy.Describe(rf"{region_gdb}\{region_raster_mask}").extent
 #        arcpy.env.mask       = rf"{region_gdb}\{region_raster_mask}"
 #        arcpy.env.snapRaster = rf"{region_gdb}\{region_raster_mask}"

        raster_mask_extent = arcpy.Describe(rf"{region_gdb}\{region_raster_mask}").extent

        arcpy.AddMessage(f"Point to Raster Conversion using {region_lat_long} to create {region_longitude}")

        #region_longitude_tmp = rf"memory\tmp_{region_longitude}"
        region_longitude_tmp = rf"{region_gdb}\tmp_{region_longitude}"

        with arcpy.EnvManager(scratchWorkspace=scratch_workspace, workspace = region_gdb, cellSize = cell_size, extent = raster_mask_extent, mask = rf"{region_gdb}\{region_raster_mask}", snapRaster = rf"{region_gdb}\{region_raster_mask}"):
            arcpy.conversion.PointToRaster(rf"{region_gdb}\{region_lat_long}", "Longitude", region_longitude_tmp, "MOST_FREQUENT", "NONE", cell_size)
            arcpy.AddMessage("\tPoint To Raster:\n\t\t{0}\n".format(arcpy.GetMessages(0).replace("\n", "\n\t\t")))

        arcpy.AddMessage(f"Extract by Mask to create {region_longitude}")

        with arcpy.EnvManager(scratchWorkspace=scratch_workspace, workspace = region_gdb,
                              cellSize = cell_size, extent = raster_mask_extent,
                              mask       = rf"{region_gdb}\{region_raster_mask}",
                              snapRaster = rf"{region_gdb}\{region_raster_mask}"):
            # Execute ExtractByMask
            outExtractByMask = arcpy.sa.ExtractByMask(region_longitude_tmp, rf"{region_gdb}\{region_raster_mask}", "INSIDE")
            arcpy.AddMessage("\tExtract By Mask:\n\t\t{0}\n".format(arcpy.GetMessages(0).replace("\n", "\n\t\t")))
            # Save the output
            outExtractByMask.save(rf"{region_gdb}\{region_longitude}")
            del outExtractByMask

        arcpy.management.Delete(region_longitude_tmp)
        del region_longitude_tmp

        #region_latitude_tmp = rf"memory\tmp_{region_latitude}"
        region_latitude_tmp = rf"{region_gdb}\tmp_{region_latitude}"

        arcpy.AddMessage(f"Point to Raster Conversion using {region_lat_long} to create {region_latitude}")

        with arcpy.EnvManager(scratchWorkspace=scratch_workspace, workspace = region_gdb,
                              cellSize = cell_size, extent = raster_mask_extent,
                              mask       = rf"{region_gdb}\{region_raster_mask}",
                              snapRaster = rf"{region_gdb}\{region_raster_mask}"):
            # Process: Point to Raster Latitude
            arcpy.conversion.PointToRaster(rf"{region_gdb}\{region_lat_long}", "Latitude", region_latitude_tmp, "MOST_FREQUENT", "NONE", cell_size, "BUILD")
            arcpy.AddMessage("\tPoint To Raster:\n\t\t{0}\n".format(arcpy.GetMessages(0).replace("\n", "\n\t\t")))

        arcpy.AddMessage(f"Extract by Mask to create {region_latitude}")

        with arcpy.EnvManager(scratchWorkspace=scratch_workspace, workspace = region_gdb, cellSize = cell_size, extent = raster_mask_extent, mask = rf"{region_gdb}\{region_raster_mask}", snapRaster = rf"{region_gdb}\{region_raster_mask}"):
            # Execute ExtractByMask
            outExtractByMask = arcpy.sa.ExtractByMask(region_latitude_tmp, rf"{region_gdb}\{region_raster_mask}", "INSIDE")
            arcpy.AddMessage("\tExtract By Mask:\n\t\t{0}\n".format(arcpy.GetMessages(0).replace("\n", "\n\t\t")))
            # Save the output
            outExtractByMask.save(rf"{region_gdb}\{region_latitude}")
            del outExtractByMask

        arcpy.management.Delete(region_latitude_tmp)
        del region_latitude_tmp

        del raster_mask_extent

        arcpy.ClearEnvironment("cellSize")
        arcpy.ClearEnvironment("extent")
        arcpy.ClearEnvironment("mask")
        arcpy.ClearEnvironment("snapRaster")

        # Reset environment settings to default settings.
        arcpy.ResetEnvironments()

        arcpy.AddMessage(f"Compacting the {os.path.basename(region_gdb)} GDB")
        arcpy.management.Compact(region_gdb)
        arcpy.AddMessage("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))

        results = [rf"{region_gdb}\{region_raster_mask}",
                   rf"{region_gdb}\{region_extent_points}",
                   rf"{region_gdb}\{region_fishnet}",
                   rf"{region_gdb}\{region_lat_long}",
                   rf"{region_gdb}\{region_latitude}",
                   rf"{region_gdb}\{region_longitude}",
                  ]

        del region_raster_mask, region_extent_points, region_fishnet
        del region_lat_long, region_latitude, region_longitude

        del psr, gsr
        del cell_size

        # End of business logic for the worker function
        arcpy.AddMessage(f"Processing for: {table_name} complete")

        # Imports
        del dismap, check_transformation

        # Variables for this function only
        del process_region, region_name
        # Basic variables
        del table_name, scratch_workspace
        # Function parameter
        del region_gdb

    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(str(traceback.print_exc()) + arcpy.GetMessages())
        raise SystemExit
    except arcpy.ExecuteError:
        arcpy.AddError(str(traceback.print_exc()) + arcpy.GetMessages())
        raise SystemExit
    except SystemExit as se:
        arcpy.AddError(str(se))
        raise SystemExit
    except:
        arcpy.AddError(str(traceback.print_exc()))
        raise SystemExit
    else:
        try:
            leave_out_keys = ["leave_out_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys
            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
        except:
            raise SystemExit(str(traceback.print_exc()))
    finally:
        if "results" in locals().keys(): del results

def main(project):
    try:
        # Imports
        from create_region_fishnets_worker import worker

        # Set basic arcpy.env variables
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        # Set varaibales
        base_project_folder = os.path.dirname(os.path.dirname(__file__))
        project_gdb    = rf"{base_project_folder}\{project}\{project}.gdb"
        project_folder = rf"{base_project_folder}\{project}"
        scratch_folder = rf"{project_folder}\Scratch"
        del project_folder, base_project_folder

        # Test if passed workspace exists, if not raise SystemExit
        if not arcpy.Exists(project_gdb):
            raise SystemExit(line_info(f"{os.path.basename(project_gdb)} is missing!!"))

        # Create worker scratch workspace, if missing
        if not arcpy.Exists(rf"{scratch_folder}\scratch.gdb"):
            if not arcpy.Exists(scratch_folder):
                os.makedirs(rf"{scratch_folder}")
            if not arcpy.Exists(rf"{scratch_folder}\scratch.gdb"):
                arcpy.management.CreateFileGDB(rf"{scratch_folder}", f"scratch")

        # Set worker parameters
        #table_name = "AI_IDW"
        #table_name = "GMEX_IDW"
        #table_name = "HI_IDW"
        #table_name = "WC_GFDL"
        #table_name = "WC_GLMME"
        table_name = "SEUS_FAL_IDW"

        region_gdb        = rf"{scratch_folder}\{table_name}.gdb"
        scratch_workspace = rf"{scratch_folder}\{table_name}\scratch.gdb"

        if not arcpy.Exists(scratch_workspace):
            os.makedirs(rf"{scratch_folder}\{table_name}")
            if not arcpy.Exists(scratch_workspace):
                arcpy.management.CreateFileGDB(rf"{scratch_folder}\{table_name}", f"scratch")
        del scratch_workspace

        # Setup worker workspace and copy data
        datasets = [rf"{project_gdb}\Datasets", rf"{project_gdb}\{table_name}_Region"]
        if not any(arcpy.management.GetCount(d)[0] == 0 for d in datasets):

            arcpy.management.CreateFileGDB(rf"{scratch_folder}", f"{table_name}")
            arcpy.AddMessage("\tCreate File GDB: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

            arcpy.management.Copy(rf"{project_gdb}\Datasets", rf"{region_gdb}\Datasets")
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

            arcpy.management.Copy(rf"{project_gdb}\{table_name}_Region", rf"{region_gdb}\{table_name}_Region")
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        else:
            arcpy.AddWarning(f"One or more datasets contains zero records!!")
            for d in datasets:
                arcpy.AddMessage(f"\t{os.path.basename(d)} has {arcpy.management.GetCount(d)[0]} records")
                del d
            raise SystemExit

        if "datasets" in locals().keys(): del datasets

        # A file geodatabase has 3 types of locks.
        # SR - schema lock
        # RD - read lock
        # ED - edit lock
        #print(clearWSLocks(project_gdb))
        #print(clearWSLocks(region_gdb))

##        arcpy.AddMessage(f"Compacting the {os.path.basename(region_gdb)} GDB")
##        arcpy.management.Compact(region_gdb)
##        arcpy.AddMessage("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))
##
##        arcpy.AddMessage(f"Compacting the {os.path.basename(project_gdb)} GDB")
##        arcpy.management.Compact(project_gdb)
##        arcpy.AddMessage("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))

        del project_gdb, scratch_folder

        results  = []

        try:
            pass
            result = worker(region_gdb=region_gdb)
            results.extend(result); del result

        except SystemExit as se:
            raise SystemExit(str(se))

        if results:
            if type(results).__name__ == "bool":
                arcpy.AddMessage(f"'Results' is a {type(results).__name__}" )
                arcpy.AddMessage(f"Result: {results}")
            elif type(results).__name__ == "str":
                arcpy.AddMessage(f"'Results' is a {type(results).__name__}" )
                arcpy.AddMessage(f"Result: {results}")
            elif type(results).__name__ == "list":
                if type(results[0]).__name__ == "list":
                        results = [r for rt in results for r in rt]
                arcpy.AddMessage(f"'Results' is a {type(results).__name__}" )
                for result in results:
                    arcpy.AddMessage(f"Result: {result}")
                del result
            else:
                arcpy.AddMessage(f"No results returned!!!")
        else:
            arcpy.AddMessage(f"No results in '{inspect.stack()[0][3]}'")

        try:
            Delete = True # Can not seem to remove the lock
            if Delete:
                arcpy.AddMessage(f"\nDelete GDB: {os.path.basename(region_gdb)}")
                arcpy.management.Delete(region_gdb)
                arcpy.AddMessage("\tDelete: {0} {1}\n".format(f"{table_name}.gdb", arcpy.GetMessages(0).replace("\n", '\n\t')))

                arcpy.AddMessage(f"Delete Folder: {os.path.basename(region_gdb).replace('.gdb','')}")
                arcpy.management.Delete(region_gdb.replace(".gdb",""))
                arcpy.AddMessage("\tDelete: {0} {1}\n".format(f"{table_name}", arcpy.GetMessages(0).replace("\n", '\n\t')))
            else:
                pass
            del Delete
        except:
            if "Delete" in locals().keys(): del Delete
            arcpy.AddError(arcpy.GetMessages(2))

        del region_gdb, table_name
        del worker
        del project

    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(str(traceback.print_exc()) + arcpy.GetMessages())
        raise SystemExit
    except arcpy.ExecuteError:
        arcpy.AddError(str(traceback.print_exc()) + arcpy.GetMessages())
        raise SystemExit
    except SystemExit as se:
        arcpy.AddError(str(se))
        raise SystemExit
    except:
        arcpy.AddError(str(traceback.print_exc()))
        raise SystemExit
    else:
        try:
            leave_out_keys = ["leave_out_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys
            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
        except:
            raise SystemExit(str(traceback.print_exc()))
    finally:
        if "results" in locals().keys(): del results

if __name__ == '__main__':
    try:
        # Import this Python module
        import create_region_fishnets_worker
        importlib.reload(create_region_fishnets_worker)

        print(f"{'-' * 90}")
        print(f"Python Script:  {os.path.basename(__file__)}")
        print(f"Location:       {os.path.dirname(__file__)}")
        print(f"Python Version: {sys.version} Environment: {os.path.basename(sys.exec_prefix)}")
        print(f"{'-' * 90}\n")

        #project = "May 1 2024"
        project = "July 1 2024"

        # Tested on 7/30/2024 -- PASSED
        main(project=project)

        del project

        from time import localtime, strftime
        print(f"\n{'-' * 90}")
        print(f"Python script: {os.path.basename(__file__)} successfully completed {strftime('%a %b %d %I:%M %p', localtime())}")
        print(f"{'-' * 90}")
        del localtime, strftime

    except SystemExit:
        pass
    except:
        traceback.print_exc()
    else:
        leave_out_keys = ["leave_out_keys"]
        leave_out_keys.extend([name for name, obj in inspect.getmembers(sys.modules[__name__]) if inspect.isfunction(obj) or inspect.ismodule(obj)])
        remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
        if remaining_keys:
            arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[1][3]}': ##--> '{', '.join(remaining_keys)}' <--##")
        del leave_out_keys, remaining_keys
    finally:
        pass
