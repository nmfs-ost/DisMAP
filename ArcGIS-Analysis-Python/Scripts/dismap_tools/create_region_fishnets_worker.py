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
import os
import sys
import traceback
import inspect

import arcpy # third-parties second

def worker(region_gdb=""):
    try:
        # Test if passed workspace exists, if not sys.exit()
        if not arcpy.Exists(rf"{region_gdb}"):
            sys.exit()(f"{os.path.basename(region_gdb)} is missing!!")

        # Imports
        from arcpy import metadata as md
        import dismap_tools

        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(1) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        table_name      = os.path.basename(region_gdb).replace(".gdb","")
        scratch_folder  = os.path.dirname(region_gdb)
        project_folder  = os.path.dirname(scratch_folder)
        csv_data_folder   = rf"{project_folder}\CSV_Data"
        scratch_workspace = rf"{scratch_folder}\{table_name}\scratch.gdb"

        #arcpy.AddMessage(f"Table Name: {table_name}\nProject Folder: {os.path.basename(project_folder)}\nScratch Folder: {os.path.basename(scratch_folder)}\n")

        del scratch_folder, project_folder

        arcpy.env.workspace                 = region_gdb
        arcpy.env.scratchWorkspace          = scratch_workspace
        arcpy.env.overwriteOutput           = True
        arcpy.env.parallelProcessingFactor  = "100%"
        arcpy.env.compression               = "LZ77"
        #arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"
        arcpy.env.pyramid                   = "PYRAMIDS -1 BILINEAR DEFAULT 75 NO_SKIP NO_SIPS"
        arcpy.env.resamplingMethod          = "BILINEAR"
        arcpy.env.rasterStatistics          = "STATISTICS 1 1"
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
        arcpy.AddMessage(f"Region GDB:  {os.path.basename(arcpy.env.workspace)}")
        arcpy.AddMessage(f"Scratch GDB: {os.path.basename(arcpy.env.scratchWorkspace)}")

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

        #arcpy.AddMessage("process_region")
        #arcpy.AddMessage(f"Spatial Reference: {str(arcpy.Describe(process_region).spatialReference.name)}")
        #arcpy.AddMessage(f"Extent:            {str(arcpy.Describe(process_region).extent).replace(' NaN', '')}")
        #arcpy.AddMessage(f"Output Coordinate System:   {arcpy.env.outputCoordinateSystem.name}")
        #arcpy.AddMessage(f"Geographic Transformations: {arcpy.env.geographicTransformations}")

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
            arcpy.AddMessage("\tAdd XY:\n\t\t{0}\n".format(arcpy.GetMessages().replace("\n", "\n\t\t")))

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
        arcpy.AddMessage("\tAlter Field:\n\t\t{0}\n".format(arcpy.GetMessages().replace("\n", "\n\t\t")))

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
        arcpy.AddMessage("\tAlter Field:\n\t\t{0}\n".format(arcpy.GetMessages().replace("\n", "\n\t\t")))

        tmp_outputCoordinateSystem = arcpy.env.outputCoordinateSystem
        arcpy.env.outputCoordinateSystem = gsr

        with arcpy.EnvManager(outputCoordinateSystem = gsr, geographicTransformations = dismap_tools.check_transformation(rf"{region_gdb}\{region_extent_points}", gsr)):
            arcpy.management.AddXY(in_features = rf"{region_gdb}\{region_extent_points}")
            arcpy.AddMessage("\tAdd XY:\n\t\t{0}\n".format(arcpy.GetMessages().replace("\n", "\n\t\t")))

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
        arcpy.AddMessage("\tAlter Field:\n\t\t{0}\n".format(arcpy.GetMessages().replace("\n", "\n\t\t")))

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
        arcpy.AddMessage("\tAlter Field:\n\t\t{0}\n".format(arcpy.GetMessages().replace("\n", "\n\t\t")))

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
        arcpy.AddMessage("\tSelect Layer By Location:\n\t\t{0}\n".format(arcpy.GetMessages().replace("\n", "\n\t\t")))
        arcpy.AddMessage(f"\t\tRecord Count: {int(arcpy.management.GetCount(f'{region_name}_Fishnet_Layer')[0]):,d}")

        arcpy.management.DeleteFeatures(f"{region_name}_Fishnet_Layer")
        arcpy.AddMessage("\tDelete Features:\n\t\t{0}\n".format(arcpy.GetMessages().replace("\n", "\n\t\t")))

        arcpy.management.Delete(f"{region_name}_Fishnet_Layer")
        arcpy.AddMessage("\tDelete {0}:\n\t\t{1}\n".format(f"{region_name}_Fishnet_Layer", arcpy.GetMessages(0).replace("\n", "\n\t\t")))

        # Creating Lat-Long
        arcpy.AddMessage(f"Creating Lat-Long: {region_lat_long}")
        arcpy.management.FeatureToPoint(rf"{region_gdb}\{region_fishnet}", rf"{region_gdb}\{region_lat_long}", "CENTROID")
        arcpy.AddMessage("\tFeature To Point:\n\t\t{0}\n".format(arcpy.GetMessages().replace("\n", "\n\t\t")))

        # Execute DeleteField
        arcpy.management.DeleteField(rf"{region_gdb}\{region_lat_long}", ['ORIG_FID'])
        arcpy.AddMessage("\tDelete Field:\n\t\t{0}\n".format(arcpy.GetMessages().replace("\n", "\n\t\t")))

        with arcpy.EnvManager(outputCoordinateSystem = psr):
            arcpy.management.AddXY(in_features=rf"{region_gdb}\{region_lat_long}")
            arcpy.AddMessage("\tAdd XY:\n\t\t{0}\n".format(arcpy.GetMessages().replace("\n", "\n\t\t")))

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
            arcpy.AddMessage("\tAlter Field:\n\t\t{0}\n".format(arcpy.GetMessages().replace("\n", "\n\t\t")))

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
            arcpy.AddMessage("\tAlter Field:\n\t\t{0}\n".format(arcpy.GetMessages().replace("\n", "\n\t\t")))

        with arcpy.EnvManager(outputCoordinateSystem = gsr, geographicTransformations = dismap_tools.check_transformation(rf"{region_gdb}\{region_extent_points}", gsr)):
            arcpy.management.AddXY(in_features=rf"{region_gdb}\{region_lat_long}")
            arcpy.AddMessage("\tAdd XY:\n\t\t{0}\n".format(arcpy.GetMessages().replace("\n", "\n\t\t")))

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
            arcpy.AddMessage("\tAlter Field:\n\t\t{0}\n".format(arcpy.GetMessages().replace("\n", "\n\t\t")))

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
            arcpy.AddMessage("\tAlter Field:\n\t\t{0}\n".format(arcpy.GetMessages().replace("\n", "\n\t\t")))

 #        arcpy.management.CalculateFields(
 #                                         in_table        = rf"{region_gdb}\{region_lat_long}",
 #                                         expression_type = "PYTHON3",
 #                                         fields          = "Easting 'round(!Easting!, 8)' #;Northing 'round(!Northing!, 8)' #;Longitude 'round(!Longitude!, 8)' #;Latitude 'round(!Latitude!, 8)' #",
 #                                         code_block      = "",
 #                                         enforce_domains = "NO_ENFORCE_DOMAINS"
 #                                        )
 #        arcpy.AddMessage("\tCalculate Fields:\n\t\t{0}\n".format(arcpy.GetMessages().replace("\n", "\n\t\t")))

        arcpy.AddMessage(f"Generating {table_name} Latitude and Longitude Rasters")

 #        arcpy.env.cellSize   = cell_size
 #        arcpy.env.extent     = arcpy.Describe(rf"{region_gdb}\{region_raster_mask}").extent
 #        arcpy.env.mask       = rf"{region_gdb}\{region_raster_mask}"
 #        arcpy.env.snapRaster = rf"{region_gdb}\{region_raster_mask}"

        raster_mask_extent = arcpy.Describe(rf"{region_gdb}\{region_raster_mask}").extent

        arcpy.AddMessage(f"Point to Raster Conversion using {region_lat_long} to create {region_longitude}")

        region_longitude_tmp = rf"{region_gdb}\tmp_{region_longitude}"

        with arcpy.EnvManager(scratchWorkspace=scratch_workspace, workspace = region_gdb, cellSize = cell_size, extent = raster_mask_extent, mask = rf"{region_gdb}\{region_raster_mask}", snapRaster = rf"{region_gdb}\{region_raster_mask}"):
            arcpy.conversion.PointToRaster(rf"{region_gdb}\{region_lat_long}", "Longitude", region_longitude_tmp, "MOST_FREQUENT", "NONE", cell_size)
            arcpy.AddMessage("\tPoint To Raster:\n\t\t{0}\n".format(arcpy.GetMessages().replace("\n", "\n\t\t")))

        arcpy.AddMessage(f"Extract by Mask to create {region_longitude}")

        with arcpy.EnvManager(scratchWorkspace=scratch_workspace, workspace = region_gdb,
                              cellSize = cell_size, extent = raster_mask_extent,
                              mask       = rf"{region_gdb}\{region_raster_mask}",
                              snapRaster = rf"{region_gdb}\{region_raster_mask}"):
            # Execute ExtractByMask
            outExtractByMask = arcpy.sa.ExtractByMask(region_longitude_tmp, rf"{region_gdb}\{region_raster_mask}", "INSIDE")
            arcpy.AddMessage("\tExtract By Mask:\n\t\t{0}\n".format(arcpy.GetMessages().replace("\n", "\n\t\t")))
            # Save the output
            outExtractByMask.save(rf"{region_gdb}\{region_longitude}")
            del outExtractByMask

        arcpy.management.Delete(region_longitude_tmp)
        del region_longitude_tmp

        region_latitude_tmp = rf"{region_gdb}\tmp_{region_latitude}"

        arcpy.AddMessage(f"Point to Raster Conversion using {region_lat_long} to create {region_latitude}")

        with arcpy.EnvManager(scratchWorkspace=scratch_workspace, workspace = region_gdb,
                              cellSize = cell_size, extent = raster_mask_extent,
                              mask       = rf"{region_gdb}\{region_raster_mask}",
                              snapRaster = rf"{region_gdb}\{region_raster_mask}"):
            # Process: Point to Raster Latitude
            arcpy.conversion.PointToRaster(rf"{region_gdb}\{region_lat_long}", "Latitude", region_latitude_tmp, "MOST_FREQUENT", "NONE", cell_size, "BUILD")
            arcpy.AddMessage("\tPoint To Raster:\n\t\t{0}\n".format(arcpy.GetMessages().replace("\n", "\n\t\t")))

        arcpy.AddMessage(f"Extract by Mask to create {region_latitude}")

        with arcpy.EnvManager(scratchWorkspace=scratch_workspace, workspace = region_gdb, cellSize = cell_size, extent = raster_mask_extent, mask = rf"{region_gdb}\{region_raster_mask}", snapRaster = rf"{region_gdb}\{region_raster_mask}"):
            # Execute ExtractByMask
            outExtractByMask = arcpy.sa.ExtractByMask(region_latitude_tmp, rf"{region_gdb}\{region_raster_mask}", "INSIDE")
            arcpy.AddMessage("\tExtract By Mask:\n\t\t{0}\n".format(arcpy.GetMessages().replace("\n", "\n\t\t")))
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

        arcpy.AddMessage(f"\t\tAlter Fields for: '{region_raster_mask}'")
        #dismap_tools.alter_fields(csv_data_folder, rf"{region_gdb}\{region_raster_mask}")
        dismap_tools.import_metadata(csv_data_folder, dataset = rf"{region_gdb}\{region_raster_mask}")

        # Create Metadata
        dataset_md = md.Metadata(region_raster_mask)
        dataset_md.synchronize("ALWAYS")
        dataset_md.save()
        del dataset_md

        arcpy.AddMessage(f"\t\tAlter Fields for: '{region_extent_points}'")
        dismap_tools.alter_fields(csv_data_folder, rf"{region_gdb}\{region_extent_points}")
        dismap_tools.import_metadata(csv_data_folder, dataset = rf"{region_gdb}\{region_extent_points}")

        # Create Metadata
        dataset_md = md.Metadata(region_extent_points)
        dataset_md.synchronize("ALWAYS")
        dataset_md.save()
        del dataset_md

        arcpy.AddMessage(f"\t\tAlter Fields for: '{region_fishnet}'")
        dismap_tools.alter_fields(csv_data_folder, rf"{region_gdb}\{region_fishnet}")
        dismap_tools.import_metadata(csv_data_folder, dataset = rf"{region_gdb}\{region_fishnet}")

        # Create Metadata
        dataset_md = md.Metadata(region_fishnet)
        dataset_md.synchronize("ALWAYS")
        dataset_md.save()
        del dataset_md

        arcpy.AddMessage(f"\t\tAlter Fields for: '{region_lat_long}'")
        dismap_tools.alter_fields(csv_data_folder, rf"{region_gdb}\{region_lat_long}")
        dismap_tools.import_metadata(csv_data_folder, dataset = rf"{region_gdb}\{region_lat_long}")

        # Create Metadata
        dataset_md = md.Metadata(region_lat_long)
        dataset_md.synchronize("ALWAYS")
        dataset_md.save()
        del dataset_md

        arcpy.AddMessage(f"\t\tAlter Fields for: '{region_latitude}'")
        dismap_tools.import_metadata(csv_data_folder, dataset = rf"{region_gdb}\{region_latitude}")

        # Create Metadata
        dataset_md = md.Metadata(region_latitude)
        dataset_md.synchronize("ALWAYS")
        dataset_md.save()
        del dataset_md

        arcpy.AddMessage(f"\t\tAlter Fields for: '{region_longitude}'")
        dismap_tools.import_metadata(csv_data_folder, dataset = rf"{region_gdb}\{region_longitude}")

        # Create Metadata
        dataset_md = md.Metadata(region_longitude)
        dataset_md.synchronize("ALWAYS")
        dataset_md.save()
        del dataset_md

        arcpy.management.Delete(process_region)
        arcpy.management.Delete(rf"{region_gdb}\Datasets")

        del process_region, region_raster_mask, region_extent_points, region_fishnet
        del region_lat_long, region_latitude, region_longitude
        del psr, gsr
        del cell_size

        arcpy.AddMessage(f"Compacting the {os.path.basename(region_gdb)} GDB")
        arcpy.management.Compact(region_gdb)
        arcpy.AddMessage("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))

        # End of business logic for the worker function
        arcpy.AddMessage(f"Processing for: {table_name} complete")

        # Declared Variables
        del region_name, table_name
        del scratch_workspace, csv_data_folder
        # Imports
        del dismap_tools, md
        # Function parameter
        del region_gdb
    except KeyboardInterrupt:
        sys.exit()
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(f"Caught an arcpy.ExecuteWarning error in the '{inspect.stack()[0][3]}' function.")
        arcpy.AddWarning(arcpy.GetMessages(1))
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

        # Set basic arcpy.env variables
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        # Set varaibales
        project_folder = os.path.dirname(project_gdb)
        scratch_folder = rf"{project_folder}\Scratch"
        del project_folder

        # Clear Scratch Folder
        dismap_tools.clear_folder(folder=scratch_folder)

        # Create project scratch workspace, if missing
        if not arcpy.Exists(os.path.join(scratch_folder, "scratch.gdb")):
            if not arcpy.Exists(scratch_folder):
                os.makedirs(scratch_folder)
            if not arcpy.Exists(os.path.join(scratch_folder, "scratch.gdb")):
                arcpy.management.CreateFileGDB(rf"{scratch_folder}", "scratch")

        # Set worker parameters
        #table_name = "AI_IDW"
        #table_name = "GMEX_IDW"
        #table_name = "HI_IDW"
        #table_name = "SEUS_FAL_IDW"
        table_name = "NBS_IDW"

        region_gdb        = os.path.join(scratch_folder, f"{table_name}.gdb")
        scratch_workspace = rf"{scratch_folder}\{table_name}\scratch.gdb"

        if not arcpy.Exists(scratch_workspace):
            os.makedirs(os.path.join(scratch_folder,  table_name))
            if not arcpy.Exists(scratch_workspace):
                arcpy.management.CreateFileGDB(os.path.join(scratch_folder, f"{table_name}"), "scratch")
        del scratch_workspace

        # Setup worker workspace and copy data
        #datasets = [ros.path.join(project_gdb, "Datasets") os.path.join(project_gdb, f"{table_name}_Region")]
        #if not any(arcpy.management.GetCount(d)[0] == 0 for d in datasets):

        if not arcpy.Exists(os.path.join(scratch_folder, f"{table_name}.gdb")):
            arcpy.management.CreateFileGDB(rf"{scratch_folder}", f"{table_name}")
            arcpy.AddMessage("\tCreate File GDB: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
        else:
            pass
        arcpy.management.Copy(os.path.join(project_gdb, "Datasets"), rf"{region_gdb}\Datasets")
        arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

        arcpy.management.Copy(os.path.join(project_gdb, f"{table_name}_Region"), rf"{region_gdb}\{table_name}_Region")
        arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

        #else:
        #    arcpy.AddWarning(f"One or more datasets contains zero records!!")
        #    for d in datasets:
        #        arcpy.AddMessage(f"\t{os.path.basename(d)} has {arcpy.management.GetCount(d)[0]} records")
        #        del d
        #    sys.exit()
        #if "datasets" in locals().keys(): del datasets

        try:
            pass
            worker(region_gdb=region_gdb)
        except SystemExit:
            arcpy.AddError(arcpy.GetMessages(2))
            traceback.print_exc()
            sys.exit()

        # Declared Varaiables
        del region_gdb, table_name, scratch_folder
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