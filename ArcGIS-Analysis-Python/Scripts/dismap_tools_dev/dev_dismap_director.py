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

def main(project_gdb=""):
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

        # Set varaibales
        project_folder      = os.path.dirname(project_gdb)
        project_name        = os.path.basename(project_folder)
        base_project_folder = os.path.dirname(project_folder)

        #
        # Step 0 - create an ArcGIS Project
        #

        # ##########################################################################
        # Step 1 - update ArcGIS Project with the databases and folders for a given
        # ##########################################################################
        # project version
        DisMapProjectSetup = False
        if DisMapProjectSetup:
            import dev_dismap_project_setup
            base_project_file = rf"{base_project_folder}\DisMAP.aprx"
            dev_dismap_project_setup.project_folders(base_project_file, project_name)
            # Declared variables
            del base_project_file
            #Imports
            del dev_dismap_project_setup
        else:
            pass
        del DisMapProjectSetup
        # ##########################################################################
        # Step 2 - zip and unzip the region shapefiles and the CSV data for a given
        # ##########################################################################
        # project version
        ZipAndUnzipCsvData = False
        if ZipAndUnzipCsvData:
            # Imports
            import dev_zip_and_unzip_csv_data
            # If "project" is the same, then an archieve file is created.
            # If different, then the archieve is created and upzipped in the new
            # location
            # In Data Path
            in_data_path  = rf"{project_folder}\CSV Data"
            out_data_path = rf"{project_folder}\CSV Data"
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
            dev_zip_and_unzip_csv_data.main(in_data_path, out_data_path, selected_files)
            # Declared variables
            del in_data_path, out_data_path, selected_files
            # Imports
            del dev_zip_and_unzip_csv_data
        else:
            pass
        del ZipAndUnzipCsvData

        ZipAndUnzipShapefileData = False
        if ZipAndUnzipShapefileData:
            # Imports
            import dev_zip_and_unzip_shapefile_data
            # If "project_name" is the same, then an archieve file is created.
            # If different, then the archieve is created and upzipped in the new
            # location
            in_data_path  = rf"{project_folder}\Dataset_Shapefiles"
            out_data_path = rf"{project_folder}\Dataset_Shapefiles"
            selected_files = ['AI_IDW_Region.shp', 'EBS_IDW_Region.shp',
                              'ENBS_IDW_Region.shp', 'GMEX_IDW_Region.shp',
                              'GOA_IDW_Region.shp', 'HI_IDW_Region.shp',
                              'NBS_IDW_Region.shp', 'NEUS_FAL_IDW_Region.shp',
                              'NEUS_SPR_IDW_Region.shp', 'SEUS_FAL_IDW_Region.shp',
                              'SEUS_SPR_IDW_Region.shp', 'SEUS_SUM_IDW_Region.shp',
                              'WC_ANN_IDW_Region.shp', 'WC_GFDL_Region.shp',
                              'WC_GLMME_Region.shp', 'WC_TRI_IDW_Region.shp',]
            selected_files = ";".join(selected_files)
            dev_zip_and_unzip_shapefile_data.main(in_data_path, out_data_path, selected_files)
            # Declared variables
            del in_data_path, out_data_path, selected_files
            # Imports
            del dev_zip_and_unzip_shapefile_data
        del ZipAndUnzipShapefileData

    # ###--->>>
        # Write script that checks CSV file headers and updates as necessary
    # ###--->>>
        # ##########################################################################
        # Step 3 - Create base bathymetry datasets in project folder
        # ##########################################################################
        # ToDo1 CreateBaseBathymetry = False
        CreateBaseBathymetry = False
        if CreateBaseBathymetry:
            # Imports
            from dev_create_base_bathymetry import create_alasaka_bathymetry, create_hawaii_bathymetry, gebco_bathymetry
            # Process base Alasak bathymetry
            create_alasaka_bathymetry(project_gdb)
            # Process base Hawaii bathymetry
            create_hawaii_bathymetry(project_gdb)
            # Process base GEBCO bathymetry
            gebco_bathymetry(project_gdb)
            # Declared variables
            # Imports
            del create_alasaka_bathymetry, create_hawaii_bathymetry, gebco_bathymetry
        else:
            pass
        del CreateBaseBathymetry
        # ##########################################################################
        # Step 4 - import the "Datasets" and the "Species_Filter" table into the
        # ##########################################################################
        # project GDB
        ImportDatasetsSpeciesFilterCsvData = False
        if ImportDatasetsSpeciesFilterCsvData:
            # Imports
            from dev_import_datasets_species_filter_csv_data import update_datecode, worker
            from dev_create_table_and_field_definitions_json import generate_data_dictionary
            datasets_csv        = rf"{project_folder}\CSV_Data\Datasets.csv"
            species_filter_csv  = rf"{project_folder}\CSV_Data\Species_Filter.csv"
            survey_metadata_csv = rf"{project_folder}\CSV_Data\DisMAP_Survey_Info.csv"
            # Update DateCode
            update_datecode(csv_file=datasets_csv, project_name=project_name)
            # Datasets CSV File
            worker(project_gdb=project_gdb, csv_file=datasets_csv)
            # Species Filter CSV File
            worker(project_gdb=project_gdb, csv_file=species_filter_csv)
            # DisMAP Survey Info CSV File
            worker(project_gdb=project_gdb, csv_file=survey_metadata_csv)
            # Generate Table and Field Definitions JSON
            generate_data_dictionary(project_gdb)
            # Declared variables
            del datasets_csv, species_filter_csv, survey_metadata_csv
            # Imports
            del update_datecode, worker, generate_data_dictionary
        else:
            pass
        del ImportDatasetsSpeciesFilterCsvData
        # ##########################################################################
        # Step 5 - Create regions from shapefiles
        # ##########################################################################
        CreateRegionsFromShapefiles = False
        if CreateRegionsFromShapefiles:
            # Imports
            from dev_create_regions_from_shapefiles_director import director
            Test = False
            if Test:
                director(project_gdb=project_gdb, Sequential=True, table_names=["WC_TRI_IDW", "AI_IDW"])
            elif not Test:
                director(project_gdb=project_gdb, Sequential=False, table_names=[])
            else:
                pass
            del Test
            # Declared variables
            # Imports
            del director
        else:
            pass
        del CreateRegionsFromShapefiles
        # ##########################################################################
        # Step 6 - Create region fishnets
        # ##########################################################################
        CreateRegionFishnets = False
        if CreateRegionFishnets:
            from dev_create_region_fishnets_director import director
            Test = False
            if Test:
                director(project_gdb=project_gdb, Sequential=True, table_names=["WC_TRI_IDW", "AI_IDW"])
            elif not Test:
                director(project_gdb=project_gdb, Sequential=False, table_names=["NBS_IDW", "ENBS_IDW", "HI_IDW", "SEUS_FAL_IDW", "SEUS_SPR_IDW", "SEUS_SUM_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["WC_TRI_IDW", "GMEX_IDW", "AI_IDW", "GOA_IDW", "WC_ANN_IDW", "NEUS_FAL_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["NEUS_SPR_IDW", "EBS_IDW"])
                #director(project_gdb=project_gdb, Sequential=False, table_names=[])
            else:
                pass
            del Test
            # Declared variables
            # Imports
            del director
        else:
            pass
        del CreateRegionFishnets
        # ##########################################################################
        # Step 7 - Create Region Bathymetry
        # ##########################################################################
        CreateRegionBathymetry = False
        if CreateRegionBathymetry:
            # Imports
            from dev_create_region_bathymetry_director import director
            Test = False
            if Test:
                director(project_gdb=project_gdb, Sequential=True, table_names=["WC_TRI_IDW", "AI_IDW"])
            elif not Test:
                director(project_gdb=project_gdb, Sequential=False, table_names=["NBS_IDW", "ENBS_IDW", "HI_IDW", "SEUS_FAL_IDW", "SEUS_SPR_IDW", "SEUS_SUM_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["WC_TRI_IDW", "GMEX_IDW", "AI_IDW", "GOA_IDW", "WC_ANN_IDW", "NEUS_FAL_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["NEUS_SPR_IDW", "EBS_IDW"])
            else:
                pass
            del Test
            # Declared variables
            # Imports
            del director
        else:
            pass
        del CreateRegionBathymetry
        # ##########################################################################
        # Step 8 - create_region_sample_locations_director
        # ##########################################################################
        CreateRegionSampleLocations = True
        if CreateRegionSampleLocations:
            # Imports
            from dev_create_region_sample_locations_director import director

            Test = False
            if Test:
                director(project_gdb=project_gdb, Sequential=True, table_names=["WC_TRI_IDW", "AI_IDW"])
            elif not Test:
                director(project_gdb=project_gdb, Sequential=False, table_names=["NBS_IDW", "ENBS_IDW", "HI_IDW", "SEUS_FAL_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["SEUS_SPR_IDW", "SEUS_SUM_IDW", "WC_TRI_IDW", "GMEX_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["AI_IDW", "GOA_IDW", "WC_ANN_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["NEUS_FAL_IDW", "NEUS_SPR_IDW", "EBS_IDW"])
            else:
                pass
            del Test
            # Declared variables
            # Imports
            del director
        else:
            pass
        del CreateRegionSampleLocations

        # ##########################################################################
        # Step 9 - Create species year image name table
        # ##########################################################################
        CreateSpeciesYearImageNameTable = False
        if CreateSpeciesYearImageNameTable:
            # Imports
            from dev_create_species_year_image_name_table_director import director, process_image_name_tables

            Test = False
            if Test:
                # Debug
                director(project_gdb=project_gdb, Sequential=False, table_names=["GMEX_IDW",])
                # Debug
            elif not Test:
                director(project_gdb=project_gdb, Sequential=False, table_names=[])
            else:
                pass
            del Test
            # Combine Image Name Tables
            #process_image_name_tables(project_gdb=project_gdb, project=project_name)

            # Declared variables
            # Imports
            del director, process_image_name_tables
        else:
            pass
        del CreateSpeciesYearImageNameTable

        # ##########################################################################
        # Step 10 - Create Rasters
        # ##########################################################################
        CreateRasters = False
        if CreateRasters:
            # Imports
            from dev_create_rasters_director import director

            Test = False
            if Test:
                # Debug
                director(project_gdb=project_gdb, Sequential=False, table_names=["GMEX_IDW",])
                # Debug
            elif not Test:
                director(project_gdb=project_gdb, Sequential=False, table_names=["NBS_IDW", "ENBS_IDW", "HI_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["SEUS_FAL_IDW", "SEUS_SPR_IDW", "SEUS_SUM_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["WC_TRI_IDW", "AI_IDW", "GMEX_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["GOA_IDW", "WC_ANN_IDW", "NEUS_FAL_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["NEUS_SPR_IDW", "EBS_IDW",])
            else:
                pass
            del Test
            # Declared variables
            # Imports
            del director
        else:
            pass
        del CreateRasters

        # ##########################################################################
        # Step 11 - Create Indicators Table
        # ##########################################################################
        CreateIndicatorsTable = False
        if CreateIndicatorsTable:
            # Imports
            from dev_create_indicators_table_director import director, process_indicator_tables

            Test = False
            if Test:
                # Debug
                director(project_gdb=project_gdb, Sequential=False, table_names=["GMEX_IDW",])
                # Debug
            elif not Test:
                director(project_gdb=project_gdb, Sequential=False, table_names=["NBS_IDW", "ENBS_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["HI_IDW", "SEUS_FAL_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["SEUS_SPR_IDW", "SEUS_SUM_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["WC_TRI_IDW", "GMEX_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["AI_IDW", "GOA_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["WC_ANN_IDW", "NEUS_FAL_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["NEUS_SPR_IDW", "EBS_IDW",])

                # Combine Indicator Tables
            else:
                pass
            del Test
            #process_indicator_tables(project_gdb=project_gdb, project=project)
            # Declared variables
            # Imports
            del director, process_indicator_tables
        else:
            pass
        del CreateIndicatorsTable

        # dataset_comparison - rasters
        # dataset_comparison - feature classes
        # dataset_comparison - tables

        # Step 12 - Create Species Richness Rasters
        CreateSpeciesRichnessRasters = False
        if CreateSpeciesRichnessRasters:
            # Imports
            from dev_create_species_richness_rasters_director import director

            Test = False
            if Test:
                director(project_gdb=project_gdb, Sequential=False, table_names=["GMEX_IDW",])
            elif not Test:
                director(project_gdb=project_gdb, Sequential=False, table_names=["NBS_IDW", "ENBS_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["HI_IDW", "SEUS_FAL_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["SEUS_SPR_IDW", "SEUS_SUM_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["WC_TRI_IDW", "GMEX_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["AI_IDW", "GOA_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["WC_ANN_IDW", "NEUS_FAL_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["NEUS_SPR_IDW", "EBS_IDW",])
            else:
                pass
            del Test
            # Declared variables
            # Imports
            del director
        else:
            pass
        del CreateSpeciesRichnessRasters

        # create_mosaics_director
        # Step 12 - Create Mosaics
        CreateMosaics = False
        if CreateMosaics:
            # Imports
            from dev_create_mosaics_director import director

            Test = False
            if Test:
                director(project_gdb=project_gdb, Sequential=False, table_names=["GMEX_IDW",])
            elif not Test:
                director(project_gdb=project_gdb, Sequential=False, table_names=["NBS_IDW", "ENBS_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["HI_IDW", "SEUS_FAL_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["SEUS_SPR_IDW", "SEUS_SUM_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["WC_TRI_IDW", "GMEX_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["AI_IDW", "GOA_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["WC_ANN_IDW", "NEUS_FAL_IDW",])
                director(project_gdb=project_gdb, Sequential=False, table_names=["NEUS_SPR_IDW", "EBS_IDW",])
            else:
                pass
            del Test
            # Declared variables
            # Imports
            del director
        else:
            pass
        del CreateMosaics

        # publish_to_portal_director

        # Declared Varaiables
        del project_name, project_folder
        # Imports
        # Function Parameters
        del project_gdb

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        print(f"\n{'-' * 80}")
        print(f"Python script: {os.path.basename(__file__)}\nCompleted: {strftime('%a %b %d %I:%M %p', localtime())}")
        print(u"Elapsed Time {0} (H:M:S)".format(strftime("%H:%M:%S", gmtime(elapse_time))))
        print(f"{'-' * 80}")
        del elapse_time, end_time, start_time
        del gmtime, localtime, strftime, time
    except:
        traceback.print_exc()
        raise SystemExit
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function at line number {inspect.stack()[0][2]}\n\t##--> '{', '.join(rk)}' <--##"); del rk
        return True
    finally:
        pass

if __name__ == '__main__':
    try:
        # Append the location of this scrip to the System Path
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        # Imports
        base_project_folder = rf"{os.path.dirname(os.path.dirname(__file__))}"
        #project = "May 1 2024"
        #project_name = "July 1 2024"
        #project_name = "December 1 2024"
        #project_name = "June 1 2025"
        #for project_name in ["June 1 2025"]:
        for project_name in ["December 1 2024", "June 1 2025"]:
            project_folder = rf"{base_project_folder}"
            project_gdb    = rf"{project_folder}\{project_name}\{project_name}.gdb"
            main(project_gdb=project_gdb)
            del project_gdb, project_folder, project_name
        # Decated Variables
        del base_project_folder
        # Imports
    except SystemExit:
        pass
    except:
        traceback.print_exc()
    else:
        pass
    finally:
        pass