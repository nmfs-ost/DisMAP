# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      john.f.kennedy
#
# Created:     03/03/2024
# Copyright:   (c) john.f.kennedy 2024
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os, sys # built-ins first
import traceback
import importlib
import inspect

import arcpy # third-parties second

sys.path.append(os.path.dirname(__file__))

##def check_transformation(fc, cs):
##    dsc_in = arcpy.Describe(fc)
##    insr = dsc_in.spatialReference
##
##    # if output coordinate system is set and is different than the input coordinate system
##    if cs and (cs.name != insr.name):
##        translist = arcpy.ListTransformations(insr, cs, dsc_in.extent)
##        trans = translist[0] if translist else ""
##        arcpy.AddMessage(f"\t{trans}\n")
##        #for trans in translist:
##        #    arcpy.AddMessage(f"\t{trans}")
##        return trans

def feature_compare(input_base_gdb="", input_test_gdb=""):
    try:
        # https://en.wikipedia.org/wiki/Decimal_degrees

        arcpy.env.overwriteOutput = True
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2)
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        #arcpy.AddMessage(f"{'-' * 90}\n")

        arcpy.AddMessage(f"Feature Comparison:\n\t Input Base GDB: {input_base_gdb}\n\t Input Target GDB: {input_test_gdb}")

        fc_dict = {
                    "AI_IDW_Boundary_Line"       : "AI_IDW_Boundary",
                    #"AI_IDW_Extent_Points"       : "AI_IDW_Extent_Points",
                    "AI_IDW_Points"              : "AI_IDW_Extent_Points",
                    "AI_IDW_Fishnet"             : "AI_IDW_Fishnet",
                    "AI_IDW_Lat_Long"            : "AI_IDW_Lat_Long",
                    "AI_IDW_Survey_Area"         : "AI_IDW_Region",
                    "AI_Sample_Locations"        : "AI_IDW_Sample_Locations",
                    "DisMAP_Regions"             : "DisMAP_Regions",
                    "EBS_IDW_Boundary_Line"      : "EBS_IDW_Boundary",
                    #"EBS_IDW_Extent_Points"      : "EBS_IDW_Extent_Points",
                    "EBS_IDW_Points"             : "EBS_IDW_Extent_Points",
                    "EBS_IDW_Fishnet"            : "EBS_IDW_Fishnet",
                    "EBS_IDW_Lat_Long"           : "EBS_IDW_Lat_Long",
                    "EBS_IDW_Survey_Area"        : "EBS_IDW_Region",
                    "EBS_Sample_Locations"       : "EBS_IDW_Sample_Locations",
                    "ENBS_IDW_Boundary_Line"     : "ENBS_IDW_Boundary",
                    #"ENBS_IDW_Extent_Points"     : "ENBS_IDW_Extent_Points",
                    "ENBS_IDW_Points"            : "ENBS_IDW_Extent_Points",
                    "ENBS_IDW_Fishnet"           : "ENBS_IDW_Fishnet",
                    "ENBS_IDW_Lat_Long"          : "ENBS_IDW_Lat_Long",
                    "ENBS_IDW_Survey_Area"       : "ENBS_IDW_Region",
                    "ENBS_Sample_Locations"      : "ENBS_IDW_Sample_Locations",
                    "GMEX_IDW_Boundary_Line"     : "GMEX_IDW_Boundary",
                    #"GMEX_IDW_Extent_Points"     : "GMEX_IDW_Extent_Points",
                    "GMEX_IDW_Points"            : "GMEX_IDW_Extent_Points",
                    "GMEX_IDW_Fishnet"           : "GMEX_IDW_Fishnet",
                    "GMEX_IDW_Lat_Long"          : "GMEX_IDW_Lat_Long",
                    "GMEX_IDW_Survey_Area"       : "GMEX_IDW_Region",
                    "GMEX_Sample_Locations"      : "GMEX_IDW_Sample_Locations",
                    "GOA_IDW_Boundary_Line"      : "GOA_IDW_Boundary",
                    #"GOA_IDW_Extent_Points"      : "GOA_IDW_Extent_Points",
                    "GOA_IDW_Points"             : "GOA_IDW_Extent_Points",
                    "GOA_IDW_Fishnet"            : "GOA_IDW_Fishnet",
                    "GOA_IDW_Lat_Long"           : "GOA_IDW_Lat_Long",
                    "GOA_IDW_Survey_Area"        : "GOA_IDW_Region",
                    "GOA_Sample_Locations"       : "GOA_IDW_Sample_Locations",
                    "HI_IDW_Boundary_Line"       : "HI_IDW_Boundary",
                    #"HI_IDW_Extent_Points"       : "HI_IDW_Extent_Points",
                    "HI_IDW_Points"              : "HI_IDW_Extent_Points",
                    "HI_IDW_Fishnet"             : "HI_IDW_Fishnet",
                    "HI_IDW_Lat_Long"            : "HI_IDW_Lat_Long",
                    "HI_IDW_Survey_Area"         : "HI_IDW_Region",
                    "HI_Sample_Locations"        : "HI_IDW_Sample_Locations",
                    "NBS_IDW_Boundary_Line"      : "NBS_IDW_Boundary",
                    #"NBS_IDW_Extent_Points"      : "NBS_IDW_Extent_Points",
                    "NBS_IDW_Points"             : "NBS_IDW_Extent_Points",
                    "NBS_IDW_Fishnet"            : "NBS_IDW_Fishnet",
                    "NBS_IDW_Lat_Long"           : "NBS_IDW_Lat_Long",
                    "NBS_IDW_Survey_Area"        : "NBS_IDW_Region",
                    "NBS_Sample_Locations"       : "NBS_IDW_Sample_Locations",
                    "NEUS_FAL_IDW_Boundary_Line" : "NEUS_FAL_IDW_Boundary",
                    #"NEUS_FAL_IDW_Extent_Points" : "NEUS_FAL_IDW_Extent_Points",
                    "NEUS_FAL_IDW_Points"        : "NEUS_FAL_IDW_Extent_Points",
                    "NEUS_FAL_IDW_Fishnet"       : "NEUS_FAL_IDW_Fishnet",
                    "NEUS_FAL_IDW_Lat_Long"      : "NEUS_FAL_IDW_Lat_Long",
                    "NEUS_FAL_IDW_Survey_Area"   : "NEUS_FAL_IDW_Region",
                    "NEUS_FAL_Sample_Locations"  : "NEUS_FAL_IDW_Sample_Locations",
                    "NEUS_SPR_IDW_Boundary_Line" : "NEUS_SPR_IDW_Boundary",
                    #"NEUS_SPR_IDW_Extent_Points" : "NEUS_SPR_IDW_Extent_Points",
                    "NEUS_SPR_IDW_Points"        : "NEUS_SPR_IDW_Extent_Points",
                    "NEUS_SPR_IDW_Fishnet"       : "NEUS_SPR_IDW_Fishnet",
                    "NEUS_SPR_IDW_Lat_Long"      : "NEUS_SPR_IDW_Lat_Long",
                    "NEUS_SPR_IDW_Survey_Area"   : "NEUS_SPR_IDW_Region",
                    "NEUS_SPR_Sample_Locations"  : "NEUS_SPR_IDW_Sample_Locations",
                    "SEUS_FAL_IDW_Boundary_Line" : "SEUS_FAL_IDW_Boundary",
                    #"SEUS_FAL_IDW_Extent_Points" : "SEUS_FAL_IDW_Extent_Points",
                    "SEUS_FAL_IDW_Points"        : "SEUS_FAL_IDW_Extent_Points",
                    "SEUS_FAL_IDW_Fishnet"       : "SEUS_FAL_IDW_Fishnet",
                    "SEUS_FAL_IDW_Lat_Long"      : "SEUS_FAL_IDW_Lat_Long",
                    "SEUS_FAL_IDW_Survey_Area"   : "SEUS_FAL_IDW_Region",
                    "SEUS_FAL_Sample_Locations"  : "SEUS_FAL_IDW_Sample_Locations",
                    "SEUS_SPR_IDW_Boundary_Line" : "SEUS_SPR_IDW_Boundary",
                    #"SEUS_SPR_IDW_Extent_Points" : "SEUS_SPR_IDW_Extent_Points",
                    "SEUS_SPR_IDW_Points"        : "SEUS_SPR_IDW_Extent_Points",
                    "SEUS_SPR_IDW_Fishnet"       : "SEUS_SPR_IDW_Fishnet",
                    "SEUS_SPR_IDW_Lat_Long"      : "SEUS_SPR_IDW_Lat_Long",
                    "SEUS_SPR_IDW_Survey_Area"   : "SEUS_SPR_IDW_Region",
                    "SEUS_SPR_Sample_Locations"  : "SEUS_SPR_IDW_Sample_Locations",
                    "SEUS_SUM_IDW_Boundary_Line" : "SEUS_SUM_IDW_Boundary",
                    #"SEUS_SUM_IDW_Extent_Points" : "SEUS_SUM_IDW_Extent_Points",
                    "SEUS_SUM_IDW_Points"        : "SEUS_SUM_IDW_Extent_Points",
                    "SEUS_SUM_IDW_Fishnet"       : "SEUS_SUM_IDW_Fishnet",
                    "SEUS_SUM_IDW_Lat_Long"      : "SEUS_SUM_IDW_Lat_Long",
                    "SEUS_SUM_IDW_Survey_Area"   : "SEUS_SUM_IDW_Region",
                    "SEUS_SUM_Sample_Locations"  : "SEUS_SUM_IDW_Sample_Locations",
                    "WC_ANN_IDW_Boundary_Line"   : "WC_ANN_IDW_Boundary",
                    #"WC_ANN_IDW_Extent_Points"   : "WC_ANN_IDW_Extent_Points",
                    "WC_ANN_IDW_Points"          : "WC_ANN_IDW_Extent_Points",
                    "WC_ANN_IDW_Fishnet"         : "WC_ANN_IDW_Fishnet",
                    "WC_ANN_IDW_Lat_Long"        : "WC_ANN_IDW_Lat_Long",
                    "WC_ANN_IDW_Survey_Area"     : "WC_ANN_IDW_Region",
                    "WC_ANN_Sample_Locations"    : "WC_ANN_IDW_Sample_Locations",
                    "WC_GFDL_Boundary_Line"      : "WC_GFDL_Boundary",
                    #"WC_GFDL_Extent_Points"      : "WC_GFDL_Extent_Points",
                    "WC_GFDL_Points"             : "WC_GFDL_Extent_Points",
                    "WC_GFDL_Fishnet"            : "WC_GFDL_Fishnet",
                    "WC_GFDL_Lat_Long"           : "WC_GFDL_Lat_Long",
                    "WC_GFDL_Sample_Locations"   : "WC_GFDL_GRID_Points",
                    "WC_GFDL_Survey_Area"        : "WC_GFDL_Region",
                    "WC_GLMME_Boundary_Line"     : "WC_GLMME_Boundary",
                    #"WC_GLMME_Extent_Points"     : "WC_GLMME_Extent_Points",
                    "WC_GLMME_Extent"            : "WC_GLMME_Extent_Points",
                    "WC_GLMME_Fishnet"           : "WC_GLMME_Fishnet",
                    "WC_GLMME_Lat_Long"          : "WC_GLMME_Lat_Long",
                    "WC_GLMME_Sample_Locations"  : "WC_GLMME_GRID_Points",
                    "WC_GLMME_Survey_Area"       : "WC_GLMME_Region",
                    "WC_TRI_IDW_Boundary_Line"   : "WC_TRI_IDW_Boundary",
                    #"WC_TRI_IDW_Extent_Points"   : "WC_TRI_IDW_Extent_Points",
                    "WC_TRI_IDW_Points"          : "WC_TRI_IDW_Extent_Points",
                    "WC_TRI_IDW_Fishnet"         : "WC_TRI_IDW_Fishnet",
                    "WC_TRI_IDW_Lat_Long"        : "WC_TRI_IDW_Lat_Long",
                    "WC_TRI_IDW_Survey_Area"     : "WC_TRI_IDW_Region",
                    "WC_TRI_Sample_Locations"    : "WC_TRI_IDW_Sample_Locations",
                  }

        sort_fields = {
                       #"Boundary"         : "Shape_Length",
                       "Boundary"         : "OBJECTID",
                       "Extent_Points"    : "OBJECTID", #Latitude;Longitude",
                       #"Fishnet"          : "Shape_Length;Shape_Area",
                       "Fishnet"          : "OID",
                       "GRID_Points"      : "Latitude;Longitude",
                       "Lat_Long"         : "OBJECTID", # GEOMETRY_ONLY
                       #"Lat_Long"         : "Latitude;Longitude",
                       "Region"           : "Shape_Length;Shape_Area",
                       "Sample_Locations" : "OBJECTID",
                       "Regions"          : "DatasetCode;Region;Season",
                      }

        differences = []

        # Filter

        # Survey_Area PASSES April 27, 2024
        #fc_dict = {k:fc_dict[k] for k in fc_dict if k.endswith("Survey_Area") and not any(lo in k for lo in ["GFDL", "GLMME"])}
        #
        # Differnce is due to adding a geometry repair step in the new script.
        # Result below are the same to 1 decimal place for area and 2 decimal places for length,
        # basically the same
        #   GOA_IDW_Survey_Area: FeatureClass: ObjectID 1 is different for Field Shape_Area (Base: 325282585482.461853027344, Test: 325282585482.406066894531).
        #   GOA_IDW_Survey_Area: FeatureClass: ObjectID 1 is different for Field Shape_Length (Base: 30445463.785311434418, Test: 30445463.784931387752).

        # In Base FC: AI_IDW_Survey_Area In Test FC: AI_IDW_Region
        #    Base Spatial Reference: NAD_1983_Albers
        #    Test Spatial Reference: NAD_1983_Albers
        #         Spatial References are the same
        #    Base Extent:            -2273985.5 379297.281300001 -715354.5 990521.375
        #    Test Extent:            -2273985.5 379297.281300001 -715354.5 990521.375
        #         Extents are the same
        # Spatial Reference and Extent are the same for all datasets

        # In Base FC: AI_IDW_Points In Test FC: AI_IDW_Extent_Points
        #     Base Spatial Reference: NAD_1983_Albers
        #     Test Spatial Reference: NAD_1983_Albers
        #          Spatial References are the same
        #     Base Extent:            -2273985.5 379297.281300001 -715354.5 990521.375
        #     Test Extent:            -2273986.4622 379297.5913 -715355.6656 990521.5711
        #          Extents are NOT the same

        # Boundary_Line PASSES April 27, 2024
        #fc_dict = {k:fc_dict[k] for k in fc_dict if k.endswith("Boundary_Line") and not any(lo in k for lo in ["GFDL", "GLMME"])}

        # In Base FC: AI_IDW_Boundary_Line In Test FC: AI_IDW_Boundary
        #    Base Spatial Reference: NAD_1983_Albers
        #    Test Spatial Reference: NAD_1983_Albers
        #         Spatial References are the same
        #    Base Extent:            -2273985.5 379297.281300001 -715354.5 990521.375
        #    Test Extent:            -2273985.5 379297.281300001 -715354.5 990521.375
        #         Extents are the same
        # Spatial Reference and Extent are the same for all datasets

        # Regions PASSES April 27, 2024
        #fc_dict = {k:fc_dict[k] for k in fc_dict if k.endswith("Regions") and not any(lo in k for lo in ["GFDL", "GLMME"])}
        # Differences are related to the two different processes and the absence of the geometry repair (needed for GOA) for add to the new script
        #
        # In Base FC: DisMAP_Regions In Test FC: DisMAP_Regions
        #    Base Spatial Reference: WGS_1984_Web_Mercator_Auxiliary_Sphere
        #    Test Spatial Reference: WGS_1984_Web_Mercator_Auxiliary_Sphere
        #         Spatial References are the same
        #    Base Extent:            -20037507.0672 2136865.3231 20037507.0672 9741436.3635
        #    Test Extent:            -20037507.0672 2136865.3231 20037507.0672 9741436.3635
        #         Extents are the same
        # Spatial Reference and Extent are the same for all datasets

        # Extent Points DOES NOT PASS April 27, 2024. Errors related to rounding of Lat/Long using arcpy.management.CalculateGeometryAttributes,
        # which is a tool (a script really) that does not run in parrell processing. Use the function coordinate_field_compare to investigate
        # and resolve.
        #fc_dict = {k:fc_dict[k] for k in fc_dict if k.endswith("IDW_Points") and not any(lo in k for lo in ["GFDL", "GLMME"])}
        # There are differences mostly do to the rounding of the latitude and longitude field to create a DMS string. This step is skipped
        # in the new script and has no impact
        # Spatial Reference and Extent are the same for all datasets

        #Feature Comparison:
        #     Input Base GDB: E:\DisMAP WI 20230426\April 1 2023\DisMAP April 1 2023 Prod.gdb
        #     Input Target GDB: C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP\May 1 2024\May 1 2024.gdb
        #In Base FC: AI_IDW_Points In Test FC: AI_IDW_Extent_Points
        #    Base Spatial Reference: NAD_1983_Albers
        #    Test Spatial Reference: NAD_1983_Albers
        #         Spatial References are the same
        #    Base Extent:            -2273985.5    379297.281300001 -715354.5    990521.375
        #    Test Extent:            -2273986.4622 379297.5913      -715355.6656 990521.5711

        #    C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP\May 1 2024\Scratch\AI_IDW.gdb\AI_IDW_Extent_Points
        #    Spatial Reference: NAD_1983_Albers
        #    Extent:            -2273986.4622 379297.5913 -715355.6656 990521.5711
        #    Geographic Transformations: None
        #    C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP\May 1 2024\May 1 2024.gdb\AI_IDW_Extent_Points
        #    Spatial Reference: NAD_1983_Albers
        #    Extent:            -2273986.4622 379297.5913 -715355.6656 990521.5711
        #    Geographic Transformations: None

        #         Extents are NOT the same (datum shift?)
        # Spatial Reference is matches for all datasets, Extent does not match, except for HI which is using the WGS84 datum, others are NAD 83

        # Fishnet PASSES April 27, 2024
        #fc_dict = {k:fc_dict[k] for k in fc_dict if k.endswith("Fishnet") and not any(lo in k for lo in ["GFDL", "GLMME"])}
        # Feature Compare: No difference between databases on "OID" & GEOMETRY_ONLY
        # Spatial Reference and Extent are the same
        #
        # Feature Comparison:
        #     Input Base GDB: E:\DisMAP WI 20230426\April 1 2023\DisMAP April 1 2023 Prod.gdb
        #     Input Target GDB: C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP\May 1 2024\May 1 2024.gdb
        # In Base FC: AI_IDW_Fishnet In Test FC: AI_IDW_Fishnet
        #    Base Spatial Reference: NAD_1983_Albers
        #    Test Spatial Reference: NAD_1983_Albers
        #         Spatial References are the same
        #    Base Extent:            -2273985.5 379297.281300001 -713985.5 991297.281300001
        #    Test Extent:            -2273985.5 379297.281300001 -713985.5 991297.281300001
        #         Extents are the same
        # Spatial Reference and Extent are the same for all datasets

        # Lat_Long DOES NOT PASS April 27, 2024. Errors related to rounding of Lat/Long using arcpy.management.CalculateGeometryAttributes,
        # which is a tool (a script really) that does not run in parrell processing. Use the function coordinate_field_compare to investigate
        # and resolve.
        #fc_dict = {k:fc_dict[k] for k in fc_dict if k.endswith("Lat_Long") and not any(lo in k for lo in ["GFDL", "GLMME"])}
        # Feature Compare:  No difference between databases on "OBJECTID" & GEOMETRY_ONLY
        # Spatial Reference and Extent are the same

        # Sample_Locations PASSES April 27, 2024
        #fc_dict = {k:fc_dict[k] for k in fc_dict if k.endswith("Sample_Locations") and not any(lo in k for lo in ["GFDL", "GLMME"])}
        #fc_dict = {k:fc_dict[k] for k in fc_dict if k == "AI_Sample_Locations"}

        # Differnce is due to adding a geometry repair step in the new script.
        # Results below are the same to 4 decimal places, basically the same

        # NOTES:
        # 1) Fishnets match
        # 2) Slight difference between GOA Boundary 20230401 v. 20240501

        for in_base_fc in sorted(fc_dict):
            #arcpy.AddMessage(rf"{in_base_fc}")

            if arcpy.Exists(rf"{input_base_gdb}\{in_base_fc}"):
                in_base_fc_path = rf"{input_base_gdb}\{in_base_fc}"
                in_test_fc      = fc_dict[in_base_fc]
                in_test_fc_path = rf"{input_test_gdb}\{in_test_fc}"

                arcpy.AddMessage(fr"In Base FC: {in_base_fc} In Test FC: {in_test_fc}")
                #arcpy.AddMessage(f"\tIn Base FC Fields: {', '.join([f.name for f in arcpy.ListFields(in_base_fc_path)])}")
                #arcpy.AddMessage(f"\tIn Test FC Fields: {', '.join([f.name for f in arcpy.ListFields(in_test_fc_path)])}")

                #sf = [sort_fields[sf] for sf in sort_fields if in_test_fc.endswith(sf)][0]
                #print(f"{in_test_fc:<30}: {sf}")
                #del sf

                CompareSpatialReferenceAndExtent = True
                if CompareSpatialReferenceAndExtent:
                    arcpy.AddMessage(f"\tBase Spatial Reference: {arcpy.Describe(in_base_fc_path).spatialReference.name}")
                    arcpy.AddMessage(f"\tTest Spatial Reference: {arcpy.Describe(in_test_fc_path).spatialReference.name}")
                    arcpy.AddMessage(f"\t\t Spatial References are the same" if arcpy.Describe(in_base_fc_path).spatialReference.name == arcpy.Describe(in_test_fc_path).spatialReference.name else f"\t\t Spatial References are NOT the same")
                    arcpy.AddMessage(f"\tBase Extent:            {str(arcpy.Describe(in_base_fc_path).extent).replace(' NaN', '')}")
                    arcpy.AddMessage(f"\tTest Extent:            {str(arcpy.Describe(in_test_fc_path).extent).replace(' NaN', '')}")
                    arcpy.AddMessage(f"\t\t Extents are the same" if str(arcpy.Describe(in_base_fc_path).extent).replace(' NaN', '') == str(arcpy.Describe(in_test_fc_path).extent).replace(' NaN', '') else f"\t\t Extents are NOT the same")
                del CompareSpatialReferenceAndExtent

                if arcpy.Exists(fr"E:\DisMAP Compare\FeatureCompareOut_{in_base_fc}.txt"): arcpy.management.Delete(fr"E:\DisMAP Compare\FeatureCompareOut_{in_base_fc}.txt")

                if "Sample_Locations" in in_base_fc:
                     #There are differences
                     #    AI_Sample_Locations: Field: Field MapValue aliases are different (Base: MapValue, Test: Map Value).
                     #    AI_Sample_Locations: Field: Field SampleID aliases are different (Base: SampleID, Test: Sample ID).
                     #    EBS_Sample_Locations: Field: Field MapValue aliases are different (Base: MapValue, Test: Map Value).
                     #    EBS_Sample_Locations: Field: Field SampleID aliases are different (Base: SampleID, Test: Sample ID).
                     #    ENBS_Sample_Locations: Field: Field MapValue aliases are different (Base: MapValue, Test: Map Value).
                     #    ENBS_Sample_Locations: Field: Field SampleID aliases are different (Base: SampleID, Test: Sample ID).
                     #    GMEX_Sample_Locations: Field: Field MapValue aliases are different (Base: MapValue, Test: Map Value).
                     #    GMEX_Sample_Locations: Field: Field SampleID aliases are different (Base: SampleID, Test: Sample ID).
                     #    GOA_Sample_Locations: Field: Field MapValue aliases are different (Base: MapValue, Test: Map Value).
                     #    GOA_Sample_Locations: Field: Field SampleID aliases are different (Base: SampleID, Test: Sample ID).
                     #    HI_Sample_Locations: Field: Field MapValue aliases are different (Base: MapValue, Test: Map Value).
                     #    HI_Sample_Locations: Field: Field SampleID aliases are different (Base: SampleID, Test: Sample ID).
                     #    NBS_Sample_Locations: Field: Field MapValue aliases are different (Base: MapValue, Test: Map Value).
                     #    NBS_Sample_Locations: Field: Field SampleID aliases are different (Base: SampleID, Test: Sample ID).
                     #    NEUS_FAL_Sample_Locations: Field: Field MapValue aliases are different (Base: MapValue, Test: Map Value).
                     #    NEUS_FAL_Sample_Locations: Field: Field SampleID aliases are different (Base: SampleID, Test: Sample ID).
                     #    NEUS_SPR_Sample_Locations: Field: Field MapValue aliases are different (Base: MapValue, Test: Map Value).
                     #    NEUS_SPR_Sample_Locations: Field: Field SampleID aliases are different (Base: SampleID, Test: Sample ID).
                     #    SEUS_FAL_Sample_Locations: Field: Field MapValue aliases are different (Base: MapValue, Test: Map Value).
                     #    SEUS_FAL_Sample_Locations: Field: Field SampleID aliases are different (Base: SampleID, Test: Sample ID).
                     #    SEUS_SPR_Sample_Locations: Field: Field MapValue aliases are different (Base: MapValue, Test: Map Value).
                     #    SEUS_SPR_Sample_Locations: Field: Field SampleID aliases are different (Base: SampleID, Test: Sample ID).
                     #    SEUS_SUM_Sample_Locations: Field: Field MapValue aliases are different (Base: MapValue, Test: Map Value).
                     #    SEUS_SUM_Sample_Locations: Field: Field SampleID aliases are different (Base: SampleID, Test: Sample ID).
                     #    WC_ANN_Sample_Locations: Field: Field MapValue aliases are different (Base: MapValue, Test: Map Value).
                     #    WC_ANN_Sample_Locations: Field: Field SampleID aliases are different (Base: SampleID, Test: Sample ID).
                     #    WC_TRI_Sample_Locations: Field: Field MapValue aliases are different (Base: MapValue, Test: Map Value).
                     #    WC_TRI_Sample_Locations: Field: Field SampleID aliases are different (Base: SampleID, Test: Sample ID).

                    #There are differences
                    #    AI_Sample_Locations: WARNING 001620: Difference count exceeds 1500; stopping display. Output compare file was saved to E:\DisMAP Compare\FeatureCompareOut_AI_Sample_Locations.txt.
                    #    EBS_Sample_Locations: WARNING 001620: Difference count exceeds 1500; stopping display. Output compare file was saved to E:\DisMAP Compare\FeatureCompareOut_EBS_Sample_Locations.txt.
                    #    ENBS_Sample_Locations: WARNING 001620: Difference count exceeds 1500; stopping display. Output compare file was saved to E:\DisMAP Compare\FeatureCompareOut_ENBS_Sample_Locations.txt.
                    #    GMEX_Sample_Locations: WARNING 001620: Difference count exceeds 1500; stopping display. Output compare file was saved to E:\DisMAP Compare\FeatureCompareOut_GMEX_Sample_Locations.txt.
                    #    GOA_Sample_Locations: WARNING 001620: Difference count exceeds 1500; stopping display. Output compare file was saved to E:\DisMAP Compare\FeatureCompareOut_GOA_Sample_Locations.txt.
                    #    HI_Sample_Locations: Field: Field CommonName aliases are different (Base: Common Name, Test: CommonName).
                    #    HI_Sample_Locations: Field: Field StratumArea aliases are different (Base: Stratum Area, Test: StratumArea).
                    #    NBS_Sample_Locations: WARNING 001620: Difference count exceeds 1500; stopping display. Output compare file was saved to E:\DisMAP Compare\FeatureCompareOut_NBS_Sample_Locations.txt.
                    #    NEUS_FAL_Sample_Locations: WARNING 001620: Difference count exceeds 1500; stopping display. Output compare file was saved to E:\DisMAP Compare\FeatureCompareOut_NEUS_FAL_Sample_Locations.txt.
                    #    NEUS_SPR_Sample_Locations: WARNING 001620: Difference count exceeds 1500; stopping display. Output compare file was saved to E:\DisMAP Compare\FeatureCompareOut_NEUS_SPR_Sample_Locations.txt.
                    #    SEUS_FAL_Sample_Locations: WARNING 001620: Difference count exceeds 1500; stopping display. Output compare file was saved to E:\DisMAP Compare\FeatureCompareOut_SEUS_FAL_Sample_Locations.txt.
                    #    SEUS_SPR_Sample_Locations: WARNING 001620: Difference count exceeds 1500; stopping display. Output compare file was saved to E:\DisMAP Compare\FeatureCompareOut_SEUS_SPR_Sample_Locations.txt.
                    #    SEUS_SUM_Sample_Locations: WARNING 001620: Difference count exceeds 1500; stopping display. Output compare file was saved to E:\DisMAP Compare\FeatureCompareOut_SEUS_SUM_Sample_Locations.txt.
                    #    WC_ANN_Sample_Locations: WARNING 001620: Difference count exceeds 1500; stopping display. Output compare file was saved to E:\DisMAP Compare\FeatureCompareOut_WC_ANN_Sample_Locations.txt.
                    #    WC_TRI_Sample_Locations: WARNING 001620: Difference count exceeds 1500; stopping display. Output compare file was saved to E:\DisMAP Compare\FeatureCompareOut_WC_TRI_Sample_Locations.txt.

                    arcpy.management.FeatureCompare(
                                                    in_base_features     = in_base_fc_path,
                                                    in_test_features     = in_test_fc_path,
                                                    sort_field           = "Region;SampleID;Year;Species;WTCPUE;MapValue;CommonName;Stratum;StratumArea;Latitude;Longitude;Depth",
                                                    compare_type         = "ATTRIBUTES_ONLY", # ALL GEOMETRY_ONLY ATTRIBUTES_ONLY, SCHEMA_ONLY, SPATIAL_REFERENCE_ONLY
                                                    #ignore_options       = ["IGNORE_M", "IGNORE_Z", "IGNORE_POINTID", "IGNORE_EXTENSION_PROPERTIES", "IGNORE_SUBTYPES", "IGNORE_RELATIONSHIPCLASSES", "IGNORE_REPRESENTATIONCLASSES", "IGNORE_FIELDALIAS"],
                                                    #ignore_options       = ["IGNORE_M", "IGNORE_Z", "IGNORE_EXTENSION_PROPERTIES", "IGNORE_SUBTYPES", "IGNORE_RELATIONSHIPCLASSES", "IGNORE_REPRESENTATIONCLASSES", "IGNORE_FIELDALIAS"],
                                                    ignore_options       = None,
                                                    xy_tolerance         = "0.001 Meters",
                                                    m_tolerance          = 0.001,
                                                    z_tolerance          = 0.001,
                                                    attribute_tolerances = None,
                                                    omit_field           = "Shape;OBJECTID;DatasetCode;Season;SummaryProduct;StdTime;TransformUnit;SpeciesCommonName;CommonNameSpecies;CoreSpecies",
                                                    continue_compare     = "CONTINUE_COMPARE",
                                                    #out_compare_file     = None
                                                    out_compare_file     = fr"E:\DisMAP Compare\FeatureCompareOut_{in_base_fc}.txt"
                                                   )

                    #arcpy.AddMessage("\t"+arcpy.GetMessages().replace("\n", "\n\t"))
                    gms = [gm for gm in arcpy.GetMessages().split("\n") if not any(m in gm for m in ["are the same", "Start Time", "Succeeded at"])]

                    if gms:
                        arcpy.AddMessage(f"\n{'-' * 90}\n")
                        for gm in gms:
                            arcpy.AddMessage(f"{in_base_fc}")
                            arcpy.AddMessage(f"\tWARNING: {gm}")
                            differences.append(f"{in_base_fc}: {gm}")
                            del gm
                        arcpy.AddMessage(f"\n{'-' * 90}\n")
                    else:
                        arcpy.AddMessage(f"\tFeature {in_base_fc} is the same in both {os.path.basename(input_base_gdb)} and {os.path.basename(input_test_gdb)}")
                        arcpy.AddMessage(f"\n")
                    del gms

                else:
                    arcpy.management.FeatureCompare(
                                                    in_base_features     = in_base_fc_path,
                                                    in_test_features     = in_test_fc_path,
                                                    sort_field           = [sort_fields[sf] for sf in sort_fields if in_test_fc.endswith(sf)][0],
                                                    #sort_field           = "OBJECTID",
                                                    compare_type         = "ALL", # ALL GEOMETRY_ONLY ATTRIBUTES_ONLY, SCHEMA_ONLY, SPATIAL_REFERENCE_ONLY
                                                    #ignore_options       = ["IGNORE_M", "IGNORE_Z", "IGNORE_POINTID", "IGNORE_EXTENSION_PROPERTIES", "IGNORE_SUBTYPES", "IGNORE_RELATIONSHIPCLASSES", "IGNORE_REPRESENTATIONCLASSES", "IGNORE_FIELDALIAS"],
                                                    #ignore_options       = ["IGNORE_M", "IGNORE_Z", "IGNORE_EXTENSION_PROPERTIES", "IGNORE_SUBTYPES", "IGNORE_RELATIONSHIPCLASSES", "IGNORE_REPRESENTATIONCLASSES", "IGNORE_FIELDALIAS"],
                                                    ignore_options       = None,
                                                    xy_tolerance         = "0.001 Meters",
                                                    m_tolerance          = 0.001,
                                                    z_tolerance          = 0.001,
                                                    attribute_tolerances = None,
                                                    omit_field           = None,
                                                    continue_compare     = "CONTINUE_COMPARE",
                                                    #out_compare_file     = None
                                                    out_compare_file     = fr"E:\DisMAP Compare\FeatureCompareOut_{in_base_fc}.txt"
                                                   )

                    #arcpy.AddMessage("\t"+arcpy.GetMessages().replace("\n", "\n\t"))
                    gms = [gm for gm in arcpy.GetMessages().split("\n") if not any(m in gm for m in ["are the same", "Start Time", "Succeeded at"])]

                    if gms:
                        arcpy.AddMessage(f"\n{'-' * 90}\n")
                        for gm in gms:
                            arcpy.AddMessage(f"{in_base_fc}")
                            arcpy.AddMessage(f"\tWARNING: {gm}")
                            differences.append(f"{in_base_fc}: {gm}")
                            del gm
                        arcpy.AddMessage(f"\n{'-' * 90}\n")
                    else:
                        arcpy.AddMessage(f"\tFeature {in_base_fc} is the same in both {os.path.basename(input_base_gdb)} and {os.path.basename(input_test_gdb)}")
                        arcpy.AddMessage(f"\n")
                    del gms


        #There are differences
        #    AI_IDW_Survey_Area: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #    AI_IDW_Survey_Area: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #    AI_IDW_Survey_Area: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #    AI_IDW_Survey_Area: Field: Field Season lengths are different (Base: 10, Test: 15).
        #    AI_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).
        #    AI_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).
        #    EBS_IDW_Survey_Area: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #    EBS_IDW_Survey_Area: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #    EBS_IDW_Survey_Area: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #    EBS_IDW_Survey_Area: Field: Field Season lengths are different (Base: 10, Test: 15).
        #    EBS_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).
        #    EBS_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).
        #    ENBS_IDW_Survey_Area: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #    ENBS_IDW_Survey_Area: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #    ENBS_IDW_Survey_Area: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #    ENBS_IDW_Survey_Area: Field: Field Season lengths are different (Base: 10, Test: 15).
        #    ENBS_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).
        #    ENBS_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).
        #    GMEX_IDW_Survey_Area: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #    GMEX_IDW_Survey_Area: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #    GMEX_IDW_Survey_Area: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #    GMEX_IDW_Survey_Area: Field: Field Season lengths are different (Base: 10, Test: 15).
        #    GMEX_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).
        #    GMEX_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).
        #    GOA_IDW_Survey_Area: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #    GOA_IDW_Survey_Area: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #    GOA_IDW_Survey_Area: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #    GOA_IDW_Survey_Area: Field: Field Season lengths are different (Base: 10, Test: 15).
        #    GOA_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).
        #    GOA_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).
        #    HI_IDW_Survey_Area: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #    HI_IDW_Survey_Area: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #    HI_IDW_Survey_Area: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #    HI_IDW_Survey_Area: Field: Field Season lengths are different (Base: 10, Test: 15).
        #    HI_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).
        #    HI_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).
        #    NBS_IDW_Survey_Area: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #    NBS_IDW_Survey_Area: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #    NBS_IDW_Survey_Area: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #    NBS_IDW_Survey_Area: Field: Field Season lengths are different (Base: 10, Test: 15).
        #    NBS_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).
        #    NBS_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).
        #    NEUS_FAL_IDW_Survey_Area: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #    NEUS_FAL_IDW_Survey_Area: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #    NEUS_FAL_IDW_Survey_Area: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #    NEUS_FAL_IDW_Survey_Area: Field: Field Season lengths are different (Base: 10, Test: 15).
        #    NEUS_FAL_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).
        #    NEUS_FAL_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).
        #    NEUS_SPR_IDW_Survey_Area: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #    NEUS_SPR_IDW_Survey_Area: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #    NEUS_SPR_IDW_Survey_Area: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #    NEUS_SPR_IDW_Survey_Area: Field: Field Season lengths are different (Base: 10, Test: 15).
        #    NEUS_SPR_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).
        #    NEUS_SPR_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).
        #    SEUS_FAL_IDW_Survey_Area: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #    SEUS_FAL_IDW_Survey_Area: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #    SEUS_FAL_IDW_Survey_Area: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #    SEUS_FAL_IDW_Survey_Area: Field: Field Season lengths are different (Base: 10, Test: 15).
        #    SEUS_FAL_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).
        #    SEUS_FAL_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).
        #    SEUS_SPR_IDW_Survey_Area: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #    SEUS_SPR_IDW_Survey_Area: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #    SEUS_SPR_IDW_Survey_Area: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #    SEUS_SPR_IDW_Survey_Area: Field: Field Season lengths are different (Base: 10, Test: 15).
        #    SEUS_SPR_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).
        #    SEUS_SPR_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).
        #    SEUS_SUM_IDW_Survey_Area: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #    SEUS_SUM_IDW_Survey_Area: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #    SEUS_SUM_IDW_Survey_Area: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #    SEUS_SUM_IDW_Survey_Area: Field: Field Season lengths are different (Base: 10, Test: 15).
        #    SEUS_SUM_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).
        #    SEUS_SUM_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).
        #    WC_ANN_IDW_Survey_Area: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #    WC_ANN_IDW_Survey_Area: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #    WC_ANN_IDW_Survey_Area: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #    WC_ANN_IDW_Survey_Area: Field: Field Season lengths are different (Base: 10, Test: 15).
        #    WC_ANN_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).
        #    WC_ANN_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).
        #    WC_TRI_IDW_Survey_Area: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #    WC_TRI_IDW_Survey_Area: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #    WC_TRI_IDW_Survey_Area: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #    WC_TRI_IDW_Survey_Area: Field: Field Season lengths are different (Base: 10, Test: 15).
        #    WC_TRI_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).
        #    WC_TRI_IDW_Survey_Area: Table: Tables have different number of fields (Base: 9, Test: 8).

        #    There are differences
        #        AI_IDW_Boundary_Line: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #        AI_IDW_Boundary_Line: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #        AI_IDW_Boundary_Line: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #        AI_IDW_Boundary_Line: Field: Field Season lengths are different (Base: 10, Test: 15).
        #        AI_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).
        #        AI_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).
        #        EBS_IDW_Boundary_Line: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #        EBS_IDW_Boundary_Line: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #        EBS_IDW_Boundary_Line: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #        EBS_IDW_Boundary_Line: Field: Field Season lengths are different (Base: 10, Test: 15).
        #        EBS_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).
        #        EBS_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).
        #        ENBS_IDW_Boundary_Line: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #        ENBS_IDW_Boundary_Line: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #        ENBS_IDW_Boundary_Line: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #        ENBS_IDW_Boundary_Line: Field: Field Season lengths are different (Base: 10, Test: 15).
        #        ENBS_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).
        #        ENBS_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).
        #        GMEX_IDW_Boundary_Line: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #        GMEX_IDW_Boundary_Line: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #        GMEX_IDW_Boundary_Line: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #        GMEX_IDW_Boundary_Line: Field: Field Season lengths are different (Base: 10, Test: 15).
        #        GMEX_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).
        #        GMEX_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).
        #        GOA_IDW_Boundary_Line: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #        GOA_IDW_Boundary_Line: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #        GOA_IDW_Boundary_Line: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #        GOA_IDW_Boundary_Line: Field: Field Season lengths are different (Base: 10, Test: 15).
        #        GOA_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).
        #        GOA_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).
        #        HI_IDW_Boundary_Line: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #        HI_IDW_Boundary_Line: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #        HI_IDW_Boundary_Line: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #        HI_IDW_Boundary_Line: Field: Field Season lengths are different (Base: 10, Test: 15).
        #        HI_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).
        #        HI_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).
        #        NBS_IDW_Boundary_Line: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #        NBS_IDW_Boundary_Line: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #        NBS_IDW_Boundary_Line: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #        NBS_IDW_Boundary_Line: Field: Field Season lengths are different (Base: 10, Test: 15).
        #        NBS_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).
        #        NBS_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).
        #        NEUS_FAL_IDW_Boundary_Line: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #        NEUS_FAL_IDW_Boundary_Line: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #        NEUS_FAL_IDW_Boundary_Line: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #        NEUS_FAL_IDW_Boundary_Line: Field: Field Season lengths are different (Base: 10, Test: 15).
        #        NEUS_FAL_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).
        #        NEUS_FAL_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).
        #        NEUS_SPR_IDW_Boundary_Line: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #        NEUS_SPR_IDW_Boundary_Line: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #        NEUS_SPR_IDW_Boundary_Line: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #        NEUS_SPR_IDW_Boundary_Line: Field: Field Season lengths are different (Base: 10, Test: 15).
        #        NEUS_SPR_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).
        #        NEUS_SPR_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).
        #        SEUS_FAL_IDW_Boundary_Line: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #        SEUS_FAL_IDW_Boundary_Line: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #        SEUS_FAL_IDW_Boundary_Line: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #        SEUS_FAL_IDW_Boundary_Line: Field: Field Season lengths are different (Base: 10, Test: 15).
        #        SEUS_FAL_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).
        #        SEUS_FAL_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).
        #        SEUS_SPR_IDW_Boundary_Line: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #        SEUS_SPR_IDW_Boundary_Line: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #        SEUS_SPR_IDW_Boundary_Line: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #        SEUS_SPR_IDW_Boundary_Line: Field: Field Season lengths are different (Base: 10, Test: 15).
        #        SEUS_SPR_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).
        #        SEUS_SPR_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).
        #        SEUS_SUM_IDW_Boundary_Line: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #        SEUS_SUM_IDW_Boundary_Line: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #        SEUS_SUM_IDW_Boundary_Line: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #        SEUS_SUM_IDW_Boundary_Line: Field: Field Season lengths are different (Base: 10, Test: 15).
        #        SEUS_SUM_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).
        #        SEUS_SUM_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).
        #        WC_ANN_IDW_Boundary_Line: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #        WC_ANN_IDW_Boundary_Line: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #        WC_ANN_IDW_Boundary_Line: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #        WC_ANN_IDW_Boundary_Line: Field: Field Season lengths are different (Base: 10, Test: 15).
        #        WC_ANN_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).
        #        WC_ANN_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).
        #        WC_TRI_IDW_Boundary_Line: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #        WC_TRI_IDW_Boundary_Line: Field: Field DistributionProjectCode aliases are different (Base: DistributionProjectCode, Test: Distribution Project Code).
        #        WC_TRI_IDW_Boundary_Line: Field: Field DistributionProjectCode lengths are different (Base: 512, Test: 10).
        #        WC_TRI_IDW_Boundary_Line: Field: Field Season lengths are different (Base: 10, Test: 15).
        #        WC_TRI_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).
        #        WC_TRI_IDW_Boundary_Line: Table: Tables have different number of fields (Base: 9, Test: 7).

        #    There are differences
        #        AI_IDW_Points: FeatureClass: ObjectID 1 is different for Field Latitude (Base: 48.447411720000, Test: 48.447411717433).
        #        AI_IDW_Points: FeatureClass: ObjectID 1 is different for Field Longitude (Base: 174.472920910000, Test: 174.472920909794).
        #        AI_IDW_Points: FeatureClass: ObjectID 2 is different for Field Latitude (Base: 53.289908220000, Test: 53.289908216252).
        #        AI_IDW_Points: FeatureClass: ObjectID 2 is different for Field Longitude (Base: 170.291264520000, Test: 170.291264519907).
        #        AI_IDW_Points: FeatureClass: ObjectID 3 is different for Field Latitude (Base: 58.315797690000, Test: 58.315797689755).
        #        AI_IDW_Points: FeatureClass: ObjectID 3 is different for Field Longitude (Base: -166.314579460000, Test: -166.314579458846).
        #        AI_IDW_Points: Table: Table fields do not match.
        #        AI_IDW_Points: Table: Table fields do not match.
        #        EBS_IDW_Points: FeatureClass: ObjectID 1 is different for Field Latitude (Base: 53.119786180000, Test: 53.119786181409).
        #        EBS_IDW_Points: FeatureClass: ObjectID 1 is different for Field Longitude (Base: -174.569547680000, Test: -174.569547683465).
        #        EBS_IDW_Points: FeatureClass: ObjectID 2 is different for Field Latitude (Base: 61.429310120000, Test: 61.429310120348).
        #        EBS_IDW_Points: FeatureClass: ObjectID 2 is different for Field Longitude (Base: 179.767833000000, Test: 179.767832999813).
        #        EBS_IDW_Points: FeatureClass: ObjectID 3 is different for Field Latitude (Base: 63.788861680000, Test: 63.788861676735).
        #        EBS_IDW_Points: FeatureClass: ObjectID 3 is different for Field Longitude (Base: -158.709091920000, Test: -158.709091924354).
        #        EBS_IDW_Points: Table: Table fields do not match.
        #        EBS_IDW_Points: Table: Table fields do not match.
        #        ENBS_IDW_Points: FeatureClass: ObjectID 1 is different for Field Latitude (Base: 53.119786180000, Test: 53.119786181409).
        #        ENBS_IDW_Points: FeatureClass: ObjectID 1 is different for Field Longitude (Base: -174.569547680000, Test: -174.569547683465).
        #        ENBS_IDW_Points: FeatureClass: ObjectID 2 is different for Field Latitude (Base: 63.568736080000, Test: 63.568736078488).
        #        ENBS_IDW_Points: FeatureClass: ObjectID 2 is different for Field Longitude (Base: 177.743609680000, Test: 177.743609683365).
        #        ENBS_IDW_Points: FeatureClass: ObjectID 3 is different for Field Latitude (Base: 66.121499490000, Test: 66.121499489759).
        #        ENBS_IDW_Points: FeatureClass: ObjectID 3 is different for Field Longitude (Base: -159.116990540000, Test: -159.116990536559).
        #        ENBS_IDW_Points: Table: Table fields do not match.
        #        ENBS_IDW_Points: Table: Table fields do not match.
        #        GMEX_IDW_Points: FeatureClass: ObjectID 1 is different for Field Latitude (Base: 25.940513060000, Test: 25.940513058943).
        #        GMEX_IDW_Points: FeatureClass: ObjectID 1 is different for Field Longitude (Base: -97.334641700000, Test: -97.334641702685).
        #        GMEX_IDW_Points: FeatureClass: ObjectID 2 is different for Field Latitude (Base: 30.465555770000, Test: 30.465555773865).
        #        GMEX_IDW_Points: FeatureClass: ObjectID 2 is different for Field Longitude (Base: -97.521684350000, Test: -97.521684353670).
        #        GMEX_IDW_Points: FeatureClass: ObjectID 3 is different for Field Latitude (Base: 30.035527440000, Test: 30.035527435012).
        #        GMEX_IDW_Points: FeatureClass: ObjectID 3 is different for Field Longitude (Base: -81.500912270000, Test: -81.500912265815).
        #        GMEX_IDW_Points: Table: Table fields do not match.
        #        GMEX_IDW_Points: Table: Table fields do not match.
        #        GOA_IDW_Points: FeatureClass: ObjectID 1 is different for Field Latitude (Base: 52.295698610000, Test: 52.295698611115).
        #        GOA_IDW_Points: FeatureClass: ObjectID 1 is different for Field Longitude (Base: -169.975970360000, Test: -169.975970359835).
        #        GOA_IDW_Points: FeatureClass: ObjectID 2 is different for Field Latitude (Base: 59.116189110000, Test: 59.116189114512).
        #        GOA_IDW_Points: FeatureClass: ObjectID 2 is different for Field Longitude (Base: -173.349930660000, Test: -173.349930657229).
        #        GOA_IDW_Points: FeatureClass: ObjectID 3 is different for Field Latitude (Base: 58.671843850000, Test: 58.671843847024).
        #        GOA_IDW_Points: FeatureClass: ObjectID 3 is different for Field Longitude (Base: -130.119998740000, Test: -130.119998743625).
        #        GOA_IDW_Points: Table: Table fields do not match.
        #        GOA_IDW_Points: Table: Table fields do not match.
        #        HI_IDW_Points: FeatureClass: ObjectID 1 is different for Field Latitude (Base: 18.871785050000, Test: 18.871785047990).
        #        HI_IDW_Points: FeatureClass: ObjectID 1 is different for Field Longitude (Base: -160.252674980000, Test: -160.252674982266).
        #        HI_IDW_Points: FeatureClass: ObjectID 2 is different for Field Latitude (Base: 22.295613340000, Test: 22.295613340182).
        #        HI_IDW_Points: FeatureClass: ObjectID 2 is different for Field Longitude (Base: -160.280950880000, Test: -160.280950883472).
        #        HI_IDW_Points: FeatureClass: ObjectID 3 is different for Field Latitude (Base: 22.244039100000, Test: 22.244039095720).
        #        HI_IDW_Points: FeatureClass: ObjectID 3 is different for Field Longitude (Base: -154.712959680000, Test: -154.712959682295).
        #        HI_IDW_Points: Table: Table fields do not match.
        #        HI_IDW_Points: Table: Table fields do not match.
        #        NBS_IDW_Points: FeatureClass: ObjectID 1 is different for Field Latitude (Base: 59.506421340000, Test: 59.506421335746).
        #        NBS_IDW_Points: FeatureClass: ObjectID 1 is different for Field Longitude (Base: -174.297500170000, Test: -174.297500166390).
        #        NBS_IDW_Points: FeatureClass: ObjectID 2 is different for Field Latitude (Base: 64.362763610000, Test: 64.362763613730).
        #        NBS_IDW_Points: FeatureClass: ObjectID 2 is different for Field Longitude (Base: -177.880043720000, Test: -177.880043719454).
        #        NBS_IDW_Points: FeatureClass: ObjectID 3 is different for Field Latitude (Base: 66.024290550000, Test: 66.024290545795).
        #        NBS_IDW_Points: FeatureClass: ObjectID 3 is different for Field Longitude (Base: -161.598786300000, Test: -161.598786297450).
        #        NBS_IDW_Points: Table: Table fields do not match.
        #        NBS_IDW_Points: Table: Table fields do not match.
        #        NEUS_FAL_IDW_Points: FeatureClass: ObjectID 1 is different for Field Latitude (Base: 35.139959070000, Test: 35.139959074329).
        #        NEUS_FAL_IDW_Points: FeatureClass: ObjectID 1 is different for Field Longitude (Base: -75.786526500000, Test: -75.786526503082).
        #        NEUS_FAL_IDW_Points: FeatureClass: ObjectID 2 is different for Field Latitude (Base: 44.729535940000, Test: 44.729535936737).
        #        NEUS_FAL_IDW_Points: FeatureClass: ObjectID 2 is different for Field Longitude (Base: -75.904842990000, Test: -75.904842991447).
        #        NEUS_FAL_IDW_Points: FeatureClass: ObjectID 3 is different for Field Latitude (Base: 44.313116780000, Test: 44.313116779067).
        #        NEUS_FAL_IDW_Points: FeatureClass: ObjectID 3 is different for Field Longitude (Base: -65.228894770000, Test: -65.228894774384).
        #        NEUS_FAL_IDW_Points: Table: Table fields do not match.
        #        NEUS_FAL_IDW_Points: Table: Table fields do not match.
        #        NEUS_SPR_IDW_Points: FeatureClass: ObjectID 1 is different for Field Latitude (Base: 35.139959070000, Test: 35.139959074329).
        #        NEUS_SPR_IDW_Points: FeatureClass: ObjectID 1 is different for Field Longitude (Base: -75.786526500000, Test: -75.786526503082).
        #        NEUS_SPR_IDW_Points: FeatureClass: ObjectID 2 is different for Field Latitude (Base: 44.729535940000, Test: 44.729535936737).
        #        NEUS_SPR_IDW_Points: FeatureClass: ObjectID 2 is different for Field Longitude (Base: -75.904842990000, Test: -75.904842991447).
        #        NEUS_SPR_IDW_Points: FeatureClass: ObjectID 3 is different for Field Latitude (Base: 44.313116780000, Test: 44.313116779067).
        #        NEUS_SPR_IDW_Points: FeatureClass: ObjectID 3 is different for Field Longitude (Base: -65.228894770000, Test: -65.228894774384).
        #        NEUS_SPR_IDW_Points: Table: Table fields do not match.
        #        NEUS_SPR_IDW_Points: Table: Table fields do not match.
        #        SEUS_FAL_IDW_Points: FeatureClass: ObjectID 1 is different for Field Latitude (Base: 28.682308850000, Test: 28.682308845648).
        #        SEUS_FAL_IDW_Points: FeatureClass: ObjectID 1 is different for Field Longitude (Base: -81.446783450000, Test: -81.446783447187).
        #        SEUS_FAL_IDW_Points: FeatureClass: ObjectID 2 is different for Field Latitude (Base: 35.355302480000, Test: 35.355302482433).
        #        SEUS_FAL_IDW_Points: FeatureClass: ObjectID 2 is different for Field Longitude (Base: -81.480424050000, Test: -81.480424046563).
        #        SEUS_FAL_IDW_Points: FeatureClass: ObjectID 3 is different for Field Latitude (Base: 35.230604780000, Test: 35.230604779914).
        #        SEUS_FAL_IDW_Points: FeatureClass: ObjectID 3 is different for Field Longitude (Base: -75.490948710000, Test: -75.490948712686).
        #        SEUS_FAL_IDW_Points: Table: Table fields do not match.
        #        SEUS_FAL_IDW_Points: Table: Table fields do not match.
        #        SEUS_SPR_IDW_Points: FeatureClass: ObjectID 1 is different for Field Latitude (Base: 28.682308850000, Test: 28.682308845648).
        #        SEUS_SPR_IDW_Points: FeatureClass: ObjectID 1 is different for Field Longitude (Base: -81.446783450000, Test: -81.446783447187).
        #        SEUS_SPR_IDW_Points: FeatureClass: ObjectID 2 is different for Field Latitude (Base: 35.355302480000, Test: 35.355302482433).
        #        SEUS_SPR_IDW_Points: FeatureClass: ObjectID 2 is different for Field Longitude (Base: -81.480424050000, Test: -81.480424046563).
        #        SEUS_SPR_IDW_Points: FeatureClass: ObjectID 3 is different for Field Latitude (Base: 35.230604780000, Test: 35.230604779914).
        #        SEUS_SPR_IDW_Points: FeatureClass: ObjectID 3 is different for Field Longitude (Base: -75.490948710000, Test: -75.490948712686).
        #        SEUS_SPR_IDW_Points: Table: Table fields do not match.
        #        SEUS_SPR_IDW_Points: Table: Table fields do not match.
        #        SEUS_SUM_IDW_Points: FeatureClass: ObjectID 1 is different for Field Latitude (Base: 28.682308850000, Test: 28.682308845648).
        #        SEUS_SUM_IDW_Points: FeatureClass: ObjectID 1 is different for Field Longitude (Base: -81.446783450000, Test: -81.446783447187).
        #        SEUS_SUM_IDW_Points: FeatureClass: ObjectID 2 is different for Field Latitude (Base: 35.355302480000, Test: 35.355302482433).
        #        SEUS_SUM_IDW_Points: FeatureClass: ObjectID 2 is different for Field Longitude (Base: -81.480424050000, Test: -81.480424046563).
        #        SEUS_SUM_IDW_Points: FeatureClass: ObjectID 3 is different for Field Latitude (Base: 35.230604780000, Test: 35.230604779914).
        #        SEUS_SUM_IDW_Points: FeatureClass: ObjectID 3 is different for Field Longitude (Base: -75.490948710000, Test: -75.490948712686).
        #        SEUS_SUM_IDW_Points: Table: Table fields do not match.
        #        SEUS_SUM_IDW_Points: Table: Table fields do not match.
        #        WC_ANN_IDW_Points: FeatureClass: ObjectID 1 is different for Field Latitude (Base: 32.209544170000, Test: 32.209544171310).
        #        WC_ANN_IDW_Points: FeatureClass: ObjectID 1 is different for Field Longitude (Base: -125.986819550000, Test: -125.986819548762).
        #        WC_ANN_IDW_Points: FeatureClass: ObjectID 2 is different for Field Latitude (Base: 48.510878510000, Test: 48.510878513201).
        #        WC_ANN_IDW_Points: FeatureClass: ObjectID 2 is different for Field Longitude (Base: -125.983213070000, Test: -125.983213068302).
        #        WC_ANN_IDW_Points: FeatureClass: ObjectID 3 is different for Field Latitude (Base: 48.060450120000, Test: 48.060450118925).
        #        WC_ANN_IDW_Points: FeatureClass: ObjectID 3 is different for Field Longitude (Base: -115.000584250000, Test: -115.000584246495).
        #        WC_ANN_IDW_Points: Table: Table fields do not match.
        #        WC_ANN_IDW_Points: Table: Table fields do not match.
        #        WC_TRI_IDW_Points: FeatureClass: ObjectID 1 is different for Field Latitude (Base: 36.154741300000, Test: 36.154741303956).
        #        WC_TRI_IDW_Points: FeatureClass: ObjectID 1 is different for Field Longitude (Base: -125.959903180000, Test: -125.959903183732).
        #        WC_TRI_IDW_Points: FeatureClass: ObjectID 2 is different for Field Latitude (Base: 49.006953810000, Test: 49.006953807178).
        #        WC_TRI_IDW_Points: FeatureClass: ObjectID 2 is different for Field Longitude (Base: -126.641453460000, Test: -126.641453462167).
        #        WC_TRI_IDW_Points: FeatureClass: ObjectID 3 is different for Field Latitude (Base: 49.054150890000, Test: 49.054150889256).
        #        WC_TRI_IDW_Points: FeatureClass: ObjectID 3 is different for Field Longitude (Base: -121.458675840000, Test: -121.458675838392).
        #        WC_TRI_IDW_Points: Table: Table fields do not match.
        #        WC_TRI_IDW_Points: Table: Table fields do not match.

        #    Feature Comparison:
        #         Input Base GDB: E:\DisMAP WI 20230426\April 1 2023\DisMAP April 1 2023 Prod.gdb
        #         Input Target GDB: C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP\May 1 2024\May 1 2024.gdb
        #    In Base FC: AI_IDW_Fishnet In Test FC: AI_IDW_Fishnet
        #        Base Spatial Reference: NAD_1983_Albers
        #        Test Spatial Reference: NAD_1983_Albers
        #             Spatial References are the same
        #        Base Extent:            -2273985.5 379297.281300001 -713985.5 991297.281300001
        #        Test Extent:            -2273985.5 379297.281300001 -713985.5 991297.281300001
        #             Extents are the same
        #        Feature AI_IDW_Fishnet is the same in both DisMAP April 1 2023 Prod.gdb and May 1 2024.gdb
        #
        #
        #    In Base FC: EBS_IDW_Fishnet In Test FC: EBS_IDW_Fishnet
        #        Base Spatial Reference: Albers_Conic_Equal_Area
        #        Test Spatial Reference: Albers_Conic_Equal_Area
        #             Spatial References are the same
        #        Base Extent:            -1359085.4303 557292.9375 -231085.430299999 1545292.9375
        #        Test Extent:            -1359085.4303 557292.9375 -231085.430299999 1545292.9375
        #             Extents are the same
        #        Feature EBS_IDW_Fishnet is the same in both DisMAP April 1 2023 Prod.gdb and May 1 2024.gdb
        #
        #
        #    In Base FC: ENBS_IDW_Fishnet In Test FC: ENBS_IDW_Fishnet
        #        Base Spatial Reference: Albers_Conic_Equal_Area
        #        Test Spatial Reference: Albers_Conic_Equal_Area
        #             Spatial References are the same
        #        Base Extent:            -1359085.4303 557292.9375 -231085.430299999 1805292.9375
        #        Test Extent:            -1359085.4303 557292.9375 -231085.430299999 1805292.9375
        #             Extents are the same
        #        Feature ENBS_IDW_Fishnet is the same in both DisMAP April 1 2023 Prod.gdb and May 1 2024.gdb
        #
        #
        #    In Base FC: GMEX_IDW_Fishnet In Test FC: GMEX_IDW_Fishnet
        #        Base Spatial Reference: NAD_1983_2011_UTM_Zone_15N
        #        Test Spatial Reference: NAD_1983_2011_UTM_Zone_15N
        #             Spatial References are the same
        #        Base Extent:            65724.1837999998 2876290.5758 1613724.1838 3380290.5758
        #        Test Extent:            65724.1837999998 2876290.5758 1613724.1838 3380290.5758
        #             Extents are the same
        #        Feature GMEX_IDW_Fishnet is the same in both DisMAP April 1 2023 Prod.gdb and May 1 2024.gdb
        #
        #
        #    In Base FC: GOA_IDW_Fishnet In Test FC: GOA_IDW_Fishnet
        #        Base Spatial Reference: NAD_1983_2011_UTM_Zone_5N
        #        Test Spatial Reference: NAD_1983_2011_UTM_Zone_5N
        #             Spatial References are the same
        #        Base Extent:            -653226.5171 5930849.5097 1810773.4829 6732849.5097
        #        Test Extent:            -653226.5171 5930849.5097 1810773.4829 6732849.5097
        #             Extents are the same
        #        Feature GOA_IDW_Fishnet is the same in both DisMAP April 1 2023 Prod.gdb and May 1 2024.gdb
        #
        #
        #    In Base FC: HI_IDW_Fishnet In Test FC: HI_IDW_Fishnet
        #        Base Spatial Reference: WGS_1984_UTM_Zone_4N
        #        Test Spatial Reference: WGS_1984_UTM_Zone_4N
        #             Spatial References are the same
        #        Base Extent:            368047.0717 2087107.4678 942047.0717 2466107.4678
        #        Test Extent:            368047.0717 2087107.4678 942047.0717 2466107.4678
        #             Extents are the same
        #        Feature HI_IDW_Fishnet is the same in both DisMAP April 1 2023 Prod.gdb and May 1 2024.gdb
        #
        #
        #    In Base FC: NBS_IDW_Fishnet In Test FC: NBS_IDW_Fishnet
        #        Base Spatial Reference: Albers_Conic_Equal_Area
        #        Test Spatial Reference: Albers_Conic_Equal_Area
        #             Spatial References are the same
        #        Base Extent:            -1127444.8872 1230743.1471 -343444.8872 1806743.1471
        #        Test Extent:            -1127444.8872 1230743.1471 -343444.8872 1806743.1471
        #             Extents are the same
        #        Feature NBS_IDW_Fishnet is the same in both DisMAP April 1 2023 Prod.gdb and May 1 2024.gdb
        #
        #
        #    In Base FC: NEUS_FAL_IDW_Fishnet In Test FC: NEUS_FAL_IDW_Fishnet
        #        Base Spatial Reference: NAD_1983_2011_UTM_Zone_18N
        #        Test Spatial Reference: NAD_1983_2011_UTM_Zone_18N
        #             Spatial References are the same
        #        Base Extent:            428349.9585 3888846.4585 1280349.9585 4954846.4585
        #        Test Extent:            428349.9585 3888846.4585 1280349.9585 4954846.4585
        #             Extents are the same
        #        Feature NEUS_FAL_IDW_Fishnet is the same in both DisMAP April 1 2023 Prod.gdb and May 1 2024.gdb
        #
        #
        #    In Base FC: NEUS_SPR_IDW_Fishnet In Test FC: NEUS_SPR_IDW_Fishnet
        #        Base Spatial Reference: NAD_1983_2011_UTM_Zone_18N
        #        Test Spatial Reference: NAD_1983_2011_UTM_Zone_18N
        #             Spatial References are the same
        #        Base Extent:            428349.9585 3888846.4585 1280349.9585 4954846.4585
        #        Test Extent:            428349.9585 3888846.4585 1280349.9585 4954846.4585
        #             Extents are the same
        #        Feature NEUS_SPR_IDW_Fishnet is the same in both DisMAP April 1 2023 Prod.gdb and May 1 2024.gdb
        #
        #
        #    In Base FC: SEUS_FAL_IDW_Fishnet In Test FC: SEUS_FAL_IDW_Fishnet
        #        Base Spatial Reference: NAD_1983_2011_UTM_Zone_17N
        #        Test Spatial Reference: NAD_1983_2011_UTM_Zone_17N
        #             Spatial References are the same
        #        Base Extent:            456350.9898 3172870.069 1002350.9898 3912870.069
        #        Test Extent:            456350.9898 3172870.069 1002350.9898 3912870.069
        #             Extents are the same
        #        Feature SEUS_FAL_IDW_Fishnet is the same in both DisMAP April 1 2023 Prod.gdb and May 1 2024.gdb
        #
        #
        #    In Base FC: SEUS_SPR_IDW_Fishnet In Test FC: SEUS_SPR_IDW_Fishnet
        #        Base Spatial Reference: NAD_1983_2011_UTM_Zone_17N
        #        Test Spatial Reference: NAD_1983_2011_UTM_Zone_17N
        #             Spatial References are the same
        #        Base Extent:            456350.9898 3172870.069 1002350.9898 3912870.069
        #        Test Extent:            456350.9898 3172870.069 1002350.9898 3912870.069
        #             Extents are the same
        #        Feature SEUS_SPR_IDW_Fishnet is the same in both DisMAP April 1 2023 Prod.gdb and May 1 2024.gdb
        #
        #
        #    In Base FC: SEUS_SUM_IDW_Fishnet In Test FC: SEUS_SUM_IDW_Fishnet
        #        Base Spatial Reference: NAD_1983_2011_UTM_Zone_17N
        #        Test Spatial Reference: NAD_1983_2011_UTM_Zone_17N
        #             Spatial References are the same
        #        Base Extent:            456350.9898 3172870.069 1002350.9898 3912870.069
        #        Test Extent:            456350.9898 3172870.069 1002350.9898 3912870.069
        #             Extents are the same
        #        Feature SEUS_SUM_IDW_Fishnet is the same in both DisMAP April 1 2023 Prod.gdb and May 1 2024.gdb
        #
        #
        #    In Base FC: WC_ANN_IDW_Fishnet In Test FC: WC_ANN_IDW_Fishnet
        #        Base Spatial Reference: NAD_1983_Albers
        #        Test Spatial Reference: NAD_1983_Albers
        #             Spatial References are the same
        #        Base Extent:            1243.30269999988 -869970.3455 819243.302700002 952029.6545
        #        Test Extent:            1243.30269999988 -869970.3455 819243.302700002 952029.6545
        #             Extents are the same
        #        Feature WC_ANN_IDW_Fishnet is the same in both DisMAP April 1 2023 Prod.gdb and May 1 2024.gdb
        #
        #
        #    In Base FC: WC_TRI_IDW_Fishnet In Test FC: WC_TRI_IDW_Fishnet
        #        Base Spatial Reference: NAD_1983_2011_UTM_Zone_10N
        #        Test Spatial Reference: NAD_1983_2011_UTM_Zone_10N
        #             Spatial References are the same
        #        Base Extent:            233718.0011 4005171.1569 613718.0011 5435171.1569
        #        Test Extent:            233718.0011 4005171.1569 613718.0011 5435171.1569
        #             Extents are the same
        #        Feature WC_TRI_IDW_Fishnet is the same in both DisMAP April 1 2023 Prod.gdb and May 1 2024.gdb


                #else:
                #    arcpy.AddMessage(f"\tIn Base FC OID: {arcpy.Describe(in_base_fc_path).OIDFieldName}")
                #    arcpy.AddMessage(f"\tIn Test FC OID: {arcpy.Describe(in_test_fc_path).OIDFieldName}")

                del in_test_fc, in_test_fc_path
                del in_base_fc, in_base_fc_path
            else:
                arcpy.AddMessage(fr"WARNING: {in_base_fc} is missing")
        del sort_fields
        del fc_dict

        if differences:
            arcpy.AddMessage(f"There are differences")
            for difference in sorted(differences):
                arcpy.AddMessage(f"\t{difference}")
                del difference
        else:
            pass
            #arcpy.AddMessage("No difference between Base and Target")
        del differences

        arcpy.AddMessage(f"\n{'-' * 90}\n")

        # Variables set in function

        # Imports

        # Function Parameters
        del input_base_gdb, input_test_gdb

    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteError:
        raise SystemExit(arcpy.GetMessages())
    except arcpy.ExecuteWarning:
        raise SystemExit(arcpy.GetMessages())
    except SystemExit as se:
        raise SystemExit(str(se))
    except:
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        raise SystemExit(pymsg)
    else:
        try:
            import inspect
            leave_out_keys = ["leave_out_keys", "remaining_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys

            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]

        except:
            traceback.print_exc()
    finally:
        try:
            if "results" in locals().keys(): del results
        except UnboundLocalError:
            pass

def coordinate_field_compare(input_base_gdb="", input_test_gdb=""):
    try:

        arcpy.env.overwriteOutput = True
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2)
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        #arcpy.AddMessage(f"{'-' * 90}\n")

        arcpy.AddMessage(f"Feature Comparison:\n\t Input Base GDB: {input_base_gdb}\n\t Input Target GDB: {input_test_gdb}")

        fc_dict = {
                    #"AI_IDW_Extent_Points"       : "AI_IDW_Extent_Points",
                    "AI_IDW_Points"              : "AI_IDW_Extent_Points",
                    "AI_IDW_Lat_Long"            : "AI_IDW_Lat_Long",
                    "AI_Sample_Locations"        : "AI_IDW_Sample_Locations",
                    "DisMAP_Regions"             : "DisMAP_Regions",
                    #"EBS_IDW_Extent_Points"      : "EBS_IDW_Extent_Points",
                    "EBS_IDW_Points"             : "EBS_IDW_Extent_Points",
                    "EBS_IDW_Lat_Long"           : "EBS_IDW_Lat_Long",
                    "EBS_Sample_Locations"       : "EBS_IDW_Sample_Locations",
                    #"ENBS_IDW_Extent_Points"     : "ENBS_IDW_Extent_Points",
                    "ENBS_IDW_Points"            : "ENBS_IDW_Extent_Points",
                    "ENBS_IDW_Lat_Long"          : "ENBS_IDW_Lat_Long",
                    "ENBS_Sample_Locations"      : "ENBS_IDW_Sample_Locations",
                    #"GMEX_IDW_Extent_Points"     : "GMEX_IDW_Extent_Points",
                    "GMEX_IDW_Points"            : "GMEX_IDW_Extent_Points",
                    "GMEX_IDW_Lat_Long"          : "GMEX_IDW_Lat_Long",
                    "GMEX_Sample_Locations"      : "GMEX_IDW_Sample_Locations",
                    #"GOA_IDW_Extent_Points"      : "GOA_IDW_Extent_Points",
                    "GOA_IDW_Points"             : "GOA_IDW_Extent_Points",
                    "GOA_IDW_Lat_Long"           : "GOA_IDW_Lat_Long",
                    "GOA_Sample_Locations"       : "GOA_IDW_Sample_Locations",
                    #"HI_IDW_Extent_Points"       : "HI_IDW_Extent_Points",
                    "HI_IDW_Points"              : "HI_IDW_Extent_Points",
                    "HI_IDW_Lat_Long"            : "HI_IDW_Lat_Long",
                    "HI_Sample_Locations"        : "HI_IDW_Sample_Locations",
                    #"NBS_IDW_Extent_Points"      : "NBS_IDW_Extent_Points",
                    "NBS_IDW_Points"             : "NBS_IDW_Extent_Points",
                    "NBS_IDW_Lat_Long"           : "NBS_IDW_Lat_Long",
                    "NBS_Sample_Locations"       : "NBS_IDW_Sample_Locations",
                    #"NEUS_FAL_IDW_Extent_Points" : "NEUS_FAL_IDW_Extent_Points",
                    "NEUS_FAL_IDW_Points"        : "NEUS_FAL_IDW_Extent_Points",
                    "NEUS_FAL_IDW_Lat_Long"      : "NEUS_FAL_IDW_Lat_Long",
                    "NEUS_FAL_Sample_Locations"  : "NEUS_FAL_IDW_Sample_Locations",
                    #"NEUS_SPR_IDW_Extent_Points" : "NEUS_SPR_IDW_Extent_Points",
                    "NEUS_SPR_IDW_Points"        : "NEUS_SPR_IDW_Extent_Points",
                    "NEUS_SPR_IDW_Lat_Long"      : "NEUS_SPR_IDW_Lat_Long",
                    "NEUS_SPR_Sample_Locations"  : "NEUS_SPR_IDW_Sample_Locations",
                    #"SEUS_FAL_IDW_Extent_Points" : "SEUS_FAL_IDW_Extent_Points",
                    "SEUS_FAL_IDW_Points"        : "SEUS_FAL_IDW_Extent_Points",
                    "SEUS_FAL_IDW_Lat_Long"      : "SEUS_FAL_IDW_Lat_Long",
                    "SEUS_FAL_Sample_Locations"  : "SEUS_FAL_IDW_Sample_Locations",
                    #"SEUS_SPR_IDW_Extent_Points" : "SEUS_SPR_IDW_Extent_Points",
                    "SEUS_SPR_IDW_Points"        : "SEUS_SPR_IDW_Extent_Points",
                    "SEUS_SPR_IDW_Lat_Long"      : "SEUS_SPR_IDW_Lat_Long",
                    "SEUS_SPR_Sample_Locations"  : "SEUS_SPR_IDW_Sample_Locations",
                    #"SEUS_SUM_IDW_Extent_Points" : "SEUS_SUM_IDW_Extent_Points",
                    "SEUS_SUM_IDW_Points"        : "SEUS_SUM_IDW_Extent_Points",
                    "SEUS_SUM_IDW_Lat_Long"      : "SEUS_SUM_IDW_Lat_Long",
                    "SEUS_SUM_Sample_Locations"  : "SEUS_SUM_IDW_Sample_Locations",
                    #"WC_ANN_IDW_Extent_Points"   : "WC_ANN_IDW_Extent_Points",
                    "WC_ANN_IDW_Points"          : "WC_ANN_IDW_Extent_Points",
                    "WC_ANN_IDW_Lat_Long"        : "WC_ANN_IDW_Lat_Long",
                    "WC_ANN_Sample_Locations"    : "WC_ANN_IDW_Sample_Locations",
                    #"WC_GFDL_Extent_Points"      : "WC_GFDL_Extent_Points",
                    "WC_GFDL_Points"             : "WC_GFDL_Extent_Points",
                    "WC_GFDL_Lat_Long"           : "WC_GFDL_Lat_Long",
                    "WC_GFDL_Sample_Locations"   : "WC_GFDL_GRID_Points",
                    #"WC_GLMME_Extent_Points"     : "WC_GLMME_Extent_Points",
                    "WC_GLMME_Points"            : "WC_GLMME_Extent_Points",
                    "WC_GLMME_Lat_Long"          : "WC_GLMME_Lat_Long",
                    "WC_GLMME_Sample_Locations"  : "WC_GLMME_GRID_Points",
                    "WC_TRI_IDW_Points"          : "WC_TRI_IDW_Extent_Points",
                    "WC_TRI_IDW_Lat_Long"        : "WC_TRI_IDW_Lat_Long",
                    "WC_TRI_Sample_Locations"    : "WC_TRI_IDW_Sample_Locations",
                  }

        # Filter

        # Extent Points
        #fc_dict = {k:fc_dict[k] for k in fc_dict if k.endswith("IDW_Points") and not any(lo in k for lo in ["GFDL", "GLMME"])}
        #fc_dict = {k:fc_dict[k] for k in fc_dict if k == "AI_IDW_Points"}

        # Lat_Long
        #fc_dict = {k:fc_dict[k] for k in fc_dict if k.endswith("Lat_Long") and not any(lo in k for lo in ["GFDL", "GLMME"])}

        # Sample_Locations
        fc_dict = {k:fc_dict[k] for k in fc_dict if k.endswith("Sample_Locations") and not any(lo in k for lo in ["GFDL", "GLMME"])}
        #fc_dict = {k:fc_dict[k] for k in fc_dict if k =="NBS_Sample_Locations"}
        #fc_dict = {k:fc_dict[k] for k in fc_dict if k =="SEUS_SPR_Sample_Locations"}

        for in_base_fc in sorted(fc_dict):

            if arcpy.Exists(rf"{input_base_gdb}\{in_base_fc}"):
                in_base_fc_path = rf"{input_base_gdb}\{in_base_fc}"
                in_test_fc      = fc_dict[in_base_fc]
                in_test_fc_path = rf"{input_test_gdb}\{in_test_fc}"

                arcpy.AddMessage(fr"In Base FC: {in_base_fc} In Test FC: {in_test_fc}")

                CompareSpatialReferenceAndExtent = False
                if CompareSpatialReferenceAndExtent:
                    arcpy.AddMessage(f"\tBase Spatial Reference: {arcpy.Describe(in_base_fc_path).spatialReference.name}")
                    arcpy.AddMessage(f"\tTest Spatial Reference: {arcpy.Describe(in_test_fc_path).spatialReference.name}")
                    arcpy.AddMessage(f"\t\t Spatial References are the same" if arcpy.Describe(in_base_fc_path).spatialReference.name == arcpy.Describe(in_test_fc_path).spatialReference.name else f"\t\t Spatial References are NOT the same")
                    arcpy.AddMessage(f"\tBase Extent:            {str(arcpy.Describe(in_base_fc_path).extent).replace(' NaN', '')}")
                    arcpy.AddMessage(f"\tTest Extent:            {str(arcpy.Describe(in_test_fc_path).extent).replace(' NaN', '')}")
                    arcpy.AddMessage(f"\t\t Extents are the same" if str(arcpy.Describe(in_base_fc_path).extent).replace(' NaN', '') == str(arcpy.Describe(in_test_fc_path).extent).replace(' NaN', '') else f"\t\t Extents are NOT the same")
                del CompareSpatialReferenceAndExtent

                dismap_gdb = rf"{os.environ['USERPROFILE']}\Documents\ArcGIS\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\DisMAP.gdb"
                in_base_fc_dismap_gdb = f"{dismap_gdb}\{in_base_fc}_Base"
                in_test_fc_dismap_gdb = f"{dismap_gdb}\{in_test_fc}_Test"

                if "Sample_Locations" in in_base_fc:

                    arcpy.AddMessage(f"\tExport Table to create: {in_base_fc}_Base")

                    arcpy.conversion.ExportTable(
                                                 in_table                = in_base_fc_path,
                                                 out_table               = in_base_fc_dismap_gdb,
                                                 where_clause            = "",
                                                 use_field_alias_as_name = "NOT_USE_ALIAS",
                                                 field_mapping           = fr'in_base_fc_Region "in_base_fc_Region" true true false 40 Text 0 0,First,#,{in_base_fc_path},Region,0,39;in_base_fc_SampleID "in_base_fc_Sample ID" true true false 20 Text 0 0,First,#,{in_base_fc_path},SampleID,0,19;in_base_fc_Year "in_base_fc_Year" true true false 4 Long 0 0,First,#,{in_base_fc_path},Year,-1,-1;in_base_fc_Species "in_base_fc_Species" true true false 50 Text 0 0,First,#,{in_base_fc_path},Species,0,49;in_base_fc_WTCPUE "in_base_fc_WTCPUE" true true false 8 Double 0 0,First,#,{in_base_fc_path},WTCPUE,-1,-1;in_base_fc_CommonName "in_base_fc_Common Name" true true false 40 Text 0 0,First,#,{in_base_fc_path},CommonName,0,39;in_base_fc_Stratum "in_base_fc_Stratum" true true false 20 Text 0 0,First,#,{in_base_fc_path},Stratum,0,19;in_base_fc_StratumArea "in_base_fc_Stratum Area" true true false 8 Double 0 0,First,#,{in_base_fc_path},StratumArea,-1,-1;in_base_fc_Latitude "in_base_fc_Latitude" true true false 8 Double 0 0,First,#,{in_base_fc_path},Latitude,-1,-1;in_base_fc_Longitude "in_base_fc_Longitude" true true false 8 Double 0 0,First,#,{in_base_fc_path},Longitude,-1,-1;in_base_fc_Depth "in_base_fc_Depth" true true false 8 Double 0 0,First,#,{in_base_fc_path},Depth,-1,-1',
                                                 sort_field              = "Region ASCENDING;SampleID ASCENDING;Year ASCENDING;Species ASCENDING;WTCPUE ASCENDING;CommonName ASCENDING;Stratum ASCENDING;StratumArea ASCENDING;Latitude ASCENDING;Longitude ASCENDING;Depth ASCENDING"
                                                )

                    arcpy.AddMessage(f"\tExport Table to create: {in_test_fc}_Test")

                    arcpy.conversion.ExportTable(
                                                 in_table                = in_test_fc_path,
                                                 out_table               = in_test_fc_dismap_gdb,
                                                 where_clause            = "",
                                                 use_field_alias_as_name = "NOT_USE_ALIAS",
                                                 field_mapping           = fr'in_test_fc_Region "in_test_fc_Region" true true false 40 Text 0 0,First,#,{in_test_fc_path},Region,0,39;in_test_fc_SampleID "in_test_fc_Sample ID" true true false 20 Text 0 0,First,#,{in_test_fc_path},SampleID,0,19;in_test_fc_Year "in_test_fc_Year" true true false 4 Long 0 0,First,#,{in_test_fc_path},Year,-1,-1;in_test_fc_Species "in_test_fc_Species" true true false 50 Text 0 0,First,#,{in_test_fc_path},Species,0,49;in_test_fc_WTCPUE "in_test_fc_WTCPUE" true true false 8 Double 0 0,First,#,{in_test_fc_path},WTCPUE,-1,-1;in_test_fc_CommonName "in_test_fc_Common Name" true true false 40 Text 0 0,First,#,{in_test_fc_path},CommonName,0,39;in_test_fc_Stratum "in_test_fc_Stratum" true true false 20 Text 0 0,First,#,{in_test_fc_path},Stratum,0,19;in_test_fc_StratumArea "in_test_fc_Stratum Area" true true false 8 Double 0 0,First,#,{in_test_fc_path},StratumArea,-1,-1;in_test_fc_Latitude "in_test_fc_Latitude" true true false 8 Double 0 0,First,#,{in_test_fc_path},Latitude,-1,-1;in_test_fc_Longitude "in_test_fc_Longitude" true true false 8 Double 0 0,First,#,{in_test_fc_path},Longitude,-1,-1;in_test_fc_Depth "in_test_fc_Depth" true true false 8 Double 0 0,First,#,{in_test_fc_path},Depth,-1,-1',
                                                 sort_field              = "Region ASCENDING;SampleID ASCENDING;Year ASCENDING;Species ASCENDING;WTCPUE ASCENDING;CommonName ASCENDING;Stratum ASCENDING;StratumArea ASCENDING;Latitude ASCENDING;Longitude ASCENDING;Depth ASCENDING"
                                                )

                    if arcpy.Exists(fr"E:\DisMAP Compare\FeatureCompareOut_{in_base_fc}.txt"): arcpy.management.Delete(fr"E:\DisMAP Compare\FeatureCompareOut_{in_base_fc}.txt")

                    arcpy.management.FeatureCompare(
                                                    in_base_features     = in_base_fc_path,
                                                    in_test_features     = in_test_fc_path,
                                                    sort_field           = "Region;SampleID;Year;Species;WTCPUE;CommonName;Stratum;StratumArea;Latitude;Longitude;Depth",
                                                    compare_type         = "ALL", # ALL GEOMETRY_ONLY ATTRIBUTES_ONLY, SCHEMA_ONLY, SPATIAL_REFERENCE_ONLY
                                                    #ignore_options       = ["IGNORE_M", "IGNORE_Z", "IGNORE_POINTID", "IGNORE_EXTENSION_PROPERTIES", "IGNORE_SUBTYPES", "IGNORE_RELATIONSHIPCLASSES", "IGNORE_REPRESENTATIONCLASSES", "IGNORE_FIELDALIAS"],
                                                    #ignore_options       = ["IGNORE_M", "IGNORE_Z", "IGNORE_EXTENSION_PROPERTIES", "IGNORE_SUBTYPES", "IGNORE_RELATIONSHIPCLASSES", "IGNORE_REPRESENTATIONCLASSES", "IGNORE_FIELDALIAS"],
                                                    ignore_options       = None,
                                                    xy_tolerance         = "0.001 Meters",
                                                    m_tolerance          = 0.001,
                                                    z_tolerance          = 0.001,
                                                    attribute_tolerances = None,
                                                    omit_field           = "OBJECTID;DatasetCode;Season;SummaryProduct;StdTime;MapValue;TransformUnit;SpeciesCommonName;CommonNameSpecies;CoreSpecies",
                                                    continue_compare     = "CONTINUE_COMPARE",
                                                    #out_compare_file     = None
                                                    out_compare_file     = fr"E:\DisMAP Compare\FeatureCompareOut_{in_base_fc}.txt"
                                                   )

                    #arcpy.AddMessage("\t"+arcpy.GetMessages().replace("\n", "\n\t"))
                    gms = [gm for gm in arcpy.GetMessages().split("\n") if not any(m in gm for m in ["are the same", "Start Time", "Succeeded at"])]

                    if gms:
                        arcpy.AddMessage(f"\n{'-' * 90}\n")
                        for gm in gms:
                            arcpy.AddMessage(f"{in_base_fc}")
                            arcpy.AddMessage(f"\tWARNING: {gm}")
                            #differences.append(f"{in_base_fc}: {gm}")
                            del gm
                        arcpy.AddMessage(f"\n{'-' * 90}\n")
                    else:
                        arcpy.AddMessage(f"\tFeature {in_base_fc} is the same in both {os.path.basename(input_base_gdb)} and {os.path.basename(input_test_gdb)}")
                        arcpy.AddMessage(f"\n")
                    del gms

                else:

                    arcpy.AddMessage(f"\tExport Table to create: {in_base_fc}_Base")

                    with arcpy.EnvManager(scratchWorkspace = dismap_gdb, workspace = dismap_gdb):
                        arcpy.conversion.ExportTable(
                                                     in_table                = in_base_fc_path,
                                                     out_table               = in_base_fc_dismap_gdb,
                                                     where_clause            = "",
                                                     use_field_alias_as_name = "NOT_USE_ALIAS",
                                                     field_mapping           = fr'in_base_fc_Longitude "in_base_fc Longitude" true true false 8 Double 0 0,First,#,{in_base_fc_path},Longitude,-1,-1;in_base_fc_Latitude "in_base_fc Latitude" true true false 8 Double 0 0,First,#,{in_base_fc_path},Latitude,-1,-1',
                                                     sort_field              = ""
                                                    )

                    #fields = [f.name for f in arcpy.ListFields(in_base_fc_dismap_gdb) if any(x in f.name for x in ["Longitude", "Latitude"])]
                    #for field in fields:
                    #    print(field)
                    #    del field

                    arcpy.AddMessage(f"\tExport Table to create: {in_test_fc}_Test")

                    with arcpy.EnvManager(scratchWorkspace = dismap_gdb, workspace = dismap_gdb):
                        arcpy.conversion.ExportTable(
                                                     in_table                = in_test_fc_path,
                                                     out_table               = in_test_fc_dismap_gdb,
                                                     where_clause            = "",
                                                     use_field_alias_as_name = "NOT_USE_ALIAS",
                                                     field_mapping           = fr'in_test_fc_Longitude "in_test_fc Longitude" true true false 8 Double 0 0,First,#,{in_test_fc_path},Longitude,-1,-1;in_test_fc_Latitude "in_test_fc Latitude" true true false 8 Double 0 0,First,#,{in_test_fc_path},Latitude,-1,-1',
                                                     sort_field              = ""
                                                    )

                #fields = [f.name for f in arcpy.ListFields(in_test_fc_dismap_gdb) if any(x in f.name for x in ["Longitude", "Latitude"])]
                #for field in fields:
                #    print(field)
                #    del field

                arcpy.AddMessage(f"\tJoin {in_test_fc}_Test to {in_base_fc}_Base")
                joined_table = arcpy.management.JoinField(
                                                          in_data           = in_base_fc_dismap_gdb,
                                                          in_field          = arcpy.Describe(in_base_fc_dismap_gdb).OIDFieldName,
                                                          join_table        = in_test_fc_dismap_gdb,
                                                          join_field        = arcpy.Describe(in_test_fc_dismap_gdb).OIDFieldName,
                                                          fields            = None,
                                                          fm_option         = "NOT_USE_FM",
                                                          field_mapping     = None,
                                                          index_join_fields = "NEW_INDEXES"
                                                         )

                arcpy.AddMessage("\tCalculate Longitude_Difference Field")
                with arcpy.EnvManager(scratchWorkspace = dismap_gdb, workspace = dismap_gdb):
                    arcpy.management.CalculateField(
                                                    in_table        = in_base_fc_dismap_gdb,
                                                    field           = "Longitude_Defference",
                                                    expression      = "!in_base_fc_Longitude! - !in_test_fc_Longitude!",
                                                    expression_type = "PYTHON3",
                                                    code_block      = "",
                                                    field_type      = "FLOAT",
                                                    enforce_domains = "NO_ENFORCE_DOMAINS"
                                                   )

                arcpy.AddMessage("\tCalculate Latitude_Difference Field")
                with arcpy.EnvManager(scratchWorkspace = dismap_gdb, workspace = dismap_gdb):
                    arcpy.management.CalculateField(
                                                    in_table        = in_base_fc_dismap_gdb,
                                                    field           = "Latitude_Difference",
                                                    expression      = "!in_base_fc_Latitude! - !in_test_fc_Latitude!",
                                                    expression_type = "PYTHON3",
                                                    code_block      = "",
                                                    field_type      = "FLOAT",
                                                    enforce_domains = "NO_ENFORCE_DOMAINS"
                                                   )
                in_base_fc_dismap_gdb_statistics = rf"{in_base_fc_dismap_gdb}_Statistics"
                with arcpy.EnvManager(scratchWorkspace = dismap_gdb, workspace = dismap_gdb):
                    arcpy.analysis.Statistics(
                                              in_table                = in_base_fc_dismap_gdb,
                                              out_table               = in_base_fc_dismap_gdb_statistics,
                                              statistics_fields       = "Longitude_Defference MIN;Longitude_Defference MAX;Longitude_Defference RANGE;Longitude_Defference MEAN;Longitude_Defference MEDIAN;Longitude_Defference STD;Longitude_Defference VARIANCE;Latitude_Difference MIN;Latitude_Difference MAX;Latitude_Difference RANGE;Latitude_Difference MEAN;Latitude_Difference MEDIAN;Latitude_Difference STD;Latitude_Difference VARIANCE",
                                              case_field              = None,
                                              concatenation_separator = ""
                                            )

                #fields = [f.name for f in arcpy.ListFields(in_base_fc_dismap_gdb_statistics) if any(x in f.name for x in ["Longitude", "Latitude"])]
                fields = [f.name for f in arcpy.ListFields(in_base_fc_dismap_gdb_statistics) if any(x in f.name for x in ["STD", "VARIANCE"])]
                #for field in fields:
                #    print(field)
                #    del field

                arcpy.AddMessage(f"\tSearch Cursor on {in_base_fc}_Statitics")

                with arcpy.da.SearchCursor(in_base_fc_dismap_gdb_statistics, fields) as cursor:
                    for row in cursor:
                        #print(row)
                        arcpy.AddMessage(f"\t\tLongitude_Defference")
                        arcpy.AddMessage(f"\t\t\tSTD_Longitude_Defference:      {row[0]}")
                        arcpy.AddMessage(f"\t\t\tVARIANCE_Longitude_Defference: {row[1]}")

                        arcpy.AddMessage(f"\t\tLatitude_Difference")
                        arcpy.AddMessage(f"\t\t\tSTD_Latitude_Difference:       {row[2]}")
                        arcpy.AddMessage(f"\t\t\tVARIANCE_Latitude_Difference:  {row[3]}")
                        del row
                    del cursor

                del fields

                arcpy.AddMessage(f"\n\tDeleting: {in_base_fc}_Statistics")
                #arcpy.management.Delete(in_base_fc_dismap_gdb_statistics)
                del in_base_fc_dismap_gdb_statistics
                arcpy.AddMessage(f"\tDeleting: {in_base_fc}_Base")
                #arcpy.management.Delete(in_base_fc_dismap_gdb)
                del in_base_fc_dismap_gdb
                arcpy.AddMessage(f"\tDeleting: {in_test_fc}_Test\n")
                #arcpy.management.Delete(in_test_fc_dismap_gdb)
                del in_test_fc_dismap_gdb

                del joined_table

                del dismap_gdb

                del in_test_fc, in_test_fc_path
                del in_base_fc, in_base_fc_path
            else:
                arcpy.AddMessage(fr"WARNING: {in_base_fc} is missing")

        del fc_dict

        arcpy.AddMessage(f"\n{'-' * 90}\n")

        # Variables set in function

        # Imports

        # Function Parameters
        del input_base_gdb, input_test_gdb

    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteError:
        raise SystemExit(arcpy.GetMessages())
    except arcpy.ExecuteWarning:
        raise SystemExit(arcpy.GetMessages())
    except SystemExit as se:
        raise SystemExit(str(se))
    except:
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        raise SystemExit(pymsg)
    else:
        try:
            import inspect
            leave_out_keys = ["leave_out_keys", "remaining_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys

            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]

        except:
            traceback.print_exc()
    finally:
        try:
            if "results" in locals().keys(): del results
        except UnboundLocalError:
            pass

def raster_compare(input_base_gdb="", input_test_gdb=""):
    try:
        pixel_types = {"U1" : "1 bit", "U2"  : "2 bits", "U4"  : "4 bits",
                       "U8"  : "Unsigned 8-bit integers", "S8"  : "8-bit integers",
                       "U16" : "Unsigned 16-bit integers", "S16" : "16-bit integers",
                       "U32" : "Unsigned 32-bit integers", "S32" : "32-bit integers",
                       "F32" : "Single-precision floating point",
                       "F64" : "Double-precision floating point",}

        arcpy.env.overwriteOutput = True
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2)
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        #arcpy.AddMessage(f"{'-' * 90}\n")

        arcpy.AddMessage(f"Raster Comparison:\n\t Input Base GDB: {input_base_gdb}\n\t Input Target GDB: {input_test_gdb}")

        arcpy.env.workspace = input_base_gdb


        # Raster_Mask: PASSED RasterStatistics 4/27/2024, PASSED RasterCompare  4/27/2024

        # Bathymetry

        # Latitude:  DOES NOT PASS RasterCompare and RasterStatistics April 27, 2024. Errors related to rounding of Lat/Long using arcpy.management.CalculateGeometryAttributes,
        # which is a tool (a script really) that does not run in parrell processing. Use the function coordinate_field_compare to investigate
        # and resolve.

        # Longitude:  DOES NOT PASS RasterCompare and RasterStatistics April 27, 2024. Errors related to rounding of Lat/Long using arcpy.management.CalculateGeometryAttributes,
        # which is a tool (a script really) that does not run in parrell processing. Use the function coordinate_field_compare to investigate
        # and resolve.

        wild_cards = ["Raster_Mask", "Bathymetry", "Latitude", "Longitude"]
        #wild_cards = ["Raster_Mask"]
        #wild_cards = ["Latitude", "Longitude"]
        #wild_cards = ["Longitude"]
        #wild_cards = ["Bathymetry"]

         # ['Raster: AI_IDW_Bathymetry,   Maximum: -0.15122437477111994, Minimum: 29.16595458984301, Mean: 0.3350581222800031, STD: -0.38234183610398986']
         # ['Raster: EBS_IDW_Bathymetry,  Maximum: 0.10109233856200994,  Minimum: 0.0,               Mean: -0.07721070856180745, STD: 0.11893745118109678']
         # ['Raster: ENBS_IDW_Bathymetry, Maximum: 0.0,                  Minimum: 0.0,               Mean: -0.051033968472808056, STD: 0.10420216558070194']
         # ['Raster: GMEX_IDW_Bathymetry, Maximum: 0.0,                  Minimum: 0.0,               Mean: 1.5166089096418034, STD: -2.787590978137601']
         # ['Raster: NBS_IDW_Bathymetry,  Maximum: -0.32422864437103005, Minimum: 0.0,               Mean: 0.026704302780700573, STD: 0.0295792511066999']


         # ['Raster: GOA_IDW_Bathymetry, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
         # ['Raster: HI_IDW_Bathymetry, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
         # ['Raster: NEUS_FAL_IDW_Bathymetry, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
         # ['Raster: NEUS_SPR_IDW_Bathymetry, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
         # ['Raster: SEUS_FAL_IDW_Bathymetry, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
         # ['Raster: SEUS_SPR_IDW_Bathymetry, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
         # ['Raster: SEUS_SUM_IDW_Bathymetry, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
         # ['Raster: WC_ANN_IDW_Bathymetry, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
         # ['Raster: WC_TRI_IDW_Bathymetry, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']


        differences = []

        for wild_card in wild_cards:
            arcpy.AddMessage(f"Wild Card: {wild_card}")

            rasters = [r for r in arcpy.ListRasters(f"*{wild_card}") if not any(lo in r for lo in ["GFDL", "GLMME"])]
            #rasters = [r for r in arcpy.ListRasters(f"*{wild_card}") if "AI_IDW" in r]
            #rasters = [r for r in arcpy.ListRasters(f"*")]

            del wild_card

            for raster in sorted(rasters):

                if arcpy.Exists(raster.replace(input_base_gdb, input_test_gdb)):

                    RasterStatistics = False
                    if RasterStatistics:

                        input_base_raster = arcpy.Raster(rf"{input_base_gdb}\{raster}")
                        input_test_raster = arcpy.Raster(rf"{input_test_gdb}\{raster}")

                        #arcpy.AddMessage(f"{raster.name}")
                        #arcpy.AddMessage(f"\tSpatial Reference: {raster.spatialReference.name}")
                        #arcpy.AddMessage(f"\tXYResolution:      {raster.spatialReference.XYResolution} {raster.spatialReference.linearUnitName}s")
                        #arcpy.AddMessage(f"\tXYTolerance:       {raster.spatialReference.XYTolerance}  {raster.spatialReference.linearUnitName}s")
                        #arcpy.AddMessage(f"\tExtent:            {raster.extent.XMin} {raster.extent.YMin} {raster.extent.XMax} {raster.extent.YMax} (XMin, YMin, XMax, YMax)")
                        #arcpy.AddMessage(f"\tCell Size:         {raster.meanCellHeight}, {raster.meanCellWidth} (H, W)")
                        #arcpy.AddMessage(f"\tRows, Columns:     {raster.height} {raster.width} (H, W)")
                        #arcpy.AddMessage(f"\tStatistics:        {raster.minimum} {raster.maximum} {raster.mean} {raster.standardDeviation} (Min, Max, Mean, STD)")
                        #arcpy.AddMessage(f"\tPixel Type:        {pixel_types[raster.pixelType]}")

                        arcpy.AddMessage(f"\tRaster: {raster}")

                        #base_maximum = float(arcpy.management.GetRasterProperties(rf"{input_base_gdb}\{raster}", "MAXIMUM").getOutput(0))
                        #test_maximum = float(arcpy.management.GetRasterProperties(rf"{input_test_gdb}\{raster}", "MAXIMUM").getOutput(0))
                        base_maximum = input_base_raster.maximum
                        test_maximum = input_test_raster.maximum
                        maximum_difference = base_maximum - test_maximum

                        arcpy.AddMessage(f"\t\tBase Maximum: {base_maximum}")
                        arcpy.AddMessage(f"\t\tTest Maximum: {test_maximum}")
                        arcpy.AddMessage(f"\t\t\tDifference: {maximum_difference}")

                        del base_maximum, test_maximum

                        #base_minimum = float(arcpy.management.GetRasterProperties(rf"{input_base_gdb}\{raster}", "MINIMUM").getOutput(0))
                        #test_minimum = float(arcpy.management.GetRasterProperties(rf"{input_test_gdb}\{raster}", "MINIMUM").getOutput(0))
                        base_minimum = input_base_raster.minimum
                        test_minimum = input_test_raster.minimum
                        minimum_difference = base_minimum - test_minimum

                        arcpy.AddMessage(f"\t\tBase Minimum: {base_minimum}")
                        arcpy.AddMessage(f"\t\tTest Minimum: {test_minimum}")
                        arcpy.AddMessage(f"\t\t\tDifference: {minimum_difference}")

                        del base_minimum, test_minimum

                        #base_mean = float(arcpy.management.GetRasterProperties(rf"{input_base_gdb}\{raster}", "MEAN").getOutput(0))
                        #test_mean = float(arcpy.management.GetRasterProperties(rf"{input_test_gdb}\{raster}", "MEAN").getOutput(0))
                        base_mean = input_base_raster.mean
                        test_mean = input_test_raster.mean
                        mean_difference = base_mean - test_mean

                        arcpy.AddMessage(f"\t\tBase Mean: {base_mean}")
                        arcpy.AddMessage(f"\t\tTest Mean: {test_mean}")
                        arcpy.AddMessage(f"\t\t\tDifference: {mean_difference}")

                        del base_mean, test_mean

                        #base_std = float(arcpy.management.GetRasterProperties(rf"{input_base_gdb}\{raster}", "STD").getOutput(0))
                        #test_std = float(arcpy.management.GetRasterProperties(rf"{input_test_gdb}\{raster}", "STD").getOutput(0))
                        base_std = input_base_raster.standardDeviation
                        test_std = input_test_raster.standardDeviation
                        std_differnce = base_std - test_std

                        arcpy.AddMessage(f"\t\tBase STD: {base_std}")
                        arcpy.AddMessage(f"\t\tTest STD: {test_std}")
                        arcpy.AddMessage(f"\t\t\tDifference: {std_differnce}")

                        del base_std, test_std

                        arcpy.AddMessage(f"\t\tBase Spatial Reference: {input_base_raster.spatialReference.name}")
                        arcpy.AddMessage(f"\t\tTest Spatial Reference: {input_test_raster.spatialReference.name}")

                        arcpy.AddMessage(f"\t\tBase XYResolution:      {input_base_raster.spatialReference.XYResolution} {input_base_raster.spatialReference.linearUnitName}s")
                        arcpy.AddMessage(f"\t\tTest XYResolution:      {input_test_raster.spatialReference.XYResolution} {input_test_raster.spatialReference.linearUnitName}s")

                        arcpy.AddMessage(f"\t\tBase XYTolerance:       {input_base_raster.spatialReference.XYTolerance}  {input_base_raster.spatialReference.linearUnitName}s")
                        arcpy.AddMessage(f"\t\tTest XYTolerance:       {input_test_raster.spatialReference.XYTolerance}  {input_test_raster.spatialReference.linearUnitName}s")

                        arcpy.AddMessage(f"\t\tBase Extent:            {input_base_raster.extent.XMin} {input_base_raster.extent.YMin} {input_base_raster.extent.XMax} {input_base_raster.extent.YMax} (XMin, YMin, XMax, YMax)")
                        arcpy.AddMessage(f"\t\tTest Extent:            {input_test_raster.extent.XMin} {input_test_raster.extent.YMin} {input_test_raster.extent.XMax} {input_test_raster.extent.YMax} (XMin, YMin, XMax, YMax)")

                        arcpy.AddMessage(f"\t\tBase Cell Size:         {input_base_raster.meanCellHeight}, {input_base_raster.meanCellWidth} (H, W)")
                        arcpy.AddMessage(f"\t\tTest Cell Size:         {input_test_raster.meanCellHeight}, {input_test_raster.meanCellWidth} (H, W)")

                        arcpy.AddMessage(f"\t\tBase Rows, Columns:     {input_base_raster.height} {input_base_raster.width} (H, W)")
                        arcpy.AddMessage(f"\t\tTest Rows, Columns:     {input_test_raster.height} {input_test_raster.width} (H, W)")

                        arcpy.AddMessage(f"\t\tBase Pixel Type:        {pixel_types[input_base_raster.pixelType]}")
                        arcpy.AddMessage(f"\t\tTest Pixel Type:        {pixel_types[input_test_raster.pixelType]}")


                        out_rc_multi_raster = input_base_raster - input_test_raster
                        out_rc_multi_raster.save(rf"{os.environ['USERPROFILE']}\Documents\ArcGIS\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\DisMAP.gdb\{raster}_Minus")

                        del out_rc_multi_raster

                        differences.append([f"Raster: {raster}, Maximum: {maximum_difference}, Minimum: {minimum_difference}, Mean: {mean_difference}, STD: {std_differnce}"])

                        del maximum_difference, minimum_difference, mean_difference, std_differnce
                        del input_base_raster, input_test_raster
                    del RasterStatistics

     #    There are differences
     #    ['Raster: AI_IDW_Bathymetry, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: -2.2737367544323206e-13']
     #    ['Raster: AI_IDW_Latitude, Maximum: -3.767226530726475e-10, Minimum: -5.91818150041945e-10, Mean: 2.1813661987835076e-11, STD: 2.3770430068736914e-11']
     #    ['Raster: AI_IDW_Longitude, Maximum: 2.2973836166784167e-09, Minimum: -4.310436452215072e-09, Mean: 7.652545264136279e-12, STD: 3.836930773104541e-12']
     #    ['Raster: AI_IDW_Raster_Mask, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
     #    ['Raster: EBS_IDW_Bathymetry, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: -2.1316282072803006e-14']
     #    ['Raster: EBS_IDW_Latitude, Maximum: 1.7891039760797867e-09, Minimum: 1.8641088672666228e-10, Mean: -1.0835776720341528e-11, STD: 4.141353926456759e-11']
     #    ['Raster: EBS_IDW_Longitude, Maximum: 2.633242957017501e-09, Minimum: -3.4507650070736418e-09, Mean: -1.4210854715202004e-13, STD: -6.557687726171935e-11']
     #    ['Raster: EBS_IDW_Raster_Mask, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
     #    ['Raster: ENBS_IDW_Bathymetry, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: -5.897504706808832e-13']
     #    ['Raster: ENBS_IDW_Latitude, Maximum: -4.162785671724123e-10, Minimum: 1.8641088672666228e-10, Mean: -6.963318810448982e-12, STD: -1.3929746245366914e-11']
     #    ['Raster: ENBS_IDW_Longitude, Maximum: 2.633242957017501e-09, Minimum: -3.4507650070736418e-09, Mean: -3.382183422218077e-12, STD: -5.749534182086791e-11']
     #    ['Raster: ENBS_IDW_Raster_Mask, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
     #    ['Raster: GMEX_IDW_Bathymetry, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
     #    ['Raster: GMEX_IDW_Latitude, Maximum: 3.854147223592008e-09, Minimum: 1.4722942864864308e-09, Mean: 2.9096725029376103e-12, STD: -1.539435245945242e-11']
     #    ['Raster: GMEX_IDW_Longitude, Maximum: -2.9517508437493234e-09, Minimum: 4.395602104523277e-09, Mean: 1.1013412404281553e-11, STD: 2.893685291383008e-12']
     #    ['Raster: GMEX_IDW_Raster_Mask, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
     #    ['Raster: GOA_IDW_Bathymetry, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 1.7053025658242404e-13']
     #    ['Raster: GOA_IDW_Latitude, Maximum: -2.593687042917736e-09, Minimum: -4.444899559530313e-09, Mean: 5.4569682106375694e-12, STD: 3.9044323330017505e-11']
     #    ['Raster: GOA_IDW_Longitude, Maximum: -1.927304538185126e-09, Minimum: 8.524523309461074e-10, Mean: 1.0800249583553523e-12, STD: -3.26316751397826e-12']
     #    ['Raster: GOA_IDW_Raster_Mask, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
     #    ['Raster: HI_IDW_Bathymetry, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
     #    ['Raster: HI_IDW_Latitude, Maximum: 2.246022035023998e-09, Minimum: -2.773088425556125e-09, Mean: -2.4840574042173102e-11, STD: -1.2713607944192518e-11']
     #    ['Raster: HI_IDW_Longitude, Maximum: -3.657390834632679e-09, Minimum: 9.184475402435055e-10, Mean: 6.565414878423326e-12, STD: -8.490008696071527e-11']
     #    ['Raster: HI_IDW_Raster_Mask, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
     #    ['Raster: NBS_IDW_Bathymetry, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 3.552713678800501e-14']
     #    ['Raster: NBS_IDW_Latitude, Maximum: -3.2783304959593806e-09, Minimum: 3.1766873576088983e-09, Mean: -1.1752376849472057e-11, STD: 1.925770654054304e-11']
     #    ['Raster: NBS_IDW_Longitude, Maximum: 3.058175934711471e-10, Minimum: -1.5539569631073391e-09, Mean: -8.526512829121202e-14, STD: -6.586420298049234e-11']
     #    ['Raster: NBS_IDW_Raster_Mask, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
     #    ['Raster: NEUS_FAL_IDW_Bathymetry, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
     #    ['Raster: NEUS_FAL_IDW_Latitude, Maximum: 2.630571316331043e-10, Minimum: -2.669480636541266e-09, Mean: -1.4104273304837989e-11, STD: 1.5087930904655877e-12']
     #    ['Raster: NEUS_FAL_IDW_Longitude, Maximum: -3.2103741887112847e-09, Minimum: 3.2974583064060425e-09, Mean: 1.5617729332007002e-11, STD: 2.62465604805584e-11']
     #    ['Raster: NEUS_FAL_IDW_Raster_Mask, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
     #    ['Raster: NEUS_SPR_IDW_Bathymetry, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
     #    ['Raster: NEUS_SPR_IDW_Latitude, Maximum: 2.630571316331043e-10, Minimum: -2.669480636541266e-09, Mean: -1.4225065569917206e-11, STD: 4.0671910284117985e-12']
     #    ['Raster: NEUS_SPR_IDW_Longitude, Maximum: -3.2103741887112847e-09, Minimum: 3.2974583064060425e-09, Mean: 1.553246420371579e-11, STD: 2.475752935993114e-11']
     #    ['Raster: NEUS_SPR_IDW_Raster_Mask, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
     #    ['Raster: SEUS_FAL_IDW_Bathymetry, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
     #    ['Raster: SEUS_FAL_IDW_Latitude, Maximum: 2.681517230485042e-10, Minimum: -2.6737438929558266e-09, Mean: -4.389022478790139e-11, STD: 1.3425704992187093e-11']
     #    ['Raster: SEUS_FAL_IDW_Longitude, Maximum: -3.9221532688316074e-09, Minimum: -2.3081838662619703e-09, Mean: 8.195399914256996e-11, STD: 5.788702850395566e-11']
     #    ['Raster: SEUS_FAL_IDW_Raster_Mask, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
     #    ['Raster: SEUS_SPR_IDW_Bathymetry, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
     #    ['Raster: SEUS_SPR_IDW_Latitude, Maximum: 2.681517230485042e-10, Minimum: -2.6737438929558266e-09, Mean: -4.388311936054379e-11, STD: 1.3747003535513613e-11']
     #    ['Raster: SEUS_SPR_IDW_Longitude, Maximum: -3.9221532688316074e-09, Minimum: -2.3081838662619703e-09, Mean: 8.195399914256996e-11, STD: 5.788702850395566e-11']
     #    ['Raster: SEUS_SPR_IDW_Raster_Mask, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
     #    ['Raster: SEUS_SUM_IDW_Bathymetry, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
     #    ['Raster: SEUS_SUM_IDW_Latitude, Maximum: 2.681517230485042e-10, Minimum: -2.6737438929558266e-09, Mean: -4.389022478790139e-11, STD: 1.3425704992187093e-11']
     #    ['Raster: SEUS_SUM_IDW_Longitude, Maximum: -3.9221532688316074e-09, Minimum: -2.3081838662619703e-09, Mean: 8.198242085200036e-11, STD: 5.840394834422113e-11']
     #    ['Raster: SEUS_SUM_IDW_Raster_Mask, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
     #    ['Raster: WC_ANN_IDW_Bathymetry, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
     #    ['Raster: WC_ANN_IDW_Latitude, Maximum: 1.3621033190247545e-09, Minimum: -3.92883947597511e-09, Mean: 1.546140993013978e-11, STD: -2.2604140781368187e-12']
     #    ['Raster: WC_ANN_IDW_Longitude, Maximum: 4.470990688787424e-09, Minimum: 1.1949339295824757e-09, Mean: 1.4068746168049984e-12, STD: 5.903322275457867e-11']
     #    ['Raster: WC_ANN_IDW_Raster_Mask, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']
     #    ['Raster: WC_TRI_IDW_Bathymetry, Maximum: 0.0, Minimum: 0.0, Mean: -0.002074419810725203, STD: 0.010330097186255216']
     #    ['Raster: WC_TRI_IDW_Latitude, Maximum: 1.0561933549979585e-09, Minimum: 1.501817337157263e-09, Mean: 1.694644424787839e-11, STD: -3.1747937612180976e-12']
     #    ['Raster: WC_TRI_IDW_Longitude, Maximum: 1.0203962119703647e-09, Minimum: 3.528882075443107e-09, Mean: 2.354738626308972e-11, STD: -5.264189084641657e-11']
     #    ['Raster: WC_TRI_IDW_Raster_Mask, Maximum: 0.0, Minimum: 0.0, Mean: 0.0, STD: 0.0']


    #    There are differences
    #    AI_IDW_Latitude: RasterDataset: Pixel data (16112 out of 238374) are different.
    #    AI_IDW_Latitude: RasterStats: Maximums are different (Base: 54.49844146, Test: 54.49844146037672).
    #    AI_IDW_Latitude: RasterStats: Means are different (Base: 52.34033150194312, Test: 52.34033150192131).
    #    AI_IDW_Latitude: RasterStats: Minimums are different (Base: 51.15699479, Test: 51.15699479059182).
    #    AI_IDW_Latitude: RasterStats: Standard Deviations are different (Base: 0.6224429616414322, Test: 0.6224429616176618)
    #    AI_IDW_Longitude: RasterDataset: Pixel data (16113 out of 238374) are different.
    #    AI_IDW_Longitude: RasterStats: Maximums are different (Base: 179.99890773, Test: 179.9989077277026).
    #    AI_IDW_Longitude: RasterStats: Means are different (Base: -37.07299309838327, Test: -37.07299309839092).
    #    AI_IDW_Longitude: RasterStats: Minimums are different (Base: -179.99985055, Test: -179.9998505456896).
    #    AI_IDW_Longitude: RasterStats: Standard Deviations are different (Base: 170.2349930562441, Test: 170.2349930562403)
    #    EBS_IDW_Latitude: RasterDataset: Pixel data (123360 out of 278052) are different.
    #    EBS_IDW_Latitude: RasterStats: Maximums are different (Base: 62.17245934, Test: 62.1724593382109).
    #    EBS_IDW_Latitude: RasterStats: Means are different (Base: 58.2851079718096, Test: 58.28510797182044).
    #    EBS_IDW_Latitude: RasterStats: Minimums are different (Base: 54.50074794, Test: 54.50074793981359).
    #    EBS_IDW_Latitude: RasterStats: Standard Deviations are different (Base: 1.66231295967939, Test: 1.662312959637976)
    #    EBS_IDW_Longitude: RasterDataset: Pixel data (123330 out of 278052) are different.
    #    EBS_IDW_Longitude: RasterStats: Maximums are different (Base: -157.95578656, Test: -157.9557865626333).
    #    EBS_IDW_Longitude: RasterStats: Minimums are different (Base: -178.97202489, Test: -178.9720248865492).
    #    EBS_IDW_Longitude: RasterStats: Standard Deviations are different (Base: 5.009573288797198, Test: 5.009573288862775)
    #    ENBS_IDW_Bathymetry: RasterStats: Standard Deviations are different (Base: 39.52488887007286, Test: 39.52488887007345)
    #    ENBS_IDW_Latitude: RasterDataset: Pixel data (173069 out of 351936) are different.
    #    ENBS_IDW_Latitude: RasterStats: Maximums are different (Base: 65.49900778, Test: 65.49900778041628).
    #    ENBS_IDW_Latitude: RasterStats: Means are different (Base: 59.60658099915545, Test: 59.60658099916241).
    #    ENBS_IDW_Latitude: RasterStats: Minimums are different (Base: 54.50074794, Test: 54.50074793981359).
    #    ENBS_IDW_Latitude: RasterStats: Standard Deviations are different (Base: 2.595643851973987, Test: 2.595643851987917)
    #    ENBS_IDW_Longitude: RasterDataset: Pixel data (173029 out of 351936) are different.
    #    ENBS_IDW_Longitude: RasterStats: Maximums are different (Base: -157.95578656, Test: -157.9557865626333).
    #    ENBS_IDW_Longitude: RasterStats: Means are different (Base: -168.7977635323551, Test: -168.7977635323517).
    #    ENBS_IDW_Longitude: RasterStats: Minimums are different (Base: -178.97202489, Test: -178.9720248865492).
    #    ENBS_IDW_Longitude: RasterStats: Standard Deviations are different (Base: 4.503739745624906, Test: 4.503739745682402)
    #    GMEX_IDW_Latitude: RasterDataset: Pixel data (58553 out of 194023) are different.
    #    GMEX_IDW_Latitude: RasterStats: Maximums are different (Base: 30.37717333, Test: 30.37717332614585).
    #    GMEX_IDW_Latitude: RasterStats: Means are different (Base: 28.38155082893642, Test: 28.38155082893351).
    #    GMEX_IDW_Latitude: RasterStats: Minimums are different (Base: 25.91211189, Test: 25.9121118885277).
    #    GMEX_IDW_Latitude: RasterStats: Standard Deviations are different (Base: 1.057945226280967, Test: 1.057945226296362)
    #    GMEX_IDW_Longitude: RasterDataset: Pixel data (58546 out of 194023) are different.
    #    GMEX_IDW_Longitude: RasterStats: Maximums are different (Base: -81.93873807, Test: -81.93873806704825).
    #    GMEX_IDW_Longitude: RasterStats: Means are different (Base: -89.30679018643251, Test: -89.30679018644352).
    #    GMEX_IDW_Longitude: RasterStats: Minimums are different (Base: -97.36920403000001, Test: -97.36920403439561).
    #    GMEX_IDW_Longitude: RasterStats: Standard Deviations are different (Base: 4.924381658042293, Test: 4.924381658039399)
    #    GOA_IDW_Latitude: RasterDataset: Pixel data (81365 out of 492800) are different.
    #    GOA_IDW_Latitude: RasterStats: Maximums are different (Base: 60.38001807, Test: 60.38001807259369).
    #    GOA_IDW_Latitude: RasterStats: Means are different (Base: 56.97336084269754, Test: 56.97336084269208).
    #    GOA_IDW_Latitude: RasterStats: Minimums are different (Base: 52.34076784, Test: 52.3407678444449).
    #    GOA_IDW_Latitude: RasterStats: Standard Deviations are different (Base: 1.998025397610071, Test: 1.998025397571027)
    #    GOA_IDW_Longitude: RasterDataset: Pixel data (81345 out of 492800) are different.
    #    GOA_IDW_Longitude: RasterStats: Maximums are different (Base: -132.61314185, Test: -132.6131418480727).
    #    GOA_IDW_Longitude: RasterStats: Minimums are different (Base: -169.99928311, Test: -169.9992831108524).
    #    GOA_IDW_Longitude: RasterStats: Standard Deviations are different (Base: 8.979155078961128, Test: 8.979155078964391)
    #    HI_IDW_Latitude: RasterDataset: Pixel data (25899 out of 870184) are different.
    #    HI_IDW_Latitude: RasterStats: Maximums are different (Base: 22.29757341, Test: 22.29757340775398).
    #    HI_IDW_Latitude: RasterStats: Means are different (Base: 20.79670183507728, Test: 20.79670183510212).
    #    HI_IDW_Latitude: RasterStats: Minimums are different (Base: 18.84874037, Test: 18.84874037277309).
    #    HI_IDW_Latitude: RasterStats: Standard Deviations are different (Base: 0.6816558740180771, Test: 0.6816558740307908)
    #    HI_IDW_Longitude: RasterDataset: Pixel data (25891 out of 870184) are different.
    #    HI_IDW_Longitude: RasterStats: Maximums are different (Base: -154.79174082, Test: -154.7917408163426).
    #    HI_IDW_Longitude: RasterStats: Means are different (Base: -156.8196455127903, Test: -156.8196455127969).
    #    HI_IDW_Longitude: RasterStats: Minimums are different (Base: -160.27488887, Test: -160.2748888709185).
    #    HI_IDW_Longitude: RasterStats: Standard Deviations are different (Base: 1.192727399280196, Test: 1.192727399365096)
    #    NBS_IDW_Latitude: RasterDataset: Pixel data (49711 out of 112217) are different.
    #    NBS_IDW_Latitude: RasterStats: Maximums are different (Base: 65.49941585000001, Test: 65.49941585327834).
    #    NBS_IDW_Latitude: RasterStats: Means are different (Base: 62.88575439503616, Test: 62.88575439504791).
    #    NBS_IDW_Latitude: RasterStats: Minimums are different (Base: 60.5011813, Test: 60.50118129682331).
    #    NBS_IDW_Latitude: RasterStats: Standard Deviations are different (Base: 1.229545212107881, Test: 1.229545212088624)
    #    NBS_IDW_Longitude: RasterDataset: Pixel data (49696 out of 112217) are different.
    #    NBS_IDW_Longitude: RasterStats: Maximums are different (Base: -161.14811963, Test: -161.1481196303058).
    #    NBS_IDW_Longitude: RasterStats: Minimums are different (Base: -176.06878283, Test: -176.068782828446).
    #    NBS_IDW_Longitude: RasterStats: Standard Deviations are different (Base: 2.876026453554216, Test: 2.876026453620081)
    #    NEUS_FAL_IDW_Latitude: RasterDataset: Pixel data (57134 out of 226100) are different.
    #    NEUS_FAL_IDW_Latitude: RasterStats: Maximums are different (Base: 44.4723772, Test: 44.47237719973694).
    #    NEUS_FAL_IDW_Latitude: RasterStats: Means are different (Base: 40.85264522672377, Test: 40.85264522673788).
    #    NEUS_FAL_IDW_Latitude: RasterStats: Minimums are different (Base: 35.15117556, Test: 35.15117556266948).
    #    NEUS_FAL_IDW_Latitude: RasterStats: Standard Deviations are different (Base: 1.987858930407973, Test: 1.987858930406464)
    #    NEUS_FAL_IDW_Longitude: RasterDataset: Pixel data (57133 out of 226100) are different.
    #    NEUS_FAL_IDW_Longitude: RasterStats: Maximums are different (Base: -65.59251707, Test: -65.59251706678963).
    #    NEUS_FAL_IDW_Longitude: RasterStats: Means are different (Base: -70.31157151316948, Test: -70.3115715131851).
    #    NEUS_FAL_IDW_Longitude: RasterStats: Minimums are different (Base: -75.79278403000001, Test: -75.79278403329747).
    #    NEUS_FAL_IDW_Longitude: RasterStats: Standard Deviations are different (Base: 2.802085845534008, Test: 2.802085845507762)
    #    NEUS_SPR_IDW_Latitude: RasterDataset: Pixel data (57134 out of 226100) are different.
    #    NEUS_SPR_IDW_Latitude: RasterStats: Maximums are different (Base: 44.4723772, Test: 44.47237719973694).
    #    NEUS_SPR_IDW_Latitude: RasterStats: Means are different (Base: 40.85264522672377, Test: 40.852645226738).
    #    NEUS_SPR_IDW_Latitude: RasterStats: Minimums are different (Base: 35.15117556, Test: 35.15117556266948).
    #    NEUS_SPR_IDW_Latitude: RasterStats: Standard Deviations are different (Base: 1.987858930407973, Test: 1.987858930403906)
    #    NEUS_SPR_IDW_Longitude: RasterDataset: Pixel data (57133 out of 226100) are different.
    #    NEUS_SPR_IDW_Longitude: RasterStats: Maximums are different (Base: -65.59251707, Test: -65.59251706678963).
    #    NEUS_SPR_IDW_Longitude: RasterStats: Means are different (Base: -70.31157151316948, Test: -70.31157151318502).
    #    NEUS_SPR_IDW_Longitude: RasterStats: Minimums are different (Base: -75.79278403000001, Test: -75.79278403329747).
    #    NEUS_SPR_IDW_Longitude: RasterStats: Standard Deviations are different (Base: 2.802085845534008, Test: 2.802085845509251)
    #    SEUS_FAL_IDW_Latitude: RasterDataset: Pixel data (4257 out of 101010) are different.
    #    SEUS_FAL_IDW_Latitude: RasterStats: Maximums are different (Base: 35.22953668, Test: 35.22953667973185).
    #    SEUS_FAL_IDW_Latitude: RasterStats: Means are different (Base: 32.39395439934467, Test: 32.39395439938856).
    #    SEUS_FAL_IDW_Latitude: RasterStats: Minimums are different (Base: 28.69158875, Test: 28.69158875267374).
    #    SEUS_FAL_IDW_Latitude: RasterStats: Standard Deviations are different (Base: 1.703230109823383, Test: 1.703230109809957)
    #    SEUS_FAL_IDW_Longitude: RasterDataset: Pixel data (4257 out of 101010) are different.
    #    SEUS_FAL_IDW_Longitude: RasterStats: Maximums are different (Base: -75.51669124999999, Test: -75.51669124607784).
    #    SEUS_FAL_IDW_Longitude: RasterStats: Means are different (Base: -79.4993973681491, Test: -79.49939736823106).
    #    SEUS_FAL_IDW_Longitude: RasterStats: Minimums are different (Base: -81.44583305, Test: -81.44583304769182).
    #    SEUS_FAL_IDW_Longitude: RasterStats: Standard Deviations are different (Base: 1.693540503942288, Test: 1.6935405038844)
    #    SEUS_SPR_IDW_Latitude: RasterDataset: Pixel data (4257 out of 101010) are different.
    #    SEUS_SPR_IDW_Latitude: RasterStats: Maximums are different (Base: 35.22953668, Test: 35.22953667973185).
    #    SEUS_SPR_IDW_Latitude: RasterStats: Means are different (Base: 32.39395439934467, Test: 32.39395439938856).
    #    SEUS_SPR_IDW_Latitude: RasterStats: Minimums are different (Base: 28.69158875, Test: 28.69158875267374).
    #    SEUS_SPR_IDW_Latitude: RasterStats: Standard Deviations are different (Base: 1.703230109823383, Test: 1.703230109809636)
    #    SEUS_SPR_IDW_Longitude: RasterDataset: Pixel data (4257 out of 101010) are different.
    #    SEUS_SPR_IDW_Longitude: RasterStats: Maximums are different (Base: -75.51669124999999, Test: -75.51669124607784).
    #    SEUS_SPR_IDW_Longitude: RasterStats: Means are different (Base: -79.4993973681491, Test: -79.49939736823106).
    #    SEUS_SPR_IDW_Longitude: RasterStats: Minimums are different (Base: -81.44583305, Test: -81.44583304769182).
    #    SEUS_SPR_IDW_Longitude: RasterStats: Standard Deviations are different (Base: 1.693540503942288, Test: 1.6935405038844)
    #    SEUS_SUM_IDW_Latitude: RasterDataset: Pixel data (4257 out of 101010) are different.
    #    SEUS_SUM_IDW_Latitude: RasterStats: Maximums are different (Base: 35.22953668, Test: 35.22953667973185).
    #    SEUS_SUM_IDW_Latitude: RasterStats: Means are different (Base: 32.39395439934467, Test: 32.39395439938856).
    #    SEUS_SUM_IDW_Latitude: RasterStats: Minimums are different (Base: 28.69158875, Test: 28.69158875267374).
    #    SEUS_SUM_IDW_Latitude: RasterStats: Standard Deviations are different (Base: 1.703230109823383, Test: 1.703230109809957)
    #    SEUS_SUM_IDW_Longitude: RasterDataset: Pixel data (4257 out of 101010) are different.
    #    SEUS_SUM_IDW_Longitude: RasterStats: Maximums are different (Base: -75.51669124999999, Test: -75.51669124607784).
    #    SEUS_SUM_IDW_Longitude: RasterStats: Means are different (Base: -79.4993973681491, Test: -79.49939736823109).
    #    SEUS_SUM_IDW_Longitude: RasterStats: Minimums are different (Base: -81.44583305, Test: -81.44583304769182).
    #    SEUS_SUM_IDW_Longitude: RasterStats: Standard Deviations are different (Base: 1.693540503942288, Test: 1.693540503883884)
    #    WC_ANN_IDW_Latitude: RasterDataset: Pixel data (30997 out of 371688) are different.
    #    WC_ANN_IDW_Latitude: RasterStats: Maximums are different (Base: 48.50052681, Test: 48.50052680863789).
    #    WC_ANN_IDW_Latitude: RasterStats: Means are different (Base: 39.33097720194896, Test: 39.3309772019335).
    #    WC_ANN_IDW_Latitude: RasterStats: Minimums are different (Base: 31.99274915, Test: 31.99274915392884).
    #    WC_ANN_IDW_Latitude: RasterStats: Standard Deviations are different (Base: 5.263036361739247, Test: 5.263036361741507)
    #    WC_ANN_IDW_Longitude: RasterDataset: Pixel data (30990 out of 371688) are different.
    #    WC_ANN_IDW_Longitude: RasterStats: Maximums are different (Base: -117.27587488, Test: -117.275874884471).
    #    WC_ANN_IDW_Longitude: RasterStats: Means are different (Base: -122.5291847856864, Test: -122.5291847856878).
    #    WC_ANN_IDW_Longitude: RasterStats: Minimums are different (Base: -125.96992747, Test: -125.9699274711949).
    #    WC_ANN_IDW_Longitude: RasterStats: Standard Deviations are different (Base: 2.475505805914034, Test: 2.475505805855001)
    #    WC_TRI_IDW_Bathymetry: RasterDataset: Pixel data (2 out of 135135) are different.
    #    WC_TRI_IDW_Bathymetry: RasterStats: Means are different (Base: -191.5584727084144, Test: -191.5563982886036).
    #    WC_TRI_IDW_Bathymetry: RasterStats: Standard Deviations are different (Base: 186.372907540231, Test: 186.3625774430447)
    #    WC_TRI_IDW_Latitude: RasterDataset: Pixel data (15431 out of 135135) are different.
    #    WC_TRI_IDW_Latitude: RasterStats: Maximums are different (Base: 49.00840152, Test: 49.00840151894381).
    #    WC_TRI_IDW_Latitude: RasterStats: Means are different (Base: 43.8396277711029, Test: 43.83962777108595).
    #    WC_TRI_IDW_Latitude: RasterStats: Minimums are different (Base: 36.19402509, Test: 36.19402508849818).
    #    WC_TRI_IDW_Latitude: RasterStats: Standard Deviations are different (Base: 3.726027110165568, Test: 3.726027110168742)
    #    WC_TRI_IDW_Longitude: RasterDataset: Pixel data (15426 out of 135135) are different.
    #    WC_TRI_IDW_Longitude: RasterStats: Maximums are different (Base: -121.76827786, Test: -121.7682778610204).
    #    WC_TRI_IDW_Longitude: RasterStats: Means are different (Base: -124.4203416071847, Test: -124.4203416072082).
    #    WC_TRI_IDW_Longitude: RasterStats: Minimums are different (Base: -126.61970282, Test: -126.6197028235289).
    #    WC_TRI_IDW_Longitude: RasterStats: Standard Deviations are different (Base: 0.8438245467310601, Test: 0.843824546783702)

                    RasterCompare = True
                    if RasterCompare:

                        arcpy.management.RasterCompare(
                                                       in_base_raster       = rf"{input_base_gdb}\{raster}",
                                                       in_test_raster       = rf"{input_test_gdb}\{raster}",
                                                       compare_type         = "GDB_RASTER_DATASET", #RASTER_DATASET,  MOSAIC_DATASET
                                                       ignore_option        = "Colormap;'Raster Attribute Table';Metadata;'Pyramids Exist';Compression;'Pyramid Origin';'Pyramid Parameters';'Tile Size'", #"Colormap;'Raster Attribute Table';Statistics;Metadata;'Pyramids Exist';Compression;'Pyramid Origin';'Pyramid Parameters';'Tile Size'",
                                                       continue_compare     = "CONTINUE_COMPARE",
                                                       out_compare_file     = fr"E:\DisMAP Compare\FeatureCompareOut_{raster}.txt",
                                                       parameter_tolerances = None,
                                                       attribute_tolerances = None,
                                                       omit_field           = None
                                                      )
                        #arcpy.AddMessage("\t"+arcpy.GetMessages().replace("\n", "\n\t"))
                        gms = [gm for gm in arcpy.GetMessages().split("\n") if not any(m in gm for m in ["are the same", "Start Time", "Succeeded at", "Raster:"])]

                        if gms:
                            arcpy.AddMessage(f"\n{'-' * 90}\n")
                            for gm in gms:
                                arcpy.AddMessage(f"{raster}")
                                arcpy.AddMessage(f"\tWARNING: {gm}")
                                differences.append(f"{raster}: {gm}")
                                del gm
                            arcpy.AddMessage(f"\n{'-' * 90}\n")
                        else:
                            arcpy.AddMessage(f"\tRaster {raster} is the same in both {os.path.basename(input_base_gdb)} and {os.path.basename(input_test_gdb)}")
                            arcpy.AddMessage(f"\n")
                        del gms

                    del RasterCompare

                else:
                    arcpy.AddMessage(f"\t\t{os.path.basename(raster.replace(input_base_gdb, input_test_gdb))} is missing from {os.path.basename(input_test_gdb)}")

                del raster
            del rasters
        del wild_cards

        if differences:
            arcpy.AddMessage(f"There are differences")
            for difference in sorted(differences):
                arcpy.AddMessage(difference)
                del difference
        else:
            pass
            #arcpy.AddMessage("No difference between Base and Target")
        del differences

        arcpy.AddMessage(f"\n{'-' * 90}\n")

        # Variables set in function
        del pixel_types
        # Imports

        # Function Parameters
        del input_base_gdb, input_test_gdb

    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteError:
        raise SystemExit(arcpy.GetMessages())
    except arcpy.ExecuteWarning:
        raise SystemExit(arcpy.GetMessages())
    except SystemExit as se:
        raise SystemExit(str(se))
    except:
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        raise SystemExit(pymsg)
    else:
        try:
            import inspect
            leave_out_keys = ["leave_out_keys", "remaining_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys

            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]

        except:
            traceback.print_exc()
    finally:
        try:
            if "results" in locals().keys(): del results
        except UnboundLocalError:
            pass

def table_compare(input_base_gdb="", input_test_gdb=""):
    try:

        arcpy.env.overwriteOutput = True
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2)
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        arcpy.AddMessage(f"{'-' * 90}\n")

        arcpy.env.workspace = input_base_gdb

        in_base_tables = [tb for tb in arcpy.ListTables("*") if tb.endswith("_Indicators") and not any(lo in tb for lo in ["GFDL", "GLMME"])]
        #in_base_tables = [tb for tb in arcpy.ListTables("*") if tb == "GMEX_IDW_Indicators"]
        #['GMEX_IDW_Indicators_Base', 'NEUS_FAL_IDW_Indicators_Base', 'NEUS_SPR_IDW_Indicators_Base']

        differences = []

        tables = []
        for in_base_table in sorted(in_base_tables):
            #arcpy.AddMessage(rf"{in_base_table}")

            if arcpy.Exists(rf"{input_base_gdb}\{in_base_table}"):
                in_base_table_path = rf"{input_base_gdb}\{in_base_table}"
                in_test_table      = in_base_table
                in_test_table_path = rf"{input_test_gdb}\{in_test_table}"

                #arcpy.AddMessage(f"In Base FC: {in_base_table} In Test FC: {in_test_table}")
                arcpy.AddMessage(f"In Base FC: {os.path.basename(os.path.dirname(in_base_table_path))}\{in_base_table}\nIn Test FC: {os.path.basename(os.path.dirname(in_test_table_path))}\{in_test_table}")

                if arcpy.Exists(f"E:\DisMAP Compare\TableCompareOut_{in_base_table}.txt"): arcpy.management.Delete(fr"E:\DisMAP Compare\TableCompareOut_{in_base_table}.txt")

                TableStatistics = True
                if TableStatistics:

                    dismap_gdb = rf"{os.environ['USERPROFILE']}\Documents\ArcGIS\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\DisMAP.gdb"

                    in_base_table_dismap_gdb = f"{dismap_gdb}\{in_base_table}_Base"
                    in_test_table_dismap_gdb = f"{dismap_gdb}\{in_test_table}_Test"

                    #arcpy.AddMessage(f"\tTable: {in_base_table}")

                    #arcpy.AddMessage(f"\tExport Table to create: {in_base_table}_Base")

                    arcpy.conversion.ExportTable(
                                                 in_table                = in_base_table_path,
                                                 out_table               = in_base_table_dismap_gdb,
                                                 where_clause            = "",
                                                 use_field_alias_as_name = "NOT_USE_ALIAS",
                                                 field_mapping           = fr'Species "Species" true true false 50 Text 0 0,First,#,{in_base_table_path},Species,0,49;Year "Year" true true false 2 Short 0 0,First,#,{in_base_table_path},Year,-1,-1;in_base_table_CenterOfGravityLongitude "in_base_table Center Of Gravity Longitude" true true false 255 Double 0 0,First,#,{in_base_table_path},CenterOfGravityLongitude,-1,-1;in_base_table_MinimumLongitude "in_base_table Minimum Longitude" true true false 255 Double 0 0,First,#,{in_base_table_path},MinimumLongitude,-1,-1;in_base_table_MaximumLongitude "in_base_table Maximum Longitude" true true false 255 Double 0 0,First,#,{in_base_table_path},MaximumLongitude,-1,-1;in_base_table_OffsetLongitude "in_base_table Offset Longitude" true true false 255 Double 0 0,First,#,{in_base_table_path},OffsetLongitude,-1,-1;in_base_table_CenterOfGravityLatitude "in_base_table Center of Gravity Latitude" true true false 8 Double 0 0,First,#,{in_base_table_path},CenterOfGravityLatitude,-1,-1;in_base_table_MinimumLatitude "in_base_table Minimum Latitude" true true false 8 Double 0 0,First,#,{in_base_table_path},MinimumLatitude,-1,-1;in_base_table_MaximumLatitude "in_base_table Maximum Latitude" true true false 8 Double 0 0,First,#,{in_base_table_path},MaximumLatitude,-1,-1;in_base_table_OffsetLatitude "in_base_table Offset Latitude" true true false 8 Double 0 0,First,#,{in_base_table_path},OffsetLatitude,-1,-1;in_base_table_CenterOfGravityDepth "in_base_table CenterOfGravityDepth" true true false 255 Double 0 0,First,#,{in_base_table_path},CenterOfGravityDepth,-1,-1;in_base_table_MinimumDepth "in_base_table Minimum Depth" true true false 255 Double 0 0,First,#,{in_base_table_path},MinimumDepth,-1,-1;in_base_table_MaximumDepth "in_base_table Maximum Depth" true true false 255 Double 0 0,First,#,{in_base_table_path},MaximumDepth,-1,-1;in_base_table_OffsetDepth "in_base_table Offset Depth" true true false 255 Double 0 0,First,#,{in_base_table_path},OffsetDepth,-1,-1',
                                                 sort_field              = "Species ASCENDING;Year ASCENDING"
                                                )

                    #arcpy.AddMessage(f"\tExport Table to create: {in_test_table}_Test")

                    arcpy.conversion.ExportTable(
                                                 in_table                = in_test_table_path,
                                                 out_table               = in_test_table_dismap_gdb,
                                                 where_clause            = "",
                                                 use_field_alias_as_name = "NOT_USE_ALIAS",
                                                 field_mapping           = fr'Species "Species" true true false 50 Text 0 0,First,#,{in_test_table_path},Species,0,49;Year "Year" true true false 2 Short 0 0,First,#,{in_test_table_path},Year,-1,-1;in_test_table_CenterOfGravityLongitude "in_test_table Center Of Gravity Longitude" true true false 255 Double 0 0,First,#,{in_test_table_path},CenterOfGravityLongitude,-1,-1;in_test_table_MinimumLongitude "in_test_table Minimum Longitude" true true false 255 Double 0 0,First,#,{in_test_table_path},MinimumLongitude,-1,-1;in_test_table_MaximumLongitude "in_test_table Maximum Longitude" true true false 255 Double 0 0,First,#,{in_test_table_path},MaximumLongitude,-1,-1;in_test_table_OffsetLongitude "in_test_table Offset Longitude" true true false 255 Double 0 0,First,#,{in_test_table_path},OffsetLongitude,-1,-1;in_test_table_CenterOfGravityLatitude "in_test_table Center of Gravity Latitude" true true false 8 Double 0 0,First,#,{in_test_table_path},CenterOfGravityLatitude,-1,-1;in_test_table_MinimumLatitude "in_test_table Minimum Latitude" true true false 8 Double 0 0,First,#,{in_test_table_path},MinimumLatitude,-1,-1;in_test_table_MaximumLatitude "in_test_table Maximum Latitude" true true false 8 Double 0 0,First,#,{in_test_table_path},MaximumLatitude,-1,-1;in_test_table_OffsetLatitude "in_test_table Offset Latitude" true true false 8 Double 0 0,First,#,{in_test_table_path},OffsetLatitude,-1,-1;in_test_table_CenterOfGravityDepth "in_test_table CenterOfGravityDepth" true true false 255 Double 0 0,First,#,{in_test_table_path},CenterOfGravityDepth,-1,-1;in_test_table_MinimumDepth "in_test_table Minimum Depth" true true false 255 Double 0 0,First,#,{in_test_table_path},MinimumDepth,-1,-1;in_test_table_MaximumDepth "in_test_table Maximum Depth" true true false 255 Double 0 0,First,#,{in_test_table_path},MaximumDepth,-1,-1;in_test_table_OffsetDepth "in_test_table Offset Depth" true true false 255 Double 0 0,First,#,{in_test_table_path},OffsetDepth,-1,-1',
                                                 sort_field              = "Species ASCENDING;Year ASCENDING"
                                                )

                    #fields = [f.name for f in arcpy.ListFields(in_test_fc_dismap_gdb) if any(x in f.name for x in ["Longitude", "Latitude"])]
                    #for field in fields:
                    #    print(field)
                    #    del field

                    #arcpy.AddMessage(f"\tJoin {in_test_table}_Test to {in_base_table}_Base")
                    joined_table = arcpy.management.JoinField(
                                                              in_data           = in_base_table_dismap_gdb,
                                                              in_field          = arcpy.Describe(in_base_table_dismap_gdb).OIDFieldName,
                                                              join_table        = in_test_table_dismap_gdb,
                                                              join_field        = arcpy.Describe(in_test_table_dismap_gdb).OIDFieldName,
                                                              fields            = None,
                                                              fm_option         = "NOT_USE_FM",
                                                              field_mapping     = None,
                                                              index_join_fields = "NEW_INDEXES"
                                                             )

                    #arcpy.AddMessage("\tCalculate Center of Gravity Longitude Difference Field")
                    with arcpy.EnvManager(scratchWorkspace = dismap_gdb, workspace = dismap_gdb):
                        arcpy.management.CalculateField(
                                                        in_table        = in_base_table_dismap_gdb,
                                                        field           = "CenterOfGravityLongitude_Defference",
                                                        expression      = "!in_base_table_CenterOfGravityLongitude! - !in_test_table_CenterOfGravityLongitude!",
                                                        expression_type = "PYTHON3",
                                                        code_block      = "",
                                                        field_type      = "FLOAT",
                                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                                       )

                    #arcpy.AddMessage("\tCalculate Center of Gravity Latitude Difference Field")
                    with arcpy.EnvManager(scratchWorkspace = dismap_gdb, workspace = dismap_gdb):
                        arcpy.management.CalculateField(
                                                        in_table        = in_base_table_dismap_gdb,
                                                        field           = "CenterOfGravityLatitude_Difference",
                                                        expression      = "!in_base_table_CenterOfGravityLatitude! - !in_test_table_CenterOfGravityLatitude!",
                                                        expression_type = "PYTHON3",
                                                        code_block      = "",
                                                        field_type      = "FLOAT",
                                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                                       )

                    #arcpy.AddMessage("\tCalculate Center of Gravity Depth Difference Field")
                    with arcpy.EnvManager(scratchWorkspace = dismap_gdb, workspace = dismap_gdb):
                        arcpy.management.CalculateField(
                                                        in_table        = in_base_table_dismap_gdb,
                                                        field           = "CenterOfGravityDepth_Difference",
                                                        expression      = "!in_base_table_CenterOfGravityDepth! - !in_test_table_CenterOfGravityDepth!",
                                                        expression_type = "PYTHON3",
                                                        code_block      = "",
                                                        field_type      = "FLOAT",
                                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                                       )

                    in_base_table_dismap_gdb_statistics = rf"{in_base_table_dismap_gdb}_Statistics"
                    with arcpy.EnvManager(scratchWorkspace = dismap_gdb, workspace = dismap_gdb):
                        arcpy.analysis.Statistics(
                                                  in_table                = in_base_table_dismap_gdb,
                                                  out_table               = in_base_table_dismap_gdb_statistics,
                                                  statistics_fields       = "CenterOfGravityLongitude_Defference MIN;CenterOfGravityLongitude_Defference MAX;CenterOfGravityLongitude_Defference RANGE;CenterOfGravityLongitude_Defference MEAN;CenterOfGravityLongitude_Defference MEDIAN;CenterOfGravityLongitude_Defference STD;CenterOfGravityLongitude_Defference VARIANCE;CenterOfGravityLatitude_Difference MIN;CenterOfGravityLatitude_Difference MAX;CenterOfGravityLatitude_Difference RANGE;CenterOfGravityLatitude_Difference MEAN;CenterOfGravityLatitude_Difference MEDIAN;CenterOfGravityLatitude_Difference STD;CenterOfGravityLatitude_Difference VARIANCE;CenterOfGravityDepth_Difference MIN;CenterOfGravityDepth_Difference MAX;CenterOfGravityDepth_Difference RANGE;CenterOfGravityDepth_Difference MEAN;CenterOfGravityDepth_Difference MEDIAN;CenterOfGravityDepth_Difference STD;CenterOfGravityDepth_Difference VARIANCE",
                                                  case_field              = None,
                                                  concatenation_separator = ""
                                                )

                    #fields = [f.name for f in arcpy.ListFields(in_base_table_dismap_gdb_statistics) if any(x in f.name for x in ["Longitude", "Latitude"])]
                    fields = [f.name for f in arcpy.ListFields(in_base_table_dismap_gdb_statistics) if any(x in f.name for x in ["STD", "VARIANCE"])]
                    #for field in fields:
                    #    print(field)
                    #    del field

                    arcpy.AddMessage(f"\tSearch Cursor on {in_base_table}_Statitics")

                    with arcpy.da.SearchCursor(in_base_table_dismap_gdb_statistics, fields) as cursor:
                        for row in cursor:
                            #print(row)
                            arcpy.AddMessage(f"\t\tCenterOfGravityLongitude_Defference")
                            arcpy.AddMessage(f"\t\t\tSTD_CenterOfGravityLongitude_Defference:      {row[0]}")
                            arcpy.AddMessage(f"\t\t\tVARIANCE_CenterOfGravityLongitude_Defference: {row[1]}")

                            arcpy.AddMessage(f"\t\tCenterOfGravityLatitude_Difference")
                            arcpy.AddMessage(f"\t\t\tSTD_CenterOfGravityLatitude_Difference:       {row[2]}")
                            arcpy.AddMessage(f"\t\t\tVARIANCE_CenterOfGravityLatitude_Difference:  {row[3]}")

                            arcpy.AddMessage(f"\t\tCenterOfGravityDepth_Difference")
                            arcpy.AddMessage(f"\t\t\tSTD_CenterOfGravityDepth_Difference:       {row[4]}")
                            arcpy.AddMessage(f"\t\t\tVARIANCE_CenterOfGravityDepth_Difference:  {row[5]}")
                            del row
                        del cursor

                    del fields

                    #arcpy.AddMessage(f"\n\tDeleting: {in_base_table}_Statistics")
                    #arcpy.management.Delete(in_base_table_dismap_gdb_statistics)
                    del in_base_table_dismap_gdb_statistics
                    #arcpy.AddMessage(f"\tDeleting: {in_base_table}_Base")
                    #arcpy.management.Delete(in_base_table_dismap_gdb)
                    del in_base_table_dismap_gdb
                    #arcpy.AddMessage(f"\tDeleting: {in_test_table}_Test\n")
                    #arcpy.management.Delete(in_test_table_dismap_gdb)
                    del in_test_table_dismap_gdb

                    del joined_table

                    del dismap_gdb



##                    in_base_table_dismap_gdb_fields = [f.name for f in arcpy.ListFields(in_base_table_dismap_gdb)]
##                    #print('", "'.join(in_base_table_dismap_gdb_fields))
##                    #"OBJECTID", "Species", "Year", "in_base_table_CenterOfGravityLongitude", "in_base_table_MinimumLongitude", "in_base_table_MaximumLongitude", "in_base_table_OffsetLongitude", "in_base_table_CenterOfGravityLatitude", "in_base_table_MinimumLatitude", "in_base_table_MaximumLatitude", "in_base_table_OffsetLatitude", "in_base_table_CenterOfGravityDepth", "in_base_table_MinimumDepth", "in_base_table_MaximumDepth", "in_base_table_OffsetDepth"
##
##                    in_test_table_dismap_gdb_fields = [f.name for f in arcpy.ListFields(in_test_table_dismap_gdb)]
##                    #print('", "'.join(in_test_table_dismap_gdb_fields))
##                    #"OBJECTID", "Species", "Year", "in_test_table_CenterOfGravityLongitude", "in_test_table_MinimumLongitude", "in_test_table_MaximumLongitude", "in_test_table_OffsetLongitude", "in_test_table_CenterOfGravityLatitude", "in_test_table_MinimumLatitude", "in_test_table_MaximumLatitude", "in_test_table_OffsetLatitude", "in_test_table_CenterOfGravityDepth", "in_test_table_MinimumDepth", "in_test_table_MaximumDepth", "in_test_table_OffsetDepth"
##
##                    with arcpy.da.SearchCursor(in_base_table_dismap_gdb, in_base_table_dismap_gdb_fields) as in_base_table_cursor:
##
##                        for in_base_table_row in in_base_table_cursor:
##
##                            #arcpy.AddMessage(f"\t\tin_base_table_row: {in_base_table_row}")
##                            #species = in_base_table_row[1]
##                            #year    = in_base_table_row[3]
##                            #print(f"Species = '{species}' and Year = {year}")
##
##                            with arcpy.da.SearchCursor(in_test_table_dismap_gdb, in_test_table_dismap_gdb_fields, f"Species = '{in_base_table_row[1]}' and Year = {in_base_table_row[2]}") as input_test_table_cursor:
##
##                                for in_test_table_row in input_test_table_cursor:
##                                    arcpy.AddMessage(f"\t\tin_base_table_row: {in_base_table_row}")
##                                    arcpy.AddMessage(f"\t\tin_test_table_row: {in_test_table_row}")
##
##                                    #if in_base_table_row[0] != in_test_table_row[0]:
##                                    #    if os.path.basename(in_base_table_dismap_gdb) not in tables:
##                                    #        tables.append(os.path.basename(in_base_table_dismap_gdb))
##                                    #    arcpy.AddMessage(f"\t\tin_base_table_row: {in_base_table_row}")
##                                    #    arcpy.AddMessage(f"\t\tin_test_table_row: {in_test_table_row}")
##
##                                    del in_test_table_row
##
##                                del input_test_table_cursor
##                            del in_base_table_row
##                        del in_base_table_cursor
##                    del in_test_table_dismap_gdb_fields, in_base_table_dismap_gdb_fields
##
##                    del dismap_gdb
##                    del in_base_table_dismap_gdb, in_test_table_dismap_gdb

                del TableStatistics

                TableCompare = False
                if TableCompare:
                    arcpy.management.TableCompare(
                                                  in_base_table        = in_base_table_path,
                                                  in_test_table        = in_test_table_path,
                                                  sort_field           = "OBJECTID;DatasetCode;Region;Species;Year",
                                                  compare_type         = "ATTRIBUTES_ONLY", # ALL, ATTRIBUTES_ONLY, SCHEMA_ONLY
                                                  ignore_options       = None,
                                                  attribute_tolerances = None,
                                                  omit_field           = "OBJECTID;Season;DateCode;DistributionProjectName;DistributionProjectCode;SummaryProduct;CenterOfGravityLatitudeSE;CenterOfGravityLongitudeSE;CenterOfGravityDepthSE",
                                                  continue_compare     = "CONTINUE_COMPARE",
                                                  out_compare_file     = fr"E:\DisMAP Compare\TableCompareOut_{in_base_table}.txt"
                                                 )

                    #arcpy.AddMessage("\t"+arcpy.GetMessages().replace("\n", "\n\t"))
                    gms = [gm for gm in arcpy.GetMessages().split("\n") if not any(m in gm for m in ["are the same", "Start Time", "Succeeded at"])]

                    if gms:
                        arcpy.AddMessage(f"\n{'-' * 90}\n")
                        for gm in gms:
                            arcpy.AddMessage(f"{in_base_table}")
                            arcpy.AddMessage(f"\tWARNING: {gm}")
                            differences.append(f"{in_base_table}: {gm}")
                            del gm
                        arcpy.AddMessage(f"\n{'-' * 90}\n")
                    else:
                        arcpy.AddMessage(f"\tFeature {in_base_table} is the same in both {os.path.basename(input_base_gdb)} and {os.path.basename(input_test_gdb)}")
                        arcpy.AddMessage(f"\n")
                    del gms
                    #        There are differences: SCHEMA_ONLY
                    #            AI_IDW_Indicators: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
                    #            EBS_IDW_Indicators: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
                    #            ENBS_IDW_Indicators: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
                    #            GMEX_IDW_Indicators: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
                    #            GOA_IDW_Indicators: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
                    #            HI_IDW_Indicators: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
                    #            NBS_IDW_Indicators: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
                    #            NEUS_FAL_IDW_Indicators: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
                    #            NEUS_SPR_IDW_Indicators: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
                    #            SEUS_FAL_IDW_Indicators: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
                    #            SEUS_SPR_IDW_Indicators: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
                    #            SEUS_SUM_IDW_Indicators: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
                    #            WC_ANN_IDW_Indicators: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
                    #            WC_TRI_IDW_Indicators: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).

                del TableCompare

                del in_test_table, in_test_table_path
                del in_base_table, in_base_table_path
            else:
                arcpy.AddMessage(fr"WARNING: {in_base_table} is missing")

        #print(tables);
        del tables
        del in_base_tables

        if differences:
            arcpy.AddMessage(f"There are differences")
            for difference in sorted(differences):
                arcpy.AddMessage(f"\t{difference}")
                del difference
        else:
            pass
            #arcpy.AddMessage("No difference between Base and Target")
        del differences

        arcpy.AddMessage(f"\n{'-' * 90}\n")

        # Variables set in function

        # Imports

        # Function Parameters
        del input_base_gdb, input_test_gdb

    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteError:
        raise SystemExit(arcpy.GetMessages())
    except arcpy.ExecuteWarning:
        raise SystemExit(arcpy.GetMessages())
    except SystemExit as se:
        raise SystemExit(str(se))
    except:
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        raise SystemExit(pymsg)
    else:
        try:
            import inspect
            leave_out_keys = ["leave_out_keys", "remaining_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys

            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]

        except:
            traceback.print_exc()
    finally:
        try:
            if "results" in locals().keys(): del results
        except UnboundLocalError:
            pass

def main(input_base_gdb="", input_test_gdb=""):
    try:
        # Imports
        #from publish_to_portal_director import director
        import dismap
        importlib.reload(dismap)

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        # Imports
        del dismap
        # Function parameters

        results = []

        try:

            GetTransformation = False
            if GetTransformation:
                get_transformation(input_base_gdb, input_test_gdb)
            del GetTransformation

            RasterCompare = False
            if RasterCompare:
                raster_compare(input_base_gdb, input_test_gdb)
            del RasterCompare

            # Completed 4/27/2024. Issue with Lat_Long and Extent_Points and the
            # rounding that occurs for arcpy.management.CalculateGeometryAttributes
            CoordinateFieldCompare = False
            if CoordinateFieldCompare:
                coordinate_field_compare(input_base_gdb, input_test_gdb)
            del CoordinateFieldCompare

            # Completed 4/27/2024. Issue with Lat_Long and Extent_Points and the
            # rounding that occurs for arcpy.management.CalculateGeometryAttributes
            FeatureCompare = False
            if FeatureCompare:
                feature_compare(input_base_gdb, input_test_gdb)
            del FeatureCompare

            # No work done on this one. So far only tables to examine are
            # *_IDW_Sample_Locations and *_IDW tables
            TableCompare = True
            if TableCompare:
                table_compare(input_base_gdb, input_test_gdb)
            del TableCompare

        except SystemExit as se:
            raise SystemExit(str(se))

        # Variable created in function

        # Function parameters
        del input_base_gdb, input_test_gdb

        if results:
            if type(results).__name__ == "bool":
                arcpy.AddMessage(f"'Results' is a {type(results).__name__}" )
                arcpy.AddMessage(f"Result: {results}")
            elif type(results).__name__ == "str":
                arcpy.AddMessage(f"'Results' is a {type(results).__name__}" )
                arcpy.AddMessage(f"Result: {results}")
            elif type(results).__name__ == "list":
                if type(results[0]).__name__ == "list":
                        results = [r for rt in results for r in rt]
                arcpy.AddMessage(f"'Results' is a {type(results).__name__}" )
                for result in results:
                    arcpy.AddMessage(f"Result: {result}")
                del result
            else:
                arcpy.AddMessage(f"No results returned!!!")
        else:
            arcpy.AddMessage(f"No results in '{inspect.stack()[0][3]}'")

    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(arcpy.GetMessages())
        raise SystemExit
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages())
        raise SystemExit
    except SystemExit as se:
        arcpy.AddError(str(se))
        raise SystemExit
    except:
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        raise SystemExit(pymsg)
    else:
        try:
            import inspect
            leave_out_keys = ["leave_out_keys", "remaining_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys

            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]

        except:
            traceback.print_exc()
    finally:
        try:
            if "results" in locals().keys(): del results
        except UnboundLocalError:
            pass

if __name__ == '__main__':
    try:
        # Import this Python module
        import publish_to_portal_director
        importlib.reload(publish_to_portal_director)

        print(f"{'-' * 90}")
        print(f"Python Script:  {os.path.basename(__file__)}")
        print(f"Location:       {os.path.dirname(__file__)}")
        print(f"Python Version: {sys.version} Environment: {os.path.basename(sys.exec_prefix)}")
        print(f"{'-' * 90}\n")

        input_base_gdb = arcpy.GetParameterAsText(0)
        input_test_gdb = arcpy.GetParameterAsText(1)

        if not input_base_gdb:
            #input_base_gdb = rf"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP\April 1 2023\April 1 2023.gdb"
            #input_base_gdb = r"E:\ArcGIS Analysis - Python\April 1 2023\DisMAP April 1 2023 Prod.gdb"
            input_base_gdb = r"E:\DisMAP WI 20230426\April 1 2023\DisMAP April 1 2023 Prod.gdb"
            #input_base_gdb = r"E:\DisMAP WI 20230426\April 1 2023\Bathymetry.gdb"
            #input_base_gdb = r"E:\ArcGIS Analysis - Python\April 1 2023\Alaska.gdb"

        if not input_test_gdb:
            input_test_gdb = rf"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP\May 1 2024\May 1 2024.gdb"
            #input_test_gdb = rf"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP\Bathymetry\Bathymetry.gdb"
            #input_test_gdb = rf"{os.environ['USERPROFILE']}\Documents\ArcGIS\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\DisMAP.gdb"

        # Tested on 4/22/2024 -- PASSED
        main(input_base_gdb, input_test_gdb)

        del input_base_gdb, input_test_gdb

        # NOTES
        #
        # Raster Data
        # No difference between:
        #    This is the output GDBs for processing Alaska, Hawaii, and GEBCO data
        #    r"E:\ArcGIS Analysis - Python\April 1 2023\Bathymetry.gdb"
        #    rf"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP\Bathymetry\Bathymetry.gdb"
        #
        # Differences between:
        #    This is the output GDBs for converting the base bathymetry data above to the spatial
        #    reference and cell size for the region
        #
        #    r"E:\ArcGIS Analysis - Python\April 1 2023\DisMAP April 1 2023 Prod.gdb"
        #    rf"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP\May 1 2024\May 1 2024.gdb"
        #
        #    NOTE!!! No difference between raster masks
        #
        #    AI_IDW_Bathymetry: RasterDataset: NoDataMasks (64 out of 238374) are different. <<<---### NoDataMasks
        #
        #    AI_IDW_Bathymetry: RasterDataset: Pixel data (9972 out of 238374) are different.
        #    AI_IDW_Latitude: RasterDataset: Pixel data (16115 out of 238374) are different.
        #    AI_IDW_Longitude: RasterDataset: Pixel data (16115 out of 238374) are different.
        #
        #    EBS_IDW_Bathymetry: RasterDataset: NoDataMasks (21 out of 278052) are different. <<<---### NoDataMasks
        #
        #    EBS_IDW_Bathymetry: RasterDataset: Pixel data (62615 out of 278052) are different.
        #    EBS_IDW_Latitude: RasterDataset: Pixel data (122988 out of 278052) are different.
        #    EBS_IDW_Longitude: RasterDataset: Pixel data (123379 out of 278052) are different.
        #
        #    ENBS_IDW_Bathymetry: RasterDataset: NoDataMasks (53 out of 351936) are different. <<<---### NoDataMasks
        #
        #    ENBS_IDW_Bathymetry: RasterDataset: Pixel data (88321 out of 351936) are different.
        #    ENBS_IDW_Latitude: RasterDataset: Pixel data (172706 out of 351936) are different.
        #    ENBS_IDW_Longitude: RasterDataset: Pixel data (173097 out of 351936) are different.
        #
        #    NBS_IDW_Bathymetry: RasterDataset: NoDataMasks (6 out of 112217) are different. <<<---### NoDataMasks
        #
        #    NBS_IDW_Bathymetry: RasterDataset: Pixel data (15886 out of 112217) are different.
        #    NBS_IDW_Latitude: RasterDataset: Pixel data (49717 out of 112217) are different.
        #    NBS_IDW_Longitude: RasterDataset: Pixel data (49717 out of 112217) are different.
        #
        #    WC_ANN_IDW_Latitude: RasterDataset: Pixel data (30999 out of 371688) are different.
        #    WC_ANN_IDW_Longitude: RasterDataset: Pixel data (30999 out of 371688) are different.
        #
        # Vector Data
        # Differences between:
        #    This is the output GDBs for converting the base bathymetry data above to the spatial
        #    reference and cell size for the region
        #
        #    r"E:\ArcGIS Analysis - Python\April 1 2023\DisMAP April 1 2023 Prod.gdb"
        #    rf"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP\May 1 2024\May 1 2024.gdb"
        #
        #    NOTE!!! No difference between Fishnets
        #    NOTE!!! No difference between DisMAP Regions geometry
        #    DisMAP_Regions: Field: Field DatasetCode lengths are different (Base: 20, Test: 30).
        #    DisMAP_Regions: Field: Field Season lengths are different (Base: 10, Test: 15).

        from time import localtime, strftime
        print(f"\n{'-' * 90}")
        print(f"Python script: {os.path.basename(__file__)} successfully completed {strftime('%a %b %d %I:%M %p', localtime())}")
        print(f"{'-' * 90}")
        del localtime, strftime

    except SystemExit as se:
        print(se)
    except Exception as e:
        print(e)
    except:
        traceback.print_exc()
    else:
        import inspect
        leave_out_keys = ["leave_out_keys", "remaining_keys", "inspect"]
        leave_out_keys.extend([name for name, obj in inspect.getmembers(sys.modules[__name__]) if inspect.isfunction(obj) or inspect.ismodule(obj)])
        remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
        if remaining_keys:
            arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[1][3]}': ##--> '{', '.join(remaining_keys)}' <--##")
        del leave_out_keys, remaining_keys
    finally:
        pass
