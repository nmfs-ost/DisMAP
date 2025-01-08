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

        # Set basic workkpace variables
        table_name         = os.path.basename(region_gdb).replace(".gdb","")
        scratch_folder     = os.path.dirname(region_gdb)
        project_folder     = os.path.dirname(scratch_folder)
        scratch_workspace  = rf"{scratch_folder}\{table_name}\scratch.gdb"

        arcpy.AddMessage(f"Table Name: {table_name}\nProject Folder: {project_folder}\nScratch Folder: {scratch_folder}\n")

        # Set basic workkpace variables
        arcpy.env.workspace                 = region_gdb
        arcpy.env.scratchWorkspace          = scratch_workspace
        arcpy.env.overwriteOutput              = True
        arcpy.env.parallelProcessingFactor  = "100%"
        #arcpy.env.compression               = "LZ77"
        #arcpy.env.geographicTransformations = "WGS_1984_(ITRF08)_To_NAD_1983_2011"
        arcpy.env.pyramid                   = "PYRAMIDS -1 BILINEAR LZ77 NO_SKIP"
        arcpy.env.resamplingMethod          = "BILINEAR"
        arcpy.env.rasterStatistics          = u'STATISTICS 1 1'
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
        geographic_area = region_list[1]
        datasetcode     = region_list[2]
        cell_size       = region_list[3]
        region          = region_list[4]
        season          = region_list[5]
        distri_code     = region_list[6]
        summary_product = region_list[7]
        del region_list

        arcpy.env.cellSize = cell_size

        # Start of business logic for the worker function
        arcpy.AddMessage(f"Processing: {table_name}")

        # Business logic for the worker function

        geographic_area_sr = rf"{project_folder}\Dataset Shapefiles\{table_name}\{geographic_area}.prj"
        # Set the output coordinate system to what is needed for the
        # DisMAP project
        psr = arcpy.SpatialReference(geographic_area_sr)
        arcpy.env.outputCoordinateSystem = psr
        del geographic_area_sr, geographic_area, psr

        region_raster_mask        = rf"{region_gdb}\{table_name}_Raster_Mask"
        layerspeciesyearimagename = rf"{region_gdb}\{table_name}_LayerSpeciesYearImageName"

        output_rasters = {}

        # ##---> This block creates the folder structure in the Images folder
        #fields = "DatasetCode;Region;Season;Species;CommonName;SpeciesCommonName;CoreSpecies;Year;StdTime;Variable;Value;Dimensions"
        fields = ['ImageName', 'Variable', 'Species', 'Year']

        with arcpy.da.SearchCursor(layerspeciesyearimagename, fields, where_clause = f"DatasetCode = '{datasetcode}'") as cursor:
            for row in cursor:
                image_name, variable, species, year = row[0], row[1], row[2], row[3]
                #if variable not in variables: variables.append(variable)
                #print(variable, image_name)
                #variable = f"_{variable}" if "Species Richness" in variable else variable
                if "Species Richness" not in variable:
                    output_raster_path = rf"{project_folder}\Images\{table_name}\{variable}\{image_name}.tif"
                    #print(output_raster_path)
                    output_rasters[image_name] = [image_name, variable, species, year, output_raster_path]
                    image_folder = os.path.dirname(output_raster_path)
                    #print(image_folder)
                    if not os.path.exists(image_folder):
                        os.makedirs(image_folder)
                    #print(output_raster_path)
                    #print(os.path.dirname(output_raster_path))
                    #print(image_folder)
                    del image_folder
                    del output_raster_path

                del row, image_name, variable, species, year
            del cursor

        del fields

        del layerspeciesyearimagename

        arcpy.AddMessage(f'Generating {table_name} Biomass Rasters')

        if "IDW" in table_name:
            point_locations = rf"{table_name}_Sample_Locations"
        elif "IDW" not in table_name:
            point_locations = rf"{table_name}_GRID_Points"
        else:
            pass

        arcpy.AddMessage(f"\tMake Feature Layer for {point_locations}")

        # Prepare the points layer
        point_locations_path = rf"{region_gdb}\{point_locations}"
        point_locations_path_layer = arcpy.management.MakeFeatureLayer(point_locations_path, "Region Sample Locations Layer")
        del point_locations_path

        if summary_product == "Yes":
            # Add the YearWeights feild
            fields =  [f.name for f in arcpy.ListFields(point_locations_path_layer) if f.type not in ['Geometry', 'OID']]
            if "YearWeights" not in fields:
                # Add the YearWeights field to the Dataset. This is used for the IDW modeling later
                arcpy.management.AddField(point_locations_path_layer, "YearWeights", "SHORT", field_alias = "Year Weights")
            del fields

        getcount = arcpy.management.GetCount(point_locations_path_layer)[0]
        arcpy.AddMessage(f'\t{point_locations} has {getcount} records')
        del getcount

        for output_raster in output_rasters:
            image_name, variable, species, year, output_raster_path =  output_rasters[output_raster]

            #if not arcpy.Exists(output_raster_path):

            msg = f"\n\t\tImage Name: {output_raster}\n"
            msg = msg + f"\t\t\tVariable:      {variable}\n"
            msg = msg + f"\t\t\tSpecies:       {species}\n"
            msg = msg + f"\t\t\tYear:          {year}\n"
            msg = msg + f"\t\t\tOutput Raster: {os.path.basename(output_raster_path)}\n"
            arcpy.AddMessage(msg); del msg

            arcpy.AddMessage(f'\t\t\tSelect Layer by Attribute: "CLEAR_SELECTION"')

            arcpy.management.SelectLayerByAttribute( point_locations_path_layer, "CLEAR_SELECTION" )

            arcpy.AddMessage(f'\t\t\tSelect Layer by Attribute: Species = "{species}" AND Year = {year}')

            # Select for species and year
            arcpy.management.SelectLayerByAttribute( point_locations_path_layer, "NEW_SELECTION", f"Species = '{species}' AND Year = {year}" )

            # Get the count of records for selected species
            getcount = arcpy.management.GetCount(point_locations_path_layer)[0]
            arcpy.AddMessage(f"\t\t\t{point_locations} has {getcount} records for {species} and year {year}")
            del getcount

            arcpy.AddMessage(f"\t\t\tCreating Raster File {output_raster}.tif for {species} and {year}")

            if summary_product == "Yes":
                arcpy.AddMessage(f"\t\t\tProcessing IDW")

                # Select weighted years
                arcpy.management.SelectLayerByAttribute( point_locations_path_layer, "NEW_SELECTION", f"Species = '{species}' AND Year >= ({year-2}) AND Year <= ({year+2})" )

                # Get the count of records for selected species
                getcount = arcpy.management.GetCount(point_locations_path_layer)[0]

                arcpy.AddMessage(f"\t\t\t\t{point_locations_path_layer} has {getcount} records for {species} and from years {year-2} to {year+2}")
                del getcount

                # Calculate YearWeights=3-(abs(Tc-Ti))
                arcpy.management.CalculateField(in_table=point_locations_path_layer, field="YearWeights", expression=f"3 - (abs({int(year)} - !Year!))", expression_type="PYTHON", code_block="")

                # we need to set the mask and extent of the environment, or the raster and items may not come out correctly.
                arcpy.env.extent     = arcpy.Describe(region_raster_mask).extent
                arcpy.env.mask       = region_raster_mask
                arcpy.env.snapRaster = region_raster_mask

                # Set variables for search neighborhood
                majSemiaxis = cell_size * 1000
                minSemiaxis = cell_size * 1000
                angle = 0
                maxNeighbors = 15
                minNeighbors = 10
                sectorType   = "ONE_SECTOR"
                searchNeighbourhood = arcpy.SearchNeighborhoodStandard(majSemiaxis, minSemiaxis, angle, maxNeighbors, minNeighbors, sectorType)

                del majSemiaxis, minSemiaxis, angle
                del maxNeighbors, minNeighbors, sectorType

                # Check out the ArcGIS Geostatistical Analyst extension license
                arcpy.CheckOutExtension("GeoStats")

                #tmp_raster = os.path.join(ScratchFolder, f"{output_raster}.tif")
                tmp_raster = f"memory\\{output_raster}"

                # Execute IDW using the selected selected species, years, and MapValue
                arcpy.ga.IDW(in_features         = point_locations_path_layer,
                             z_field             = 'MapValue',
                             out_ga_layer        = '',
                             out_raster          = tmp_raster,
                             #cell_size = '',
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

                # Reser the YearWeights to None
                arcpy.management.CalculateField(in_table=point_locations_path_layer, field="YearWeights", expression="None", expression_type="PYTHON", code_block="")

            elif summary_product == "No":
                arcpy.AddMessage(f"\t\t\tProcessing SDM")

                # we need to set the mask and extent of the environment, or the raster and items may not come out correctly.
                arcpy.env.extent     = arcpy.Describe(region_raster_mask).extent
                arcpy.env.mask       = region_raster_mask
                arcpy.env.snapRaster = region_raster_mask
                #del region_raster_mask

                # Set local variables
                inFeatures     = point_locations_path_layer
                valField       = 'MapValue'
                #outRaster      = tmp_raster
                outRaster      = output_raster_path
                assignmentType = "MEAN"
                priorityField  = ""
                cellSize       = cell_size

                # Run PointToRaster
                arcpy.conversion.PointToRaster(inFeatures, valField, outRaster, assignmentType, priorityField, cell_size)
                arcpy.AddMessage("\t\t\t\tPoint To Raster: \t{0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

                del inFeatures, valField, outRaster, assignmentType, priorityField, cellSize

                arcpy.ClearEnvironment("extent")
                arcpy.ClearEnvironment("mask")
                arcpy.ClearEnvironment("snapRaster")

# ##                # Set local variables
# ##                inPntFeat      = point_locations_path_layer
# ##                zField         = 'MapValue'
# ##                cellSize       = cell_size
# ##                splineType     = "REGULARIZED"
# ##                weight         = 0.1  # Default
# ##                #numberOfPoints = 12 # Default
# ##                numberOfPoints = 4
# ##                # Execute Spline
# ##                outSpline = arcpy.sa.Spline(inPntFeat, zField, cell_size, splineType, weight)
# ##                # Save the output
# ##                outSpline.save(output_raster_path)
# ##                del inPntFeat, zField, cell_size, splineType, weight, numberOfPoints, outSpline

            else:
                pass

            # Clear selection
            arcpy.management.SelectLayerByAttribute( point_locations_path_layer, "CLEAR_SELECTION" )

            from arcpy import metadata as md
            tif_md = md.Metadata(output_raster_path)
            tif_md.title = image_name.replace("_", " ")
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

        del point_locations
        # Delete point_locations_path_layer
        arcpy.management.Delete(point_locations_path_layer)
        del point_locations_path_layer

        # Gather results to be returned
        results = [region_gdb]

        # End of business logic for the worker function
        arcpy.AddMessage(f"Processing for: {table_name} complete")

        # Clean up
        del output_rasters
        del region_raster_mask

        # Variables for this function only
        del region, season, distri_code, summary_product
        del datasetcode, cell_size
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
        from create_rasters_worker import worker

        # Set basic arcpy.env variables
        arcpy.env.overwriteOutput             = True
        arcpy.env.parallelProcessingFactor = "100%"

        # Set varaibales
        base_project_folder = os.path.dirname(os.path.dirname(__file__))
        project_gdb         = rf"{base_project_folder}\{project}\{project}.gdb"
        project_folder      = rf"{base_project_folder}\{project}"
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
        #table_name = "WC_GFDL"

        region_gdb        = rf"{scratch_folder}\{table_name}.gdb"
        scratch_workspace = rf"{scratch_folder}\{table_name}\scratch.gdb"

        # Create worker scratch workspace, if missing
        if not arcpy.Exists(scratch_workspace):
            os.makedirs(rf"{scratch_folder}\{table_name}")
            if not arcpy.Exists(scratch_workspace):
                arcpy.management.CreateFileGDB(rf"{scratch_folder}\{table_name}", f"scratch")
        del scratch_workspace

        if "IDW" in table_name:
            point_locations = rf"{table_name}_Sample_Locations"
        elif "IDW" not in table_name:
            point_locations = rf"{table_name}_GRID_Points"
        else:
            pass

        # Setup worker workspace and copy data
        datasets = [rf"{project_gdb}\Datasets", rf"{project_gdb}\{table_name}_LayerSpeciesYearImageName", rf"{project_gdb}\{point_locations}"]
        if not any(arcpy.management.GetCount(d)[0] == 0 for d in datasets):

            arcpy.management.CreateFileGDB(rf"{scratch_folder}", f"{table_name}")
            arcpy.AddMessage("\tCreate File GDB: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

            arcpy.management.Copy(rf"{project_gdb}\Datasets", rf"{region_gdb}\Datasets")
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

            arcpy.management.Copy(rf"{project_gdb}\{table_name}_LayerSpeciesYearImageName", rf"{region_gdb}\{table_name}_LayerSpeciesYearImageName")
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

            arcpy.management.Copy(rf"{project_gdb}\{point_locations}", rf"{region_gdb}\{point_locations}")
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

            arcpy.management.Copy(rf"{project_gdb}\{table_name}_Raster_Mask", rf"{region_gdb}\{table_name}_Raster_Mask")
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

        else:
            arcpy.AddWarning(f"One or more datasets contains zero records!!")
            for d in datasets:
                arcpy.AddMessage(f"\t{os.path.basename(d)} has {arcpy.management.GetCount(d)[0]} records")
                del d
                se = f"SystemExit at line number: '{traceback.extract_stack()[-1].lineno}'"
            raise SystemExit(se)

        if "datasets" in locals().keys(): del datasets

        del point_locations
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

        deletes = [region_gdb, region_gdb.replace('.gdb','')]

        for delete in deletes:
            try:
                Delete = True
                if Delete and arcpy.Exists(delete):
                    arcpy.AddMessage(f"Delete: {delete}")
                    arcpy.management.Delete(delete)
                    arcpy.AddMessage("\tDelete: {0} {1}\n".format(os.path.basename(delete), arcpy.GetMessages(0).replace("\n", '\n\t')))
                del Delete
            except:
                if "Delete" in locals().keys(): del Delete
                if "delete" in locals().keys(): del delete
                arcpy.AddError(arcpy.GetMessages(2))
            if "delete" in locals().keys(): del delete
        del deletes

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
        import create_rasters_worker
        importlib.reload(create_rasters_worker)

        print(f"{'-' * 90}")
        print(f"Python Script:  {os.path.basename(__file__)}")
        print(f"Location:       {os.path.dirname(__file__)}")
        print(f"Python Version: {sys.version} Environment: {os.path.basename(sys.exec_prefix)}")
        print(f"{'-' * 90}\n")

        #project = "May 1 2024"
        project = "july 1 2024"

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
