"""
Script documentation
- Tool parameters are accessed using arcpy.GetParameter() or
                                     arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or
                                        arcpy.SetParameterAsText()
"""

import inspect
import os
import traceback

import arcpy


def script_tool(new_project_folder, project_folders):
    """Script code goes below"""
    try:
        arcpy.env.overwriteOutput = True

        try:
            aprx = arcpy.mp.ArcGISProject("CURRENT")
            os.chdir(aprx.homeFolder)
            arcpy.env.workspace = aprx.defaultGeodatabase
            #del aprx
        except Exception:
            #print(e)
            aprx = arcpy.mp.ArcGISProject(os.path.join(os.path.expanduser('~'), "Documents\\ArcGIS\\Projects\\DisMAP\\ArcGIS-Analysis-Python\\DisMAP.aprx"))
            os.chdir(aprx.homeFolder)
            arcpy.env.workspace = aprx.defaultGeodatabase
            #del aprx


        if not arcpy.Exists(os.path.join(aprx.homeFolder, new_project_folder)):
            arcpy.AddMessage(f"Creating Home Folder: '{os.path.basename(aprx.homeFolder)}'")
            arcpy.management.CreateFolder(aprx.homeFolder, new_project_folder)
            arcpy.AddMessage(arcpy.GetMessages())
        else:
            arcpy.AddMessage(f"Home Folder: '{os.path.basename(os.path.join(aprx.homeFolder, new_project_folder))}' Exists")


        if not arcpy.Exists(os.path.join(aprx.homeFolder, new_project_folder, f"{new_project_folder}.gdb")):
            arcpy.AddMessage(
                f"Creating Project GDB: '{new_project_folder}.gdb'"
            )
            arcpy.management.CreateFileGDB(os.path.join(aprx.homeFolder, new_project_folder), f"{new_project_folder}"
            )
            arcpy.AddMessage(arcpy.GetMessages())
        else:
            arcpy.AddMessage(f"Project GDB: '{new_project_folder}.gdb' exists")

        if not arcpy.Exists(os.path.join(aprx.homeFolder, new_project_folder, "Scratch")):
            arcpy.AddMessage("Creating the Scratch Folder")
            arcpy.management.CreateFolder(os.path.join(aprx.homeFolder, new_project_folder), "Scratch")
            arcpy.AddMessage(arcpy.GetMessages())
        else:
            arcpy.AddMessage(f"Scratch Folder for: {new_project_folder} exists")

        if not arcpy.Exists(os.path.join(aprx.homeFolder, new_project_folder, "Scratch", "scratch.gdb")):
            arcpy.AddMessage("Creating the Scratch GDB")
            arcpy.management.CreateFileGDB(os.path.join(aprx.homeFolder, new_project_folder, "Scratch"), "scratch")
            arcpy.AddMessage(arcpy.GetMessages())
        else:
            arcpy.AddMessage("Scratch GDB Exists")

        for _project_folder in project_folders.split(";"):
            if not arcpy.Exists(
                rf"{aprx.homeFolder}\{new_project_folder}\{_project_folder}"
            ):
                arcpy.AddMessage(f"Creating Folder: {_project_folder}")
                arcpy.management.CreateFolder(
                    rf"{aprx.homeFolder}\{new_project_folder}", _project_folder
                )
                arcpy.AddMessage(arcpy.GetMessages())
            else:
                arcpy.AddMessage(f"Folder: '{_project_folder}' Exists")
            del _project_folder
        if not arcpy.Exists(os.path.join(aprx.homeFolder, new_project_folder, f"{new_project_folder}.aprx")):
            aprx.saveACopy(os.path.join(aprx.homeFolder, new_project_folder, f"{new_project_folder}.aprx")
            )
            arcpy.AddMessage(arcpy.GetMessages())
        else:
            pass

        _aprx = arcpy.mp.ArcGISProject(os.path.join(aprx.homeFolder, new_project_folder,
            f"{new_project_folder}.aprx")
        )
        # Remove maps
        _maps = _aprx.listMaps()
        if len(_maps) > 0:
            for _map in _maps:
                arcpy.AddMessage(_map.name)
                #aprx.deleteItem(_map)
                del _map
        del _maps
        _aprx.save()

        databases = []
        databases.append(
            {
                "databasePath": rf"{aprx.homeFolder}\{new_project_folder}\{new_project_folder}.gdb",
                "isDefaultDatabase": True,
            }
        )
        _aprx.updateDatabases(databases)
        arcpy.AddMessage(f"Databases: {databases}")
        del databases
        _aprx.save()

        toolboxes = []
        toolboxes.append(
            {"toolboxPath": rf"{aprx.homeFolder}\DisMAP.atbx", "isDefaultToolbox": True}
        )
        _aprx.updateToolboxes(toolboxes)
        arcpy.AddMessage(f"Toolboxes: {toolboxes}")
        del toolboxes
        _aprx.save()
        del _aprx

        # Declared variables
        del aprx
        # Function parameters
        del new_project_folder, project_folders

    except arcpy.ExecuteWarning:
        arcpy.AddWarning(
            f"ArcPy Execute Warning in '{inspect.stack()[0][3]}':\n{arcpy.GetMessages(1)}"
        )
    except arcpy.ExecuteError:
        arcpy.AddError(
            f"ArcPy Execute Error in '{inspect.stack()[0][3]}':\n{arcpy.GetMessages(2)}"
        )
        arcpy.AddError("Traceback:\n")
        traceback.print_exc()
    except SystemExit:
        # This is not an error, so we allow the script to exit.
        pass
    except Exception as e:
        arcpy.AddError(
            f"An unexpected error occurred in '{inspect.stack()[0][3]}': {e}"
        )
        arcpy.AddError("Traceback:\n")
        traceback.print_exc()
    else:
        arcpy.AddMessage("\nScript finished successfully.")
        return True
    finally:
        arcpy.AddMessage(f"\n{'--End' * 10}--")


if __name__ == "__main__":
    try:
        new_project_folder = arcpy.GetParameterAsText(0)
        project_folders = arcpy.GetParameterAsText(1)

        if not new_project_folder:
            # new_project_folder = "August-1-2025"
            # new_project_folder = "February-1-2026"
            new_project_folder = "June-1-2026"
        else:
            pass

        if not project_folders:
            project_folders = (
                "CRFs;CSV_Data;Dataset_Shapefiles;Images;Layers;Metadata_ArcGIS;Metadata_Export;Metadata_Gemini;Metadata_InPort;Publish"
            )
        else:
            pass

        script_tool(new_project_folder, project_folders)

        arcpy.SetParameterAsText(3, "Result")

        del new_project_folder, project_folders

    except SystemExit:
        # This is not an error, so we allow the script to exit.
        pass
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
    except Exception:
        traceback.print_exc()


# This is an autogenerated comment.
