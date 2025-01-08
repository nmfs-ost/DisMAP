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
        import dismap
        importlib.reload(dismap)

        # Import
        import numpy as np

        # Set History and Metadata logs, set serverity and message level
        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        # Set basic workkpace variables
        table_name         = os.path.basename(region_gdb).replace(".gdb","")
        scratch_folder     = os.path.dirname(region_gdb)
        project_folder     = os.path.dirname(scratch_folder)
        scratch_workspace  = rf"{scratch_folder}\{table_name}\scratch.gdb"
        region_raster_mask = rf"{region_gdb}\{table_name}_Raster_Mask"

        arcpy.AddMessage(f"Table Name: {table_name}\nProject Folder: {project_folder}\nScratch Folder: {scratch_folder}\n")

        del scratch_folder

        # Set basic workkpace variables
        arcpy.env.workspace                = region_gdb
        arcpy.env.scratchWorkspace         = scratch_workspace
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.env.pyramid                  = "PYRAMIDS -1 BILINEAR LZ77 NO_SKIP"
        arcpy.env.resamplingMethod         = "BILINEAR"
        arcpy.env.rasterStatistics         = u'STATISTICS 1 1'

        arcpy.AddMessage(f"Creating {table_name} Species Richness Rasters")

        arcpy.AddMessage(f"\tGet list of variables from the 'Datasets' table")

        # DatasetCode, CSVFile, TransformUnit, TableName, GeographicArea, CellSize,
        # PointFeatureType, FeatureClassName, Region, Season, DateCode, Status,
        # DistributionProjectCode, DistributionProjectName, SummaryProduct,
        # FilterRegion, FilterSubRegion, FeatureServiceName, FeatureServiceTitle,
        # MosaicName, MosaicTitle, ImageServiceName, ImageServiceTitle

        # Get values for table_name from Datasets table
        fields = ["TableName", "GeographicArea", "DatasetCode", "CellSize"]
        region_list = [row for row in arcpy.da.SearchCursor(rf"{region_gdb}\Datasets", fields, where_clause = f"TableName = '{table_name}'")][0]
        del fields

        # Assigning variables from items in the chosen table list
        # ['AI_IDW', 'AI_IDW_Region', 'AI', 'Aleutian Islands', None, 'IDW']
        table_name      = region_list[0]
        geographic_area = region_list[1]
        datasetcode     = region_list[2]
        cell_size       = region_list[3]
        del region_list

        arcpy.AddMessage(f"\tGet the 'rowCount', 'columnCount', and 'lowerLeft' corner of '{table_name}_Raster_Mask'")
        # These are used later to set the rows and columns for a zero numpy array
        rowCount = int(arcpy.management.GetRasterProperties(region_raster_mask, "ROWCOUNT" ).getOutput(0))
        columnCount = int(arcpy.management.GetRasterProperties(region_raster_mask, "COLUMNCOUNT" ).getOutput(0))

        # Create Raster from Array
        raster_mask_extent = arcpy.Raster(region_raster_mask)
        lowerLeft = arcpy.Point(raster_mask_extent.extent.XMin, raster_mask_extent.extent.YMin)
        del raster_mask_extent

        arcpy.AddMessage(f"\tSet the 'outputCoordinateSystem' based on the projection information for the geographic region")

        geographic_area_sr = rf"{project_folder}\Dataset Shapefiles\{table_name}\{geographic_area}.prj"
        # Set the output coordinate system to what is needed for the
        # DisMAP project
        psr = arcpy.SpatialReference(geographic_area_sr)
        arcpy.env.outputCoordinateSystem = psr
        del geographic_area_sr, geographic_area, psr

        arcpy.AddMessage(f"\tGet information for input rasters")

        layerspeciesyearimagename = rf"{region_gdb}\{table_name}_LayerSpeciesYearImageName"

        fields = ['DatasetCode', 'CoreSpecies', 'Year', 'Variable', 'ImageName']
        input_rasters = {}
        input_rasters_path = rf"{project_folder}\Images\{table_name}"

        with arcpy.da.SearchCursor(layerspeciesyearimagename, fields, where_clause=f"Variable NOT IN ('Core Species Richness', 'Species Richness') and DatasetCode = '{datasetcode}'") as cursor:
            for row in cursor:
                _datasetcode    = row[0]
                _corespecies    = row[1]
                _year           = row[2]
                _variable       = row[3]
                _image          = row[4]
                input_rasters[f"{_image}.tif"] = [_variable, _corespecies, _year, os.path.join(input_rasters_path, _variable, f"{_image}.tif")]
                del row, _datasetcode, _corespecies, _year, _variable, _image
            del cursor
        del input_rasters_path, fields, layerspeciesyearimagename

        #for input_raster in input_rasters:
        #    print(input_raster, input_rasters[input_raster])
        #    del input_raster

        arcpy.AddMessage(f"\tSet the output and scratch paths")

        # Set species_richness_path
        species_richness_path         = rf"{project_folder}\Images\{table_name}\_Species Richness"
        species_richness_scratch_path = rf"{project_folder}\Scratch\{table_name}\_Species Richness"

        if not os.path.exists(species_richness_path):
            os.makedirs(species_richness_path)
        if not os.path.exists(species_richness_scratch_path):
            os.makedirs(species_richness_scratch_path)

        years = sorted(list(set([input_rasters[input_raster][2] for input_raster in input_rasters])))

        arcpy.AddMessage(f"\tProcessing all species")

        for year in years:
            arcpy.AddMessage(f"\t\tYear: {year}")

            layercode_year_richness = os.path.join(species_richness_path, f"{table_name}_Species_Richness_{year}.tif")

            #if not arcpy.Exists(layercode_year_richness):

            arcpy.AddMessage("\t\tProcessing rasters for the year")

            richnessArray = np.zeros((rowCount, columnCount), dtype='float32', order='C')

            rasters = [r for r in input_rasters if input_rasters[r][2] == year]

            # For each raster exported, create the Con mask
            for raster in rasters:
                arcpy.AddMessage(f"\t\t\tProcessing the {raster} raster")

                _in_raster = input_rasters[raster][3]

                rasterArray = arcpy.RasterToNumPyArray(_in_raster, nodata_to_value=np.nan)

                rasterArray[rasterArray < 0.0] = np.nan

                rasterArray[rasterArray > 0.0] = 1.0

                #add rasterArray to richnessArray
                richnessArray = np.add(richnessArray, rasterArray) # Can also use: richnessArray + rasterArray
                del rasterArray, _in_raster, raster

            arcpy.AddMessage("\t\tCreating Species Richness Raster")

            # Cast array as float32
            richnessArray = richnessArray.astype('float32')

            # Convert Array to Raster
            with arcpy.EnvManager(scratchWorkspace=species_richness_scratch_path, workspace = species_richness_path):
                richnessArrayRaster = arcpy.NumPyArrayToRaster(richnessArray, lowerLeft, cell_size, cell_size, -3.40282346639e+38) #-3.40282346639e+38
                richnessArrayRaster.save(layercode_year_richness)
                del richnessArrayRaster
                # Add statitics
                arcpy.management.CalculateStatistics(layercode_year_richness)

            from arcpy import metadata as md
            raster_md = md.Metadata(layercode_year_richness)
            raster_md.title = os.path.basename(layercode_year_richness).replace("_", " ")
            raster_md.save()
            del raster_md, md

            del richnessArray, rasters

            #else:
            #    arcpy.AddMessage(f"\t\t{os.path.basename(layercode_year_richness)} exists")

            del year, layercode_year_richness

        del years, species_richness_path, species_richness_scratch_path

            # ###--->>>

        arcpy.AddMessage(f"\tCreating the {table_name} Core Species Richness Rasters")

        # Set core_species_richness_path
        core_species_richness_path         = rf"{project_folder}\Images\{table_name}\_Core Species Richness"
        core_species_richness_scratch_path = rf"{project_folder}\Scratch\{table_name}\_Core Species Richness"

        if not os.path.exists(core_species_richness_path):
            os.makedirs(core_species_richness_path)
        if not os.path.exists(core_species_richness_scratch_path):
            os.makedirs(core_species_richness_scratch_path)

        years = sorted(list(set([input_rasters[input_raster][2] for input_raster in input_rasters if input_rasters[input_raster][1] == "Yes"])))

        # ###--->>>
        arcpy.AddMessage(f"\t\tProcessing Core Species")

        for year in years:
            arcpy.AddMessage(f"\t\tYear: {year}")

            layercode_year_richness = os.path.join(core_species_richness_path, f"{table_name}_Core_Species_Richness_{year}.tif")

            #if not arcpy.Exists(layercode_year_richness):

            richnessArray = np.zeros((rowCount, columnCount), dtype='float32', order='C')

            rasters = [r for r in input_rasters if input_rasters[r][2] == year and input_rasters[r][1] == "Yes"]

            arcpy.AddMessage("\t\tProcessing rasters")

            # For each raster exported, create the Con mask
            for raster in rasters:
                arcpy.AddMessage(f"\t\t\tProcessing {raster} raster")

                _in_raster = input_rasters[raster][3]

                rasterArray = arcpy.RasterToNumPyArray(_in_raster, nodata_to_value=np.nan)
                rasterArray[rasterArray < 0.0] = np.nan

                rasterArray[rasterArray > 0.0] = 1.0

                #add rasterArray to richnessArray
                richnessArray = np.add(richnessArray, rasterArray)
                # Can also use: richnessArray + rasterArray
                del rasterArray, _in_raster, raster

            arcpy.AddMessage("\t\tCreating Core Species Richness Raster")

            # Cast array as float32
            richnessArray = richnessArray.astype('float32')

            # Convert Array to Raster
            with arcpy.EnvManager(scratchWorkspace=core_species_richness_scratch_path, workspace = core_species_richness_path):
                richnessArrayRaster = arcpy.NumPyArrayToRaster(richnessArray, lowerLeft, cell_size, cell_size, -3.40282346639e+38) #-3.40282346639e+38
                richnessArrayRaster.save(layercode_year_richness)
                del richnessArrayRaster
                # Add statistics
                arcpy.management.CalculateStatistics(layercode_year_richness)

            from arcpy import metadata as md
            raster_md = md.Metadata(layercode_year_richness)
            raster_md.title = os.path.basename(layercode_year_richness).replace("_", " ")
            raster_md.save()
            del raster_md, md

            del richnessArray, rasters
            #else:
            #    arcpy.AddMessage(f"\t\t{os.path.basename(layercode_year_richness)} exists")

            del year, layercode_year_richness
        del years, core_species_richness_path, core_species_richness_scratch_path

        results = [region_gdb]

        # End of business logic for the worker function
        arcpy.AddMessage(f"Processing for: {table_name} complete")

        # Clean up
        # Variables for this function only
        del rowCount, columnCount, lowerLeft, input_rasters
        del datasetcode, cell_size
        del region_raster_mask

        # Basic variables
        del table_name, project_folder, scratch_workspace
        # Imports
        del dismap, np
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
            raise SystemExit(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

def main(project=""):
    try:
        pass

        from create_species_richness_rasters_worker import worker

        arcpy.env.overwriteOutput           = True
        arcpy.env.parallelProcessingFactor  = "100%"

        base_project_folder = os.path.dirname(os.path.dirname(__file__))
        project_gdb         = rf"{base_project_folder}\{project}\{project}.gdb"
        project_folder      = rf"{base_project_folder}\{project}"
        scratch_folder      = rf"{project_folder}\Scratch"
        del project_folder, base_project_folder

        # Test if passed workspace exists, if not raise SystemExit
        if not arcpy.Exists(project_gdb):
            raise SystemExit(line_info(f"{os.path.basename(project_gdb)} is missing!!"))

        if not arcpy.Exists(rf"{scratch_folder}\scratch.gdb"):
            if not arcpy.Exists(scratch_folder):
                os.makedirs(rf"{scratch_folder}")
            if not arcpy.Exists(rf"{scratch_folder}\scratch.gdb"):
                arcpy.management.CreateFileGDB(rf"{scratch_folder}", f"scratch")

        table_name     = "HI_IDW"
        #table_name     = "SEUS_SPR_IDW"
        region_gdb     = rf"{scratch_folder}\{table_name}.gdb"
        scratch_workspace = rf"{scratch_folder}\{table_name}\scratch.gdb"

        if not arcpy.Exists(scratch_workspace):
            os.makedirs(rf"{scratch_folder}\{table_name}")
            if not arcpy.Exists(scratch_workspace):
                arcpy.management.CreateFileGDB(rf"{scratch_folder}\{table_name}", f"scratch")
        del scratch_workspace

        datasets = [rf"{project_gdb}\Datasets", rf"{project_gdb}\{table_name}_LayerSpeciesYearImageName"]
        if not any(arcpy.management.GetCount(d)[0] == 0 for d in datasets):

            arcpy.management.CreateFileGDB(rf"{scratch_folder}", f"{table_name}")
            arcpy.AddMessage("\tCreate File GDB: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

            arcpy.management.Copy(rf"{project_gdb}\Datasets", rf"{region_gdb}\Datasets")
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

            arcpy.management.Copy(rf"{project_gdb}\{table_name}_LayerSpeciesYearImageName", rf"{region_gdb}\{table_name}_LayerSpeciesYearImageName")
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

            arcpy.management.Copy(rf"{project_gdb}\{table_name}_Raster_Mask", rf"{region_gdb}\{table_name}_Raster_Mask")
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        else:
            arcpy.AddWarning(f"One or more datasets contains zero records!!")
            for d in [rf"{project_gdb}\Datasets", rf"{project_gdb}\{table_name}_LayerSpeciesYearImageName"]:
                arcpy.AddMessage(f"\t{os.path.basename(d)} has {arcpy.management.GetCount(d)[0]} records")
                del d
            raise SystemExit(f"One or more datasets contains zero records!!")

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
            raise SystemExit(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

if __name__ == '__main__':
    try:
        # Import this Python module
        import create_species_richness_rasters_worker
        importlib.reload(create_species_richness_rasters_worker)

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
