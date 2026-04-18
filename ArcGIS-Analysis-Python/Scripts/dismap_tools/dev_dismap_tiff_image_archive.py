#---------------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      john.f.kennedy
#
# Created:     22/12/2025
# Copyright:   (c) john.f.kennedy 2025
# Licence:     <your licence>
#---------------------------------------------------------------------------------------
import zipfile
import os
import sys
import traceback
import inspect

import arcpy

def trace():
    import sys, traceback  # noqa: E401
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    line = tbinfo.split(", ")[1]
    filename = sys.path[0] + os.sep + "test.py"
    synerror = traceback.format_exc().splitlines()[-1]
    return line, filename, synerror

def zip_folder(folder_path="", archive_folder=""):
    """
    Creates a zip archive of a given folder and its contents.

    Args:
        folder_path (str): The path to the folder to be archived.
    """
    try:
        output_zip_path = rf"{archive_folder}\{os.path.basename(folder_path)}.zip"
        #arcpy.AddMessage(output_zip_path)
        arcpy.AddMessage(f"\t\t\t\t../{'/'.join(output_zip_path.split(os.sep)[-3:])}")

        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Calculate the relative path within the zip archive
                    arcname = os.path.relpath(file_path, folder_path)
                    #arcpy.AddMessage(arcname)
                    zipf.write(file_path, arcname)
                for dir_name in dirs:
                    # Add empty directories to the archive
                    dir_path = os.path.join(root, dir_name)
                    arcname = os.path.relpath(dir_path, folder_path)
                    #arcpy.AddMessage(arcname)
                    # Ensure directory entries end with a slash in the archive
                    if not arcname.endswith('/'):
                        arcname += '/'
                    zipf.writestr(zipfile.ZipInfo(arcname), '')


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
        sys.exit()
        return False
    else:
        return True

def main(base_folder="", versions="", archive_folder=""):
    try:
        import dismap_tools
        arcpy.AddMessage(f"Home Folder: {os.path.basename(base_folder)} in '{inspect.stack()[0][3]}'")
        arcpy.AddMessage(f"Versions: {', '.join(versions)} in '{inspect.stack()[0][3]}'")

        for version in versions:
            image_folder = rf"{base_folder}\{version}\Images"
            _archive_folder = os.path.join(archive_folder, f"DisMAP_{dismap_tools.date_code(version)}", "results\\raster")
            #arcpy.AddMessage(f"\tImage Folder: {os.path.basename(image_folder)} in '{inspect.stack()[0][3]}'")
            arcpy.AddMessage(f"\tImage Folder: {os.path.basename(image_folder)}")
            arcpy.AddMessage(f"\t\tArchive Folder: {os.path.basename(_archive_folder)}")

            for entry in os.scandir(image_folder):
                if entry.is_dir():
                    arcpy.AddMessage(f"\t\t\tInput Folder: {os.path.basename(entry.path)}")
                    zip_folder(entry.path, _archive_folder)
                else:
                    pass
                del entry
            del image_folder, version, _archive_folder

        # Delete Declared Varibales
        # Delete Functions Parameters
        del base_folder, versions, archive_folder
        # Imports
        del dismap_tools

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
        base_folder    = arcpy.GetParameterAsText(0)
        versions       = arcpy.GetParameterAsText(1)
        archive_folder = arcpy.GetParameterAsText(2)

        if not base_folder:
            base_folder = os.path.join(os.path.expanduser('~'), "Documents\\ArcGIS\\Projects\\DisMap\\ArcGIS-Analysis-Python")
        else:
            arcpy.AddMessage(f"Home Folder: {os.path.basename(base_folder)}")

        if not versions:
            #versions = ["April 1 2023", "July 1 2024", "August 1 2025",]
            #versions = ["April 1 2023"]
            versions = ["February 1 2026"]
        else:
            arcpy.AddMessage(f"Versions: {', '.join(versions)}")

        if not archive_folder:
            archive_folder = os.path.join(os.path.expanduser('~'), "Documents\\ArcGIS\\Projects\\DisMap\\ArcGIS-Analysis-Python\\NCEI Archive")
        else:
            arcpy.AddMessage(f"Home Folder: {os.path.basename(base_folder)}")

        result = main(base_folder=base_folder, versions=versions, archive_folder=archive_folder)

        if result:
            arcpy.SetParameterAsText(3, result)
        del result

        # Clean-up declared variables
        del base_folder, versions, archive_folder

    except:  # noqa: E722
        traceback.print_exc()
    else:
        pass
    finally:
        sys.exit()