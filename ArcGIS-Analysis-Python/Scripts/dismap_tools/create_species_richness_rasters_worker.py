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

def print_table(table=""):
    try:
        """ Print first 5 rows of a table """
        desc = arcpy.da.Describe(table)
        fields = [f.name for f in desc["fields"] if f.type == "String"]
        #Get OID field
        oid    = desc["OIDFieldName"]
        # Use SQL TOP to sort field values
        arcpy.AddMessage(f"{', '.join(fields)}")
        for row in arcpy.da.SearchCursor(table, fields, f"{oid} <= 5"):
            arcpy.AddMessage(row)
            del row
        del desc, fields, oid
        del table
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

def worker(region_gdb=""):
    try:
        # Test if passed workspace exists, if not sys.exit()
        if not arcpy.Exists(region_gdb):
            arcpy.AddError(f"{os.path.basename(region_gdb)} is missing!!")
            sys.exit()

        # Import
        import numpy as np
        from arcpy import metadata as md
        # Import the dismap module to access tools
        import dismap_tools

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

        arcpy.AddMessage(f"Table Name: {table_name}\n\tProject Folder: {project_folder}\n\tScratch Folder: {scratch_folder}\n")

        del scratch_folder

        # Set basic workkpace variables
        arcpy.env.workspace                = region_gdb
        arcpy.env.scratchWorkspace         = scratch_workspace
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.env.pyramid                  = "PYRAMIDS -1 BILINEAR LZ77 NO_SKIP"
        arcpy.env.resamplingMethod         = "BILINEAR"
        arcpy.env.rasterStatistics         = "STATISTICS 1 1"

        arcpy.AddMessage(f"Creating {table_name} Species Richness Rasters")

        arcpy.AddMessage("\tGet list of variables from the 'Datasets' table")

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
        #geographic_area = region_list[1]
        datasetcode     = region_list[2]
        cell_size       = region_list[3]
        del region_list


        if isinstance(cell_size, type('str')):
            cell_size = int(cell_size)
        else:
            pass

        arcpy.AddMessage(f"\tGet the 'rowCount', 'columnCount', and 'lowerLeft' corner of '{table_name}_Raster_Mask'")
        # These are used later to set the rows and columns for a zero numpy array
        rowCount = int(arcpy.management.GetRasterProperties(region_raster_mask, "ROWCOUNT" ).getOutput(0))
        columnCount = int(arcpy.management.GetRasterProperties(region_raster_mask, "COLUMNCOUNT" ).getOutput(0))

        # Create Raster from Array
        raster_mask_extent = arcpy.Raster(region_raster_mask)
        lowerLeft = arcpy.Point(raster_mask_extent.extent.XMin, raster_mask_extent.extent.YMin)
        del raster_mask_extent

        arcpy.AddMessage("\tSet the 'outputCoordinateSystem' based on the projection information for the geographic region")
        #geographic_area_sr = rf"{project_folder}\Dataset_Shapefiles\{table_name}\{geographic_area}.prj"
        #geographic_area_sr = arcpy.Describe(region_raster_mask).spatialReference
        #geographic_area_sr = rf"{project_folder}\Dataset_Shapefiles\{table_name}\{geographic_area}.prj"
        # Set the output coordinate system to what is needed for the
        # DisMAP project
        arcpy.env.outputCoordinateSystem = arcpy.Describe(region_raster_mask).spatialReference
        #del geographic_area_sr, geographic_area, psr
        #del geographic_area

        arcpy.AddMessage("\tGet information for input rasters")

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
        #    arcpy.AddMessage(input_raster, input_rasters[input_raster])
        #    del input_raster

        arcpy.AddMessage("\tSet the output and scratch paths")

        # Set species_richness_path
        species_richness_path         = rf"{project_folder}\Images\{table_name}\_Species Richness"
        species_richness_scratch_path = rf"{project_folder}\Scratch\{table_name}\_Species Richness"

        if not os.path.exists(species_richness_path):
            os.makedirs(species_richness_path)
        if not os.path.exists(species_richness_scratch_path):
            os.makedirs(species_richness_scratch_path)

        years = sorted(list(set([input_rasters[input_raster][2] for input_raster in input_rasters])))

        arcpy.AddMessage("\tProcessing all species")

        for year in years:

            layercode_year_richness = os.path.join(species_richness_path, f"{table_name}_Species_Richness_{year}.tif")

            #if not arcpy.Exists(layercode_year_richness):

            arcpy.AddMessage(f"\t\tProcessing rasters for year: {year}")

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

            arcpy.AddMessage(f"\t\tCreating Species Richness Raster for year: {year}")

            # Cast array as float321
            richnessArray = richnessArray.astype('float32')

            # Convert Array to Raster
            with arcpy.EnvManager(scratchWorkspace=species_richness_scratch_path, workspace = species_richness_path):
                richnessArrayRaster = arcpy.NumPyArrayToRaster(richnessArray, lowerLeft, cell_size, cell_size, -3.40282346639e+38) #-3.40282346639e+38
                richnessArrayRaster.save(layercode_year_richness)
                del richnessArrayRaster
                # Add statitics
                arcpy.management.CalculateStatistics(layercode_year_richness)

            raster_md = md.Metadata(layercode_year_richness)
            raster_md.title = os.path.basename(layercode_year_richness).replace("_", " ")
            raster_md.save()
            raster_md.synchronize("ALWAYS")
            raster_md.save()
            del raster_md

            del richnessArray, rasters

            #else:
            #    arcpy.AddMessage(f"\t\t{os.path.basename(layercode_year_richness)} exists")

            del year, layercode_year_richness

        del years, species_richness_path, species_richness_scratch_path

            # ###--->>>

        arcpy.AddMessage("\tCreating the {table_name} Core Species Richness Rasters")

        # Set core_species_richness_path
        core_species_richness_path         = rf"{project_folder}\Images\{table_name}\_Core Species Richness"
        core_species_richness_scratch_path = rf"{project_folder}\Scratch\{table_name}\_Core Species Richness"

        if not os.path.exists(core_species_richness_path):
            os.makedirs(core_species_richness_path)
        if not os.path.exists(core_species_richness_scratch_path):
            os.makedirs(core_species_richness_scratch_path)

        years = sorted(list(set([input_rasters[input_raster][2] for input_raster in input_rasters if input_rasters[input_raster][1] == "Yes"])))

        # ###--->>>
        arcpy.AddMessage("\t\tProcessing Core Species")

        for year in years:

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

            arcpy.AddMessage(f"\t\tCreating Core Species Richness Raster for year: {year}")

            # Cast array as float32
            richnessArray = richnessArray.astype('float32')

            # Convert Array to Raster
            with arcpy.EnvManager(scratchWorkspace=core_species_richness_scratch_path, workspace = core_species_richness_path):
                richnessArrayRaster = arcpy.NumPyArrayToRaster(richnessArray, lowerLeft, cell_size, cell_size, -3.40282346639e+38) #-3.40282346639e+38
                richnessArrayRaster.save(layercode_year_richness)
                del richnessArrayRaster
                # Add statistics
                arcpy.management.CalculateStatistics(layercode_year_richness)

            raster_md = md.Metadata(layercode_year_richness)
            raster_md.title = os.path.basename(layercode_year_richness).replace("_", " ")
            raster_md.save()
            del raster_md

            del richnessArray, rasters
            #else:
            #    arcpy.AddMessage(f"\t\t{os.path.basename(layercode_year_richness)} exists")

            del year, layercode_year_richness
        del years, core_species_richness_path, core_species_richness_scratch_path

        # End of business logic for the worker function
        arcpy.AddMessage(f"Processing for: {table_name} complete")

        # Clean up
        # Declared Variables for this function only
        del rowCount, columnCount, lowerLeft, input_rasters
        del cell_size
        del region_raster_mask

        # Declared Variables for this function only
        del datasetcode
        # Basic variables
        del table_name, project_folder, scratch_workspace
        # Imports
        del md, dismap_tools, np
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
        from create_species_richness_rasters_director import preprocessing
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

        # Clear Scratch Folder
        ClearScratchFolder = False
        if ClearScratchFolder:
            dismap_tools.clear_folder(folder=rf"{os.path.dirname(project_gdb)}\Scratch")
        else:
            pass
        del ClearScratchFolder

        ##        # Set worker parameters
        ##        #table_name = "AI_IDW"
        ##        table_name = "HI_IDW"
        ##        #table_name = "NBS_IDW"
        ##        #table_name = "ENBS_IDW"

        table_names = ["HI_IDW"]

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
                sys.exit()

            del table_name, region_gdb

        del table_names

        # Declared Varaiables
        # Imports
        del dismap_tools, preprocessing
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
