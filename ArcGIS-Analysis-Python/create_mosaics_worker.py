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

        # Import the dismap module to access tools
        #import dismap
        #importlib.reload(dismap)

        # Import the worker module to process data
        # N/A

        # Set History and Metadata logs, set serverity and message level
        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        table_name        = os.path.basename(region_gdb).replace(".gdb","")
        scratch_folder    = os.path.dirname(region_gdb)
        project_folder    = os.path.dirname(scratch_folder)
        scratch_workspace = rf"{scratch_folder}\{table_name}\scratch.gdb"

        arcpy.AddMessage(f"Table Name: {table_name}\nProject Folder: {project_folder}\nScratch Folder: {scratch_folder}\n")

        # Set basic workkpace variables
        arcpy.env.workspace                 = region_gdb
        arcpy.env.scratchWorkspace          = scratch_workspace
        arcpy.env.overwriteOutput              = True
        arcpy.env.parallelProcessingFactor  = "100%"
        #arcpy.env.compression               = "LZ77"
        #arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"
        #arcpy.env.pyramid                   = "PYRAMIDS -1 BILINEAR LZ77 NO_SKIP"
        arcpy.env.resamplingMethod          = "BILINEAR"
        arcpy.env.rasterStatistics          = u'STATISTICS 1 1'
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
        geographic_area = region_list[1]
        datasetcode     = region_list[2]
        cell_size       = region_list[3]
        mosaic_name     = region_list[4]
        mosaic_title    = region_list[5]
        del region_list

        # Start of business logic for the worker function
        arcpy.AddMessage(f"Processing: {table_name}")

        geographic_area_sr = rf"{project_folder}\Dataset Shapefiles\{table_name}\{geographic_area}.prj"
        # Set the output coordinate system to what is needed for the
        # DisMAP project
        psr = arcpy.SpatialReference(geographic_area_sr)
        arcpy.env.outputCoordinateSystem = psr
        del geographic_area_sr, geographic_area

        arcpy.AddMessage(f"Building the 'input_raster_paths' list")

        layerspeciesyearimagename = rf"{region_gdb}\{table_name}_LayerSpeciesYearImageName"

        input_raster_paths = []

        fields = ['Variable', 'ImageName']
        with arcpy.da.SearchCursor(layerspeciesyearimagename, fields, where_clause = f"DatasetCode = '{datasetcode}'") as cursor:
            for row in cursor:
                variable, image_name = row[0], row[1]
                #if variable not in variables: variables.append(variable)
                #print(variable, image_name)
                variable = f"_{variable}" if "Species Richness" in variable else variable
                input_raster_path = rf"{project_folder}\Images\{table_name}\{variable}\{image_name}.tif"
                if arcpy.Exists(input_raster_path):
                    #print(input_raster_path)
                    input_raster_paths.append(input_raster_path)
                else:
                    arcpy.AddError(f"{os.path.basename(input_raster_path)} is missing!!")
                #print(input_raster_path)
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

            arcpy.AddMessage("\tCreate Mosaic Dataset: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

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
        arcpy.AddMessage("\tAdd Rasters To Mosaic Dataset: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))
        del input_raster_paths
        del psr

        arcpy.AddMessage(f"Joining {os.path.basename(mosaic_path)} with {os.path.basename(layerspeciesyearimagename)}")

        arcpy.management.JoinField(in_data = mosaic_path, in_field="Name", join_table = layerspeciesyearimagename, join_field="ImageName", fields="DatasetCode;Region;Season;Species;CommonName;SpeciesCommonName;CoreSpecies;Year;StdTime;Variable;Value;Dimensions")
        arcpy.AddMessage("\tJoin Field: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))
        del layerspeciesyearimagename

        arcpy.AddMessage(f'Removing field index from {os.path.basename(mosaic_path)}')

        try:
            arcpy.management.RemoveIndex(mosaic_path, [f"{table_name}_MosaicSpeciesIndex",])
        except:
            pass

        arcpy.AddMessage(f"Adding field index to {os.path.basename(mosaic_path)}")

        # Add Attribute Index
        arcpy.management.AddIndex(mosaic_path, ['Species', 'CommonName', 'SpeciesCommonName', 'Year'], f"{table_name}_MosaicSpeciesIndex", "NON_UNIQUE", "NON_ASCENDING")
        arcpy.AddMessage("\tAdd Index: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        arcpy.management.CalculateStatistics(mosaic_path, 1, 1, [], "OVERWRITE", "")
        arcpy.AddMessage("\tCalculate Statistics: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

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
        arcpy.AddMessage("\tSet Mosaic Dataset Properties: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))
        del fields

        arcpy.AddMessage(f"Analyze Mosaic {os.path.basename(mosaic_path)} Dataset")

        arcpy.management.AnalyzeMosaicDataset(
                                              in_mosaic_dataset = mosaic_path,
                                              where_clause      = "",
                                              checker_keywords  = "FOOTPRINT;FUNCTION;RASTER;PATHS;SOURCE_VALIDITY;STALE;PYRAMIDS;STATISTICS;PERFORMANCE;INFORMATION"
                                             )
        arcpy.AddMessage("\tSet Mosaic Dataset Properties: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        arcpy.AddMessage(f"Adding Multidimensional Information to {os.path.basename(mosaic_path)} Dataset")

        with arcpy.EnvManager(scratchWorkspace = scratch_workspace, workspace = region_gdb):
            arcpy.md.BuildMultidimensionalInfo(
                                                in_mosaic_dataset            = mosaic_path,
                                                variable_field               = "Variable",
                                                dimension_fields             = [["StdTime", "Time Step", "Year"],],
                                                variable_desc_units          = None,
                                                delete_multidimensional_info = "NO_DELETE_MULTIDIMENSIONAL_INFO"
                                               )
            arcpy.AddMessage("\tBuild Multidimensional Info: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        #arcpy.management.CalculateStatistics(mosaic_path, 1, 1, [], "OVERWRITE", "")
        #arcpy.AddMessage("\tCalculate Statistics: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

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
        arcpy.AddMessage("\tCopy Raster: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        arcpy.AddMessage(f"Calculate Statistics for {os.path.basename(crf_path)}")

        arcpy.management.CalculateStatistics(crf_path, 1, 1, [], "OVERWRITE", "")
        arcpy.AddMessage("\tCalculate Statistics: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        # Gather results to be returned
        results = [mosaic_path, crf_path]
        del mosaic_path, crf_path

        # End of business logic for the worker function
        arcpy.AddMessage(f"Processing for: {table_name} complete")

        # Variables for this function only
        del datasetcode, cell_size, mosaic_name, mosaic_title
        # Basic variables
        del table_name, scratch_folder, project_folder, scratch_workspace
        # Imports
        #del dismap
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
        from create_mosaics_worker import worker

        # Set basic arcpy.env variables
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        # Set varaibales
        base_project_folder = os.path.dirname(os.path.dirname(__file__))
        project_gdb         = rf"{base_project_folder}\{project}\{project}.gdb"
        project_folder      = rf"{base_project_folder}\{project}\{project}.gdb"
        scratch_folder      = rf"{project_folder}\Scratch"
        del project_folder, base_project_folder

        # Test if passed workspace exists, if not raise SystemExit
        if not arcpy.Exists(project_gdb):
            raise SystemExit(line_info(f"{os.path.basename(project_gdb)} is missing!!"))

        # Create project scratch workspace, if missing
        if not arcpy.Exists(rf"{scratch_folder}\scratch.gdb"):
            if not arcpy.Exists(scratch_folder):
                os.makedirs(rf"{scratch_folder}")
            if not arcpy.Exists(rf"{scratch_folder}\scratch.gdb"):
                arcpy.management.CreateFileGDB(rf"{scratch_folder}", f"scratch")

        # Set worker parameters
        #table_name = "AI_IDW"
        table_name = "HI_IDW"
        #table_name = "NBS_IDW"

        region_gdb        = rf"{scratch_folder}\{table_name}.gdb"
        scratch_workspace = rf"{scratch_folder}\{table_name}\scratch.gdb"

        # Create worker scratch workspace, if missing
        if not arcpy.Exists(scratch_workspace):
            os.makedirs(rf"{scratch_folder}\{table_name}")
            if not arcpy.Exists(scratch_workspace):
                arcpy.management.CreateFileGDB(rf"{scratch_folder}\{table_name}", f"scratch")
        del scratch_workspace

        # Setup worker workspace and copy data
        datasets = [rf"{project_gdb}\Datasets", rf"{project_gdb}\{table_name}_LayerSpeciesYearImageName",]
        if not any(arcpy.management.GetCount(d)[0] == 0 for d in datasets):

            arcpy.management.CreateFileGDB(rf"{scratch_folder}", f"{table_name}")
            arcpy.AddMessage("\tCreate File GDB: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

            arcpy.management.Copy(rf"{project_gdb}\Datasets", rf"{region_gdb}\Datasets")
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

            arcpy.management.Copy(rf"{project_gdb}\{table_name}_LayerSpeciesYearImageName", rf"{region_gdb}\{table_name}_LayerSpeciesYearImageName")
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        else:
            arcpy.AddWarning(f"One or more datasets contains zero records!!")
            for d in datasets:
                arcpy.AddMessage(f"\t{os.path.basename(d)} has {arcpy.management.GetCount(d)[0]} records")
                del d
            raise SystemExit

        if "datasets" in locals().keys(): del datasets

        del scratch_folder, project_gdb

        results  = []

        try:

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
            Delete = True
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
        import create_mosaics_worker
        importlib.reload(create_mosaics_worker)

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
