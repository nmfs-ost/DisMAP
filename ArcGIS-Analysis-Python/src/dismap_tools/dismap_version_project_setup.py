"""
Script documentation
- Tool parameters are accessed using arcpy.GetParameter() or
                                     arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or
                                        arcpy.SetParameterAsText()
"""
import os
import arcpy
import traceback

def trace():
    import sys, traceback  # noqa: E401
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    line = tbinfo.split(", ")[1]
    filename = sys.path[0] + os.sep + "test.py"
    synerror = traceback.format_exc().splitlines()[-1]
    return line, filename, synerror

def script_tool(base_project_folder="", new_project_folder="", project_folders=""):
    """Script code goes below"""
    try:
        arcpy.env.overwriteOutput = True
        try:
            aprx = arcpy.mp.ArcGISProject("CURRENT")
        except:  # noqa: E722
            aprx = arcpy.mp.ArcGISProject(rf"{base_project_folder}\DisMAP.aprx")

        aprx.save()
        home_folder = aprx.homeFolder
        if not arcpy.Exists(rf"{home_folder}\{new_project_folder}"):
            arcpy.AddMessage(f"Creating Home Folder: '{os.path.basename(home_folder)}'")
            arcpy.management.CreateFolder(home_folder, new_project_folder)
            arcpy.AddMessage(arcpy.GetMessages())
        else:
            arcpy.AddMessage(f"Home Folder: '{os.path.basename(home_folder)}' Exists")
        if not arcpy.Exists(rf"{home_folder}\{new_project_folder}\{new_project_folder}.gdb"):
            arcpy.AddMessage(f"Creating Project GDB: '{os.path.basename(home_folder)}.gdb'")
            arcpy.management.CreateFileGDB(rf"{home_folder}\{new_project_folder}", f"{new_project_folder}")
            arcpy.AddMessage(arcpy.GetMessages())
        else:
            arcpy.AddMessage(f"Project GDB: {new_project_folder}.gdb exists")
        if not arcpy.Exists(rf"{home_folder}\{new_project_folder}\Scratch"):
            arcpy.AddMessage("Creating the Scratch Folder")
            arcpy.management.CreateFolder(rf"{home_folder}\{new_project_folder}", "Scratch")
            arcpy.AddMessage(arcpy.GetMessages())
        else:
            arcpy.AddMessage(f"Scratch Folder: {new_project_folder} exists")
        if not arcpy.Exists(rf"{home_folder}\{new_project_folder}\Scratch\scratch.gdb"):
            arcpy.AddMessage("Creating the Scratch GDB")
            arcpy.management.CreateFileGDB(rf"{home_folder}\{new_project_folder}\Scratch", "scratch")
            arcpy.AddMessage(arcpy.GetMessages())
        else:
            arcpy.AddMessage("Scratch GDB Exists")
        for _project_folder in project_folders.split(";"):
            if not arcpy.Exists(rf"{home_folder}\{new_project_folder}\{_project_folder}"):
                arcpy.AddMessage(f"Creating Folder: {_project_folder}")
                arcpy.management.CreateFolder(rf"{home_folder}\{new_project_folder}", _project_folder)
                arcpy.AddMessage(arcpy.GetMessages())
            else:
                arcpy.AddMessage(f"Folder: '{_project_folder}' Exists")
            del _project_folder
        if not arcpy.Exists(rf"{home_folder}\{new_project_folder}\{new_project_folder}.aprx"):
            aprx.saveACopy(rf"{home_folder}\{new_project_folder}\{new_project_folder}.aprx")
            arcpy.AddMessage(arcpy.GetMessages())
        else:
            pass

        _aprx = arcpy.mp.ArcGISProject(rf"{home_folder}\{new_project_folder}\{new_project_folder}.aprx")
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
        databases.append({"databasePath": rf"{home_folder}\{new_project_folder}\{new_project_folder}.gdb", "isDefaultDatabase": True})
        _aprx.updateDatabases(databases)
        arcpy.AddMessage(f"Databases: {databases}")
        del databases
        _aprx.save()

        toolboxes = []
        toolboxes.append({"toolboxPath": rf"{home_folder}\DisMAP.atbx", "isDefaultToolbox": True})
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
        #raise SystemExit
    except SystemExit:
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
        #raise SystemExit
    except Exception:
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
        #raise SystemExit
    except:  # noqa: E722  # noqa: E722
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
        #raise SystemExit
    else:
        pass
        return True
    finally:
        pass
if __name__ == "__main__":
    try:
        base_project_folder = arcpy.GetParameterAsText(0)
        new_project_folder  = arcpy.GetParameterAsText(1)
        project_folders     = arcpy.GetParameterAsText(2)

        if not base_project_folder:
            base_project_folder = rf"{os.path.expanduser('~')}\Documents\ArcGIS\Projects\DisMAP\ArcGIS-Analysis-Python"
        else:
            pass

        if not new_project_folder:
            new_project_folder = "February 1 2026"
        else:
            pass

        if not project_folders:
            project_folders = "CRFs;CSV_Data;Dataset_Shapefiles;Images;Layers;Metadata_Export;Publish"
        else:
            pass

        script_tool(base_project_folder, new_project_folder, project_folders)

        arcpy.SetParameterAsText(3, "Result")

        del base_project_folder, new_project_folder, project_folders

    except:  # noqa: E722
        #Gets non-tool errors
        line, filename, err = trace()
        arcpy.AddError("Python error on " + line + " of " + filename)
        arcpy.AddError(err)
