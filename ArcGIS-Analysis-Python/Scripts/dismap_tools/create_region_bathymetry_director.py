# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      john.f.kennedy
#
# Created:     05/03/2024
# Copyright:   (c) john.f.kennedy 2024
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os
import sys # built-ins first
import traceback

import arcpy # third-parties second

def trace():
    import sys, traceback  # noqa: E401
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    line = tbinfo.split(", ")[1]
    filename = sys.path[0] + os.sep + "test.py"
    synerror = traceback.format_exc().splitlines()[-1]
    return line, filename, synerror

def preprocessing(project_gdb="", table_names="", clear_folder=True):
    try:
        import dismap_tools

        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(1) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        # Set basic arcpy.env variables
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        # Set varaibales
        project_folder    = os.path.dirname(project_gdb)
        scratch_folder    = os.path.join(project_folder, "Scratch")
        scratch_workspace = os.path.join(project_folder, "Scratch\\scratch.gdb")
        csv_data_folder   = os.path.join(project_folder, "CSV_Data")
        base_project_bathymetry_gdb = os.path.join(os.path.dirname(project_folder), "Bathymetry\\Bathymetry.gdb")

##        # Clear Scratch Folder
##        #ClearScratchFolder = True
##        #if ClearScratchFolder:
##        if clear_folder:
##            dismap_tools.clear_folder(folder = scratch_folder)
##        else:
##            pass
##        #del ClearScratchFolder
##        del clear_folder

        arcpy.env.workspace        = project_gdb
        arcpy.env.scratchWorkspace = scratch_workspace
        del project_folder, scratch_workspace

        if not table_names:
            table_names = [row[0] for row in arcpy.da.SearchCursor(os.path.join(project_gdb, "Datasets"), "TableName", where_clause = "TableName LIKE '%_IDW'")]
        else:
            pass

        for table_name in table_names:
            arcpy.AddMessage(f"Pre-Processing: {table_name}")

            region_gdb = os.path.join(scratch_folder, f"{table_name}.gdb")
            region_scratch_workspace = os.path.join(scratch_folder, f"{table_name}", "scratch.gdb")

            # Create Scratch Workspace for Region
            if not arcpy.Exists(region_scratch_workspace):
                os.makedirs(os.path.join(scratch_folder,  table_name))
                if not arcpy.Exists(region_scratch_workspace):
                    arcpy.AddMessage(f"Create File GDB: '{table_name}'")
                    arcpy.management.CreateFileGDB(os.path.join(scratch_folder,  table_name), "scratch")
                    arcpy.AddMessage("\tCreate File GDB: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
            del region_scratch_workspace
            # # # CreateFileGDB
            arcpy.AddMessage(f"Creating File GDB: '{table_name}'")
            arcpy.management.CreateFileGDB(scratch_folder, table_name)
            arcpy.AddMessage("\tCreate File GDB: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
            # # # CreateFileGDB

            # # # Datasets
            # Process: Make Table View (Make Table View) (management)
            datasets = rf'{project_gdb}\Datasets'
            arcpy.AddMessage(f"'{os.path.basename(datasets)}' has {arcpy.management.GetCount(datasets)[0]} records")
            arcpy.management.Copy(datasets, os.path.join(region_gdb, "Datasets"))
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
            del datasets
            # # # Datasets

            # # # Fishnet
            region_fishnet = os.path.join(project_gdb, f"{table_name}_Fishnet")
            arcpy.AddMessage(f"The table '{table_name}_Fishnet' has {arcpy.management.GetCount(region_fishnet)[0]} records")
            arcpy.management.Copy(region_fishnet, os.path.join(region_gdb, f"{table_name}_Fishnet"))
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
            del region_fishnet
            # # # Fishnet

            # # # Raster_Mask
            region_raster_mask = os.path.join(project_gdb, f"{table_name}_Raster_Mask")
            arcpy.AddMessage(f"Copy Raster Mask for '{table_name}'")
            #arcpy.management.Copy(os.path.join(project_gdb, f"{table_name}_Raster_Mask"), os.path.join(region_gdb, f"{table_name}_Raster_Mask"))
            arcpy.management.CopyRaster(region_raster_mask, os.path.join(region_gdb, f"{table_name}_Raster_Mask"))
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
            del region_raster_mask
            # # # Raster_Mask

            # # # Bathymetry
            base_fishnet_bathymetry = os.path.join(base_project_bathymetry_gdb, f"{table_name}_Bathymetry")
            arcpy.AddMessage(f"Copy Bathymetry for '{table_name}'")
            #arcpy.management.Copy(os.path.join(project_bathymetry_gdb, f"{table_name}_Bathymetry"), os.path.join(region_gdb, f"{table_name}_Fishnet_Bathymetry"))
            arcpy.management.CopyRaster(base_fishnet_bathymetry, os.path.join(region_gdb, f"{table_name}_Fishnet_Bathymetry"))
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
            del base_fishnet_bathymetry
            # # # Bathymetry

            # Declared Variables
            del table_name

        # Declared Variables
        del scratch_folder, region_gdb
        del csv_data_folder, base_project_bathymetry_gdb
        # Imports
        del dismap_tools
        # Function Parameters
        del project_gdb, table_names

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

def director(project_gdb="", Sequential=True, table_names=[]):
    try:
        # Imports
        import dismap_tools
        from create_region_bathymetry_worker import worker

        # Test if passed workspace exists, if not sys.exit()
        if not arcpy.Exists(project_gdb):
            arcpy.AddError(f"{os.path.basename(project_gdb)} is missing!!")
            arcpy.AddError(arcpy.GetMessages(2))
            sys.exit()
        else:
            pass

        # Set History and Metadata logs, set serverity and message level
        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        project_folder    = os.path.dirname(project_gdb)
        scratch_folder    = rf"{os.path.dirname(project_gdb)}\Scratch"
        scratch_workspace = rf"{os.path.dirname(project_gdb)}\Scratch\scratch.gdb"
        csv_data_folder   = rf"{os.path.dirname(project_gdb)}\CSV_Data"
        #project_bathymetry_gdb = rf"{os.path.dirname(project_gdb)}\Bathymetry\Bathymetry.gdb"

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.env.workspace                = project_gdb
        arcpy.env.scratchWorkspace         = scratch_workspace

        preprocessing(project_gdb=project_gdb, table_names=table_names, clear_folder=True)

        del project_folder, scratch_workspace

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
                    traceback.print_exc()
                del region_gdb, table_name
                del i
        else:
            pass

        # Non-Sequential Processing
        if not Sequential:
            import multiprocessing
            from time import time, localtime, strftime, sleep, gmtime
            arcpy.AddMessage("Sequential Processing")
            #Set multiprocessing exe in case we're running as an embedded process, i.e ArcGIS
            #get_install_path() uses a registry query to figure out 64bit python exe if available
            multiprocessing.set_executable(os.path.join(sys.exec_prefix, 'pythonw.exe'))
            # Get CPU count and then take 2 away for other process
            _processes = multiprocessing.cpu_count() - 2
            _processes = _processes if len(table_names) >= _processes else len(table_names)
            arcpy.AddMessage(f"Creating the multiprocessing Pool with {_processes} processes")
            #Create a pool of workers, keep one cpu free for surfing the net.
            #Let each worker process only handle 1 task before being restarted (in case of nasty memory leaks)
            with multiprocessing.Pool(processes=_processes, maxtasksperchild=1) as pool:
                arcpy.AddMessage("\tPrepare arguments for processing")
                # Use apply_async so we can handle exceptions gracefully
                jobs={}
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
                    elapse_time =  end_time - start_time
                    arcpy.AddMessage(f"\nStart Time: {strftime('%a %b %d %I:%M %p', localtime(start_time))}")
                    arcpy.AddMessage("Have the workers finished?")
                    finish_time = strftime('%a %b %d %I:%M %p', localtime())
                    time_elapsed = u"Elapsed Time {0} (H:M:S)".format(strftime("%H:%M:%S", gmtime(elapse_time)))
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
                            arcpy.AddMessage(f"Process {table_name}\n\tFinished on {result_completed[table_name]}")
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
                arcpy.AddMessage("\tWait for all tasks to complete and processes to close")
                pool.join()
                # Just in case
                pool.terminate()
                del pool
                del jobs
            del _processes
            del time, multiprocessing, localtime, strftime, sleep, gmtime

            arcpy.AddMessage("\tDone with multiprocessing Pool")

        # Post-Processing
        arcpy.AddMessage("Post-Processing Begins")
        arcpy.AddMessage("Processing Results")

        datasets = list()

        walk = arcpy.da.Walk(scratch_folder, datatype="RasterDataset", type=[])
        for dirpath, dirnames, filenames in walk:
            for filename in filenames:
                datasets.append(os.path.join(dirpath, filename))
                del filename
            del dirpath, dirnames, filenames
        del walk

        for dataset in datasets:
            dataset_short_path = f"..{'/'.join(__file__.split(os.sep)[-4:])}"
            #arcpy.AddMessage(fc_short_path)
            dataset_name = os.path.basename(dataset)
            region_gdb   = os.path.dirname(dataset)
            arcpy.AddMessage(f"\tDataset: '{dataset_name}'")
            arcpy.AddMessage(f"\t\tPath:       '{dataset_short_path}'")
            arcpy.AddMessage(f"\t\tRegion GDB: '{os.path.basename(region_gdb)}'")

##            if arcpy.Exists(rf"{project_gdb}\{dataset_name}"):
##                arcpy.management.Delete(rf"{project_gdb}\{dataset_name}")
##            else:
##                pass

            arcpy.management.CopyRaster(dataset, rf"{project_gdb}\{dataset_name}")
            arcpy.AddMessage("\tCopy: {0} {1}\n".format(f"{dataset_name}", arcpy.GetMessages(0).replace("\n", '\n\t')))

            desc = arcpy.da.Describe(dataset)
            if desc["dataType"] in ["FeatureClass", "Table", "MosaicDataset"]:
                dismap_tools.alter_fields(csv_data_folder, rf"{project_gdb}\{dataset_name}")
            del desc

            del region_gdb, dataset_name, dataset_short_path, dataset

        del datasets

        arcpy.AddMessage(f"Compacting the {os.path.basename(project_gdb)} GDB")
        arcpy.management.Compact(project_gdb)
        arcpy.AddMessage("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))

        # Declared Variables
        del csv_data_folder, scratch_folder
        # Imports
        del dismap_tools, worker
        # Function Parameters
        del project_gdb, Sequential, table_names

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
        from time import gmtime, localtime, strftime, time
        # Set a start time so that we can see how log things take
        start_time = time()
        arcpy.AddMessage(f"{'-' * 80}")
        arcpy.AddMessage(f"Python Script:  {os.path.basename(__file__)}")
        arcpy.AddMessage(f"Location:       ..{'/'.join(__file__.split(os.sep)[-4:])}")
        arcpy.AddMessage(f"Python Version: {sys.version}")
        arcpy.AddMessage(f"Environment:    {os.path.basename(sys.exec_prefix)}")
        arcpy.AddMessage(f"Start Time:     {strftime('%a %b %d %I:%M %p', localtime(start_time))}")
        arcpy.AddMessage(f"{'-' * 80}\n")

        try:
            # "AI_IDW", "EBS_IDW", "ENBS_IDW", "GMEX_IDW", "GOA_IDW", "HI_IDW", "NBS_IDW", "NEUS_FAL_IDW", "NEUS_SPR_IDW",
            # "SEUS_FAL_IDW", "SEUS_SPR_IDW", "SEUS_SUM_IDW", "WC_ANN_IDW", "WC_TRI_IDW",

            Test = False
            if Test:
                director(project_gdb=project_gdb, Sequential=True, table_names=["HI_IDW"])
            else:
                director(project_gdb=project_gdb, Sequential=False, table_names=["AI_IDW", "EBS_IDW", "ENBS_IDW", "GMEX_IDW", "GOA_IDW", "HI_IDW", "NBS_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["NEUS_FAL_IDW", "NEUS_SPR_IDW", "SEUS_FAL_IDW", "SEUS_SPR_IDW", "SEUS_SUM_IDW", "WC_ANN_IDW", "WC_TRI_IDW",])
            del Test

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

    except:  # noqa: E722
        #Gets non-tool errors
        line, filename, err = trace()
        arcpy.AddError("Python error on " + line + " of " + filename)
        arcpy.AddError(err)

