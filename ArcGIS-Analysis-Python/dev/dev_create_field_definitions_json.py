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

def get_list_of_fields(project_gdb=""):
    try:
        # Imports
        from lxml import etree
        from io import StringIO
        import arcpy
        from arcpy import metadata as md

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

        print(f"\n{'--Start' * 10}--\n")

        field_definitions = dict()

        datasets = list()

        walk = arcpy.da.Walk(project_gdb)

        for dirpath, dirnames, filenames in walk:
            for filename in filenames:
                datasets.append(os.path.join(dirpath, filename))
                del filename
            del dirpath, dirnames, filenames
        del walk

        for dataset_path in sorted(datasets):
            dataset_name = os.path.basename(dataset_path)
            print(f"Dataset Name: {dataset_name}")
            # Create a list of fields using the ListFields function
            fields = [f for f in arcpy.ListFields(dataset_path) if f.type not in ["Geometry", "OID"] and f.name not in ["Shape_Area", "Shape_Length"]]

            if fields:
                # Iterate through the list of fields
                for field in fields:
                    #print(f"\tField: {field.name} {field.type}")
                    if field.name not in field_definitions:
                        field_definitions[field.name] = {"field_aliasName"    : field.aliasName,
                                                         "field_baseName"     : field.baseName,
                                                         "field_defaultValue" : field.defaultValue,
                                                         "field_domain"       : field.domain,
                                                         "field_editable"     : field.editable,
                                                         "field_isNullable"   : field.isNullable,
                                                         "field_length"       : field.length,
                                                         "field_name"         : field.name,
                                                         "field_precision"    : field.precision,
                                                         "field_required"     : field.required,
                                                         "field_scale"        : field.scale,
                                                         "field_type"         : field.type,}
                    else:
                        pass
                    del field
            else:
                pass

            dataset_md = md.Metadata(dataset_path)
            dataset_md_xml = dataset_md.xml
            del dataset_md

            # Parse the XML
            parser = etree.XMLParser(encoding='UTF-8', remove_blank_text=True)
            tree = etree.parse(StringIO(dataset_md_xml), parser=parser)
            root = tree.getroot()
            del parser, dataset_md_xml

            #print(etree.tostring(tree, encoding="utf-8",  method='xml', xml_declaration=True, pretty_print=True).decode())
            # etree.indent(tree, space='   ')
            # tree.write(xml_file, encoding="utf-8",  method='xml', xml_declaration=True, pretty_print=True)

            for field in fields:
                attributes = root.xpath(f".//attrlabl[text()='{field.name}']/..")
                if not isinstance(attributes, type(None)) and len(attributes) > 0:
                    for attribute in attributes:
                        #<attrdef Sync="TRUE"></attrdef>
                        #<attrdefs Sync="TRUE"></attrdefs>
                        #<attrdomv><udom Sync="TRUE"></udom></attrdomv>
                        if not isinstance(attribute.find("./attrdef/.."), type(None)) and len(attribute.find("./attrdef/..")) > 0:
                            #print(attribute.find("./attrdef/.."))
                            print(etree.tostring(attribute, encoding="utf-8",  method='xml', xml_declaration=True, pretty_print=True).decode())
                        del attribute
                else:
                    pass
                del attributes
                del field

##            attributes = root.xpath(f".//attr")
##            if not isinstance(attributes, type(None)) and len(attributes) > 0:
##                for field in fields:
##                    field_element = root.xpath(f".//attrlabl")
##                    print(etree.tostring(field_element[0], encoding="utf-8",  method='xml', xml_declaration=True, pretty_print=True).decode())
##                    del field_element
##                    del field
##            else:
##                pass

            del root, tree
            del fields
            del dataset_name
            del dataset_path

        #for field in sorted(field_definitions):
        #    print(f"Field: {field}")
        #    # Print field properties
        #    print(f"\tField Alias:   {field_definitions[field]['field_aliasName']}")
        #    print(f"\tBase Name:     {field_definitions[field]['field_baseName']}")
        #    print(f"\tDefault Value: {field_definitions[field]['field_defaultValue']}")
        #    print(f"\tDomain:        {field_definitions[field]['field_domain']}")
        #    print(f"\tIs Editable:   {field_definitions[field]['field_editable']}")
        #    print(f"\tIs Nullable:   {field_definitions[field]['field_isNullable']}")
        #    print(f"\tLength:        {field_definitions[field]['field_length']}")
        #    print(f"\tField Name:    {field_definitions[field]['field_name']}")
        #    print(f"\tPrecision:     {field_definitions[field]['field_precision']}")
        #    print(f"\tRequired:      {field_definitions[field]['field_required']}")
        #    print(f"\tScale:         {field_definitions[field]['field_scale']}")
        #    print(f"\tType:          {field_definitions[field]['field_type']}")
        #    del field

        field_definitions = {k:v for k,v in sorted(field_definitions.items())}

        import json
        # Write to File
        with open(json_path, 'w') as json_file:
            json.dump(field_definitions, json_file, indent=4)
        del json_file
        del json

        del datasets
        del field_definitions
        del json_path
        # Compact GDB
        print(f"\nCompacting: {os.path.basename(project_gdb)}" )
        arcpy.management.Compact(project_gdb)

        print(f"\n{'--End' * 10}--")

        # Imports
        del etree, StringIO, arcpy, md
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

        GetListOfFields = True
        if GetListOfFields:
            get_list_of_fields(project_gdb=project_gdb)
        else:
            pass
        del GetListOfFields

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
        project_name = "July 1 2024"
        project_name   = "December 1 2024"
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
