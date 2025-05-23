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
    return f"Script: {os.path.basename(i.filename)}\n\tNear Line: {i.lineno}\n\tFunction: {i.function}\n\tMessage: {msg}"

def add_fields(csv_data_folder="", in_table=""):
    try:
        # Import this Python module
        import dismap
        importlib.reload(dismap)

        table       = os.path.basename(in_table)
        project_gdb = os.path.dirname(in_table)

        field_definitions = dismap.field_definitions(csv_data_folder, "")
        table_definitions = dismap.table_definitions(csv_data_folder, "")
        del csv_data_folder

        # set workspace environment
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.env.workspace                = project_gdb
        arcpy.env.scratchWorkspace         = rf"Scratch\scratch.gdb"
        arcpy.SetLogMetadata(True)

        if "_IDW_Region" in table:
            table = "IDW_Data"
        elif "GFDL_Region" in table:
            table = "GFDL_Data"
        elif "GLMME_Region" in table:
            table = "GLMME_Data"
        elif "Indicators" in table:
            table = "Indicators"
        else:
            table = table

        fields = table_definitions[table]
        del table_definitions

        field_definition_list = []
        for field in fields:
            field_definition_list.append([
                                          field_definitions[field]["field_name"],
                                          field_definitions[field]["field_type"],
                                          field_definitions[field]["field_alias"],
                                          field_definitions[field]["field_length"],
                                        ])
            del field
        del field_definitions

        arcpy.AddMessage(f"Adding Fields to Table: {table}")
        # arcpy.AddMessage(in_table)
        # arcpy.AddMessage(field_definition_list)
        arcpy.management.AddFields(in_table=in_table, field_description=field_definition_list, template="")
        arcpy.AddMessage("\t{0}\n".format(arcpy.GetMessages().replace("\n", "\n\t")))

        del fields, field_definition_list
        del project_gdb, table

        # Imports
        del dismap
        # Function parameters
        del in_table

    except KeyboardInterrupt:
        raise Exception
    except arcpy.ExecuteWarning:
        raise Exception(arcpy.GetMessages())
    except arcpy.ExecuteError:
        raise Exception(arcpy.GetMessages())
    except Exception as e:
        raise Exception(e)
    except:
        traceback.print_exc()
        raise Exception
    else:
        try:
            leave_out_keys = ["leave_out_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys
            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
        except:
            raise Exception(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

def alter_fields(csv_data_folder="", in_table=""):
    try:
        # Import this Python module
        import dismap
        importlib.reload(dismap)

        table = os.path.basename(in_table)
        project_gdb = os.path.dirname(in_table)
        del in_table

        field_definitions = dismap.field_definitions(csv_data_folder, "")
        del csv_data_folder

        arcpy.env.workspace = project_gdb
        arcpy.SetLogMetadata(True)

        if arcpy.Exists(table):
            arcpy.AddMessage(f"Altering Field Aliases for Table: {table}")

            fields = [f for f in arcpy.ListFields(table) if f.type not in ["Geometry", "OID"] and f.name not in ["Shape_Area", "Shape_Length"]]

            for field in fields:
                field_name = field.name
                arcpy.AddMessage(f"\tAltering Field: {field_name} {field.type}")

                if field_name in field_definitions:

                    arcpy.AddMessage(f"\t\tAltering Field: {field_name} to: {field_definitions[field_name]['field_alias']}")

                    arcpy.management.AlterField(
                                                in_table=table,
                                                field=field_definitions[field_name]["field_name"],
                                                new_field_name=field_definitions[field_name]["field_name"],
                                                new_field_alias=field_definitions[field_name]["field_alias"],
                                                field_length=field_definitions[field_name]["field_length"],
                                                field_is_nullable="NULLABLE",
                                                clear_field_alias="DO_NOT_CLEAR",
                                               )
                    arcpy.AddMessage("\t\t\t{0}\n".format(arcpy.GetMessages().replace("\n", "\n\t\t\t")))

                elif field_name not in field_definitions:
                    arcpy.AddMessage(f"###--->>> Field: {field_name} is not in fieldDefinitions <<<---###")

                del field, field_name
            del fields
        else:
            arcpy.AddWarning(f"###--->>> Alter fields: {table} not found <<<---###")

        del field_definitions, table, project_gdb

        results = True

        del dismap

    except KeyboardInterrupt:
        raise Exception
    except arcpy.ExecuteWarning:
        raise Exception(arcpy.GetMessages())
    except arcpy.ExecuteError:
        raise Exception(arcpy.GetMessages())
    except Exception as e:
        raise Exception(e)
    except:
        traceback.print_exc()
        raise Exception
    else:
        try:
            leave_out_keys = ["leave_out_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys
            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
        except:
            raise Exception(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

def backup_gdb(project_gdb=""):
    try:

        arcpy.AddMessage("Making a backup")
        arcpy.management.Copy(project_gdb, project_gdb.replace(".gdb", f"_Backup.gdb"))
        arcpy.AddMessage("\t" + arcpy.GetMessages(0).replace("\n", "\n\t"))

        arcpy.AddMessage("Compacting the backup")
        arcpy.management.Compact(project_gdb.replace(".gdb", f"_Backup.gdb"))
        arcpy.AddMessage("\t" + arcpy.GetMessages(0).replace("\n", "\n\t"))

        del project_gdb

    except KeyboardInterrupt:
        raise Exception
    except arcpy.ExecuteWarning:
        raise Exception(arcpy.GetMessages())
    except arcpy.ExecuteError:
        raise Exception(arcpy.GetMessages())
    except Exception as e:
        raise Exception(e)
    except:
        traceback.print_exc()
        raise Exception
    else:
        try:
            leave_out_keys = ["leave_out_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys
            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
        except:
            raise Exception(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

def basic_metadata(csv_data_folder="", in_table=""):
    # Deprecated
    try:

        table       = os.path.basename(in_table)
        project_gdb = os.path.dirname(in_table)

        metadata_dictionary = metadata_dictionary_json(csv_data_folder, "")
        del csv_data_folder

        # set workspace environment
        arcpy.env.overwriteOutput = True
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.env.scratchWorkspace = rf"Scratch\scratch.gdb"
        arcpy.env.workspace = project_gdb
        arcpy.SetLogMetadata(True)

        if arcpy.Exists(table):
            arcpy.AddMessage(f"Adding metadata to: {table}")

            if table.endswith(".crf"):
                table = table.replace(".crf", "_Mosaic")

            # from arcpy import metadata as md
            # # https://pro.arcgis.com/en/pro-app/latest/arcpy/metadata/metadata-class.htm
            # dataset_md = md.Metadata(in_table)
            # dataset_md.synchronize("ALWAYS", 0)
            # dataset_md.save()
            # dataset_md.reload()

            # dataset_md.synchronize("NOT_CREATED", 0)
            # dataset_md.title             = metadata_dictionary[table]["md_title"]
            # dataset_md.tags              = metadata_dictionary[table]["md_tags"]
            # dataset_md.summary           = metadata_dictionary[table]["md_summary"]
            # dataset_md.description       = metadata_dictionary[table]["md_description"]
            # dataset_md.credits           = metadata_dictionary[table]["md_credits"]
            # dataset_md.accessConstraints = metadata_dictionary[table]["md_access_constraints"]
            # dataset_md.save()
            # dataset_md.reload()

            # print(metadata_dictionary[table]["md_title"])
            # print(metadata_dictionary[table]["md_tags"])
            # print(metadata_dictionary[table]["md_summary"])
            # print(metadata_dictionary[table]["md_description"])
            # print(metadata_dictionary[table]["md_credits"])
            # print(metadata_dictionary[table]["md_access_constraints"])

            arcpy.AddMessage(f"Adding metadata to: {table} completed")

            #del dataset_md, md

        else:
            arcpy.AddWarning(f"Adding Metadata: {table} not found")

        del metadata_dictionary, table, project_gdb, in_table

        results = True

    except KeyboardInterrupt:
        raise Exception
    except arcpy.ExecuteWarning:
        raise Exception(arcpy.GetMessages())
    except arcpy.ExecuteError:
        raise Exception(arcpy.GetMessages())
    except Exception as e:
        raise Exception(e)
    except:
        traceback.print_exc()
        raise Exception
    else:
        try:
            leave_out_keys = ["leave_out_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys
            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
        except:
            raise Exception(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

def check_datasets(datasets=[]):
    try:

        def formatDateTime(dateTime):
            from datetime import datetime, timezone

            d = datetime.strptime(dateTime, "%Y-%m-%dT%H:%M:%S.%f")
            d = d.replace(tzinfo=timezone.utc)
            d = d.astimezone()
            return d.strftime("%b %d %Y %I:%M:%S %p")

        for dataset in datasets:
            # Create a Describe object from the feature class
            #
            desc = arcpy.da.Describe(dataset)
            # Print some feature class properties
            # baseName
            # catalogPath
            # children
            # childrenExpanded
            # Examine children and print their name and dataType
            #
            # print("Children:")
            # for child in desc.children:
            #    print("\t%s = %s" % (child.name, child.dataType))
            # dataElementType
            # dataType
            # extension
            # file
            # fullPropsRetrieved
            # metadataRetrieved

            arcpy.AddMessage(f"Dataset Name:         {desc['name']}")
            arcpy.AddMessage(f"\tDataset Path:      {desc['path']}")
            arcpy.AddMessage(f"\tDataset Type:      {desc['dataType']}")

            if desc["dataType"] == "FeatureClass":
                # arcpy.AddMessage(f"\tFeature Type:     {desc['featureType']}")
                arcpy.AddMessage(f"\tData Type:         {desc['dataType']}")
                # arcpy.AddMessage(f"\tDataset Type:     {desc['datasetType']}")
                arcpy.AddMessage(f"\tShape Type:        {desc['shapeType']}")
                arcpy.AddMessage(f"\tDate Created:      {formatDateTime(desc['dateCreated'])}")
                arcpy.AddMessage(f"\tDate Accessed:     {formatDateTime(desc['dateAccessed'])}")
                arcpy.AddMessage(f"\tDate Modified:     {formatDateTime(desc['dateModified'])}")
                arcpy.AddMessage(f"\tSize:              {round(desc['size'] * 0.000001, 2)} MB")
                arcpy.AddMessage(f"\tSpatial Reference: {desc['spatialReference'].name}")
                # arcpy.AddMessage(f"Spatial Index:    {str(desc.hasSpatialIndex)}")
                # arcpy.AddMessage(f"Has M:            {desc.hasM}")
                # arcpy.AddMessage(f"Has Z:            {desc.hasZ}")
                # arcpy.AddMessage(f"Shape Field Name: {desc.shapeFieldName}")
                # arcpy.AddMessage(f"Split Model:      {str(desc.hasSpatialIndex)}")
                # print(desc["fields"])
                fields = [f.name for f in desc["fields"]]
                oid = desc["OIDFieldName"]
                # Use SQL TOP to sort field values
                arcpy.AddMessage(f"\t{', '.join(fields)}")
                for row in arcpy.da.SearchCursor(dataset, fields, f"{oid} <= 5"):
                    arcpy.AddMessage(f"\t{row}")
                    del row
                del oid, fields

            ##                fields         = [f.name for f in desc["fields"]]
            ##                oid_field_name = desc["OIDFieldName"]
            ##                # Use SQL TOP to sort field values
            ##                arcpy.AddMessage(f"\t{', '.join(fields)}")
            ##                oids = [oid for oid in arcpy.da.SearchCursor(dataset, f"{oid_field_name}")]
            ##                from random import sample
            ##                random_indices = sample(oids, 5)
            ##                del sample
            ##                for row in arcpy.da.SearchCursor(dataset, fields, f"{oid_field_name} in {random_indices}"):
            ##                    arcpy.AddMessage(f"\t{row}")
            ##                    del row
            ##                del oids, random_indices, oid_field_name, fields

            elif desc["dataType"] == "RasterDataset":
                arcpy.AddMessage(f"\tData Type:         {desc['dataType']}")
                arcpy.AddMessage(f"\tCell Size:         {desc['meanCellHeight']} x {desc['meanCellWidth']}")
                arcpy.AddMessage(f"\tExtent:            {desc['extent']}")
                arcpy.AddMessage(f"\tHeight & Width:    {desc['height']} x {desc['width']}")
                arcpy.AddMessage(f"\tSpatial Reference: {desc['spatialReference'].name}")

                # for key in sorted(desc):
                #    value = str(desc[key])
                #    print(f"Key: '{key:<30}' Value: '{value:<25}'")
                #    del value, key

            elif desc["dataType"] == "Table":
                arcpy.AddMessage(f"\tData Type:         {desc['dataType']}")
                arcpy.AddMessage(f"\tDate Created:      {formatDateTime(desc['dateCreated'])}")
                arcpy.AddMessage(f"\tDate Accessed:     {formatDateTime(desc['dateAccessed'])}")
                arcpy.AddMessage(f"\tDate Modified:     {formatDateTime(desc['dateModified'])}")
                arcpy.AddMessage(f"\tSize:              {round(desc['size'] * 0.000001, 2)} MB")
                # print(desc["fields"])
                fields = [f.name for f in desc["fields"]]
                oid = desc["OIDFieldName"]
                # Use SQL TOP to sort field values
                arcpy.AddMessage(f"\t{', '.join(fields)}")
                for row in arcpy.da.SearchCursor(dataset, fields, f"{oid} <= 5"):
                    arcpy.AddMessage(f"\t{row}")
                    del row
                del oid, fields

            elif desc["dataType"] == "MosaicDataset":
                arcpy.AddMessage(f"\t DSID: {desc['DSID']}")
                arcpy.AddMessage(f"\t JPEGQuality: {desc['JPEGQuality']}")
                arcpy.AddMessage(f"\t LERCTolerance: {desc['LERCTolerance']}")
                arcpy.AddMessage(f"\t MExtent: {desc['MExtent']}")
                arcpy.AddMessage(f"\t OIDFieldName: {desc['OIDFieldName']}")
                arcpy.AddMessage(f"\t ZExtent: {desc['ZExtent']}")
                arcpy.AddMessage(f"\t allowedCompressionMethods: {desc['allowedCompressionMethods']}")
                arcpy.AddMessage(f"\t allowedFields: {desc['allowedFields']}")
                arcpy.AddMessage(f"\t allowedMensurationCapabilities: {desc['allowedMensurationCapabilities']}")
                arcpy.AddMessage(f"\t allowedMosaicMethods: {desc['allowedMosaicMethods']}")
                arcpy.AddMessage(f"\t bandCount: {desc['bandCount']}")
                arcpy.AddMessage(f"\t baseName: {desc['baseName']}")
                arcpy.AddMessage(f"\t blendWidth: {desc['blendWidth']}")
                arcpy.AddMessage(f"\t blendWidthUnits: {desc['blendWidthUnits']}")
                arcpy.AddMessage(f"\t catalogPath: {desc['catalogPath']}")
                arcpy.AddMessage(f"\t cellSizeToleranceFactor: {desc['cellSizeToleranceFactor']}")
                arcpy.AddMessage(f"\t children: {desc['children']}")
                arcpy.AddMessage(f"\t childrenExpanded: {desc['childrenExpanded']}")
                arcpy.AddMessage(f"\t childrenNames: {desc['childrenNames']}")
                arcpy.AddMessage(f"\t clipToBoundary: {desc['clipToBoundary']}")
                arcpy.AddMessage(f"\t compressionType: {desc['compressionType']}")
                arcpy.AddMessage(f"\t dataElementType: {desc['dataElementType']}")
                arcpy.AddMessage(f"\t dataType: {desc['dataType']}")
                arcpy.AddMessage(f"\t datasetType: {desc['datasetType']}")
                arcpy.AddMessage(f"\t defaultCompressionMethod: {desc['defaultCompressionMethod']}")
                arcpy.AddMessage(f"\t defaultMensurationCapability: {desc['defaultMensurationCapability']}")
                arcpy.AddMessage(f"\t defaultMosaicMethod: {desc['defaultMosaicMethod']}")
                arcpy.AddMessage(f"\t defaultResamplingMethod: {desc['defaultResamplingMethod']}")
                arcpy.AddMessage(f"\t defaultSubtypeCode: {desc['defaultSubtypeCode']}")
                arcpy.AddMessage(f"\t endTimeField: {desc['endTimeField']}")
                arcpy.AddMessage(f"\t extent: {desc['extent']}")
                arcpy.AddMessage(f"\t featureType: {desc['featureType']}")
                arcpy.AddMessage(f"\t fields: {desc['fields']}")
                arcpy.AddMessage(f"\t file: {desc['file']}")
                arcpy.AddMessage(f"\t footprintMayContainNoData: {desc['footprintMayContainNoData']}")
                arcpy.AddMessage(f"\t format: {desc['format']}")
                arcpy.AddMessage(f"\t fullPropsRetrieved: {desc['fullPropsRetrieved']}")
                arcpy.AddMessage(f"\t hasOID: {desc['hasOID']}")
                arcpy.AddMessage(f"\t hasSpatialIndex: {desc['hasSpatialIndex']}")
                arcpy.AddMessage(f"\t indexes: {desc['indexes']}")
                arcpy.AddMessage(f"\t isInteger: {desc['isInteger']}")
                arcpy.AddMessage(f"\t isTimeInUTC: {desc['isTimeInUTC']}")
                arcpy.AddMessage(f"\t maxDownloadImageCount: {desc['maxDownloadImageCount']}")
                arcpy.AddMessage(f"\t maxDownloadSizeLimit: {desc['maxDownloadSizeLimit']}")
                arcpy.AddMessage(f"\t maxRastersPerMosaic: {desc['maxRastersPerMosaic']}")
                arcpy.AddMessage(f"\t maxRecordsReturned: {desc['maxRecordsReturned']}")
                arcpy.AddMessage(f"\t maxRequestSizeX: {desc['maxRequestSizeX']}")
                arcpy.AddMessage(f"\t maxRequestSizeY: {desc['maxRequestSizeY']}")
                arcpy.AddMessage(f"\t minimumPixelContribution: {desc['minimumPixelContribution']}")
                arcpy.AddMessage(f"\t mosaicOperator: {desc['mosaicOperator']}")
                arcpy.AddMessage(f"\t name: {desc['name']}")
                arcpy.AddMessage(f"\t orderField: {desc['orderField']}")
                arcpy.AddMessage(f"\t path: {desc['path']}")
                arcpy.AddMessage(f"\t permanent: {desc['permanent']}")
                arcpy.AddMessage(f"\t rasterFieldName: {desc['rasterFieldName']}")
                arcpy.AddMessage(f"\t rasterMetadataLevel: {desc['rasterMetadataLevel']}")
                arcpy.AddMessage(f"\t shapeFieldName: {desc['shapeFieldName']}")
                arcpy.AddMessage(f"\t shapeType: {desc['shapeType']}")
                arcpy.AddMessage(f"\t sortAscending: {desc['sortAscending']}")
                arcpy.AddMessage(f"\t spatialReference: {desc['spatialReference']}")
                arcpy.AddMessage(f"\t startTimeField: {desc['startTimeField']}")
                arcpy.AddMessage(f"\t supportsBigInteger: {desc['supportsBigInteger']}")
                arcpy.AddMessage(f"\t supportsBigObjectID: {desc['supportsBigObjectID']}")
                arcpy.AddMessage(f"\t supportsDateOnly: {desc['supportsDateOnly']}")
                arcpy.AddMessage(f"\t supportsTimeOnly: {desc['supportsTimeOnly']}")
                arcpy.AddMessage(f"\t supportsTimestampOffset: {desc['supportsTimestampOffset']}")
                arcpy.AddMessage(f"\t timeValueFormat: {desc['timeValueFormat']}")
                arcpy.AddMessage(f"\t useTime: {desc['useTime']}")
                arcpy.AddMessage(f"\t viewpointSpacingX: {desc['viewpointSpacingX']}")
                arcpy.AddMessage(f"\t viewpointSpacingY: {desc['viewpointSpacingY']}")
                arcpy.AddMessage(f"\t workspace: {desc['workspace']}")

                # print(desc["fields"])
                fields = [f.name for f in desc["fields"]]
                oid = desc["OIDFieldName"]
                # Use SQL TOP to sort field values
                arcpy.AddMessage(f"\t{', '.join(fields)}")
                for row in arcpy.da.SearchCursor(dataset, fields, f"{oid} <= 5"):
                    arcpy.AddMessage(f"\t{row}")
                    del row
                del oid, fields

            elif desc["dataType"]:
                arcpy.AddWarning(desc["dataType"])

            else:
                arcpy.AddWarning("No data to describe!!")

            del desc, dataset

        del formatDateTime, datasets

        results = True

    except KeyboardInterrupt:
        raise Exception
    except arcpy.ExecuteWarning:
        raise Exception(arcpy.GetMessages())
    except arcpy.ExecuteError:
        raise Exception(arcpy.GetMessages())
    except Exception as e:
        raise Exception(e)
    except:
        traceback.print_exc()
        raise Exception
    else:
        try:
            leave_out_keys = ["leave_out_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys
            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
        except:
            raise Exception(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

def check_transformation(ds, cs):
    dsc_in = arcpy.Describe(ds)
    insr = dsc_in.spatialReference

    # if output coordinate system is set and is different than the input coordinate system
    if cs and (cs.name != insr.name):
        translist = arcpy.ListTransformations(insr, cs, dsc_in.extent)
        trans = translist[0] if translist else ""
        # arcpy.AddMessage(f"\t{trans}\n")
        # for trans in translist:
        #    arcpy.AddMessage(f"\t{trans}")
        return trans

def compare_metadata_xml(file1="", file2=""):
    """This requires the use of the clone ArcGIS Pro env and the installation of xmldiff."""
    # https://buildmedia.readthedocs.org/media/pdf/xmldiff/latest/xmldiff.pdf
    try:
        # Test if passed workspace exists, if not raise Exception
        if not os.path.exists(rf"{file1}") or not os.path.exists(rf"{file2}"):
            raise Exception(line_info(f"{os.path.basename(file1)} or {os.path.basename(file2)} is missing!!"))

        from lxml import etree
        from xmldiff import main, formatting

        # Examples
        # diff = main.diff_files(file1, file2, formatter=formatting.XMLFormatter())
        # diff = main.diff_files(file1, file2, formatter=formatting.XMLFormatter(normalize=formatting.WS_BOTH, pretty_print=True))
        # The DiffFormatter creates a script of steps to take to make file2 like file1
        diff = main.diff_files(file1, file2, formatter=formatting.DiffFormatter())
        # If there are differences
        if diff:
            diff = main.diff_files(file1, file2, formatter=formatting.XMLFormatter())
            return diff
        else:
            return None

        del etree, main, formatting, file1, file2

        #import copy
        #results = copy.deepycopy(diff)

        del copy
        del diff

    except KeyboardInterrupt:
        raise Exception
    except arcpy.ExecuteWarning:
        raise Exception(arcpy.GetMessages())
    except arcpy.ExecuteError:
        raise Exception(arcpy.GetMessages())
    except Exception as e:
        raise Exception(e)
    except:
        traceback.print_exc()
        raise Exception
    else:
        try:
            leave_out_keys = ["leave_out_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys
            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
        except:
            raise Exception(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

def convertSeconds(seconds):
    try:
        _min, _sec = divmod(seconds, 60)
        _hour, _min = divmod(_min, 60)
        return f"{int(_hour)}:{int(_min)}:{_sec:.3f}"

    except:
        traceback.print_exc()

def calculate_core_species(table):
    try:

        region_gdb = os.path.dirname(table)

        arcpy.env.workspace = region_gdb
        arcpy.env.scratchWorkspace = region_gdb
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.env.overwriteOutput = True
        arcpy.SetLogHistory(True)  # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(1)  # 0—A tool will not throw an exception, even if the tool produces an error or warning.
        # 1—If a tool produces a warning or an error, it will throw an exception.
        # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(["NORMAL"])  # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        del region_gdb

        # def unique_years(table):
        #    with arcpy.da.SearchCursor(table, ["Year"]) as cursor:
        #        return sorted({row[0] for row in cursor})

        def unique_values(table, field):
            with arcpy.da.SearchCursor(table, [field]) as cursor:
                return sorted({row[0] for row in cursor})  # Uses list comprehension

        # Get  unique list of years from the table
        all_years = unique_values(table, "Year")

        PrintListOfYears = False
        if PrintListOfYears:
            # Print list of years
            arcpy.AddMessage(f"--> Years: {', '.join([str(y) for y in all_years])}")

            # Get minimum year (first year) and maximum year (last year)
            min_year, max_year = min(all_years), max(all_years)

            # Print min year
            arcpy.AddMessage(f"--> Min Year: {min_year} and Max Year: {max_year}")

            del min_year, max_year

        del PrintListOfYears

        arcpy.AddMessage(f"\t Creating {os.path.basename(table)} Table View")

        species_table_view = arcpy.management.MakeTableView(table, f"{os.path.basename(table)} Table View")

        unique_species = unique_values(species_table_view, "Species")

        for unique_specie in unique_species:
            arcpy.AddMessage(f"\t\t Unique Species: {unique_specie}")

            # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
            # The following inputs are layers or table views: "ai_csv"
            arcpy.management.SelectLayerByAttribute(in_layer_or_view=species_table_view, selection_type="NEW_SELECTION", where_clause=f"Species = '{unique_specie}' AND WTCPUE > 0.0")

            all_specie_years = unique_values(species_table_view, "Year")

            # arcpy.AddMessage(f"\t\t\t Years: {', '.join([str(y) for y in all_specie_years])}")

            # arcpy.AddMessage(f"\t\t Select Species ({unique_specie}) by attribute")

            arcpy.management.SelectLayerByAttribute(in_layer_or_view=species_table_view, selection_type="NEW_SELECTION", where_clause=f"Species = '{unique_specie}'")

            # arcpy.AddMessage(f"\t Set CoreSpecies to Yes or No")

            if all_years == all_specie_years:
                arcpy.AddMessage(f"\t\t\t {unique_specie} is a Core Species")
                arcpy.management.CalculateField(in_table=species_table_view, field="CoreSpecies", expression="'Yes'", expression_type="PYTHON", code_block="")
            else:
                arcpy.AddMessage(f"\t\t\t @@@@ {unique_specie} is not a Core Species @@@@")
                arcpy.management.CalculateField(in_table=species_table_view, field="CoreSpecies", expression="'No'", expression_type="PYTHON", code_block="")

            arcpy.management.SelectLayerByAttribute(species_table_view, "CLEAR_SELECTION")
            del unique_specie, all_specie_years

        arcpy.management.Delete(f"{os.path.basename(table)} Table View")
        del species_table_view, unique_species, all_years
        del unique_values
        del table

        results = True

    except KeyboardInterrupt:
        raise Exception
    except arcpy.ExecuteWarning:
        raise Exception(arcpy.GetMessages())
    except arcpy.ExecuteError:
        raise Exception(arcpy.GetMessages())
    except Exception as e:
        raise Exception(e)
    except:
        traceback.print_exc()
        raise Exception
    else:
        try:
            leave_out_keys = ["leave_out_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys
            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
        except:
            raise Exception(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

def dataset_title_dict(project_gdb=""):
    try:
        # Test if passed workspace exists, if not raise Exception
        if not arcpy.Exists(project_gdb):
            raise Exception(line_info(f"{os.path.basename(project_gdb)} is missing!!"))

        if "Scratch" in project_gdb:
            project = os.path.basename(os.path.dirname(os.path.dirname(project_gdb)))
        else:
            project = os.path.basename(os.path.dirname(project_gdb))

        project_folder     = os.path.dirname(project_gdb)
        crf_folder         = rf"{project_folder}\CRFs"
        _credits           = "These data were produced by NMFS OST."
        access_constraints = "***No Warranty*** The user assumes the entire risk related to its use of these data. NMFS is providing these data 'as is' and NMFS disclaims any and all warranties, whether express or implied, including (without limitation) any implied warranties of merchantability or fitness for a particular purpose. No warranty expressed or implied is made regarding the accuracy or utility of the data on any other system or for general or scientific purposes, nor shall the act of distribution constitute any such warranty. It is strongly recommended that careful attention be paid to the contents of the metadata file associated with these data to evaluate dataset limitations, restrictions or intended use. In no event will NMFS be liable to you or to any third party for any direct, indirect, incidental, consequential, special or exemplary damages or lost profit resulting from any use or misuse of these data."

        datasets_dict = {}

        dataset_codes = {row[0] : [row[1], row[2], row[3], row[4]] for row in arcpy.da.SearchCursor(rf"{project_gdb}\Datasets", ["DatasetCode", "PointFeatureType", "DistributionProjectCode", "Region", "Season"])}
        for dataset_code in dataset_codes:
            point_feature_type        = dataset_codes[dataset_code][0] if dataset_codes[dataset_code][0] else ""
            distribution_project_code = dataset_codes[dataset_code][1] if dataset_codes[dataset_code][1] else ""
            region                    = dataset_codes[dataset_code][2] if dataset_codes[dataset_code][2] else dataset_code.replace("_", " ")
            season                    = dataset_codes[dataset_code][3] if dataset_codes[dataset_code][3] else ""

            tags    = f"DisMap, {region}, {season}" if season else f"DisMap, {region}"
            #tags    = f"{tags}, distribution, seasonal distribution, fish, invertebrates, climate change, fishery-independent surveys, ecological dynamics, oceans, biosphere, earth science, species/population interactions, aquatic sciences, fisheries, range changes"
            summary = "These data were created as part of the DisMAP project to enable visualization and analysis of changes in fish and invertebrate distributions"

            #arcpy.AddMessage(f"Dateset Code: {dataset_code}")
            if distribution_project_code:
                if distribution_project_code == "IDW":

                    #table_name            = f"{dataset_code}_{distribution_project_code}_TABLE"
                    table_name            = f"{dataset_code}_{distribution_project_code}"
                    table_name_s          = f"{table_name}_{date_code(project)}"
                    table_name_st         = f"{region} {season} Table {date_code(project)}".replace('  ',' ')

                    #arcpy.AddMessage(f"\tProcessing: {table_name}")

                    datasets_dict[table_name] = {"Dataset Service"       : table_name_s,
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
                    feature_service_title = f"{region} {season} {point_feature_type} {date_code(project)}"
                    sample_locations_fcst = f"{feature_service_title.replace('  ',' ')}"
                    del feature_service_title

                    datasets_dict[sample_locations_fc] = {"Dataset Service"       : sample_locations_fcs,
                                                          "Dataset Service Title" : sample_locations_fcst,
                                                          "Tags"                  : tags,
                                                          "Summary"               : f"{summary}. These layers provide information on the spatial extent/boundaries of the bottom trawl surveys. Information on species distributions is of paramount importance for understanding and preparing for climate-change impacts, and plays a key role in climate-ready fisheries management.",
                                                          "Description"           : f"This survey points layer provides information on both the locations where species are caught in several NOAA Fisheries surveys and the amount (i.e., biomass weight catch per unit effort, standardized to kg/ha) of each species that was caught at each location. Information on species distributions is of paramount importance for understanding and preparing for climate-change impacts, and plays a key role in climate-ready fisheries management.",
                                                          "Credits"               : _credits,
                                                          "Access Constraints"    : access_constraints}

                    #arcpy.AddMessage(f"\tSample Locations FC:   {sample_locations_fc}")
                    #arcpy.AddMessage(f"\tSample Locations FCS:  {sample_locations_fcs}")
                    #arcpy.AddMessage(f"\tSample Locations FST:  {sample_locations_fcst}")

                    del table_name, sample_locations_fc, sample_locations_fcs, sample_locations_fcst

                elif distribution_project_code != "IDW":

                    #table_name            = f"{dataset_code}_TABLE"
                    table_name            = f"{dataset_code}"
                    table_name_s          = f"{table_name}_{date_code(project)}"
                    table_name_st         = f"{region} {season} Table {date_code(project)}".replace('  ',' ')

                    #arcpy.AddMessage(f"\tProcessing: {table_name}")

                    datasets_dict[table_name] = {"Dataset Service"       : table_name_s,
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
                    feature_service_title = f"{region} {season} Sample Locations {date_code(project)}"
                    grid_points_fcst      = f"{dataset_code.replace('_', ' ')} {point_feature_type} {date_code(project)}"

                    datasets_dict[grid_points_fc] = {"Dataset Service"       : grid_points_fcs,
                                                     "Dataset Service Title" : grid_points_fcst,
                                                     "Tags"                  : tags,
                                                     "Summary"               : summary,
                                                     "Description"           : f"This grid points layer provides information on model output amount (i.e., biomass weight catch per unit effort, standardized to kg/ha) of each species that was modeled at each location. Information on species distributions is of paramount importance for understanding and preparing for climate-change impacts, and plays a key role in climate-ready fisheries management.",
                                                     "Credits"               : _credits,
                                                     "Access Constraints"    : access_constraints}

                    #arcpy.AddMessage(f"\tGRID Points FC:   {grid_points_fc}")
                    #arcpy.AddMessage(f"\tGRID Points FCS:  {grid_points_fcs}")
                    #arcpy.AddMessage(f"\tGRID Points FCST: {grid_points_fcst}")

                    del table_name, grid_points_fc, grid_points_fcs, grid_points_fcst

                dataset_code = f"{dataset_code}_{distribution_project_code}" if distribution_project_code not in dataset_code else dataset_code

                # Bathymetry
                bathymetry_r          = f"{dataset_code}_Bathymetry"
                bathymetry_rs         = f"{dataset_code}_Bathymetry_{date_code(project)}"
                feature_service_title = f"{region} {season} Bathymetry {date_code(project)}"
                bathymetry_rst        = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #arcpy.AddMessage(f"\tProcessing: {bathymetry_r}")

                datasets_dict[bathymetry_r] = {"Dataset Service"       : bathymetry_rs,
                                               "Dataset Service Title" : bathymetry_rst,
                                               "Tags"                  : tags,
                                               "Summary"               : summary,
                                               "Description"           : f"The bathymetry dataset represents the ocean depth at that grid cell.",
                                               "Credits"               : _credits,
                                               "Access Constraints"    : access_constraints}

                #arcpy.AddMessage(f"\tBathymetry R:   {bathymetry_r}")
                #arcpy.AddMessage(f"\tBathymetry RS:  {bathymetry_rs}")
                #arcpy.AddMessage(f"\tBathymetry RST: {bathymetry_rst}")

                del bathymetry_r, bathymetry_rs, bathymetry_rst

                # Boundary
                boundary_fc           = f"{dataset_code}_Boundary"
                boundary_fcs          = f"{dataset_code}_Boundary_{date_code(project)}"
                feature_service_title = f"{region} {season} Boundary {date_code(project)}"
                boundary_fcst         = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #arcpy.AddMessage(f"\tProcessing: {boundary_fc}")

                datasets_dict[boundary_fc] = {"Dataset Service"       : boundary_fcs,
                                              "Dataset Service Title" : boundary_fcst,
                                              "Tags"                  : tags,
                                              "Summary"               : summary,
                                              "Description"           : f"These files contain the spatial boundaries of the NOAA Fisheries Bottom-trawl surveys. This data set covers 8 regions of the United States: Northeast, Southeast, Gulf of Mexico, West Coast, Eastern Bering Sea, Aleutian Islands, Gulf of Alaska, and Hawai'i Islands.",
                                              "Credits"               : _credits,
                                              "Access Constraints"    : access_constraints}

                #arcpy.AddMessage(f"\tBoundary FC:   {boundary_fc}")
                #arcpy.AddMessage(f"\tBoundary FCS:  {boundary_fcs}")
                #arcpy.AddMessage(f"\tBoundary FCST: {boundary_fcst}")

                del boundary_fc, boundary_fcs, boundary_fcst

                # CRF
                crf_r                 = f"{dataset_code}_CRF"
                crf_rs                = f"{dataset_code}_{date_code(project)}"
                feature_service_title = f"{region} {season} {dataset_code[dataset_code.rfind('_')+1:]} {date_code(project)}"
                crf_rst               = f"{feature_service_title.replace('  ',' ')}"
                #del feature_service_title

                #arcpy.AddMessage(f"Processing: {crf_r}")
                #arcpy.AddMessage(f"\t{crf_rs}")
                #arcpy.AddMessage(f"\t{feature_service_title}")
                #arcpy.AddMessage(f"\t{crf_rst}")

                datasets_dict[crf_r] = {"Dataset Service"       : crf_rs,
                                        "Dataset Service Title" : crf_rst,
                                        "Tags"                  : tags,
                                        "Summary"               : f"{summary}. These interpolated biomass layers provide information on the spatial distribution of species caught in the NOAA Fisheries fisheries-independent surveys. Information on species distributions is of paramount importance for understanding and preparing for climate-change impacts, and plays a key role in climate-ready fisheries management.",
                                        "Description"           : f"NOAA Fisheries and its partners conduct fisheries-independent surveys in 8 regions in the US (Northeast, Southeast, Gulf of Mexico, West Coast, Gulf of Alaska, Bering Sea, Aleutian Islands, Hawai’i Islands). These surveys are designed to collect information on the seasonal distribution, relative abundance, and biodiversity of fish and invertebrate species found in U.S. waters. Over 400 species of fish and invertebrates have been identified in these surveys.",
                                        "Credits"               : _credits,
                                        "Access Constraints"    : access_constraints}

                #arcpy.AddMessage(f"\tCRF R:   {crf_r}")
                #arcpy.AddMessage(f"\tCRF RS:  {crf_rs}")
                #arcpy.AddMessage(f"\tCRF RST: {crf_rst}")

                del crf_r, crf_rs, crf_rst

                # Extent Points
                extent_points_fc      = f"{dataset_code}_Extent_Points"
                extent_points_fcs     = f"{dataset_code}_Extent_Points_{date_code(project)}"
                feature_service_title = f"{region} {season} Extent Points {date_code(project)}"
                extent_points_fcst    = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #arcpy.AddMessage(f"\tProcessing: {extent_points_fc}")

                datasets_dict[extent_points_fc] = {"Dataset Service"       : extent_points_fcs,
                                                   "Dataset Service Title" : extent_points_fcst,
                                                   "Tags"                  : tags,
                                                   "Summary"               : summary,
                                                   "Description"           : f"The Extent Points layer represents the extent of the model region.",
                                                   "Credits"               : _credits,
                                                   "Access Constraints"    : access_constraints}

                #arcpy.AddMessage(f"\tExtent Points FC:   {extent_points_fc}")
                #arcpy.AddMessage(f"\tExtent Points FCS:  {extent_points_fcs}")
                #arcpy.AddMessage(f"\tExtent Points FCST: {extent_points_fcst}")

                del extent_points_fc, extent_points_fcs, extent_points_fcst

                fishnet_fc            = f"{dataset_code}_Fishnet"
                fishnet_fcs           = f"{dataset_code}_Fishnet_{date_code(project)}"
                feature_service_title = f"{region} {season} Fishnet {date_code(project)}"
                fishnet_fcst          = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #arcpy.AddMessage(f"\tProcessing: {fishnet_fc}")

                datasets_dict[fishnet_fc] = {"Dataset Service"       : fishnet_fcs,
                                             "Dataset Service Title" : fishnet_fcst,
                                             "Tags"                  : tags,
                                             "Summary"               : summary,
                                             "Description"           : f"The Fishnet is used to create the latitude and longitude rasters.",
                                             "Credits"               : _credits,
                                             "Access Constraints"    : access_constraints}

                #arcpy.AddMessage(f"\tFishnet FC:   {fishnet_fc}")
                #arcpy.AddMessage(f"\tFishnet FCS:  {fishnet_fcs}")
                #arcpy.AddMessage(f"\tFishnet FCST: {fishnet_fcst}")

                del fishnet_fc, fishnet_fcs, fishnet_fcst

                indicators_tb         = f"{dataset_code}_Indicators"
                indicators_tbs        = f"{dataset_code}_Indicators_{date_code(project)}"
                feature_service_title = f"{region} {season} Indicators Table {date_code(project)}"
                indicators_tbst       = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #arcpy.AddMessage(f"\tProcessing: {indicators_t}")

                datasets_dict[indicators_tb] = {"Dataset Service"       : indicators_tbs,
                                               "Dataset Service Title" : indicators_tbst,
                                               "Tags"                  : tags,
                                               "Summary"               : f"{summary}. This table provides the key metrics used to evaluate a species distribution shift. Information on species distributions is of paramount importance for understanding and preparing for climate-change impacts, and plays a key role in climate-ready fisheries management.",
                                               "Description"           : f"These data contain the key distribution metrics of center of gravity, range limits, and depth for each species in the portal. This data set covers 8 regions of the United States: Northeast, Southeast, Gulf of Mexico, West Coast, Bering Sea, Aleutian Islands, Gulf of Alaska, and Hawai'i Islands.",
                                               "Credits"               : _credits,
                                               "Access Constraints"    : access_constraints}

                #arcpy.AddMessage(f"\tIndicators T:   {indicators_t}")
                #arcpy.AddMessage(f"\tIndicators TS:  {indicators_ts}")
                #arcpy.AddMessage(f"\tIndicators TST: {indicators_tst}")

                del indicators_tb, indicators_tbs, indicators_tbst

                lat_long_fc           = f"{dataset_code}_Lat_Long"
                lat_long_fcs          = f"{dataset_code}_Lat_Long_{date_code(project)}"
                feature_service_title = f"{region} {season} Lat Long {date_code(project)}"
                lat_long_fcst         = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #arcpy.AddMessage(f"\tProcessing: {lat_long_fc}")

                datasets_dict[lat_long_fc] = {"Dataset Service"       : lat_long_fcs,
                                              "Dataset Service Title" : lat_long_fcst,
                                              "Tags"                  : tags,
                                              "Summary"               : summary,
                                              "Description"           : f"The lat_long layer is used to get the latitude & longitude values to create these rasters",
                                              "Credits"               : _credits,
                                              "Access Constraints"    : access_constraints}

                #arcpy.AddMessage(f"\tLat Long FC:   {lat_long_fc}")
                #arcpy.AddMessage(f"\tLat Long FCS:  {lat_long_fcs}")
                #arcpy.AddMessage(f"\tLat Long FCST: {lat_long_fcst}")

                del lat_long_fc, lat_long_fcs, lat_long_fcst

                latitude_r            = f"{dataset_code}_Latitude"
                latitude_rs           = f"{dataset_code}_Latitude_{date_code(project)}"
                feature_service_title = f"{region} {season} Latitude {date_code(project)}"
                latitude_rst          = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #arcpy.AddMessage(f"\tProcessing: {latitude_r}")

                datasets_dict[latitude_r] = {"Dataset Service"       : latitude_rs,
                                             "Dataset Service Title" : latitude_rst,
                                             "Tags"                  : tags,
                                             "Summary"               : summary,
                                             "Description"           : f"The Latitude raster",
                                             "Credits"               : _credits,
                                             "Access Constraints"    : access_constraints}

                #arcpy.AddMessage(f"\tLatitude R:   {latitude_r}")
                #arcpy.AddMessage(f"\tLatitude RS:  {latitude_rs}")
                #arcpy.AddMessage(f"\tLatitude RST: {latitude_rst}")

                del latitude_r, latitude_rs, latitude_rst

                layer_species_year_image_name_tb   = f"{dataset_code}_LayerSpeciesYearImageName"
                layer_species_year_image_name_tbs  = f"{dataset_code}_LayerSpeciesYearImageName_{date_code(project)}"
                feature_service_title             = f"{region} {season} Layer Species Year Image Name Table {date_code(project)}"
                layer_species_year_image_name_tbst = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #arcpy.AddMessage(f"\tProcessing: {layer_species_year_image_name_tb}")

                datasets_dict[layer_species_year_image_name_tb] = {"Dataset Service"       : layer_species_year_image_name_tbs,
                                                                   "Dataset Service Title" : layer_species_year_image_name_tbst,
                                                                   "Tags"                  : tags,
                                                                   "Summary"               : summary,
                                                                   "Description"           : f"Layer Species Year Image Name Table",
                                                                   "Credits"               : _credits,
                                                                   "Access Constraints"    : access_constraints}

                #arcpy.AddMessage(f"\tLayerSpeciesYearImageName T:   {layer_species_year_image_name_tb}")
                #arcpy.AddMessage(f"\tLayerSpeciesYearImageName TS:  {layer_species_year_image_name_tbs}")
                #arcpy.AddMessage(f"\tLayerSpeciesYearImageName TST: {layer_species_year_image_name_tbst}")

                del layer_species_year_image_name_tb, layer_species_year_image_name_tbs, layer_species_year_image_name_tbst

                longitude_r           = f"{dataset_code}_Longitude"
                longitude_rs          = f"{dataset_code}_Longitude_{date_code(project)}"
                feature_service_title = f"{region} {season} Longitude {date_code(project)}"
                longitude_rst         = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #arcpy.AddMessage(f"\tProcessing: {longitude_r}")

                datasets_dict[longitude_r] = {"Dataset Service"       : longitude_rs,
                                              "Dataset Service Title" : longitude_rst,
                                              "Tags"                  : tags,
                                              "Summary"               : summary,
                                              "Description"           : f"The Longitude raster",
                                              "Credits"               : _credits,
                                              "Access Constraints"    : access_constraints}

                #arcpy.AddMessage(f"\tLongitude R:   {longitude_r}")
                #arcpy.AddMessage(f"\tLongitude RS:  {longitude_rs}")
                #arcpy.AddMessage(f"\tLongitude RST: {longitude_rst}")

                del longitude_r, longitude_rs, longitude_rst

                mosaic_r              = f"{dataset_code}_Mosaic"
                mosaic_rs             = f"{dataset_code}_Mosaic_{date_code(project)}"
                feature_service_title = f"{region} {season} {dataset_code[dataset_code.rfind('_')+1:]} Mosaic {date_code(project)}"
                mosaic_rst            = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #arcpy.AddMessage(f"\tProcessing: {mosaic_r}")

                datasets_dict[mosaic_r] = {"Dataset Service"       : mosaic_rs,
                                           "Dataset Service Title" : mosaic_rst,
                                           #"Tags"                  : _tags,
                                           "Tags"                  : tags,
                                           "Summary"               : f"{summary}. These interpolated biomass layers provide information on the spatial distribution of species caught in the NOAA Fisheries fisheries-independent surveys. Information on species distributions is of paramount importance for understanding and preparing for climate-change impacts, and plays a key role in climate-ready fisheries management.",
                                           "Description"           : f"NOAA Fisheries and its partners conduct fisheries-independent surveys in 8 regions in the US (Northeast, Southeast, Gulf of Mexico, West Coast, Gulf of Alaska, Bering Sea, Aleutian Islands, Hawai’i Islands). These surveys are designed to collect information on the seasonal distribution, relative abundance, and biodiversity of fish and invertebrate species found in U.S. waters. Over 400 species of fish and invertebrates have been identified in these surveys.",
                                           "Credits"               : _credits,
                                           "Access Constraints"    : access_constraints}

                #arcpy.AddMessage(f"\tMosaic R:   {mosaic_r}")
                #arcpy.AddMessage(f"\tMosaic RS:  {mosaic_rs}")
                #arcpy.AddMessage(f"\tMosaic RST: {mosaic_rst}")

                del mosaic_r, mosaic_rs, mosaic_rst

                raster_mask_r         = f"{dataset_code}_Raster_Mask"
                raster_mask_rs        = f"{dataset_code}_Raster_Mask_{date_code(project)}"
                feature_service_title = f"{region} {season} Raster Mask {date_code(project)}"
                raster_mask_rst       = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #arcpy.AddMessage(f"\tProcessing: {raster_mask_r}")

                datasets_dict[raster_mask_r] = {"Dataset Service"       : raster_mask_rs,
                                                "Dataset Service Title" : raster_mask_rst,
                                                "Tags"                  : tags,
                                                "Summary"               : summary,
                                                "Description"           : f"Raster Mask is used for image production",
                                                "Credits"               : _credits,
                                                "Access Constraints"    : access_constraints}

                #arcpy.AddMessage(f"\tRaster_Mask R:   {raster_mask_r}")
                #arcpy.AddMessage(f"\tRaster_Mask RS:  {raster_mask_rs}")
                #arcpy.AddMessage(f"\tRaster_Mask RST: {raster_mask_rst}")

                del raster_mask_r, raster_mask_rs, raster_mask_rst

                region_fc             = f"{dataset_code}_Region"
                region_fcs            = f"{dataset_code}_Region_{date_code(project)}"
                feature_service_title = f"{region} {season} Region {date_code(project)}"
                region_fcst           = f"{feature_service_title.replace('  ',' ')}"
                del feature_service_title

                #arcpy.AddMessage(f"\tProcessing: {region_fc}")

                datasets_dict[region_fc] = {"Dataset Service"       : region_fcs,
                                            "Dataset Service Title" : region_fcst,
                                            "Tags"                  : tags,
                                            "Summary"               : summary,
                                            "Description"           : f"These files contain the spatial boundaries of the NOAA Fisheries Bottom-trawl surveys. This data set covers 8 regions of the United States: Northeast, Southeast, Gulf of Mexico, West Coast, Bering Sea, Aleutian Islands, Gulf of Alaska, and Hawai'i Islands.",
                                            "Credits"               : _credits,
                                            "Access Constraints"    : access_constraints}

                #arcpy.AddMessage(f"\tRegion FC:   {region_fc}")
                #arcpy.AddMessage(f"\tRegion FCS:  {region_fcs}")
                #arcpy.AddMessage(f"\tRegion FCST: {region_fcst}")

                del region_fc, region_fcs, region_fcst

            del tags

            if not distribution_project_code:

                if "Datasets" == dataset_code:

                    #arcpy.AddMessage(f"\tProcessing: Datasets")

                    datasets_tb   = dataset_code
                    datasets_tbs  = f"{dataset_code}_{date_code(project)}"
                    datasets_tbst = f"{dataset_code} {date_code(project)}"

                    datasets_dict[datasets_tb] = {"Dataset Service"       : datasets_tbs,
                                                  "Dataset Service Title" : datasets_tbst,
                                                  "Tags"                  : "DisMAP, Datasets",
                                                  "Summary"               : summary,
                                                  "Description"           : "This table functions as a look-up table of vales",
                                                  "Credits"               : _credits,
                                                  "Access Constraints"    : access_constraints}

                    del datasets_tb, datasets_tbs, datasets_tbst

                elif "DisMAP_Regions" == dataset_code:

                    #arcpy.AddMessage(f"\tProcessing: DisMAP_Regions")

                    regions_fc   = dataset_code
                    regions_fcs  = f"{dataset_code}_{date_code(project)}"
                    regions_fcst = f"DisMAP Regions {date_code(project)}"

                    datasets_dict[regions_fc] = {"Dataset Service"       : regions_fcs,
                                                 "Dataset Service Title" : regions_fcst,
                                                 "Tags"                  : "DisMAP Regions",
                                                 "Summary"               : summary,
                                                 "Description"           : "These files contain the spatial boundaries of the NOAA Fisheries Bottom-trawl surveys. This data set covers 8 regions of the United States: Northeast, Southeast, Gulf of Mexico, West Coast, Eastern Bering Sea, Aleutian Islands, Gulf of Alaska, and Hawai'i Islands.",
                                                 "Credits"               : _credits,
                                                 "Access Constraints"    : access_constraints}

                    del regions_fc, regions_fcs, regions_fcst

                elif "Indicators" == dataset_code:

                    #arcpy.AddMessage(f"\tProcessing: Indicators")

                    indicators_tb   = f"{dataset_code}_Table"
                    indicators_tbs  = f"{dataset_code}_{date_code(project)}"
                    indicators_tbst = f"{dataset_code} {date_code(project)}"

                    datasets_dict[indicators_tb] = {"Dataset Service"    : indicators_tbs,
                                                   "Dataset Service Title" : indicators_tbst,
                                                   "Tags"                  : "DisMAP, Indicators",
                                                   "Summary"               : f"{summary}. This table provides the key metrics used to evaluate a species distribution shift. Information on species distributions is of paramount importance for understanding and preparing for climate-change impacts, and plays a key role in climate-ready fisheries management.",
                                                   "Description"           : f"These data contain the key distribution metrics of center of gravity, range limits, and depth for each species in the portal. This data set covers 8 regions of the United States: Northeast, Southeast, Gulf of Mexico, West Coast, Bering Sea, Aleutian Islands, Gulf of Alaska, and Hawai'i Islands.",
                                                   "Credits"               : _credits,
                                                   "Access Constraints"    : access_constraints}

                    del indicators_tb, indicators_tbs, indicators_tbst

                elif "LayerSpeciesYearImageName" == dataset_code:

                    #arcpy.AddMessage(f"\tProcessing: LayerSpeciesYearImageName")

                    layer_species_year_image_name_tb   = dataset_code
                    layer_species_year_image_name_tbs  = f"{dataset_code}_{date_code(project)}"
                    layer_species_year_image_name_tbst = f"Layer Species Year Image Name Table {date_code(project)}"

                    #arcpy.AddMessage(f"\tProcessing: {layer_species_year_image_name_tb}")

                    datasets_dict[layer_species_year_image_name_tb] = {"Dataset Service"       : layer_species_year_image_name_tbs,
                                                                       "Dataset Service Title" : layer_species_year_image_name_tbst,
                                                                       "Tags"                  : "DisMAP, Layer Species Year Image Name Table",
                                                                       "Summary"               : summary,
                                                                       "Description"           : "This table functions as a look-up table of values",
                                                                       "Credits"               : _credits,
                                                                       "Access Constraints"    : access_constraints}

                    #arcpy.AddMessage(f"\tLayerSpeciesYearImageName T:   {layer_species_year_image_name_tb}")
                    #arcpy.AddMessage(f"\tLayerSpeciesYearImageName TS:  {layer_species_year_image_name_tbs}")
                    #arcpy.AddMessage(f"\tLayerSpeciesYearImageName TST: {layer_species_year_image_name_tbst}")

                    del layer_species_year_image_name_tb, layer_species_year_image_name_tbs, layer_species_year_image_name_tbst


                elif "Species_Filter" == dataset_code:

                    #arcpy.AddMessage(f"\tProcessing: Species_Filter")

                    species_filter_tb   = dataset_code
                    species_filter_tbs  = f"{dataset_code}_{date_code(project)}"
                    species_filter_tbst = f"Layer Species Year Image Name Table {date_code(project)}"

                    datasets_dict[species_filter_tb] = {"Dataset Service"       : species_filter_tbs,
                                                        "Dataset Service Title" : species_filter_tbst,
                                                        "Tags"                  : "DisMAP, Species Filter Table",
                                                        "Summary"               : summary,
                                                        "Description"           : "This table functions as a look-up table of values",
                                                        "Credits"               : _credits,
                                                        "Access Constraints"    : access_constraints}

                    #arcpy.AddMessage(f"\tLayerSpeciesYearImageName T:   {species_filter_tb}")
                    #arcpy.AddMessage(f"\tLayerSpeciesYearImageName TS:  {species_filter_tbs}")
                    #arcpy.AddMessage(f"\tLayerSpeciesYearImageName TST: {species_filter_tbst}")

                    del species_filter_tb, species_filter_tbs, species_filter_tbst

                else:
                    #arcpy.AddMessage(f"\tProcessing: {dataset_code}")

                    table    = dataset_code
                    table_s  = f"{dataset_code}_{date_code(project)}"
                    table_st = f"{table_s.replace('_',' ')} {date_code(project)}"

                    #arcpy.AddMessage(f"\tProcessing: {table_s}")

                    datasets_dict[table] = {"Dataset Service"       : table_s,
                                            "Dataset Service Title" : table_st,
                                            "Tags"                  : f"DisMAP, {table}",
                                            "Summary"               : summary,
                                            "Description"           : "Unknown table",
                                            "Credits"               : _credits,
                                            "Access Constraints"    : access_constraints}

                    #arcpy.AddMessage(f"\tTable:     {table}")
                    #arcpy.AddMessage(f"\tTable TS:  {table_s}")
                    #arcpy.AddMessage(f"\tTable TST: {table_st}")

                    del table, table_s, table_st

            else:
                pass

            del summary
            del point_feature_type, distribution_project_code, region, season
            del dataset_code

        del _credits, access_constraints

        del dataset_codes
        del project_folder, crf_folder
        del project, project_gdb

        results = datasets_dict
        del datasets_dict

    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteWarning:
        traceback.print_exc()
        arcpy.AddWarning(arcpy.GetMessages())
        raise SystemExit
    except arcpy.ExecuteError:
        traceback.print_exc()
        arcpy.AddError(arcpy.GetMessages())
        raise SystemExit
    except SystemExit:
        traceback.print_exc()
        raise SystemExit
    except Exception:
        traceback.print_exc()
        raise SystemExit
    except:
        traceback.print_exc()
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
            raise Exception(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

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
        results = copy.deepcopy(_date_code)
        del _date_code, copy

    except KeyboardInterrupt:
        raise Exception
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(str(traceback.print_exc()) + arcpy.GetMessages())
        raise Exception
    except arcpy.ExecuteError:
        arcpy.AddError(str(traceback.print_exc()) + arcpy.GetMessages())
        raise Exception
    except Exception as e:
        arcpy.AddError(str(e))
        raise Exception
    except:
        arcpy.AddError(str(traceback.print_exc()))
        raise Exception
    else:
        try:
            leave_out_keys = ["leave_out_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys
            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
        except:
            raise Exception(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

def dTypesCSV(csv_data_folder="", table=""):
    try:
        import dismap

        if "IDW" in table:
            table = "IDW_Data"
        elif "GLMME" in table:
            table = "GLMME_Data"
        elif "GFDL" in table:
            table = "GFDL_Data"
        elif "Indicators" in table:
            table = "Indicators"

        ##        elif "DisMAP_Regions" in table:
        ##            table = "DisMAP_Regions"
        ##
        ##        elif "Datasets" in table:
        ##            table = "Datasets"
        ##
        ##        elif "Datasets" in table:
        ##            table = "Datasets"
        ##
        ##        elif "Datasets" in table:
        ##            table = "Datasets"

        else:
            table = table

        table_definitions = dismap.table_definitions(csv_data_folder, "")

        fields = table_definitions[table.replace(".csv", "")]

        field_csv_dtypes = {k.replace(" ", "_") : "str" for k in table_definitions[table.replace(".csv", "")]}

        del fields, table_definitions
        del csv_data_folder, table

        # Import
        del dismap

        import copy
        results = copy.deepcopy(field_csv_dtypes)
        del field_csv_dtypes, copy

    except KeyboardInterrupt:
        raise Exception
    except arcpy.ExecuteWarning:
        raise Exception(arcpy.GetMessages())
    except arcpy.ExecuteError:
        raise Exception(arcpy.GetMessages())
    except Exception as e:
        raise Exception(e)
    except:
        traceback.print_exc()
        raise Exception
    else:
        try:
            leave_out_keys = ["leave_out_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys
            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
        except:
            raise Exception(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

def dTypesGDB(csv_data_folder="", table=""):
    try:
        import dismap

        if "IDW" in table:
            table = "IDW_Data"
        elif "GLMME" in table:
            table = "GLMME_Data"
        elif "GFDL" in table:
            table = "GFDL_Data"
        else:
            pass

        field_definitions = dismap.field_definitions(csv_data_folder, "")
        table_definitions = dismap.table_definitions(csv_data_folder, "")

        fields = table_definitions[table.replace(".csv", "")]

        field_gdb_dtypes = []
        for field in fields:
            field_definition = field_definitions[field]
            # print(field_definition["field_type"])
            # fd = field_definition[:-2]
            # del fd[2], field_definition
            if field_definition["field_type"] == "TEXT":
                field_dtype = f"U{field_definition['field_length']}"
            elif field_definition["field_type"] == "SHORT":
                # np.dtype('u4') == dtype('uint32')
                field_dtype = f"U4"
            elif field_definition["field_type"] == "DOUBLE":
                # np.dtype('d') == dtype('float64'), np.dtype('f') == dtype('float32'), np.dtype('f8') == dtype('float64')
                field_dtype = f"d"
            elif field_definition["field_type"] == "DATE":
                field_dtype = f"M8[us]"
            else:
                field_dtype = ""
            field_gdb_dtypes.append((f"{field}", f"{field_dtype}"))
            del field_definition, field, field_dtype
        del fields

        del field_definitions, table_definitions

        del table, csv_data_folder

        import copy
        results = copy.deepcopy(field_gdb_dtypes)
        del field_gdb_dtypes, copy

        del dismap

    except KeyboardInterrupt:
        raise Exception
    except arcpy.ExecuteWarning:
        raise Exception(arcpy.GetMessages())
    except arcpy.ExecuteError:
        raise Exception(arcpy.GetMessages())
    except Exception as e:
        raise Exception(e)
    except:
        traceback.print_exc()
        raise Exception
    else:
        try:
            leave_out_keys = ["leave_out_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys
            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
        except:
            raise Exception(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

def export_metadata(csv_data_folder="", in_table=""):
    # Deprecated
    try:
        table = os.path.basename(in_table)
        ws = os.path.dirname(in_table)
        project_folder = os.path.dirname(ws)
        # csv_data_folder = os.path.join(project_folder, "CSV Data")
        project = os.path.basename(project_folder)
        version = project[7:]
        del in_table, project_folder, project, version, csv_data_folder

        ws_type = arcpy.Describe(ws).workspaceType

        if ws_type == "LocalDatabase":
            os.chdir(os.path.dirname(ws))
        elif ws_type == "FileSystem":
            os.chdir(ws)
        elif ws_type == "RemoteDatabase":
            pass
        else:
            pass
        del ws_type

        cwd = os.getcwd()

        # ArcPy Environments
        # Set the overwriteOutput to True
        arcpy.env.overwriteOutput = True
        # Use all of the cores on the machine.
        arcpy.env.parallelProcessingFactor = "100%"
        # Set the scratch workspace
        arcpy.env.scratchWorkspace = rf"Scratch\scratch.gdb"
        # Set the workspace to the workspace
        arcpy.env.workspace = ws

        # Set Log Metadata to False in order to not record all geoprocessing
        # steps in metadata
        arcpy.SetLogMetadata(True)

        arcpy.AddMessage(f"Dataset: {table}")

        # Process: Export Metadata
        arcpy.AddMessage(f"\tExporting Metadata Object for Dataset: {table}")

        # https://pro.arcgis.com/en/pro-app/latest/arcpy/metadata/metadata-class.htm
        from arcpy import metadata as md

        dataset_md = md.Metadata(table)
        dataset_md.synchronize("ALWAYS")
        dataset_md.save()
        dataset_md.reload()

        arcpy.AddMessage(f"\t\tStep 1: Saving the metadata file for: {table} as an EXACT_COPY")
        out_xml = os.path.join(cwd, "Export Metadata", f"{table} Step 1 EXACT_COPY.xml")
        dataset_md.saveAsXML(out_xml, "EXACT_COPY")
        pretty_format_xml_file(out_xml)
        del out_xml

        arcpy.AddMessage(f"\t\tStep 2: Saving the metadata file for: {table} as a TEMPLATE")
        out_xml = os.path.join(cwd, "Export Metadata", f"{table} Step 2 TEMPLATE.xml")
        dataset_md.saveAsXML(out_xml, "TEMPLATE")
        pretty_format_xml_file(out_xml)
        del out_xml

        del dataset_md, md

        # Declared variable
        del ws, table, cwd

        results = True

    except KeyboardInterrupt:
        raise Exception
    except arcpy.ExecuteWarning:
        raise Exception(arcpy.GetMessages())
    except arcpy.ExecuteError:
        raise Exception(arcpy.GetMessages())
    except Exception as e:
        raise Exception(e)
    except:
        traceback.print_exc()
        raise Exception
    else:
        try:
            leave_out_keys = ["leave_out_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys
            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
        except:
            raise Exception(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

def field_definitions(csv_data_folder="", field=""):
    try:
        import json, copy

        # Read a File
        with open(os.path.join(csv_data_folder, "field_definitions.json"), "r") as json_file:
            field_definitions = json.load(json_file)
        del json_file

        if not field:  # if ""
            # Returns a dictionaty of field definitions
            results = copy.deepcopy(field_definitions)
        elif field:  # If a field was passed, then return
            if field in field_definitions:
                results = copy.deepcopy(field_definitions[field])
            else:
                results = False
        # else:
        #    #return arcpy.AddError(f"Field {field} is not in field definitions")
        #    return field
        del field_definitions

        # Imports copy
        del json, copy

        # Function parameters
        del csv_data_folder, field

    except KeyboardInterrupt:
        raise Exception
    except arcpy.ExecuteWarning:
        raise Exception(arcpy.GetMessages())
    except arcpy.ExecuteError:
        raise Exception(arcpy.GetMessages())
    except Exception as e:
        raise Exception(e)
    except:
        traceback.print_exc()
        raise Exception
    else:
        try:
            leave_out_keys = ["leave_out_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys
            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
        except:
            raise Exception(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

def get_encoding_index_col(csv_file):
    import chardet
    import pandas as pd
    # Open the file in binary mode
    with open(csv_file, 'rb') as f:
        # Read the file's content
        data = f.read()
    # Detect the encoding using chardet.detect()
    encoding_result = chardet.detect(data)
    # Retrieve the encoding information
    encoding = encoding_result['encoding']
    del f, data, encoding_result
    # Print the detected encoding
    #print("Detected Encoding:", encoding)

    dtypes = {}
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file, encoding  = encoding, delimiter = ",",)
    # Analyze the data types and lengths
    for column in df.columns: dtypes[column] = df[column].dtype; del column
    first_column = list(dtypes.keys())[0]
    index_column = 0 if first_column == "Unnamed: 0" else None
    # Variables
    del df, dtypes, first_column

    # Import
    del chardet, pd

    return encoding, index_column

def get_transformation(gsr_wkt="", psr_wkt=""):
    gsr = arcpy.SpatialReference()
    gsr.loadFromString(gsr_wkt)
    # print(f"\tGSR: {gsr.name}")

    psr = arcpy.SpatialReference()
    psr.loadFromString(psr_wkt)
    # print(f"\tPSR: {psr.name}")

    transformslist = arcpy.ListTransformations(gsr, psr)
    transform = transformslist[0] if transformslist else ""
    # arcpy.AddMessage(f"\t\tTransformation: {transform}\n")
    # for transform in transformslist:
    #    arcpy.AddMessage(f"\t{transform}")

    del gsr_wkt, psr_wkt

    return transform

def import_metadata(dataset=""):
    try:
        # Deprecated
        from arcpy import metadata as md

        dataset_name = os.path.basename(dataset)

        if dataset_name.endswith(".crf"):
            dataset_name = dataset_name.replace(".crf", "_CRF")
            _project = os.path.basename(os.path.dirname(os.path.dirname(dataset)))
            project_gdb = rf"{os.path.dirname(os.path.dirname(dataset))}\{_project}.gdb"
            del _project
        else:
            project_gdb = os.path.dirname(dataset)

        project_folder  = os.path.dirname(project_gdb)
        metadata_folder = rf"{project_folder}\ArcGIS Metadata"

        # ArcPy Environments
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.env.workspace                = project_gdb
        arcpy.env.scratchWorkspace         = rf"Scratch\scratch.gdb"
        arcpy.SetLogMetadata(True)

        metadata_dictionary = dataset_title_dict(project_gdb)
        #print(metadata_dictionary.keys())

        arcpy.AddMessage(f"Metadata for: {dataset_name} dataset")

        # print(f"\tDataset Service:       {datasets_dict[dataset]['Dataset Service']}")
        # print(f"\tDataset Service Title: {datasets_dict[dataset]['Dataset Service Title']}")

        # https://pro.arcgis.com/en/pro-app/latest/arcpy/metadata/metadata-class.htm
        dataset_md = md.Metadata(dataset)
        dataset_md.synchronize("ALWAYS")
        dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
        dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
        dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
        dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
        dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
        dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
        dataset_md.save()
        dataset_md.reload()

        poc_template = r"{metadata_folder}\poc_template.xml"
        poc_template_md = md.Metadata(poc_template)
        #dataset_md.copy(poc_template_md)
        dataset_md.importMetadata(r"{metadata_folder}\poc_template.xml")
        #dataset_md.synchronize("ACCESSED", 0)
        #dataset_md.synchronize("ALWAYS")
        #dataset_md.synchronize("CREATED")
        #dataset_md.synchronize("NOT_CREATED")
        #dataset_md.synchronize("OVERWRITE")
        dataset_md.synchronize("SELECTIVE")
        dataset_md.save()
        #dataset_md.reload()
        del poc_template, poc_template_md

        # Delete all geoprocessing history and any enclosed files from the item's metadata
        #dataset_md.deleteContent('GPHISTORY')
        #dataset_md.deleteContent('ENCLOSED_FILES')
        #dataset_md.save()
        #dataset_md.reload()

        out_xml = rf"{metadata_folder}\{dataset_md.title}.xml"
        #dataset_md.saveAsXML(out_xml, "REMOVE_ALL_SENSITIVE_INFO")
        dataset_md.saveAsXML(out_xml, "REMOVE_MACHINE_NAMES")
        #dataset_md.saveAsXML(out_xml)

        pretty_format_xml_file(out_xml)
        del out_xml

        del dataset_md

##        arcpy.AddMessage(f"Dataset: {dataset_name}")
##        dataset_md_path = rf"{metadata_folder}\{dataset_name}.xml"
##        if arcpy.Exists(dataset_md_path):
##            arcpy.AddMessage(f"\tMetadata File: {os.path.basename(dataset_md_path)}")
##            from arcpy import metadata as md
##            try:
##                dataset_md = md.Metadata(dataset)
##                # Import the standard-format metadata content to the target item
##                if not dataset_md.isReadOnly:
##                    dataset_md.importMetadata(dataset_md_path, "ARCGIS_METADATA")
##                    dataset_md.save()
##                    dataset_md.reload()
##                    dataset_md.title = title
##                    dataset_md.save()
##                    dataset_md.reload()
##
##                arcpy.AddMessage(f"\tExporting metadata file from {dataset_name}")
##
##                out_xml = rf"{project_folder}\Export Metadata\{title} EXACT_COPY.xml"
##                dataset_md.saveAsXML(out_xml, "EXACT_COPY")
##
##                pretty_format_xml_file(out_xml)
##                del out_xml
##
##                del dataset_md, md
##
##            except:
##                arcpy.AddError(f"\tDataset metadata import error!! {arcpy.GetMessages()}")
##        else:
##            arcpy.AddWarning(f"\tDataset missing metadata file!!")

        # Import
        del md
        # Declared variable
        del metadata_dictionary
        del dataset_name, project_gdb, project_folder, metadata_folder

        # Function parameters
        del dataset

        results = True

    except KeyboardInterrupt:
        raise Exception
    except arcpy.ExecuteWarning:
        raise Exception(arcpy.GetMessages())
    except arcpy.ExecuteError:
        raise Exception(arcpy.GetMessages())
    except Exception as e:
        raise Exception(e)
    except:
        traceback.print_exc()
        raise Exception
    else:
        try:
            leave_out_keys = ["leave_out_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys
            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
        except:
            raise Exception(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

def metadata_dictionary_json(csv_data_folder="", dataset_name=""):
    try:
        import json

        # Read a File
        with open(rf"{csv_data_folder}\metadata_dictionary.json", "r") as json_file:
            metadata_dictionary = json.load(json_file)
        del json_file, json, csv_data_folder

        if not dataset_name:
            results = metadata_dictionary
        elif dataset_name:
            results = metadata_dictionary[dataset_name]
        else:
            results = None

    except KeyboardInterrupt:
        raise Exception
    except arcpy.ExecuteWarning:
        raise Exception(arcpy.GetMessages())
    except arcpy.ExecuteError:
        raise Exception(arcpy.GetMessages())
    except Exception as e:
        raise Exception(e)
    except:
        traceback.print_exc()
        raise Exception
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

def pretty_format_xml_file(metadata=""):
    try:
        # xml.etree.ElementTree Imports
        import xml.etree.ElementTree as ET

        #arcpy.AddMessage(f"###--->>> Converting metadata file: {os.path.basename(metadata)} to pretty format")
        if os.path.isfile(metadata):
            tree = ET.ElementTree(file=metadata)
            root = tree.getroot()
            tree = ET.ElementTree(root)
            ET.indent(tree, space="\t", level=0)
            xmlstr = ET.tostring(root, encoding="UTF-8").decode("UTF-8")
            xmlstr = xmlstr.replace(' Sync="TRUE">\n', ' Sync="TRUE">')
            xmlstr = xmlstr.replace(' Sync="FALSE">\n', ' Sync="FALSE">')
            xmlstr = xmlstr.replace(' value="eng">\n', ' value="eng">')
            xmlstr = xmlstr.replace(' value="US">\n', ' value="US">')
            xmlstr = xmlstr.replace(' value="001">\n', ' value="001">')
            xmlstr = xmlstr.replace(' value="002">\n', ' value="002">')
            xmlstr = xmlstr.replace(' value="003">\n', ' value="003">')
            xmlstr = xmlstr.replace(' value="004">\n', ' value="004">')
            xmlstr = xmlstr.replace(' value="005">\n', ' value="005">')
            xmlstr = xmlstr.replace(' value="006">\n', ' value="006">')
            xmlstr = xmlstr.replace(' value="007">\n', ' value="007">')
            xmlstr = xmlstr.replace(' value="008">\n', ' value="008">')
            xmlstr = xmlstr.replace(' value="009">\n', ' value="009">')
            xmlstr = xmlstr.replace(' value="010">\n', ' value="010">')
            xmlstr = xmlstr.replace(' value="011">\n', ' value="011">')
            xmlstr = xmlstr.replace(' value="012">\n', ' value="012">')
            xmlstr = xmlstr.replace(' value="013">\n', ' value="013">')
            xmlstr = xmlstr.replace(' value="014">\n', ' value="014">')
            xmlstr = xmlstr.replace(' value="015">\n', ' value="015">')
            xmlstr = xmlstr.replace(' code="0">\n', ' code="0">')
            xmlstr = xmlstr.replace('<RefSystem dimension="horizontal">\n', '<RefSystem dimension="horizontal">',)
            xmlstr = xmlstr.replace('<UOM type="length">\n', '<UOM type="length">')

            xmlstr = xmlstr.replace("<attrdef>", '<attrdef Sync="TRUE">')
            xmlstr = xmlstr.replace("<attrdefs>", '<attrdefs Sync="TRUE">')
            xmlstr = xmlstr.replace("<udom>", '<udom Sync="TRUE">')

            xmlstr = xmlstr.replace('Sync="FALSE"', 'Sync="TRUE"')

            try:
                with open(metadata, "w") as f:
                    f.write(xmlstr)
                    del f
            except:
                arcpy.AddError(f"The metadata file: {os.path.basename(metadata)} can not be overwritten!!")
            del xmlstr, tree, root
        else:
            arcpy.AddWarning(f"\t###--->>> {os.path.basename(metadata)} is missing!! <<<---###")
            arcpy.AddWarning(f"\t###--->>> {metadata} <<<---###")
        # Declared variable
        del metadata, ET

        results = True

    except KeyboardInterrupt:
        raise Exception
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(arcpy.GetMessages())
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages())
    except Exception as e:
        arcpy.AddError(str(e))
        traceback.print_exc()
        raise SystemExit
    except:
        traceback.print_exc()
    else:
        try:
            leave_out_keys = ["leave_out_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys
            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
        except:
            raise Exception(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

def pretty_format_xml_files(metadata_folder=""):
    try:
        arcpy.env.overwriteOutput = True
        arcpy.env.workspace = metadata_folder

        xml_files = [rf"{metadata_folder}\{xml}" for xml in arcpy.ListFiles("*.xml")]
        for xml_file in xml_files:
            arcpy.AddMessage(os.path.basename(xml_file))
            pretty_format_xml_file(xml_file)
            del xml_file

        # Variables declared in the function
        del xml_files

        # Function paramters
        del metadata_folder

        #print(tgt_item_md.title)
        results = True

    except KeyboardInterrupt:
        raise Exception
    except arcpy.ExecuteWarning:
        raise Exception(arcpy.GetMessages())
    except arcpy.ExecuteError:
        raise Exception(arcpy.GetMessages())
    except Exception as e:
        raise Exception(e)
    except:
        traceback.print_exc()
        raise Exception
    else:
        try:
            leave_out_keys = ["leave_out_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys
            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
        except:
            raise Exception(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

def table_definitions(csv_data_folder="", dataset_name=""):
    try:
        import json, copy

        # Read a File
        with open(os.path.join(csv_data_folder, "table_definitions.json"), "r") as json_file:
            table_definitions = json.load(json_file)
        del json_file

        if not dataset_name or dataset_name == "":
            # Return a dictionary of all values
            results = copy.deepcopy(table_definitions)
        elif dataset_name:
            # arcpy.AddMessage(f"IN: {dataset_name}")
            if "_IDW" in dataset_name:
                dataset_name = "IDW_Data"
            elif "_GLMME" in dataset_name:
                dataset_name = "GLMME_Data"
            elif "_GFDL" in dataset_name:
                dataset_name = "GFDL_Data"
            else:
                pass
            # arcpy.AddMessage(f"OUT: {dataset_name}")
            results = copy.deepcopy(table_definitions[dataset_name])
        else:
            arcpy.AddError("something wrong")

        # Variables created in function
        del table_definitions
        # Import
        del json, copy
        # Function parameters
        del csv_data_folder, dataset_name

    except KeyboardInterrupt:
        raise Exception
    except arcpy.ExecuteWarning:
        raise Exception(arcpy.GetMessages())
    except arcpy.ExecuteError:
        raise Exception(arcpy.GetMessages())
    except Exception as e:
        raise Exception(e)
    except:
        traceback.print_exc()
        raise Exception
    else:
        try:
            leave_out_keys = ["leave_out_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys
            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
        except:
            raise Exception(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

# #
# Function: unique_years
#       Gets the unique years in a table
# @param string table: The name of the layer
# @return array: a sorted year array so we can go in order.
# #
def unique_years(table):
    #arcpy.AddMessage(table)
    arcpy.management.SelectLayerByAttribute( table, "CLEAR_SELECTION" )
    arcpy.management.SelectLayerByAttribute( table, "NEW_SELECTION", "Year IS NOT NULL")
    with arcpy.da.SearchCursor(table, ["Year"]) as cursor:
        return sorted({row[0] for row in cursor})

def test_bed_1(project_gdb=""):
##            raise SystemExit(traceback.print_exc())
##    finally:
##        if "results" in locals().keys(): del results
    try:

        base_project_folder = os.path.dirname(os.path.dirname(__file__))

        project_gdb = rf"{base_project_folder}\{project}\{project}.gdb"

        del base_project_folder

        # Test if passed workspace exists, if not raise SystemExit
        if not arcpy.Exists(fr"{project_gdb}"):
            raise SystemExit(line_info(f"{os.path.basename(project_gdb)} is missing!!"))
        else:
            pass

        ##        # Write to File
        ##        with open('fieldDefinitions.json', 'w') as json_file:
        ##            json.dump(fieldDefinitions(), json_file, indent=4)
        ##        del json_file
        ##
        ##        # Write to File
        ##        with open('tableDefinitions.json', 'w') as json_file:
        ##            json.dump(tableDefinitions(), json_file, indent=4)
        ##        del json_file

        ##        # Read a File
        ##        with open('fieldDefinitions.json', 'r') as json_file:
        ##            field_definitions = json.load(json_file)
        ##            for field_definition in field_definitions:
        ##                print(f'Field: {field_definition}')
        ##                for key in field_definitions[field_definition]:
        ##                    print(f"\t{key:<17} : {field_definitions[field_definition][key]}")
        ##                del field_definition
        ##            #del field_definitions
        ##        del json_file

        ##        # Read a File
        ##        with open('tableDefinitions.json', 'r') as json_file:
        ##            table_definitions = json.load(json_file)
        ##            for table_definition in table_definitions:
        ##                print(f"Table: {table_definition}")
        ##                table_fields = table_definitions[table_definition]
        ##                for table_field in table_fields:
        ##                    #print(f"\tField Name: {field}")
        ##                    print(f"\tField Name: {table_field:<17}")
        ##                    for key in field_definitions[table_field]:
        ##                        print(f"\t\t{key:<17} : {field_definitions[table_field][key]}")
        ##                        del key
        ##                    del table_field
        ##                del table_fields
        ##                del table_definition
        ##            del table_definitions
        ##        del json_file
        ##        del field_definitions
        ##
        ##        # Read a File
        ##        with open('fieldDefinitions.json', 'r') as json_file:
        ##            field_definitions = json.load(json_file)
        ##        del json_file
        ##
        ##        # Read a File
        ##        with open('tableDefinitions.json', 'r') as json_file:
        ##            table_definitions = json.load(json_file)
        ##        del json_file
        ##
        ##        # print(field_definitions["Species"]["field_name"])
        ##        print(table_definitions["Datasets"])
        ##
        ##        del field_definitions
        ##        del table_definitions

        ##        project_name = os.path.basename(os.path.dirname(csv_data_folder))
        ##        print(project_name)
        ##        print(date_code(date_code(project_name)))
        ##        del project_name

        # # # ###--->>>

        ##        #tables = ["Datasets", "WC_GLMME"]
        ##        tables = ["Datasets", "DisMAP_Regions", "AI_IDW", "WC_GFDL", "WC_GLMME"]
        ##        for table in tables:
        ##            field_csv_dtypes = dTypesCSV(csv_data_folder, table)
        ##
        ##            print(table)
        ##            for field_csv_dtype in field_csv_dtypes:
        ##                print(f"\t{field_csv_dtype}"); del field_csv_dtype
        ##            del field_csv_dtypes
        ##
        ##            field_gdb_dtypes = dTypesGDB(csv_data_folder, table)
        ##            for field_gdb_dtype in field_gdb_dtypes:
        ##                print(f"\t{field_gdb_dtype}"); del field_gdb_dtype
        ##            del field_gdb_dtypes
        ##
        ##            del table
        ##        del tables

        ##        field_definitions = fieldDefinitions(csv_data_folder, "")
        ##        for field in field_definitions:
        ##            print(field)
        ##            print(f"\t{field_definitions[field]}")
        ##            del field
        ##        del field_definitions

##        # First Test
##        table_definitions = table_definitions(csv_data_folder, "")
##        #print(table_definitions)
##        for table in table_definitions:
##            print(table)
##            print(f"\t{table_definitions[table]}");
##            del table
##        del table_definitions

        ##        # Second Test
        ##        table_definition = tableDefinitions(csv_data_folder, "WC_GLMME")
        ##        print(table_definition); del table_definition
        ##
        ##        #table = "DataSets"
        ##        #print(table_definitions[table])
        ##        #print(f"\t"); del table

        ##        # Third Test
        ##        tables = ["Datasets", "DisMAP_Regions", "AI_IDW", "WC_GFDL", "WC_GLMME"]
        ##        for table in tables:
        ##            table_definition = tableDefinitions(csv_data_folder, table)
        ##            print(f"Table: {table}:\n\t{', '.join(table_definition)}"); del table_definition
        ##            del table
        ##        del tables

        ##        field = "DMSLat"
        ##        field_definitions = fieldDefinitions(csv_data_folder, field)
        ##        if field_definitions:
        ##            for field in field_definitions:
        ##                print(field)
        ##                #print(f"\t{field_definitions[field]}")
        ##                del field
        ##        else:
        ##            print(f"Field: {field} is not in fieldDefinitions")
        ##        del field_definitions, field

        ##        import dismap
        ##
        ##        csv_file=r"C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\April 1 2023\CSV Data\Datasets.csv"
        ##        #csv_file=r"C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\April 1 2023\CSV Data\Species_Filter.csv"
        ##
        ##        table           = os.path.basename(csv_file).replace(".csv", "")
        ##        csv_data_folder = os.path.dirname(csv_file)
        ##        project_folder  = os.path.dirname(csv_data_folder)
        ##        project         = os.path.basename(project_folder)
        ##        #version         = project[7:]
        ##
        ##        arcpy.AddMessage(f"\tProject GDB: DisMAP {project}.gdb")
        ##        gdb = os.path.join(project_folder, f"{project}.gdb")
        ##
        ##        arcpy.env.overwriteOutput = True
        ##        arcpy.env.parallelProcessingFactor = "100%"
        ##        arcpy.env.scratchWorkspace = rf"Scratch\scratch.gdb"
        ##        arcpy.env.workspace = gdb
        ##        arcpy.SetLogMetadata(True)
        ##
        ##        field_csv_dtypes = dTypesCSV(csv_data_folder, table)
        ##        field_gdb_dtypes = dTypesGDB(csv_data_folder, table)
        ##
        ##        arcpy.AddMessage(f"\tCreating Table: {table}")
        ##        arcpy.management.CreateTable(gdb, f"{table}", "", "", table.replace("_", " "))
        ##
        ##        in_table = os.path.join(gdb, table)
        ##
        ##        #add_fields(in_table)
        ##        #alterFields(in_table)
        ##        basic_metadata(in_table)
        ##        export_metadata(in_table)
        ##
        ##        del csv_file, table, project_folder, project, gdb
        ##        del field_csv_dtypes, field_gdb_dtypes
        ##        del dismap, in_table

##    # ###--->>>
##        dataset = r'C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\May 1 2024\CRFs\NBS_IDW.crf'
##        import_metadata(dataset)
##    # ###--->>>

##    # ###--->>>
##        # Update Dataset Metadata Dictionary
##        datasets_dict = dataset_title_dict(project_gdb)
##
##        # Write to File
##        with open(rf"{csv_data_folder}\metadata_dictionary.json", "w") as json_file:
##            json.dump(datasets_dict, json_file, indent=4)
##        del json_file
##
##        # Read a File
##        with open(rf"{csv_data_folder}\metadata_dictionary.json", "r") as json_file:
##            datasets_dict = json.load(json_file)
##        del json_file
##
##        for dataset in sorted(datasets_dict):
##            print(f"Table: {dataset}")
##            print(f"\tDataset Service:       {datasets_dict[dataset]['Dataset Service']}")
##            print(f"\tDataset Service Title: {datasets_dict[dataset]['Dataset Service Title']}")
##            print(F"\tTags:                  {datasets_dict[dataset]['Tags']}")
##            print(F"\tSummary:               {datasets_dict[dataset]['Summary']}")
##            print(F"\tDescription:           {datasets_dict[dataset]['Description']}")
##            #print(F"\tCredits:               {datasets_dict[dataset]['Credits']}")
##            #print(F"\tAccess Constraints:    {datasets_dict[dataset]['Access Constraints']}")
##            print(f"{'-'*80}")
##
##            # dataset_md.synchronize("NOT_CREATED", 0)
##            # dataset_md.title             = metadata_dictionary[table]["md_title"]
##            # dataset_md.tags              = metadata_dictionary[table]["md_tags"]
##            # dataset_md.summary           = metadata_dictionary[table]["md_summary"]
##            # dataset_md.description       = metadata_dictionary[table]["md_description"]
##            # dataset_md.credits           = metadata_dictionary[table]["md_credits"]
##            # dataset_md.accessConstraints = metadata_dictionary[table]["md_access_constraints"]
##
##            del dataset
##        del datasets_dict
##
##    # ###--->>>

##    # ###--->>>
##        dataset = r'C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\May 1 2024\May 1 2024.gdb\Datasets'
##        import_metadata(dataset)
##        del dataset
##    # ###--->>>

##    # ###--->>>
##        from arcpy import metadata as md
##
##        arcpy.env.overwriteOutput = True
##        arcpy.env.workspace = rf"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\DisMAP.gdb"
##
##        arcpy.management.CreateFeatureclass(arcpy.env.workspace, "temp_fc", "POLYGON")
##        dataset = rf"{arcpy.env.workspace}\temp_fc"
##        dataset_xml = r'C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\May 1 2024\ArcGIS Metadata\temp_fc.xml'
##        new_md_xml = r'C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\May 1 2024\ArcGIS Metadata\new_md.xml'
##
##        dataset_md = md.Metadata(dataset)
##        dataset_md.saveAsXML(dataset_xml.replace(".xml", " no sync.xml"))
##        pretty_format_xml_file(dataset_xml.replace(".xml", " no sync.xml"))
##
##        new_md.saveAsXML(new_md_xml)
##        pretty_format_xml_file(new_md_xml)
##        #if not dataset_md.isReadOnly:
##        dataset_md.copy(new_md)
##        dataset_md.synchronize("ACCESSED")
##        dataset_md.save()
##        dataset_md.reload()
##        del new_md, new_md_xml
##
##        dataset_md.saveAsXML(dataset_xml.replace(".xml", " new data.xml"))
##        pretty_format_xml_file(dataset_xml.replace(".xml", " new data.xml"))
##
##        del dataset_md
##        del dataset, dataset_xml
##        del md

##        # Path to new metadata XML file
##        new_dataset_path = r'C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\May 1 2024\ArcGIS Metadata\new_dataset.xml'
##        poc_template_path = r'C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\May 1 2024\ArcGIS Metadata\poc_template.xml'
##
##        # Create a new Metadata object, add some content to it, and then save
##        new_md = md.Metadata()
##        new_md.title = 'My Title'
##        new_md.tags = 'Tag1, Tag2'
##        new_md.summary = 'My Summary'
##        new_md.description = 'My Description'
##        new_md.credits = 'My Credits'
##        new_md.accessConstraints = 'My Access Constraints'
##        #new_md.saveAsXML(new_dataset_path, "TEMPLATE")
##        #dataset_md.saveAsXML(new_dataset_path)
##        #del dataset_md
##
##        # Create the dataset metadata object
##        dataset_md = md.Metadata(dataset)
##        dataset_md.synchronize("ALWAYS")
##        dataset_md.save()
##        dataset_md.reload()
##        dataset_md.saveAsXML(dataset_xml)
##        if not dataset_md.isReadOnly:
##            dataset_md.copy(new_md)
##            dataset_md.synchronize("NOT_CREATED")
##            dataset_md.save()
##            dataset_md.reload()
##        dataset_md.synchronize("NOT_CREATED")
##        dataset_md.copy(new_md)
##        dataset_md.save()
##        dataset_md.reload()
##        # Create the POC metadata object
##        #poc_template_md = md.Metadata(poc_template_path)
##
##        #Copy the POC metadata to the dataset metadata object
##        # Copy Start
##        #dataset_md.synchronize("ACCESSED", 0) # With copy and ACCESSED the POC overwites all metadata content
##        #dataset_md.synchronize("ALWAYS") # With copy and ALWAYS the POC overwites all metadata content
##        #dataset_md.synchronize("CREATED") # With copy and CREATED the POC overwites all metadata content
##        #dataset_md.synchronize("NOT_CREATED") # With copy and NOT_CREATED the POC overwites all metadata content
##        #dataset_md.synchronize("OVERWRITE") # With copy and OVERWRITE the POC overwites all metadata content
##        #dataset_md.synchronize("SELECTIVE") # With copy and SELECTIVE the POC overwites all metadata content
##        # Copy End
##        # Import Start
##        #dataset_md.synchronize("ACCESSED", 0) # With import and ACCESSED the POC is mergeed, but with only the XML flag
##        #dataset_md.synchronize("ALWAYS") # With import and ALWAYS the POC is mergeed, but with only the XML flag
##        #dataset_md.synchronize("CREATED") # With import and CREATED the POC is mergeed, but with only the XML flag
##        #dataset_md.synchronize("NOT_CREATED") # With import and NOT_CREATED POC is mergeed, but with only the XML flag
##        #dataset_md.synchronize("OVERWRITE") # With import and OVERWRITE the POC is mergeed, but with only the XML flag
##        #dataset_md.synchronize("SELECTIVE") # With import and SELECTIVE the POC is mergeed, but with only the XML flag
##        # Import End
##        #if not dataset_md.isReadOnly:
##        #    dataset_md.copy(poc_template_md)
##            #dataset_md.importMetadata(poc_template_md)
##        # Copy Start
##        #dataset_md.synchronize("ACCESSED", 0) # With copy and ACCESSED the POC overwites all metadata content
##        #dataset_md.synchronize("ALWAYS") # With copy and ALWAYS the POC overwites all metadata content
##        #dataset_md.synchronize("CREATED") # With copy and CREATED the POC overwites all metadata content
##        #dataset_md.synchronize("NOT_CREATED") # With copy and NOT_CREATED the POC overwites all metadata content
##        #dataset_md.synchronize("OVERWRITE") # With copy and OVERWRITE the POC overwites all metadata content
##        #dataset_md.synchronize("SELECTIVE") # With copy and SELECTIVE the POC overwites all metadata content
##        # Copy End
##        # Import Start
##        #dataset_md.synchronize("ACCESSED", 0) # With import and ACCESSED the POC is mergeed, but with only the XML flag
##        #dataset_md.synchronize("ALWAYS") # With import and ALWAYS the POC is mergeed, but with only the XML flag
##        #dataset_md.synchronize("CREATED") # With import and CREATED the POC is mergeed, but with only the XML flag
##        #dataset_md.synchronize("NOT_CREATED") # With import and NOT_CREATED POC is mergeed, but with only the XML flag
##        #dataset_md.synchronize("OVERWRITE") # With import and OVERWRITE the POC is mergeed, but with only the XML flag
##        #dataset_md.synchronize("SELECTIVE") # With import and SELECTIVE the POC is mergeed, but with only the XML flag
##        # Import End
##        #dataset_md.save()
##        #dataset_md.reload()
##        #out_xml = new_dataset_path.replace(".xml", " copy do nothing .xml")
##        dataset_md.saveAsXML(new_dataset_path)
##        #dataset_md.saveAsXML(new_dataset_path.replace(".xml", " import SELECTIVE after.xml"))
##        del dataset_md, poc_template_path
##        #del poc_template_md
##
##        pretty_format_xml_file(new_dataset_path)
##        pretty_format_xml_file(dataset_xml)
##        #del out_xml
##
##        del new_dataset_path, dataset_xml
##        del md
##        del dataset, new_md
##
##    # ###--->>>

##    # ###--->>> COMPARE TWO XML DOCUMENTS
##        # This requires use of the clone ArcGIS Pro arcpy.env.
##        # https://buildmedia.readthedocs.org/media/pdf/xmldiff/latest/xmldiff.pdf
##        table                  = "DisMAP_Regions"
##        project_folder         = os.path.dirname(project_gdb)
##        export_metadata_folder = rf"{project_folder}\ArcGIS Metadata"
##
##        in_xml  = r"C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\May 1 2024\ArcGIS Metadata\DisMAP_Regions.xml"
##        out_xml = r"C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\May 1 2024\ArcGIS Metadata\DisMAP Regions Current.xml"
##
##        diff = compare_metadata_xml(in_xml, out_xml)
##        if diff:
##            diff_metadata = rf"{export_metadata_folder}\{table} EXACT_COPY DIFF of Import.xml"
##            with open(diff_metadata, "w") as f:
##                f.write(diff)
##                del f
##            del diff_metadata
##        else:
##            pass
##
##        del diff
##
##        del in_xml, out_xml
##        del table, project_folder, export_metadata_folder
##    # ###--->>> COMPARE TWO XML DOCUMENTS

        #pretty_format_xml_file(r"C:\Users\john.f.kennedy\AppData\Local\ESRI\ArcGISPro\Staging\SharingProcesses\SharingMainLog - Copy.xml")
        #pretty_format_xml_file(r"C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\July 1 2024\Export Metadata\EBS_IDW.crf.xml")

## Doesn't really work
##        # ###--->>>
##        def xml_json_test(project_gdb, metadata_xml):
##
##            from xml.dom import minidom
##            import json
##
##            project_folder         = os.path.dirname(project_gdb)
##            metadata_folder        = rf"{project_folder}\ArcGIS Metadata"
##            export_metadata_folder = rf"{project_folder}\Export Metadata"
##            metadata_xml_path      = rf"{metadata_folder}\{metadata_xml}"
##
##            def parse_element(element):
##                dict_data = dict()
##                if element.nodeType == element.TEXT_NODE:
##                    dict_data['data'] = element.data
##                if element.nodeType not in [element.TEXT_NODE, element.DOCUMENT_NODE,
##                                            element.DOCUMENT_TYPE_NODE]:
##                    for item in element.attributes.items():
##                        dict_data[item[0]] = item[1]
##                if element.nodeType not in [element.TEXT_NODE, element.DOCUMENT_TYPE_NODE]:
##                    for child in element.childNodes:
##                        child_name, child_dict = parse_element(child)
##                        if child_name in dict_data:
##                            try:
##                                dict_data[child_name].append(child_dict)
##                            except AttributeError:
##                                dict_data[child_name] = [dict_data[child_name], child_dict]
##                        else:
##                            dict_data[child_name] = child_dict
##                return element.nodeName, dict_data
##
##            #dom = minidom.parse('data.xml')
##            #f = open('data.json', 'w')
##            dom = minidom.parse(metadata_xml_path)
##            f = open(rf"{export_metadata_folder}\{metadata_xml.replace('.xml', '.json')}", "w")
##            f.write(json.dumps(parse_element(dom), sort_keys=True, indent=4))
##            f.close()
##
##            del minidom, json
##
##        metadata_xml = "AI_Sample_Locations_20230401.xml"
##
##        xml_json_test(project_gdb, metadata_xml)
##
##        del metadata_xml, xml_json_test
##
##        # ###--->>>


##    # ###--->>>
##        from arcpy import metadata as md
##
##        arcpy.env.overwriteOutput = True
##        arcpy.env.workspace = rf"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\DisMAP.gdb"
##
##        arcpy.management.CreateFeatureclass(arcpy.env.workspace, "temp_fc", "POLYGON")
##        dataset = rf"{arcpy.env.workspace}\temp_fc"
##        dataset_xml = r"C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\May 1 2024\Export Metadata\temp_fc.xml"
##        new_md_xml = r"C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\May 1 2024\Export Metadata\new_md.xml"
##
##        poc_template = r"C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\May 1 2024\ArcGIS Metadata\poc_template.xml"
##
## #        dataset_md = md.Metadata(dataset)
## #        dataset_md.saveAsXML(dataset_xml.replace(".xml", " no sync.xml"))
## #        pretty_format_xml_file(dataset_xml.replace(".xml", " no sync.xml"))
## #        dataset_md.synchronize("ALWAYS")
## #        dataset_md.save()
## #        dataset_md.reload()
## #        dataset_md.title = 'My Title'
## #        dataset_md.tags = 'Tag1, Tag2'
## #        dataset_md.summary = 'My Summary'
## #        dataset_md.description = 'My Description'
## #        dataset_md.credits = 'My Credits'
## #        dataset_md.accessConstraints = 'My Access Constraints'
## #        dataset_md.save()
## #        dataset_md.reload()
## #        dataset_md.saveAsXML(dataset_xml.replace(".xml", " ALWAYS sync.xml"))
## #        pretty_format_xml_file(dataset_xml.replace(".xml", " ALWAYS sync.xml"))
##
##        #del dataset_md
##        #dataset_md = md.Metadata(dataset)
##
##        # Create a new Metadata object, add some content to it, and then save
##        new_md = md.Metadata()
## #        new_md.title = 'My Title'
## #        new_md.tags = 'Tag1, Tag2'
## #        new_md.summary = 'My Summary'
## #        new_md.description = 'My Description'
## #        new_md.credits = 'My Credits'
## #        new_md.accessConstraints = 'My Access Constraints'
##        new_md.importMetadata(new_md_xml)
##        new_md.importMetadata(poc_template)
##        #new_md.save()
##        #new_md.reload()
##        new_md.saveAsXML(new_md_xml)
##        pretty_format_xml_file(new_md_xml)
##
##        del new_md
##
## #        dataset_md.synchronize("ACCESSED")
## #        dataset_md.importMetadata(new_md_xml)
## #        dataset_md.synchronize("CREATED")
## #        dataset_md.save()
## #        dataset_md.reload()
## #
## #        del dataset_md
## #        dataset_md = md.Metadata(dataset)
## #
## #        dataset_md.importMetadata(poc_template)
## #        #dataset_md.save()
## #        #dataset_md.reload()
## #        #dataset_md.synchronize("ALWAYS")
## #        #dataset_md.synchronize("SELECTIVE")
## #        dataset_md.save()
## #        dataset_md.reload()
##
##
##        del new_md_xml
##        del poc_template
##
## #        # Delete all geoprocessing history and any enclosed files from the item's metadata
## #        #dataset_md.deleteContent('GPHISTORY')
## #        #dataset_md.deleteContent('ENCLOSED_FILES')
## #
## #        #dataset_md.saveAsXML(dataset_xml.replace(".xml", " new data.xml"))
## #        dataset_md.saveAsXML(dataset_xml.replace(".xml", " new data.xml"), "REMOVE_MACHINE_NAMES")
## #        pretty_format_xml_file(dataset_xml.replace(".xml", " new data.xml"))
## #
## #        del dataset_md
##
##        del dataset, dataset_xml
##        del md
##    # ###--->>>

##    # ###--->>>
##        from arcpy import metadata as md
##
##        metadata_folder = r"C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\May 1 2024\Export Metadata"
##        new_md_xml      = rf"{metadata_folder}\new_md.xml"
##        dataset_md_xml  = rf"{metadata_folder}\dataset_md.xml"
##
##        # Create a new Metadata object, add some content to it, and then save
##        new_md = md.Metadata()
##        new_md.title = 'My Title'
##        new_md.tags = 'Tag1, Tag2'
## #        new_md.summary = 'My Summary'
## #        new_md.description = 'My Description'
## #        new_md.credits = 'My Credits'
## #        new_md.accessConstraints = 'My Access Constraints'
##        new_md.saveAsXML(new_md_xml)
##        pretty_format_xml_file(new_md_xml)
##        new_md.saveAsXML(dataset_md_xml)
##        pretty_format_xml_file(dataset_md_xml)
##        del new_md
##
##        dataset_md = md.Metadata(dataset_md_xml)
##        dataset_md.importMetadata("""<?xml version="1.0"?><metadata xml:lang="en"><Esri><CreaDate>20240701</CreaDate><CreaTime>00000000</CreaTime><ArcGISFormat>1.0</ArcGISFormat><SyncOnce>FALSE</SyncOnce></Esri></metadata>""")
##        dataset_md.synchronize("NOT_CREATED")
##        dataset_md.save()
##        dataset_md.reload()
##        dataset_md.saveAsXML(dataset_md_xml)
##        pretty_format_xml_file(dataset_md_xml)
##        del dataset_md
##
##        # Variables
##        del dataset_md_xml
##        del new_md_xml
##        del metadata_folder
##
##        # Imports
##        del md
##
##    # ###--->>>

##    # ###--->>>
##        import datetime
##        import pytz
##
##        #unaware = datetime.datetime(2011, 8, 15, 8, 15, 12, 0)
##        #aware = datetime.datetime(2011, 8, 15, 8, 15, 12, 0, pytz.UTC)
##
##        unaware = datetime.datetime(2011, 1, 1, 0, 0, 0, 0)
##        aware = datetime.datetime(2011, 1, 1, 0, 0, 0, 0, pytz.UTC)
##
##
##        now_aware = pytz.utc.localize(unaware)
##        assert aware == now_aware
##
##        print(now_aware)
##
##        from datetime import datetime, timezone
##
##        dt = datetime(2011, 1, 1, 0, 0, 0, 0)
##        dt = dt.replace(tzinfo=timezone.utc)
##        print(dt.isoformat())
##
##        del datetime, timezone, dt
##
##
##        import pandas as pd
##        df = pd.DataFrame({"Year": [2014, 2015, 2016],})
##        #df.insert(df.columns.get_loc("Year")+1, "StdTime", pd.to_datetime(df["Year"], format="%Y").dt.tz_localize('Etc/GMT'))
##        df.insert(df.columns.get_loc("Year")+1, "StdTime", pd.to_datetime(df["Year"], format="%Y", utc=True))
##        #df.insert(df.columns.get_loc("Year")+1, "StdTime", pd.to_datetime(df["Year"], format="%Y"))
##
##        print(df)
##
##        del pd, df
##    # ###--->>>

        # Function parameters
        del project_gdb

        results = True

    except KeyboardInterrupt:
        raise Exception
    except arcpy.ExecuteWarning:
        raise Exception(arcpy.GetMessages())
    except arcpy.ExecuteError:
        raise Exception(arcpy.GetMessages())
    except Exception as e:
        raise Exception(e)
    except:
        traceback.print_exc()
        raise Exception
        # Get the traceback object
##        tb = sys.exc_info()[2]
##        tbinfo = traceback.format_tb(tb)[0]
##        # Concatenate information together concerning the error into a message string
##        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
##        arcpy.AddError(pymsg)
    else:
        try:
            leave_out_keys = ["leave_out_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys
            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
        except:
            traceback.print_exc()
    finally:
        if "results" in locals().keys(): del results

def main(project=""):
    try:
        arcpy.env.overwriteOutput = True
        arcpy.env.parallelProcessingFactor = "100%"

        base_project_folder = os.path.dirname(os.path.dirname(__file__))
        project_gdb         = rf"{base_project_folder}\{project}\{project}.gdb"

        del base_project_folder

        # Test if passed workspace exists, if not raise SystemExit
        if not arcpy.Exists(project_gdb):
            raise SystemExit(line_info(f"{os.path.basename(project_gdb)} is missing!!"))
        else:
            pass

##    # ###--->>>
##        from arcpy import metadata as md
##
##        project_folder = os.path.dirname(project_gdb)
##
##        metadata_folder = rf"{project_folder}\Export Metadata"
##        new_md_xml      = rf"{metadata_folder}\new_md.xml"
##        dataset_md_xml  = rf"{metadata_folder}\dataset_md.xml"
##
##        # Create a new Metadata object, add some content to it, and then save
##        new_md = md.Metadata()
##        #new_md.title = 'My Title'
##        new_md.tags = 'Tag1, Tag2'
##        new_md.summary = 'My Summary'
##        new_md.description = 'My Description'
##        new_md.credits = 'My Credits'
##        new_md.accessConstraints = 'My Access Constraints'
##        # Save the original
##        new_md.saveAsXML(new_md_xml)
##
##        # Pretty Format
##        pretty_format_xml_file(new_md_xml)
##
##        # Save a copy to modify
##        new_md.saveAsXML(dataset_md_xml)
##
##        # Pretty Format
##        pretty_format_xml_file(dataset_md_xml)
##        del new_md
##
##        dataset_md = md.Metadata(dataset_md_xml)
##        #dataset_md.synchronize("ALWAYS")
##        #dataset_md.importMetadata("""<?xml version="1.0"?><metadata xml:lang="en"><Esri><CreaDate>20240701</CreaDate><CreaTime>00000000</CreaTime><ArcGISFormat>1.0</ArcGISFormat><SyncOnce>FALSE</SyncOnce></Esri></metadata>""")
##        #dataset_md.importMetadata(md.Metadata("""<metadata xml:lang="en"><dataIdInfo><idCitation><resTitle>My Title</resTitle></idCitation></dataIdInfo></metadata>"""))
##
##        #dataset_md.synchronize("SELECTIVE")
##        #dataset_md.importMetadata(rf"{metadata_folder}\AI_IDW_Sample_Locations.xml")
##        #dataset_md.synchronize("CREATED")
##
##        #dataset_md.synchronize("CREATED")
##        #dataset_md.save()
##        #dataset_md.reload()
##        dataset_md.importMetadata(rf"{metadata_folder}\poc_template.xml")
##        dataset_md.save()
##        dataset_md.synchronize("SELECTIVE")
##        #print(dataset_md.xml)
##        #dataset_md.save()
##        #dataset_md.reload()
##        # Save the modified file
##        #dataset_md.saveAsXML(dataset_md_xml)
##
##        # Pretty Format
##        pretty_format_xml_file(dataset_md_xml)
##
##        del dataset_md
##
##        # Variables
##        del dataset_md_xml
##        del new_md_xml
##        del metadata_folder, project_folder
##
##        # Imports
##        del md
##
##    # ###--->>>

##    # ###--->>>
##
##        project_folder  = os.path.dirname(project_gdb)
##        metadata_folder = rf"{project_folder}\Export Metadata"
##        xml_file_1      = rf"{metadata_folder}\AI_IDW_Sample_Locations.xml"
##        xml_file_2      = rf"{metadata_folder}\poc_template.xml"
##
##        xml_combiner(project_gdb=project_gdb, xml_file_1=xml_file_1, xml_file_2=xml_file_2)
##
##        del project_folder, metadata_folder
##        del xml_file_1, xml_file_2
##
##    # ###--->>>

##    # ###--->>>
##
##        from arcpy import metadata as md
##
##        project_folder  = os.path.dirname(project_gdb)
##        metadata_folder = rf"{project_folder}\Export Metadata"
##
##        # ArcPy Environments
##        arcpy.env.overwriteOutput             = True
##        arcpy.env.parallelProcessingFactor = "100%"
##        arcpy.env.workspace                = project_gdb
##        arcpy.env.scratchWorkspace         = rf"Scratch\scratch.gdb"
##        arcpy.SetLogMetadata(True)
##
##        metadata_dictionary = dataset_title_dict(project_gdb)
##
##        dataset = rf"{project_gdb}\DisMAP_Regions"
##        table = os.path.basename(dataset)
##
##        # #arcpy.conversion.FeaturesToJSON(
##        # #                                in_features      = dataset,
##        # #                                out_json_file    = rf"{metadata_folder}\{table}.json",
##        # #                                format_json      = "FORMATTED",
##        # #                                include_z_values = "NO_Z_VALUES",
##        # #                                include_m_values = "NO_M_VALUES",
##        # #                                geoJSON          = "NO_GEOJSON",
##        # #                                outputToWGS84    = "KEEP_INPUT_SR",
##        # #                                use_field_alias  = "USE_FIELD_NAME"
##        # #                               )


##        arcpy.AddMessage(f"JSON To Features")
##
##        arcpy.conversion.JSONToFeatures(
##                                        in_json_file  = rf"{metadata_folder}\{table}.json",
##                                        out_features  = dataset,
##                                        geometry_type = "POLYLINE"
##                                       )

##        arcpy.AddMessage(f"Dataset: {table}")
##
##        dataset_md = md.Metadata(dataset)
##        #dataset_md.xml = '<metadata xml:lang="en"><Esri><CreaDate>20240701</CreaDate><CreaTime>00000000</CreaTime><ArcGISFormat>1.0</ArcGISFormat><SyncOnce>FALSE</SyncOnce></Esri></metadata>'
##        dataset_md.synchronize("ALWAYS")
##        out_xml = rf"{metadata_folder}\{table}_Step_1.xml"
##        dataset_md.saveAsXML(out_xml)
##
##        pretty_format_xml_file(out_xml)
##        del out_xml
##
##        dataset_md.importMetadata(rf"{metadata_folder}\poc_john.xml")
##        dataset_md.synchronize("SELECTIVE")
##        dataset_md.save()
##        dataset_md.reload()
##        out_xml = rf"{metadata_folder}\{table}_Step_2.xml"
##        dataset_md.saveAsXML(out_xml)
##
##        pretty_format_xml_file(out_xml)
##        del out_xml
##
##        dataset_md.title             = metadata_dictionary[table]["Dataset Service Title"]
##        dataset_md.tags              = metadata_dictionary[table]["Tags"]
##        dataset_md.summary           = metadata_dictionary[table]["Summary"]
##        dataset_md.description       = metadata_dictionary[table]["Description"]
##        dataset_md.credits           = metadata_dictionary[table]["Credits"]
##        dataset_md.accessConstraints = metadata_dictionary[table]["Access Constraints"]
##        dataset_md.save()
##        dataset_md.reload()
##        out_xml = rf"{metadata_folder}\{table}_Step_3.xml"
##        dataset_md.saveAsXML(out_xml)
##
##        pretty_format_xml_file(out_xml)
##        del out_xml
##
##        del dataset_md


##        # print(f"\tDataset Service:       {datasets_dict[dataset]['Dataset Service']}")
##        # print(f"\tDataset Service Title: {datasets_dict[dataset]['Dataset Service Title']}")
##
## #        # https://pro.arcgis.com/en/pro-app/latest/arcpy/metadata/metadata-class.htm
## #        dataset_md = md.Metadata(dataset)
## #        dataset_md.xml = '<metadata xml:lang="en"></metadata>'
## #        dataset_md.save()
## #        #dataset_md.synchronize("ALWAYS")
## #        dataset_md.save()
## #        del dataset_md
## #
## #        dataset_md = md.Metadata(dataset)
## #        dataset_md.importMetadata(rf"{metadata_folder}\poc_template.xml")
## #        dataset_md.save()
## #        del dataset_md
## #
## #        dataset_md = md.Metadata(dataset)
## #        dataset_md.synchronize("ALWAYS")
## #        dataset_md.importMetadata(rf"{metadata_folder}\dismap_regions_entity.xml")
## #        dataset_md.save()
## #        del dataset_md
##
##        dataset_md = md.Metadata(dataset)
##        dataset_md.synchronize("ALWAYS")
##        dataset_md.save()
##        dataset_md.reload()
##        #dataset_md.synchronize("SELECTIVE")
##        dataset_md.title             = metadata_dictionary[table]["Dataset Service Title"]
##        dataset_md.tags              = metadata_dictionary[table]["Tags"]
##        dataset_md.summary           = metadata_dictionary[table]["Summary"]
##        dataset_md.description       = metadata_dictionary[table]["Description"]
##        dataset_md.credits           = metadata_dictionary[table]["Credits"]
##        dataset_md.accessConstraints = metadata_dictionary[table]["Access Constraints"]
##        dataset_md.save()
##        del dataset_md
##
##        dataset_md = md.Metadata(dataset)
##
##        # Delete all geoprocessing history and any enclosed files from the item's metadata
##        #dataset_md.deleteContent('GPHISTORY')
##        #dataset_md.deleteContent('ENCLOSED_FILES')
##        #dataset_md.save()
##        #dataset_md.reload()
##
##        #out_xml = rf"{metadata_folder}\{dataset_md.title}.xml"
##        out_xml = rf"{metadata_folder}\{table}.xml"
##        dataset_md.saveAsXML(out_xml, "REMOVE_ALL_SENSITIVE_INFO")
##        #dataset_md.saveAsXML(out_xml, "REMOVE_MACHINE_NAMES")
##        #dataset_md.saveAsXML(out_xml)
##
##        pretty_format_xml_file(out_xml)
##        del out_xml
##
##        del dataset_md
##
## #        arcpy.AddMessage(f"Dataset: {table}")
## #        dataset_md_path = rf"{metadata_folder}\{table}.xml"
## #        if arcpy.Exists(dataset_md_path):
## #            arcpy.AddMessage(f"\tMetadata File: {os.path.basename(dataset_md_path)}")
## #            from arcpy import metadata as md
## #            try:
## #                dataset_md = md.Metadata(dataset)
## #                # Import the standard-format metadata content to the target item
## #                if not dataset_md.isReadOnly:
## #                    dataset_md.importMetadata(dataset_md_path, "ARCGIS_METADATA")
## #                    dataset_md.save()
## #                    dataset_md.reload()
## #                    dataset_md.title = title
## #                    dataset_md.save()
## #                    dataset_md.reload()
## #
## #                arcpy.AddMessage(f"\tExporting metadata file from {table}")
## #
## #                out_xml = rf"{project_folder}\Export Metadata\{title} EXACT_COPY.xml"
## #                dataset_md.saveAsXML(out_xml, "EXACT_COPY")
## #
## #                pretty_format_xml_file(out_xml)
## #                del out_xml
## #
## #                del dataset_md, md
## #
## #            except:
## #                arcpy.AddError(f"\tDataset metadata import error!! {arcpy.GetMessages()}")
## #        else:
## #            arcpy.AddWarning(f"\tDataset missing metadata file!!")

##        del md
##        del project_folder, metadata_folder, metadata_dictionary
##        del dataset, table
##
##    # ###--->>>


##    # ###--->>>
##        from arcpy import metadata as md
##
##        base_project_folder = os.path.dirname(os.path.dirname(__file__))
##        project_gdb         = rf"{base_project_folder}\{project}\{project}.gdb"
##        workspace           = rf"{base_project_folder}\DisMAP.gdb"
##
##        arcpy.env.overwriteOutput = True
##        arcpy.env.workspace = workspace
##
##        arcpy.management.CreateFeatureclass(arcpy.env.workspace, "temp_fc", "POLYGON")
##
##        dataset     = rf"{workspace}\temp_fc"
##        dataset_xml = rf"{base_project_folder}\{project}\Export Metadata\temp_fc.xml"
##
##        dataset_md = md.Metadata(dataset)
##        dataset_md.saveAsXML(dataset_xml.replace(".xml", " no sync.xml"), "REMOVE_ALL_SENSITIVE_INFO")
##        pretty_format_xml_file(dataset_xml.replace(".xml", " no sync.xml"))
##
##        dataset_md.synchronize("ALWAYS")
##        dataset_md.save()
##
##        dataset_md.saveAsXML(dataset_xml.replace(".xml", " ALWAYS.xml"), "REMOVE_ALL_SENSITIVE_INFO")
##        pretty_format_xml_file(dataset_xml.replace(".xml", " ALWAYS.xml"))
##
##        dataset_md.title = 'My Title'
##        dataset_md.tags = 'Tag1, Tag2'
##        dataset_md.summary = 'My Summary'
##        dataset_md.description = 'My Description'
##        dataset_md.credits = 'My Credits'
##        dataset_md.accessConstraints = 'My Access Constraints'
##        dataset_md.save()
##        dataset_md.saveAsXML(dataset_xml.replace(".xml", " Title added.xml"), "REMOVE_ALL_SENSITIVE_INFO")
##        pretty_format_xml_file(dataset_xml.replace(".xml", " Title added.xml"))
##
##        del dataset, dataset_xml
##        del dataset_md
##        del md
##        del base_project_folder, workspace
##    # ###--->>>

##        base_project_folder = os.path.dirname(os.path.dirname(__file__))
##
##        pretty_format_xml_files(rf"{base_project_folder}\{project}\Current Metadata")
##        #pretty_format_xml_files(rf"{base_project_folder}\{project}\ArcGIS Metadata")
##        #pretty_format_xml_files(r"E:\DisMAP WI 20230426\April 1 2023\ArcGIS Metadata")
##
##        del base_project_folder


##    # ###--->>> dataset_title_dict Test #1
##        md_dict = dataset_title_dict(project_gdb)
##
##        for key in md_dict:
##            #print(key)
##            #if "_CRF" in key:
##            print(key)
##            print(f"\tDataset Service Title: {md_dict[key]['Dataset Service Title']}")
##            print(f"\tDataset Service:       {md_dict[key]['Dataset Service']}")
##            print(f"\tTags:                  {md_dict[key]['Tags']}")
##            del key
##        del md_dict
##    # ###--->>>

##        project_folder  = os.path.dirname(project_gdb)
##        csv_data_folder = rf"{project_folder}\CSV Data"
##
##        # First Test
##        table_definitions = dismap.table_definitions(csv_data_folder, "")
##        #print(table_definitions)
##        for table in table_definitions:
##            print(table)
##            print(f"\t{table_definitions[table]}");
##            del table
##        del table_definitions
##        del project_folder, csv_data_folder


        # Function parameters
        del project_gdb
        del project

        results = True

    except KeyboardInterrupt:
        raise Exception
    except arcpy.ExecuteWarning:
        raise Exception(arcpy.GetMessages())
    except arcpy.ExecuteError:
        raise Exception(arcpy.GetMessages())
    except Exception as e:
        raise Exception(e)
    except:
        traceback.print_exc()
        raise Exception
    else:
        try:
            leave_out_keys = ["leave_out_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys
            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
        except:
            raise Exception(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

if __name__ == "__main__":
    try:
        # Import this Python module
        import dismap
        importlib.reload(dismap)

        print(f"{'-' * 90}")
        print(f"Python Script:  {os.path.basename(__file__)}")
        print(f"Location:       {os.path.dirname(__file__)}")
        print(f"Python Version: {sys.version} Environment: {os.path.basename(sys.exec_prefix)}")
        print(f"{'-' * 90}\n")

        # project = "April 1 2023"
        #project = "May 1 2024"
        #project = "July 1 2024"
        project = "December 1 2024"

        # Tested on 7/30/2024 -- PASSED
        main(project=project)

        del project

        from time import localtime, strftime

        print(f"\n{'-' * 90}")
        print(f"Python script: {os.path.basename(__file__)} successfully completed {strftime('%a %b %d %I:%M %p', localtime())}")
        print(f"{'-' * 90}")
        del localtime, strftime

    except Exception:
        pass
    except:
        traceback.print_exc()
    else:
        leave_out_keys = ["leave_out_keys", "remaining_keys"]
        leave_out_keys.extend([name for name, obj in inspect.getmembers(sys.modules[__name__]) if inspect.isfunction(obj) or inspect.ismodule(obj)])
        remaining_keys = [key for key in locals().keys() if not key.startswith("__") and key not in leave_out_keys]
        if remaining_keys:
            arcpy.AddWarning(f"Remaining Keys: ##--> '{', '.join(remaining_keys)}' <--##")
        del leave_out_keys, remaining_keys
    finally:
        pass
