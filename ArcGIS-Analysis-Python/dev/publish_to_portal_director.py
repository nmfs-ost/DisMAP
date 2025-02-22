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

sys.path.append(os.path.dirname(__file__))

def line_info(msg):
    f = inspect.currentframe()
    i = inspect.getframeinfo(f.f_back)
    return f"Script: {os.path.basename(i.filename)}\n\tNear Line: {i.lineno}\n\tFunction: {i.function}\n\tMessage: {msg}"

##def publish_dismap_regions(base_project_file="", project="", project_gdb=""):
##    try:
##        # Test if passed workspace exists, if not raise Exception
##        if not arcpy.Exists(project_gdb):
##            raise SystemExit(f"{os.path.basename(project_gdb)} is missing!!")
##
##        # Import the dismap module to access tools
##        #import dismap
##        #importlib.reload(dismap)
##
##        # Set History and Metadata logs, set serverity and message level
##        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
##        arcpy.SetLogMetadata(True)
##        arcpy.SetSeverityLevel(2) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
##                                  # 1—If a tool produces a warning or an error, it will throw an exception.
##                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
##        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION
##
##        # Set basic workkpace variables
##        project_folder    = os.path.dirname(project_gdb)
##        scratch_workspace = rf"{project_folder}\Scratch\scratch.gdb"
##
##        # Set basic workkpace variables
##        arcpy.env.workspace                = project_gdb
##        arcpy.env.scratchWorkspace         = scratch_workspace
##        arcpy.env.overwriteOutput          = True
##        arcpy.env.parallelProcessingFactor = "100%"
##
##        arcpy.AddMessage(f"\n{'-' * 90}\n")
##
##        # DatasetCode, CSVFile, TransformUnit, TableName, GeographicArea, CellSize,
##        # PointFeatureType, FeatureClassName, Region, Season, DateCode, Status,
##        # DistributionProjectCode, DistributionProjectName, SummaryProduct,
##        # FilterRegion, FilterSubRegion, FeatureServiceName, FeatureServiceTitle,
##        # MosaicName, MosaicTitle, ImageServiceName, ImageServiceTitle
##
##        # Get values for table_name from Datasets table
##        fields = ["FeatureClassName", "FeatureServiceName", "FeatureServiceTitle"]
##        region_list = [row for row in arcpy.da.SearchCursor(rf"{project_gdb}\Datasets", fields, where_clause = f"FeatureClassName = 'DisMAP_Regions'")][0]
##        del fields
##
##        # Assigning variables from items in the chosen table list
##        # ['AI_IDW', 'AI_IDW_Region', 'AI', 'Aleutian Islands', None, 'IDW']
##        featureclass_name     = region_list[0]
##        feature_service_name  = region_list[1]
##        feature_service_title = region_list[2]
##        del region_list
##
##        LogInAGOL = False
##        if LogInAGOL:
##            portal = "https://noaa.maps.arcgis.com/"
##            user = "John.F.Kennedy_noaa"
##
##            # Sign in to portal
##            #arcpy.SignInToPortal("https://www.arcgis.com", "MyUserName", "MyPassword")
##            # For example: 'http://www.arcgis.com/'
##            arcpy.SignInToPortal(portal)
##
##            arcpy.AddMessage(f"###---> Signed into Portal: {arcpy.GetActivePortalURL()} <---###")
##            del portal, user
##        del LogInAGOL
##
##        # Start of business logic for the worker function
##        arcpy.AddMessage(f"###---> Processing begins for: {feature_service_title} <---###")
##        arcpy.AddMessage(f"Feature Class Name:   {featureclass_name}")
##        arcpy.AddMessage(f"Feature Service Name: {feature_service_name}")
##
##        # Business logic for the worker function
##        arcpy.AddMessage(f"Is there a map?")
##        arcpy.AddMessage(f"Is there a layer file map?")
##        arcpy.AddMessage(f"What are the layers in the map?")
##
##        # Gather results to be returned
##        results = [f"{feature_service_title}"]
##
##        # End of business logic for the worker function
##        arcpy.AddMessage(f"###---> Processing {feature_service_title} complete <---###")
##
##        arcpy.AddMessage(f"\n{'-' * 90}\n")
##
##        # Variable assigned in function
##        del featureclass_name, feature_service_name, feature_service_title
##        del project_folder, scratch_workspace
##
##        # Function Parameter
##        del base_project_file, project, project_gdb
##
##    except SystemExit:
##        raise SystemExit
##    except:
##        traceback.print_exc()
##        raise SystemExit
##    else:
##        try:
##            import inspect
##            leave_out_keys = ["leave_out_keys", "remaining_keys", "results"]
##            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
##            if remaining_keys:
##                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
##            del leave_out_keys, remaining_keys
##
##            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
##
##        except:
##            traceback.print_exc()
##    finally:
##        try:
##            if "results" in locals().keys(): del results
##        except UnboundLocalError:
##            pass

def feature_sharing_draft_report(sd_draft=""):
    try:
        import xml.dom.minidom as DOM

        docs = DOM.parse(sd_draft)
        key_list = docs.getElementsByTagName("Key")
        value_list = docs.getElementsByTagName("Value")

        for i in range(key_list.length):
            value = f"Value: {value_list[i].firstChild.nodeValue}" if value_list[i].firstChild else f"Value is missing"

            arcpy.AddMessage(f"\t\tKey: {key_list[i].firstChild.nodeValue:<45} {value}")
            # arcpy.AddMessage(f"\t\tKey: {key_list[i].firstChild.nodeValue:<45} {value[:50]}")
            del i

        del DOM, key_list, value_list, docs
        del sd_draft

    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(arcpy.GetMessages())
        traceback.print_exc()
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages())
        traceback.print_exc()
    except Exception as e:
        print(e)
        traceback.print_exc()
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
            raise SystemExit(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

def create_feature_class_layers(base_project_file="", project=""):
    try:
        # Test if passed workspace exists, if not raise SystemExit
        if not arcpy.Exists(base_project_file):
            raise SystemExit(line_info(f"{os.path.basename(base_project_file)} is missing!!"))

        # Import
        import dismap
        importlib.reload(dismap)
        from dismap import dataset_title_dict, pretty_format_xml_file

        # Set History and Metadata logs, set serverity and message level
        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(1) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        aprx = arcpy.mp.ArcGISProject(base_project_file)
        home_folder = aprx.homeFolder

        project_gdb = rf"{home_folder}\{project}\{project}.gdb"

        # Test if passed workspace exists, if not raise SystemExit
        if not arcpy.Exists(project_gdb):
            raise SystemExit(line_info(f"{os.path.basename(project_gdb)} is missing!!"))

        # Set basic workkpace variables
        project_folder    = os.path.dirname(project_gdb)
        scratch_folder    = rf"{project_folder}\Scratch"
        scratch_workspace = rf"{project_folder}\Scratch\scratch.gdb"

        # Create Scratch Workspace for Project
        if not arcpy.Exists(rf"{scratch_folder}\scratch.gdb"):
            if not arcpy.Exists(scratch_folder):
                os.makedirs(rf"{scratch_folder}")
            if not arcpy.Exists(rf"{scratch_folder}\scratch.gdb"):
                arcpy.management.CreateFileGDB(rf"{scratch_folder}", f"scratch")

        # Set basic workkpace variables
        arcpy.env.workspace                = project_gdb
        arcpy.env.scratchWorkspace         = scratch_workspace
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        del project_folder, scratch_folder, scratch_workspace

        arcpy.AddMessage(f"{'-' * 90}\n")

        datasets_dict = dataset_title_dict(project_gdb)

        datasets = []

        #datasets.extend(arcpy.ListFeatureClasses("AI_IDW_Sample_Locations"))
        datasets.extend(arcpy.ListFeatureClasses("*Sample_Locations"))
        datasets.extend(arcpy.ListFeatureClasses("DisMAP_Regions"))
        datasets.extend(arcpy.ListTables("Indicators"))
        datasets.extend(arcpy.ListTables("Species_Filter"))
        datasets.extend(arcpy.ListTables("Species_Filter"))

        for dataset in sorted(datasets):

            feature_service_title = datasets_dict[dataset]["Dataset Service Title"]

            arcpy.AddMessage(f"Dataset: {dataset}")
            arcpy.AddMessage(f"\tTitle: {feature_service_title}")

            desc = arcpy.da.Describe(dataset)

            feature_class_path = rf"{project_gdb}\{dataset}"

            if desc["dataType"] == "FeatureClass":

                arcpy.AddMessage(f"\tMake Feature Layer")
                feature_class_layer = arcpy.management.MakeFeatureLayer(feature_class_path, feature_service_title)
                feature_class_layer_file = rf"{home_folder}\{project}\Layers\{feature_class_layer}.lyrx"

                arcpy.AddMessage(f"\tSave Layer File")
                _result = arcpy.management.SaveToLayerFile(
                                                           in_layer         = feature_class_layer,
                                                           out_layer        = feature_class_layer_file,
                                                           is_relative_path = "RELATIVE",
                                                           version          = "CURRENT"
                                                          )
                del _result

                arcpy.management.Delete(feature_class_layer)
                del feature_class_layer

            elif desc["dataType"] == "Table":

                arcpy.AddMessage(f"\tMake Table View")
                feature_class_layer = arcpy.management.MakeTableView(
                                                                     in_table     = feature_class_path,
                                                                     out_view     = feature_service_title,
                                                                     where_clause = "",
                                                                     workspace    = project_gdb,
                                                                     field_info   = "OBJECTID OBJECTID VISIBLE NONE;DatasetCode DatasetCode VISIBLE NONE;Region Region VISIBLE NONE;Season Season VISIBLE NONE;DateCode DateCode VISIBLE NONE;Species Species VISIBLE NONE;CommonName CommonName VISIBLE NONE;CoreSpecies CoreSpecies VISIBLE NONE;Year Year VISIBLE NONE;DistributionProjectName DistributionProjectName VISIBLE NONE;DistributionProjectCode DistributionProjectCode VISIBLE NONE;SummaryProduct SummaryProduct VISIBLE NONE;CenterOfGravityLatitude CenterOfGravityLatitude VISIBLE NONE;MinimumLatitude MinimumLatitude VISIBLE NONE;MaximumLatitude MaximumLatitude VISIBLE NONE;OffsetLatitude OffsetLatitude VISIBLE NONE;CenterOfGravityLatitudeSE CenterOfGravityLatitudeSE VISIBLE NONE;CenterOfGravityLongitude CenterOfGravityLongitude VISIBLE NONE;MinimumLongitude MinimumLongitude VISIBLE NONE;MaximumLongitude MaximumLongitude VISIBLE NONE;OffsetLongitude OffsetLongitude VISIBLE NONE;CenterOfGravityLongitudeSE CenterOfGravityLongitudeSE VISIBLE NONE;CenterOfGravityDepth CenterOfGravityDepth VISIBLE NONE;MinimumDepth MinimumDepth VISIBLE NONE;MaximumDepth MaximumDepth VISIBLE NONE;OffsetDepth OffsetDepth VISIBLE NONE;CenterOfGravityDepthSE CenterOfGravityDepthSE VISIBLE NONE"
                                                                    )
                feature_class_layer_file = rf"{home_folder}\{project}\Layers\{feature_class_layer}.lyrx"

                arcpy.AddMessage(f"\tSave Layer File")
                _result = arcpy.management.SaveToLayerFile(
                                                           in_layer         = feature_class_layer,
                                                           out_layer        = feature_class_layer_file,
                                                           is_relative_path = "RELATIVE",
                                                           version          = "CURRENT"
                                                          )
                del _result

                arcpy.management.Delete(feature_class_layer)
                del feature_class_layer

            else:
                pass

            # Load Metadata
            ImportMetadata = False
            if ImportMetadata:
                dismap.import_metadata(dataset=feature_class_path)
            del ImportMetadata

            if [f.name for f in arcpy.ListFields(feature_class_path) if f.name == "StdTime"]:
                arcpy.AddMessage(f"\tSet Time Enabled if time field is in dataset")
                # Get time information from a layer in a layer file
                layer_file = arcpy.mp.LayerFile(feature_class_layer_file)
                layer = layer_file.listLayers()[0]
                layer.enableTime("StdTime", "StdTime", True)
                layer_file.save()
                del layer

                for layer in layer_file.listLayers():
                    if layer.supports("TIME"):
                        if layer.isTimeEnabled:
                            lyrTime = layer.time
                            startTime = lyrTime.startTime
                            endTime = lyrTime.endTime
                            timeDelta = endTime - startTime
                            startTimeField = lyrTime.startTimeField
                            endTimeField = lyrTime.endTimeField
                            arcpy.AddMessage(f"\tLayer: {layer.name}")
                            arcpy.AddMessage(f"\t\tStart Time Field: {startTimeField}")
                            arcpy.AddMessage(f"\t\tEnd Time Field: {endTimeField}")
                            arcpy.AddMessage(f"\t\tStart Time: {str(startTime.strftime('%m-%d-%Y'))}")
                            arcpy.AddMessage(f"\t\tEnd Time:   {str(endTime.strftime('%m-%d-%Y'))}")
                            arcpy.AddMessage(f"\t\tTime Extent: {str(timeDelta.days)} days")
                            del lyrTime, startTime, endTime, timeDelta
                            del startTimeField, endTimeField
                        else:
                            arcpy.AddMessage("No time properties have been set on the layer")
                    else:
                        arcpy.AddMessage("Time is not supported on this layer")
                    del layer
                del layer_file
            else:
                arcpy.AddMessage(f"\tDataset does not have a time field")

            layer_file = arcpy.mp.LayerFile(feature_class_layer_file)

            # aprx.listBasemaps() to get a list of available basemaps
            #
            #    ['Charted Territory Map',
            #     'Colored Pencil Map',
            #     'Community Map',
            #     'Dark Gray Canvas',
            #     'Firefly Imagery Hybrid',
            #     'GEBCO Basemap (NOAA NCEI Visualization)',
            #     'GEBCO Basemap/Contours (NOAA NCEI Visualization)',
            #     'GEBCO Gray Basemap (NOAA NCEI Visualization)',
            #     'GEBCO Gray Basemap/Contours (NOAA NCEI Visualization)',
            #     'Human Geography Dark Map',
            #     'Human Geography Map',
            #     'Imagery',
            #     'Imagery Hybrid',
            #     'Light Gray Canvas',
            #     'Mid-Century Map',
            #     'Modern Antique Map',
            #     'National Geographic Style Map',
            #     'Navigation',
            #     'Navigation (Dark)',
            #     'Newspaper Map',
            #     'NOAA Charts',
            #     'NOAA ENC® Charts',
            #     'Nova Map',
            #     'Oceans',
            #     'OpenStreetMap',
            #     'Streets',
            #     'Streets (Night)',
            #     'Terrain with Labels',
            #     'Topographic']

            if aprx.listMaps(feature_service_title):
                aprx.deleteItem(aprx.listMaps(feature_service_title)[0])
                aprx.save()

            arcpy.AddMessage(f"\tCreating Map: {feature_service_title}")
            aprx.createMap(f"{feature_service_title}", "Map")
            aprx.save()

            current_map = aprx.listMaps(feature_service_title)[0]

            basemap = "Terrain with Labels"
            current_map.addLayer(layer_file)
            current_map.addBasemap(basemap)
            aprx.save()
            del basemap

            arcpy.AddMessage(f"\t\tCreate map thumbnail and update metadata")
            current_map_view = current_map.defaultView
            current_map_view.exportToPNG(
                                            rf"{home_folder}\{project}\Layers\{feature_service_title}.png",
                                            width=288,
                                            height=192,
                                            resolution=96,
                                            color_mode="24-BIT_TRUE_COLOR",
                                            embed_color_profile=True,
                                        )
            del current_map_view

            from arcpy import metadata as md

            fc_md = md.Metadata(feature_class_path)
            fc_md.title = feature_service_title
            fc_md.thumbnailUri = (rf"{home_folder}\{project}\Layers\{feature_service_title}.png")
            fc_md.save()
            fc_md.reload()
            fc_md.saveAsXML(rf"{home_folder}\{project}\Project Metadata\{feature_service_title}.xml")
            del fc_md, md

            pretty_format_xml_file(rf"{home_folder}\{project}\Project Metadata\{feature_service_title}.xml")

            from arcpy import metadata as md

            in_md = md.Metadata(feature_class_path)
            layer_file.metadata.copy(in_md)
            layer_file.metadata.save()
            layer_file.save()
            current_map.metadata.copy(in_md)
            current_map.metadata.save()
            aprx.save()
            del in_md, md

            arcpy.AddMessage(f"\t\tLayer File Path:     {layer_file.filePath}")
            arcpy.AddMessage(f"\t\tLayer File Version:  {layer_file.version}")
            arcpy.AddMessage(f"\t\tLayer File Metadata:")
            arcpy.AddMessage(f"\t\t\tLayer File Title:              {layer_file.metadata.title}")
            #arcpy.AddMessage(f"\t\t\tLayer File Tags:               {layer_file.metadata.tags}")
            #arcpy.AddMessage(f"\t\t\tLayer File Summary:            {layer_file.metadata.summary}")
            #arcpy.AddMessage(f"\t\t\tLayer File Description:        {layer_file.metadata.description}")
            #arcpy.AddMessage(f"\t\t\tLayer File Credits:            {layer_file.metadata.credits}")
            #arcpy.AddMessage(f"\t\t\tLayer File Access Constraints: {layer_file.metadata.accessConstraints}")

            arcpy.AddMessage(f"\t\tList of layers or tables in Layer File:")
            if current_map.listLayers(feature_service_title):
                layer = current_map.listLayers(feature_service_title)[0]
            elif current_map.listTables(feature_service_title):
                layer = current_map.listTables(feature_service_title)[0]
            else:
                arcpy.AddWarning(f"Something wrong")

            from arcpy import metadata as md

            in_md = md.Metadata(feature_class_path)
            layer.metadata.copy(in_md)
            layer.metadata.save()
            layer_file.save()
            aprx.save()
            del in_md, md

            arcpy.AddMessage(f"\t\t\tLayer Name: {layer.name}")
            arcpy.AddMessage(f"\t\t\tLayer Metadata:")#
            arcpy.AddMessage(f"\t\t\t\tLayer Title:              {layer.metadata.title}")
            #arcpy.AddMessage(f"\t\t\t\tLayer Tags:               {layer.metadata.tags}")
            #arcpy.AddMessage(f"\t\t\t\tLayer Summary:            {layer.metadata.summary}")
            #arcpy.AddMessage(f"\t\t\t\tLayer Description:        {layer.metadata.description}")
            #arcpy.AddMessage(f"\t\t\t\tLayer Credits:            {layer.metadata.credits}")
            #arcpy.AddMessage(f"\t\t\t\tLayer Access Constraints: {layer.metadata.accessConstraints}")
            del layer
            del layer_file
            del feature_class_layer_file
            del feature_class_path

            aprx.deleteItem(current_map)
            del current_map
            aprx.save()

                #del dataset_code, point_feature_type, feature_class_name, region, season
                #del date_code, distribution_project_code
                #del feature_class_path

            del desc
            del feature_service_title
            del dataset

        del datasets_dict
        del datasets

        arcpy.AddMessage(f"\n{'-' * 90}\n")

        # Variables set in function
        del aprx
        del project_gdb
        del home_folder

        # Imports
        del dismap, dataset_title_dict, pretty_format_xml_file

        # Function Parameters
        del base_project_file, project

        results = True

    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(arcpy.GetMessages())
        traceback.print_exc()
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages())
        traceback.print_exc()
    except Exception as e:
        print(e)
        traceback.print_exc()
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
            raise SystemExit(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

def create_feature_class_services(base_project_file="", project=""):
    try:
        # Test if passed workspace exists, if not raise SystemExit
        if not arcpy.Exists(base_project_file):
            raise SystemExit(line_info(f"{os.path.basename(base_project_file)} is missing!!"))

        # Import
        import dismap
        importlib.reload(dismap)
        from dismap import dataset_title_dict

        # Set History and Metadata logs, set serverity and message level
        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(1) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        aprx = arcpy.mp.ArcGISProject(base_project_file)
        home_folder = aprx.homeFolder

        project_gdb = rf"{home_folder}\{project}\{project}.gdb"

        # Test if passed workspace exists, if not raise SystemExit
        if not arcpy.Exists(project_gdb):
            raise SystemExit(line_info(f"{os.path.basename(project_gdb)} is missing!!"))

        # Set basic workkpace variables
        project_folder    = os.path.dirname(project_gdb)
        scratch_folder    = rf"{project_folder}\Scratch"
        scratch_workspace = rf"{project_folder}\Scratch\scratch.gdb"

        # Create Scratch Workspace for Project
        if not arcpy.Exists(rf"{scratch_folder}\scratch.gdb"):
            if not arcpy.Exists(scratch_folder):
                os.makedirs(rf"{scratch_folder}")
            if not arcpy.Exists(rf"{scratch_folder}\scratch.gdb"):
                arcpy.management.CreateFileGDB(rf"{scratch_folder}", f"scratch")

        # Set basic workkpace variables
        arcpy.env.workspace                = project_gdb
        arcpy.env.scratchWorkspace         = scratch_workspace
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        del project_folder, scratch_folder, scratch_workspace

        #LogInAGOL = False
        #if LogInAGOL:
            #try:
                #portal = "https://noaa.maps.arcgis.com/"
                #user = "John.F.Kennedy_noaa"
               # Sign in to portal
                # arcpy.SignInToPortal("https://www.arcgis.com", "MyUserName", "MyPassword")
                # For example: 'http://www.arcgis.com/'
                #arcpy.SignInToPortal(portal)

                #arcpy.AddMessage(f"###---> Signed into Portal: {arcpy.GetActivePortalURL()} <---###")
                #del portal, user
            #except:
                #arcpy.AddError(f"###---> Signed into Portal faild <---###")
        #del LogInAGOL

        arcpy.AddMessage(f"\n{'-' * 90}\n")

        datasets_dict = dataset_title_dict(project_gdb)

        datasets = []

        #datasets.extend(arcpy.ListFeatureClasses("AI_IDW_Sample_Locations"))
        #datasets.extend(arcpy.ListFeatureClasses("HI_IDW_Sample_Locations"))
        datasets.extend(arcpy.ListFeatureClasses("*Sample_Locations"))
        datasets.extend(arcpy.ListFeatureClasses("DisMAP_Regions"))
        datasets.extend(arcpy.ListTables("Indicators"))
        datasets.extend(arcpy.ListTables("Species_Filter"))

        for dataset in sorted(datasets):

            feature_service       = datasets_dict[dataset]["Dataset Service"]
            feature_service_title = datasets_dict[dataset]["Dataset Service Title"]

            arcpy.AddMessage(f"Dataset: {dataset}")
            arcpy.AddMessage(f"\tFS:  {feature_service}")
            arcpy.AddMessage(f"\tFST: {feature_service_title}")

            feature_class_layer_file = rf"{home_folder}\{project}\Layers\{feature_service_title}.lyrx"

            layer_file = arcpy.mp.LayerFile(feature_class_layer_file)

            del feature_class_layer_file

            # aprx.listBasemaps() to get a list of available basemaps
            #
            #    ['Charted Territory Map',
            #     'Colored Pencil Map',
            #     'Community Map',
            #     'Dark Gray Canvas',
            #     'Firefly Imagery Hybrid',
            #     'GEBCO Basemap (NOAA NCEI Visualization)',
            #     'GEBCO Basemap/Contours (NOAA NCEI Visualization)',
            #     'GEBCO Gray Basemap (NOAA NCEI Visualization)',
            #     'GEBCO Gray Basemap/Contours (NOAA NCEI Visualization)',
            #     'Human Geography Dark Map',
            #     'Human Geography Map',
            #     'Imagery',
            #     'Imagery Hybrid',
            #     'Light Gray Canvas',
            #     'Mid-Century Map',
            #     'Modern Antique Map',
            #     'National Geographic Style Map',
            #     'Navigation',
            #     'Navigation (Dark)',
            #     'Newspaper Map',
            #     'NOAA Charts',
            #     'NOAA ENC® Charts',
            #     'Nova Map',
            #     'Oceans',
            #     'OpenStreetMap',
            #     'Streets',
            #     'Streets (Night)',
            #     'Terrain with Labels',
            #     'Topographic']

            if aprx.listMaps(feature_service_title):
                aprx.deleteItem(aprx.listMaps(feature_service_title)[0])
                aprx.save()

            arcpy.AddMessage(f"\tCreating Map: {feature_service_title}")
            aprx.createMap(feature_service_title, "Map")
            aprx.save()

            current_map = aprx.listMaps(feature_service_title)[0]

            from arcpy import metadata as md
            in_md = md.Metadata(dataset)
            current_map.metadata.copy(in_md)
            current_map.metadata.save()
            aprx.save()
            del md, in_md

            current_map.addLayer(layer_file)
            aprx.save()

            del layer_file

            arcpy.AddMessage(f"\t\tList of layers or tables in Layer File:")
            if current_map.listLayers(feature_service_title):
                lyr = current_map.listLayers(feature_service_title)[0]
            elif current_map.listTables(feature_service_title):
                lyr = current_map.listTables(feature_service_title)[0]
            else:
                arcpy.AddWarning(f"Something wrong")

            from arcpy import metadata as md
            in_md = md.Metadata(dataset)
            lyr.metadata.copy(in_md)
            lyr.metadata.save()
            aprx.save()
            del md, in_md

            arcpy.AddMessage(f"\tGet Web Layer Sharing Draft")
            # Get Web Layer Sharing Draft
            server_type = "HOSTING_SERVER"  # FEDERATED_SERVER
            #            m.getWebLayerSharingDraft (server_type, service_type, service_name, {layers_and_tables})
            # sddraft = m.getWebLayerSharingDraft(server_type, "FEATURE", service_name, [selected_layer, selected_table])
            # https://pro.arcgis.com/en/pro-app/latest/arcpy/sharing/featuresharingdraft-class.htm#GUID-8E27A3ED-A705-4ACF-8C7D-AA861327AD26
            sddraft = current_map.getWebLayerSharingDraft(server_type=server_type, service_type="FEATURE", service_name=feature_service, layers_and_tables=lyr)
            del server_type

            sddraft.allowExporting = False
            sddraft.offline = False
            sddraft.offlineTarget = None
            sddraft.credits                  = lyr.metadata.credits
            sddraft.description              = lyr.metadata.description
            sddraft.summary                  = lyr.metadata.summary
            sddraft.tags                     = lyr.metadata.tags
            sddraft.useLimitations           = lyr.metadata.accessConstraints
            sddraft.overwriteExistingService = True
            sddraft.portalFolder = f"DisMAP {project}"

            del lyr

            arcpy.AddMessage(f"\t\tAllow Exporting:            {sddraft.allowExporting}")
            arcpy.AddMessage(f"\t\tCheck Unique ID Assignment: {sddraft.checkUniqueIDAssignment}")
            arcpy.AddMessage(f"\t\tOffline:                    {sddraft.offline}")
            arcpy.AddMessage(f"\t\tOffline Target:             {sddraft.offlineTarget}")
            arcpy.AddMessage(f"\t\tOverwrite Existing Service: {sddraft.overwriteExistingService}")
            arcpy.AddMessage(f"\t\tPortal Folder:              {sddraft.portalFolder}")
            arcpy.AddMessage(f"\t\tServer Type:                {sddraft.serverType}")
            arcpy.AddMessage(f"\t\tService Name:               {sddraft.serviceName}")
            #arcpy.AddMessage(f"\t\tCredits:                    {sddraft.credits}")
            #arcpy.AddMessage(f"\t\tDescription:                {sddraft.description}")
            #arcpy.AddMessage(f"\t\tSummary:                    {sddraft.summary}")
            #arcpy.AddMessage(f"\t\tTags:                       {sddraft.tags}")
            #arcpy.AddMessage(f"\t\tUse Limitations:            {sddraft.useLimitations}")

            arcpy.AddMessage(f"\tExport to SD Draft")
            # Create Service Definition Draft file
            sddraft.exportToSDDraft(rf"{home_folder}\{project}\Publish\{feature_service}.sddraft")

            del sddraft

            sd_draft = rf"{home_folder}\{project}\Publish\{feature_service}.sddraft"

            arcpy.AddMessage(f"\tModify SD Draft")
            # https://pro.arcgis.com/en/pro-app/latest/arcpy/sharing/featuresharingdraft-class.htm
            import xml.dom.minidom as DOM

            docs = DOM.parse(sd_draft)
            key_list = docs.getElementsByTagName("Key")
            value_list = docs.getElementsByTagName("Value")

            for i in range(key_list.length):
                if key_list[i].firstChild.nodeValue == "maxRecordCount":
                    arcpy.AddMessage(f"\t\tUpdating maxRecordCount from 2000 to 10000")
                    value_list[i].firstChild.nodeValue = 10000
                if key_list[i].firstChild.nodeValue == "ServiceTitle":
                    arcpy.AddMessage(f"\t\tUpdating ServiceTitle from {value_list[i].firstChild.nodeValue} to {feature_service_title}")
                    value_list[i].firstChild.nodeValue = feature_service_title
                # Doesn't work
                #if key_list[i].firstChild.nodeValue == "GeodataServiceName":
                #    arcpy.AddMessage(f"\t\tUpdating GeodataServiceName from {value_list[i].firstChild.nodeValue} to {feature_service}")
                #    value_list[i].firstChild.nodeValue = feature_service
                del i

            # Write to the .sddraft file
            f = open(sd_draft, "w")
            docs.writexml(f)
            f.close()
            del f

            del DOM, docs, key_list, value_list

            FeatureSharingDraftReport = False
            if FeatureSharingDraftReport:
                arcpy.AddMessage(f"\tReport for {os.path.basename(sd_draft)} SD File")
                feature_sharing_draft_report(sd_draft)
            del FeatureSharingDraftReport

            arcpy.AddMessage(f"\tCreate/Stage {os.path.basename(sd_draft)} SD File")
            arcpy.server.StageService(in_service_definition_draft=sd_draft, out_service_definition=sd_draft.replace("sddraft", "sd"), staging_version=5)

            UploadServiceDefinition = True
            if UploadServiceDefinition:
                if project != "April 1 2023":
                    arcpy.AddMessage(f"\tUpload {os.path.basename(sd_draft).replace('sddraft', 'sd')} Service Definition")
                    arcpy.server.UploadServiceDefinition(
                                                         in_sd_file      = sd_draft.replace("sddraft", "sd"),
                                                         in_server       = "HOSTING_SERVER",  # in_service_name = "", #in_cluster      = "",
                                                         in_folder_type  = "FROM_SERVICE_DEFINITION",  # EXISTING #in_folder       = "",
                                                         in_startupType  = "STARTED",
                                                         in_override     = "OVERRIDE_DEFINITION",
                                                         in_my_contents  = "NO_SHARE_ONLINE",
                                                         in_public       = "PRIVATE",
                                                         in_organization = "NO_SHARE_ORGANIZATION",  # in_groups       = ""
                                                        )
                else:
                    arcpy.AddWarning(f"Project is {project}")
            del UploadServiceDefinition

            del sd_draft

            #aprx.deleteItem(current_map)
            del current_map
            aprx.save()

            del feature_service, feature_service_title
            del dataset
        del datasets
        del datasets_dict

        # TODO: Possibly create a dictionary that can be saved to JSON

        aprx.save()

        current_maps = aprx.listMaps()

        if current_maps:
            arcpy.AddMessage(f"\nCurrent Maps\n")
            for current_map in current_maps:
                arcpy.AddMessage(f"\tProject Map: {current_map.name}")
                del current_map
        else:
            arcpy.AddWarning("No maps in Project")

        arcpy.AddMessage(f"\n{'-' * 90}\n")

        del current_maps

        del project_gdb

        # Variables set in function for aprx
        del home_folder
        # Save aprx one more time and then delete
        aprx.save()
        del aprx

        # Variables set in function

        # Imports
        del dismap, dataset_title_dict

        # Function Parameters
        del base_project_file, project

        results = True

    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(arcpy.GetMessages())
        traceback.print_exc()
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages())
        traceback.print_exc()
    except Exception as e:
        print(e)
        traceback.print_exc()
    except:
        traceback.print_exc()
    else:
        try:
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in ["results"]]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del remaining_keys
            return results
        except:
            traceback.print_exc()
    finally:
        if "results" in locals().keys(): del results

##def update_metadata_from_published_md(base_project_file="", project=""):
##    try:
##        # Import
##        import dismap
##        importlib.reload(dismap)
##
##        arcpy.env.overwriteOutput = True
##        arcpy.env.parallelProcessingFactor = "100%"
##        arcpy.SetLogMetadata(True)
##        arcpy.SetSeverityLevel(2)
##        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION
##
##        LogInAGOL = False
##        if LogInAGOL:
##            try:
##                portal = "https://noaa.maps.arcgis.com/"
##                user = "John.F.Kennedy_noaa"
##
##                # Sign in to portal
##                #arcpy.SignInToPortal("https://www.arcgis.com", "MyUserName", "MyPassword")
##                # For example: 'http://www.arcgis.com/'
##                arcpy.SignInToPortal(portal)
##
##                arcpy.AddMessage(f"###---> Signed into Portal: {arcpy.GetActivePortalURL()} <---###")
##                del portal, user
##            except:
##                arcpy.AddError(f"###---> Signed into Portal faild <---###")
##        del LogInAGOL
##
##        aprx = arcpy.mp.ArcGISProject(base_project_file)
##        home_folder = aprx.homeFolder
##        del aprx
##
##        project_gdb = rf"{home_folder}\{project}\{project}.gdb"
##
##        arcpy.AddMessage(f"{'-' * 90}\n")
##
##        # DatasetCode, CSVFile, TransformUnit, TableName, GeographicArea, CellSize,
##        # PointFeatureType, FeatureClassName, Region, Season, DateCode, Status,
##        # DistributionProjectCode, DistributionProjectName, SummaryProduct,
##        # FilterRegion, FilterSubRegion, FeatureServiceName, FeatureServiceTitle,
##        # MosaicName, MosaicTitle, ImageServiceName, ImageServiceTitle
##
##        # Get values for table_name from Datasets table
##        #fields = ["FeatureClassName", "FeatureServiceName", "FeatureServiceTitle"]
##        fields = ["DatasetCode", "PointFeatureType", "FeatureClassName", "Region", "Season", "DateCode", "DistributionProjectCode"]
##        datasets = [row for row in arcpy.da.SearchCursor(rf"{project_gdb}\Datasets", fields, where_clause = f"FeatureClassName IS NOT NULL AND DistributionProjectCode NOT IN ('GLMME', 'GFDL')")]
##        #datasets = [row for row in arcpy.da.SearchCursor(rf"{project_gdb}\Datasets", fields, where_clause = f"FeatureClassName IN ('AI_IDW_Sample_Locations', 'DisMAP_Regions')")]
##        del fields
##
##        for dataset in datasets:
##            dataset_code, point_feature_type, feature_class_name, region_latitude, season, date_code, distribution_project_code = dataset
##
##            feature_service_name  = f"{dataset_code}_{point_feature_type}_{date_code}".replace("None", "").replace(" ", "_").replace("__", "_")
##
##            if distribution_project_code == "IDW":
##                feature_service_title = f"{region_latitude} {season} {point_feature_type} {date_code}".replace("None", "").replace("  ", " ")
##            #elif distribution_project_code in ["GLMME", "GFDL"]:
##            #    feature_service_title = f"{region_latitude} {distribution_project_code} {point_feature_type} {date_code}".replace("None", "").replace("  ", " ")
##            else:
##                feature_service_title = f"{feature_service_name}".replace("_", " ")
##
##            map_title = feature_service_title.replace("GRID Points", "").replace("Sample Locations", "").replace("  ", " ")
##
##            feature_class_path = f"{project_gdb}\{feature_class_name}"
##
##            arcpy.AddMessage(f"Dataset Code: {dataset_code}")
##            arcpy.AddMessage(f"\tFeature Service Name:   {feature_service_name}")
##            arcpy.AddMessage(f"\tFeature Service Title:  {feature_service_title}")
##            arcpy.AddMessage(f"\tMap Title:              {map_title}")
##            arcpy.AddMessage(f"\tLayer Title:            {feature_service_title}")
##            arcpy.AddMessage(f"\tFeature Class Name:     {feature_class_name}")
##            arcpy.AddMessage(f"\tFeature Class Path:     {feature_class_path}")
##
##            if arcpy.Exists(rf"{home_folder}\{project}\Publish\{feature_service_name}.xml"):
##                arcpy.AddMessage(f"\t###--->>> {feature_service_name}.xml Exists <<<---###")
##
##                from arcpy import metadata as md
##                in_md = md.Metadata(rf"{home_folder}\{project}\Publish\{feature_service_name}.xml")
##                fc_md = md.Metadata(feature_class_path)
##                fc_md.copy(in_md)
##                fc_md.save()
##                del in_md, fc_md
##                del md
##
##            else:
##                arcpy.AddWarning(f"\t###--->>> {feature_service_name}.xml Does Not Exist <<<---###")
##
##            del dataset_code, point_feature_type, feature_class_name, region_latitude, season
##            del date_code, distribution_project_code
##
##            del feature_service_name, feature_service_title
##            del map_title, feature_class_path
##            del dataset
##        del datasets
##
##        arcpy.AddMessage(f"\n{'-' * 90}\n")
##
##        # Variables set in function
##        del project_gdb
##        del home_folder
##
##        # Imports
##        del dismap
##
##        # Function Parameters
##        del base_project_file, project
##
##    except SystemExit:
##        raise SystemExit
##    except:
##        traceback.print_exc()
##        raise SystemExit
##    else:
##        try:
##            leave_out_keys = ["leave_out_keys", "remaining_keys", "results"]
##            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
##            if remaining_keys:
##                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
##            del leave_out_keys, remaining_keys
##
##            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
##
##        except:
##            traceback.print_exc()
##    finally:
##        try:
##            if "results" in locals().keys(): del results
##        except UnboundLocalError:
##            pass

def create_image_services(base_project_file="", project=""):
    try:
        # Test if passed workspace exists, if not raise SystemExit
        if not arcpy.Exists(base_project_file):
            raise SystemExit(line_info(f"{os.path.basename(base_project_file)} is missing!!"))

        # Import
        import dismap
        importlib.reload(dismap)

        # Set History and Metadata logs, set serverity and message level
        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(1) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        aprx = arcpy.mp.ArcGISProject(base_project_file)
        home_folder = aprx.homeFolder

        project_gdb = rf"{home_folder}\{project}\{project}.gdb"

        # Test if passed workspace exists, if not raise SystemExit
        if not arcpy.Exists(project_gdb):
            raise SystemExit(line_info(f"{os.path.basename(project_gdb)} is missing!!"))

        # Set basic workkpace variables
        project_folder    = os.path.dirname(project_gdb)
        scratch_folder    = rf"{project_folder}\Scratch"
        scratch_workspace = rf"{project_folder}\Scratch\scratch.gdb"

        # Create Scratch Workspace for Project
        if not arcpy.Exists(rf"{scratch_folder}\scratch.gdb"):
            if not arcpy.Exists(scratch_folder):
                os.makedirs(rf"{scratch_folder}")
            if not arcpy.Exists(rf"{scratch_folder}\scratch.gdb"):
                arcpy.management.CreateFileGDB(rf"{scratch_folder}", f"scratch")

        # Set basic workkpace variables
        arcpy.env.workspace                = project_gdb
        arcpy.env.scratchWorkspace         = scratch_workspace
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        del scratch_folder, scratch_workspace

        LogIntoPortal = False
        if LogIntoPortal:
            try:
                portal = "https://noaa.maps.arcgis.com/"
                user = "John.F.Kennedy_noaa"

                #portal = "https://maps.fisheries.noaa.gov/portal/home"
                #portal = "https://maps.fisheries.noaa.gov"
                #user   = "John.F.Kennedy_noaa"

                # Sign in to portal
                # arcpy.SignInToPortal("https://www.arcgis.com", "MyUserName", "MyPassword")
                # For example: 'http://www.arcgis.com/'
                arcpy.SignInToPortal(portal)

                arcpy.AddMessage(f"###---> Signed into Portal: {arcpy.GetActivePortalURL()} <---###")
                del portal, user
            except:
                arcpy.AddError(f"###---> Signed into Portal faild <---###")
                raise SystemExit
        del LogIntoPortal

        arcpy.AddMessage(f"\n{'-' * 90}\n")

        # Publishes an image service to a machine "myserver" from a folder of ortho images
        # this code first author a mosaic dataset from the images, then publish it as an image service.
        # A connection to ArcGIS Server must be established in the Catalog window of ArcMap
        # before running this script

        #import time
        #import arceditor # this is required to create a mosaic dataset from images

        #
        # Define local variables:
        #ImageSource=r"\\myserver\data\SourceData\Portland"  # the folder of input images
        #MyWorkspace=r"\\myserver\Data\DemoData\ArcPyPublishing" # the folder for mosaic dataset and the service defintion draft file
        #GdbName="fgdb1.gdb"
        #GDBpath = os.path.join(MyWorkspace,GdbName) #File geodatabase used to store a mosaic dataset
        #Name = "OrthoImages"
        #Md = os.path.join(GDBpath, Name)
        #Sddraft = os.path.join(MyWorkspace,Name+".sddraft")
        #Sd = os.path.join(MyWorkspace,Name+".sd")
        #con = os.path.join(MyWorkspace, "arcgis on myserver_6080 (admin).ags")
        con = r"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\server on maps.fisheries.noaa.gov.ags"

        mosiac_name    = "SEUS_FAL_Mosaic"
        mosiac_path    = rf"{project_gdb}\{mosiac_name}"
        mosiac_sddraft = rf"{project_folder}\Publish\{mosiac_name}.sddraft"

##        SrsLookup = {
##          'Mercator': "PROJCS['World_Mercator',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137,298.257223563]],PRIMEM['Greenwich',0],UNIT['Degree',0.017453292519943295]],PROJECTION['Mercator'],PARAMETER['False_Easting',0],PARAMETER['False_Northing',0],PARAMETER['Central_Meridian',0],PARAMETER['Standard_Parallel_1',0],UNIT['Meter',1]]",
##          'WGS84': "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137,298.257223563]],PRIMEM['Greenwich',0],UNIT['Degree',0.017453292519943295]]",
##          'GZ4': "PROJCS['Germany_Zone_4',GEOGCS['GCS_Deutsches_Hauptdreiecksnetz',DATUM['D_Deutsches_Hauptdreiecksnetz',SPHEROID['Bessel_1841',6377397.155,299.1528128]],PRIMEM['Greenwich',0],UNIT['Degree',0.017453292519943295]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',4500000],PARAMETER['False_Northing',0],PARAMETER['Central_Meridian',12],PARAMETER['Scale_Factor',1],PARAMETER['Latitude_Of_Origin',0],UNIT['Meter',1]]",
##          'GCS_NAD83': "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137,298.257222101]],PRIMEM['Greenwich',0],UNIT['Degree',0.017453292519943295]]",
##          'PUG': "PROJCS['PUG1',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',1640416.666666667],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-87.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Foot_US',0.3048006096012192]]",
##          'Florida_East': "PROJCS['NAD_1983_StatePlane_Florida_East_FIPS_0901_Feet',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137,298.257222101]],PRIMEM['Greenwich',0],UNIT['Degree',0.0174532925199432955]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',656166.6666666665],PARAMETER['False_Northing',0],PARAMETER['Central_Meridian',-81],PARAMETER['Scale_Factor',0.9999411764705882],PARAMETER['Latitude_Of_Origin',24.33333333333333],UNIT['Foot_US',0.304800609601219241]]",
##          'SoCalNad83': "PROJCS['NAD_1983_StatePlane_California_V_FIPS_0405',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137,298.257222101]],PRIMEM['Greenwich',0],UNIT['Degree',0.0174532925199432955]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',2000000],PARAMETER['False_Northing',500000],PARAMETER['Central_Meridian',-118],PARAMETER['Standard_Parallel_1',34.03333333333333],PARAMETER['Standard_Parallel_2',35.46666666666667],PARAMETER['Latitude_Of_Origin',33.5],UNIT['Meter',1]]"
##        }

##        # First author a mosaic dataset from a folder of images
##        try:
##            arcpy.AddMessage("Creating fgdb")
##            arcpy.CreateFileGDB_management(MyWorkspace, GdbName)
##
##            arcpy.AddMessage("Creating mosaic dataset")
##            #arcpy.CreateMosaicDataset_management(GDBpath, Name, SrsLookup['Mercator'], "", "", "NONE", "")
##            arcpy.CreateMosaicDataset_management(project_gdb, mosiac_name, SrsLookup['Mercator'], "", "", "NONE", "")
##
##            arcpy.AddMessage("Adding images to mosaic dataset") # also caculate cell size range, build boundary, and build overviews
##            #arcpy.AddRastersToMosaicDataset_management(Md, "Raster Dataset", ImageSource, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "UPDATE_OVERVIEWS", "#", "0", "1500", "#", "#", "SUBFOLDERS", "ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", "", "NO_FORCE_SPATIAL_REFERENCE")
##            arcpy.AddRastersToMosaicDataset_management(mosiac_path, "Raster Dataset", ImageSource, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "UPDATE_OVERVIEWS", "#", "0", "1500", "#", "#", "SUBFOLDERS", "ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", "", "NO_FORCE_SPATIAL_REFERENCE")
##        except:
##            arcpy.AddError(arcpy.GetMessages()+ "\n\n")
##            sys.exit("Failed in authoring a mosaic dataset")

        # Create service definition draft
        try:
            arcpy.AddMessage("Creating SD draft")
            #arcpy.CreateImageSDDraft(Md, Sddraft, Name, 'ARCGIS_SERVER', con, False, None, "Ortho Images","ortho images,image service")
            arcpy.CreateImageSDDraft(mosiac_path, mosiac_sddraft, mosiac_name, 'ARCGIS_SERVER', con, False, None, "Ortho Images", "ortho images,image service")
        except:
            arcpy.AddError(arcpy.GetMessages()+ "\n\n")
            sys.exit("Failed in creating SD draft")

##        # Analyze the service definition draft
##        analysis = arcpy.mapping.AnalyzeForSD(Sddraft)
##        arcpy.AddMessage("The following information was returned during analysis of the image service:")
##        for key in ('messages', 'warnings', 'errors'):
##          arcpy.AddMessage('----' + key.upper() + '---')
##          vars = analysis[key]
##          for ((message, code), layerlist) in vars.iteritems():
##            arcpy.AddMessage('    ', message, ' (CODE %i)' % code)
##            arcpy.AddMessage('       applies to:'),
##            for layer in layerlist:
##                arcpy.AddMessage(layer.name),
##            arcpy.AddMessage()
##
##        # Stage and upload the service if the sddraft analysis did not contain errors
##        if analysis['errors'] == {}:
##            try:
##                arcpy.AddMessage("Adding data path to data store to avoid data copy")
##                arcpy.AddDataStoreItem(con, "FOLDER","Images", MyWorkspace, MyWorkspace)
##
##                arcpy.AddMessage("Staging service to create service definition")
##                arcpy.StageService_server(Sddraft, Sd)
##
##                arcpy.AddMessage("Uploading the service definition and publishing image service")
##                arcpy.UploadServiceDefinition_server(Sd, con)
##
##                arcpy.AddMessage("Service successfully published")
##            except:
##                arcpy.AddError(arcpy.GetMessages()+ "\n\n")
##                sys.exit("Failed to stage and upload service")
##        else:
##            arcpy.AddError("Service could not be published because errors were found during analysis.")
##            arcpy.AddError(arcpy.GetMessages())

        arcpy.AddMessage(f"\n{'-' * 90}\n")

        del project_gdb

        # Variables set in function for aprx
        del home_folder
        # Save aprx one more time and then delete
        aprx.save()
        del aprx

        # Variables set in function

        # Imports
        del dismap

        # Function Parameters
        del base_project_file, project

        results = [True]

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

def create_basic_template_xml_files(base_project_file="", project=""):
    try:
        # Import
        from arcpy import metadata as md

        import dismap
        importlib.reload(dismap)
        from dismap import dataset_title_dict, pretty_format_xml_file

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2)
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        # Map Cleanup
        MapCleanup = False
        if MapCleanup:
            map_cleanup(base_project_file)
        del MapCleanup

        base_project_folder = rf"{os.path.dirname(base_project_file)}"
        base_project_file   = rf"{base_project_folder}\DisMAP.aprx"
        project_folder      = rf"{base_project_folder}\{project}"
        project_gdb         = rf"{project_folder}\{project}.gdb"
        metadata_folder     = rf"{project_folder}\Export Metadata"
        crfs_folder         = rf"{project_folder}\CRFs"
        scratch_folder      = rf"{project_folder}\Scratch"

        metadata_dictionary = dataset_title_dict(project_gdb)

        workspaces = [project_gdb, crfs_folder]

        for workspace in workspaces:

            arcpy.env.workspace        = workspace
            arcpy.env.scratchWorkspace = rf"{scratch_folder}\scratch.gdb"

            datasets = list()

            walk = arcpy.da.Walk(workspace)

            for dirpath, dirnames, filenames in walk:
                for filename in filenames:
                    datasets.append(os.path.join(dirpath, filename))
                    del filename
                del dirpath, dirnames, filenames
            del walk

            for dataset_path in sorted(datasets):
                #arcpy.AddMessage(dataset_path)
                dataset_name = os.path.basename(dataset_path)

                arcpy.AddMessage(f"Dataset Name: {dataset_name}")

                if "Datasets" == dataset_name:

                    arcpy.AddMessage(f"\tDataset Table")

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    del empty_md

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    datasets_table_template = rf"{metadata_folder}\datasets_table_template.xml"
                    dataset_md.saveAsXML(datasets_table_template, "REMOVE_ALL_SENSITIVE_INFO")
                    pretty_format_xml_file(datasets_table_template)
                    del datasets_table_template

                    del dataset_md

                elif "Species_Filter" == dataset_name:

                    arcpy.AddMessage(f"\tSpecies Filter Table")

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    del empty_md

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    species_filter_table_template = rf"{metadata_folder}\species_filter_table_template.xml"
                    dataset_md.saveAsXML(species_filter_table_template, "REMOVE_ALL_SENSITIVE_INFO")
                    pretty_format_xml_file(species_filter_table_template)
                    del species_filter_table_template

                    del dataset_md

                elif "Indicators" in dataset_name:

                    arcpy.AddMessage(f"\tIndicators")

                    if dataset_name == "Indicators":
                        dataset_name = f"{dataset_name}_Table"
                    else:
                        pass

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    del empty_md

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    indicators_template = rf"{metadata_folder}\indicators_template.xml"
                    dataset_md.saveAsXML(indicators_template, "REMOVE_ALL_SENSITIVE_INFO")
                    pretty_format_xml_file(indicators_template)
                    del indicators_template

                    del dataset_md

                elif "LayerSpeciesYearImageName" in dataset_name:

                    arcpy.AddMessage(f"\tLayer Species Year Image Name")

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    del empty_md

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    layer_species_year_image_name_template = rf"{metadata_folder}\layer_species_year_image_name_template.xml"
                    dataset_md.saveAsXML(layer_species_year_image_name_template, "REMOVE_ALL_SENSITIVE_INFO")
                    pretty_format_xml_file(layer_species_year_image_name_template)
                    del layer_species_year_image_name_template

                    del dataset_md

                elif dataset_name.endswith("Boundary"):

                    arcpy.AddMessage(f"\tBoundary")

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    del empty_md

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    boundary_template = rf"{metadata_folder}\boundary_template.xml"
                    dataset_md.saveAsXML(boundary_template, "REMOVE_ALL_SENSITIVE_INFO")
                    pretty_format_xml_file(boundary_template)
                    del boundary_template

                    del dataset_md

                elif dataset_name.endswith("Extent_Points"):

                    arcpy.AddMessage(f"\tExtent_Points")

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    del empty_md

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    extent_points_template = rf"{metadata_folder}\extent_points_template.xml"
                    dataset_md.saveAsXML(extent_points_template, "REMOVE_ALL_SENSITIVE_INFO")
                    pretty_format_xml_file(extent_points_template)
                    del extent_points_template

                    del dataset_md

                elif dataset_name.endswith("Fishnet"):

                    arcpy.AddMessage(f"\tFishnet")

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    del empty_md

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    fishnet_template = rf"{metadata_folder}\fishnet_template.xml"
                    dataset_md.saveAsXML(fishnet_template, "REMOVE_ALL_SENSITIVE_INFO")
                    pretty_format_xml_file(fishnet_template)
                    del fishnet_template

                    del dataset_md

                elif dataset_name.endswith("Lat_Long"):

                    arcpy.AddMessage(f"\tLat_Long")

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    del empty_md

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    lat_long_template = rf"{metadata_folder}\lat_long_template.xml"
                    dataset_md.saveAsXML(lat_long_template, "REMOVE_ALL_SENSITIVE_INFO")
                    pretty_format_xml_file(lat_long_template)
                    del lat_long_template

                    del dataset_md

                elif dataset_name.endswith("Region"):

                    arcpy.AddMessage(f"\tRegion")

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    del empty_md

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    region_template = rf"{metadata_folder}\region_template.xml"
                    dataset_md.saveAsXML(region_template, "REMOVE_ALL_SENSITIVE_INFO")
                    pretty_format_xml_file(region_template)
                    del region_template

                    del dataset_md

                elif dataset_name.endswith("Sample_Locations"):

                    arcpy.AddMessage(f"\tSample_Locations")

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    del empty_md

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    sample_locations_template = rf"{metadata_folder}\sample_locations_template.xml"
                    dataset_md.saveAsXML(sample_locations_template, "REMOVE_ALL_SENSITIVE_INFO")
                    pretty_format_xml_file(sample_locations_template)
                    del sample_locations_template

                    del dataset_md

                elif dataset_name.endswith("GRID_Points"):

                    arcpy.AddMessage(f"\tGRID_Points")

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    del empty_md

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    grid_points_template = rf"{metadata_folder}\grid_points_template.xml"
                    dataset_md.saveAsXML(grid_points_template, "REMOVE_ALL_SENSITIVE_INFO")
                    pretty_format_xml_file(grid_points_template)
                    del grid_points_template

                    del dataset_md

                elif "DisMAP_Regions" == dataset_name:

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    del empty_md

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    dismap_regions_template = rf"{metadata_folder}\dismap_regions_template.xml"
                    dataset_md.saveAsXML(dismap_regions_template, "REMOVE_ALL_SENSITIVE_INFO")
                    pretty_format_xml_file(dismap_regions_template)
                    del dismap_regions_template

                    del dataset_md

                elif dataset_name.endswith("Bathymetry"):

                    arcpy.AddMessage(f"\tBathymetry")

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    del empty_md

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    bathymetry_template = rf"{metadata_folder}\bathymetry_template.xml"
                    dataset_md.saveAsXML(bathymetry_template, "REMOVE_ALL_SENSITIVE_INFO")
                    pretty_format_xml_file(bathymetry_template)
                    del bathymetry_template

                    del dataset_md

                elif dataset_name.endswith("Latitude"):

                    arcpy.AddMessage(f"\tLatitude")

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    del empty_md

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    latitude_template = rf"{metadata_folder}\latitude_template.xml"
                    dataset_md.saveAsXML(latitude_template, "REMOVE_ALL_SENSITIVE_INFO")
                    pretty_format_xml_file(latitude_template)
                    del latitude_template

                    del dataset_md

                elif dataset_name.endswith("Longitude"):

                    arcpy.AddMessage(f"\tLongitude")

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    del empty_md

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    longitude_template = rf"{metadata_folder}\longitude_template.xml"
                    dataset_md.saveAsXML(longitude_template, "REMOVE_ALL_SENSITIVE_INFO")
                    pretty_format_xml_file(longitude_template)
                    del longitude_template

                    del dataset_md

                elif dataset_name.endswith("Raster_Mask"):

                    arcpy.AddMessage(f"\tRaster_Mask")

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    del empty_md

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    raster_mask_template = rf"{metadata_folder}\raster_mask_template.xml"
                    dataset_md.saveAsXML(raster_mask_template, "REMOVE_ALL_SENSITIVE_INFO")
                    pretty_format_xml_file(raster_mask_template)
                    del raster_mask_template

                    del dataset_md

                elif dataset_name.endswith("Mosaic"):

                    arcpy.AddMessage(f"\tMosaic")

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    del empty_md

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    mosaic_template = rf"{metadata_folder}\mosaic_template.xml"
                    dataset_md.saveAsXML(mosaic_template, "REMOVE_ALL_SENSITIVE_INFO")
                    pretty_format_xml_file(mosaic_template)
                    del mosaic_template

                    del dataset_md

                elif dataset_name.endswith(".crf"):

                    arcpy.AddMessage(f"\tCRF")

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    del empty_md

                    dataset_md.title             = metadata_dictionary[dataset_name.replace(".crf", "_CRF")]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name.replace(".crf", "_CRF")]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name.replace(".crf", "_CRF")]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name.replace(".crf", "_CRF")]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name.replace(".crf", "_CRF")]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name.replace(".crf", "_CRF")]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    crf_template = rf"{metadata_folder}\crf_template.xml"
                    dataset_md.saveAsXML(crf_template, "REMOVE_ALL_SENSITIVE_INFO")
                    pretty_format_xml_file(crf_template)
                    del crf_template

                    del dataset_md

                else:
                    arcpy.AddMessage(f"\tRegion Table")

                    if dataset_name.endswith("IDW"):

                        dataset_md = md.Metadata(dataset_path)
                        empty_md   = md.Metadata()
                        dataset_md.copy(empty_md)
                        dataset_md.save()
                        del empty_md

                        dataset_md.title             = metadata_dictionary[f"{dataset_name}"]["Dataset Service Title"]
                        dataset_md.tags              = metadata_dictionary[f"{dataset_name}"]["Tags"]
                        dataset_md.summary           = metadata_dictionary[f"{dataset_name}"]["Summary"]
                        dataset_md.description       = metadata_dictionary[f"{dataset_name}"]["Description"]
                        dataset_md.credits           = metadata_dictionary[f"{dataset_name}"]["Credits"]
                        dataset_md.accessConstraints = metadata_dictionary[f"{dataset_name}"]["Access Constraints"]
                        dataset_md.save()

                        dataset_md.synchronize("ALWAYS")

                        idw_region_table_template = rf"{metadata_folder}\idw_region_table_template.xml"
                        dataset_md.saveAsXML(idw_region_table_template, "REMOVE_ALL_SENSITIVE_INFO")
                        pretty_format_xml_file(idw_region_table_template)
                        del idw_region_table_template

                        del dataset_md

                    elif dataset_name.endswith("GLMME"):

                        dataset_md = md.Metadata(dataset_path)
                        empty_md   = md.Metadata()
                        dataset_md.copy(empty_md)
                        dataset_md.save()
                        del empty_md

                        dataset_md.title             = metadata_dictionary[f"{dataset_name}"]["Dataset Service Title"]
                        dataset_md.tags              = metadata_dictionary[f"{dataset_name}"]["Tags"]
                        dataset_md.summary           = metadata_dictionary[f"{dataset_name}"]["Summary"]
                        dataset_md.description       = metadata_dictionary[f"{dataset_name}"]["Description"]
                        dataset_md.credits           = metadata_dictionary[f"{dataset_name}"]["Credits"]
                        dataset_md.accessConstraints = metadata_dictionary[f"{dataset_name}"]["Access Constraints"]
                        dataset_md.save()

                        dataset_md.synchronize("ALWAYS")

                        glmme_region_table_template = rf"{metadata_folder}\glmme_region_table_template.xml"
                        dataset_md.saveAsXML(glmme_region_table_template, "REMOVE_ALL_SENSITIVE_INFO")
                        pretty_format_xml_file(glmme_region_table_template)
                        del glmme_region_table_template

                        del dataset_md

                    else:
                        pass
                del dataset_name, dataset_path
            del workspace

        del datasets

        # Variables set in function
        del project_gdb, base_project_folder, metadata_folder
        del project_folder, scratch_folder, crfs_folder
        del metadata_dictionary, workspaces

        # Imports
        del dismap, dataset_title_dict, pretty_format_xml_file
        del md

        # Function Parameters
        del base_project_file, project

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

def import_basic_template_xml_files(base_project_file="", project=""):
    try:
        # Import
        from arcpy import metadata as md

        import dismap
        importlib.reload(dismap)
        from dismap import dataset_title_dict, pretty_format_xml_files, unique_years

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2)
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        # Map Cleanup
        MapCleanup = False
        if MapCleanup:
            map_cleanup(base_project_file)
        del MapCleanup

        base_project_folder = rf"{os.path.dirname(base_project_file)}"
        base_project_file   = rf"{base_project_folder}\DisMAP.aprx"
        project_folder      = rf"{base_project_folder}\{project}"
        project_gdb         = rf"{project_folder}\{project}.gdb"
        metadata_folder     = rf"{project_folder}\Current Metadata"
        crfs_folder         = rf"{project_folder}\CRFs"
        scratch_folder      = rf"{project_folder}\Scratch"

        #arcpy.AddMessage("Creating the Metadata Dictionary. Please wait!!")
        metadata_dictionary = dataset_title_dict(project_gdb)
        #arcpy.AddMessage("Creating the Metadata Dictionary. Completed")

        #workspaces = [project_gdb, crfs_folder]
        workspaces = [crfs_folder]

        for workspace in workspaces:

            arcpy.env.workspace        = workspace
            arcpy.env.scratchWorkspace = rf"{scratch_folder}\scratch.gdb"

            datasets = list()

            walk = arcpy.da.Walk(workspace)

            for dirpath, dirnames, filenames in walk:
                for filename in filenames:
                    datasets.append(os.path.join(dirpath, filename))
                    del filename
                del dirpath, dirnames, filenames
            del walk

            for dataset_path in sorted(datasets):
                #arcpy.AddMessage(dataset_path)
                dataset_name = os.path.basename(dataset_path)

                arcpy.AddMessage(f"Dataset Name: {dataset_name}")

                if "Datasets" == dataset_name:

                    arcpy.AddMessage(f"\tDataset Table")

                    datasets_table_template = rf"{metadata_folder}\datasets_table_template.xml"
                    template_md = md.Metadata(datasets_table_template)

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    #dataset_md.importMetadata(datasets_table_template)
                    dataset_md.save()
                    #dataset_md.synchronize("SELECTIVE")

                    del empty_md, template_md, datasets_table_template

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    del dataset_md

                elif "Species_Filter" == dataset_name:

                    arcpy.AddMessage(f"\tSpecies Filter Table")

                    species_filter_table_template = rf"{metadata_folder}\species_filter_table_template.xml"
                    template_md = md.Metadata(species_filter_table_template)

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    del empty_md, template_md, species_filter_table_template

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    del dataset_md

                elif "Indicators" in dataset_name:

                    arcpy.AddMessage(f"\tIndicators")

                    if dataset_name == "Indicators":
                        indicators_template = rf"{metadata_folder}\indicators_template.xml"
                    else:
                        indicators_template = rf"{metadata_folder}\region_indicators_template.xml"

                    template_md = md.Metadata(indicators_template)

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    del empty_md, template_md, indicators_template

                    # Max-Min Year range table
                    years_md = unique_years(dataset_path)
                    _tags = f", {min(years_md)} to {max(years_md)}"
                    del years_md

                    #print(metadata_dictionary[dataset_name]["Tags"])
                    #print(_tags)

                    if dataset_name == "Indicators":
                        dataset_name = f"{dataset_name}_Table"
                    else:
                        pass

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"] + _tags
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    del dataset_md, _tags

                elif "LayerSpeciesYearImageName" in dataset_name:

                    arcpy.AddMessage(f"\tLayer Species Year Image Name")

                    layer_species_year_image_name_template = rf"{metadata_folder}\layer_species_year_image_name_template.xml"
                    template_md = md.Metadata(layer_species_year_image_name_template)

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    del empty_md, template_md, layer_species_year_image_name_template

                    # Max-Min Year range table
                    years_md = unique_years(dataset_path)
                    _tags = f", {min(years_md)} to {max(years_md)}"
                    del years_md

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"] + _tags
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    del dataset_md, _tags

                elif dataset_name.endswith("Boundary"):

                    arcpy.AddMessage(f"\tBoundary")

                    boundary_template = rf"{metadata_folder}\boundary_template.xml"
                    template_md = md.Metadata(boundary_template)

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    del empty_md, template_md, boundary_template

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    del dataset_md

                elif dataset_name.endswith("Extent_Points"):

                    arcpy.AddMessage(f"\tExtent_Points")

                    extent_points_template = rf"{metadata_folder}\extent_points_template.xml"
                    template_md = md.Metadata(extent_points_template)

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    del empty_md, template_md, extent_points_template

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    del dataset_md

                elif dataset_name.endswith("Fishnet"):

                    arcpy.AddMessage(f"\tFishnet")

                    fishnet_template = rf"{metadata_folder}\fishnet_template.xml"
                    template_md = md.Metadata(fishnet_template)

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    del empty_md, template_md, fishnet_template

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    del dataset_md

                elif dataset_name.endswith("Lat_Long"):

                    arcpy.AddMessage(f"\tLat_Long")

                    lat_long_template = rf"{metadata_folder}\lat_long_template.xml"
                    template_md = md.Metadata(lat_long_template)

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    del empty_md, template_md, lat_long_template

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    del dataset_md

                elif dataset_name.endswith("Region"):

                    arcpy.AddMessage(f"\tRegion")

                    region_template = rf"{metadata_folder}\region_template.xml"
                    template_md = md.Metadata(region_template)

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    del empty_md, template_md, region_template

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    del dataset_md

                elif dataset_name.endswith("Sample_Locations"):

                    arcpy.AddMessage(f"\tSample_Locations")

                    sample_locations_template = rf"{metadata_folder}\sample_locations_template.xml"
                    template_md = md.Metadata(sample_locations_template)

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    del empty_md, template_md, sample_locations_template

                    # Max-Min Year range table
                    years_md = unique_years(dataset_path)
                    _tags = f", {min(years_md)} to {max(years_md)}"
                    del years_md

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"] + _tags
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    del dataset_md, _tags

                elif dataset_name.endswith("GRID_Points"):

                    arcpy.AddMessage(f"\tGRID_Points")

                    grid_points_template = rf"{metadata_folder}\grid_points_template.xml"
                    template_md = md.Metadata(grid_points_template)

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    del empty_md, template_md, grid_points_template

                    # Max-Min Year range table
                    years_md = unique_years(dataset_path)
                    _tags = f", {min(years_md)} to {max(years_md)}"
                    del years_md

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"] + _tags
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    del dataset_md, _tags

                elif "DisMAP_Regions" == dataset_name:

                    arcpy.AddMessage(f"\tDisMAP_Regions")

                    dismap_regions_template = rf"{metadata_folder}\dismap_regions_template.xml"
                    template_md = md.Metadata(dismap_regions_template)

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    del empty_md, template_md, dismap_regions_template

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    del dataset_md

                elif dataset_name.endswith("Bathymetry"):

                    arcpy.AddMessage(f"\tBathymetry")

                    bathymetry_template = rf"{metadata_folder}\bathymetry_template.xml"
                    template_md = md.Metadata(bathymetry_template)

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    del empty_md, template_md, bathymetry_template

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    del dataset_md

                elif dataset_name.endswith("Latitude"):

                    arcpy.AddMessage(f"\tLatitude")

                    latitude_template = rf"{metadata_folder}\latitude_template.xml"
                    template_md = md.Metadata(latitude_template)

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    del empty_md, template_md, latitude_template

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    del dataset_md

                elif dataset_name.endswith("Longitude"):

                    arcpy.AddMessage(f"\tLongitude")

                    longitude_template = rf"{metadata_folder}\longitude_template.xml"
                    template_md = md.Metadata(longitude_template)

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    del empty_md, template_md, longitude_template

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    del dataset_md

                elif dataset_name.endswith("Raster_Mask"):

                    arcpy.AddMessage(f"\tRaster_Mask")

                    raster_mask_template = rf"{metadata_folder}\raster_mask_template.xml"
                    template_md = md.Metadata(raster_mask_template)

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    del empty_md, template_md, raster_mask_template

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    del dataset_md

                elif dataset_name.endswith("Mosaic"):

                    arcpy.AddMessage(f"\tMosaic")

                    mosaic_template = rf"{metadata_folder}\mosaic_template.xml"
                    template_md = md.Metadata(mosaic_template)

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    del empty_md, template_md, mosaic_template

                    # Max-Min Year range table
                    years_md = unique_years(dataset_path)
                    _tags = f", {min(years_md)} to {max(years_md)}"
                    del years_md

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"] + _tags
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    del dataset_md, _tags

                elif dataset_name.endswith(".crf"):

                    arcpy.AddMessage(f"\tCRF")
                    #print(dataset_name)
                    #print(dataset_path)
                    #dataset_path = dataset_path.replace(crfs_folder, project_gdb).replace(".crf", "_Mosaic")
                    #print(dataset_path)

                    crf_template = rf"{metadata_folder}\crf_template.xml"
                    template_md = md.Metadata(crf_template)

                    dataset_md = md.Metadata(dataset_path)
                    empty_md   = md.Metadata()
                    dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    del empty_md, template_md, crf_template

                    # Max-Min Year range table
                    years_md = unique_years(dataset_path.replace(crfs_folder, project_gdb).replace(".crf", "_Mosaic"))
                    _tags = f", {min(years_md)} to {max(years_md)}"
                    del years_md

                    dataset_md.title             = metadata_dictionary[dataset_name.replace(".crf", "_CRF")]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name.replace(".crf", "_CRF")]["Tags"] + _tags
                    dataset_md.summary           = metadata_dictionary[dataset_name.replace(".crf", "_CRF")]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name.replace(".crf", "_CRF")]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name.replace(".crf", "_CRF")]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name.replace(".crf", "_CRF")]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    del dataset_md, _tags

                else:
                    arcpy.AddMessage(f"\tRegion Table")

                    if dataset_name.endswith("IDW"):

                        idw_region_table_template = rf"{metadata_folder}\idw_region_table_template.xml"
                        template_md = md.Metadata(idw_region_table_template)

                        dataset_md = md.Metadata(dataset_path)
                        empty_md   = md.Metadata()
                        dataset_md.copy(empty_md)
                        dataset_md.save()
                        dataset_md.copy(template_md)
                        dataset_md.save()
                        del empty_md, template_md, idw_region_table_template

                        # Max-Min Year range table
                        years_md = unique_years(dataset_path)
                        _tags = f", {min(years_md)} to {max(years_md)}"
                        del years_md

                        dataset_md.title             = metadata_dictionary[f"{dataset_name}"]["Dataset Service Title"]
                        dataset_md.tags              = metadata_dictionary[f"{dataset_name}"]["Tags"] + _tags
                        dataset_md.summary           = metadata_dictionary[f"{dataset_name}"]["Summary"]
                        dataset_md.description       = metadata_dictionary[f"{dataset_name}"]["Description"]
                        dataset_md.credits           = metadata_dictionary[f"{dataset_name}"]["Credits"]
                        dataset_md.accessConstraints = metadata_dictionary[f"{dataset_name}"]["Access Constraints"]
                        dataset_md.save()

                        dataset_md.synchronize("ALWAYS")

                        del dataset_md, _tags

                    elif dataset_name.endswith("GLMME"):

                        glmme_region_table_template = rf"{metadata_folder}\glmme_region_table_template.xml"
                        template_md = md.Metadata(glmme_region_table_template)

                        dataset_md = md.Metadata(dataset_path)
                        empty_md   = md.Metadata()
                        dataset_md.copy(empty_md)
                        dataset_md.save()
                        dataset_md.copy(template_md)
                        dataset_md.save()
                        del empty_md, template_md, glmme_region_table_template

                        # Max-Min Year range table
                        years_md = unique_years(dataset_path)
                        _tags = f", {min(years_md)} to {max(years_md)}"
                        del years_md

                        dataset_md.title             = metadata_dictionary[f"{dataset_name}"]["Dataset Service Title"]
                        dataset_md.tags              = metadata_dictionary[f"{dataset_name}"]["Tags"] + _tags
                        dataset_md.summary           = metadata_dictionary[f"{dataset_name}"]["Summary"]
                        dataset_md.description       = metadata_dictionary[f"{dataset_name}"]["Description"]
                        dataset_md.credits           = metadata_dictionary[f"{dataset_name}"]["Credits"]
                        dataset_md.accessConstraints = metadata_dictionary[f"{dataset_name}"]["Access Constraints"]
                        dataset_md.save()

                        dataset_md.synchronize("ALWAYS")

                        del dataset_md, _tags

                    else:
                        pass
                del dataset_name, dataset_path
            del workspace

        base_project_folder = os.path.dirname(os.path.dirname(__file__))

        #pretty_format_xml_files(rf"{base_project_folder}\{project}\Current Metadata")

        del datasets

        # Variables set in function
        del project_gdb, base_project_folder, metadata_folder
        del project_folder, scratch_folder, crfs_folder
        del metadata_dictionary, workspaces

        # Imports
        del dismap, dataset_title_dict, pretty_format_xml_files, unique_years
        del md

        # Function Parameters
        del base_project_file, project

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

def create_maps(base_project_file="", project=""):
    try:
        # Import
        from arcpy import metadata as md

        import dismap
        importlib.reload(dismap)
        from dismap import dataset_title_dict, pretty_format_xml_file

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2)
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        # Map Cleanup
        MapCleanup = False
        if MapCleanup:
            map_cleanup(base_project_file)
        del MapCleanup

        base_project_folder = rf"{os.path.dirname(base_project_file)}"
        base_project_file   = rf"{base_project_folder}\DisMAP.aprx"
        project_folder      = rf"{base_project_folder}\{project}"
        project_gdb         = rf"{project_folder}\{project}.gdb"
        metadata_folder     = rf"{project_folder}\Export Metadata"
        scratch_folder      = rf"{project_folder}\Scratch"

        arcpy.env.workspace        = project_gdb
        arcpy.env.scratchWorkspace = rf"{scratch_folder}\scratch.gdb"

        aprx = arcpy.mp.ArcGISProject(base_project_file)
        home_folder = aprx.homeFolder

        #arcpy.AddMessage(f"\n{'-' * 90}\n")

        metadata_dictionary = dataset_title_dict(project_gdb)

        datasets = list()

        walk = arcpy.da.Walk(project_gdb)

        for dirpath, dirnames, filenames in walk:
            for filename in filenames:
                datasets.append(os.path.join(dirpath, filename))
                del filename
            del dirpath, dirnames, filenames
        del walk

        for dataset_path in sorted(datasets):
            arcpy.AddMessage(dataset_path)
            dataset_name = os.path.basename(dataset_path)
            data_type = arcpy.Describe(dataset_path).dataType
            if data_type == "Table":
                #arcpy.AddMessage(f"Dataset Name: {dataset_name}")
                #arcpy.AddMessage(f"\tData Type: {data_type}")

                if "IDW" in dataset_name:
                    arcpy.AddMessage(f"Dataset Name: {dataset_name}")
                    if "Indicators" in dataset_name:
                        arcpy.AddMessage(f"\tRegion Indicators")

                    elif "LayerSpeciesYearImageName" in dataset_name:
                        arcpy.AddMessage(f"\tRegion Layer Species Year Image Name")

                    else:
                        arcpy.AddMessage(f"\tRegion Table")

                elif "GLMME" in dataset_name:
                    arcpy.AddMessage(f"Dataset Name: {dataset_name}")
                    if "Indicators" in dataset_name:
                        arcpy.AddMessage(f"\tGLMME Region Indicators")

                    elif "LayerSpeciesYearImageName" in dataset_name:
                        arcpy.AddMessage(f"\tGLMME Layer Species Year Image Name")

                    else:
                        arcpy.AddMessage(f"\tGLMME Region Table")

                else:
                    arcpy.AddMessage(f"Dataset Name: {dataset_name}")
                    if "Indicators" in dataset_name:
                        arcpy.AddMessage(f"\tMain Indicators Table")

                    elif "LayerSpeciesYearImageName" in dataset_name:
                        arcpy.AddMessage(f"\tLayer Species Year Image Name")

                    elif "Datasets" in dataset_name:
                        arcpy.AddMessage(f"\tDataset Table")

                    elif "Species_Filter" in dataset_name:
                        arcpy.AddMessage(f"\tSpecies Filter Table")

                    else:
                        arcpy.AddMessage(f"\tDataset Name: {dataset_name}")

            elif data_type == "FeatureClass":
                #arcpy.AddMessage(f"\tData Type: {data_type}")

                if "IDW" in dataset_name:
                    arcpy.AddMessage(f"Dataset Name: {dataset_name}")
                    if dataset_name.endswith("Boundary"):
                        arcpy.AddMessage(f"\tBoundary")

                    elif dataset_name.endswith("Extent_Points"):
                        arcpy.AddMessage(f"\tExtent_Points")

                    elif dataset_name.endswith("Fishnet"):
                        arcpy.AddMessage(f"\tFishnet")

                    elif dataset_name.endswith("Lat_Long"):
                        arcpy.AddMessage(f"\tLat_Long")

                    elif dataset_name.endswith("Region"):
                        arcpy.AddMessage(f"\tRegion")

                    elif dataset_name.endswith("Sample_Locations"):
                        arcpy.AddMessage(f"\tSample_Locations")

                    else:
                        pass

                elif "GLMME" in dataset_name:
                    arcpy.AddMessage(f"Dataset Name: {dataset_name}")
                    if dataset_name.endswith("Boundary"):
                        arcpy.AddMessage(f"\tBoundary")

                    elif dataset_name.endswith("Extent_Points"):
                        arcpy.AddMessage(f"\tExtent_Points")

                    elif dataset_name.endswith("Fishnet"):
                        arcpy.AddMessage(f"\tFishnet")

                    elif dataset_name.endswith("Lat_Long"):
                        arcpy.AddMessage(f"\tLat_Long")

                    elif dataset_name.endswith("Region"):
                        arcpy.AddMessage(f"\tRegion")

                    elif dataset_name.endswith("GRID_Points"):
                        arcpy.AddMessage(f"\tGRID_Points")

                    else:
                        pass

                elif "DisMAP_Regions" == dataset_name:
                    arcpy.AddMessage(f"Dataset Name: {dataset_name}")
                    if dataset_name.endswith("Regions"):
                        arcpy.AddMessage(f"\tDisMAP Regions")

                else:
                    arcpy.AddMessage(f"Else Dataset Name: {dataset_name}")

            elif data_type == "RasterDataset":

                if "IDW" in dataset_name:
                    arcpy.AddMessage(f"Dataset Name: {dataset_name}")
                    if dataset_name.endswith("Bathymetry"):
                        arcpy.AddMessage(f"\tBathymetry")

                    elif dataset_name.endswith("Latitude"):
                        arcpy.AddMessage(f"\tLatitude")

                    elif dataset_name.endswith("Longitude"):
                        arcpy.AddMessage(f"\tLongitude")

                    elif dataset_name.endswith("Raster_Mask"):
                        arcpy.AddMessage(f"\tRaster_Mask")

                elif "GLMME" in dataset_name:
                    arcpy.AddMessage(f"Dataset Name: {dataset_name}")
                    if dataset_name.endswith("Bathymetry"):
                        arcpy.AddMessage(f"\tBathymetry")

                    elif dataset_name.endswith("Latitude"):
                        arcpy.AddMessage(f"\tLatitude")

                    elif dataset_name.endswith("Longitude"):
                        arcpy.AddMessage(f"\tLongitude")

                    elif dataset_name.endswith("Raster_Mask"):
                        arcpy.AddMessage(f"\tRaster_Mask")

            elif data_type == "MosaicDataset":

                if "IDW" in dataset_name:
                    arcpy.AddMessage(f"Dataset Name: {dataset_name}")
                    if dataset_name.endswith("Mosaic"):
                        arcpy.AddMessage(f"\tMosaic")

                elif "GLMME" in dataset_name:
                    arcpy.AddMessage(f"Dataset Name: {dataset_name}")
                    if dataset_name.endswith("Mosaic"):
                        arcpy.AddMessage(f"\tMosaic")

                elif "CRF" in dataset_name:
                    arcpy.AddMessage(f"Dataset Name: {dataset_name}")
                    if dataset_name.endswith("CRF"):
                        arcpy.AddMessage(f"\tCRF")

                else:
                    pass
            else:
                pass

            del data_type

            del dataset_name, dataset_path
        del datasets

##        # DatasetCode, CSVFile, TransformUnit, TableName, GeographicArea, CellSize,
##        # PointFeatureType, FeatureClassName, Region, Season, DateCode, Status,
##        # DistributionProjectCode, DistributionProjectName, SummaryProduct,
##        # FilterRegion, FilterSubRegion, FeatureServiceName, FeatureServiceTitle,
##        # MosaicName, MosaicTitle, ImageServiceName, ImageServiceTitle
##
##        # Get values for table_name from Datasets table
##        #fields = ["FeatureClassName", "FeatureServiceName", "FeatureServiceTitle"]
##        fields = ["DatasetCode", "PointFeatureType", "FeatureClassName", "Region", "Season", "DateCode", "DistributionProjectCode"]
##        datasets = [row for row in arcpy.da.SearchCursor(rf"{project_gdb}\Datasets", fields, where_clause = f"FeatureClassName IS NOT NULL AND DistributionProjectCode NOT IN ('GLMME', 'GFDL')")]
##        #datasets = [row for row in arcpy.da.SearchCursor(rf"{project_gdb}\Datasets", fields, where_clause = f"FeatureClassName IS NOT NULL and TableName = 'AI_IDW'")]
##        del fields
##
##        for dataset in datasets:
##            dataset_code, point_feature_type, feature_class_name, region_latitude, season, date_code, distribution_project_code = dataset
##
##            feature_service_name  = f"{dataset_code}_{point_feature_type}_{date_code}".replace("None", "").replace(" ", "_").replace("__", "_")
##
##            if distribution_project_code == "IDW":
##                feature_service_title = f"{region_latitude} {season} {point_feature_type} {date_code}".replace("None", "").replace("  ", " ")
##            elif distribution_project_code in ["GLMME", "GFDL"]:
##                feature_service_title = f"{region_latitude} {distribution_project_code} {point_feature_type} {date_code}".replace("None", "").replace("  ", " ")
##            else:
##                feature_service_title = f"{feature_service_name}".replace("_", " ")
##
##            map_title = feature_service_title.replace("GRID Points", "").replace("Sample Locations", "").replace("  ", " ")
##
##            feature_class_path = f"{project_gdb}\{feature_class_name}"
##
##            arcpy.AddMessage(f"Dataset Code: {dataset_code}")
##            arcpy.AddMessage(f"\tFeature Service Name:   {feature_service_name}")
##            arcpy.AddMessage(f"\tFeature Service Title:  {feature_service_title}")
##            arcpy.AddMessage(f"\tMap Title:              {map_title}")
##            arcpy.AddMessage(f"\tFeature Class Name:     {feature_class_name}")
##            arcpy.AddMessage(f"\tFeature Class Path:     {feature_class_path}")
##
##            height = arcpy.Describe(feature_class_path).extent.YMax - arcpy.Describe(feature_class_path).extent.YMin
##            width  = arcpy.Describe(feature_class_path).extent.XMax - arcpy.Describe(feature_class_path).extent.XMin
##
##            # map_width, map_height
##            map_width, map_height = 2, 3
##            #map_width, map_height = 8.5, 11
##
##            if height > width:
##                page_height = map_height; page_width = map_width
##            elif height < width:
##                page_height = map_width; page_width = map_height
##            else:
##                page_width = map_width; page_height = map_height
##
##            del map_width, map_height
##            del height, width
##
##            if map_title not in [cm.name for cm in aprx.listMaps()]:
##                arcpy.AddMessage(f"Creating Map: {map_title}")
##                aprx.createMap(f"{map_title}", "Map")
##                aprx.save()
##
##            if map_title not in [cl.name for cl in aprx.listLayouts()]:
##                arcpy.AddMessage(f"Creating Layout: {map_title}")
##                aprx.createLayout(page_width, page_height, "INCH", f"{map_title}")
##                aprx.save()
##
##            del feature_service_name, feature_service_title
##            del dataset_code, point_feature_type, feature_class_name, region_latitude, season
##            del date_code, distribution_project_code
##
##            current_map = [cm for cm in aprx.listMaps() if cm.name == map_title][0]
##            arcpy.AddMessage(f"Current Map:  {current_map.name}")
##
##            feature_class_layer = arcpy.management.MakeFeatureLayer(feature_class_path, f"{map_title}")
##
##            feature_class_layer_file = arcpy.management.SaveToLayerFile(feature_class_layer, rf"{home_folder}\{project}\Layers\{feature_class_layer}.lyrx")
##            del feature_class_layer_file
##
##            feature_class_layer_file = arcpy.mp.LayerFile(rf"{home_folder}\{project}\Layers\{feature_class_layer}.lyrx")
##
##            arcpy.management.Delete(feature_class_layer)
##            del feature_class_layer
##
##            current_map.addLayer(feature_class_layer_file)
##            del feature_class_layer_file
##
##            #aprx_basemaps = aprx.listBasemaps()
##            #basemap = 'GEBCO Basemap/Contours (NOAA NCEI Visualization)'
##            basemap = "Terrain with Labels"
##
##            current_map.addBasemap(basemap)
##            del basemap
##
##            #current_map_view = current_map.defaultView
##            #current_map_view.exportToPNG(rf"{home_folder}\{project}\Layers\{map_title}.png", width=200, height=133, resolution = 96, color_mode="24-BIT_TRUE_COLOR", embed_color_profile=True)
##            #del current_map_view
##
##        # #            from arcpy import metadata as md
##        # #
##        # #            fc_md = md.Metadata(feature_class_path)
##        # #            fc_md.thumbnailUri = rf"{home_folder}\{project}\Layers\{map_title}.png"
##        # #            fc_md.save()
##        # #            del fc_md
##        # #            del md
##
##            aprx.save()
##
##            current_layout = [cl for cl in aprx.listLayouts() if cl.name == map_title][0]
##            arcpy.AddMessage(f"Current Layout: {current_layout.name}")
##
##            current_layout.openView()
##
##            arcpy.AddMessage(f"Create a new map frame using a point geometry")
##            #Create a new map frame using a point geometry
##            mf1 = current_layout.createMapFrame(arcpy.Point(0.01,0.01), current_map, 'New MF - Point')
##            #mf1.elementWidth = 10
##            #mf1.elementHeight = 7.5
##            mf1.elementWidth  = page_width  - 0.01
##            mf1.elementHeight = page_height - 0.01
##
##            lyr = current_map.listLayers(f"{map_title}")[0]
##
##            #Zoom to ALL selected features and export to PDF
##            arcpy.SelectLayerByAttribute_management(lyr, 'NEW_SELECTION')
##            mf1.zoomToAllLayers(True)
##            arcpy.SelectLayerByAttribute_management(lyr, 'CLEAR_SELECTION')
##
##            #Set the map frame extent to the extent of a layer and export to PDF
##            mf1.camera.setExtent(mf1.getLayerExtent(lyr, False, True))
##            mf1.camera.scale = mf1.camera.scale * 1.1 #add a slight buffer
##
##            del lyr
##
##            arcpy.AddMessage(f"Create a new bookmark set to the map frame's default extent")
##            #Create a new bookmark set to the map frame's default extent
##            bkmk = mf1.createBookmark('Default Extent', "The map's default extent")
##            bkmk.updateThumbnail()
##            del mf1
##            del bkmk
##
##            #Create point text element using a system style item
##            #txtStyleItem = aprx.listStyleItems('ArcGIS 2D', 'TEXT', 'Title (Serif)')[0]
##            #ptTxt = aprx.createTextElement(current_layout, arcpy.Point(5.5, 4.25), 'POINT', f'{map_title}', 10, style_item=txtStyleItem)
##            #del txtStyleItem
##
##            #Change the anchor position and reposition the text to center
##            #ptTxt.setAnchor('Center_Point')
##            #ptTxt.elementPositionX = page_width / 2.0
##            #ptTxt.elementPositionY = page_height - 0.25
##            #del ptTxt
##
##            #arcpy.AddMessage(f"Using CIM to update border")
##            #current_layout_cim = current_layout.getDefinition('V3')
##            #for elm in current_layout_cim.elements:
##            #    if type(elm).__name__ == 'CIMMapFrame':
##            #        if elm.graphicFrame.borderSymbol.symbol.symbolLayers:
##            #            sym = elm.graphicFrame.borderSymbol.symbol.symbolLayers[0]
##            #            sym.width = 5
##            #            sym.color.values = [255, 0, 0, 100]
##            #        else:
##            #            arcpy.AddWarning(elm.name + ' has NO symbol layers')
##            #current_layout.setDefinition(current_layout_cim)
##            #del current_layout_cim, elm, sym
##
##            ExportLayout = True
##            if ExportLayout:
##                #Export the resulting imported layout and changes to JPEG
##                arcpy.AddMessage(f"Exporting '{current_layout.name}'")
##                current_layout.exportToJPEG(rf"{home_folder}\{project}\Layouts\{current_layout.name}.jpg")
##            del ExportLayout
##
##
##            from arcpy import metadata as md
##
##            fc_md = md.Metadata(feature_class_path)
##            #fc_md.thumbnailUri = rf"{home_folder}\{project}\Layers\{map_title}.png"
##            fc_md.thumbnailUri = rf"{home_folder}\{project}\Layouts\{current_layout.name}.jpg"
##            fc_md.save()
##            del fc_md
##            del md
##
##            aprx.save()
##
##            aprx.deleteItem(current_map); del current_map
##            aprx.deleteItem(current_layout); del current_layout
##
##            del page_width, page_height
##            del map_title, feature_class_path
##            del dataset
##        del datasets
##
##        # TODO: Possibly create a dictionary that can be saved to JSON
##
##        aprx.save()
##
##        arcpy.AddMessage(f"\nCurrent Maps & Layouts")
##
##        current_maps    = aprx.listMaps()
##        current_layouts = aprx.listLayouts()
##
##        if current_maps:
##            arcpy.AddMessage(f"\nCurrent Maps\n")
##            for current_map in current_maps:
##                arcpy.AddMessage(f"\tProject Map: {current_map.name}")
##                del current_map
##        else:
##            arcpy.AddWarning("No maps in Project")
##
##        if current_layouts:
##            arcpy.AddMessage(f"\nCurrent Layouts\n")
##            for current_layout in current_layouts:
##                arcpy.AddMessage(f"\tProject Layout: {current_layout.name}")
##                del current_layout
##        else:
##            arcpy.AddWarning("No layouts in Project")
##
##        arcpy.AddMessage(f"\n{'-' * 90}\n")
##
##        del current_layouts, current_maps

        # Variables set in function for aprx
        del home_folder
        # Save aprx one more time and then delete
        aprx.save()
        del aprx

        # Variables set in function
        del project_gdb, base_project_folder, metadata_folder
        del project_folder, scratch_folder
        del metadata_dictionary

        # Imports
        del dismap, dataset_title_dict
        del md

        # Function Parameters
        del base_project_file, project

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

def main(project=""):
    try:
        # Imports
        import dismap
        importlib.reload(dismap)

        arcpy.env.overwriteOutput = True
        arcpy.env.parallelProcessingFactor = "100%"

        base_project_folder = os.path.dirname(os.path.dirname(__file__))
        base_project_file   = rf"{base_project_folder}\DisMAP.aprx"
        project_gdb         = rf"{base_project_folder}\{project}\{project}.gdb"

        # Test if passed workspace exists, if not raise SystemExit
        if not arcpy.Exists(base_project_file):
            raise SystemExit(line_info(f"{os.path.basename(base_project_file)} is missing!!"))

        # Test if passed workspace exists, if not raise SystemExit
        if not arcpy.Exists(project_gdb):
            raise SystemExit(line_info(f"{os.path.basename(project_gdb)} is missing!!"))

        del base_project_folder

        Backup = False
        if Backup:
            dismap.backup_gdb(project_gdb)
        del Backup

        # Imports
        del dismap
        # Function parameters

        try:

            CreateFeatureClassLayers = False
            if CreateFeatureClassLayers:
                result = create_feature_class_layers(base_project_file, project)
                arcpy.AddMessage(result)
                del result
            del CreateFeatureClassLayers

            CreateFeaturClasseServices = False
            if CreateFeaturClasseServices:
                result = create_feature_class_services(base_project_file, project)
                arcpy.AddMessage(result)
                del result
            del CreateFeaturClasseServices

            CreateImagesServices = False
            if CreateImagesServices:
                result = create_image_services(base_project_file, project)
                arcpy.AddMessage(result)
                del result
            del CreateImagesServices

            # UpdateMetadataFromPublishedMd = False
            # if UpdateMetadataFromPublishedMd:
            #    update_metadata_from_published_md(base_project_file, project)
            # del UpdateMetadataFromPublishedMd

            CreateMaps = False
            if CreateMaps:
                result = create_maps(base_project_file, project)
                arcpy.AddMessage(result)
                del result
            del CreateMaps

            CreateBasicTemplateXMLFiles = False
            if CreateBasicTemplateXMLFiles:
                result = create_basic_template_xml_files(base_project_file, project)
                arcpy.AddMessage(result)
                del result
            del CreateBasicTemplateXMLFiles

            ImportBasicTemplateXmlFiles = False
            if ImportBasicTemplateXmlFiles:
                result = import_basic_template_xml_files(base_project_file, project)
                arcpy.AddMessage(result)
                del result
            del ImportBasicTemplateXmlFiles

        except Exception as e:
            print(e)

        # Variable created in function
        del project_gdb
        # Function parameters
        del base_project_file, project

    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(arcpy.GetMessages())
        traceback.print_exc()
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages())
        traceback.print_exc()
    except SystemExit as se:
        print(se)
    except Exception as e:
        print(e)
    except:
        traceback.print_exc()
    else:
        try:
            remaining_keys = [key for key in locals().keys() if not key.startswith('__')]
            if remaining_keys:
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del remaining_keys
        except:
            traceback.print_exc()
    finally:
        pass

if __name__ == "__main__":
    try:
        # Import this Python module
        import publish_to_portal_director
        importlib.reload(publish_to_portal_director)

        print(f"{'-' * 90}")
        print(f"Python Script:  {os.path.basename(__file__)}")
        print(f"Location:       {os.path.dirname(__file__)}")
        print(f"Python Version: {sys.version} Environment: {os.path.basename(sys.exec_prefix)}")
        print(f"{'-' * 90}\n")

        #project = "May 1 2024"
        #project = "July 1 2024"
        project = "December 1 2024"

        # Tested on 8/1/2024 -- PASSED
        main(project=project)

        del project

        from time import localtime, strftime

        print(f"\n{'-' * 90}")
        print(f"Python script: {os.path.basename(__file__)} successfully completed {strftime('%a %b %d %I:%M %p', localtime())}")
        print(f"{'-' * 90}")
        del localtime, strftime

    except SystemExit:
        pass
    except Exception:
        pass
    except:
        traceback.print_exc()
    else:
        leave_out_keys = ["leave_out_keys" ]
        leave_out_keys.extend([name for name, obj in inspect.getmembers(sys.modules[__name__]) if inspect.isfunction(obj) or inspect.ismodule(obj)])
        remaining_keys = [key for key in locals().keys() if not key.startswith("__") and key not in leave_out_keys]
        if remaining_keys: arcpy.AddWarning(f"Remaining Keys: ##--> '{', '.join(remaining_keys)}' <--##")
        del leave_out_keys, remaining_keys
    finally:
        pass
