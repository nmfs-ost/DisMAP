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

def create_field_metadata_xml(project_gdb=""):
    try:
        # Imports
        from lxml import etree
        from io import StringIO
        import arcpy

        # Use all of the cores on the machine
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.env.overwriteOutput = True

        # Define variables
        project_folder  = os.path.dirname(project_gdb)
        scratch_folder  = rf"{project_folder}\Scratch"
        scratch_gdb     = rf"{scratch_folder}\scratch.gdb"
        json_path       = rf"{project_folder}\CSV Data\field_definitions.json"

        # Set the workspace environment to local file geodatabase
        arcpy.env.workspace = project_gdb
        # Set the scratchWorkspace environment to local file geodatabase
        arcpy.env.scratchWorkspace = scratch_gdb
        # Clean-up variables
        del scratch_folder, scratch_gdb
        del project_folder

        print(f"{'--Start' * 10}--\n")

        # Create the root element
        root = etree.Element("metadata")
        root.set("{http://www.w3.org/XML/1998/namespace}lang", "en-US")
        tree = etree.ElementTree(root)

        # Create child elements and add them to the root
        xml = '''<eainfo>
                    <detailed xmlns="" Name="" Sync="TRUE">
                        <enttyp>
                            <enttypl Sync="TRUE">Attribute Table Fields</enttypl>
                            <enttypt Sync="TRUE">Feature Class</enttypt>
                            <enttypc Sync="TRUE">1</enttypc>
                            <enttypd>A collection of geographic features with the same geometry type.</enttypd>
                            <enttypds>Esri</enttypds>
                        </enttyp>
                    </detailed>
                 </eainfo>'''

        # Parse the XML
        parser = etree.XMLParser(encoding='UTF-8', remove_blank_text=True)
        _tree = etree.parse(StringIO(xml), parser=parser)
        eainfo = _tree.getroot()
        del parser
        del xml
        del _tree

        # Append element
        root.append(eainfo)
        #root.insert(100, _root)
        del eainfo
        # Serialize the tree to a string
        # xml_string = etree.tostring(tree, pretty_print=True, method='xml', xml_declaration=True, encoding="utf-8").decode()
        # print(xml_string)
        # del xml_string

        field_definitions = dict()

        import json
        # Read a File
        with open(json_path, 'r') as json_file:
            field_definitions = json.load(json_file)
            for field_definition in field_definitions:
                #print(f'Field: {field_definition}')
                for key in field_definitions[field_definition]:
                    #print(f"\t{key:<18} : {field_definitions[field_definition][key]}")
                    del key
                del field_definition
        del json_file
        del json

        for field in sorted(field_definitions):
            #print(f"Field: {field}")
            xml = f'<attr> \
                    <attrlabl Sync="TRUE">{field_definitions[field]["field_name"]}</attrlabl> \
                    <attalias Sync="TRUE">{field_definitions[field]["field_aliasName"]}</attalias> \
                    <attrtype Sync="TRUE">{field_definitions[field]["field_type"]}</attrtype> \
                    <attwidth Sync="TRUE">{field_definitions[field]["field_length"]}</attwidth> \
                    <atprecis Sync="TRUE">{field_definitions[field]["field_precision"]}</atprecis> \
                    <attscale Sync="TRUE">{field_definitions[field]["field_scale"]}</attscale> \
                    <attrdef Sync="TRUE"></attrdef> \
                    <attrdefs Sync="TRUE"></attrdefs> \
                    <attrdomv> \
                        <udom Sync="TRUE"></udom> \
                    </attrdomv> \
                </attr>'
            parser = etree.XMLParser(remove_blank_text=True)
            attr = etree.fromstring(xml, parser=parser)
            del parser

            detailed = tree.xpath(".//detailed")
            detailed[0].append(attr)

            print(etree.tostring(detailed[0], pretty_print=True, method='xml', xml_declaration=True, encoding="utf-8").decode())

            del attr
            del detailed
            del field

        xml_string = etree.tostring(tree, pretty_print=True, method='xml', xml_declaration=True, encoding="utf-8").decode()
        print(xml_string)
        del xml_string

        del root, tree

        #field_definitions = {k:v for k,v in sorted(field_definitions.items())}
        #import json
        # Write to File
        #with open(json_path, 'w') as json_file:
        #    json.dump(field_definitions, json_file, indent=4)
        #del json_file
        #del json

        del field_definitions
        del json_path
        # Compact GDB
        print(f"\nCompacting: {os.path.basename(project_gdb)}" )
        arcpy.management.Compact(project_gdb)

        print(f"\n{'--End' * 10}--")

        # Imports
        del etree, StringIO, arcpy
        # Function parameters
        del project_gdb
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
        # Append the location of this scrip to the System Path
        #sys.path.append(os.path.dirname(__file__))
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))

        from time import gmtime, localtime, strftime, time
        # Set a start time so that we can see how log things take
        start_time = time()
        print(f"{'-' * 80}")
        print(f"Python Script:  {os.path.basename(__file__)}")
        print(f"Location:       ..\Documents\ArcGIS\Projects\..\{os.path.basename(os.path.dirname(__file__))}\{os.path.basename(__file__)}")
        print(f"Python Version: {sys.version}")
        print(f"Environment:    {os.path.basename(sys.exec_prefix)}")
        print(f"{'-' * 80}\n")

        CreateFieldMetadataXml = True
        if CreateFieldMetadataXml:
            create_field_metadata_xml(project_gdb=project_gdb)
        else:
            pass
        del CreateFieldMetadataXml

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
        project_name   = "April 1 2023"
        #project_name   = "July 1 2024"
        #project_name   = "December 1 2024"
        project_gdb    = rf"{project_folder}\{project_name}\{project_name}.gdb"

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