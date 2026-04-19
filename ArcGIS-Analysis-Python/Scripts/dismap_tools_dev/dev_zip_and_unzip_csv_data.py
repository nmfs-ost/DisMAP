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

def zip_data(source_folder, selected_files, out_zip_file):
    try:
        # Imports
        import copy
        from zipfile import ZipFile

        os.chdir(source_folder)

        print(f"Zipping up files into: '{os.path.basename(out_zip_file)}'")

        selected_files = selected_files.split(";")

        source_files = [f for f in os.listdir(source_folder) if f in selected_files]
        with ZipFile(out_zip_file, mode="w") as archive:
            for source_file in source_files:
                archive.write(source_file)
                del source_file
        del archive
        del source_files

        print(f"Done zipping up files into '{os.path.basename(out_zip_file)}'")

        __results = copy.deepcopy(out_zip_file)
        del out_zip_file

        # Imports
        del ZipFile, copy
        # Function parameters
        del source_folder, selected_files

    except:
        traceback.print_exc()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function at line number {inspect.stack()[0][2]}\n\t##--> '{', '.join(rk)}' <--##"); del rk
        return __results
    finally:
        if "__results" in locals().keys(): del __results

def un_zip_data(source_zip_file, out_data_path):
    try:
        # Imports
        import copy
        from zipfile import ZipFile

        # Change Directory
        os.chdir(out_data_path)

        print(f"Un-Zipping files from {os.path.basename(source_zip_file)}")

        with ZipFile(source_zip_file, mode="r") as archive:
            for file in archive.namelist():
                #if file.endswith(".csv"):
                #   archive.extract(file, ".")
                archive.extract(file, ".")
                del file
        del archive

        print(f"Done Un-Zipping files from {os.path.basename(source_zip_file)}")

        __results = copy.deepcopy(out_data_path)
        del out_data_path
        # Declared variable

        # Imports
        del ZipFile, copy
        # Function Parameters
        del source_zip_file

    except:
        traceback.print_exc()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function at line number {inspect.stack()[0][2]}\n\t##--> '{', '.join(rk)}' <--##"); del rk
        return __results
    finally:
        if "__results" in locals().keys(): del __results

def main(in_data_path, out_data_path, selected_files):
    try:
        from time import gmtime, localtime, strftime, time
        # Set a start time so that we can see how log things take
        start_time = time()
        print(f"{'-' * 80}")
        print(f"Python Script:  {os.path.basename(__file__)}")
        print(f"Location:       ..\Documents\ArcGIS\Projects\..\{os.path.basename(os.path.dirname(__file__))}\{os.path.basename(__file__)}")
        print(f"Python Version: {sys.version}")
        print(f"Environment:    {os.path.basename(sys.exec_prefix)}")
        print(f"{'-' * 80}\n")

        # Imports
        from dev_dismap_tools import date_code

        in_project = os.path.basename(os.path.dirname(in_data_path))
        in_version = date_code(in_project)
        in_zip_file = rf"{in_data_path}\CSV Data {in_version}.zip"

        out_project = os.path.basename(os.path.dirname(out_data_path))
        out_version = date_code(out_project)
        out_zip_file = rf"{out_data_path}\CSV Data {out_version}.zip"

        print(in_project)
        print(os.path.basename(in_zip_file))
        print(os.path.basename(out_zip_file))

        outZipFile = zip_data(in_data_path, selected_files, out_zip_file)
        un_zip_data(outZipFile, out_data_path)

        del in_project, in_version, in_zip_file
        del out_project, out_version, out_zip_file, outZipFile
        # Imports
        del date_code
        # Function parameters
        del in_data_path, out_data_path, selected_files

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time

        print(f"\n{'-' * 80}")
        print(f"Python script: {os.path.basename(__file__)}\nCompleted: {strftime('%a %b %d %I:%M %p', localtime())}")
        print(u"Elapsed Time {0} (H:M:S)".format(strftime("%H:%M:%S", gmtime(elapse_time))))
        print(f"{'-' * 80}")
        del elapse_time, end_time, start_time
        del gmtime, localtime, strftime, time

    except Exception:
        pass
    except:
        traceback.print_exc()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function at line number {inspect.stack()[0][2]}\n\t##--> '{', '.join(rk)}' <--##"); del rk
        return True
    finally:
        pass

if __name__ == "__main__":
    try:
        # Append the location of this scrip to the System Path
        #sys.path.append(os.path.dirname(__file__))
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))

        # Imports
        import dev_zip_and_unzip_csv_data
        importlib.reload(dev_zip_and_unzip_csv_data)

        base_project_folder = rf"{os.path.dirname(os.path.dirname(__file__))}"

        #in_project = "July 1 2024"
        in_project = "December 1 2024"
        in_data_path = rf"{base_project_folder}\{in_project}\CSV Data"
        del in_project

        #out_project = "December 1 2024"
        out_project = "June 1 2025"
        out_data_path = rf"{base_project_folder}\{out_project}\CSV Data"
        del out_project

        selected_files = ["AI_IDW.csv",   "Datasets.csv", "DisMAP_Survey_Info.csv",
                          "EBS_IDW.csv",  "ENBS_IDW.csv", "field_definitions.json",
                          "GMEX_IDW.csv", "GOA_IDW.csv",  "HI_IDW.csv",
                          "metadata_dictionary.json", "NBS_IDW.csv",
                          "NEUS_FAL_IDW.csv", "NEUS_SPR_IDW.csv",
                          "SEUS_FAL_IDW.csv", "SEUS_SPR_IDW.csv",
                          "SEUS_SUM_IDW.csv", "Species_Filter.csv",
                          "table_definitions.json", "WC_ANN_IDW.csv",
                          "WC_GFDL.csv", "WC_GLMME.csv", "WC_TRI_IDW.csv",
                         ]

        selected_files = ";".join(selected_files)

        main(in_data_path, out_data_path, selected_files)

        del in_data_path, out_data_path, selected_files
        del base_project_folder

        # Imports
        del dev_zip_and_unzip_csv_data

    except:
        traceback.print_exc()
    else:
        pass
    finally:
        pass
