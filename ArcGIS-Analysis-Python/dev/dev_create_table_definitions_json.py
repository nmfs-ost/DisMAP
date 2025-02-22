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

def get_list_of_table_fields(project_gdb=""):
    try:
        # Imports
        import arcpy

        # Use all of the cores on the machine
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.env.overwriteOutput = True

        # Define variables
        project_folder  = os.path.dirname(project_gdb)
        scratch_folder  = rf"{project_folder}\Scratch"
        scratch_gdb     = rf"{scratch_folder}\scratch.gdb"
        json_path       = rf"{project_folder}\CSV Data\table_definitions.json"

        # Set the workspace environment to local file geodatabase
        arcpy.env.workspace = project_gdb
        # Set the scratchWorkspace environment to local file geodatabase
        arcpy.env.scratchWorkspace = scratch_gdb
        # Clean-up variables
        del scratch_folder, scratch_gdb
        del project_folder

        print(f"\n{'--Start' * 10}--\n")

        table_definitions = dict()

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
            fields = [f.name for f in arcpy.ListFields(dataset_path) if f.type not in ["Geometry", "OID"] and f.name not in ["Shape_Area", "Shape_Length"]]

            table_definitions[dataset_name] = fields

            del fields
            del dataset_name
            del dataset_path

        table_definitions = {k:v for k,v in sorted(table_definitions.items())}

        import json
        # Write to File
        with open(json_path, 'w') as json_file:
            json.dump(table_definitions, json_file, indent=4)
        del json_file
        del json

        for table in table_definitions:
            print(f"{table}")
            fields = table_definitions[table]
            del table
            for field in fields:
                print(f"\t{field}")
                del field
            del fields

        del datasets
        del table_definitions
        del json_path
        # Compact GDB
        print(f"\nCompacting: {os.path.basename(project_gdb)}" )
        arcpy.management.Compact(project_gdb)

        print(f"\n{'--End' * 10}--")

        # Imports
        del arcpy
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

        GetListOfTableAndFields = True
        if GetListOfTableAndFields:
            get_list_of_table_fields(project_gdb=project_gdb)
        else:
            pass
        del GetListOfTableAndFields
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