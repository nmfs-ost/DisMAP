# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        create_region_fishnets_director.py
# Purpose:
#
# Author:      john.f.kennedy
#
# Created:     25/02/2024
# Copyright:   (c) john.f.kennedy 2024
# Licence:     <your licence>
# -------------------------------------------------------------------------------
import inspect
import os
import sys
import traceback

import arcpy  # third-parties second


def director(project_gdb="", Sequential=True, table_names=[]):
    try:
        # Imports
        import dismap_tools
        from create_region_fishnets_worker import worker

        # Set History and Metadata logs, set serverity and message level
        arcpy.SetLogHistory(
            True
        )  # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(
            1
        )  # 0—A tool will not throw an exception, even if the tool produces an error or warning.
        # 1—If a tool produces a warning or an error, it will throw an exception.
        # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(
            ["NORMAL"]
        )  # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        # Set basic workkpace variables
        project_folder = os.path.dirname(project_gdb)
        scratch_folder = os.path.join(project_folder, "Scratch")
        scratch_workspace = os.path.join(project_folder, "Scratch\\scratch.gdb")
        csv_data_folder = os.path.join(project_folder, f"CSV_Data")

        # Clear Scratch Folder
        dismap_tools.clear_folder(folder=scratch_folder)

        # Create Scratch Workspace for Project
        if not arcpy.Exists(os.path.join(scratch_folder, "scratch.gdb")):
            if not arcpy.Exists(scratch_folder):
                os.makedirs(scratch_folder)
            if not arcpy.Exists(os.path.join(scratch_folder, "scratch.gdb")):
                arcpy.management.CreateFileGDB(rf"{scratch_folder}", "scratch")

        # Set basic workkpace variables
        arcpy.env.workspace = project_gdb
        arcpy.env.scratchWorkspace = scratch_workspace
        arcpy.env.overwriteOutput = True
        arcpy.env.parallelProcessingFactor = "100%"

        del project_folder

        if not table_names:
            table_names = [
                row[0]
                for row in arcpy.da.SearchCursor(
                    os.path.join(project_gdb, "Datasets"),
                    "TableName",
                    where_clause="TableName LIKE '%_IDW'",
                )
            ]
        else:
            pass

        # Pre Processing
        for table_name in table_names:
            arcpy.AddMessage(f"Pre-Processing: {table_name}")

            region_gdb = os.path.join(scratch_folder, f"{table_name}.gdb")
            region_scratch_workspace = os.path.join(
                scratch_folder, f"{table_name}", "scratch.gdb"
            )

            # Create Scratch Workspace for Region
            if not arcpy.Exists(region_scratch_workspace):
                os.makedirs(os.path.join(scratch_folder, table_name))
                if not arcpy.Exists(region_scratch_workspace):
                    arcpy.management.CreateFileGDB(
                        os.path.join(scratch_folder, table_name), "scratch"
                    )
            del region_scratch_workspace

            datasets = [
                os.path.join(project_gdb, "Datasets"),
                os.path.join(project_gdb, f"{table_name}_Region"),
            ]
            if not any(arcpy.management.GetCount(d)[0] == 0 for d in datasets):
                if not arcpy.Exists(os.path.join(scratch_folder, f"{table_name}.gdb")):
                    arcpy.management.CreateFileGDB(
                        rf"{scratch_folder}", f"{table_name}"
                    )
                    arcpy.AddMessage(
                        "\tCreate File GDB: {0}\n".format(
                            arcpy.GetMessages().replace("\n", "\n\t")
                        )
                    )
                else:
                    pass

                arcpy.management.Copy(
                    os.path.join(project_gdb, "Datasets"), rf"{region_gdb}\Datasets"
                )
                arcpy.AddMessage(
                    "\tCopy: {0}\n".format(arcpy.GetMessages().replace("\n", "\n\t"))
                )

                arcpy.management.Copy(
                    os.path.join(project_gdb, f"{table_name}_Region"),
                    rf"{region_gdb}\{table_name}_Region",
                )
                arcpy.AddMessage(
                    "\tCopy: {0}\n".format(arcpy.GetMessages().replace("\n", "\n\t"))
                )

            else:
                arcpy.AddWarning("One or more datasets contains zero records!!")
                for d in datasets:
                    arcpy.AddMessage(
                        f"\t{os.path.basename(d)} has {arcpy.management.GetCount(d)[0]} records"
                    )
                    del d
                arcpy.AddError(
                    f"SystemExit at line number: '{traceback.extract_stack()[-1].lineno}'"
                )
                sys.exit()

            if "datasets" in locals().keys():
                del datasets

            del region_gdb, table_name

        del scratch_workspace

        # Sequential Processing
        if Sequential:
            arcpy.AddMessage("Sequential Processing")
            for i in range(0, len(table_names)):
                arcpy.AddMessage(f"Processing: {table_names[i]}")
                table_name = table_names[i]
                region_gdb = os.path.join(scratch_folder, f"{table_name}.gdb")
                try:
                    pass
                    worker(region_gdb=region_gdb)
                except:  # noqa: E722
                    arcpy.AddError(arcpy.GetMessages(2))
                    traceback.print_exc()
                    sys.exit()
                del region_gdb, table_name
                del i

        # Non-Sequential Processing
        if not Sequential:
            import multiprocessing
            from time import gmtime, localtime, sleep, strftime, time

            arcpy.AddMessage("Sequential Processing")
            # Set multiprocessing exe in case we're running as an embedded process, i.e ArcGIS
            # get_install_path() uses a registry query to figure out 64bit python exe if available
            multiprocessing.set_executable(os.path.join(sys.exec_prefix, "pythonw.exe"))
            # Get CPU count and then take 2 away for other process
            _processes = multiprocessing.cpu_count() - 2
            _processes = (
                _processes if len(table_names) >= _processes else len(table_names)
            )
            arcpy.AddMessage(
                f"Creating the multiprocessing Pool with {_processes} processes"
            )
            # Create a pool of workers, keep one cpu free for surfing the net.
            # Let each worker process only handle 1 task before being restarted (in case of nasty memory leaks)
            with multiprocessing.Pool(processes=_processes, maxtasksperchild=1) as pool:
                arcpy.AddMessage("\tPrepare arguments for processing")
                # Use apply_async so we can handle exceptions gracefully
                jobs = {}
                for i in range(0, len(table_names)):
                    try:
                        arcpy.AddMessage(f"Processing: {table_names[i]}")
                        table_name = table_names[i]
                        region_gdb = os.path.join(scratch_folder, f"{table_name}.gdb")
                        jobs[table_name] = pool.apply_async(worker, [region_gdb])
                        del table_name, region_gdb
                    except:  # noqa: E722
                        pool.terminate()
                        arcpy.AddError(arcpy.GetMessages(2))
                        traceback.print_exc()
                        sys.exit()
                    del i
                all_finished = False
                # Set a start time so that we can see how log things take
                start_time = time()
                result_completed = {}
                while True:
                    all_finished = True
                    # Elapsed time
                    end_time = time()
                    elapse_time = end_time - start_time
                    arcpy.AddMessage(
                        f"\nStart Time: {strftime('%a %b %d %I:%M %p', localtime(start_time))}"
                    )
                    arcpy.AddMessage("Have the workers finished?")
                    finish_time = strftime("%a %b %d %I:%M %p", localtime())
                    time_elapsed = "Elapsed Time {0} (H:M:S)".format(
                        strftime("%H:%M:%S", gmtime(elapse_time))
                    )
                    arcpy.AddMessage(f"It's {finish_time}\n{time_elapsed}")
                    finish_time = f"{finish_time}.\n\t{time_elapsed}"
                    del time_elapsed
                    for table_name, result in jobs.items():
                        if result.ready():
                            if table_name not in result_completed:
                                result_completed[table_name] = finish_time
                                try:
                                    # wait for and get the result from the task
                                    result.get()
                                except SystemExit:
                                    pool.terminate()
                                    arcpy.AddError(arcpy.GetMessages(2))
                                    traceback.print_exc()
                                    sys.exit()
                                except:  # noqa: E722
                                    pool.terminate()
                                    arcpy.AddError(arcpy.GetMessages(2))
                                    traceback.print_exc()
                                    sys.exit()
                            else:
                                pass
                            arcpy.AddMessage(
                                f"Process {table_name}\n\tFinished on {result_completed[table_name]}"
                            )
                        else:
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
                arcpy.AddMessage("\tClose the process pool")
                # close the process pool
                pool.close()
                # wait for all tasks to complete and processes to close
                arcpy.AddMessage(
                    "\tWait for all tasks to complete and processes to close"
                )
                pool.join()
                # Just in case
                pool.terminate()
                del pool
                del jobs
            del _processes
            del time, multiprocessing, localtime, strftime, sleep, gmtime
            arcpy.AddMessage("\tDone with multiprocessing Pool")

        arcpy.AddMessage("Post-Processing")
        arcpy.AddMessage("Processing Results")
        datasets = list()
        # walk = arcpy.da.Walk(scratch_folder, datatype="FeatureClass", type=["Polyline", "Polygon"])
        walk = arcpy.da.Walk(scratch_folder)
        for dirpath, dirnames, filenames in walk:
            for filename in filenames:
                datasets.append(os.path.join(dirpath, filename))
                del filename
            del dirpath, dirnames, filenames
        del walk
        for dataset in datasets:
            datasets_short_path = f".. {'/'.join(dataset.split(os.sep)[-4:])}"
            dataset_name = os.path.basename(dataset)
            region_gdb = os.path.dirname(dataset)
            arcpy.AddMessage(f"\tDataset: '{dataset_name}'")
            arcpy.AddMessage(f"\t\tPath:       '{datasets_short_path}'")
            arcpy.AddMessage(f"\t\tRegion GDB: '{os.path.basename(region_gdb)}'")
            arcpy.management.Copy(dataset, rf"{project_gdb}\{dataset_name}")
            arcpy.AddMessage(
                "\tCopy: {0}\n".format(arcpy.GetMessages().replace("\n", "\n\t"))
            )
            arcpy.management.Delete(dataset)
            arcpy.AddMessage(
                "\tDelete: {0}\n".format(arcpy.GetMessages().replace("\n", "\n\t"))
            )
            arcpy.management.Compact(region_gdb)
            arcpy.AddMessage(
                "\tCompact: {0}\n".format(arcpy.GetMessages().replace("\n", "\n\t"))
            )
            del region_gdb
            del dataset
            del dataset_name
            del datasets_short_path
        del datasets
        arcpy.AddMessage(f"Compacting the {os.path.basename(project_gdb)} GDB")
        arcpy.management.Compact(project_gdb)
        arcpy.AddMessage("\t" + arcpy.GetMessages(0).replace("\n", "\n\t"))
        # Declared Variables assigned in function
        del scratch_folder, csv_data_folder
        # Imports
        del dismap_tools, worker
        # Function Parameters
        del project_gdb, Sequential, table_names
    except KeyboardInterrupt:
        sys.exit()
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(
            f"Caught an arcpy.ExecuteWarning error in the '{inspect.stack()[0][3]}' function."
        )
        arcpy.AddWarning(arcpy.GetMessages(1))
    except arcpy.ExecuteError:
        arcpy.AddError(
            f"Caught an arcpy.ExecuteError error in the '{inspect.stack()[0][3]}' function."
        )
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
        sys.exit()
    except SystemExit as se:
        arcpy.AddError(
            f"Caught an SystemExit error: {se} in the '{inspect.stack()[0][3]}' function."
        )
        sys.exit()
    except Exception as e:
        arcpy.AddError(
            f"Caught an Exception error: {e} in the '{inspect.stack()[0][3]}' function."
        )
        traceback.print_exc()
        sys.exit()
    except:  # noqa: E722
        arcpy.AddError(
            f"Caught an except error in the '{inspect.stack()[0][3]}' function."
        )
        traceback.print_exc()
        sys.exit()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith("__")]
        if rk:
            arcpy.AddMessage(
                f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function at line number {inspect.stack()[0][2]}\n\t##--> '{', '.join(rk)}' <--##"
            )
        del rk
        return True
    finally:
        pass


def script_tool(project_gdb=""):
    try:
        # Imports
        from time import gmtime, localtime, strftime, time

        # Set a start time so that we can see how log things take
        start_time = time()
        arcpy.AddMessage(f"{'-' * 80}")
        arcpy.AddMessage(f"Python Script:  {os.path.basename(__file__)}")
        arcpy.AddMessage(f"Location:       .. {'/'.join(__file__.split(os.sep)[-4:])}")
        arcpy.AddMessage(f"Python Version: {sys.version}")
        arcpy.AddMessage(f"Environment:    {os.path.basename(sys.exec_prefix)}")
        arcpy.AddMessage(
            f"Start Time:     {strftime('%a %b %d %I:%M %p', localtime(start_time))}"
        )
        arcpy.AddMessage(f"{'-' * 80}\n")

        # Set varaibales
        project_folder = os.path.dirname(project_gdb)
        scratch_folder = rf"{project_folder}\Scratch"
        del project_folder

        # Create project scratch workspace, if missing
        if not arcpy.Exists(os.path.join(scratch_folder, "scratch.gdb")):
            if not arcpy.Exists(scratch_folder):
                os.makedirs(scratch_folder)
            if not arcpy.Exists(os.path.join(scratch_folder, "scratch.gdb")):
                arcpy.management.CreateFileGDB(rf"{scratch_folder}", "scratch")
        del scratch_folder

        # Set basic arcpy.env variables
        arcpy.env.overwriteOutput = True
        arcpy.env.parallelProcessingFactor = "100%"

        try:
            pass
            # "AI_IDW", "EBS_IDW", "ENBS_IDW", "GMEX_IDW", "GOA_IDW", "HI_IDW", "NBS_IDW", "NEUS_FAL_IDW", "NEUS_SPR_IDW",
            # "SEUS_FAL_IDW", "SEUS_SPR_IDW", "SEUS_SUM_IDW", "WC_ANN_IDW", "WC_TRI_IDW",

            test = False
            if test:
                # director(project_gdb=project_gdb, Sequential=True, table_names=["HI_IDW"])
                # director(project_gdb=project_gdb, Sequential=False, table_names=["SEUS_SPR_IDW", "HI_IDW"])
                # director(project_gdb=project_gdb, Sequential=False, table_names=["SEUS_SPR_IDW", "SEUS_FAL_IDW",])
                director(
                    project_gdb=project_gdb,
                    Sequential=True,
                    table_names=["NBS_IDW", "SEUS_FAL_IDW"],
                )
            else:
                director(
                    project_gdb=project_gdb,
                    Sequential=False,
                    table_names=[
                        "NBS_IDW",
                        "ENBS_IDW",
                        "HI_IDW",
                        "SEUS_FAL_IDW",
                        "SEUS_SPR_IDW",
                    ],
                )
                director(
                    project_gdb=project_gdb,
                    Sequential=False,
                    table_names=[
                        "WC_TRI_IDW",
                        "GMEX_IDW",
                        "AI_IDW",
                        "GOA_IDW",
                        "WC_ANN_IDW",
                    ],
                )
                director(
                    project_gdb=project_gdb,
                    Sequential=False,
                    table_names=[
                        "NEUS_SPR_IDW",
                        "EBS_IDW",
                        "NEUS_FAL_IDW",
                        "SEUS_SUM_IDW",
                    ],
                )
            del test

        except:  # noqa: E722
            arcpy.AddError(arcpy.GetMessages(2))
            traceback.print_exc()
            sys.exit()

        # Declared Varaiables
        # Imports
        # Function Parameters
        del project_gdb
        # Elapsed time
        end_time = time()
        elapse_time = end_time - start_time
        hours, rem = divmod(end_time - start_time, 3600)
        minutes, seconds = divmod(rem, 60)
        arcpy.AddMessage(f"\n{'-' * 80}")
        arcpy.AddMessage(f"Python script: {os.path.basename(__file__)}")
        arcpy.AddMessage(
            f"Start Time:    {strftime('%a %b %d %I:%M %p', localtime(start_time))}"
        )
        arcpy.AddMessage(
            f"End Time:      {strftime('%a %b %d %I:%M %p', localtime(end_time))}"
        )
        arcpy.AddMessage(
            f"Elapsed Time   {int(hours):0>2}:{int(minutes):0>2}:{seconds:05.2f} (H:M:S)"
        )
        arcpy.AddMessage(f"{'-' * 80}")
        del hours, rem, minutes, seconds
        del elapse_time, end_time, start_time
        del gmtime, localtime, strftime, time

    except KeyboardInterrupt:
        sys.exit()
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(
            f"Caught an arcpy.ExecuteWarning error in the '{inspect.stack()[0][3]}' function."
        )
        arcpy.AddWarning(arcpy.GetMessages(1))
    except arcpy.ExecuteError:
        arcpy.AddError(
            f"Caught an arcpy.ExecuteError error in the '{inspect.stack()[0][3]}' function."
        )
        arcpy.AddError(arcpy.GetMessages(2))
    except SystemExit as se:
        arcpy.AddError(
            f"Caught an SystemExit error: {se} in the '{inspect.stack()[0][3]}' function."
        )
        sys.exit()
    except Exception as e:
        arcpy.AddError(
            f"Caught an Exception error: {e} in the '{inspect.stack()[0][3]}' function."
        )
        traceback.print_exc()
        sys.exit()
    except:  # noqa: E722
        arcpy.AddError(
            f"Caught an except error in the '{inspect.stack()[0][3]}' function."
        )
        traceback.print_exc()
        sys.exit()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith("__")]
        if rk:
            arcpy.AddMessage(
                f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function at line number {inspect.stack()[0][2]}\n\t##--> '{', '.join(rk)}' <--##"
            )
        del rk
        return True
    finally:
        pass


if __name__ == "__main__":
    try:
        project_gdb = arcpy.GetParameterAsText(0)
        if not project_gdb:
            # project_gdb = rf"{os.path.expanduser('~')}\Documents\ArcGIS\Projects\DisMAP\ArcGIS-Analysis-Python\February 1 2026\February 1 2026.gdb"
            project_gdb = os.path.join(
                os.path.expanduser("~"),
                "Documents\\ArcGIS\\Projects\\DisMAP\\ArcGIS-Analysis-Python\\February 1 2026\\February 1 2026.gdb",
            )
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
# This is an autogenerated comment.
