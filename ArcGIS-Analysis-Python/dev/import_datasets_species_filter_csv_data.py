# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        create_species_year_image_name_table_worker
# Purpose:
#
# Author:      john.f.kennedy
#
# Created:     09/03/2024
# Copyright:   (c) john.f.kennedy 2024
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os, sys # built-ins first
import traceback
import importlib
import inspect

import arcpy # third-parties second

def line_info(msg):
    f = inspect.currentframe()
    i = inspect.getframeinfo(f.f_back)
    return f"Script: {os.path.basename(i.filename)}\n\tNear Line: {i.lineno}\n\tFunction: {i.function}\n\tMessage: {msg}"

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

def worker(project_gdb="", csv_file=""):
    try:
        # Test if passed workspace exists, if not raise SystemExit
        if not arcpy.Exists(project_gdb) or not arcpy.Exists(csv_file):
            raise SystemExit(f"{os.path.basename(project_gdb)} OR {os.path.basename(csv_file)} is missing!!")

        # Imports
        import dismap
        importlib.reload(dismap)

        # Set History and Metadata logs, set serverity and message level
        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        # Set basic workkpace variables
        table_name        = os.path.basename(csv_file).replace(".csv", "")
        csv_data_folder   = os.path.dirname(csv_file)
        project_folder    = os.path.dirname(csv_data_folder)
        scratch_workspace = rf"{project_folder}\Scratch\scratch.gdb"

        # Set basic workkpace variables
        arcpy.env.workspace                = project_gdb
        arcpy.env.scratchWorkspace         = rf"Scratch\scratch.gdb"
        arcpy.env.overwriteOutput             = True
        arcpy.env.parallelProcessingFactor = "100%"

        #print(table_name)
        #print(csv_data_folder)

        field_csv_dtypes = dismap.dTypesCSV(csv_data_folder, table_name)
        field_gdb_dtypes = dismap.dTypesGDB(csv_data_folder, table_name)

        #print(field_csv_dtypes)
        #print(field_gdb_dtypes)

        print(f"\tCreating Table: {table_name}")
        arcpy.management.CreateTable(project_gdb, f"{table_name}", "", "", table_name.replace("_", " "))
        print("\t{0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

        import pandas as pd
        import numpy as np
        import warnings
        print(f"> Importing {table_name} CSV Table")
        #csv_table = f"{table_name}.csv"
        # https://pandas.pydata.org/pandas-docs/stable/getting_started/intro_tutorials/09_timeseries.html?highlight=datetime
        # https://www.tutorialsandyou.com/python/numpy-data-types-66.html
        #df = pd.read_csv('my_file.tsv', sep='\t', header=0)  ## not setting the index_col
        #df.set_index(['0'], inplace=True)
        # C:\. . .\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\lib\site-packages\numpy\lib\arraysetops.py:583:
        # FutureWarning: elementwise comparison failed; returning scalar instead, but in the future will perform elementwise comparison
        # mask |= (ar1 == a)
        # A fix: https://www.youtube.com/watch?v=TTeElATMpoI
        # TLDR: pandas are Jedi; numpy are the hutts; and python is the galatic empire

        encoding, index_column = dismap.get_encoding_index_col(csv_file)

        with warnings.catch_warnings():
            warnings.simplefilter(action='ignore', category=FutureWarning)
            # DataFrame
            df = pd.read_csv(
                             csv_file,
                             index_col = index_column,
                             encoding  = encoding,
                             delimiter = ",",
                             dtype     = field_csv_dtypes,
                            )
        del encoding, index_column
        #print(field_csv_dtypes)
        #print(field_gdb_dtypes)
        del field_csv_dtypes
        #print(df)
        # Replace NaN with an empty string. When pandas reads a cell
        # with missing data, it asigns that cell with a Null or nan
        # value. So, we are changing that value to an empty string of ''.
        # https://community.esri.com/t5/python-blog/those-pesky-null-things/ba-p/902664
        # https://community.esri.com/t5/python-blog/numpy-snippets-6-much-ado-about-nothing-nan-stuff/ba-p/893702
        df.fillna('', inplace=True)
        #df.fillna(np.nan)
        #df = df.replace({np.nan: None})

        # Alternatively, apply to all columns at once
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

        print(f">-> Creating the {table_name} Geodatabase Table")
        try:
            array = np.array(np.rec.fromrecords(df.values), dtype = field_gdb_dtypes)
        except:
            traceback.print_exc()
            raise Exception
        del df
        del field_gdb_dtypes

        # Temporary table
        tmp_table = rf"memory\{table_name.lower()}_tmp"
        try:
            arcpy.da.NumPyArrayToTable(array, tmp_table)
            del array
        # Captures ArcPy type of error
        except:
            traceback.print_exc()
            raise Exception

        print(f">-> Copying the {table_name} Table from memory to the GDB")
        fields = [f.name for f in arcpy.ListFields(tmp_table) if f.type == "String"]
        for field in fields:
            arcpy.management.CalculateField(tmp_table, field=field, expression=f"None if !{field}! == '' else !{field}!")
            print("Calculate Field:\t{0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
            del field
        del fields

        arcpy.management.CopyRows(tmp_table, rf"{project_gdb}\{table_name}", "")
        print("Copy Rows:\t{0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
        # Remove the temporary table
        arcpy.management.Delete(tmp_table)
        del tmp_table

        arcpy.conversion.ExportTable(in_table = rf"{project_gdb}\{table_name}", out_table  = rf"{csv_data_folder}\_{table_name}.csv", where_clause="", use_field_alias_as_name = "NOT_USE_ALIAS")
        print("Export Table:\t{0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
        del pd, np, warnings

        # Alter Fields
        dismap.alter_fields(csv_data_folder, rf"{project_gdb}\{table_name}")

        # Load Metadata
        dismap.import_metadata(dataset=rf"{project_gdb}\{table_name}")
        # Export Metadata
        #

        print(f"Compacting the {os.path.basename(project_gdb)} GDB")
        arcpy.management.Compact(project_gdb)
        print("\t"+arcpy.GetMessages().replace("\n", "\n\t"))

        # Basic variables
        del table_name, csv_data_folder, project_folder, scratch_workspace
        # Imports
        del dismap
        # Function parameters
        del project_gdb, csv_file

    except:
        traceback.print_exc()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function: ##--> '{', '.join(rk)}' <--##"); del rk
        return True
    finally:
        pass

def update_datecode(csv_file="", project_name=""):
    try:
        # Imports
        import dismap
        importlib.reload(dismap)

        import pandas as pd
        import warnings

        # Set History and Metadata logs, set serverity and message level
        arcpy.SetLogHistory(True) # Look in %AppData%\Roaming\Esri\ArcGISPro\ArcToolbox\History
        arcpy.SetLogMetadata(True)
        arcpy.SetSeverityLevel(2) # 0—A tool will not throw an exception, even if the tool produces an error or warning.
                                  # 1—If a tool produces a warning or an error, it will throw an exception.
                                  # 2—If a tool produces an error, it will throw an exception. This is the default.
        arcpy.SetMessageLevels(['NORMAL']) # NORMAL, COMMANDSYNTAX, DIAGNOSTICS, PROJECTIONTRANSFORMATION

        table_name      = os.path.basename(csv_file).replace(".csv", "")
        csv_data_folder = os.path.dirname(csv_file)

        # Set basic arcpy.env variables
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        field_csv_dtypes = dismap.dTypesCSV(csv_data_folder, table_name)

        print(f"\tUpdating CSV file: {os.path.basename(csv_file)}")
        #print(f"\t\t{csv_file}")

        # C:\. . .\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\lib\site-packages\numpy\lib\arraysetops.py:583:
        # FutureWarning: elementwise comparison failed; returning scalar instead, but in the future will perform elementwise comparison
        # mask |= (ar1 == a)
        # A fix: https://www.youtube.com/watch?v=TTeElATMpoI
        # TLDR: pandas are Jedi; numpy are the hutts; and python is the galatic empire
        with warnings.catch_warnings():
            warnings.simplefilter(action='ignore', category=FutureWarning)
            # DataFrame
            df = pd.read_csv(csv_file,
                             index_col = 0,
                             encoding  = "utf-8",
                             delimiter = ',',
                             dtype     = field_csv_dtypes,
                            )

        old_date_code = df.DateCode.unique()[0]

        print(f"\tOld Date Code: {old_date_code}")
        print(f"\tNew Date Code: {dismap.date_code(project_name)}")

        df = df.replace(regex = old_date_code, value = dismap.date_code(project_name))

        df.to_csv(path_or_buf = f"{csv_file}", sep = ',')

        del df, pd, warnings
        del old_date_code

        print(f"\tCompleted updating CSV file: {os.path.basename(csv_file)}")

        # Variables infunction
        del field_csv_dtypes, table_name, csv_data_folder
        # Imports
        del dismap
        # Function parameters
        del csv_file, project_name

    except:
        traceback.print_exc()
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk: print(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function: ##--> '{', '.join(rk)}' <--##"); del rk
        return True
    finally:
        pass

def main(base_project_folder="", project_name=""):
    try:
        from import_datasets_species_filter_csv_data import worker

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        project_folder      = rf"{base_project_folder}\{project_name}"
        base_project_file   = rf"{base_project_folder}\DisMAP.aprx"
        project_gdb         = rf"{base_project_folder}\{project_name}\{project_name}.gdb"
        csv_data_folder     = rf"{project_folder}\CSV Data"
        datasets_csv        = rf"{csv_data_folder}\Datasets.csv"
        species_filter_csv  = rf"{csv_data_folder}\Species_Filter.csv"
        survey_metadata_csv = rf"{csv_data_folder}\DisMAP_Survey_Info.csv"

        #print(species_filter_csv)
        #print(project_gdb)
        #print(arcpy.Exists(species_filter_csv))
        #print(arcpy.Exists(project_gdb))

        del project_folder, csv_data_folder

        Backup = False
        if Backup:
            print("Making a backup")
            arcpy.management.Copy(project_gdb, project_gdb.replace(".gdb", f"_Backup.gdb"))
            print("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))

            print("Compacting the backup")
            arcpy.management.Compact(project_gdb.replace(".gdb", f"_Backup.gdb"))
            print("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))
        del Backup

        UpdateDatecode = False
        if UpdateDatecode:
            # Update DateCode
            update_datecode(csv_file=datasets_csv, project_name=project_name)
        del UpdateDatecode

        DatasetsCSVFile = False
        if DatasetsCSVFile:
            # Datasets CSV File
            #print(datasets_csv)
            worker(project_gdb=project_gdb, csv_file=datasets_csv)
        del DatasetsCSVFile

        SpeciesFilterCSVFile = False
        if SpeciesFilterCSVFile:
            # Species Filter CSV File
            #print(species_filter_csv)
            #print(project_gdb)
            worker(project_gdb=project_gdb, csv_file=species_filter_csv)
        del SpeciesFilterCSVFile

        DisMAPSurveyInfoFile = False
        if DisMAPSurveyInfoFile:
            # DisMAP Survey Info File
            #print(survey_metadata_csv)
            worker(project_gdb=project_gdb, csv_file=survey_metadata_csv)
        del DisMAPSurveyInfoFile

        del base_project_file
        del datasets_csv, species_filter_csv, survey_metadata_csv
        del project_gdb
        del worker

        # Function parameters
        del base_project_folder, project_name

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
        # Append the location of this scrip to the System Path
        #sys.path.append(os.path.dirname(__file__))
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))

        # Import this Python module
        import import_datasets_species_filter_csv_data
        importlib.reload(import_datasets_species_filter_csv_data)

        print(f"{'-' * 90}")
        print(f"Python Script:  {os.path.basename(__file__)}")
        print(f"Location:       {os.path.dirname(__file__)}")
        print(f"Python Version: {sys.version} Environment: {os.path.basename(sys.exec_prefix)}")
        print(f"{'-' * 90}\n")

        base_project_folder = rf"{os.path.dirname(os.path.dirname(__file__))}"
        #project_name = "May 1 2024"
        #project_name = "July 1 2024"
        project_name = "December 1 2024"

        # Tested on 7/30/2024 -- PASSED
        main(base_project_folder=base_project_folder, project_name=project_name)

        del base_project_folder, project_name

        from time import localtime, strftime
        print(f"\n{'-' * 90}")
        print(f"Python script: {os.path.basename(__file__)} successfully completed {strftime('%a %b %d %I:%M %p', localtime())}")
        print(f"{'-' * 90}")
        del localtime, strftime

    except:
        traceback.print_exc()
    else:
        pass
    finally:
        pass

