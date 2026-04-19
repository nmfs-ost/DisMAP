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
        if not arcpy.Exists(rf"{region_gdb}"):
            sys.exit()(f"{os.path.basename(region_gdb)} is missing!!")

        # Import the dismap module to access tools
        #import dev_dismap_tools
        #importlib.reload(dev_dismap_tools)

        # Import the worker module to process data
        # N/A

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

        arcpy.AddMessage(f"Table Name: {table_name}\nProject Folder: {os.path.basename(project_folder)}\nScratch Folder: {os.path.basename(scratch_folder)}\n")

        # Set basic workkpace variables
        arcpy.env.workspace                 = region_gdb
        arcpy.env.scratchWorkspace          = scratch_workspace
        arcpy.env.overwriteOutput           = True
        arcpy.env.parallelProcessingFactor  = "100%"
        #arcpy.env.compression               = "LZ77"
        #arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"
        arcpy.env.pyramid                   = "PYRAMIDS -1 BILINEAR LZ77 NO_SKIP"
        arcpy.env.resamplingMethod          = "BILINEAR"
        arcpy.env.rasterStatistics          = "STATISTICS 1 1"
        #arcpy.env.buildStatsAndRATForTempRaster = True

        # DatasetCode, CSVFile, TransformUnit, TableName, GeographicArea, CellSize,
        # PointFeatureType, FeatureClassName, Region, Season, DateCode, Status,
        # DistributionProjectCode, DistributionProjectName, SummaryProduct,
        # FilterRegion, FilterSubRegion, FeatureServiceName, FeatureServiceTitle,
        # MosaicName, MosaicTitle, ImageServiceName, ImageServiceTitle

        # Get values for table_name from Datasets table
        fields = ["TableName", "GeographicArea", "DatasetCode", "CellSize", "Region", "Season", "DistributionProjectCode", "SummaryProduct"]
        region_list = [row for row in arcpy.da.SearchCursor(rf"{region_gdb}\Datasets", fields, where_clause = f"TableName = '{table_name}'")][0]
        del fields

        # Assigning variables from items in the chosen table list
        # ['AI_IDW', 'AI_IDW_Region', 'AI', 'Aleutian Islands', None, 'IDW']
        table_name      = region_list[0]
        #geographic_area = region_list[1]
        datasetcode     = region_list[2]
        cell_size       = region_list[3] if not isinstance(region_list[3], type("str")) else int(region_list[3])
        region          = region_list[4]
        season          = region_list[5]
        distri_code     = region_list[6]
        summary_product = region_list[7]
        del region_list

        #print(cell_size)
        #print(type(cell_size))
        #sys.exit()
        arcpy.env.cellSize = cell_size

        # Start of business logic for the worker function
        arcpy.AddMessage(f"Processing: {table_name}")

        # Business logic for the worker function

        #geographic_area_sr = rf"{project_folder}\Dataset_Shapefiles\{table_name}\{geographic_area}.prj"
        # Set the output coordinate system to what is needed for the
        # DisMAP project
        #psr = arcpy.SpatialReference(geographic_area_sr)
        #arcpy.env.outputCoordinateSystem = psr
        #del geographic_area_sr, geographic_area, psr

        region_raster_mask        = rf"{region_gdb}\{table_name}_Raster_Mask"
        layerspeciesyearimagename = rf"{region_gdb}\{table_name}_LayerSpeciesYearImageName"

        arcpy.env.outputCoordinateSystem = arcpy.Describe(region_raster_mask).spatialReference

        output_rasters = {}

        # ##---> This block creates the folder structure in the Images folder
        #fields = "DatasetCode;Region;Season;Species;CommonName;SpeciesCommonName;CoreSpecies;Year;StdTime;Variable;Value;Dimensions"
        fields = ['ImageName', 'Variable', 'Species', 'Year']

        #with arcpy.da.SearchCursor(layerspeciesyearimagename, fields, where_clause = f"TableName = '{table_name}'") as cursor:
        with arcpy.da.SearchCursor(layerspeciesyearimagename, fields) as cursor:
            for row in cursor:
                image_name, variable, species, year = row[0], row[1], row[2], row[3]
                #if variable not in variables: variables.append(variable)
                #arcpy.AddMessage(f"{variable}, {image_name}, {species}, {year}")
                #variable = f"_{variable}" if "Species Richness" in variable else variable
                if "Species Richness" not in variable:
                    output_raster_path = rf"{project_folder}\Images\{table_name}\{variable}\{image_name}.tif"
                    #arcpy.AddMessage(output_raster_path)
                    output_rasters[image_name] = [image_name, variable, species, year, output_raster_path]
                    image_folder = os.path.dirname(output_raster_path)
                    #arcpy.AddMessage(image_folder)
                    if not os.path.exists(image_folder):
                        os.makedirs(image_folder)
                    #arcpy.AddMessage(output_raster_path)
                    #arcpy.AddMessage(os.path.dirname(output_raster_path))
                    #arcpy.AddMessage(image_folder)
                    del image_folder
                    del output_raster_path

                del row, image_name, variable, species, year
            del cursor

        del fields

        del layerspeciesyearimagename

        arcpy.AddMessage(f'Generating {table_name} Biomass Rasters')

        sample_locations = rf"{table_name}_Sample_Locations"

        arcpy.AddMessage(f"\tMake Feature Layer for {sample_locations}")

        # Prepare the points layer
        sample_locations_path = rf"{region_gdb}\{sample_locations}"
        sample_locations_path_layer = arcpy.management.MakeFeatureLayer(sample_locations_path, "Region Sample Locations Layer")
        del sample_locations_path

        if summary_product == "Yes":
            # Add the YearWeights feild
            fields =  [f.name for f in arcpy.ListFields(sample_locations_path_layer) if f.type not in ['Geometry', 'OID']]
            if "YearWeights" not in fields:
                # Add the YearWeights field to the Dataset. This is used for the IDW modeling later
                arcpy.management.AddField(sample_locations_path_layer, "YearWeights", "SHORT", field_alias = "Year Weights")
            del fields

        getcount = arcpy.management.GetCount(sample_locations_path_layer)[0]
        arcpy.AddMessage(f'\t{sample_locations} has {getcount} records')
        del getcount

        for output_raster in output_rasters:
            image_name, variable, species, year, output_raster_path =  output_rasters[output_raster]

            #if not arcpy.Exists(output_raster_path):

            msg = f"\n\t\tImage Name: {output_raster}\n"
            msg = msg + f"\t\t\tVariable:      {variable}\n"
            msg = msg + f"\t\t\tSpecies:       {species}\n"
            msg = msg + f"\t\t\tYear:          {year}\n"
            msg = msg + f"\t\t\tOutput Raster: {os.path.basename(output_raster_path)}\n"
            arcpy.AddMessage(msg)
            del msg

            arcpy.AddMessage('\t\t\tSelect Layer by Attribute: "CLEAR_SELECTION"')

            arcpy.management.SelectLayerByAttribute( sample_locations_path_layer, "CLEAR_SELECTION" )

            arcpy.AddMessage(f"\t\t\tSelect Layer by Attribute: Species = '{species}' AND Year = {year}")

            # Select for species and year
            #print(sample_locations_path_layer)
            #print(f"Species = '{species}' AND Year = {year}")
            arcpy.management.SelectLayerByAttribute( in_layer_or_view = sample_locations_path_layer,
                                                     selection_type = "NEW_SELECTION",
                                                     where_clause = f"Species = '{species}' And Year = '{year}'",
                                                     invert_where_clause=None
                                                    )

            # Get the count of records for selected species
            getcount = arcpy.management.GetCount(sample_locations_path_layer)[0]
            arcpy.AddMessage(f"\t\t\t{sample_locations} has {getcount} records for {species} and year {year}")
            del getcount

            arcpy.AddMessage(f"\t\t\tCreating Raster File {output_raster}.tif for {species} and {year}")

            #if summary_product == "Yes":

            arcpy.AddMessage("\t\t\tProcessing IDW")

            # Select weighted years
            arcpy.management.SelectLayerByAttribute( sample_locations_path_layer,
                                                     "NEW_SELECTION",
                                                     f"Species = '{species}' AND Year >= ({year-2}) AND Year <= ({year+2})"
                                                    )

            # Get the count of records for selected species
            getcount = arcpy.management.GetCount(sample_locations_path_layer)[0]

            arcpy.AddMessage(f"\t\t\t\t{sample_locations_path_layer} has {getcount} records for {species} and from years {year-2} to {year+2}")
            del getcount

            # Calculate YearWeights=3-(abs(Tc-Ti))
            arcpy.management.CalculateField(in_table=sample_locations_path_layer, field="YearWeights", expression=f"3 - (abs({int(year)} - !Year!))", expression_type="PYTHON", code_block="")

            # we need to set the mask and extent of the environment, or the raster and items may not come out correctly.
            arcpy.env.extent     = arcpy.Describe(region_raster_mask).extent
            arcpy.env.mask       = region_raster_mask
            arcpy.env.snapRaster = region_raster_mask

            # Set variables for search neighborhood
            majSemiaxis = int(cell_size) * 1000
            minSemiaxis = int(cell_size) * 1000
            angle = 0
            maxNeighbors = 15
            minNeighbors = 10
            sectorType   = "ONE_SECTOR"
            searchNeighbourhood = arcpy.SearchNeighborhoodStandard(majSemiaxis, minSemiaxis, angle, maxNeighbors, minNeighbors, sectorType)
            #print(majSemiaxis, minSemiaxis, angle, maxNeighbors, minNeighbors, sectorType)

            del majSemiaxis, minSemiaxis, angle
            del maxNeighbors, minNeighbors, sectorType

            # Check out the ArcGIS Geostatistical Analyst extension license
            arcpy.CheckOutExtension("GeoStats")

            #tmp_raster = os.path.join(ScratchFolder, f"{output_raster}.tif")
            tmp_raster = f"memory\\{output_raster}"

            #print(sample_locations_path_layer)
            #print(tmp_raster)
            #print(cell_size)
            #print(searchNeighbourhood)
            #sys.exit()

            # Execute IDW using the selected selected species, years, and MapValue
            arcpy.ga.IDW(in_features         = sample_locations_path_layer,
                         z_field             = 'MapValue',
                         out_ga_layer        = '',
                         out_raster          = tmp_raster,
                         cell_size           = cell_size,
                         power               = 2,
                         search_neighborhood = searchNeighbourhood,
                         weight_field        = "YearWeights")

            del searchNeighbourhood

            arcpy.ClearEnvironment("extent")
            arcpy.ClearEnvironment("mask")
            arcpy.ClearEnvironment("snapRaster")

            # Check In GeoStats Extension
            arcpy.CheckInExtension("GeoStats")

            # Execute Power to convert the raster back to WTCPUE from WTCPUECubeRoot
            out_cube = arcpy.sa.Power(tmp_raster, 3)
            #out_cube.save(tmp_raster_power)
            out_cube.save(output_raster_path)
            del out_cube

            if tmp_raster:
                arcpy.management.Delete(tmp_raster)
            del tmp_raster

            # Reset the YearWeights to None
            arcpy.management.CalculateField(in_table=sample_locations_path_layer, field="YearWeights", expression="None", expression_type="PYTHON", code_block="")

            # Clear selection
            arcpy.management.SelectLayerByAttribute( sample_locations_path_layer, "CLEAR_SELECTION" )

            from arcpy import metadata as md
            tif_md = md.Metadata(output_raster_path)
            tif_md.title = image_name.replace("_", " ")
            tif_md.save()
            tif_md.synchronize("ALWAYS")
            tif_md.save()
            del md, tif_md

            arcpy.management.BuildPyramids(
                                            in_raster_dataset   = output_raster_path,
                                            pyramid_level       = -1,
                                            SKIP_FIRST          = "NONE",
                                            resample_technique  = "BILINEAR",
                                            compression_type    = "DEFAULT",
                                            compression_quality = 75,
                                            skip_existing       = "OVERWRITE"
                                          )

            # Clean up
            del image_name, variable, species, year, output_raster_path, output_raster

        del sample_locations
        # Delete sample_locations_path_layer
        arcpy.management.Delete(sample_locations_path_layer)
        del sample_locations_path_layer

        # End of business logic for the worker function
        arcpy.AddMessage(f"Processing for: {table_name} complete")

        # Clean up
        del output_rasters
        del region_raster_mask

        # Declared Variables for this function only
        del region, season, distri_code, summary_product
        del datasetcode, cell_size
        # Basic variables
        del table_name, scratch_folder, project_folder, scratch_workspace
        # Imports
        #del dismap
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
        from create_rasters_director import preprocessing
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