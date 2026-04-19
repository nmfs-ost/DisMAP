"""
Script documentation

- Tool parameters are accessed using arcpy.GetParameter() or
                                     arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or
                                        arcpy.SetParameterAsText()
"""
import arcpy
import os
import traceback
import inspect

def script_tool(project_gdb=""):
    """Script code goes below"""
    try:
        # Imports
        # Use all of the cores on the machine
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.env.overwriteOutput = True

        # Define variables
        project_folder  = os.path.dirname(project_gdb)
        scratch_folder  = rf"{project_folder}\Scratch"
        scratch_gdb     = os.path.join(scratch_folder, "scratch.gdb")

        # Set the workspace environment to local file geodatabase
        arcpy.env.workspace = project_gdb
        # Set the scratchWorkspace environment to local file geodatabase
        arcpy.env.scratchWorkspace = scratch_gdb
        # Clean-up variables
        del scratch_folder, scratch_gdb

        arcpy.AddMessage(f"\n{'--Start' * 10}--\n")
        arcpy.AddMessage(f"Creating Table and Field definitions for: {os.path.basename(project_gdb)}")

        field_definitions = {   "Bio_Inc_Dec": {
                                    "field_aliasName": "Bio_Inc_Dec",
                                    "field_baseName": "Bio_Inc_Dec",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 30,
                                    "field_name": "Bio_Inc_Dec",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Bio_Inc_Dec",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Bio_Inc_Dec"
                                    }
                                },
                                "CSVFile": {
                                    "field_aliasName": "CSV File",
                                    "field_baseName": "CSVFile",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 20,
                                    "field_name": "CSVFile",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "CSV File",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "CSV File"
                                    }
                                },
                                "Category": {
                                    "field_aliasName": "Category",
                                    "field_baseName": "Category",
                                    "field_defaultValue": "null",
                                    "field_domain": "MosaicCatalogItemCategoryDomain",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 4,
                                    "field_name": "Category",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Integer",
                                    "field_attrdef": "Category",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Category"
                                    }
                                },
                                "CellSize": {
                                    "field_aliasName": "Cell Size",
                                    "field_baseName": "CellSize",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 4,
                                    "field_name": "CellSize",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Cell Size",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Cell Size"
                                    }
                                },
                                "CenterOfGravityDepth": {
                                    "field_aliasName": "Center of Gravity Depth",
                                    "field_baseName": "CenterOfGravityDepth",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "CenterOfGravityDepth",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Center of Gravity Depth",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Center of Gravity Depth"
                                    }
                                },
                                "CenterOfGravityDepthSE": {
                                    "field_aliasName": "Center of Gravity Depth Standard Error",
                                    "field_baseName": "CenterOfGravityDepthSE",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "CenterOfGravityDepthSE",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Center of Gravity Depth Standard Error",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Center of Gravity Depth Standard Error"
                                    }
                                },
                                "CenterOfGravityLatitude": {
                                    "field_aliasName": "Center of Gravity Latitude",
                                    "field_baseName": "CenterOfGravityLatitude",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "CenterOfGravityLatitude",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Center of Gravity Latitude",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Center of Gravity Latitude"
                                    }
                                },
                                "CenterOfGravityLatitudeSE": {
                                    "field_aliasName": "Center of Gravity Latitude Standard Error",
                                    "field_baseName": "CenterOfGravityLatitudeSE",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "CenterOfGravityLatitudeSE",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Center of Gravity Latitude Standard Error",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Center of Gravity Latitude Standard Error"
                                    }
                                },
                                "CenterOfGravityLongitude": {
                                    "field_aliasName": "Center of Gravity Longitude",
                                    "field_baseName": "CenterOfGravityLongitude",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "CenterOfGravityLongitude",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Center of Gravity Longitude",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Center of Gravity Longitude"
                                    }
                                },
                                "CenterOfGravityLongitudeSE": {
                                    "field_aliasName": "Center of Gravity Longitude Standard Error",
                                    "field_baseName": "CenterOfGravityLongitudeSE",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "CenterOfGravityLongitudeSE",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Center of Gravity Longitude Standard Error",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Center of Gravity Longitude Standard Error"
                                    }
                                },
                                "CenterX": {
                                    "field_aliasName": "CenterX",
                                    "field_baseName": "CenterX",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "CenterX",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "CenterX",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "CenterX"
                                    }
                                },
                                "CenterY": {
                                    "field_aliasName": "CenterY",
                                    "field_baseName": "CenterY",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "CenterY",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "CenterY",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "CenterY"
                                    }
                                },
                                "CommonName": {
                                    "field_aliasName": "Common Name",
                                    "field_baseName": "CommonName",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 40,
                                    "field_name": "CommonName",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Common Name",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Common Name"
                                    }
                                },
                                "CommonNameSpecies": {
                                    "field_aliasName": "Common Name (Species)",
                                    "field_baseName": "CommonNameSpecies",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 90,
                                    "field_name": "CommonNameSpecies",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Common Name (Species)",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Common Name (Species)"
                                    }
                                },
                                "CoreSpecies": {
                                    "field_aliasName": "Core Species",
                                    "field_baseName": "CoreSpecies",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 5,
                                    "field_name": "CoreSpecies",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Core Species",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Core Species"
                                    }
                                },
                                "Count": {
                                    "field_aliasName": "Count",
                                    "field_baseName": "Count",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "false",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "Count",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Count",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Count"
                                    }
                                },
                                "DataCitation": {
                                    "field_aliasName": "Data Citation",
                                    "field_baseName": "DataCitation",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 255,
                                    "field_name": "DataCitation",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Data Citation",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Data Citation"
                                    }
                                },
                                "DataFilteringNotes": {
                                    "field_aliasName": "Data Filtering Notes",
                                    "field_baseName": "DataFilteringNotes",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 150,
                                    "field_name": "DataFilteringNotes",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Data Filtering Notes",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Data Filtering Notes"
                                    }
                                },
                                "DataSource": {
                                    "field_aliasName": "Data Source",
                                    "field_baseName": "DataSource",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 100,
                                    "field_name": "DataSource",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Data Source",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Data Source"
                                    }
                                },
                                "DatasetCode": {
                                    "field_aliasName": "Dataset Code",
                                    "field_baseName": "DatasetCode",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 50,
                                    "field_name": "DatasetCode",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Dataset Code",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Dataset Code"
                                    }
                                },
                                "DateCode": {
                                    "field_aliasName": "Date Code",
                                    "field_baseName": "DateCode",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 20,
                                    "field_name": "DateCode",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Date Code",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Date Code"
                                    }
                                },
                                "Depth": {
                                    "field_aliasName": "Depth",
                                    "field_baseName": "Depth",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "Depth",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Depth",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Depth"
                                    }
                                },
                                "Dimensions": {
                                    "field_aliasName": "Dimensions",
                                    "field_baseName": "Dimensions",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 10,
                                    "field_name": "Dimensions",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Dimensions",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Dimensions"
                                    }
                                },
                                "DistributionProjectCode": {
                                    "field_aliasName": "Distribution Project Code",
                                    "field_baseName": "DistributionProjectCode",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 10,
                                    "field_name": "DistributionProjectCode",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Distribution Project Code",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Distribution Project Code"
                                    }
                                },
                                "DistributionProjectName": {
                                    "field_aliasName": "Distribution Project Name",
                                    "field_baseName": "DistributionProjectName",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 60,
                                    "field_name": "DistributionProjectName",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Distribution Project Name",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Distribution Project Name"
                                    }
                                },
                                "Easting": {
                                    "field_aliasName": "Easting",
                                    "field_baseName": "Easting",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "Easting",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Easting",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Easting"
                                    }
                                },
                                "FeatureClassName": {
                                    "field_aliasName": "Feature Class Name",
                                    "field_baseName": "FeatureClassName",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 60,
                                    "field_name": "FeatureClassName",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Feature Class Name",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Feature Class Name"
                                    }
                                },
                                "FeatureServiceName": {
                                    "field_aliasName": "Feature Service Name",
                                    "field_baseName": "FeatureServiceName",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 60,
                                    "field_name": "FeatureServiceName",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Feature Service Name",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Feature Service Name"
                                    }
                                },
                                "FeatureServiceTitle": {
                                    "field_aliasName": "Feature Service Title",
                                    "field_baseName": "FeatureServiceTitle",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 80,
                                    "field_name": "FeatureServiceTitle",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Feature Service Title",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Feature Service Title"
                                    }
                                },
                                "FilterRegion": {
                                    "field_aliasName": "Filter Region",
                                    "field_baseName": "FilterRegion",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 25,
                                    "field_name": "FilterRegion",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Filter Region",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Filter Region"
                                    }
                                },
                                "FilterSubRegion": {
                                    "field_aliasName": "Filter Sub-Region",
                                    "field_baseName": "FilterSubRegion",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 40,
                                    "field_name": "FilterSubRegion",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Filter Sub-Region",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Filter Sub-Region"
                                    }
                                },
                                "Frequency": {
                                    "field_aliasName": "Frequency",
                                    "field_baseName": "Frequency",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 25,
                                    "field_name": "Frequency",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Frequency",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Frequency"
                                    }
                                },
                                "GearType": {
                                    "field_aliasName": "Gear Type",
                                    "field_baseName": "GearType",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 150,
                                    "field_name": "GearType",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Gear Type",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Gear Type"
                                    }
                                },
                                "GeographicArea": {
                                    "field_aliasName": "Geographic Area",
                                    "field_baseName": "GeographicArea",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 20,
                                    "field_name": "GeographicArea",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Geographic Area",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Geographic Area"
                                    }
                                },
                                "GroupName": {
                                    "field_aliasName": "Group Name",
                                    "field_baseName": "GroupName",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 100,
                                    "field_name": "GroupName",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Group Name",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Group Name"
                                    }
                                },
                                "HaulBin": {
                                    "field_aliasName": "Haul Bin",
                                    "field_baseName": "HaulBin",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 20,
                                    "field_name": "HaulBin",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Haul Bin",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Haul Bin"
                                    }
                                },
                                "Haul_Inc_Dec": {
                                    "field_aliasName": "Haul_Inc_Dec",
                                    "field_baseName": "Haul_Inc_Dec",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 30,
                                    "field_name": "Haul_Inc_Dec",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Haul_Inc_Dec",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Haul_Inc_Dec"
                                    }
                                },
                                "HaulProportion": {
                                    "field_aliasName": "Haul Proportion",
                                    "field_baseName": "HaulProportion",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "HaulProportion",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Haul Proportion",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Haul Proportion"
                                    }
                                },




                                "HighPS": {
                                    "field_aliasName": "HighPS",
                                    "field_baseName": "HighPS",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "HighPS",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "HighPS",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "HighPS"
                                    }
                                },
                                "ID": {
                                    "field_aliasName": "ID",
                                    "field_baseName": "ID",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 2,
                                    "field_name": "ID",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "ID",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "ID"
                                    }
                                },
                                "ImageName": {
                                    "field_aliasName": "Image Name",
                                    "field_baseName": "ImageName",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 100,
                                    "field_name": "ImageName",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Image Name",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Image Name"
                                    }
                                },
                                "ImageServiceName": {
                                    "field_aliasName": "Image Service Name",
                                    "field_baseName": "ImageServiceName",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 40,
                                    "field_name": "ImageServiceName",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Image Service Name",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Image Service Name"
                                    }
                                },
                                "ImageServiceTitle": {
                                    "field_aliasName": "Image Service Title",
                                    "field_baseName": "ImageServiceTitle",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 60,
                                    "field_name": "ImageServiceTitle",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Image Service Title",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Image Service Title"
                                    }
                                },
                                "ItemTS": {
                                    "field_aliasName": "ItemTS",
                                    "field_baseName": "ItemTS",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "ItemTS",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "ItemTS",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "ItemTS"
                                    }
                                },
                                "Latitude": {
                                    "field_aliasName": "Latitude",
                                    "field_baseName": "Latitude",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "Latitude",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Latitude",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Latitude"
                                    }
                                },
                                "Longitude": {
                                    "field_aliasName": "Longitude",
                                    "field_baseName": "Longitude",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "Longitude",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Longitude",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Longitude"
                                    }
                                },
                                "LowPS": {
                                    "field_aliasName": "LowPS",
                                    "field_baseName": "LowPS",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "LowPS",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "LowPS",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "LowPS"
                                    }
                                },
                                "ManagementBody": {
                                    "field_aliasName": "Management Body",
                                    "field_baseName": "ManagementBody",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 20,
                                    "field_name": "ManagementBody",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Management Body",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Management Body"
                                    }
                                },
                                "ManagementPlan": {
                                    "field_aliasName": "Management Plan",
                                    "field_baseName": "ManagementPlan",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 90,
                                    "field_name": "ManagementPlan",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Management Plan",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Management Plan"
                                    }
                                },
                                "MapValue": {
                                    "field_aliasName": "Map Value",
                                    "field_baseName": "MapValue",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "MapValue",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Map Value",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Map Value"
                                    }
                                },
                                "MaxPS": {
                                    "field_aliasName": "MaxPS",
                                    "field_baseName": "MaxPS",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "MaxPS",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "MaxPS",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "MaxPS"
                                    }
                                },
                                "MaximumDepth": {
                                    "field_aliasName": "Maximum Depth",
                                    "field_baseName": "MaximumDepth",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "MaximumDepth",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Maximum Depth",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Maximum Depth"
                                    }
                                },
                                "MaximumLatitude": {
                                    "field_aliasName": "Maximum Latitude",
                                    "field_baseName": "MaximumLatitude",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "MaximumLatitude",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Maximum Latitude",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Maximum Latitude"
                                    }
                                },
                                "MaximumLongitude": {
                                    "field_aliasName": "Maximum Longitude",
                                    "field_baseName": "MaximumLongitude",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "MaximumLongitude",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Maximum Longitude",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Maximum Longitude"
                                    }
                                },
                                "MedianEstimate": {
                                    "field_aliasName": "Median Estimate",
                                    "field_baseName": "MedianEstimate",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "MedianEstimate",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Median Estimate",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Median Estimate"
                                    }
                                },
                                "MinPS": {
                                    "field_aliasName": "MinPS",
                                    "field_baseName": "MinPS",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "MinPS",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "MinPS",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "MinPS"
                                    }
                                },
                                "MinimumDepth": {
                                    "field_aliasName": "Minimum Depth",
                                    "field_baseName": "MinimumDepth",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "MinimumDepth",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Minimum Depth",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Minimum Depth"
                                    }
                                },
                                "MinimumLatitude": {
                                    "field_aliasName": "Minimum Latitude",
                                    "field_baseName": "MinimumLatitude",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "MinimumLatitude",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Minimum Latitude",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Minimum Latitude"
                                    }
                                },
                                "MinimumLongitude": {
                                    "field_aliasName": "Minimum Longitude",
                                    "field_baseName": "MinimumLongitude",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "MinimumLongitude",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Minimum Longitude",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Minimum Longitude"
                                    }
                                },
                                "MosaicName": {
                                    "field_aliasName": "Mosaic Name",
                                    "field_baseName": "MosaicName",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 20,
                                    "field_name": "MosaicName",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Mosaic Name",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Mosaic Name"
                                    }
                                },
                                "MosaicTitle": {
                                    "field_aliasName": "Mosaic Title",
                                    "field_baseName": "MosaicTitle",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 60,
                                    "field_name": "MosaicTitle",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Mosaic Title",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Mosaic Title"
                                    }
                                },
                                "Name": {
                                    "field_aliasName": "Name",
                                    "field_baseName": "Name",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 200,
                                    "field_name": "Name",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Name",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Name"
                                    }
                                },
                                "NetWTCPUE": {
                                    "field_aliasName": "Net WTCPUE",
                                    "field_baseName": "NetWTCPUE",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "NetWTCPUE",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Net WTCPUE",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Net WTCPUE"
                                    }
                                },
                                "Northing": {
                                    "field_aliasName": "Northing",
                                    "field_baseName": "Northing",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "Northing",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Northing",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Northing"
                                    }
                                },
                                "Notes": {
                                    "field_aliasName": "Notes",
                                    "field_baseName": "Notes",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 40,
                                    "field_name": "Notes",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Notes",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Notes"
                                    }
                                },
                                "OffsetDepth": {
                                    "field_aliasName": "Offset Depth",
                                    "field_baseName": "OffsetDepth",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "OffsetDepth",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Offset Depth",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Offset Depth"
                                    }
                                },
                                "OffsetLatitude": {
                                    "field_aliasName": "Offset Latitude",
                                    "field_baseName": "OffsetLatitude",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "OffsetLatitude",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Offset Latitude",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Offset Latitude"
                                    }
                                },
                                "OffsetLongitude": {
                                    "field_aliasName": "Offset Longitude",
                                    "field_baseName": "OffsetLongitude",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "OffsetLongitude",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Offset Longitude",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Offset Longitude"
                                    }
                                },
                                "Percentile": {
                                    "field_aliasName": "Percentile",
                                    "field_baseName": "Percentile",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "Percentile",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Percentile",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Percentile"
                                    }
                                },
                                "PercentileBin": {
                                    "field_aliasName": "Percentile Bin",
                                    "field_baseName": "PercentileBin",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 20,
                                    "field_name": "PercentileBin",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Percentile Bin",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Percentile Bin"
                                    }
                                },
                                "PointFeatureType": {
                                    "field_aliasName": "Point Feature Type",
                                    "field_baseName": "PointFeatureType",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 20,
                                    "field_name": "PointFeatureType",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Point Feature Type",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Point Feature Type"
                                    }
                                },
                                "ProductName": {
                                    "field_aliasName": "Product Name",
                                    "field_baseName": "ProductName",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 100,
                                    "field_name": "ProductName",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Product Name",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Product Name"
                                    }
                                },
                                "Raster": {
                                    "field_aliasName": "Raster",
                                    "field_baseName": "Raster",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 0,
                                    "field_name": "Raster",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Raster",
                                    "field_attrdef": "Raster",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Raster"
                                    }
                                },
                                "Region": {
                                    "field_aliasName": "Region",
                                    "field_baseName": "Region",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 40,
                                    "field_name": "Region",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Region",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Region"
                                    }
                                },
                                "SampleID": {
                                    "field_aliasName": "Sample ID",
                                    "field_baseName": "SampleID",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 20,
                                    "field_name": "SampleID",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Sample ID",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Sample ID"
                                    }
                                },
                                "Season": {
                                    "field_aliasName": "Season",
                                    "field_baseName": "Season",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 15,
                                    "field_name": "Season",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Season",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Season"
                                    }
                                },
                                "Species": {
                                    "field_aliasName": "Species",
                                    "field_baseName": "Species",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 50,
                                    "field_name": "Species",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Species",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Species"
                                    }
                                },
                                "SpeciesCommonName": {
                                    "field_aliasName": "Species (Common Name)",
                                    "field_baseName": "SpeciesCommonName",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 90,
                                    "field_name": "SpeciesCommonName",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Species (Common Name)",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Species (Common Name)"
                                    }
                                },
                                "StandardError": {
                                    "field_aliasName": "Standard Error",
                                    "field_baseName": "StandardError",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "StandardError",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Standard Error",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Standard Error"
                                    }
                                },
                                "Status": {
                                    "field_aliasName": "Status",
                                    "field_baseName": "Status",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 10,
                                    "field_name": "Status",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Status",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Status"
                                    }
                                },
                                "StdTime": {
                                    "field_aliasName": "StdTime",
                                    "field_baseName": "StdTime",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "StdTime",
                                    "field_precision": 1,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Date",
                                    "field_attrdef": "StdTime",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "StdTime"
                                    }
                                },
                                "Stratum": {
                                    "field_aliasName": "Stratum",
                                    "field_baseName": "Stratum",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 20,
                                    "field_name": "Stratum",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Stratum",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Stratum"
                                    }
                                },
                                "StratumArea": {
                                    "field_aliasName": "Stratum Area",
                                    "field_baseName": "StratumArea",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "StratumArea",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "Stratum Area",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Stratum Area"
                                    }
                                },
                                "SummaryProduct": {
                                    "field_aliasName": "Summary Product",
                                    "field_baseName": "SummaryProduct",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 5,
                                    "field_name": "SummaryProduct",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Summary Product",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Summary Product"
                                    }
                                },
                                "SurveyName": {
                                    "field_aliasName": "Survey Name",
                                    "field_baseName": "SurveyName",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 100,
                                    "field_name": "SurveyName",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Survey Name",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Survey Name"
                                    }
                                },
                                "TableName": {
                                    "field_aliasName": "Table Name",
                                    "field_baseName": "TableName",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 50,
                                    "field_name": "TableName",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Table Name",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Table Name"
                                    }
                                },
                                "Tag": {
                                    "field_aliasName": "Tag",
                                    "field_baseName": "Tag",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 100,
                                    "field_name": "Tag",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Tag",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Tag"
                                    }
                                },
                                "TaxonomicGroup": {
                                    "field_aliasName": "Taxonomic Group",
                                    "field_baseName": "TaxonomicGroup",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 80,
                                    "field_name": "TaxonomicGroup",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Taxonomic Group",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Taxonomic Group"
                                    }
                                },
                                "TotalSpeciesCount": {
                                    "field_aliasName": "Total Species Count",
                                    "field_baseName": "TotalSpeciesCount",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 4,
                                    "field_name": "TotalSpeciesCount",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Total Species Count",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Total Species Count"
                                    }
                                },
                                "TransformUnit": {
                                    "field_aliasName": "Transform Unit",
                                    "field_baseName": "TransformUnit",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 20,
                                    "field_name": "TransformUnit",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Transform Unit",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Transform Unit"
                                    }
                                },
                                "TrendCategory": {
                                    "field_aliasName": "Trend Category",
                                    "field_baseName": "TrendCategory",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 40,
                                    "field_name": "TrendCategory",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Trend Category",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Trend Category"
                                    }
                                },
                                "TypeID": {
                                    "field_aliasName": "Raster Type ID",
                                    "field_baseName": "TypeID",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 4,
                                    "field_name": "TypeID",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Integer",
                                    "field_attrdef": "Raster Type ID",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Raster Type ID"
                                    }
                                },
                                "Uri": {
                                    "field_aliasName": "Uri",
                                    "field_baseName": "Uri",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 0,
                                    "field_name": "Uri",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Blob",
                                    "field_attrdef": "Uri",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Uri"
                                    }
                                },
                                "UriHash": {
                                    "field_aliasName": "UriHash",
                                    "field_baseName": "UriHash",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 50,
                                    "field_name": "UriHash",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "UriHash",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "UriHash"
                                    }
                                },
                                "Value": {
                                    "field_aliasName": "Value",
                                    "field_baseName": "Value",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 50,
                                    "field_name": "Value",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Value",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Value"
                                    }
                                },
                                "Variable": {
                                    "field_aliasName": "Variable",
                                    "field_baseName": "Variable",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 50,
                                    "field_name": "Variable",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Variable",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Variable"
                                    }
                                },
                                "WTCPUE": {
                                    "field_aliasName": "WTCPUE",
                                    "field_baseName": "WTCPUE",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 8,
                                    "field_name": "WTCPUE",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Double",
                                    "field_attrdef": "WTCPUE",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "WTCPUE"
                                    }
                                },
                                "Year": {
                                    "field_aliasName": "Year",
                                    "field_baseName": "Year",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 4,
                                    "field_name": "Year",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "String",
                                    "field_attrdef": "Year",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Year"
                                    }
                                },
                                "Years": {
                                    "field_aliasName": "Years",
                                    "field_baseName": "Years",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 25,
                                    "field_name": "Years",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    #"field_type": "String",
                                    "field_type": "Integer",
                                    "field_attrdef": "Years",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "Years"
                                    }
                                },
                                "ZOrder": {
                                    "field_aliasName": "ZOrder",
                                    "field_baseName": "ZOrder",
                                    "field_defaultValue": "null",
                                    "field_domain": "",
                                    "field_editable": "true",
                                    "field_isNullable": "true",
                                    "field_length": 4,
                                    "field_name": "ZOrder",
                                    "field_precision": 0,
                                    "field_required": "true",
                                    "field_scale": 0,
                                    "field_type": "Integer",
                                    "field_attrdef": "ZOrder",
                                    "field_attrdefs": "DisMAP Project GDB Data Dictionary",
                                    "field_attrdomv": {
                                        "udom": "ZOrder"
                                    }
                                }
                            }

        _Bathymetry = []
        _Boundary   = ["DatasetCode", "Region", "Season", "DistributionProjectCode"]
        _Datasets = ["DatasetCode", "CSVFile", "TransformUnit", "TableName",
                     "GeographicArea", "CellSize", "PointFeatureType", "FeatureClassName",
                     "Region", "Season", "DateCode", "Status", "DistributionProjectCode",
                     "DistributionProjectName", "SummaryProduct", "FilterRegion",
                     "FilterSubRegion", "FeatureServiceName", "FeatureServiceTitle",
                     "MosaicName", "MosaicTitle", "ImageServiceName",
                     "ImageServiceTitle"]
        _DisMAP_Survey_Info = ["SurveyName", "Region", "Season", "GearType",
                               "Years", "Frequency", "DataFilteringNotes",
                               "TotalSpeciesCount", "DataSource", "DataCitation"]
        _Extent_Points = ["Easting", "Northing", "Longitude", "Latitude"]
        _Fishnet       = []
        #_GLMME = ["DatasetCode", "Region", "SummaryProduct", "Year", "StdTime",
        #        "Species", "WTCPUE", "MapValue", "StandardError", "TransformUnit",
        #        "CommonName", "SpeciesCommonName", "CommonNameSpecies", "Easting",
        #        "Northing", "Latitude", "Longitude", "MedianEstimate", "Depth"]
        #_GRID_Points = ["DatasetCode", "Region", "SummaryProduct", "Year",
        #                "StdTime", "Species", "WTCPUE", "MapValue", "StandardError",
        #                "TransformUnit", "CommonName", "SpeciesCommonName",
        #                "CommonNameSpecies", "Easting", "Northing", "Latitude",
        #                "Longitude", "MedianEstimate", "Depth"]
        _IDW = ["DatasetCode", "Region", "Season", "DistributionProjectName",
                "SummaryProduct", "SampleID", "Year", "StdTime", "Species",
                "WTCPUE", "MapValue", "TransformUnit", "CommonName",
                "SpeciesCommonName", "CommonNameSpecies", "CoreSpecies",
                "Stratum", "StratumArea", "Latitude", "Longitude", "Depth"]
        _Indicators = ["DatasetCode", "Region", "Season", "DateCode", "Species",
                       "CommonName", "CoreSpecies", "Year", "DistributionProjectName",
                       "DistributionProjectCode", "SummaryProduct",
                       "CenterOfGravityLatitude", "MinimumLatitude",
                       "MaximumLatitude", "OffsetLatitude", "CenterOfGravityLatitudeSE",
                       "CenterOfGravityLongitude", "MinimumLongitude",
                       "MaximumLongitude", "OffsetLongitude", "CenterOfGravityLongitudeSE",
                       "CenterOfGravityDepth", "MinimumDepth", "MaximumDepth",
                       "OffsetDepth", "CenterOfGravityDepthSE"]
        _LayerSpeciesYearImageName = ["DatasetCode", "Region", "Season", "SummaryProduct",
                                      "FilterRegion", "FilterSubRegion", "Species",
                                      "CommonName", "SpeciesCommonName",
                                      "CommonNameSpecies", "TaxonomicGroup",
                                      "ManagementBody", "ManagementPlan",
                                      "DistributionProjectName", "CoreSpecies",
                                      "Year", "StdTime", "Variable",
                                      "Value", "Dimensions", "ImageName"]
        _Lat_Long  = ["Easting", "Northing", "Longitude", "Latitude"]
        _Latitude  = []
        _Longitude = []
        _Mosaic    = ["Raster", "Name", "MinPS", "MaxPS", "LowPS", "HighPS",
                      "Category", "Tag", "GroupName", "ProductName", "CenterX",
                      "CenterY", "ZOrder", "TypeID", "ItemTS", "UriHash", "Uri",
                      "DatasetCode", "Region", "Season", "Species", "CommonName",
                      "SpeciesCommonName", "CoreSpecies", "Year", "StdTime",
                      "Variable", "Value", "Dimensions"]
        _Raster_Mask = ["Value", "Count", "ID"]
        _Region      = ["DatasetCode", "Region", "Season", "DistributionProjectCode"]
        _Sample_Locations = ["DatasetCode", "Region", "Season", "SummaryProduct",
                             "SampleID", "Year", "StdTime", "Species", "WTCPUE",
                             "MapValue", "TransformUnit", "CommonName",
                             "SpeciesCommonName", "CommonNameSpecies", "CoreSpecies",
                             "Stratum", "StratumArea", "Latitude", "Longitude",
                             "Depth"]
        _Species_Filter = ["Species", "CommonName", "TaxonomicGroup", "FilterRegion",
                           "FilterSubRegion", "ManagementBody", "ManagementPlan", "DistributionProjectName"]
        _SpeciesPersistenceIndicatorTrend = ["Region", "SurveyName", "Species", "CommonName", "TrendCategory", "Notes", "Haul_Inc_Dec", "Bio_Inc_Dec"]
        _SpeciesPersistenceIndicatorPercentileBin = ["Region", "SurveyName", "Year", "Species", "CommonName", "PercentileBin", "WTCPUE", "HaulProportion", "HaulBin"]


        #datasets_table = arcpy.ListTables("Datasets")[0]
        #datasets_table_fields = [f.name for f in arcpy.ListFields(datasets_table) if f.type not in ["Geometry", "OID"] and f.name not in ["Shape_Area", "Shape_Length"]]

        data_dictionary = dict()
        #arcpy.AddMessage(datasets_table_fields)
        #['DatasetCode', 'CSVFile', 'TransformUnit', 'TableName',
        # 'GeographicArea', 'CellSize', 'PointFeatureType', 'FeatureClassName',
        # 'Region', 'Season', 'DateCode', 'Status', 'DistributionProjectCode',
        # 'DistributionProjectName', 'SummaryProduct', 'FilterRegion',
        # 'FilterSubRegion', 'FeatureServiceName', 'FeatureServiceTitle',
        # 'MosaicName', 'MosaicTitle', 'ImageServiceName', 'ImageServiceTitle']

        table_names = ["AI_IDW", "EBS_IDW", "ENBS_IDW", "GMEX_IDW", "GOA_IDW",
                       "HI_IDW", "NBS_IDW", "NEUS_FAL_IDW", "NEUS_SPR_IDW",
                       "SEUS_FAL_IDW", "SEUS_SPR_IDW", "SEUS_SUM_IDW",
                       "WC_ANN_IDW", "WC_TRI_IDW", "DisMAP_Regions", "Datasets",
                       "LayerSpeciesYearImageName", "Indicators", "Species_Filter",
                       "DisMAP_Survey_Info", "SpeciesPersistenceIndicatorTrend",
                       "SpeciesPersistenceIndicatorPercentileBin",]

        for table_name in table_names:
            arcpy.AddMessage(table_name)
            if table_name == "DisMAP_Regions":
                data_dictionary[table_name] = _Region
            elif table_name == "Datasets":
                data_dictionary[table_name] = _Datasets
            elif table_name == "LayerSpeciesYearImageName":
                data_dictionary[table_name] = _LayerSpeciesYearImageName
            elif table_name == "Indicators":
                data_dictionary[table_name] = _Indicators
            elif table_name == "Species_Filter":
                data_dictionary[table_name] = _Species_Filter
            elif table_name == "DisMAP_Survey_Info":
                data_dictionary[table_name] = _DisMAP_Survey_Info
            elif table_name == "SpeciesPersistenceIndicatorPercentileBin":
                data_dictionary[table_name] = _SpeciesPersistenceIndicatorPercentileBin
            elif table_name == "SpeciesPersistenceIndicatorTrend":
                data_dictionary[table_name] = _SpeciesPersistenceIndicatorTrend
            elif table_name.endswith("_IDW"): # or table_name.endswith("_GLMME"):
                if table_name.endswith("_IDW"):
                    data_dictionary[table_name] = _IDW
                    data_dictionary[f"{table_name}_Sample_Locations"] = _Sample_Locations
                    data_dictionary[f"{table_name}_Indicators"] = _Indicators
                #elif table_name.endswith("_GLMME"):
                #    data_dictionary[table_name] = _GLMME
                #    data_dictionary[f"{table_name}_GRID_Points"] = _GRID_Points
                else:
                    pass
                data_dictionary[f"{table_name}_Bathymetry"] = _Bathymetry
                data_dictionary[f"{table_name}_Boundary"] = _Boundary
                data_dictionary[f"{table_name}_Extent_Points"] = _Extent_Points
                data_dictionary[f"{table_name}_Fishnet"] = _Fishnet
                data_dictionary[f"{table_name}_LayerSpeciesYearImageName"] = _LayerSpeciesYearImageName
                data_dictionary[f"{table_name}_Lat_Long"] = _Lat_Long
                data_dictionary[f"{table_name}_Latitude"] = _Latitude
                data_dictionary[f"{table_name}_Longitude"] = _Longitude
                data_dictionary[f"{table_name}_Mosaic"] = _Mosaic
                data_dictionary[f"{table_name}_Raster_Mask"] = _Raster_Mask
                data_dictionary[f"{table_name}_Region"] = _Region
            else:
                pass
            del table_name

##        fields = ['DatasetCode', 'DistributionProjectCode']

##        with arcpy.da.SearchCursor(datasets_table, fields) as cursor:
##            for row in cursor:
##                DatasetCode = f'{row[0]}'
##                DistributionProjectCode = f'{"_"+row[1] if row[1] is not None and row[1] not in row[0] else ""}'
##                table_name = f'{DatasetCode}{DistributionProjectCode}'
##                arcpy.AddMessage(table_name)
##                if table_name == "DisMAP_Regions":
##                    data_dictionary[table_name] = _Region
##                elif table_name == "Datasets":
##                    data_dictionary[table_name] = _Datasets
##                elif table_name == "LayerSpeciesYearImageName":
##                    data_dictionary[table_name] = _LayerSpeciesYearImageName
##                elif table_name == "Indicators":
##                    data_dictionary[table_name] = _Indicators
##                elif table_name == "Species_Filter":
##                    data_dictionary[table_name] = _Species_Filter
##                elif table_name == "DisMAP_Survey_Info":
##                    data_dictionary[table_name] = _DisMAP_Survey_Info
##                elif table_name == "SpeciesPersistenceIndicatorPercentileBin":
##                    data_dictionary[table_name] = _SpeciesPersistenceIndicatorPercentileBin
##                elif table_name == "SpeciesPersistenceIndicatorTrend":
##                    data_dictionary[table_name] = _SpeciesPersistenceIndicatorTrend
##                elif table_name.endswith("_IDW") or table_name.endswith("_GLMME"):
##                    if table_name.endswith("_IDW"):
##                        data_dictionary[table_name] = _IDW
##                        data_dictionary[f"{table_name}_Sample_Locations"] = _Sample_Locations
##                        data_dictionary[f"{table_name}_Indicators"] = _Indicators
##                    elif table_name.endswith("_GLMME"):
##                        data_dictionary[table_name] = _GLMME
##                        data_dictionary[f"{table_name}_GRID_Points"] = _GRID_Points
##                    else:
##                        pass
##                    data_dictionary[f"{table_name}_Bathymetry"] = _Bathymetry
##                    data_dictionary[f"{table_name}_Boundary"] = _Boundary
##                    data_dictionary[f"{table_name}_Extent_Points"] = _Extent_Points
##                    data_dictionary[f"{table_name}_Fishnet"] = _Fishnet
##                    data_dictionary[f"{table_name}_LayerSpeciesYearImageName"] = _LayerSpeciesYearImageName
##                    data_dictionary[f"{table_name}_Lat_Long"] = _Lat_Long
##                    data_dictionary[f"{table_name}_Latitude"] = _Latitude
##                    data_dictionary[f"{table_name}_Longitude"] = _Longitude
##                    data_dictionary[f"{table_name}_Mosaic"] = _Mosaic
##                    data_dictionary[f"{table_name}_Raster_Mask"] = _Raster_Mask
##                    data_dictionary[f"{table_name}_Region"] = _Region
##                else:
##                    pass
##                del DistributionProjectCode
##                del DatasetCode
##                del table_name
##                del row
##        del cursor

        for key in sorted(data_dictionary):
            arcpy.AddMessage(f"Table: {key}")
            _fields = data_dictionary[key]
            for _field in _fields:
                arcpy.AddMessage(f"\t{_field}")
                del _field
            del _fields
            del key

        table_definitions = {k:v for k,v in sorted(data_dictionary.items())}
        import json
        # Write to File
        json_path = rf"{project_folder}\CSV_Data\table_definitions.json"
        #print(f"project folder: {project_folder}")
        with open(json_path, 'w') as json_file:
            json.dump(table_definitions, json_file, indent=4)
        del json_file
        del json_path
        del json

        for table in table_definitions:
            #arcpy.AddMessage(f"{table}")
            fields = table_definitions[table]
            #arcpy.AddMessage(f"\t{type(fields)}")
            del table
            for field in fields:
                #arcpy.AddMessage(f"\t{field}")
                if field in field_definitions.keys():
                    pass
                    #arcpy.AddMessage(f"\t{field_definitions[field]}")
                else:
                    pass
                    #arcpy.AddMessage(f"\t\t###--->>> {field} not in _field_definitions")
                del field
            del fields
        del table_definitions

        #for key in sorted(field_definitions):
        #    #arcpy.AddMessage(f"Table: {key}")
        #    _fields = field_definitions[key]
        #    if "attrdef" not in _fields:
        #         field_definitions[key]["field_attrdef"] = field_definitions[key]["field_aliasName"]
        #    if "attrdefs" not in _fields:
        #        field_definitions[key]["field_attrdefs"] = "DisMAP Project GDB Data Dictionary"
        #    if "attrdomv" not in _fields:
        #        field_definitions[key]["field_attrdomv"] = {"udom": f"{field_definitions[key]['field_aliasName']}"}
        #    else:
        #        pass
        #    del _fields
        #    del key

        #for key in sorted(field_definitions):
        #    #arcpy.AddMessage(f"Table: {key}")
        #    _fields = field_definitions[key]
        #    for _field in _fields:
        #        #arcpy.AddMessage(f"\t{_field}")
        #        del _field
        #    del _fields
        #    del key

        import json
        # Write to File
        json_path = rf"{project_folder}\CSV_Data\field_definitions.json"
        with open(json_path, 'w') as json_file:
            json.dump(field_definitions, json_file, indent=4)
        del json_file
        del json_path
        del json

        del field_definitions
        del data_dictionary, table_names
        del _Bathymetry, _Boundary, _Datasets, _DisMAP_Survey_Info,
        del _Extent_Points, _Fishnet, _IDW, _Indicators,
        #del _GLMME, _GRID_Points,
        del _LayerSpeciesYearImageName, _Lat_Long, _Latitude, _Longitude,
        del _Mosaic, _Raster_Mask, _Region, _Sample_Locations, _Species_Filter
        del _SpeciesPersistenceIndicatorPercentileBin
        del _SpeciesPersistenceIndicatorTrend

        # Compact GDB
        #arcpy.AddMessage(f"\nCompacting: {os.path.basename(project_gdb)}" )
        arcpy.management.Compact(project_gdb)

        arcpy.AddMessage(f"\n{'--End' * 10}--")

        # Declared Variables
        del project_folder
        # Imports
        # Function parameters
        del project_gdb

    except arcpy.ExecuteWarning:
        arcpy.AddWarning(f"Caught an arcpy.ExecuteWarning error in the '{inspect.stack()[0][3]}' function.")
        arcpy.AddWarning(arcpy.GetMessages(1))
    except arcpy.ExecuteError:
        arcpy.AddError(f"Caught an arcpy.ExecuteError error in the '{inspect.stack()[0][3]}' function.")
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()

    except SystemExit as se:
        arcpy.AddError(f"Caught an SystemExit error: {se} in the '{inspect.stack()[0][3]}' function.")
    except Exception as e:
        arcpy.AddError(f"Caught an Exception error: {e} in the '{inspect.stack()[0][3]}' function.")
        traceback.print_exc()
    except:  # noqa: E722
        arcpy.AddError(f"Caught an except error in the '{inspect.stack()[0][3]}' function.")
        traceback.print_exc()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk:
            arcpy.AddMessage(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function at line number {inspect.stack()[0][2]}\n\t##--> '{', '.join(rk)}' <--##")
        del rk
        return True
    finally:
        pass

if __name__ == "__main__":
    try:

       project_gdb = arcpy.GetParameterAsText(0)
       if not project_gdb:
           project_gdb = rf"{os.path.expanduser('~')}\Documents\ArcGIS\Projects\DisMAP\ArcGIS-Analysis-Python\February 1 2026\February 1 2026.gdb"
       else:
           pass

       script_tool(project_gdb)
       arcpy.SetParameterAsText(1, "Result")

       del project_gdb

    except SystemExit:
        pass
    except:  # noqa: E722
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
    else:
        pass
    finally:
        pass






