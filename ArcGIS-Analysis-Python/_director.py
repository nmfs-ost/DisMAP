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
import os, sys  # built-ins first
import traceback
import importlib
import inspect

import arcpy  # third-parties second

sys.path.append(os.path.dirname(__file__))

def line_info(msg):
    f = inspect.currentframe()
    i = inspect.getframeinfo(f.f_back)
    arcpy.AddMessage(f"Script: {os.path.basename(i.filename)}\n\tNear Line: {i.lineno}\n\tFunction: {i.function}\n\tMessage: {msg}")

def main(project=""):
    try:
        base_project_folder = os.path.dirname(os.path.dirname(__file__))

        #
        # Step 0 - create an ArcGIS Project
        #

        # ##########################################################################
        # Step 1 - update ArcGIS Project with the databases and folders for a given
        # ##########################################################################
        # project version
        DisMapProjectSetup = False
        if DisMapProjectSetup:

            import dismap_project_setup

            base_project_file = rf"{base_project_folder}\DisMAP.aprx"

            dismap_project_setup.project_folders(base_project_file, project)

            del dismap_project_setup, base_project_file

        del DisMapProjectSetup

        # ##########################################################################
        # Step 2 - zip and unzip the region shapefiles and the CVS data for a given
        # ##########################################################################
        # project version
        ZipAndUnzipCsvData = False
        if ZipAndUnzipCsvData:

            import zip_and_unzip_csv_data

            # If "project" is the same, then an archieve file is created.
            # If different, then the archieve is created and upzipped in the new
            # location
            # In Data Path

            in_data_path  = rf"{base_project_folder}\{project}\CSV Data"

            out_data_path = rf"{base_project_folder}\{project}\CSV Data"

            selected_files = ["AI_IDW.csv", "Datasets.csv", "EBS_IDW.csv",
                              "ENBS_IDW.csv", "GMEX_IDW.csv",
                              "GOA_IDW.csv", "HI_IDW.csv", "NBS_IDW.csv",
                              "NEUS_FAL_IDW.csv", "NEUS_SPR_IDW.csv",
                              "SEUS_FAL_IDW.csv", "SEUS_SPR_IDW.csv",
                              "SEUS_SUM_IDW.csv", "Species_Filter.csv",
                              "WC_ANN_IDW.csv", "WC_GLMME.csv",
                              "WC_TRI_IDW.csv", "field_definitions.json",
                              "metadata_dictionary.json", "table_definitions.json"
                             ]
            selected_files = ";".join(selected_files)

            zip_and_unzip_csv_data.main(in_data_path, out_data_path, selected_files)

            del in_data_path, out_data_path, selected_files
            del zip_and_unzip_csv_data
        del ZipAndUnzipCsvData

        ZipAndUnzipShapefileData = False
        if ZipAndUnzipShapefileData:

            import zip_and_unzip_shapefile_data

            # If "project" is the same, then an archieve file is created.
            # If different, then the archieve is created and upzipped in the new
            # location

            in_data_path  = rf"{base_project_folder}\{project}\CSV Data"

            out_data_path = rf"{base_project_folder}\{project}\Dataset Shapefiles"

            selected_files = ['AI_IDW_Region.shp', 'EBS_IDW_Region.shp',
                              'ENBS_IDW_Region.shp', 'GMEX_IDW_Region.shp',
                              'GOA_IDW_Region.shp', 'HI_IDW_Region.shp',
                              'NBS_IDW_Region.shp', 'NEUS_FAL_IDW_Region.shp',
                              'NEUS_SPR_IDW_Region.shp', 'SEUS_FAL_IDW_Region.shp',
                              'SEUS_SPR_IDW_Region.shp', 'SEUS_SUM_IDW_Region.shp',
                              'WC_ANN_IDW_Region.shp', 'WC_GFDL_Region.shp',
                              'WC_GLMME_Region.shp', 'WC_TRI_IDW_Region.shp',]
            selected_files = ";".join(selected_files)

            zip_and_unzip_shapefile_data.main(in_data_path, out_data_path, selected_files)

            del in_data_path, out_data_path, selected_files
            del zip_and_unzip_shapefile_data
        del ZipAndUnzipShapefileData

    # ###--->>>

        # Write script that checks CSV file headers and updates as necessary

    # ###--->>>

        # ##########################################################################
        # Step 3 - Create base bathymetry datasets in project folder
        # ##########################################################################
        CreateBaseBathymetry = False
        if CreateBaseBathymetry:

            from create_base_bathymetry import create_alasaka_bathymetry, create_hawaii_bathymetry, gebco_bathymetry

            project_gdb = rf"{base_project_folder}\{project}\{project}.gdb"

            # Process base Alasak bathymetry
            create_alasaka_bathymetry(project_gdb)

            # Process base Hawaii bathymetry
            create_hawaii_bathymetry(project_gdb)

            # Process base GEBCO bathymetry
            gebco_bathymetry(project_gdb)

            del project_gdb
            del create_alasaka_bathymetry, create_hawaii_bathymetry, gebco_bathymetry
        del CreateBaseBathymetry

        # ##########################################################################
        # Step 4 - import the "Datasets" and the "Species_Filter" table into the
        # ##########################################################################
        # project GDB
        ImportDatasetsSpeciesFilterCsvData = False
        if ImportDatasetsSpeciesFilterCsvData:

            from import_datasets_species_filter_csv_data import update_datecode, worker

            project_gdb        = rf"{base_project_folder}\{project}\{project}.gdb"
            datasets_csv       = rf"{base_project_folder}\{project}\CSV Data\Datasets.csv"
            species_filter_csv = rf"{base_project_folder}\{project}\CSV Data\Species_Filter.csv"

            # Update DateCode
            update_datecode(csv_file=datasets_csv, project=project)

            # Datasets CSV File
            worker(project_gdb=project_gdb, csv_file=datasets_csv)

            # Species Filter CSV File
            worker(project_gdb=project_gdb, csv_file=species_filter_csv)

            del project_gdb, datasets_csv, species_filter_csv
            del update_datecode, worker
        del ImportDatasetsSpeciesFilterCsvData

        # ##########################################################################
        # Step 5 - Create regions from shapefiles
        # ##########################################################################
        CreateRegionsFromShapefiles = False
        if CreateRegionsFromShapefiles:

            from create_regions_from_shapefiles_director import director

            project_gdb = rf"{base_project_folder}\{project}\{project}.gdb"

            director(project_gdb=project_gdb, Sequential=False, table_names=[])

            del project_gdb
            del director
        del CreateRegionsFromShapefiles

        # ##########################################################################
        # Step 6 - Create region fishnets
        # ##########################################################################
        CreateRegionFishnets = False
        if CreateRegionFishnets:

            from create_region_fishnets_director import director

            project_gdb = rf"{base_project_folder}\{project}\{project}.gdb"

            director(project_gdb=project_gdb, Sequential=False, table_names=["NBS_IDW", "ENBS_IDW", "HI_IDW", "SEUS_FAL_IDW", "SEUS_SPR_IDW", "SEUS_SUM_IDW",])

            director(project_gdb=project_gdb, Sequential=False, table_names=["WC_TRI_IDW", "GMEX_IDW", "AI_IDW", "GOA_IDW", "WC_ANN_IDW", "NEUS_FAL_IDW",])

            director(project_gdb=project_gdb, Sequential=False, table_names=["NEUS_SPR_IDW", "EBS_IDW", "WC_GLMME"])

            # Debug
            #director(project_gdb=project_gdb, Sequential=False, table_names=["WC_GLMME",])

            #director(project_gdb=project_gdb, Sequential=False, table_names=[])

            del project_gdb
            del director
        del CreateRegionFishnets

        # ##########################################################################
        # Step 7 - Create Region Bathymetry
        # ##########################################################################
        CreateRegionBathymetry = False
        if CreateRegionBathymetry:

            from create_region_bathymetry_director import director

            project_gdb = rf"{base_project_folder}\{project}\{project}.gdb"

            director(project_gdb=project_gdb, Sequential=False, table_names=["NBS_IDW", "ENBS_IDW", "HI_IDW", "SEUS_FAL_IDW", "SEUS_SPR_IDW", "SEUS_SUM_IDW",])

            director(project_gdb=project_gdb, Sequential=False, table_names=["WC_TRI_IDW", "GMEX_IDW", "AI_IDW", "GOA_IDW", "WC_ANN_IDW", "NEUS_FAL_IDW",])

            director(project_gdb=project_gdb, Sequential=False, table_names=["NEUS_SPR_IDW", "EBS_IDW", "WC_GLMME"])

            del project_gdb
            del director
        del CreateRegionBathymetry

        # ##########################################################################
        # Step 8 - create_region_sample_locations_director
        # ##########################################################################
        CreateRegionSampleLocations = False
        if CreateRegionSampleLocations:

            from create_region_sample_locations_director import director

            project_gdb = rf"{base_project_folder}\{project}\{project}.gdb"

            Test = False
            if Test:
                director(project_gdb=project_gdb, Sequential=False, table_names=["WC_TRI_IDW", "AI_IDW"])
            del Test

            director(project_gdb=project_gdb, Sequential=False, table_names=["NBS_IDW", "ENBS_IDW", "HI_IDW",])

            director(project_gdb=project_gdb, Sequential=False, table_names=["SEUS_FAL_IDW", "SEUS_SPR_IDW", "SEUS_SUM_IDW",])

            director(project_gdb=project_gdb, Sequential=False, table_names=["WC_TRI_IDW", "GMEX_IDW", "AI_IDW",])

            director(project_gdb=project_gdb, Sequential=False, table_names=["GOA_IDW", "WC_ANN_IDW", "NEUS_FAL_IDW",])

            director(project_gdb=project_gdb, Sequential=False, table_names=["NEUS_SPR_IDW", "EBS_IDW", "WC_GLMME"])

            del project_gdb
            del director
        del CreateRegionSampleLocations

        # ##########################################################################
        # Step 9 - Create species year image name table
        # ##########################################################################
        CreateSpeciesYearImageNameTable = False
        if CreateSpeciesYearImageNameTable:

            from create_species_year_image_name_table_director import director, process_image_name_tables

            project_gdb = rf"{base_project_folder}\{project}\{project}.gdb"

            director(project_gdb=project_gdb, Sequential=False, table_names=[])

            # Combine Image Name Tables
            #process_image_name_tables(project_gdb=project_gdb, project=project)

            del project_gdb
            del director, process_image_name_tables
        del CreateSpeciesYearImageNameTable

        # ##########################################################################
        # Step 10 - Create Rasters
        # ##########################################################################
        CreateRasters = False
        if CreateRasters:

            from create_rasters_director import director

            project_gdb = rf"{base_project_folder}\{project}\{project}.gdb"

            results = []

##            result = director(project_gdb=project_gdb, Sequential=False, table_names=["NBS_IDW", "ENBS_IDW", "HI_IDW",])
##            results.extend(result); del result
##
##            result = director(project_gdb=project_gdb, Sequential=False, table_names=["SEUS_FAL_IDW", "SEUS_SPR_IDW", "SEUS_SUM_IDW",])
##            results.extend(result); del result

##            result = director(project_gdb=project_gdb, Sequential=False, table_names=["WC_TRI_IDW", "AI_IDW", "GMEX_IDW",])
##            results.extend(result); del result

##            result = director(project_gdb=project_gdb, Sequential=False, table_names=["GOA_IDW", "WC_ANN_IDW", "NEUS_FAL_IDW",])
##            results.extend(result); del result
##
##            result = director(project_gdb=project_gdb, Sequential=False, table_names=["NEUS_SPR_IDW", "EBS_IDW",])
##            results.extend(result); del result

            #result = director(project_gdb=project_gdb, Sequential=False, table_names=["WC_GLMME",])
            #results.extend(result); del result

            del project_gdb
            del director
        del CreateRasters

        # ##########################################################################
        # Step 11 - Create Indicators Table
        # ##########################################################################
        CreateIndicatorsTable = False
        if CreateIndicatorsTable:

            from create_indicators_table_director import director, process_indicator_tables

            project_gdb = rf"{base_project_folder}\{project}\{project}.gdb"

            Test = False
            if Test:
                # Debug
                director(project_gdb=project_gdb, Sequential=False, table_names=["GMEX_IDW",])
                # Debug
            del Test

            director(project_gdb=project_gdb, Sequential=False, table_names=["NBS_IDW", "ENBS_IDW",])

            director(project_gdb=project_gdb, Sequential=False, table_names=["HI_IDW", "SEUS_FAL_IDW",])

            director(project_gdb=project_gdb, Sequential=False, table_names=["SEUS_SPR_IDW", "SEUS_SUM_IDW",])

            director(project_gdb=project_gdb, Sequential=False, table_names=["WC_TRI_IDW", "GMEX_IDW",])

            director(project_gdb=project_gdb, Sequential=False, table_names=["AI_IDW", "GOA_IDW",])

            director(project_gdb=project_gdb, Sequential=False, table_names=["WC_ANN_IDW", "NEUS_FAL_IDW",])

            director(project_gdb=project_gdb, Sequential=False, table_names=["NEUS_SPR_IDW", "EBS_IDW",])

                # Not yet
                #result = director(project_gdb=project_gdb, Sequential=False, table_names=["WC_GLMME",])
                #results.extend(result); del result

            # Combine Indicator Tables
            process_indicator_tables(project_gdb=project_gdb, project=project)
            del project_gdb
            del director, process_indicator_tables
        del CreateIndicatorsTable

        # dataset_comparison - rasters
        # dataset_comparison - feature classes
        # dataset_comparison - tables

        # Step 12 - Create Species Richness Rasters
        CreateSpeciesRichnessRasters = False
        if CreateSpeciesRichnessRasters:

            from create_species_richness_rasters_director import director

            project_gdb = rf"{base_project_folder}\{project}\{project}.gdb"

            # Debug
            director(project_gdb=project_gdb, Sequential=False, table_names=["GMEX_IDW",])
            # Debug

    ##            director(project_gdb=project_gdb, Sequential=False, table_names=["NBS_IDW", "ENBS_IDW",])
    ##
    ##            director(project_gdb=project_gdb, Sequential=False, table_names=["HI_IDW", "SEUS_FAL_IDW",])
    ##
    ##            director(project_gdb=project_gdb, Sequential=False, table_names=["SEUS_SPR_IDW", "SEUS_SUM_IDW",])
    ##
    ##            director(project_gdb=project_gdb, Sequential=False, table_names=["WC_TRI_IDW", "GMEX_IDW",])
    ##
    ##            director(project_gdb=project_gdb, Sequential=False, table_names=["AI_IDW", "GOA_IDW",])
    ##
    ##            director(project_gdb=project_gdb, Sequential=False, table_names=["WC_ANN_IDW", "NEUS_FAL_IDW",])
    ##
    ##            director(project_gdb=project_gdb, Sequential=False, table_names=["NEUS_SPR_IDW", "EBS_IDW",])

            del project_gdb
            del director
        del CreateSpeciesRichnessRasters

        # create_mosaics_director
        # Step 12 - Create Mosaics
        CreateMosaics = False
        if CreateMosaics:

            from create_mosaics_director import director

            project_gdb = rf"{base_project_folder}\{project}\{project}.gdb"

            # Debug
            #director(project_gdb=project_gdb, Sequential=False, table_names=["GMEX_IDW",])
            # Debug

            director(project_gdb=project_gdb, Sequential=False, table_names=["NBS_IDW", "ENBS_IDW",])

            director(project_gdb=project_gdb, Sequential=False, table_names=["HI_IDW", "SEUS_FAL_IDW",])

            director(project_gdb=project_gdb, Sequential=False, table_names=["SEUS_SPR_IDW", "SEUS_SUM_IDW",])

            director(project_gdb=project_gdb, Sequential=False, table_names=["WC_TRI_IDW", "GMEX_IDW",])

            director(project_gdb=project_gdb, Sequential=False, table_names=["AI_IDW", "GOA_IDW",])

            director(project_gdb=project_gdb, Sequential=False, table_names=["WC_ANN_IDW", "NEUS_FAL_IDW",])

            director(project_gdb=project_gdb, Sequential=False, table_names=["NEUS_SPR_IDW", "EBS_IDW",])

            del project_gdb
            del director
        del CreateMosaics

    # publish_to_portal_director

        del project

        results = True

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
            leave_out_keys = ["leave_out_keys", "remaining_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys
            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
        except:
            raise SystemExit(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

if __name__ == '__main__':
    try:
        # Import this Python module
        import _director
        importlib.reload(_director)

        print(f"{'-' * 90}")
        print(f"Python Script:  {os.path.basename(__file__)}")
        print(f"Location:       {os.path.dirname(__file__)}")
        print(f"Python Version: {sys.version} Environment: {os.path.basename(sys.exec_prefix)}")
        print(f"{'-' * 90}\n")

        # Tested on 5/20/2024 -- PASSED
        #project = "May 1 2024"
        project = "July 1 2024"

        main(project=project)

        del project

        from time import localtime, strftime

        print(f"\n{'-' * 90}")
        print(f"Python script: {os.path.basename(__file__)} successfully completed {strftime('%a %b %d %I:%M %p', localtime())}")
        print(f"{'-' * 90}")
        del localtime, strftime

    except:
        traceback.print_exc()
    else:
        import inspect
        leave_out_keys = ["leave_out_keys", "remaining_keys", "inspect"]
        leave_out_keys.extend([name for name, obj in inspect.getmembers(sys.modules[__name__]) if inspect.isfunction(obj) or inspect.ismodule(obj)])
        remaining_keys = [key for key in locals().keys() if not key.startswith("__") and key not in leave_out_keys]
        if remaining_keys:
            print(f"Remaining Keys: ##--> '{', '.join(remaining_keys)}' <--##")
        del leave_out_keys, remaining_keys
    finally:
        pass