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

sys.path.append(os.path.dirname(__file__))

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
            raise SystemExit(line_info(f"{os.path.basename(project_gdb)} OR {os.path.basename(csv_file)} is missing!!"))

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

        arcpy.AddMessage(f"\tCreating Table: {table_name}")
        arcpy.management.CreateTable(project_gdb, f"{table_name}", "", "", table_name.replace("_", " "))
        arcpy.AddMessage("\t{0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

        import pandas as pd
        import numpy as np
        import warnings
        arcpy.AddMessage(f"> Importing {table_name} CSV Table")
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

        arcpy.AddMessage(f">-> Creating the {table_name} Geodatabase Table")
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

        arcpy.AddMessage(f">-> Copying the {table_name} Table from memory to the GDB")
        fields = [f.name for f in arcpy.ListFields(tmp_table) if f.type == "String"]
        for field in fields:
            arcpy.management.CalculateField(tmp_table, field=field, expression=f"None if !{field}! == '' else !{field}!")
            arcpy.AddMessage("Calculate Field:\t{0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
            del field
        del fields

        arcpy.management.CopyRows(tmp_table, rf"{project_gdb}\{table_name}", "")
        arcpy.AddMessage("Copy Rows:\t{0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
        # Remove the temporary table
        arcpy.management.Delete(tmp_table)
        del tmp_table

        arcpy.conversion.ExportTable(in_table = rf"{project_gdb}\{table_name}", out_table  = rf"{csv_data_folder}\_{table_name}.csv", where_clause="", use_field_alias_as_name = "NOT_USE_ALIAS")
        arcpy.AddMessage("Export Table:\t{0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
        del pd, np, warnings

        # Alter Fields
        dismap.alter_fields(csv_data_folder, rf"{project_gdb}\{table_name}")

        # Load Metadata
        dismap.import_metadata(dataset=rf"{project_gdb}\{table_name}")
        # Export Metadata
        #

        arcpy.AddMessage(f"Compacting the {os.path.basename(project_gdb)} GDB")
        arcpy.management.Compact(project_gdb)
        arcpy.AddMessage("\t"+arcpy.GetMessages().replace("\n", "\n\t"))

        results = [rf"{project_gdb}\{table_name}"]

        # Basic variables
        del table_name, csv_data_folder, project_folder, scratch_workspace
        # Imports
        del dismap
        # Function parameters
        del project_gdb, csv_file

    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteWarning:
        traceback.print_exc()
        arcpy.AddWarning(arcpy.GetMessages())
    except arcpy.ExecuteError:
        traceback.print_exc()
        arcpy.AddError(arcpy.GetMessages())
    except Exception as e:
        print(e)
        traceback.print_exc()
        raise Exception
    except SystemExit as se:
        print(se)
        traceback.print_exc()
    except:
        traceback.print_exc()
        raise Exception
    else:
        try:
            leave_out_keys = ["leave_out_keys", "results"]
            remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
            if remaining_keys:
                pass
                arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[0][3]}': ##--> '{', '.join(remaining_keys)}' <--## Line Number: {traceback.extract_stack()[-1].lineno}")
            del leave_out_keys, remaining_keys
            return results if "results" in locals().keys() else ["NOTE!! The 'results' variable not yet set!!"]
        except:
            raise SystemExit(traceback.print_exc())
    finally:
        if "results" in locals().keys(): del results

def update_datecode(csv_file="", project=""):
    try:
        # Imports
        import dismap
        importlib.reload(dismap)

        import pandas as pd
        import warnings

        # Test if passed workspace exists, if not raise SystemExit
        if not arcpy.Exists(csv_file):
            raise SystemExit(line_info(f"{os.path.basename(csv_file)} is missing!!"))
        else:
            pass

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

        arcpy.AddMessage(f"\tUpdating CSV file: {os.path.basename(csv_file)}")
        #arcpy.AddMessage(f"\t\t{csv_file}")

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

        arcpy.AddMessage(f"\tOld Date Code: {old_date_code}")
        arcpy.AddMessage(f"\tNew Date Code: {dismap.date_code(project)}")

        df = df.replace(regex = old_date_code, value = dismap.date_code(project))

        df.to_csv(path_or_buf = f"{csv_file}", sep = ',')

        del df, pd, warnings
        del old_date_code

        arcpy.AddMessage(f"\tCompleted updating CSV file: {os.path.basename(csv_file)}")

        results = [csv_file]

        # Variables infunction
        del field_csv_dtypes, table_name, csv_data_folder
        # Imports
        del dismap
        # Function parameters
        del csv_file, project

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

def main(project):
    try:
        from import_datasets_species_filter_csv_data import worker

        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"

        project_gdb = rf"{os.environ['USERPROFILE']}\Documents\ArcGIS\Projects\DisMAP-ArcGIS-Analysis\{project}\{project}.gdb"
        project_folder = os.path.dirname(project_gdb)
        csv_data_folder = rf"{project_folder}\CSV Data"

        datasets_csv        = rf"{csv_data_folder}\Datasets.csv"
        species_filter_csv  = rf"{csv_data_folder}\Species_Filter.csv"
        survey_metadata_csv = rf"{csv_data_folder}\DisMAP_Survey_Info.csv"

        del project_folder, csv_data_folder

        Backup = False
        if Backup:
            arcpy.AddMessage("Making a backup")
            arcpy.management.Copy(project_gdb, project_gdb.replace(".gdb", f"_Backup.gdb"))
            arcpy.AddMessage("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))

            arcpy.AddMessage("Compacting the backup")
            arcpy.management.Compact(project_gdb.replace(".gdb", f"_Backup.gdb"))
            arcpy.AddMessage("\t"+arcpy.GetMessages(0).replace("\n", "\n\t"))
        del Backup

        results = []

        try:

            UpdateDatecode = False
            if UpdateDatecode:
                # Update DateCode
                update_datecode(csv_file=datasets_csv, project=project)
            del UpdateDatecode

            DatasetsCSVFile = False
            if DatasetsCSVFile:
                # Datasets CSV File
                arcpy.AddMessage(datasets_csv)
                result = worker(project_gdb=project_gdb, csv_file=datasets_csv)
                if result:
                    results.extend(result)
                del result
            del DatasetsCSVFile

            SpeciesFilterCSVFile = True
            if SpeciesFilterCSVFile:
                # Species Filter CSV File
                arcpy.AddMessage(species_filter_csv)
                result = worker(project_gdb=project_gdb, csv_file=species_filter_csv)
                if result:
                    results.extend(result)
                del result
            del SpeciesFilterCSVFile

            DisMAPSurveyInfoFile = False
            if DisMAPSurveyInfoFile:
                # DisMAP Survey Info File
                arcpy.AddMessage(survey_metadata_csv)
                try:
                    result = worker(project_gdb=project_gdb, csv_file=survey_metadata_csv)
                    if result:
                        results.extend(result)
                    del result
                except:
                    pass
            del DisMAPSurveyInfoFile

        except Exception as e:
            print(e)

        if results:
            print(results)

##        if results:
##            if type(results).__name__ == "bool":
##                arcpy.AddMessage(f"'Results' is a {type(results).__name__}" )
##                arcpy.AddMessage(f"Result: {results}")
##            elif type(results).__name__ == "str":
##                arcpy.AddMessage(f"'Results' is a {type(results).__name__}" )
##                arcpy.AddMessage(f"Result: {results}")
##            elif type(results).__name__ == "list":
##                if type(results[0]).__name__ == "list":
##                        results = [r for rt in results for r in rt]
##                arcpy.AddMessage(f"'Results' is a {type(results).__name__}" )
##                for result in results:
##                    arcpy.AddMessage(f"Result: {result}")
##                del result
##            else:
##                arcpy.AddMessage(f"No results returned!!!")
##        else:
##            arcpy.AddMessage(f"No results in '{inspect.stack()[0][3]}'")

        del datasets_csv, species_filter_csv, survey_metadata_csv
        del project_gdb
        del worker
        del project

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

if __name__ == "__main__":
    try:
        # Import this Python module
        import import_datasets_species_filter_csv_data
        importlib.reload(import_datasets_species_filter_csv_data)

        print(f"{'-' * 90}")
        print(f"Python Script:  {os.path.basename(__file__)}")
        print(f"Location:       {os.path.dirname(__file__)}")
        print(f"Python Version: {sys.version} Environment: {os.path.basename(sys.exec_prefix)}")
        print(f"{'-' * 90}\n")

        #project = "May 1 2024"
        #project = "July 1 2024"
        project = "December 1 2024"

        # Tested on 7/30/2024 -- PASSED
        main(project=project)

        del project

        from time import localtime, strftime
        print(f"\n{'-' * 90}")
        print(f"Python script: {os.path.basename(__file__)} successfully completed {strftime('%a %b %d %I:%M %p', localtime())}")
        print(f"{'-' * 90}")
        del localtime, strftime

    except SystemExit:
        pass
    except:
        traceback.print_exc()
    else:
        leave_out_keys = ["leave_out_keys"]
        leave_out_keys.extend([name for name, obj in inspect.getmembers(sys.modules[__name__]) if inspect.isfunction(obj) or inspect.ismodule(obj)])
        remaining_keys = [key for key in locals().keys() if not key.startswith('__') and key not in leave_out_keys]
        if remaining_keys:
            arcpy.AddWarning(f"Remaining Keys in '{inspect.stack()[1][3]}': ##--> '{', '.join(remaining_keys)}' <--##")
        del leave_out_keys, remaining_keys
    finally:
        pass
