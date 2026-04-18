"""
Script documentation

- Tool parameters are accessed using arcpy.GetParameter() or
                                     arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or
                                        arcpy.SetParameterAsText()
"""
import os
import sys
import traceback
import inspect

import arcpy


def script_tool(project_gdb=""):
    """Script code goes below"""
    try:
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

        project_folder = os.path.dirname(project_gdb)
        out_data_path = rf"{project_folder}\CSV_Data"

        root_dict = {"Esri"        :  0,
                     "dataIdInfo"  :  1,
                     "dqInfo"      :  2,
                     "distInfo"    :  3,
                     "mdContact"   :  4,
                     "mdLang"      :  5,
                     "mdChar"      :  6,
                     "mdDateSt"    :  7,
                     "mdHrLv"      :  8,
                     "mdHrLvName"  :  9,
                     "mdFileID"    : 10,
                     "mdParentID"  : 11,
                     "mdMaint"     : 12,
                     "refSysInfo"  : 13,
                     "spatRepInfo" : 14,
                     "spdoinfo"    : 15,
                     "spref"       : 16,
                     "contInfo"    : 17,
                     "dataSetFn"   : 18,
                     "eainfo"      : 19,
                     "Binary"      : 20,
                     }

        import json
        json_path = rf"{out_data_path}\root_dict.json"
        # Write to File
        with open(json_path, 'w') as json_file:
            json.dump(root_dict, json_file, indent=4)
        del json_file
        del root_dict
        with open(json_path, "r") as json_file:
            root_dict = json.load(json_file)
        del json_file
        arcpy.AddMessage(root_dict)
        del root_dict
        del json_path
        del json

        esri_dict ={"CreaDate"       : 0,
                    "CreaTime"       : 1,
                    "ArcGISFormat"   : 2,
                    "ArcGISstyle"    : 3,
                    "ArcGISProfile"  : 4,
                    "SyncOnce"       : 5,
                    "DataProperties" : 6,
                        "lineage"      : 0,
                        "itemProps"    :  1,
                            "itemName"       :  0,
                            "imsContentType" : 1,
                        "nativeExtBox" :  2,
                            "westBL"     : 0,
                            "eastBL"     : 1,
                            "southBL"    : 2,
                            "northBL"    : 3,
                            "exTypeCode" : 4,
                        "itemLocation" : 3,
                            "linkage"  : 0,
                            "protocol" : 1,
                        "coordRef"     : 4,
                            "type"    : 0,
                            "geogcsn" : 1,
                            "csUnits" : 2,
                            "projcsn" : 3,
                            "peXml"   : 4,
                    "SyncDate"       :  7,
                    "SyncTime"       :  8,
                    "ModDate"        :  9,
                    "ModTime"        : 10,
                    "scaleRange"     : 11,
                    "minScale"       : 12,
                    "maxScale"       : 13,
                    "locales"        : 14,
                   }

        import json
        json_path = rf"{out_data_path}\esri_dict.json"
        # Write to File
        with open(json_path, 'w') as json_file:
            json.dump(esri_dict, json_file, indent=4)
        del json_file
        del esri_dict
        with open(json_path, "r") as json_file:
            esri_dict = json.load(json_file)
        del json_file
        arcpy.AddMessage(esri_dict)
        del esri_dict
        del json_path
        del json

        dataIdInfo_dict = {"dataIdInfo" : 0,
                            "envirDesc"  :  0,
                            "dataLang"   :  1,
                            "dataChar"   :  2,
                            "idCitation" :  3,
                                "resTitle"     : 0,
                                "resAltTitle"  : 1,
                                "collTitle"    : 2,
                                "date"         : 3,
                                "presForm"     : 4,
                                    "PresFormCd"  : 0,
                                    "fgdcGeoform" : 1,
                                "citRespParty" : 5,
                            "spatRpType" :  4,
                            "dataExt"    :  5,
                                "exDesc"  : 0,
                                "geoEle"  : 1,
                                    "GeoBndBox" : 0,
                                        "exTypeCode" : 0,
                                        "westBL"     : 1,
                                        "eastBL"     : 2,
                                        "northBL"    : 3,
                                        "southBL"    : 4,
                                "tempEle" : 2,
                                    "TempExtent" : 0,
                                        "exTemp" : 0,
                                            "TM_Period"  : 0,
                                                "tmBegin" : 0,
                                                "tmEnd"   : 1,
                                            "TM_Instant" : 1,
                                                "tmPosition" : 0,
                            "searchKeys" :  1,
                            "idPurp"     :  2,
                            "idAbs"      :  3,
                            "idCredit"   :  4,
                            "idStatus"   :  5,
                            "resConst"   :  6,
                            "discKeys"   :  7,
                                "keyword"   : 0,
                                "thesaName" : 1,
                                    "resTitle" : 0,  # noqa: F601
                                    "date"     : 1,  # noqa: F601
                                        "createDate" : 0,
                                        "pubDate"    : 1,
                                        "reviseDate" : 2,
                                    "citOnlineRes" : 2,
                                        "linkage" : 0,
                                        "orFunct" : 1,
                                            "OnFunctCd" : 0,
                                    "thesaLang" : 2,
                                        "languageCode" : 0,
                                        "countryCode"  : 1,
                            "themeKeys"  :  8,  # noqa: F601
                                "keyword"   : 0,  # noqa: F601
                                "thesaName" : 1,  # noqa: F601
                                    "resTitle" : 0,  # noqa: F601
                                    "date"     : 1,  # noqa: F601
                                        "createDate" : 0,  # noqa: F601
                                        "pubDate"    : 1,  # noqa: F601
                                        "reviseDate" : 2,  # noqa: F601
                                    "citOnlineRes" : 2,  # noqa: F601
                                        "linkage" : 0,  # noqa: F601
                                        "orFunct" : 1,  # noqa: F601
                                            "OnFunctCd" : 0,  # noqa: F601
                                    "thesaLang" : 2,  # noqa: F601
                                        "languageCode" : 0,  # noqa: F601
                                        "countryCode"  : 1,  # noqa: F601
                            "placeKeys"  :  9,
                                "keyword"   : 0,  # noqa: F601
                                "thesaName" : 1,  # noqa: F601
                                    "resTitle" : 0,  # noqa: F601
                                    "date"     : 1,  # noqa: F601
                                        "createDate" : 0,  # noqa: F601
                                        "pubDate"    : 1,  # noqa: F601
                                        "reviseDate" : 2,  # noqa: F601
                                    "citOnlineRes" : 2,  # noqa: F601
                                        "linkage" : 0,  # noqa: F601
                                        "orFunct" : 1,  # noqa: F601
                                            "OnFunctCd" : 0,  # noqa: F601
                                    "thesaLang" : 2,  # noqa: F601
                                        "languageCode" : 0,  # noqa: F601
                                        "countryCode"  : 1,  # noqa: F601
                            "tempKeys"   : 10,  # noqa: F601
                                "keyword"   : 0,  # noqa: F601
                                "thesaName" : 1,  # noqa: F601
                                    "resTitle" : 0,  # noqa: F601
                                    "date"     : 1,  # noqa: F601
                                        "createDate" : 0,  # noqa: F601
                                        "pubDate"    : 1,  # noqa: F601
                                        "reviseDate" : 2,  # noqa: F601
                                    "citOnlineRes" : 2,  # noqa: F601
                                        "linkage" : 0,  # noqa: F601
                                        "orFunct" : 1,  # noqa: F601
                                            "OnFunctCd" : 0,  # noqa: F601
                                    "thesaLang" : 2,  # noqa: F601
                                        "languageCode" : 0,  # noqa: F601
                                        "countryCode"  : 1,  # noqa: F601
                            "otherKeys"  : 11,  # noqa: F601
                                "keyword"   : 0,  # noqa: F601
                                "thesaName" : 1,  # noqa: F601
                                    "resTitle" : 0,  # noqa: F601
                                    "date"     : 1,  # noqa: F601
                                        "createDate" : 0,  # noqa: F601
                                        "pubDate"    : 1,  # noqa: F601
                                        "reviseDate" : 2,  # noqa: F601
                                    "citOnlineRes" : 2,  # noqa: F601
                                        "linkage" : 0,  # noqa: F601
                                        "orFunct" : 1,  # noqa: F601
                                            "OnFunctCd" : 0,  # noqa: F601
                                    "thesaLang" : 2,  # noqa: F601
                                        "languageCode" : 0,  # noqa: F601
                                        "countryCode"  : 1,  # noqa: F601
                            "idPoC"      : 11,  # noqa: F601
                            "resMaint"   : 12,  # noqa: F601
                            "tpCat"      : 18,  # noqa: F601
                           }

        import json
        json_path = rf"{out_data_path}\dataIdInfo_dict.json"
        # Write to File
        with open(json_path, 'w') as json_file:
            json.dump(dataIdInfo_dict, json_file, indent=4)
        del json_file
        del dataIdInfo_dict
        with open(json_path, "r") as json_file:
            dataIdInfo_dict = json.load(json_file)
        del json_file
        arcpy.AddMessage(dataIdInfo_dict)
        del dataIdInfo_dict
        del json_path
        del json

        idCitation_dict = {"idCitation" : 0,
                                "resTitle"    : 0,
                                "resAltTitle" : 1,
                                "collTitle"   : 2,
                                "presForm"    : 3,
                                    "PresFormCd"  : 0,
                                    "fgdcGeoform" : 1,
                                "date"        : 4,
                                    "createDate" : 0,
                                    "pubDate"    : 1,
                                    "reviseDate" : 2,
                                "citRespParty"  : 6,
                           }

        import json
        json_path = rf"{out_data_path}\idCitation_dict.json"
        # Write to File
        with open(json_path, 'w') as json_file:
            json.dump(idCitation_dict, json_file, indent=4)
        del json_file
        del idCitation_dict
        with open(json_path, "r") as json_file:
            idCitation_dict = json.load(json_file)
        del json_file
        arcpy.AddMessage(idCitation_dict)
        del idCitation_dict
        del json_path
        del json

        contact_element_order_dict = {"editorSource" : 0, "editorDigest" : 1,"rpIndName"     : 2,
                                      "rpOrgName"    : 3, "rpPosName"    : 4, "rpCntInfo"    : 5,
                                      "cntAddress"   : 0, "delPoint"     : 0, "city"         : 1,
                                      "adminArea"    : 2, "postCode"     : 3, "eMailAdd"     : 4,
                                      "country"      : 5, "cntPhone"     : 1, "voiceNum"     : 0,
                                      "faxNum"       : 1, "cntHours"     : 2, "cntOnlineRes" : 3,
                                      "linkage"      : 0, "protocol"     : 1, "orName"       : 2,
                                      "orDesc"       : 3, "orFunct"      : 4, "OnFunctCd"    : 0,
                                      "editorSave"   : 6, "displayName"  : 7, "role"         : 8,
                                      "RoleCd"       : 0, "srcCitatn"    : 1, "resTitle"     : 0,
                                      "resAltTitle"  : 1, "collTitle"    : 2, "date"         : 10,
                                      "createDate"   : 0, "pubDate"      : 1, "reviseDate"   : 2,
                                      "presForm"     : 3, "PresFormCd"   : 0, "fgdcGeoform"  : 1,
                                      "citRespParty" : 6, "citOnlineRes" : 2,
                                     }

        import json
        json_path = rf"{out_data_path}\contact_element_order_dict.json"
        # Write to File
        with open(json_path, 'w') as json_file:
            json.dump(contact_element_order_dict, json_file, indent=4)
        del json_file
        del contact_element_order_dict
        with open(json_path, "r") as json_file:
            contact_element_order_dict = json.load(json_file)
        del json_file
        arcpy.AddMessage(contact_element_order_dict)
        del contact_element_order_dict
        del json_path
        del json

        dqInfo_dict = { "dqScope"        : 0,
                            "scpLvl"     : 0,
                            "ScopeCd"    : 0,
                            "scpLvlDesc" : 1,
                            "datasetSet" : 0,
                        "report"         : 1,
                            "measDesc"   : 0,
                            "measResult" : 1,
                        "dataLineage"    : 3,
                            "statement"  : 0,
                            "dataSource" : 1,
                                "srcDesc"    : 0,
                                "srcCitatn"  : 1,
                                    "resTitle"     : 0,
                                    "resAltTitle" : 1,
                                    "collTitle"  : 2,
                                "citOnlineRes" : 2,
                                        "linkage"  : 0,
                                        "protocol" : 1,
                                        "orName"   : 2,
                                        "orDesc"   : 3,
                                        "orFunct" : 4,
                                            "OnFunctCd" : 0,
                                "date"        : 3,
                                    "createDate" : 0,
                                    "pubDate"    : 1,
                                    "reviseDate" : 2,
                                "otherCitDet" : 4,
                                "presForm"    : 5,
                                    "PresFormCd"  : 0,
                                    "fgdcGeoform" : 1,
                                "citRespParty" : 6,
                                    "editorSource" : 0, "editorDigest" : 1,"rpIndName"     : 2,
                                    "rpOrgName"    : 3, "rpPosName"    : 4, "rpCntInfo"    : 5,
                                    "cntAddress"   : 0, "delPoint"     : 0, "city"         : 1,
                                    "adminArea"    : 2, "postCode"     : 3, "eMailAdd"     : 4,
                                    "country"      : 5, "cntPhone"     : 1, "voiceNum"     : 0,
                                    "faxNum"       : 1, "cntHours"     : 2, "cntOnlineRes" : 3,
                                    "linkage"      : 0, "protocol"     : 1, "orName"       : 2,  # noqa: F601
                                    "orDesc"       : 3, "orFunct"      : 4, "OnFunctCd"    : 0,  # noqa: F601
                                    "editorSave"   : 6, "displayName"  : 7, "role"         : 8,  # noqa: F601
                                    "RoleCd"       : 0,
                                "srcMedName" : 7,
                                    "MedNameCd" : 0,
                            "prcStep"    : 3,
                                "stepDesc"   : 0,
                                "stepProc"   : 1,
                                    "editorSource" : 0, "editorDigest" : 1,"rpIndName"     : 2,  # noqa: F601
                                    "rpOrgName"    : 3, "rpPosName"    : 4, "rpCntInfo"    : 5,  # noqa: F601
                                    "cntAddress"   : 0, "delPoint"     : 0, "city"         : 1,  # noqa: F601
                                    "adminArea"    : 2, "postCode"     : 3, "eMailAdd"     : 4,  # noqa: F601
                                    "country"      : 5, "cntPhone"     : 1, "voiceNum"     : 0,  # noqa: F601
                                    "faxNum"       : 1, "cntHours"     : 2, "cntOnlineRes" : 3,  # noqa: F601
                                    "linkage"      : 0, "protocol"     : 1, "orName"       : 2,  # noqa: F601
                                    "orDesc"       : 3, "orFunct"      : 4, "OnFunctCd"    : 0,  # noqa: F601
                                    "editorSave"   : 6, "displayName"  : 7, "role"         : 8,  # noqa: F601
                                    "RoleCd"       : 0,  # noqa: F601

                                "stepDateTm" : 2,
                                "cntOnlineRes" : 3, "linkage"     : 0,  # noqa: F601
                                "protocol"   : 1, "orName"       : 2, "orDesc"      : 3,  # noqa: F601
                                "orFunct"    : 4, "OnFunctCd"    : 0,  # noqa: F601
                      }

        import json
        json_path = rf"{out_data_path}\dqInfo_dict.json"
        # Write to File
        with open(json_path, 'w') as json_file:
            json.dump(dqInfo_dict, json_file, indent=4)
        del json_file
        del dqInfo_dict
        with open(json_path, "r") as json_file:
            dqInfo_dict = json.load(json_file)
        del json_file
        arcpy.AddMessage(dqInfo_dict)
        del dqInfo_dict
        del json_path
        del json

        distInfo_dict = {"distInfo" : 0,
                            "distFormat"  : 0,
                                "formatName"   : 0,
                                "formatVer"    : 1,
                                "fileDecmTech" : 2,
                                "formatInfo"   : 3,
                            "distributor" : 1,
                                "distorCont" : 0,
                                    "editorSource" : 0,
                                    "editorDigest" : 1,
                                    "rpIndName"    : 2,
                                    "rpOrgName"    : 3,
                                    "rpPosName"    : 4,
                                    "rpCntInfo"    : 5,
                                        "cntAddress"   : 0,
                                            "delPoint"  : 0,
                                            "city"      : 1,
                                            "adminArea" : 2,
                                            "postCode"  : 3,
                                            "eMailAdd"  : 4,
                                            "country"   : 5,
                                        "cntPhone"     : 1,
                                            "voiceNum" : 0,
                                            "faxNum" : 1,
                                        "cntHours"     : 2,
                                        "cntOnlineRes" : 3,
                                            "linkage" : 0,
                                            "orName" : 1,
                                            "orDesc" : 2,
                                            "orFunct" : 3,
                                                "OnFunctCd" : 0,
                                    "editorSave"   : 6,
                                    "displayName"  : 7,
                                    "role"         : 8,
                                        "RoleCd" : 0,
                            "distTranOps" : 2,
                                "unitsODist" : 0,
                                "transSize"  : 1,
                                "onLineSrc"  : 2,
                                    "linkage"  : 0,  # noqa: F601
                                    "protocol" : 1,
                                    "orName"   : 2,  # noqa: F601
                                    "orDesc"   : 3,  # noqa: F601
                                    "orFunct"  : 4,  # noqa: F601
                                        "OnFunctCd" : 0,  # noqa: F601
                           }

        import json
        json_path = rf"{out_data_path}\distInfo_dict.json"
        # Write to File
        with open(json_path, 'w') as json_file:
            json.dump(distInfo_dict, json_file, indent=4)
        del json_file
        del distInfo_dict
        with open(json_path, "r") as json_file:
            distInfo_dict = json.load(json_file)
        del json_file
        arcpy.AddMessage(distInfo_dict)
        del distInfo_dict
        del json_path
        del json

        RoleCd_dict = {"001" : "Resource Provider", "002" : "Custodian",
                       "003" : "Owner",             "004" : "User",
                       "005" : "Distributor",       "006" : "Originator",
                       "007" : "Point of Contact",  "008" : "Principal Investigator",
                       "009" : "Processor",         "010" : "Publisher",
                       "011" : "Author",            "012" : "Collaborator",
                       "013" : "Editor",            "014" : "Mediator",
                       "015" : "Rights Holder",}

        import json
        json_path = rf"{out_data_path}\RoleCd_dict.json"
        # Write to File
        with open(json_path, 'w') as json_file:
            json.dump(RoleCd_dict, json_file, indent=4)
        del json_file
        del RoleCd_dict
        with open(json_path, "r") as json_file:
            RoleCd_dict = json.load(json_file)
        del json_file
        arcpy.AddMessage(RoleCd_dict)
        del RoleCd_dict
        del json_path
        del json

        #role_dict = {"citRespParty"  : ,
        #             "idPoC"        : ,
        #             "distorCont"   : ,
        #             "mdContact"    : ,
        #             "stepProc"


        tpCat_dict = {"002": '<tpCat><TopicCatCd value="002"></TopicCatCd></tpCat>',
                      "007": '<tpCat><TopicCatCd value="007"></TopicCatCd></tpCat>',
                      "014": '<tpCat><TopicCatCd value="014"></TopicCatCd></tpCat>',}

        import json
        json_path = rf"{out_data_path}\tpCat_dict.json"
        # Write to File
        with open(json_path, 'w') as json_file:
            json.dump(tpCat_dict, json_file, indent=4)
        del json_file
        del tpCat_dict
        with open(json_path, "r") as json_file:
            tpCat_dict = json.load(json_file)
        del json_file
        arcpy.AddMessage(tpCat_dict)
        del tpCat_dict
        del json_path
        del json

        # ###################### DisMAP ########################################
        RoleCd_dict = {"001" : "Resource Provider", "002" : "Custodian",
                       "003" : "Owner",             "004" : "User",
                       "005" : "Distributor",       "006" : "Originator",
                       "007" : "Point of Contact",  "008" : "Principal Investigator",
                       "009" : "Processor",         "010" : "Publisher",
                       "011" : "Author",            "012" : "Collaborator",
                       "013" : "Editor",            "014" : "Mediator",
                       "015" : "Rights Holder",}
        contact_dict = {"citRespParty" : [{"role"  : "Custodian",              "rpIndName" : "Timothy J Haverland", "eMailAdd" : "tim.haverland@noaa.gov"},],
                        "idPoC"        : [{"role"  : "Point of Contact",       "rpIndName" : "Melissa Ann Karp",    "eMailAdd" : "melissa.karp@noaa.gov"},],
                        "distorCont"   : [{"role"  : "Distributor",            "rpIndName" : "Timothy J Haverland", "eMailAdd" : "tim.haverland@noaa.gov"},],
                        "mdContact"    : [{"role"  : "Author",                 "rpIndName" : "John F Kennedy",      "eMailAdd" : "john.f.kennedy@noaa.gov"},],
                        "srcCitatn"    : [{"role"  : "Principal Investigator", "rpIndName" : "Melissa Ann Karp",    "eMailAdd" : "melissa.karp@noaa.gov"},],
                        "stepProc"     : [{"role"  : "Processor",              "rpIndName" : "John F Kennedy",      "eMailAdd" : "john.f.kennedy@noaa.gov"},
                                          {"role"  : "Processor",              "rpIndName" : "Melissa Ann Karp",    "eMailAdd" : "melissa.karp@noaa.gov"},
                                         ],}
        del RoleCd_dict

        import json
        json_path = rf"{out_data_path}\contact_dict.json"
        #arcpy.AddMessage(json_path)
        # Write to File
        with open(json_path, 'w') as json_file:
            json.dump(contact_dict, json_file, indent=4)
        del json_file
        del contact_dict
        with open(json_path, "r") as json_file:
            contact_dict = json.load(json_file)
        del json_file
        arcpy.AddMessage(contact_dict)
        del contact_dict
        del json_path
        del json

        # ###################### DisMAP ########################################

        # Declared Varaiables
        del project_folder, out_data_path
        # Imports
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

    except KeyboardInterrupt:
        sys.exit()
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(f"Caught an arcpy.ExecuteWarning error in the '{inspect.stack()[0][3]}' function.")
        arcpy.AddWarning(arcpy.GetMessages(1))
    except arcpy.ExecuteError:
        arcpy.AddError(f"Caught an arcpy.ExecuteError error in the '{inspect.stack()[0][3]}' function.")
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
        sys.exit()
    except SystemExit as se:
        arcpy.AddError(f"Caught an SystemExit error: {se} in the '{inspect.stack()[0][3]}' function.")
        sys.exit()
    except Exception as e:
        arcpy.AddError(f"Caught an Exception error: {e} in the '{inspect.stack()[0][3]}' function.")
        traceback.print_exc()
        sys.exit()
    except:  # noqa: E722
        arcpy.AddError(f"Caught an except error in the '{inspect.stack()[0][3]}' function.")
        traceback.print_exc()
        sys.exit()
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

        script_tool(project_gdb=project_gdb)
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
        sys.exit()