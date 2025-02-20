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
        scratch_workspace = rf"{scratch_folder}\{table_name}\scratch.gdb"

        arcpy.AddMessage(f"Table Name: {table_name}\nProject Folder: {project_folder}\nScratch Folder: {scratch_folder}\n")

        del scratch_folder

        # Set basic workkpace variables
        arcpy.env.workspace                = region_gdb
        arcpy.env.scratchWorkspace         = scratch_workspace
        arcpy.env.overwriteOutput             = True
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

        geographicarea_sr = os.path.join(f"{project_folder}", "Dataset Shapefiles", f"{table_name}", f"{geographic_area}.prj")
        datasetcode_sr = arcpy.SpatialReference(geographicarea_sr); del geographicarea_sr

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

        # The shapefile used to create the extent and mask for the environment variable
        geographic_area_shape_file    = rf"{project_folder}\Dataset Shapefiles\{table_name}\{geographic_area}.shp"
        geographic_area_boundary      = f"{geographic_area.replace('_Region','_Boundary')}"
        geographic_area_boundary_path = rf"{region_gdb}\{geographic_area.replace('_Region','_Boundary')}"

        # TODO: reverse this
        # arcpy.AddMessage(f'\t\tRepair Geometry for: {geographic_area} Shape File.')
        # geographic_area_shape_file = arcpy.management.RepairGeometry(in_features=geographic_area_shape_file, delete_null="DELETE_NULL", validation_method="ESRI")
        # arcpy.AddMessage("\t\t\t{0}\n".format(arcpy.GetMessages().replace("\n", '\n\t\t\t')))

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

        results = [rf"{region_gdb}\{geographic_area}", rf"{region_gdb}\{geographic_area_boundary}"]
        del geographic_area, geographic_area_boundary

        del geographic_area_path, geographic_area_shape_file
        del geographic_area_boundary_path

        # Variables for this function only
        del datasetcode, region, season, distri_code
        # Basic variables
        del table_name, project_folder
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
        from create_regions_from_shapefiles_worker import worker

        # Set basic arcpy.env variables
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        # Set varaibales
        project_gdb     = rf"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\{project}\{project}.gdb"
        project_folder = os.path.dirname(project_gdb)
        scratch_folder = rf"{project_folder}\Scratch"
        del project_folder

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
        #table_name = "HI_IDW"
        #table_name = "GMEX_IDW"
        #table_name = "GOA_IDW"
        #table_name = "NBS_IDW"
        table_name = "SEUS_FAL_IDW"

        region_gdb        = rf"{scratch_folder}\{table_name}.gdb"
        scratch_workspace = rf"{scratch_folder}\{table_name}\scratch.gdb"

        # Create worker scratch workspace, if missing
        if not arcpy.Exists(scratch_workspace):
            os.makedirs(rf"{scratch_folder}\{table_name}")
            if not arcpy.Exists(scratch_workspace):
                arcpy.management.CreateFileGDB(rf"{scratch_folder}\{table_name}", f"scratch")
        del scratch_workspace

        # Setup worker workspace and copy data
        datasets = [rf"{project_gdb}\Datasets", rf"{project_gdb}\DisMAP_Regions"]
        if not any(arcpy.management.GetCount(d)[0] == 0 for d in datasets):

            arcpy.management.CreateFileGDB(rf"{scratch_folder}", f"{table_name}")
            arcpy.AddMessage("\tCreate File GDB: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

            arcpy.management.Copy(rf"{project_gdb}\Datasets", rf"{region_gdb}\Datasets")
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

            arcpy.management.CreateFeatureclass(rf"{region_gdb}", "DisMAP_Regions", "POLYLINE", rf"{project_gdb}\DisMAP_Regions")
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

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
        import importlib, create_regions_from_shapefiles_worker
        importlib.reload(create_regions_from_shapefiles_worker)

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
        leave_out_keys = ["leave_out_keys", "remaining_keys"]
        leave_out_keys.extend([name for name, obj in inspect.getmembers(sys.modules[__name__]) if inspect.isfunction(obj) or inspect.ismodule(obj)])
        remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
        if remaining_keys:
            arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[1][3]}': ##--> '{', '.join(remaining_keys)}' <--##")
        del leave_out_keys, remaining_keys
    finally:
        pass
