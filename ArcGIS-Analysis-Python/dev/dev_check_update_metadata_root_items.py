#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      john.f.kennedy
#
# Created:     03/01/2025
# Copyright:   (c) john.f.kennedy 2025
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# Python Built-in's modules are loaded first
import os, sys
import traceback
import inspect

# Third-party modules are loaded second
#import arcpy

def new_function():
    try:

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

def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)

def update_xml_elements(species_range_fc="", fc_metadata_xml_file=""):
    try:
        # Imports
        from lxml import etree
        from io import StringIO
        import arcpy
        from arcpy import metadata as md
        # Project modules
        from src.project_tools import pretty_format_xml_file

        # Check if file exists first and then the file size
        if not os.path.isfile(fc_metadata_xml_file) or os.path.getsize(fc_metadata_xml_file) == 0:
            print(f"File '{os.path.basename(fc_metadata_xml_file)}' is missing or empty")
            print("Get metadata from feature class")
            # Assign the Metadata object's content to a target item
            dataset_md = md.Metadata(species_range_fc)
            dataset_md.synchronize('ALWAYS')
            dataset_md.save()
            dataset_md.reload()
            print("Save Metadata as an XML file")
            dataset_md.saveAsXML(fc_metadata_xml_file, "REMOVE_ALL_SENSITIVE_INFO")
            del dataset_md

        elif os.path.isfile(fc_metadata_xml_file) or os.path.getsize(fc_metadata_xml_file) > 0:
            print(f"File '{os.path.basename(fc_metadata_xml_file)}' exists and has size: {file_size(fc_metadata_xml_file)}")

        else:
            pass

        root_dict = {"Esri"       :  0, "dataIdInfo" :  1, "mdChar"      :  2,
                     "mdContact"  :  3, "mdDateSt"   :  4, "mdFileID"    :  5,
                     "mdLang"     :  6, "mdMaint"    :  7, "mdHrLv"      :  8,
                     "mdHrLvName" :  9, "refSysInfo" : 10, "spatRepInfo" : 11,
                     "spdoinfo"   : 12, "dqInfo"     : 13, "distInfo"    : 14,
                     "eainfo"     : 15, "contInfo"   : 16, "spref"       : 17,
                     "spatRepInfo" : 18, "dataSetFn" : 19, "Binary"      : 100,}

        # Parse the XML
        parser = etree.XMLParser(remove_blank_text=True, encoding='UTF-8')
        target_name = os.path.basename(fc_metadata_xml_file).replace(".xml", "")
        target_tree = etree.parse(fc_metadata_xml_file, parser=parser)
        target_root = target_tree.getroot()
        del parser

        # Sort the XML
        for child in target_root.xpath("."):
            child[:] = sorted(child, key=lambda x: root_dict[x.tag])
            del child

        #etree.indent(target_root, space="    ")
        #print(etree.tostring(target_root, xml_declaration=True, encoding="utf-8").decode())

        # ######################################################################
        #               ###--->>> Esri section Start <<<---###
        # ######################################################################

        Esri = target_tree.xpath(f"./Esri")
        if len(Esri) == 0:
            xml = '''<Esri><CreaDate>20250201</CreaDate><CreaTime>12234100</CreaTime><ArcGISFormat>1.0</ArcGISFormat><ArcGISStyle>ISO 19139 Metadata Implementation Specification</ArcGISStyle><SyncOnce>FALSE</SyncOnce><DataProperties><itemProps><itemName Sync="TRUE">SpeciesRangeTemplate</itemName><imsContentType Sync="TRUE">002</imsContentType><nativeExtBox><westBL Sync="TRUE">-82.000000</westBL><eastBL Sync="TRUE">-72.000000</eastBL><southBL Sync="TRUE">11.000000</southBL><northBL Sync="TRUE">24.000000</northBL><exTypeCode Sync="TRUE">1</exTypeCode></nativeExtBox></itemProps><coordRef><type Sync="TRUE">Geographic</type><geogcsn Sync="TRUE">GCS_WGS_1984</geogcsn><csUnits Sync="TRUE">Angular Unit: Degree (0.017453)</csUnits><peXml Sync="TRUE">&lt;GeographicCoordinateSystem xsi:type='typens:GeographicCoordinateSystem' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xmlns:xs='http://www.w3.org/2001/XMLSchema' xmlns:typens='http://www.esri.com/schemas/ArcGIS/3.4.0'&gt;&lt;WKT&gt;GEOGCS[&amp;quot;GCS_WGS_1984&amp;quot;,DATUM[&amp;quot;D_WGS_1984&amp;quot;,SPHEROID[&amp;quot;WGS_1984&amp;quot;,6378137.0,298.257223563]],PRIMEM[&amp;quot;Greenwich&amp;quot;,0.0],UNIT[&amp;quot;Degree&amp;quot;,0.0174532925199433],AUTHORITY[&amp;quot;EPSG&amp;quot;,4326]]&lt;/WKT&gt;&lt;XOrigin&gt;-400&lt;/XOrigin&gt;&lt;YOrigin&gt;-400&lt;/YOrigin&gt;&lt;XYScale&gt;999999999.99999988&lt;/XYScale&gt;&lt;ZOrigin&gt;-100000&lt;/ZOrigin&gt;&lt;ZScale&gt;10000&lt;/ZScale&gt;&lt;MOrigin&gt;-100000&lt;/MOrigin&gt;&lt;MScale&gt;10000&lt;/MScale&gt;&lt;XYTolerance&gt;8.983152841195215e-09&lt;/XYTolerance&gt;&lt;ZTolerance&gt;0.001&lt;/ZTolerance&gt;&lt;MTolerance&gt;0.001&lt;/MTolerance&gt;&lt;HighPrecision&gt;true&lt;/HighPrecision&gt;&lt;LeftLongitude&gt;-180&lt;/LeftLongitude&gt;&lt;WKID&gt;4326&lt;/WKID&gt;&lt;LatestWKID&gt;4326&lt;/LatestWKID&gt;&lt;/GeographicCoordinateSystem&gt;</peXml></coordRef></DataProperties><SyncDate>20250202</SyncDate><SyncTime>14404400</SyncTime><ModDate>20250202</ModDate><ModTime>14404400</ModTime><scaleRange><minScale>150000000</minScale><maxScale>5000</maxScale></scaleRange><ArcGISProfile>ISO19139</ArcGISProfile></Esri>'''
            position = root_dict["Esri"]
            esri_root = etree.XML(xml)
            #print("Inserting Esri at position: {position}")
            idCitation.insert(position, esri_root)
            target_root.insert(position, element)
            del position, esri_root
            del xml
        elif len(Esri) == 1:
            pass
            #print(f"{len(Esri)} {Esri[0].tag} element is found")
        elif len(Esri) > 1:
            #print(f"Removing {len(Esri)-1} 'Esri' elements")
            for i in range(1, len(Esri)):
                target_root.remove(Esri[i])
                i+=1
                del i
        else:
            pass

        esri_dict ={"CreaDate" : 0,  "CreaTime" : 1, "ArcGISFormat" : 2,
                    "ArcGISStyle" : 3, "SyncOnce" : 4, "DataProperties" : 5,
                    "itemProps" : 0, "itemName" : 0, "imsContentType" : 1,
                    "nativeExtBox" : 2, "westBL" : 0, "eastBL" : 1, "southBL" : 2,
                    "northBL" : 3, "exTypeCode" : 4, "coordRef" : 1, "type" : 0,
                    "geogcsn" : 2, "csUnits" : 3, "peXml" : 4, "SyncDate" : 6,
                    "SyncTime" : 7, "ModDate" : 8, "ModTime" : 9,
                    "scaleRange" : 10, "minScale" : 11, "maxScale" : 12,
                    "ArcGISProfile" : 13,}

        # Check for ArcGISStyle
        Esri = target_tree.xpath(f"./Esri")[0]
        ArcGISStyle = Esri.xpath(f"./ArcGISStyle")
        if len(ArcGISStyle) == 0:
            position = esri_dict["ArcGISStyle"]
            #print(f"Inserting ArcGISStyle at position {position}")
            ArcGIS_Style = etree.SubElement(Esri, "ArcGISStyle")
            ArcGIS_Style.text = "ISO 19139 Metadata Implementation Specification"
            Esri.insert(position, ArcGIS_Style)
            del position, ArcGIS_Style
        elif len(ArcGISStyle) == 1:
            position = esri_dict["ArcGISStyle"]
            #print(f"{len(ArcGISStyle)} {ArcGISStyle[0].tag} element is found with value: {position}")
            ArcGISStyle[0].text = "ISO 19139 Metadata Implementation Specification"
            del position
        elif len(ArcGISStyle) > 1:
            #print(f"Removing {len(ArcGISStyle)-1} 'ArcGISStyle' elements")
            for i in range(1, len(ArcGISStyle)):
                Esri.remove(ArcGISStyle[i])
                i+=1
                del i
        else:
            pass
        del Esri, ArcGISStyle

        # ###--->>> Deletes an unwanted element
        Esri = target_tree.xpath(f"./Esri")[0]
        itemSize = Esri.xpath(f".//itemSize")
        if len(itemSize) == 0:
            pass
        elif len(itemSize) == 1:
            Esri.remove(itemSize)
        elif len(itemSize) > 1:
            #print(f"Removing {len(itemSize)-1} 'itemSize' elements")
            for i in range(1, len(itemSize)):
                Esri.remove(itemSize[i])
                i+=1
                del i
        else:
            pass
        del itemSize
        del Esri
        # ###--->>> Deletes an unwanted element

        # Check for scaleRange
        Esri = target_tree.xpath(f"./Esri")[0]
        scaleRange = Esri.xpath(f"./scaleRange")
        if len(scaleRange) == 0:
            #print("Inserting scaleRange, minScale, maxScale")
            scale_range = etree.SubElement(Esri, "scaleRange")
            Esri.insert(esri_dict["scaleRange"], scale_range)
            minScale    = etree.SubElement(scale_range, "minScale")
            minScale.text = '150000000'
            scaleRange.insert(esri_dict["minScale"], minScale)
            maxScale    = etree.SubElement(scale_range, "maxScale")
            maxScale.text = '5000'
            scaleRange.insert(esri_dict["maxScale"], maxScale)
            # print(etree.tostring(scale_range, pretty_print=True).decode())
            del scale_range, minScale, maxScale
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
        #print(etree.tostring(Esri, pretty_print=True, encoding="utf-8").decode())
        del scaleRange, Esri

        # Check for ArcGISProfile
        Esri = target_tree.xpath(f"./Esri")[0]
        ArcGISProfile = Esri.xpath(f"./ArcGISProfile")
        if len(ArcGISProfile) == 0:
            #print("Inserting ArcGISProfile")
            ArcGIS_Profile = etree.SubElement(Esri, "ArcGISProfile")
            ArcGIS_Profile.text = 'ISO19139'
            Esri.insert(esri_dict["ArcGISProfile"], ArcGIS_Profile)
            del ArcGIS_Profile
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

        del esri_dict

        # ######################################################################
        #               ###--->>> Esri section End <<<---###
        # ######################################################################

        # ######################################################################
        #               ###--->>> dataIdInfo section Start <<<---###
        # ######################################################################

        # idCitation sub-section

        dataIdInfo = target_tree.xpath(f"./dataIdInfo")
        if len(dataIdInfo) == 0:
            #print("Inserting dataIdInfo at {root_dict['envirDesc']}")
            position = root_dict["dataIdInfo"]
            element = etree.SubElement(target_root, "dataIdInfo")
            target_root.insert(position, element)
            del position, element
        elif len(dataIdInfo) == 1:
            pass
            #print(f"{len(dataIdInfo)} {dataIdInfo[0].tag} element is found")
        elif len(dataIdInfo) > 1:
            print(f"{len(dataIdInfo)} {dataIdInfo[0].tag} elements are found")
        else:
            pass
        del dataIdInfo

        dataIdInfo_dict = { "idCitation" : 0, "searchKeys" :  1, "idPurp"     : 2,
                            "idAbs"      : 3, "idCredit"   :  4, "resConst"   : 5,
                            "envirDesc"  : 6, "dataLang"   :  7, "spatRpType" : 8,
                            "dataExt"    : 9, "tpCat"      : 10,}

        dataIdInfo = target_tree.xpath(f"./dataIdInfo")[0]
        for child in dataIdInfo.xpath("."):
            child[:] = sorted(child, key=lambda x: dataIdInfo_dict[x.tag])
            del child
        del dataIdInfo

        dataIdInfo = target_tree.xpath(f"./dataIdInfo")[0]
        envirDesc = dataIdInfo.xpath(f"./envirDesc")
        if len(envirDesc) == 0:
            #print(f"Inserting envirDesc at {dataIdInfo_dict['envirDesc']}")
            element = etree.SubElement(dataIdInfo, "envirDesc")
            element.set("Sync", "TRUE")
            dataIdInfo.insert(dataIdInfo_dict['envirDesc'], element)
            del element
        elif len(envirDesc) == 1:
            #print(f"Updating envirDesc if needed at index: {dataIdInfo.index(dataIdInfo.xpath(f'./envirDesc')[0])}")
            envirDesc[0].set("Sync", "TRUE")
            dataIdInfo.insert(dataIdInfo_dict['envirDesc'], envirDesc[0])
        elif len(envirDesc) > 1:
            pass
        else:
            pass

        del envirDesc, dataIdInfo
        #envirDesc = dataIdInfo.xpath(f"./envirDesc")[0]
        # print(f"Set envirDesc to TRUE")
        #envirDesc.set("Sync", "TRUE")
        #del envirDesc, dataIdInfo

        # ######################################################################
        # Resource Title
        # ######################################################################

        # idCitation sub-section
        idCitation  = target_tree.xpath(f"./dataIdInfo/idCitation")[0]

        idCitation_dict = {"idCitation" : 0, "resTitle" : 0, "resAltTitle" : 1,
                           "collTitle"  : 2, "presForm" : 3, "PresFormCd"  : 0,
                           "fgdcGeoform" : 1, "date" : 4, "createDate" : 0,
                           "pubDate"    : 1, "revisedDate" : 2, "citRespParty"  : 6,
                           }

        resTitle = idCitation.xpath(f"./resTitle")
        if len(resTitle) == 0:
            #print(f"Inserting resTitle {idCitation_dict['resTitle']}")
            element = etree.SubElement(idCitation, "resTitle")
            element.text = target_name
            idCitation.insert(0, element)
            del element
        elif len(resTitle) == 1:
            #print(f"Updating resTitle if needed at index: {idCitation.index(idCitation.xpath(f'./resTitle')[0])}")
            if target_name not in resTitle[0].text:
                new_resTitle = resTitle[0].text + ". " + target_name
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
        #print(etree.tostring(idCitation, pretty_print=True, encoding="utf-8").decode())
        del resTitle

        # ######################################################################
        # Resource Alternate Title
        # ######################################################################

        # idCitation sub-section
        idCitation  = target_tree.xpath(f"./dataIdInfo/idCitation")[0]
        resAltTitle = idCitation.xpath(f"./resAltTitle")
        if len(resAltTitle) == 0:
            position = idCitation_dict['resAltTitle']
            #print(f"Inserting resAltTitle at {position}")
            element = etree.SubElement(idCitation, "resAltTitle")
            element.text = "Sample Species Template"
            idCitation.insert(position, element)
            del element, position
        elif len(resAltTitle) == 1:
            position = idCitation_dict['resAltTitle']
            #print(f"Updating resAltTitle if needed {position}")
            resAltTitle[0].text = "Sample Species Template"
            if target_name not in resAltTitle[0].text:
                new_resAltTitle = resAltTitle[0].text + ". " + target_name
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
        #print(etree.tostring(idCitation, pretty_print=True, encoding="utf-8").decode())
        del resAltTitle

        # ######################################################################
        # Collective Title
        # ######################################################################

        collTitle = idCitation.xpath(f"./collTitle")
        if len(collTitle) == 0:
            position = idCitation_dict['collTitle']
            #print(f"Inserting collTitle {position}")
            element = etree.SubElement(idCitation, "collTitle")
            element.text = 'NMFS ESA Range Geodatabase 2024'
            idCitation.insert(position, element)
            del element, position
        elif len(collTitle) == 1:
            position = idCitation_dict['collTitle']
            #print(f"Updating collTitle if needed {position}")
            if 'NMFS ESA Range Geodatabase 2024' not in collTitle[0].text:
                new_rescollTitle = collTitle[0].text + ". " + 'NMFS ESA Range Geodatabase 2024'
                collTitle[0].text = new_rescollTitle
                del new_rescollTitle
            else:
                pass
            del position
        elif len(collTitle) > 1:
            print(f"May need to delete: {len(collTitle)} collTitle")

        else:
            pass
        #print(etree.tostring(idCitation, pretty_print=True, encoding="utf-8").decode())
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
        #print(etree.tostring(idCitation, pretty_print=True, encoding="utf-8").decode())
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
            pubDate = etree.SubElement(element, "pubDate")
            pubDate.text = "2025-01-01T00:00:00"
            idCitation.insert(position, element)
            del element, pubDate, position
        elif len(date) == 1:
            #print(f"Updating date if needed at position: {idCitation.index(date[0])}")
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
            idCitation.insert(4, date[0])
            del pubDate
        elif len(date) > 1:
            # May not get here
            print(f"May needed to be deleted {len(date)} date")
        else:
            pass
        #print(etree.tostring(idCitation, pretty_print=True, encoding="utf-8").decode())
        del date

        # ######################################################################
        # Citation Responsiable Party
        # ######################################################################

        citRespParty  = idCitation.xpath(f"./citRespParty")
        xml = '''<citRespParty>
                    <editorSource>extermal</editorSource>
                    <editorDigest>9cc0fe80de5687cc4d79f50f3a254f2c3ceb08ce</editorDigest>
                    <rpIndName>Nikki Wildart</rpIndName>
                    <rpOrgName>Office of Protected Resources, National Marine Fisheries Service</rpOrgName>
                    <rpPosName>Biologist</rpPosName>
                    <rpCntInfo>
                        <cntAddress addressType="both">
                            <delPoint>1315 East West Highway</delPoint>
                            <city>Silver Spring</city>
                            <adminArea>MD</adminArea>
                            <postCode>20910-3282</postCode>
                            <eMailAdd>nikki.wildart@noaa.gov</eMailAdd>
                            <country>US</country>
                        </cntAddress>
                        <cntPhone>
                            <voiceNum tddtty="">(301) 427-8443</voiceNum>
                            <faxNum>(301) 427-8443</faxNum>
                        </cntPhone>
                        <cntHours>0700 - 1800 EST/EDT</cntHours>
                        <cntOnlineRes>
                            <linkage>https://www.fisheries.noaa.gov/about/office-protected-resources</linkage>
                            <protocol>REST Service</protocol>
                            <orName>Fisheries OPR</orName>
                            <orDesc>NOAA Fisheries Office of Science and Technology</orDesc>
                            <orFunct>
                                <OnFunctCd value="002"></OnFunctCd>
                            </orFunct>
                        </cntOnlineRes>
                    </rpCntInfo>
                    <editorSave>True</editorSave>
                    <displayName>Nikki Wildart</displayName>
                    <role>
                        <RoleCd value="002"></RoleCd>
                    </role>
                </citRespParty>'''

        # Create an XML string
        citRespParty_root = etree.XML(xml)
        citRespParty_email = citRespParty_root.xpath(f".//eMailAdd")[0].text

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

        if len(citRespParty) == 0:
            position = idCitation_dict['citRespParty']
            #print("Inserting citRespParty at position: {position}")
            idCitation.insert(position, citRespParty_root)
            del position
        elif len(citRespParty) == 1:
            position = idCitation_dict['citRespParty']
            #print(f"Updating citRespParty if needed at position: {position}")
            idCitation.insert(position, citRespParty[0])
            del position
            # Get email address from citRespParty[0]
            cit_resp_party_email = citRespParty[0].xpath(f".//eMailAdd")[0].text
            if cit_resp_party_email:
                #print(f"\tFound {cit_resp_party_email}")
                position = idCitation.index(citRespParty[0])
                if cit_resp_party_email != citRespParty_email:
                    #print("\t\tInserting an additional citRespParty")
                    idCitation.insert(position+1, citRespParty_root)
                else:
                    pass
                    #print("\t\tcitRespParty update complete")
                del position
            else:
                pass
            del cit_resp_party_email
        elif len(citRespParty) > 1:
            #print(f"{len(citRespParty)} citRespParty")
            #print("does it have the same email and the new contact?")
            cit_resp_party_emails = list()
            for cit_resp_party in citRespParty:
                if len(idCitation.xpath(f"./citRespParty/rpCntInfo/cntAddress/eMailAdd")) > 0:
                    cit_resp_party_email = idCitation.xpath(f"./citRespParty/rpCntInfo/cntAddress/eMailAdd")[0]
                    #print(f"\tFound: {cit_resp_party_email.text}")
                    if cit_resp_party_email not in cit_resp_party_emails:
                        #print(f"\t{cit_resp_party_email.text} not in email list")
                        cit_resp_party_emails.append(cit_resp_party_email)
                    elif cit_resp_party_email in cit_resp_party_emails:
                        # Remove the element
                        if cit_resp_party is not None:
                            #print(f"\tRemoving {cit_resp_party_email.text}")
                            idCitation.remove(cit_resp_party)
                        else:
                            pass
                    else:
                        pass
                    del cit_resp_party_email
                    #position = idCitation.index(cit_resp_party)
                else:
                    pass
                del cit_resp_party
            del cit_resp_party_emails
        else:
            pass
        del citRespParty_root, citRespParty_email
        del idCitation_dict

        #print(etree.tostring(idCitation, pretty_print=True, encoding="utf-8").decode())
        del xml, citRespParty
        del idCitation

        # ######################################################################
        # Topics
        # ######################################################################
        tpCat_dict = {"002": '<tpCat><TopicCatCd value="002"></TopicCatCd></tpCat>',
         "007": '<tpCat><TopicCatCd value="007"></TopicCatCd></tpCat>',
         "014": '<tpCat><TopicCatCd value="014"></TopicCatCd></tpCat>',}

        dataIdInfo = target_tree.xpath(f"./dataIdInfo")[0]
        tpCat      = dataIdInfo.xpath(f"./tpCat")
        if len(tpCat) == 0:
            position = dataIdInfo_dict['tpCat']
            #print(f"Inserting tpCat at {position}")
            for key in tpCat_dict:
                xml = tpCat_dict[key]
                root = etree.XML(xml)
                dataIdInfo.insert(position, root)
                position+=1
                del root, xml, key
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


##            #print(f"Updating tpCat at {position}")
##            for key in tpCat_dict:
##                xml = tpCat_dict[key]
##                root = etree.XML(xml)
##                dataIdInfo.insert(position, root)
##                position+=1
##                del root, xml, key
##            del position

        else:
            pass
        #print(etree.tostring(Esri, encoding="utf-8").decode())
        #print(etree.tostring(dataIdInfo, pretty_print=True, encoding="utf-8").decode())
        del tpCat, tpCat_dict

        del dataIdInfo
        del dataIdInfo_dict

        # ######################################################################
        #               ###--->>> dataIdInfo section End <<<---###
        # ######################################################################

        # ######################################################################
        #               ###--->>> metadata detail section Start <<<---###
        # ######################################################################

        mdChar = target_tree.xpath(f"./mdChar")
        if len(mdChar) == 0:
            #print(f"Inserting 'mdChar' at position: {root_dict['mdChar']}")
            xml = '<mdChar><CharSetCd value="004" Sync="TRUE"></CharSetCd></mdChar>'
            root = etree.XML(xml)
            position = root_dict['mdChar']
            target_root.insert(position, root)
            del position, root, xml
        elif len(mdChar) == 1:
            #print(f"Updating '{mdChar[0].tag}' if needed at position: {target_root.index(target_root.xpath(f'./mdChar')[0])}")
            position = root_dict['mdChar']
            target_root.insert(position, mdChar[0])
        elif len(mdChar) > 1:
            # if it is multiples, is that ok or not. eainfo has multiples, topic does, contacts
            print(f"Removing {len(mdChar)-1} mdChar elements")
            for i in range(1, len(mdChar)):
                target_root.remove(mdChar[i])
                i+=1
                del i
        else:
            pass
        #print(etree.tostring(idCitation, pretty_print=True, encoding="utf-8").decode())
        del mdChar

        # ######################################################################
        #               ###--->>> mdContact section Start <<<---###
        # ######################################################################
        mdContact = target_tree.xpath(f"./mdContact")
        xml = '''<citRespParty>
            <editorSource>extermal</editorSource>
            <editorDigest>9cc0fe80de5687cc4d79f50f3a254f2c3ceb08ce</editorDigest>
            <rpIndName>Nikki Wildart</rpIndName>
            <rpOrgName>Office of Protected Resources, National Marine Fisheries Service</rpOrgName>
            <rpPosName>Biologist</rpPosName>
            <rpCntInfo>
                <cntAddress addressType="both">
                    <delPoint>1315 East West Highway</delPoint>
                    <city>Silver Spring</city>
                    <adminArea>MD</adminArea>
                    <postCode>20910-3282</postCode>
                    <eMailAdd>nikki.wildart@noaa.gov</eMailAdd>
                    <country>US</country>
                </cntAddress>
                <cntPhone>
                    <voiceNum tddtty="">(301) 427-8443</voiceNum>
                    <faxNum>(301) 427-8443</faxNum>
                </cntPhone>
                <cntHours>0700 - 1800 EST/EDT</cntHours>
                <cntOnlineRes>
                    <linkage>https://www.fisheries.noaa.gov/about/office-protected-resources</linkage>
                    <protocol>REST Service</protocol>
                    <orName>Fisheries OPR</orName>
                    <orDesc>NOAA Fisheries Office of Science and Technology</orDesc>
                    <orFunct>
                        <OnFunctCd value="002"></OnFunctCd>
                    </orFunct>
                </cntOnlineRes>
            </rpCntInfo>
            <editorSave>True</editorSave>
            <displayName>Nikki Wildart</displayName>
            <role>
                <RoleCd value="002"></RoleCd>
            </role>
        </citRespParty>'''

        # Create an XML string
        mdContact_root = etree.XML(xml)
        mdContact_email = mdContact_root.xpath(f".//eMailAdd")[0].text
        del xml

 #        if len(mdContact) == 0:
 #            position = 5
 #            print("Inserting mdContact at position: {idCitation.index(citRespParty[0])}")
 #            target_root.insert(position, new_cit_resp_party_root)
 #            del position

        if len(mdContact) == 0:
            #print(f"Inserting 'mdContact' at position: {root_dict['mdContact']}")
            xml = '<mdContact Sync="TRUE"></mdContact>'
            root = etree.XML(xml)
            position = root_dict['mdContact']
            target_root.insert(position, root)
            del position, root, xml
        elif len(mdContact) == 1:
            #print(f"Updating '{mdContact[0].tag}' if needed at position: {root_dict['mdContact']}")
            position = root_dict['mdContact']
            target_root.insert(position, mdContact[0])
            del position
        elif len(mdContact) > 1:
            # if it is multiples, is that ok or not. eainfo has multiples, topic does, contacts
            print(f"Removing {len(mdContact)-1} mdContact elements")
            for i in range(1, len(mdContact)):
                target_root.remove(mdContact[i])
                i+=1
                del i
        else:
            pass
        #print(etree.tostring(idCitation, pretty_print=True, encoding="utf-8").decode())

##   #
##   #        elif len(citRespParty) == 1:
##   #            print(f"Updating citRespParty if needed at position: {idCitation.index(citRespParty[0])}")
##   #            position = 5
##   #            idCitation.insert(position, citRespParty[0])
##   #            # Get email address from citRespParty[0]
##   #            cit_resp_party_email = citRespParty[0].xpath(f".//eMailAdd")[0].text
##   #            if cit_resp_party_email:
##   #                print(f"\tFound {cit_resp_party_email}")
##   #                position = idCitation.index(citRespParty[0])
##   #                if cit_resp_party_email != new_cit_resp_party_email:
##   #                    print("\t\tInserting an additional citRespParty")
##   #                    idCitation.insert(position+1, new_cit_resp_party_root)
##   #                else:
##   #                    print("\t\tcitRespParty update complete")
##   #            else:
##   #                pass
##   #            del cit_resp_party_email
##   #            del position
##   #        elif len(citRespParty) > 1:
##   #            print(f"{len(citRespParty)} citRespParty")
##   #            print("does it have the same email and the new contact?")
##   #            cit_resp_party_emails = list()
##   #            for cit_resp_party in citRespParty:
##   #                if len(idCitation.xpath(f"./citRespParty/rpCntInfo/cntAddress/eMailAdd")) > 0:
##   #                    cit_resp_party_email = idCitation.xpath(f"./citRespParty/rpCntInfo/cntAddress/eMailAdd")[0]
##   #                    print(f"\tFound: {cit_resp_party_email.text}")
##   #                    if cit_resp_party_email not in cit_resp_party_emails:
##   #                        print(f"\t{cit_resp_party_email.text} not in email list")
##   #                        cit_resp_party_emails.append(cit_resp_party_email)
##   #                    elif cit_resp_party_email in cit_resp_party_emails:
##   #                        # Remove the element
##   #                        if cit_resp_party is not None:
##   #                            print(f"\tRemoving {cit_resp_party_email.text}")
##   #                            idCitation.remove(cit_resp_party)
##   #                        else:
##   #                            pass
##   #                    else:
##   #                        pass
##   #                    del cit_resp_party_email
##   #                    #position = idCitation.index(cit_resp_party)
##   #                else:
##   #                    pass
##   #                del cit_resp_party
##   #            del cit_resp_party_emails
##   #        else:
##   #            pass
##   #        del new_cit_resp_party_email, new_cit_resp_party_root
##   #        #print(etree.tostring(idCitation, pretty_print=True, encoding="utf-8").decode())
##   #        del xml, citRespParty

        del contact_dict, mdContact_root, mdContact_email
        del mdContact
        # #######################################################################
        #               ###--->>> mdContact section End <<<---###
        # #######################################################################

        mdDateSt = target_tree.xpath(f"./mdDateSt")
        if len(mdDateSt) == 0:
            #print(f"Inserting 'mdDateSt' at position: {root_dict['mdDateSt']}")
            xml = '<mdDateSt Sync="TRUE">20250129</mdDateSt>'
            root = etree.XML(xml)
            position = root_dict['mdDateSt']
            target_root.insert(position, root)
            del position, root, xml
        elif len(mdDateSt) == 1:
            #print(f"Updating '{mdDateSt[0].tag}' if needed at position: {target_root.index(target_root.xpath(f'./mdDateSt')[0])}")
            position = root_dict['mdDateSt']
            target_root.insert(position, mdDateSt[0])
            del position
        elif len(mdDateSt) > 1:
            # if it is multiples, is that ok or not. eainfo has multiples, topic does, contacts
            print(f"Removing {len(mdDateSt)-1} mdDateSt elements")
            for i in range(1, len(mdDateSt)):
                target_root.remove(mdDateSt[i])
                i+=1
                del i
        else:
            pass
        #print(etree.tostring(idCitation, pretty_print=True, encoding="utf-8").decode())
        del mdDateSt

        mdFileID = target_tree.xpath(f"./mdFileID")
        if len(mdFileID) == 0:
            #print(f"Inserting 'mdFileID' at position: {root_dict['mdFileID']}")
            xml = '<mdFileID>gov.noaa.nmfs.inport:</mdFileID>'
            root = etree.XML(xml)
            position = root_dict['mdFileID']
            target_root.insert(position, root)
            del position, root, xml
        elif len(mdFileID) == 1:
            #print(f"Updating '{mdFileID[0].tag}' if needed at position: {target_root.index(target_root.xpath(f'./mdFileID')[0])}")
            position = root_dict['mdFileID']
            target_root.insert(position, mdFileID[0])
            del position
        elif len(mdFileID) > 1:
            # if it is multiples, is that ok or not. eainfo has multiples, topic does, contacts
            print(f"Removing {len(mdFileID)-1} mdFileID elements")
            for i in range(1, len(mdFileID)):
                target_root.remove(mdFileID[i])
                i+=1
                del i
        else:
            pass
        del mdFileID

        mdLang = target_tree.xpath(f"./mdLang")
        if len(mdLang) == 0:
            #print(f"Inserting 'mdLang' at position: {root_dict['mdLang']}")
            xml = '<mdLang><languageCode value="eng" Sync="TRUE"></languageCode><countryCode value="USA" Sync="TRUE"></countryCode></mdLang>'
            root = etree.XML(xml)
            position = root_dict['mdLang']
            target_root.insert(position, root)
            del position, root, xml
        elif len(mdLang) == 1:
            #print(f"Updating '{mdLang[0].tag}' if needed at position: {target_root.index(target_root.xpath(f'./{mdLang[0].tag}')[0])}")
            position = root_dict['mdLang']
            target_root.insert(position, mdLang[0])
            del position
        elif len(mdLang) > 1:
            # if it is multiples, is that ok or not. eainfo has multiples, topic does, contacts
            print(f"Removing {len(mdLang)-1} mdLang elements")
            for i in range(1, len(mdLang)):
                target_root.remove(mdLang[i])
                i+=1
                del i
        else:
            pass
        del mdLang

        mdMaint = target_tree.xpath(f"./mdMaint")
        if len(mdMaint) == 0:
            #print(f"Inserting 'mdMaint' at position: {root_dict['mdMaint']}")
            xml = '<mdMaint><maintFreq><MaintFreqCd value="009"></MaintFreqCd></maintFreq></mdMaint>'
            root = etree.XML(xml)
            position = root_dict['mdMaint']
            target_root.insert(position, root)
            del position, root, xml
        elif len(mdMaint) == 1:
            #print(f"Updating '{mdMaint[0].tag}' if needed at position: {target_root.index(target_root.xpath(f'./{mdMaint[0].tag}')[0])}")
            position = root_dict['mdMaint']
            target_root.insert(position, mdMaint[0])
            del position
        elif len(mdLang) > 1:
            # if it is multiples, is that ok or not. eainfo has multiples, topic does, contacts
            print(f"Removing {len(mdMaint)-1} mdMaint elements")
            for i in range(1, len(mdMaint)):
                target_root.remove(mdMaint[i])
                i+=1
                del i
        else:
            pass
        del mdMaint

        mdHrLv = target_tree.xpath(f"./mdHrLv")
        if len(mdHrLv) == 0:
            #print(f"Inserting mdHrLv at position: {root_dict['mdHrLv']}")
            xml = '<mdHrLv><ScopeCd value="005" Sync="TRUE"></ScopeCd></mdHrLv>'
            root = etree.XML(xml)
            position = root_dict['mdHrLv']
            target_root.insert(position, root)
            del position, root, xml
        elif len(mdHrLv) == 1:
            #print(f"Updating '{mdHrLv[0].tag}' if needed at position: {target_root.index(target_root.xpath(f'./{mdHrLv[0].tag}')[0])}")
            position = root_dict['mdHrLv']
            target_root.insert(position, mdHrLv[0])
            del position
        elif len(mdLang) > 1:
            # if it is multiples, is that ok or not. eainfo has multiples, topic does, contacts
            print(f"Removing {len(mdHrLv)-1} mdHrLv elements")
            for i in range(1, len(mdHrLv)):
                target_root.remove(mdHrLv[i])
                i+=1
                del i
        else:
            pass
        del mdHrLv

        mdHrLvName  = target_tree.xpath(f"./mdHrLvName")
        if len(mdHrLvName) == 0:
            #print(f"Inserting 'mdHrLvName' at position: {root_dict['mdHrLvName']}")
            xml = '<mdHrLvName Sync="TRUE">dataset</mdHrLvName>'
            root = etree.XML(xml)
            position = root_dict['mdHrLvName']
            target_root.insert(position, root)
            del position, root, xml
        elif len(mdHrLvName) == 1:
            #print(f"Updating '{mdHrLvName[0].tag}' if needed at position: {target_root.index(target_root.xpath(f'./{mdHrLvName[0].tag}')[0])}")
            position = root_dict['mdHrLvName']
            target_root.insert(position, mdHrLvName[0])
            del position
        elif len(mdHrLvName) > 1:
            # if it is multiples, is that ok or not. eainfo has multiples, topic does, contacts
            print(f"Removing {len(mdHrLvName)-1} mdHrLvName elements")
            for i in range(1, len(mdHrLvName)):
                target_root.remove(mdHrLvName[i])
                i+=1
                del i
        else:
            pass
        del mdHrLvName

         # ###--->>> These elements are in vrey few xlm files
         #mdStanName  = target_tree.xpath(f"./mdStanName")
         #if len(mdStanName) == 0:
         #    print(f"Inserting 'mdStanName' at position: {root_dict['mdStanName']}")
         #    xml = '<mdStanName Sync="TRUE"></mdStanName>'
         #    root = etree.XML(xml)
         #    position = root_dict['mdStanName']
         #    target_root.insert(position, root)
         #    del position, root, xml
         #elif len(mdStanName) == 1:
         #    print(f"Updating '{mdStanName[0].tag}'if needed at position: {target_root.index(target_root.xpath(f'./{mdStanName[0].tag}')[0])}")
         #    position = root_dict['mdStanName']
         #    target_root.insert(position, mdStanName[0])
         #    del position
         #elif len(mdStanName) > 1:
         #    # if it is multiples, is that ok or not. eainfo has multiples, topic does, contacts
         #    print(f"Removing {len(mdStanName)-1} mdStanName elements")
         #    for i in range(1, len(mdStanName)):
         #        target_root.remove(mdStanName[i])
         #        i+=1
         #        del i
         #else:
         #    pass
         #del mdStanName
         #
         #mdStanVer   = target_tree.xpath(f"./mdStanVer")
         #if len(mdStanVer) == 0:
         #    print(f"Inserting 'mdStanVer' at position: {root_dict['mdStanVer']}")
         #    xml = '<mdStanVer Sync="TRUE"></mdStanVer>'
         #    root = etree.XML(xml)
         #    position = root_dict['mdStanVer']
         #    target_root.insert(position, root)
         #    del position, root, xml
         #elif len(mdStanVer) == 1:
         #    print(f"Updating '{mdStanVer[0].tag}' if needed at position: {target_root.index(target_root.xpath(f'./{mdStanVer[0].tag}')[0])}")
         #    position = root_dict['mdStanVer']
         #    target_root.insert(position, mdStanVer[0])
         #    del position
         #elif len(mdStanVer) > 1:
         #    # if it is multiples, is that ok or not. eainfo has multiples, topic does, contacts
         #    print(f"Removing {len(mdStanVer)-1} mdStanVer elements")
         #    for i in range(1, len(mdStanVer)):
         #        target_root.remove(mdStanVer[i])
         #        i+=1
         #        del i
         #else:
         #    pass
         #del mdStanVer

        refSysInfo  = target_tree.xpath(f"./refSysInfo")
        if len(refSysInfo) == 0:
            #print(f"Inserting 'refSysInfo' at position: {root_dict['refSysInfo']}")
            xml = '<refSysInfo Sync="TRUE"></refSysInfo>'
            root = etree.XML(xml)
            position = root_dict['refSysInfo']
            target_root.insert(position, root)
            del position, root, xml
        elif len(refSysInfo) == 1:
            #print(f"Updating '{refSysInfo[0].tag}' if needed at position: {root_dict['refSysInfo']}")
            position = root_dict['refSysInfo']
            target_root.insert(position, refSysInfo[0])
            del position
        elif len(refSysInfo) > 1:
            # if it is multiples, is that ok or not. eainfo has multiples, topic does, contacts
            print(f"Removing {len(refSysInfo)-1} refSysInfo elements")
            for i in range(1, len(refSysInfo)):
                target_root.remove(refSysInfo[i])
                i+=1
                del i
        else:
            pass
        del refSysInfo

        spatRepInfo = target_tree.xpath(f"./spatRepInfo")
        if len(spatRepInfo) == 0:
            #print(f"Inserting 'spatRepInfo' at position: {root_dict['spatRepInfo']}")
            xml = '''<spatRepInfo><VectSpatRep><geometObjs Name="SpeciesRangeTemplate" Sync="TRUE">
                     <geoObjTyp><GeoObjTypCd value="002" Sync="TRUE"></GeoObjTypCd></geoObjTyp>
                     <geoObjCnt Sync="TRUE">2</geoObjCnt></geometObjs><topLvl>
                     <TopoLevCd value="001" Sync="TRUE"></TopoLevCd></topLvl>
                     </VectSpatRep></spatRepInfo>'''
            root = etree.XML(xml)
            position = root_dict['spatRepInfo']
            target_root.insert(position, root)
            del position, root, xml
        elif len(spatRepInfo) == 1:
            #print(f"Updating '{spatRepInfo[0].tag}' if needed at position: {root_dict['spatRepInfo']}")
            #xml = '''<spatRepInfo><VectSpatRep><geometObjs Name="SpeciesRangeTemplate" Sync="TRUE">
            #         <geoObjTyp><GeoObjTypCd value="002" Sync="TRUE"></GeoObjTypCd></geoObjTyp>
            #         <geoObjCnt Sync="TRUE">2</geoObjCnt></geometObjs><topLvl>
            #         <TopoLevCd value="001" Sync="TRUE"></TopoLevCd></topLvl>
            #         </VectSpatRep></spatRepInfo>'''
            #root = etree.XML(xml)
            position = root_dict['spatRepInfo']
            target_root.insert(position, spatRepInfo[0])
            del position #, root, xml
        elif len(spatRepInfo) > 1:
            # if it is multiples, is that ok or not. eainfo has multiples, topic does, contacts
            print(f"Removing {len(spatRepInfo)-1} spatRepInfo elements")
            for i in range(1, len(spatRepInfo)):
                target_root.remove(spatRepInfo[i])
                i+=1
                del i
        else:
            pass
        del spatRepInfo

        spdoinfo = target_tree.xpath(f"./spdoinfo")
        if len(spdoinfo) == 0:
            #print(f"Inserting 'spdoinfo' at position: {root_dict['spdoinfo']}")
            xml = '''<spdoinfo Sync="TRUE"></spdoinfo>'''
            root = etree.XML(xml)
            position = root_dict['spdoinfo']
            target_root.insert(position, root)
            del position, root, xml
        elif len(spdoinfo) == 1:
            #print(f"Updating '{spdoinfo[0].tag}' if needed at position: {root_dict['spdoinfo']}")
            position = root_dict['spdoinfo']
            target_root.insert(position, spdoinfo[0])
            del position
        elif len(spdoinfo) > 1:
            # if it is multiples, is that ok or not. eainfo has multiples, topic does, contacts
            print(f"Removing {len(spdoinfo)-1} spdoinfo elements")
            for i in range(1, len(spdoinfo)):
                target_root.remove(spdoinfo[i])
                i+=1
                del i
        else:
            pass
        del spdoinfo

        # #######################################################################
        #               ###--->>> metadata detail section End <<<---###
        # #######################################################################

        # #######################################################################
        #               ###--->>> dqInfo section Start <<<---###
        # #######################################################################
        dqInfo = target_tree.xpath(f"./dqInfo")
        if len(dqInfo) == 0:
            #print(f"Inserting 'dqInfo' at position: {root_dict['dqInfo']}")
            xml = '''<dqInfo>
                        <dqScope xmlns="">
                            <scpLvl>
                                <ScopeCd value="005"></ScopeCd>
                            </scpLvl>
                            <scpLvlDesc xmlns="">
                                <datasetSet>Feature Class</datasetSet>
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
                        </dataLineage>
                    </dqInfo>'''
            root = etree.XML(xml)
            position = root_dict['dqInfo']
            target_root.insert(position, root)
            del position, root, xml
        elif len(dqInfo) == 1:
            #print(f"Updating '{dqInfo[0].tag}' if needed at position: {root_dict['dqInfo']}")
            position = root_dict['dqInfo']
            target_root.insert(position, dqInfo[0])
            del position
        elif len(dqInfo) > 1:
            # if it is multiples, is that ok or not. eainfo has multiples, topic does, contacts
            #print(f"Removing {len(dqInfo)-1} dqInfo elements")
            for i in range(1, len(dqInfo)):
                target_root.remove(dqInfo[i])
                i+=1
                del i
        else:
            pass
        del dqInfo

        dqInfo_dict = { "dqScope" : 0, "scpLvl" : 0, "ScopeCd" : 0,
                        "scpLvlDesc" : 1, "datasetSet" : 0, "report" : 1,
                        "measDesc" : 0, "report" : 2, "measDesc" : 0,
                        "dataLineage" : 3, "statement" : 0, "dataSource" : 1,
                        "srcDesc" : 0, "srcCitatn" : 1, "resTitle" : 0,
                        "date" : 1, "createDate" : 0, "prcStep" : 2,
                        "stepDesc" : 0, "stepProc" : 1, "stepDateTm" : 2,
                      }

        dqInfo  = target_tree.xpath(f"./dqInfo")
        dqScope = dqInfo[0].xpath(f"./dqScope")
        if len(dqScope) == 0:
            #print(f"Inserting 'dqScope' at position: {dqInfo_dict['dqScope']}")
            xml = '''<dqScope xmlns=""><scpLvl><ScopeCd value="005"></ScopeCd></scpLvl><scpLvlDesc xmlns=""><datasetSet>Feature Class</datasetSet></scpLvlDesc></dqScope>'''
            root = etree.XML(xml)
            position = dqInfo_dict['dqScope']
            dqInfo[0].insert(position, root)
            del position, root, xml
        elif len(dqScope) == 1:
            #print(f"Updating '{dqScope[0].tag}' if needed at position: {dqInfo_dict['dqScope']}")
            #xml = '''<dqScope xmlns=""><scpLvl><ScopeCd value="005"></ScopeCd></scpLvl><scpLvlDesc xmlns=""><datasetSet>Feature Class</datasetSet></scpLvlDesc></dqScope>'''
            #root = etree.XML(xml)
            #position = dqInfo_dict["dqScope"]
            #dqInfo[0].insert(position, root)
            #del position, root, xml
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

        dqInfo  = target_tree.xpath(f"./dqInfo")
        report = dqInfo[0].xpath(f"./report")
        if len(report) == 0:
            #print(f"Inserting 'report' at position: {dqInfo_dict['report']}")
            xml = '''<report type="DQConcConsis" dimension="horizontal">
                        <measDesc>Based on a review from species' experts, we determined that all necessary features were included in the species' range file.</measDesc>
                     </report>'''
            root = etree.XML(xml)
            position = dqInfo_dict['report']
            dqInfo[0].insert(position, root)
            del position, root, xml

            #print(f"Inserting 'report' at position: {dqInfo_dict['report']+1}")
            xml = '''<report type="DQCompOm" dimension="horizontal">
                        <measDesc>Based on a review from species' experts, we determined that all necessary features were included in the species' range file.</measDesc>
                     </report>'''
            root = etree.XML(xml)
            position = dqInfo_dict['report']
            dqInfo[0].insert(position+1, root)
            del position, root, xml

        elif len(report) == 1:
            #print(f"Updating '{report[0].tag}' if needed at position: {dqInfo_dict['report']}")
            _report = dqInfo[0].xpath(f"./report[@type='DQConcConsis']")
            if len(_report) == 1:
                xml = '''<report type="DQConcConsis" dimension="horizontal">
                            <measDesc>Based on a review from species' experts, we determined that all necessary features were included in the species' range file.</measDesc>
                         </report>'''
                root = etree.XML(xml)
                dqInfo[0].replace(_report[0], root)
                del root, xml

                xml = '''<report type="DQCompOm" dimension="horizontal">
                            <measDesc>Based on a review from species' experts, we determined that all necessary features were included in the species' range file.</measDesc>
                         </report>'''
                root = etree.XML(xml)
                position = dqInfo_dict["report"]+1
                dqInfo[0].insert(position, root)
                del position, root, xml

            elif len(_report) > 1:
                dqInfo[0].remove(_report[-1])
            del _report

            _report = dqInfo[0].xpath(f"./report[@type='DQCompOm']")
            if len(_report) == 1:
                xml = '''<report type="DQCompOm" dimension="horizontal">
                            <measDesc>Based on a review from species' experts, we determined that all necessary features were included in the species' range file.</measDesc>
                         </report>'''
                root = etree.XML(xml)
                dqInfo[0].replace(_report[0], root)
                del root, xml

                xml = '''<report type="DQConcConsis" dimension="horizontal">
                            <measDesc>Based on a review from species' experts, we determined that all necessary features were included in the species' range file.</measDesc>
                         </report>'''
                root = etree.XML(xml)
                position = dqInfo_dict["report"]
                dqInfo[0].insert(position, root)
                del position, root, xml

            elif len(_report) > 1:
                dqInfo[0].remove(_report[-1])
            del _report

            #root = etree.XML(xml)
            #position = dqInfo_dict["report"]
            #dqInfo[0].insert(position, root)
            #del position, root, xml
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

        dqInfo  = target_tree.xpath(f"./dqInfo")
        dataLineage = dqInfo[0].xpath(f"./dataLineage")
        if len(dataLineage) == 0:
            print(f"Inserting 'dataLineage' at position: {dqInfo_dict['dataLineage']}")
            xml = '''<dataLineage>
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
            root = etree.XML(xml)
            position = dqInfo_dict['dataLineage']
            dqInfo[0].insert(position, root)
            del position, root, xml
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

        del contact_dict
        del dqInfo_dict

        # #######################################################################
        #               ###--->>> dqInfo section End <<<---###
        # #######################################################################

##        # #######################################################################
##        #               ###--->>> distInfo section Start <<<---###
##        # #######################################################################
##        distInfo    = target_tree.xpath(f"./distInfo")
##        if len(distInfo) == 0:
##            print(f"Inserting 'distInfo' at position: {root_dict['distInfo']}")
##            xml = '<distInfo Sync="TRUE"></distInfo>'
##            root = etree.XML(xml)
##            position = root_dict['distInfo']
##            target_root.insert(position, root)
##            del position, root, xml
##        elif len(distInfo) == 1:
##            print(f"Updating '{distInfo[0].tag}' if needed at position: {root_dict['distInfo']}")
##            position = root_dict['distInfo']
##            target_root.insert(position, distInfo[0])
##            del position
##        elif len(distInfo) > 1:
##            # if it is multiples, is that ok or not. eainfo has multiples, topic does, contacts
##            print(f"Removing {len(distInfo)-1} distInfo elements")
##            for i in range(1, len(distInfo)):
##                target_root.remove(distInfo[i])
##                i+=1
##                del i
##        else:
##            pass
##        del distInfo
##        # #######################################################################
##        #               ###--->>> distInfo section End <<<---###
##        # #######################################################################
##
##        # #######################################################################
##        #               ###--->>> eainfo section Start <<<---###
##        # #######################################################################
##        eainfo      = target_tree.xpath(f"./eainfo")
##        if len(eainfo) == 0:
##            print(f"Inserting 'eainfo' at position: {root_dict['eainfo']}")
##            xml = '<eainfo Sync="TRUE"></eainfo>'
##            root = etree.XML(xml)
##            position = root_dict['eainfo']
##            target_root.insert(position, root)
##            del position, root, xml
##        elif len(eainfo) == 1:
##            print(f"Updating '{eainfo[0].tag}' if needed at position: {root_dict['eainfo']}")
##            position = root_dict['eainfo']
##            target_root.insert(position, eainfo[0])
##            del position
##        elif len(eainfo) > 1:
##            # if it is multiples, is that ok or not. eainfo has multiples, topic does, contacts
##            print(f"Removing {len(eainfo)-1} eainfo elements")
##            for i in range(1, len(eainfo)):
##                target_root.remove(eainfo[i])
##                i+=1
##                del i
##        else:
##            pass
##        del eainfo
##        # ######################################################################
##        #               ###--->>> eainfo section End <<<---###
##        # ######################################################################
##
##        # ######################################################################
##        #               ###--->>> Binary section Start <<<---###
##        # ######################################################################
##        Binary      = target_tree.xpath(f"./Binary")
##        if len(Binary) == 0:
##            print(f"Inserting 'Binary' at position: {root_dict['Binary']}")
##            xml = '<Binary Sync="TRUE"><Thumbnail><Data EsriPropertyType="PictureX"></Data></Thumbnail></Binary>'
##            root = etree.XML(xml)
##            position = root_dict['Binary']
##            target_root.insert(position, root)
##            del position, root, xml
##        elif len(Binary) == 1:
##            print(f"Updating '{Binary[0].tag}' if needed at position: {root_dict['Binary']}")
##            position = root_dict['Binary']
##            target_root.insert(position, Binary[0])
##            del position
##        elif len(Binary) > 1:
##            # if it is multiples, is that ok or not. Binary has multiples, topic does, contacts
##            print(f"Removing {len(Binary)-1} Binary elements")
##            for i in range(1, len(Binary)):
##                target_root.remove(Binary[i])
##                i+=1
##                del i
##        else:
##            pass
##        del Binary
##        # ######################################################################
##        #               ###--->>> Binary section End <<<---###
##        # ######################################################################
##
##        #etree.indent(target_root, space='    ')
##        #etree.dump(target_root)
##
##        #etree.indent(target_root, space="    ")
##        #print(etree.tostring(target_root, xml_declaration=True, encoding="utf-8").decode())



##        # Parse the XML
##        parser = etree.XMLParser(remove_blank_text=True, encoding='UTF-8')
##        target_name = os.path.basename(fc_metadata_xml_file).replace(".xml", "")
##        target_tree = etree.parse(fc_metadata_xml_file, parser=parser)
##        target_root = target_tree.getroot()
##        del parser


        etree.indent(target_root, space='')
        #target_xml_string = etree.tostring(target_tree, pretty_print=True, method='html', encoding="utf-8", xml_declaration=True).decode()
        target_xml_string = etree.tostring(target_tree, xml_declaration=True).decode()
        #print(target_xml_string)
        try:
            with open(fc_metadata_xml_file, "w") as f:
                f.write(target_xml_string)
            del f
        except:
            print(f"The metadata file: {os.path.basename(fc_metadata_xml_file)} can not be overwritten!!")
        del target_xml_string

        pretty_format_xml_file(fc_metadata_xml_file)

        # Declare Variables
        del root_dict
        del target_tree, target_root, target_name
        # Imports
        del etree, StringIO, arcpy, md, pretty_format_xml_file
        # Function Parameters
        del species_range_fc, fc_metadata_xml_file

    except:
        traceback.print_exc()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function: ##--> '{', '.join(rk)}' <--##"); del rk
        return True
    finally:
        pass

def insert_xml_elements(fc_metadata_xml_file=""):
    try:
        # Imports
        from lxml import etree
        from io import StringIO
        import arcpy
        from arcpy import metadata as md
        # Project modules
        from src.project_tools import pretty_format_xml_file

        def insert_element(tree, element, xml):
            try:
                _element = tree.xpath(f"./{element}")[0]
                root = etree.XML(xml)
                target_root.replace(_element, root)
                del root, _element
                del tree, element, xml
            except:
                traceback.print_exc()

        # Create the root element
        root = etree.Element("metadata")
        #root.attrib[QName("http://www.w3.org/XML/1998/namespace", "lang")] = "en-US"
        root.set("{http://www.w3.org/XML/1998/namespace}lang", "en-US")
        # Serialize the tree to a string
        xml_string = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="utf-8").decode()
        #print(xml_string)
        del root


        #etree.indent(target_root, space='')
        #target_xml_string = etree.tostring(target_tree, pretty_print=True, method='html', encoding="utf-8", xml_declaration=True).decode()
        #target_xml_string = etree.tostring(target_tree, xml_declaration=True).decode()
        #print(target_xml_string)
        try:
            with open(fc_metadata_xml_file, "w") as f:
                f.write(xml_string)
            del f
        except:
            print(f"The metadata file: {os.path.basename(fc_metadata_xml_file)} can not be overwritten!!")
        del xml_string
        #pretty_format_xml_file(fc_metadata_xml_file)

        # Parse the XML
        parser = etree.XMLParser(remove_blank_text=True, encoding='UTF-8')
        target_name = os.path.basename(fc_metadata_xml_file).replace(".xml", "")
        target_tree = etree.parse(fc_metadata_xml_file, parser=parser)
        target_root = target_tree.getroot()
        del parser

        #etree.indent(target_root, space="    ")
        #print(etree.tostring(target_root, xml_declaration=True, encoding="utf-8").decode())

        # ######################################################################
        #               ###--->>> Esri section Start <<<---###
        # ######################################################################

        root_dict = {"Esri"       :  0, "dataIdInfo" :  1, "mdChar"      :  2,
                     "mdContact"  :  3, "mdDateSt"   :  4, "mdFileID"    :  5,
                     "mdLang"     :  6, "mdMaint"    :  7, "mdHrLv"      :  8,
                     "mdHrLvName" :  9, "refSysInfo" : 10, "spatRepInfo" : 11,
                     "spdoinfo"   : 12, "dqInfo"     : 13, "distInfo"    : 14,
                     "eainfo"     : 15, "contInfo"   : 16, "spref"       : 17,
                     "spatRepInfo" : 18, "dataSetFn" : 19, "Binary"      : 100,}

        for key in root_dict:
            print(f"Inserting: {key}")
            element = etree.SubElement(target_root, f"{key}")
            target_root.append(element)
            del element
            del key
        root_dict

        # ###--->>> Esri section <<<---###
        element = "Esri"
        print(f"Replacing {element} root")
        xml = '''<Esri>
                    <CreaDate></CreaDate>
                    <CreaTime></CreaTime>
                    <ArcGISFormat>1.0</ArcGISFormat>
                    <ArcGISStyle>ISO 19139 Metadata Implementation Specification</ArcGISStyle>
                    <SyncOnce>FALSE</SyncOnce>
                    <DataProperties>
                        <itemProps>
                            <itemName Sync="TRUE"></itemName>
                            <imsContentType Sync="TRUE">002</imsContentType>
                            <nativeExtBox>
                                <westBL Sync="TRUE"></westBL>
                                <eastBL Sync="TRUE"></eastBL>
                                <southBL Sync="TRUE"></southBL>
                                <northBL Sync="TRUE"></northBL>
                                <exTypeCode Sync="TRUE">1</exTypeCode>
                            </nativeExtBox>
                        </itemProps>
                        <coordRef>
                            <type Sync="TRUE"></type>
                            <geogcsn Sync="TRUE"></geogcsn>
                            <csUnits Sync="TRUE"></csUnits>
                            <peXml Sync="TRUE"></peXml>
                        </coordRef>
                    </DataProperties>
                    <SyncDate></SyncDate>
                    <SyncTime></SyncTime>
                    <ModDate></ModDate>
                    <ModTime></ModTime>
                    <scaleRange>
                        <minScale>150000000</minScale>
                        <maxScale>5000</maxScale>
                    </scaleRange>
                    <ArcGISProfile>ISO19139</ArcGISProfile>
                </Esri>'''
        insert_element(target_tree, element, xml)
        del xml, element

        # ###--->>> dataIdInfo section <<<---###
        element = "dataIdInfo"
        print(f"Replacing {element} root")
        xml = '''<dataIdInfo>
                    <idCitation>
                        <resTitle/>
                        <resAltTitle/>
                        <collTitle/>
                        <presForm>
                            <PresFormCd>
                                <PresFormCd value="005" Sync="TRUE"></PresFormCd>
                                <fgdcGeoform>vector digital data</fgdcGeoform>
                            </PresFormCd>
                        </presForm>
                        <date>
                            <createDate/>
                            <pubDate/>
                            <revisedDate/>
                        </date>
                        <citRespParty>
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
                        </citRespParty>
                    </idCitation>
                    <searchKeys/>
                    <idPurp/>
                    <idAbs/>
                    <idCredit/>
                    <resConst/>
                    <envirDesc Sync="TRUE">Esri ArcGIS 13.4.0.55405</envirDesc>
                    <dataLang/>
                    <spatRpType>
                        <SpatRepTypCd value="001" Sync="TRUE"></SpatRepTypCd>
                    </spatRpType>
                    <dataExt/>
                    <tpCat><TopicCatCd value="002"></TopicCatCd></tpCat>
                    <tpCat><TopicCatCd value="007"></TopicCatCd></tpCat>
                    <tpCat><TopicCatCd value="014"></TopicCatCd></tpCat>
                 </dataIdInfo>'''
        insert_element(target_tree, element, xml)
        del xml, element

        # ###--->>> mdChar section <<<---###
        element = "mdChar"
        print(f"Replacing {element} root")
        xml = '''<mdChar>
                    <CharSetCd value="004" Sync="TRUE"/>
                 </mdChar>'''
        insert_element(target_tree, element, xml)
        del xml, element

        # ###--->>> mdContact section <<<---###
        element = "mdContact"
        print(f"Replacing {element} root")
        xml = '''<mdContact>
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
                    </mdContact>'''
        insert_element(target_tree, element, xml)
        del xml, element

        # ###--->>> mdDateSt section <<<---###
        element = "mdDateSt"
        print(f"Replacing {element} root")
        xml = '''<mdDateSt Sync="TRUE">20250129</mdDateSt>'''
        insert_element(target_tree, element, xml)
        del xml, element

        # ###--->>> mdFileID section <<<---###
        element = "mdFileID"
        print(f"Replacing {element} root")
        xml = '''<mdFileID>gov.noaa.nmfs.inport:</mdFileID>'''
        insert_element(target_tree, element, xml)
        del xml, element

        # ###--->>> mdLang section <<<---###
        element = "mdLang"
        print(f"Replacing {element} root")
        xml = '''<mdLang>
                    <languageCode value="eng" Sync="TRUE"></languageCode>
                    <countryCode value="USA" Sync="TRUE"></countryCode>
                 </mdLang>'''
        insert_element(target_tree, element, xml)
        del xml, element

        # ###--->>> mdMaint section <<<---###
        element = "mdMaint"
        print(f"Replacing {element} root")
        xml = '''<mdMaint>
                    <maintFreq>
                        <MaintFreqCd value="009"></MaintFreqCd>
                    </maintFreq>
                 </mdMaint>'''
        insert_element(target_tree, element, xml)
        del xml, element

        # ###--->>> mdHrLv section <<<---###
        element = "mdHrLv"
        print(f"Replacing {element} root")
        xml = '''<mdHrLv>
                    <ScopeCd value="005" Sync="TRUE"></ScopeCd>
                 </mdHrLv>'''
        insert_element(target_tree, element, xml)
        del xml, element

        # ###--->>> mdHrLvName section <<<---###
        element = "mdHrLvName"
        print(f"Replacing {element} root")
        xml = '''<mdHrLvName Sync="TRUE">dataset</mdHrLvName>'''
        insert_element(target_tree, element, xml)
        del xml, element

        # ###--->>> refSysInfo section <<<---###
        element = "refSysInfo"
        print(f"Replacing {element} root")
        xml = '''<refSysInfo>
                    <RefSystem dimension="horizontal">
                        <refSysID>
                            <identCode code="4326" Sync="TRUE"/>
                            <idCodeSpace Sync="TRUE">EPSG</idCodeSpace>
                            <idVersion Sync="TRUE">6.2(3.0.1)</idVersion>
                        </refSysID>
                    </RefSystem>
                 </refSysInfo>'''
        insert_element(target_tree, element, xml)
        del xml, element

        # ###--->>> spatRepInfo section <<<---###
        element = "spatRepInfo"
        print(f"Replacing {element} root")
        xml = '''<spatRepInfo>
                    <VectSpatRep>
                        <geometObjs Name="SpeciesRangeTemplate" Sync="TRUE">
                            <geoObjTyp>
                                <GeoObjTypCd value="002" Sync="TRUE"/>
                            </geoObjTyp>
                            <geoObjCnt Sync="TRUE">2</geoObjCnt>
                        </geometObjs>
                        <topLvl>
                            <TopoLevCd value="001" Sync="TRUE"/>
                        </topLvl>
                    </VectSpatRep>
                 </spatRepInfo>'''
        insert_element(target_tree, element, xml)
        del xml, element

        # ###--->>> spdoinfo section <<<---###
        element = "spdoinfo"
        print(f"Replacing {element} root")
        xml = '''<spdoinfo>
                    <ptvctinf>
                        <esriterm Name="AbaloneBlack_20210712" Sync="TRUE">
                            <efeatyp Sync="TRUE">Simple</efeatyp>
                            <efeageom code="4" Sync="TRUE"></efeageom>
                            <esritopo Sync="TRUE">FALSE</esritopo>
                            <efeacnt Sync="TRUE">1</efeacnt>
                            <spindex Sync="TRUE">TRUE</spindex>
                            <linrefer Sync="TRUE">FALSE</linrefer>
                        </esriterm>
                    </ptvctinf>
                </spdoinfo>'''
        insert_element(target_tree, element, xml)
        del xml, element

        # ###--->>> dqInfo section <<<---###
        element = "dqInfo"
        print(f"Replacing {element} root")
        xml = '''<dqInfo>
                    <dqScope xmlns="">
                        <scpLvl>
                            <ScopeCd value="005"/>
                        </scpLvl>
                        <scpLvlDesc>
                            <datasetSet>Feature Class</datasetSet>
                        </scpLvlDesc>
                    </dqScope>
                    <report type="DQConcConsis" dimension="horizontal">
                        <measDesc>Based on a review from species' experts, we determined that all necessary features were included in the species' range file.</measDesc>
                    </report>
                    <report type="DQCompOm" dimension="horizontal">
                        <measDesc>Based on a review from species' experts, we determined that all necessary features were included in the species' range file.</measDesc>
                    </report>
                    <dataLineage>
                        <statement/>
                        <dataSource type="">
                            <srcDesc/>
                            <srcCitatn>
                                <resTitle/>
                                <date>
                                    <createDate/>
                                </date>
                            </srcCitatn>
                        </dataSource>
                        <prcStep>
                            <stepDesc/>
                            <stepProc>
                                <editorSource>extermal</editorSource>
                                <editorDigest/>
                                <rpIndName/>
                                <rpOrgName/>
                                <rpPosName/>
                                <rpCntInfo>
                                    <cntAddress addressType="both">
                                        <delPoint/>
                                        <city/>
                                        <adminArea/>
                                        <postCode/>
                                        <eMailAdd/>
                                        <country/>
                                    </cntAddress>
                                    <cntPhone>
                                        <voiceNum tddtty=""/>
                                        <faxNum/>
                                    </cntPhone>
                                    <cntHours/>
                                    <cntOnlineRes>
                                        <linkage/>
                                        <protocol>REST Service</protocol>
                                        <orName/>
                                        <orDesc/>
                                        <orFunct>
                                            <OnFunctCd value="002"/>
                                        </orFunct>
                                    </cntOnlineRes>
                                </rpCntInfo>
                                <editorSave>True</editorSave>
                                <displayName/>
                                <role>
                                    <RoleCd value="009"/>
                                </role>
                            </stepProc>
                            <stepDateTm/>
                        </prcStep>
                    </dataLineage>
                </dqInfo>'''
        insert_element(target_tree, element, xml)
        del xml, element

        # ###--->>> distInfo section <<<---###
        element = "distInfo"
        print(f"Replacing {element} root")
        xml = '''<distInfo>
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
                                    <country>US</country>
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
                    <distTranOps>
                        <unitsODist>MB</unitsODist>
                        <transSize>0</transSize>
                        <onLineSrc>
                            <linkage></linkage>
                            <protocol>REST Services</protocol>
                            <orFunct>
                                <OnFunctCd value="001"></OnFunctCd>
                            </orFunct>
                        </onLineSrc>
                    </distTranOps>
                </distInfo>'''
        insert_element(target_tree, element, xml)
        del xml, element

        # ###--->>> eainfo section <<<---###
        element = "eainfo"
        print(f"Replacing {element} root")
        xml = '''<eainfo>
                    <detailed xmlns="" Name="" Sync="TRUE">
                        <enttyp>
                            <enttypl Sync="TRUE">Attribute Table Fields</enttypl>
                            <enttypt Sync="TRUE">Feature Class</enttypt>
                            <enttypc Sync="TRUE">1</enttypc>
                            <enttypd>A collection of geographic features with the same geometry type.</enttypd>
                            <enttypds>Esri</enttypds>
                        </enttyp>
                        <attr>
                            <attrlabl Sync="TRUE">OBJECTID</attrlabl>
                            <attalias Sync="TRUE">OBJECTID</attalias>
                            <attrtype Sync="TRUE">OID</attrtype>
                            <attwidth Sync="TRUE">4</attwidth>
                            <atprecis Sync="TRUE">0</atprecis>
                            <attscale Sync="TRUE">0</attscale>
                            <attrdef Sync="TRUE">Internal feature number.</attrdef>
                            <attrdefs Sync="TRUE">Esri</attrdefs>
                            <attrdomv>
                                <udom Sync="TRUE">Sequential unique whole numbers that are automatically generated.</udom>
                            </attrdomv>
                        </attr>
                        <attr>
                            <attrlabl Sync="TRUE">Shape</attrlabl>
                            <attalias Sync="TRUE">Shape</attalias>
                            <attrtype Sync="TRUE">Geometry</attrtype>
                            <attwidth Sync="TRUE">0</attwidth>
                            <atprecis Sync="TRUE">0</atprecis>
                            <attscale Sync="TRUE">0</attscale>
                            <attrdef Sync="TRUE">Feature geometry.</attrdef>
                            <attrdefs Sync="TRUE">Esri</attrdefs>
                            <attrdomv>
                                <udom Sync="TRUE">Coordinates defining the features.</udom>
                            </attrdomv>
                        </attr>
                    </detailed>
                 </eainfo>'''
        insert_element(target_tree, element, xml)
        del xml, element

        # ###--->>> Binary section <<<---###
        element = "Binary"
        print(f"Replacing {element} root")
        xml = '''<Binary Sync="TRUE"><Thumbnail><Data EsriPropertyType="PictureX"></Data></Thumbnail></Binary>'''
        insert_element(target_tree, element, xml)
        del xml, element


        del insert_element

        etree.indent(target_root, space='    ')
        #target_xml_string = etree.tostring(target_tree, pretty_print=True, method='html', encoding="utf-8", xml_declaration=True).decode()
        target_xml_string = etree.tostring(target_tree, pretty_print=True, xml_declaration=True, encoding="utf-8").decode()
        #print(target_xml_string)
        try:
            with open(fc_metadata_xml_file, "w") as f:
                f.write(target_xml_string)
            del f
        except:
            print(f"The metadata file: {os.path.basename(fc_metadata_xml_file)} can not be overwritten!!")
        del target_xml_string

        #pretty_format_xml_file(fc_metadata_xml_file)

        # Declare Variables
        del root_dict
        del target_tree, target_root, target_name
        # Imports
        del etree, StringIO, arcpy, md, pretty_format_xml_file
        # Function Parameters
        del fc_metadata_xml_file

    except:
        traceback.print_exc()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function: ##--> '{', '.join(rk)}' <--##"); del rk
        return True
    finally:
        pass

def check_update_metadata_root_items(project_gdb=""):
    try:
        # Imports
        from lxml import etree
        from io import StringIO
        import arcpy
        from arcpy import metadata as md

        # Project modules
        from src.project_tools import pretty_format_xml_file

        # Use all of the cores on the machine
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.env.overwriteOutput = True

        # Define variables
        project_folder = os.path.dirname(project_gdb)
        scratch_gdb    = rf"{project_folder}\Scratch\scratch.gdb"

        # Set the workspace environment to local file geodatabase
        arcpy.env.workspace = project_gdb
        # Set the scratchWorkspace environment to local file geodatabase
        arcpy.env.scratchWorkspace = scratch_gdb

        # Clean-up variables
        del scratch_gdb

        print(f"{'--Start' * 10}--\n")

        #fcs = [fc for fc in arcpy.ListFeatureClasses() if fc == "WhaleNorthPacificRight_20201015"]
        fcs = [rf"{project_gdb}\{fc}" for fc in arcpy.ListFeatureClasses()]

        for fc in sorted(fcs):
            print(os.path.basename(fc))

            dataset_md = md.Metadata(fc)
            dataset_md.synchronize('ALWAYS')
            dataset_md.save()
            dataset_md.reload()
            dataset_md_xml = dataset_md.xml

            # Parse the XML
            parser = etree.XMLParser(remove_blank_text=True, encoding='UTF-8')
            tree = etree.parse(StringIO(dataset_md_xml), parser=parser)
            root = tree.getroot()
            del parser

            root_dict = {"Esri"       :  0, "dataIdInfo" :  1, "mdChar"      :  2,
                         "mdContact"  :  3, "mdDateSt"   :  4, "mdFileID"    :  5,
                         "mdLang"     :  6, "mdMaint"    :  7, "mdHrLv"      :  8,
                         "mdHrLvName" :  9, "refSysInfo" : 10, "spatRepInfo" : 11,
                         "spdoinfo"   : 12, "dqInfo"     : 13, "distInfo"    : 14,
                         "eainfo"     : 15, "contInfo"   : 16, "spref"       : 17,
                         "spatRepInfo" : 18, "dataSetFn" : 19, "Binary"      : 100,}

            for key in root_dict:
                element = root.xpath(f"./{key}")
                if len(element) == 0:
                    print(f"\tInsert Element: {key}")

                    if key == "mdContact":
                        xml = '''<mdContact>
                                    <editorSource>extermal</editorSource>
                                    <editorDigest>9cc0fe80de5687cc4d79f50f3a254f2c3ceb08ce</editorDigest>
                                    <rpIndName>Nikki Wildart</rpIndName>
                                    <rpOrgName>Office of Protected Resources, National Marine Fisheries Service</rpOrgName>
                                    <rpPosName>Biologist</rpPosName>
                                    <rpCntInfo>
                                        <cntAddress addressType="both">
                                            <delPoint>1315 East West Highway</delPoint>
                                            <city>Silver Spring</city>
                                            <adminArea>MD</adminArea>
                                            <postCode>20910-3282</postCode>
                                            <eMailAdd>nikki.wildart@noaa.gov</eMailAdd>
                                            <country>US</country>
                                        </cntAddress>
                                        <cntPhone>
                                            <voiceNum tddtty="">(301) 427-8443</voiceNum>
                                            <faxNum>(301) 427-8443</faxNum>
                                        </cntPhone>
                                        <cntHours>0700 - 1800 EST/EDT</cntHours>
                                        <cntOnlineRes>
                                            <linkage>https://www.fisheries.noaa.gov/about/office-protected-resources</linkage>
                                            <protocol>REST Service</protocol>
                                            <orName>Fisheries OPR</orName>
                                            <orDesc>NOAA Fisheries Office of Science and Technology</orDesc>
                                            <orFunct>
                                                <OnFunctCd value="002"></OnFunctCd>
                                            </orFunct>
                                        </cntOnlineRes>
                                    </rpCntInfo>
                                    <editorSave>True</editorSave>
                                    <displayName>Nikki Wildart</displayName>
                                    <role>
                                        <RoleCd value="002"></RoleCd>
                                    </role>
                                </mdContact>'''
                        _root = etree.XML(xml)
                        root.insert(root_dict[f"{key}"], _root)
                        del _root, xml
                    if key == "mdFileID":
                        xml = '''<mdFileID>gov.noaa.nmfs.inport:</mdFileID>'''
                        _root = etree.XML(xml)
                        root.insert(root_dict[f"{key}"], _root)
                        del _root, xml
                    if key == "mdLang":
                        xml = '''<mdLang>
                                    <languageCode value="eng" Sync="TRUE"></languageCode>
                                    <countryCode value="USA" Sync="TRUE"></countryCode>
                                 </mdLang>'''
                        _root = etree.XML(xml)
                        root.insert(root_dict[f"{key}"], _root)
                        del _root, xml
                    if key == "Binary":
                        xml = '''<Binary Sync="TRUE"><Thumbnail><Data EsriPropertyType="PictureX"></Data></Thumbnail></Binary>'''
                        _root = etree.XML(xml)
                        root.insert(root_dict[f"{key}"], _root)
                        del _root, xml

                elif len(element) == 1:
                    #print(f"\tFound Element: {element[0].tag}")

                    if key == "mdFileID":
                        xml = '''<mdFileID>gov.noaa.nmfs.inport:</mdFileID>'''
                        _root = etree.XML(xml)
                        root.replace(element[0], _root)
                        del _root, xml
                    if key == "mdLang":
                        xml = '''<mdLang>
                                    <languageCode value="eng" Sync="TRUE"></languageCode>
                                    <countryCode value="USA" Sync="TRUE"></countryCode>
                                 </mdLang>'''
                        _root = etree.XML(xml)
                        root.replace(element[0], _root)
                        del _root, xml
                    if key == "mdMaint":
                        xml = '''<mdMaint>
                                    <maintFreq>
                                        <MaintFreqCd value="009"></MaintFreqCd>
                                    </maintFreq>
                                 </mdMaint>'''
                        _root = etree.XML(xml)
                        root.replace(element[0], _root)
                        del _root, xml
                    if key == "mdHrLv":
                        xml = '''<mdHrLv>
                                    <ScopeCd value="005" Sync="TRUE"></ScopeCd>
                                 </mdHrLv>'''
                        _root = etree.XML(xml)
                        root.replace(element[0], _root)
                        del _root, xml
                    if key == "mdHrLvName":
                        xml = '''<mdHrLvName Sync="TRUE">dataset</mdHrLvName>'''
                        _root = etree.XML(xml)
                        root.replace(element[0], _root)
                        del _root, xml
                    if key == "refSysInfo":
                        xml = '''<refSysInfo>
                                    <RefSystem dimension="horizontal">
                                        <refSysID>
                                            <identCode code="4326" Sync="TRUE"/>
                                            <idCodeSpace Sync="TRUE">EPSG</idCodeSpace>
                                            <idVersion Sync="TRUE">6.2(3.0.1)</idVersion>
                                        </refSysID>
                                    </RefSystem>
                                 </refSysInfo>'''
                        _root = etree.XML(xml)
                        root.replace(element[0], _root)
                        del _root, xml
                    if key == "spatRepInfo":
                        xml = '''<spatRepInfo>
                                    <VectSpatRep>
                                        <geometObjs Name="SpeciesRangeTemplate" Sync="TRUE">
                                            <geoObjTyp>
                                                <GeoObjTypCd value="002" Sync="TRUE"/>
                                            </geoObjTyp>
                                            <geoObjCnt Sync="TRUE">2</geoObjCnt>
                                        </geometObjs>
                                        <topLvl>
                                            <TopoLevCd value="001" Sync="TRUE"/>
                                        </topLvl>
                                    </VectSpatRep>
                                 </spatRepInfo>'''
                        _root = etree.XML(xml)
                        root.replace(element[0], _root)
                        del _root, xml
                    if key == "spdoinfo":
                        xml = '''<spdoinfo>
                                    <ptvctinf>
                                        <esriterm Name="AbaloneBlack_20210712" Sync="TRUE">
                                            <efeatyp Sync="TRUE">Simple</efeatyp>
                                            <efeageom code="4" Sync="TRUE"></efeageom>
                                            <esritopo Sync="TRUE">FALSE</esritopo>
                                            <efeacnt Sync="TRUE">1</efeacnt>
                                            <spindex Sync="TRUE">TRUE</spindex>
                                            <linrefer Sync="TRUE">FALSE</linrefer>
                                        </esriterm>
                                    </ptvctinf>
                                </spdoinfo>'''
                        _root = etree.XML(xml)
                        root.replace(element[0], _root)
                        del _root, xml

                del element, key

            # ###############################################
            # ###--->>> This removes extra elements <<<---###
            # ###############################################
            for parent in root.xpath('*'): # Search for parent elements
                if parent.tag not in root_dict:
                    element_to_remove = root.find(f"{parent.tag}")
                    # Remove the element
                    if not isinstance(element_to_remove, type(None)):
                        print(f"\t\tRemoving: {parent.tag}")
                        root.remove(element_to_remove)
                    del element_to_remove
                del parent
            # ###############################################

            # ###############################################
            # ###--->>> This reorders the elements  <<<---###
            # ###############################################
            dataset_md_xml = etree.tostring(tree).decode()
            #print(dataset_md_xml)
            # This allows for sorting
            doc = etree.XML(dataset_md_xml, etree.XMLParser(remove_blank_text=True))
            for parent in doc.xpath('.'): # Search for parent elements
              parent[:] = sorted(parent,key=lambda x: root_dict[x.tag])
              del parent
            #print( etree.tostring(doc,pretty_print=True).decode() )
            del doc
            # ###############################################

            # ###############################################
            # ###--->>> Saves the updated XML       <<<---###
            # ###############################################
            dataset_md.xml = dataset_md_xml
            dataset_md.save()
            dataset_md.reload()

            del root_dict

            del tree, root
            del dataset_md_xml
            del dataset_md
            del fc

        del fcs

        print(f"\n{'--End' * 10}--")

        # Decalred Variables
        del project_folder
        #del species_range_fc, species_range_fc_metadata_xml

        # Imports
        del etree, StringIO, md, pretty_format_xml_file

        # Function parameters
        del project_gdb

    except:
        traceback.print_exc()
    else:
        # Cleanup
        arcpy.management.ClearWorkspaceCache()
        del arcpy
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function: ##--> '{', '.join(rk)}' <--##"); del rk
        return True
    finally:
        pass

def update_eainfo(project_gdb=""):
    try:
        # Imports
        from lxml import etree
        from io import StringIO
        import arcpy
        from arcpy import metadata as md

        # Project modules
        from src.project_tools import pretty_format_xml_file

        # Use all of the cores on the machine
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.env.overwriteOutput = True

        # Define variables
        project_folder = os.path.dirname(project_gdb)
        scratch_gdb    = rf"{project_folder}\Scratch\scratch.gdb"

        # Set the workspace environment to local file geodatabase
        arcpy.env.workspace = project_gdb
        # Set the scratchWorkspace environment to local file geodatabase
        arcpy.env.scratchWorkspace = scratch_gdb

        # Clean-up variables
        del scratch_gdb

        print(f"{'--Start' * 10}--\n")

        # Parse the XML
        eainfo_xml_file = rf"{project_folder}\eainfo.xml"
        eainfo_root = etree.parse(eainfo_xml_file)
        eainfo_element = eainfo_root.xpath("./eainfo")[0]
        del eainfo_root
        del eainfo_xml_file

        #print( etree.tostring(eainfo,pretty_print=True).decode() )

        #fcs = [fc for fc in arcpy.ListFeatureClasses() if fc == "WhaleNorthPacificRight_20201015"]
        fcs = [rf"{project_gdb}\{fc}" for fc in arcpy.ListFeatureClasses()]

        for fc in sorted(fcs):
            print(os.path.basename(fc))

            dataset_md = md.Metadata(fc)
            dataset_md.synchronize('ALWAYS')
            dataset_md.save()
            dataset_md.reload()
            dataset_md_xml = dataset_md.xml

            # Parse the XML
            parser = etree.XMLParser(remove_blank_text=True, encoding='UTF-8')
            tree = etree.parse(StringIO(dataset_md_xml), parser=parser)
            root = tree.getroot()
            del parser

            root_dict = {"Esri"       :  0, "dataIdInfo" :  1, "mdChar"      :  2,
                         "mdContact"  :  3, "mdDateSt"   :  4, "mdFileID"    :  5,
                         "mdLang"     :  6, "mdMaint"    :  7, "mdHrLv"      :  8,
                         "mdHrLvName" :  9, "refSysInfo" : 10, "spatRepInfo" : 11,
                         "spdoinfo"   : 12, "dqInfo"     : 13, "distInfo"    : 14,
                         "eainfo"     : 15, "contInfo"   : 16, "spref"       : 17,
                         "spatRepInfo" : 18, "dataSetFn" : 19, "Binary"      : 100,}

            _eainfo_root = root.xpath('./eainfo')[0]

            root.replace(_eainfo_root, eainfo_element)
            #print( etree.tostring(_eainfo_root,pretty_print=True).decode() )
            del _eainfo_root

            # ###############################################
            # ###--->>> Saves the updated XML       <<<---###
            # ###############################################

            #print( etree.tostring(root,pretty_print=True).decode() )

            dataset_md_xml = etree.tostring(tree).decode()
            dataset_md.xml = dataset_md_xml
            dataset_md.save()
            dataset_md.synchronize("ALWAYS")
            dataset_md.save()
            dataset_md.reload()

            del root_dict
            del tree, root
            del dataset_md_xml
            del dataset_md
            del fc

        del fcs

        print(f"\n{'--End' * 10}--")

        # Decalred Variables
        del project_folder
        del eainfo_element

        # Imports
        del etree, StringIO, md, pretty_format_xml_file

        # Function parameters
        del project_gdb

    except:
        traceback.print_exc()
    else:
        # Cleanup
        arcpy.management.ClearWorkspaceCache()
        del arcpy
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function: ##--> '{', '.join(rk)}' <--##"); del rk
        return True
    finally:
        pass

def update_dataIdInfo(project_gdb=""):
    try:
        # Imports
        from lxml import etree
        from io import StringIO
        import arcpy
        from arcpy import metadata as md

        # Project modules
        from src.project_tools import pretty_format_xml_file

        # Use all of the cores on the machine
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.env.overwriteOutput = True

        # Define variables
        project_folder = os.path.dirname(project_gdb)
        scratch_gdb    = rf"{project_folder}\Scratch\scratch.gdb"

        # Set the workspace environment to local file geodatabase
        arcpy.env.workspace = project_gdb
        # Set the scratchWorkspace environment to local file geodatabase
        arcpy.env.scratchWorkspace = scratch_gdb

        # Clean-up variables
        del scratch_gdb

        print(f"{'--Start' * 10}--\n")

        #print( etree.tostring(eainfo,pretty_print=True).decode() )

        root_dict = {"Esri"       :  0, "dataIdInfo" :  1, "mdChar"      :  2,
                     "mdContact"  :  3, "mdDateSt"   :  4, "mdFileID"    :  5,
                     "mdLang"     :  6, "mdMaint"    :  7, "mdHrLv"      :  8,
                     "mdHrLvName" :  9, "refSysInfo" : 10, "spatRepInfo" : 11,
                     "spdoinfo"   : 12, "dqInfo"     : 13, "distInfo"    : 14,
                     "eainfo"     : 15, "contInfo"   : 16, "spref"       : 17,
                     "spatRepInfo" : 18, "dataSetFn" : 19, "Binary"      : 100,}

        esri_dict ={"CreaDate" : 0,  "CreaTime" : 1, "ArcGISFormat" : 2,
                    "ArcGISStyle" : 3, "SyncOnce" : 4, "DataProperties" : 5,
                    "itemProps" : 0, "itemName" : 0, "imsContentType" : 1,
                    "nativeExtBox" : 2, "westBL" : 0, "eastBL" : 1, "southBL" : 2,
                    "northBL" : 3, "exTypeCode" : 4, "coordRef" : 1, "type" : 0,
                    "geogcsn" : 2, "csUnits" : 3, "peXml" : 4, "SyncDate" : 6,
                    "SyncTime" : 7, "ModDate" : 8, "ModTime" : 9,
                    "scaleRange" : 10, "minScale" : 11, "maxScale" : 12,
                    "ArcGISProfile" : 13,}

        dataIdInfo_dict = { "idCitation" : 0, "searchKeys" :  1, "idPurp"   : 2,
                            "idAbs"      : 3, "idCredit"   :  4, "resConst" : 5,
                            "envirDesc"  : 6, "dataLang"   :  7, "dataChar" : 8,
                            "spatRpType" : 9, "dataExt"    : 10, "tpCat"    : 11,}

        fcs = [fc for fc in arcpy.ListFeatureClasses() if fc == "WhaleNorthPacificRight_20201015"]
        #fcs = [rf"{project_gdb}\{fc}" for fc in arcpy.ListFeatureClasses()]

        for fc in sorted(fcs):
            print(os.path.basename(fc))

            dataset_md = md.Metadata(fc)
            print(f"\tTitle: {dataset_md.title}")
            #dataset_md.title = f"{os.path.basename(species_range_fc)}"
            #dataset_md.tags = f"{os.path.basename(species_range_fc)}; ESA; range; NMFS"
            #print(f"\tTags: {dataset_md.tags}")
            #dataset_md.summary = "This feature class depicts the entire range of the [common name (species name) DPS or ESU]. All boundaries should be considered approximate and, as such, caution is warranted when using it for any other purpose (e.g., analyses)."
            #print(f"\tSummary: {dataset_md.summary}")
            dataset_md.description = 'This range includes [all; marine; freshwater; adult; immature/juvenile; larval] life stages of the species [add any caveats, e.g., why something is not included]. The range was based on the following [tracking, tagging, bycatch, and sighting] data: [Provide data and citations used to create range, including name/version/date of shoreline data.] Disclaimer: The spatial data provided here display an approximate distribution of the listed entity based on the best available information at the time of creation; they should not be conflated with the definitive range of the listed entity under the ESA. As such, the distribution of the listed entity may not be exclusively limited to the range identified herein, and we have not verified the listed entity’s occurrence in every area comprising the range. Please notify us if you have recent information that is not reflected in our data (see Citation contacts). Use of these data do not replace the ESA section 7 consultation process; however, these data may be a first step in determining whether a proposed federal action overlaps with listed species’ ranges or critical habitat.'
            #print(f"\tDescription: {dataset_md.description}")
            dataset_md.credits = 'NOAA Fisheries Service. 2024. Endangered Species Act Species Range Geodatabase. Silver Spring, MD: National Oceanic and Atmospheric Administration (NOAA), National Marine Fisheries Service (NMFS), Office of Protected Resources (OPR).'
            #print(f"\tCredits: {dataset_md.credits}")
            dataset_md.accessConstraints = '*** Attribution *** Whenever NMFS material is reproduced and re-disseminated, we request that users attribute the material appropriately. Pursuant to 17 U.S. C. 403, parties who produce copyrighted works consisting predominantly of material created by the Federal Government are encouraged to provide notice with such work(s) identifying the U.S. Government material incorporated and stating that such material is not subject to copyright protection. Please cite the species range datasets as indicated in the metadata for each species, or if not indicated, as follows with the appropriate information substituted for all text in {CURLY BRACKETS}:\n\nNOAA Fisheries Service. Endangered Species Act Species Range Geodatabase. Silver Spring, MD: National Oceanic and Atmospheric Administration (NOAA), National Marine Fisheries Service (NMFS), Office of Protected Resources (OPR) [producer] {GEODATABASE PUBLICATION DATE}. {ADD URL}\n\n***No Warranty*** The user assumes the entire risk related to its use of these data. NMFS is providing these data "as is," and NMFS disclaims any and all warranties, whether express or implied, including (without limitation) any implied warranties of merchantability or fitness for a particular purpose. No warranty expressed or implied is made regarding the accuracy or utility of the data on any other system or for general or scientific purposes, nor shall the act of distribution constitute any such warranty. It is strongly recommended that careful attention be paid to the contents of the metadata file associated with these data to evaluate dataset limitations, restrictions or intended use. In no event will NMFS be liable to you or to any third party for any direct, indirect, incidental, consequential, special or exemplary damages or lost profit resulting from any use or misuse of this data.\n\n*** Proper Usage *** The information on government servers are in the public domain, unless specifically annotated otherwise, and may be used freely by the public. Before using information obtained from this server, special attention should be given to the date and time of the data and products being displayed. This information shall not be modified in content and then presented as official government material. This dataset was created to generally represent our best professional judgment of the ranges of listed species based on the best available information at the time of publication, including: geographic factors, time of year, and the biology of each species. The dataset should not be used to infer information regarding the existence or details of other marine features or resources, including, but not limited to, navigable waters, coastlines, bathymetry, submerged features, or man-made structures. Users assume responsibility for determining the appropriate use of this dataset.\n\n*** Temporal Considerations *** Species’ ranges are subject to change or modification. Generally, we become aware of these changes during the 5-year review of the species’ status, as required under the ESA. If changes to the range are deemed necessary, we will make such changes in the database, which will be archived and replaced by an updated version as soon as feasible. It is the user’s responsibility to ensure the most recent species’ range data are being used.\n\n*** Shorelines/Base Layers *** The accuracy of this dataset is dependent upon the accuracy and resolution of the datasets (e.g. shoreline, hydrography, bathymetry, shared administrative boundaries) used in the creation process. Source datasets used are specified in the metadata. These data sources were selected for their suitability to a broad audience, and may not be suitable for specific uses requiring higher-resolution information. Coastlines and water body boundaries change. Unless otherwise noted, where the National Hydrography Dataset or NOAA Medium Resolution Shoreline is used, assume the boundary reaches the most current river, estuary, or coastal shoreline delineation available.*** Data Limitations *** Our data may lack the spatial resolution to capture the entire range of a species, especially outside of a major waterway (e.g., in a very small tributary, or shallow area near a marsh). For section 7 consultations, we recommend that Federal action agencies request technical assistance to verify presence/absence of listed species within their action area.'
            #print(f"\tAccessConstraints: {dataset_md.accessConstraints}")
            dataset_md.save()
            dataset_md.reload()
            del dataset_md

            dataset_md = md.Metadata(fc)
            dataset_md.synchronize('ALWAYS')
            dataset_md.save()
            dataset_md.reload()
            dataset_md_xml = dataset_md.xml

            # Parse the XML
            parser = etree.XMLParser(remove_blank_text=True, encoding='UTF-8')
            tree = etree.parse(StringIO(dataset_md_xml), parser=parser)
            root = tree.getroot()
            del parser

            dataIdInfo_root = root.xpath('./dataIdInfo')[0]
            #print(etree.tostring(dataIdInfo_root, pretty_print=True).decode())

            # ##################################
            for key in dataIdInfo_dict:
                print(f"\t\tProcessing: {key}")

                if key == "idCitation":
                    print(f"\t\t\t{key}")
                    idCitation_dict = {"resTitle" : 0, "resAltTitle" : 1,
                                       "collTitle"  : 2, "presForm" : 3, "PresFormCd"  : 0,
                                       "fgdcGeoform" : 1, "date" : 4, "createDate" : 0,
                                       "pubDate"    : 1, "revisedDate" : 2, "citRespParty"  : 6,
                                       }
                    element = dataIdInfo_root.xpath(f"./{key}")
                    for _key in idCitation_dict:
                        _key_element = element[0].xpath(f"./{_key}")
                        if len(_key_element) == 0:
                            print(f"\t\t\t\t'{_key}' not found")
                        elif len(_key_element) == 1:
                            print(f"\t\t\t\tFound '{_key}' with value: {_key_element[0].text}")
                        elif len(_key_element) > 1:
                            print("found too many")

                        del _key_element

                    del element
                if key == "searchKeys":
                    print(f"\t\t\t{key}")
                    element = dataIdInfo_root.xpath(f"./{key}")
                    del element
                if key == "idPurp":
                    pass
                    #print(f"\t\t\t{key}")
                    #element = dataIdInfo_root.xpath(f"./{key}")
                    #del element
                if key == "idAbs":
                    pass
                    #print(f"\t\t\t{key}")
                    #element = dataIdInfo_root.xpath(f"./{key}")
                    #del element
                if key == "idCredit":
                    pass
                    #print(f"\t\t\t{key}")
                    #element = dataIdInfo_root.xpath(f"./{key}")
                    #del element
                if key == "resConst":
                   pass
                    #print(f"\t\t\t{key}")
                    #element = dataIdInfo_root.xpath(f"./{key}")
                    #del element
                if key == "envirDesc":
                    print(f"\t\t\t{key}")
                    element = dataIdInfo_root.xpath(f"./{key}")
                    xml = '''<envirDesc Sync="TRUE">Esri ArcGIS 13.4.0.55405</envirDesc>'''
                    _root = etree.XML(xml)
                    if len(element) == 0:
                        position = dataIdInfo_dict[f'{key}']
                        print(f"\t\t\tInserting f'{key}' at {position}")
                        dataIdInfo_root.insert(position, _root)
                        del position
                    if len(element) == 1:
                        print(f"\t\t\t\tUpdating: '{key}'")
                        dataIdInfo_root.replace(element[0], _root)
                    if len(element) > 1:
                        print(f"\t\t\t\tThere are {len(element)} for: '{key}'")
                    else:
                        pass
                    del _root, xml, element
                if key == "dataLang":
                    print(f"\t\t\t{key}")
                    element = dataIdInfo_root.xpath(f"./{key}")
                    xml = '''<dataLang><languageCode value="eng" Sync="TRUE"></languageCode><countryCode value="USA" Sync="TRUE"></countryCode></dataLang>'''
                    _root = etree.XML(xml)
                    if len(element) == 0:
                        position = dataIdInfo_dict[f'{key}']
                        print(f"\t\t\tInserting f'{key}' at {position}")
                        dataIdInfo_root.insert(position, _root)
                        del position
                    if len(element) == 1:
                        print(f"\t\t\t\tUpdating: '{key}'")
                        dataIdInfo_root.replace(element[0], _root)
                    if len(element) > 1:
                        print(f"\t\t\t\tThere are {len(element)} for: '{key}'")
                    else:
                        pass
                    del _root, xml, element
                if key == "dataChar":
                    print(f"\t\t\t{key}")
                    element = dataIdInfo_root.xpath(f"./{key}")
                    xml = '''<dataChar><CharSetCd value="004"></CharSetCd></dataChar>'''
                    _root = etree.XML(xml)
                    if len(element) == 0:
                        position = dataIdInfo_dict[f'{key}']
                        print(f"\t\t\tInserting f'{key}' at {position}")
                        dataIdInfo_root.insert(position, _root)
                        del position
                    if len(element) == 1:
                        print(f"\t\t\t\tUpdating: '{key}'")
                        dataIdInfo_root.replace(element[0], _root)
                    if len(element) > 1:
                        print(f"\t\t\t\tThere are {len(element)} for: '{key}'")
                    else:
                        pass
                    del _root, xml, element
                if key == "spatRpType":
                    print(f"\t\t\t{key}")
                    element = dataIdInfo_root.xpath(f"./{key}")
                    xml = '''<spatRpType><SpatRepTypCd value="001" Sync="TRUE"></SpatRepTypCd></spatRpType>'''
                    _root = etree.XML(xml)
                    if len(element) == 0:
                        position = dataIdInfo_dict[f'{key}']
                        print(f"\t\t\tInserting f'{key}' at {position}")
                        dataIdInfo_root.insert(position, _root)
                        del position
                    if len(element) == 1:
                        print(f"\t\t\t\tUpdating: '{key}'")
                        dataIdInfo_root.replace(element[0], _root)
                    if len(element) > 1:
                        print(f"\t\t\t\tThere are {len(element)} for: '{key}'")
                    else:
                        pass
                    del _root, xml, element
                if key == "dataExt":
                    print(f"\t\t\t{key}")
                    element = dataIdInfo_root.xpath(f"./{key}")
                    xml = '''<dataExt></dataExt> '''
                    _root = etree.XML(xml)
                    if len(element) == 0:
                        position = dataIdInfo_dict[f'{key}']
                        print(f"\t\t\tInserting f'{key}' at {position}")
                        #dataIdInfo_root.insert(position, _root)
                        del position
                    if len(element) == 1:
                        #print(f"\t\t\t\tUpdating: '{key}'")
                        dataIdInfo_root.replace(element[0], _root)
                    if len(element) > 1:
                        print(f"\t\t\t\tThere are {len(element)} for: '{key}'")
                    else:
                        pass
                    del _root, xml, element
                if key == "tpCat":
                    print(f"\t\t\t{key}")
                    tpCat_dict = {"002": '<tpCat><TopicCatCd value="002"></TopicCatCd></tpCat>',
                     "007": '<tpCat><TopicCatCd value="007"></TopicCatCd></tpCat>',
                     "014": '<tpCat><TopicCatCd value="014"></TopicCatCd></tpCat>',}

                    tpCat = dataIdInfo_root.xpath(f"./tpCat")
                    if len(tpCat) == 0:
                        position = dataIdInfo_dict['tpCat']
                        print(f"\t\t\tInserting tpCat at {position}")
                        #for key in tpCat_dict:
                        #    xml = tpCat_dict[key]
                        #    root = etree.XML(xml)
                        #    dataIdInfo_root.insert(position, root)
                        #    position+=1
                        #    del root, xml, key
                        del position

                    elif len(tpCat) >= 1:
                        tp_cat_dict = dict()
                        for i, tp_cat in enumerate(tpCat):
                            topic_cat_cd = tp_cat.xpath("./TopicCatCd")[0].get("value")

                            if topic_cat_cd not in tp_cat_dict:
                                tp_cat_dict[topic_cat_cd] = etree.tostring(tp_cat).decode()
                            else:
                                pass

                            del topic_cat_cd
                            del i, tp_cat

                        insert_list = [tpc for tpc in tpCat_dict if tpc not in tp_cat_dict]
                        if insert_list:
                            for insert_item in insert_list:
                                #print(insert_item)
                                xml = tpCat_dict[insert_item]
                                _root = etree.XML(xml)
                                dataIdInfo_root.append(_root)
                                del _root, xml, insert_item
                        del insert_list
                        del tp_cat_dict
                    else:
                        pass

                    del tpCat, tpCat_dict

                del key


            del dataIdInfo_root

            # ###############################################
            # ###--->>> Saves the updated XML       <<<---###
            # ###############################################

            #print( etree.tostring(root,pretty_print=True).decode() )

            dataset_md_xml = etree.tostring(tree).decode()
            dataset_md.xml = dataset_md_xml
            dataset_md.save()
            dataset_md.synchronize("ALWAYS")
            dataset_md.save()
            dataset_md.reload()

            del tree, root
            del dataset_md_xml
            del dataset_md
            del fc

        del fcs

        print(f"\n{'--End' * 10}--")

        # Decalred Variables
        del esri_dict, root_dict, dataIdInfo_dict
        del project_folder

        # Imports
        del etree, StringIO, md, pretty_format_xml_file

        # Function parameters
        del project_gdb

    except:
        traceback.print_exc()
    else:
        # Cleanup
        arcpy.management.ClearWorkspaceCache()
        del arcpy
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function: ##--> '{', '.join(rk)}' <--##"); del rk
        return True
    finally:
        pass

def update_contacts(project_gdb=""):
    try:
        # Imports
        from lxml import etree
        from io import StringIO
        import copy
        from arcpy import metadata as md

        # Project modules
        from src.project_tools import pretty_format_xml_file

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2)
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        project_folder = os.path.dirname(project_gdb)
        scratch_folder      = rf"{project_folder}\Scratch"

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

        workspaces = [project_gdb]

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
                parser = etree.XMLParser(remove_blank_text=True, encoding='UTF-8')
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
                        #print(old_contact_parent)
                        #print(etree.tostring(contact_parent, encoding="utf-8",  method='xml', pretty_print=True).decode())

                        user_name = contact_parent.find(f"./rpIndName").text
                        print(f"\tUser Name:     {user_name}")
                        email_address = contact_parent.find(f".//eMailAdd").text
                        print(f"\tEmail Address: {email_address}")
                        user_role = contact_parent.find(f".//RoleCd")
                        print(f"\tRole:          {user_role.attrib}")

                        contact_root = root.xpath(f".//eMailAdd[text()='{email_address}']/ancestor::{old_contact_parent}/rpIndName[text()='{user_name}']/..")
                        #contact_root = copy.deepcopy(root.xpath(f".//eMailAdd[text()='{email_address}']/ancestor::{old_contact_parent}/rpIndName[text()='{user_name}']/.."))
                        #print(etree.tostring(contact_root[0], encoding="utf-8",  method='xml', pretty_print=True).decode())

                        #print(etree.tostring(contact_root[0], encoding="utf-8",  method='xml', pretty_print=True).decode())

                        new_contact_root = contacts_xml_root.xpath(f".//eMailAdd[text()='{email_address}']/ancestor::contact/rpIndName[text()='{user_name}']/ancestor::contact/editorSave[text()='True']/..")

                        if len(new_contact_root) == 1:
                            new_contact = copy.deepcopy(new_contact_root[0])
                            new_contact.tag = old_contact_parent
                            new_contact.append(contact_root[0].find(f".//role"))
                            #print(etree.tostring(new_contact, encoding="utf-8",  method='xml', pretty_print=True).decode())

                            #contact_root[0].getparent().replace(contact_root[0], new_contact)
                            #print(etree.tostring(contact_root[0], encoding="utf-8",  method='xml', pretty_print=True).decode())

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

                #dataset_md = md.Metadata(dataset_path)
                #dataset_md.xml = etree.tostring(tree, encoding="utf-8",  method='xml', xml_declaration=True, pretty_print=True).decode()
                #dataset_md.save()
                #dataset_md.synchronize("ALWAYS")
                #del dataset_md

                #del dataset_md_xml
                #del dataset_name, dataset_path
                #del root, tree

            del datasets
            del workspace

        # Variables set in function
        del contacts_xml_root, contacts_xml_tree
        del RoleCd_dict, root_dict
        del project_gdb, project_folder, scratch_folder
        del workspaces

        # Imports

        del md, etree, StringIO, copy

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

        InsertXmlElements = False
        if InsertXmlElements:
            fc_metadata_xml_file = rf"{local_temp}\SpeciesRangeTemplate.xml"
            insert_xml_elements(fc_metadata_xml_file=fc_metadata_xml_file)
            del fc_metadata_xml_file
        del InsertXmlElements

        CheckUpdateMetadataRootItems = False
        if CheckUpdateMetadataRootItems:
            check_update_metadata_root_items(project_gdb=project_gdb)
        del CheckUpdateMetadataRootItems

        UpdateEainfo = False
        if UpdateEainfo:
            update_eainfo(project_gdb=project_gdb)
        del UpdateEainfo

        UpdateDataIdInfo = False
        if UpdateDataIdInfo:
            update_dataIdInfo(project_gdb=project_gdb)
        del UpdateDataIdInfo

        UpdateContacts = False
        if UpdateContacts:
            update_contacts(project_gdb=project_gdb)
        else:
            pass
        del UpdateContacts

        #from lxml import etree
        #dataset_md_xml = r'C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\ArcPy Studies\XML\nmfs-species-range-metatdata\WhaleNorthAtlanticRight_20201215.xml'
        #parser = etree.XMLParser(remove_blank_text=True, encoding='UTF-8')
        #tree = etree.parse(dataset_md_xml, parser=parser)
        #root = tree.getroot()
        #del parser
        #print(etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding="utf-8").decode())

        # Declared Varaiables
        # Imports
        # Function Parameters
        del project_gdb

        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time

        print(f"\n{'-' * 80}")
        print(f"Python script: {os.path.basename(__file__)} completed {strftime('%a %b %d %I:%M %p', localtime())}")
        print(u"Elapsed Time {0} (H:M:S)".format(strftime("%H:%M:%S", gmtime(elapse_time))))
        print(f"{'-' * 80}")
        del elapse_time, end_time, start_time
        del gmtime, localtime, strftime, time

    except:
        traceback.print_exc()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function: ##--> '{', '.join(rk)}' <--##"); del rk
        return True
    finally:
        pass

if __name__ == '__main__':
    try:
        # Imports

        # Append the location of this scrip to the System Path
        #sys.path.append(os.path.dirname(__file__))
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))

        project_folder = rf"{os.path.dirname(os.path.dirname(__file__))}"
        #project_name   = "NMFS_ESA_Range" National Mapper
        project_name   = "National Mapper"
        project_gdb    = rf"{project_folder}\{project_name}.gdb"

        main(project_gdb=project_gdb)

        # Variables
        del project_folder, project_name, project_gdb

        # Imports

    except:
        traceback.print_exc()
    else:
        pass
    finally:
        pass