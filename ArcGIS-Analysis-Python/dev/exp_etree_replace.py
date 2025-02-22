#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      john.f.kennedy
#
# Created:     06/02/2025
# Copyright:   (c) john.f.kennedy 2025
# Licence:     <your licence>
#-------------------------------------------------------------------------------

def main():
    from arcpy import metadata as md
    from lxml import etree
    from io import StringIO

    #fc = "C:\\Users\\john.f.kennedy\\Documents\\ArcGIS\\Projects\\ArcPy Studies\\XML\\nmfs-species-range-metatdata\\National Mapper.gdb\\WhaleNorthAtlanticRight_20201215"
    fc = r"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\ArcPy Studies\XML\nmfs-species-range-metatdata\National Mapper.gdb\WhaleNorthPacificRight_20201015"
    dataset_md = md.Metadata(fc)
    dataset_md_xml = dataset_md.xml
    #print(dataset_md_xml)

    parser = etree.XMLParser(encoding='UTF-8', remove_blank_text=True)
    tree = etree.parse(StringIO(dataset_md_xml), parser=parser)
    root = tree.getroot()
    del parser

    #print(etree.tostring(root).decode())

    _eainfo_root = root.xpath('./eainfo')[0]

    #print(etree.tostring(_eainfo_root, encoding="utf-8", pretty_print=True).decode())

    eainfo_xml_file = r"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\ArcPy Studies\XML\nmfs-species-range-metatdata\eainfo.xml"
    eainfo_root = etree.parse(eainfo_xml_file)
    eainfo_element = eainfo_root.xpath("./eainfo")[0]
    #print(eainfo_element)

##    eainfo_xml_file = r"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\ArcPy Studies\XML\nmfs-species-range-metatdata\eainfo.xml"
##    parser = etree.XMLParser(encoding='UTF-8', remove_blank_text=True)
##    eainfo_tree = etree.parse(StringIO(eainfo_xml_file), parser=parser)
##    eainfo_root = eainfo_tree.getroot()
##    eainfo_element = eainfo_root.xpath("./eainfo")[0]
##
##    #eainfo_tree = etree.parse(eainfo_xml_file)
##    #eainfo_root = eainfo_tree.getroot()
##    #eainfo_element = eainfo_root.xpath("./eainfo")[0]
##    eainfo = etree.XML(etree.tostring(eainfo_element))
    root.replace(_eainfo_root, eainfo_element)
    dataset_md_xml = etree.tostring(tree).decode()
    dataset_md.xml = dataset_md_xml
    dataset_md.save()
    dataset_md.reload()

    #print(etree.XML(etree.tostring(eainfo_element)))

if __name__ == '__main__':
    main()
