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

def worker(dismap_gdb="", data_type="", table_name="", dataset_filter=""):
    try:
        if not arcpy.Exists(dismap_gdb):
            raise SystemExit(se)

        import dismap
        importlib.reload(dismap)

        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        project_folder     = os.path.dirname(dismap_gdb)
        scratch_workspace  = rf"{project_folder}\Scratch\scratch.gdb"

        arcpy.env.workspace                 = dismap_gdb
        arcpy.env.scratchWorkspace          = scratch_workspace
        arcpy.env.overwriteOutput              = True
        arcpy.env.parallelProcessingFactor  = "100%"

        arcpy.AddMessage(f"Gathering Data Types, please wait")

        walk = arcpy.da.Walk(dismap_gdb, datatype=data_type)
        for dirpath, dirnames, filenames in walk:
            for filename in filenames:
                if table_name == filename[:len(table_name)]:
                    if dataset_filter:
                        if filename.endswith(dataset_filter):
                            dataset = os.path.join(dirpath, filename)
                            arcpy.AddMessage(f"\tDataset: {filename}")
                            dismap.check_datasets([dataset])
                            del dataset
                        else:
                            pass
                    else:
                        dataset = os.path.join(dirpath, filename)
                        arcpy.AddMessage(f"\tDataset: {filename}")
                        dismap.check_datasets([dataset])
                        del dataset
                del filename
            del filenames
            del dirpath, dirnames
        del walk

        del dismap, project_folder, scratch_workspace
        del dismap_gdb, data_type, table_name, dataset_filter

    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteError:
        raise SystemExit(arcpy.GetMessages())
    except arcpy.ExecuteWarning:
        raise SystemExit(arcpy.GetMessages())
    except SystemExit as se:
        raise SystemExit(str(se))
    except:
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        raise SystemExit(pymsg)
    else:
        try:
            import inspect
            leave_out_keys = ["leave_out_keys", "remaining_keys", "inspect",]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys

            return True

        except:
            traceback.print_exc()
    finally:
        try:
            pass
        except:
            traceback.print_exc()

def main():
    try:

        from check_datasets import worker

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        dismap_gdb = rf"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP\April 1 2023\April 1 2023.gdb"
        project_folder = os.path.dirname(dismap_gdb)
        csv_data_folder = rf"{project_folder}\CSV Data"

        dismap_gdb_dataset_dictionary = {}

        try:
            import json
            with open(rf"{csv_data_folder}\dismap_gdb_dataset_dictionary.json", 'r') as json_file:
                dismap_gdb_dataset_dictionary = json.load(json_file)
            del json_file, json
        except:
            pass

            arcpy.AddMessage(f"Gathering Filenames and Data Types, please wait")

            table_names = [row[0] for row in arcpy.da.SearchCursor(rf"{dismap_gdb}\Datasets", "TableName", where_clause = f"TableName IS NOT NULL")]

            datasets = {}
            walk = arcpy.da.Walk(dismap_gdb)
            for dirpath, dirnames, filenames in walk:
                for filename in filenames:
                    dataset = os.path.join(dirpath, filename)
                    desc = arcpy.Describe(dataset)
                    arcpy.AddMessage(f"Dataset: {filename:<30} {desc.dataType}")
                    if filename not in datasets:

                        table_name = ""

                        if filename in table_names:
                            table_name = filename

                        elif [tn for tn in table_names if filename.startswith(tn) and filename != tn]:
                            table_name = [tn for tn in table_names if filename.startswith(tn) and filename != tn][0]
                        else:
                            table_name = filename

                        datasets[filename] = [desc.dataType, table_name]

                        del table_name

                    del desc, dataset, filename
                del filenames
                del dirpath, dirnames
            del walk

            #for dataset in sorted(datasets):
            #    data_type = datasets[dataset][0]
            #    table_name = datasets[dataset][1]
            #    arcpy.AddMessage(f"Dataset: {dataset:<30} Type: {data_type} Name: {table_name}")
            #    del data_type, table_name, dataset

            # Write to File
            import json
            with open(rf"{csv_data_folder}\dismap_gdb_dataset_dictionary.json", 'w') as json_file:
                json.dump(datasets, json_file, indent=4)
            del json_file, json

            del table_names
            del datasets

        del project_folder, csv_data_folder

        #table_names = [row[0] for row in arcpy.da.SearchCursor(rf"{dismap_gdb}\Datasets", "TableName", where_clause = f"TableName IS NOT NULL")]
        #print(table_names)
        # ['AI_IDW', 'EBS_IDW', 'ENBS_IDW', 'GMEX_IDW', 'GOA_IDW', 'HI_IDW',
        #  'NBS_IDW', 'NEUS_FAL_IDW', 'NEUS_SPR_IDW', 'SEUS_FAL_IDW',
        #  'SEUS_SPR_IDW', 'SEUS_SUM_IDW', 'WC_GLMME', 'WC_GFDL', 'WC_ANN_IDW',
        #  'WC_TRI_IDW', 'Datasets', 'LayerSpeciesYearImageName', 'Indicators',
        #  'Species_Filter']

        #data_type  = "FeatureClass"
        #table_name = "NBS_IDW"
        #for dataset in dismap_gdb_dataset_dictionary:
        #    #data_type, table_name = dismap_gdb_dataset_dictionary[dataset]
        #    #print(f"{dataset:<30} {data_type:<13} {table_name}")
        #    #del table_name, data_type, dataset
        #    if table_name == dismap_gdb_dataset_dictionary[dataset][1]:
        #        if data_type == dismap_gdb_dataset_dictionary[dataset][0]:
        #            print(f"{dataset:<30} {data_type:<13} {table_name}")
        #    del dataset
        #del table_name, data_type

        results = ""

##            data_type  = "FeatureClass"
##            table_name = "SEUS_SPR_IDW"
##            results = worker(dismap_gdb=dismap_gdb, data_type=data_type, table_name=table_name)
##            del table_name, data_type
    # "AI_IDW", "EBS_IDW", "ENBS_IDW", "GMEX_IDW", "GOA_IDW", "HI_IDW", "NBS_IDW", "NEUS_FAL_IDW", "NEUS_SPR_IDW",
    # "SEUS_FAL_IDW", "SEUS_SPR_IDW", "SEUS_SUM_IDW", "WC_GLMME", "WC_GFDL", "WC_ANN_IDW", "WC_TRI_IDW",

        data_type      = "RasterDataset"
        dataset_filter = "Raster_Mask"
        #table_names = [row[0] for row in arcpy.da.SearchCursor(rf"{dismap_gdb}\Datasets", "TableName", where_clause = f"GeographicArea IS NOT NULL")]
        #table_names = ["AI_IDW", "HI_IDW", "WC_GFDL",]
        table_names = ["SEUS_FAL_IDW", "SEUS_SPR_IDW", "SEUS_SUM_IDW", "WC_GLMME", "WC_GFDL", "WC_ANN_IDW", "WC_TRI_IDW"]
        #ws = rf"{os.path.dirname(dismap_gdb)}\Images"
        #ws = fr"F:\DisMAP\ArcGIS Analysis - Python\April 1 2023\Images\AI_IDW"
        #ws = fr"F:\DisMAP\ArcGIS Analysis - Python\April 1 2023\DisMAP April 1 2023 Prod.gdb"
        for table_name in table_names:
            try:
                worker(dismap_gdb=dismap_gdb, data_type=data_type, table_name=table_name, dataset_filter="")
            except SystemExit as se:
                raise SystemExit(str(se))
            del table_name
        #del ws
        del table_names, data_type, dataset_filter

##        if results:
##            if type(results).__name__ == "bool":
##                arcpy.AddMessage(f"'Results' is a {type(results).__name__}" )
##                arcpy.AddMessage(f"Result: {results}")
##            elif type(results).__name__ == "str":
##                arcpy.AddMessage(f"'Results' is a {type(results).__name__}" )
##                arcpy.AddMessage(f"Result: {results}")
##            elif type(results).__name__ == "list":
##                if type(results[0]).__name__ == "list":
##                        results = [r for rt in results for r in rt]
##                arcpy.AddMessage(f"'Results' is a {type(results).__name__}" )
##                for result in results:
##                    arcpy.AddMessage(f"Result: {result}")
##                del result
##            else:
##                arcpy.AddMessage(f"No results returned!!!")
##        else:
##            arcpy.AddMessage(f"No results in '{inspect.stack()[0][3]}'")

        del dismap_gdb_dataset_dictionary
        del dismap_gdb
        del worker

    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(arcpy.GetMessages())
        raise SystemExit
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages())
        raise SystemExit
    except SystemExit as se:
        arcpy.AddError(str(se))
        raise SystemExit
    except:
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        raise SystemExit(pymsg)
    else:
        try:
            import inspect
            leave_out_keys = ["leave_out_keys", "remaining_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys

            return results

        except:
            traceback.print_exc()
    finally:
        try:
            del results
        except UnboundLocalError:
            pass

if __name__ == '__main__':
    try:
        import check_datasets
        importlib.reload(check_datasets)

        # Tested on 3/20/2024 -- development in progress
        results = main()
        if results:
            from time import localtime, strftime
            print(f"Python script: {os.path.basename(__file__)} successfully completed {strftime('%a %b %d %I:%M %p', localtime())}")
            del localtime, strftime
        del results

    except SystemExit:
        pass
    except:
        traceback.print_exc()
    else:
        import inspect
        leave_out_keys = ["leave_out_keys", "remaining_keys"]
        leave_out_keys.extend([name for name, obj in inspect.getmembers(sys.modules[__name__]) if inspect.isfunction(obj) or inspect.ismodule(obj)])
        remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
        if remaining_keys:
            arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[1][3]}': ##--> '{', '.join(remaining_keys)}' <--##")
        del leave_out_keys, remaining_keys
    finally:
        pass
