# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        create_indicators_table_worker
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

def main(project_gdb=""):
    try:

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        arcpy.env.workspace = project_gdb

        table_names = [row[0] for row in arcpy.da.SearchCursor(rf"{project_gdb}\Datasets", "TableName", where_clause = "DistributionProjectCode = 'IDW'")]

        tables = [tb for tb in arcpy.ListTables("*") if tb in table_names]

        for table in sorted(tables):
            #arcpy.AddMessage(f"{table}")

            sample_locations = f"{table}_Sample_Locations"

            table_count            = int(arcpy.management.GetCount(table)[0])
            sample_locations_count = int(arcpy.management.GetCount(sample_locations)[0])

            diff = table_count - sample_locations_count

            #arcpy.AddMessage(f"{table:<13} has {table_count:<8} records")
            #arcpy.AddMessage(f"{sample_locations:<13} has {sample_locations_count:<8} records")
            if diff > 0:
                arcpy.AddMessage(f"{table} and {sample_locations} difference:\n\t {diff:<4} records")

            del sample_locations, table_count, sample_locations_count, diff

            del table

        del project_gdb, table_names, tables

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
        print(f"{'-' * 90}")
        print(f"Python Script:  {os.path.basename(__file__)}")
        print(f"Location:       {os.path.dirname(__file__)}")
        print(f"Python Version: {sys.version} Environment: {os.path.basename(sys.exec_prefix)}")
        print(f"{'-' * 90}\n")

        base_project_folder = os.path.dirname(os.path.dirname(__file__))

        # project = "April 1 2023"
        #project = "May 1 2024"
        project = "July 1 2024"

        project_gdb = rf"{base_project_folder}\{project}\{project}.gdb"

        # Tested on 7/30/2024 -- PASSED
        main(project_gdb=project_gdb)

        del project, project_gdb
        del base_project_folder

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
        remaining_keys = [key for key in locals().keys() if not key.startswith("__") and key not in leave_out_keys]
        if remaining_keys:
            arcpy.AddWarning(f"Remaining Keys: ##--> '{', '.join(remaining_keys)}' <--##")
        del leave_out_keys, remaining_keys
    finally:
        pass
