# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      john.f.kennedy
#
# Created:     03/03/2024
# Copyright:   (c) john.f.kennedy 2024
# Licence:     <your licence>
# -------------------------------------------------------------------------------
import os, sys  # built-ins first
import traceback
import importlib
import inspect

import arcpy  # third-parties second

def new_function():
    try:
        pass
        # Declared Varaiables
        # Imports
        # Function Parameters
    except KeyboardInterrupt:
        raise SystemExit
    except:
        traceback.print_exc()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function at line number {inspect.stack()[0][2]}\n\t##--> '{', '.join(rk)}' <--##"); del rk
        return True
    finally:
        pass

def date_code(version):
    try:
        from datetime import datetime
        from time import strftime

        _date_code = ""

        if version.isdigit():
            # The version value is 'YYYYMMDD' format (20230501)
            # and is converted to 'Month Day and Year' (i.e. May 1 2023)
            _date_code = datetime.strptime(version, "%Y%m%d").strftime("%B %#d %Y")
        elif not version.isdigit():
            # The version value is 'Month Day and Year' (i.e. May 1 2023)
            # and is converted to 'YYYYMMDD' format (20230501)
            _date_code = datetime.strptime(version, "%B %d %Y").strftime("%Y%m%d")
        else:
            _date_code = "error"
        # Imports
        del datetime, strftime
        del version

        import copy
        __results = copy.deepcopy(_date_code)
        del _date_code, copy
    except KeyboardInterrupt:
        raise SystemExit
    except:
        traceback.print_exc()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function at line number {inspect.stack()[0][2]}\n\t##--> '{', '.join(rk)}' <--##"); del rk
        return __results
    finally:
        if "__results" in locals().keys(): del __results

# #
# Function: unique_years
#       Gets the unique years in a table
# @param string table: The name of the layer
# @return array: a sorted year array so we can go in order.
# #
def unique_years(table):
    #print(table)
    arcpy.management.SelectLayerByAttribute( table, "CLEAR_SELECTION" )
    arcpy.management.SelectLayerByAttribute( table, "NEW_SELECTION", "Year IS NOT NULL")
    with arcpy.da.SearchCursor(table, ["Year"]) as cursor:
        return sorted({row[0] for row in cursor})

def xml_tree_merge(source, target):
    import copy
    """Merge two xml trees A and B, so that each recursively found leaf element of B is added to A.  If the element
    already exists in A, it is replaced with B's version.  Tree structure is created in A as required to reflect the
    position of the leaf element in B.
    Given <top><first><a/><b/></first></top> and  <top><first><c/></first></top>, a merge results in
    <top><first><a/><b/><c/></first></top> (order not guaranteed)
    """
    def inner(aparent, bparent):
        for bchild in bparent:
            achild = aparent.xpath('./' + bchild.tag)
            if not achild:
                aparent.append(bchild)
            elif bchild.getchildren():
                inner(achild[0], bchild)

    source_copy = copy.deepcopy(source)
    inner(source_copy, target)
    return source_copy

def dataset_title_dict(project_gdb=""):
    try:
        if "Scratch" in project_gdb:
            project = os.path.basename(os.path.dirname(os.path.dirname(project_gdb)))
        else:
            project = os.path.basename(os.path.dirname(project_gdb))

        project_folder     = os.path.dirname(project_gdb)
        crf_folder         = rf"{project_folder}\CRFs"
        _credits           = "These data were produced by NMFS OST."
        access_constraints = "***No Warranty*** The user assumes the entire risk related to its use of these data. NMFS is providing these data 'as is' and NMFS disclaims any and all warranties, whether express or implied, including (without limitation) any implied warranties of merchantability or fitness for a particular purpose. No warranty expressed or implied is made regarding the accuracy or utility of the data on any other system or for general or scientific purposes, nor shall the act of distribution constitute any such warranty. It is strongly recommended that careful attention be paid to the contents of the metadata file associated with these data to evaluate dataset limitations, restrictions or intended use. In no event will NMFS be liable to you or to any third party for any direct, indirect, incidental, consequential, special or exemplary damages or lost profit resulting from any use or misuse of these data."

        __datasets_dict = {}

        dataset_codes = {row[0] : [row[1], row[2], row[3], row[4], row[5]] for row in arcpy.da.SearchCursor(rf"{project_gdb}\Datasets", ["DatasetCode", "PointFeatureType", "DistributionProjectCode", "FilterRegion", "FilterSubRegion", "Season"])}
        for dataset_code in dataset_codes:
            point_feature_type        = dataset_codes[dataset_code][0] if dataset_codes[dataset_code][0] else ""
            distribution_project_code = dataset_codes[dataset_code][1] if dataset_codes[dataset_code][1] else ""
            filter_region             = dataset_codes[dataset_code][2] if dataset_codes[dataset_code][2] else dataset_code.replace("_", " ")
            filter_sub_region         = dataset_codes[dataset_code][3] if dataset_codes[dataset_code][3] else dataset_code.replace("_", " ")
            season                    = dataset_codes[dataset_code][4] if dataset_codes[dataset_code][4] else ""

            tags    = f"DisMAP; {filter_region}" if filter_region == filter_sub_region else f"DisMAP; {filter_region}; {filter_sub_region}"
            tags    = f"{tags}; {season}" if season else f"{tags}"
            tags    = f"{tags}; distribution; seasonal distribution; fish; invertebrates; climate change; fishery-independent surveys; ecological dynamics; oceans; biosphere; earth science; species/population interactions; aquatic sciences; fisheries; range changes"
            summary = "These data were created as part of the DisMAP project to enable visualization and analysis of changes in fish and invertebrate distributions"

            #print(f"Dateset Code: {dataset_code}")
            if distribution_project_code:
                if distribution_project_code == "IDW":

                    #table_name            = f"{dataset_code}_{distribution_project_code}_TABLE"
                    table_name            = f"{dataset_code}_{distribution_project_code}"
                    table_name_s          = f"{table_name}_{date_code(project)}"
                    table_name_st         = f"{filter_sub_region} {season} Table {date_code(project)}".replace('  ',' ')

                    #print(f"\tProcessing: {table_name}")

                    __datasets_dict[table_name] = {"Dataset Service"       : table_name_s,
                                                 "Dataset Service Title" : table_name_st,
                                                 "Tags"                  : tags,
                                                 "Summary"               : summary,
                                                 "Description"           : f"This table represents the CSV Data files in ArcGIS format",
                                                 "Credits"               : _credits,
                                                 "Access Constraints"    : access_constraints}

                    del table_name, table_name_s, table_name_st

                    table_name            = f"{dataset_code}_{distribution_project_code}"
                    sample_locations_fc   = f"{table_name}_{point_feature_type.replace(' ', '_')}"
                    sample_locations_fcs  = f"{table_name}_{point_feature_type.replace(' ', '_')}_{date_code(project)}"
                    feature_service_title = f"{filter_sub_region} {season} {point_feature_type} {date_code(project)}"
                    sample_locations_fcst = f"{feature_service_title.replace('  ',' ')}"
                    del feature_service_title

                    __datasets_dict[sample_locations_fc] = {"Dataset Service"       : sample_locations_fcs,
                                                          "Dataset Service Title" : sample_locations_fcst,
                                                          "Tags"                  : tags,
                                                          "Summary"               : f"{summary}. These layers provide information on the spatial extent/boundaries of the bottom trawl surveys. Information on species distributions is of paramount importance for understanding and preparing for climate-change impacts, and plays a key role in climate-ready fisheries management.",
                                                          "Description"           : f"This survey points layer provides information on both the locations where species are caught in several NOAA Fisheries surveys and the amount (i.e., biomass weight catch per unit effort, standardized to kg/ha) of each species that was caught at each location. Information on species distributions is of paramount importance for understanding and preparing for climate-change impacts, and plays a key role in climate-ready fisheries management.",
                                                          "Credits"               : _credits,
                                                          "Access Constraints"    : access_constraints}

                    #print(f"\tSample Locations FC:   {sample_locations_fc}")
                    #print(f"\tSample Locations FCS:  {sample_locations_fcs}")
                    #print(f"\tSample Locations FST:  {sample_locations_fcst}")

                    del table_name, sample_locations_fc, sample_locations_fcs, sample_locations_fcst

                    table_name            = f"{dataset_code}"
                    sample_locations_fc   = f"{table_name}_{point_feature_type.replace(' ', '_')}"
                    sample_locations_fcs  = f"{table_name}_{point_feature_type.replace(' ', '_')}_{date_code(project)}"
                    feature_service_title = f"{filter_sub_region} {season} {point_feature_type} {date_code(project)}"
                    sample_locations_fcst = f"{feature_service_title.replace('  ',' ')}"
                    del feature_service_title

                    __datasets_dict[sample_locations_fc] = {"Dataset Service"       : sample_locations_fcs,
                                                          "Dataset Service Title" : sample_locations_fcst,
                                                          "Tags"                  : tags,
                                                          "Summary"               : f"{summary}. These layers provide information on the spatial extent/boundaries of the bottom trawl surveys. Information on species distributions is of paramount importance for understanding and preparing for climate-change impacts, and plays a key role in climate-ready fisheries management.",
                                                          "Description"           : f"This survey points layer provides information on both the locations where species are caught in several NOAA Fisheries surveys and the amount (i.e., biomass weight catch per unit effort, standardized to kg/ha) of each species that was caught at each location. Information on species distributions is of paramount importance for understanding and preparing for climate-change impacts, and plays a key role in climate-ready fisheries management.",
                                                          "Credits"               : _credits,
                                                          "Access Constraints"    : access_constraints}

                    #print(f"\tSample Locations FC:   {sample_locations_fc}")
                    #print(f"\tSample Locations FCS:  {sample_locations_fcs}")
                    #print(f"\tSample Locations FST:  {sample_locations_fcst}")

                    del table_name, sample_locations_fc, sample_locations_fcs, sample_locations_fcst


                elif distribution_project_code != "IDW":

                    #table_name            = f"{dataset_code}_TABLE"
                    table_name            = f"{dataset_code}"
                    table_name_s          = f"{table_name}_{date_code(project)}"
                    table_name_st         = f"{filter_sub_region} {season} Table {date_code(project)}".replace('  ',' ')

                    #print(f"\tProcessing: {table_name}")

                    __datasets_dict[table_name] = {"Dataset Service"       : table_name_s,
                                                 "Dataset Service Title" : table_name_st,
                                                 "Tags"                  : tags,
                                                 "Summary"               : summary,
                                                 "Description"           : f"This table represents the CSV Data files in ArcGIS format",
                                                 "Credits"               : _credits,
                                                 "Access Constraints"    : access_constraints}

                    del table_name, table_name_s, table_name_st

                    table_name            = f"{dataset_code}"
                    grid_points_fc        = f"{table_name}_{point_feature_type.replace(' ', '_')}"
                    grid_points_fcs       = f"{table_name}_{point_feature_type.replace(' ', '_')}_{date_code(project)}"
                    feature_service_title = f"{filter_sub_region} {season} Sample Locations {date_code(project)}"
                    grid_points_fcst      = f"{dataset_code.replace('_', ' ')} {point_feature_type} {date_code(project)}"

                    __datasets_dict[grid_points_fc] = {"Dataset Service"       : grid_points_fcs,
                                                     "Dataset Service Title" : grid_points_fcst,
                                                     "Tags"                  : tags,
                                                     "Summary"               : summary,
                                                     "Description"           : f"This grid points layer provides information on model output amount (i.e., biomass weight catch per unit effort, standardized to kg/ha) of each species that was modeled at each location. Information on species distributions is of paramount importance for understanding and preparing for climate-change impacts, and plays a key role in climate-ready fisheries management.",
                                                     "Credits"               : _credits,
                                                     "Access Constraints"    : access_constraints}

                    #print(f"\tGRID Points FC:   {grid_points_fc}")
                    #print(f"\tGRID Points FCS:  {grid_points_fcs}")
                    #print(f"\tGRID Points FCST: {grid_points_fcst}")

                    del table_name, grid_points_fc, grid_points_fcs, grid_points_fcst

                dataset_code = f"{dataset_code}_{distribution_project_code}" if distribution_project_code not in dataset_code else dataset_code

                # Bathymetry
                bathymetry_r          = f"{dataset_code}_Bathymetry"
                bathymetry_rs         = f"{dataset_code}_Bathymetry_{date_code(project)}"
                feature_service_title = f"{filter_sub_region} {season} Bathymetry {date_code(project)}"
                bathymetry_rst        = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #print(f"\tProcessing: {bathymetry_r}")

                __datasets_dict[bathymetry_r] = {"Dataset Service"       : bathymetry_rs,
                                               "Dataset Service Title" : bathymetry_rst,
                                               "Tags"                  : tags,
                                               "Summary"               : summary,
                                               "Description"           : f"The bathymetry dataset represents the ocean depth at that grid cell.",
                                               "Credits"               : _credits,
                                               "Access Constraints"    : access_constraints}

                #print(f"\tBathymetry R:   {bathymetry_r}")
                #print(f"\tBathymetry RS:  {bathymetry_rs}")
                #print(f"\tBathymetry RST: {bathymetry_rst}")

                del bathymetry_r, bathymetry_rs, bathymetry_rst

                # Boundary
                boundary_fc           = f"{dataset_code}_Boundary"
                boundary_fcs          = f"{dataset_code}_Boundary_{date_code(project)}"
                feature_service_title = f"{filter_sub_region} {season} Boundary {date_code(project)}"
                boundary_fcst         = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #print(f"\tProcessing: {boundary_fc}")

                __datasets_dict[boundary_fc] = {"Dataset Service"       : boundary_fcs,
                                              "Dataset Service Title" : boundary_fcst,
                                              "Tags"                  : tags,
                                              "Summary"               : summary,
                                              "Description"           : f"These files contain the spatial boundaries of the NOAA Fisheries Bottom-trawl surveys. This data set covers 8 regions of the United States: Northeast, Southeast, Gulf of Mexico, West Coast, Eastern Bering Sea, Aleutian Islands, Gulf of Alaska, and Hawai'i Islands.",
                                              "Credits"               : _credits,
                                              "Access Constraints"    : access_constraints}

                #print(f"\tBoundary FC:   {boundary_fc}")
                #print(f"\tBoundary FCS:  {boundary_fcs}")
                #print(f"\tBoundary FCST: {boundary_fcst}")

                del boundary_fc, boundary_fcs, boundary_fcst

                # Boundary
                boundary_line_fc      = f"{dataset_code}_Boundary_Line"
                boundary_line_fcs     = f"{dataset_code}_Boundary_Line_{date_code(project)}"
                feature_service_title = f"{filter_sub_region} {season} Boundary Line {date_code(project)}"
                boundary_line_fcst    = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #print(f"\tProcessing: {boundary_line_fc}")

                __datasets_dict[boundary_line_fc] = {"Dataset Service"       : boundary_line_fcs,
                                                   "Dataset Service Title" : boundary_line_fcst,
                                                   "Tags"                  : tags,
                                                   "Summary"               : summary,
                                                   "Description"           : f"These files contain the spatial boundaries of the NOAA Fisheries Bottom-trawl surveys. This data set covers 8 regions of the United States: Northeast, Southeast, Gulf of Mexico, West Coast, Eastern Bering Sea, Aleutian Islands, Gulf of Alaska, and Hawai'i Islands.",
                                                   "Credits"               : _credits,
                                                   "Access Constraints"    : access_constraints}

                #print(f"\tBoundary FC:   {boundary_line_fc}")
                #print(f"\tBoundary FCS:  {boundary_line_fcs}")
                #print(f"\tBoundary FCST: {boundary_line_fcst}")

                del boundary_line_fc, boundary_line_fcs, boundary_line_fcst

                # CRF
                crf_r                 = f"{dataset_code}_CRF"
                crf_rs                = f"{dataset_code}_{date_code(project)}"
                feature_service_title = f"{filter_sub_region} {season} {dataset_code[dataset_code.rfind('_')+1:]} {date_code(project)}"
                crf_rst               = f"{feature_service_title.replace('  ',' ')}"
                #del feature_service_title

                #print(f"Processing: {crf_r}")
                #print(f"\t{crf_rs}")
                #print(f"\t{feature_service_title}")
                #print(f"\t{crf_rst}")

                __datasets_dict[crf_r] = {"Dataset Service"       : crf_rs,
                                        "Dataset Service Title" : crf_rst,
                                        "Tags"                  : tags,
                                        "Summary"               : f"{summary}. These interpolated biomass layers provide information on the spatial distribution of species caught in the NOAA Fisheries fisheries-independent surveys. Information on species distributions is of paramount importance for understanding and preparing for climate-change impacts, and plays a key role in climate-ready fisheries management.",
                                        "Description"           : f"NOAA Fisheries and its partners conduct fisheries-independent surveys in 8 regions in the US (Northeast, Southeast, Gulf of Mexico, West Coast, Gulf of Alaska, Bering Sea, Aleutian Islands, Hawai’i Islands). These surveys are designed to collect information on the seasonal distribution, relative abundance, and biodiversity of fish and invertebrate species found in U.S. waters. Over 400 species of fish and invertebrates have been identified in these surveys.",
                                        "Credits"               : _credits,
                                        "Access Constraints"    : access_constraints}

                #print(f"\tCRF R:   {crf_r}")
                #print(f"\tCRF RS:  {crf_rs}")
                #print(f"\tCRF RST: {crf_rst}")

                del crf_r, crf_rs, crf_rst

                # Extent Points
                extent_points_fc      = f"{dataset_code}_Extent_Points"
                extent_points_fcs     = f"{dataset_code}_Extent_Points_{date_code(project)}"
                feature_service_title = f"{filter_sub_region} {season} Extent Points {date_code(project)}"
                extent_points_fcst    = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #print(f"\tProcessing: {extent_points_fc}")

                __datasets_dict[extent_points_fc] = {"Dataset Service"       : extent_points_fcs,
                                                   "Dataset Service Title" : extent_points_fcst,
                                                   "Tags"                  : tags,
                                                   "Summary"               : summary,
                                                   "Description"           : f"The Extent Points layer represents the extent of the model region.",
                                                   "Credits"               : _credits,
                                                   "Access Constraints"    : access_constraints}

                #print(f"\tExtent Points FC:   {extent_points_fc}")
                #print(f"\tExtent Points FCS:  {extent_points_fcs}")
                #print(f"\tExtent Points FCST: {extent_points_fcst}")

                del extent_points_fc, extent_points_fcs, extent_points_fcst

                # Extent Points
                points_fc      = f"{dataset_code}_Points"
                points_fcs     = f"{dataset_code}_Points_{date_code(project)}"
                feature_service_title = f"{filter_sub_region} {season} Extent Points {date_code(project)}"
                points_fcst    = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #print(f"\tProcessing: {points_fc}")

                __datasets_dict[points_fc] = {"Dataset Service"       : points_fcs,
                                            "Dataset Service Title" : points_fcst,
                                            "Tags"                  : tags,
                                            "Summary"               : summary,
                                            "Description"           : f"The Points layer represents the extent of the model region.",
                                            "Credits"               : _credits,
                                            "Access Constraints"    : access_constraints}

                #print(f"\tExtent Points FC:   {points_fc}")
                #print(f"\tExtent Points FCS:  {points_fcs}")
                #print(f"\tExtent Points FCST: {points_fcst}")

                del points_fc, points_fcs, points_fcst

                fishnet_fc            = f"{dataset_code}_Fishnet"
                fishnet_fcs           = f"{dataset_code}_Fishnet_{date_code(project)}"
                feature_service_title = f"{filter_sub_region} {season} Fishnet {date_code(project)}"
                fishnet_fcst          = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #print(f"\tProcessing: {fishnet_fc}")

                __datasets_dict[fishnet_fc] = {"Dataset Service"       : fishnet_fcs,
                                             "Dataset Service Title" : fishnet_fcst,
                                             "Tags"                  : tags,
                                             "Summary"               : summary,
                                             "Description"           : f"The Fishnet is used to create the latitude and longitude rasters.",
                                             "Credits"               : _credits,
                                             "Access Constraints"    : access_constraints}

                #print(f"\tFishnet FC:   {fishnet_fc}")
                #print(f"\tFishnet FCS:  {fishnet_fcs}")
                #print(f"\tFishnet FCST: {fishnet_fcst}")

                del fishnet_fc, fishnet_fcs, fishnet_fcst

                indicators_tb         = f"{dataset_code}_Indicators"
                indicators_tbs        = f"{dataset_code}_Indicators_{date_code(project)}"
                feature_service_title = f"{filter_sub_region} {season} Indicators Table {date_code(project)}"
                indicators_tbst       = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #print(f"\tProcessing: {indicators_t}")

                __datasets_dict[indicators_tb] = {"Dataset Service"       : indicators_tbs,
                                               "Dataset Service Title" : indicators_tbst,
                                               "Tags"                  : tags,
                                               "Summary"               : f"{summary}. This table provides the key metrics used to evaluate a species distribution shift. Information on species distributions is of paramount importance for understanding and preparing for climate-change impacts, and plays a key role in climate-ready fisheries management.",
                                               "Description"           : f"These data contain the key distribution metrics of center of gravity, range limits, and depth for each species in the portal. This data set covers 8 regions of the United States: Northeast, Southeast, Gulf of Mexico, West Coast, Bering Sea, Aleutian Islands, Gulf of Alaska, and Hawai'i Islands.",
                                               "Credits"               : _credits,
                                               "Access Constraints"    : access_constraints}

                #print(f"\tIndicators T:   {indicators_t}")
                #print(f"\tIndicators TS:  {indicators_ts}")
                #print(f"\tIndicators TST: {indicators_tst}")

                del indicators_tb, indicators_tbs, indicators_tbst

                lat_long_fc           = f"{dataset_code}_Lat_Long"
                lat_long_fcs          = f"{dataset_code}_Lat_Long_{date_code(project)}"
                feature_service_title = f"{filter_sub_region} {season} Lat Long {date_code(project)}"
                lat_long_fcst         = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #print(f"\tProcessing: {lat_long_fc}")

                __datasets_dict[lat_long_fc] = {"Dataset Service"       : lat_long_fcs,
                                              "Dataset Service Title" : lat_long_fcst,
                                              "Tags"                  : tags,
                                              "Summary"               : summary,
                                              "Description"           : f"The lat_long layer is used to get the latitude & longitude values to create these rasters",
                                              "Credits"               : _credits,
                                              "Access Constraints"    : access_constraints}

                #print(f"\tLat Long FC:   {lat_long_fc}")
                #print(f"\tLat Long FCS:  {lat_long_fcs}")
                #print(f"\tLat Long FCST: {lat_long_fcst}")

                del lat_long_fc, lat_long_fcs, lat_long_fcst

                latitude_r            = f"{dataset_code}_Latitude"
                latitude_rs           = f"{dataset_code}_Latitude_{date_code(project)}"
                feature_service_title = f"{filter_sub_region} {season} Latitude {date_code(project)}"
                latitude_rst          = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #print(f"\tProcessing: {latitude_r}")

                __datasets_dict[latitude_r] = {"Dataset Service"       : latitude_rs,
                                             "Dataset Service Title" : latitude_rst,
                                             "Tags"                  : tags,
                                             "Summary"               : summary,
                                             "Description"           : f"The Latitude raster",
                                             "Credits"               : _credits,
                                             "Access Constraints"    : access_constraints}

                #print(f"\tLatitude R:   {latitude_r}")
                #print(f"\tLatitude RS:  {latitude_rs}")
                #print(f"\tLatitude RST: {latitude_rst}")

                del latitude_r, latitude_rs, latitude_rst

                layer_species_year_image_name_tb   = f"{dataset_code}_LayerSpeciesYearImageName"
                layer_species_year_image_name_tbs  = f"{dataset_code}_LayerSpeciesYearImageName_{date_code(project)}"
                feature_service_title             = f"{filter_sub_region} {season} Layer Species Year Image Name Table {date_code(project)}"
                layer_species_year_image_name_tbst = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #print(f"\tProcessing: {layer_species_year_image_name_tb}")

                __datasets_dict[layer_species_year_image_name_tb] = {"Dataset Service"       : layer_species_year_image_name_tbs,
                                                                   "Dataset Service Title" : layer_species_year_image_name_tbst,
                                                                   "Tags"                  : tags,
                                                                   "Summary"               : summary,
                                                                   "Description"           : f"Layer Species Year Image Name Table",
                                                                   "Credits"               : _credits,
                                                                   "Access Constraints"    : access_constraints}

                #print(f"\tLayerSpeciesYearImageName T:   {layer_species_year_image_name_tb}")
                #print(f"\tLayerSpeciesYearImageName TS:  {layer_species_year_image_name_tbs}")
                #print(f"\tLayerSpeciesYearImageName TST: {layer_species_year_image_name_tbst}")

                del layer_species_year_image_name_tb, layer_species_year_image_name_tbs, layer_species_year_image_name_tbst

                longitude_r           = f"{dataset_code}_Longitude"
                longitude_rs          = f"{dataset_code}_Longitude_{date_code(project)}"
                feature_service_title = f"{filter_sub_region} {season} Longitude {date_code(project)}"
                longitude_rst         = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #print(f"\tProcessing: {longitude_r}")

                __datasets_dict[longitude_r] = {"Dataset Service"       : longitude_rs,
                                              "Dataset Service Title" : longitude_rst,
                                              "Tags"                  : tags,
                                              "Summary"               : summary,
                                              "Description"           : f"The Longitude raster",
                                              "Credits"               : _credits,
                                              "Access Constraints"    : access_constraints}

                #print(f"\tLongitude R:   {longitude_r}")
                #print(f"\tLongitude RS:  {longitude_rs}")
                #print(f"\tLongitude RST: {longitude_rst}")

                del longitude_r, longitude_rs, longitude_rst

                mosaic_r              = f"{dataset_code}_Mosaic"
                mosaic_rs             = f"{dataset_code}_Mosaic_{date_code(project)}"
                feature_service_title = f"{filter_sub_region} {season} {dataset_code[dataset_code.rfind('_')+1:]} Mosaic {date_code(project)}"
                mosaic_rst            = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #print(f"\tProcessing: {mosaic_r}")

                __datasets_dict[mosaic_r] = {"Dataset Service"       : mosaic_rs,
                                           "Dataset Service Title" : mosaic_rst,
                                           #"Tags"                  : _tags,
                                           "Tags"                  : tags,
                                           "Summary"               : f"{summary}. These interpolated biomass layers provide information on the spatial distribution of species caught in the NOAA Fisheries fisheries-independent surveys. Information on species distributions is of paramount importance for understanding and preparing for climate-change impacts, and plays a key role in climate-ready fisheries management.",
                                           "Description"           : f"NOAA Fisheries and its partners conduct fisheries-independent surveys in 8 regions in the US (Northeast, Southeast, Gulf of Mexico, West Coast, Gulf of Alaska, Bering Sea, Aleutian Islands, Hawai’i Islands). These surveys are designed to collect information on the seasonal distribution, relative abundance, and biodiversity of fish and invertebrate species found in U.S. waters. Over 400 species of fish and invertebrates have been identified in these surveys.",
                                           "Credits"               : _credits,
                                           "Access Constraints"    : access_constraints}

                #print(f"\tMosaic R:   {mosaic_r}")
                #print(f"\tMosaic RS:  {mosaic_rs}")
                #print(f"\tMosaic RST: {mosaic_rst}")

                del mosaic_r, mosaic_rs, mosaic_rst

                crf_r                 = f"{dataset_code}.crf"
                crf_rs                = f"{dataset_code}_CRF_{date_code(project)}"
                feature_service_title = f"{filter_sub_region} {season} {dataset_code[dataset_code.rfind('_')+1:]} C {date_code(project)}"
                crf_rst               = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #print(f"\tProcessing: {mosaic_r}")

                __datasets_dict[crf_r] = {"Dataset Service"       : crf_rs,
                                        "Dataset Service Title" : crf_rst,
                                        #"Tags"                  : _tags,
                                        "Tags"                  : tags,
                                        "Summary"               : f"{summary}. These interpolated biomass layers provide information on the spatial distribution of species caught in the NOAA Fisheries fisheries-independent surveys. Information on species distributions is of paramount importance for understanding and preparing for climate-change impacts, and plays a key role in climate-ready fisheries management.",
                                        "Description"           : f"NOAA Fisheries and its partners conduct fisheries-independent surveys in 8 regions in the US (Northeast, Southeast, Gulf of Mexico, West Coast, Gulf of Alaska, Bering Sea, Aleutian Islands, Hawai’i Islands). These surveys are designed to collect information on the seasonal distribution, relative abundance, and biodiversity of fish and invertebrate species found in U.S. waters. Over 400 species of fish and invertebrates have been identified in these surveys.",
                                        "Credits"               : _credits,
                                        "Access Constraints"    : access_constraints}

                #print(f"\tCFR R:   {crf_r}")
                #print(f"\tCFR RS:  {crf_rs}")
                #print(f"\tCFR RST: {crf_rst}")

                del crf_r, crf_rs, crf_rst

                raster_mask_r         = f"{dataset_code}_Raster_Mask"
                raster_mask_rs        = f"{dataset_code}_Raster_Mask_{date_code(project)}"
                feature_service_title = f"{filter_sub_region} {season} Raster Mask {date_code(project)}"
                raster_mask_rst       = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #print(f"\tProcessing: {raster_mask_r}")

                __datasets_dict[raster_mask_r] = {"Dataset Service"       : raster_mask_rs,
                                                "Dataset Service Title" : raster_mask_rst,
                                                "Tags"                  : tags,
                                                "Summary"               : summary,
                                                "Description"           : f"Raster Mask is used for image production",
                                                "Credits"               : _credits,
                                                "Access Constraints"    : access_constraints}

                #print(f"\tRaster_Mask R:   {raster_mask_r}")
                #print(f"\tRaster_Mask RS:  {raster_mask_rs}")
                #print(f"\tRaster_Mask RST: {raster_mask_rst}")

                del raster_mask_r, raster_mask_rs, raster_mask_rst

                region_fc             = f"{dataset_code}_Region"
                region_fcs            = f"{dataset_code}_Region_{date_code(project)}"
                feature_service_title = f"{filter_sub_region} {season} Region {date_code(project)}"
                region_fcst           = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #print(f"\tProcessing: {region_fc}")

                __datasets_dict[region_fc] = {"Dataset Service"       : region_fcs,
                                            "Dataset Service Title" : region_fcst,
                                            "Tags"                  : tags,
                                            "Summary"               : summary,
                                            "Description"           : f"These files contain the spatial boundaries of the NOAA Fisheries Bottom-trawl surveys. This data set covers 8 regions of the United States: Northeast, Southeast, Gulf of Mexico, West Coast, Bering Sea, Aleutian Islands, Gulf of Alaska, and Hawai'i Islands.",
                                            "Credits"               : _credits,
                                            "Access Constraints"    : access_constraints}

                #print(f"\tRegion FC:   {region_fc}")
                #print(f"\tRegion FCS:  {region_fcs}")
                #print(f"\tRegion FCST: {region_fcst}")

                del region_fc, region_fcs, region_fcst

                survey_area_fc        = f"{dataset_code}_Survey_Area"
                survey_area_fcs       = f"{dataset_code}_Region_{date_code(project)}"
                feature_service_title = f"{filter_sub_region} {season} Region {date_code(project)}"
                survey_area_fcst      = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #print(f"\tProcessing: {survey_area_fc}")

                __datasets_dict[survey_area_fc] = {"Dataset Service"       : survey_area_fcs,
                                                 "Dataset Service Title" : survey_area_fcst,
                                                 "Tags"                  : tags,
                                                 "Summary"               : summary,
                                                 "Description"           : f"These files contain the spatial boundaries of the NOAA Fisheries Bottom-trawl surveys. This data set covers 8 regions of the United States: Northeast, Southeast, Gulf of Mexico, West Coast, Bering Sea, Aleutian Islands, Gulf of Alaska, and Hawai'i Islands.",
                                                 "Credits"               : _credits,
                                                 "Access Constraints"    : access_constraints}

                #print(f"\tRegion FC:   {survey_area_fc}")
                #print(f"\tRegion FCS:  {survey_area_fcs}")
                #print(f"\tRegion FCST: {survey_area_fcst}")

                del survey_area_fc, survey_area_fcs, survey_area_fcst


            del tags

            if not distribution_project_code:

                if "Datasets" == dataset_code:

                    #print(f"\tProcessing: Datasets")

                    datasets_tb   = dataset_code
                    datasets_tbs  = f"{dataset_code}_{date_code(project)}"
                    datasets_tbst = f"{dataset_code} {date_code(project)}"

                    __datasets_dict[datasets_tb] = {"Dataset Service"       : datasets_tbs,
                                                  "Dataset Service Title" : datasets_tbst,
                                                  "Tags"                  : "DisMAP, Datasets",
                                                  "Summary"               : summary,
                                                  "Description"           : "This table functions as a look-up table of vales",
                                                  "Credits"               : _credits,
                                                  "Access Constraints"    : access_constraints}

                    del datasets_tb, datasets_tbs, datasets_tbst

                elif "DisMAP_Regions" == dataset_code:

                    #print(f"\tProcessing: DisMAP_Regions")

                    regions_fc   = dataset_code
                    regions_fcs  = f"{dataset_code}_{date_code(project)}"
                    regions_fcst = f"DisMAP Regions {date_code(project)}"

                    __datasets_dict[regions_fc] = {"Dataset Service"       : regions_fcs,
                                                 "Dataset Service Title" : regions_fcst,
                                                 "Tags"                  : "DisMAP Regions",
                                                 "Summary"               : summary,
                                                 "Description"           : "These files contain the spatial boundaries of the NOAA Fisheries Bottom-trawl surveys. This data set covers 8 regions of the United States: Northeast, Southeast, Gulf of Mexico, West Coast, Eastern Bering Sea, Aleutian Islands, Gulf of Alaska, and Hawai'i Islands.",
                                                 "Credits"               : _credits,
                                                 "Access Constraints"    : access_constraints}

                    del regions_fc, regions_fcs, regions_fcst

                elif "Indicators" == dataset_code:

                    #print(f"\tProcessing: Indicators")

                    indicators_tb   = f"{dataset_code}"
                    indicators_tbs  = f"{dataset_code}_{date_code(project)}"
                    indicators_tbst = f"{dataset_code} {date_code(project)}"

                    __datasets_dict[indicators_tb] = {"Dataset Service"    : indicators_tbs,
                                                   "Dataset Service Title" : indicators_tbst,
                                                   "Tags"                  : "DisMAP, Indicators",
                                                   "Summary"               : f"{summary}. This table provides the key metrics used to evaluate a species distribution shift. Information on species distributions is of paramount importance for understanding and preparing for climate-change impacts, and plays a key role in climate-ready fisheries management.",
                                                   "Description"           : f"These data contain the key distribution metrics of center of gravity, range limits, and depth for each species in the portal. This data set covers 8 regions of the United States: Northeast, Southeast, Gulf of Mexico, West Coast, Bering Sea, Aleutian Islands, Gulf of Alaska, and Hawai'i Islands.",
                                                   "Credits"               : _credits,
                                                   "Access Constraints"    : access_constraints}

                    del indicators_tb, indicators_tbs, indicators_tbst

                elif "LayerSpeciesYearImageName" == dataset_code:

                    #print(f"\tProcessing: LayerSpeciesYearImageName")

                    layer_species_year_image_name_tb   = dataset_code
                    layer_species_year_image_name_tbs  = f"{dataset_code}_{date_code(project)}"
                    layer_species_year_image_name_tbst = f"Layer Species Year Image Name Table {date_code(project)}"

                    #print(f"\tProcessing: {layer_species_year_image_name_tb}")

                    __datasets_dict[layer_species_year_image_name_tb] = {"Dataset Service"       : layer_species_year_image_name_tbs,
                                                                       "Dataset Service Title" : layer_species_year_image_name_tbst,
                                                                       "Tags"                  : "DisMAP, Layer Species Year Image Name Table",
                                                                       "Summary"               : summary,
                                                                       "Description"           : "This table functions as a look-up table of values",
                                                                       "Credits"               : _credits,
                                                                       "Access Constraints"    : access_constraints}

                    #print(f"\tLayerSpeciesYearImageName T:   {layer_species_year_image_name_tb}")
                    #print(f"\tLayerSpeciesYearImageName TS:  {layer_species_year_image_name_tbs}")
                    #print(f"\tLayerSpeciesYearImageName TST: {layer_species_year_image_name_tbst}")

                    del layer_species_year_image_name_tb, layer_species_year_image_name_tbs, layer_species_year_image_name_tbst

                elif "Species_Filter" == dataset_code:

                    #print(f"\tProcessing: Species_Filter")

                    species_filter_tb   = dataset_code
                    species_filter_tbs  = f"{dataset_code}_{date_code(project)}"
                    species_filter_tbst = f"Species Filter Table {date_code(project)}"

                    __datasets_dict[species_filter_tb] = {"Dataset Service"       : species_filter_tbs,
                                                        "Dataset Service Title" : species_filter_tbst,
                                                        "Tags"                  : "DisMAP, Species Filter Table",
                                                        "Summary"               : summary,
                                                        "Description"           : "This table functions as a look-up table of values",
                                                        "Credits"               : _credits,
                                                        "Access Constraints"    : access_constraints}

                    #print(f"\tLayerSpeciesYearImageName T:   {species_filter_tb}")
                    #print(f"\tLayerSpeciesYearImageName TS:  {species_filter_tbs}")
                    #print(f"\tLayerSpeciesYearImageName TST: {species_filter_tbst}")

                    del species_filter_tb, species_filter_tbs, species_filter_tbst

                elif "DisMAP_Survey_Info" == dataset_code:

                    #print(f"\tProcessing: DisMAP_Survey_Info")

                    tb   = dataset_code
                    tbs  = f"{dataset_code}_{date_code(project)}"
                    tbst = f"DisMAP Survey Info Table {date_code(project)}"

                    __datasets_dict[tb] = {"Dataset Service"       : tbs,
                                         "Dataset Service Title" : tbst,
                                         "Tags"                  : "DisMAP; DisMAP Survey Info Table",
                                         "Summary"               : summary,
                                         "Description"           : "This table functions as a look-up table of values",
                                         "Credits"               : _credits,
                                         "Access Constraints"    : access_constraints}

                    #print(f"\tLayerSpeciesYearImageName T:   {tb}")
                    #print(f"\tLayerSpeciesYearImageName TS:  {tbs}")
                    #print(f"\tLayerSpeciesYearImageName TST: {tbst}")

                    del tb, tbs, tbst

                else:
                    #print(f"\tProcessing: {dataset_code}")

                    #table    = dataset_code
                    #table_s  = f"{dataset_code}_{date_code(project)}"
                    #table_st = f"{table_s.replace('_',' ')} {date_code(project)}"
                    #print(f"\tProcessing: {table_s}")
                    #__datasets_dict[table] = {"Dataset Service"       : table_s,
                    #                        "Dataset Service Title" : table_st,
                    #                        "Tags"                  : f"DisMAP, {table}",
                    #                        "Summary"               : summary,
                    #                        "Description"           : "Unknown table",
                    #                        "Credits"               : _credits,
                    #                        "Access Constraints"    : access_constraints}

                    #print(f"\tTable:     {table}")
                    #print(f"\tTable TS:  {table_s}")
                    #print(f"\tTable TST: {table_st}")

                    #del table, table_s, table_st

                    raise Exception(f"{dataset_code} is missing")

            else:
                pass

            del summary
            del point_feature_type, distribution_project_code
            del filter_region, filter_sub_region, season
            del dataset_code

        del _credits, access_constraints

        del dataset_codes
        del project_folder, crf_folder
        del project, project_gdb
    except KeyboardInterrupt:
        raise SystemExit
    except:
        traceback.print_exc()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function at line number {inspect.stack()[0][2]}\n\t##--> '{', '.join(rk)}' <--##"); del rk
        return __datasets_dict
    finally:
        if "__datasets_dict" in locals().keys(): del __datasets_dict

def import_basic_template_xml(dataset_path=""):
    try:
        # Import
        from lxml import etree
        from io import StringIO, BytesIO
        from arcpy import metadata as md

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        project_gdb    = os.path.dirname(dataset_path)
        project_folder = os.path.dirname(project_gdb)
        scratch_folder = rf"{project_folder}\Scratch"

        arcpy.env.workspace        = project_gdb
        arcpy.env.scratchWorkspace = rf"{scratch_folder}\scratch.gdb"

        import json
        json_path = rf"{project_folder}\root_dict.json"
        with open(json_path, "r") as json_file:
            root_dict = json.load(json_file)
        del json_file
        del json_path
        del json

##        #print("Creating the Metadata Dictionary. Please wait!!")
##        metadata_dictionary = dataset_title_dict(project_gdb)
##        #print("Creating the Metadata Dictionary. Completed")

        #print(dataset_path)
        dataset_name = os.path.basename(dataset_path)

        print(f"Dataset: {dataset_name}")

##        xml_file = '''<?xml version='1.0' encoding='UTF-8'?>
##                        <metadata xml:lang="en">
##                            <dataIdInfo>
##                                <idCitation>
##                                    <citRespParty>
##                                        <rpIndName>Timothy J Haverland</rpIndName>
##                                        <rpCntInfo>
##                                          <cntAddress addressType="">
##                                            <eMailAdd>tim.haverland@noaa.gov</eMailAdd>
##                                          </cntAddress>
##                                          <cntOnlineRes>
##                                            <linkage>https://www.fisheries.noaa.gov/about/office-science-and-technology</linkage>
##                                          </cntOnlineRes>
##                                        </rpCntInfo>
##                                        <role>
##                                            <RoleCd value="002"/>
##                                        </role>
##                                    </citRespParty>
##                                </idCitation>
##                                <idPoC>
##                                    <rpIndName>Melissa Ann Karp</rpIndName>
##                                    <rpCntInfo>
##                                      <cntAddress addressType="">
##                                        <eMailAdd>melissa.karp@noaa.gov</eMailAdd>
##                                      </cntAddress>
##                                      <cntOnlineRes>
##                                        <linkage>https://www.fisheries.noaa.gov/about/office-science-and-technology</linkage>
##                                      </cntOnlineRes>
##                                    </rpCntInfo>
##                                    <role>
##                                        <RoleCd value="007"/>
##                                    </role>
##                                </idPoC>
##                            </dataIdInfo>
##                            <distInfo>
##                                <distributor>
##                                    <distorCont>
##                                        <rpIndName>NMFS Office of Science and Technology</rpIndName>
##                                        <rpCntInfo>
##                                          <cntAddress addressType="">
##                                            <eMailAdd>tim.haverland@noaa.gov</eMailAdd>
##                                          </cntAddress>
##                                          <cntOnlineRes>
##                                            <linkage>https://www.fisheries.noaa.gov/about/office-science-and-technology</linkage>
##                                          </cntOnlineRes>
##                                        </rpCntInfo>
##                                        <role>
##                                            <RoleCd value="005"/>
##                                        </role>
##                                    </distorCont>
##                                </distributor>
##                            </distInfo>
##                            <mdContact>
##                                <rpIndName Sync="TRUE">John F Kennedy</rpIndName>
##                                <rpCntInfo>
##                                  <cntAddress addressType="">
##                                    <eMailAdd Sync="TRUE">john.f.kennedy@noaa.gov</eMailAdd>
##                                  </cntAddress>
##                                  <cntOnlineRes>
##                                    <linkage Sync="TRUE">https://www.fisheries.noaa.gov/about/office-science-and-technology</linkage>
##                                  </cntOnlineRes>
##                                </rpCntInfo>
##                                <role>
##                                    <RoleCd value="011" Sync="TRUE"/>
##                                </role>
##                            </mdContact>
##                        </metadata>'''

##        xml_file = '''<?xml version='1.0' encoding='UTF-8'?>
##                        <metadata xml:lang="en">
##                            <mdContact Sync="TRUE">
##                                <rpIndName Sync="TRUE">John F Kennedy</rpIndName>
##                                <rpCntInfo Sync="TRUE">
##                                  <cntAddress addressType="" Sync="TRUE">
##                                    <eMailAdd Sync="TRUE">john.f.kennedy@noaa.gov</eMailAdd>
##                                  </cntAddress>
##                                  <cntOnlineRes Sync="TRUE">
##                                    <linkage Sync="TRUE">https://www.fisheries.noaa.gov/about/office-science-and-technology</linkage>
##                                  </cntOnlineRes>
##                                </rpCntInfo>
##                                <role Sync="TRUE">
##                                    <RoleCd value="011" Sync="TRUE"/>
##                                </role>
##                            </mdContact>
##                        </metadata>'''

##        # Parse the XML
##        dataset_md = md.Metadata(dataset_path)
##        #dataset_md.synchronize('ALWAYS')
##        #dataset_md.save()
##        in_md = md.Metadata(rf"C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMap\ArcGIS-Analysis-Python\December 1 2024\Export\WC_TRI_IDW.xml")
##        dataset_md.copy(in_md)
##        #dataset_md.importMetadata(rf"C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMap\ArcGIS-Analysis-Python\December 1 2024\Export\WC_TRI_IDW.xml", "ARCGIS_METADATA")
##        #dataset_md.importMetadata(xml_file, "ARCGIS_METADATA")
##        dataset_md.save()
##        dataset_md.synchronize("OVERWRITE")
##        dataset_md.save()
##        #dataset_md.reload()
##        #dataset_md.synchronize("ALWAYS")
##        #dataset_md.save()
##        #dataset_md.reload()
##        del in_md
##        del dataset_md
##        del xml_file
##
##        tags = "DisMap;"
##        summary = "These data were created as part of the DisMAP project to enable visualization and analysis of changes in fish and invertebrate distributions"
##        description = ""
##        project_credits   = "These data were produced by NMFS OST."
##        access_constraints = "***No Warranty*** The user assumes the entire risk related to its use of these data. NMFS is providing these data 'as is' and NMFS disclaims any and all warranties, whether express or implied, including (without limitation) any implied warranties of merchantability or fitness for a particular purpose. No warranty expressed or implied is made regarding the accuracy or utility of the data on any other system or for general or scientific purposes, nor shall the act of distribution constitute any such warranty. It is strongly recommended that careful attention be paid to the contents of the metadata file associated with these data to evaluate dataset limitations, restrictions or intended use. In no event will NMFS be liable to you or to any third party for any direct, indirect, incidental, consequential, special or exemplary damages or lost profit resulting from any use or misuse of these data."
##
##        dataset_md                   = md.Metadata(dataset_path)
##        dataset_md.title             = f"{dataset_name.replace('_', ' ')}"
##        dataset_md.tags              = f"{tags}{dataset_name.replace('_', ' ')};"
##        dataset_md.summary           = summary
##        dataset_md.description       = f"{description}{dataset_name.replace('_', ' ')}"
##        dataset_md.credits           = project_credits
##        dataset_md.accessConstraints = access_constraints
##        dataset_md.save()
##        dataset_md.synchronize("ALWAYS")
##        dataset_md.save()
##        del dataset_md
##
##        del tags, summary, description, project_credits, access_constraints


        # Option #1
        #empty_md   = md.Metadata()
        #dataset_md = md.Metadata(dataset_path)
        #dataset_md.copy(empty_md)
        #dataset_md.save()
        #del empty_md
        # Option #2
        #empty_md   = md.Metadata(xml_file)
        #dataset_md = md.Metadata(dataset_path)
        #dataset_md.copy(empty_md)
        #dataset_md.save()
        #del empty_md
        # Option #3
        #
        #dataset_md = md.Metadata(dataset_path)
        #dataset_md.copy(in_md)
        #dataset_md.save()
        #del in_md
        # Option #4
        dataset_md = md.Metadata(dataset_path)
        dataset_md.importMetadata(rf"{project_folder}\metadata_template.xml")
        dataset_md.save()
        del dataset_md

        tags = "DisMap;"
        summary = "These data were created as part of the DisMAP project to enable visualization and analysis of changes in fish and invertebrate distributions"
        description = ""
        project_credits   = "These data were produced by NMFS OST."
        access_constraints = "***No Warranty*** The user assumes the entire risk related to its use of these data. NMFS is providing these data 'as is' and NMFS disclaims any and all warranties, whether express or implied, including (without limitation) any implied warranties of merchantability or fitness for a particular purpose. No warranty expressed or implied is made regarding the accuracy or utility of the data on any other system or for general or scientific purposes, nor shall the act of distribution constitute any such warranty. It is strongly recommended that careful attention be paid to the contents of the metadata file associated with these data to evaluate dataset limitations, restrictions or intended use. In no event will NMFS be liable to you or to any third party for any direct, indirect, incidental, consequential, special or exemplary damages or lost profit resulting from any use or misuse of these data."

        dataset_md                   = md.Metadata(dataset_path)
        dataset_md.title             = f"{dataset_name.replace('_', ' ')}"
        dataset_md.tags              = f"{tags}{dataset_name.replace('_', ' ')};"
        dataset_md.summary           = summary
        dataset_md.description       = f"{description}{dataset_name.replace('_', ' ')}"
        dataset_md.credits           = project_credits
        dataset_md.accessConstraints = access_constraints
        dataset_md.save()
        dataset_md.synchronize("ALWAYS")
        dataset_md.save()
        dataset_md.reload()
        export_folder  = rf"{os.path.dirname(os.path.dirname(dataset_path))}\Export"
        dataset_md.saveAsXML(rf"{export_folder}\{os.path.basename(dataset_path)}.xml", "REMOVE_ALL_SENSITIVE_INFO")
        # To parse from a string, use the fromstring() function instead.
        _tree = etree.parse(rf"{export_folder}\{os.path.basename(dataset_path)}.xml", parser=etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
        _root = _tree.getroot()
        _root[:] = sorted(_root, key=lambda x: root_dict[x.tag])
        del _root
        etree.indent(_tree, space='\t')
        _tree.write(rf"{export_folder}\{os.path.basename(dataset_path)}.xml", encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True)
        del _tree
        del export_folder
        del dataset_md

        del tags, summary, description, project_credits, access_constraints


        # Parse the XML
        dataset_md = md.Metadata(dataset_path)
        parser = etree.XMLParser(encoding='UTF-8', remove_blank_text=True)
        target_tree = etree.parse(StringIO(dataset_md.xml), parser=parser)
        #target_tree = etree.parse(xml_file, parser=parser)
        target_root = target_tree.getroot()
        target_root[:] = sorted(target_root, key=lambda x: root_dict[x.tag])
        etree.indent(target_tree, space='\t')
        print(etree.tostring(target_tree, encoding='UTF-8', method='xml', pretty_print=True).decode())
        del parser, dataset_md

        del target_tree, target_root



##        _tree = etree.parse(BytesIO(xml_file), etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
##        _root = _tree.getroot()
##        distributor = target_root.xpath(f"./distInfo/distributor")
##        if len(distributor) == 0:
##            target_root.xpath(f"./distInfo")[0].insert(distInfo_dict["distributor"], _root)
##        elif len(distributor) == 1:
##            distributor[0].getparent().replace(distributor[0], _root)
##        else:
##            pass
##        del _root, _tree, xml_file
##        #print(f"\n\t{etree.tostring(target_root.xpath(f'./distInfo/distributor')[0], encoding='UTF-8', method='xml', pretty_print=True).decode()}\n")
##        del distributor


##        mdFileID = target_root.xpath(f"//mdFileID")
##        if mdFileID is not None and len(mdFileID) == 0:
##            _xml = '<mdFileID>gov.noaa.nmfs.inport:</mdFileID>'
##            _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
##            target_root.insert(root_dict['mdFileID'], _root)
##            del _root, _xml
##        elif mdFileID is not None and len(mdFileID) and len(mdFileID[0]) == 0:
##            mdFileID[0].text = "gov.noaa.nmfs.inport:"
##        elif mdFileID is not None and len(mdFileID) and len(mdFileID[0]) == 1:
##            pass
##        #print(etree.tostring(mdFileID[0], encoding='UTF-8', method='xml', pretty_print=True).decode())
##        del mdFileID
##        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        mdMaint = target_root.xpath(f"//mdMaint")
##        if mdMaint is not None and len(mdMaint) == 0:
##            _xml = '<mdMaint><maintFreq><MaintFreqCd value="009"></MaintFreqCd></maintFreq></mdMaint>'
##            _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
##            target_root.insert(root_dict['mdMaint'], _root)
##            del _root, _xml
##        elif mdMaint is not None and len(mdMaint) and len(mdMaint[0]) == 0:
##            target_root.xpath("./mdMaint/maintFreq/MaintFreqCd")[0].attrib["value"] = "009"
##        elif mdMaint is not None and len(mdMaint) and len(mdMaint[0]) == 1:
##            pass #print(etree.tostring(mdMaint[0], encoding='UTF-8', method='xml', pretty_print=True).decode())
##        else:
##            pass
##        #print(etree.tostring(mdMaint[0], encoding='UTF-8', method='xml', pretty_print=True).decode())
##        del mdMaint
##
##        # No changes needed below
##        #print(etree.tostring(target_tree, encoding='UTF-8', method='xml', pretty_print=True).decode())
##        etree.indent(target_root, space='    ')
##        dataset_md_xml = etree.tostring(target_tree, encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True)
##
##        SaveBackXml = False
##        if SaveBackXml:
##            dataset_md = md.Metadata(dataset_path)
##            dataset_md.xml = dataset_md_xml
##            dataset_md.save()
##            dataset_md.synchronize("ALWAYS")
##            dataset_md.save()
##            #dataset_md.reload()
##            del dataset_md
##        else:
##            pass
##        del SaveBackXml
##        del dataset_md_xml

        # Declared Variables
        del root_dict
        #del target_tree, target_root
        #del metadata_dictionary,
        del dataset_name
        del project_gdb, project_folder, scratch_folder
        # Imports
        del md
        del etree, StringIO, BytesIO
        # Function Parameters
        del dataset_path
    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(arcpy.GetMessages(1))
        raise SystemExit
    except arcpy.ExecuteError:
        #traceback.print_exc()
        arcpy.AddError(arcpy.GetMessages(2))
        raise SystemExit
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

def update_eainfo_xml_elements(dataset_path=""):
    try:
        # Imports
        from lxml import etree
        from io import StringIO, BytesIO
        #import copy
        from arcpy import metadata as md
        # Project modules
        #from src.project_tools import pretty_format_xml_file

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        project_gdb    = os.path.dirname(dataset_path)
        project_folder = os.path.dirname(project_gdb)
        scratch_folder = rf"{project_folder}\Scratch"

        arcpy.env.workspace        = project_gdb
        arcpy.env.scratchWorkspace = rf"{scratch_folder}\scratch.gdb"

        import json
        json_path = rf"{project_folder}\root_dict.json"
        with open(json_path, "r") as json_file:
            root_dict = json.load(json_file)
        del json_file
        del json_path
        del json

        dataset_md = md.Metadata(dataset_path)
        dataset_md.synchronize("ALWAYS")
        dataset_md.save()
        dataset_md.reload()
        dataset_md_xml = dataset_md.xml
        del dataset_md

        # Parse the XML
        parser = etree.XMLParser(encoding='UTF-8', remove_blank_text=True)
        target_tree = etree.parse(StringIO(dataset_md_xml), parser=parser)
        target_root = target_tree.getroot()
        del parser, dataset_md_xml

        dataset_name = os.path.basename(dataset_path)
        print(f"Processing Entity Attributes for dataset: '{dataset_name}'")

        # Root
        mdTimeSt = target_root.find("./mdTimeSt")
        #print(mdTimeSt)
        if mdTimeSt is not None:
            mdTimeSt.getparent().remove(mdTimeSt)
        else:
            pass
        del mdTimeSt

        enttyp   = target_root.find("enttyp")
        if enttyp is not None:
            enttypd  = enttyp.find("enttypd")
            enttypds = enttyp.find("enttypds")
            if enttypd is None:
                _xml = "<enttypd>A collection of geographic features with the same geometry type.</enttypd>"
                _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
                enttyp.insert(0, _root)
                del _root, _xml
            else:
                pass
            if enttypds is None:
                _xml = "<enttypds>Esri</enttypds>"
                _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
                enttyp.insert(0, _root)
                del _root, _xml
            else:
                pass
            del enttypds, enttypd
        else:
            pass
        del enttyp

        # Create a list of fields using the ListFields function
        fields = [f for f in arcpy.ListFields(dataset_path) if f.type not in ["Geometry", "OID"] and f.name not in ["Shape_Area", "Shape_Length"]]
        for field in fields:
            attributes = target_root.xpath(f".//attrlabl[text()='{field.name}']/..")
            if attributes is not None and len(attributes) > 0:
                for attribute in attributes:
                    #print(attribute)
                    #print(etree.tostring(attribute, encoding='UTF-8', method='xml', pretty_print=True).decode())
                    attrdef = attribute.find("./attrdef/..")
                    if attrdef is None:
                        _xml = f"<attrdef Sync='TRUE'>Definition for: {field.name}</attrdef>"
                        _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
                        attribute.insert(7, _root)
                        del _root, _xml
                    else:
                        pass
                    attrdefs = attribute.find("./attrdefs/..")
                    if attrdefs is None:
                        _xml = "<attrdefs Sync='TRUE'>NMFS OST DisMAP 2025</attrdefs>"
                        _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
                        attribute.insert(8, _root)
                        del _root, _xml
                    else:
                        pass
                    attrdomv  = attribute.find("./attrdomv/..")
                    if attrdomv is None:
                        _xml = "<attrdomv><udom Sync='TRUE'>None</udom></attrdomv>"
                        _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
                        attribute.insert(8, _root)
                        del _root, _xml
                    else:
                        pass
                    del attrdef, attrdefs, attrdomv
                    del attribute
            else:
                pass
            del attributes
            del field

        attributes = target_root.xpath(f".//attr")
        for attribute in attributes:
            #print(etree.tostring(attribute, encoding='UTF-8', method='xml', pretty_print=True).decode())
            del attribute
        del attributes
        del fields

        # Metadata
        target_root[:] = sorted(target_root, key=lambda x: root_dict[x.tag])

        # No changes needed below
        #print(etree.tostring(target_tree, encoding='UTF-8', method='xml', pretty_print=True).decode())
        etree.indent(target_tree, space='    ')
        dataset_md_xml = etree.tostring(target_tree, encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True)

        SaveBackXml = True
        if SaveBackXml:
            dataset_md = md.Metadata(dataset_path)
            dataset_md.xml = dataset_md_xml
            dataset_md.save()
            dataset_md.synchronize("CREATED")
            dataset_md.save()
            #_target_tree = etree.parse(StringIO(dataset_md.xml), parser=etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
            #_target_tree.write(rf"{export_folder}\{dataset_name}.xml", pretty_print=True)
            #print(etree.tostring(_target_tree.find("./eainfo"), encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True).decode())
            #del _target_tree
            del dataset_md
        else:
            pass
        del SaveBackXml
        del dataset_md_xml

        # Declared Varaiables
        del dataset_name
        del target_tree, target_root
        del project_gdb, project_folder, scratch_folder, root_dict
        # Imports
        del md, etree, StringIO, BytesIO
        # Function Parameters
        del dataset_path
    except KeyboardInterrupt:
        raise SystemExit
    except:
        traceback.print_exc()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function at line number {inspect.stack()[0][2]}\n\t##--> '{', '.join(rk)}' <--##"); del rk
        return True
    finally:
        pass

def insert_missing_elements(dataset_path):
    try:
        from lxml import etree
        from arcpy import metadata as md
        from io import BytesIO, StringIO
        import copy

        project_gdb    = os.path.dirname(dataset_path)
        project_folder = os.path.dirname(project_gdb)
        project        = os.path.basename(os.path.dirname(project_gdb))
        export_folder  = rf"{project_folder}\Export"
        scratch_folder = rf"{project_folder}\Scratch"

        import json
        json_path = rf"{project_folder}\root_dict.json"
        with open(json_path, "r") as json_file:
            root_dict = json.load(json_file)
        json_path = rf"{project_folder}\esri_dict.json"
        with open(json_path, "r") as json_file:
            esri_dict = json.load(json_file)
        json_path = rf"{project_folder}\dataIdInfo_dict.json"
        with open(json_path, "r") as json_file:
            dataIdInfo_dict = json.load(json_file)
        json_path = rf"{project_folder}\contact_dict.json"
        with open(json_path, "r") as json_file:
            contact_dict = json.load(json_file)
        json_path = rf"{project_folder}\dqInfo_dict.json"
        with open(json_path, "r") as json_file:
            dqInfo_dict = json.load(json_file)
        json_path = rf"{project_folder}\distInfo_dict.json"
        with open(json_path, "r") as json_file:
            distInfo_dict = json.load(json_file)
        #json_path = rf"{project_folder}\RoleCd_dict.json"
        #with open(json_path, "r") as json_file:
        #    RoleCd_dict = json.load(json_file)
        #json_path = rf"{project_folder}\tpCat_dict.json"
        #with open(json_path, "r") as json_file:
        #    tpCat_dict = json.load(json_file)
        del json_file
        del json_path
        del json

        arcpy.env.workspace        = project_gdb
        arcpy.env.scratchWorkspace = rf"{scratch_folder}\scratch.gdb"
        del scratch_folder
        del project_folder
        del project_gdb

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Get contact information
        contacts_xml = rf"{os.environ['USERPROFILE']}\Documents\ArcGIS\Descriptions\contacts.xml"
        contacts_xml_tree = etree.parse(contacts_xml, parser=etree.XMLParser(encoding='UTF-8', remove_blank_text=True)) # To parse from a string, use the fromstring() function instead.
        del contacts_xml

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Get Prefered contact information
        mdContact_rpIndName = contact_dict["mdContact"][0]["rpIndName"]
        mdContact_eMailAdd  = contact_dict["mdContact"][0]["eMailAdd"]
        mdContact_role      = contact_dict["mdContact"][0]["role"]

        citRespParty_rpIndName = contact_dict["citRespParty"][0]["rpIndName"]
        citRespParty_eMailAdd  = contact_dict["citRespParty"][0]["eMailAdd"]
        citRespParty_role      = contact_dict["citRespParty"][0]["role"]

        idPoC_rpIndName = contact_dict["idPoC"][0]["rpIndName"]
        idPoC_eMailAdd  = contact_dict["idPoC"][0]["eMailAdd"]
        idPoC_role      = contact_dict["idPoC"][0]["role"]

        distorCont_rpIndName = contact_dict["distorCont"][0]["rpIndName"]
        distorCont_eMailAdd  = contact_dict["distorCont"][0]["eMailAdd"]
        distorCont_role      = contact_dict["distorCont"][0]["role"]

        srcCitatn_rpIndName = contact_dict["srcCitatn"][0]["rpIndName"]
        srcCitatn_eMailAdd  = contact_dict["srcCitatn"][0]["eMailAdd"]
        srcCitatn_role      = contact_dict["srcCitatn"][0]["role"]

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #print(etree.tostring(target_root, encoding='UTF-8', method='xml', pretty_print=True).decode())

        dataset_md = md.Metadata(dataset_path)
        dataset_md.synchronize("ALWAYS")
        dataset_md.save()
        dataset_md.reload()
        dataset_md_xml = dataset_md.xml
        del dataset_md

        # Parse the XML
        parser = etree.XMLParser(encoding='UTF-8', remove_blank_text=True)
        target_tree = etree.parse(StringIO(dataset_md_xml), parser=parser)
        target_root = target_tree.getroot()
        del parser, dataset_md_xml

        CreaDate = target_root.xpath(f"//Esri/CreaDate")[0].text
        CreaTime = target_root.xpath(f"//Esri/CreaTime")[0].text
        #print(CreaDate, CreaTime)
        CreaDateTime = f"{CreaDate[:4]}-{CreaDate[4:6]}-{CreaDate[6:]}T{CreaTime[:2]}:{CreaTime[2:4]}:{CreaTime[4:6]}"
        #print(f"\tCreaDateTime: {CreaDateTime}")
        #del CreaDateTime
        del CreaDate, CreaTime
        ModDate = target_root.xpath(f"//Esri/ModDate")[0].text
        ModTime = target_root.xpath(f"//Esri/ModTime")[0].text
        #print(ModDate, ModTime)
        ModDateTime = f"{ModDate[:4]}-{ModDate[4:6]}-{ModDate[6:]}T{ModTime[:2]}:{ModTime[2:4]}:{ModTime[4:6]}"
        #print(f"\tModDateTime: {ModDateTime}")
        #del ModDateTime
        del ModDate, ModTime

        dataset_name = os.path.basename(dataset_path)
        print(f"Processing/Updating elements for dataset: '{dataset_name}'")

        xml_file = b'''<?xml version='1.0' encoding='UTF-8'?>
                        <metadata xml:lang="en">
                            <Esri>
                                <ArcGISstyle>ISO 19139 Metadata Implementation Specification GML3.2</ArcGISstyle>
                                <ArcGISProfile>ISO19139</ArcGISProfile>
                                <locales>
                                    <locale xmlns="" language="eng" country="US"/>
                                </locales>
                            </Esri>
                            <dataIdInfo>
                                <idCitation>
                                    <resTitle>feature class name</resTitle>
                                    <resAltTitle>feature class name</resAltTitle>
                                    <collTitle>NMFS OST DisMAP</collTitle>
                                    <presForm>
                                        <PresFormCd value="005" Sync="TRUE"></PresFormCd>
                                        <fgdcGeoform></fgdcGeoform>
                                    </presForm>
                                    <date>
                                        <createDate/>
                                        <pubDate/>
                                        <reviseDate/>
                                    </date>
                                    <citRespParty>
                                        <editorSource>external</editorSource>
                                        <editorDigest>810ad1c47a347c4bf5c88f2ea5077cd5d7a1bdcb</editorDigest>
                                        <rpIndName>Timothy J Haverland</rpIndName>
                                        <rpOrgName>NMFS Office of Science and Technology</rpOrgName>
                                        <rpPosName>GIS App Developer</rpPosName>
                                        <rpCntInfo editorFillOnly="True" editorExpand="True">
                                          <cntAddress addressType="both">
                                            <delPoint>1315 East West Highway</delPoint>
                                            <city>Silver Spring</city>
                                            <adminArea>MD</adminArea>
                                            <postCode>20910-3282</postCode>
                                            <eMailAdd>tim.haverland@noaa.gov</eMailAdd>
                                          </cntAddress>
                                          <cntPhone>
                                            <voiceNum tddtty="">301-427-8137</voiceNum>
                                            <faxNum>301-713-4137</faxNum>
                                          </cntPhone>
                                          <cntHours>0700 - 1800 EST/EDT</cntHours>
                                          <cntOnlineRes>
                                            <linkage>https://www.fisheries.noaa.gov/about/office-science-and-technology</linkage>
                                            <protocol>REST Service</protocol>
                                            <orName>NMFS Office of Science and Technology</orName>
                                            <orDesc>NOAA Fisheries Office of Science and Technology</orDesc>
                                            <orFunct>
                                              <OnFunctCd value="002" />
                                            </orFunct>
                                          </cntOnlineRes>
                                        </rpCntInfo>
                                        <displayName>Timothy J Haverland</displayName>
                                        <editorSave>True</editorSave>
                                        <role>
                                            <RoleCd value="002"/>
                                        </role>
                                    </citRespParty>
                                </idCitation>
                                <themeKeys xmlns="">
                                     <keyword></keyword>
                                     <thesaName>
                                        <resTitle>Global Change Master Directory (GCMD) Science Keywords</resTitle>
                                        <date>
                                            <createDate/>
                                            <pubDate/>
                                            <reviseDate/>
                                        </date>
                                        <citOnlineRes>
                                            <linkage>https://www.fisheries.noaa.gov/inport/help/components/keywords</linkage>
                                            <protocol>REST Service</protocol>
                                            <orName>GCMD</orName>
                                            <orDesc>Global Change Master Directory (GCMD) Science Keywords</orDesc>
                                            <orFunct>
                                                <OnFunctCd value="002"/>
                                            </orFunct>
                                        </citOnlineRes>
                                     </thesaName>
                                     <thesaLang>
                                        <languageCode value="eng"/>
                                        <countryCode value="US"/>
                                     </thesaLang>
                                </themeKeys>
                                <placeKeys xmlns="">
                                     <keyword></keyword>
                                     <thesaName>
                                        <resTitle>Global Change Master Directory (GCMD) Location Keywords</resTitle>
                                        <date>
                                            <createDate></createDate>
                                            <pubDate></pubDate>
                                            <reviseDate></reviseDate>
                                        </date>
                                        <citOnlineRes>
                                            <linkage>https://www.fisheries.noaa.gov/inport/help/components/keywords</linkage>
                                            <protocol>REST Service</protocol>
                                            <orName>GCMD</orName>
                                            <orDesc>Global Change Master Directory (GCMD) Location Keywords</orDesc>
                                            <orFunct>
                                                <OnFunctCd value="002"/>
                                            </orFunct>
                                        </citOnlineRes>
                                     </thesaName>
                                     <thesaLang>
                                        <languageCode value="eng"/>
                                        <countryCode value="US"/>
                                     </thesaLang>
                                </placeKeys>
                                <tempKeys xmlns="">
                                  <keyword></keyword>
                                   <thesaName>
                                      <resTitle>Global Change Master Directory (GCMD) Temporal Data Resolution Keywords</resTitle>
                                      <date>
                                          <createDate></createDate>
                                          <pubDate></pubDate>
                                          <reviseDate/>
                                      </date>
                                      <citOnlineRes>
                                          <linkage>https://www.fisheries.noaa.gov/inport/help/components/keywords</linkage>
                                          <protocol>REST Service</protocol>
                                          <orName>GCMD</orName>
                                          <orDesc>Global Change Master Directory (GCMD) Temporal Data Resolution Keywords</orDesc>
                                          <orFunct>
                                              <OnFunctCd value="002"/>
                                          </orFunct>
                                      </citOnlineRes>
                                   </thesaName>
                                   <thesaLang>
                                      <languageCode value="eng"/>
                                      <countryCode value="US"/>
                                   </thesaLang>
                                </tempKeys>
                                <discKeys>
                                    <keyword></keyword>
                                    <thesaName>
                                        <resTitle>Integrated Taxonomic Information System (ITIS)</resTitle>
                                        <date>
                                            <createDate/>
                                            <pubDate/>
                                            <reviseDate/>
                                        </date>
                                        <citOnlineRes>
                                            <linkage>https://www.itits.org</linkage>
                                            <protocol>REST Service</protocol>
                                            <orName>ITIS</orName>
                                            <orDesc>Integrated Taxonomic Information System (ITIS)</orDesc>
                                            <orFunct>
                                                <OnFunctCd value="002"/>
                                            </orFunct>
                                        </citOnlineRes>
                                    </thesaName>
                                </discKeys>
                                <idStatus>
                                    <ProgCd value="004"/>
                                </idStatus>
                                <idPoC>
                                    <editorSource>external</editorSource>
                                    <editorDigest>c66ffbb333c48d18d81856ec0e0c37ea752bff1a</editorDigest>
                                    <rpIndName>Melissa Ann Karp</rpIndName>
                                    <rpOrgName>NMFS Office of Science and Technology</rpOrgName>
                                    <rpPosName>Fisheries Science Coordinator</rpPosName>
                                    <rpCntInfo editorFillOnly="True" editorExpand="True">
                                      <cntAddress addressType="both">
                                        <delPoint>1315 East West Hwy</delPoint>
                                        <city>Silver Spring</city>
                                        <adminArea>MD</adminArea>
                                        <postCode>20910-3282</postCode>
                                        <eMailAdd>melissa.karp@noaa.gov</eMailAdd>
                                        <country>US</country>
                                      </cntAddress>
                                      <cntPhone>
                                        <voiceNum tddtty="">301-427-8202</voiceNum>
                                        <faxNum>301-713-4137</faxNum>
                                      </cntPhone>
                                      <cntHours>0700 - 1800 EST/EDT</cntHours>
                                      <cntOnlineRes>
                                        <linkage>https://www.fisheries.noaa.gov/about/office-science-and-technology</linkage>
                                        <protocol>REST Service</protocol>
                                        <orName>NMFS Office of Science and Technology</orName>
                                        <orDesc>NOAA Fisheries Office of Science and Technology</orDesc>
                                        <orFunct>
                                          <OnFunctCd value="002" />
                                        </orFunct>
                                      </cntOnlineRes>
                                    </rpCntInfo>
                                    <displayName>Melissa Ann Karp</displayName>
                                    <editorSave>True</editorSave>
                                    <role>
                                        <RoleCd value="007"/>
                                    </role>
                                </idPoC>
                                <resConst>
                                     <LegConsts xmlns="">
                                        <accessConsts>
                                           <RestrictCd value="005"/>
                                        </accessConsts>
                                        <useConsts>
                                           <RestrictCd value="005"/>
                                        </useConsts>
                                        <useLimit>Data License: CC0-1.0
                            Data License URL: https://creativecommons.org/publicdomain/zero/1.0/
                            Data License Statement: These data were produced by NOAA and are not subject to copyright protection in the United States. NOAA waives any potential copyright and related rights in these data worldwide through the Creative Commons Zero 1.0 Universal Public Domain Dedication (CC0-1.0).</useLimit>
                                     </LegConsts>
                                     <SecConsts xmlns="">
                                        <class>
                                           <ClasscationCd value="001"/>
                                        </class>
                                        <classSys>FISMA Low</classSys>
                                     </SecConsts>
                                     <Consts xmlns="">
                                        <useLimit>&lt;DIV STYLE="text-align:Left;"&gt;&lt;DIV&gt;&lt;DIV&gt;&lt;P&gt;&lt;SPAN&gt;***No Warranty*** The user assumes the entire risk related to its use of these data. NMFS is providing these data 'as is' and NMFS disclaims any and all warranties, whether express or implied, including (without limitation) any implied warranties of merchantability or fitness for a particular purpose. No warranty expressed or implied is made regarding the accuracy or utility of the data on any other system or for general or scientific purposes, nor shall the act of distribution constitute any such warranty. It is strongly recommended that careful attention be paid to the contents of the metadata file associated with these data to evaluate dataset limitations, restrictions or intended use. In no event will NMFS be liable to you or to any third party for any direct, indirect, incidental, consequential, special or exemplary damages or lost profit resulting from any use or misuse of these data.&lt;/SPAN&gt;&lt;/P&gt;&lt;/DIV&gt;&lt;/DIV&gt;&lt;/DIV&gt;</useLimit>
                                     </Consts>
                                  </resConst>
                                <resMaint>
                                    <maintFreq>
                                        <MaintFreqCd value="009"></MaintFreqCd>
                                    </maintFreq>
                                </resMaint>
                                <dataLang>
                                    <languageCode value="eng" Sync="TRUE"></languageCode>
                                    <countryCode value="USA" Sync="TRUE"></countryCode>
                                </dataLang>
                                <dataChar>
                                    <CharSetCd value="004"></CharSetCd>
                                </dataChar>
                                <dataExt>
                                    <exDesc></exDesc>
                                    <tempEle>
                                        <TempExtent>
                                            <exTemp>
                                                <TM_Period Sync="TRUE">
                                                    <tmBegin></tmBegin>
                                                    <tmEnd></tmEnd>
                                                </TM_Period>
                                                <TM_Instant Sync="TRUE">
                                                    <tmPosition></tmPosition>
                                                </TM_Instant>
                                            </exTemp>
                                        </TempExtent>
                                    </tempEle>
                                </dataExt>
                                <spatRpType>
                                    <SpatRepTypCd value="001" Sync="TRUE"></SpatRepTypCd>
                                </spatRpType>
                                <tpCat Sync="TRUE"><TopicCatCd value="002"></TopicCatCd></tpCat>
                                <tpCat Sync="TRUE"><TopicCatCd value="007"></TopicCatCd></tpCat>
                                <tpCat Sync="TRUE"><TopicCatCd value="014"></TopicCatCd></tpCat>
                            </dataIdInfo>
                            <dqInfo>
                                <dqScope xmlns="">
                                    <scpLvl>
                                        <ScopeCd value="005" Sync="TRUE"></ScopeCd>
                                    </scpLvl>
                                    <scpLvlDesc xmlns="">
                                        <datasetSet>dataset</datasetSet>
                                    </scpLvlDesc>
                                </dqScope>
                                <report type="DQConcConsis" dimension="horizontal">
                                    <measDesc>Based on a review from DisMAP Team all necessary features are present.</measDesc>
                                     <measResult>
                                        <ConResult>
                                           <conSpec>
                                              <resTitle>Conceptual Consistency Report</resTitle>
                                              <resAltTitle></resAltTitle>
                                              <collTitle>NMFS OST DisMAP</collTitle>
                                              <date>
                                                <createDate></createDate>
                                                <pubDate></pubDate>
                                                <reviseDate></reviseDate>
                                              </date>
                                           </conSpec>
                                           <conExpl>Based on a review from DisMAP Team all necessary features are present.</conExpl>
                                           <conPass>1</conPass>
                                        </ConResult>
                                     </measResult>
                                </report>
                                <report type="DQCompOm" dimension="horizontal">
                                    <measDesc>Based on a review from DisMAP Team all necessary features are present.</measDesc>
                                     <measResult>
                                        <ConResult>
                                           <conSpec>
                                              <resTitle>Completeness Report</resTitle>
                                              <resAltTitle></resAltTitle>
                                              <collTitle>NMFS OST DisMAP</collTitle>
                                              <date>
                                                <createDate></createDate>
                                                <pubDate></pubDate>
                                                <reviseDate></reviseDate>
                                              </date>
                                           </conSpec>
                                           <conExpl>Based on a review from DisMAP Team all necessary features are present.</conExpl>
                                           <conPass>1</conPass>
                                        </ConResult>
                                     </measResult>
                                </report>
                                <dataLineage>
                                    <statement></statement>
                                    <dataSource type="">
                                        <srcDesc>Data for 'region' 'version'</srcDesc>
                                        <srcMedName>
                                            <MedNameCd value="015"/>
                                        </srcMedName>
                                        <srcCitatn>
                                            <resTitle>Source Citation for: </resTitle>
                                            <resAltTitle></resAltTitle>
                                            <collTitle>NMFS OST DisMAP</collTitle>
                                            <citOnlineRes>
                                                <linkage>https://www.fisheries.noaa.gov/about/office-science-and-technology</linkage>
                                                <protocol>REST Service</protocol>
                                                <orName>NMFS Office of Science and Technology</orName>
                                                <orDesc>NOAA Fisheries Office of Science and Technology</orDesc>
                                                <orFunct>
                                                    <OnFunctCd value="002" />
                                                </orFunct>
                                            </citOnlineRes>
                                            <date>
                                                <createDate></createDate>
                                                <pubDate></pubDate>
                                                <reviseDate></reviseDate>
                                            </date>
                                            <presForm>
                                                <fgdcGeoform>document</fgdcGeoform>
                                                <PresFormCd value="001"></PresFormCd>
                                            </presForm>
                                            <citRespParty>
                                                <editorSource>external</editorSource>
                                                <editorDigest>c66ffbb333c48d18d81856ec0e0c37ea752bff1a</editorDigest>
                                                <rpIndName>Melissa Ann Karp</rpIndName>
                                                <rpOrgName>NMFS Office of Science and Technology</rpOrgName>
                                                <rpPosName>Fisheries Science Coordinator</rpPosName>
                                                <rpCntInfo editorFillOnly="True" editorExpand="True">
                                                  <cntAddress addressType="both">
                                                    <delPoint>1315 East West Hwy</delPoint>
                                                    <city>Silver Spring</city>
                                                    <adminArea>MD</adminArea>
                                                    <postCode>20910-3282</postCode>
                                                    <eMailAdd>melissa.karp@noaa.gov</eMailAdd>
                                                    <country>US</country>
                                                  </cntAddress>
                                                  <cntPhone>
                                                    <voiceNum tddtty="">301-427-8202</voiceNum>
                                                    <faxNum>301-713-4137</faxNum>
                                                  </cntPhone>
                                                  <cntHours>0700 - 1800 EST/EDT</cntHours>
                                                  <cntOnlineRes>
                                                    <linkage>https://www.fisheries.noaa.gov/about/office-science-and-technology</linkage>
                                                    <protocol>REST Service</protocol>
                                                    <orName>NMFS Office of Science and Technology</orName>
                                                    <orDesc>NOAA Fisheries Office of Science and Technology</orDesc>
                                                    <orFunct>
                                                      <OnFunctCd value="002" />
                                                    </orFunct>
                                                  </cntOnlineRes>
                                                </rpCntInfo>
                                                <displayName>Melissa Ann Karp</displayName>
                                                <editorSave>True</editorSave>
                                                <role>
                                                    <RoleCd value="008"/>
                                                </role>
                                            </citRespParty>
                                        </srcCitatn>
                                    </dataSource>
                                    <prcStep>
                                        <stepDesc>Geoprocessing Steps for 'region' 'version date'</stepDesc>
                                        <stepDateTm></stepDateTm>
                                        <stepProc>
                                            <editorSource>external</editorSource>
                                            <editorDigest>c66ffbb333c48d18d81856ec0e0c37ea752bff1a</editorDigest>
                                            <rpIndName>Melissa Ann Karp</rpIndName>
                                            <rpOrgName>NMFS Office of Science and Technology</rpOrgName>
                                            <rpPosName>Fisheries Science Coordinator</rpPosName>
                                            <rpCntInfo editorFillOnly="True" editorExpand="True">
                                              <cntAddress addressType="both">
                                                <delPoint>1315 East West Hwy</delPoint>
                                                <city>Silver Spring</city>
                                                <adminArea>MD</adminArea>
                                                <postCode>20910-3282</postCode>
                                                <eMailAdd>melissa.karp@noaa.gov</eMailAdd>
                                                <country>US</country>
                                              </cntAddress>
                                              <cntPhone>
                                                <voiceNum tddtty="">301-427-8202</voiceNum>
                                                <faxNum>301-713-4137</faxNum>
                                              </cntPhone>
                                              <cntHours>0700 - 1800 EST/EDT</cntHours>
                                              <cntOnlineRes>
                                                <linkage>https://www.fisheries.noaa.gov/about/office-science-and-technology</linkage>
                                                <protocol>REST Service</protocol>
                                                <orName>NMFS Office of Science and Technology</orName>
                                                <orDesc>NOAA Fisheries Office of Science and Technology</orDesc>
                                                <orFunct>
                                                  <OnFunctCd value="002" />
                                                </orFunct>
                                              </cntOnlineRes>
                                            </rpCntInfo>
                                            <displayName>Melissa Ann Karp</displayName>
                                            <editorSave>True</editorSave>
                                            <role>
                                                <RoleCd value="009"/>
                                            </role>
                                        </stepProc>
                                        <stepProc>
                                            <editorSource>external</editorSource>
                                            <editorDigest>b212accd6134b5457de3ed1debca061419d927ce</editorDigest>
                                            <rpIndName>John F Kennedy</rpIndName>
                                            <rpOrgName>NMFS Office of Science and Technology</rpOrgName>
                                            <rpPosName>GIS Specialist</rpPosName>
                                            <rpCntInfo editorFillOnly="True" editorExpand="True">
                                              <cntAddress addressType="both">
                                                <delPoint>1315 East West Highway</delPoint>
                                                <city>Silver Spring</city>
                                                <adminArea>MD</adminArea>
                                                <postCode>20910-3282</postCode>
                                                <country>US</country>
                                                <eMailAdd>john.f.kennedy@noaa.gov</eMailAdd>
                                              </cntAddress>
                                              <cntPhone>
                                                <voiceNum tddtty="">301-427-8149</voiceNum>
                                                <faxNum>301-713-4137</faxNum>
                                              </cntPhone>
                                              <cntHours>0930 - 2030 EST/EDT</cntHours>
                                              <cntOnlineRes>
                                                <linkage>https://www.fisheries.noaa.gov/about/office-science-and-technology</linkage>
                                                <protocol>REST Service</protocol>
                                                <orName>NMFS Office of Science and Technology</orName>
                                                <orDesc>NOAA Fisheries Office of Science and Technology</orDesc>
                                                <orFunct>
                                                  <OnFunctCd value="002" />
                                                </orFunct>
                                              </cntOnlineRes>
                                            </rpCntInfo>
                                            <displayName>John F Kennedy</displayName>
                                            <editorSave>True</editorSave>
                                            <role>
                                                <RoleCd value="009"/>
                                            </role>
                                        </stepProc>
                                        <stepSrc type="used">
                                            <srcDesc>DisMAP</srcDesc>
                                            <srcMedName><MedNameCd value="015"/></srcMedName>
                                        </stepSrc>
                                    </prcStep>
                                </dataLineage>
                            </dqInfo>
                            <distInfo>
                                <distFormat>
                                    <formatName Sync="FALSE">ESRI REST Service</formatName>
                                    <formatVer></formatVer>
                                    <fileDecmTech>Uncompressed</fileDecmTech>
                                    <formatInfo></formatInfo>
                                </distFormat>
                                <distributor>
                                    <distorCont>
                                        <editorSource>external</editorSource>
                                        <editorDigest>579ce2e21b888ac8f6ac1dac30f04cddec7a0d7c</editorDigest>
                                        <rpIndName>NMFS Office of Science and Technology</rpIndName>
                                        <rpOrgName>NMFS Office of Science and Technology</rpOrgName>
                                        <rpPosName>GIS App Developer</rpPosName>
                                        <rpCntInfo editorFillOnly="True" editorExpand="True">
                                          <cntAddress addressType="both">
                                            <delPoint>1315 East West Highway</delPoint>
                                            <city>Silver Spring</city>
                                            <adminArea>MD</adminArea>
                                            <postCode>20910-3282</postCode>
                                            <country>US</country>
                                            <eMailAdd>tim.haverland@noaa.gov</eMailAdd>
                                          </cntAddress>
                                          <cntPhone>
                                            <voiceNum tddtty="">301-427-8137</voiceNum>
                                            <faxNum>301-713-4137</faxNum>
                                          </cntPhone>
                                          <cntHours>0700 - 1800 EST/EDT</cntHours>
                                          <cntOnlineRes>
                                            <linkage>https://www.fisheries.noaa.gov/about/office-science-and-technology</linkage>
                                            <protocol>REST Service</protocol>
                                            <orName>NMFS Office of Science and Technology</orName>
                                            <orDesc>NOAA Fisheries Office of Science and Technology</orDesc>
                                            <orFunct>
                                              <OnFunctCd value="002" />
                                            </orFunct>
                                          </cntOnlineRes>
                                        </rpCntInfo>
                                        <displayName>NMFS Office of Science and Technology (Distributor)</displayName>
                                        <editorSave>True</editorSave>
                                        <role>
                                            <RoleCd value="005"/>
                                        </role>
                                    </distorCont>
                                </distributor>
                                <distTranOps xmlns="">
                                    <unitsODist>MB</unitsODist>
                                    <transSize>8</transSize>
                                    <onLineSrc xmlns="">
                                        <linkage>https://services2.arcgis.com/C8EMgrsFcRFL6LrL/arcgis/rest/services/.../FeatureServer</linkage>
                                        <protocol>ESRI REST Service</protocol>
                                        <orName>NMFS Office of Science and Technology</orName>
                                        <orDesc>Dataset Feature Service</orDesc>
                                        <orFunct>
                                           <OnFunctCd value="002"/>
                                        </orFunct>
                                    </onLineSrc>
                                </distTranOps>
                            </distInfo>
                            <mdContact>
                                <editorSource>external</editorSource>
                                <editorDigest>b212accd6134b5457de3ed1debca061419d927ce</editorDigest>
                                <rpIndName>John F Kennedy</rpIndName>
                                <rpOrgName>NMFS Office of Science and Technology</rpOrgName>
                                <rpPosName>GIS Specialist</rpPosName>
                                <rpCntInfo editorFillOnly="True" editorExpand="True">
                                  <cntAddress addressType="both">
                                    <delPoint>1315 East West Highway</delPoint>
                                    <city>Silver Spring</city>
                                    <adminArea>MD</adminArea>
                                    <postCode>20910-3282</postCode>
                                    <country>US</country>
                                    <eMailAdd>john.f.kennedy@noaa.gov</eMailAdd>
                                  </cntAddress>
                                  <cntPhone>
                                    <voiceNum tddtty="">301-427-8149</voiceNum>
                                    <faxNum>301-713-4137</faxNum>
                                  </cntPhone>
                                  <cntHours>0930 - 2030 EST/EDT</cntHours>
                                  <cntOnlineRes>
                                    <linkage>https://www.fisheries.noaa.gov/about/office-science-and-technology</linkage>
                                    <protocol>REST Service</protocol>
                                    <orName>NMFS Office of Science and Technology</orName>
                                    <orDesc>NOAA Fisheries Office of Science and Technology</orDesc>
                                    <orFunct>
                                      <OnFunctCd value="002" />
                                    </orFunct>
                                  </cntOnlineRes>
                                </rpCntInfo>
                                <displayName>John F Kennedy (Metadata Author)</displayName>
                                <editorSave>True</editorSave>
                                <role>
                                    <RoleCd value="011"/>
                                </role>
                            </mdContact>
                        <.>
                         '''

        source_tree = etree.parse(BytesIO(xml_file), etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
        source_root = source_tree.getroot()

        # Merge Target wtih Source
        target_source_merge = xml_tree_merge(target_root, source_root)
        #print(etree.tostring(target_source_merge, encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True).decode())
        # Merge Source wtih Target
        source_target_merge = xml_tree_merge(target_source_merge, target_root)
        #print(etree.tostring(source_target_merge, encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True).decode())
        del target_source_merge
        del source_tree, source_root, xml_file

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        dataset_md_xml = etree.tostring(source_target_merge, encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=False)

        SaveBackXml = False
        if SaveBackXml:
            dataset_md = md.Metadata(dataset_path)
            dataset_md.xml = dataset_md_xml
            dataset_md.save()
            dataset_md.synchronize("CREATED")
            dataset_md.save()
            #dataset_md.reload()
            #dataset_md_xml = dataset_md.xml
            del dataset_md
            # Parse the XML
            #_target_tree = etree.parse(StringIO(dataset_md_xml), parser=etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
            #del dataset_md_xml
            #print(etree.tostring(_target_tree, encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True).decode())
            #del _target_tree
        else:
            pass
        del SaveBackXml
        del dataset_md_xml

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        dataset_md = md.Metadata(dataset_path)
        dataset_md.synchronize("ALWAYS")
        dataset_md.save()
        dataset_md.reload()
        dataset_md_xml = dataset_md.xml
        del dataset_md

        # Parse the XML
        parser = etree.XMLParser(encoding='UTF-8', remove_blank_text=True)
        target_tree = etree.parse(StringIO(dataset_md_xml), parser=parser)
        target_root = target_tree.getroot()
        del parser, dataset_md_xml

##        target_root.xpath("./distInfo/distFormat/formatName")[0].set('Sync', "FALSE")
##        target_root.xpath("./dataIdInfo/envirDesc")[0].set('Sync', "TRUE")

##        for key in root_dict:
##            #print(key)
##            elem = target_root.find(f"./{key}")
##            if elem is not None and len(elem) > 0:
##                #print(elem.tag)
##                pass
##            del elem
##            del key
##
##        # Root
##        mdTimeSt = target_root.find("./mdTimeSt")
##        #print(mdTimeSt)
##        if mdTimeSt is not None:
##            mdTimeSt.getparent().remove(mdTimeSt)
##        else:
##            pass
##        del mdTimeSt

##        # Metadata
##        target_root[:] = sorted(target_root, key=lambda x: root_dict[x.tag])
##        # Esri
##        Esri = target_root.xpath("./Esri")[0]
##        Esri[:] = sorted(Esri, key=lambda x: esri_dict[x.tag])
##        #print(etree.tostring(Esri, encoding='UTF-8', method='xml', pretty_print=True).decode())
##        del Esri
##        # dataIdInfo
##        dataIdInfo = target_root.xpath("./dataIdInfo")[0]
##        dataIdInfo[:] = sorted(dataIdInfo, key=lambda x: dataIdInfo_dict[x.tag])
##        #print(etree.tostring(dataIdInfo, encoding='UTF-8', method='xml', pretty_print=True).decode())
##        del dataIdInfo
##        # dqInfo
##        dqInfo = target_root.xpath("./dqInfo")[0]
##        dqInfo[:] = sorted(dqInfo, key=lambda x: dqInfo_dict[x.tag])
##        #print(etree.tostring(dqInfo, encoding='UTF-8', method='xml', pretty_print=True).decode())
##        del dqInfo
##        # distInfo
##        distInfo = target_root.xpath("./distInfo")[0]
##        distInfo[:] = sorted(distInfo, key=lambda x: distInfo_dict[x.tag])
##        #print(etree.tostring(distInfo, encoding='UTF-8', method='xml', pretty_print=True).decode())
##        del distInfo
        # mdContact
        # mdLang
        # mdHrLv
        # refSysInfo
        # spatRepInfo
        # spdoinfo
        # eainfo

##        enttyp   = target_root.find("enttyp")
##        if enttyp is not None:
##            enttypd  = enttyp.find("enttypd")
##            enttypds = enttyp.find("enttypds")
##            if enttypd is None:
##                _xml = "<enttypd>A collection of geographic features with the same geometry type.</enttypd>"
##                _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
##                enttyp.insert(0, _root)
##                del _root, _xml
##            else:
##                pass
##            if enttypds is None:
##                _xml = "<enttypds>Esri</enttypds>"
##                _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
##                enttyp.insert(0, _root)
##                del _root, _xml
##            else:
##                pass
##            del enttypds, enttypd
##        else:
##            pass
##        del enttyp

        # idCredit completed
        #for idCredit in target_root.xpath("./dataIdInfo/idCredit"):
        #    #print(etree.tostring(idCredit, encoding='UTF-8', method='xml', pretty_print=True).decode())
        #    #idCredit.text = "NOAA Fisheries. 2025.."
        #    del idCredit
        #print(etree.tostring(target_root.xpath("./dataIdInfo/idCredit")[0], encoding='UTF-8', method='xml', pretty_print=True).decode())

##        # resTitle completed
##        resTitle = target_root.xpath("./dataIdInfo/idCitation/resTitle")[0]
##        target_root.xpath("./dqInfo/dataLineage/dataSource/srcCitatn/resTitle")[0].text = resTitle.text
##        #print(f"\tresTitle: {resTitle.text}")
##        #resTitle.text = f""
##        del resTitle
##        resAltTitle = target_root.xpath("./dataIdInfo/idCitation/resAltTitle")[0]
##        target_root.xpath("./dqInfo/dataLineage/dataSource/srcCitatn/resAltTitle")[0].text = resAltTitle.text
##        #print(f"\tresAltTitle: {resAltTitle.text}")
##        #resAltTitle.text = f""
##        del resAltTitle
##        collTitle = target_root.xpath("./dataIdInfo/idCitation/collTitle")[0]
##        #print(f"\tcollTitle: {collTitle.text}")
##        collTitle.text = "NMFS OST DisMAP"
##        target_root.xpath("./dqInfo/dataLineage/dataSource/srcCitatn/collTitle")[0].text = collTitle.text
##        #print(f"\tcollTitle: {collTitle.text}")
##        del collTitle

##        resConst = target_root.xpath("./dataIdInfo/resConst")
##        if len(resConst) == 1:
##            xml_file = b'''<resConst>
##                             <LegConsts xmlns="">
##                                <accessConsts>
##                                   <RestrictCd value="005"/>
##                                </accessConsts>
##                                <useConsts>
##                                   <RestrictCd value="005"/>
##                                </useConsts>
##                                <useLimit>Data License: CC0-1.0
##Data License URL: https://creativecommons.org/publicdomain/zero/1.0/
##Data License Statement: These data were produced by NOAA and are not subject to copyright protection in the United States. NOAA waives any potential copyright and related rights in these data worldwide through the Creative Commons Zero 1.0 Universal Public Domain Dedication (CC0-1.0).
##                                </useLimit>
##                             </LegConsts>
##                             <SecConsts xmlns="">
##                                <class>
##                                   <ClasscationCd value="001"/>
##                                </class>
##                                <classSys>FISMA Low</classSys>
##                             </SecConsts>
##                             <Consts xmlns="">
##                                <useLimit>&lt;DIV STYLE="text-align:Left;"&gt;&lt;DIV&gt;&lt;DIV&gt;&lt;P&gt;&lt;SPAN&gt;***No Warranty*** The user assumes the entire risk related to its use of these data. NMFS is providing these data 'as is' and NMFS disclaims any and all warranties, whether express or implied, including (without limitation) any implied warranties of merchantability or fitness for a particular purpose. No warranty expressed or implied is made regarding the accuracy or utility of the data on any other system or for general or scientific purposes, nor shall the act of distribution constitute any such warranty. It is strongly recommended that careful attention be paid to the contents of the metadata file associated with these data to evaluate dataset limitations, restrictions or intended use. In no event will NMFS be liable to you or to any third party for any direct, indirect, incidental, consequential, special or exemplary damages or lost profit resulting from any use or misuse of these data.&lt;/SPAN&gt;&lt;/P&gt;&lt;/DIV&gt;&lt;/DIV&gt;&lt;/DIV&gt;</useLimit>
##                             </Consts>
##                          </resConst>'''
##            _tree = etree.parse(BytesIO(xml_file), etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
##            _root = _tree.getroot()
##            resConst[0].getparent().replace(resConst[0], _root)
##            del _root, _tree, xml_file
##        else:
##            pass
##        del resConst

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # discKeys, themeKeys, placeKeys, tempKeys
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #searchKeys = target_root.xpath("./dataIdInfo/searchKeys")
        #for searchKey in searchKeys:
        #    #print(etree.tostring(searchKey, encoding='UTF-8', method='xml', pretty_print=True).decode())
        #    del searchKey
        #del searchKeys
##        searchKeys = target_root.xpath("./dataIdInfo/searchKeys")
##        for searchKey in searchKeys:
##            #print(etree.tostring(searchKey, encoding='UTF-8', method='xml', pretty_print=True).decode())
##            for keyword in searchKey.xpath("./keyword"):
##                if isinstance(keyword.text, type(None)):
##                    keyword.getparent().remove(keyword)
##                else:
##                    pass #print(etree.tostring(keyword, encoding='UTF-8', method='xml', pretty_print=True).decode())
##            del searchKey
##        del searchKeys
##        target_root.xpath("./dataIdInfo/searchKeys/keyword")[0].text = f"{species_range_dict[dataset_name]['LISTENTITY']}; ESA; range; NMFS"
##
##        keywords = target_root.xpath("./dataIdInfo/discKeys/keyword")
##        if keywords is not None and len(keywords) and len(keywords[0]) == 0:
##            keyword = target_root.xpath("./dataIdInfo/discKeys/keyword")[0]
##            keyword.text = f"{species_range_dict[dataset_name]['SCIENAME']}"
##            del keyword
##        #elif keywords is not None and len(keywords) and len(keywords[0]) >= 1:
##        #    pass
##        del keywords
##        createDate = target_root.xpath("./dataIdInfo/discKeys/thesaName/date/createDate")
##        if createDate is not None and len(createDate) and len(createDate[0]) == 0:
##            target_root.xpath("./dataIdInfo/discKeys/thesaName/date/createDate")[0].text = CreaDateTime
##        elif createDate is not None and len(createDate) and len(createDate[0]) == 1:
##            pass
##        else:
##            pass
##        del createDate
##        pubDate    = target_root.xpath("./dataIdInfo/discKeys/thesaName/date/pubDate")
##        if pubDate is not None and len(pubDate) and len(pubDate[0]) == 0:
##            target_root.xpath("./dataIdInfo/discKeys/thesaName/date/pubDate")[0].text = CreaDateTime
##        elif pubDate is not None and len(pubDate) and len(pubDate[0]) == 1:
##            pass
##        else:
##            pass
##        del pubDate
##        reviseDate = target_root.xpath("./dataIdInfo/discKeys/thesaName/date/reviseDate")
##        if reviseDate is not None and len(reviseDate) and len(reviseDate[0]) == 0:
##            target_root.xpath("./dataIdInfo/discKeys/thesaName/date/reviseDate")[0].text = ModDateTime
##        elif reviseDate is not None and len(reviseDate) and len(reviseDate[0]) == 1:
##            pass
##        else:
##            pass
##        del reviseDate
##        resTitle = target_root.xpath("./dataIdInfo/discKeys/thesaName/resTitle")
##        if resTitle is not None and len(resTitle) and len(resTitle[0]) == 0:
##            target_root.xpath("./dataIdInfo/discKeys/thesaName/resTitle")[0].text = "Integrated Taxonomic Information System (ITIS)"
##        elif resTitle is not None and len(resTitle) and len(resTitle[0]) == 1:
##            pass
##        else:
##            pass
##        del resTitle
##        discKeys = target_root.xpath("./dataIdInfo/discKeys")
##        for i in range(0, len(discKeys)):
##            #print(etree.tostring(discKeys[i], encoding='UTF-8', method='xml', pretty_print=True).decode())
##            del i
##        del discKeys
##        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        # themeKeys
##        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        keywords = target_root.xpath("./dataIdInfo/themeKeys/keyword")
##        if keywords is not None and len(keywords) and len(keywords[0]) == 0:
##            new_item_name = target_root.find("./Esri/DataProperties/itemProps/itemName").text
##            keyword = target_root.xpath("./dataIdInfo/themeKeys/keyword")[0]
##            keyword.text = f"{species_range_dict[dataset_name]['COMNAME'].title()}; {species_range_dict[dataset_name]['SCIENAME']}; Endangered Species; NMFS"
##            del keyword, new_item_name
##        elif keywords is not None and len(keywords) and len(keywords[0]) >= 1:
##            pass
##        del keywords
##        createDate = target_root.xpath("./dataIdInfo/themeKeys/thesaName/date/createDate")
##        if createDate is not None and len(createDate) and len(createDate[0]) == 0:
##            target_root.xpath("./dataIdInfo/themeKeys/thesaName/date/createDate")[0].text = CreaDateTime
##        elif createDate is not None and len(createDate) and len(createDate[0]) == 1:
##            pass
##        else:
##            pass
##        del createDate
##        pubDate    = target_root.xpath("./dataIdInfo/themeKeys/thesaName/date/pubDate")
##        if pubDate is not None and len(pubDate) and len(pubDate[0]) == 0:
##            target_root.xpath("./dataIdInfo/themeKeys/thesaName/date/pubDate")[0].text = CreaDateTime
##        elif pubDate is not None and len(pubDate) and len(pubDate[0]) == 1:
##            pass
##        else:
##            pass
##        del pubDate
##        reviseDate = target_root.xpath("./dataIdInfo/themeKeys/thesaName/date/reviseDate")
##        if reviseDate is not None and len(reviseDate) and len(reviseDate[0]) == 0:
##            target_root.xpath("./dataIdInfo/themeKeys/thesaName/date/reviseDate")[0].text = ModDateTime
##        elif reviseDate is not None and len(reviseDate) and len(reviseDate[0]) == 1:
##            pass
##        else:
##            pass
##        del reviseDate
##        resTitle = target_root.xpath("./dataIdInfo/themeKeys/thesaName/resTitle")
##        if resTitle is not None and len(resTitle) and len(resTitle[0]) == 0:
##            target_root.xpath("./dataIdInfo/themeKeys/thesaName/resTitle")[0].text = "Global Change Master Directory (GCMD) Science Keyword"
##        elif resTitle is not None and len(resTitle) and len(resTitle[0]) == 1:
##            pass
##        else:
##            pass
##        del resTitle
##        themeKeys = target_root.xpath("./dataIdInfo/themeKeys")
##        for i in range(0, len(themeKeys)):
##            #print(etree.tostring(themeKeys[i], encoding='UTF-8', method='xml', pretty_print=True).decode())
##            del i
##        del themeKeys
##        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        # placeKeys
##        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        keywords = target_root.xpath("./dataIdInfo/placeKeys/keyword")
##        if keywords is not None and len(keywords) and len(keywords[0]) == 0:
##            new_item_name = target_root.find("./Esri/DataProperties/itemProps/itemName").text
##            keyword = target_root.xpath("./dataIdInfo/placeKeys/keyword")[0]
##            keyword.text = f"Enter place/geography keywords for {new_item_name}, separated by a semicolon"
##            del keyword, new_item_name
##        elif keywords is not None and len(keywords) and len(keywords[0]) >= 1:
##            pass
##        del keywords
##        createDate = target_root.xpath("./dataIdInfo/placeKeys/thesaName/date/createDate")
##        if createDate is not None and len(createDate) and len(createDate[0]) == 0:
##            target_root.xpath("./dataIdInfo/placeKeys/thesaName/date/createDate")[0].text = CreaDateTime
##        elif createDate is not None and len(createDate) and len(createDate[0]) == 1:
##            pass
##        else:
##            pass
##        del createDate
##        pubDate = target_root.xpath("./dataIdInfo/placeKeys/thesaName/date/pubDate")
##        if pubDate is not None and len(pubDate) and len(pubDate[0]) == 0:
##            target_root.xpath("./dataIdInfo/placeKeys/thesaName/date/pubDate")[0].text = CreaDateTime
##        elif pubDate is not None and len(pubDate) and len(pubDate[0]) == 1:
##            pass
##        else:
##            pass
##        del pubDate
##        reviseDate = target_root.xpath("./dataIdInfo/placeKeys/thesaName/date/reviseDate")
##        if reviseDate is not None and len(reviseDate) and len(reviseDate[0]) == 0:
##            target_root.xpath("./dataIdInfo/placeKeys/thesaName/date/reviseDate")[0].text = ModDateTime
##        elif reviseDate is not None and len(reviseDate) and len(reviseDate[0]) == 1:
##            pass
##        else:
##            pass
##        del reviseDate
##        resTitle = target_root.xpath("./dataIdInfo/placeKeys/thesaName/resTitle")
##        if resTitle is not None and len(resTitle) and len(resTitle[0]) == 0:
##            target_root.xpath("./dataIdInfo/placeKeys/thesaName/resTitle")[0].text = "Global Change Master Directory (GCMD) Location Keywords"
##        elif resTitle is not None and len(resTitle) and len(resTitle[0]) == 1:
##            pass
##        else:
##            pass
##        del resTitle
##        placeKeys = target_root.xpath("./dataIdInfo/placeKeys")
##        for i in range(0, len(placeKeys)):
##            #print(etree.tostring(placeKeys[i], encoding='UTF-8', method='xml', pretty_print=True).decode())
##            del i
##        del placeKeys
##        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        # tempKeys
##        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        keywords = target_root.xpath("./dataIdInfo/tempKeys/keyword")
##        if keywords is not None and len(keywords) and len(keywords[0]) == 0:
##            new_item_name = target_root.find("./Esri/DataProperties/itemProps/itemName").text
##            keyword = target_root.xpath("./dataIdInfo/tempKeys/keyword")[0]
##            keyword.text = f"Enter temporal keywords (e.g. year, year range, season, etc.) for {new_item_name}, separated by a semicolon"
##            del keyword, new_item_name
##        elif keywords is not None and len(keywords) and len(keywords[0]) >= 1:
##            pass
##        del keywords
##        createDate = target_root.xpath("./dataIdInfo/tempKeys/thesaName/date/createDate")
##        if createDate is not None and len(createDate) and len(createDate[0]) == 0:
##            target_root.xpath("./dataIdInfo/tempKeys/thesaName/date/createDate")[0].text = CreaDateTime
##        elif createDate is not None and len(createDate) and len(createDate[0]) == 1:
##            pass
##        else:
##            pass
##        del createDate
##        pubDate = target_root.xpath("./dataIdInfo/tempKeys/thesaName/date/pubDate")
##        if pubDate is not None and len(pubDate) and len(pubDate[0]) == 0:
##            target_root.xpath("./dataIdInfo/tempKeys/thesaName/date/pubDate")[0].text = CreaDateTime
##        elif pubDate is not None and len(pubDate) and len(pubDate[0]) == 1:
##            pass
##        else:
##            pass
##        del pubDate
##        reviseDate = target_root.xpath("./dataIdInfo/tempKeys/thesaName/date/reviseDate")
##        if reviseDate is not None and len(reviseDate) and len(reviseDate[0]) == 0:
##            target_root.xpath("./dataIdInfo/tempKeys/thesaName/date/reviseDate")[0].text = ModDateTime
##        elif reviseDate is not None and len(reviseDate) and len(reviseDate[0]) == 1:
##            pass
##        else:
##            pass
##        del reviseDate
##        resTitle = target_root.xpath("./dataIdInfo/tempKeys/thesaName/resTitle")
##        if resTitle is not None and len(resTitle) and len(resTitle[0]) == 0:
##            target_root.xpath("./dataIdInfo/tempKeys/thesaName/resTitle")[0].text = "Global Change Master Directory (GCMD) Temporal Data Resolution Keywords"
##        elif resTitle is not None and len(resTitle) and len(resTitle[0]) == 1:
##            pass
##        else:
##            pass
##        del resTitle
##        tempKeys = target_root.xpath("./dataIdInfo/tempKeys")
##        for i in range(0, len(tempKeys)):
##            #print(etree.tostring(tempKeys[i], encoding='UTF-8', method='xml', pretty_print=True).decode())
##            del i
##        del tempKeys
##        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        # Data Extent
##        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        dataExt = target_root.xpath("./dataIdInfo/dataExt")[0]
##        exDesc = dataExt.xpath("//exDesc")
##        if len(exDesc) == 0:
##            _xml = "<exDesc>[Location extent description]. The data represents an approximate distribution of the listed entity based on the best available information from [date of first source] to [date of final species expert review].</exDesc>"
##            _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
##            dataExt.insert(0, _root)
##            del _root, _xml
##        elif len(exDesc) == 1:
##            exDesc[0].text = "[Location extent description]. The data represents an approximate distribution of the listed entity based on the best available information from [date of first source] to [date of final species expert review]."
##        else:
##            pass
##        del exDesc
##        tempEle = dataExt.xpath("//tempEle")
##        if len(tempEle) == 0:
##            _xml = f'<tempEle><TempExtent><exTemp><TM_Period Sync="TRUE"> \
##                     <tmBegin>{CreaDateTime}</tmBegin><tmEnd>{ModDateTime}</tmEnd></TM_Period><TM_Instant Sync="TRUE"> \
##                     <tmPosition>{ModDateTime}</tmPosition></TM_Instant></exTemp></TempExtent></tempEle>'
##            _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
##            dataExt.insert(2, _root)
##            del _root, _xml
##        elif len(tempEle) == 1:
##            _xml = f'<tempEle><TempExtent><exTemp><TM_Period Sync="TRUE"> \
##                     <tmBegin>{CreaDateTime}</tmBegin><tmEnd>{ModDateTime}</tmEnd></TM_Period><TM_Instant Sync="TRUE"> \
##                     <tmPosition>{ModDateTime}</tmPosition></TM_Instant></exTemp></TempExtent></tempEle>'
##            _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
##            tempEle[0].getparent().replace(tempEle[0], _root)
##            del _root, _xml
##        del tempEle
##        del dataExt
        #dataExt = target_root.xpath("./dataIdInfo/dataExt")
        #for i in range(0, len(dataExt)):
        #    #print(etree.tostring(dataExt[i], encoding='UTF-8', method='xml', pretty_print=True).decode())
        #    del i
        #del dataExt
        #dataExt = target_root.xpath("./dataIdInfo/dataExt")
        #for i in range(1, len(dataExt)):
        #    dataExt[i].getparent().remove(dataExt[i])
        #    del i
        #del dataExt
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        #target_root.xpath("./dqInfo/dqScope/scpLvl/ScopeCd")[0].set('value', "005")
##        PresFormCd   = target_root.xpath("./dataIdInfo/idCitation/presForm/PresFormCd")[0]
##        fgdcGeoform  = target_root.xpath("./dataIdInfo/idCitation/presForm/fgdcGeoform")[0]
##        SpatRepTypCd = target_root.xpath("./dataIdInfo/spatRpType/SpatRepTypCd")[0]
##        PresFormCd.set('Sync', "TRUE")
##        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        # SpatRepTypCd "Empty" "001" (vector) "002" (raster/grid) "003" (tabular)
##        # PresFormCd           "005"          "003"               "011"
##        # fgdcGeoform          "vector data"  "raster data"       "tabular data"
##        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        datasetSet   = target_root.xpath("./dqInfo/dqScope/scpLvlDesc/datasetSet")[0]
##        if SpatRepTypCd.get("value") == "001":
##            PresFormCd.set("value", "005")
##            fgdcGeoform.text = "vector digital data"
##            datasetSet.text  = "Vector Digital Data"
##        elif SpatRepTypCd.get("value") == "002":
##            PresFormCd.set("value", "003")
##            fgdcGeoform.text = "raster digital data"
##            datasetSet.text  = "Raster Digital Data"
##        elif SpatRepTypCd.get("value") == "003":
##            PresFormCd.set("value", "011")
##            fgdcGeoform.text = "tabular digital data"
##            datasetSet.text  = "Tabular Digital Data"
##        else:
##            pass
##        #print("------" * 10)
##        #print(etree.tostring(SpatRepTypCd, encoding='UTF-8', method='xml', pretty_print=True).decode())
##        #print(etree.tostring(target_root.xpath("./dataIdInfo/idCitation/presForm")[0], encoding='UTF-8', method='xml', pretty_print=True).decode())
##        #print(etree.tostring(target_root.xpath("./dqInfo/dqScope")[0], encoding='UTF-8', method='xml', pretty_print=True).decode())
##        #print("------" * 10)
##        del datasetSet, SpatRepTypCd, fgdcGeoform, PresFormCd
##        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        formatName = target_root.xpath("./distInfo/distFormat/formatName")[0]
##        envirDesc = target_root.xpath("./dataIdInfo/envirDesc")[0]
##        envirDesc.set('Sync', "TRUE")
##        target_root.xpath("./distInfo/distFormat/fileDecmTech")[0].text = "Uncompressed"
##        #                                                        # 001 = Vector
##        #'''<spatRpType>                                         # 002 = Grid
##        # <SpatRepTypCd value="003" Sync="TRUE"></SpatRepTypCd>  # 003 = Text Table
##        #</spatRpType>'''
##        #format_name_text = ""
##        #try:
##        #    GeoObjTypCd = target_root.xpath("./spatRepInfo/VectSpatRep/geometObjs/geoObjTyp/GeoObjTypCd")[0].get("value")
##        #    if GeoObjTypCd == "002":
##        #       format_name_text = "ESRI File Geodatabase"
##        #    del GeoObjTypCd
##        #except:
##        #    format_name_text = "ESRI Geodatabase Table"
##        formatName.text = "ESRI REST Service"
##        formatVer_text = str.rstrip(str.lstrip(envirDesc.text))
##        formatVer = target_root.xpath("./distInfo/distFormat/formatVer")[0]
##        formatVer.text = str.rstrip(str.lstrip(formatVer_text))
##        del formatVer_text
##        del envirDesc
##        del formatVer
##        del formatName
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        mdFileID = target_root.xpath(f"//mdFileID")
##        if mdFileID is not None and len(mdFileID) == 0:
##            _xml = '<mdFileID>gov.noaa.nmfs.inport:</mdFileID>'
##            _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
##            target_root.insert(root_dict['mdFileID'], _root)
##            del _root, _xml
##        elif mdFileID is not None and len(mdFileID) and len(mdFileID[0]) == 0:
##            mdFileID[0].text = "gov.noaa.nmfs.inport:"
##        elif mdFileID is not None and len(mdFileID) and len(mdFileID[0]) == 1:
##            pass
##        #print(etree.tostring(mdFileID[0], encoding='UTF-8', method='xml', pretty_print=True).decode())
##        del mdFileID
##        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        mdMaint = target_root.xpath(f"//mdMaint")
##        if mdMaint is not None and len(mdMaint) == 0:
##            _xml = '<mdMaint><maintFreq><MaintFreqCd value="009"></MaintFreqCd></maintFreq></mdMaint>'
##            _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
##            target_root.insert(root_dict['mdMaint'], _root)
##            del _root, _xml
##        elif mdMaint is not None and len(mdMaint) and len(mdMaint[0]) == 0:
##            target_root.xpath("./mdMaint/maintFreq/MaintFreqCd")[0].attrib["value"] = "009"
##        elif mdMaint is not None and len(mdMaint) and len(mdMaint[0]) == 1:
##            pass #print(etree.tostring(mdMaint[0], encoding='UTF-8', method='xml', pretty_print=True).decode())
##        else:
##            pass
##        #print(etree.tostring(mdMaint[0], encoding='UTF-8', method='xml', pretty_print=True).decode())
##        del mdMaint
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        distorTran = target_root.xpath("//distorTran")
##        for _distorTran in distorTran:
##            _distorTran.tag = "distTranOps"
##            del _distorTran
##        del distorTran

##        distTranOps = target_root.xpath("//distTranOps")
##        for i in range(0, len(distTranOps)):
##            if i == 0:
##                xml_file = b'''<distTranOps xmlns="">
##                                <unitsODist>MB</unitsODist>
##                                <transSize>0</transSize>
##                                <onLineSrc xmlns="">
##                                    <linkage>https://services2.arcgis.com/C8EMgrsFcRFL6LrL/arcgis/rest/services/.../FeatureServer</linkage>
##                                    <protocol>ESRI REST Service</protocol>
##                                    <orName>NMFS Office of Science and Technology</orName>
##                                    <orDesc>Dataset Feature Service</orDesc>
##                                    <orFunct>
##                                       <OnFunctCd value="002"/>
##                                    </orFunct>
##                                </onLineSrc>
##                              </distTranOps>'''
##                _tree = etree.parse(BytesIO(xml_file), etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
##                _root = _tree.getroot()
##                distTranOps[i].getparent().replace(distTranOps[i], _root)
##                del _root, _tree, xml_file
##            elif i > 0:
##                distTranOps[i].getparent().remove(distTranOps[i])
##            else:
##                pass
##            del i
##        del distTranOps
        #print(etree.tostring(target_root.xpath("./distInfo")[0], encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True).decode())
        #print(etree.tostring(target_root.xpath("./Esri/DataProperties/itemProps")[0], encoding='UTF-8', method='xml', pretty_print=True).decode())
##        new_item_name = target_root.find("./Esri/DataProperties/itemProps/itemName").text
##        new_item_name = new_item_name.replace("IDW_Sample_Locations", "Sample_Locations") if "Sample_Locations" in new_item_name else new_item_name
##        onLineSrcs = target_root.findall("./distInfo/distTranOps/onLineSrc")
##        for onLineSrc in onLineSrcs:
##            if onLineSrc.find('./protocol').text == "ESRI REST Service":
##                old_linkage_element = onLineSrc.find('./linkage')
##                old_linkage = old_linkage_element.text
##                #print(old_linkage, flush=True)
##                old_item_name = old_linkage[old_linkage.find("/services/")+len("/services/"):old_linkage.find("/FeatureServer")]
##                new_linkage = old_linkage.replace(old_item_name, f"{new_item_name}_{date_code(project)}")
##                #print(new_linkage, flush=True)
##                old_linkage_element.text = new_linkage
##                #print(old_linkage_element.text, flush=True)
##                del old_linkage_element
##                del old_item_name, old_linkage, new_linkage
##            else:
##                pass
##            del onLineSrc
##        del onLineSrcs, new_item_name
##        #print(etree.tostring(target_root.xpath("./distInfo")[0], encoding='UTF-8', method='xml', pretty_print=True).decode())

##        xml_file = b'''<distributor>
##                        <distorCont>
##                            <editorSource>external</editorSource>
##                            <editorDigest>579ce2e21b888ac8f6ac1dac30f04cddec7a0d7c</editorDigest>
##                            <rpIndName>NMFS Office of Science and Technology</rpIndName>
##                            <rpOrgName>NMFS Office of Science and Technology</rpOrgName>
##                            <rpPosName>GIS App Developer</rpPosName>
##                            <rpCntInfo editorFillOnly="True" editorExpand="True">
##                              <cntAddress addressType="both">
##                                <delPoint>1315 East West Highway</delPoint>
##                                <city>Silver Spring</city>
##                                <adminArea>MD</adminArea>
##                                <postCode>20910-3282</postCode>
##                                <country>US</country>
##                                <eMailAdd>tim.haverland@noaa.gov</eMailAdd>
##                              </cntAddress>
##                              <cntPhone>
##                                <voiceNum tddtty="">301-427-8137</voiceNum>
##                                <faxNum>301-713-4137</faxNum>
##                              </cntPhone>
##                              <cntHours>0700 - 1800 EST/EDT</cntHours>
##                              <cntOnlineRes>
##                                <linkage>https://www.fisheries.noaa.gov/about/office-science-and-technology</linkage>
##                                <protocol>REST Service</protocol>
##                                <orName>NMFS Office of Science and Technology</orName>
##                                <orDesc>NOAA Fisheries Office of Science and Technology</orDesc>
##                                <orFunct>
##                                  <OnFunctCd value="002" />
##                                </orFunct>
##                              </cntOnlineRes>
##                            </rpCntInfo>
##                            <displayName>NMFS Office of Science and Technology (Distributor)</displayName>
##                            <editorSave>True</editorSave>
##                            <role>
##                                <RoleCd value="005"/>
##                            </role>
##                        </distorCont>
##                    </distributor>
##                    '''
##        _tree = etree.parse(BytesIO(xml_file), etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
##        _root = _tree.getroot()
##        distributor = target_root.xpath(f"./distInfo/distributor")[0]
##        distributor.getparent().replace(distributor, _root)
##        del _root, _tree, xml_file
##        #print(f"\n\t{etree.tostring(target_root.xpath(f'./distInfo/distributor')[0], encoding='UTF-8', method='xml', pretty_print=True).decode()}\n")
##        del distributor

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # statement
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        statement = target_root.xpath("./dqInfo/dataLineage/statement")
##        if statement is not None and len(statement) == 0:
##            pass # Need to insert statement
##        elif statement is not None and len(statement) and len(statement[0]) == 0:
##            target_root.xpath("./dqInfo/dataLineage/statement")[0].text = "Need to update datalienage statement"
##        elif statement is not None and len(statement) and len(statement[0]) == 1:
##            pass
##        elif statement is not None and len(statement) and len(statement[0]) >= 1:
##            pass
##        else:
##            pass
##        #print(f"\n\t{etree.tostring(statement[0], encoding='UTF-8', method='xml', pretty_print=True).decode()}\n")
##        del statement
##        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        # srcDesc
##        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        srcDesc = target_root.xpath("./dqInfo/dataLineage/dataSource/srcDesc")
##        if srcDesc is not None and len(srcDesc) == 0:
##            pass # Need to insert srcDesc
##        elif srcDesc is not None and len(srcDesc) and len(srcDesc[0]) == 0:
##            target_root.xpath("./dqInfo/dataLineage/dataSource/srcDesc")[0].text = "Need to update srcDesc"
##        elif srcDesc is not None and len(srcDesc) and len(srcDesc[0]) == 1:
##            pass
##        elif srcDesc is not None and len(srcDesc) and len(srcDesc[0]) >= 1:
##            pass
##        else:
##            pass
##        #print(f"\n\t{etree.tostring(srcDesc[0], encoding='UTF-8', method='xml', pretty_print=True).decode()}\n")
##        del srcDesc
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # prcStep
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        stepProcs = target_root.xpath("./dqInfo/dataLineage/prcStep/stepProc")
##        for stepProc in stepProcs:
##            rpIndName = stepProc.find("rpIndName")
##            if rpIndName is None:
##                stepProc.getparent().remove(stepProc)
##            else:
##                pass
##            del rpIndName
##            #print(f"{etree.tostring(stepProc, encoding='UTF-8', method='xml', pretty_print=True).decode()}")
##            del stepProc
##        del stepProcs

##        _report = target_root.xpath(f"./dqInfo/report[@type='DQConcConsis']")
##        if len(_report) == 1:
##            _xml = '''<report type="DQConcConsis" dimension="horizontal">
##                        <measDesc>Based on a review from DisMAP Team all necessary features are present.</measDesc>
##                         <measResult>
##                            <ConResult>
##                               <conSpec>
##                                  <resTitle>Conceptual Consistency Report</resTitle>
##                                  <resAltTitle></resAltTitle>
##                                  <collTitle>NMFS OST DisMAP</collTitle>
##                                  <date>
##                                    <createDate></createDate>
##                                    <pubDate></pubDate>
##                                    <reviseDate></reviseDate>
##                                  </date>
##                               </conSpec>
##                               <conExpl>Based on a review from DisMAP Team all necessary features are present.</conExpl>
##                               <conPass>1</conPass>
##                            </ConResult>
##                         </measResult>
##                    </report>'''
##            _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
##            #print(f"{etree.tostring(_root, encoding='UTF-8', method='xml', pretty_print=True).decode()}")
##            #raise SystemExit
##            _report[0].getparent().replace(_report[0], _root)
##            del _root, _xml
##        else:
##            pass
##        del _report
##
##        _report = target_root.xpath(f"./dqInfo/report[@type='DQCompOm']")
##        if len(_report) == 1:
##            _xml = '''<report type="DQCompOm" dimension="horizontal">
##                        <measDesc>Based on a review from DisMAP Team all necessary features are present.</measDesc>
##                         <measResult>
##                            <ConResult>
##                               <conSpec>
##                                  <resTitle>Completeness Report</resTitle>
##                                  <resAltTitle></resAltTitle>
##                                  <collTitle>NMFS OST DisMAP</collTitle>
##                                  <date>
##                                    <createDate></createDate>
##                                    <pubDate></pubDate>
##                                    <reviseDate></reviseDate>
##                                  </date>
##                               </conSpec>
##                               <conExpl>Based on a review from DisMAP Team all necessary features are present.</conExpl>
##                               <conPass>1</conPass>
##                            </ConResult>
##                         </measResult>
##                    </report>'''
##            _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
##            _report[0].getparent().replace(_report[0], _root)
##            del _root, _xml
##        else:
##            pass
##        del _report


##        prcStep = target_root.xpath("./dqInfo/dataLineage/prcStep")
##        #print(len(prcStep))
##        if prcStep is not None and len(prcStep) == 0:
##            pass
##            #print("prcStep missing")
##        elif prcStep is not None and len(prcStep) and len(prcStep[0]) == 0:
##            #print("found empty element prcStep. Now adding content.")
##            target_root.xpath("./dqInfo/dataLineage/prcStep")[0].text = "Update Metadata 2025"
##        elif prcStep is not None and len(prcStep) and len(prcStep[0]) >= 1:
##            for i in range(0, len(prcStep)):
##                stepDesc = prcStep[i].xpath("./stepDesc")[0]
##                if stepDesc.text == "pre-Update Metadata 2025":
##                    prcStep[i].xpath("./stepDateTm")[0].text = CreaDateTime
##                elif stepDesc.text == "Update Metadata 2025":
##                    prcStep[i].xpath("./stepDateTm")[0].text = ModDateTime
##                elif stepDesc.text not in ["pre-Update Metadata 2025", "Update Metadata 2025"]:
##                    prcStep[i].xpath("./stepDateTm")[0].text = CreaDateTime
##                del stepDesc
##                del i
##        else:
##            pass
##        del prcStep

        #srcDesc = target_root.xpath("./dqInfo/dataLineage/dataSource/srcDesc")
        #for _srcDesc in srcDesc:
        #    #print(f"\t{etree.tostring(_srcDesc, encoding='UTF-8', method='xml', pretty_print=True).decode()}")
        #    del _srcDesc
        #del srcDesc
        # print(etree.tostring(reports[0].getparent(), encoding='UTF-8', method='xml', pretty_print=True).decode())
        #del dataSources
        #dataLineage = target_root.xpath("./dqInfo/dataLineage")
        #for i in range(0, len(dataLineage)):
        #    #print(etree.tostring(dataLineage[i], encoding='UTF-8', method='xml', pretty_print=True).decode())
        #    del i
        #del dataLineage
        #distInfo = target_root.xpath("./distInfo")[0]
        #print(etree.tostring(distInfo, encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True).decode())
        #del distInfo

##        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        # Reorder Elements
##        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        # Metadata
##        target_root[:] = sorted(target_root, key=lambda x: root_dict[x.tag])
##        # Esri
##        Esri = target_root.xpath("./Esri")[0]
##        Esri[:] = sorted(Esri, key=lambda x: esri_dict[x.tag])
##        #print(etree.tostring(Esri, encoding='UTF-8', method='xml', pretty_print=True).decode())
##        del Esri
##        # dataIdInfo
##        dataIdInfo = target_root.xpath("./dataIdInfo")[0]
##        dataIdInfo[:] = sorted(dataIdInfo, key=lambda x: dataIdInfo_dict[x.tag])
##        #print(etree.tostring(dataIdInfo, encoding='UTF-8', method='xml', pretty_print=True).decode())
##        del dataIdInfo
##        # dqInfo
##        dqInfo = target_root.xpath("./dqInfo")[0]
##        dqInfo[:] = sorted(dqInfo, key=lambda x: dqInfo_dict[x.tag])
##        #print(etree.tostring(dqInfo, encoding='UTF-8', method='xml', pretty_print=True).decode())
##        del dqInfo
##        # distInfo
##        distInfo = target_root.xpath("./distInfo")[0]
##        distInfo[:] = sorted(distInfo, key=lambda x: distInfo_dict[x.tag])
##        #print(etree.tostring(distInfo, encoding='UTF-8', method='xml', pretty_print=True).decode())
##        del distInfo
##        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #print(etree.tostring(target_tree, encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True).decode())
        etree.indent(target_tree, space='    ')
        dataset_md_xml = etree.tostring(target_tree, encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True)

        SaveBackXml = False
        if SaveBackXml:
            dataset_md = md.Metadata(dataset_path)
            dataset_md.xml = dataset_md_xml
            dataset_md.save()
            dataset_md.synchronize("ALWAYS")
            dataset_md.save()
            #_target_tree = etree.parse(StringIO(dataset_md.xml), parser=etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
            #_target_tree.write(rf"{export_folder}\{dataset_name}.xml", pretty_print=True)
            #print(etree.tostring(_target_tree, encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True).decode())
            #del _target_tree
            del dataset_md
        else:
            pass
        del SaveBackXml
        del dataset_md_xml

        # Declared Variables
        del project
        del contacts_xml_tree
        del source_target_merge
        del export_folder
        del mdContact_rpIndName, mdContact_eMailAdd, mdContact_role
        del citRespParty_rpIndName, citRespParty_eMailAdd, citRespParty_role
        del idPoC_rpIndName, idPoC_eMailAdd, idPoC_role
        del distorCont_rpIndName, distorCont_eMailAdd, distorCont_role
        del srcCitatn_rpIndName, srcCitatn_eMailAdd, srcCitatn_role
        del dataset_name
        del CreaDateTime, ModDateTime
        del contact_dict
        #del RoleCd_dict, tpCat_dict,
        del dataIdInfo_dict, dqInfo_dict, distInfo_dict, esri_dict, root_dict
        # Imports
        del etree, md, BytesIO, StringIO, copy
        # Declared variables
        del target_root, target_tree
        # Function Parameters
        del dataset_path

    except KeyboardInterrupt:
        raise SystemExit
    except SystemExit:
        raise SystemExit
    except:
        traceback.print_exc()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function at line number {inspect.stack()[0][2]}\n\t##--> '{', '.join(rk)}' <--##"); del rk
        return True
    finally:
        pass

def add_update_dates(dataset_path=""):
    try:
        # Imports
        from lxml import etree
        from io import StringIO, BytesIO
        import copy
        from arcpy import metadata as md

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        #print(dataset_path)
        dataset_name = os.path.basename(dataset_path)
        print(f"Processing Add/Update Dates for dataset: '{dataset_name}'")
        #print(f"\tDataset Location: {os.path.basename(os.path.dirname(dataset_path))}")

        dataset_md = md.Metadata(dataset_path)
        dataset_md.synchronize("ALWAYS")
        dataset_md.save()
        dataset_md.reload()
        dataset_md_xml = dataset_md.xml
        del dataset_md

        # Parse the XML
        parser = etree.XMLParser(encoding='UTF-8', remove_blank_text=True)
        target_tree = etree.parse(StringIO(dataset_md_xml), parser=parser)
        target_root = target_tree.getroot()
        del parser, dataset_md_xml

        CreaDate = target_root.xpath(f"//Esri/CreaDate")[0].text
        CreaTime = target_root.xpath(f"//Esri/CreaTime")[0].text
        #print(CreaDate, CreaTime)
        CreaDateTime = f"{CreaDate[:4]}-{CreaDate[4:6]}-{CreaDate[6:]}T{CreaTime[:2]}:{CreaTime[2:4]}:{CreaTime[4:6]}"
        #print(f"\tCreaDateTime: {CreaDateTime}")
        #del CreaDateTime
        del CreaDate, CreaTime
        ModDate = target_root.xpath(f"//Esri/ModDate")[0].text
        ModTime = target_root.xpath(f"//Esri/ModTime")[0].text
        #print(ModDate, ModTime)
        ModDateTime = f"{ModDate[:4]}-{ModDate[4:6]}-{ModDate[6:]}T{ModTime[:2]}:{ModTime[2:4]}:{ModTime[4:6]}"
        #print(f"\tModDateTime: {ModDateTime}")
        #del ModDateTime
        del ModDate, ModTime

        dates = target_tree.xpath(f"//date")
        count=0
        count_dates = len(dates)
        for date in dates:
            #_date = copy.deepcopy(date)
            count+=1

            createDate = date.xpath(f"./createDate")
            #print(f"Element list:  '{createDate}'")
            #print(f"Element count: '{len(createDate)}'")
            #print(len(createDate[0].text))
            #print(type(createDate[0].text))
            if not len(createDate):
                _xml = f"<createDate>{CreaDateTime}</createDate>"
                _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
                date.insert(0, _root)
                del _root, _xml
            elif len(createDate) and createDate[0].text is not None:
                pass
                #print(f"createDate exists and has content '{createDate[0].text}'")
                #print(etree.tostring(createDate[0], encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True).decode())
            elif len(createDate) and createDate[0].text is None:
                #print(f"createDate exists and but does not have content.")
                createDate[0].text = CreaDateTime
                date.insert(0, createDate[0])
            del createDate

            pubDate = date.xpath(f"./pubDate")
            if not len(pubDate):
                _xml = f"<pubDate>{CreaDateTime}</pubDate>"
                _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
                date.insert(0, _root)
                del _root, _xml
            if len(pubDate) and pubDate[0].text is not None:
                pass
                #print(f"pubDate exists and has content '{pubDate[0].text}'")
                #print(etree.tostring(pubDate[0], encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True).decode())
            elif len(pubDate) and pubDate[0].text is None:
                #print(f"pubDate exists and but does not have content.")
                pubDate[0].text = CreaDateTime
                date.insert(1, pubDate[0])
            del pubDate

            reviseDate = date.xpath(f"./reviseDate")
            if not len(reviseDate):
                _xml = f"<reviseDate>{ModDateTime}</reviseDate>"
                _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
                date.insert(0, _root)
                del _root, _xml
            if len(reviseDate) and reviseDate[0].text is not None:
                pass
                #print(f"reviseDate exists and has content '{reviseDate[0].text}'")
                #print(etree.tostring(reviseDate[0], encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True).decode())
            elif len(reviseDate) and reviseDate[0].text is None:
                #print(f"reviseDate exists and but does not have content.")
                reviseDate[0].text = ModDateTime
                date.insert(2, reviseDate[0])
            del reviseDate

##            if len(createDate) == 0:
##                _xml = f"<createDate>{CreaDateTime}</createDate>"
##                _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
##                date.insert(0, _root)
##                del _root, _xml
##            elif len(createDate) == 1:
##                if createDate[0].text:
##                    createDate[0].text = createDate[0].text
##                elif not createDate[0].text:
##                    createDate[0].text = CreaDateTime
##                else:
##                    pass
##            else:
##                pass
            #print(etree.tostring(createDate[0], encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True).decode())
##            pubDate = date.xpath(f"./date/pubDate")
##            if len(pubDate) == 0:
##                _xml = f"<pubDate>{CreaDateTime}</pubDate>"
##                _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
##                date.insert(0, _root)
##                del _root, _xml
##            elif len(pubDate) == 1:
##                if pubDate[0].text:
##                    pubDate[0].text = pubDate[0].text
##                elif not pubDate[0].text:
##                    pubDate[0].text = CreaDateTime
##                else:
##                    pass
##            else:
##                pass
##            del pubDate
##
##            try:
##                revisedDate = date.xpath(f"./date/revisedDate")[0]
##                revisedDate.tag = "reviseDate"
##                del revisedDate
##            except:
##                pass
##
##            reviseDate = date.xpath(f"./date/reviseDate")
##            if len(reviseDate) == 0:
##                _xml = f"<reviseDate>{CreaDateTime}</reviseDate>"
##                _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
##                date.insert(0, _root)
##                del _root, _xml
##            elif len(reviseDate) == 1:
##                if reviseDate[0].text:
##                    reviseDate[0].text = reviseDate[0].text
##                elif not reviseDate[0].text:
##                    reviseDate[0].text = ModDateTime
##                else:
##                    pass
##            else:
##                pass
##            del reviseDate

##            date.getparent().replace(date, _date)

            #print(etree.tostring(date, encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True).decode())

            del date
        del count, count_dates
        del dates

        dates = target_root.xpath(f"//date")
        count=0
        count_dates = len(dates)
        for date in dates:
            count+=1
            #print(f"\tDate: {count} of {count_dates}")
            #print(f"\t\tCreaDateTime: {CreaDateTime}")
            #print(f"\t\tModDateTime:  {ModDateTime}")
            #print(date.getroottree().getpath(date))
            #print(etree.tostring(date, encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True).decode())
            del date
        del count, count_dates
        del dates

        # No changes needed below
        #print(etree.tostring(target_tree, encoding='UTF-8', method='xml', pretty_print=True).decode())
        etree.indent(target_root, space='    ')
        dataset_md_xml = etree.tostring(target_tree, encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True)

        SaveBackXml = True
        if SaveBackXml:
            dataset_md = md.Metadata(dataset_path)
            dataset_md.xml = dataset_md_xml
            dataset_md.save()
            dataset_md.synchronize("ALWAYS")
            dataset_md.save()
            #dataset_md.reload()
            del dataset_md
        else:
            pass
        del SaveBackXml
        del dataset_md_xml

        del dataset_name, target_tree, target_root

        # Declared Variables
        del CreaDateTime, ModDateTime
        # Imports
        del etree, StringIO, BytesIO, copy, md
        # Function Parameters
        del dataset_path

    except KeyboardInterrupt:
        raise SystemExit
    except Exception:
        traceback.print_exc()
    except:
        traceback.print_exc()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function at line number {inspect.stack()[0][2]}\n\t##--> '{', '.join(rk)}' <--##"); del rk
        return True
    finally:
        pass

def basic_metadata_report(dataset_path=""):
    try:
        # Imports
        from lxml import etree
        from io import StringIO, BytesIO
        import copy
        from arcpy import metadata as md

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        project_gdb    = os.path.dirname(dataset_path)
        project_folder = os.path.dirname(project_gdb)
        project        = os.path.basename(os.path.dirname(project_gdb))
        export_folder  = rf"{project_folder}\Export"
        scratch_folder = rf"{project_folder}\Scratch"

        arcpy.env.workspace        = project_gdb
        arcpy.env.scratchWorkspace = rf"{scratch_folder}\scratch.gdb"
        del scratch_folder
        del project_folder
        del project_gdb

        #print(dataset_path)
        dataset_name = os.path.basename(dataset_path)
        print(f"Reporting on Basic XML Metadata for dataset: '{dataset_name}'")
        #print(f"\tDataset Location: {os.path.basename(os.path.dirname(dataset_path))}")

        dataset_md = md.Metadata(dataset_path)
        #dataset_md.synchronize("ALWAYS")
        #dataset_md.save()
        #dataset_md.reload()
        dataset_md_xml = dataset_md.xml
        del dataset_md

        # Parse the XML
        parser = etree.XMLParser(encoding='UTF-8', remove_blank_text=True)
        target_tree = etree.parse(StringIO(dataset_md_xml), parser=parser)
        target_root = target_tree.getroot()
        del parser, dataset_md_xml

        dataset_md = md.Metadata(dataset_path)
        print(f"\tTitle:       {dataset_md.title}")
        print(f"\tSearch Keys: {dataset_md.tags}")
        print(f"\tSummary:     {dataset_md.summary}")
        print(f"\tDescription: {dataset_md.description}")
        print(f"\tCredits:     {dataset_md.credits}")
        print(f"\tUse Limits:  {dataset_md.accessConstraints}")
        del dataset_md

        # No changes needed below
        #print(etree.tostring(target_tree, encoding='UTF-8', method='xml', pretty_print=True).decode())
        etree.indent(target_root, space='    ')
        dataset_md_xml = etree.tostring(target_tree, encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True)

        SaveBackXml = True
        if SaveBackXml:
            dataset_md = md.Metadata(dataset_path)
            dataset_md.xml = dataset_md_xml
            dataset_md.save()
            dataset_md.synchronize("ALWAYS")
            dataset_md.save()
            #dataset_md.reload()
            del dataset_md
        else:
            pass
        del SaveBackXml
        del dataset_md_xml

        # Declared Varaiables
        del project, export_folder
        del dataset_name
        del target_tree, target_root
        # Imports
        del etree, StringIO, BytesIO, copy, md
        # Function Parameters
        del dataset_path
    except KeyboardInterrupt:
        raise SystemExit
    except:
        traceback.print_exc()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function at line number {inspect.stack()[0][2]}\n\t##--> '{', '.join(rk)}' <--##"); del rk
        return True
    finally:
        pass

def metadata_esri_report(dataset_path=""):
    try:
        # Imports
        from lxml import etree
        from io import StringIO, BytesIO
        import copy
        from arcpy import metadata as md

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        #print(dataset_path)
        dataset_name = os.path.basename(dataset_path)
        print(f"Reporting on Esri XML for dataset: '{dataset_name}'")
        #print(f"\tDataset Location: {os.path.basename(os.path.dirname(dataset_path))}")

        dataset_md = md.Metadata(dataset_path)
        #dataset_md.synchronize("ALWAYS")
        #dataset_md.save()
        #dataset_md.reload()
        dataset_md_xml = dataset_md.xml
        del dataset_md

        # Parse the XML
        parser = etree.XMLParser(encoding='UTF-8', remove_blank_text=True)
        target_tree = etree.parse(StringIO(dataset_md_xml), parser=parser)
        target_root = target_tree.getroot()
        del parser, dataset_md_xml

        if target_root.find("Esri") is not None:
            Esri = target_root.xpath("./Esri")[0]
            _xml = '''<Esri>
                        <ArcGISstyle>ISO 19139 Metadata Implementation Specification GML3.2</ArcGISstyle>
                        <ArcGISProfile>ISO19139</ArcGISProfile>
                        <locales>
                            <locale xmlns="" language="eng" country="US"/>
                        </locales>
                      </Esri>'''
            _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
            # Merge Target wtih Source
            target_source_merge = xml_tree_merge(Esri, _root)
            #print(etree.tostring(target_source_merge, encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True).decode())
            # Merge Source wtih Target
            source_target_merge = xml_tree_merge(target_source_merge, Esri)
            #print(etree.tostring(source_target_merge, encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True).decode())
            Esri.getparent().replace(Esri, source_target_merge)
            del target_source_merge, source_target_merge
            del _root, _xml
            #print(etree.tostring(target_root.find("Esri"), encoding='UTF-8', method='xml', pretty_print=True).decode())
            del Esri
        else:
            pass

        # No changes needed below
        #print(etree.tostring(target_tree, encoding='UTF-8', method='xml', pretty_print=True).decode())
        etree.indent(target_root, space='    ')
        dataset_md_xml = etree.tostring(target_tree, encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True)

        SaveBackXml = True
        if SaveBackXml:
            dataset_md = md.Metadata(dataset_path)
            dataset_md.xml = dataset_md_xml
            dataset_md.save()
            dataset_md.synchronize("ALWAYS")
            dataset_md.save()
            #dataset_md.reload()
            del dataset_md
        else:
            pass
        del SaveBackXml
        del dataset_md_xml

        # Declared Varaiables
        del dataset_name
        del target_tree, target_root
        # Imports
        del etree, StringIO, BytesIO, copy, md
        # Function Parameters
        del dataset_path
    except KeyboardInterrupt:
        raise SystemExit
    except:
        traceback.print_exc()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function at line number {inspect.stack()[0][2]}\n\t##--> '{', '.join(rk)}' <--##"); del rk
        return True
    finally:
        pass

def metadata_dataidinfo_report(dataset_path=""):
    try:
        # Imports
        from lxml import etree
        from io import StringIO, BytesIO
        import copy
        from arcpy import metadata as md

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        import json
        json_path = rf"{project_folder}\dataIdInfo_dict.json"
        with open(json_path, "r") as json_file:
            dataIdInfo_dict = json.load(json_file)
        del json_file
        del json_path
        json_path = rf"{project_folder}\root_dict.json"
        with open(json_path, "r") as json_file:
            root_dict = json.load(json_file)
        del json_file
        del json_path
        del json

        #print(dataset_path)
        dataset_name = os.path.basename(dataset_path)
        print(f"Reporting on dataIdInfo XML for dataset: '{dataset_name}'")
        #print(f"\tDataset Location: {os.path.basename(os.path.dirname(dataset_path))}")

        dataset_md = md.Metadata(dataset_path)
        dataset_md.synchronize("ALWAYS")
        dataset_md.save()
        dataset_md.reload()
        dataset_md_xml = dataset_md.xml
        del dataset_md

        # Parse the XML
        parser = etree.XMLParser(encoding='UTF-8', remove_blank_text=True)
        target_tree = etree.parse(StringIO(dataset_md_xml), parser=parser)
        target_root = target_tree.getroot()
        del parser, dataset_md_xml

        #target_root[:] = sorted(target_root, key=lambda x: root_dict[x.tag])
        #for child in target_root:
        #    #print(child.tag)
        #    #print(etree.tostring(child, encoding='UTF-8', method='xml', pretty_print=True).decode())
        #    del child
        # Esri
        # dataIdInfo
        # dqInfo
        # distInfo
        # mdContact
        # mdLang
        # mdChar
        # mdDateSt
        # mdHrLv
        # mdHrLvName
        # mdFileID
        # mdMaint
        # refSysInfo
        # spatRepInfo
        # spdoinfo
        # eainfo

        refSysInfo = target_root.xpath("./refSysInfo")
        if len(refSysInfo) == 0:
            pass #print("missing")
        elif len(refSysInfo) == 1:
            pass #print(etree.tostring(target_root.xpath("./refSysInfo")[0], encoding='UTF-8', method='xml', pretty_print=True).decode())
        elif  len(refSysInfo) > 1:
            pass #print("too many")
        else:
            pass
        del refSysInfo

        dqInfo = target_root.xpath("./dqInfo")
        if len(dqInfo) == 0:
            _xml = '''<dqInfo>
                        <dqScope xmlns="">
                            <scpLvl>
                                <ScopeCd value="005" Sync="TRUE"></ScopeCd>
                            </scpLvl>
                            <scpLvlDesc xmlns="">
                                <datasetSet>dataset</datasetSet>
                            </scpLvlDesc>
                        </dqScope>
                      </dqInfo>
                   '''
            _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
            target_root.insert(root_dict["dqInfo"], _root)
            del _root, _xml
        else:
            pass
        del dqInfo

        mdHrLv = target_root.xpath("./mdHrLv")
        if len(mdHrLv) == 0:
            _xml = '''<mdHrLv>
                        <ScopeCd value="005" Sync="TRUE"/>
                      </mdHrLv>
                   '''
            _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
            target_root.insert(root_dict["mdHrLv"], _root)
            del _root, _xml
        else:
            pass
        del mdHrLv

        mdHrLvName = target_root.xpath("./mdHrLvName")
        if len(mdHrLvName) == 0:
            _xml = '''<mdHrLvName Sync="TRUE">dataset</mdHrLvName>'''
            _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
            target_root.insert(root_dict["mdHrLvName"], _root)
            del _root, _xml
        else:
            pass
        del mdHrLvName

        fgdcGeoform = target_root.xpath("./dataIdInfo/idCitation/presForm/fgdcGeoform")
        if len(fgdcGeoform) == 0:
            _xml = '''<fgdcGeoform>document</fgdcGeoform>'''
            _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
            target_root.xpath("./dataIdInfo/idCitation/presForm")[0].insert(dataIdInfo_dict["fgdcGeoform"], _root)
            del _root, _xml
        else:
            pass
        del fgdcGeoform

        #print(etree.tostring(target_root.xpath("./distInfo")[0], encoding='UTF-8', method='xml', pretty_print=True).decode())

        distInfo = target_root.xpath("./distInfo")
        if len(distInfo) == 0:
            _xml = '''<distInfo>
                        <distFormat>
                            <formatName Sync="FALSE">ESRI REST Service</formatName>
                            <formatVer></formatVer>
                            <fileDecmTech>Uncompressed</fileDecmTech>
                            <formatInfo></formatInfo>
                        </distFormat>
                      </distInfo>
                   '''
            _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
            target_root.xpath("./dataIdInfo/idCitation/presForm")[0].insert(dataIdInfo_dict["fgdcGeoform"], _root)
            del _root, _xml
        elif len(distInfo) == 1:
            formatVer = distInfo[0].xpath("./distFormat/formatVer")
            if len(formatVer) == 0:
                _xml = '''<formatVer></formatVer>'''
                _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
                target_root.xpath("./distInfo/distFormat")[0].insert(1, _root)
                del _root, _xml
            elif len(formatVer) == 1:
                pass
            elif len(formatVer) > 1:
                for i in range(1, len(formatVer)):
                    formatVer[i].getparent().remove(formatVer[i])
                    del i
            else:
                pass
            del formatVer

            fileDecmTech = distInfo[0].xpath("./distFormat/fileDecmTech")
            if len(fileDecmTech) == 0:
                _xml = '''<fileDecmTech></fileDecmTech>'''
                _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
                target_root.xpath("./distInfo/distFormat")[0].insert(2, _root)
                del _root, _xml
            elif len(fileDecmTech) == 1:
                pass
            elif len(fileDecmTech) > 1:
                for i in range(1, len(fileDecmTech)):
                    fileDecmTech[i].getparent().remove(fileDecmTech[i])
                    del i
            else:
                pass
            del fileDecmTech

            formatInfo = distInfo[0].xpath("./distFormat/formatInfo")
            if len(formatInfo) == 0:
                _xml = '''<formatInfo></formatInfo>'''
                _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
                target_root.xpath("./distInfo/distFormat")[0].insert(2, _root)
                del _root, _xml
            elif len(formatInfo) == 1:
                pass
            elif len(formatInfo) > 1:
                for i in range(1, len(formatInfo)):
                    formatInfo[i].getparent().remove(formatInfo[i])
                    del i
            else:
                pass
            del formatInfo
        else:
            pass
        del distInfo

        #print(etree.tostring(target_root.xpath("./mdHrLv")[0], encoding='UTF-8', method='xml', pretty_print=True).decode())
        #print(etree.tostring(target_root.xpath("./mdHrLvName")[0], encoding='UTF-8', method='xml', pretty_print=True).decode())
        #print(etree.tostring(target_root.xpath("./dqInfo/dqScope")[0], encoding='UTF-8', method='xml', pretty_print=True).decode())
        #print(etree.tostring(target_root.xpath("./dataIdInfo/idCitation/presForm")[0], encoding='UTF-8', method='xml', pretty_print=True).decode())
        #print(etree.tostring(target_root.xpath("./distInfo")[0], encoding='UTF-8', method='xml', pretty_print=True).decode())

        #raise Exception
        mdHrLvName = target_root.xpath("./mdHrLvName")
        if len(mdHrLvName) == 0:
            _xml = '''<mdHrLvName Sync="TRUE">dataset</mdHrLvName>'''
            _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
            target_root.insert(root_dict["mdHrLvName"], _root)
            del _root, _xml
        else:
            pass
        del mdHrLvName

        target_root.xpath("./dataIdInfo/envirDesc")[0].set('Sync', "TRUE")
        #target_root.xpath("./dqInfo/dqScope/scpLvl/ScopeCd")[0].set('value', "005")
        #target_root.xpath("./dqInfo/dqScope/scpLvl/ScopeCd")[0].set('Sync', "TRUE")
        mdHrLvName   = target_root.xpath("./mdHrLvName")[0]
        ScopeCd      = target_root.xpath("./dqInfo/dqScope/scpLvl/ScopeCd")[0]
        PresFormCd   = target_root.xpath("./dataIdInfo/idCitation/presForm/PresFormCd")[0]
        fgdcGeoform  = target_root.xpath("./dataIdInfo/idCitation/presForm/fgdcGeoform")[0]
        SpatRepTypCd = target_root.xpath("./dataIdInfo/spatRpType/SpatRepTypCd")[0]
        PresFormCd.set('Sync', "TRUE")
        #print("------" * 10)
        #print(etree.tostring(SpatRepTypCd, encoding='UTF-8', method='xml', pretty_print=True).decode())
        #print(etree.tostring(target_root.xpath("./dataIdInfo/idCitation/presForm")[0], encoding='UTF-8', method='xml', pretty_print=True).decode())
        #print(etree.tostring(target_root.xpath("./dqInfo/dqScope")[0], encoding='UTF-8', method='xml', pretty_print=True).decode())
        #print("------" * 10)
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # SpatRepTypCd "Empty" "001" (vector) "002" (raster/grid) "003" (tabular)
        # ScopeCd              "005"          "005"               "007"
        # PresFormCd           "005"          "003"               "011"
        # fgdcGeoform          "vector data"  "raster data"       "tabular data"
        # mdHrLvName           "vector data"  "raster data"       "tabular data"
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        datasetSet = target_root.xpath("./dqInfo/dqScope/scpLvlDesc/datasetSet")
        if len(datasetSet) == 0:
            _xml = '<scpLvlDesc xmlns=""><datasetSet></datasetSet></scpLvlDesc>'
            _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
            target_root.xpath("./dqInfo/dqScope")[0].insert(1, _root)
            del _root, _xml
        else:
            pass
        datasetSet   = target_root.xpath("./dqInfo/dqScope/scpLvlDesc/datasetSet")[0]
        if SpatRepTypCd.get("value") == "001":
            ScopeCd.set('value', "005")
            PresFormCd.set("value", "005")
            fgdcGeoform.text = "vector digital data"
            datasetSet.text  = "Vector Digital Data"
            mdHrLvName.text  = "Vector Digital Data"
        elif SpatRepTypCd.get("value") == "002":
            ScopeCd.set('value', "005")
            PresFormCd.set("value", "003")
            fgdcGeoform.text = "raster digital data"
            datasetSet.text  = "Raster Digital Data"
            mdHrLvName.text  = "Raster Digital Data"
        elif SpatRepTypCd.get("value") == "003":
            ScopeCd.set('value', "007")
            PresFormCd.set("value", "011")
            fgdcGeoform.text = "tabular digital data"
            datasetSet.text  = "Tabular Digital Data"
            mdHrLvName.text  = "Tabular Digital Data"
        else:
            pass
        #print("------" * 10)
        #print(etree.tostring(SpatRepTypCd, encoding='UTF-8', method='xml', pretty_print=True).decode())
        #print(etree.tostring(target_root.xpath("./dataIdInfo/idCitation/presForm")[0], encoding='UTF-8', method='xml', pretty_print=True).decode())
        #print(etree.tostring(target_root.xpath("./dqInfo/dqScope")[0], encoding='UTF-8', method='xml', pretty_print=True).decode())
        #print("------" * 10)
        del datasetSet, SpatRepTypCd, fgdcGeoform, PresFormCd, ScopeCd, mdHrLvName
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        formatName = target_root.xpath("./distInfo/distFormat/formatName")[0]
        envirDesc = target_root.xpath("./dataIdInfo/envirDesc")[0]
        envirDesc.set('Sync', "TRUE")
        target_root.xpath("./distInfo/distFormat/fileDecmTech")[0].text = "Uncompressed"
        formatName.text = "ESRI REST Service"
        formatVer_text = str.rstrip(str.lstrip(envirDesc.text))
        formatVer = target_root.xpath("./distInfo/distFormat/formatVer")[0]
        formatVer.text = str.rstrip(str.lstrip(formatVer_text))
        del formatVer_text
        del envirDesc
        del formatVer
        del formatName

        xml_file = b'''<idPoC>
                            <editorSource>external</editorSource>
                            <editorDigest>c66ffbb333c48d18d81856ec0e0c37ea752bff1a</editorDigest>
                            <rpIndName>Melissa Ann Karp</rpIndName>
                            <rpOrgName>NMFS Office of Science and Technology</rpOrgName>
                            <rpPosName>Fisheries Science Coordinator</rpPosName>
                            <rpCntInfo editorFillOnly="True" editorExpand="True">
                              <cntAddress addressType="both">
                                <delPoint>1315 East West Hwy</delPoint>
                                <city>Silver Spring</city>
                                <adminArea>MD</adminArea>
                                <postCode>20910-3282</postCode>
                                <eMailAdd>melissa.karp@noaa.gov</eMailAdd>
                                <country>US</country>
                              </cntAddress>
                              <cntPhone>
                                <voiceNum tddtty="">301-427-8202</voiceNum>
                                <faxNum>301-713-4137</faxNum>
                              </cntPhone>
                              <cntHours>0700 - 1800 EST/EDT</cntHours>
                              <cntOnlineRes>
                                <linkage>https://www.fisheries.noaa.gov/about/office-science-and-technology</linkage>
                                <protocol>REST Service</protocol>
                                <orName>NMFS Office of Science and Technology</orName>
                                <orDesc>NOAA Fisheries Office of Science and Technology</orDesc>
                                <orFunct>
                                  <OnFunctCd value="002" />
                                </orFunct>
                              </cntOnlineRes>
                            </rpCntInfo>
                            <displayName>Melissa Ann Karp</displayName>
                            <editorSave>True</editorSave>
                            <role>
                                <RoleCd value="007"/>
                            </role>
                        </idPoC>
                    '''
        _tree = etree.parse(BytesIO(xml_file), etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
        _root = _tree.getroot()
        idPoC = target_root.xpath(f"./dataIdInfo/idPoC")
        if len(idPoC) == 0:
            target_root.xpath(f"./dataIdInfo")[0].insert(dataIdInfo_dict["idPoC"], _root)
        elif len(idPoC) == 1:
            idPoC[0].getparent().replace(idPoC[0], _root)
        else:
            pass
        del _root, _tree, xml_file
        #print(f"\n\t{etree.tostring(target_root.xpath(f'./dataIdInfo/idPoC')[0], encoding='UTF-8', method='xml', pretty_print=True).decode()}\n")
        del idPoC

        xml_file = b'''<citRespParty>
                            <editorSource>external</editorSource>
                            <editorDigest>579ce2e21b888ac8f6ac1dac30f04cddec7a0d7c</editorDigest>
                            <rpIndName>NMFS Office of Science and Technology</rpIndName>
                            <rpOrgName>NMFS Office of Science and Technology</rpOrgName>
                            <rpPosName>GIS App Developer</rpPosName>
                            <rpCntInfo editorFillOnly="True" editorExpand="True">
                              <cntAddress addressType="both">
                                <delPoint>1315 East West Highway</delPoint>
                                <city>Silver Spring</city>
                                <adminArea>MD</adminArea>
                                <postCode>20910-3282</postCode>
                                <country>US</country>
                                <eMailAdd>tim.haverland@noaa.gov</eMailAdd>
                              </cntAddress>
                              <cntPhone>
                                <voiceNum tddtty="">301-427-8137</voiceNum>
                                <faxNum>301-713-4137</faxNum>
                              </cntPhone>
                              <cntHours>0700 - 1800 EST/EDT</cntHours>
                              <cntOnlineRes>
                                <linkage>https://www.fisheries.noaa.gov/about/office-science-and-technology</linkage>
                                <protocol>REST Service</protocol>
                                <orName>NMFS Office of Science and Technology</orName>
                                <orDesc>NOAA Fisheries Office of Science and Technology</orDesc>
                                <orFunct>
                                  <OnFunctCd value="002" />
                                </orFunct>
                              </cntOnlineRes>
                            </rpCntInfo>
                            <displayName>NMFS Office of Science and Technology (Distributor)</displayName>
                            <editorSave>True</editorSave>
                            <role>
                                <RoleCd value="002"/>
                            </role>
                        </citRespParty>
                    '''
        _tree = etree.parse(BytesIO(xml_file), etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
        _root = _tree.getroot()
        citRespParty = target_root.xpath(f"./dataIdInfo/idCitation/citRespParty")
        if len(citRespParty) == 0:
            target_root.xpath(f"./dataIdInfo/idCitation")[0].insert(dataIdInfo_dict["citRespParty"], _root)
        elif len(citRespParty) == 1:
            citRespParty[0].getparent().replace(citRespParty[0], _root)
        else:
            pass
        del _root, _tree, xml_file
        #print(f"\n\t{etree.tostring(target_root.xpath(f'./dataIdInfo/idCitation/citRespParty')[0], encoding='UTF-8', method='xml', pretty_print=True).decode()}\n")
        del citRespParty

        resConst = target_root.xpath("./dataIdInfo/resConst")
        if len(resConst) == 1:
            xml_file = b'''<resConst>
                             <LegConsts xmlns="">
                                <accessConsts>
                                   <RestrictCd value="005"/>
                                </accessConsts>
                                <useConsts>
                                   <RestrictCd value="005"/>
                                </useConsts>
                                <useLimit>Data License: CC0-1.0
Data License URL: https://creativecommons.org/publicdomain/zero/1.0/
Data License Statement: These data were produced by NOAA and are not subject to copyright protection in the United States. NOAA waives any potential copyright and related rights in these data worldwide through the Creative Commons Zero 1.0 Universal Public Domain Dedication (CC0-1.0).
                                </useLimit>
                             </LegConsts>
                             <SecConsts xmlns="">
                                <class>
                                   <ClasscationCd value="001"/>
                                </class>
                                <classSys>FISMA Low</classSys>
                             </SecConsts>
                             <Consts xmlns="">
                                <useLimit>&lt;DIV STYLE="text-align:Left;"&gt;&lt;DIV&gt;&lt;DIV&gt;&lt;P&gt;&lt;SPAN&gt;***No Warranty*** The user assumes the entire risk related to its use of these data. NMFS is providing these data 'as is' and NMFS disclaims any and all warranties, whether express or implied, including (without limitation) any implied warranties of merchantability or fitness for a particular purpose. No warranty expressed or implied is made regarding the accuracy or utility of the data on any other system or for general or scientific purposes, nor shall the act of distribution constitute any such warranty. It is strongly recommended that careful attention be paid to the contents of the metadata file associated with these data to evaluate dataset limitations, restrictions or intended use. In no event will NMFS be liable to you or to any third party for any direct, indirect, incidental, consequential, special or exemplary damages or lost profit resulting from any use or misuse of these data.&lt;/SPAN&gt;&lt;/P&gt;&lt;/DIV&gt;&lt;/DIV&gt;&lt;/DIV&gt;</useLimit>
                             </Consts>
                          </resConst>'''
            _tree = etree.parse(BytesIO(xml_file), etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
            _root = _tree.getroot()
            resConst[0].getparent().replace(resConst[0], _root)
            del _root, _tree, xml_file
        else:
            pass
        del resConst

        dataIdInfo = target_root.xpath("./dataIdInfo")
        for data_Id_Info in dataIdInfo:
            data_Id_Info[:] = sorted(data_Id_Info, key=lambda x: dataIdInfo_dict[x.tag])
            #print(etree.tostring(data_Id_Info, encoding='UTF-8', method='xml', pretty_print=True).decode())
            del data_Id_Info
        del dataIdInfo

        # No changes needed below
        #print(etree.tostring(target_tree, encoding='UTF-8', method='xml', pretty_print=True).decode())
        etree.indent(target_root, space='    ')
        dataset_md_xml = etree.tostring(target_tree, encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True)

        SaveBackXml = True
        if SaveBackXml:
            dataset_md = md.Metadata(dataset_path)
            dataset_md.xml = dataset_md_xml
            dataset_md.save()
            dataset_md.synchronize("ALWAYS")
            dataset_md.save()
            #dataset_md.reload()
            del dataset_md
        else:
            pass
        del SaveBackXml
        del dataset_md_xml

        # Declared Varaiables
        del dataset_name
        del dataIdInfo_dict, root_dict
        del target_tree, target_root
        # Imports
        del etree, StringIO, BytesIO, copy, md
        # Function Parameters
        del dataset_path
    except KeyboardInterrupt:
        raise SystemExit
    except:
        traceback.print_exc()
        raise SystemExit
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk:
            print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function at line number {inspect.stack()[0][2]}\n\t##--> '{', '.join(rk)}' <--##")
            del rk
        return True
    finally:
        pass

def metadata_dq_info_report(dataset_path=""):
    try:
        # Imports
        from lxml import etree
        from io import StringIO, BytesIO
        import copy
        from arcpy import metadata as md

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        import json
        json_path = rf"{project_folder}\dqInfo_dict.json"
        with open(json_path, "r") as json_file:
            dqInfo_dict = json.load(json_file)
        del json_file
        del json_path
        del json

        export_folder  = rf"{os.path.dirname(os.path.dirname(dataset_path))}\Export"

        #print(dataset_path)
        dataset_name = os.path.basename(dataset_path)
        print(f"Reporting on dqInfo XML for dataset: '{dataset_name}'")
        #print(f"\tDataset Location: {os.path.basename(os.path.dirname(dataset_path))}")

        dataset_md = md.Metadata(dataset_path)
        #dataset_md.synchronize("ALWAYS")
        #dataset_md.save()
        #dataset_md.reload()
        dataset_md_xml = dataset_md.xml
        del dataset_md

        # Parse the XML
        parser = etree.XMLParser(encoding='UTF-8', remove_blank_text=True)
        target_tree = etree.parse(StringIO(dataset_md_xml), parser=parser)
        target_root = target_tree.getroot()
        del parser, dataset_md_xml

        # dqInfo
        dqInfo = target_root.xpath("./dqInfo")[0]
        dqInfo[:] = sorted(dqInfo, key=lambda x: dqInfo_dict[x.tag])
        #print(etree.tostring(dqInfo, encoding='UTF-8', method='xml', pretty_print=True).decode())

        #target_root[:] = sorted(target_root, key=lambda x: dqInfo_dict[x.tag])
        #for child in target_root:
        #    #print(child.tag)
        #    #print(etree.tostring(child, encoding='UTF-8', method='xml', pretty_print=True).decode())
        #    del child
        # Esri
        # dataIdInfo
        # dqInfo
        # distInfo
        # mdContact
        # mdLang
        # mdChar
        # mdDateSt
        # mdHrLv
        # mdHrLvName
        # mdFileID
        # mdMaint
        # refSysInfo
        # spatRepInfo
        # spdoinfo
        # eainfo

        _report = target_root.xpath(f"./dqInfo/report[@type='DQConcConsis']")
        if len(_report) == 1:
            _xml = '''<report type="DQConcConsis" dimension="horizontal">
                        <measDesc>Based on a review from DisMAP Team all necessary features are present.</measDesc>
                         <measResult>
                            <ConResult>
                               <conSpec>
                                  <resTitle>Conceptual Consistency Report</resTitle>
                                  <resAltTitle></resAltTitle>
                                  <collTitle>NMFS OST DisMAP</collTitle>
                                  <date>
                                    <createDate></createDate>
                                    <pubDate></pubDate>
                                    <reviseDate></reviseDate>
                                  </date>
                               </conSpec>
                               <conExpl>Based on a review from DisMAP Team all necessary features are present.</conExpl>
                               <conPass>1</conPass>
                            </ConResult>
                         </measResult>
                    </report>'''
            _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
            #print(f"{etree.tostring(_root, encoding='UTF-8', method='xml', pretty_print=True).decode()}")
            #raise SystemExit
            _report[0].getparent().replace(_report[0], _root)
            del _root, _xml
        else:
            pass
        del _report

        _report = target_root.xpath(f"./dqInfo/report[@type='DQCompOm']")
        if len(_report) == 1:
            _xml = '''<report type="DQCompOm" dimension="horizontal">
                        <measDesc>Based on a review from DisMAP Team all necessary features are present.</measDesc>
                         <measResult>
                            <ConResult>
                               <conSpec>
                                  <resTitle>Completeness Report</resTitle>
                                  <resAltTitle></resAltTitle>
                                  <collTitle>NMFS OST DisMAP</collTitle>
                                  <date>
                                    <createDate></createDate>
                                    <pubDate></pubDate>
                                    <reviseDate></reviseDate>
                                  </date>
                               </conSpec>
                               <conExpl>Based on a review from DisMAP Team all necessary features are present.</conExpl>
                               <conPass>1</conPass>
                            </ConResult>
                         </measResult>
                    </report>'''
            _root = etree.XML(_xml, etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
            _report[0].getparent().replace(_report[0], _root)
            del _root, _xml
        else:
            pass
        del _report

        dqInfo = target_root.xpath("./dqInfo")
        #print(len(dqInfo))
        for dq_Info in dqInfo:
            dq_Info[:] = sorted(dq_Info, key=lambda x: dqInfo_dict[x.tag])
            #print(etree.tostring(dq_Info, encoding='UTF-8', method='xml', pretty_print=True).decode())
            del dq_Info
        del dqInfo

        #print(len(target_root.xpath("./dqInfo")))
        for i in range(1, len(target_root.xpath("./dqInfo"))):
            dq_Info = target_root.xpath("./dqInfo")[i] #.write(rf"{export_folder}\{os.path.basename(dataset_path)} dqInfo.xml", encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True)
            # Writing to a new file
            file = open(rf"{export_folder}\{os.path.basename(dataset_path)} dqInfo.xml", "w")
            file.write(etree.tostring(dq_Info, encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True).decode())
            file.close()
            del file
            dq_Info.getparent().remove(dq_Info)
            del dq_Info
            del i

        # No changes needed below
        #print(etree.tostring(target_tree, encoding='UTF-8', method='xml', pretty_print=True).decode())
        etree.indent(target_root, space='    ')
        dataset_md_xml = etree.tostring(target_tree, encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True)

        SaveBackXml = True
        if SaveBackXml:
            dataset_md = md.Metadata(dataset_path)
            dataset_md.xml = dataset_md_xml
            dataset_md.save()
            dataset_md.synchronize("ALWAYS")
            dataset_md.save()
            #dataset_md.reload()
            del dataset_md
        else:
            pass
        del SaveBackXml
        del dataset_md_xml

        # Declared Varaiables
        del export_folder
        del dataset_name
        del dqInfo_dict
        del target_tree, target_root
        # Imports
        del etree, StringIO, BytesIO, copy, md
        # Function Parameters
        del dataset_path
    except KeyboardInterrupt:
        raise SystemExit
    except:
        traceback.print_exc()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function at line number {inspect.stack()[0][2]}\n\t##--> '{', '.join(rk)}' <--##"); del rk
        return True
    finally:
        pass

def metadata_dist_info_report(dataset_path=""):
    try:
        # Imports
        from lxml import etree
        from io import StringIO, BytesIO
        import copy
        from arcpy import metadata as md

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        import json
        json_path = rf"{project_folder}\distInfo_dict.json"
        with open(json_path, "r") as json_file:
            distInfo_dict = json.load(json_file)
        del json_file
        del json_path
        del json

        project        = os.path.basename(os.path.dirname(os.path.dirname(dataset_path)))
        export_folder  = rf"{os.path.dirname(os.path.dirname(dataset_path))}\Export"

        #print(dataset_path)
        dataset_name = os.path.basename(dataset_path)
        print(f"Reporting on distInfo XML for dataset: '{dataset_name}'")
        #print(f"\tDataset Location: {os.path.basename(os.path.dirname(dataset_path))}")

        dataset_md = md.Metadata(dataset_path)
        #dataset_md.synchronize("ALWAYS")
        #dataset_md.save()
        #dataset_md.reload()
        dataset_md_xml = dataset_md.xml
        del dataset_md

        # Parse the XML
        parser = etree.XMLParser(encoding='UTF-8', remove_blank_text=True)
        target_tree = etree.parse(StringIO(dataset_md_xml), parser=parser)
        target_root = target_tree.getroot()
        del parser, dataset_md_xml

        #target_root[:] = sorted(target_root, key=lambda x: distInfo_dict[x.tag])
        #for child in target_root:
        #    #print(child.tag)
        #    #print(etree.tostring(child, encoding='UTF-8', method='xml', pretty_print=True).decode())
        #    del child
        # Esri
        # dataIdInfo
        # dqInfo
        # distInfo
        # mdContact
        # mdLang
        # mdChar
        # mdDateSt
        # mdHrLv
        # mdHrLvName
        # mdFileID
        # mdMaint
        # refSysInfo
        # spatRepInfo
        # spdoinfo
        # eainfo

        distorTran = target_root.xpath("//distorTran")
        for _distorTran in distorTran:
            _distorTran.tag = "distTranOps"
            del _distorTran
        del distorTran

##        target_root.xpath("./distInfo/distFormat/formatName")[0].set('Sync', "FALSE")
##        target_root.xpath("./dataIdInfo/envirDesc")[0].set('Sync', "TRUE")
##        #target_root.xpath("./dqInfo/dqScope/scpLvl/ScopeCd")[0].set('value', "005")
##        PresFormCd   = target_root.xpath("./dataIdInfo/idCitation/presForm/PresFormCd")[0]
##        fgdcGeoform  = target_root.xpath("./dataIdInfo/idCitation/presForm/fgdcGeoform")[0]
##        SpatRepTypCd = target_root.xpath("./dataIdInfo/spatRpType/SpatRepTypCd")[0]
##        PresFormCd.set('Sync', "TRUE")
##        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        # SpatRepTypCd "Empty" "001" (vector) "002" (raster/grid) "003" (tabular)
##        # PresFormCd           "005"          "003"               "011"
##        # fgdcGeoform          "vector data"  "raster data"       "tabular data"
##        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        datasetSet   = target_root.xpath("./dqInfo/dqScope/scpLvlDesc/datasetSet")[0]
##        if SpatRepTypCd.get("value") == "001":
##            PresFormCd.set("value", "005")
##            fgdcGeoform.text = "vector digital data"
##            datasetSet.text  = "Vector Digital Data"
##        elif SpatRepTypCd.get("value") == "002":
##            PresFormCd.set("value", "003")
##            fgdcGeoform.text = "raster digital data"
##            datasetSet.text  = "Raster Digital Data"
##        elif SpatRepTypCd.get("value") == "003":
##            PresFormCd.set("value", "011")
##            fgdcGeoform.text = "tabular digital data"
##            datasetSet.text  = "Tabular Digital Data"
##        else:
##            pass
##        #print("------" * 10)
##        #print(etree.tostring(SpatRepTypCd, encoding='UTF-8', method='xml', pretty_print=True).decode())
##        #print(etree.tostring(target_root.xpath("./dataIdInfo/idCitation/presForm")[0], encoding='UTF-8', method='xml', pretty_print=True).decode())
##        #print(etree.tostring(target_root.xpath("./dqInfo/dqScope")[0], encoding='UTF-8', method='xml', pretty_print=True).decode())
##        #print("------" * 10)
##        del datasetSet, SpatRepTypCd, fgdcGeoform, PresFormCd
##        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##        formatName = target_root.xpath("./distInfo/distFormat/formatName")[0]
##        envirDesc = target_root.xpath("./dataIdInfo/envirDesc")[0]
##        envirDesc.set('Sync', "TRUE")
##        target_root.xpath("./distInfo/distFormat/fileDecmTech")[0].text = "Uncompressed"
##        formatName.text = "ESRI REST Service"
##        formatVer_text = str.rstrip(str.lstrip(envirDesc.text))
##        formatVer = target_root.xpath("./distInfo/distFormat/formatVer")[0]
##        formatVer.text = str.rstrip(str.lstrip(formatVer_text))
##        del formatVer_text
##        del envirDesc
##        del formatVer
##        del formatName

        xml_file = b'''<distributor>
                        <distorCont>
                            <editorSource>external</editorSource>
                            <editorDigest>579ce2e21b888ac8f6ac1dac30f04cddec7a0d7c</editorDigest>
                            <rpIndName>NMFS Office of Science and Technology</rpIndName>
                            <rpOrgName>NMFS Office of Science and Technology</rpOrgName>
                            <rpPosName>GIS App Developer</rpPosName>
                            <rpCntInfo editorFillOnly="True" editorExpand="True">
                              <cntAddress addressType="both">
                                <delPoint>1315 East West Highway</delPoint>
                                <city>Silver Spring</city>
                                <adminArea>MD</adminArea>
                                <postCode>20910-3282</postCode>
                                <country>US</country>
                                <eMailAdd>tim.haverland@noaa.gov</eMailAdd>
                              </cntAddress>
                              <cntPhone>
                                <voiceNum tddtty="">301-427-8137</voiceNum>
                                <faxNum>301-713-4137</faxNum>
                              </cntPhone>
                              <cntHours>0700 - 1800 EST/EDT</cntHours>
                              <cntOnlineRes>
                                <linkage>https://www.fisheries.noaa.gov/about/office-science-and-technology</linkage>
                                <protocol>REST Service</protocol>
                                <orName>NMFS Office of Science and Technology</orName>
                                <orDesc>NOAA Fisheries Office of Science and Technology</orDesc>
                                <orFunct>
                                  <OnFunctCd value="002" />
                                </orFunct>
                              </cntOnlineRes>
                            </rpCntInfo>
                            <displayName>NMFS Office of Science and Technology (Distributor)</displayName>
                            <editorSave>True</editorSave>
                            <role>
                                <RoleCd value="005"/>
                            </role>
                        </distorCont>
                    </distributor>
                    '''
        _tree = etree.parse(BytesIO(xml_file), etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
        _root = _tree.getroot()
        distributor = target_root.xpath(f"./distInfo/distributor")
        if len(distributor) == 0:
            target_root.xpath(f"./distInfo")[0].insert(distInfo_dict["distributor"], _root)
        elif len(distributor) == 1:
            distributor[0].getparent().replace(distributor[0], _root)
        else:
            pass
        del _root, _tree, xml_file
        #print(f"\n\t{etree.tostring(target_root.xpath(f'./distInfo/distributor')[0], encoding='UTF-8', method='xml', pretty_print=True).decode()}\n")
        del distributor

##        new_item_name = target_root.find("./Esri/DataProperties/itemProps/itemName").text
##        new_item_name = new_item_name.replace("IDW_Sample_Locations", "Sample_Locations") if "Sample_Locations" in new_item_name else new_item_name
##        onLineSrcs = target_root.findall("./distInfo/distTranOps/onLineSrc")
##        for onLineSrc in onLineSrcs:
##            if onLineSrc.find('./protocol').text == "ESRI REST Service":
##                old_linkage_element = onLineSrc.find('./linkage')
##                old_linkage = old_linkage_element.text
##                #print(old_linkage, flush=True)
##                old_item_name = old_linkage[old_linkage.find("/services/")+len("/services/"):old_linkage.find("/FeatureServer")]
##                new_linkage = old_linkage.replace(old_item_name, f"{new_item_name}_{date_code(project)}")
##                #print(new_linkage, flush=True)
##                old_linkage_element.text = new_linkage
##                #print(old_linkage_element.text, flush=True)
##                del old_linkage_element
##                del old_item_name, old_linkage, new_linkage
##            else:
##                pass
##            del onLineSrc
##        del onLineSrcs, new_item_name
##        #print(etree.tostring(target_root.xpath("./distInfo")[0], encoding='UTF-8', method='xml', pretty_print=True).decode())

        new_item_name = target_root.find("./Esri/DataProperties/itemProps/itemName").text
        if "Sample_Locations" in new_item_name:
            _new_item_name = new_item_name.replace("IDW_Sample_Locations", "Sample_Locations") if "Sample_Locations" in new_item_name else new_item_name
            onLineSrcs = target_root.findall("./distInfo/distTranOps/onLineSrc")
            for onLineSrc in onLineSrcs:
                onLineSrc.find('./protocol').text = "ESRI REST Service"
                old_linkage_element = onLineSrc.find('./linkage')
                old_linkage = old_linkage_element.text
                #print(old_linkage, flush=True)
                old_item_name = old_linkage[old_linkage.find("/services/")+len("/services/"):old_linkage.find("/FeatureServer")]
                if old_item_name != f"{_new_item_name}_{date_code(project)}":
                    #print('remove')
                    onLineSrc.getparent().remove(onLineSrc)
                else:
                    pass
                #print(old_item_name, f"{_new_item_name}_{date_code(project)}")
                #new_linkage = old_linkage.replace(old_item_name, f"{_new_item_name}_{date_code(project)}")
                #print(new_linkage, flush=True)
                #old_linkage_element.text = new_linkage
                #print(old_linkage_element.text, flush=True)
                del old_linkage_element
                del old_item_name, old_linkage #, new_linkage
                #print(etree.tostring(onLineSrc, encoding='UTF-8', method='xml', pretty_print=True).decode())
                #if onLineSrc.find('./protocol').text == "ESRI REST Service":
                #    old_linkage_element = onLineSrc.find('./linkage')
                #    old_linkage = old_linkage_element.text
                #    #print(old_linkage, flush=True)
                #    old_item_name = old_linkage[old_linkage.find("/services/")+len("/services/"):old_linkage.find("/FeatureServer")]
                #    new_linkage = old_linkage.replace(old_item_name, f"{new_item_name}_{date_code(project)}")
                #    #print(new_linkage, flush=True)
                #    old_linkage_element.text = new_linkage
                #    #print(old_linkage_element.text, flush=True)
                #    del old_linkage_element
                #    del old_item_name, old_linkage, new_linkage
                #else:
                #    pass
                del onLineSrc
            #print(_new_item_name)
            del onLineSrcs, _new_item_name
        else:
            pass
        #print(etree.tostring(target_root.xpath("./distInfo")[0], encoding='UTF-8', method='xml', pretty_print=True).decode())
        #print(new_item_name)
        del new_item_name

        distInfo = target_root.xpath("./distInfo")
        #print(len(distInfo))
        for dist_Info in distInfo:
            dist_Info[:] = sorted(dist_Info, key=lambda x: distInfo_dict[x.tag])
            #print(etree.tostring(dist_Info, encoding='UTF-8', method='xml', pretty_print=True).decode())
            del dist_Info
        del distInfo

        # No changes needed below
        #print(etree.tostring(target_tree, encoding='UTF-8', method='xml', pretty_print=True).decode())
        etree.indent(target_root, space='    ')
        dataset_md_xml = etree.tostring(target_tree, encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True)

        SaveBackXml = True
        if SaveBackXml:
            dataset_md = md.Metadata(dataset_path)
            dataset_md.xml = dataset_md_xml
            dataset_md.save()
            dataset_md.synchronize("ALWAYS")
            dataset_md.save()
            #dataset_md.reload()
            del dataset_md
        else:
            pass
        del SaveBackXml
        del dataset_md_xml

        # Declared Varaiables
        del export_folder, project
        del dataset_name
        del distInfo_dict
        del target_tree, target_root
        # Imports
        del etree, StringIO, BytesIO, copy, md
        # Function Parameters
        del dataset_path
    except KeyboardInterrupt:
        raise SystemExit
    except:
        traceback.print_exc()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function at line number {inspect.stack()[0][2]}\n\t##--> '{', '.join(rk)}' <--##"); del rk
        return True
    finally:
        pass

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

        #Imports
        from lxml import etree
        from io import StringIO, BytesIO
        #import copy
        #import arcpy
        from arcpy import metadata as md

        arcpy.env.overwriteOutput = True
        arcpy.env.parallelProcessingFactor = "100%"

        # Test if passed workspace exists, if not raise SystemExit
        if not arcpy.Exists(project_gdb):
            print(f"{os.path.basename(project_gdb)} is missing!!")
            print(f"{project_gdb}")

        project_folder = os.path.dirname(project_gdb)
        scratch_folder = rf"{project_folder}\Scratch"
        #print(project_folder)

        arcpy.env.workspace        = project_gdb
        arcpy.env.scratchWorkspace = rf"{scratch_folder}\scratch.gdb"

        #metadata_dictionary = dataset_title_dict(project_gdb)
        #for key in metadata_dictionary:
        #    print(key, metadata_dictionary[key])
        #    del key

        datasets = list()
        walk = arcpy.da.Walk(arcpy.env.workspace)
        for dirpath, dirnames, filenames in walk:
            for filename in filenames:
                datasets.append(os.path.join(dirpath, filename))
                del filename
            del dirpath, dirnames, filenames
        del walk

        del scratch_folder, project_folder

        print(f"Processing: {os.path.basename(arcpy.env.workspace)} in the '{inspect.stack()[0][3]}' function")

        # Points
        #for dataset_path in sorted([ds for ds in datasets if ds.endswith("AI_Sample_Locations") or ds.endswith("AI_IDW_Sample_Locations")]):
        #for dataset_path in sorted([ds for ds in datasets if ds.endswith("_Sample_Locations")]):
        #for dataset_path in sorted([ds for ds in datasets if ds.endswith("EBS_Sample_Locations") or ds.endswith("EBS_IDW_Sample_Locations")]):
        # Polylines
        #for dataset_path in sorted([ds for ds in datasets if ds.endswith("AI_Boundary") or ds.endswith("AI_IDW_Boundary")]):
        # Polygons
        #for dataset_path in sorted([ds for ds in datasets if ds.endswith("AI_Region") or ds.endswith("AI_IDW_Region")]):
        # Table
        #for dataset_path in sorted([ds for ds in datasets if ds.endswith("AI_Indicators") or ds.endswith("AI_IDW_Indicators")]):
        #for dataset_path in sorted([ds for ds in datasets if ds.endswith("Indicators")]):
        # Raster
        #for dataset_path in sorted([ds for ds in datasets if ds.endswith("AI_Bathymetry") or ds.endswith("AI_IDW_Bathymetry")]):
        #for dataset_path in sorted([ds for ds in datasets if ds.endswith("AI_Raster_Mask") or ds.endswith("AI_IDW_Raster_Mask")]):
        #for dataset_path in sorted([ds for ds in datasets if ds.endswith("AI_Raster_Mosaic") or ds.endswith("AI_IDW_Mosaic")]):
        #for dataset_path in sorted([ds for ds in datasets if any (ds.endswith(d) for d in ["Datasets", "AI_IDW_Extent_Points", "AI_IDW_Latitude", "AI_IDW_Raster_Mask"])]):
        #for dataset_path in sorted([ds for ds in datasets if "AI_IDW" in os.path.basename(ds)]):
        #for dataset_path in sorted([ds for ds in datasets if "EBS_IDW" in os.path.basename(ds)]):
        #for dataset_path in sorted([ds for ds in datasets if any (ds.endswith(d) for d in ["Species_Filer", "EBS_IDW_Extent_Points", "EBS_IDW_Latitude", "EBS_IDW_Raster_Mask"])]):
        #for dataset_path in sorted([ds for ds in datasets if any (ds.endswith(d) for d in ['SpeciesPersistenceIndicatorNetWTCPUE', 'SpeciesPersistenceIndicatorPercentileWTCPUE', 'Species_Filter', 'DisMAP_Survey_Info'])]):
        for dataset_path in sorted([ds for ds in datasets if any (ds.endswith(d) for d in ['Species_Filter'])]):

        # ALL
        #for dataset_path in sorted(datasets):
            #dataset_name = os.path.basename(dataset_path)
            #print(f"Dataset: '{dataset_name}'\n\tType: '{arcpy.Describe(dataset_path).datasetType}'")
            #del dataset_name

            ImportBasicTemplateXml = True
            if ImportBasicTemplateXml:
                import_basic_template_xml(dataset_path)
            else:
                pass
            del ImportBasicTemplateXml

            BasicMetadataReport = False # Just a report
            if BasicMetadataReport:
                basic_metadata_report(dataset_path)
            else:
                pass
            del BasicMetadataReport

            MetadataEsriReport = False
            if MetadataEsriReport:
                metadata_esri_report(dataset_path)
            else:
                pass
            del MetadataEsriReport

            MetadataDataIdInfoReport = False
            if MetadataDataIdInfoReport:
                metadata_dataidinfo_report(dataset_path)
            else:
                pass
            del MetadataDataIdInfoReport

            MetadataDqInfoReport = False
            if MetadataDqInfoReport:
                metadata_dq_info_report(dataset_path)
            else:
                pass
            del MetadataDqInfoReport

            MetadataDistInfoReport = False
            if MetadataDistInfoReport:
                metadata_dist_info_report(dataset_path)
            else:
                pass
            del MetadataDistInfoReport

            UpdateEaInfoXmlElements = False
            if UpdateEaInfoXmlElements:
                update_eainfo_xml_elements(dataset_path)
            else:
                pass
            del UpdateEaInfoXmlElements

            AddUpdateDates = False
            if AddUpdateDates:
                add_update_dates(dataset_path)
            else:
                pass
            del AddUpdateDates

            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # A keeper. Adds entity attribute details, if missing
            InsertMissingElements = False
            if InsertMissingElements:
                insert_missing_elements(dataset_path)
            else:
                pass
            del InsertMissingElements

            AddUpdateContacts = False
            if AddUpdateContacts:
                add_update_contacts(dataset_path=dataset_path)
            else:
                pass
            del AddUpdateContacts

            CreateFeatureClassLayers = False
            if CreateFeatureClassLayers:
                create_feature_class_layers(dataset_path=dataset_path)
            else:
                pass
            del CreateFeatureClassLayers

            PrintTargetTree = False
            if PrintTargetTree:
                dataset_md = md.Metadata(dataset_path)
                #dataset_md.synchronize("ALWAYS")
                #dataset_md.save()
                #dataset_md.reload()
                # Parse the XML
                export_folder  = rf"{os.path.dirname(os.path.dirname(dataset_path))}\Export"
                #print(export_folder)
                #_target_tree = etree.parse(StringIO(dataset_md.xml), parser=etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
                #etree.indent(_target_tree, "    ")
                #_target_tree.write(rf"{export_folder}\{os.path.basename(dataset_path)}.xml", encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True)
                #print(etree.tostring(_target_tree, encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True).decode())
                #del _target_tree
                dataset_md.saveAsXML(rf"{export_folder}\{os.path.basename(dataset_path)}.xml", "TEMPLATE")
                del export_folder
                del dataset_md
            else:
                pass
            del PrintTargetTree
            del dataset_path

        CompactGDB = False
        if CompactGDB:
            print(f"Compact GDB")
            arcpy.management.Compact(project_gdb)
            print("\t"+arcpy.GetMessages().replace("\n", "\n\t")+"\n")
        else:
            pass
        del CompactGDB

        # Declared Varaiables
        del datasets
        # Imports
        del etree, StringIO, BytesIO, md
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
    except KeyboardInterrupt:
        raise SystemExit
    except Exception:
        raise SystemExit
    except:
        traceback.print_exc()
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
        #project_name = "April 1 2023"
        #project_name = "July 1 2024"
        project_name   = "December 1 2024"
        #project_name   = "June 1 2025"
        project_folder = rf"{base_project_folder}\{project_name}"
        project_gdb    = rf"{project_folder}\{project_name}.gdb"

        main(project_gdb=project_gdb)

        # Declared Variables
        #del collective_title
        del project_gdb, project_name, project_folder, base_project_folder
        # Imports
    except:
        traceback.print_exc()
    else:
        pass
    finally:
        pass