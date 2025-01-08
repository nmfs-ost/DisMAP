# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        dismap_project_setup
# Purpose:
#
# Author:      john.f.kennedy
#
# Created:     09/03/2024
# Copyright:   (c) john.f.kennedy 2024
# Licence:     <your licence>
# -------------------------------------------------------------------------------
import os, sys  # built-ins first
import traceback
import importlib
import inspect

import arcpy  # third-parties second

sys.path.append(os.path.dirname(__file__))

def project_folders(base_project_file="", project=""):
    try:
        import calendar

        arcpy.env.overwriteOutput = True
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2)
        arcpy.SetMessageLevels(["NORMAL"])  # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        aprx = arcpy.mp.ArcGISProject(base_project_file)
        home_folder = aprx.homeFolder

        # Get a list of projects in the base folder
        projects = [pf for pf in os.listdir(home_folder) if any(m in pf for m in list(calendar.month_name)[1:])]

        # print(f"In Project: {project}")
        # for _project in projects:
        #    print(f"Found project: {_project}")
        #    del _project

        # Add project passed to function to the projects list
        if project and project not in projects:
            projects.append(project)

        for _project in projects:
            arcpy.AddMessage(f"Checking/Creating folders for the {_project} project")
            if not os.path.isdir(rf"{home_folder}\{_project}\ArcGIS Metadata"):
                os.makedirs(rf"{home_folder}\{_project}\ArcGIS Metadata")

            if not os.path.isdir(rf"{home_folder}\{_project}\Bathymetry"):
                os.makedirs(rf"{home_folder}\{_project}\Bathymetry")

            if not os.path.isdir(rf"{home_folder}\{_project}\CRFs"):
                os.makedirs(rf"{home_folder}\{_project}\CRFs")

            if not os.path.isdir(rf"{home_folder}\{_project}\CSV Data"):
                os.makedirs(rf"{home_folder}\{_project}\CSV Data")

            if not os.path.isdir(rf"{home_folder}\{_project}\Current Metadata"):
                os.makedirs(rf"{home_folder}\{_project}\Current Metadata")

            if not os.path.isdir(rf"{home_folder}\{_project}\Dataset Shapefiles"):
                os.makedirs(rf"{home_folder}\{_project}\Dataset Shapefiles")

            if not os.path.isdir(rf"{home_folder}\{_project}\Export Metadata"):
                os.makedirs(rf"{home_folder}\{_project}\Export Metadata")

            if not os.path.isdir(rf"{home_folder}\{_project}\Template Metadata"):
                os.makedirs(rf"{home_folder}\{_project}\Template Metadata")

            if not os.path.isdir(rf"{home_folder}\{_project}\Images"):
                os.makedirs(rf"{home_folder}\{_project}\Images")

            if not os.path.isdir(rf"{home_folder}\{_project}\InPort Metadata"):
                os.makedirs(rf"{home_folder}\{_project}\InPort Metadata")

            if not os.path.isdir(rf"{home_folder}\{_project}\Import Metadata"):
                os.makedirs(rf"{home_folder}\{_project}\Import Metadata")

            if not os.path.isdir(rf"{home_folder}\{_project}\Layers"):
                os.makedirs(rf"{home_folder}\{_project}\Layers")

            if not os.path.isdir(rf"{home_folder}\{_project}\Layouts"):
                os.makedirs(rf"{home_folder}\{_project}\Layouts")

            if not os.path.isdir(rf"{home_folder}\{_project}\Project Metadata"):
                os.makedirs(rf"{home_folder}\{_project}\Project Metadata")

            if not os.path.isdir(rf"{home_folder}\{_project}\Publish"):
                os.makedirs(rf"{home_folder}\{_project}\Publish")

            if not os.path.isdir(rf"{home_folder}\{_project}\Scratch"):
                os.makedirs(rf"{home_folder}\{_project}\Scratch")

            if not arcpy.Exists(rf"{home_folder}\{_project}\Scratch\scratch.gdb"):
                arcpy.management.CreateFileGDB(rf"{home_folder}\{_project}\Scratch", f"scratch")

            if not arcpy.Exists(rf"{home_folder}\{_project}\{_project}.gdb"):
                arcpy.management.CreateFileGDB(rf"{home_folder}\{_project}", f"{_project}")

            if not arcpy.Exists(rf"{home_folder}\{_project}\Bathymetry\Bathymetry.gdb"):
                arcpy.management.CreateFileGDB(rf"{home_folder}\{_project}\Bathymetry", "Bathymetry")

            del _project

        aprx.save()

        if aprx.folderConnections:
            arcpy.AddMessage(f"Folder Connections")
            connection_strings = aprx.folderConnections
            # Removes duplicate folder connections if they exists
            cs_list = []
            for cs in connection_strings:
                if cs not in cs_list and arcpy.Exists(cs["connectionString"]):
                    cs_list.append(cs)
                del cs
            aprx.updateFolderConnections(cs_list)
            aprx.save()
            del cs_list, connection_strings

            folder_connection_paths = [cs["connectionString"] for cs in aprx.folderConnections]
            #arcpy.AddMessage(f"{folder_connection_paths}")

            my_documents = rf"{os.environ['USERPROFILE']}\Documents"
            my_projects = rf"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects"

            if my_documents not in folder_connection_paths:
                arcpy.AddMessage(f"\tMy Documents: {my_documents}")
                connection_strings = aprx.folderConnections
                connection_strings.append({"alias": "My Documents", "connectionString": my_documents, "isHomeFolder": False,})
                aprx.updateFolderConnections(connection_strings)
                aprx.save()
                del connection_strings
            if my_projects not in folder_connection_paths:
                arcpy.AddMessage(rf"\tMy Projects: {my_projects}")
                connection_strings = aprx.folderConnections
                connection_strings.append({"alias": "My Projects", "connectionString": my_projects, "isHomeFolder": False,})
                aprx.updateFolderConnections(connection_strings)
                aprx.save()
                del connection_strings

            del my_documents, my_projects

            for folder in projects:
                arcpy.AddMessage(f"\tProject: {folder}")
                project_path = rf"{aprx.homeFolder}\{folder}"
                if project_path not in folder_connection_paths:
                    arcpy.AddMessage(f"\t\tProject Path: {project_path}")
                    connection_strings = aprx.folderConnections
                    connection_strings.append({"alias" : "", "connectionString" : project_path, "isHomeFolder" : False,})
                    aprx.updateFolderConnections(connection_strings)
                    aprx.save()
                    del connection_strings
                del project_path
                del folder
            del folder_connection_paths

        if aprx.databases:
            arcpy.AddMessage(f"Databases")
            database_paths = [db["databasePath"] for db in aprx.databases]
            #arcpy.AddMessage(database_paths)
            for database_path in database_paths:
                if arcpy.Exists(database_path):
                    arcpy.AddMessage(database_path)
                    arcpy.management.Compact(database_path)
                del database_path
            #del database_paths
            for folder in projects:
                arcpy.AddMessage(f"\tProject: {folder}")
                project_gdb_path = rf"{aprx.homeFolder}\{folder}\{folder}.gdb"
                #arcpy.management.Compact(project_gdb_path)
                if project_gdb_path not in database_paths:
                    arcpy.AddMessage(f"\t\tProject GDB: {project_gdb_path}")
                    databases = aprx.databases
                    databases.append({"databasePath": project_gdb_path, "isDefaultDatabase": False})
                    aprx.updateDatabases(databases)
                    del databases
                del project_gdb_path
                del folder
            del database_paths

        aprx.save()

        # Variables assigned in function
        del projects
        del home_folder
        del aprx
        # Import
        del calendar
        # Function Parameters
        del base_project_file, project

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
            raise SystemExit(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

def main(project=""):
    try:
        arcpy.env.overwriteOutput = True
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2)
        arcpy.SetMessageLevels(["NORMAL"])  # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        base_project_folder = os.path.dirname(os.path.dirname(__file__))
        base_project_file = rf"{base_project_folder}\DisMAP.aprx"

        project_folders(base_project_file, project)

        del base_project_folder, base_project_file
        del project

    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(str(traceback.print_exc()) + arcpy.GetMessages())
    except arcpy.ExecuteError:
        arcpy.AddError(str(traceback.print_exc()) + arcpy.GetMessages())
    except SystemExit as se:
        arcpy.AddError(str(se))
    except:
        arcpy.AddError(str(traceback.print_exc()))
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

if __name__ == "__main__":
    try:
        import dismap_project_setup
        importlib.reload(dismap_project_setup)

        print(f"{'-' * 90}")
        print(f"Python Script:  {os.path.basename(__file__)}")
        print(f"Location:       {os.path.dirname(__file__)}")
        print(f"Python Version: {sys.version} Environment: {os.path.basename(sys.exec_prefix)}")
        print(f"{'-' * 90}\n")

        #project = "May 1 2024"
        #project = "July 1 2024"
        project = "December 1 2024"

        # Tested on 8/2/2024 -- PASSED
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
        remaining_keys = [key for key in locals().keys() if not key.startswith("__") and key not in leave_out_keys]
        if remaining_keys:
            arcpy.AddWarning(f"Remaining Keys: ##--> '{', '.join(remaining_keys)}' <--##")
        del leave_out_keys, remaining_keys
    finally:
        pass
