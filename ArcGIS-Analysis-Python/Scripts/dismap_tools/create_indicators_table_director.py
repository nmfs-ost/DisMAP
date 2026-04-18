# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        create_indicators_table_director
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

def director(project_gdb="", Sequential=True, table_names=[]):
    try:
        # Imports
        import dismap_tools
        from create_indicators_table_worker import preprocessing, worker

        # Test if passed workspace exists, if not sys.exit()
        if not arcpy.Exists(rf"{project_gdb}"):
            arcpy.AddError(f"{os.path.basename(project_gdb)} is missing!!")
            arcpy.AddError(arcpy.GetMessages(2))
            sys.exit()
        else:
            pass

        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(1) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        #project_folder    = os.path.dirname(project_gdb)
        scratch_workspace = rf"{os.path.dirname(project_gdb)}\Scratch\scratch.gdb"
        scratch_folder    = rf"{os.path.dirname(project_gdb)}\Scratch"
        csv_data_folder   = rf"{os.path.dirname(project_gdb)}\CSV_Data"

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.env.workspace                = project_gdb
        arcpy.env.scratchWorkspace         = scratch_workspace

        preprocessing(project_gdb=project_gdb, table_names=table_names, clear_folder=True)

        # Sequential Processing
        if Sequential:
            arcpy.AddMessage("Sequential Processing")
            for i in range(0, len(table_names)):
                arcpy.AddMessage(f"Processing: {table_names[i]}")
                table_name = table_names[i]
                region_gdb = os.path.join(scratch_folder, f"{table_name}.gdb")
                try:
                    worker(region_gdb=region_gdb)
                except:  # noqa: E722
                    arcpy.AddError(arcpy.GetMessages(2))
                    traceback.print_exc()
                    sys.exit()
                del region_gdb, table_name
                del i
        else:
            pass

        # Non-Sequential Processing
        if not Sequential:
            arcpy.AddMessage("Non-Sequential Processing")
            # Imports
            import multiprocessing
            from time import time, localtime, strftime, sleep, gmtime
            arcpy.AddMessage("Start multiprocessing using the ArcGIS Pro pythonw.exe.")
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
                                except:  # noqa: E722
                                    pool.terminate()
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

        datasets = list()
        walk = arcpy.da.Walk(scratch_folder, datatype=["Table", "FeatureClass"])
        for dirpath, dirnames, filenames in walk:
            for filename in filenames:
                datasets.append(os.path.join(dirpath, filename))
                del filename
            del dirpath, dirnames, filenames
        del walk
        for dataset in datasets:
            datasets_short_path = f".. {'/'.join(dataset.split(os.sep)[-4:])}"
            dataset_name = os.path.basename(dataset)
            region_gdb   = os.path.dirname(dataset)
            arcpy.AddMessage(f"\tDataset: '{dataset_name}'")
            arcpy.AddMessage(f"\t\tPath:       '{datasets_short_path}'")
            arcpy.AddMessage(f"\t\tRegion GDB: '{os.path.basename(region_gdb)}'")
            arcpy.management.Copy(dataset, rf"{project_gdb}\{dataset_name}")
            arcpy.AddMessage("\tCopy: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
            #arcpy.management.Delete(dataset)
            #arcpy.AddMessage(f"\t\tAlter Fields for: '{dataset}'")
            #dismap_tools.alter_fields(csv_data_folder, rf"{project_gdb}\{dataset}")
            del region_gdb, dataset_name, datasets_short_path
            del dataset
        del datasets

        arcpy.AddMessage(f"Compacting the {os.path.basename(project_gdb)} GDB")
        arcpy.management.Compact(project_gdb)
        arcpy.AddMessage("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))
        # Declared Variables
        del scratch_folder, csv_data_folder, scratch_workspace
        # Imports
        del preprocessing, worker, dismap_tools
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

def process_indicator_tables(project_gdb=""):
    try:
        # Import
        from arcpy import metadata as md
        import dismap_tools

        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(1) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        project_folder    = os.path.dirname(project_gdb)
        scratch_folder    = os.path.join(project_folder, "Scratch")
        scratch_workspace = os.path.join(project_folder, "Scratch\\scratch.gdb")
        csv_data_folder   = rf"{project_folder}\CSV_Data"

        arcpy.env.workspace                = project_gdb
        arcpy.env.scratchWorkspace         = scratch_workspace
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        arcpy.management.CreateTable(project_gdb, "Indicators", "", "", "")
        arcpy.AddMessage("\tCreate Table: {0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

        indicators = rf"{project_gdb}\Indicators"

        dismap_tools.add_fields(csv_data_folder, indicators)
        #dismap_tools.alter_fields(csv_data_folder, indicators)
        dismap_tools.import_metadata(csv_data_folder, indicators)

        #in_tables = [it for it in arcpy.ListTables("*_Indicators") if it == "AI_IDW_Indicators"]
        #in_tables = [it for it in arcpy.ListTables("*_Indicators") if not any(lo in it for lo in ["GFDL", "GLMME"])]
        in_tables = [it for it in arcpy.ListTables("*_Indicators")]

        if not in_tables:
            arcpy.AddWarning(f"Indicator Tables are not present in the {os.path.basename(project_gdb)} GDB")
        else:
            for in_table in sorted(in_tables):
                arcpy.AddMessage(f"Table: {in_table}")
                in_table_path = rf"{project_gdb}\{in_table}"
                del in_table

                arcpy.AddMessage("\tUpdating field values to replace None with empty string")

                fields = [f.name for f in arcpy.ListFields(in_table_path) if f.type == "String"]
                #for field in fields:
                #    arcpy.AddMessage(f"\t{field.name}\t{field.type}")
                #    del field
                # Create update cursor for feature class
                with arcpy.da.UpdateCursor(in_table_path, fields) as cursor:
                    for row in cursor:
                        #arcpy.AddMessage(row)
                        for field_value in row:
                            #arcpy.AddMessage(field_value)
                            if field_value is None:
                                row[row.index(field_value)] = ""
                                cursor.updateRow(row)
                            del field_value
                        del row
                    del cursor
                del fields

                fields = [f.name for f in arcpy.ListFields(in_table_path) if f.name == "DateCode"]
                #for field in fields:
                #    arcpy.AddMessage(f"\t{field.name}\t{field.type}")
                #    del field
                # Create update cursor for feature class
                with arcpy.da.UpdateCursor(in_table_path, fields) as cursor:
                    for row in cursor:
                        #arcpy.AddMessage(row)
                        #arcpy.AddMessage(dismap_tools.date_code(row[0]))
                        datecode = dismap_tools.date_code(row[0])
                        #arcpy.AddMessage(datecode)
                        row[0] = datecode
                        cursor.updateRow(row)
                        del datecode
                        del row
                    del cursor
                del fields

                arcpy.management.Append(inputs=in_table_path, target=indicators, schema_type="TEST", field_mapping="", subtype="")
                arcpy.AddMessage("\tAppend: {0} {1}\n".format(f"{os.path.basename(in_table_path)}", arcpy.GetMessages(0).replace("\n", '\n\t')))

                del in_table_path
            # end for loop

        dataset_md = md.Metadata(indicators)
        dataset_md.synchronize("ALWAYS")
        dataset_md.save()
        del dataset_md

        arcpy.AddMessage(f"Compacting the {os.path.basename(project_gdb)} GDB")
        arcpy.management.Compact(project_gdb)
        arcpy.AddMessage("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))
        # Declared Variables assigned in function
        del in_tables, indicators
        del scratch_folder, scratch_workspace, csv_data_folder, project_folder
        # Imports
        del dismap_tools, md
        # Function Parameters
        del project_gdb

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
        arcpy.AddMessage(f"Location:       .. {'/'.join(__file__.split(os.sep)[-4:])}")
        arcpy.AddMessage(f"Python Version: {sys.version}")
        arcpy.AddMessage(f"Environment:    {os.path.basename(sys.exec_prefix)}")
        arcpy.AddMessage(f"Start Time:     {strftime('%a %b %d %I:%M %p', localtime(start_time))}")
        arcpy.AddMessage(f"{'-' * 80}\n")

        # Test if passed workspace exists, if not sys.exit()
        if not arcpy.Exists(project_gdb):
            sys.exit()(f"{os.path.basename(project_gdb)} is missing!!")
        else:
            pass

        try:
            pass
            # "AI_IDW", "EBS_IDW", "ENBS_IDW", "GMEX_IDW", "GOA_IDW", "HI_IDW", "NBS_IDW", "NEUS_FAL_IDW", "NEUS_SPR_IDW",
            # "SEUS_FAL_IDW", "SEUS_SPR_IDW", "SEUS_SUM_IDW", "WC_ANN_IDW", "WC_TRI_IDW",

            Test = False
            if Test:
                director(project_gdb=project_gdb, Sequential=True, table_names=["AI_IDW", "HI_IDW",])
            elif not Test:
                pass
                director(project_gdb=project_gdb, Sequential=False, table_names=["AI_IDW", "EBS_IDW", "ENBS_IDW", "GMEX_IDW", "GOA_IDW", "HI_IDW", "NBS_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["NEUS_FAL_IDW", "NEUS_SPR_IDW", "SEUS_FAL_IDW", "SEUS_SPR_IDW", "SEUS_SUM_IDW", "WC_ANN_IDW", "WC_TRI_IDW",])
            else:
                pass
            del Test

            # Combine Indicator Tables
            CombineIndicatorTables = True
            if CombineIndicatorTables:
                process_indicator_tables(project_gdb=project_gdb)
            else:
                pass
            del CombineIndicatorTables

        except:  # noqa: E722
            traceback.print_exc()
            sys.exit()

        # Declared Variables
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
