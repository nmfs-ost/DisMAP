"""
Script documentation
- Tool parameters are accessed using arcpy.GetParameter() or
                                     arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or
                                        arcpy.SetParameterAsText()
"""
import os
# type: ignore # Temporarily ignore Pylance messages for development mode
import sys
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
        #print("Detected Encoding:", __encoding)
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
    except arcpy.ExecuteWarning:
        arcpy.AddWarning(
            f"ArcPy Execute Warning in '{inspect.stack()[0][3]}':\n{arcpy.GetMessages(1)}"
        )
    except arcpy.ExecuteError:
        arcpy.AddError(
            f"ArcPy Execute Error in '{inspect.stack()[0][3]}':\n{arcpy.GetMessages(2)}"
        )
        arcpy.AddError(f"Traceback:\n{traceback.print_exc()}")
    except SystemExit:
        # This is not an error, so we allow the script to exit.
        pass
    except Exception as e:
        arcpy.AddError(
            f"An unexpected error occurred in '{inspect.stack()[0][3]}': {e}"
        )
        arcpy.AddError("Traceback:\n")
        traceback.print_exc()
    else:
        return __encoding, __index_column

def worker(project_gdb="", csv_file=""):
    try:
        # Imports
        import pandas as pd
        import numpy as np
        import warnings
        #import shutil
        #from reportlab.lib.pagesizes import letter  # noqa: F401
        #from reportlab.platypus import SimpleDocTemplate, Paragraph  # noqa: F401
        #from reportlab.lib.styles import getSampleStyleSheet  # noqa: F401
        #import webbrowser

        from lxml import etree
        from  io import StringIO
        import json

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
        project_name      = rf"{os.path.basename(project_folder)}"
        home_folder       = rf"{os.path.dirname(project_folder)}"

        arcgis_metadata   = rf"{project_folder}\Metadata_ArcGIS"
        # inport_metadata   = rf"{project_folder}\Metadata_InPort"

        # Set basic workkpace variables
        arcpy.env.workspace                = project_gdb
        arcpy.env.scratchWorkspace         = r"Scratch\\scratch.gdb"
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"
        # print(table_name)
        # print(csv_data_folder)

        field_csv_dtypes = dismap_tools.dTypesCSV(csv_data_folder, table_name)
        field_gdb_dtypes = dismap_tools.dTypesGDB(csv_data_folder, table_name)

        #print(field_csv_dtypes)
        # print(field_gdb_dtypes)

        print(f"\tCreating Table: {table_name}")
        arcpy.management.CreateTable(project_gdb, f"{table_name}", "", "", table_name.replace("_", " "))
        print("\t{0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

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
        #encoding, index_column = dismap_tools.get_encoding_index_col(csv_file)
        encoding, index_column = get_encoding_index_col(csv_file) # pyright: ignore[reportGeneralTypeIssues]
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
        except Exception as e:
            arcpy.AddError(
                f"An unexpected error occurred in '{inspect.stack()[0][3]}': {e}"
            )
            arcpy.AddError("Traceback:\n")
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
        except Exception as e:
            arcpy.AddError(
                f"An unexpected error occurred in '{inspect.stack()[0][3]}': {e}"
            )
            arcpy.AddError("Traceback:\n")
            traceback.print_exc()
            raise SystemExit

        print(f">-> Copying the {table_name} Table from memory to the GDB")
        fields = [f.name for f in arcpy.ListFields(tmp_table) if f.type == "String"]
        for field in fields:
            arcpy.management.CalculateField(tmp_table, field=field, expression=f"'' if !{field}! is None else !{field}!")
            print("Calculate Field:\t{0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))
            del field
        del fields

        dataset_path = rf"{project_gdb}\{table_name}"
        arcpy.management.CopyRows(tmp_table, dataset_path, "")
        print("Copy Rows:\t{0}\n".format(arcpy.GetMessages().replace("\n", '\n\t')))

        # Remove the temporary table
        arcpy.management.Delete(tmp_table)
        del tmp_table

        # Alter Fields
        dismap_tools.alter_fields(csv_data_folder, dataset_path)

        version_code = dismap_tools.date_code(project_name)

        contacts = rf"{home_folder}\Initial-Data\DisMAP_Contacts_{version_code}.xml"

        # print(contacts)
        etree.parse(contacts, parser=etree.XMLParser(encoding='UTF-8', remove_blank_text=True)).write(contacts, pretty_print=True, xml_declaration=True, encoding="UTF-8") # pyright: ignore[reportAttributeAccessIssue]

        # Copy a file to a new file or into a directory
        #dismap_logo = os.path.join(home_folder, "NOAA DisMAP 2026 Final [Logo].png")
        #table_thumbnail = os.path.join(home_folder, "table_thumbnail.png")
        #shutil.copy(dismap_logo, table_thumbnail)

        xml_file = os.path.join(arcgis_metadata, f"{os.path.basename(dataset_path)}.xml")

        # Load Metadata
        #contacts_md = md.Metadata(contacts)
        dataset_md  = md.Metadata(dataset_path)
        dataset_md.save()
        dataset_md.synchronize("ALWAYS")
        dataset_md.save()
        if not arcpy.Exists(xml_file):
            dataset_md.importMetadata(contacts, "ARCGIS_METADATA")
        else:
            dataset_md.importMetadata(xml_file, "ARCGIS_METADATA")
        #dataset_md.copy(contacts_md)
        dataset_md.save()
        dataset_md.synchronize("ALWAYS")
        dataset_md.save()
        #dataset_md.thumbnailUri = table_thumbnail
        #dataset_md.save()
        #print(dataset_md.thumbnailUri)
        #del contacts_md
        del dataset_md
        del xml_file

        # Import Metadata
        dismap_tools.import_metadata(csv_data_folder=csv_data_folder, dataset=dataset_path)

##        #dataset_md.importMetadata(rf"{os.path.join(csv_data_folder, table_name)}.xml", "ARCGIS_METADATA")
##        #dataset_md.save()
##        dataset_md.synchronize("ALWAYS")
##        dataset_md.save()

        dataset_md  = md.Metadata(dataset_path)

        parser = etree.XMLParser(encoding="UTF-8", remove_blank_text=True) # pyright: ignore[reportAttributeAccessIssue]
        tree = etree.parse(StringIO(dataset_md.xml), parser=parser) # pyright: ignore[reportAttributeAccessIssue]
        root = tree.getroot()

        old_linkage = root.find("./distInfo/distTranOps/onLineSrc/linkage").text
        new_item_name = root.find("Esri/DataProperties/itemProps/itemName").text + "_" + version_code
        old_item_name = old_linkage[old_linkage.find("/services/")+len("/services/"):old_linkage.find("/FeatureServer")]
        new_linkage = old_linkage.replace(old_item_name, new_item_name)
        root.find("./distInfo/distTranOps/onLineSrc/linkage").text = new_linkage

        res_title = root.find("./dataIdInfo/idCitation/resTitle").text

        root.find(".//enttypl").text = res_title if " Table " in res_title else res_title[:-9] + " Table " + version_code
        root.find(".//enttypl").attrib["Sync"] = "FALSE"

        print("*" * 75 + "\n")

        #print(res_title[-8:] if " Table " in res_title else res_title[:-9] + " Table " + version_code)

        print(root.find("./dataIdInfo/idCitation/resTitle").text)
        print(root.find(".//enttypl").text)
        print("\n" + "*" * 75)

        del res_title

        etree.indent(root, space="\t") # pyright: ignore[reportAttributeAccessIssue]
        dataset_md.xml = etree.tostring( # pyright: ignore[reportAttributeAccessIssue]
            tree,
            encoding="UTF-8",
            method="xml",
            xml_declaration=True,
            pretty_print=True,
        )
        dataset_md.save()

        del new_linkage, old_linkage
        del old_item_name, new_item_name
        del version_code
        del root, tree, parser

        json_path = os.path.join(csv_data_folder, "root_dict.json")

        with open(json_path, "r", encoding='utf-8') as json_file:
            root_dict = json.load(json_file)
        del json_file
        del json_path
        ##        root_dict = {"Esri"       :  0, "dataIdInfo" :  1, "mdChar"      :  2,
        ##                     "mdContact"  :  3, "mdDateSt"   :  4, "mdFileID"    :  5,
        ##                     "mdLang"     :  6, "mdMaint"    :  7, "mdHrLv"      :  8,
        ##                     "mdHrLvName" :  9, "refSysInfo" : 10, "spatRepInfo" : 11,
        ##                     "spdoinfo"   : 12, "dqInfo"     : 13, "distInfo"    : 14,
        ##                     "eainfo"     : 15, "contInfo"   : 16, "spref"       : 17,
        ##                     "spatRepInfo" : 18, "dataSetFn" : 19, "Binary"      : 100,}

        parser = etree.XMLParser(encoding="UTF-8", remove_blank_text=True) # pyright: ignore[reportAttributeAccessIssue]

        tree = etree.parse(StringIO(dataset_md.xml), parser=parser)  # pyright: ignore[reportAttributeAccessIssue] # To parse from a string, use the fromstring() function instead.

        del parser

        root = tree.getroot()
        for child in root.xpath("."):
            child[:] = sorted(child, key=lambda x: root_dict[x.tag])
            del child

        etree.indent(root, space="\t") # pyright: ignore[reportAttributeAccessIssue]
        dataset_md.xml = etree.tostring( # pyright: ignore[reportAttributeAccessIssue]
            tree,
            encoding="UTF-8",
            method="xml",
            xml_declaration=True,
            pretty_print=True,
        )

        del root

        dataset_md.save()

        # Save as ArcGIS Metadata XML
        #xml_file = os.path.join(arcgis_metadata, f"{os.path.basename(dataset_path)}.xml")
        #dataset_md.saveAsXML(xml_file, "REMOVE_ALL_SENSITIVE_INFO")
        #etree.parse(xml_file, parser=etree.XMLParser(encoding='UTF-8', remove_blank_text=True)).write(xml_file, pretty_print=True, xml_declaration=True, encoding="UTF-8") # pyright: ignore[reportAttributeAccessIssue]
        #webbrowser.open(xml_file)
        #del xml_file

        # Save as ArcGIS Metadata HTML
        # html_file = os.path.join(arcgis_metadata, f"{os.path.basename(dataset_path)}.html")
        # xslt_file = os.path.join(os.path.expanduser('~'), "AppData\\Local\\Programs\\ArcGIS\\Pro\\Resources\\Metadata\\Stylesheets\\ArcGIS_Imports\\htmlHeaderPro.xslt")
        # dataset_md.saveAsUsingCustomXSLT(outputPath = html_file, customStylesheetPath = xslt_file)
        # del xslt_file, html_file

        # Save as InPort Metadata XML
        #xml_file = os.path.join(inport_metadata, f"{os.path.basename(dataset_path)}.xml")
        #xsl_file = rf"{os.path.dirname(project_folder)}\Initial-Data\ArcGIS2InPort.xsl"
        #dataset_md.saveAsUsingCustomXSLT(outputPath = xml_file, customStylesheetPath = xsl_file)
        #etree.parse(xml_file, parser=etree.XMLParser(encoding='UTF-8', remove_blank_text=True)).write(xml_file, pretty_print=True, xml_declaration=True, encoding="UTF-8") # pyright: ignore[reportAttributeAccessIssue]
        #del xml_file

        del dataset_md

        # Basic variables
        del dataset_path
        del table_name, csv_data_folder, project_folder, scratch_workspace

        # Function parameters
        del project_gdb, csv_file

    except arcpy.ExecuteWarning:
        arcpy.AddWarning(
            f"ArcPy Execute Warning in '{inspect.stack()[0][3]}':\n{arcpy.GetMessages(1)}"
        )
    except arcpy.ExecuteError:
        arcpy.AddError(
            f"ArcPy Execute Error in '{inspect.stack()[0][3]}':\n{arcpy.GetMessages(2)}"
        )
        arcpy.AddError(f"Traceback:\n{traceback.print_exc()}")
    except SystemExit:
        # This is not an error, so we allow the script to exit.
        pass
    except Exception as e:
        arcpy.AddError(
            f"An unexpected error occurred in '{inspect.stack()[0][3]}': {e}"
        )
        arcpy.AddError("Traceback:\n")
        traceback.print_exc()
    else:
        return True


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

        old_date_code = str(df.DateCode.unique()[0])

        #new_date_code = dismap_tools.date_code(project_name)

        #print(f"\tOld Date Code: {old_date_code}")
        #print(f"\tNew Date Code: {new_date_code}")
        # print(old_date_code)
        # print(type(old_date_code))
        # print(new_date_code)
        # print(type(new_date_code))
        # raise SystemExit

        df = df.replace(regex = old_date_code, value = dismap_tools.date_code(project_name))

        df.to_csv(path_or_buf = f"{csv_file}", sep = ',')

        del df, pd, warnings
        del old_date_code

        print(f"\tCompleted updating CSV file: {os.path.basename(csv_file)}")

        # Declared Variables
        del field_csv_dtypes, table_name, csv_data_folder
        # Imports
        del dismap_tools
        # Function parameters
        del csv_file, project_name

    except arcpy.ExecuteWarning:
        arcpy.AddWarning(
            f"ArcPy Execute Warning in '{inspect.stack()[0][3]}':\n{arcpy.GetMessages(1)}"
        )
    except arcpy.ExecuteError:
        arcpy.AddError(
            f"ArcPy Execute Error in '{inspect.stack()[0][3]}':\n{arcpy.GetMessages(2)}"
        )
        arcpy.AddError("Traceback:\n")
        traceback.print_exc()
    except SystemExit:
        # This is not an error, so we allow the script to exit.
        pass
    except Exception as e:
        arcpy.AddError(
            f"An unexpected error occurred in '{inspect.stack()[0][3]}': {e}"
        )
        arcpy.AddError("Traceback:\n")
        traceback.print_exc()
    else:
        # print("\nScript finished successfully.")
        return True

def metadata_arcgis_worker(project_gdb="", csv_file=""):
    try:
        # Imports
        #import shutil

        from lxml import etree
        from  io import StringIO
        import json

        from arcpy import metadata as md
        import dismap_tools

        # Set basic workkpace variables
        table_name        = os.path.basename(csv_file).replace(".csv", "")
        dataset_path      = os.path.join(project_gdb, table_name)
        csv_data_folder   = os.path.dirname(csv_file)
        project_folder    = os.path.dirname(project_gdb)
        scratch_workspace = os.path.join(project_folder, "Scratch\\scratch.gdb")
        project_name      = rf"{os.path.basename(project_folder)}"
        #home_folder       = rf"{os.path.dirname(project_folder)}"

        arcgis_metadata   = rf"{project_folder}\Metadata_ArcGIS"
        inport_metadata   = rf"{project_folder}\Metadata_InPort"

        # Set basic workkpace variables
        arcpy.env.workspace                = project_gdb
        arcpy.env.scratchWorkspace         = r"Scratch\\scratch.gdb"
        arcpy.env.overwriteOutput          = True
        arcpy.env.parallelProcessingFactor = "100%"
        # print(table_name)
        # print(csv_data_folder)


        # Load Metadata
        dataset_md  = md.Metadata(dataset_path)

        parser = etree.XMLParser(encoding="UTF-8", remove_blank_text=True) # pyright: ignore[reportAttributeAccessIssue]
        tree = etree.parse(StringIO(dataset_md.xml), parser=parser) # pyright: ignore[reportAttributeAccessIssue]
        root = tree.getroot()

        print("*" * 75 + "\n")

        create_date = root.xpath("/metadata/Esri/CreaDate")

        if len(create_date) > 1:
            for i in range(1, len(create_date)):
                create_date[i].getparent().remove(create_date[i])

        if len(create_date) == 1:
            print(f"Create Date exists: {create_date[0].text}")
            create_date[0].text = dismap_tools.date_code(project_name)

        elif len(create_date) == 0:
            print("Create Date does not exists")
            esri = root.xpath("/metadata/Esri")[0]
            _create_date = etree.SubElement(esri, "CreaDate")
            _create_date.text = dismap_tools.date_code(project_name)
            del esri, _create_date
        else:
            pass
        del create_date

        create_time = root.xpath("/metadata/Esri/CreaTime")

        if len(create_time) > 1:
            for i in range(1, len(create_time)):
                create_time[i].getparent().remove(create_time[i])

        if len(create_time) == 1:
            print(f"Create Time exists: {create_time[0].text}")
            create_time[0].text = "00000000"

        elif len(create_time) == 0:
            print("Create Time does not exists")
            esri = root.xpath("/metadata/Esri")[0]
            _create_time = etree.SubElement(esri, "CreaTime")
            _create_time.text = "00000000"
            del esri, _create_time
        else:
            pass
        del create_time

        print("\n" + "*" * 75)

        etree.indent(root, space="\t") # pyright: ignore[reportAttributeAccessIssue]
        dataset_md.xml = etree.tostring( # pyright: ignore[reportAttributeAccessIssue]
            tree,
            encoding="UTF-8",
            method="xml",
            xml_declaration=True,
            pretty_print=True,
        )

        del tree, root

        dataset_md.save()

        json_path = os.path.join(csv_data_folder, "root_dict.json")

        with open(json_path, "r", encoding='utf-8') as json_file:
            root_dict = json.load(json_file)

        del json_file, json_path

        #        root_dict = {"Esri"       :  0, "dataIdInfo" :  1, "mdChar"      :  2,
        #                     "mdContact"  :  3, "mdDateSt"   :  4, "mdFileID"    :  5,
        #                     "mdLang"     :  6, "mdMaint"    :  7, "mdHrLv"      :  8,
        #                     "mdHrLvName" :  9, "refSysInfo" : 10, "spatRepInfo" : 11,
        #                     "spdoinfo"   : 12, "dqInfo"     : 13, "distInfo"    : 14,
        #                     "eainfo"     : 15, "contInfo"   : 16, "spref"       : 17,
        #                     "spatRepInfo" : 18, "dataSetFn" : 19, "Binary"      : 100,}

        parser = etree.XMLParser(encoding="UTF-8", remove_blank_text=True) # pyright: ignore[reportAttributeAccessIssue]

        tree = etree.parse(StringIO(dataset_md.xml), parser=parser)  # pyright: ignore[reportAttributeAccessIssue] # To parse from a string, use the fromstring() function instead.

        del parser

        root = tree.getroot()
        for child in root.xpath("."):
            child[:] = sorted(child, key=lambda x: root_dict[x.tag])
            del child

        etree.indent(root, space="\t") # pyright: ignore[reportAttributeAccessIssue]
        dataset_md.xml = etree.tostring( # pyright: ignore[reportAttributeAccessIssue]
            tree,
            encoding="UTF-8",
            method="xml",
            xml_declaration=True,
            pretty_print=True,
        )

        del root

        dataset_md.save()

        # Save as ArcGIS Metadata XML
        xml_file = os.path.join(arcgis_metadata, f"{os.path.basename(dataset_path)}.xml")
        #dataset_md.saveAsXML(xml_file, "REMOVE_ALL_SENSITIVE_INFO")
        dataset_md.saveAsXML(xml_file)
        etree.parse(xml_file, parser=etree.XMLParser(encoding='UTF-8', remove_blank_text=True)).write(xml_file, pretty_print=True, xml_declaration=True, encoding="UTF-8") # pyright: ignore[reportAttributeAccessIssue]
        #webbrowser.open(xml_file)
        del xml_file

        # Save as ArcGIS Metadata HTML
        # html_file = os.path.join(arcgis_metadata, f"{os.path.basename(dataset_path)}_2.xml")
        # xslt_file = os.path.join(os.path.expanduser('~'), "AppData\\Local\\Programs\\ArcGIS\\Pro\\Resources\\Metadata\\Stylesheets\\ArcGIS_Imports\\htmlHeaderPro.xslt")
        # dataset_md.saveAsUsingCustomXSLT(outputPath = html_file, customStylesheetPath = xslt_file)
        # del xslt_file, html_file

        # Save as InPort Metadata XML
        xml_file = os.path.join(inport_metadata, f"{os.path.basename(dataset_path)}.xml")
        xsl_file = rf"{os.path.dirname(project_folder)}\Initial-Data\ArcGIS2InPort.xsl"
        dataset_md.saveAsUsingCustomXSLT(outputPath = xml_file, customStylesheetPath = xsl_file)
        etree.parse(xml_file, parser=etree.XMLParser(encoding='UTF-8', remove_blank_text=True)).write(xml_file, pretty_print=True, xml_declaration=True, encoding="UTF-8") # pyright: ignore[reportAttributeAccessIssue]
        del xml_file

        del dataset_md

        # Basic variables
        del dataset_path
        del table_name, project_folder, scratch_workspace, csv_data_folder

        # Function parameters
        del project_gdb, csv_file

    except arcpy.ExecuteWarning:
        arcpy.AddWarning(
            f"ArcPy Execute Warning in '{inspect.stack()[0][3]}':\n{arcpy.GetMessages(1)}"
        )
    except arcpy.ExecuteError:
        arcpy.AddError(
            f"ArcPy Execute Error in '{inspect.stack()[0][3]}':\n{arcpy.GetMessages(2)}"
        )
        arcpy.AddError(f"Traceback:\n{traceback.print_exc()}")
    except SystemExit:
        # This is not an error, so we allow the script to exit.
        pass
    except Exception as e:
        arcpy.AddError(
            f"An unexpected error occurred in '{inspect.stack()[0][3]}': {e}"
        )
        arcpy.AddError("Traceback:\n")
        traceback.print_exc()
    else:
        return True


def script_tool(project_folder=""):
    """Script code goes below"""
    try:
        from lxml import etree
        from  io import StringIO
        #import requests

        from arcpy import metadata as md

        import dismap_tools

        #xml_file = r"C:\Users\john.f.kennedy\Documents\ArcGIS\Projects\DisMAP\ArcGIS-Analysis-Python\Initial-Data\DisMAP_Contacts_20260601.xml"
        #dismap_tools.print_xml_file(xml_file)

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

        project_name        = rf"{os.path.basename(project_folder)}"
        project_gdb         = rf"{project_folder}\{project_name}.gdb"
        home_folder         = rf"{os.path.dirname(project_folder)}"
        csv_data_folder     = rf"{project_folder}\CSV_Data"
        datasets_csv        = rf"{csv_data_folder}\Datasets.csv"
        species_filter_csv  = rf"{csv_data_folder}\Species_Filter.csv"
        survey_metadata_csv = rf"{csv_data_folder}\DisMAP_Survey_Info.csv"

        SpeciesPersistenceIndicatorTrend = rf"{csv_data_folder}\SpeciesPersistenceIndicatorTrend.csv"
        SpeciesPersistenceIndicatorPercentileBin = rf"{csv_data_folder}\SpeciesPersistenceIndicatorPercentileBin.csv"
        SpatialGroup_SpeciesPersistenceIndicator = rf"{csv_data_folder}\SpatialGroup_SpeciesPersistenceIndicator.csv"

        arcpy.management.Copy(rf"{home_folder}\Initial-Data\Datasets_{dismap_tools.date_code(project_name)}.csv", datasets_csv)
        arcpy.management.Copy(rf"{home_folder}\Initial-Data\Species_Filter_{dismap_tools.date_code(project_name)}.csv", species_filter_csv)
        arcpy.management.Copy(rf"{home_folder}\Initial-Data\DisMAP_Survey_Info_{dismap_tools.date_code(project_name)}.csv", survey_metadata_csv)
        arcpy.management.Copy(rf"{home_folder}\Initial-Data\SpeciesPersistenceIndicatorTrend_{dismap_tools.date_code(project_name)}.csv", SpeciesPersistenceIndicatorTrend)
        arcpy.management.Copy(rf"{home_folder}\Initial-Data\SpeciesPersistenceIndicatorPercentileBin_{dismap_tools.date_code(project_name)}.csv", SpeciesPersistenceIndicatorPercentileBin)
        arcpy.management.Copy(rf"{home_folder}\Initial-Data\SpatialGroup_SpeciesPersistenceIndicator_{dismap_tools.date_code(project_name)}.csv", SpatialGroup_SpeciesPersistenceIndicator)

        del csv_data_folder
        #
        UpdateDatecode = False
        if UpdateDatecode:
            # Update DateCode
            #arcpy.AddMessage(datasets_csv)
            arcpy.AddMessage(project_name)
            update_datecode(csv_file=datasets_csv, project_name=project_name)
        del UpdateDatecode
        #
        DatasetsCSVFile = True
        if DatasetsCSVFile:
            # Worker: creates table, loads data, imports metadata, and then saves an XML
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
            # Worker: creates table, loads data, imports metadata, and then saves an XML
            worker(project_gdb=project_gdb, csv_file=survey_metadata_csv)
        del DisMAPSurveyInfoFile
        #
        SpeciesPersistenceIndicatorPercentileBinFile = False
        if SpeciesPersistenceIndicatorPercentileBinFile:
            # Worker: creates table, loads data, imports metadata, and then saves an XML
            worker(project_gdb=project_gdb, csv_file=SpeciesPersistenceIndicatorPercentileBin)
        del SpeciesPersistenceIndicatorPercentileBinFile
        #
        SpeciesPersistenceIndicatorTrendFile = False
        if SpeciesPersistenceIndicatorTrendFile:
            # Worker: creates table, loads data, imports metadata, and then saves an XML
            worker(project_gdb=project_gdb, csv_file=SpeciesPersistenceIndicatorTrend)
        del SpeciesPersistenceIndicatorTrendFile
        #
        SpatialGroup_SpeciesPersistenceIndicatorFile = False
        if SpatialGroup_SpeciesPersistenceIndicatorFile:
            # Worker: creates table, loads data, imports metadata, and then saves an XML
            worker(project_gdb=project_gdb, csv_file=SpatialGroup_SpeciesPersistenceIndicator)
        del SpatialGroup_SpeciesPersistenceIndicatorFile

        # Export Meatadata
        metadata_arcgis_worker(project_gdb = project_gdb, csv_file = species_filter_csv)
        metadata_arcgis_worker(project_gdb = project_gdb, csv_file = survey_metadata_csv)
        metadata_arcgis_worker(project_gdb = project_gdb, csv_file = SpeciesPersistenceIndicatorPercentileBin)
        metadata_arcgis_worker(project_gdb = project_gdb, csv_file = SpeciesPersistenceIndicatorTrend)
        metadata_arcgis_worker(project_gdb = project_gdb, csv_file = SpatialGroup_SpeciesPersistenceIndicator)

        #print(f"Compacting the {os.path.basename(project_gdb)} GDB")
        arcpy.management.Compact(project_gdb)
        #print("\t"+arcpy.GetMessages().replace("\n", "\n\t"))

        # # # # # #
        # Declared Varaiables
        del SpeciesPersistenceIndicatorPercentileBin, SpeciesPersistenceIndicatorTrend
        del datasets_csv, species_filter_csv, survey_metadata_csv, home_folder, project_name

        # Imports
        del etree, md, StringIO, dismap_tools
        # Function Parameters
        del project_folder

    except arcpy.ExecuteWarning:
        arcpy.AddWarning(
            f"ArcPy Execute Warning in '{inspect.stack()[0][3]}':\n{arcpy.GetMessages(1)}"
        )
    except arcpy.ExecuteError:
        arcpy.AddError(
            f"ArcPy Execute Error in '{inspect.stack()[0][3]}':\n{arcpy.GetMessages(2)}"
        )
        arcpy.AddError("Traceback:\n")
        traceback.print_exc()
    except SystemExit:
        # This is not an error, so we allow the script to exit.
        pass
    except Exception as e:
        arcpy.AddError(
            f"An unexpected error occurred in '{inspect.stack()[0][3]}': {e}"
        )
        arcpy.AddError("Traceback:")
        traceback.print_exc()
    else:
        arcpy.AddMessage("\nScript finished successfully.\n")
    finally:
        arcpy.AddMessage(f"\n{'--End' * 10}--")


if __name__ == '__main__':
    try:

        project_folder = arcpy.GetParameterAsText(0)
        if not project_folder:
            # project_name = "February-1-2026"
            # project_name = "August-1-2025"
            project_name = "June-1-2026"
            project_folder = os.path.join(os.path.expanduser('~'), f"Documents\\ArcGIS\\Projects\\DisMAP\\ArcGIS-Analysis-Python\\{project_name}")
        else:
            pass

        script_tool(project_folder)

        arcpy.SetParameterAsText(1, "Result")

        del project_folder

    except SystemExit:
        # This is not an error, so we allow the script to exit.
        pass
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages(2))
        traceback.print_exc()
    except Exception:
        traceback.print_exc()


# This is an autogenerated comment.
