# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        module1
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

### error callback function
##def custom_error_callback(error):
##    traceback.print_exception(type(error), error, error.__traceback__)

### error callback function
##def custom_error_callback(error):
##    import traceback, sys
##    #traceback.print_exception(type(error), error, error.__traceback__)
##    print("".join(traceback.format_exception(*sys.exc_info())), flush=True)
##    raise Exception("".join(traceback.format_exception(*sys.exc_info())))
##
### custom callback function
##def custom_callback(result):
##    #arcpy.AddMessage(f'\tResult: {result}')
##    print(f'\tResult: {result}', flush=True)

# custom callback function
def custom_callback(result):
    print(f'Callback got values: {result}', flush=True)

# custom error callback function
def custom_error_callback(error):
    print(f'Got an error: {error}', flush=True)

def director(project_gdb="", Sequential=True, table_names=[]):
    try:
        # Test if passed workspace exists, if not raise SystemExit
        if not arcpy.Exists(project_gdb):
            raise SystemExit(line_info(f"{os.path.basename(project_gdb)} is missing!!"))

        import dismap
        importlib.reload(dismap)
        import math

        import create_region_sample_locations_worker
        importlib.reload(create_region_sample_locations_worker)
        from create_region_sample_locations_worker import worker
        del create_region_sample_locations_worker
        from time import sleep, gmtime, localtime, strftime, time

        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(1) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

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

        arcpy.env.workspace                = project_gdb
        arcpy.env.scratchWorkspace         = scratch_workspace
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        del project_folder, scratch_workspace

        if not table_names:
            table_names = [row[0] for row in arcpy.da.SearchCursor(rf"{project_gdb}\Datasets", "TableName", where_clause = f"GeographicArea IS NOT NULL")]

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

            del region_gdb
            del table_name

        results = []

        # Sequential Processing
        if Sequential:
            arcpy.AddMessage(f"Sequential Processing")
            jobs={}
            for i in range(0, len(table_names)):
                try:
                    arcpy.AddMessage(f"Processing: {table_names[i]}")

                    table_name = table_names[i]
                    region_gdb = rf"{scratch_folder}\{table_name}.gdb"

                    worker_results = ""

                    worker_results = worker(region_gdb=region_gdb)

                    results.extend(worker_results)

                    del worker_results, region_gdb, table_name

                except SystemExit as se:
                    arcpy.AddError(str(se))
                    traceback.print_exc()
                except Exception as e:
                    arcpy.AddError(str(e))
                    traceback.print_exc()
                except:
                    traceback.print_exc()

                del i
            del jobs

        # Non-Sequential Processing
        # https://superfastpython.com/multiprocessing-pool-map_async/
        if not Sequential:
            arcpy.AddMessage(f"Non-Sequential Processing")

            import multiprocessing

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
            chunk_size = math.ceil((len(table_names) / _processes) / 2) * 2
            arcpy.AddMessage(f"Creating the multiprocessing Pool with {_processes} processes")
            #Create a pool of workers, keep one cpu free for surfing the net.
            #Let each worker process only handle 1 task before being restarted (in case of nasty memory leaks)
            with multiprocessing.Pool(processes=_processes, maxtasksperchild=1) as pool:

##                # issues tasks to process pool
##                gdbs = [[rf"{scratch_folder}\{table_name}.gdb" for table_name in table_names]]
##                #result = pool.starmap_async(worker, gdbs, chunksize=chunk_size, callback=custom_callback, error_callback=custom_error_callback)
##                result = pool.starmap_async(worker, gdbs, chunksize=chunk_size)
##                # get the return values
##                try:
##                    values = result.get()
##                except Exception as e:
##                    print(f'Failed with: {e}')
##                del result, gdbs
##                if "values" in locals().keys(): del values

                arcpy.AddMessage(f"\tPrepare arguments for processing")

                # Use apply_async so we can handle exceptions gracefully
                jobs={}
                for i in range(0, len(table_names)):
                    try:
                        arcpy.AddMessage(f"Processing: {table_names[i]}")

                        table_name = table_names[i]
                        region_gdb = rf"{scratch_folder}\{table_name}.gdb"

                        #jobs[table_name] = pool.starmap_async(worker, [[region_gdb]], chunksize=4, callback=custom_callback, error_callback=custom_error_callback)
                        #jobs[table_name] = pool.starmap_async(worker, [[region_gdb]], chunksize=10, error_callback=custom_error_callback)
                        #jobs[table_name] = pool.starmap_async(worker2, [[region_gdb]], chunksize=chunk_size, callback=custom_callback, error_callback=custom_error_callback)
                        jobs[table_name] = pool.apply_async(worker, [region_gdb])

                        del table_name, region_gdb

                    except:
                        pool.terminate()
                        traceback.print_exc()

                    del i

                all_finished = False
                # Set a start time so that we can see how log things take
                start_time = time()
                result_completed = {}
                while True:
                    all_finished = True

                    # Elapsed time
                    end_time = time()
                    elapse_time =  end_time - start_time

                    arcpy.AddMessage(f"\nHave the workers finished?")
                    finish_time = strftime('%a %b %d %I:%M %p', localtime())
                    arcpy.AddMessage(f"It's {finish_time}")
                    time_elapsed = u"Elapsed Time {0} (H:M:S)".format(strftime("%H:%M:%S", gmtime(elapse_time)))
                    arcpy.AddMessage(time_elapsed)

                    finish_time = f"{finish_time}. {time_elapsed}"
                    del time_elapsed

                    for table_name, result in jobs.items():
                        #arcpy.AddMessage(f"Ready: {result.get()}")
                        #try:
                        #    arcpy.AddMessage(f"Sucessful: {result.successful()}")
                        #except ValueError:
                        #    print(f"Process: {table_name} is not ready!!")
                        #try:
                        #    # wait for and get the result from the task
                        #    value = result.get()
                        #    # report the result
                        #    print(f'Got: {value}')
                        #except Exception as e:
                        #    print(f'Failed to get the result: {e}')
                        #    raise SystemExit
                        if result.ready():
                            #try:
                            #    # wait for and get the result from the task
                            #    value = result.get()
                            #    # report the result
                            #    print(f'Got: {value}')
                            #except Exception as e:
                            #    print(f'Failed to get the result: {e}')
                            # check if the tasks were successful
                            #if result.successful():
                            #    print('Successful')
                            #else:
                            #    print('Unsuccessful')
                            if table_name not in result_completed:
                                result_completed[table_name] = finish_time
                                try:
                                    # wait for and get the result from the task
                                    value = result.get()
                                    del value
                                    # report the result
                                    #print(f'Got: {value}')
                                    #arcpy.AddMessage(f"Ready: {result.get()}")
                                    #arcpy.AddMessage(f"Sucessful: {result.successful()}")
                                except Exception as e:
                                    print(f'Failed to get the result: {e}')
                                    pool.terminate()
                            arcpy.AddMessage(f"Process {table_name} was finished on {result_completed[table_name]}")
                        else:
                            #print(result.get())
                            all_finished = False
                            arcpy.AddMessage(f"Process {table_name} is running. . .")
                        del table_name, result

                    del elapse_time, end_time, finish_time

                    if all_finished:
                        break

                    sleep(_processes * 7.5)

                del result_completed
                del start_time
                del all_finished

                arcpy.AddMessage(f"Get the return values")

                for table_name, job_result in jobs.items():
                    worker_results = job_result.get()
                    results.extend(worker_results)
                    del table_name, job_result, worker_results

                arcpy.AddMessage(f"\tClose the process pool")
                # close the process pool
                pool.close()
                # wait for all tasks to complete and processes to close
                pool.join()
                # Just in case
                pool.terminate()

                del jobs

            del pool
            del _processes, chunk_size
            del multiprocessing

            arcpy.AddMessage(f"\tDone with multiprocessing Pool")

        # Post-Processing
        arcpy.AddMessage("Post-Processing")
        if results:
            arcpy.AddMessage("Processing Results")
            #print(results)

            for result in results:
                dataset = os.path.basename(result)
                region_gdb  = os.path.dirname(result)

                arcpy.AddMessage(f"\tResult: '{dataset}'")
                arcpy.AddMessage(f"\t\tPath:       '{result}'")
                arcpy.AddMessage(f"\t\tRegion GDB: '{region_gdb}'")

                #if arcpy.Exists(rf"{project_gdb}\{dataset}"):
                #    arcpy.management.Delete(rf"{project_gdb}\{dataset}")
                #    arcpy.AddMessage("\tDelete: {0} {1}\n".format(dataset, arcpy.GetMessages(0).replace("\n", '\n\t')))

                arcpy.management.Copy(result, rf"{project_gdb}\{dataset}")
                arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

                dismap.alter_fields(csv_data_folder, rf"{project_gdb}\{dataset}")

                try:
                    dismap.import_metadata(rf"{project_gdb}\{dataset}")
                except SystemExit as se:
                    arcpy.AddError("SystemExit " + str(se))
                    traceback.print_exc()
                except Exception as e:
                    arcpy.AddError("Exception " + str(e))
                    traceback.print_exc()
                except:
                    traceback.print_exc()


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
        del dismap, math, worker
        del sleep, gmtime, localtime, strftime, time
        # Function Parameters
        del project_gdb, Sequential, table_names

    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(arcpy.GetMessages())
        traceback.print_exc()
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages())
        traceback.print_exc()
    except SystemExit as se:
        arcpy.AddError(str(se))
        traceback.print_exc()
    except Exception as e:
        arcpy.AddError(str(e))
        traceback.print_exc()
    except:
        traceback.print_exc()
    else:
        try:
            leave_out_keys = ["leave_out_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys
            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
        except:
            raise Exception(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

def post_processing(project_gdb=""):
    try:
        import dismap
        importlib.reload(dismap)

        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(1) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        project_folder  = os.path.dirname(project_gdb)
        scratch_folder  = rf"{project_folder}\Scratch"
        scratch_gdb     = rf"{project_folder}\Scratch\scratch.gdb"
        csv_data_folder = rf"{project_folder}\CSV Data"

        arcpy.env.workspace                = project_gdb
        arcpy.env.scratchWorkspace         = scratch_gdb
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        del project_folder, scratch_gdb

        results = []

        arcpy.env.workspace = scratch_folder

        # List all file geodatabases in the current workspace
        wss = [ws for ws in arcpy.ListWorkspaces("*", "FileGDB") if not ws.endswith("scratch.gdb")]

        for ws in wss:
            arcpy.AddMessage(f"Compacting the '{os.path.basename(ws)}' GDB")
            arcpy.management.Compact(ws)
            arcpy.AddMessage("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))

            arcpy.env.workspace = ws

            tbs = [tb for tb in arcpy.ListTables("*") if not tb.endswith("Datasets")]
            if len(tbs) == 1:
                tb = tbs[0]
            if tb:
                fcs = [fc for fc in arcpy.ListFeatureClasses(f"{tb}*", "Point")]
                if len(fcs) == 1:
                    fc = fcs[0]

            results.append(rf"{ws}\{tb}")
            results.append(rf"{ws}\{fc}")

            del tbs, fcs
            del tb, fc
            del ws
        del wss

        # Post-Processing
        arcpy.AddMessage("Post-Processing")
        if results:
            arcpy.AddMessage("Processing Results")
            #print(results)

            for result in results:
                dataset = os.path.basename(result)
                region_gdb  = os.path.dirname(result)

                arcpy.AddMessage(f"\tResult: '{dataset}'")
                arcpy.AddMessage(f"\t\tPath:       '{result}'")
                arcpy.AddMessage(f"\t\tRegion GDB: '{region_gdb}'")

                arcpy.management.Copy(result, rf"{project_gdb}\{dataset}")
                arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages(0).replace("\n", '\n\t')))

                dismap.alter_fields(csv_data_folder, rf"{project_gdb}\{dataset}")

                try:
                    dismap.import_metadata(rf"{project_gdb}\{dataset}")
                except SystemExit as se:
                    arcpy.AddError("SystemExit " + str(se))
                    traceback.print_exc()
                except Exception as e:
                    arcpy.AddError("Exception " + str(e))
                    traceback.print_exc()
                except:
                    traceback.print_exc()

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
            #results = list(map(lambda region_gdb: region_gdb.replace(os.path.dirname(region_gdb), project_gdb), results))

        else:
            arcpy.AddMessage(f"No results in '{inspect.stack()[0][3]}'")

        arcpy.AddMessage(f"Compacting the '{os.path.basename(project_gdb)}' GDB")
        arcpy.management.Compact(project_gdb)
        arcpy.AddMessage("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))

        # Variables assigned in function
        del scratch_folder, csv_data_folder
        # Imports
        del dismap
        # Function Parameters
        del project_gdb

    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(arcpy.GetMessages())
        traceback.print_exc()
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages())
        traceback.print_exc()
    except SystemExit as se:
        arcpy.AddError(str(se))
        traceback.print_exc()
    except Exception as e:
        arcpy.AddError(str(e))
        traceback.print_exc()
    except:
        traceback.print_exc()
    else:
        try:
            leave_out_keys = ["leave_out_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys
            return True
        except:
            raise Exception(traceback.print_exc())
    finally:
        pass

def main(project="", test=False):
    try:
        from create_region_sample_locations_director import director

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        project_gdb = rf"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\{project}\{project}.gdb"

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

        project_folder  = rf"{os.path.dirname(project_gdb)}"
        csv_data_folder = rf"{project_folder}\CSV Data"

        # Change directory
        os.chdir(csv_data_folder)
        # Get list of files using a wildcard
        wild_card = "_survey.csv"
        csv_data_files = [f for f in os.listdir() if f.endswith(f"{wild_card}")]
        for csv_data_file in csv_data_files:
            if arcpy.Exists(csv_data_file.replace("_survey", "_IDW")):
                arcpy.management.Delete(csv_data_file.replace("_survey", "_IDW"))
            arcpy.AddMessage(csv_data_file)
            os.rename(csv_data_file, csv_data_file.replace("_survey", "_IDW"))
            del csv_data_file

        del wild_card, csv_data_files

        try:
            pass
            # "AI_IDW", "EBS_IDW", "ENBS_IDW", "GMEX_IDW", "GOA_IDW", "HI_IDW", "NBS_IDW", "NEUS_FAL_IDW", "NEUS_SPR_IDW",
            # "SEUS_FAL_IDW", "SEUS_SPR_IDW", "SEUS_SUM_IDW", "WC_GLMME", "WC_GFDL", "WC_ANN_IDW", "WC_TRI_IDW",

            if test:
                pass
                #director(project_gdb=project_gdb, Sequential=True, table_names=["NBS_IDW", "ENBS_IDW", "HI_IDW"])
                #result = director(project_gdb=project_gdb, Sequential=True, table_names=["HI_IDW"])
                #results.extend(result)del result
                #print(result); del result
            else:
                pass
                #director(project_gdb=project_gdb, Sequential=False, table_names=["NBS_IDW", "ENBS_IDW", "HI_IDW"])
                director(project_gdb=project_gdb, Sequential=False, table_names=["AI_IDW", "EBS_IDW", "ENBS_IDW", "GMEX_IDW", "GOA_IDW", "HI_IDW", "NBS_IDW", "NEUS_FAL_IDW", "NEUS_SPR_IDW", "SEUS_FAL_IDW", "SEUS_SPR_IDW", "SEUS_SUM_IDW", "WC_ANN_IDW", "WC_TRI_IDW"])
                #director(project_gdb=project_gdb, Sequential=False, table_names=["EBS_IDW", "GMEX_IDW", "SEUS_SUM_IDW", "WC_ANN_IDW", "WC_TRI_IDW"])
                #director(project_gdb=project_gdb, Sequential=False, table_names=["HI_IDW"])
                #result = director(project_gdb=project_gdb, Sequential=False, table_names=["HI_IDW"])
                #results.extend(result); del result
                #print(result); del result

##                director(project_gdb=project_gdb, Sequential=True, table_names=["NBS_IDW", "ENBS_IDW", "HI_IDW",])
##                #result = director(project_gdb=project_gdb, Sequential=True, table_names=["NBS_IDW", "ENBS_IDW", "HI_IDW",])
##                #results.extend(result); del result
##
##                director(project_gdb=project_gdb, Sequential=True, table_names=["SEUS_FAL_IDW", "SEUS_SPR_IDW", "SEUS_SUM_IDW",])
##                #result = director(project_gdb=project_gdb, Sequential=True, table_names=["SEUS_FAL_IDW", "SEUS_SPR_IDW", "SEUS_SUM_IDW",])
##                #results.extend(result); del result
##
##                director(project_gdb=project_gdb, Sequential=True, table_names=["WC_TRI_IDW", "GMEX_IDW", "AI_IDW",])
##                #result = director(project_gdb=project_gdb, Sequential=True, table_names=["WC_TRI_IDW", "GMEX_IDW", "AI_IDW",])
##                #results.extend(result); del result
##
##                director(project_gdb=project_gdb, Sequential=True, table_names=["GOA_IDW", "WC_ANN_IDW", "NEUS_FAL_IDW",])
##                #result = director(project_gdb=project_gdb, Sequential=True, table_names=["GOA_IDW", "WC_ANN_IDW", "NEUS_FAL_IDW",])
##                #results.extend(result); del result
##
##                director(project_gdb=project_gdb, Sequential=True, table_names=["NEUS_SPR_IDW", "EBS_IDW",])
##                #result = director(project_gdb=project_gdb, Sequential=True, table_names=["NEUS_SPR_IDW", "EBS_IDW",])
##                #results.extend(result); del result

            PostProcessing = False
            if PostProcessing:
                post_processing(project_gdb=project_gdb)
            del PostProcessing

        except SystemExit as se:
            arcpy.AddError(str(se))
            traceback.print_exc()
        except Exception as e:
            arcpy.AddError(str(e))
            traceback.print_exc()
        except:
            traceback.print_exc()

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

        # Function Variables
        del project_gdb
        del project_folder, csv_data_folder
        # Function Imports
        del director
        # Function Parameters
        del project
        if "test" in locals().keys(): del test

    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(arcpy.GetMessages())
        traceback.print_exc()
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages())
        traceback.print_exc()
    except SystemExit as se:
        arcpy.AddError(str(se))
        traceback.print_exc()
    except Exception as e:
        arcpy.AddError(str(e))
        traceback.print_exc()
    except:
        traceback.print_exc()
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
        import create_region_sample_locations_director
        importlib.reload(create_region_sample_locations_director)

        from time import gmtime, localtime, strftime, time

        # Set a start time so that we can see how log things take
        start_time = time()

        print(f"{'-' * 90}")
        print(f"Python Script:  {os.path.basename(__file__)}")
        print(f"Location:       {os.path.dirname(__file__)}")
        print(f"Python Version: {sys.version} Environment: {os.path.basename(sys.exec_prefix)}")
        print(f"{'-' * 90}\n")

        #project = "April 1 2023"
        #project = "May 1 2024"
        #project = "July 1 2024"
        project = "December 1 2024"

        # Tested on 7/31/2024 -- PASSED
        main(project=project, test=False)

        del project

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time

        print(f"\n{'-' * 90}")
        print(f"Python script: {os.path.basename(__file__)} successfully completed {strftime('%a %b %d %I:%M %p', localtime())}")
        print(u"Elapsed Time {0} (H:M:S)".format(strftime("%H:%M:%S", gmtime(elapse_time))))
        print(f"{'-' * 90}")
        del elapse_time, end_time, start_time
        del gmtime, localtime, strftime, time

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
