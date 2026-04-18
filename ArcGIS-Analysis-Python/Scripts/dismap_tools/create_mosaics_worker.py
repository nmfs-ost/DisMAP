# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        create_species_year_image_name_table_worker
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

import arcpy # third-parties second

def trace():
    import sys, traceback  # noqa: E401
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    line = tbinfo.split(", ")[1]
    #filename = sys.path[0] + os.sep + f"{os.path.basename(__file__)}"
    filename = os.path.basename(__file__)
    synerror = traceback.format_exc().splitlines()[-1]
    return line, filename, synerror

def worker(region_gdb=""):
    try:

        # Set History and Metadata logs, set serverity and message level
        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        table_name         = os.path.basename(region_gdb).replace(".gdb","")
        scratch_folder     = os.path.dirname(region_gdb)
        project_folder     = os.path.dirname(scratch_folder)
        scratch_workspace  = rf"{scratch_folder}\{table_name}\scratch.gdb"
        region_raster_mask = rf"{region_gdb}\{table_name}_Raster_Mask"

        arcpy.AddMessage(f"Table Name: {table_name}\nProject Folder: {os.path.basename(project_folder)}\nScratch Folder: {os.path.basename(scratch_folder)}\n")

        # Set basic workkpace variables
        arcpy.env.workspace                 = region_gdb
        arcpy.env.scratchWorkspace          = scratch_workspace
        arcpy.env.overwriteOutput           = True
        arcpy.env.parallelProcessingFactor  = "100%"
        #arcpy.env.compression               = "LZ77"
        #arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"
        #arcpy.env.pyramid                   = "PYRAMIDS -1 BILINEAR LZ77 NO_SKIP"
        arcpy.env.resamplingMethod          = "BILINEAR"
        arcpy.env.rasterStatistics          = "STATISTICS 1 1"
        #arcpy.env.buildStatsAndRATForTempRaster = True

        # DatasetCode, CSVFile, TransformUnit, TableName, GeographicArea, CellSize,
        # PointFeatureType, FeatureClassName, Region, Season, DateCode, Status,
        # DistributionProjectCode, DistributionProjectName, SummaryProduct,
        # FilterRegion, FilterSubRegion, FeatureServiceName, FeatureServiceTitle,
        # MosaicName, MosaicTitle, ImageServiceName, ImageServiceTitle

        # Get values for table_name from Datasets table
        fields = ["TableName", "GeographicArea", "DatasetCode", "CellSize", "MosaicName", "MosaicTitle"]
        region_list = [row for row in arcpy.da.SearchCursor(rf"{region_gdb}\Datasets", fields, where_clause = f"TableName = '{table_name}'")][0]
        del fields

        # Assigning variables from items in the chosen table list
        # ['AI_IDW', 'AI_IDW_Region', 'AI', 'Aleutian Islands', None, 'IDW']
        table_name      = region_list[0]
        #geographic_area = region_list[1]
        datasetcode     = region_list[2]
        cell_size       = region_list[3]
        mosaic_name     = region_list[4]
        mosaic_title    = region_list[5]
        del region_list

        # Start of business logic for the worker function
        arcpy.AddMessage(f"Processing: {table_name}")

        #geographic_area_sr = rf"{project_folder}\Dataset_Shapefiles\{table_name}\{geographic_area}.prj"
        # Set the output coordinate system to what is needed for the
        # DisMAP project
        #psr = arcpy.SpatialReference(geographic_area_sr)
        #arcpy.env.outputCoordinateSystem = psr
        #del geographic_area_sr, geographic_area

        arcpy.AddMessage("\tSet the 'outputCoordinateSystem' based on the projection information for the geographic region")
        psr = arcpy.Describe(region_raster_mask).spatialReference
        arcpy.env.outputCoordinateSystem = psr
        del region_raster_mask

        arcpy.AddMessage("Building the 'input_raster_paths' list")

        layerspeciesyearimagename = rf"{region_gdb}\{table_name}_LayerSpeciesYearImageName"

        input_raster_paths = []

        fields = ['Variable', 'ImageName']
        with arcpy.da.SearchCursor(layerspeciesyearimagename, fields, where_clause = f"DatasetCode = '{datasetcode}'") as cursor:
            for row in cursor:
                variable, image_name = row[0], row[1]
                #if variable not in variables: variables.append(variable)
                #arcpy.AddMessage(f"{variable}, {image_name}")
                variable = f"_{variable}" if "Species Richness" in variable else variable
                input_raster_path = rf"{project_folder}\Images\{table_name}\{variable}\{image_name}.tif"
                if arcpy.Exists(input_raster_path):
                    #arcpy.AddMessage(input_raster_path)
                    input_raster_paths.append(input_raster_path)
                else:
                    arcpy.AddError(f"{os.path.basename(input_raster_path)} is missing!!")
                #arcpy.AddMessage(input_raster_path)
                del row, variable, image_name, input_raster_path
            del cursor
        del fields

        mosaic_path = os.path.join(region_gdb, mosaic_name)

        # Loading images into the Mosaic.
        arcpy.AddMessage(f"Loading the '{table_name}' Mosaic. This may take a while. . . Please wait. . .")

        with arcpy.EnvManager(scratchWorkspace = scratch_workspace, workspace = region_gdb):
            arcpy.management.CreateMosaicDataset(in_workspace             = region_gdb,
                                                 in_mosaicdataset_name    = mosaic_name,
                                                 coordinate_system        = psr,
                                                 num_bands                = "1",
                                                 pixel_type               = "32_BIT_FLOAT",
                                                 product_definition       = "",
                                                 product_band_definitions = "")

            arcpy.AddMessage("\tCreate Mosaic Dataset: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

        arcpy.AddMessage(f"Loading Rasters into the {os.path.basename(mosaic_path)}.")

        arcpy.management.AddRastersToMosaicDataset(in_mosaic_dataset       = mosaic_path,
                                                   raster_type             = "Raster Dataset",
                                                   input_path              = input_raster_paths,
                                                   update_cellsize_ranges  = "UPDATE_CELL_SIZES",
                                                   #update_cellsize_ranges = "NO_CELL_SIZES",
                                                   update_boundary         = "UPDATE_BOUNDARY",
                                                   #update_boundary        = "NO_BOUNDARY",
                                                   update_overviews        = "NO_OVERVIEWS",
                                                   maximum_pyramid_levels  = None,
                                                   maximum_cell_size       = "0",
                                                   minimum_dimension       = "1500",
                                                   spatial_reference       = psr,
                                                   filter                  = "",
                                                   sub_folder              = "NO_SUBFOLDERS",
                                                   #duplicate_items_action = "OVERWRITE_DUPLICATES",
                                                   duplicate_items_action  = "EXCLUDE_DUPLICATES",
                                                   build_pyramids          = "NO_PYRAMIDS",
                                                   #calculate_statistics   = "CALCULATE_STATISTICS",
                                                   calculate_statistics    = "NO_STATISTICS",
                                                   #build_thumbnails       = "BUILD_THUMBNAILS",
                                                   build_thumbnails        = "NO_THUMBNAILS",
                                                   operation_description   = "DisMAP",
                                                   #force_spatial_reference= "NO_FORCE_SPATIAL_REFERENCE",
                                                   force_spatial_reference = "FORCE_SPATIAL_REFERENCE",
                                                   #estimate_statistics    = "ESTIMATE_STATISTICS",
                                                   estimate_statistics     = "NO_STATISTICS",
                                                   )
        arcpy.AddMessage("\tAdd Rasters To Mosaic Dataset: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
        del input_raster_paths
        del psr

        arcpy.AddMessage(f"Joining {os.path.basename(mosaic_path)} with {os.path.basename(layerspeciesyearimagename)}")

        arcpy.management.JoinField(in_data = mosaic_path, in_field="Name", join_table = layerspeciesyearimagename, join_field="ImageName", fields="DatasetCode;Region;Season;Species;CommonName;SpeciesCommonName;CoreSpecies;Year;StdTime;Variable;Value;Dimensions")
        arcpy.AddMessage("\tJoin Field: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
        del layerspeciesyearimagename

        arcpy.AddMessage(f'Removing field index from {os.path.basename(mosaic_path)}')

        try:
            arcpy.management.RemoveIndex(mosaic_path, [f"{table_name}_MosaicSpeciesIndex",])
        except:  # noqa: E722
            pass

        arcpy.AddMessage(f"Adding field index to {os.path.basename(mosaic_path)}")

        # Add Attribute Index
        arcpy.management.AddIndex(mosaic_path, ['Species', 'CommonName', 'SpeciesCommonName', 'Year'], f"{table_name}_MosaicSpeciesIndex", "NON_UNIQUE", "NON_ASCENDING")
        arcpy.AddMessage("\tAdd Index: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

        arcpy.management.CalculateStatistics(mosaic_path, 1, 1, [], "OVERWRITE", "")
        arcpy.AddMessage("\tCalculate Statistics: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

        #--->>> SetMosaicDatasetProperties
        arcpy.AddMessage(f"Set Mosaic Dataset Properties for {os.path.basename(mosaic_path)}")

        #fields = [f.name for f in arcpy.ListFields(mosaic_path) if f.type not in ['Geometry', 'OID'] and f.name not in ["Shape", "Raster", "Category", "TypeID", "ItemTS", "UriHash", "Uri",]]
        fields = [f.name for f in arcpy.ListFields(mosaic_path)]

        fields = ";".join(fields)

        arcpy.management.SetMosaicDatasetProperties(in_mosaic_dataset                = mosaic_path,
                                                    rows_maximum_imagesize           = 4100,
                                                    columns_maximum_imagesize        = 15000,
                                                    allowed_compressions             = "LZ77;None",
                                                    default_compression_type         = "LZ77",
                                                    JPEG_quality                     = 75,
                                                    LERC_Tolerance                   = 0.01,
                                                    resampling_type                  = "BILINEAR",
                                                    clip_to_footprints               = "NOT_CLIP",
                                                    footprints_may_contain_nodata    = "FOOTPRINTS_MAY_CONTAIN_NODATA",
                                                    clip_to_boundary                 = "CLIP",
                                                    color_correction                 = "NOT_APPLY",
                                                    allowed_mensuration_capabilities = "Basic",
                                                    default_mensuration_capabilities = "Basic",
                                                    allowed_mosaic_methods           = "None",
                                                    default_mosaic_method            = "None",
                                                    order_field                      = "StdTime",
                                                    order_base                       = "",
                                                    sorting_order                    = "ASCENDING",
                                                    mosaic_operator                  = "FIRST",
                                                    blend_width                      = 10,
                                                    view_point_x                     = 600,
                                                    view_point_y                     = 300,
                                                    max_num_per_mosaic               = 50,
                                                    cell_size_tolerance              = 0.8,
                                                    cell_size                        = f"{cell_size} {cell_size}",
                                                    metadata_level                   = "FULL",
                                                    transmission_fields              = fields,
                                                    use_time                         = "ENABLED",
                                                    start_time_field                 = "StdTime",
                                                    end_time_field                   = "StdTime",
                                                    time_format                      = "YYYY", #YYYYMMDD
                                                    geographic_transform             = None,
                                                    max_num_of_download_items        = 20,
                                                    max_num_of_records_returned      = 1000,
                                                    data_source_type                 = "GENERIC",
                                                    minimum_pixel_contribution       = 1,
                                                    processing_templates             = "None",
                                                    default_processing_template      = "None",
                                                    time_interval                    = 1,
                                                    time_interval_units              = "Years",
                                                    product_definition               = "NONE",
                                                    product_band_definitions         = None
                                                   )
        arcpy.AddMessage("\tSet Mosaic Dataset Properties: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
        del fields

        arcpy.AddMessage(f"Analyze Mosaic {os.path.basename(mosaic_path)} Dataset")

        arcpy.management.AnalyzeMosaicDataset(
                                              in_mosaic_dataset = mosaic_path,
                                              where_clause      = "",
                                              checker_keywords  = "FOOTPRINT;FUNCTION;RASTER;PATHS;SOURCE_VALIDITY;STALE;PYRAMIDS;STATISTICS;PERFORMANCE;INFORMATION"
                                             )
        arcpy.AddMessage("\tSet Mosaic Dataset Properties: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

        arcpy.AddMessage(f"Adding Multidimensional Information to {os.path.basename(mosaic_path)} Dataset")

        with arcpy.EnvManager(scratchWorkspace = scratch_workspace, workspace = region_gdb):
            arcpy.md.BuildMultidimensionalInfo(
                                                in_mosaic_dataset            = mosaic_path,
                                                variable_field               = "Variable",
                                                dimension_fields             = [["StdTime", "Time Step", "Year"],],
                                                variable_desc_units          = None,
                                                delete_multidimensional_info = "NO_DELETE_MULTIDIMENSIONAL_INFO"
                                               )
            arcpy.AddMessage("\tBuild Multidimensional Info: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

        #arcpy.management.CalculateStatistics(mosaic_path, 1, 1, [], "OVERWRITE", "")
        #arcpy.AddMessage("\tCalculate Statistics: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

        # Copy Raster to CRF
        crf_path = rf"{scratch_folder}\{table_name}\{mosaic_name.replace('_Mosaic', '')}.crf"

        arcpy.management.CopyRaster(
                                    in_raster                        = mosaic_path,
                                    out_rasterdataset                = crf_path,
                                    config_keyword                   = "",
                                    background_value                 = None,
                                    nodata_value                     = "-3.40282e+38",
                                    onebit_to_eightbit               = "NONE",
                                    colormap_to_RGB                  = "NONE",
                                    pixel_type                       = "32_BIT_FLOAT",
                                    scale_pixel_value                = "NONE",
                                    RGB_to_Colormap                  = "NONE",
                                    format                           = "CRF",
                                    transform                        = None,
                                    process_as_multidimensional      = "ALL_SLICES",
                                    build_multidimensional_transpose = "NO_TRANSPOSE"
                                   )
        arcpy.AddMessage("\tCopy Raster: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

        arcpy.AddMessage(f"Calculate Statistics for {os.path.basename(crf_path)}")

        arcpy.management.CalculateStatistics(crf_path, 1, 1, [], "OVERWRITE", "")
        arcpy.AddMessage("\tCalculate Statistics: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
        del crf_path
        del mosaic_path

        # End of business logic for the worker function
        arcpy.AddMessage(f"Processing for: {table_name} complete")

        arcpy.management.Delete(rf"{region_gdb}\Datasets")
        arcpy.management.Delete(rf"{region_gdb}\{table_name}_LayerSpeciesYearImageName")
        arcpy.management.Delete(rf"{region_gdb}\{table_name}_Raster_Mask")

        # Declared Variables for this function only
        del datasetcode, cell_size, mosaic_name, mosaic_title
        # Basic variables
        del table_name, scratch_folder, project_folder, scratch_workspace
        # Imports
        # Function parameter
        del region_gdb

    except arcpy.ExecuteError:
        #Return Geoprocessing tool specific errors
        line, filename, err = trace()
        arcpy.AddError("Geoprocessing error on " + line + " of " + filename + " :")
        for msg in range(0, arcpy.GetMessageCount()):
            if arcpy.GetSeverity(msg) == 2:
                arcpy.AddReturnMessage(msg)
        return False
    except:  # noqa: E722
        #Gets non-tool errors
        line, filename, err = trace()
        arcpy.AddError("Python error on " + line + " of " + filename)
        arcpy.AddError(err)
        return False
    else:
        return True

def script_tool(project_gdb=""):
    try:
        # Imports
        import dismap_tools
        from create_mosaics_director import preprocessing
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

        table_names = ["HI_IDW", "NBS_IDW"]

        preprocessing(project_gdb=project_gdb, table_names=table_names, clear_folder=True)

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

    except arcpy.ExecuteError:
        #Return Geoprocessing tool specific errors
        line, filename, err = trace()
        arcpy.AddError("Geoprocessing error on " + line + " of " + filename + " :")
        for msg in range(0, arcpy.GetMessageCount()):
            if arcpy.GetSeverity(msg) == 2:
                arcpy.AddReturnMessage(msg)
        return False
    except:  # noqa: E722
        #Gets non-tool errors
        line, filename, err = trace()
        arcpy.AddError("Python error on " + line + " of " + filename)
        arcpy.AddError(err)
        return False
    else:
        return True

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

    except arcpy.ExecuteError:
        #Return Geoprocessing tool specific errors
        line, filename, err = trace()
        arcpy.AddError("Geoprocessing error on " + line + " of " + filename + " :")
        for msg in range(0, arcpy.GetMessageCount()):
            if arcpy.GetSeverity(msg) == 2:
                arcpy.AddReturnMessage(msg)
    except:  # noqa: E722
        #Gets non-tool errors
        line, filename, err = trace()
        arcpy.AddError("Python error on " + line + " of " + filename)
        arcpy.AddError(err)
