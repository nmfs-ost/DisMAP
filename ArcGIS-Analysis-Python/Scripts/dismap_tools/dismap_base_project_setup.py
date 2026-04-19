# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        dismap.py
# Purpose:     Common DisMAP functions
#
# Author:      john.f.kennedy
#
# Created:     12/01/2024
# Copyright:   (c) john.f.kennedy 2024
# Licence:     <your licence>
# -------------------------------------------------------------------------------
import os
import sys  # built-ins first

import arcpy  # third-parties second  # noqa: F401

def trace():
    import sys, traceback  # noqa: E401
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    line = tbinfo.split(", ")[1]
    filename = sys.path[0] + os.sep + "test.py"
    synerror = traceback.format_exc().splitlines()[-1]
    return line, filename, synerror

def script_tool(base_project_folder="", base_project_folders=""):
    try:
        from time import gmtime, localtime, strftime, time
        # Set a start time so that we can see how log things take
        start_time = time()
        arcpy.AddMessage(f"{'-' * 80}")
        arcpy.AddMessage(f"Python Script:  {os.path.basename(__file__)}")
        #arcpy.AddMessage(f"Location:       ../{'/'.join(__file__.split(os.sep)[-4:])}")
        arcpy.AddMessage(f"Python Version: {sys.version}")
        arcpy.AddMessage(f"Environment:    {os.path.basename(sys.exec_prefix)}")
        arcpy.AddMessage(f"{'-' * 80}\n")

        arcpy.AddMessage(base_project_folder)

        arcpy.env.workspace = base_project_folder

        #for folder in arcpy.ListWorkspaces("*", "Folder"):
        #    arcpy.AddMessage(os.path.basename(folder))
        #    del folder

        for project_folder in base_project_folders.split(";"):
            project_folder_path = os.path.abspath(os.path.join(base_project_folder, f"{project_folder}"))
            if not os.path.isdir(project_folder_path):
                os.makedirs(project_folder_path)
            else:
                pass
            del project_folder_path
            del project_folder

        # Set varaibales

        # Declared Varaiables
        # Imports
        # Function Parameters
        del base_project_folder, base_project_folders

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        arcpy.AddMessage(f"\n{'-' * 80}")
        arcpy.AddMessage(f"Python script: {os.path.basename(__file__)}\nCompleted: {strftime('%a %b %d %I:%M %p', localtime())}")
        arcpy.AddMessage(u"Elapsed Time {0} (H:M:S)".format(strftime("%H:%M:%S", gmtime(elapse_time))))
        arcpy.AddMessage(f"{'-' * 80}")
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
    except:# noqa: E722
        #Gets non-tool errors
        line, filename, err = trace()
        arcpy.AddError("Python error on " + line + " of " + filename)
        arcpy.AddError(err)
        return False
    else:
        return True

if __name__ == '__main__':
    try:
        base_project_folder  = arcpy.GetParameterAsText(0)
        base_project_folders = arcpy.GetParameterAsText(1)

        if not base_project_folder:
            base_project_folder = rf"{os.path.expanduser('~')}\Documents\ArcGIS\Projects\DisMap\ArcGIS-Analysis-Python"
        else:
            pass

        if not base_project_folders:
            base_project_folders = "Bathymetry;Dataset Shapefiles;Initial Data"
        else:
            pass

        script_tool(base_project_folder, base_project_folders)
        arcpy.SetParameterAsText(3, "Result")

        del base_project_folder, base_project_folders

    except:  # noqa: E722
        #Gets non-tool errors
        line, filename, err = trace()
        arcpy.AddError("Python error on " + line + " of " + filename)
        arcpy.AddError(err)
    else:
        pass