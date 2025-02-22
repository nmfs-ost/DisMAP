#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      john.f.kennedy
#
# Created:     09/01/2024
# Copyright:   (c) john.f.kennedy 2024
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import arcpy, os

def xmlMetadataDictionary(table=""):

    md_title              = table.replace("_", " ")
    md_tags               = f"{md_title}: Tags"
    md_summary            = f"{md_title}: Summary"
    md_description        = f"{md_title}: Description"
    md_credits            = f"{md_title}: Credits"
    md_access_constraints = "***No Warranty*** The user assumes the entire risk related to its use of these data. NMFS is providing these data 'as is' and NMFS disclaims any and all warranties, whether express or implied, including (without limitation) any implied warranties of merchantability or fitness for a particular purpose. No warranty expressed or implied is made regarding the accuracy or utility of the data on any other system or for general or scientific purposes, nor shall the act of distribution constitute any such warranty. It is strongly recommended that careful attention be paid to the contents of the metadata file associated with these data to evaluate dataset limitations, restrictions or intended use. In no event will NMFS be liable to you or to any third party for any direct, indirect, incidental, consequential, special or exemplary damages or lost profit resulting from any use or misuse of these data."

    if "Region" in table or "Boundary"  in table:
        md_tags        = "distribution, seasonal distribution, fish, invertebrates, climate change, fishery-independent surveys, ecological dynamics, oceans, biosphere, earth science, species/population interactions, aquatic sciences, fisheries, range changes"
        md_summary     = "These files contain the spatial boundaries of the NOAA Fisheries Bottom-trawl surveys. This data set covers 8 regions of the United States: Northeast, Southeast, Gulf of Mexico, West Coast, Bering Sea, Aleutian Islands, Gulf of Alaska, and Hawai'i Islands."
        md_description = "These data were created as part of the DisMAP project to enable visualization and analysis of changes in fish and invertebrate distributions. These layers provide information on the spatial extent/boundaries of the bottom trawl surveys. Information on species distributions is of paramount importance for understanding and preparing for climate-change impacts, and plays a key role in climate-ready fisheries management."
        md_credits     = "The region boundaries were produced by NMFS OST in partnership with OceanAdapt at Rutgers University"

    if "DisMAP_Regions" in table:      md_tags = f"Aleutian Islands, Bering Sea, Eastern and Northern Bering Sea, Gulf of Alaska, Gulf of Mexico, Hawaii Islands, Hawai'i Islands, West Coast, Northeast US, Southeast US, {md_tags}"

    if "AI_IDW_Boundary" in table:       md_tags = f"Aleutian Islands, {md_tags}"
    if "EBS_IDW_Boundary" in table:      md_tags = f"Bering Sea, {md_tags}"
    if "ENBS_IDW_Boundary" in table:     md_tags = f"Eastern and Northern Bering Sea, {md_tags}"
    if "GMEX_IDW_Boundary" in table:     md_tags = f"Gulf of Mexico, {md_tags}"
    if "GOA_IDW_Boundary" in table:      md_tags = f"Gulf of Alaska, {md_tags}"
    if "HI_IDW_Boundary" in table:       md_tags = f"Hawaii Islands, Hawai'i Islands, {md_tags}"
    if "NBS_IDW_Boundary" in table:      md_tags = f"Northern Bering Sea, {md_tags}"
    if "NEUS_FAL_IDW_Boundary" in table: md_tags = f"Northeast US, {md_tags}"
    if "NEUS_SPR_IDW_Boundary" in table: md_tags = f"Northeast US, {md_tags}"
    if "SEUS_FAL_IDW_Boundary" in table: md_tags = f"Southeast US, {md_tags}"
    if "SEUS_SPR_IDW_Boundary" in table: md_tags = f"Southeast US, {md_tags}"
    if "SEUS_SUM_IDW_Boundary" in table: md_tags = f"Southeast US, {md_tags}"
    if "WC_GLMME_Boundary" in table:     md_tags = f"West Coast, {md_tags}"
    if "WC_GFDL_Boundary" in table:      md_tags = f"West Coast, {md_tags}"
    if "WC_ANN_IDW_Boundary" in table:   md_tags = f"West Coast, {md_tags}"
    if "WC_TRI_IDW_Boundary" in table:   md_tags = f"West Coast, {md_tags}"

    if "AI_IDW_Extent_Points" in table:       md_tags = f"Aleutian Islands, {md_tags}"
    if "EBS_IDW_Extent_Points" in table:      md_tags = f"Bering Sea, {md_tags}"
    if "ENBS_IDW_Extent_Points" in table:     md_tags = f"Eastern and Northern Bering Sea, {md_tags}"
    if "GMEX_IDW_Extent_Points" in table:     md_tags = f"Gulf of Mexico, {md_tags}"
    if "GOA_IDW_Extent_Points" in table:      md_tags = f"Gulf of Alaska, {md_tags}"
    if "HI_IDW_Extent_Points" in table:       md_tags = f"Hawaii Islands, Hawai'i Islands, {md_tags}"
    if "NBS_IDW_Extent_Points" in table:      md_tags = f"Northern Bering Sea, {md_tags}"
    if "NEUS_FAL_IDW_Extent_Points" in table: md_tags = f"Northeast US, {md_tags}"
    if "NEUS_SPR_IDW_Extent_Points" in table: md_tags = f"Northeast US, {md_tags}"
    if "SEUS_FAL_IDW_Extent_Points" in table: md_tags = f"Southeast US, {md_tags}"
    if "SEUS_SPR_IDW_Extent_Points" in table: md_tags = f"Southeast US, {md_tags}"
    if "SEUS_SUM_IDW_Extent_Points" in table: md_tags = f"Southeast US, {md_tags}"
    if "WC_GLMME_Extent_Points" in table:     md_tags = f"West Coast, {md_tags}"
    if "WC_GFDL_Extent_Points" in table:      md_tags = f"West Coast, {md_tags}"
    if "WC_ANN_IDW_Extent_Points" in table:   md_tags = f"West Coast, {md_tags}"
    if "WC_TRI_IDW_Extent_Points" in table:   md_tags = f"West Coast, {md_tags}"

    if "AI_IDW_Fishnet" in table:       md_tags = f"Aleutian Islands, {md_tags}"
    if "EBS_IDW_Fishnet" in table:      md_tags = f"Bering Sea, {md_tags}"
    if "ENBS_IDW_Fishnet" in table:     md_tags = f"Eastern and Northern Bering Sea, {md_tags}"
    if "GMEX_IDW_Fishnet" in table:     md_tags = f"Gulf of Mexico, {md_tags}"
    if "GOA_IDW_Fishnet" in table:      md_tags = f"Gulf of Alaska, {md_tags}"
    if "HI_IDW_Fishnet" in table:       md_tags = f"Hawaii Islands, Hawai'i Islands, {md_tags}"
    if "NBS_IDW_Fishnet" in table:      md_tags = f"Northern Bering Sea, {md_tags}"
    if "NEUS_FAL_IDW_Fishnet" in table: md_tags = f"Northeast US, {md_tags}"
    if "NEUS_SPR_IDW_Fishnet" in table: md_tags = f"Northeast US, {md_tags}"
    if "SEUS_FAL_IDW_Fishnet" in table: md_tags = f"Southeast US, {md_tags}"
    if "SEUS_SPR_IDW_Fishnet" in table: md_tags = f"Southeast US, {md_tags}"
    if "SEUS_SUM_IDW_Fishnet" in table: md_tags = f"Southeast US, {md_tags}"
    if "WC_GLMME_Fishnet" in table:     md_tags = f"West Coast, {md_tags}"
    if "WC_GFDL_Fishnet" in table:      md_tags = f"West Coast, {md_tags}"
    if "WC_ANN_IDW_Fishnet" in table:   md_tags = f"West Coast, {md_tags}"
    if "WC_TRI_IDW_Fishnet" in table:   md_tags = f"West Coast, {md_tags}"

    if "AI_IDW_Lat_Long" in table:       md_tags = f"Aleutian Islands, {md_tags}"
    if "EBS_IDW_Lat_Long" in table:      md_tags = f"Bering Sea, {md_tags}"
    if "ENBS_IDW_Lat_Long" in table:     md_tags = f"Eastern and Northern Bering Sea, {md_tags}"
    if "GMEX_IDW_Lat_Long" in table:     md_tags = f"Gulf of Mexico, {md_tags}"
    if "GOA_IDW_Lat_Long" in table:      md_tags = f"Gulf of Alaska, {md_tags}"
    if "HI_IDW_Lat_Long" in table:       md_tags = f"Hawaii Islands, Hawai'i Islands, {md_tags}"
    if "NBS_IDW_Lat_Long" in table:      md_tags = f"Northern Bering Sea, {md_tags}"
    if "NEUS_FAL_IDW_Lat_Long" in table: md_tags = f"Northeast US, {md_tags}"
    if "NEUS_SPR_IDW_Lat_Long" in table: md_tags = f"Northeast US, {md_tags}"
    if "SEUS_FAL_IDW_Lat_Long" in table: md_tags = f"Southeast US, {md_tags}"
    if "SEUS_SPR_IDW_Lat_Long" in table: md_tags = f"Southeast US, {md_tags}"
    if "SEUS_SUM_IDW_Lat_Long" in table: md_tags = f"Southeast US, {md_tags}"
    if "WC_GLMME_Lat_Long" in table:     md_tags = f"West Coast, {md_tags}"
    if "WC_GFDL_Lat_Long" in table:      md_tags = f"West Coast, {md_tags}"
    if "WC_ANN_IDW_Lat_Long" in table:   md_tags = f"West Coast, {md_tags}"
    if "WC_TRI_IDW_Lat_Long" in table:   md_tags = f"West Coast, {md_tags}"

    if "AI_IDW_Raster_Mask" in table:       md_tags = f"Aleutian Islands, {md_tags}"
    if "EBS_IDW_Raster_Mask" in table:      md_tags = f"Bering Sea, {md_tags}"
    if "ENBS_IDW_Raster_Mask" in table:     md_tags = f"Eastern and Northern Bering Sea, {md_tags}"
    if "GMEX_IDW_Raster_Mask" in table:     md_tags = f"Gulf of Mexico, {md_tags}"
    if "GOA_IDW_Raster_Mask" in table:      md_tags = f"Gulf of Alaska, {md_tags}"
    if "HI_IDW_Raster_Mask" in table:       md_tags = f"Hawaii Islands, Hawai'i Islands, {md_tags}"
    if "NBS_IDW_Raster_Mask" in table:      md_tags = f"Northern Bering Sea, {md_tags}"
    if "NEUS_FAL_IDW_Raster_Mask" in table: md_tags = f"Northeast US, {md_tags}"
    if "NEUS_SPR_IDW_Raster_Mask" in table: md_tags = f"Northeast US, {md_tags}"
    if "SEUS_FAL_IDW_Raster_Mask" in table: md_tags = f"Southeast US, {md_tags}"
    if "SEUS_SPR_IDW_Raster_Mask" in table: md_tags = f"Southeast US, {md_tags}"
    if "SEUS_SUM_IDW_Raster_Mask" in table: md_tags = f"Southeast US, {md_tags}"
    if "WC_GLMME_Raster_Mask" in table:     md_tags = f"West Coast, {md_tags}"
    if "WC_GFDL_Raster_Mask" in table:      md_tags = f"West Coast, {md_tags}"
    if "WC_ANN_IDW_Raster_Mask" in table:   md_tags = f"West Coast, {md_tags}"
    if "WC_TRI_IDW_Raster_Mask" in table:   md_tags = f"West Coast, {md_tags}"

    if "AI_IDW_Region" in table:       md_tags = f"Aleutian Islands, {md_tags}"
    if "EBS_IDW_Region" in table:      md_tags = f"Bering Sea, {md_tags}"
    if "ENBS_IDW_Region" in table:     md_tags = f"Eastern and Northern Bering Sea, {md_tags}"
    if "GMEX_IDW_Region" in table:     md_tags = f"Gulf of Mexico, {md_tags}"
    if "GOA_IDW_Region" in table:      md_tags = f"Gulf of Alaska, {md_tags}"
    if "HI_IDW_Region" in table:       md_tags = f"Hawaii Islands, Hawai'i Islands, {md_tags}"
    if "NBS_IDW_Region" in table:      md_tags = f"Northern Bering Sea, {md_tags}"
    if "NEUS_FAL_IDW_Region" in table: md_tags = f"Northeast US, {md_tags}"
    if "NEUS_SPR_IDW_Region" in table: md_tags = f"Northeast US, {md_tags}"
    if "SEUS_FAL_IDW_Region" in table: md_tags = f"Southeast US, {md_tags}"
    if "SEUS_SPR_IDW_Region" in table: md_tags = f"Southeast US, {md_tags}"
    if "SEUS_SUM_IDW_Region" in table: md_tags = f"Southeast US, {md_tags}"
    if "WC_GLMME_Region" in table:     md_tags = f"West Coast, {md_tags}"
    if "WC_GFDL_Region" in table:      md_tags = f"West Coast, {md_tags}"
    if "WC_ANN_IDW_Region" in table:   md_tags = f"West Coast, {md_tags}"
    if "WC_TRI_IDW_Region" in table:   md_tags = f"West Coast, {md_tags}"

    if not table: return [f"Title", "Tags", "Summary", "Description", "Credits", "Access Constraints"]
    elif table: return [md_title, md_tags, md_summary, md_description, md_credits, md_access_constraints]
    else: return None

def main():
    try:
        pass
    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]; tbinfo = traceback.format_tb(tb)[0]; del tb
        # Concatenate information together concerning the error into a message string
        pymsg = f"Python ##-->{tbinfo}\t" + str(sys.exc_info()[1]).replace("\n", "\n\t")
        arcpy.AddError(pymsg); del pymsg
        if arcpy.GetMessages(2):
            # Return tool error messages for use with a script tool
            msgs = f"Arcpy ##-->{tbinfo}\t" + arcpy.GetMessages(2).replace("\n", "\n\t")
            arcpy.AddError(msgs); del msgs
    else:
        leave_out_keys = "local_keys, leave_out_keys, sys, time, datetime, math, numpy, arcpy, main, os"
        local_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
        if local_keys:
            arcpy.AddWarning(f"Local Keys: #-> '{', '.join(local_keys)}' <-#"); del local_keys

def tester():
    try:

        tables = [  "Datasets", "DisMAP_Regions", "Species_Filter", "AI_IDW_Boundary",
                    "EBS_IDW_Boundary", "ENBS_IDW_Boundary", "GMEX_IDW_Boundary",
                    "GOA_IDW_Boundary", "HI_IDW_Boundary", "NBS_IDW_Boundary",
                    "NEUS_FAL_IDW_Boundary", "NEUS_SPR_IDW_Boundary", "SEUS_FAL_IDW_Boundary",
                    "SEUS_SPR_IDW_Boundary", "SEUS_SUM_IDW_Boundary", "WC_GLMME_Boundary",
                    "WC_GFDL_Boundary", "WC_ANN_IDW_Boundary", "WC_TRI_IDW_Boundary",
                    "AI_IDW_Extent_Points", "EBS_IDW_Extent_Points", "ENBS_IDW_Extent_Points",
                    "GMEX_IDW_Extent_Points", "GOA_IDW_Extent_Points", "HI_IDW_Extent_Points",
                    "NBS_IDW_Extent_Points", "NEUS_FAL_IDW_Extent_Points", "NEUS_SPR_IDW_Extent_Points",
                    "SEUS_FAL_IDW_Extent_Points", "SEUS_SPR_IDW_Extent_Points",
                    "SEUS_SUM_IDW_Extent_Points", "WC_GLMME_Extent_Points", "WC_GFDL_Extent_Points",
                    "WC_ANN_IDW_Extent_Points", "WC_TRI_IDW_Extent_Points", "AI_IDW_Fishnet",
                    "EBS_IDW_Fishnet", "ENBS_IDW_Fishnet", "GMEX_IDW_Fishnet", "GOA_IDW_Fishnet",
                    "HI_IDW_Fishnet", "NBS_IDW_Fishnet",
                    "NEUS_FAL_IDW_Fishnet",
                    "NEUS_SPR_IDW_Fishnet",
                    "SEUS_FAL_IDW_Fishnet",
                    "SEUS_SPR_IDW_Fishnet",
                    "SEUS_SUM_IDW_Fishnet",
                    "WC_GLMME_Fishnet",
                    "WC_GFDL_Fishnet",
                    "WC_ANN_IDW_Fishnet",
                    "WC_TRI_IDW_Fishnet",
                    "AI_IDW_Lat_Long",
                    "EBS_IDW_Lat_Long",
                    "ENBS_IDW_Lat_Long",
                    "GMEX_IDW_Lat_Long",
                    "GOA_IDW_Lat_Long",
                    "HI_IDW_Lat_Long",
                    "NBS_IDW_Lat_Long",
                    "NEUS_FAL_IDW_Lat_Long",
                    "NEUS_SPR_IDW_Lat_Long",
                    "SEUS_FAL_IDW_Lat_Long",
                    "SEUS_SPR_IDW_Lat_Long",
                    "SEUS_SUM_IDW_Lat_Long",
                    "WC_GLMME_Lat_Long",
                    "WC_GFDL_Lat_Long",
                    "WC_ANN_IDW_Lat_Long",
                    "WC_TRI_IDW_Lat_Long",
                    "AI_IDW_Raster_Mask",
                    "EBS_IDW_Raster_Mask",
                    "ENBS_IDW_Raster_Mask",
                    "GMEX_IDW_Raster_Mask",
                    "GOA_IDW_Raster_Mask",
                    "HI_IDW_Raster_Mask",
                    "NBS_IDW_Raster_Mask",
                    "NEUS_FAL_IDW_Raster_Mask",
                    "NEUS_SPR_IDW_Raster_Mask",
                    "SEUS_FAL_IDW_Raster_Mask",
                    "SEUS_SPR_IDW_Raster_Mask",
                    "SEUS_SUM_IDW_Raster_Mask",
                    "WC_GLMME_Raster_Mask",
                    "WC_GFDL_Raster_Mask",
                    "WC_ANN_IDW_Raster_Mask",
                    "WC_TRI_IDW_Raster_Mask",
                    "AI_IDW_Region",
                    "EBS_IDW_Region",
                    "ENBS_IDW_Region",
                    "GMEX_IDW_Region",
                    "GOA_IDW_Region",
                    "HI_IDW_Region",
                    "NBS_IDW_Region",
                    "NEUS_FAL_IDW_Region",
                    "NEUS_SPR_IDW_Region",
                    "SEUS_FAL_IDW_Region",
                    "SEUS_SPR_IDW_Region",
                    "SEUS_SUM_IDW_Region",
                    "WC_GLMME_Region",
                    "WC_GFDL_Region",
                    "WC_ANN_IDW_Region",
                    "WC_TRI_IDW_Region",]

        metadata_dictionary = {}
        for table in tables:
            #print(table)
            #for item in xmlMetadataDictionary(table):
            #    print(f"\t{item}")
            md_title, md_tags, md_summary, md_description, md_credits, md_access_constraints = xmlMetadataDictionary(table)
            #print(f"\t{md_title}")
            #print(f"\t{md_tags}")
            #print(f"\t{md_summary}")
            #print(f"\t{md_description}")
            #print(f"\t{md_credits}")
            #print(f"\t{md_access_constraints}")

            metadata_dictionary[table] = {"md_title" : md_title, "md_tags" : md_tags,
                                          "md_summary" : md_summary, "md_description" : md_description,
                                          "md_credits" : md_credits,
                                          "md_access_constraints" : md_access_constraints,}

##            for key in metadata_dictionary:
##                print(f"{key}")
##                md = metadata_dictionary[key]
##                for m in md:
##                    print(f"\t{m}: {md[m]}")
##                    del m
##                del md
##                del key

            del md_title, md_tags, md_summary, md_description, md_credits, md_access_constraints
            del table

        import json
        metadata_dictionary_json = r"C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP\DisMAP April 1 2023\CSV Data\metadata_dictionary.json"

        # Write to File
        with open(metadata_dictionary_json, "w") as json_file:
            json.dump(metadata_dictionary, json_file, indent=4)
        del json_file, json

        del metadata_dictionary, metadata_dictionary_json

        del tables

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]; tbinfo = traceback.format_tb(tb)[0]; del tb
        # Concatenate information together concerning the error into a message string
        pymsg = f"Python ##-->{tbinfo}\t" + str(sys.exc_info()[1]).replace("\n", "\n\t")
        arcpy.AddError(pymsg); del pymsg
        if arcpy.GetMessages(2):
            # Return tool error messages for use with a script tool
            msgs = f"Arcpy ##-->{tbinfo}\t" + arcpy.GetMessages(2).replace("\n", "\n\t")
            arcpy.AddError(msgs); del msgs
    else:
        leave_out_keys = "local_keys, leave_out_keys, sys, time, datetime, math, numpy, arcpy, main, os"
        local_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
        if local_keys:
            arcpy.AddWarning(f"Local Keys: #-> '{', '.join(local_keys)}' <-#"); del local_keys


if __name__ == '__main__':
    try:
        pass

        #tester()

    except:
        import sys, traceback
        # Get the traceback object
        tb = sys.exc_info()[2]; tbinfo = traceback.format_tb(tb)[0]; del tb
        # Concatenate information together concerning the error into a message string
        pymsg = f"Python ##-->{tbinfo}\t" + str(sys.exc_info()[1]).replace("\n", "\n\t")
        arcpy.AddError(pymsg); del pymsg
        if arcpy.GetMessages(2):
            # Return tool error messages for use with a script tool
            msgs = f"Arcpy ##-->{tbinfo}\t" + arcpy.GetMessages(2).replace("\n", "\n\t")
            arcpy.AddError(msgs); del msgs
    else:
        leave_out_keys = "local_keys, leave_out_keys, sys, time, datetime, math, \
                          numpy, arcpy, main, os, addFields, alterFields, basicMetadata, \
                          compareXML, convertSeconds, createFeatureClass, createMetadata, \
                          createTable, dateCode, deleteFields, dTypesCSV, dTypesGDB, \
                          exportMetadata, importMetadata, prettyXML, zipCsvData, \
                          unZipData, zipDatasetShapeFiles, updateDatasetsVersionTool, \
                          tester, fieldDefinitions, tableDefinitions, xmlMetadataDictionary"
        local_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
        if local_keys:
            arcpy.AddWarning(f"Local Keys: #-> '{', '.join(local_keys)}' <-#"); del local_keys