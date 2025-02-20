# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        zip_and_unzip_csv_data
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

def zip_data(source_folder, selected_files, out_zip_file):
    try:
        from zipfile import ZipFile

        os.chdir(source_folder)

        arcpy.AddMessage(f"Zipping up files into: '{os.path.basename(out_zip_file)}'")

        selected_files = selected_files.split(";")

        source_files = [f for f in os.listdir(source_folder) if f in selected_files]

        with ZipFile(out_zip_file, mode="w") as archive:
            for source_file in source_files:
                archive.write(source_file)
                del source_file
        del archive

        arcpy.AddMessage(f"Done zipping up files into '{os.path.basename(out_zip_file)}'")

        results = out_zip_file
        del out_zip_file

        # Imports
        del ZipFile
        # Passed parameters
        del source_folder, selected_files, source_files

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

def un_zip_data(source_zip_file, out_data_path):
    try:
        # zipFile import
        from zipfile import ZipFile

        # Change Directory
        os.chdir(out_data_path)

        arcpy.AddMessage(f"Un-Zipping files from {os.path.basename(source_zip_file)}")

        with ZipFile(source_zip_file, mode="r") as archive:
            for file in archive.namelist():
                #if file.endswith(".csv"):
                #   archive.extract(file, ".")
                archive.extract(file, ".")
                del file
        del archive

        arcpy.AddMessage(f"Done Un-Zipping files from {os.path.basename(source_zip_file)}")

        results = out_data_path
        del out_data_path
        # Declared variable
        del source_zip_file, ZipFile

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

def main(in_data_path, out_data_path, selected_files):
    try:
        from dismap import date_code

        in_project = os.path.basename(os.path.dirname(in_data_path))
        in_version = date_code(in_project)
        in_zip_file = rf"{in_data_path}\CVS Data {in_version}.zip"

        out_project = os.path.basename(os.path.dirname(out_data_path))
        out_version = date_code(out_project)
        out_zip_file = rf"{out_data_path}\CVS Data {out_version}.zip"

        arcpy.AddMessage(in_project)
        arcpy.AddMessage(in_zip_file)
        arcpy.AddMessage(out_zip_file)

        outZipFile = zip_data(in_data_path, selected_files, out_zip_file)
        un_zip_data(outZipFile, out_data_path)

        del in_project, in_version, in_zip_file
        del out_project, out_version, out_zip_file, outZipFile
        # Imports
        del date_code
        # Function parameters
        del in_data_path, out_data_path, selected_files

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

if __name__ == "__main__":
    try:
        #import zip_and_unzip_csv_data
        #importlib.reload(zip_and_unzip_csv_data)

        print(f"{'-' * 90}")
        print(f"Python Script:  {os.path.basename(__file__)}")
        print(f"Location:       {os.path.dirname(__file__)}")
        print(f"Python Version: {sys.version} Environment: {os.path.basename(sys.exec_prefix)}")
        print(f"{'-' * 90}\n")

        base_project_folder = os.path.dirname(os.path.dirname(__file__))

        #in_project = "July 1 2024"
        in_project = "December 1 2024"
        in_data_path = rf"{base_project_folder}\{in_project}\CSV Data"
        del in_project

        out_project = "December 1 2024"
        out_data_path = rf"{base_project_folder}\{out_project}\CSV Data"
        del out_project

        selected_files = ["AI_IDW.csv", "Datasets.csv", "EBS_IDW.csv",
                          "ENBS_IDW.csv", "GMEX_IDW.csv",
                          "GOA_IDW.csv", "HI_IDW.csv", "NBS_IDW.csv",
                          "NEUS_FAL_IDW.csv", "NEUS_SPR_IDW.csv",
                          "SEUS_FAL_IDW.csv", "SEUS_SPR_IDW.csv",
                          "SEUS_SUM_IDW.csv", "Species_Filter.csv",
                          "WC_ANN_IDW.csv", "WC_GFDL.csv", "WC_GLMME.csv",
                          "WC_TRI_IDW.csv", "field_definitions.json",
                          "metadata_dictionary.json", "table_definitions.json"
                         ]
        selected_files = ";".join(selected_files)

        main(in_data_path, out_data_path, selected_files)

        del in_data_path, out_data_path, selected_files
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
        remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
        if remaining_keys:
            arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[1][3]}': ##--> '{', '.join(remaining_keys)}' <--##")
        del leave_out_keys, remaining_keys
    finally:
        pass
