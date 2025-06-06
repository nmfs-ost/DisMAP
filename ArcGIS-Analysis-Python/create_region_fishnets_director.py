# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        create_region_fishnets_director.py
# Purpose:
#
# Author:      john.f.kennedy
#
# Created:     25/02/2024
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

# error callback function
def custom_error_callback(error):
    traceback.print_exception(type(error), error, error.__traceback__)

def director(project_gdb="", Sequential=True, table_names=[]):
    try:
        # Test if passed workspace exists, if not raise SystemExit
        if not arcpy.Exists(project_gdb):
            raise SystemExit(line_info(f"{os.path.basename(project_gdb)} is missing!!"))

        # Import the dismap module to access tools
        import dismap
        importlib.reload(dismap)

        # Imports
        import create_region_fishnets_worker
        importlib.reload(create_region_fishnets_worker)
        from create_region_fishnets_worker import worker
        del create_region_fishnets_worker

        # Set History and Metadata logs, set serverity and message level
        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(1) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        # Set basic workkpace variables
        project_folder    = os.path.dirname(project_gdb)
        scratch_folder    = rf"{project_folder}\Scratch"
        scratch_workspace = rf"{project_folder}\Scratch\scratch.gdb"
        csv_data_folder   = rf"{project_folder}\CSV Data"

        # Create Scratch Workspace for Project
        if not arcpy.Exists(rf"{scratch_folder}\scratch.gdb"):
            if not arcpy.Exists(scratch_folder):
                os.makedirs(rf"{scratch_folder}")
            if not arcpy.Exists(rf"{scratch_folder}\scratch.gdb"):
                arcpy.management.CreateFileGDB(rf"{scratch_folder}", f"scratch")

        # Set basic workkpace variables
        arcpy.env.workspace                = project_gdb
        arcpy.env.scratchWorkspace         = scratch_workspace
        arcpy.env.overwriteOutput             = True
        arcpy.env.parallelProcessingFactor = "100%"

        del project_folder

        if not table_names:
            table_names = [row[0] for row in arcpy.da.SearchCursor("Datasets", "TableName", where_clause = f"GeographicArea IS NOT NULL")]

        # Pre Processing
        for table_name in table_names:
            arcpy.AddMessage(f"Pre-Processing: {table_name}")

            region_gdb               = rf"{scratch_folder}\{table_name}.gdb"
            region_scratch_workspace = rf"{scratch_folder}\{table_name}\scratch.gdb"

            # Create Scratch Workspace for Region
            if not arcpy.Exists(region_scratch_workspace):
                os.makedirs(rf"{scratch_folder}\{table_name}")
                if not arcpy.Exists(region_scratch_workspace):
                    arcpy.management.CreateFileGDB(rf"{scratch_folder}\{table_name}", f"scratch")
            del region_scratch_workspace

            datasets = [rf"{project_gdb}\Datasets", rf"{project_gdb}\{table_name}_Region"]
            if not any(arcpy.management.GetCount(d)[0] == 0 for d in datasets):
                arcpy.management.CreateFileGDB(rf"{scratch_folder}", f"{table_name}")
                arcpy.AddMessage("\tCreate File GDB: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

                arcpy.management.Copy(rf"{project_gdb}\Datasets", rf"{region_gdb}\Datasets")
                arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

                arcpy.management.Copy(rf"{project_gdb}\{table_name}_Region", rf"{region_gdb}\{table_name}_Region")
                arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

            else:
                arcpy.AddWarning(f"One or more datasets contains zero records!!")
                for d in datasets:
                    arcpy.AddMessage(f"\t{os.path.basename(d)} has {arcpy.management.GetCount(d)[0]} records")
                    del d
                se = f"SystemExit at line number: '{traceback.extract_stack()[-1].lineno}'"
                raise SystemExit(se)

            if "datasets" in locals().keys(): del datasets

            del region_gdb, table_name

        del scratch_workspace

        results = []

        # Sequential Processing
        if Sequential:
            arcpy.AddMessage(f"Sequential Processing")
            jobs={}
            for i in range(0, len(table_names)):
                arcpy.AddMessage(f"Processing: {table_names[i]}")

                table_name = table_names[i]
                region_gdb = rf"{scratch_folder}\{table_name}.gdb"

                worker_results = ""

                try:
                    worker_results = worker(region_gdb=region_gdb)
                except SystemExit as se:
                    raise SystemExit(str(se))

                if type(worker_results).__name__ == "str" and len(worker_results) != 0:
                    results.append(worker_results)
                elif type(worker_results).__name__ == "str" and len(worker_results) == 0:
                    raise SystemExit(f"worker_results is str, but empty!!")
                elif type(worker_results).__name__ == "list" and len(worker_results) != 0:
                    if type(worker_results[0]).__name__ == "list":
                        worker_results = [r for rt in worker_results for r in rt]
                    for result in worker_results:
                        results.append(result)
                        del result
                elif type(worker_results).__name__ == "list" and len(worker_results) == 0:
                    raise SystemExit(f"worker_results is list, but empty!!")

                del worker_results, region_gdb, table_name

                del i
            del jobs

        # Non-Sequential Processing
        # https://superfastpython.com/multiprocessing-pool-map_async/
        if not Sequential:
            arcpy.AddMessage(f"Non-Sequential Processing")

            import multiprocessing
            from time import localtime, strftime, sleep

            arcpy.env.autoCancelling = True

            sys.path.append(os.path.dirname(__file__))
            sys.path.append(sys.exec_prefix)

            arcpy.AddMessage(f"Start multiprocessing using the ArcGIS Pro pythonw.exe.")
            #Set multiprocessing exe in case we're running as an embedded process, i.e ArcGIS
            #get_install_path() uses a registry query to figure out 64bit python exe if available
            multiprocessing.set_executable(os.path.join(sys.exec_prefix, 'pythonw.exe'))

            # Get CPU count and then take 2 away for other process
            _processes = multiprocessing.cpu_count() - 2
            _processes = _processes if len(table_names) >= _processes else len(table_names)
            arcpy.AddMessage(f"Creating the multiprocessing Pool with {_processes} processes")
            #Create a pool of workers, keep one cpu free for surfing the net.
            #Let each worker process only handle 1 task before being restarted (in case of nasty memory leaks)
            #with multiprocessing.Pool(processes=multiprocessing.cpu_count() - 1) as pool:
            #with multiprocessing.Pool(processes=multiprocessing.cpu_count() - 1, maxtasksperchild=10) as pool:
            with multiprocessing.Pool(processes=_processes, maxtasksperchild=10) as pool:

                arcpy.AddMessage(f"\tPrepare arguments for processing")

                # Use apply_async so we can handle exceptions gracefully
                jobs={}
                for i in range(0, len(table_names)):
                    try:
                        arcpy.AddMessage(f"Processing: {table_names[i]}")

                        table_name = table_names[i]
                        region_gdb = rf"{scratch_folder}\{table_name}.gdb"

                        jobs[table_name] = pool.starmap_async(worker, [[region_gdb]], chunksize=10, error_callback=custom_error_callback)

                        del table_name, region_gdb

                    except SystemExit as se:
                        pool.terminate()
                        raise SystemExit(str(se))

                    del i

                all_finished = False
                while True:
                    all_finished = True

                    arcpy.AddMessage(f"\nHave the workers finished?\nIt's {strftime('%a %b %d %I:%M %p', localtime())}")

                    for table_name, result in jobs.items():
                        if result.ready():
                            arcpy.AddMessage(f"Process {table_name} has finished")
                        else:
                            all_finished = False
                            arcpy.AddMessage(f"Process {table_name} is running. . .")
                        del table_name, result

                    if all_finished:
                        break

                    sleep(_processes * 7.5)

                del all_finished
                del _processes

                arcpy.AddMessage(f"Get the return values")

                for table_name, job_result in jobs.items():

                    worker_results = ""

                    try:
                        worker_results = job_result.get()
                    except SystemExit as se:
                        pool.terminate()
                        raise SystemExit(str(se))

                    if type(worker_results).__name__ == "str" and len(worker_results) != 0:
                        results.append(worker_results)
                    elif type(worker_results).__name__ == "str" and len(worker_results) == 0:
                        raise SystemExit(f"worker_results is str, but empty!!")
                    elif type(worker_results).__name__ == "list" and len(worker_results) != 0:
                        if type(worker_results[0]).__name__ == "list":
                            worker_results = [r for rt in worker_results for r in rt]
                        for result in worker_results:
                            results.append(result)
                            del result
                    elif type(worker_results).__name__ == "list" and len(worker_results) == 0:
                        raise SystemExit(f"worker_results is list, but empty!!")

                    del table_name, job_result, worker_results

                arcpy.AddMessage(f"\tClose the process pool")
                # close the process pool
                pool.close()
                # wait for all tasks to complete and processes to close
                arcpy.AddMessage(f"\tWait for all tasks to complete and processes to close")
                pool.join()
                # Just in case
                pool.terminate()

                del pool
                del jobs

            del multiprocessing, localtime, strftime, sleep

            arcpy.AddMessage(f"\tDone with multiprocessing Pool")

        # Post-Processing
        arcpy.AddMessage("Post-Processing")
        if results:
            arcpy.AddMessage("Processing Results")

            for result in results:

                dataset = os.path.basename(result)
                region_gdb  = os.path.dirname(result)

                arcpy.AddMessage(f"\tResult: '{dataset}'")
                arcpy.AddMessage(f"\t\tPath:       '{result}'")
                arcpy.AddMessage(f"\t\tRegion GDB: '{region_gdb}'")

                arcpy.AddMessage(f"\tProcessing Result: '{dataset}'")

                if arcpy.Exists(rf"{project_gdb}\{dataset}"):
                    arcpy.management.Delete(rf"{project_gdb}\{dataset}")

                arcpy.management.Copy(result, rf"{project_gdb}\{dataset}")
                arcpy.AddMessage("\tCopy: {0} {1}\n".format(f"{dataset}", arcpy.GetMessages(0).replace("\n", '\n\t')))

                desc = arcpy.da.Describe(result)
                if desc["dataType"] in ["FeatureClass", "Table", "MosaicDataset"]:
                    dismap.alter_fields(csv_data_folder, rf"{project_gdb}\{dataset}")
                del desc

                dismap.import_metadata(rf"{project_gdb}\{dataset}")

                del region_gdb, dataset

                del result

            deletes = []
            for result in results:
                data_type = arcpy.Describe(result).dataType
                arcpy.AddMessage(f"\tResult: {result} Data Type: {data_type}")
                if data_type == "Workspace":
                    deletes.append(result)
                    deletes.append(result.replace(".gdb",""))
                elif data_type in ["FeatureClass", "Table"]:
                    deletes.append(os.path.dirname(result))
                    deletes.append(os.path.dirname(result).replace(".gdb",""))
                else:
                    pass
                del result, data_type

            deletes = list(set(deletes))

            if project_gdb in deletes: deletes.remove(project_gdb)

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

            # Replace region_gdb workspace for project_gdb
            results = list(map(lambda region_gdb: region_gdb.replace(os.path.dirname(region_gdb), project_gdb), results))

        else:
            arcpy.AddMessage(f"No results in '{inspect.stack()[0][3]}'")

        arcpy.AddMessage(f"Compacting the {os.path.basename(project_gdb)} GDB")
        arcpy.management.Compact(project_gdb)
        arcpy.AddMessage("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))

        # Variables assigned in function
        del scratch_folder, csv_data_folder
        # Imports
        del dismap, worker
        # Function Parameters
        del project_gdb, Sequential, table_names

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

def main(project="", test=False):
    try:
        # Imports
        from create_region_fishnets_director import director

        # Set basic arcpy.env variables
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        base_project_folder = os.path.dirname(os.path.dirname(__file__))
        project_gdb = rf"{base_project_folder}\{project}\{project}.gdb"
        del base_project_folder

        # Test if passed workspace exists, if not raise SystemExit
        if not arcpy.Exists(project_gdb):
            raise SystemExit(line_info(f"{os.path.basename(project_gdb)} is missing!!"))

        Backup = False
        if Backup:
            arcpy.AddMessage("Making a backup")
            arcpy.management.Copy(project_gdb, project_gdb.replace(".gdb", f"_Backup.gdb"))
            arcpy.AddMessage("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))

            arcpy.AddMessage("Compacting the backup")
            arcpy.management.Compact(project_gdb.replace(".gdb", f"_Backup.gdb"))
            arcpy.AddMessage("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))
        del Backup

        results = []

        try:
            pass
            # "AI_IDW", "EBS_IDW", "ENBS_IDW", "GMEX_IDW", "GOA_IDW", "HI_IDW", "NBS_IDW", "NEUS_FAL_IDW", "NEUS_SPR_IDW",
            # "SEUS_FAL_IDW", "SEUS_SPR_IDW", "SEUS_SUM_IDW", "WC_GLMME", "WC_GFDL", "WC_ANN_IDW", "WC_TRI_IDW",

            if test:
                result = director(project_gdb=project_gdb, Sequential=True, table_names=["GMEX_IDW"])
                results.extend(result); del result
            else:
                result = director(project_gdb=project_gdb, Sequential=False, table_names=["NBS_IDW", "ENBS_IDW", "HI_IDW", "SEUS_FAL_IDW", "SEUS_SPR_IDW", "SEUS_SUM_IDW",])
                results.extend(result); del result

                result = director(project_gdb=project_gdb, Sequential=False, table_names=["WC_TRI_IDW", "GMEX_IDW", "AI_IDW", "GOA_IDW", "WC_ANN_IDW", "NEUS_FAL_IDW",])
                results.extend(result); del result

                result = director(project_gdb=project_gdb, Sequential=False, table_names=["NEUS_SPR_IDW", "EBS_IDW", "WC_GLMME"])
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

        del project_gdb
        del director
        del project, test

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
        import create_region_fishnets_director
        importlib.reload(create_region_fishnets_director)

        print(f"{'-' * 90}")
        print(f"Python Script:  {os.path.basename(__file__)}")
        print(f"Location:       {os.path.dirname(__file__)}")
        print(f"Python Version: {sys.version} Environment: {os.path.basename(sys.exec_prefix)}")
        print(f"{'-' * 90}\n")

        project = arcpy.GetParameterAsText(0)

        if not project:
            #project = "April 1 2023"
            #project = "May 1 2024"
            project = "July 1 2024"

        # Tested on 7/24/2024 -- PASSED
        main(project=project, test=True)

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
