"""
Script documentation
- Tool parameters are accessed using arcpy.GetParameter() or
                                     arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or
                                        arcpy.SetParameterAsText()
"""
import os
import sys # built-ins first
import traceback
import inspect
import arcpy

def get_encoding_index_col(csv_file):
    try:
        # Imports
        import chardet
        import pandas as pd
        # Open the file in binary mode
        with open(csv_file, 'rb') as f:
            # Read the file's content
            data = f.read()
        # Detect the encoding using chardet.detect()
        encoding_result = chardet.detect(data)
        # Retrieve the encoding information
        __encoding = encoding_result['encoding']
        del f, data, encoding_result
        # arcpy.AddMessage the detected encoding
        #arcpy.AddMessage("Detected Encoding:", __encoding)
        dtypes = {}
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_file, encoding  = __encoding, delimiter = ",",)
        # Analyze the data types and lengths
        for column in df.columns:
            dtypes[column] = df[column].dtype
            del column
        first_column = list(dtypes.keys())[0]
        __index_column = 0 if first_column == "Unnamed: 0" else None
        # Declared Variables
        del df, dtypes, first_column
        # Import
        del chardet, pd
        # Function Parameter
        del csv_file
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages(2))
        raise SystemExit
    except Exception:
        traceback.print_exc()
        arcpy.AddError(arcpy.GetMessages(2))
        raise SystemExit
    except:  # noqa: E722
        traceback.print_exc()
        arcpy.AddError(arcpy.GetMessages(2))
        raise SystemExit
    else:
        return __encoding, __index_column
    finally:
        pass

def worker(project_gdb="", csv_file=""):
    try:
        # Test if passed workspace exists, if not raise SystemExit
        if not arcpy.Exists(project_gdb) or not arcpy.Exists(csv_file):
            raise SystemExit(f"{os.path.basename(project_gdb)} OR {os.path.basename(csv_file)} is missing!!")
        # Imports
        from arcpy import metadata as md
        import dismap_tools
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
        scratch_workspace = os.path.join(project_folder, "Scratch\\scratch.gdb")
        # Set basic workkpace variables
        arcpy.env.workspace                = project_gdb
        arcpy.env.scratchWorkspace         = r"Scratch\\scratch.gdb"
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"
        #arcpy.AddMessage(table_name)
        #arcpy.AddMessage(csv_data_folder)
        field_csv_dtypes = dismap_tools.dTypesCSV(csv_data_folder, table_name)
        field_gdb_dtypes = dismap_tools.dTypesGDB(csv_data_folder, table_name)
        #arcpy.AddMessage(field_csv_dtypes)
        #arcpy.AddMessage(field_gdb_dtypes)
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
        #encoding, index_column = dismap_tools.get_encoding_index_col(csv_file)
        encoding, index_column = get_encoding_index_col(csv_file)
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
        #arcpy.AddMessage(field_csv_dtypes)
        #arcpy.AddMessage(field_gdb_dtypes)
        del field_csv_dtypes
        #arcpy.AddMessage(df)
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
        arcpy.AddMessage(f">-> Creating the {table_name} Geodatabase Table")
        try:
            array = np.array(np.rec.fromrecords(df.values), dtype = field_gdb_dtypes)
        except:  # noqa: E722
            traceback.print_exc()
            raise SystemExit
        del df
        del field_gdb_dtypes
        # Temporary table
        tmp_table = rf"memory\{table_name.lower()}_tmp"
        try:
            arcpy.da.NumPyArrayToTable(array, tmp_table)
            del array
        # Captures ArcPy type of error
        except:  # noqa: E722
            traceback.print_exc()
            raise SystemExit
        arcpy.AddMessage(f">-> Copying the {table_name} Table from memory to the GDB")
        fields = [f.name for f in arcpy.ListFields(tmp_table) if f.type == "String"]
        for field in fields:
            arcpy.management.CalculateField(tmp_table, field=field, expression=f"'' if !{field}! is None else !{field}!")
            arcpy.AddMessage("Calculate Field:\t{0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
            del field
        del fields
        dataset_path = rf"{project_gdb}\{table_name}"
        arcpy.management.CopyRows(tmp_table, dataset_path, "")
        arcpy.AddMessage("Copy Rows:\t{0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
        # Remove the temporary table
        arcpy.management.Delete(tmp_table)
        del tmp_table
        #arcpy.conversion.ExportTable(in_table = dataset_path, out_table  = rf"{csv_data_folder}\_{table_name}.csv", where_clause="", use_field_alias_as_name = "NOT_USE_ALIAS")
        #arcpy.AddMessage("Export Table:\t{0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
        # Alter Fields
        dismap_tools.alter_fields(csv_data_folder, dataset_path)
        dismap_tools.import_metadata(csv_data_folder=csv_data_folder,dataset=dataset_path)
        # Load Metadata
        #dataset_md = md.Metadata(dataset_path)
        #dataset_md.synchronize("ALWAYS")
        #dataset_md.save()
        #del dataset_md
        arcpy.AddMessage(f"Compacting the {os.path.basename(project_gdb)} GDB")
        arcpy.management.Compact(project_gdb)
        arcpy.AddMessage("\t"+arcpy.GetMessages().replace("\n", "\n\t"))
        # Basic variables
        del dataset_path
        del table_name, csv_data_folder, project_folder, scratch_workspace
        # Imports
        del dismap_tools, md, pd, np, warnings
        # Function parameters
        del project_gdb, csv_file
    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(arcpy.GetMessages(1))
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
        raise SystemExit
    except SystemExit:
        sys.exit()
    except Exception:
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
        raise SystemExit
    except:  # noqa: E722
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
        raise SystemExit
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk:
            arcpy.AddMessage(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function at line number {inspect.stack()[0][2]}\n\t##--> '{', '.join(rk)}' <--##")
        del rk
        return True
    finally:
        pass
def update_datecode(csv_file="", project_name=""):
    try:
        #sys.path.append(os.path.abspath('../dev'))
        # Imports
        import dismap_tools
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
        field_csv_dtypes = dismap_tools.dTypesCSV(csv_data_folder, table_name)
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
        arcpy.AddMessage(f"\tNew Date Code: {dismap_tools.date_code(project_name)}")
        df = df.replace(regex = old_date_code, value = dismap_tools.date_code(project_name))
        df.to_csv(path_or_buf = f"{csv_file}", sep = ',')
        del df, pd, warnings
        del old_date_code
        arcpy.AddMessage(f"\tCompleted updating CSV file: {os.path.basename(csv_file)}")
        # Declared Variables
        del field_csv_dtypes, table_name, csv_data_folder
        # Imports
        del dismap_tools
        # Function parameters
        del csv_file, project_name
    except KeyboardInterrupt:
        raise SystemExit
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(arcpy.GetMessages(1))
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
        raise SystemExit
    except SystemExit:
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
        raise SystemExit
    except Exception:
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
        raise SystemExit
    except:  # noqa: E722
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
        raise SystemExit
    else:
        # While in development, leave here. For test, move to finally
        rk = [key for key in locals().keys() if not key.startswith('__')]
        if rk:
            arcpy.AddMessage(f"WARNING!! Remaining Keys in the '{inspect.stack()[0][3]}' function at line number {inspect.stack()[0][2]}\n\t##--> '{', '.join(rk)}' <--##")
        del rk
        return True
    finally:
        pass
def script_tool(project_folder=""):
    """Script code goes below"""
    try:
        from lxml import etree
        from arcpy import metadata as md
        from  io import StringIO
        import dismap_tools
        from time import gmtime, localtime, strftime, time
        # Set a start time so that we can see how log things take
        start_time = time()
        arcpy.AddMessage(f"{'-' * 80}")
        arcpy.AddMessage(f"Python Script:  {os.path.basename(__file__)}")
        arcpy.AddMessage(f"Location:       .. {'/'.join(__file__.split(os.sep)[-4:])}")
        arcpy.AddMessage(f"Python Version: {sys.version}")
        arcpy.AddMessage(f"Environment:    {os.path.basename(sys.exec_prefix)}")
        arcpy.AddMessage(f"{'-' * 80}\n")
        # Imports
        #from dev_import_datasets_species_filter_csv_data import worker
        # Set basic arcpy.env variables
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"
        #project_folder      = rf"{os.path.dirname(project_gdb)}"
        project_name        = rf"{os.path.basename(project_folder)}"
        project_gdb         = rf"{project_folder}\{project_name}.gdb"
        home_folder         = rf"{os.path.dirname(project_folder)}"
        csv_data_folder     = rf"{project_folder}\CSV_Data"
        datasets_csv        = rf"{csv_data_folder}\Datasets.csv"
        species_filter_csv  = rf"{csv_data_folder}\Species_Filter.csv"
        survey_metadata_csv = rf"{csv_data_folder}\DisMAP_Survey_Info.csv"
        SpeciesPersistenceIndicatorTrend = rf"{csv_data_folder}\SpeciesPersistenceIndicatorTrend.csv"
        SpeciesPersistenceIndicatorPercentileBin = rf"{csv_data_folder}\SpeciesPersistenceIndicatorPercentileBin.csv"
        arcpy.management.Copy(rf"{home_folder}\Initial Data\Datasets_{dismap_tools.date_code(project_name)}.csv", datasets_csv)
        arcpy.management.Copy(rf"{home_folder}\Initial Data\Species_Filter_{dismap_tools.date_code(project_name)}.csv", species_filter_csv)
        arcpy.management.Copy(rf"{home_folder}\Initial Data\DisMAP_Survey_Info_{dismap_tools.date_code(project_name)}.csv", survey_metadata_csv)
        arcpy.management.Copy(rf"{home_folder}\Initial Data\SpeciesPersistenceIndicatorTrend_{dismap_tools.date_code(project_name)}.csv", SpeciesPersistenceIndicatorTrend)
        arcpy.management.Copy(rf"{home_folder}\Initial Data\SpeciesPersistenceIndicatorPercentileBin_{dismap_tools.date_code(project_name)}.csv", SpeciesPersistenceIndicatorPercentileBin)
        import json
        json_path = rf"{csv_data_folder}\root_dict.json"
        with open(json_path, "r") as json_file:
            root_dict = json.load(json_file)
        del json_file
        del json_path
        del json
        contacts = rf"{home_folder}\Datasets\DisMAP Contacts 2026 02 01.xml"
        datasets = [datasets_csv, species_filter_csv, survey_metadata_csv, SpeciesPersistenceIndicatorTrend, SpeciesPersistenceIndicatorPercentileBin]
        for dataset in datasets:
            arcpy.AddMessage(rf"Metadata for: {os.path.basename(dataset)}")
            dataset_md = md.Metadata(dataset)
            dataset_md.synchronize("ALWAYS")
            dataset_md.save()
            dataset_md.importMetadata(contacts, "ARCGIS_METADATA")
            dataset_md.save()
            dataset_md.synchronize("OVERWRITE")
            dataset_md.save()
            dataset_md.synchronize("ALWAYS")
            dataset_md.save()
            target_tree = etree.parse(StringIO(dataset_md.xml), parser=etree.XMLParser(encoding='UTF-8', remove_blank_text=True))
            target_root = target_tree.getroot()
            target_root[:] = sorted(target_root, key=lambda x: root_dict[x.tag])  # noqa: F821
            new_item_name = target_root.find("Esri/DataProperties/itemProps/itemName").text
            #arcpy.AddMessage(new_item_name)
            etree.indent(target_root, space='    ')
            dataset_md.xml = etree.tostring(target_tree, encoding='UTF-8', method='xml', xml_declaration=True, pretty_print=True)
            dataset_md.save()
            dataset_md.synchronize("ALWAYS")
            dataset_md.save()
            #arcpy.AddMessage(dataset_md.xml)
            del dataset_md
            del dataset
        del datasets
        del csv_data_folder
        #
        UpdateDatecode = True
        if UpdateDatecode:
            # Update DateCode
            #arcpy.AddMessage(datasets_csv)
            arcpy.AddMessage(project_name)
            update_datecode(csv_file=datasets_csv, project_name=project_name)
        del UpdateDatecode
        #
        DatasetsCSVFile = True
        if DatasetsCSVFile:
            worker(project_gdb=project_gdb, csv_file=datasets_csv)
        del DatasetsCSVFile
        #
        SpeciesFilterCSVFile = True
        if SpeciesFilterCSVFile:
            worker(project_gdb=project_gdb, csv_file=species_filter_csv)
        del SpeciesFilterCSVFile
        #
        DisMAPSurveyInfoFile = True
        if DisMAPSurveyInfoFile:
            worker(project_gdb=project_gdb, csv_file=survey_metadata_csv)
        del DisMAPSurveyInfoFile
        #
        SpeciesPersistenceIndicatorPercentileBinFile = True
        if SpeciesPersistenceIndicatorPercentileBinFile:
            worker(project_gdb=project_gdb, csv_file=SpeciesPersistenceIndicatorPercentileBin)
        del SpeciesPersistenceIndicatorPercentileBinFile
        #
        SpeciesPersistenceIndicatorTrendFile = True
        if SpeciesPersistenceIndicatorTrendFile:
            worker(project_gdb=project_gdb, csv_file=SpeciesPersistenceIndicatorTrend)
        del SpeciesPersistenceIndicatorTrendFile
        # # # # # #
        # Declared Varaiables
        del SpeciesPersistenceIndicatorPercentileBin, SpeciesPersistenceIndicatorTrend
        del datasets_csv, species_filter_csv, survey_metadata_csv, home_folder, project_name
        # Declared Variables
        del contacts, target_tree, target_root, new_item_name, root_dict
        # Imports
        del etree, md, StringIO, dismap_tools
        # Function Parameters
        del project_folder
        # Elapsed time
        end_time = time()
        elapse_time =  end_time - start_time
        arcpy.AddMessage(f"\n{'-' * 80}")
        arcpy.AddMessage(f"Python script: {os.path.basename(__file__)}\nCompleted: {strftime('%a %b %d %I:%M %p', localtime())}")
        arcpy.AddMessage(u"Elapsed Time {0} (H:M:S)".format(strftime("%H:%M:%S", gmtime(elapse_time))))
        arcpy.AddMessage(f"{'-' * 80}")
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

        project_folder = arcpy.GetParameterAsText(0)
        if not project_folder:
            project_folder = os.path.join(os.path.expanduser('~'), "Documents\\ArcGIS\\Projects\\DisMAP\\ArcGIS-Analysis-Python\\February 1 2026")
        else:
            pass

        script_tool(project_folder)

        arcpy.SetParameterAsText(1, "Result")

        del project_folder

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