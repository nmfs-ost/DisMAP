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

def dis_map_archive_folders(home_folder="", versions="", archive_folder=""):
    try:
        import dismap_tools

        arcpy.env.overwriteOutput = True

        #arcpy.AddMessage(f"Home Folder: {os.path.basename(home_folder)} in '{inspect.stack()[0][3]}'")
        #arcpy.AddMessage(f"Versions: {', '.join(versions)} in '{inspect.stack()[0][3]}'")

        for version in versions:
            project_gdb = rf"{home_folder}\{version}\{version}.gdb"
            _archive_folder = os.path.join(archive_folder, f"DisMAP_{dismap_tools.date_code(version)}")
            #archive_gdb = rf"{_archive_folder}\DisMAP_{dismap_tools.date_code(version)}.gpkg"

            archive_folders = ["initial", "results/vector-tabular/metadata", "results/raster"]

            #arcpy.AddMessage(f"\tProject GDB: {os.path.basename(project_gdb)} in '{inspect.stack()[0][3]}'")
            #arcpy.AddMessage(f"\tProject GDB: {project_gdb}")
            #arcpy.AddMessage(f"\t\tArchive Folder: {_archive_folder}")
            for archiveFolder in archive_folders:
                archiveFolder_path = os.path.abspath(os.path.join(archive_folder, f"DisMAP_{dismap_tools.date_code(version)}", archiveFolder))
                #arcpy.AddMessage(f"\t\t\tFolder: {archiveFolder_path}")
                if not os.path.isdir(archiveFolder_path):
                    os.makedirs(archiveFolder_path)
                else:
                    pass
                pass

                del archiveFolder_path, archiveFolder
            del archive_folders

            del project_gdb, _archive_folder
            del version

        # Delete Declared Varibales
        # Delete Functions Parameters
        del home_folder, versions, archive_folder
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

def zip_folder(folder_path="", archive_folder=""):
    """
    Creates a zip archive of a given folder and its contents.

    Args:
        folder_path (str): The path to the folder to be archived.
    """
    output_zip_path = rf"{archive_folder}\{os.path.basename(folder_path)}.zip"

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


def main(home_folder="", versions="", archive_folder=""):
    try:
        import dismap_tools
        from arcpy import metadata as md

        arcpy.env.overwriteOutput = True

        dis_map_archive_folders(home_folder=home_folder, versions=versions, archive_folder=archive_folder)

        #archive_folders = ["initial", "results/vector-tabular/metadata", "results/raster"]
        #archiveFolder_path = os.path.abspath(os.path.join(archive_folder, f"DisMAP_{dismap_tools.date_code(version)}", archiveFolder))

        arcpy.AddMessage(f"Home Folder: {os.path.basename(home_folder)} in '{inspect.stack()[0][3]}'")
        arcpy.AddMessage(f"Versions: {', '.join(versions)} in '{inspect.stack()[0][3]}'")

        for version in versions:
            project_gdb = rf"{home_folder}\{version}\{version}.gdb"
            _archive_folder = os.path.abspath(os.path.join(archive_folder, f"DisMAP_{dismap_tools.date_code(version)}", "results/vector-tabular"))
            archive_gdb = os.path.abspath(rf"{_archive_folder}\DisMAP_{dismap_tools.date_code(version)}.gpkg")

            #arcpy.AddMessage(f"\tProject GDB: {os.path.basename(project_gdb)} in '{inspect.stack()[0][3]}'")
            arcpy.AddMessage(f"\tProject GDB: {os.path.basename(project_gdb)}")
            arcpy.AddMessage(f"\t\tArchive Folder: {os.path.basename(_archive_folder)}")

            arcpy.env.workspace = project_gdb

            arcpy.management.CreateSQLiteDatabase(out_database_name=archive_gdb, spatial_type="GEOPACKAGE")

            archive_tbs = [
            "DisMAP_Survey_Info",
            "Indicators",
            "SpeciesPersistenceIndicatorPercentileBin",
            "SpeciesPersistenceIndicatorTrend",
            "Species_Filter",
            ]
            # fc_md.exportMetadata("C:\\Users\\john.f.kennedy\\Documents\\ArcGIS\\Projects\\DisMAP\\ArcGIS-Analysis-Python\\NCEI Archive\fc_md.xml", "ISO19139_GML32", 'REMOVE_ALL_SENSITIVE_INFO')
            for tb in sorted([tb for tb in arcpy.ListTables("*") if tb in archive_tbs or tb.endswith("_IDW")]):
                arcpy.AddMessage(f"\t\t\tTable: {tb}")
                arcpy.management.Copy(rf"{project_gdb}\{tb}", rf"{archive_gdb}\{tb}")
                tb_md = md.Metadata(rf"{project_gdb}\{tb}")
                tb_md.exportMetadata(os.path.abspath(os.path.join(archive_folder, f"DisMAP_{dismap_tools.date_code(version)}", f"results/vector-tabular/metadata/{tb}.xml")), "ISO19139", "REMOVE_ALL_SENSITIVE_INFO")
                del tb_md

                del tb
            del archive_tbs

            archive_fcs = [
            "Regions",
            "Sample_Locations",
            ]

            for fc in sorted([fc for fc in arcpy.ListFeatureClasses("*") if any(fc.endswith(f"{f}") for f in archive_fcs)]):
                arcpy.AddMessage(f"\t\t\tFeature Class: {fc}")
                arcpy.management.Copy(rf"{project_gdb}\{fc}", rf"{archive_gdb}\{fc}")
                fc_md = md.Metadata(rf"{project_gdb}\{fc}")
                fc_md.exportMetadata(os.path.abspath(os.path.join(archive_folder, f"DisMAP_{dismap_tools.date_code(version)}", f"results/vector-tabular/metadata/{fc}.xml")), "ISO19139", "REMOVE_ALL_SENSITIVE_INFO")
                del fc_md

                del fc

            del project_gdb, _archive_folder, archive_gdb
            del version

        # Delete Declared Varibales
        # Delete Functions Parameters
        del home_folder, versions, archive_folder
        # Imports
        del dismap_tools, md

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
        home_folder    = arcpy.GetParameterAsText(0)
        versions       = arcpy.GetParameterAsText(1)
        archive_folder = arcpy.GetParameterAsText(2)

        if not home_folder:
            home_folder = os.path.join(os.path.expanduser('~'), "Documents\\ArcGIS\\Projects\\DisMap\\ArcGIS-Analysis-Python")
        else:
            arcpy.AddMessage(f"Home Folder: {os.path.basename(home_folder)}")

        if not versions:
            versions = ["February 1 2026"]
            #versions = ["April 1 2023", "July 1 2024", "August 1 2025", "February 1 2026"]
            #versions = ["July 1 2024", "August 1 2025",]
        else:
            arcpy.AddMessage(f"Versions: {', '.join(versions)}")

        if not archive_folder:
            archive_folder = os.path.join(os.path.expanduser('~'), "Documents\\ArcGIS\\Projects\\DisMap\\ArcGIS-Analysis-Python\\NCEI Archive")
        else:
            arcpy.AddMessage(f"Home Folder: {os.path.basename(home_folder)}")

        result = main(home_folder=home_folder, versions=versions, archive_folder=archive_folder)

        if result:
            arcpy.SetParameterAsText(3, result)
        else:
            pass
        del result

        # Clean-up declared variables
        del home_folder, versions, archive_folder

    except:  # noqa: E722
        #Gets non-tool errors
        line, filename, err = trace()
        arcpy.AddError("Python error on " + line + " of " + filename)
        arcpy.AddError(err)
    else:
        pass
