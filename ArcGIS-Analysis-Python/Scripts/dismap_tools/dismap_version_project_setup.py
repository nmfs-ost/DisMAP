"""
Script documentation
- Tool parameters are accessed using arcpy.GetParameter() or
                                     arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or
                                        arcpy.SetParameterAsText()
"""

import os
import traceback

import arcpy


def trace():
    import sys  # noqa: E401
    import traceback

    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    line = tbinfo.split(", ")[1]
    filename = sys.path[0] + os.sep + "test.py"
    synerror = traceback.print_exc().splitlines()[-1]
    return line, filename, synerror


def _create_project_structure(home_folder, new_project_folder, project_folders):
    """
    Helper function to create the project's folder and geodatabase structure.
    """
    try:
        # Create main project folder
        project_path = rf"{home_folder}\{new_project_folder}"
        if not arcpy.Exists(project_path):
            arcpy.AddMessage(f"Creating Project Folder: '{new_project_folder}'")
            arcpy.management.CreateFolder(home_folder, new_project_folder)
            arcpy.AddMessage(arcpy.GetMessages())
        else:
            arcpy.AddMessage(f"Project Folder: '{new_project_folder}' Exists")

        # Create project geodatabase
        project_gdb_path = rf"{project_path}\{new_project_folder}.gdb"
        if not arcpy.Exists(project_gdb_path):
            arcpy.AddMessage(f"Creating Project GDB: '{new_project_folder}.gdb'")
            arcpy.management.CreateFileGDB(project_path, new_project_folder)
            arcpy.AddMessage(arcpy.GetMessages())
        else:
            arcpy.AddMessage(f"Project GDB: {new_project_folder}.gdb exists")

        # Create Scratch folder
        scratch_folder_path = rf"{project_path}\Scratch"
        if not arcpy.Exists(scratch_folder_path):
            arcpy.AddMessage("Creating the Scratch Folder")
            arcpy.management.CreateFolder(project_path, "Scratch")
            arcpy.AddMessage(arcpy.GetMessages())
        else:
            arcpy.AddMessage(f"Scratch Folder: {new_project_folder}/Scratch exists")

        # Create Scratch geodatabase
        scratch_gdb_path = rf"{scratch_folder_path}\scratch.gdb"
        if not arcpy.Exists(scratch_gdb_path):
            arcpy.AddMessage("Creating the Scratch GDB")
            arcpy.management.CreateFileGDB(scratch_folder_path, "scratch")
            arcpy.AddMessage(arcpy.GetMessages())
        else:
            arcpy.AddMessage("Scratch GDB Exists")

        # Create additional project folders
        for _project_folder in project_folders.split(";"):
            folder_path = rf"{project_path}\{_project_folder}"
            if not arcpy.Exists(folder_path):
                arcpy.AddMessage(f"Creating Folder: {_project_folder}")
                arcpy.management.CreateFolder(project_path, _project_folder)
                arcpy.AddMessage(arcpy.GetMessages())
            else:
                arcpy.AddMessage(f"Folder: '{_project_folder}' Exists")

        return True
    except Exception as e:
        arcpy.AddError(f"Error creating project structure: {e}")
        traceback.print_exc()
        return False


def script_tool(base_project_folder="", new_project_folder="", project_folders=""):
    """Script code goes below"""
    try:
        arcpy.env.overwriteOutput = True
        aprx = None # Initialize aprx to None
        try: # Attempt to get the current project
            aprx = arcpy.mp.ArcGISProject("CURRENT")
        except (RuntimeError, FileNotFoundError) as e: # If no current project, try to open a specific one
            arcpy.AddWarning(f"Could not open current ArcGIS Project: {e}. Attempting to open default project.")
            aprx = arcpy.mp.ArcGISProject(os.path.join(base_project_folder, "DisMAP.aprx"))
        except Exception as e: # Catch any other unexpected errors during aprx loading
            arcpy.AddError(f"An unexpected error occurred while loading the ArcGIS Project: {e}")
            traceback.print_exc()
            return False

        # Check if aprx object is valid before proceeding
        if aprx is None:
            arcpy.AddError("Failed to load ArcGIS Project. Exiting script_tool.")
            return False

        aprx.save()
        home_folder = aprx.homeFolder

        if not _create_project_structure(home_folder, new_project_folder, project_folders):
            return False # Exit if project structure creation failed

        if not arcpy.Exists(
            rf"{home_folder}\{new_project_folder}\{new_project_folder}.aprx"
        ):
            aprx.saveACopy(
                rf"{home_folder}\{new_project_folder}\{new_project_folder}.aprx"
            )
            arcpy.AddMessage(arcpy.GetMessages())
        else:
            pass

        _aprx = arcpy.mp.ArcGISProject(
            rf"{home_folder}\{new_project_folder}\{new_project_folder}.aprx"
        )
        # Remove maps
        _maps = _aprx.listMaps()
        if len(_maps) > 0:
            for _map in _maps:
                arcpy.AddMessage(_map.name)
                aprx.deleteItem(_map)
                del _map
        del _maps
        _aprx.save()

        databases = []
        databases.append(
            {
                "databasePath": rf"{home_folder}\{new_project_folder}\{new_project_folder}.gdb",
                "isDefaultDatabase": True,
            }
        )
        _aprx.updateDatabases(databases)
        arcpy.AddMessage(f"Databases: {databases}")
        del databases
        _aprx.save()

        toolboxes = []
        toolboxes.append(
            {"toolboxPath": rf"{home_folder}\DisMAP.atbx", "isDefaultToolbox": True}
        )
        _aprx.updateToolboxes(toolboxes)
        arcpy.AddMessage(f"Toolboxes: {toolboxes}")
        del toolboxes
        _aprx.save()
        del _aprx

        # Declared variables
        del home_folder, aprx
        # Function parameters
        del new_project_folder, project_folders
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(arcpy.GetMessages(1))
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
        # raise SystemExit
    except SystemExit:
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
        # raise SystemExit
    except Exception:
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
        # raise SystemExit
    except:  # noqa: E722  # noqa: E722
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
        # raise SystemExit
    else:
        pass
        return True
    finally:
        pass

if __name__ == "__main__":
    try:

        base_project_folder = arcpy.GetParameterAsText(0)
        new_project_folder = arcpy.GetParameterAsText(1)
        project_folders = arcpy.GetParameterAsText(2)

        if not base_project_folder:
            base_project_folder = os.path.join(
                os.path.expanduser("~"),
                f"Documents\\ArcGIS\\Projects\\DisMAP\\ArcGIS-Analysis-Python",
            )
        else:
            pass

        if not new_project_folder:
            new_project_folder = "August-1-2025"
        else:
            pass

        if not project_folders:
            project_folders = (
                "CRFs;CSV_Data;Dataset_Shapefiles;Images;Layers;Metadata_Export;Gemini_Metadata_Export;Publish"
            )
        else:
            pass

        # Call script_tool and check its return value
        result = script_tool(base_project_folder, new_project_folder, project_folders)

        if result:
            arcpy.SetParameterAsText(3, "Success")
        else:
            arcpy.SetParameterAsText(3, "Failed")

        del base_project_folder, new_project_folder, project_folders

    except SystemExit:
        # SystemExit is usually raised for intentional exits, but still log it if it happens here.
        arcpy.AddError("Script terminated by SystemExit in main block.")
        traceback.print_exc()
        arcpy.SetParameterAsText(3, "Failed")
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
        arcpy.SetParameterAsText(3, "Failed")
    except Exception:
        traceback.print_exc()
        arcpy.AddError("An unexpected error occurred in main block.")
        arcpy.SetParameterAsText(3, "Failed")

# This is an autogenerated comment.
