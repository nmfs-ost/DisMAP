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
import os
import sys
import traceback

import arcpy  # third-parties second

def trace():
    import sys, traceback  # noqa: E401
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    line = tbinfo.split(", ")[1]
    #filename = sys.path[0] + os.sep + f"{os.path.basename(__file__)}"
    filename = os.path.basename(__file__)
    synerror = traceback.format_exc().splitlines()[-1]
    return line, filename, synerror

def feature_sharing_draft_report(sd_draft=""):
    try:
        import xml.dom.minidom as DOM

        docs = DOM.parse(sd_draft)
        key_list = docs.getElementsByTagName("Key")
        value_list = docs.getElementsByTagName("Value")

        for i in range(key_list.length):
            value = f"Value: {value_list[i].firstChild.nodeValue}" if value_list[i].firstChild else "Value is missing"

            arcpy.AddMessage(f"\t\tKey: {key_list[i].firstChild.nodeValue:<45} {value}")
            # arcpy.AddMessage(f"\t\tKey: {key_list[i].firstChild.nodeValue:<45} {value[:50]}")
            del i, value

        del DOM, key_list, value_list, docs
        del sd_draft

    except arcpy.ExecuteError:
        #Return Geoprocessing tool specific errors
        line, filename, err = trace()
        arcpy.AddError("Geoprocessing error on " + line + " of " + filename + " :")
        for msg in range(0, arcpy.GetMessageCount()):
            if arcpy.GetSeverity(msg) == 2:
                arcpy.AddReturnMessage(msg)
        return False
    except:  # noqa: E722
        #Gets non-tool errors
        line, filename, err = trace()
        arcpy.AddError("Python error on " + line + " of " + filename)
        arcpy.AddError(err)
        return False
    else:
        return True

def create_feature_class_layers(project_gdb=""):
    try:
        # Import
        from arcpy import metadata as md
        from dismap_tools import dataset_title_dict, parse_xml_file_format_and_save, clear_folder

        # Test if passed workspace exists, if not sys.exit()
        if not arcpy.Exists(project_gdb):
            sys.exit()(f"{os.path.basename(project_gdb)} is missing!!")

        # Set History and Metadata logs, set serverity and message level
        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(1) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        # Set basic workkpace variables
        project_folder    = os.path.dirname(project_gdb)
        project_name      = os.path.basename(project_folder)
        csv_data_folder   = rf"{project_folder}\CSV_Data"
        scratch_folder    = os.path.join(project_folder, "Scratch")
        scratch_workspace = os.path.join(project_folder, "Scratch\\scratch.gdb")

        # Clear Scratch Folder
        clear_folder(folder=scratch_folder)

        # Create Scratch Workspace for Project
        if not arcpy.Exists(os.path.join(scratch_folder, "scratch.gdb")):
            if not arcpy.Exists(scratch_folder):
                os.makedirs(scratch_folder)
            if not arcpy.Exists(os.path.join(scratch_folder, "scratch.gdb")):
                arcpy.management.CreateFileGDB(rf"{scratch_folder}", "scratch")

        # Set basic workkpace variables
        arcpy.env.workspace                = project_gdb
        arcpy.env.scratchWorkspace         = scratch_workspace
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        aprx = arcpy.mp.ArcGISProject(rf"{project_folder}\{project_name}.aprx")

        del scratch_folder, scratch_workspace

        arcpy.AddMessage("Loading the Dataset Title Dictionary. Please wait")
        datasets_dict = dataset_title_dict(project_gdb)

        datasets = []

        #datasets.extend(arcpy.ListFeatureClasses("AI_IDW_Sample_Locations"))
        datasets.extend(arcpy.ListFeatureClasses("*Sample_Locations"))
        datasets.extend(arcpy.ListFeatureClasses("DisMAP_Regions"))
        datasets.extend(arcpy.ListTables("Indicators"))
        datasets.extend(arcpy.ListTables("Species_Filter"))
        datasets.extend(arcpy.ListTables("DisMAP_Survey_Info"))
        datasets.extend(arcpy.ListTables("SpeciesPersistenceIndicatorPercentileBin"))
        datasets.extend(arcpy.ListTables("SpeciesPersistenceIndicatorTrend"))

        for dataset in sorted(datasets):

            feature_service_title = datasets_dict[dataset]["Dataset Service Title"]

            arcpy.AddMessage(f"Dataset: {dataset}")
            arcpy.AddMessage(f"\tTitle: {feature_service_title}")

            desc = arcpy.da.Describe(dataset)

            feature_class_path = rf"{project_gdb}\{dataset}"

            if desc["dataType"] == "FeatureClass":

                arcpy.AddMessage("\tMake Feature Layer")
                feature_class_layer = arcpy.management.MakeFeatureLayer(feature_class_path, feature_service_title)
                feature_class_layer_file = rf"{project_folder}\Layers\{feature_class_layer}.lyrx"

                arcpy.AddMessage("\tSave Layer File")
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

                arcpy.AddMessage("\tMake Table View")
                feature_class_layer = arcpy.management.MakeTableView(
                                                                     in_table     = feature_class_path,
                                                                     out_view     = feature_service_title,
                                                                     where_clause = "",
                                                                     workspace    = project_gdb,
                                                                     field_info   = "OBJECTID OBJECTID VISIBLE NONE;DatasetCode DatasetCode VISIBLE NONE;Region Region VISIBLE NONE;Season Season VISIBLE NONE;DateCode DateCode VISIBLE NONE;Species Species VISIBLE NONE;CommonName CommonName VISIBLE NONE;CoreSpecies CoreSpecies VISIBLE NONE;Year Year VISIBLE NONE;DistributionProjectName DistributionProjectName VISIBLE NONE;DistributionProjectCode DistributionProjectCode VISIBLE NONE;SummaryProduct SummaryProduct VISIBLE NONE;CenterOfGravityLatitude CenterOfGravityLatitude VISIBLE NONE;MinimumLatitude MinimumLatitude VISIBLE NONE;MaximumLatitude MaximumLatitude VISIBLE NONE;OffsetLatitude OffsetLatitude VISIBLE NONE;CenterOfGravityLatitudeSE CenterOfGravityLatitudeSE VISIBLE NONE;CenterOfGravityLongitude CenterOfGravityLongitude VISIBLE NONE;MinimumLongitude MinimumLongitude VISIBLE NONE;MaximumLongitude MaximumLongitude VISIBLE NONE;OffsetLongitude OffsetLongitude VISIBLE NONE;CenterOfGravityLongitudeSE CenterOfGravityLongitudeSE VISIBLE NONE;CenterOfGravityDepth CenterOfGravityDepth VISIBLE NONE;MinimumDepth MinimumDepth VISIBLE NONE;MaximumDepth MaximumDepth VISIBLE NONE;OffsetDepth OffsetDepth VISIBLE NONE;CenterOfGravityDepthSE CenterOfGravityDepthSE VISIBLE NONE"
                                                                    )
                feature_class_layer_file = rf"{project_folder}\Layers\{feature_class_layer}.lyrx"

                arcpy.AddMessage("\tSave Layer File")
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

            if [f.name for f in arcpy.ListFields(feature_class_path) if f.name == "StdTime"]:
                arcpy.AddMessage("\tSet Time Enabled if time field is in dataset")
                # Get time information from a layer in a layer file
                layer_file = arcpy.mp.LayerFile(feature_class_layer_file)
                layer = layer_file.listLayers()[0]
                layer.enableTime("StdTime", "StdTime", True)
                layer.time.timeZone = arcpy.mp.ListTimeZones("(UTC) Coordinated Universal Time")[0]
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
                            arcpy.AddMessage(f"\t\tTime Zone:   {str(layer.time.timeZone)}")
                            del lyrTime, startTime, endTime, timeDelta
                            del startTimeField, endTimeField
                        else:
                            arcpy.AddMessage("No time properties have been set on the layer")
                    else:
                        arcpy.AddMessage("Time is not supported on this layer")
                    del layer
                del layer_file
            else:
                arcpy.AddMessage("\tDataset does not have a time field")

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
            else:
                pass

            arcpy.AddMessage(f"\tCreating Map: {feature_service_title}")
            aprx.createMap(f"{feature_service_title}", "Map")
            aprx.save()

            current_map = aprx.listMaps(feature_service_title)[0]

            basemap = "Terrain with Labels"
            current_map.addLayer(layer_file)
            current_map.addBasemap(basemap)
            aprx.save()
            del basemap

            arcpy.AddMessage("\t\tCreate map thumbnail and update metadata")
            current_map_view = current_map.defaultView
            current_map_view.exportToPNG(
                                            rf"{project_folder}\Layers\{feature_service_title}.png",
                                            width=288,
                                            height=192,
                                            resolution=96,
                                            color_mode="24-BIT_TRUE_COLOR",
                                            embed_color_profile=True,
                                        )
            del current_map_view

            fc_md = md.Metadata(feature_class_path)
            fc_md.title = feature_service_title
            fc_md.thumbnailUri = (rf"{project_folder}\Layers\{feature_service_title}.png")
            fc_md.save()
            fc_md.reload()
            fc_md.saveAsXML(rf"{project_folder}\Metadata_Export\{feature_service_title}.xml")
            del fc_md

            parse_xml_file_format_and_save(csv_data_folder=csv_data_folder, xml_file=rf"{project_folder}\Metadata_Export\{feature_service_title}.xml", sort=True)
            #parse_xml_file_format_and_save(csv_data_folder=csv_data_folder, xml_file="", sort=True)

            in_md = md.Metadata(feature_class_path)
            layer_file.metadata.copy(in_md)
            layer_file.metadata.save()
            layer_file.save()
            current_map.metadata.copy(in_md)
            current_map.metadata.save()
            aprx.save()
            del in_md

            arcpy.AddMessage(f"\t\tLayer File Path:     {layer_file.filePath}")
            arcpy.AddMessage(f"\t\tLayer File Version:  {layer_file.version}")
            arcpy.AddMessage("\t\tLayer File Metadata:")
            arcpy.AddMessage(f"\t\t\tLayer File Title:              {layer_file.metadata.title}")
            #arcpy.AddMessage(f"\t\t\tLayer File Tags:               {layer_file.metadata.tags}")
            #arcpy.AddMessage(f"\t\t\tLayer File Summary:            {layer_file.metadata.summary}")
            #arcpy.AddMessage(f"\t\t\tLayer File Description:        {layer_file.metadata.description}")
            #arcpy.AddMessage(f"\t\t\tLayer File Credits:            {layer_file.metadata.credits}")
            #arcpy.AddMessage(f"\t\t\tLayer File Access Constraints: {layer_file.metadata.accessConstraints}")

            arcpy.AddMessage("\t\tList of layers or tables in Layer File:")
            if current_map.listLayers(feature_service_title):
                layer = current_map.listLayers(feature_service_title)[0]
            elif current_map.listTables(feature_service_title):
                layer = current_map.listTables(feature_service_title)[0]
            else:
                arcpy.AddWarning("Something wrong")

            in_md = md.Metadata(feature_class_path)
            layer.metadata.copy(in_md)
            layer.metadata.save()
            layer_file.save()
            aprx.save()
            del in_md

            arcpy.AddMessage(f"\t\t\tLayer Name: {layer.name}")
            arcpy.AddMessage("\t\t\tLayer Metadata:")
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

        # Declared Variables set in function
        del aprx
        del csv_data_folder, project_folder, project_name

        # Imports
        del dataset_title_dict, parse_xml_file_format_and_save, md

        # Function Parameters
        del project_gdb

    except arcpy.ExecuteError:
        #Return Geoprocessing tool specific errors
        line, filename, err = trace()
        arcpy.AddError("Geoprocessing error on " + line + " of " + filename + " :")
        for msg in range(0, arcpy.GetMessageCount()):
            if arcpy.GetSeverity(msg) == 2:
                arcpy.AddReturnMessage(msg)
        return False
    except:  # noqa: E722
        #Gets non-tool errors
        line, filename, err = trace()
        arcpy.AddError("Python error on " + line + " of " + filename)
        arcpy.AddError(err)
        return False
    else:
        return True

def create_feature_class_services(project_gdb=""):
    try:
        # Import
        from arcpy import metadata as md
        from dismap_tools import dataset_title_dict

        # Test if passed workspace exists, if not sys.exit()
        if not arcpy.Exists(project_gdb):
            sys.exit()(f"{os.path.basename(project_gdb)} is missing!!")

        # Set History and Metadata logs, set serverity and message level
        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(1) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        # Set basic workkpace variables
        project_folder    = os.path.dirname(project_gdb)
        project_name      = os.path.basename(project_folder)
        csv_data_folder   = rf"{project_folder}\CSV_Data"
        scratch_folder    = os.path.join(project_folder, "Scratch")
        scratch_workspace = os.path.join(project_folder, "Scratch\\scratch.gdb")

        # Create Scratch Workspace for Project
        if not arcpy.Exists(os.path.join(scratch_folder, "scratch.gdb")):
            if not arcpy.Exists(scratch_folder):
                os.makedirs(scratch_folder)
            if not arcpy.Exists(os.path.join(scratch_folder, "scratch.gdb")):
                arcpy.management.CreateFileGDB(rf"{scratch_folder}", "scratch")

        # Set basic workkpace variables
        arcpy.env.workspace                = project_gdb
        arcpy.env.scratchWorkspace         = scratch_workspace
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        aprx = arcpy.mp.ArcGISProject(rf"{project_folder}\{project_name}.aprx")

        del scratch_folder, scratch_workspace

        arcpy.AddMessage("Loading the Dataset Title Dictionary. Please wait")
        datasets_dict = dataset_title_dict(project_gdb)

        datasets = []

        #datasets.extend(arcpy.ListFeatureClasses("AI_IDW_Sample_Locations"))
        datasets.extend(arcpy.ListFeatureClasses("*Sample_Locations"))
        datasets.extend(arcpy.ListFeatureClasses("DisMAP_Regions"))
        datasets.extend(arcpy.ListTables("Indicators"))
        datasets.extend(arcpy.ListTables("Species_Filter"))
        datasets.extend(arcpy.ListTables("DisMAP_Survey_Info"))
        datasets.extend(arcpy.ListTables("SpeciesPersistenceIndicatorPercentileBin"))
        datasets.extend(arcpy.ListTables("SpeciesPersistenceIndicatorTrend"))

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

        for dataset in sorted(datasets):

            feature_service       = datasets_dict[dataset]["Dataset Service"]
            feature_service_title = datasets_dict[dataset]["Dataset Service Title"]

            arcpy.AddMessage(f"Dataset: {dataset}")
            arcpy.AddMessage(f"\tFS:  {feature_service}")
            arcpy.AddMessage(f"\tFST: {feature_service_title}")

            feature_class_layer_file = rf"{project_folder}\Layers\{feature_service_title}.lyrx"

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

            in_md = md.Metadata(rf"{project_gdb}\{dataset}")
            current_map.metadata.copy(in_md)
            current_map.metadata.save()
            aprx.save()
            del in_md

            current_map.addLayer(layer_file)
            aprx.save()

            del layer_file

            arcpy.AddMessage("\t\tList of layers or tables in Layer File:")
            if current_map.listLayers(feature_service_title):
                lyr = current_map.listLayers(feature_service_title)[0]
            elif current_map.listTables(feature_service_title):
                lyr = current_map.listTables(feature_service_title)[0]
            else:
                arcpy.AddWarning("Something wrong")

            in_md = md.Metadata(rf"{project_gdb}\{dataset}")
            lyr.metadata.copy(in_md)
            lyr.metadata.save()
            aprx.save()
            del in_md

            arcpy.AddMessage("\tGet Web Layer Sharing Draft")
            # Get Web Layer Sharing Draft
            server_type = "HOSTING_SERVER"  # FEDERATED_SERVER
            #            m.getWebLayerSharingDraft (server_type, service_type, service_name, {layers_and_tables})
            # sddraft = m.getWebLayerSharingDraft(server_type, "FEATURE", service_name, [selected_layer, selected_table])
            # https://pro.arcgis.com/en/pro-app/latest/arcpy/sharing/featuresharingdraft-class.htm#GUID-8E27A3ED-A705-4ACF-8C7D-AA861327AD26
            sddraft = current_map.getWebLayerSharingDraft(server_type=server_type, service_type="FEATURE", service_name=feature_service, layers_and_tables=lyr)
            del server_type

            sddraft.allowExporting           = False
            sddraft.offline                  = False
            sddraft.offlineTarget            = None
            sddraft.credits                  = lyr.metadata.credits
            sddraft.description              = lyr.metadata.description
            sddraft.summary                  = lyr.metadata.summary
            sddraft.tags                     = lyr.metadata.tags
            sddraft.useLimitations           = lyr.metadata.accessConstraints
            sddraft.overwriteExistingService = True
            sddraft.portalFolder             = f"DisMAP {project_name}"

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

            arcpy.AddMessage("\tExport to SD Draft")
            # Create Service Definition Draft file
            sddraft.exportToSDDraft(rf"{project_folder}\Publish\{feature_service}.sddraft")

            del sddraft

            sd_draft = rf"{project_folder}\Publish\{feature_service}.sddraft"

            arcpy.AddMessage("\tModify SD Draft")
            # https://pro.arcgis.com/en/pro-app/latest/arcpy/sharing/featuresharingdraft-class.htm
            # https://www.esri.com/arcgis-blog/products/arcgis-pro/mapping/streamline-your-code-with-new-properties-in-arcpy-sharing
            import xml.dom.minidom as DOM

            docs = DOM.parse(sd_draft)
            key_list = docs.getElementsByTagName("Key")
            value_list = docs.getElementsByTagName("Value")

            for i in range(key_list.length):
                if key_list[i].firstChild.nodeValue == "maxRecordCount":
                    arcpy.AddMessage("\t\tUpdating maxRecordCount from 2000 to 10000")
                    value_list[i].firstChild.nodeValue = 2000
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

            FeatureSharingDraftReport = True
            if FeatureSharingDraftReport:
                arcpy.AddMessage(f"\tReport for {os.path.basename(sd_draft)} SD File")
                feature_sharing_draft_report(sd_draft)
            del FeatureSharingDraftReport

            arcpy.AddMessage(f"\tCreate/Stage {os.path.basename(sd_draft)} SD File")
            arcpy.server.StageService(in_service_definition_draft=sd_draft, out_service_definition=sd_draft.replace("sddraft", "sd"), staging_version=5)

            UploadServiceDefinition = True
            if UploadServiceDefinition:
                #if project != "April 1 2023":
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
                #else:
                #    arcpy.AddWarning(f"Project is {project}")
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
            arcpy.AddMessage("\nCurrent Maps\n")
            for current_map in current_maps:
                arcpy.AddMessage(f"\tProject Map: {current_map.name}")
                del current_map
        else:
            arcpy.AddWarning("No maps in Project")

        del current_maps

        # Declared Variables set in function for aprx

        # Save aprx one more time and then delete
        aprx.save()
        del aprx

        # Declared Variables set in function
        del project_folder, project_name, csv_data_folder

        # Imports
        del dataset_title_dict, md

        # Function Parameters
        del project_gdb

    except arcpy.ExecuteError:
        #Return Geoprocessing tool specific errors
        line, filename, err = trace()
        arcpy.AddError("Geoprocessing error on " + line + " of " + filename + " :")
        for msg in range(0, arcpy.GetMessageCount()):
            if arcpy.GetSeverity(msg) == 2:
                arcpy.AddReturnMessage(msg)
        return False
    except:  # noqa: E722
        #Gets non-tool errors
        line, filename, err = trace()
        arcpy.AddError("Python error on " + line + " of " + filename)
        arcpy.AddError(err)
        return False
    else:
        return True

##def update_metadata_from_published_md(project_gdb=""):
##    try:
##        # Import
##        import dismap_tools
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
##        project_gdb = rf"{project_folder}\{project}.gdb"
##
##
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
##        datasets = [row for row in arcpy.da.SearchCursor(os.path.join(project_gdb, "Datasets"), fields, where_clause = f"FeatureClassName IS NOT NULL AND DistributionProjectCode NOT IN ('GLMME', 'GFDL')")]
##        #datasets = [row for row in arcpy.da.SearchCursor(os.path.join(project_gdb, "Datasets"), fields, where_clause = f"FeatureClassName IN ('AI_IDW_Sample_Locations', 'DisMAP_Regions')")]
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
##            if arcpy.Exists(rf"{project_folder}\Publish\{feature_service_name}.xml"):
##                arcpy.AddMessage(f"\t###--->>> {feature_service_name}.xml Exists <<<---###")
##
##                from arcpy import metadata as md
##                in_md = md.Metadata(rf"{project_folder}\Publish\{feature_service_name}.xml")
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
##        # Declared Variables set in function
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
##        sys.exit()
##    except:
##        traceback.print_exc()
##        sys.exit()
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

def create_image_services(project_gdb=""):
    try:
        # Import

        # Set History and Metadata logs, set serverity and message level
        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(1) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        #aprx = arcpy.mp.ArcGISProject(base_project_file)  # noqa: F821
        #home_folder = aprx.homeFolder
        #project_gdb = rf"{project_folder}\{project}.gdb"  # noqa: F821

        # Set basic workkpace variables
        project_folder    = os.path.dirname(project_gdb)
        crfs_folder       = os.path.join(project_folder, "CRFs")
        scratch_folder    = os.path.join(project_folder, "Scratch")
        scratch_workspace = os.path.join(project_folder, "Scratch\\scratch.gdb")

        # Create Scratch Workspace for Project
        if not arcpy.Exists(os.path.join(scratch_folder, "scratch.gdb")):
            if not arcpy.Exists(scratch_folder):
                os.makedirs(scratch_folder)
            if not arcpy.Exists(os.path.join(scratch_folder, "scratch.gdb")):
                arcpy.management.CreateFileGDB(rf"{scratch_folder}", "scratch")

        # Set basic workkpace variables
        arcpy.env.workspace                = project_gdb
        arcpy.env.scratchWorkspace         = scratch_workspace
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        del scratch_folder, scratch_workspace

        arcpy.env.workspace = crfs_folder

        for crf in arcpy.ListRasters("*"):
            arcpy.AddMessage(crf)

        arcpy.env.workspace = project_gdb

##        LogIntoPortal = False
##        if LogIntoPortal:
##            try:
##                portal = "https://noaa.maps.arcgis.com/"
##                user = "John.F.Kennedy_noaa"
##
##                #portal = "https://maps.fisheries.noaa.gov/portal/home"
##                #portal = "https://maps.fisheries.noaa.gov"
##                #user   = "John.F.Kennedy_noaa"
##
##                # Sign in to portal
##                # arcpy.SignInToPortal("https://www.arcgis.com", "MyUserName", "MyPassword")
##                # For example: 'http://www.arcgis.com/'
##                arcpy.SignInToPortal(portal)
##
##                arcpy.AddMessage(f"###---> Signed into Portal: {arcpy.GetActivePortalURL()} <---###")
##                del portal, user
##            except:  # noqa: E722
##                arcpy.AddError("###---> Signed into Portal faild <---###")
##                sys.exit()
##        del LogIntoPortal

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

        con = os.path.join(os.path.expanduser('~'), "Documents\\ArcGIS\\Projects\\DisMAP\\ArcGIS-Analysis\\image on maps.fisheries.noaa.gov.ags")

        mosiac_name    = "SEUS_FAL_Mosaic"
        mosiac_path    = rf"{project_gdb}\{mosiac_name}"
        mosiac_sddraft = rf"{project_folder}\Publish\{mosiac_name}.sddraft"


        # Create service definition draft
        try:
            arcpy.AddMessage("Creating SD draft")
            #arcpy.CreateImageSDDraft(Md, Sddraft, Name, 'ARCGIS_SERVER', con, False, None, "Ortho Images","ortho images,image service")
            arcpy.CreateImageSDDraft(mosiac_path, mosiac_sddraft, mosiac_name, 'ARCGIS_SERVER', con, False, None, "Biomass Rasters", "biomass rasters,image service")
        except arcpy.ExecuteError:
            #Return Geoprocessing tool specific errors
            line, filename, err = trace()
            arcpy.AddError("Geoprocessing error on " + line + " of " + filename + " :")
            for msg in range(0, arcpy.GetMessageCount()):
                if arcpy.GetSeverity(msg) == 2:
                    arcpy.AddReturnMessage(msg)
            import traceback
            traceback.print_exc()
            return False
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
##            arcpy.AddError(arcpy.GetMessages(2))

        #del project_gdb

        # Declared Variables set in function for aprx
        #del home_folder
        # Save aprx one more time and then delete
        #aprx.save()
        #del aprx

        # Declared Variables set in function

        # Imports

        # Function Parameters
        del project_gdb

    except arcpy.ExecuteError:
        #Return Geoprocessing tool specific errors
        line, filename, err = trace()
        arcpy.AddError("Geoprocessing error on " + line + " of " + filename + " :")
        for msg in range(0, arcpy.GetMessageCount()):
            if arcpy.GetSeverity(msg) == 2:
                arcpy.AddReturnMessage(msg)
        return False
    except Exception:
        #Gets non-tool errors
        line, filename, err = trace()
        arcpy.AddError("Python error on " + line + " of " + filename)
        arcpy.AddError(err)
        return False
    else:
        return True

def create_maps(project_gdb=""):
    try:
        # Import
        from arcpy import metadata as md

        from dismap_tools import dataset_title_dict

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2)
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

##        # Map Cleanup
##        MapCleanup = False
##        if MapCleanup:
##            map_cleanup(base_project_file)
##        del MapCleanup

        base_project_folder = rf"{os.path.dirname(base_project_file)}"  # noqa: F821
        base_project_file   = rf"{base_project_folder}\DisMAP.aprx"
        project_folder      = rf"{base_project_folder}\{project}"  # noqa: F821
        project_gdb         = rf"{project_folder}\{project}.gdb"  # noqa: F821
        metadata_folder     = rf"{project_folder}\Export Metadata"
        scratch_folder      = rf"{project_folder}\Scratch"

        arcpy.env.workspace        = project_gdb
        arcpy.env.scratchWorkspace = os.path.join(scratch_folder, "scratch.gdb")

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
                        arcpy.AddMessage("\tRegion Indicators")

                    elif "LayerSpeciesYearImageName" in dataset_name:
                        arcpy.AddMessage("\tRegion Layer Species Year Image Name")

                    else:
                        arcpy.AddMessage("\tRegion Table")

                else:
                    arcpy.AddMessage(f"Dataset Name: {dataset_name}")
                    if "Indicators" in dataset_name:
                        arcpy.AddMessage("\tMain Indicators Table")

                    elif "LayerSpeciesYearImageName" in dataset_name:
                        arcpy.AddMessage("\tLayer Species Year Image Name")

                    elif "Datasets" in dataset_name:
                        arcpy.AddMessage("\tDataset Table")

                    elif "Species_Filter" in dataset_name:
                        arcpy.AddMessage("\tSpecies Filter Table")

                    else:
                        arcpy.AddMessage(f"\tDataset Name: {dataset_name}")

            elif data_type == "FeatureClass":
                #arcpy.AddMessage(f"\tData Type: {data_type}")

                if "IDW" in dataset_name:
                    arcpy.AddMessage(f"Dataset Name: {dataset_name}")
                    if dataset_name.endswith("Boundary"):
                        arcpy.AddMessage("\tBoundary")

                    elif dataset_name.endswith("Extent_Points"):
                        arcpy.AddMessage("\tExtent_Points")

                    elif dataset_name.endswith("Fishnet"):
                        arcpy.AddMessage("\tFishnet")

                    elif dataset_name.endswith("Lat_Long"):
                        arcpy.AddMessage("\tLat_Long")

                    elif dataset_name.endswith("Region"):
                        arcpy.AddMessage("\tRegion")

                    elif dataset_name.endswith("Sample_Locations"):
                        arcpy.AddMessage("\tSample_Locations")

                    else:
                        pass

                elif "DisMAP_Regions" == dataset_name:
                    arcpy.AddMessage(f"Dataset Name: {dataset_name}")
                    if dataset_name.endswith("Regions"):
                        arcpy.AddMessage("\tDisMAP Regions")

                else:
                    arcpy.AddMessage(f"Else Dataset Name: {dataset_name}")

            elif data_type == "RasterDataset":

                if "IDW" in dataset_name:
                    arcpy.AddMessage(f"Dataset Name: {dataset_name}")
                    if dataset_name.endswith("Bathymetry"):
                        arcpy.AddMessage("\tBathymetry")

                    elif dataset_name.endswith("Latitude"):
                        arcpy.AddMessage("\tLatitude")

                    elif dataset_name.endswith("Longitude"):
                        arcpy.AddMessage("\tLongitude")

                    elif dataset_name.endswith("Raster_Mask"):
                        arcpy.AddMessage("\tRaster_Mask")
                else:
                    pass

            elif data_type == "MosaicDataset":

                if "IDW" in dataset_name:
                    arcpy.AddMessage(f"Dataset Name: {dataset_name}")
                    if dataset_name.endswith("Mosaic"):
                        arcpy.AddMessage("\tMosaic")
                    else:
                        pass

                elif "CRF" in dataset_name:
                    arcpy.AddMessage(f"Dataset Name: {dataset_name}")
                    if dataset_name.endswith("CRF"):
                        arcpy.AddMessage("\tCRF")

                else:
                    pass
            else:
                pass

            del data_type

            del dataset_name, dataset_path
        del datasets

        # Declared Variables set in function for aprx
        del home_folder
        # Save aprx one more time and then delete
        aprx.save()
        del aprx

        # Declared Variables set in function
        del base_project_folder, metadata_folder
        del project_folder, scratch_folder
        del metadata_dictionary

        # Imports
        del dataset_title_dict, md

        # Function Parameters
        del project_gdb

    except arcpy.ExecuteError:
        #Return Geoprocessing tool specific errors
        line, filename, err = trace()
        arcpy.AddError("Geoprocessing error on " + line + " of " + filename + " :")
        for msg in range(0, arcpy.GetMessageCount()):
            if arcpy.GetSeverity(msg) == 2:
                arcpy.AddReturnMessage(msg)
        return False
    except:  # noqa: E722
        #Gets non-tool errors
        line, filename, err = trace()
        arcpy.AddError("Python error on " + line + " of " + filename)
        arcpy.AddError(err)
        return False
    else:
        return True

def script_tool(project_gdb=""):
    try:
        # Imports
        from time import gmtime, localtime, strftime, time
        # Set a start time so that we can see how log things take
        start_time = time()
        arcpy.AddMessage(f"{'-' * 80}")
        arcpy.AddMessage(f"Python Script:  {os.path.basename(__file__)}")
        arcpy.AddMessage(f"Location:       .. {'/'.join(__file__.split(os.sep)[-4:])}")
        arcpy.AddMessage(f"Python Version: {sys.version}")
        arcpy.AddMessage(f"Environment:    {os.path.basename(sys.exec_prefix)}")
        arcpy.AddMessage(f"Start Time:     {strftime('%a %b %d %I:%M %p', localtime(start_time))}")
        arcpy.AddMessage(f"{'-' * 80}\n")

        # Set varaibales
        project_folder = os.path.dirname(project_gdb)
        scratch_folder = rf"{project_folder}\Scratch"
        del project_folder

        # Create project scratch workspace, if missing
        if not arcpy.Exists(os.path.join(scratch_folder, "scratch.gdb")):
            if not arcpy.Exists(scratch_folder):
                os.makedirs(scratch_folder)
            if not arcpy.Exists(os.path.join(scratch_folder, "scratch.gdb")):
                arcpy.management.CreateFileGDB(rf"{scratch_folder}", "scratch")
        del scratch_folder

        # Set basic arcpy.env variables
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        try:

            CreateFeatureClassLayers = False
            if CreateFeatureClassLayers:
                create_feature_class_layers(project_gdb=project_gdb)
            del CreateFeatureClassLayers

            CreateFeaturClasseServices = False
            if CreateFeaturClasseServices:
                create_feature_class_services(project_gdb=project_gdb)
            del CreateFeaturClasseServices

            CreateImagesServices = True
            if CreateImagesServices:
                create_image_services(project_gdb=project_gdb)
            del CreateImagesServices

            # UpdateMetadataFromPublishedMd = False
            # if UpdateMetadataFromPublishedMd:
            #    update_metadata_from_published_md(project_gdb=project_gdb)
            # del UpdateMetadataFromPublishedMd

            CreateMaps = False
            if CreateMaps:
                create_maps(project_gdb=project_gdb)
            del CreateMaps

##            CreateBasicTemplateXMLFiles = False
##            if CreateBasicTemplateXMLFiles:
##                create_basic_template_xml_files(project_gdb=project_gdb)
##            del CreateBasicTemplateXMLFiles
##
##            ImportBasicTemplateXmlFiles = False
##            if ImportBasicTemplateXmlFiles:
##                import_basic_template_xml_files(project_gdb=project_gdb)
##            del ImportBasicTemplateXmlFiles

        except SystemExit:
            arcpy.AddError(arcpy.GetMessages(2))
            traceback.print_exc()
            sys.exit()

        # Variable created in function
        #
        # Function Parameters
        del project_gdb
        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        hours, rem = divmod(end_time-start_time, 3600)
        minutes, seconds = divmod(rem, 60)
        arcpy.AddMessage(f"\n{'-' * 80}")
        arcpy.AddMessage(f"Python script: {os.path.basename(__file__)}")
        arcpy.AddMessage(f"Start Time:    {strftime('%a %b %d %I:%M %p', localtime(start_time))}")
        arcpy.AddMessage(f"End Time:      {strftime('%a %b %d %I:%M %p', localtime(end_time))}")
        arcpy.AddMessage(f"Elapsed Time   {int(hours):0>2}:{int(minutes):0>2}:{seconds:05.2f} (H:M:S)")
        arcpy.AddMessage(f"{'-' * 80}")
        del hours, rem, minutes, seconds
        del elapse_time, end_time, start_time
        del gmtime, localtime, strftime, time

    except arcpy.ExecuteError:
        #Return Geoprocessing tool specific errors
        line, filename, err = trace()
        arcpy.AddError("Geoprocessing error on " + line + " of " + filename + " :")
        for msg in range(0, arcpy.GetMessageCount()):
            if arcpy.GetSeverity(msg) == 2:
                arcpy.AddReturnMessage(msg)
        return False
    except:  # noqa: E722
        #Gets non-tool errors
        line, filename, err = trace()
        arcpy.AddError("Python error on " + line + " of " + filename)
        arcpy.AddError(err)
        return False
    else:
        return True

if __name__ == '__main__':
    try:
        project_gdb = arcpy.GetParameterAsText(0)

        if not project_gdb:
            project_gdb = os.path.join(os.path.expanduser('~'), "Documents\\ArcGIS\\Projects\\DisMAP\\ArcGIS-Analysis-Python\\February 1 2026\\February 1 2026.gdb")
        else:
            pass

        script_tool(project_gdb)

        arcpy.SetParameterAsText(1, "Result")

        del project_gdb

    except arcpy.ExecuteError:
        #Return Geoprocessing tool specific errors
        line, filename, err = trace()
        arcpy.AddError("Geoprocessing error on " + line + " of " + filename + " :")
        for msg in range(0, arcpy.GetMessageCount()):
            if arcpy.GetSeverity(msg) == 2:
                arcpy.AddReturnMessage(msg)
    except:  # noqa: E722
        #Gets non-tool errors
        line, filename, err = trace()
        arcpy.AddError("Python error on " + line + " of " + filename)
        arcpy.AddError(err)
