# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      john.f.kennedy
#
# Created:     03/03/2024
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

        # Import the dismap_tools module to access tools
        import dismap_tools
        # Imports
        from arcpy import metadata as md

        # Set History and Metadata logs, set serverity and message level
        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        # Set basic workkpace variables
        table_name        = os.path.basename(region_gdb).replace(".gdb","")
        scratch_folder    = os.path.dirname(region_gdb)
        project_folder    = os.path.dirname(scratch_folder)
        csv_data_folder   = rf"{project_folder}\CSV_Data"
        scratch_workspace = rf"{scratch_folder}\{table_name}\scratch.gdb"

        arcpy.AddMessage(f"Table Name: {table_name}\nProject Folder: {os.path.basename(project_folder)}\nScratch Folder: {os.path.basename(scratch_folder)}\n")

        del scratch_folder

        # Set basic workkpace variables
        arcpy.env.workspace                = region_gdb
        arcpy.env.scratchWorkspace         = scratch_workspace
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        del scratch_workspace

        # DatasetCode CSVFile TransformUnit TableName  GeographicArea  CellSize
        # PointFeatureType    FeatureClassName    Region    Season    DateCode
        # Status    DistributionProjectCode    DistributionProjectName
        # SummaryProduct    FilterRegion    FilterSubRegion    FeatureServiceName
        # FeatureServiceTitle    MosaicName    MosaicTitle    ImageServiceName, ImageServiceTitle

        fields = ["TableName", "GeographicArea", "DatasetCode", "Region", "Season", "DistributionProjectCode"]
        region_list = [row for row in arcpy.da.SearchCursor(rf"{region_gdb}\Datasets", fields, where_clause = f"TableName = '{table_name}'")][0]
        del fields

        # Assigning variables from items in the chosen table list
        # ['AI_IDW', 'AI_IDW_Region', 'AI', 'Aleutian Islands', None, 'IDW']
        table_name      = region_list[0]
        geographic_area = region_list[1]
        datasetcode     = region_list[2]
        region          = region_list[3]
        season          = region_list[4] if region_list[4] else ""
        distri_code     = region_list[5]

        del region_list

        arcpy.AddMessage(f"\tTable Name:      {table_name}")
        arcpy.AddMessage(f"\tGeographic Area: {geographic_area}")
        arcpy.AddMessage(f"\tDataset Code:    {datasetcode}")
        arcpy.AddMessage(f"\tRegion:          {region}")
        arcpy.AddMessage(f"\tSeason:          {season}")
        arcpy.AddMessage(f"\tDistri Code:     {distri_code}")

        geographicarea_sr = os.path.join(project_folder, f"Dataset_Shapefiles\\{table_name}\\{geographic_area}.prj")
        arcpy.AddMessage(geographicarea_sr)
        datasetcode_sr = arcpy.SpatialReference(geographicarea_sr)
        del geographicarea_sr

        if datasetcode_sr.linearUnitName == "Kilometer":
            arcpy.env.cellSize = 1
            arcpy.env.XYResolution = 0.1
            arcpy.env.XYTolerance  = 1.0
        elif datasetcode_sr.linearUnitName == "Meter":
            arcpy.env.cellSize = 1000
            arcpy.env.XYResolution = 0.0001
            arcpy.env.XYTolerance  = 0.001

        arcpy.AddMessage(f"\t\tCreating Feature Class: {geographic_area}")
        # Execute Create Feature Class
        # Use DisMAP regions as a template
        geographic_area_path = arcpy.management.CreateFeatureclass(
                                                                   out_path          = region_gdb,
                                                                   out_name          = f"{geographic_area}",
                                                                   geometry_type     = "POLYGON",
                                                                   template          = rf"{region_gdb}\DisMAP_Regions",
                                                                   has_m             = "DISABLED",
                                                                   has_z             = "DISABLED",
                                                                   spatial_reference = datasetcode_sr,
                                                                   config_keyword    = "",
                                                                   spatial_grid_1    = "0",
                                                                   spatial_grid_2    = "0",
                                                                   spatial_grid_3    = "0"
                                                                  )
        arcpy.AddMessage("\t\t\t{0}\n".format(arcpy.GetMessages().replace("\n", '\n\t\t\t')))
        del datasetcode_sr
        del geographic_area_path

        geographic_area_path = rf"{region_gdb}\{geographic_area}"

        # The shapefile used to create the extent and mask for the environment variable
        geographic_area_shape_file    = rf"{project_folder}\Dataset_Shapefiles\{table_name}\{geographic_area}.shp"
        geographic_area_boundary      = f"{geographic_area.replace('_Region','_Boundary')}"
        geographic_area_boundary_path = rf"{region_gdb}\{geographic_area.replace('_Region','_Boundary')}"

        dismap_regions_md = md.Metadata(rf"{region_gdb}\DisMAP_Regions")
        dataset_md = md.Metadata(geographic_area_path)
        dataset_md.copy(dismap_regions_md)
        dataset_md.save()
        dataset_md.synchronize("OVERWRITE")
        dataset_md.save()
        dataset_md.synchronize("ALWAYS")
        dataset_md.save()
        del dataset_md, dismap_regions_md

        arcpy.AddMessage(f'\t\tCopy {geographic_area} Shape File.')

        arcpy.AddMessage(f"\t\tAppend: {geographic_area}")
        arcpy.management.Append(inputs = geographic_area_shape_file, target = geographic_area_path, schema_type = "NO_TEST")
        arcpy.AddMessage("\t\t\t{0}\n".format(arcpy.GetMessages().replace("\n", '\n\t\t\t')))

        arcpy.AddMessage(f"\t\tCalculate Fields for: {geographic_area}")
        arcpy.management.CalculateFields(geographic_area_path, "PYTHON3",
                                         [
                                          ["DatasetCode",             f'"{datasetcode}"'],
                                          ["Region",                  f'"{region}"'],
                                          ["Season",                  f'"{season}"'],
                                          ["DistributionProjectCode", f'"{distri_code}"'],
                                         ],
                                        )
        arcpy.AddMessage("\t\t\tCalculate Fields: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t\t\t')))

        arcpy.AddMessage(f"\t\tFeature to Line to create: {geographic_area_boundary}")
        arcpy.management.FeatureToLine(in_features = geographic_area_path, out_feature_class = geographic_area_boundary_path, cluster_tolerance="", attributes="ATTRIBUTES")
        arcpy.AddMessage("\t\t\t{0}\n".format(arcpy.GetMessages().replace("\n", '\n\t\t\t')))

        arcpy.AddMessage(f"\t\tDeleting fields from table: {geographic_area_boundary}")
        arcpy.management.DeleteField(in_table = rf"{region_gdb}\{geographic_area_boundary}", drop_field = [f"FID_{geographic_area}"])
        arcpy.AddMessage("\t\t\t{0}\n".format(arcpy.GetMessages().replace("\n", '\n\t\t\t')))


        arcpy.AddMessage(f"\t\tAlter Fields for: '{os.path.basename(geographic_area_path)}'")
        dismap_tools.alter_fields(csv_data_folder, geographic_area_path)

        dataset_md = md.Metadata(geographic_area_path)
        dataset_md.synchronize("ALWAYS")
        dataset_md.save()
        del dataset_md

        arcpy.AddMessage(f"\t\tAlter Fields for: '{os.path.basename(geographic_area_boundary_path)}'")
        dismap_tools.alter_fields(csv_data_folder, geographic_area_boundary_path)

        geographic_area_path_md = md.Metadata(geographic_area_path)
        dataset_md = md.Metadata(geographic_area_boundary_path)
        dataset_md.copy(geographic_area_path_md)
        dataset_md.save()
        dataset_md.synchronize("OVERWRITE")
        dataset_md.save()
        dataset_md.synchronize("ALWAYS")
        dataset_md.save()
        del dataset_md, geographic_area_path_md

        del geographic_area, geographic_area_boundary

        del geographic_area_path, geographic_area_shape_file
        del geographic_area_boundary_path

        # Remove template
        arcpy.management.Delete(rf"{region_gdb}\DisMAP_Regions")
        arcpy.AddMessage("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))

        arcpy.management.Delete(rf"{region_gdb}\Datasets")
        arcpy.AddMessage("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))

        arcpy.management.Compact(region_gdb)

        # Declared Variables for this function only
        del datasetcode, region, season, distri_code
        # Basic variables
        del table_name, project_folder, csv_data_folder
        # Imports
        del md, dismap_tools
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
        # Imports
        import dismap_tools
        from arcpy import metadata as md
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
        scratch_folder = os.path.join(project_folder, "Scratch")
        del project_folder

        # Clear Scratch Folder
        dismap_tools.clear_folder(folder=scratch_folder)

        # Create project scratch workspace, if missing
        if not arcpy.Exists(os.path.join(scratch_folder, "scratch.gdb")):
            if not arcpy.Exists(scratch_folder):
                os.makedirs(scratch_folder)
            if not arcpy.Exists(os.path.join(scratch_folder, "scratch.gdb")):
                arcpy.management.CreateFileGDB(scratch_folder, "scratch")
        else:
            pass

        # Set worker parameters
        table_name = "AI_IDW"
        #table_name = "HI_IDW"
        #table_name = "GMEX_IDW"
        #table_name = "GOA_IDW"
        #table_name = "NBS_IDW"
        #table_name = "SEUS_SPR_IDW"

        region_gdb        = os.path.join(scratch_folder, f"{table_name}.gdb")
        scratch_workspace = os.path.join(scratch_folder, f"{table_name}\\scratch.gdb")

        # Create worker scratch workspace, if missing
        if not arcpy.Exists(scratch_workspace):
            os.makedirs(os.path.join(scratch_folder, table_name))
            if not arcpy.Exists(scratch_workspace):
                arcpy.management.CreateFileGDB(os.path.join(scratch_folder, table_name), "scratch")
        del scratch_workspace

##        edit = arcpy.da.Editor(region_gdb)
##        arcpy.AddMessage("edit created")
##        edit.startEditing()
##        arcpy.AddMessage("edit started")
##        edit.startOperation()
##        arcpy.AddMessage("operation started")

        # Setup worker workspace and copy data
        #datasets = [ros.path.join(project_gdb, "Datasets") os.path.join(project_gdb, "DisMAP_Regions")]
        #if not any(arcpy.management.GetCount(d)[0] == 0 for d in datasets):
        if not arcpy.Exists(os.path.join(scratch_folder, f"{table_name}.gdb")):
            arcpy.management.CreateFileGDB(scratch_folder, table_name)
            arcpy.AddMessage("\tCreate File GDB: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
        else:
            pass

        arcpy.management.Copy(os.path.join(project_gdb, "Datasets"), rf"{region_gdb}\Datasets")
        arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

        arcpy.management.CreateFeatureclass(rf"{region_gdb}", "DisMAP_Regions", "POLYLINE", os.path.join(project_gdb, "DisMAP_Regions"))
        arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

        dismap_regions_md = md.Metadata(os.path.join(project_gdb, "DisMAP_Regions"))
        dataset_md = md.Metadata(rf"{region_gdb}\DisMAP_Regions")
        dataset_md.copy(dismap_regions_md)
        dataset_md.save()
        dataset_md.synchronize("OVERWRITE")
        dataset_md.save()
        dataset_md.synchronize("ALWAYS")
        dataset_md.save()
        del dataset_md, dismap_regions_md

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
        del md, dismap_tools

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
            project_gdb = os.path.join(os.path.expanduser('~'), "Documents\\ArcGIS\\Projects\\DisMAP\\ArcGIS-Analysis-Python\\February 1 2026\\February 1 2026.gdb")))
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