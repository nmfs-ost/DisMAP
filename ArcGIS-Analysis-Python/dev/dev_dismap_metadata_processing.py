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

def line_info(msg):
    f = inspect.currentframe()
    i = inspect.getframeinfo(f.f_back)
    return f"Script: {os.path.basename(i.filename)}\n\tNear Line: {i.lineno}\n\tFunction: {i.function}\n\tMessage: {msg}"

def _add_basic_metadata(dataset_name, dataset_md, metadata_dictionary):
    try:
        if "_Sample_Locations" in dataset_name:
            if "WC_Sample_Locations" == dataset_name:
                dataset_name = "WC_ANN_IDW_Sample_Locations"
            elif "_IDW_Sample_Locations" not in dataset_name:
                dataset_name = dataset_name.replace("_Sample_Locations", "_IDW_Sample_Locations")
            else:
                pass
                dataset_name = dataset_name

        #if dataset_name.endswith(".crf"):
        #    dataset_name = dataset_name.replace(".crf", "_crf")

        if dataset_name in metadata_dictionary:
            try:
                #dataset_md.synchronize("ALWAYS")
                #dataset_md.save()
                #dataset_md.reload()
                dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                dataset_md.save()
            except:
                traceback.print_exc()
        else:
            print(f"###--->>> {dataset_name} <<<---### not in metadata dictionary")

        return dataset_md
    except Exception:
        traceback.print_exc()
    except:
        traceback.print_exc()
        raise Exception

def update_existing_contacts(project_gdb=""):
    try:
        # Imports
        from lxml import etree
        from io import StringIO
        import copy
        from arcpy import metadata as md

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2)
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        project_folder = os.path.dirname(project_gdb)
        crfs_folder    = rf"{project_folder}\CRFs"
        scratch_folder = rf"{project_folder}\Scratch"

        root_dict = {"Esri"       :  0, "dataIdInfo" :  1, "mdChar"      :  2,
                     "mdContact"  :  3, "mdDateSt"   :  4, "mdFileID"    :  5,
                     "mdLang"     :  6, "mdMaint"    :  7, "mdHrLv"      :  8,
                     "mdHrLvName" :  9, "refSysInfo" : 10, "spatRepInfo" : 11,
                     "spdoinfo"   : 12, "dqInfo"     : 13, "distInfo"    : 14,
                     "eainfo"     : 15, "contInfo"   : 16, "spref"       : 17,
                     "spatRepInfo" : 18, "dataSetFn" : 19, "Binary"      : 100,}

        RoleCd_dict = {"001" : "Resource Provider", "002" : "Custodian",
                       "003" : "Owner",             "004" : "User",
                       "005" : "Distributor",       "006" : "Originator",
                       "007" : "Point of Contact",  "008" : "Principal Investigator",
                       "009" : "Processor",         "010" : "Publisher",
                       "011" : "Author",            "012" : "Collaborator",
                       "013" : "Editor",            "014" : "Mediator",
                       "015" : "Rights Holder",}

        workspaces = [project_gdb, crfs_folder]

        contacts_xml = rf"{os.environ['USERPROFILE']}\Documents\ArcGIS\Descriptions\contacts.xml"
        parser = etree.XMLParser(encoding='UTF-8', remove_blank_text=True)
        contacts_xml_tree = etree.parse(contacts_xml, parser=parser) # To parse from a string, use the fromstring() function instead.
        del parser
        del contacts_xml
        contacts_xml_root = contacts_xml_tree.getroot()
        #etree.indent(contacts_xml_root, space="  ")
        #print(etree.tostring(contacts_xml_root, encoding="utf-8",  method='xml', xml_declaration=True, pretty_print=True).decode())

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
                #print(dataset_path)
                dataset_name = os.path.basename(dataset_path)

                #print(f"Dataset Name:     {dataset_name}")
                #print(f"\tDataset Location: {os.path.basename(os.path.dirname(dataset_path))}")

                dataset_md = md.Metadata(dataset_path)
                dataset_md_xml = dataset_md.xml
                del dataset_md

                # Parse the XML
                parser = etree.XMLParser(encoding='UTF-8', remove_blank_text=True)
                tree = etree.parse(StringIO(dataset_md_xml), parser=parser)
                root = tree.getroot()
                del parser, dataset_md_xml

                # print(etree.tostring(tree, encoding="utf-8",  method='xml', xml_declaration=True, pretty_print=True).decode())
                # etree.indent(tree, space='   ')
                # tree.write(xml_file, encoding="utf-8",  method='xml', xml_declaration=True, pretty_print=True)

                print(f"Dataset Name: {dataset_name}")

                contact_parents = root.xpath(f".//eMailAdd/text()/ancestor::*//rpIndName/text()/ancestor::*//rpIndName/..")
                #contact_parents = copy.deepcopy(root.xpath(f".//eMailAdd/text()/ancestor::*//rpIndName/text()/ancestor::*//rpIndName/.."))
                #contact_parents = root.xpath(f".//eMailAdd/text()/ancestor::rpCntInfo/..")

                if len(contact_parents) > 0:
                    #count = 0
                    for contact_parent in contact_parents:
                        #count+=1
                        old_contact_parent = contact_parent.tag
                        print(f"\tContact Parent: {old_contact_parent}")
                        #print(etree.tostring(contact_parent, encoding="utf-8",  method='xml', xml_declaration=True, pretty_print=True).decode())

                        if isinstance(contact_parent.find(f"./rpCntInfo"), type(None)):
                            _xml = etree.XML('<rpCntInfo><cntAddress addressType="both"><delPoint></delPoint><city></city><adminArea></adminArea> \
                                              <postCode></postCode><eMailAdd></eMailAdd><country></country></cntAddress><cntPhone><voiceNum tddtty=""></voiceNum> \
                                              <faxNum></faxNum></cntPhone><cntHours></cntHours><cntOnlineRes><linkage></linkage><protocol>REST Service</protocol> \
                                              <orName></orName><orDesc></orDesc><orFunct><OnFunctCd value="002"></OnFunctCd></orFunct></cntOnlineRes></rpCntInfo>')
                            # Append element
                            contact_parent.append(_xml)
                            del _xml

                        if not isinstance(contact_parent.find(f".//eMailAdd"), type(None)):
                            email_address = contact_parent.find(f".//eMailAdd")
                            #print(f"\t\tEmail Address: {email_address}")
                            if not email_address.text:
                                _user_name = contact_parent.find(f"./rpIndName").text
                                _email_address = _user_name.lower().replace(" ", ".") + "@noaa.gov"
                                email_address.text = _email_address
                                del _email_address, _user_name
                            else:
                                pass
                        else:
                            pass
                            _rpCntInfo = contact_parent.find(f".//rpCntInfo")
                            _cntAddress = _rpCntInfo.find(f".//cntAddress")
                            _user_name = contact_parent.find(f"./rpIndName").text
                            #print(f"\t\tUser Name:     {_user_name}")
                            _email_address = _user_name.lower().replace(" ", ".") + "@noaa.gov"
                            _xml = etree.XML(f'<eMailAdd>{_email_address}</eMailAdd>')
                            # Append element
                            _cntAddress.append(_xml)
                            del _xml, _user_name, _email_address, _cntAddress, _rpCntInfo

                        if old_contact_parent == "citRespParty":
                            if not isinstance(contact_parent.find(f"./role"), type(None)):
                                user_role = contact_parent.find(f".//RoleCd")
                                user_role.set("value", "002")
                            else:
                                _xml = etree.XML('<role><RoleCd value="002"/></role>')
                                # Append element
                                contact_parent.append(_xml)
                                del _xml

                        if old_contact_parent == "idPoC":
                            if not isinstance(contact_parent.find(f"./role"), type(None)):
                                user_role = contact_parent.find(f".//RoleCd")
                                user_role.set("value", "007")
                            else:
                                _xml = etree.XML('<role><RoleCd value="007"/></role>')
                                # Append element
                                contact_parent.append(_xml)
                                del _xml

                        if old_contact_parent == "distorCont":
                            if not isinstance(contact_parent.find(f"./role"), type(None)):
                                user_role = contact_parent.find(f".//RoleCd")
                                user_role.set("value", "005")
                            else:
                                _xml = etree.XML('<role><RoleCd value="005"/></role>')
                                # Append element
                                contact_parent.append(_xml)
                                del _xml

                        if old_contact_parent == "mdContact":
                            if not isinstance(contact_parent.find(f"./role"), type(None)):
                                user_role = contact_parent.find(f".//RoleCd")
                                user_role.set("value", "011")
                            else:
                                _xml = etree.XML('<role><RoleCd value="011"/></role>')
                                # Append element
                                contact_parent.append(_xml)
                                del _xml

                        if old_contact_parent == "stepProc":
                            if not isinstance(contact_parent.find(f"./role"), type(None)):
                                user_role = contact_parent.find(f".//RoleCd")
                                user_role.set("value", "009")
                            else:
                                _xml = etree.XML('<role><RoleCd value="009"/></role>')
                                # Append element
                                contact_parent.append(_xml)
                                del _xml

                        if not isinstance(contact_parent.find(f"./rpIndName"), type(None)):
                            user_name = contact_parent.find(f"./rpIndName").text
                            print(f"\t\tUser Name:     {user_name}")
                        else:
                            user_name = ""

                        if not isinstance(contact_parent.find(f".//eMailAdd"), type(None)):
                            email_address = contact_parent.find(f".//eMailAdd").text
                            print(f"\t\tEmail Address: {email_address}")
                        else:
                            email_address = ""
                        if not isinstance(contact_parent.find(f".//RoleCd"), type(None)):
                            user_role = contact_parent.find(f".//RoleCd")
                            print(f"\t\tRole:          {user_role.attrib}")
                        else:
                            user_role = ""

                        contact_root = root.xpath(f".//eMailAdd[text()='{email_address}']/ancestor::{old_contact_parent}/rpIndName[text()='{user_name}']/..")
                        #contact_root = copy.deepcopy(root.xpath(f".//eMailAdd[text()='{email_address}']/ancestor::{old_contact_parent}/rpIndName[text()='{user_name}']/.."))
                        #print(etree.tostring(contact_root[0], encoding="utf-8",  method='xml', xml_declaration=True, pretty_print=True).decode())
                        #print(etree.tostring(contact_root[0], encoding="utf-8",  method='xml', xml_declaration=True, pretty_print=True).decode())

                        new_contact_root = contacts_xml_root.xpath(f".//eMailAdd[text()='{email_address}']/ancestor::contact/rpIndName[text()='{user_name}']/ancestor::contact/editorSave[text()='True']/..")

                        if len(new_contact_root) == 1:
                            new_contact = copy.deepcopy(new_contact_root[0])
                            new_contact.tag = old_contact_parent
                            #new_contact.append(contact_root[0].find(f".//role"))
                            #print(etree.tostring(new_contact, encoding="utf-8",  method='xml', pretty_print=True).decode())

                            contact_root[0].getparent().replace(contact_root[0], new_contact)
                            #print(etree.tostring(contact_root[0], encoding="utf-8",  method='xml', xml_declaration=True, pretty_print=True).decode())

                            del new_contact

                        del new_contact_root, contact_root
                        del user_role, email_address, user_name
                        del old_contact_parent, contact_parent

                dataset_md = md.Metadata(dataset_path)
                dataset_md.xml = etree.tostring(tree, encoding="utf-8",  method='xml', xml_declaration=True, pretty_print=True).decode()
                dataset_md.save()
                dataset_md.synchronize("ALWAYS")
                del dataset_md

                del contact_parents
                del dataset_name, dataset_path
                del root, tree
            del datasets
            del workspace

        # Variables set in function
        del contacts_xml_root, contacts_xml_tree
        del RoleCd_dict, root_dict
        del project_folder, crfs_folder, scratch_folder
        del workspaces

        # Imports
        del md, etree, StringIO, copy

        # Function Parameters
        del project_gdb

    except Exception:
        traceback.print_exc()
    except:
        traceback.print_exc()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function: ##--> '{', '.join(rk)}' <--##"); del rk
        return True
    finally:
        pass

def create_basic_template_xml_files(base_project_file="", project_name=""):
    try:
        # Import
        from arcpy import metadata as md

        import dismap
        importlib.reload(dismap)
        from dismap import dataset_title_dict, parse_xml_file_format_and_save

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2)
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        base_project_folder = rf"{os.path.dirname(base_project_file)}"
        base_project_file   = rf"{base_project_folder}\DisMAP.aprx"
        project_folder      = rf"{base_project_folder}\{project_name}"
        project_gdb         = rf"{project_folder}\{project_name}.gdb"
        metadata_folder     = rf"{project_folder}\Template Metadata"
        crfs_folder         = rf"{project_folder}\CRFs"
        scratch_folder      = rf"{project_folder}\Scratch"

        if not os.path.isdir(metadata_folder): os.mkdir(metadata_folder)

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
                #print(dataset_path)
                dataset_name = os.path.basename(dataset_path)

                print(f"Dataset Name: {dataset_name}")

                if "Datasets" == dataset_name:

                    print(f"\tDataset Table")

                    dataset_md = md.Metadata(dataset_path)

                    _add_basic_metadata(dataset_name, dataset_md, metadata_dictionary)

                    dataset_md.synchronize("ALWAYS")
                    dataset_md.save()

                    datasets_table_template = rf"{metadata_folder}\datasets_table_template.xml"
                    dataset_md.saveAsXML(datasets_table_template, "REMOVE_ALL_SENSITIVE_INFO")
                    parse_xml_file_format_and_save(datasets_table_template)
                    del datasets_table_template

##                    target_file_path = rf"{project_folder}\InPort Metadata\datasets_table_template.xml"
##                    custom_xslt_path = rf"{project_folder}\InPort Metadata\ArcGIS2InPort.xsl"
##                    dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
##                    del target_file_path, custom_xslt_path

                    del dataset_md

                elif "Species_Filter" == dataset_name:

                    print(f"\tSpecies Filter Table")

                    dataset_md = md.Metadata(dataset_path)

                    _add_basic_metadata(dataset_name, dataset_md, metadata_dictionary)

                    dataset_md.synchronize("ALWAYS")
                    dataset_md.save()

                    species_filter_table_template = rf"{metadata_folder}\species_filter_table_template.xml"
                    dataset_md.saveAsXML(species_filter_table_template, "REMOVE_ALL_SENSITIVE_INFO")
                    parse_xml_file_format_and_save(species_filter_table_template)
                    del species_filter_table_template

##                    target_file_path = rf"{project_folder}\InPort Metadata\species_filter_table_template.xml"
##                    custom_xslt_path = rf"{project_folder}\InPort Metadata\ArcGIS2InPort.xsl"
##                    dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
##                    del target_file_path, custom_xslt_path

                    del dataset_md

                elif "Indicators" in dataset_name:

                    if dataset_name == "Indicators":
                        dataset_name = f"{dataset_name}_Table"
                    else:
                        pass

                    print(f"\t{dataset_name}")

                    dataset_md = md.Metadata(dataset_path)

                    _add_basic_metadata(dataset_name, dataset_md, metadata_dictionary)

                    dataset_md.synchronize("ALWAYS")
                    dataset_md.save()

                    indicators_template = rf"{metadata_folder}\indicators_template.xml"
                    dataset_md.saveAsXML(indicators_template, "REMOVE_ALL_SENSITIVE_INFO")
                    parse_xml_file_format_and_save(indicators_template)
                    del indicators_template

##                    target_file_path = rf"{project_folder}\InPort Metadata\indicators_template.xml"
##                    custom_xslt_path = rf"{project_folder}\InPort Metadata\ArcGIS2InPort.xsl"
##                    dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
##                    del target_file_path, custom_xslt_path

                    del dataset_md

                elif "LayerSpeciesYearImageName" in dataset_name:

                    print(f"\t{dataset_name}")

                    dataset_md = md.Metadata(dataset_path)

                    _add_basic_metadata(dataset_name, dataset_md, metadata_dictionary)

                    dataset_md.synchronize("ALWAYS")
                    dataset_md.save()

                    layer_species_year_image_name_template = rf"{metadata_folder}\layer_species_year_image_name_template.xml"
                    dataset_md.saveAsXML(layer_species_year_image_name_template, "REMOVE_ALL_SENSITIVE_INFO")
                    parse_xml_file_format_and_save(layer_species_year_image_name_template)
                    del layer_species_year_image_name_template

                    del dataset_md

                elif "DisMAP_Survey_Info" in dataset_name:

                    print(f"\t{dataset_name}")

                    dataset_md = md.Metadata(dataset_path)

                    _add_basic_metadata(dataset_name, dataset_md, metadata_dictionary)

                    dataset_md.synchronize("ALWAYS")
                    dataset_md.save()

                    dismap_survey_info_template = rf"{metadata_folder}\dismap_survey_info_template.xml"
                    dataset_md.saveAsXML(dismap_survey_info_template, "REMOVE_ALL_SENSITIVE_INFO")
                    parse_xml_file_format_and_save(dismap_survey_info_template)
                    del dismap_survey_info_template

##                    target_file_path = rf"{project_folder}\InPort Metadata\dismap_survey_info_template.xml"
##                    custom_xslt_path = rf"{project_folder}\InPort Metadata\ArcGIS2InPort.xsl"
##                    dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
##                    del target_file_path, custom_xslt_path

                    del dataset_md

                elif dataset_name.endswith("Boundary"):

                    print(f"\t{dataset_name}")

                    dataset_md = md.Metadata(dataset_path)

                    _add_basic_metadata(dataset_name, dataset_md, metadata_dictionary)

                    dataset_md.synchronize("ALWAYS")
                    dataset_md.save()

                    boundary_template = rf"{metadata_folder}\boundary_template.xml"
                    dataset_md.saveAsXML(boundary_template, "REMOVE_ALL_SENSITIVE_INFO")
                    parse_xml_file_format_and_save(boundary_template)
                    del boundary_template

                    del dataset_md

                elif dataset_name.endswith("Boundary_Line"):

                    print(f"\t{dataset_name}")

                    dataset_md = md.Metadata(dataset_path)

                    _add_basic_metadata(dataset_name, dataset_md, metadata_dictionary)

                    dataset_md.synchronize("ALWAYS")
                    dataset_md.save()

                    boundary_line_template = rf"{metadata_folder}\boundary_line_template.xml"
                    dataset_md.saveAsXML(boundary_line_template, "REMOVE_ALL_SENSITIVE_INFO")
                    parse_xml_file_format_and_save(boundary_line_template)
                    del boundary_line_template

                    del dataset_md

                elif dataset_name.endswith("Extent_Points"):

                    print(f"\t{dataset_name}")

                    dataset_md = md.Metadata(dataset_path)

                    _add_basic_metadata(dataset_name, dataset_md, metadata_dictionary)

                    dataset_md.synchronize("ALWAYS")
                    dataset_md.save()

                    extent_points_template = rf"{metadata_folder}\extent_points_template.xml"
                    dataset_md.saveAsXML(extent_points_template, "REMOVE_ALL_SENSITIVE_INFO")
                    parse_xml_file_format_and_save(extent_points_template)
                    del extent_points_template

                    del dataset_md

                elif dataset_name.endswith("Fishnet"):

                    print(f"\t{dataset_name}")

                    dataset_md = md.Metadata(dataset_path)

                    _add_basic_metadata(dataset_name, dataset_md, metadata_dictionary)

                    dataset_md.synchronize("ALWAYS")
                    dataset_md.save()

                    fishnet_template = rf"{metadata_folder}\fishnet_template.xml"
                    dataset_md.saveAsXML(fishnet_template, "REMOVE_ALL_SENSITIVE_INFO")
                    parse_xml_file_format_and_save(fishnet_template)
                    del fishnet_template

                    del dataset_md

                elif dataset_name.endswith("Lat_Long"):

                    print(f"\t{dataset_name}")

                    dataset_md = md.Metadata(dataset_path)

                    _add_basic_metadata(dataset_name, dataset_md, metadata_dictionary)

                    dataset_md.synchronize("ALWAYS")
                    dataset_md.save()
                    lat_long_template = rf"{metadata_folder}\lat_long_template.xml"
                    dataset_md.saveAsXML(lat_long_template, "REMOVE_ALL_SENSITIVE_INFO")
                    parse_xml_file_format_and_save(lat_long_template)
                    del lat_long_template

                    del dataset_md

                elif dataset_name.endswith("Region"):

                    print(f"\t{dataset_name}")

                    dataset_md = md.Metadata(dataset_path)

                    _add_basic_metadata(dataset_name, dataset_md, metadata_dictionary)

                    dataset_md.synchronize("ALWAYS")
                    dataset_md.save()

                    region_template = rf"{metadata_folder}\region_template.xml"
                    dataset_md.saveAsXML(region_template, "REMOVE_ALL_SENSITIVE_INFO")
                    parse_xml_file_format_and_save(region_template)
                    del region_template

                    del dataset_md

                elif dataset_name.endswith("Sample_Locations"):

                    print(f"\t{dataset_name}")

                    dataset_md = md.Metadata(dataset_path)

                    _add_basic_metadata(dataset_name, dataset_md, metadata_dictionary)

                    dataset_md.synchronize("ALWAYS")
                    dataset_md.save()

                    sample_locations_template = rf"{metadata_folder}\sample_locations_template.xml"
                    dataset_md.saveAsXML(sample_locations_template, "REMOVE_ALL_SENSITIVE_INFO")
                    parse_xml_file_format_and_save(sample_locations_template)
                    del sample_locations_template

##                    target_file_path = rf"{project_folder}\InPort Metadata\sample_locations_template.xml"
##                    custom_xslt_path = rf"{project_folder}\InPort Metadata\ArcGIS2InPort.xsl"
##                    try:
##                        dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
##                    except RuntimeError:
##                        pass
##                    del target_file_path, custom_xslt_path

                    del dataset_md

                elif dataset_name.endswith("GRID_Points"):

                    print(f"\t{dataset_name}")

                    dataset_md = md.Metadata(dataset_path)

                    _add_basic_metadata(dataset_name, dataset_md, metadata_dictionary)

                    dataset_md.synchronize("ALWAYS")
                    dataset_md.save()

                    grid_points_template = rf"{metadata_folder}\grid_points_template.xml"
                    dataset_md.saveAsXML(grid_points_template, "REMOVE_ALL_SENSITIVE_INFO")
                    parse_xml_file_format_and_save(grid_points_template)
                    del grid_points_template

                    del dataset_md

                elif dataset_name.endswith("Points"):

                    print(f"\t{dataset_name}")

                    dataset_md = md.Metadata(dataset_path)

                    _add_basic_metadata(dataset_name, dataset_md, metadata_dictionary)

                    dataset_md.synchronize("ALWAYS")
                    dataset_md.save()

                    points_template = rf"{metadata_folder}\points_template.xml"
                    dataset_md.saveAsXML(points_template, "REMOVE_ALL_SENSITIVE_INFO")
                    parse_xml_file_format_and_save(points_template)
                    del points_template

                    del dataset_md

                elif dataset_name.endswith("Survey_Area"):

                    print(f"\t{dataset_name}")

                    dataset_md = md.Metadata(dataset_path)

                    _add_basic_metadata(dataset_name, dataset_md, metadata_dictionary)

                    dataset_md.synchronize("ALWAYS")
                    dataset_md.save()

                    survey_area_template = rf"{metadata_folder}\survey_area_template.xml"
                    dataset_md.saveAsXML(survey_area_template, "REMOVE_ALL_SENSITIVE_INFO")
                    parse_xml_file_format_and_save(survey_area_template)
                    del survey_area_template

                    del dataset_md

                elif "DisMAP_Regions" == dataset_name:

                    print(f"\t{dataset_name}")

                    dataset_md = md.Metadata(dataset_path)

                    _add_basic_metadata(dataset_name, dataset_md, metadata_dictionary)

                    dataset_md.synchronize("ALWAYS")
                    dataset_md.save()

                    dismap_regions_template = rf"{metadata_folder}\dismap_regions_template.xml"
                    dataset_md.saveAsXML(dismap_regions_template, "REMOVE_ALL_SENSITIVE_INFO")
                    parse_xml_file_format_and_save(dismap_regions_template)
                    del dismap_regions_template

##                    target_file_path = rf"{project_folder}\InPort Metadata\dismap_regions_template.xml"
##                    custom_xslt_path = rf"{project_folder}\InPort Metadata\ArcGIS2InPort.xsl"
##                    dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
##                    del target_file_path, custom_xslt_path

                    del dataset_md

                elif dataset_name.endswith("Bathymetry"):

                    print(f"\t{dataset_name}")

                    dataset_md = md.Metadata(dataset_path)

                    _add_basic_metadata(dataset_name, dataset_md, metadata_dictionary)

                    dataset_md.synchronize("ALWAYS")
                    dataset_md.save()

                    bathymetry_template = rf"{metadata_folder}\bathymetry_template.xml"
                    dataset_md.saveAsXML(bathymetry_template, "REMOVE_ALL_SENSITIVE_INFO")
                    parse_xml_file_format_and_save(bathymetry_template)
                    del bathymetry_template

                    del dataset_md

                elif dataset_name.endswith("Latitude"):

                    print(f"\t{dataset_name}")

                    dataset_md = md.Metadata(dataset_path)

                    _add_basic_metadata(dataset_name, dataset_md, metadata_dictionary)

                    dataset_md.synchronize("ALWAYS")
                    dataset_md.save()

                    latitude_template = rf"{metadata_folder}\latitude_template.xml"
                    dataset_md.saveAsXML(latitude_template, "REMOVE_ALL_SENSITIVE_INFO")
                    parse_xml_file_format_and_save(latitude_template)
                    del latitude_template

                    del dataset_md

                elif dataset_name.endswith("Longitude"):

                    print(f"\t{dataset_name}")

                    dataset_md = md.Metadata(dataset_path)

                    _add_basic_metadata(dataset_name, dataset_md, metadata_dictionary)

                    dataset_md.synchronize("ALWAYS")
                    dataset_md.save()

                    longitude_template = rf"{metadata_folder}\longitude_template.xml"
                    dataset_md.saveAsXML(longitude_template, "REMOVE_ALL_SENSITIVE_INFO")
                    parse_xml_file_format_and_save(longitude_template)
                    del longitude_template

                    del dataset_md

                elif dataset_name.endswith("Raster_Mask"):

                    print(f"\t{dataset_name}")

                    dataset_md = md.Metadata(dataset_path)

                    _add_basic_metadata(dataset_name, dataset_md, metadata_dictionary)

                    dataset_md.synchronize("ALWAYS")
                    dataset_md.save()

                    raster_mask_template = rf"{metadata_folder}\raster_mask_template.xml"
                    dataset_md.saveAsXML(raster_mask_template, "REMOVE_ALL_SENSITIVE_INFO")
                    parse_xml_file_format_and_save(raster_mask_template)
                    del raster_mask_template

                    del dataset_md

                elif dataset_name.endswith("Mosaic"):

                    print(f"\t{dataset_name}")

                    dataset_md = md.Metadata(dataset_path)

                    _add_basic_metadata(dataset_name, dataset_md, metadata_dictionary)

                    dataset_md.synchronize("ALWAYS")
                    dataset_md.save()

                    mosaic_template = rf"{metadata_folder}\mosaic_template.xml"
                    dataset_md.saveAsXML(mosaic_template, "REMOVE_ALL_SENSITIVE_INFO")
                    parse_xml_file_format_and_save(mosaic_template)
                    del mosaic_template

##                    target_file_path = rf"{project_folder}\InPort Metadata\mosaic_template.xml"
##                    custom_xslt_path = rf"{project_folder}\InPort Metadata\ArcGIS2InPort.xsl"
##                    dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
##                    del target_file_path, custom_xslt_path

                    del dataset_md

                elif dataset_name.endswith(".crf"):

                    print(f"\t{dataset_name}")

                    dataset_md = md.Metadata(dataset_path)

                    _add_basic_metadata(dataset_name, dataset_md, metadata_dictionary)

                    dataset_md.synchronize("ALWAYS")
                    dataset_md.save()

                    crf_template = rf"{metadata_folder}\crf_template.xml"
                    dataset_md.saveAsXML(crf_template, "REMOVE_ALL_SENSITIVE_INFO")
                    parse_xml_file_format_and_save(crf_template)
                    del crf_template

##                    target_file_path = rf"{project_folder}\InPort Metadata\crf_template.xml"
##                    custom_xslt_path = rf"{project_folder}\InPort Metadata\ArcGIS2InPort.xsl"
##                    dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
##                    del target_file_path, custom_xslt_path

                    del dataset_md

                else:
                    print(f"\tRegion Table")

                    if dataset_name.endswith("IDW"):

                        print(f"\t{dataset_name}")

                        dataset_md = md.Metadata(dataset_path)

                        _add_basic_metadata(dataset_name, dataset_md, metadata_dictionary)

                        dataset_md.synchronize("ALWAYS")
                        dataset_md.save()

                        idw_region_table_template = rf"{metadata_folder}\idw_region_table_template.xml"
                        dataset_md.saveAsXML(idw_region_table_template, "REMOVE_ALL_SENSITIVE_INFO")
                        parse_xml_file_format_and_save(idw_region_table_template)
                        del idw_region_table_template

                        del dataset_md

                    elif dataset_name.endswith("GLMME"):

                        dataset_md = md.Metadata(dataset_path)

                        _add_basic_metadata(dataset_name, dataset_md, metadata_dictionary)

                        dataset_md.synchronize("ALWAYS")
                        dataset_md.save()

                        glmme_region_table_template = rf"{metadata_folder}\glmme_region_table_template.xml"
                        dataset_md.saveAsXML(glmme_region_table_template, "REMOVE_ALL_SENSITIVE_INFO")
                        parse_xml_file_format_and_save(glmme_region_table_template)
                        del glmme_region_table_template

                        del dataset_md

                    else:
                        print(f"\t\t ###--->>> {dataset_name} <<<---###")

                del dataset_name, dataset_path

            del datasets
            del workspace

        # Variables set in function
        del project_gdb, base_project_folder, metadata_folder
        del project_folder, scratch_folder, crfs_folder
        del metadata_dictionary, workspaces

        # Imports
        del dismap, dataset_title_dict, parse_xml_file_format_and_save
        del md

        # Function Parameters
        del base_project_file, project_name

    except Exception:
        traceback.print_exc()
    except:
        traceback.print_exc()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function: ##--> '{', '.join(rk)}' <--##"); del rk
        return True
    finally:
        pass

def import_basic_template_xml_files(base_project_file="", project_name=""):
    try:
        # Import
        from arcpy import metadata as md

        import dismap
        importlib.reload(dismap)
        from dismap import dataset_title_dict, parse_xml_file_format_and_save, unique_years

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2)
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        base_project_folder = rf"{os.path.dirname(base_project_file)}"
        project_folder      = rf"{base_project_folder}\{project_name}"
        project_gdb         = rf"{project_folder}\{project_name}.gdb"
        current_md_folder   = rf"{project_folder}\Current Metadata"
        inport_md_folder    = rf"{project_folder}\InPort Metadata"
        crfs_folder         = rf"{project_folder}\CRFs"
        scratch_folder      = rf"{project_folder}\Scratch"

        #print("Creating the Metadata Dictionary. Please wait!!")
        metadata_dictionary = dataset_title_dict(project_gdb)
        #print("Creating the Metadata Dictionary. Completed")

        workspaces = [project_gdb, crfs_folder]
        #workspaces = [crfs_folder]

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
                #print(dataset_path)
                dataset_name = os.path.basename(dataset_path)

                print(f"Dataset Name: {dataset_name}")

                if "Datasets" == dataset_name:

                    print(f"\tDataset Table")

                    datasets_table_template = rf"{current_md_folder}\Table\datasets_table_template.xml"
                    template_md = md.Metadata(datasets_table_template)

                    dataset_md = md.Metadata(dataset_path)
                    #empty_md   = md.Metadata()
                    #dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    #dataset_md.importMetadata(datasets_table_template)
                    dataset_md.save()
                    #dataset_md.synchronize("SELECTIVE")

                    #del empty_md, template_md, datasets_table_template

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    out_xml = rf"{current_md_folder}\Table\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

##                    target_file_path = rf"{inport_md_folder}\Table\{dataset_name}.xml"
##                    custom_xslt_path = rf"{inport_md_folder}\ArcGIS2InPort.xsl"
##                    dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
##                    parse_xml_file_format_and_save(target_file_path)
##                    del target_file_path, custom_xslt_path

                    del dataset_md

                elif "Species_Filter" == dataset_name:

                    print(f"\tSpecies Filter Table")

                    species_filter_table_template = rf"{current_md_folder}\Table\species_filter_table_template.xml"
                    template_md = md.Metadata(species_filter_table_template)

                    dataset_md = md.Metadata(dataset_path)
                    #empty_md   = md.Metadata()
                    #dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    #del empty_md, template_md, species_filter_table_template

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    out_xml = rf"{current_md_folder}\Table\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    target_file_path = rf"{inport_md_folder}\Table\{dataset_name}.xml"
                    custom_xslt_path = rf"{inport_md_folder}\ArcGIS2InPort.xsl"

                    dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
                    parse_xml_file_format_and_save(target_file_path)

                    del target_file_path, custom_xslt_path

                    del dataset_md

                elif "Indicators" in dataset_name:

                    print(f"\tIndicators")

                    if dataset_name == "Indicators":
                        indicators_template = rf"{current_md_folder}\Table\indicators_template.xml"
                    else:
                        indicators_template = rf"{current_md_folder}\Table\region_indicators_template.xml"

                    template_md = md.Metadata(indicators_template)

                    dataset_md = md.Metadata(dataset_path)
                    #empty_md   = md.Metadata()
                    #dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    #del empty_md, template_md, indicators_template

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

                    out_xml = rf"{current_md_folder}\Table\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    target_file_path = rf"{inport_md_folder}\Table\{dataset_name}.xml"
                    custom_xslt_path = rf"{inport_md_folder}\ArcGIS2InPort.xsl"

                    dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
                    parse_xml_file_format_and_save(target_file_path)

                    del target_file_path, custom_xslt_path

                    del dataset_md, _tags

                elif "LayerSpeciesYearImageName" in dataset_name:

                    print(f"\tLayer Species Year Image Name")

                    layer_species_year_image_name_template = rf"{current_md_folder}\Table\layer_species_year_image_name_template.xml"
                    template_md = md.Metadata(layer_species_year_image_name_template)

                    dataset_md = md.Metadata(dataset_path)
                    #empty_md   = md.Metadata()
                    #dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    #del empty_md, template_md, layer_species_year_image_name_template

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

                    out_xml = rf"{current_md_folder}\Table\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    target_file_path = rf"{inport_md_folder}\Table\{dataset_name}.xml"
                    custom_xslt_path = rf"{inport_md_folder}\ArcGIS2InPort.xsl"

                    dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
                    parse_xml_file_format_and_save(target_file_path)

                    del target_file_path, custom_xslt_path

                    del dataset_md, _tags

                elif dataset_name.endswith("Boundary"):

                    print(f"\tBoundary")

                    boundary_template = rf"{current_md_folder}\Boundary\boundary_template.xml"
                    template_md = md.Metadata(boundary_template)

                    dataset_md = md.Metadata(dataset_path)
                    #empty_md   = md.Metadata()
                    #dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    #del empty_md, template_md, boundary_template

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    out_xml = rf"{current_md_folder}\Boundary\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    target_file_path = rf"{inport_md_folder}\Boundary\{dataset_name}.xml"
                    custom_xslt_path = rf"{inport_md_folder}\ArcGIS2InPort.xsl"

                    dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
                    parse_xml_file_format_and_save(target_file_path)

                    del target_file_path, custom_xslt_path

                    del dataset_md

                elif dataset_name.endswith("Extent_Points"):

                    print(f"\tExtent_Points")

                    extent_points_template = rf"{current_md_folder}\Extent_Points\extent_points_template.xml"
                    template_md = md.Metadata(extent_points_template)

                    dataset_md = md.Metadata(dataset_path)
                    #empty_md   = md.Metadata()
                    #dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    #del empty_md, template_md, extent_points_template

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    out_xml = rf"{current_md_folder}\Extent_Points\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    target_file_path = rf"{inport_md_folder}\Extent_Points\{dataset_name}.xml"
                    custom_xslt_path = rf"{inport_md_folder}\ArcGIS2InPort.xsl"

                    dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
                    parse_xml_file_format_and_save(target_file_path)

                    del target_file_path, custom_xslt_path

                    del dataset_md

                elif dataset_name.endswith("Fishnet"):

                    print(f"\tFishnet")

                    fishnet_template = rf"{current_md_folder}\Fishnet\fishnet_template.xml"
                    template_md = md.Metadata(fishnet_template)


                    dataset_md = md.Metadata(dataset_path)
                    #empty_md   = md.Metadata()
                    #dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    #del empty_md, template_md, fishnet_template

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    out_xml = rf"{current_md_folder}\Fishnet\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    target_file_path = rf"{inport_md_folder}\Fishnet\{dataset_name}.xml"
                    custom_xslt_path = rf"{inport_md_folder}\ArcGIS2InPort.xsl"

                    dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
                    parse_xml_file_format_and_save(target_file_path)

                    del target_file_path, custom_xslt_path

                    del dataset_md

                elif dataset_name.endswith("Lat_Long"):

                    print(f"\tLat_Long")

                    lat_long_template = rf"{current_md_folder}\Lat_Long\lat_long_template.xml"
                    template_md = md.Metadata(lat_long_template)

                    dataset_md = md.Metadata(dataset_path)
                    #empty_md   = md.Metadata()
                    #dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    #del empty_md, template_md, lat_long_template

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    out_xml = rf"{current_md_folder}\Lat_Long\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    target_file_path = rf"{inport_md_folder}\Lat_Long\{dataset_name}.xml"
                    custom_xslt_path = rf"{inport_md_folder}\ArcGIS2InPort.xsl"

                    dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
                    parse_xml_file_format_and_save(target_file_path)

                    del target_file_path, custom_xslt_path

                    del dataset_md

                elif dataset_name.endswith("Region"):

                    print(f"\tRegion")

                    region_template = rf"{current_md_folder}\Region\region_template.xml"
                    template_md = md.Metadata(region_template)

                    dataset_md = md.Metadata(dataset_path)
                    #empty_md   = md.Metadata()
                    #dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    #del empty_md, template_md, region_template

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    out_xml = rf"{current_md_folder}\Region\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    target_file_path = rf"{inport_md_folder}\Region\{dataset_name}.xml"
                    custom_xslt_path = rf"{inport_md_folder}\ArcGIS2InPort.xsl"

                    dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
                    parse_xml_file_format_and_save(target_file_path)

                    del target_file_path, custom_xslt_path

                    del dataset_md

                elif dataset_name.endswith("Sample_Locations"):

                    print(f"\tSample_Locations")

                    sample_locations_template = rf"{current_md_folder}\Sample_Locations\sample_locations_template.xml"
                    template_md = md.Metadata(sample_locations_template)

                    dataset_md = md.Metadata(dataset_path)
                    #empty_md   = md.Metadata()
                    #dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    #del empty_md, template_md, sample_locations_template

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

                    out_xml = rf"{current_md_folder}\Sample_Locations\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    target_file_path = rf"{inport_md_folder}\Sample_Locations\{dataset_name}.xml"
                    custom_xslt_path = rf"{inport_md_folder}\ArcGIS2InPort.xsl"

                    dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
                    parse_xml_file_format_and_save(target_file_path)

                    del target_file_path, custom_xslt_path

                    del dataset_md, _tags

                elif dataset_name.endswith("GRID_Points"):

                    print(f"\tGRID_Points")

                    grid_points_template = rf"{current_md_folder}\GRID_Points\grid_points_template.xml"
                    template_md = md.Metadata(grid_points_template)

                    dataset_md = md.Metadata(dataset_path)
                    #empty_md   = md.Metadata()
                    #dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    #del empty_md, template_md, grid_points_template

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

                    out_xml = rf"{current_md_folder}\GRID_Points\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    target_file_path = rf"{inport_md_folder}\GRID_Points\{dataset_name}.xml"
                    custom_xslt_path = rf"{inport_md_folder}\ArcGIS2InPort.xsl"

                    dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
                    parse_xml_file_format_and_save(target_file_path)

                    del target_file_path, custom_xslt_path

                    del dataset_md, _tags

                elif "DisMAP_Regions" == dataset_name:

                    print(f"\tDisMAP_Regions")

                    dismap_regions_template = rf"{current_md_folder}\Region\dismap_regions_template.xml"
                    template_md = md.Metadata(dismap_regions_template)

                    dataset_md = md.Metadata(dataset_path)
                    #empty_md   = md.Metadata()
                    #dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    #del empty_md, template_md, dismap_regions_template

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    out_xml = rf"{current_md_folder}\Region\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    target_file_path = rf"{inport_md_folder}\Region\{dataset_name}.xml"
                    custom_xslt_path = rf"{inport_md_folder}\ArcGIS2InPort.xsl"

                    dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
                    parse_xml_file_format_and_save(target_file_path)

                    del target_file_path, custom_xslt_path

                    del dataset_md

                elif dataset_name.endswith("Bathymetry"):

                    print(f"\tBathymetry")

                    bathymetry_template = rf"{current_md_folder}\Bathymetry\bathymetry_template.xml"
                    template_md = md.Metadata(bathymetry_template)

                    dataset_md = md.Metadata(dataset_path)
                    #empty_md   = md.Metadata()
                    #dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    #del empty_md, template_md, bathymetry_template

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    out_xml = rf"{current_md_folder}\Bathymetry\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    target_file_path = rf"{inport_md_folder}\Bathymetry\{dataset_name}.xml"
                    custom_xslt_path = rf"{inport_md_folder}\ArcGIS2InPort.xsl"

                    dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
                    parse_xml_file_format_and_save(target_file_path)

                    del target_file_path, custom_xslt_path

                    del dataset_md

                elif dataset_name.endswith("Latitude"):

                    print(f"\tLatitude")

                    latitude_template = rf"{current_md_folder}\Latitude\latitude_template.xml"
                    template_md = md.Metadata(latitude_template)

                    dataset_md = md.Metadata(dataset_path)
                    #empty_md   = md.Metadata()
                    #dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    #del empty_md, template_md, latitude_template

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    out_xml = rf"{current_md_folder}\Latitude\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    target_file_path = rf"{inport_md_folder}\Latitude\{dataset_name}.xml"
                    custom_xslt_path = rf"{inport_md_folder}\ArcGIS2InPort.xsl"

                    dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
                    parse_xml_file_format_and_save(target_file_path)

                    del target_file_path, custom_xslt_path

                    del dataset_md

                elif dataset_name.endswith("Longitude"):

                    print(f"\tLongitude")

                    longitude_template = rf"{current_md_folder}\Longitude\longitude_template.xml"
                    template_md = md.Metadata(longitude_template)

                    dataset_md = md.Metadata(dataset_path)
                    #empty_md   = md.Metadata()
                    #dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    #del empty_md, template_md, longitude_template

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    out_xml = rf"{current_md_folder}\Longitude\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    target_file_path = rf"{inport_md_folder}\Longitude\{dataset_name}.xml"
                    custom_xslt_path = rf"{inport_md_folder}\ArcGIS2InPort.xsl"

                    dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
                    parse_xml_file_format_and_save(target_file_path)

                    del target_file_path, custom_xslt_path

                    del dataset_md

                elif dataset_name.endswith("Raster_Mask"):

                    print(f"\tRaster_Mask")

                    raster_mask_template = rf"{current_md_folder}\Raster_Mask\raster_mask_template.xml"
                    template_md = md.Metadata(raster_mask_template)

                    dataset_md = md.Metadata(dataset_path)
                    #empty_md   = md.Metadata()
                    #dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    #del empty_md, template_md, raster_mask_template

                    dataset_md.title             = metadata_dictionary[dataset_name]["Dataset Service Title"]
                    dataset_md.tags              = metadata_dictionary[dataset_name]["Tags"]
                    dataset_md.summary           = metadata_dictionary[dataset_name]["Summary"]
                    dataset_md.description       = metadata_dictionary[dataset_name]["Description"]
                    dataset_md.credits           = metadata_dictionary[dataset_name]["Credits"]
                    dataset_md.accessConstraints = metadata_dictionary[dataset_name]["Access Constraints"]
                    dataset_md.save()

                    dataset_md.synchronize("ALWAYS")

                    out_xml = rf"{current_md_folder}\Raster_Mask\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    target_file_path = rf"{inport_md_folder}\Raster_Mask\{dataset_name}.xml"
                    custom_xslt_path = rf"{inport_md_folder}\ArcGIS2InPort.xsl"

                    dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
                    parse_xml_file_format_and_save(target_file_path)

                    del target_file_path, custom_xslt_path

                    del dataset_md

                elif dataset_name.endswith("Mosaic"):

                    print(f"\tMosaic")

                    mosaic_template = rf"{current_md_folder}\Mosaic\mosaic_template.xml"
                    template_md = md.Metadata(mosaic_template)

                    dataset_md = md.Metadata(dataset_path)
                    #empty_md   = md.Metadata()
                    #dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    #del empty_md, template_md, mosaic_template

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

                    out_xml = rf"{current_md_folder}\Mosaic\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    target_file_path = rf"{inport_md_folder}\Mosaic\{dataset_name}.xml"
                    custom_xslt_path = rf"{inport_md_folder}\ArcGIS2InPort.xsl"

                    dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
                    parse_xml_file_format_and_save(target_file_path)

                    del target_file_path, custom_xslt_path

                    del dataset_md, _tags

                elif dataset_name.endswith(".crf"):

                    print(f"\tCRF")
                    #print(dataset_name)
                    #print(dataset_path)
                    #dataset_path = dataset_path.replace(crfs_folder, project_gdb).replace(".crf", "_Mosaic")
                    #print(dataset_path)

                    crf_template = rf"{current_md_folder}\CRF\crf_template.xml"
                    template_md = md.Metadata(crf_template)

                    dataset_md = md.Metadata(dataset_path)
                    #empty_md   = md.Metadata()
                    #dataset_md.copy(empty_md)
                    dataset_md.save()
                    dataset_md.copy(template_md)
                    dataset_md.save()
                    #del empty_md, template_md, crf_template

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

                    out_xml = rf"{current_md_folder}\CRF\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    target_file_path = rf"{inport_md_folder}\CRF\{dataset_name}.xml"
                    custom_xslt_path = rf"{inport_md_folder}\ArcGIS2InPort.xsl"

                    dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
                    parse_xml_file_format_and_save(target_file_path)

                    del target_file_path, custom_xslt_path

                    del dataset_md, _tags

                else:
                    print(f"\tRegion Table")

                    if dataset_name.endswith("IDW"):

                        idw_region_table_template = rf"{current_md_folder}\Table\idw_region_table_template.xml"
                        template_md = md.Metadata(idw_region_table_template)

                        dataset_md = md.Metadata(dataset_path)
                        #empty_md   = md.Metadata()
                        #dataset_md.copy(empty_md)
                        dataset_md.save()
                        dataset_md.copy(template_md)
                        dataset_md.save()
                        #del empty_md, template_md, idw_region_table_template

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

                        out_xml = rf"{current_md_folder}\Table\{dataset_name}.xml"
                        dataset_md.saveAsXML(out_xml)
                        parse_xml_file_format_and_save(out_xml)
                        del out_xml

                        target_file_path = rf"{inport_md_folder}\Table\{dataset_name}.xml"
                        custom_xslt_path = rf"{inport_md_folder}\ArcGIS2InPort.xsl"

                        dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
                        parse_xml_file_format_and_save(target_file_path)

                        del target_file_path, custom_xslt_path

                        del dataset_md, _tags

                    elif dataset_name.endswith("GLMME"):

                        glmme_region_table_template = rf"{current_md_folder}\Table\glmme_region_table_template.xml"
                        template_md = md.Metadata(glmme_region_table_template)

                        dataset_md = md.Metadata(dataset_path)
                        #empty_md   = md.Metadata()
                        #dataset_md.copy(empty_md)
                        dataset_md.save()
                        dataset_md.copy(template_md)
                        dataset_md.save()
                        #del empty_md, template_md, glmme_region_table_template

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

                        out_xml = rf"{current_md_folder}\Table\{dataset_name}.xml"
                        dataset_md.saveAsXML(out_xml)
                        parse_xml_file_format_and_save(out_xml)
                        del out_xml

                        target_file_path = rf"{inport_md_folder}\Table\{dataset_name}.xml"
                        custom_xslt_path = rf"{inport_md_folder}\ArcGIS2InPort.xsl"

                        dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
                        parse_xml_file_format_and_save(target_file_path)

                        del target_file_path, custom_xslt_path

                        del dataset_md, _tags

                    else:
                        pass

                del dataset_name, dataset_path

            del workspace

        del datasets

        # Variables set in function
        del project_gdb, base_project_folder, current_md_folder, inport_md_folder
        del project_folder, scratch_folder, crfs_folder
        del metadata_dictionary, workspaces

        # Imports
        del dismap, dataset_title_dict, parse_xml_file_format_and_save, unique_years
        del md

        # Function Parameters
        del base_project_file, project_name

    except Exception:
        pass
    except:
        traceback.print_exc()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function: ##--> '{', '.join(rk)}' <--##"); del rk
        return True
    finally:
        pass

def create_thumbnails(base_project_file="", project_name=""):
    try:
        # Import
        from arcpy import metadata as md

        import dismap
        importlib.reload(dismap)
        from dismap import parse_xml_file_format_and_save

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2)
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        base_project_folder = rf"{os.path.dirname(base_project_file)}"
        base_project_file   = rf"{base_project_folder}\DisMAP.aprx"
        project_folder      = rf"{base_project_folder}\{project_name}"
        project_gdb         = rf"{project_folder}\{project_name}.gdb"
        metadata_folder     = rf"{project_folder}\Export Metadata"
        crfs_folder         = rf"{project_folder}\CRFs"
        scratch_folder      = rf"{project_folder}\Scratch"

        arcpy.env.workspace        = project_gdb
        arcpy.env.scratchWorkspace = rf"{scratch_folder}\scratch.gdb"

        aprx = arcpy.mp.ArcGISProject(base_project_file)
        home_folder = aprx.homeFolder

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
                #print(dataset_path)
                dataset_name = os.path.basename(dataset_path)

                print(f"Dataset Name: {dataset_name}")

                if "Datasets" == dataset_name:

                    print(f"\tDataset Table")

                    dataset_md = md.Metadata(dataset_path)

                    out_xml = rf"{metadata_folder}\Table\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    del dataset_md

                elif "Species_Filter" == dataset_name:

                    print(f"\tSpecies Filter Table")

                    dataset_md = md.Metadata(dataset_path)

                    out_xml = rf"{metadata_folder}\Table\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    del dataset_md

                elif "Indicators" in dataset_name:

                    print(f"\tIndicators")

                    dataset_md = md.Metadata(dataset_path)

                    out_xml = rf"{metadata_folder}\Table\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    del dataset_md

                elif "LayerSpeciesYearImageName" in dataset_name:

                    print(f"\tLayer Species Year Image Name")

                    dataset_md = md.Metadata(dataset_path)

                    out_xml = rf"{metadata_folder}\Table\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    del dataset_md

                elif dataset_name.endswith("Boundary"):

                    print(f"\tBoundary")

                    dataset_md = md.Metadata(dataset_path)

                    out_xml = rf"{metadata_folder}\Boundary\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    del dataset_md

                elif dataset_name.endswith("Extent_Points"):

                    print(f"\tExtent_Points")

                    dataset_md = md.Metadata(dataset_path)

                    out_xml = rf"{metadata_folder}\Extent_Points\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    del dataset_md

                elif dataset_name.endswith("Fishnet"):

                    print(f"\tFishnet")

                    dataset_md = md.Metadata(dataset_path)

                    out_xml = rf"{metadata_folder}\Fishnet\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    del dataset_md

                elif dataset_name.endswith("Lat_Long"):

                    print(f"\tLat_Long")

                    dataset_md = md.Metadata(dataset_path)

                    out_xml = rf"{metadata_folder}\Lat_Long\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    del dataset_md

                elif dataset_name.endswith("Region"):

                    print(f"\tRegion")

                    dataset_md = md.Metadata(dataset_path)

                    out_xml = rf"{metadata_folder}\Region\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    del dataset_md

                elif dataset_name.endswith("Sample_Locations"):

                    print(f"\tSample_Locations")

                    dataset_md = md.Metadata(dataset_path)

                    out_xml = rf"{metadata_folder}\Sample_Locations\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    del dataset_md

                elif dataset_name.endswith("GRID_Points"):

                    print(f"\tGRID_Points")

                    dataset_md = md.Metadata(dataset_path)

                    out_xml = rf"{metadata_folder}\GRID_Points\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    del dataset_md

                elif "DisMAP_Regions" == dataset_name:

                    print(f"\tDisMAP_Regions")

                    dataset_md = md.Metadata(dataset_path)

                    out_xml = rf"{metadata_folder}\Region\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    del dataset_md

                elif dataset_name.endswith("Bathymetry"):

                    print(f"\tBathymetry")

                    dataset_md = md.Metadata(dataset_path)

                    out_xml = rf"{metadata_folder}\Bathymetry\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    del dataset_md

                elif dataset_name.endswith("Latitude"):

                    print(f"\tLatitude")

                    dataset_md = md.Metadata(dataset_path)

                    out_xml = rf"{metadata_folder}\Latitude\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    del dataset_md

                elif dataset_name.endswith("Longitude"):

                    print(f"\tLongitude")

                    dataset_md = md.Metadata(dataset_path)

                    out_xml = rf"{metadata_folder}\Longitude\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    del dataset_md

                elif dataset_name.endswith("Raster_Mask"):

                    print(f"\tRaster_Mask")

                    dataset_md = md.Metadata(dataset_path)

                    out_xml = rf"{metadata_folder}\Raster_Mask\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    del dataset_md

                elif dataset_name.endswith("Mosaic"):

                    print(f"\tMosaic")

                    dataset_md = md.Metadata(dataset_path)

                    out_xml = rf"{metadata_folder}\Mosaic\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    del dataset_md

                elif dataset_name.endswith(".crf"):

                    print(f"\tCRF")

                    dataset_md = md.Metadata(dataset_path)

                    out_xml = rf"{metadata_folder}\CRF\{dataset_name}.xml"
                    dataset_md.saveAsXML(out_xml)
                    parse_xml_file_format_and_save(out_xml)
                    del out_xml

                    del dataset_md

                else:
                    pass
                    print(f"\tRegion Table")

                    if dataset_name.endswith("IDW"):

                        dataset_md = md.Metadata(dataset_path)

                        out_xml = rf"{metadata_folder}\Table\{dataset_name}.xml"
                        dataset_md.saveAsXML(out_xml)
                        parse_xml_file_format_and_save(out_xml)
                        del out_xml

                        del dataset_md

                    elif dataset_name.endswith("GLMME"):

                        dataset_md = md.Metadata(dataset_path)

                        out_xml = rf"{metadata_folder}\Table\{dataset_name}.xml"
                        dataset_md.saveAsXML(out_xml)
                        parse_xml_file_format_and_save(out_xml)
                        del out_xml

                        del dataset_md

                    else:
                        pass

                del dataset_name, dataset_path

            del workspace, datasets

        del workspaces

        # Variables set in function for aprx
        del home_folder
        # Save aprx one more time and then delete
        aprx.save()
        del aprx

        # Variables set in function
        del project_gdb, base_project_folder, metadata_folder, crfs_folder
        del project_folder, scratch_folder

        # Imports
        del dismap, parse_xml_file_format_and_save
        del md

        # Function Parameters
        del base_project_file, project_name

    except Exception:
        pass
    except:
        traceback.print_exc()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function: ##--> '{', '.join(rk)}' <--##"); del rk
        return True
    finally:
        pass

def export_to_inport_xml_files(base_project_file="", project_name=""):
    try:
        if not base_project_file or not project_name: raise SystemExit("parameters are missing")

        # Import
        from arcpy import metadata as md

        import dismap
        importlib.reload(dismap)
        from dismap import parse_xml_file_format_and_save

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2)
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        base_project_folder = rf"{os.path.dirname(base_project_file)}"
        project_folder      = rf"{base_project_folder}\{project_name}"
        project_gdb         = rf"{project_folder}\{project_name}.gdb"
        metadata_folder     = rf"{project_folder}\InPort Metadata"
        crfs_folder         = rf"{project_folder}\CRFs"
        scratch_folder      = rf"{project_folder}\Scratch"

        arcpy.env.workspace        = project_gdb
        arcpy.env.scratchWorkspace = rf"{scratch_folder}\scratch.gdb"

        datasets = [rf"{project_gdb}\Species_Filter", rf"{project_gdb}\Indicators", rf"{project_gdb}\DisMAP_Regions", rf"{project_gdb}\GMEX_IDW_Sample_Locations", rf"{project_gdb}\GMEX_IDW_Mosaic", rf"{crfs_folder}\GMEX_IDW.crf"]

        for dataset_path in sorted(datasets):
            print(dataset_path)

            dataset_name = os.path.basename(dataset_path)

            print(f"Dataset Name: {dataset_name}")

            target_file_path = rf"{metadata_folder}\{dataset_name}.xml"
            custom_xslt_path = rf"{metadata_folder}\ArcGIS2InPort.xsl"

            dataset_md = md.Metadata(dataset_path)
            dataset_md.saveAsUsingCustomXSLT(target_file_path, custom_xslt_path)
            del dataset_md

            try:
                parse_xml_file_format_and_save(target_file_path)
            except Exception:
                raise Exception

            del target_file_path, custom_xslt_path

            del dataset_name, dataset_path

        del datasets

        # Variables set in function
        del project_gdb, base_project_folder, metadata_folder
        del project_folder, scratch_folder, crfs_folder

        # Imports
        del dismap, parse_xml_file_format_and_save
        del md

        # Function Parameters
        del base_project_file, project_name

    except Exception:
        pass
    except:
        traceback.print_exc()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function: ##--> '{', '.join(rk)}' <--##"); del rk
        return True
    finally:
        pass

def create_maps(base_project_file="", project_name="", dataset=""):
    try:
        # Import
        from arcpy import metadata as md

        import dismap
        importlib.reload(dismap)
        from dismap import parse_xml_file_format_and_save

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2)
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        base_project_folder = rf"{os.path.dirname(base_project_file)}"
        base_project_file   = rf"{base_project_folder}\DisMAP.aprx"
        project_folder      = rf"{base_project_folder}\{project_name}"
        project_gdb         = rf"{project_folder}\{project_name}.gdb"
        metadata_folder     = rf"{project_folder}\Export Metadata"
        crfs_folder         = rf"{project_folder}\CRFs"
        scratch_folder      = rf"{project_folder}\Scratch"

        arcpy.env.workspace        = project_gdb
        arcpy.env.scratchWorkspace = rf"{scratch_folder}\scratch.gdb"

        aprx = arcpy.mp.ArcGISProject(base_project_file)

        dataset_name = os.path.basename(dataset)

        print(f"Dataset Name: {dataset_name}")

        if dataset_name not in [cm.name for cm in aprx.listMaps()]:
            print(f"Creating Map: {dataset_name}")
            aprx.createMap(f"{dataset_name}", "Map")
            aprx.save()
        else:
            pass

        current_map = aprx.listMaps(f"{dataset_name}")[0]
        print(f"Current Map:  {current_map.name}")

        if dataset_name not in [lyr.name for lyr in current_map.listLayers(f"{dataset_name}")]:
            print(f"Adding {dataset_name} to Map")

            map_layer = arcpy.management.MakeFeatureLayer(dataset, f"{dataset_name}")

            #arcpy.management.Delete(rf"{project_folder}\Layers\{dataset_name}.lyrx")
            #os.remove(rf"{project_folder}\Layers\{dataset_name}.lyrx")

            map_layer_file = arcpy.management.SaveToLayerFile(map_layer, rf"{project_folder}\Layers\{dataset_name}.lyrx")
            del map_layer_file

            map_layer_file = arcpy.mp.LayerFile(rf"{project_folder}\Layers\{dataset_name}.lyrx")

            arcpy.management.Delete(map_layer)
            del map_layer

            current_map.addLayer(map_layer_file)
            del map_layer_file

            aprx.save()
        else:
            pass

        #aprx_basemaps = aprx.listBasemaps()
        #basemap = 'GEBCO Basemap/Contours (NOAA NCEI Visualization)'
        basemap = "Terrain with Labels"

        current_map.addBasemap(basemap)
        del basemap

        # Set Reference Scale
        current_map.referenceScale = 50000000

        # Clear Selection
        current_map.clearSelection()

        current_map_cim = current_map.getDefinition('V3')
        current_map_cim.enableWraparound = True
        current_map.setDefinition(current_map_cim)

        # Return the layer's CIM definition
        cim_lyr = lyr.getDefinition('V3')

        # Modify the color, width and dash template for the SolidStroke layer
        symLvl1 = cim_lyr.renderer.symbol.symbol.symbolLayers[0]
        symLvl1.color.values = [0, 0, 0, 100]
        symLvl1.width = 1

        # Push the changes back to the layer object
        lyr.setDefinition(cim_lyr)
        del symLvl1, cim_lyr

        aprx.save()

        height = arcpy.Describe(dataset).extent.YMax - arcpy.Describe(dataset).extent.YMin
        width  = arcpy.Describe(dataset).extent.XMax - arcpy.Describe(dataset).extent.XMin

        # map_width, map_height
        map_width, map_height = 8.5, 11

        if height > width:
            page_height = map_height; page_width = map_width
        elif height < width:
            page_height = map_width; page_width = map_height
        else:
            page_width = map_width; page_height = map_height

        del map_width, map_height
        del height, width

        if dataset_name not in [cl.name for cl in aprx.listLayouts()]:
            print(f"Creating Layout: {dataset_name}")
            aprx.createLayout(page_width, page_height, "INCH", f"{dataset_name}")
            aprx.save()
        else:
            print(f"Layout: {dataset_name} exists")

        #Set the default map camera to the extent of the park boundary before opening the new view
        #default camera only affects newly opened views
        lyr = current_map.listLayers(f"{dataset_name}")[-1]

        #
        arcpy.management.SelectLayerByAttribute(lyr, 'NEW_SELECTION', "DatasetCode in ('ENBS', 'HI', 'NEUS_SPR')")

        mv = current_map.openView()
        mv.panToExtent(mv.getLayerExtent(lyr, True, True))
        mv.zoomToAllLayers()
        del mv

        arcpy.management.SelectLayerByAttribute(lyr, 'CLEAR_SELECTION')

        av = aprx.activeView
        av.exportToPNG(rf"{project_folder}\Layers\{dataset_name}.png", width=288, height=192, resolution = 96, color_mode="24-BIT_TRUE_COLOR", embed_color_profile=True)
        av.exportToJPEG(rf"{project_folder}\Layers\{dataset_name}.jpg", width=288, height=192, resolution = 96, jpeg_color_mode="24-BIT_TRUE_COLOR", embed_color_profile=True)
        del av

        #print(current_map.referenceScale)

        #export the newly opened active view to PDF, then delete the new map
        #mv = aprx.activeView
        #mv.exportToPDF(r"C:\Temp\RangerStations.pdf", width=700, height=500, resolution=96)
        #aprx.deleteItem(current_map)

        #mv = aprx.activeView
        #mv = current_map.defaultView
        #mv.zoomToAllLayers()
        #print(mv.camera.getExtent())
        #arcpy.management.Delete(rf"{project_folder}\Layers\{dataset_name}.png")
        #arcpy.management.Delete(rf"{project_folder}\Layers\{dataset_name}.jpg")

        #os.remove(rf"{project_folder}\Layers\{dataset_name}.png")
        #os.remove(rf"{project_folder}\Layers\{dataset_name}.jpg")


        #mv.exportToPNG(rf"{project_folder}\Layers\{dataset_name}.png", width=288, height=192, resolution = 96, color_mode="24-BIT_TRUE_COLOR", embed_color_profile=True)
        #mv.exportToJPEG(rf"{project_folder}\Layers\{dataset_name}.jpg", width=288, height=192, resolution = 96, jpeg_color_mode="24-BIT_TRUE_COLOR", embed_color_profile=True)
        #del mv

        #Export the resulting imported layout and changes to JPEG
        #print(f"Exporting '{current_layout.name}'")
        #current_map.exportToJPEG(rf"{project_folder}\Layouts\{current_layout.name}.jpg", page_width, page_height)
        #current_map.exportToPNG(rf"{project_folder}\Layouts\{current_layout.name}.png", page_width, page_height)

        #fc_md = md.Metadata(dataset)
        #fc_md.thumbnailUri = rf"{project_folder}\Layouts\{dataset_name}.png"
        #fc_md.thumbnailUri = rf"{project_folder}\Layouts\{dataset_name}.jpg"
        #fc_md.save()
        #del fc_md

        aprx.save()


    # #            from arcpy import metadata as md
    # #
    # #            fc_md = md.Metadata(dataset)
    # #            fc_md.thumbnailUri = rf"{project_folder}\Layers\{dataset_name}.png"
    # #            fc_md.save()
    # #            del fc_md
    # #            del md

##        aprx.save()
##
##        current_layout = [cl for cl in aprx.listLayouts() if cl.name == dataset_name][0]
##        print(f"Current Layout: {current_layout.name}")
##
##        current_layout.openView()
##
##        # Remove all map frames
##        for mf in current_layout.listElements("MapFrame_Element"): current_layout.deleteElement(mf); del mf
##
##        # print(f'Layout Name: {current_layout.name}')
##        # print(f'    Width x height: {current_layout.pageWidth} x {current_layout.pageHeight} units are {current_layout.pageUnits}')
##        # print(f'    MapFrame count: {str(len(current_layout.listElements("MapFrame_Element")))}')
##        # for mf in current_layout.listElements("MapFrame_Element"):
##        #     if len(current_layout.listElements("MapFrame_Element")) > 0:
##        #         print(f'        MapFrame name: {mf.name}')
##        # print(f'    Total element count: {str(len(current_layout.listElements()))} \n')
##
##
##        print(f"Create a new map frame using a point geometry")
##        #Create a new map frame using a point geometry
##        #mf1 = current_layout.createMapFrame(arcpy.Point(0.01,0.01), current_map, 'New MF - Point')
##        mf1 = current_layout.createMapFrame(arcpy.Point(0.0,0.0), current_map, 'New MF - Point')
##        #mf1.elementWidth = 10
##        #mf1.elementHeight = 7.5
##        #mf1.elementWidth  = page_width  - 0.01
##        #mf1.elementHeight = page_height - 0.01
##        mf1.elementWidth  = page_width
##        mf1.elementHeight = page_height

##        lyr = current_map.listLayers(f"{dataset_name}")[0]
##
##        #Zoom to ALL selected features and export to PDF
##        #arcpy.SelectLayerByAttribute_management(lyr, 'NEW_SELECTION')
##        #mf1.zoomToAllLayers(True)
##        #arcpy.SelectLayerByAttribute_management(lyr, 'CLEAR_SELECTION')
##
##        #Set the map frame extent to the extent of a layer
##        #mf1.camera.setExtent(mf1.getLayerExtent(lyr, False, True))
##        #mf1.camera.scale = mf1.camera.scale * 1.1 #add a slight buffer
##
##        del lyr

##        print(f"Create a new bookmark set to the map frame's default extent")
##        #Create a new bookmark set to the map frame's default extent
##        bkmk = mf1.createBookmark('Default Extent', "The map's default extent")
##        bkmk.updateThumbnail()
##        del mf1
##        del bkmk

        # Create point text element using a system style item
        # txtStyleItem = aprx.listStyleItems('ArcGIS 2D', 'TEXT', 'Title (Serif)')[0]
        # ptTxt = aprx.createTextElement(current_layout, arcpy.Point(5.5, 4.25), 'POINT', f'{dataset_name}', 10, style_item=txtStyleItem)
        # del txtStyleItem

        # Change the anchor position and reposition the text to center
        # ptTxt.setAnchor('Center_Point')
        # ptTxt.elementPositionX = page_width / 2.0
        # ptTxt.elementPositionY = page_height - 0.25
        # del ptTxt

        # print(f"Using CIM to update border")
        # current_layout_cim = current_layout.getDefinition('V3')
        # for elm in current_layout_cim.elements:
        #     if type(elm).__name__ == 'CIMMapFrame':
        #         if elm.graphicFrame.borderSymbol.symbol.symbolLayers:
        #             sym = elm.graphicFrame.borderSymbol.symbol.symbolLayers[0]
        #             sym.width = 5
        #             sym.color.values = [255, 0, 0, 100]
        #         else:
        #             arcpy.AddWarning(elm.name + ' has NO symbol layers')
        # current_layout.setDefinition(current_layout_cim)
        # del current_layout_cim, elm, sym

##        ExportLayout = True
##        if ExportLayout:
##            #Export the resulting imported layout and changes to JPEG
##            print(f"Exporting '{current_layout.name}'")
##            current_layout.exportToJPEG(rf"{project_folder}\Layouts\{current_layout.name}.jpg")
##            current_layout.exportToPNG(rf"{project_folder}\Layouts\{current_layout.name}.png")
##        del ExportLayout

##        #Export the resulting imported layout and changes to JPEG
##        print(f"Exporting '{current_layout.name}'")
##        current_map.exportToJPEG(rf"{project_folder}\Layouts\{current_layout.name}.jpg", page_width, page_height)
##        current_map.exportToPNG(rf"{project_folder}\Layouts\{current_layout.name}.png", page_width, page_height)
##
##        fc_md = md.Metadata(dataset)
##        fc_md.thumbnailUri = rf"{project_folder}\Layouts\{current_layout.name}.png"
##        #fc_md.thumbnailUri = rf"{project_folder}\Layouts\{current_layout.name}.jpg"
##        fc_md.save()
##        del fc_md
##
##        aprx.save()

        # aprx.deleteItem(current_map)
        #aprx.deleteItem(current_layout)

        del current_map
        #, current_layout
        #del page_width, page_height
        del dataset_name, dataset

        aprx.save()

        print(f"\nCurrent Maps & Layouts")

        current_maps    = aprx.listMaps()
        #current_layouts = aprx.listLayouts()

        if current_maps:
            print(f"\nCurrent Maps\n")
            for current_map in current_maps:
                print(f"\tProject Map: {current_map.name}")
                del current_map
        else:
            arcpy.AddWarning("No maps in project_name")

##        if current_layouts:
##            print(f"\nCurrent Layouts\n")
##            for current_layout in current_layouts:
##                print(f"\tProject Layout: {current_layout.name}")
##                del current_layout
##        else:
##            arcpy.AddWarning("No layouts in Project")

        #del current_layouts
        del current_maps

        # Variables set in function for aprx

        # Save aprx one more time and then delete
        aprx.save()
        del aprx

        # Variables set in function
        del project_gdb, base_project_folder, metadata_folder, crfs_folder
        del project_folder, scratch_folder

        # Imports
        del dismap, parse_xml_file_format_and_save
        del md

        # Function Parameters
        del base_project_file, project_name

    except Exception:
        pass
    except:
        traceback.print_exc()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function: ##--> '{', '.join(rk)}' <--##"); del rk
        return True
    finally:
        pass

def update_xml_elements(project_gdb="", contacts=""):
    try:
        # Imports
        from lxml import etree
        from io import StringIO
        import copy
        import arcpy
        from arcpy import metadata as md
        # Project modules
        #from src.project_tools import pretty_format_xml_file

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2)
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        project_folder = os.path.dirname(project_gdb)
        crfs_folder    = rf"{project_folder}\CRFs"
        scratch_folder = rf"{project_folder}\Scratch"

        root_dict = {"Esri"       :  0, "dataIdInfo" :  1, "mdChar"      :  2,
                     "mdContact"  :  3, "mdDateSt"   :  4, "mdFileID"    :  5,
                     "mdLang"     :  6, "mdMaint"    :  7, "mdHrLv"      :  8,
                     "mdHrLvName" :  9, "refSysInfo" : 10, "spatRepInfo" : 11,
                     "spdoinfo"   : 12, "dqInfo"     : 13, "distInfo"    : 14,
                     "eainfo"     : 15, "contInfo"   : 16, "spref"       : 17,
                     "spatRepInfo" : 18, "dataSetFn" : 19, "Binary"      : 100,}

        esri_dict ={"CreaDate" : 0,  "CreaTime" : 1, "ArcGISFormat" : 2,
                    "ArcGISstyle" : 3, "SyncOnce" : 4, "DataProperties" : 5,
                    "itemProps" : 0, "itemName" : 0, "imsContentType" : 1,
                    "nativeExtBox" : 2, "westBL" : 0, "eastBL" : 1, "southBL" : 2,
                    "northBL" : 3, "exTypeCode" : 4, "coordRef" : 1, "type" : 0,
                    "geogcsn" : 2, "csUnits" : 3, "peXml" : 4, "SyncDate" : 6,
                    "SyncTime" : 7, "ModDate" : 8, "ModTime" : 9,
                    "scaleRange" : 10, "minScale" : 11, "maxScale" : 12,
                    "ArcGISProfile" : 13,}

        idCitation_dict = {"idCitation" : 0, "resTitle" : 0, "resAltTitle" : 1,
                           "collTitle"  : 2, "presForm" : 3, "PresFormCd"  : 0,
                           "fgdcGeoform" : 1, "date" : 4, "createDate" : 0,
                           "pubDate"    : 1, "revisedDate" : 2, "citRespParty"  : 6,
                           }

        dataIdInfo_dict = { "idCitation" :  0, "searchKeys" :  1, "idPurp"   : 2,
                            "idAbs"      :  3, "idCredit"   :  4, "idStatus" : 5,
                            "idPoC"      :  6, "themeKeys"  :  7, "placeKeys" : 8,
                            "tempKeys" : 9, "resConst" : 12,
                            "resMaint"   : 13, "envirDesc"  : 14, "dataLang" : 15,
                            "dataChar"   : 16, "spatRpType" : 17, "dataExt"  : 18,
                            "spatRpType" : 19, "tpCat"      : 20,}

        contact_dict = {"editorSource" : 0, "editorDigest" : 1,"rpIndName" : 2,
                        "rpOrgName"    : 3, "rpPosName"    : 4, "rpCntInfo" : 5,
                        "cntAddress"   : 0, "delPoint" : 0, "city" : 1,
                        "adminArea"    : 2, "postCode" : 3, "eMailAdd" : 4,
                        "country"      : 5, "cntPhone" : 1, "voiceNum" : 0,
                        "faxNum"       : 1, "cntHours" : 2, "cntOnlineRes" : 3,
                        "linkage"      : 0, "protocol" : 1, "orName" : 2,
                        "orDesc"       : 3, "orFunct"  : 4, "OnFunctCd" : 0,
                        "editorSave"   : 6, "displayName"  : 7, "role" : 8,
                        "RoleCd"     : 0,
                        }

        dqInfo_dict = { "dqScope" : 0, "scpLvl" : 0, "ScopeCd" : 0,
                        "scpLvlDesc" : 1, "datasetSet" : 0, "report" : 1,
                        "measDesc" : 0, "report" : 2, "measDesc" : 0,
                        "dataLineage" : 3, "statement" : 0, "dataSource" : 1,
                        "srcDesc" : 0, "srcCitatn" : 1, "resTitle" : 0,
                        "date" : 1, "createDate" : 0, "prcStep" : 2,
                        "stepDesc" : 0, "stepProc" : 1, "stepDateTm" : 2,
                      }
        RoleCd_dict = {"001" : "Resource Provider", "002" : "Custodian",
                       "003" : "Owner",             "004" : "User",
                       "005" : "Distributor",       "006" : "Originator",
                       "007" : "Point of Contact",  "008" : "Principal Investigator",
                       "009" : "Processor",         "010" : "Publisher",
                       "011" : "Author",            "012" : "Collaborator",
                       "013" : "Editor",            "014" : "Mediator",
                       "015" : "Rights Holder",}

        tpCat_dict = {"002": '<tpCat><TopicCatCd value="002"></TopicCatCd></tpCat>',
         "007": '<tpCat><TopicCatCd value="007"></TopicCatCd></tpCat>',
         "014": '<tpCat><TopicCatCd value="014"></TopicCatCd></tpCat>',}

        workspaces = [project_gdb, crfs_folder]

        contacts_xml = rf"{os.environ['USERPROFILE']}\Documents\ArcGIS\Descriptions\contacts.xml"
        parser = etree.XMLParser(encoding='UTF-8', remove_blank_text=True)
        contacts_xml_tree = etree.parse(contacts_xml, parser=parser) # To parse from a string, use the fromstring() function instead.
        del parser
        del contacts_xml
        contacts_xml_root = contacts_xml_tree.getroot()
        #etree.indent(contacts_xml_root, space="  ")
        #print(etree.tostring(contacts_xml_root, encoding="utf-8",  method='xml', xml_declaration=True, pretty_print=True).decode())

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
                #print(dataset_path)
                dataset_name = os.path.basename(dataset_path)
                #print(f"Dataset Name:     {dataset_name}")
                #print(f"\tDataset Location: {os.path.basename(os.path.dirname(dataset_path))}")

                dataset_md = md.Metadata(dataset_path)
                dataset_md_xml = dataset_md.xml
                del dataset_md

                # Parse the XML
                parser = etree.XMLParser(encoding='UTF-8', remove_blank_text=True)
                tree = etree.parse(StringIO(dataset_md_xml), parser=parser)
                root = tree.getroot()
                del parser, dataset_md_xml

                # print(etree.tostring(tree, encoding="utf-8",  method='xml', xml_declaration=True, pretty_print=True).decode())
                # etree.indent(tree, space='   ')
                # tree.write(xml_file, encoding="utf-8",  method='xml', xml_declaration=True, pretty_print=True)

                print(f"Dataset Name: {dataset_name}")

                #etree.indent(root, space="    ")
                #print(etree.tostring(root, xml_declaration=True, encoding="utf-8").decode())

                # ######################################################################
                #               ###--->>> Esri section Start <<<---###
                # ######################################################################

                # Check for ArcGISstyle
                Esri = tree.xpath(f"./Esri")[0]
                ArcGISstyle = Esri.xpath(f"./ArcGISstyle")
                if len(ArcGISstyle) == 0:
                    _xml = "<ArcGISstyle>ISO 19139 Metadata Implementation Specification</ArcGISstyle>"
                    _root = etree.XML(_xml)
                    position = esri_dict["ArcGISstyle"]
                    Esri.insert(position, _root)
                    del position, _root, _xml
                elif len(ArcGISstyle) == 1:
                    #print(f"{len(ArcGISstyle)} {ArcGISstyle[0].tag} element is found with value: {position}")
                    ArcGISstyle[0].text = "ISO 19139 Metadata Implementation Specification"
                elif len(ArcGISstyle) > 1:
                    #print(f"Removing {len(ArcGISstyle)-1} 'ArcGISstyle' elements")
                    for i in range(1, len(ArcGISstyle)):
                        Esri.remove(ArcGISstyle[i])
                        i+=1
                        del i
                else:
                    pass
                del Esri, ArcGISstyle

                # ###--->>> Deletes an unwanted element
                Esri = tree.xpath(f"./Esri")[0]
                itemSize = Esri.xpath(f".//itemSize")
                if len(itemSize) == 0:
                    pass
                elif len(itemSize) == 1:
                    pass
                    # Esri.remove(itemSize[0])
                elif len(itemSize) > 1:
                    #print(f"Removing {len(itemSize)-1} 'itemSize' elements")
                    for i in range(1, len(itemSize)):
                        #Esri.remove(itemSize[i])
                        i+=1
                        del i
                else:
                    pass
                del itemSize
                del Esri
                # ###--->>> Deletes an unwanted element

                # Check for scaleRange
                Esri = tree.xpath(f"./Esri")[0]
                scaleRange = Esri.xpath(f"./scaleRange")
                if len(scaleRange) == 0:
                    #print("Inserting scaleRange, minScale, maxScale")
                    _xml = "<scaleRange><minScale>150000000</minScale><maxScale>5000</maxScale></scaleRange>"
                    _root = etree.XML(_xml)
                    #scale_range = etree.SubElement(Esri, "scaleRange")
                    Esri.insert(esri_dict["scaleRange"], _root)
                    #minScale    = etree.SubElement(scale_range, "minScale")
                    #minScale.text = '150000000'
                    #scaleRange.insert(esri_dict["minScale"], minScale)
                    #maxScale    = etree.SubElement(scale_range, "maxScale")
                    #maxScale.text = '5000'
                    #scaleRange.insert(esri_dict["maxScale"], maxScale)
                    # print(etree.tostring(scale_range, pretty_print=True).decode())
                    del _root, _xml
                elif len(scaleRange) == 1:
                    pass
                elif len(scaleRange) > 1:
                    print(f"Removing {len(scaleRange)-1} 'scaleRange' elements")
                    for i in range(1, len(scaleRange)):
                        Esri.remove(scaleRange[i])
                        i+=1
                        del i
                else:
                    pass
                #print(etree.tostring(Esri, encoding="utf-8", pretty_print=True).decode())
                del scaleRange, Esri

                # Check for ArcGISProfile
                Esri = tree.xpath(f"./Esri")[0]
                ArcGISProfile = Esri.xpath(f"./ArcGISProfile")
                if len(ArcGISProfile) == 0:
                    #print("Inserting ArcGISProfile")
                    _xml = "<ArcGISProfile>ISO19139</ArcGISProfile>"
                    _root = _root = etree.XML(_xml)
                    #ArcGIS_Profile = etree.SubElement(Esri, "")
                    #ArcGIS_Profile.text = 'ISO19139'
                    Esri.insert(esri_dict["ArcGISProfile"], _root)
                    #del ArcGIS_Profile
                    del _root, _xml
                elif len(ArcGISProfile) == 1:
                    ArcGISProfile[0].text = 'ISO19139'
                    #Esri.insert(esri_dict["ArcGISProfile"], ArcGISProfile[0])
                elif len(ArcGISProfile) > 1:
                    #print(f"Removing {len(ArcGISProfile)-1} 'ArcGISProfile' elements")
                    for i in range(1, len(ArcGISProfile)):
                        Esri.remove(ArcGISProfile[i])
                        i+=1
                        del i
                else:
                    pass
                #print(etree.tostring(Esri, encoding="utf-8").decode())
                del ArcGISProfile
                del Esri

                # ######################################################################
                #               ###--->>> Esri section End <<<---###
                # ######################################################################

                # ######################################################################
                #               ###--->>> dataIdInfo section Start <<<---###
                # ######################################################################

                # idCitation sub-section

                envirDesc = tree.xpath(f"./dataIdInfo/envirDesc")
                envirDesc[0].set("Sync", "TRUE")
                #if len(envirDesc) == 0:
                #    #print(f"Inserting envirDesc at {dataIdInfo_dict['envirDesc']}")
                #    element = etree.SubElement(dataIdInfo, "envirDesc")
                #    element.set("Sync", "TRUE")
                #    dataIdInfo.insert(dataIdInfo_dict['envirDesc'], element)
                #    del element
                #elif len(envirDesc) == 1:
                #    #print(f"Updating envirDesc if needed at index: {dataIdInfo.index(dataIdInfo.xpath(f'./envirDesc')[0])}")
                #    envirDesc[0].set("Sync", "TRUE")
                #    #dataIdInfo.insert(dataIdInfo_dict['envirDesc'], envirDesc[0])
                #elif len(envirDesc) > 1:
                #    pass
                #else:
                #    pass
                del envirDesc
                #envirDesc = dataIdInfo.xpath(f"./envirDesc")[0]
                # print(f"Set envirDesc to TRUE")
                #envirDesc.set("Sync", "TRUE")
                #del envirDesc, dataIdInfo

                # ######################################################################
                # Resource Title
                # ######################################################################

                # idCitation sub-section
                idCitation  = tree.xpath(f"./dataIdInfo/idCitation")[0]
                resTitle = idCitation.xpath(f"./resTitle")
                if len(resTitle) == 0:
                    #print(f"Inserting resTitle {idCitation_dict['resTitle']}")
                    _xml = f"<resTitle>{dataset_name}</resTitle>"
                    _root = etree.XML(_xml)
                    position = idCitation_dict['resTitle']
                    idCitation.insert(position, _root)
                    del position, _root, _xml
                elif len(resTitle) == 1:
                    #print(f"Updating resTitle if needed at index: {idCitation.index(idCitation.xpath(f'./resTitle')[0])}")
                    if dataset_name not in resTitle[0].text:
                        new_resTitle = resTitle[0].text + ". " + dataset_name
                        resTitle[0].text = new_resTitle
                        idCitation.insert(0, resTitle[0])
                        del new_resTitle
                    else:
                        pass
                elif len(resTitle) > 1:
                    print(f"HEADSUP!! there are {len(resTitle)} resTitle elements")
                    #print(len(resTitle))
                    #print(resTitle)
                    #print(resTitle[-1])
                    #for res_title in resTitle:
                    #    print(f"Removing resTitle at index: {idCitation.index(idCitation.xpath(f'./resTitle')[0])}")
                    #    idCitation.remove(resTitle[-1])

                else:
                    pass
                #print(etree.tostring(idCitation, encoding="utf-8", pretty_print=True).decode())
                del resTitle

                # ######################################################################
                # Resource Alternate Title
                # ######################################################################

                # idCitation sub-section
                idCitation  = tree.xpath(f"./dataIdInfo/idCitation")[0]
                resAltTitle = idCitation.xpath(f"./resAltTitle")
                if len(resAltTitle) == 0:
                    _xml = f"<resAltTitle>{dataset_name.replace('_', ' ')}</resAltTitle>"
                    _root = etree.XML(_xml)
                    position = idCitation_dict['resAltTitle']
                    idCitation.insert(position, _root)
                    del position, _root, _xml
                elif len(resAltTitle) == 1:
                    position = idCitation_dict['resAltTitle']
                    #print(f"Updating resAltTitle if needed {position}")
                    resAltTitle[0].text = f"{dataset_name.replace('_', ' ')}"
                    if dataset_name not in resAltTitle[0].text:
                        new_resAltTitle = resAltTitle[0].text + ". " + dataset_name
                        resAltTitle[0].text = new_resAltTitle
                        idCitation.insert(idCitation_dict['resAltTitle'], resAltTitle[0])
                        del new_resAltTitle
                    else:
                        pass
                    del position
                elif len(resAltTitle) > 1:
                    print(f"May need to delete: {len(resAltTitle)} resAltTitle")
                else:
                    pass
                #print(etree.tostring(idCitation, encoding="utf-8", pretty_print=True).decode())
                del resAltTitle

                # ######################################################################
                # Collective Title
                # ######################################################################

                collTitle = idCitation.xpath(f"./collTitle")
                if len(collTitle) == 0:
                    _xml = f"<collTitle>NMFS DisMAP 2024</collTitle>"
                    _root = etree.XML(_xml)
                    position = idCitation_dict['collTitle']
                    idCitation.insert(position, _root)
                    del position, _root, _xml
                elif len(collTitle) == 1:
                    position = idCitation_dict['collTitle']
                    #print(f"Updating collTitle if needed {position}")
                    if 'NMFS DisMAP 2024' not in collTitle[0].text:
                        new_rescollTitle = collTitle[0].text + ". " + 'NMFS DisMAP 2024'
                        collTitle[0].text = new_rescollTitle
                        del new_rescollTitle
                    else:
                        pass
                    del position
                elif len(collTitle) > 1:
                    print(f"May need to delete: {len(collTitle)} collTitle")

                else:
                    pass
                #print(etree.tostring(idCitation, encoding="utf-8", pretty_print=True).decode())
                del collTitle

                # ######################################################################
                # Presentation form
                # ######################################################################

                # presForm sub-section
                presForm  = idCitation.xpath(f"./presForm")[0]
                fgdcGeoform = presForm.xpath(f"./fgdcGeoform")
                if len(fgdcGeoform) == 0:
                    position = idCitation_dict['fgdcGeoform']
                    #print(f"Inserting fgdcGeoform at {position}")
                    element = etree.SubElement(presForm, "fgdcGeoform")
                    element.text = 'vector digital data'
                    del element, position
                elif len(fgdcGeoform) == 1:
                    position = idCitation_dict['fgdcGeoform']
                    #print(f"Updating fgdcGeoform if needed {position}")
                    fgdcGeoform[0].text = 'vector digital data'
                    del position
                elif len(fgdcGeoform) > 1:
                    print(f"May need to delete: {len(fgdcGeoform)} fgdcGeoform")
                else:
                    pass
                #print(etree.tostring(idCitation, encoding="utf-8", pretty_print=True).decode())
                del fgdcGeoform, presForm

                # ######################################################################
                # Publication Date
                # ######################################################################

                # presForm sub-section
                date  = idCitation.xpath(f"./date")
                if len(date) == 0:
                    position = idCitation_dict['date']
                    #print(f"Inserting date at position: {position}")
                    element = etree.SubElement(idCitation, "date")
                    createDate = etree.SubElement(element, "createDate")
                    createDate.text = "2025-01-01T00:00:00"
                    pubDate = etree.SubElement(element, "pubDate")
                    pubDate.text = "2025-01-01T00:00:00"
                    revisedDate = etree.SubElement(element, "revisedDate")
                    revisedDate.text = "2025-01-01T00:00:00"
                    idCitation.insert(position, element)
                    del element, createDate, pubDate, revisedDate, position
                elif len(date) == 1:
                    #print(f"Updating date if needed at position: {idCitation.index(date[0])}")
                    createDate = date[0].xpath(f"./createDate")
                    if len(createDate) == 0:
                        #print(f"\tInserting createDate at position: {idCitation.index(idCitation.xpath(f'./date')[0])}")
                        createDate = etree.SubElement(date[0], "createDate")
                        createDate.text = "2025-01-01T00:00:00"
                        date.append(createDate)
                    elif len(createDate) == 1:
                        #print(f"Updating createDate if needed  at position: {date[0].index(date[0].xpath(f'./createDate')[0])}")
                        createDate[0].text = "2025-01-01T00:00:00"
                    elif len(createDate) > 1:
                        #print(f"Removing {len(createDate)-1} createDate elements")
                        for i in range(1, len(createDate)):
                            date[0].remove(createDate[i])
                            i+=1
                            del i
                    else:
                        pass
                    del createDate
                    pubDate = date[0].xpath(f"./pubDate")
                    if len(pubDate) == 0:
                        #print(f"\tInserting pubDate at position: {idCitation.index(idCitation.xpath(f'./date')[0])}")
                        pubDate = etree.SubElement(date[0], "pubDate")
                        pubDate.text = "2025-01-01T00:00:00"
                        date.append(pubDate)
                    elif len(pubDate) == 1:
                        #print(f"Updating pubDate if needed  at position: {date[0].index(date[0].xpath(f'./pubDate')[0])}")
                        pubDate[0].text = "2025-01-01T00:00:00"
                    elif len(pubDate) > 1:
                        #print(f"Removing {len(pubDate)-1} pubDate elements")
                        for i in range(1, len(pubDate)):
                            date[0].remove(pubDate[i])
                            i+=1
                            del i
                    else:
                        pass
                    del pubDate
                    revisedDate = date[0].xpath(f"./revisedDate")
                    if len(revisedDate) == 0:
                        #print(f"\tInserting revisedDate at position: {idCitation.index(idCitation.xpath(f'./date')[0])}")
                        revisedDate = etree.SubElement(date[0], "revisedDate")
                        revisedDate.text = "2025-01-01T00:00:00"
                        date.append(revisedDate)
                    elif len(revisedDate) == 1:
                        #print(f"Updating revisedDate if needed  at position: {date[0].index(date[0].xpath(f'./revisedDate')[0])}")
                        revisedDate[0].text = "2025-01-01T00:00:00"
                    elif len(revisedDate) > 1:
                        #print(f"Removing {len(revisedDate)-1} revisedDate elements")
                        for i in range(1, len(revisedDate)):
                            date[0].remove(revisedDate[i])
                            i+=1
                            del i
                    else:
                        pass
                    del revisedDate

                    idCitation.insert(4, date[0])

                elif len(date) > 1:
                    # May not get here
                    print(f"May needed to be deleted {len(date)} date")
                else:
                    pass
                #print(etree.tostring(idCitation, encoding="utf-8", pretty_print=True).decode())
                del date

                del idCitation

##                # ######################################################################
##                # Citation Responsiable Party
##                # ######################################################################
##
##                citRespParty  = idCitation.xpath(f"./citRespParty")
##                xml = '''<citRespParty>
##                            <editorSource>extermal</editorSource>
##                            <editorDigest>9cc0fe80de5687cc4d79f50f3a254f2c3ceb08ce</editorDigest>
##                            <rpIndName>Nikki Wildart</rpIndName>
##                            <rpOrgName>Office of Protected Resources, National Marine Fisheries Service</rpOrgName>
##                            <rpPosName>Biologist</rpPosName>
##                            <rpCntInfo>
##                                <cntAddress addressType="both">
##                                    <delPoint>1315 East West Highway</delPoint>
##                                    <city>Silver Spring</city>
##                                    <adminArea>MD</adminArea>
##                                    <postCode>20910-3282</postCode>
##                                    <eMailAdd>nikki.wildart@noaa.gov</eMailAdd>
##                                    <country>US</country>
##                                </cntAddress>
##                                <cntPhone>
##                                    <voiceNum tddtty="">(301) 427-8443</voiceNum>
##                                    <faxNum>(301) 427-8443</faxNum>
##                                </cntPhone>
##                                <cntHours>0700 - 1800 EST/EDT</cntHours>
##                                <cntOnlineRes>
##                                    <linkage>https://www.fisheries.noaa.gov/about/office-protected-resources</linkage>
##                                    <protocol>REST Service</protocol>
##                                    <orName>Fisheries OPR</orName>
##                                    <orDesc>NOAA Fisheries Office of Science and Technology</orDesc>
##                                    <orFunct>
##                                        <OnFunctCd value="002"></OnFunctCd>
##                                    </orFunct>
##                                </cntOnlineRes>
##                            </rpCntInfo>
##                            <editorSave>True</editorSave>
##                            <displayName>Nikki Wildart</displayName>
##                            <role>
##                                <RoleCd value="002"></RoleCd>
##                            </role>
##                        </citRespParty>'''
##
##                # Create an XML string
##                citRespParty_root = etree.XML(_xml)
##                citRespParty_email = citRespParty_root.xpath(f".//eMailAdd")[0].text
##
##                if len(citRespParty) == 0:
##                    position = idCitation_dict['citRespParty']
##                    #print("Inserting citRespParty at position: {position}")
##                    idCitation.insert(position, citRespParty_root)
##                    del position
##                elif len(citRespParty) == 1:
##                    position = idCitation_dict['citRespParty']
##                    #print(f"Updating citRespParty if needed at position: {position}")
##                    idCitation.insert(position, citRespParty[0])
##                    del position
##                    # Get email address from citRespParty[0]
##                    cit_resp_party_email = citRespParty[0].xpath(f".//eMailAdd")[0].text
##                    if cit_resp_party_email:
##                        #print(f"\tFound {cit_resp_party_email}")
##                        position = idCitation.index(citRespParty[0])
##                        if cit_resp_party_email != citRespParty_email:
##                            #print("\t\tInserting an additional citRespParty")
##                            idCitation.insert(position+1, citRespParty_root)
##                        else:
##                            pass
##                            #print("\t\tcitRespParty update complete")
##                        del position
##                    else:
##                        pass
##                    del cit_resp_party_email
##                elif len(citRespParty) > 1:
##                    #print(f"{len(citRespParty)} citRespParty")
##                    #print("does it have the same email and the new contact?")
##                    cit_resp_party_emails = list()
##                    for cit_resp_party in citRespParty:
##                        if len(idCitation.xpath(f"./citRespParty/rpCntInfo/cntAddress/eMailAdd")) > 0:
##                            cit_resp_party_email = idCitation.xpath(f"./citRespParty/rpCntInfo/cntAddress/eMailAdd")[0]
##                            #print(f"\tFound: {cit_resp_party_email.text}")
##                            if cit_resp_party_email not in cit_resp_party_emails:
##                                #print(f"\t{cit_resp_party_email.text} not in email list")
##                                cit_resp_party_emails.append(cit_resp_party_email)
##                            elif cit_resp_party_email in cit_resp_party_emails:
##                                # Remove the element
##                                if cit_resp_party is not None:
##                                    #print(f"\tRemoving {cit_resp_party_email.text}")
##                                    idCitation.remove(cit_resp_party)
##                                else:
##                                    pass
##                            else:
##                                pass
##                            del cit_resp_party_email
##                            #position = idCitation.index(cit_resp_party)
##                        else:
##                            pass
##                        del cit_resp_party
##                    del cit_resp_party_emails
##                else:
##                    pass
##                del citRespParty_root, citRespParty_email
##                del idCitation_dict
##
##                #print(etree.tostring(idCitation, encoding="utf-8", pretty_print=True).decode())
##                del xml, citRespParty
##                del idCitation

                # ######################################################################
                # Topics
                # ######################################################################

                dataIdInfo = tree.xpath(f"./dataIdInfo")[0]
                tpCat      = dataIdInfo.xpath(f"./tpCat")
                if len(tpCat) == 0:
                    position = dataIdInfo_dict['tpCat']
                    #print(f"Inserting tpCat at {position}")
                    for key in tpCat_dict:
                        _xml = tpCat_dict[key]
                        _root = etree.XML(_xml)
                        dataIdInfo.insert(position, _root)
                        position+=1
                        del _root, _xml, key
                    del position

                #elif len(tpCat) == 1:
                #    position = dataIdInfo_dict['tpCat']
                #    #print(f"Updating tpCat if needed at position: {position}")
                #    dataIdInfo.insert(position, tpCat[0])
                elif len(tpCat) >= 1:
                    for i, key in enumerate(tpCat):
                        position = dataIdInfo_dict['tpCat']
                        if int(dataIdInfo.index(key)) not in range(position, position + len(tpCat_dict)):
                            #print(f"delete: {key.tag}")
                            dataIdInfo.remove(key)
                        del position
                        del i, key

                else:
                    pass

                #print(etree.tostring(dataIdInfo, encoding="utf-8", pretty_print=True).decode())
                del tpCat
                del dataIdInfo

                # ######################################################################
                #               ###--->>> dataIdInfo section End <<<---###
                # ######################################################################

                # ######################################################################
                #               ###--->>> mdContact section Start <<<---###
                # ######################################################################
                mdContact = tree.xpath(f"./mdContact")

                email_address = contacts["mdContact"]["eMailAdd"]
                user_name = contacts["mdContact"]["rpIndName"]
                #print(user_name, email_address)

                new_contact = None

                new_contact_root = contacts_xml_root.xpath(f".//eMailAdd[text()='{email_address}']/ancestor::contact/rpIndName[text()='{user_name}']/ancestor::contact/editorSave[text()='True']/..")
                if not isinstance(new_contact_root, type(None)) and len(new_contact_root) == 0:
                    print("There has been a mistake")
                elif not isinstance(new_contact_root, type(None)) and len(new_contact_root) == 1:
                    #print(etree.tostring(new_contact_root[0], encoding="utf-8",  method='xml', pretty_print=True).decode())
                    #print(f"\tInserting Role into new contact")
                    new_contact = copy.deepcopy(new_contact_root[0])
                    new_contact.tag = "mdContact"
                    _xml = etree.XML('<role><RoleCd value="011"/></role>')
                    # Append element
                    new_contact.append(_xml)
                    #print(etree.tostring(new_contact, encoding="utf-8",  method='xml', pretty_print=True).decode())
                    del _xml
                elif not isinstance(new_contact_root, type(None)) and len(new_contact_root) > 1:
                    print(f"\tFound too many contacts")
                else:
                    pass

                #print(etree.tostring(new_contact, encoding="utf-8",  method='xml', pretty_print=True).decode())

                if len(mdContact) == 0:
                    print(f"\tInserting 'mdContact' at position: {root_dict['mdContact']}")
                    position = root_dict['mdContact']
                    root.insert(position, new_contact)
                    del position
                elif len(mdContact) == 1:
                    print(f"\tUpdating '{mdContact[0].tag}' if needed at position: {root_dict['mdContact']}")
                    position = root_dict['mdContact']
                    root.replace(mdContact[0], new_contact)
                    del position
                elif len(mdContact) > 1:
                    # if it is multiples, is that ok or not. eainfo has multiples, topic does, contacts
                    print(f"\tRemoving {len(mdContact)-1} mdContact elements")
                    for i in range(1, len(mdContact)):
                        root.remove(mdContact[i])
                        i+=1
                        del i
                else:
                    pass
                #print(etree.tostring(idCitation, encoding="utf-8", pretty_print=True).decode())

                del new_contact
                del new_contact_root
                del user_name, email_address
                del mdContact

                #del mdContact_email, mdContact_root, mdContact
           #
           #        elif len(citRespParty) == 1:
           #            print(f"Updating citRespParty if needed at position: {idCitation.index(citRespParty[0])}")
           #            position = 5
           #            idCitation.insert(position, citRespParty[0])
           #            # Get email address from citRespParty[0]
           #            cit_resp_party_email = citRespParty[0].xpath(f".//eMailAdd")[0].text
           #            if cit_resp_party_email:
           #                print(f"\tFound {cit_resp_party_email}")
           #                position = idCitation.index(citRespParty[0])
           #                if cit_resp_party_email != new_cit_resp_party_email:
           #                    print("\t\tInserting an additional citRespParty")
           #                    idCitation.insert(position+1, new_cit_resp_party_root)
           #                else:
           #                    print("\t\tcitRespParty update complete")
           #            else:
           #                pass
           #            del cit_resp_party_email
           #            del position
           #        elif len(citRespParty) > 1:
           #            print(f"{len(citRespParty)} citRespParty")
           #            print("does it have the same email and the new contact?")
           #            cit_resp_party_emails = list()
           #            for cit_resp_party in citRespParty:
           #                if len(idCitation.xpath(f"./citRespParty/rpCntInfo/cntAddress/eMailAdd")) > 0:
           #                    cit_resp_party_email = idCitation.xpath(f"./citRespParty/rpCntInfo/cntAddress/eMailAdd")[0]
           #                    print(f"\tFound: {cit_resp_party_email.text}")
           #                    if cit_resp_party_email not in cit_resp_party_emails:
           #                        print(f"\t{cit_resp_party_email.text} not in email list")
           #                        cit_resp_party_emails.append(cit_resp_party_email)
           #                    elif cit_resp_party_email in cit_resp_party_emails:
           #                        # Remove the element
           #                        if cit_resp_party is not None:
           #                            print(f"\tRemoving {cit_resp_party_email.text}")
           #                            idCitation.remove(cit_resp_party)
           #                        else:
           #                            pass
           #                    else:
           #                        pass
           #                    del cit_resp_party_email
           #                    #position = idCitation.index(cit_resp_party)
           #                else:
           #                    pass
           #                del cit_resp_party
           #            del cit_resp_party_emails
           #        else:
           #            pass
           #        del new_cit_resp_party_email, new_cit_resp_party_root
           #        #print(etree.tostring(idCitation, encoding="utf-8", pretty_print=True).decode())
           #        del xml, citRespParty

                # #######################################################################
                #               ###--->>> mdContact section End <<<---###
                # #######################################################################

                mdFileID = tree.xpath(f"./mdFileID")
                if len(mdFileID) == 0:
                    #print(f"Inserting 'mdFileID' at position: {root_dict['mdFileID']}")
                    _xml = '<mdFileID>gov.noaa.nmfs.inport:</mdFileID>'
                    _root = etree.XML(_xml)
                    position = root_dict['mdFileID']
                    root.insert(position, _root)
                    del position, _root, _xml
                elif len(mdFileID) == 1:
                    #print(f"Updating '{mdFileID[0].tag}' if needed at position: {root.index(root.xpath(f'./mdFileID')[0])}")
                    position = root_dict['mdFileID']
                    root.insert(position, mdFileID[0])
                    del position
                elif len(mdFileID) > 1:
                    # if it is multiples, is that ok or not. eainfo has multiples, topic does, contacts
                    print(f"Removing {len(mdFileID)-1} mdFileID elements")
                    for i in range(1, len(mdFileID)):
                        #root.remove(mdFileID[i])
                        i+=1
                        del i
                else:
                    pass
                del mdFileID

                mdMaint = tree.xpath(f"./mdMaint")
                if len(mdMaint) == 0:
                    #print(f"Inserting 'mdMaint' at position: {root_dict['mdMaint']}")
                    _xml = '<mdMaint><maintFreq><MaintFreqCd value="009"></MaintFreqCd></maintFreq></mdMaint>'
                    _root = etree.XML(_xml)
                    position = root_dict['mdMaint']
                    root.insert(position, _root)
                    del position, _root, _xml
                elif len(mdMaint) == 1:
                    #print(f"Updating '{mdMaint[0].tag}' if needed at position: {root.index(root.xpath(f'./{mdMaint[0].tag}')[0])}")
                    position = root_dict['mdMaint']
                    root.insert(position, mdMaint[0])
                    del position
                elif len(mdLang) > 1:
                    # if it is multiples, is that ok or not. eainfo has multiples, topic does, contacts
                    print(f"Removing {len(mdMaint)-1} mdMaint elements")
                    for i in range(1, len(mdMaint)):
                        root.remove(mdMaint[i])
                        i+=1
                        del i
                else:
                    pass
                del mdMaint

                # #######################################################################
                #               ###--->>> metadata detail section End <<<---###
                # #######################################################################

                # #######################################################################
                #               ###--->>> dqInfo section Start <<<---###
                # #######################################################################
                _xml = '''<dqInfo>
                            <dqScope xmlns="">
                                <scpLvl>
                                    <ScopeCd value="005"></ScopeCd>
                                </scpLvl>
                                <scpLvlDesc xmlns="">
                                    <datasetSet Sync="TRUE"></datasetSet>
                                </scpLvlDesc>
                            </dqScope>
                            <report type="DQConcConsis" dimension="horizontal">
                                <measDesc>Based on a review from species' experts, we determined that all necessary features were included in the species' range file.</measDesc>
                            </report>
                            <report type="DQCompOm" dimension="horizontal">
                                <measDesc>Based on a review from species' experts, we determined that all necessary features were included in the species' range file.</measDesc>
                            </report>
                            <dataLineage>
                                <statement></statement>
                                <dataSource type="">
                                    <srcDesc></srcDesc>
                                    <srcCitatn>
                                        <resTitle></resTitle>
                                        <date>
                                            <createDate></createDate>
                                        </date>
                                    </srcCitatn>
                                </dataSource>
                                <prcStep>
                                    <stepDesc>Metadata Update</stepDesc>
                                    <stepProc>
                                        <editorSource>extermal</editorSource>
                                        <editorDigest></editorDigest>
                                        <rpIndName></rpIndName>
                                        <rpOrgName></rpOrgName>
                                        <rpPosName></rpPosName>
                                        <rpCntInfo>
                                            <cntAddress addressType="both">
                                                <delPoint></delPoint>
                                                <city></city>
                                                <adminArea></adminArea>
                                                <postCode></postCode>
                                                <eMailAdd></eMailAdd>
                                                <country>US</country>
                                            </cntAddress>
                                            <cntPhone>
                                                <voiceNum tddtty=""></voiceNum>
                                                <faxNum></faxNum>
                                            </cntPhone>
                                            <cntHours>0700 - 1800 EST/EDT</cntHours>
                                            <cntOnlineRes>
                                                <linkage></linkage>
                                                <protocol>REST Service</protocol>
                                                <orName>Fisheries</orName>
                                                <orDesc></orDesc>
                                                <orFunct>
                                                    <OnFunctCd value="002"></OnFunctCd>
                                                </orFunct>
                                            </cntOnlineRes>
                                        </rpCntInfo>
                                        <editorSave>True</editorSave>
                                        <displayName></displayName>
                                        <role>
                                            <RoleCd value="009"></RoleCd>
                                        </role>
                                    </stepProc>
                                    <stepDateTm></stepDateTm>
                                </prcStep>
                            </dataLineage>
                        </dqInfo>'''
                # Create an XML string
                dqInfo_root = etree.XML(_xml)
                del _xml

                dqInfo = tree.xpath(f"./dqInfo")
                if len(dqInfo) == 0:
                    #print(f"Inserting 'dqInfo' at position: {root_dict['dqInfo']}")
                    position = root_dict['dqInfo']
                    root.insert(position, dqInfo_root)
                    del position
                elif len(dqInfo) == 1:
                    pass
                    #print(f"Updating '{dqInfo[0].tag}' if needed at position: {root_dict['dqInfo']}")
                    #position = root_dict['dqInfo']
                    #root.replace(dqInfo[0], dqInfo_root)
                    #del position
                elif len(dqInfo) > 1:
                    # if it is multiples, is that ok or not. eainfo has multiples, topic does, contacts
                    #print(f"Removing {len(dqInfo)-1} dqInfo elements")
                    for i in range(1, len(dqInfo)):
                        #root.remove(dqInfo[i])
                        i+=1
                        del i
                else:
                    pass
                del dqInfo
                del dqInfo_root

                dqInfo  = tree.xpath(f"./dqInfo")
                dqScope = dqInfo[0].xpath(f"./dqScope")
                if len(dqScope) == 0:
                    #print(f"Inserting 'dqScope' at position: {dqInfo_dict['dqScope']}")
                    _xml = '''<dqScope xmlns=""><scpLvl><ScopeCd value="005"></ScopeCd></scpLvl><scpLvlDesc xmlns=""><datasetSet Sync="TRUE">Feature Class</datasetSet></scpLvlDesc></dqScope>'''
                    _root = etree.XML(_xml)
                    position = dqInfo_dict['dqScope']
                    dqInfo[0].insert(position, _root)
                    del position, _root, _xml
                elif len(dqScope) == 1:
                    #print(f"Updating '{dqScope[0].tag}' if needed at position: {dqInfo_dict['dqScope']}")
                    #_xml = '''<dqScope xmlns=""><scpLvl><ScopeCd value="005"></ScopeCd></scpLvl><scpLvlDesc xmlns=""><datasetSet>Feature Class</datasetSet></scpLvlDesc></dqScope>'''
                    #_root = etree.XML(_xml)
                    #position = dqInfo_dict["dqScope"]
                    #dqInfo[0].insert(position, root)
                    #del position, _root, _xml
                    position = dqInfo_dict["dqScope"]
                    dqInfo[0].insert(position, dqScope[0])
                    del position
                elif len(dqScope) > 1:
                    # if it is multiples, is that ok or not. eainfo has multiples, topic does, contacts
                    #print(f"Removing {len(dqScope)-1} dqScope elements")
                    for i in range(1, len(dqScope)):
                        dqInfo[0].remove(dqScope[i])
                        i+=1
                        del i
                else:
                    pass
                #etree.indent(dqInfo[0], space="  ")
                #print(etree.tostring(dqInfo[0], xml_declaration=True, encoding="utf-8").decode())
                del dqScope, dqInfo

                dqInfo  = tree.xpath(f"./dqInfo")
                report = dqInfo[0].xpath(f"./report")
                if len(report) == 0:
                    #print(f"Inserting 'report' at position: {dqInfo_dict['report']}")
                    _xml = '''<report type="DQConcConsis" dimension="horizontal">
                                <measDesc>Based on a review from species' experts, we determined that all necessary features were included in the species' range file.</measDesc>
                             </report>'''
                    _root = etree.XML(_xml)
                    position = dqInfo_dict['report']
                    dqInfo[0].insert(position, _root)
                    del position, _root, _xml

                    #print(f"Inserting 'report' at position: {dqInfo_dict['report']+1}")
                    _xml = '''<report type="DQCompOm" dimension="horizontal">
                                <measDesc>Based on a review from species' experts, we determined that all necessary features were included in the species' range file.</measDesc>
                             </report>'''
                    _root = etree.XML(_xml)
                    position = dqInfo_dict['report']
                    dqInfo[0].insert(position+1, _root)
                    del position, _root, _xml

                elif len(report) == 1:
                    #print(f"Updating '{report[0].tag}' if needed at position: {dqInfo_dict['report']}")
                    _report = dqInfo[0].xpath(f"./report[@type='DQConcConsis']")
                    if len(_report) == 1:
                        _xml = '''<report type="DQConcConsis" dimension="horizontal">
                                    <measDesc>Based on a review from species' experts, we determined that all necessary features were included in the species' range file.</measDesc>
                                 </report>'''
                        _root = etree.XML(_xml)
                        dqInfo[0].replace(_report[0], _root)
                        del _root, _xml

                        _xml = '''<report type="DQCompOm" dimension="horizontal">
                                    <measDesc>Based on a review from species' experts, we determined that all necessary features were included in the species' range file.</measDesc>
                                 </report>'''
                        _root = etree.XML(_xml)
                        position = dqInfo_dict["report"]+1
                        dqInfo[0].insert(position, _root)
                        del position, _root, _xml

                    elif len(_report) > 1:
                        dqInfo[0].remove(_report[-1])
                    del _report

                    _report = dqInfo[0].xpath(f"./report[@type='DQCompOm']")
                    if len(_report) == 1:
                        _xml = '''<report type="DQCompOm" dimension="horizontal">
                                    <measDesc>Based on a review from species' experts, we determined that all necessary features were included in the species' range file.</measDesc>
                                 </report>'''
                        _root = etree.XML(_xml)
                        dqInfo[0].replace(_report[0], _root)
                        del _root, _xml

                        _xml = '''<report type="DQConcConsis" dimension="horizontal">
                                    <measDesc>Based on a review from species' experts, we determined that all necessary features were included in the species' range file.</measDesc>
                                 </report>'''
                        _root = etree.XML(_xml)
                        position = dqInfo_dict["report"]
                        dqInfo[0].insert(position, _root)
                        del position, _root, _xml

                    elif len(_report) > 1:
                        dqInfo[0].remove(_report[-1])
                    del _report

                    #root = etree.XML(_xml)
                    #position = dqInfo_dict["report"]
                    #dqInfo[0].insert(position, root)
                    #del position, _root, _xml
                    #position = dqInfo_dict["report"]
                    #dqInfo[0].insert(position, report[0])
                    #del position

                elif len(report) > 1:
                    _report = dqInfo[0].xpath(f"./report[@type='DQConcConsis']")
                    if len(_report) > 1:
                        dqInfo[0].remove(_report[-1])
                    del _report

                    _report = dqInfo[0].xpath(f"./report[@type='DQCompOm']")
                    if len(_report) > 1:
                        dqInfo[0].remove(_report[-1])
                    del _report

                    # if it is multiples, is that ok or not. eainfo has multiples, topic does, contacts
                    #print(f"Removing {len(report)-1} report elements")
                    #for i in range(1, len(report)):
                    #    dqInfo[0].remove(report[i])
                    #    i+=1
                    #    del i
                else:
                    pass
                #etree.indent(dqInfo[0], space="  ")
                #print(etree.tostring(dqInfo[0], xml_declaration=True, encoding="utf-8").decode())
                del report, dqInfo

                dqInfo  = tree.xpath(f"./dqInfo")
                dataLineage = dqInfo[0].xpath(f"./dataLineage")
                if len(dataLineage) == 0:
                    print(f"Inserting 'dataLineage' at position: {dqInfo_dict['dataLineage']}")
                    _xml = '''<dataLineage>
                                <statement></statement>
                                <dataSource type="">
                                    <srcDesc></srcDesc>
                                    <srcCitatn>
                                        <resTitle></resTitle>
                                        <date>
                                            <createDate></createDate>
                                        </date>
                                    </srcCitatn>
                                </dataSource>
                                <prcStep>
                                    <stepDesc></stepDesc>
                                    <stepProc>
                                        <editorSource>extermal</editorSource>
                                        <editorDigest></editorDigest>
                                        <rpIndName></rpIndName>
                                        <rpOrgName></rpOrgName>
                                        <rpPosName></rpPosName>
                                        <rpCntInfo>
                                            <cntAddress addressType="both">
                                                <delPoint></delPoint>
                                                <city></city>
                                                <adminArea></adminArea>
                                                <postCode></postCode>
                                                <eMailAdd></eMailAdd>
                                                <country></country>
                                            </cntAddress>
                                            <cntPhone>
                                                <voiceNum tddtty=""></voiceNum>
                                                <faxNum></faxNum>
                                            </cntPhone>
                                            <cntHours></cntHours>
                                            <cntOnlineRes>
                                                <linkage></linkage>
                                                <protocol>REST Service</protocol>
                                                <orName></orName>
                                                <orDesc></orDesc>
                                                <orFunct>
                                                    <OnFunctCd value="002"></OnFunctCd>
                                                </orFunct>
                                            </cntOnlineRes>
                                        </rpCntInfo>
                                        <editorSave>True</editorSave>
                                        <displayName></displayName>
                                        <role>
                                            <RoleCd value="009"></RoleCd>
                                        </role>
                                    </stepProc>
                                    <stepDateTm></stepDateTm>
                                </prcStep>
                            </dataLineage>'''
                    _root = etree.XML(_xml)
                    position = dqInfo_dict['dataLineage']
                    dqInfo[0].insert(position, _root)
                    del position, _root, _xml
                elif len(dataLineage) == 1:
                    position = dqInfo_dict["dataLineage"]
                    dqInfo[0].insert(position, dataLineage[0])
                    del position
                elif len(dataLineage) > 1:
                    # if it is multiples, is that ok or not. eainfo has multiples, topic does, contacts
                    #print(f"Removing {len(dataLineage)-1} dataLineage elements")
                    for i in range(1, len(dataLineage)):
                        dqInfo[0].remove(dataLineage[i])
                        i+=1
                        del i
                else:
                    pass
                #etree.indent(dqInfo[0], space="  ")
                #print(etree.tostring(dqInfo[0], xml_declaration=True, encoding="utf-8").decode())
                del dataLineage, dqInfo

                # #######################################################################
                #               ###--->>> dqInfo section End <<<---###
                # #######################################################################

                # #######################################################################
                #               ###--->>> distInfo section Start <<<---###
                # #######################################################################
                _xml = '''<distInfo>
                            <distFormat>
                                <formatName Sync="TRUE">File Geodatabase Feature Class</formatName>
                                <formatVer>NMFS ESA Range Geodatabase 2024</formatVer>
                                <fileDecmTech>ZIP</fileDecmTech>
                            </distFormat>
                            <distributor>
                                <distorCont>
                                    <editorSource>extermal</editorSource>
                                    <editorDigest></editorDigest>
                                    <rpIndName></rpIndName>
                                    <rpOrgName></rpOrgName>
                                    <rpPosName></rpPosName>
                                    <rpCntInfo>
                                        <cntAddress addressType="both">
                                            <delPoint></delPoint>
                                            <city></city>
                                            <adminArea></adminArea>
                                            <postCode></postCode>
                                            <eMailAdd></eMailAdd>
                                            <country></country>
                                        </cntAddress>
                                        <cntPhone>
                                            <voiceNum tddtty=""></voiceNum>
                                            <faxNum></faxNum>
                                        </cntPhone>
                                        <cntHours></cntHours>
                                        <cntOnlineRes>
                                            <linkage></linkage>
                                            <protocol>REST Service</protocol>
                                            <orName></orName>
                                            <orDesc></orDesc>
                                            <orFunct>
                                                <OnFunctCd value="002"></OnFunctCd>
                                            </orFunct>
                                        </cntOnlineRes>
                                    </rpCntInfo>
                                    <editorSave>True</editorSave>
                                    <displayName></displayName>
                                    <role>
                                        <RoleCd value="005"></RoleCd>
                                    </role>
                                </distorCont>
                            </distributor>
                             <distorTran xmlns="">
                                <onLineSrc xmlns="">
                                   <linkage>https://www.fisheries.noaa.gov/science-and-data</linkage>
                                   <protocol>REST Service</protocol>
                                   <orName>NMFS ESA Range Geodatabase 2024</orName>
                                   <orDesc>File Geodatabase Download</orDesc>
                                   <orFunct>
                                      <OnFunctCd value="001"/>
                                   </orFunct>
                                </onLineSrc>
                                <unitsODist>MB</unitsODist>
                                <transSize>0</transSize>
                             </distorTran>
                             <distorTran xmlns="">
                                <onLineSrc xmlns="">
                                   <linkage>https://services2.arcgis.com/C8EMgrsFcRFL6LrL/arcgis/rest/services/.../FeatureServer</linkage>
                                   <protocol>ArcGIS REST Services</protocol>
                                   <orName>AbaloneBlack_20210712</orName>
                                   <orDesc>AbaloneBlack_20210712 Feature Service</orDesc>
                                   <orFunct>
                                      <OnFunctCd value="002"/>
                                   </orFunct>
                                </onLineSrc>
                             </distorTran>
                        </distInfo>'''
                # Create an XML string
                distInfo_root = etree.XML(_xml)
                del _xml

                distInfo = tree.xpath(f"./distInfo")
                if len(distInfo) == 0:
                    #print(f"Inserting 'distInfo' at position: {root_dict['distInfo']}")
                    position = root_dict['distInfo']
                    #root.insert(position, distInfo_root)
                    del position
                elif len(distInfo) == 1:
                    pass
                    #print(f"Updating '{distInfo[0].tag}' if needed at position: {root_dict['distInfo']}")
                    #position = root_dict['distInfo']
                    #root.replace(distInfo[0], distInfo_root)
                    #del position
                elif len(distInfo) > 1:
                    # if it is multiples, is that ok or not. eainfo has multiples, topic does, contacts
                    #print(f"Removing {len(distInfo)-1} distInfo elements")
                    for i in range(1, len(distInfo)):
                        root.remove(distInfo[i])
                        i+=1
                        del i
                else:
                    pass
                del distInfo_root
                del distInfo

                # #######################################################################
                #               ###--->>> distInfo section End <<<---###
                # #######################################################################

        ##        # #######################################################################
        ##        #               ###--->>> eainfo section Start <<<---###
        ##        # #######################################################################
        ##        eainfo      = tree.xpath(f"./eainfo")
        ##        if len(eainfo) == 0:
        ##            print(f"Inserting 'eainfo' at position: {root_dict['eainfo']}")
        ##            _xml = '<eainfo Sync="TRUE"></eainfo>'
        ##            _root = etree.XML(_xml)
        ##            position = root_dict['eainfo']
        ##            root.insert(position, _root)
        ##            del position, _root, _xml
        ##        elif len(eainfo) == 1:
        ##            print(f"Updating '{eainfo[0].tag}' if needed at position: {root_dict['eainfo']}")
        ##            position = root_dict['eainfo']
        ##            root.insert(position, eainfo[0])
        ##            del position
        ##        elif len(eainfo) > 1:
        ##            # if it is multiples, is that ok or not. eainfo has multiples, topic does, contacts
        ##            print(f"Removing {len(eainfo)-1} eainfo elements")
        ##            for i in range(1, len(eainfo)):
        ##                root.remove(eainfo[i])
        ##                i+=1
        ##                del i
        ##        else:
        ##            pass
        ##        del eainfo
        ##        # ######################################################################
        ##        #               ###--->>> eainfo section End <<<---###
        ##        # ######################################################################

                # ######################################################################
                #               ###--->>> Binary section Start <<<---###
                # ######################################################################
                Binary      = tree.xpath(f"./Binary")
                if len(Binary) == 0:
                    #print(f"Inserting 'Binary' at position: {root_dict['Binary']}")
                    _xml = '<Binary Sync="TRUE"><Thumbnail><Data EsriPropertyType="PictureX"></Data></Thumbnail></Binary>'
                    _root = etree.XML(_xml)
                    position = root_dict['Binary']
                    root.insert(position, _root)
                    del position, _root, _xml
                elif len(Binary) == 1:
                    #print(f"Updating '{Binary[0].tag}' if needed at position: {root_dict['Binary']}")
                    position = root_dict['Binary']
                    root.insert(position, Binary[0])
                    del position
                elif len(Binary) > 1:
                    # if it is multiples, is that ok or not. Binary has multiples, topic does, contacts
                    print(f"Removing {len(Binary)-1} Binary elements")
                    for i in range(1, len(Binary)):
                        #root.remove(Binary[i])
                        i+=1
                        del i
                else:
                    pass
                del Binary
                # ######################################################################
                #               ###--->>> Binary section End <<<---###
                # ######################################################################

        ##        #etree.indent(root, space='    ')
        ##        #etree.dump(root)
        ##
        ##        #etree.indent(root, space="    ")
        ##        #print(etree.tostring(root, xml_declaration=True, encoding="utf-8").decode())



        ##        # Parse the XML
        ##        parser = etree.XMLParser(encoding='UTF-8', remove_blank_text=True)
        ##        dataset_name = os.path.basename(fc_metadata_xml_file).replace(".xml", "")
        ##        tree = etree.parse(fc_metadata_xml_file, parser=parser)
        ##        root = tree.getroot()
        ##        del parser

##                # Parse the XML
##                parser = etree.XMLParser(encoding='UTF-8', remove_blank_text=True)
##                tree = etree.parse(fc_metadata_xml_file, parser=parser)
##                root = tree.getroot()
##                del parser

                dqInfo = tree.xpath(f"./dqInfo")[0]
                for child in dqInfo.xpath("."):
                    child[:] = sorted(child, key=lambda x: dqInfo_dict[x.tag])
                    del child
                del dqInfo

                dataIdInfo = tree.xpath(f"./dataIdInfo")[0]
                for child in dataIdInfo.xpath("."):
                    child[:] = sorted(child, key=lambda x: dataIdInfo_dict[x.tag])
                    del child
                del dataIdInfo

                Esri = tree.xpath(f"./Esri")[0]
                for child in Esri.xpath("."):
                    child[:] = sorted(child, key=lambda x: esri_dict[x.tag])
                    del child
                del Esri

                # Sort the XML
                for child in root.xpath("."):
                    child[:] = sorted(child, key=lambda x: root_dict[x.tag])
                    del child

                #etree.indent(root, space='    ')
                #target_xml_string = etree.tostring(tree, pretty_print=True, method='html', encoding="utf-8", xml_declaration=True).decode()
                #etree.tostring(contacts_xml_root, encoding="utf-8",  method='xml', xml_declaration=True, pretty_print=True).decode()
                #target_xml_string = etree.tostring(tree, encoding="utf-8",  method='xml', xml_declaration=True, pretty_print=True).decode()
                #print(target_xml_string)
                #try:
                #    with open(fc_metadata_xml_file, "w") as f:
                #        f.write(target_xml_string)
                #    del f
                #except:
                #    print(f"The metadata file: {os.path.basename(fc_metadata_xml_file)} can not be overwritten!!")
                #del target_xml_string

                #pretty_format_xml_file(fc_metadata_xml_file)

                etree.indent(root, space='    ')
                dataset_md_xml = etree.tostring(tree, encoding="utf-8",  method='xml', xml_declaration=True, pretty_print=True)
                #print(dataset_md_xml)
                # This allows for sorting
                doc = etree.XML(dataset_md_xml, etree.XMLParser(remove_blank_text=True))
                for parent in doc.xpath('.'): # Search for parent elements
                  parent[:] = sorted(parent,key=lambda x: root_dict[x.tag])
                  del parent
                #print( etree.tostring(doc,pretty_print=True).decode() )
                del doc

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

                del dataset_path, dataset_name, tree, root
            del workspace, datasets
        # Declare Variables
        del root_dict, contact_dict, dqInfo_dict
        del dataIdInfo_dict, tpCat_dict, esri_dict
        del idCitation_dict, RoleCd_dict
        del contacts_xml_root, contacts_xml_tree
        del project_folder, crfs_folder, scratch_folder, workspaces
        #del tree, root, dataset_name
        # Imports
        del etree, StringIO, copy, arcpy, md
        # Function Parameters
        del project_gdb, contacts

    except:
        traceback.print_exc()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function: ##--> '{', '.join(rk)}' <--##"); del rk
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

        arcpy.env.overwriteOutput = True
        arcpy.env.parallelProcessingFactor = "100%"

        project_folder      = rf"{os.path.dirname(project_gdb)}"
        #base_project_folder = rf"{os.path.dirname(project_folder)}"
        #base_project_file   = rf"{base_project_folder}\DisMAP.aprx"

        del project_folder

        # Test if passed workspace exists, if not raise SystemExit
        #if not arcpy.Exists(base_project_file):
        #    print(f"{os.path.basename(base_project_file)} is missing!!")

        # Test if passed workspace exists, if not raise SystemExit
        if not arcpy.Exists(project_gdb):
            print(f"{os.path.basename(project_gdb)} is missing!!")

        Backup = False
        if Backup:
            dismap.backup_gdb(project_gdb)
        del Backup

        try:
            UpdateXmlElements = True
            if UpdateXmlElements:
                contact_dict = {"citRespParty" : {"rpIndName" : "", "eMailAdd" : "tim.haverland@noaa.gov"},
                                "idPoC"        : {"rpIndName" : "Melissa Karp", "eMailAdd" : "melissa.karp@noaa.gov"},
                                "distorCont"   : {"rpIndName" : "Timothy J Haverland", "eMailAdd" : "tim.haverland@noaa.gov"},
                                "mdContact"    : {"rpIndName" : "John F Kennedy", "eMailAdd" : "john.f.kennedy@noaa.gov"},
                                "stepProc"     : [{"rpIndName" : "John F Kennedy", "eMailAdd" : "john.f.kennedy@noaa.gov"},
                                                  {"rpIndName" : "Melissa Karp", "eMailAdd" : "melissa.karp@noaa.gov"}],
                                }

                update_xml_elements(project_gdb=project_gdb, contacts=contact_dict)
                del contact_dict
            else:
                pass
            del UpdateXmlElements

            UpdateExistingContacts = False
            if UpdateExistingContacts:
                update_existing_contacts(project_gdb=project_gdb)
            else:
                pass
            del UpdateExistingContacts

            CreateBasicTemplateXMLFiles = False
            if CreateBasicTemplateXMLFiles:
                create_basic_template_xml_files(project_gdb=project_gdb)
            else:
                pass
            del CreateBasicTemplateXMLFiles

            ImportBasicTemplateXmlFiles = False
            if ImportBasicTemplateXmlFiles:
                import_basic_template_xml_files(project_gdb=project_gdb)
            else:
                pass
            del ImportBasicTemplateXmlFiles

            CreateThumbnails = False
            if CreateThumbnails:
               create_thumbnails(project_gdb=project_gdb)
            else:
                pass
            del CreateThumbnails

            CreateMaps = False
            if CreateMaps:
                create_maps(project_gdb=project_gdb, dataset=rf"{project_gdb}\DisMAP_Regions")
            else:
                pass
            del CreateMaps

            ExportToInportXmlFiles = False
            if ExportToInportXmlFiles:
                export_to_inport_xml_files(project_gdb=project_gdb)
            else:
                pass
            del ExportToInportXmlFiles

        except Exception as e:
            arcpy.AddError(str(e))

        # Declared Varaiables

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

    except Exception:
        pass
    except:
        traceback.print_exc()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function: ##--> '{', '.join(rk)}' <--##"); del rk
        return True
    finally:
        pass

if __name__ == "__main__":
    try:
        # Imports

        # Append the location of this scrip to the System Path
        #sys.path.append(os.path.dirname(__file__))
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))

        base_project_folder = rf"{os.path.dirname(os.path.dirname(__file__))}"
        project_name = "April 1 2023"
        #project_name = "July 1 2024"
        #project_name   = "December 1 2024"
        project_folder = rf"{base_project_folder}\{project_name}"
        project_gdb    = rf"{project_folder}\{project_name}.gdb"

        main(project_gdb=project_gdb)

        # Variables
        del project_gdb, project_name, project_folder, base_project_folder

        # Imports

    except:
        traceback.print_exc()
    else:
        pass
    finally:
        pass
