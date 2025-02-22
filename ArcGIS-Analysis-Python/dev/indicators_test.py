# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        create_indicators_table_director
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

def main():
    try:
        pass

##arcpy.conversion.ExportTable(
##    in_table="April 1 2023 Prod Indicators",
##    out_table=r"{os.environ['USERPROFILE']}\Documents\ArcGIS\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\DisMAP.gdb\April_1_2023_Indicators",
##    where_clause="",
##    use_field_alias_as_name="NOT_USE_ALIAS",
##    field_mapping='DatasetCode "Dataset Code" true true false 20 Text 0 0,First,#,April 1 2023 Prod Indicators,DatasetCode,0,19;Region "Region" true true false 40 Text 0 0,First,#,April 1 2023 Prod Indicators,Region,0,39;Season "Season" true true false 10 Text 0 0,First,#,April 1 2023 Prod Indicators,Season,0,9;DateCode "Date Code" true true false 10 Text 0 0,First,#,April 1 2023 Prod Indicators,DateCode,0,9;Species "Species" true true false 50 Text 0 0,First,#,April 1 2023 Prod Indicators,Species,0,49;CommonName "Common Name" true true false 40 Text 0 0,First,#,April 1 2023 Prod Indicators,CommonName,0,39;CoreSpecies "Core Species" true true false 5 Text 0 0,First,#,April 1 2023 Prod Indicators,CoreSpecies,0,4;Year "Year" true true false 0 Short 0 0,First,#,April 1 2023 Prod Indicators,Year,-1,-1;DistributionProjectName "Distribution Project Name" true true false 60 Text 0 0,First,#,April 1 2023 Prod Indicators,DistributionProjectName,0,59;DistributionProjectCode "Distribution Project Code" true true false 10 Text 0 0,First,#,April 1 2023 Prod Indicators,DistributionProjectCode,0,9;SummaryProduct "Summary Product" true true false 10 Text 0 0,First,#,April 1 2023 Prod Indicators,SummaryProduct,0,9;CenterOfGravityLatitude "Center of Gravity Latitude" true true false 0 Double 0 0,First,#,April 1 2023 Prod Indicators,CenterOfGravityLatitude,-1,-1;MinimumLatitude "Minimum Latitude" true true false 0 Double 0 0,First,#,April 1 2023 Prod Indicators,MinimumLatitude,-1,-1;MaximumLatitude "Maximum Latitude" true true false 0 Double 0 0,First,#,April 1 2023 Prod Indicators,MaximumLatitude,-1,-1;OffsetLatitude "Offset Latitude" true true false 0 Double 0 0,First,#,April 1 2023 Prod Indicators,OffsetLatitude,-1,-1;CenterOfGravityLatitudeSE "Center of Gravity Latitude Standard Error" true true false 0 Double 0 0,First,#,April 1 2023 Prod Indicators,CenterOfGravityLatitudeSE,-1,-1;CenterOfGravityLongitude "Center of Gravity Longitude" true true false 0 Double 0 0,First,#,April 1 2023 Prod Indicators,CenterOfGravityLongitude,-1,-1;MinimumLongitude "Minimum Longitude" true true false 0 Double 0 0,First,#,April 1 2023 Prod Indicators,MinimumLongitude,-1,-1;MaximumLongitude "Maximum Longitude" true true false 0 Double 0 0,First,#,April 1 2023 Prod Indicators,MaximumLongitude,-1,-1;OffsetLongitude "Offset Longitude" true true false 0 Double 0 0,First,#,April 1 2023 Prod Indicators,OffsetLongitude,-1,-1;CenterOfGravityLongitudeSE "Center of Gravity Longitude Standard Error" true true false 0 Double 0 0,First,#,April 1 2023 Prod Indicators,CenterOfGravityLongitudeSE,-1,-1;CenterOfGravityDepth "Center of Gravity Depth" true true false 0 Double 0 0,First,#,April 1 2023 Prod Indicators,CenterOfGravityDepth,-1,-1;MinimumDepth "Minimum Depth" true true false 0 Double 0 0,First,#,April 1 2023 Prod Indicators,MinimumDepth,-1,-1;MaximumDepth "Maximum Depth" true true false 0 Double 0 0,First,#,April 1 2023 Prod Indicators,MaximumDepth,-1,-1;OffsetDepth "Offset Depth" true true false 0 Double 0 0,First,#,April 1 2023 Prod Indicators,OffsetDepth,-1,-1;CenterOfGravityDepthSE "Center of Gravity Depth Standard Error" true true false 0 Double 0 0,First,#,April 1 2023 Prod Indicators,CenterOfGravityDepthSE,-1,-1',
##    sort_field=None
##)

        dismap_gdb = rf"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP\April 1 2023\April 1 2023.gdb"

        april_1_2023_indicators = rf"{os.environ['USERPROFILE']}\Documents\ArcGIS\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\DisMAP.gdb\April_1_2023_Indicators"

        # "AI_IDW", "EBS_IDW", "ENBS_IDW", "GMEX_IDW", "GOA_IDW", "HI_IDW", "NBS_IDW", "NEUS_FAL_IDW", "NEUS_SPR_IDW",
        # "SEUS_FAL_IDW", "SEUS_SPR_IDW", "SEUS_SUM_IDW", "WC_GLMME", "WC_GFDL", "WC_ANN_IDW", "WC_TRI_IDW",

        ai_indicators   = rf"{dismap_gdb}\AI_IDW_Indicators"
        ebs_indicators  = rf"{dismap_gdb}\EBS_IDW_Indicators"
        enbs_indicators = rf"{dismap_gdb}\ENBS_IDW_Indicators"
        gmex_indicators = rf"{dismap_gdb}\GMEX_IDW_Indicators"
        goa_indicators  = rf"{dismap_gdb}\GOA_IDW_Indicators"
        hi_indicators   = rf"{dismap_gdb}\HI_IDW_Indicators"
        nbs_indicators  = rf"{dismap_gdb}\NBS_IDW_Indicators"
        neus_fal_nbs_indicators = rf"{dismap_gdb}\NEUS_FAL_IDW_Indicators"
        neus_spr_nbs_indicators = rf"{dismap_gdb}\NEUS_SPR_IDW_Indicators"
        seus_fal_nbs_indicators = rf"{dismap_gdb}\SEUS_FAL_IDW_Indicators"
        seus_spr_nbs_indicators = rf"{dismap_gdb}\SEUS_SPR_IDW_Indicators"
        seus_sum_nbs_indicators = rf"{dismap_gdb}\SEUS_SUM_IDW_Indicators"
        wc_ann_indicators       = rf"{dismap_gdb}\WC_ANN_IDW_Indicators"
        wc_glmme_nbs_indicators = rf"{dismap_gdb}\WC_GLMME_IDW_Indicators"
        wc_gfdl_nbs_indicators  = rf"{dismap_gdb}\WC_GFDL_IDW_Indicators"
        wc_tri_indicators       = rf"{dismap_gdb}\WC_TRI_IDW_Indicators"

        arcpy.management.CalculateField(
                                        in_table        = april_1_2023_indicators,
                                        field           = "ImageName",
                                        expression      = """!DatasetCode! + "_" + !DistributionProjectCode! + "_" + !Species!.replace(' ','_')  + "_" + str(!Year!)""",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "TEXT",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = ai_indicators,
                                        field           = "ImageName",
                                        expression      = """!DatasetCode! + "_" + !DistributionProjectCode! + "_" + !Species!.replace(' ','_')  + "_" + str(!Year!)""",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "TEXT",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = ebs_indicators,
                                        field           = "ImageName",
                                        expression      = """!DatasetCode! + "_" + !DistributionProjectCode! + "_" + !Species!.replace(' ','_')  + "_" + str(!Year!)""",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "TEXT",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = enbs_indicators,
                                        field           = "ImageName",
                                        expression      = """!DatasetCode! + "_" + !DistributionProjectCode! + "_" + !Species!.replace(' ','_')  + "_" + str(!Year!)""",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "TEXT",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = gmex_indicators,
                                        field           = "ImageName",
                                        expression      = """!DatasetCode! + "_" + !DistributionProjectCode! + "_" + !Species!.replace(' ','_')  + "_" + str(!Year!)""",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "TEXT",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = goa_indicators,
                                        field           = "ImageName",
                                        expression      = """!DatasetCode! + "_" + !DistributionProjectCode! + "_" + !Species!.replace(' ','_')  + "_" + str(!Year!)""",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "TEXT",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = hi_indicators,
                                        field           = "ImageName",
                                        expression      = """!DatasetCode! + "_" + !DistributionProjectCode! + "_" + !Species!.replace(' ','_')  + "_" + str(!Year!)""",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "TEXT",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = nbs_indicators,
                                        field           = "ImageName",
                                        expression      = """!DatasetCode! + "_" + !DistributionProjectCode! + "_" + !Species!.replace(' ','_')  + "_" + str(!Year!)""",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "TEXT",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = neus_fal_nbs_indicators,
                                        field           = "ImageName",
                                        expression      = """!DatasetCode! + "_" + !DistributionProjectCode! + "_" + !Species!.replace(' ','_')  + "_" + str(!Year!)""",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "TEXT",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = neus_spr_nbs_indicators,
                                        field           = "ImageName",
                                        expression      = """!DatasetCode! + "_" + !DistributionProjectCode! + "_" + !Species!.replace(' ','_')  + "_" + str(!Year!)""",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "TEXT",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = seus_fal_nbs_indicators,
                                        field           = "ImageName",
                                        expression      = """!DatasetCode! + "_" + !DistributionProjectCode! + "_" + !Species!.replace(' ','_')  + "_" + str(!Year!)""",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "TEXT",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = seus_spr_nbs_indicators,
                                        field           = "ImageName",
                                        expression      = """!DatasetCode! + "_" + !DistributionProjectCode! + "_" + !Species!.replace(' ','_')  + "_" + str(!Year!)""",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "TEXT",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = seus_sum_nbs_indicators,
                                        field           = "ImageName",
                                        expression      = """!DatasetCode! + "_" + !DistributionProjectCode! + "_" + !Species!.replace(' ','_')  + "_" + str(!Year!)""",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "TEXT",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = wc_ann_indicators,
                                        field           = "ImageName",
                                        expression      = """!DatasetCode! + "_" + !DistributionProjectCode! + "_" + !Species!.replace(' ','_')  + "_" + str(!Year!)""",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "TEXT",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

##        arcpy.management.CalculateField(
##                                        in_table        = wc_glmme_nbs_indicators,
##                                        field           = "ImageName",
##                                        expression      = """!DatasetCode! + "_" + !DistributionProjectCode! + "_" + !Species!.replace(' ','_')  + "_" + str(!Year!)""",
##                                        expression_type = "PYTHON3",
##                                        code_block      = "",
##                                        field_type      = "TEXT",
##                                        enforce_domains = "NO_ENFORCE_DOMAINS"
##                                       )
##
##        arcpy.management.CalculateField(
##                                        in_table        = wc_gfdl_nbs_indicators,
##                                        field           = "ImageName",
##                                        expression      = """!DatasetCode! + "_" + !DistributionProjectCode! + "_" + !Species!.replace(' ','_')  + "_" + str(!Year!)""",
##                                        expression_type = "PYTHON3",
##                                        code_block      = "",
##                                        field_type      = "TEXT",
##                                        enforce_domains = "NO_ENFORCE_DOMAINS"
##                                       )

        arcpy.management.CalculateField(
                                        in_table        = wc_tri_indicators,
                                        field           = "ImageName",
                                        expression      = """!DatasetCode! + "_" + !DistributionProjectCode! + "_" + !Species!.replace(' ','_')  + "_" + str(!Year!)""",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "TEXT",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        # ###--->>> ai_indicators
        indicators_joined_table = arcpy.management.AddJoin(
                                                           in_layer_or_view  = april_1_2023_indicators,
                                                           in_field          = "ImageName",
                                                           join_table        = ai_indicators,
                                                           join_field        = "ImageName",
                                                           join_type         = "KEEP_COMMON",
                                                           index_join_fields = "INDEX_JOIN_FIELDS",
                                                           rebuild_index     = "REBUILD_INDEX"
                                                          )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLatDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLatitude! - !AI_IDW_Indicators.CenterOfGravityLatitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLongDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLongitude! - !AI_IDW_Indicators.CenterOfGravityLongitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravDepthDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityDepth! - !AI_IDW_Indicators.CenterOfGravityDepth!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.RemoveJoin(in_layer_or_view = indicators_joined_table)

        del indicators_joined_table
        del ai_indicators
        # ###--->>> ai_indicators

        # ###--->>> ebs_indicators
        indicators_joined_table = arcpy.management.AddJoin(
                                                           in_layer_or_view  = april_1_2023_indicators,
                                                           in_field          = "ImageName",
                                                           join_table        = ebs_indicators,
                                                           join_field        = "ImageName",
                                                           join_type         = "KEEP_COMMON",
                                                           index_join_fields = "INDEX_JOIN_FIELDS",
                                                           rebuild_index     = "REBUILD_INDEX"
                                                          )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLatDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLatitude! - !EBS_IDW_Indicators.CenterOfGravityLatitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLongDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLongitude! - !EBS_IDW_Indicators.CenterOfGravityLongitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravDepthDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityDepth! - !EBS_IDW_Indicators.CenterOfGravityDepth!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.RemoveJoin(in_layer_or_view = indicators_joined_table)

        del indicators_joined_table
        del ebs_indicators
        # ###--->>> ebs_indicators

        # ###--->>> enbs_indicators
        indicators_joined_table = arcpy.management.AddJoin(
                                                           in_layer_or_view  = april_1_2023_indicators,
                                                           in_field          = "ImageName",
                                                           join_table        = enbs_indicators,
                                                           join_field        = "ImageName",
                                                           join_type         = "KEEP_COMMON",
                                                           index_join_fields = "INDEX_JOIN_FIELDS",
                                                           rebuild_index     = "REBUILD_INDEX"
                                                          )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLatDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLatitude! - !ENBS_IDW_Indicators.CenterOfGravityLatitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLongDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLongitude! - !ENBS_IDW_Indicators.CenterOfGravityLongitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravDepthDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityDepth! - !ENBS_IDW_Indicators.CenterOfGravityDepth!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.RemoveJoin(in_layer_or_view = indicators_joined_table)

        del indicators_joined_table
        del enbs_indicators
        # ###--->>> enbs_indicators

       # ###--->>> gmex_indicators
        indicators_joined_table = arcpy.management.AddJoin(
                                                           in_layer_or_view  = april_1_2023_indicators,
                                                           in_field          = "ImageName",
                                                           join_table        = gmex_indicators,
                                                           join_field        = "ImageName",
                                                           join_type         = "KEEP_COMMON",
                                                           index_join_fields = "INDEX_JOIN_FIELDS",
                                                           rebuild_index     = "REBUILD_INDEX"
                                                          )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLatDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLatitude! - !GMEX_IDW_Indicators.CenterOfGravityLatitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLongDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLongitude! - !GMEX_IDW_Indicators.CenterOfGravityLongitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravDepthDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityDepth! - !GMEX_IDW_Indicators.CenterOfGravityDepth!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.RemoveJoin(in_layer_or_view = indicators_joined_table)

        del indicators_joined_table
        del gmex_indicators
        # ###--->>> gmex_indicators

       # ###--->>> goa_indicators
        indicators_joined_table = arcpy.management.AddJoin(
                                                           in_layer_or_view  = april_1_2023_indicators,
                                                           in_field          = "ImageName",
                                                           join_table        = goa_indicators,
                                                           join_field        = "ImageName",
                                                           join_type         = "KEEP_COMMON",
                                                           index_join_fields = "INDEX_JOIN_FIELDS",
                                                           rebuild_index     = "REBUILD_INDEX"
                                                          )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLatDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLatitude! - !GOA_IDW_Indicators.CenterOfGravityLatitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLongDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLongitude! - !GOA_IDW_Indicators.CenterOfGravityLongitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravDepthDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityDepth! - !GOA_IDW_Indicators.CenterOfGravityDepth!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.RemoveJoin(in_layer_or_view = indicators_joined_table)

        del indicators_joined_table
        del goa_indicators
        # ###--->>> goa_indicators

        # ###--->>> hi_indicators
        indicators_joined_table = arcpy.management.AddJoin(
                                                           in_layer_or_view  = april_1_2023_indicators,
                                                           in_field          = "ImageName",
                                                           join_table        = hi_indicators,
                                                           join_field        = "ImageName",
                                                           join_type         = "KEEP_COMMON",
                                                           index_join_fields = "INDEX_JOIN_FIELDS",
                                                           rebuild_index     = "REBUILD_INDEX"
                                                          )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLatDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLatitude! - !HI_IDW_Indicators.CenterOfGravityLatitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLongDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLongitude! - !HI_IDW_Indicators.CenterOfGravityLongitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravDepthDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityDepth! - !HI_IDW_Indicators.CenterOfGravityDepth!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.RemoveJoin(in_layer_or_view = indicators_joined_table)

        del indicators_joined_table
        del hi_indicators
        # ###--->>> hi_indicators

        # ###--->>> nbs_indicators
        indicators_joined_table = arcpy.management.AddJoin(
                                                           in_layer_or_view  = april_1_2023_indicators,
                                                           in_field          = "ImageName",
                                                           join_table        = nbs_indicators,
                                                           join_field        = "ImageName",
                                                           join_type         = "KEEP_COMMON",
                                                           index_join_fields = "INDEX_JOIN_FIELDS",
                                                           rebuild_index     = "REBUILD_INDEX"
                                                          )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLatDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLatitude! - !NBS_IDW_Indicators.CenterOfGravityLatitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLongDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLongitude! - !NBS_IDW_Indicators.CenterOfGravityLongitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravDepthDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityDepth! - !NBS_IDW_Indicators.CenterOfGravityDepth!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.RemoveJoin(in_layer_or_view = indicators_joined_table)

        del indicators_joined_table
        del nbs_indicators
        # ###--->>> nbs_indicators

        # ###--->>> neus_fal_nbs_indicators
        indicators_joined_table = arcpy.management.AddJoin(
                                                           in_layer_or_view  = april_1_2023_indicators,
                                                           in_field          = "ImageName",
                                                           join_table        = neus_fal_nbs_indicators,
                                                           join_field        = "ImageName",
                                                           join_type         = "KEEP_COMMON",
                                                           index_join_fields = "INDEX_JOIN_FIELDS",
                                                           rebuild_index     = "REBUILD_INDEX"
                                                          )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLatDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLatitude! - !NEUS_FAL_IDW_Indicators.CenterOfGravityLatitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLongDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLongitude! - !NEUS_FAL_IDW_Indicators.CenterOfGravityLongitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravDepthDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityDepth! - !NEUS_FAL_IDW_Indicators.CenterOfGravityDepth!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.RemoveJoin(in_layer_or_view = indicators_joined_table)

        del indicators_joined_table
        del neus_fal_nbs_indicators
        # ###--->>> neus_fal_nbs_indicators

        # ###--->>> neus_spr_nbs_indicators
        indicators_joined_table = arcpy.management.AddJoin(
                                                           in_layer_or_view  = april_1_2023_indicators,
                                                           in_field          = "ImageName",
                                                           join_table        = neus_spr_nbs_indicators,
                                                           join_field        = "ImageName",
                                                           join_type         = "KEEP_COMMON",
                                                           index_join_fields = "INDEX_JOIN_FIELDS",
                                                           rebuild_index     = "REBUILD_INDEX"
                                                          )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLatDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLatitude! - !NEUS_SPR_IDW_Indicators.CenterOfGravityLatitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLongDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLongitude! - !NEUS_SPR_IDW_Indicators.CenterOfGravityLongitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravDepthDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityDepth! - !NEUS_SPR_IDW_Indicators.CenterOfGravityDepth!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.RemoveJoin(in_layer_or_view = indicators_joined_table)

        del indicators_joined_table
        del neus_spr_nbs_indicators
        # ###--->>> neus_spr_nbs_indicators

        # ###--->>> seus_fal_nbs_indicators
        indicators_joined_table = arcpy.management.AddJoin(
                                                           in_layer_or_view  = april_1_2023_indicators,
                                                           in_field          = "ImageName",
                                                           join_table        = seus_fal_nbs_indicators,
                                                           join_field        = "ImageName",
                                                           join_type         = "KEEP_COMMON",
                                                           index_join_fields = "INDEX_JOIN_FIELDS",
                                                           rebuild_index     = "REBUILD_INDEX"
                                                          )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLatDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLatitude! - !SEUS_FAL_IDW_Indicators.CenterOfGravityLatitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLongDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLongitude! - !SEUS_FAL_IDW_Indicators.CenterOfGravityLongitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravDepthDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityDepth! - !SEUS_FAL_IDW_Indicators.CenterOfGravityDepth!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.RemoveJoin(in_layer_or_view = indicators_joined_table)

        del indicators_joined_table
        del seus_fal_nbs_indicators
        # ###--->>> seus_fal_nbs_indicators

        # ###--->>> seus_spr_nbs_indicators
        indicators_joined_table = arcpy.management.AddJoin(
                                                           in_layer_or_view  = april_1_2023_indicators,
                                                           in_field          = "ImageName",
                                                           join_table        = seus_spr_nbs_indicators,
                                                           join_field        = "ImageName",
                                                           join_type         = "KEEP_COMMON",
                                                           index_join_fields = "INDEX_JOIN_FIELDS",
                                                           rebuild_index     = "REBUILD_INDEX"
                                                          )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLatDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLatitude! - !SEUS_SPR_IDW_Indicators.CenterOfGravityLatitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLongDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLongitude! - !SEUS_SPR_IDW_Indicators.CenterOfGravityLongitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravDepthDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityDepth! - !SEUS_SPR_IDW_Indicators.CenterOfGravityDepth!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.RemoveJoin(in_layer_or_view = indicators_joined_table)

        del indicators_joined_table
        del seus_spr_nbs_indicators
        # ###--->>> seus_spr_nbs_indicators

        # ###--->>> seus_sum_nbs_indicators
        indicators_joined_table = arcpy.management.AddJoin(
                                                           in_layer_or_view  = april_1_2023_indicators,
                                                           in_field          = "ImageName",
                                                           join_table        = seus_sum_nbs_indicators,
                                                           join_field        = "ImageName",
                                                           join_type         = "KEEP_COMMON",
                                                           index_join_fields = "INDEX_JOIN_FIELDS",
                                                           rebuild_index     = "REBUILD_INDEX"
                                                          )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLatDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLatitude! - !SEUS_SUM_IDW_Indicators.CenterOfGravityLatitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLongDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLongitude! - !SEUS_SUM_IDW_Indicators.CenterOfGravityLongitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravDepthDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityDepth! - !SEUS_SUM_IDW_Indicators.CenterOfGravityDepth!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.RemoveJoin(in_layer_or_view = indicators_joined_table)

        del indicators_joined_table
        del seus_sum_nbs_indicators
        # ###--->>> seus_sum_nbs_indicators

        # ###--->>> wc_ann_indicators
        indicators_joined_table = arcpy.management.AddJoin(
                                                           in_layer_or_view  = april_1_2023_indicators,
                                                           in_field          = "ImageName",
                                                           join_table        = wc_ann_indicators,
                                                           join_field        = "ImageName",
                                                           join_type         = "KEEP_COMMON",
                                                           index_join_fields = "INDEX_JOIN_FIELDS",
                                                           rebuild_index     = "REBUILD_INDEX"
                                                          )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLatDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLatitude! - !WC_ANN_IDW_Indicators.CenterOfGravityLatitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLongDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLongitude! - !WC_ANN_IDW_Indicators.CenterOfGravityLongitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravDepthDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityDepth! - !WC_ANN_IDW_Indicators.CenterOfGravityDepth!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.RemoveJoin(in_layer_or_view = indicators_joined_table)

        del indicators_joined_table
        del wc_ann_indicators
        # ###--->>> wc_ann_indicators

        # ###--->>> wc_tri_indicators
        indicators_joined_table = arcpy.management.AddJoin(
                                                           in_layer_or_view  = april_1_2023_indicators,
                                                           in_field          = "ImageName",
                                                           join_table        = wc_tri_indicators,
                                                           join_field        = "ImageName",
                                                           join_type         = "KEEP_COMMON",
                                                           index_join_fields = "INDEX_JOIN_FIELDS",
                                                           rebuild_index     = "REBUILD_INDEX"
                                                          )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLatDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLatitude! - !WC_TRI_IDW_Indicators.CenterOfGravityLatitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravLongDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityLongitude! - !WC_TRI_IDW_Indicators.CenterOfGravityLongitude!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.CalculateField(
                                        in_table        = indicators_joined_table,
                                        field           = "CentGravDepthDiff",
                                        expression      = "round(!April_1_2023_Indicators.CenterOfGravityDepth! - !WC_TRI_IDW_Indicators.CenterOfGravityDepth!, 6)",
                                        expression_type = "PYTHON3",
                                        code_block      = "",
                                        field_type      = "DOUBLE",
                                        enforce_domains = "NO_ENFORCE_DOMAINS"
                                       )

        arcpy.management.RemoveJoin(in_layer_or_view = indicators_joined_table)

        del indicators_joined_table
        del wc_tri_indicators
        # ###--->>> wc_tri_indicators

        del wc_glmme_nbs_indicators, wc_gfdl_nbs_indicators

        del april_1_2023_indicators

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
            leave_out_keys = ["leave_out_keys", "remaining_keys", "inspect", "dismap_gdb"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys

            return True

        except:
            traceback.print_exc()
    finally:
        try:
            arcpy.AddMessage(f"Compacting {os.path.basename(dismap_gdb)}")
            arcpy.management.Compact(dismap_gdb)
            arcpy.AddMessage("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))

            del dismap_gdb

            pass
            # "results" in locals().keys(): del results
        except UnboundLocalError:
            pass

if __name__ == '__main__':
    try:

        main()

    except SystemExit:
        pass
    except:
        traceback.print_exc()
    else:
        import inspect
        leave_out_keys = ["leave_out_keys", "remaining_keys"]
        leave_out_keys.extend([name for name, obj in inspect.getmembers(sys.modules[__name__]) if inspect.isfunction(obj) or inspect.ismodule(obj)])
        remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
        if remaining_keys:
            arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[1][3]}': ##--> '{', '.join(remaining_keys)}' <--##")
        del leave_out_keys, remaining_keys
    finally:
        pass
