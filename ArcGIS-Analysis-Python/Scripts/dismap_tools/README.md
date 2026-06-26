# DisMAP ArcGIS Pro Analysis using Python
> This code is always in development. Find the code used for various reports in the code [releases](https://github.com/nmfs-fish-tools/DisMAP/releases).

### Table of contents ###

> - [*Purpose*](#purpose)
> - [*DisMAP Processing Steps*](#dismap-processing-steps)
> - [*DisMAP ArcGIS Python Processing Setup*](#dismap-arcigs-python-processing-setup)
>   - [Zip and Unzip CSV Data](#zip-and-unzip-csv-data)
>   - [Zip and Unzip Shapefile Data](#zip-and-unzip-shapefile-data)
>   - [DisMAP Tools](#dismap-tools)
>   - [DisMAP Project Setup](#dismap-project-setup)
>   - [Create Base Bathymetry](#create-base-bathymetry)
>   - [Create Data Dictionary JSON Files](#create-data-dictionary-json-files)
>   - [Create Metadata JSON Files](#create-metadata-json-files)
>   - [Import Datasets Species Filter CSV Data](#import-datasets-species-filter-csv-data)
> - [*DisMAP ArcGIS Python Processing*](#dismap-arcigs-python-processing)
>   - [Create Regions from Shapefiles Director and Worker](#create-regions-from-shapefiles-director-and-worker)
>   - [Create Region Fishnets Director and Worker](#create-region-fishnets-director-and-worker)
>   - [Create Region Bathymetry Director and Worker](#create-region-bathymetry-director-and-worker)
>   - [Create Region Sample Locations Director and Worker](#create-region-sample-locations-director-and-worker)
>   - [Create Region Species Year Image Name Table Director and Worker](#create-region-species-year-image-name-table-director-and-worker)
>   - [Create Region Rasters Director and Worker](#create-region-rasters-director-and-worker)
>   - [Create Region Species Richness Director and Worker](#create-region-species-richness-director-and-worker)
>   - [Create Region Mosaics Director and Worker](#create-region-mosaics-director-and-worker)
>   - [Create Region Indicators Table Direcor and Worker](#create-region-indicators-table-director-and-worker)
>   - [Publish to Portal Director](#publish-to-portal-director)
> - [*Suggestions and Comments*](#suggestions-and-comments)
> - [*NOAA README*](#noaa-readme)
> - [*NOAA-NMFS GitHub Enterprise Disclaimer*](#noaa-nmfs-github-enterprise-disclaimer)
> - [*NOAA License*](#noaa-license)

### *Purpose*
These Python scripts were developed for the DisMAP ArcGIS Python Processing phase of the project. In general the scripts listed below are ran in the order they are presented in a Python IDE such as [*Pyscripter*](https://sourceforge.net/projects/pyscripter/).

# DisMAP Processing Steps
- ### Step 1 create a folder for this project

- ### Step 2 create an ArcGIS Pro project, call it DisMAP, and save in the folder above

- ### Step 3 create three folders: Bathymetry, Dataset Shapefiles, and Initial Data, or use the python script dismap_base_project.py script

- ### Step 4 place the contents of the Bathemetry zip file into the "Bathemetry folder"

- ### Step 5 place the contents of the CSV zip file intp the "Initial Data" folder

- ### Step 6 place the contents of the Dataset Shapefiles.zip file into the Dataset Shapefiles folder

- ### Step 7 Update the create_base_bathymetry.py file by changing the project_folder variable to the base project folder created above

- ### Step 8 Update the dismap_version_project_setup.py file by changing the new_project_folder variable to a version date, like "February 1 2026". Then run the script

- ### Step 9 Update the create_data_dictionary_json_files.py file by changing the project_gdb variable to a version date, like "February 1 2026". Then run the script

- ### Step 10 Update the create_metadata_json_files.py file by changing the project_folder variable to a version date, like "February 1 2026". Then run the script

- ### Step 11 Update the import_datasets_species_filter_csv_data.py file by changing the project_gdb variable to a version date, like "February 1 2026". Then run the script

- ### Step 12 Copy the contents from the folder "Dataset Shapefiles" to the version project folder "Dataset_Shapefiles"

- ### Step 13 Update the create_regions_from_shapefiles_director.py file by changing the project_gdb variable to a version date, like "February 1 2026". Then run the script

- ### Step 14 Update the create_region_fishnets_director.py file by changing the project_gdb variable to a version date, like "February 1 2026". Then run the script

- ### Step 15 Update the create_region_bathymetry_director.py file by changing the project_gdb variable by updating the version folder. For example: from "Project Folder\August 1 2025\August 1 2025.gdb" to "Project Folder\February 1 2026\February 1 2026.gdb". Then run the script

- ### Step 16 Update the create_species_year_image_name_table_director.py file by changing the project_gdb variable by updating the version folder. For example: from "Project Folder\August 1 025\August 1 2025.gdb" to "Project Folder\February 1 2026\February 1 2026.gdb". Then run the script

- ### Step 17 Update the create_region_sample_locations_director.py file by changing the project_gdb variable by updating the version folder. For example: from "Project Folder\August 1 025\August 1 2025.gdb" to "Project Folder\February 1 2026\February 1 2026.gdb". Then run the script
- 
- ### Step 18 Update the create_rasters_director.py file by changing the project_gdb variable by updating the version folder. For example: from "Project Folder\August 1 025\August 1 2025.gdb" to "Project Folder\February 1 2026\February 1 2026.gdb". Then run the script

- ### Step 19 Update the create_species_richness_rasters_director.py file by changing the project_gdb variable by updating the version folder. For example: from "Project Folder\August 1 025\August 1 2025.gdb" to "Project Folder\February 1 2026\February 1 2026.gdb". Then run the script

- ### Step 20 Update the create_mosaics_director.py file by changing the project_gdb variable by updating the version folder. For example: from "Project Folder\August 1 025\August 1 2025.gdb" to "Project Folder\February 1 2026\February 1 2026.gdb". Then run the script

- ### Step 21 Update the create_indicators_table_director.py file by changing the project_gdb variable by updating the version folder. For example: from "Project Folder\August 1 025\August 1 2025.gdb" to "Project Folder\February 1 2026\February 1 2026.gdb". Then run the script

- ### Step 22  Update the publish_to_portal_director.py file by changing the project_gdb variable by updating the version folder. For example: from "Project Folder\August 1 025\August 1 2025.gdb" to "Project Folder\February 1 2026\February 1 2026.gdb". Then run the script

### *DisMAP ArcGIS Python Processing Project Setup*
- #### Zip and Unzip CSV Data
  - The [zip_and_unzip_csv_data.py](zip_and_unzip_csv_data.py) file archives/extracts sample location and biomass measurements in a CSV data file
  - The script takes the target location of were the file will be extracted and the source Zip file path
  - Extracts CSV survey data from a ZIP archive, renames files, and attaches metadata:
    1. **Extract ZIP** — Unzips files from source ZIP (e.g., `CSV Data 2025 08 01.zip`) into the project's `CSV_Data` folder
    2. **Rename CSV files** — Copies extracted `*_survey.csv` files and renames them to `*_IDW.csv` (e.g., `AI_IDW_survey.csv` → `AI_IDW.csv`)
    3. **Clean up** — Removes the temporary `python/` extraction subdirectory
    4. **Attach metadata** — For each `*_IDW.csv` file:
       - Synchronizes ArcGIS metadata
       - Imports contact/organizational metadata from `DisMAP Contacts 2025 08 01.xml`
       - Parses XML with lxml, sorts elements by a predefined `root_dict` order
       - Writes updated metadata back to file
    5. **Return path** — Returns the `CSV_Data` output directory path

  - Uses ArcGIS tool parameters and defaults to `~\Documents\ArcGIS\Projects\DisMAP\ArcGIS-Analysis-Python\August 1 2025`.
 
- #### Zip and Unzip Shapefile Data
  - The [zip_and_unzip_shapefile_data.py](zip_and_unzip_shapefile_data.py) file contains functions to archive/extract the shapefiles that represent each region
  - The script takes the target location of were the file will be extracted and the source Zip file path
  - No metadata processing or file renaming; straightforward extraction of shapefiles (e.g., `AI_IDW_Region.shp`, `EBS_IDW_Region.shp`, etc.) into their target directory
  - Extracts shapefile data from a ZIP archive:
    1. **Extract ZIP** — Unzips files from source ZIP into the project's `Dataset_Shapefiles` folder (changes working directory with `os.chdir()`)
    2. **Return path** — Returns the `Dataset_Shapefiles` output directory path
  - Uses ArcGIS tool parameters and defaults to `~\Documents\ArcGIS\Projects\DisMAP\ArcGIS-Analysis-Python\August 1 2025`.
  - Follows ArcGIS tool conventions (parameter access via `arcpy.GetParameterAsText()`, messaging via `arcpy.AddMessage()`, error handling with `arcpy.ExecuteError`)

- #### DisMAP Tools
  - The [dismap_tools.py](dismap_tools.py) file is a utility library with XML/metadata parsing, field transformation, and spatial analysis helpers using lxml & ArcPy that is imported into many of the project scripts
  
    **XML & Metadata Functions:**
    - **`parse_xml_file_format_and_save(csv_data_folder, xml_file, sort)`** — Parses and reformats XML metadata using lxml; optionally sorts elements by predefined priority order from `root_dict.json`; writes back to file
    - **`print_xml_file(xml_file, sort)`** — Displays formatted XML metadata to ArcGIS messages
    - **`compare_metadata_xml(file1, file2)`** — Compares two metadata XML files
    - **`export_metadata(csv_data_folder, in_table)`** — Exports ArcGIS metadata from a dataset
    - **`import_metadata(csv_data_folder, dataset)`** — Imports standardized metadata from JSON definitions into GDB dataset

    **Field & Table Management:**
    - **`add_fields(csv_data_folder, in_table)`** — Adds fields to a GDB table based on schema from `table_definitions.json` + `field_definitions.json`
    - **`alter_fields(csv_data_folder, in_table)`** — Updates field aliases and properties on existing fields
    - **`field_definitions(csv_data_folder, field)`** — Loads field schema dictionary from `field_definitions.json`
    - **`dTypesCSV(csv_data_folder, table)`** — Returns pandas data types for CSV columns based on table schema
    - **`dTypesGDB(csv_data_folder, table)`** — Returns NumPy data types for GDB fields based on table schema

    **Data Inspection & Utilities:**
    - **`check_datasets(datasets)`** — Logs detailed metadata (extent, cell size, date created, spatial reference, sample rows) for feature classes, rasters, and tables
    - **`check_transformation(ds, cs)`** — Validates spatial reference transformation compatibility
    - **`get_transformation(gsr_wkt, psr_wkt)`** — Gets geographic transformation between two coordinate systems
    - **`clear_folder(folder)`** — Removes all files from a folder
    - **`backup_gdb(project_gdb)`** — Creates a backup copy of geodatabase and compacts both

    **Data Lookup & Conversion:**
    - **`date_code(version)`** — Generates/extracts DateCode from project version name (e.g., `"August 1 2025"` → `"20250801"`)
    - **`convertSeconds(seconds)`** — Converts seconds to HH:MM:SS format
    - **`get_encoding_index_col(csv_file)`** — Detects CSV file encoding using `chardet`
    - **`dataset_title_dict(project_gdb)`** — Builds lookup dictionary mapping region/dataset codes to display titles
    - **`metadata_dictionary_json(csv_data_folder, dataset_name)`** — Loads metadata templates from JSON
    - **`table_definitions(csv_data_folder, field)`** — Loads table-to-fields schema mapping from JSON

    **Pattern**: Serves as central helper library for other DisMAP tools; heavily uses JSON schema files (`field_definitions.json`, `table_definitions.json`) as single source of truth for GDB structure; consistent exception handling with ArcPy logging; all functions clean up local variables at completion.

- #### DisMAP Project Setup
  - The [dismap_project_setup.py](dismap_project_setup.py) ArcGIS/ArcPy/Python script creates ArcGIS Pro project folder structure: GDB, scratch workspace, subfolders, and configures toolboxes/databases in `.aprx`
  - The input for the script is the Project Folder path (i.e. "Documents/ArcGIS/Projects/DisMAP/ArcGIS-Analysis-Python/December 1 2025")

    **Main function: `script_tool(new_project_folder, project_folders)`**

      1. **Get home folder**
         - Accesses current ArcGIS Pro project's home folder via `arcpy.mp.ArcGISProject("CURRENT")`

      2. **Create project folder structure**:
         - Creates main project folder (e.g., `"September 1 2025"`)
         - Creates project GDB: `{new_project_folder}\{new_project_folder}.gdb`
         - Creates Scratch folder: `{new_project_folder}\Scratch`
         - Creates scratch GDB: `Scratch\scratch.gdb`
         - Creates subfolders from comma-separated list (e.g., `CRFs;CSV_Data;Dataset_Shapefiles;Images;Layers;Metadata_Export;Publish`)

      3. **Configure `.aprx` file**:
         - Saves a copy of the current project as `{new_project_folder}.aprx`
         - Opens the new APRX file
         - Removes all existing maps
         - Updates project databases: sets the new project GDB as default database
         - Updates project toolboxes: registers `DisMAP.atbx` as default toolbox
         - Saves the configured APRX

      4. **Parameters**:
         - `new_project_folder` — Name of new project folder (defaults to `"September 1 2025"`)
         - `project_folders` — Semicolon-separated subfolder names (defaults to `"CRFs;CSV_Data;Dataset_Shapefiles;Images;Layers;Metadata_Export;Publish"`)

    **Pattern**: Designed to be called from ArcGIS Pro as a script tool; uses standard toolbox parameter conventions (`arcpy.GetParameterAsText()`, `arcpy.SetParameterAsText()`) and follows DisMAP folder/naming conventions (date-based project folders, standard GDB/subfolder structure).

- #### Create Base Bathymetry
  - The [create_base_bathymetry.py](create_base_bathymetry.py) ArcGIS/ArcPy/Python script processes bathymetry data for use in later scripts
  - The input for the script is the Project Folder path (i.e. "Documents/ArcGIS/Projects/DisMAP/ArcGIS-Analysis-Python/December 1 2025")
  - All functions follow ArcGIS Pro logging/error handling patterns, manage ArcPy environments (workspace, cellsize, resampling), and clean up local variables at the end. 
  - The script contains four main functions:

    1. **`raster_properties_report()`** — Utility that logs raster metadata (spatial reference, extent, cell size, statistics, pixel type) using `arcpy.AddMessage()`.

    2. **`create_alasaka_bathymetry(project_folder)`** — Processes Alaska bathymetry:
       - Copies ASCII GRID files (AI, EBS, GOA) into a geodatabase
       - Converts positive depth values to negative
       - Appends/clips rasters to ensure full coverage
       - Reprojects each region's bathymetry to its regional spatial reference (AI_IDW, EBS_IDW, etc.)
       - Copies final rasters to the project bathymetry GDB and compacts the database

    3. **`create_hawaii_bathymetry(project_folder)`** — Processes Hawaii bathymetry:
       - Converts a polygon shapefile grid (BFISH_PSU.shp) to a raster using depth field
       - Negates values and saves to GDB
       - Copies final rasters to the project bathymetry GDB and compacts the database

    4. **`gebco_bathymetry(project_folder)`** — Processes GEBCO data for all other regions:
       - Converts GEBCO ASCII rasters to GDM rasters for each region
       - Copies final rasters to the project bathymetry GDB and compacts the database

- #### Create Data Dictionary JSON Files
  - The [create_data_dictionary_json_files.py](create_data_dictionary_json_files.py) ArcGIS/ArcPy/Python script that generates JSON metadata definitions for all GDB tables and fields in the DisMAP project:

    ***Main function: `script_tool(project_folder)`***

    1. **Field Definitions Dictionary** (massive hardcoded dict covering ~200+ fields):
         - Defines every GDB field used in DisMAP with metadata:
           - `field_aliasName`, `field_name`, `field_type`, `field_length`, `field_precision`, `field_scale`
           - `field_editable`, `field_isNullable`, `field_required`
           - `field_attrdef`, `field_attrdefs`, `field_attrdomv` (ArcGIS ISO metadata attributes)
           - `field_domain` (for referential integrity links)
         - Examples: `CSVFile`, `Category`, `CellSize`, `CenterOfGravityDepth`, `CommonName`, `DateCode`, `Depth`, `Dimensions`, etc.

    2. **Table Field Mappings** (hardcoded list patterns):
         - Defines which fields belong to each table type:
           - `_Datasets` — dataset catalog fields (DatasetCode, CSVFile, TableName, Region, Season, DateCode, etc.)
           - `_Indicators` — distribution indicator fields (CenterOfGravity*, MinimumLatitude, MaximumDepth, etc.)
           - `_IDW` — Inverse Distance Weighting survey data (Species, WTCPUE, MapValue, Coordinates, Depth)
           - `_Sample_Locations` — sample point data (SampleID, Year, Species, WTCPUE, Stratum, Coordinates)
           - `_Species_Filter` — species metadata (Species, CommonName, TaxonomicGroup, FilterRegion, ManagementBody)
           - `_DisMAP_Survey_Info` — survey metadata (SurveyName, Region, Season, GearType, Years, DataSource)
           - `_SpeciesPersistenceIndicatorTrend`, `_SpeciesPersistenceIndicatorPercentileBin` — persistence indicators
           - Region-specific: `_Boundary`, `_Extent_Points`, `_Fishnet`, `_Lat_Long`, `_Mosaic`, `_Raster_Mask`

    3. **Dynamic Table-to-Fields Mapping**:
         - Iterates over hardcoded table names (15 IDW regions + 6 metadata tables)
         - For each `*_IDW` region: assigns fields + auto-generates derived table variants (Sample_Locations, Indicators, Bathymetry, Boundary, Extent_Points, Fishnet, LayerSpeciesYearImageName, Lat_Long, Latitude, Longitude, Mosaic, Raster_Mask, Region)
         - Special handling for metadata tables (Datasets, DisMAP_Regions, Indicators, Species_Filter, DisMAP_Survey_Info, SpeciesPersistenceIndicatorTrend, SpeciesPersistenceIndicatorPercentileBin)

    4. **JSON Output**:
         - Exports `field_definitions.json` → all field metadata (keyed by field name)
         - Exports `table_definitions.json` → all table field lists (keyed by table name, values are lists of field names)
         - Both written to `{project_folder}\CSV_Data\`

    5. **Cleanup & Validation**:
         - Logs all table/field mappings
         - Cross-checks that all mapped fields exist in `field_definitions`
         - Compacts GDB

    **Key Pattern**: Serves as schema/metadata registry for the entire DisMAP project; JSON files are consumed by downstream tools (e.g., import_datasets_species_filter_csv_data.py loads field schemas) to enforce consistent data types and field properties across all CSV imports and GDB operations.

- #### Create Metadata JSON Files
  - The [create_metadata_json_files.py](create_metadata_json_files.py) ArcGIS/ArcPy/Python script that generates standardized XML metadata ordering dictionaries and contact information JSON files for ArcGIS Pro metadata templates:

    **Main function: `script_tool(project_gdb)`**
    Creates and exports multiple JSON lookup/mapping files to `{project_folder}\CSV_Data\`:

    1. **`root_dict.json`**
        - XML element priority ordering for top-level ISO 19139 metadata sections:
        - Maps 21 root elements to sort order (e.g., `Esri: 0`, `dataIdInfo: 1`, `dqInfo: 2`, `distInfo: 3`)
        - Used to normalize/sort XML metadata trees consistently

    2. **`esri_dict.json`** — ArcGIS Esri-specific metadata element ordering:
        - Nested structure for `DataProperties` (lineage, itemProps, nativeExtBox, itemLocation, coordRef)
        - Maps ~15 Esri metadata subelements to sort priorities

    3. **`dataIdInfo_dict.json`** — ISO 19139 Data Identification nested element hierarchy:
        - Complex nested mapping for keyword sections (discKeys, themeKeys, placeKeys, tempKeys, otherKeys)
        - Maps spatial representation, data extent, temporal elements, and citation structures

    4. **`idCitation_dict.json`** — Resource citation element ordering:
        - Maps citation subelements (resTitle, date, presForm, citRespParty) to priorities

    5. **`contact_element_order_dict.json`** — Contact/responsible party element ordering:
        - Defines sort order for ~35 contact metadata fields (name, organization, email, phone, role, citation info)

    6. **`distInfo_dict.json`** — Distribution information element ordering:
        - Maps distribution channel metadata (distorFormat, distorCont, distTranOps)

    7. **`RoleCd_dict.json`** — Role code lookup table:
        - Maps codes (`"001"` → `"Resource Provider"`, `"007"` → `"Point of Contact"`, etc.) for 15 ISO roles

    8. **`tpCat_dict.json`** — ISO Topic Category XML snippets:
      3- Maps topic codes to pre-formatted XML strings (e.g., `"002"` → `<tpCat>...<TopicCatCd value="002">...`)

    9.  **`contact_dict.json`** — DisMAP team hardcoded contact information:
        - Defines role-based contacts: Custodian, Point of Contact, Distributor, Author, Principal Investigator, Processors
        - Names: Timothy J Haverland, Melissa Ann Karp, John F Kennedy (with @noaa.gov emails)
        - Used to populate metadata for all DisMAP datasets

      **Pattern**: All dicts are created, serialized to JSON, then immediately re-read to verify round-trip integrity. These JSON files are consumed by other tools (e.g., import_datasets_species_filter_csv_data.py, dismap_metadata_processing.py) to ensure consistent metadata formatting and sort order across all GDB objects and portal publications.

- #### Import Datasets Species Filter CSV Data
  - The [import_datasets_species_filter_csv_data.py](import_datasets_species_filter_csv_data.py) ArcGIS/ArcPy/Python script creates ArcGIS Pro project folder structure: GDB, scratch workspace, subfolders, and configures toolboxes/databases in `.aprx`
  - The input for the script is the Project Folder path (i.e. "Documents/ArcGIS/Projects/DisMAP/ArcGIS-Analysis-Python/December 1 2025") and CSV files for:
    1. Datasets
    2. Species_Filter
    3. DisMAP_Survey_Info
    4. SpeciesPersistenceIndicatorTrend
    5. SpeciesPersistenceIndicatorPercentileBin
  - Multi-function script that imports survey metadata CSVs into an ArcGIS Pro GDB and manages related utilities:

    1. **`get_encoding_index_col(csv_file)`** — Detects CSV encoding using `chardet` and identifies index column:
         - Reads raw file bytes and auto-detects character encoding
         - Uses pandas to load CSV and check if first column is `"Unnamed: 0"` (pandas-generated index)
         - Returns encoding and index column position

    2. **`worker(project_gdb, csv_file)`** — Main worker function; converts CSV to GDB table:
         - Validates GDB and CSV exist; sets ArcGIS logging/environment
         - Uses `dismap_tools` helper functions to load CSV dtypes and GDB field schema
         - Loads CSV with pandas, handling encoding/index column detection
         - Replaces NaN with empty strings; strips whitespace
         - Converts pandas DataFrame to NumPy structured array matching GDB field types
         - Writes array to temporary in-memory table, then copies to GDB using `arcpy.da.NumPyArrayToTable()`
         - Cleans up string fields (replaces None with empty strings)
         - Calls `dismap_tools.alter_fields()` to adjust field properties
         - Calls `dismap_tools.import_metadata()` to attach metadata from JSON definitions
         - Compacts the GDB

    3. **`update_datecode(csv_file, project_name)`** — Updates DateCode values in CSV:
         - Loads CSV with pandas
         - Extracts old DateCode from first row
         - Replaces all DateCode occurrences with new code based on project_name (using `dismap_tools.date_code()`)
         - Writes updated CSV back to disk

    4. **`script_tool(project_folder)`** — Orchestrates full import workflow:
         - Copies dated CSV files from `home_folder\Datasets\` to project's `CSV_Data\` folder (e.g., `Datasets_20250801.csv` → `Datasets.csv`)
         - Loads metadata template mapping from `root_dict.json`
         - Imports contact metadata from `DisMAP Contacts 2025 08 01.xml` into each CSV file
         - Parses XML with lxml, sorts elements by priority order from `root_dict`
         - Calls `update_datecode()` to update date codes in Datasets.csv
         - Calls `worker()` for each of five tables: Datasets, Species_Filter, DisMAP_Survey_Info, SpeciesPersistenceIndicatorTrend, SpeciesPersistenceIndicatorPercentileBin
         - Logs elapsed time

  - Key pattern: Heavy use of pandas for CSV parsing + NumPy array conversion to ensure type safety between CSV and GDB; metadata synchronization with lxml XML manipulation
 
### *DisMAP ArcGIS Python Processing*

- #### Director/Worker Pattern (parallel-capable processing): 
  The codebase follows a **director** → **worker** architecture for scalability:
- **Directors** orchestrate workflows and can spawn parallel jobs using `multiprocessing.Pool`
  - create_rasters_director.py — Orchestrates raster creation; supports sequential or multiprocess execution
  - create_regions_from_shapefiles_director.py — Builds region geometries
  - create_region_bathymetry_director.py — Bathymetry preprocessing
  - Similar pairs for: species richness, sample locations, fishnets, year/image name tables

- **Workers** perform the actual ArcGIS/ArcPy operations:
  - create_rasters_worker.py — Creates interpolated rasters per region
  - create_regions_from_shapefiles_worker.py — Converts shapefiles to GDB regions
  - And corresponding worker files for each director

- **Pattern Notes:**
  - All modules use raw f-strings with Windows paths (e.g., `rf"{project_folder}\Bathymetry\Bathymetry.gdb"`)
  - Consistent error handling: ArcPy exception catching + traceback + `sys.exit()`
  - Functions clear local variables at completion (`del var`) and warn about remaining keys
  - ArcGIS Pro logging is configured (history, metadata, message levels)

- ### Create Regions from Shapefiles Director and Worker
  - This director/worker pair converts survey region shapefiles into feature classes within the DisMAP geodatabase.

  - #### **Director (create_regions_from_shapefiles_director.py)**

    - **Purpose**: Orchestrates the creation of region boundaries and extent polygons from shapefiles for all IDW regions (AI, EBS, GOA, GMEX, SEUS, etc.).

    - **Key Functions:**

      1. **`create_dismap_regions(project_gdb)`** — Initializes the DisMAP_Regions polyline template feature class:
         - Creates empty `DisMAP_Regions` feature class in project GDB (spatial reference: WGS_1984_Web_Mercator_Auxiliary_Sphere)
         - Adds schema fields via `dismap_tools.add_fields()`
         - Imports metadata via `dismap_tools.import_metadata()`

      2. **`director(project_gdb, Sequential, table_names)`** — Main orchestration function:
         - **Pre-processing** (sequential):
           - Calls `create_dismap_regions()` to initialize template
           - For each region (e.g., "AI_IDW", "EBS_IDW"):
             - Creates region-specific GDB and scratch workspace (`{scratch_folder}\{table_name}.gdb`)
             - Copies `Datasets` table and `DisMAP_Regions` template to region GDB
             - Synchronizes metadata via `arcpy.metadata.Metadata`
         
         - **Sequential or parallel processing**:
           - **Sequential mode**: Calls `worker()` for each region sequentially
           - **Parallel mode**: Uses `multiprocessing.Pool` (processes = CPU count - 2) with `apply_async()` to spawn workers; monitors job completion with status polling every ~7.5×processes seconds; gracefully handles exceptions with pool termination
         
         - **Post-processing** (sequential):
           - Walks scratch folder for all generated feature classes (Polygon/Polyline)
           - Copies each result to project GDB
           - For `*_Boundary` feature classes, appends them to the master `DisMAP_Regions` feature class
           - Compacts project GDB

      3. **`script_tool(project_gdb)`** — Entry point (ArcGIS Pro tool parameter wrapper):
         - Supports test/dev toggles for processing specific regions (hardcoded table names or empty list)
         - Calls `director()` with default parallel processing (`Sequential=False`)
         - Logs timing and environment info

  - #### **Worker (create_regions_from_shapefiles_worker.py)**

    - **Purpose**: Processes a single region; converts a region's boundary shapefile to feature classes (Region polygon + Boundary polyline).

    - **Key Steps in `worker(region_gdb)`:**

      1. **Extract region metadata** — Queries `Datasets` table to fetch region info:
           - Fields: TableName, GeographicArea, DatasetCode, Region, Season, DistributionProjectCode
           - Example result: `['AI_IDW', 'AI_IDW_Region', 'AI', 'Aleutian Islands', None, 'IDW']`

      2. **Set spatial reference** — Loads `.prj` file from `Dataset_Shapefiles\{table_name}\{geographic_area}.prj`:
           - Adjusts cell size and XY tolerance based on linear unit (Kilometer → 1 cell size; Meter → 1000 cell size)

      3. **Create region feature class** — Creates POLYGON feature class:
           - Uses `DisMAP_Regions` template as schema source
           - Applies region-specific spatial reference

      4. **Append shapefile data** — Imports geometry and attributes from source shapefile:
           - `arcpy.management.Append()` copies features from `{geographic_area}.shp` into the new feature class

      5. **Calculate region fields** — Populates DatasetCode, Region, Season, DistributionProjectCode fields with values from Datasets table

      6. **Create boundary feature class** — Uses `FeatureToLine()` to extract boundary polylines from the region polygon; deletes auto-generated FID field

      7. **Alter field metadata** — Calls `dismap_tools.alter_fields()` to set field aliases and properties for both Region and Boundary feature classes

      8. **Synchronize metadata** — Copies metadata from source region feature class to boundary feature class via `arcpy.metadata.Metadata`

      9. **Cleanup** — Deletes template tables (`DisMAP_Regions`, `Datasets`), compacts region GDB

    - ##### **Key Architectural Patterns**

      - **Scalable parallelism**: Director spawns region workers in parallel pool; each worker processes independently with isolated GDB workspaces
      - **Metadata cascade**: Copies metadata templates between feature classes to maintain consistency
      - **Region isolation**: Each worker uses separate `.gdb` to avoid locking; director merges results post-processing
      - **Workspace cleanup**: Removes intermediate templates and compacts GDBs to minimize database size

    - ##### **Integration Points**

      - Depends on `Dataset_Shapefiles\{region}\{geographic_area}.shp/.prj` files
      - Reads region metadata from `Datasets` table (populated by `import_datasets_species_filter_csv_data.py`)
      - Outputs region boundaries appended to master `DisMAP_Regions` feature class
      - Boundary feature classes available for fishnet creation and region extent workflows downstream

  - ### Create Region Fishnets Director and Worker
    - This director/worker pair generates fishnet grids, extent points, and latitude/longitude rasters for each survey region.

    - #### **Director (create_region_fishnets_director.py)**

      - **Purpose**: Orchestrates fishnet generation for all IDW regions, supporting parallel processing with batch grouping for CPU efficiency.

      - **Key Functions:**

        1. **`director(project_gdb, Sequential, table_names)`** — Main orchestration function:
          - **Pre-processing** (sequential):
            - Validates that `Datasets` and `*_Region` feature classes exist and contain records
            - Creates region-specific GDB and scratch workspaces (`{scratch_folder}\{table_name}.gdb`)
            - Copies `Datasets` table and `{table_name}_Region` feature class to each region GDB
          
          - **Sequential or parallel processing**:
            - **Sequential mode**: Calls `worker()` sequentially for each region
            - **Parallel mode**: Uses `multiprocessing.Pool` (processes = CPU count - 2, maxtasksperchild=1); monitors job completion with status polling every ~7.5×processes seconds
          
          - **Post-processing** (sequential):
            - Walks scratch folder collecting all generated datasets (rasters, feature classes)
            - Copies each result to project GDB
            - Deletes source intermediate files from scratch workspace
            - Compacts each region GDB and the project GDB

        2. **`script_tool(project_gdb)`** — Entry point with hardcoded batch grouping:
          - Supports test/dev toggles with region subsets
          - **Production batches** (parallel): Processes regions in two parallel director calls:
            - Batch 1: `WC_TRI_IDW, GMEX_IDW, AI_IDW, GOA_IDW, WC_ANN_IDW`
            - Batch 2: `NEUS_SPR_IDW, EBS_IDW, NEUS_FAL_IDW, SEUS_SUM_IDW`
          - Logs timing and environment info

  - #### **Worker (create_region_fishnets_worker.py)**

    **Purpose**: For a single region, creates fishnet grid cells, extent points, and geographic coordinate rasters.

    **Key Outputs Generated:**

    1. **Raster Mask** (`{table_name}_Raster_Mask`):
       - Converts region boundary polygon to raster using cell size from Datasets table
       - Serves as template for coordinate rasters

    2. **Extent Points** (`{table_name}_Extent_Points`):
       - Creates 3 corner points (lower-left, upper-left, upper-right) of region boundary
       - Calculates both projected (Easting/Northing) and geographic (Longitude/Latitude) coordinates using `AddXY()` and field aliasing

    3. **Fishnet** (`{table_name}_Fishnet`):
       - Creates regular grid of POLYGON cells (cell size from Datasets table)
       - Overlays fishnet on region boundary and removes cells outside region using `SelectLayerByLocation()` with 2×cell_size buffer
       - Result: Only cells intersecting the region are retained

    4. **Lat-Long Centroids** (`{table_name}_Lat_Long`):
       - Extracts fishnet cell centroids as point feature class
       - Calculates both projected (Easting/Northing) and geographic (Longitude/Latitude) coordinates

    5. **Latitude Raster** (`{table_name}_Latitude`):
       - Converts Lat-Long point centroids to raster using "Latitude" field
       - Extracts values within raster mask using `ExtractByMask()`

    6. **Longitude Raster** (`{table_name}_Longitude`):
       - Converts Lat-Long point centroids to raster using "Longitude" field
       - Extracts values within raster mask using `ExtractByMask()`

    **Technical Details:**

    - **Coordinate system handling**: 
      - Uses `EnvManager` context managers to temporarily override output coordinate system
      - Converts from region's projected system (via `.prj` file) to WGS84 (EPSG:4326) for geographic coordinates
      - Uses `dismap_tools.check_transformation()` to get geographic transformation parameters

    - **Field renaming pattern**:
      - `POINT_X` → `Easting` (projected) or `Longitude` (geographic)
      - `POINT_Y` → `Northing` (projected) or `Latitude` (geographic)

    - **Metadata & cleanup**:
      - Calls `dismap_tools.alter_fields()` for field aliases
      - Calls `dismap_tools.import_metadata()` to attach standardized metadata
       - Synchronizes metadata via `arcpy.metadata.Metadata`
      - Deletes intermediate `Datasets` and `{table_name}_Region` templates
      - Compacts region GDB

    ##### **Key Architectural Patterns**

    - **Batch parallelism**: Director runs multiple fishnet directors in sequence but each director spawns workers in parallel pool
    - **Coordinate duality**: Each feature class maintains both projected (Easting/Northing) and geographic (Longitude/Latitude) coordinates
    - **Region masking**: Fishnet cells are intelligently filtered to align with region boundary
    - **Raster template**: Raster mask constrains all downstream latitude/longitude raster generation

    ##### **Integration Points**

    - Reads region geometry from `{table_name}_Region` feature class (from `create_regions_from_shapefiles_worker`)
    - Reads cell size and dataset metadata from `Datasets` table
    - Outputs fishnet cells, extent points, and coordinate rasters available for downstream IDW interpolation
    - Longitude/Latitude rasters used for geographic coordinate layers in map displays

- ### Create Region Bathymetry Director and Worker
  - This director/worker pair generates region-specific bathymetry rasters using zonal statistics over fishnet grids.

  - #### **Director (create_region_bathymetry_director.py)**
    
    - **Purpose**: Orchestrates bathymetry processing for all IDW regions, handling data staging and parallel worker coordination.

    - **Key Functions:**

      1. **`director(project_gdb, Sequential, table_names)`** — Main orchestration function:
        - **Pre-processing**:
          - Calls `preprocessing()` to stage fishnet, raster mask, and bathymetry data for each region into separate GDBs
          - Creates region-specific workspaces under Scratch folder
        
        - **Sequential or parallel processing**:
          - **Sequential mode**: Calls `worker()` sequentially for each region (currently commented/disabled)
          - **Parallel mode**: Uses `multiprocessing.Pool` (processes = CPU count - 2, maxtasksperchild=1) to execute workers in parallel; monitors job completion with status polling every ~7.5×processes seconds
        
        - **Post-processing** (sequential):
          - Walks scratch folder collecting all generated raster datasets
          - Copies each bathymetry raster to project GDB
          - Calls `dismap_tools.alter_fields()` for feature classes/tables/mosaics
          - Compacts project GDB

      2. **`script_tool(project_gdb)`** — Entry point with hardcoded batch grouping:
        - **Production batches** (parallel): Processes regions in three parallel director calls:
          - Batch 1: `NBS_IDW, ENBS_IDW, HI_IDW, SEUS_FAL_IDW, SEUS_SPR_IDW, SEUS_SUM_IDW`
          - Batch 2: `WC_TRI_IDW, GMEX_IDW, AI_IDW, GOA_IDW, WC_ANN_IDW, NEUS_FAL_IDW`
          - Batch 3: `NEUS_SPR_IDW, EBS_IDW`
        - Logs timing and environment info

  -  #### **Worker (create_region_bathymetry_worker.py)**

      This file contains three functions:

      #### **1. `preprocessing(project_gdb, table_names, clear_folder)`**
      Stages data for all regions into scratch workspace:
      - Clears scratch folder if `clear_folder=True`
      - For each region (e.g., `AI_IDW`), creates:
        - Region-specific GDB: `{scratch_folder}\{table_name}.gdb`
        - Region scratch workspace: `{scratch_folder}\{table_name}\scratch.gdb`
        - Copies `Datasets` table from project GDB
        - Copies `{table_name}_Fishnet` feature class from project GDB
        - Copies `{table_name}_Raster_Mask` raster from project GDB
        - Copies `{table_name}_Bathymetry` from `Bathymetry\Bathymetry.gdb` and renames to `{table_name}_Fishnet_Bathymetry`

      #### **2. `worker(region_gdb)`**
      Performs zonal statistics computation for a single region:

      **Inputs:**
      - `{table_name}_Fishnet` — Polygon feature class with fishnet grid cells (OID field)
      - `{table_name}_Raster_Mask` — Template raster defining cell size, extent, and spatial reference
      - `{table_name}_Fishnet_Bathymetry` — Bathymetry raster with depth values

      **Processing:**
      - Extracts cell size from raster mask metadata
      - Sets environment: cell size, extent, mask, snapRaster from raster template
      - Executes `arcpy.sa.ZonalStatistics()`:
        - **Zone data**: Fishnet grid (one value per cell)
        - **Zone field**: OID (unique cell identifier)
        - **Value raster**: Bathymetry (depth values)
        - **Statistics**: MEDIAN (median depth per cell)
        - **Ignore NoData**: DATA (include NoData pixels in calculation)
        - **Percentile**: 90th percentile (optional, for reference)

      **Output:**
      - `{table_name}_Bathymetry` — Raster with median depth value for each fishnet cell

      **Cleanup:**
      - Calls `dismap_tools.import_metadata()` to attach metadata
      - Deletes intermediate files: `Datasets`, `Raster_Mask`, `Fishnet`, `Fishnet_Bathymetry`
      - Compacts region GDB

      #### **3. `script_tool(project_gdb)`**
      Development entry point (currently runs single region test):
      - Calls `preprocessing()` to stage data
      - Calls `worker()` for test region (`HI_IDW`)
      - Used for single-region testing/debugging

      #### **Key Architectural Patterns**

      - **Two-stage processing**: Preprocessing stages all data in parallel-safe workspaces, then workers compute independently
      - **Raster template pattern**: Raster mask provides all spatial environment parameters (cell size, extent, SR) for consistency
      - **Zonal statistics optimization**: Uses median depth to provide representative bathymetry per fishnet cell
      - **Batch grouping**: Director distributes 15 regions across 3 parallel batches to balance load across CPU cores

      #### **Integration Points**

      - **Inputs**:
        - Fishnet grid from `create_region_fishnets_worker` outputs
        - Raster mask from `create_region_fishnets_worker` outputs
        - Bathymetry raster from `create_base_bathymetry.py` or bathymetry GDB
        
      - **Outputs**:
        - `{table_name}_Bathymetry` rasters available for downstream analysis and visualization
        - Rasters propagated to project GDB for inclusion in maps and services

      - **Data flow**:
        ```
        Bathymetry GDB → preprocessing() → region GDB → worker() → ZonalStatistics
        Fishnet ─────────────────────────→ region GDB → worker() → (zone field)
        Raster Mask ───────────────────────→ region GDB → worker() → (environment template)
        ```

      #### **Technical Details**

      - **Zonal Statistics parameters**:
        - Ignores NoData in value raster (DATA mode) so pixels with No Data still participate in zone calculations
        - Uses MEDIAN to handle outliers better than MEAN for depth measurements
        - Produces one output value per zone (fishnet cell) linked by OID

      - **Environment management**:
        - Uses `EnvManager` context manager for scratch workspace isolation
        - Cell size derived from raster metadata: `arcpy.Describe(raster/Band_1).meanCellWidth`
        - Linear unit handling: Kilometer → cell size 1 km; Meter → cell size 1000 m

- ### Create Region Sample Locations Director and Worker
  - This director/worker pair creates sample location point feature classes from survey data CSVs, converting raw data into spatial datasets with standardized fields and metadata.

  - ### **Director (create_region_sample_locations_director.py)**

    - **Purpose**: Orchestrates sample location processing for all IDW regions, handling data staging and parallel worker coordination.

    - **Key Functions:**

      1. **`director(project_gdb, Sequential, table_names)`** — Main orchestration function:
         - **Pre-processing** (sequential):
           - Clears scratch folder
           - Creates region-specific GDBs under Scratch folder
           - Copies `Datasets` table and `{table_name}_Region` feature class to each region GDB
         
         - **Sequential or parallel processing**:
           - **Sequential mode**: Calls `worker()` sequentially for each region
           - **Parallel mode**: Uses `multiprocessing.Pool` (processes = CPU count - 2, maxtasksperchild=1); monitors job completion with status polling every ~7.5×processes seconds
         
         - **Post-processing** (sequential):
           - Walks scratch folder collecting all generated tables and feature classes
           - Copies each result to project GDB
           - Compacts project GDB

      2. **`script_tool(project_gdb)`** — Entry point with test mode:
         - Default test mode: Single region (`GMEX_IDW`)
         - Can run all 15 IDW regions in non-sequential mode
         - Logs timing and environment info

   - ### **Worker (create_region_sample_locations_worker.py)**

      - **Purpose**: For a single region, imports survey CSV data, transforms and enriches fields, converts to GDB table, then exports as point feature class with spatial reference.

      - **Processing Pipeline (3 Major Phases):**

        #### **Phase 1: CSV Loading & Field Extraction**

        - Detects CSV encoding using `dismap_tools.get_encoding_index_col()` (chardet-based)
        - Loads CSV with pandas using schema-based data types from `dismap_tools.dTypesCSV()`
        - Queries `Datasets` table to extract region metadata:
          - TableName, GeographicArea, DatasetCode, Region, Season, DistributionProjectCode
          
        - **Column renaming** (22 aliases handled):
          - `spp` / `spp_sci` → `Species`
          - `common` / `spp_common` → `CommonName`
          - `lon` / `Longitude`; `lat` / `Latitude`
          - `lon_UTM` / `Easting`; `lat_UTM` / `Northing`
          - `haulid` / `sampleid` → `SampleID`
          - `wtcpue` → `WTCPUE`
          - `median_est` / `mean_est` → `MedianEstimate` / `MeanEstimate`
          - `est5` / `est95` → `Estimate5` / `Estimate95`
          - `year` → `Year`; `depth_m` → `Depth`
          - `stratum` → `Stratum`; `transformed` → `MapValue`

        #### **Phase 2: DataFrame Transformation & Enrichment**

           **Insert new columns with derived/default values:**

          - `DatasetCode`: From Datasets table
          - `Region`: From Datasets table (or default if None)
          - `Season`: From Datasets table (or empty string if None)
          - `StdTime`: Calculated from Year (pd.to_datetime with GMT+12 timezone)
          - `MapValue`: Cube root transformation of WTCPUE (`WTCPUE ^ (1/3)`)
          - `SpeciesCommonName`: Format `"Species (CommonName)"` where CommonName exists
          - `CommonNameSpecies`: Format `"CommonName (Species)"` where CommonName exists
          - `SummaryProduct`: Set to "Yes"
          - `TransformUnit`: Set to "cuberoot" (documents MapValue transformation)
          - `CoreSpecies`: Set to "No" (default; could be calculated later)

           **Handle null/missing values:**

          - Replace `NaN` with empty string for string fields (CommonName, DistributionProjectName)
          - Replace `Inf` and `-Inf` with `NaN` in numeric fields (WTCPUE, coordinates, depth)
          - Fill numeric nulls appropriately for Latitude, Longitude, Depth, WTCPUE

        - **Reorder columns** using `dismap_tools.table_definitions()` to match schema order

        #### **Phase 3: GDB Table Creation & Feature Conversion**
          - Convert enriched DataFrame to NumPy structured array using GDB field types (`dismap_tools.dTypesGDB()`)
          - Create temporary GDB table via `arcpy.da.NumPyArrayToTable()`
          - Copy rows to output table: `{table_name}` (permanent table in region GDB)
          - Delete temporary table

          **Convert Table to Feature Class:**

          - Create XY Event Layer from output table using:
            - X field: `Longitude` (geographic coordinates, WGS84)
            - Y field: `Latitude` (geographic coordinates, WGS84)
            - Spatial reference: WGS84 (EPSG:4326)
            - Geographic transformation: Auto-determined via `dismap_tools.get_transformation()`
            
          - Export XY Event Layer to feature class: `{table_name}_Sample_Locations`
          - Add attribute index on: Species, CommonName, SpeciesCommonName, Year
          - Delete temporary XY Event Layer

          **Metadata & Field Aliasing:**

          - Copy metadata from CSV to output table via `arcpy.metadata.Metadata`
          - Call `dismap_tools.alter_fields()` to set field aliases and properties for both table and feature class
          - Synchronize metadata for both

          **Cleanup:**

          - Delete intermediate datasets: `{table_name}_Boundary`, `{table_name}_Region`, `Datasets`
          - Compact region GDB

    - #### **Key Data Transformations**
         1. **MapValue (WTCPUE Cube Root)**: Normalizes highly skewed WTCPUE distribution for visualization
         2. **SpeciesCommonName/CommonNameSpecies**: Dual naming conventions for UI display flexibility
         3. **StdTime**: Creates ISO 8601 timestamp for temporal queries
         4. **Field Reordering**: Enforces consistent column order matching GDB schema

    - #### **Integration Points**

      - **Inputs**:
        - Survey CSV files from `{project_folder}\CSV_Data\{table_name}.csv`
        - Region geometry from `{table_name}_Region` (from `create_regions_from_shapefiles_worker`)
        - Schema definitions from `field_definitions.json` and `table_definitions.json`
        - Datasets metadata table (populated by `import_datasets_species_filter_csv_data.py`)

      - **Outputs**:
        - `{table_name}` — GDB table with all survey records and enriched fields
        - `{table_name}_Sample_Locations` — Point feature class in WGS84 (for web/portal publishing)
        - Spatial index on (Species, CommonName, Year) for fast queries

      - **Data flow**:
        ```
        CSV File → pandas DataFrame (with encoding detection)
                → Column rename & enrichment (22+ derived fields)
                → NumPy array conversion (type casting)
                → GDB table creation
                → XY Event Layer (geographic coordinates)
                → Point Feature Class (WGS84)
        ```

    -  #### **Technical Details**

      - **Encoding detection**: chardet-based; handles non-ASCII characters in CommonName fields
      - **Data type schema**: Schema-driven via JSON; ensures type safety across CSV→DataFrame→NumPy→GDB pipeline
      - **Coordinate systems**:
        - CSV source: Latitude/Longitude (WGS84) and Easting/Northing (projected, region-specific)
        - Output table: Both coordinate systems preserved
        - Output feature class: WGS84 only (for portal interoperability)
      - **Transformation chain**: WTCPUE → MapValue (cube root) documented via TransformUnit field for traceability
      - **Pandas optimizations**: Set display options for logging; use `inplace=False` operations for clarity; delete DataFrame after NumPy conversion to free memory

- ### Create Species Year Image Name Table Director and Worker
  - This director/worker pair generates a catalog table mapping species/year combinations to image names, which coordinates what rasters should be created during downstream workflows (IDW, richness, mosaics).

  - #### **Director (create_species_year_image_name_table_director.py)**

    - **Purpose**: Orchestrates the creation of `LayerSpeciesYearImageName` metadata tables for all IDW regions, which serve as operational catalogs for subsequent raster generation workflows.

    **Key Functions:**

    1. **`director(project_gdb, Sequential, table_names)`** — Main orchestration function:
      - **Pre-processing** (sequential):
        - Calls `preprocessing()` to stage sample location data and species filter tables for each region
        - Creates region-specific GDBs under Scratch folder
      
      - **Sequential or parallel processing**:
        - **Sequential mode**: Calls `worker()` sequentially for each region
        - **Parallel mode**: Uses `multiprocessing.Pool` (processes = CPU count - 2, maxtasksperchild=1); monitors job completion with status polling every ~7.5×processes seconds
      
      - **Post-processing** (sequential):
        - Walks scratch folder collecting all generated `*_LayerSpeciesYearImageName` tables
        - Copies each table to project GDB
        - Replaces None values with empty strings in string fields
        - Compacts project GDB

    2. **`script_tool(project_gdb)`** — Entry point with hardcoded batch grouping:
      - **Production batches** (parallel):
        - Batch 1: `GMEX_IDW, HI_IDW, WC_ANN_IDW, WC_TRI_IDW` (4 regions, test mode)
        - Batch 2: `AI_IDW, EBS_IDW, ENBS_IDW, GOA_IDW, NBS_IDW` (5 regions, commented)
        - Batch 3: `HI_IDW, WC_ANN_IDW, WC_TRI_IDW` (3 regions, commented)
        - Batch 4: `GMEX_IDW, NEUS_FAL_IDW, NEUS_SPR_IDW` (3 regions, commented)
        - Batch 5: `NEUS_FAL_IDW, NEUS_SPR_IDW, SEUS_FAL_IDW, SEUS_SPR_IDW, SEUS_SUM_IDW` (5 regions, active)
      - Logs timing and environment info

  - #### **Worker (create_species_year_image_name_table_worker.py)**
    - **Purpose**: For a single region, generates a `LayerSpeciesYearImageName` table that catalogs all species/year combinations and assigns standardized image names for raster outputs.

    - **Processing Pipeline (Multi-Stage):**

    #### **Phase 1: Create Base LayerSpeciesYearImageName Table**

    - Creates new empty table: `{table_name}_LayerSpeciesYearImageName`
    - Calls `dismap_tools.add_fields()` to populate schema (200+ fields from `field_definitions.json`)
    - Calls `dismap_tools.import_metadata()` to attach metadata templates

    #### **Phase 2: Load Reference Data**

    **a) Datasets Table:**
    - Queries `Datasets` table for region metadata
    - Extracts: FilterRegion, FilterSubRegion
    - Example: `['Aleutian Islands', 'Alaska']`

    **b) Region IDW Table:**
    - The main sample location table: `{table_name}` (e.g., `AI_IDW`)
    - Contains all survey records with Species, Year, CommonName, etc.
    - Logs unique species count

    **c) Species Filter Table:**
    - Filters to: `FilterSubRegion = '{filter_subregion}' AND DistributionProjectName = 'NMFS/Rutgers IDW Interpolation'`
    - Builds species_filter dict: `{species: [CommonName, TaxonomicGroup, FilterRegion, FilterSubRegion, ManagementBody, ManagementPlan, DistributionProjectName]}`
    - Example entry: `'Anoplopoma fimbria': ['Sablefish', 'Perciformes/Cottoidei (sculpins)', 'Alaska', 'Aleutian Islands', 'NPFMC', '...', 'NMFS/Rutgers IDW Interpolation']`

    #### **Phase 3: Generate Base Species/Year Records**

    **Statistical Aggregation:**
    - Uses `arcpy.analysis.Statistics()` to get unique species/year combinations from sample locations
    - Case fields: Filters to fields that appear in both LayerSpeciesYearImageName schema and region IDW table
    - Removes COUNT/FREQUENCY fields to create unique species/year records
    - Result: `{table_name}_tmp` temporary table with one row per species/year combination

    **Field Addition:**
    - Adds 5 new fields to `{table_name}_tmp`:
      - FilterRegion, FilterSubRegion, TaxonomicGroup, ManagementBody, ManagementPlan, DistributionProjectName
      - Variable, Value, Dimensions, ImageName

    **Row Population with Update Cursor:**

    For each species/year combination:
    - **Variable**: Species name (parentheses/periods removed) → e.g., `"Anoplopoma fimbria"` becomes `"Anoplopoma_fimbria"`
    - **Value**: Set to `"Species"` (literal)
    - **Dimensions**: Set to `"StdTime"` (standard time dimension)
    - **ImageName**: Formatted as `{table_name}_{variable}_{year}` → e.g., `AI_IDW_Anoplopoma_fimbria_2020`
    - **FilterRegion/FilterSubRegion**: Looked up from species_filter dict if species found, else empty string
    - **TaxonomicGroup/ManagementBody/ManagementPlan/DistributionProjectName**: Looked up from species_filter dict

    **Append to Output Table:**
    - Appends populated records to `layer_species_year_image_name` table

    #### **Phase 4: Generate Species Richness Records (Core)**

    **Statistical Aggregation for Core Species:**
    - Applies second `arcpy.analysis.Statistics()` to group by non-species fields
    - Creates `{table_name}_tmp_stats` with unique region/season/dataset records
    - Adds Variable, Value, Dimensions, ImageName fields

    **Row Population - Core Species Richness:**

    For each region/season combination (only where core species exist):
    - **Variable**: `"Core Species Richness"`
    - **Value**: `"Core Species Richness"`
    - **Dimensions**: `"StdTime"`
    - **ImageName**: `{table_name}_Core_Species_Richness_{year}`
    - **CoreSpecies**: Set to `"Yes"` (signals core richness raster)
    - **FilterRegion/FilterSubRegion**: From region metadata

    **Append Core Records to Output Table**

    #### **Phase 5: Generate Species Richness Records (Total)**

    **Row Population - Total Species Richness:**

    For each region/season combination (all species):
    - **Variable**: `"Species Richness"` (differs from core)
    - **Value**: `"Species Richness"`
    - **Dimensions**: `"StdTime"`
    - **ImageName**: `{table_name}_Species_Richness_{year}`
    - **CoreSpecies**: Set to `"No"` (signals all-species richness raster)

    **Append Total Records to Output Table**

    #### **Phase 6: Finalization**

    - Calls `dismap_tools.alter_fields()` to set field aliases and properties
    - Sets metadata on `layer_species_year_image_name`: synchronizes ArcGIS metadata
    - Deletes intermediate tables: `{table_name}_tmp`, `{table_name}_tmp_stats`, and optionally temporary dataset tables
    - Compacts region GDB

    ### **Output Table Structure**

    `{table_name}_LayerSpeciesYearImageName` contains records with fields:

    | Field Name | Purpose | Example |
    |---|---|---|
    | DatasetCode | Region code | `AI` |
    | Region | Region name | `Aleutian Islands` |
    | Species | Scientific species name | `Anoplopoma fimbria` |
    | CommonName | Common species name | `Sablefish` |
    | SpeciesCommonName | Formatted combo | `Anoplopoma fimbria (Sablefish)` |
    | Year | Survey year | `2020` |
    | StdTime | Standard time (derived) | (calculated) |
    | Variable | Raster type | `Anoplopoma_fimbria` or `Species Richness` |
    | Value | Raster value description | `Species` or `Species Richness` |
    | Dimensions | Analysis dimension | `StdTime` |
    | ImageName | Output raster name | `AI_IDW_Anoplopoma_fimbria_2020` or `AI_IDW_Species_Richness_2020` |
    | CoreSpecies | Flag for richness rasters | `Yes` (core) / `No` (total) / blank (species) |
    | FilterRegion/FilterSubRegion | Geographic filters | From species_filter lookup |
    | TaxonomicGroup | Taxonomic class | From species_filter lookup |
    | ManagementBody | Fishery management org | From species_filter lookup |
    | ManagementPlan | Management plan reference | From species_filter lookup |
    | DistributionProjectName | Distribution project | `NMFS/Rutgers IDW Interpolation` |

    #### **Key Data Operations**

    1. **Statistical Deduplication:**
      - Uses `arcpy.analysis.Statistics()` twice:
        - First: Identify unique species/year combinations from sample locations
        - Second: Identify unique region/season combinations for richness catalogs

    2. **Multi-Stage Table Generation:**
      - Three types of rows generated in sequence:
        1. Species-specific rasters (one per species/year)
        2. Core species richness rasters (aggregate)
        3. Total species richness rasters (aggregate)

    3. **Dictionary Lookup for Metadata:**
      - Species filter dict enables efficient lookups during cursor operations
      - Prevents repeated database queries (performance optimization)

    4. **Name Standardization:**
      - Removes special characters (parentheses, periods) from species names for file naming
      - Creates consistent `ImageName` format: `{region}_{variable}_{year}`

    #### **Integration Points**

    - **Inputs**:
      - `{table_name}` (sample locations table from `create_region_sample_locations_worker`)
      - `Species_Filter` table (metadata table with species/management mappings)
      - `Datasets` table (region metadata: FilterRegion, FilterSubRegion)

    - **Outputs**:
      - `{table_name}_LayerSpeciesYearImageName` table — Catalog of all rasters to generate
      - Contains 3 record types: species-specific (many), core richness (few), total richness (few)

    - **Data flow**:
      ```
      Sample Locations (Species/Year data)
              → Statistics → unique combinations
              ↓
      Species Filter (Taxonomy/Management)
              ↓
      Update Cursor (populate Variable/ImageName/Metadata)
              ↓
      LayerSpeciesYearImageName Table (operational catalog)
      
      Used downstream by:
      - create_rasters_worker.py (species rasters per ImageName)
      - create_species_richness_rasters_worker.py (richness rasters per ImageName)
      - create_mosaics_worker.py (mosaic generation)
      ```

    #### **Technical Architecture**

    - **Deduplication Strategy**: Uses ArcGIS `Statistics` tool rather than manual cursor loops for efficient unique-value extraction
    - **Temporary Tables**: Uses `_tmp` suffix for intermediate working tables; cleaned up post-processing
    - **Cursor Operations**: Three separate update cursor passes to populate different record types (species, core richness, total richness)
    - **Metadata Lookup**: Builds in-memory dict from Species_Filter to avoid repeated database queries
    - **Name Formatting**: Removes special characters from species names to ensure valid raster filenames
    - **Batch Parallelism**: Director processes multiple regions in parallel batches; each worker independently generates catalog

- ### Create Rasters Director and Worker
  - This director/worker pair creates interpolated rasters from sample location data using Inverse Distance Weighting (IDW) geostatistical analysis.

  - #### **Director (create_rasters_director.py)**

    - **Purpose**: Orchestrates raster creation for all IDW regions, generating spatially-interpolated surfaces from survey data with parallel processing support.

    - **Key Functions:**

      1. **`director(project_gdb, Sequential, table_names)`** — Main orchestration function:
           - **Pre-processing** (sequential):
             - Calls `preprocessing()` to stage sample location data for each region into separate GDBs
             - Creates region-specific workspaces under Scratch folder
           
           - **Sequential or parallel processing**:
             - **Sequential mode**: Calls `worker()` sequentially for each region
             - **Parallel mode**: Uses `multiprocessing.Pool` (processes = CPU count - 2, maxtasksperchild=1); monitors job completion with status polling every ~7.5×processes seconds
           
           - **Post-processing** (sequential):
             - Compacts project GDB only (no explicit raster copying—results already in region GDBs)

      2. **`script_tool(project_gdb)`** — Entry point with hardcoded batch grouping:
           - **Production batches** (parallel):
             - Batch 1: `AI_IDW` (single region, default test)
             - Batch 2: `EBS_IDW, ENBS_IDW, GMEX_IDW, GOA_IDW, NBS_IDW` (5 regions)
             - Batch 3: `HI_IDW` (single region)
             - Batch 4: `WC_ANN_IDW, WC_TRI_IDW` (2 regions)
             - Batch 5: `SEUS_FAL_IDW, SEUS_SPR_IDW, SEUS_SUM_IDW` (3 regions)
             - Batch 6: `NEUS_FAL_IDW, NEUS_SPR_IDW` (2 regions, currently active in code)
           - Logs timing and environment info

  - #### **Worker (create_rasters_worker.py)**
    - **Purpose**: For a single region, generates IDW interpolated rasters for each species/year combination using survey sample locations.

    - **Processing Pipeline:**

      - #### **Phase 1: Data Staging (`preprocessing()` function)**

        Pre-processes data for all regions into isolated region GDBs:

        - Clears scratch folder if `clear_folder=True`
        - For each region (e.g., `AI_IDW`), creates:
          - Region-specific GDB: `{scratch_folder}\{table_name}.gdb`
          - Region scratch workspace: `{scratch_folder}\{table_name}\scratch.gdb`
          
        - Copies data to region GDB:
          - `Datasets` table (metadata for region parameters: cell size, geographic area)
          - `{table_name}_LayerSpeciesYearImageName` table (catalog of rasters to generate)
          - `{table_name}_Sample_Locations` feature class (survey data points filtered for IDW species distribution)
          - `{table_name}_Raster_Mask` raster (spatial template: extent, cell size, coordinate system)

        - Extracts FilterRegion and FilterSubRegion values for later reference

      - #### **Phase 2: Raster Generation (`worker()` function)**

        For each species/year combination, executes multi-step IDW interpolation:

        **1. Prepare Output Raster Catalog:**
        - Queries `{table_name}_LayerSpeciesYearImageName` table for all rasters to generate
        - Extracts 4 fields: ImageName, Variable, Species, Year
        - Filters to exclude "Species Richness" rasters (handled by separate workflow)
        - Builds output_rasters dict: `{image_name: [image_name, variable, species, year, output_raster_path]}`
        - Creates folder structure: `{project_folder}\Images\{table_name}\{variable}\{image_name}.tif`

        **2. Prepare Sample Location Feature Layer:**
        - Creates feature layer from `{table_name}_Sample_Locations` for attribute selection
        - Filters for `DistributionProjectName = 'NMFS/Rutgers IDW Interpolation'` (IDW-compatible data)
        - If `SummaryProduct == "Yes"`: Adds `YearWeights` field (short integer, alias "Year Weights")

        **3. For Each Raster to Generate:**

          **a) Select Species and Year Data:**
            - Clears previous selection
            - Selects sample points where `Species = '{species}' AND Year = {year}`
            - Logs count of selected records

          **b) Set IDW Search Neighborhood:**
          - Extracts cell size from region metadata
          - Calculates search ellipse:
            - Major axis: `cell_size × 1000` (converts kilometers to meters)
            - Minor axis: `cell_size × 1000`
            - Angle: 0 (no rotation)
            - Max neighbors: 15
            - Min neighbors: 10
            - Sector type: ONE_SECTOR
          - Uses `arcpy.SearchNeighborhoodStandard()` for neighbor selection

          **c) Weight Years for Temporal Smoothing:**
          - Selects weighted years: `Year >= (year-2) AND Year <= (year+2)` (±2 years from target year)
          - Calculates YearWeights using: `YearWeights = 3 - abs(year_target - year_sample)`
            - Target year: weight = 3
            - ±1 year: weight = 2
            - ±2 years: weight = 1
          - Logs count of weighted records

          **d) Execute IDW Interpolation:**
          - Checks out GeoStats extension: `arcpy.CheckOutExtension("GeoStats")`
          - Sets environment parameters:
            - Extent, mask, snapRaster from `region_raster_mask` (spatial alignment)
            - Cell size from region metadata
            - Output coordinate system from raster mask
          - Calls `arcpy.ga.IDW()` with parameters:
            - Input features: `sample_locations_path_layer` (selected points)
            - Z field: `MapValue` (cube-root transformed WTCPUE from sample locations)
            - Output raster: `memory\{output_raster}` (temporary in-memory raster)
            - Cell size: region-specific
            - Power: 2 (standard IDW power for distance weighting)
            - Search neighborhood: calculated ellipse with temporal weights
            - Weight field: `YearWeights` (applies temporal smoothing)

          **e) Reverse MapValue Transformation:**
          - Executes `arcpy.sa.Power(tmp_raster, 3)` to cube the interpolated values
          - Reverses the cube-root transformation: `MapValue^3 = WTCPUE`
          - Saves power-transformed raster to output TIF file path

          **f) Build Pyramids:**
          - Constructs pyramid levels (-1 = all levels)
          - Resampling: BILINEAR
          - Compression: DEFAULT with 75% quality
          - Skip existing: OVERWRITE

        **4. Metadata & Cleanup:**
        - Sets raster metadata title: image_name with underscores replaced by spaces
        - Synchronizes metadata: `tif_md.synchronize("ALWAYS")`
        - Deletes intermediate in-memory raster
        - Resets YearWeights field to None
        - Clears feature layer selection

        **5. Final Cleanup:**
        - Deletes sample location feature layer
        - Deletes intermediate datasets: `Datasets`, `Raster_Mask`, `LayerSpeciesYearImageName`
        - Compacts region GDB

     - #### **Key Data Transformations**

      1. **MapValue → WTCPUE (Cube Root Reversal):**
        - Input rasters: Cube-root transformed WTCPUE (MapValue) from sample locations
        - IDW interpolates across landscape: `MapValue = WTCPUE^(1/3)`
        - Output: `interpolated_MapValue^3 = WTCPUE` (restores original units)
        - Justification: Cube root normalizes highly skewed WTCPUE distribution for interpolation

      2. **Temporal Weighting:**
        - For target year Y: selects sample data from years Y-2 to Y+2
        - Weight formula: `3 - |Y_target - Y_sample|`
        - Effect: Center year has 3× influence; ±2 years have 1× influence
        - Reduces temporal noise while maintaining year-specific estimates

      3. **Search Neighborhood:**
        - Ellipse major/minor axes = `cell_size × 1000` meters
        - Ensures interpolation uses local sample points (not global)
        - Min/Max neighbors: 10–15 points per cell (balance: detail vs. stability)

     - #### **Integration Points**

      - **Inputs**:
        - `{table_name}_Sample_Locations` feature class (from `create_region_sample_locations_worker`)
        - `{table_name}_Raster_Mask` raster (from `create_region_fishnets_worker`)
        - `{table_name}_LayerSpeciesYearImageName` table (mapping of species/year to raster outputs)
        - `Datasets` table (region cell size, metadata)
        - MapValue field (cube-root WTCPUE from sample enrichment)

      - **Outputs**:
        - Raster TIFs saved to: `{project_folder}\Images\{table_name}\{variable}\{image_name}.tif`
        - One interpolated surface per species/year/region combination
        - Rasters include pyramids and spatial reference from region mask

      - **Data flow**:
        ```
        Sample Locations (points with MapValue)
                → Feature selection by species/year
                → IDW interpolation (with YearWeights neighbor weighting)
                → Power transform (cube back to WTCPUE)
                → TIF output with pyramids
        ```

     - #### **Technical Details**

        - **Geostatistical Analyst Requirements**: Raster creation depends on ArcGIS GeoStats extension checkout/check-in
        - **Memory Management**: Uses in-memory raster (`memory\{name}`) for temporary IDW output before power transform and final TIF save
        - **Raster Masking**: Extent, mask, and snapRaster from `region_raster_mask` ensure outputs conform to fishnet grid alignment
        - **Year Weights Implementation**: CalculateField expressions: `3 - (abs({year} - !Year!))` dynamically applied to selected records
        - **Coordinate System**: Output rasters inherit spatial reference from `region_raster_mask` (region-specific projection)
        - **Parallel Batching**: Director splits 15 IDW regions into 6 sequential batches (sizes 1–5 regions) to manage CPU load across multiple `director()` calls

- ### Create Species Richness Rasters Director and Worker

This director/worker pair generates species richness rasters by counting the presence/absence of species across interpolated surfaces for each year and region.

### **Director (create_species_richness_rasters_director.py)**

**Purpose**: Orchestrates species richness raster generation for all IDW regions, aggregating species count rasters from existing interpolated species distributions.

**Key Functions:**

1. **`director(project_gdb, Sequential, table_names)`** — Main orchestration function:
   - **Pre-processing** (sequential):
     - Calls `preprocessing()` to stage required data for each region into separate GDBs
     - Creates region-specific workspaces under Scratch folder
   
   - **Sequential or parallel processing**:
     - **Sequential mode**: Calls `worker()` sequentially for each region
     - **Parallel mode**: Uses `multiprocessing.Pool` (processes = CPU count - 2, maxtasksperchild=1); monitors job completion with status polling every ~7.5×processes seconds
   
   - **Post-processing** (sequential):
     - Compacts project GDB

2. **`script_tool(project_gdb)`** — Entry point with hardcoded batch grouping:
   - **Production batches** (parallel):
     - Batch 1: `AI_IDW, EBS_IDW, GOA_IDW` (3 regions, currently in test mode)
     - Batch 2: `ENBS_IDW, GOA_IDW, NBS_IDW` (3 regions, alt batch)
     - Batch 3: `SEUS_FAL_IDW, SEUS_SPR_IDW, SEUS_SUM_IDW` (3 regions)
     - Batch 4: `HI_IDW, WC_ANN_IDW, WC_TRI_IDW` (3 regions)
     - Batch 5: `GMEX_IDW, NEUS_FAL_IDW, NEUS_SPR_IDW` (3 regions)
   - Currently in test mode with single region: `SEUS_FAL_IDW`
   - Logs timing and environment info

### **Worker (create_species_richness_rasters_worker.py)**

**Purpose**: For a single region, generates species richness rasters (total and core species) by counting presence/absence across all interpolated species distributions for each year.

**Processing Pipeline:**

#### **Phase 1: Data Staging (`preprocessing()` function)**

Pre-processes data for all regions into isolated region GDBs:

- Clears scratch folder if `clear_folder=True`
- For each region (e.g., `AI_IDW`), creates:
  - Region-specific GDB: `{scratch_folder}\{table_name}.gdb`
  - Region scratch workspace: `{scratch_folder}\{table_name}\scratch.gdb`
  
- Copies data to region GDB:
  - `Datasets` table (metadata for region parameters: cell size, DatasetCode)
  - `{table_name}_LayerSpeciesYearImageName` table (catalog of rasters; contains metadata about which species/years have interpolated surfaces)
  - `{table_name}_Raster_Mask` raster (spatial template: extent, cell size, coordinate system)

- Creates these tables by:
  - Filtering Datasets to matching region
  - Copying LayerSpeciesYearImageName table
  - Copying Raster_Mask raster

#### **Phase 2: Richness Raster Generation (`worker()` function)**

For each year, generates two types of species richness rasters:

**1. Prepare Raster Catalog:**
- Queries `{table_name}_LayerSpeciesYearImageName` table for all interpolated surfaces
- Extracts 5 fields: DatasetCode, CoreSpecies, Year, Variable, ImageName
- Filters for: `Variable NOT IN ('Core Species Richness', 'Species Richness')` (excludes pre-computed richness layers)
- Further filters: `DatasetCode = '{datasetcode}'` (single dataset per region)
- Builds `input_rasters` dict: `{image_name.tif: [variable, corespecies, year, path_to_tif]}`
- Result: Catalog of all species/year raster TIF files available

**2. Prepare Output Paths:**
- Total richness path: `{project_folder}\Images\{table_name}\_Species Richness\{table_name}_Species_Richness_{year}.tif`
- Core richness path: `{project_folder}\Images\{table_name}\_Core Species Richness\{table_name}_Core_Species_Richness_{year}.tif`
- Scratch paths for temporary working space
- Creates directories if they don't exist

**3. Extract Raster Dimensions and Extent:**
- Gets row count and column count from `{table_name}_Raster_Mask` using `GetRasterProperties()`
- Extracts lower-left corner point from mask extent (used as spatial reference for output raster)
- Used to create zero-initialized NumPy arrays

**4. Generate Total Species Richness Rasters:**

For each unique year in the input rasters:

   **a) Initialize richness array:**
   - Creates zero-filled NumPy array: `shape=(rowCount, columnCount), dtype='float32'`
   - Will accumulate presence counts per raster cell

   **b) Process all species for the year:**
   - Filters input_rasters to only records where `Year == {target_year}`
   - For each species/year combination:
     - Loads raster as NumPy array: `arcpy.RasterToNumPyArray(_in_raster, nodata_to_value=np.nan)`
     - Replaces negative values with NaN (removes invalid data)
     - Converts positive values (>0.0) to 1.0 (binary presence indicator)
     - Adds species binary array to accumulating richness array: `richnessArray += rasterArray`

   **c) Convert array to raster:**
   - Casts array as float32 for consistency
   - Converts NumPy array to raster using `arcpy.NumPyArrayToRaster()` with:
     - Lower-left corner point (spatial reference)
     - Cell size (from region metadata)
     - NoData value: -3.40282346639e+38 (minimum float32)
   - Saves raster to TIF file path
   - Calculates statistics: `arcpy.management.CalculateStatistics()`

   **d) Set metadata:**
   - Sets raster title: image filename with underscores replaced by spaces
   - Synchronizes metadata: `raster_md.synchronize("ALWAYS")`

**5. Generate Core Species Richness Rasters:**

Similar process as total richness, but filters to only core species (`CoreSpecies == "Yes"`):

   - Extracts unique years where core species data exists
   - For each core-species year:
     - Filters input_rasters to `Year == {year} AND CoreSpecies == "Yes"`
     - Accumulates presence/absence binary counts per cell
     - Saves to core richness output path
     - Sets metadata

**Output Result:**

For each region and year:
- `{table_name}_Species_Richness_{year}.tif` — Count of all species present in each fishnet cell
- `{table_name}_Core_Species_Richness_{year}.tif` — Count of core species only

**Technical Details:**

- **NumPy Operations**: Uses NumPy array operations for efficient raster counting (all species processed in-memory)
- **Binary Conversion**: All input rasters (interpolated surfaces with WTCPUE values) converted to 1.0 (presence) or NaN (absence/nodata)
- **Accumulation**: `np.add(richnessArray, rasterArray)` counts species presence per cell
- **Output Type**: float32 for compatibility with ArcGIS raster formats
- **NoData Handling**: NoData pixels from input treated as NaN (not counted toward richness)
- **Coordinate System**: Output rasters inherit spatial reference from `region_raster_mask`

#### **Phase 3: Cleanup**

- Deletes intermediate datasets: `Datasets`, `LayerSpeciesYearImageName`, `Raster_Mask`
- Compacts region GDB
- Logs completion message

### **Key Data Transformations**

1. **Interpolated Surface → Binary Presence:**
   - Input: WTCPUE values (cube-root transformed from IDW rasters)
   - Conversion: Any value > 0.0 becomes 1.0; negative/NaN values remain NaN
   - Effect: Creates presence/absence indicator for each species

2. **Raster Accumulation:**
   - Sum across all species rasters for a given year
   - Result: Each fishnet cell contains count of species observed (0 to N species)
   - Semantics: Higher values = greater species diversity

3. **Core Species Filtering:**
   - Subset of species marked with `CoreSpecies = "Yes"` in metadata
   - Richness rasters generated separately: total vs. core
   - Enables comparison: all species diversity vs. managed/target species diversity

### **Integration Points**

- **Inputs**:
  - Interpolated species rasters from `create_rasters_worker` outputs (saved to `{project_folder}\Images\{table_name}\{variable}\{image_name}.tif`)
  - `{table_name}_LayerSpeciesYearImageName` table (maps species/year to raster files; from data catalog)
  - `{table_name}_Raster_Mask` raster (spatial template)
  - `Datasets` table (region metadata: DatasetCode, CellSize)

- **Outputs**:
  - `_Species Richness\{table_name}_Species_Richness_{year}.tif` — Total richness rasters
  - `_Core Species Richness\{table_name}_Core_Species_Richness_{year}.tif` — Core richness rasters
  - Rasters saved to: `{project_folder}\Images\{table_name}\`
  - One raster per year per richness type per region

- **Data flow**:
  ```
  Interpolated Species Rasters (TIF files)
           → Binary presence/absence conversion (NumPy)
           → Accumulation per cell across species (NumPy.add)
           → NumPy array → Raster conversion
           → Richness TIF output with statistics & metadata
  ```

  - #### **Technical Architecture**

    - **Array-based computation**: All raster operations performed via NumPy for efficiency (avoids pixel-by-pixel cursor operations)
    - **Lazy evaluation**: Rasters loaded only when needed (one species/year at a time)
    - **Memory efficiency**: Processes complete regions before cleanup; avoids storing all input rasters simultaneously
    - **Coordinate system consistency**: Output rasters tied to `region_raster_mask` extent/resolution/SR
    - **Batch parallelism**: Director splits 15 IDW regions into 5 sequential batches (3 regions each) to manage CPU load across multiple `director()` calls
    - **Dual richness generation**: Single worker pass generates both total and core richness by filtering CoreSpecies flag during accumulation


- ### Create Region Mosaics Director and Worker
  - This director/worker pair creates mosaic datasets and Cloud Raster Format (CRF) files from interpolated species rasters, enabling efficient multi-band image services for portal publishing.

  ### **Director (create_mosaics_director.py)**

  **Purpose**: Orchestrates mosaic dataset creation for all IDW regions, aggregating species rasters into multi-dimensional mosaic structures for web services.

  **Key Functions:**

  1. **`director(project_gdb, Sequential, table_names)`** — Main orchestration function:
    - **Pre-processing** (sequential):
      - Calls `preprocessing()` to stage data for each region into separate GDBs
      - Creates region-specific workspaces under Scratch folder
    
    - **Sequential or parallel processing**:
      - **Sequential mode**: Calls `worker()` sequentially for each region
      - **Parallel mode**: Uses `multiprocessing.Pool` (processes = CPU count - 2, maxtasksperchild=1); monitors job completion with status polling every ~7.5×processes seconds
    
    - **Post-processing** (sequential):
      - Walks scratch folder collecting all mosaic datasets and `.crf` files
      - Copies mosaic datasets to project GDB
      - Copies `.crf` files to `CRFs` folder
      - Calls `dismap_tools.import_metadata()` to attach metadata
      - Deletes source datasets from scratch
      - Compacts project GDB

  2. **`script_tool(project_gdb)`** — Entry point with test mode:
    - Currently in test mode: `Sequential=True, table_names=["SEUS_FAL_IDW"]`
    - Alternative production batches commented (non-sequential options available)
    - Logs timing and environment info

  ### **Worker (create_mosaics_worker.py)**

  **Purpose**: For a single region, creates a mosaic dataset by aggregating all interpolated species rasters, then exports to Cloud Raster Format (CRF) for efficient storage and web service delivery.

  **Processing Pipeline:**

  #### **Phase 1: Prepare Output Paths & Metadata**

  - Queries `Datasets` table for region metadata:
    - Extracts: TableName, DatasetCode, CellSize, MosaicName, MosaicTitle
    
  - Sets output coordinate system from `{table_name}_Raster_Mask` spatial reference

  #### **Phase 2: Build Input Raster List**

  - Queries `{table_name}_LayerSpeciesYearImageName` table for all rasters to include
  - Filters by: `DatasetCode = '{datasetcode}'` (region-specific data)
  - Extracts: Variable, ImageName
  - Constructs input raster paths:
    - Path format: `{project_folder}\Images\{table_name}\{variable}\{image_name}.tif`
    - Special handling: Prepends underscore to "Species Richness" variable for folder naming
    - Validates: Each raster file must exist; logs errors for missing files
  - Result: List of input_raster_paths for mosaic ingestion

  #### **Phase 3: Create Mosaic Dataset**

  - Calls `arcpy.management.CreateMosaicDataset()`:
    - Workspace: region GDB
    - Name: `{mosaic_name}` (e.g., `AI_IDW_Mosaic`)
    - Coordinate system: From region raster mask (region-specific projection)
    - Pixel type: 32-bit float (matches interpolated raster values)
    - One band (single-band species/richness rasters)

  #### **Phase 4: Load Rasters into Mosaic**

  - Calls `arcpy.management.AddRastersToMosaicDataset()` with parameters:
    - Raster type: "Raster Dataset" (add pre-existing TIF rasters)
    - Input path: List of all input_raster_paths from Phase 2
    - **Cell size handling**:
      - `update_cellsize_ranges = "UPDATE_CELL_SIZES"` — Automatically determine cell size ranges
    - **Boundary handling**:
      - `update_boundary = "UPDATE_BOUNDARY"` — Update mosaic extent from input rasters
    - **Pyramid/statistics**:
      - `build_pyramids = "NO_PYRAMIDS"` — Skip pyramid building for now
      - `calculate_statistics = "NO_STATISTICS"` — Skip statistics calculation during load
      - `estimate_statistics = "NO_STATISTICS"` — Don't estimate statistics
    - **Duplicate handling**:
      - `duplicate_items_action = "EXCLUDE_DUPLICATES"` — Skip duplicate rasters
    - **Spatial reference**:
      - `force_spatial_reference = "FORCE_SPATIAL_REFERENCE"` — Force region-specific SR
    - Minimum dimension: 1500 (cells) — Only include larger rasters

  #### **Phase 5: Join Metadata Attributes**

  - Calls `arcpy.management.JoinField()`:
    - Join on: Mosaic catalog Name field ← LayerSpeciesYearImageName ImageName field
    - Joins fields:
      - DatasetCode, Region, Season, Species, CommonName, SpeciesCommonName
      - CoreSpecies, Year, StdTime, Variable, Value, Dimensions
    - Result: Mosaic catalog rows enriched with species/year/metadata attributes

  #### **Phase 6: Create Attribute Indexes**

  - Removes existing index if present: `{table_name}_MosaicSpeciesIndex`
  - Creates new non-unique index on: Species, CommonName, SpeciesCommonName, Year
  - Improves query performance for species-based filtering in web services

  #### **Phase 7: Calculate Statistics**

  - Calls `arcpy.management.CalculateStatistics()` with:
    - Skip existing: False (recalculate)
    - x_skip_factor / y_skip_factor: 1 (use all data)

  #### **Phase 8: Configure Mosaic Properties**

  - Calls `arcpy.management.SetMosaicDatasetProperties()` with detailed configuration:
    - **Image sizing**:
      - Maximum image size: 4100×15000 pixels (supports large composite images)
    - **Compression**:
      - Allowed: LZ77, None
      - Default: LZ77
      - JPEG quality: 75%
      - LERC tolerance: 0.01
    - **Resampling/display**:
      - Resampling: BILINEAR
      - Clip to footprints: NOT_CLIP
      - Clip to boundary: CLIP (constrain to mosaic extent)
      - Blend width: 10 pixels (feather edges)
      - Viewpoint: 600×300 (north corner bias)
    - **Mosaic operations**:
      - Method: FIRST (display first raster when overlapping)
      - Max items per mosaic: 50 (limit composite slices)
      - Cell size tolerance: 0.8 (80% match required)
      - Cell size: `{cell_size} {cell_size}` (from region metadata)
    - **Metadata**:
      - Level: FULL (include all metadata)
      - Transmission fields: All mosaic catalog fields
    - **Temporal dimension**:
      - Time enabled: YES
      - Start/end time field: StdTime (same field for point-in-time data)
      - Time format: "YYYY" (year-only dimension)
      - Time interval: 1 year
      - Time interval units: Years
    - **Service capabilities**:
      - Max download items: 20
      - Max records returned: 1000
      - Data source type: GENERIC
      - Minimum pixel contribution: 1 (include all valid pixels)

  #### **Phase 9: Analyze Mosaic Dataset**

  - Calls `arcpy.management.AnalyzeMosaicDataset()` with checker keywords:
    - FOOTPRINT, FUNCTION, RASTER, PATHS, SOURCE_VALIDITY, STALE
    - PYRAMIDS, STATISTICS, PERFORMANCE, INFORMATION
    - Validates: All rasters are accessible, pyramids/statistics present, performance optimal

  #### **Phase 10: Build Multidimensional Information**

  - Calls `arcpy.md.BuildMultidimensionalInfo()`:
    - Variable field: "Variable" (species name or "Species Richness")
    - Dimension fields: StdTime (Time Step, Year)
    - Enables time-based slicing: Web services can query by year
    - Deletes existing multidimensional info before rebuilding

  #### **Phase 11: Export to Cloud Raster Format (CRF)**

  - Calls `arcpy.management.CopyRaster()`:
    - Source: Mosaic dataset (in-memory processed)
    - Output: `{scratch_folder}\{table_name}\{mosaic_name}.crf`
    - Format: CRF (Cloud Raster Format — compressed, cloud-optimized)
    - Pixel type: 32-bit float (maintains scientific precision)
    - NoData value: -3.40282e+38 (minimum float32 sentinel)
    - Process as multidimensional: ALL_SLICES (export all time steps)
    - No transpose (keep dimension order)

  - Calls `arcpy.management.CalculateStatistics()` on CRF output

  #### **Phase 12: Cleanup**

  - Deletes intermediate tables: Datasets, LayerSpeciesYearImageName, Raster_Mask
  - Compacts region GDB

  ### **Key Data Operations**

  1. **Multi-Dimensional Raster Assembly:**
    - Combines many 2D rasters (species/year) into 4D mosaic (X, Y, Species, Time)
    - Dimension fields enable web service queries: "Get richness for 2020"

  2. **Metadata Enrichment via Join:**
    - Links mosaic catalog (N rows = N input rasters) to species/year metadata
    - Enables filtering/sorting by taxonomy, management body, temporal attributes

  3. **Temporal Dimension:**
    - StdTime field as single timestamp per year (point-in-time data)
    - Time format "YYYY" enables time-series visualization in web services

  4. **Cloud Raster Format Export:**
    - CRF enables efficient tiling, caching, and pyramid generation
    - Supports efficient web delivery without additional processing

  ### **Integration Points**

  - **Inputs**:
    - Interpolated species rasters from `create_rasters_worker` (TIF files)
    - Species richness rasters from `create_species_richness_rasters_worker` (TIF files)
    - `{table_name}_LayerSpeciesYearImageName` table (raster metadata catalog)
    - `Datasets` table (region metadata: CellSize, MosaicName)
    - `{table_name}_Raster_Mask` (spatial template: extent, resolution, SR)

  - **Outputs**:
    - `{table_name}_Mosaic` mosaic dataset in project GDB
    - `{table_name}.crf` cloud raster format file in `CRFs` folder
    - Mosaic indexed on: Species, CommonName, Year (for web service queries)
    - Multidimensional structure: Variable (species) × Time (year)

  - **Data flow**:
    ```
    Interpolated Species/Richness TIFs
            → AddRastersToMosaicDataset → Build Mosaic Catalog
            ↓
    LayerSpeciesYearImageName Table (Metadata)
            → JoinField → Enrich Catalog
            ↓
    SetMosaicDatasetProperties (Configure temporal, compression, bounds)
            → BuildMultidimensionalInfo (Enable time-series)
            → CopyRaster to CRF (Cloud-optimized export)
            ↓
    CRF File (Portal publishing) + Mosaic Dataset (Project GDB)
    ```

  - #### **Technical Architecture**

    - **Mosaic as aggregation layer**: Combines isolated raster files (TIFs) into unified queryable structure
    - **Temporal indexing**: StdTime field enables time-series web services without refactoring
    - **Cloud Raster Format**: Enables efficient caching and pyramid generation for web services
    - **Multidimensional support**: Allows portal to expose "Variable" (species) and "Year" (time) as separate dimensions
    - **Metadata join pattern**: Links mosaic records to taxonomy/management attributes for UI filtering
    - **Batch parallelism**: Director processes multiple regions in parallel; each worker independently creates mosaic

- ### Create Indicators Table Director and Worker
  - This director/worker pair generates distribution indicators (center of gravity, min/max coordinates, depth statistics) for each species/year combination using spatial statistics derived from interpolated raster surfaces.

  - #### **Director (create_indicators_table_director.py)**

  - **Purpose**: Orchestrates distribution indicator calculation for all IDW regions, aggregating species-specific spatial statistics into region-level indicator tables.

  - **Key Functions:**

    1. **`director(project_gdb, Sequential, table_names)`** — Main orchestration function:
       - **Pre-processing** (sequential):
         - Calls `preprocessing()` to stage raster and metadata data for each region
         - Creates region-specific GDBs under Scratch folder
       
       - **Sequential or parallel processing**:
         - **Sequential mode**: Calls `worker()` sequentially for each region
         - **Parallel mode**: Uses `multiprocessing.Pool` (processes = CPU count - 2, maxtasksperchild=1); monitors job completion with status polling every ~7.5×processes seconds
       
       - **Post-processing** (sequential):
         - Walks scratch folder collecting all generated `*_Indicators` tables and feature classes
         - Copies each to project GDB
         - Compacts project GDB

    2. **`process_indicator_tables(project_gdb)`** — Consolidation function:
       - Creates master `Indicators` table in project GDB
       - Adds standardized fields via `dismap_tools.add_fields()`
       - Appends all region-specific `*_Indicators` tables into master table
       - Replaces None values with empty strings in string fields
       - Updates DateCode field using `dismap_tools.date_code()` for standardization
       - Synchronizes metadata

    3. **`script_tool(project_gdb)`** — Entry point with test mode:
       - Currently disabled: Test=False (director calls commented out)
       - Calls `process_indicator_tables()` to combine all indicator tables into master
       - Logs timing and environment info

    ### **Worker (create_indicators_table_worker.py)**

    **Purpose**: For a single region, calculates distribution indicators (center of gravity, percentile bounds, offsets, standard errors) for each species/year from biomass rasters.

    **Processing Pipeline:**

    #### **Phase 1: Create Indicators Table & Load Data**

    - Creates empty table: `{table_name}_Indicators`
    - Calls `dismap_tools.add_fields()` to populate schema (200+ fields from `field_definitions.json`)
    - Queries `Datasets` table for region metadata:
      - Extracts: DatasetCode, TableName, CellSize, Region, Season, DateCode, DistributionProjectCode, DistributionProjectName, SummaryProduct

    #### **Phase 2: Set Spatial Environment**

    - Sets environment parameters:
      - Cell size: From region metadata
      - Extent, mask, snapRaster: From `{table_name}_Raster_Mask` (spatial alignment)
    - Prepares raster references:
      - `{table_name}_Bathymetry` — Depth values per cell (negative values; zero is surface)
      - `{table_name}_Latitude` — Geographic latitude per cell
      - `{table_name}_Longitude` — Geographic longitude per cell (0-360 initially, converted to -180 to 180)

    #### **Phase 3: Prepare Raster Catalog**

    - Queries `{table_name}_LayerSpeciesYearImageName` for all species rasters
    - Filters: `DatasetCode = '{datasetcode}'` AND `NOT Species Richness`
    - Builds input_rasters nested dict structure: `{variable: {year: [metadata + path]}}`
    - Validates: Each raster file exists

    #### **Phase 4: Calculate Distribution Indicators (Per Species/Year)**

    For each species and year, calculates 5 dimensions of distribution:

    ##### **A. Biomass Statistics**
    - Loads biomass raster as NumPy array (from species/year interpolated surface)
    - Replaces negative/zero values with NaN
    - Calculates: `sumBiomassArray = np.nansum(biomassArray)`
    - Logs: Maximum biomass value (>0 indicates valid data)

    ##### **B. Center of Gravity & Percentile Bounds — Latitude**

    - Loads latitude raster array; aligns with biomass (NaN where biomass is NaN)
    - **Percentile calculation**:
      - Sorts latitude values by latitude coordinate
      - Calculates cumulative biomass sum: `cumSum = np.nancumsum(sorted_biomass)`
      - Converts to quantile: `quantile = cumSum / total_biomass`
      - Finds 95th and 5th percentile latitude bounds using closest quantile match
      - Result: `MaximumLatitude` (95th percentile), `MinimumLatitude` (5th percentile)

    - **Center of Gravity**:
      - Calculates weighted latitude: `weighted = biomass × latitude`
      - Result: `CenterOfGravityLatitude = Σ(weighted) / Σ(biomass)`

    - **Offset**:
      - On first year of species: `first_year_offset_latitude = CenterOfGravityLatitude`
      - For subsequent years: `OffsetLatitude = CenterOfGravityLatitude - first_year_offset_latitude`
      - Semantics: Tracks migration direction relative to baseline year

    - **Standard Error**:
      - `variance = np.nanvar(weighted_array)`
      - `count = np.count_nonzero(~np.isnan(weighted_array))`
      - Result: `CenterOfGravityLatitudeSE = √variance / √count`

    ##### **C. Center of Gravity & Percentile Bounds — Longitude**

    - **International Date Line Handling**:
      - Converts longitude from -180/180 to 0/360 range: `lon_360 = np.mod(longitude, 360)`
      - Applies same percentile/CoG/offset/SE calculations as latitude
      - Converts back: `lon_180 = np.mod(lon_360 - 180, 360) - 180`
      - Result: Handles species crossing Pacific antimeridian without wrapping errors

    ##### **D. Center of Gravity & Percentile Bounds — Depth (Bathymetry)**

    - Loads bathymetry raster array (negative values for depth below surface; zero at surface)
    - Aligns with biomass (NaN where biomass is NaN)
    - Applies same percentile/CoG/offset/SE calculations as lat/lon
    - Result: `CenterOfGravityDepth` (weighted mean depth), `MinimumDepth` (5th percentile shallow), `MaximumDepth` (95th percentile deep)

    #### **Phase 5: Row Population**

    For each species/year combination with biomass > 0:
    - Creates row with 26 fields:
      - Standard fields: DatasetCode, Region, Season, DateCode, Species, CommonName, CoreSpecies, Year, DistributionProjectName, DistributionProjectCode, SummaryProduct (11 fields)
      - Latitude indicators: CenterOfGravityLatitude, MinimumLatitude, MaximumLatitude, OffsetLatitude, CenterOfGravityLatitudeSE (5 fields)
      - Longitude indicators: CenterOfGravityLongitude, MinimumLongitude, MaximumLongitude, OffsetLongitude, CenterOfGravityLongitudeSE (5 fields)
      - Depth indicators: CenterOfGravityDepth, MinimumDepth, MaximumDepth, OffsetDepth, CenterOfGravityDepthSE (5 fields)

    For species/years with biomass = 0:
    - All indicator fields set to None (null in GDB)

    #### **Phase 6: Insert Rows into Table**

    - Accumulates all row_values in memory
    - Uses `InsertCursor` to bulk-insert all rows
    - Replaces NaN values (self != self check) with None for proper null handling in GDB
    - Logs final record count: `"{table_name}_Indicators has N records"`

    #### **Phase 7: Cleanup**

    - Deletes intermediate datasets: Datasets, Bathymetry, Latitude, Longitude, Raster_Mask, LayerSpeciesYearImageName
    - Compacts region GDB

    ### **Key Data Operations**

    1. **Weighted Center of Gravity**:
       - Formula: `CoG = Σ(biomass × coordinate) / Σ(biomass)`
       - Effect: Locates mean position weighted by species abundance
       - Used for: Tracking population distribution shifts over time

    2. **Percentile Bounds (5th/95th)**:
       - Accumulates cumulative biomass sum along sorted coordinate axis
       - Finds coordinate where 95% of biomass lies beyond (upper bound) and 5% lies beyond (lower bound)
       - Effect: Robust bounds capturing 90% of population (insensitive to outliers)

    3. **Offset Tracking**:
       - Baseline: First year of each species' data
       - Subsequent years: Difference from baseline CoG
       - Semantics: Measures northward/southward/deepward migration relative to initial distribution

    4. **Standard Error Calculation**:
       - Measures variability in weighted coordinate values
       - Formula: `SE = √(variance) / √(count)`
       - Effect: Indicates confidence in CoG estimate (lower SE = more concentrated distribution)

    ### **Integration Points**

    - **Inputs**:
      - Interpolated species rasters from `create_rasters_worker` (TIF files with WTCPUE)
      - `{table_name}_LayerSpeciesYearImageName` table (species/year catalog)
      - `{table_name}_Raster_Mask` (spatial template)
      - `{table_name}_Bathymetry` (depth raster from `create_region_bathymetry_worker`)
      - `{table_name}_Latitude` and `{table_name}_Longitude` (coordinate rasters from `create_region_fishnets_worker`)
      - `Datasets` table (region metadata)

    - **Outputs**:
      - `{table_name}_Indicators` table — Distribution statistics per species/year
      - Master `Indicators` table (consolidated from all regions)
      - One row per species/year combination with valid biomass

    - **Data flow**:
      ```
      Interpolated Species Rasters (Biomass)
               → NumPy array loading
               ↓
      Latitude/Longitude/Bathymetry Rasters
               → Weighted CoG calculation
               → Percentile bound extraction
               ↓
      Offset tracking (baseline year subtraction)
               → Standard error calculation
               ↓
      Indicators Table Row Construction
               → InsertCursor → Region-specific table
               ↓
      Master Indicators Table (all regions appended)
      ```

    ### **Computational Architecture**

    - **NumPy-based efficiency**: All spatial statistics computed via array operations (no pixel-by-pixel cursors)
    - **Multi-dimensional calculation**: Single pass over rasters generates 5 spatial dimensions (lat, lon, depth × CoG + bounds)
    - **Baseline year tracking**: Per-species first year stored to enable offset calculation
    - **International date line handling**: Special modulo arithmetic prevents wrapping errors at ±180°
    - **Zero-biomass handling**: Skips computation when `maximumBiomass == 0` (avoids NaN propagation)
    - **Batch parallelism**: Director processes multiple regions; each worker independently calculates indicators

    ### **Field Output Summary**

    | Field Group | Fields | Calculation |
    |---|---|---|
    | **Identifiers** | DatasetCode, Region, Season, Year | From Datasets table & raster metadata |
    | **Taxonomy** | Species, CommonName, CoreSpecies | From LayerSpeciesYearImageName |
    | **Spatial Center** | CenterOfGravityLatitude, CenterOfGravityLongitude, CenterOfGravityDepth | Σ(biomass × coordinate) / Σ(biomass) |
    | **Percentile Bounds** | MinimumLatitude, MaximumLatitude, MinimumLongitude, MaximumLongitude, MinimumDepth, MaximumDepth | 5th/95th percentile of coordinate distribution |
    | **Migration** | OffsetLatitude, OffsetLongitude, OffsetDepth | CoG(year) - CoG(first_year) |
    | **Uncertainty** | CenterOfGravityLatitudeSE, CenterOfGravityLongitudeSE, CenterOfGravityDepthSE | √(variance / count) of weighted coordinates |

- ### Publish to Portal Director
  - Publishes processed datasets to ArcGIS Portal with credentials
  - #### **Director(publish_to_portal_director.py)** 

    **Purpose & Architecture:**
    This is the final (10th) director-only file in the DisMAP pipeline, responsible for orchestrating ArcGIS Portal publishing workflows. Unlike previous director/worker pairs that execute parallel spatial processing, this director manages sequential feature service creation, service definition draft generation, metadata enrichment, and portal upload operations. It serves as the gateway for publishing all DisMAP-processed datasets (feature classes, tables, indicators, mosaics) as web services to ArcGIS Portal.

    **Core Functions:**

    1. **`feature_sharing_draft_report(sd_draft="")`** (Lines 17-60)
      - Parses XML service definition draft files (`.sddraft`)
      - Extracts all Key-Value property pairs via DOM parsing
      - Displays configuration details for manual validation before publishing
      - Used for transparency: shows maxRecordCount, ServiceTitle, and all portal configurations
      - Error handling: comprehensive exception catching for XML parsing failures

    2. **`create_feature_class_layers(project_gdb="")`** (Lines 62-420)
      - **Pre-processing phase**: Workspace setup, scratch GDB creation, ArcPy environment configuration
      - **Core logic**: Iterates over all publishable datasets (feature classes + tables):
        - `*Sample_Locations` feature classes
        - `DisMAP_Regions` feature class
        - `Indicators`, `Species_Filter`, `DisMAP_Survey_Info`, species persistence tables
      - **Layer file creation**: For each dataset:
        - Creates feature layer (MakeFeatureLayer) or table view (MakeTableView)
        - Saves as `.lyrx` file to `Layers\` folder with dataset title name
        - Applies metadata copying (title, tags, summary, description, credits, access constraints)
        - Exports layer to PNG thumbnail (288×192 px, 96 DPI)
      - **Time enablement**: Detects `StdTime` field and configures temporal layer properties
        - Sets UTC timezone, calculates temporal extent (start/end dates)
        - Outputs time range diagnostic information
      - **Map & metadata lifecycle**:
        - Creates/overwrites ArcGIS Pro map per dataset
        - Adds layer file + "Terrain with Labels" basemap
        - Saves layer file metadata (title, tags, summary) to XML export
        - Calls `parse_xml_file_format_and_save()` for formatted metadata export
      - **Post-processing**: Cleanup—deletes temporary maps, saves project
      - Integration: Depends on upstream `{table_name}` features created by prior directors

    3. **`create_feature_class_services(project_gdb="")`** (Lines 422-900)
      - **Purpose**: Primary service publishing function—creates feature service definitions, stages, and uploads to Portal
      - **Pre-processing**: Same workspace setup as `create_feature_class_layers()`
      - **Service definition draft generation** (Lines 550-630):
        - Loads layer files from `Layers\` folder
        - Calls `map.getWebLayerSharingDraft()` for FEATURE service type on HOSTING_SERVER
        - Configures draft properties:
          - `allowExporting = False`
          - `offline = False`
          - `overwriteExistingService = True`
          - `portalFolder = "DisMAP {project_name}"`
          - Metadata: credits, description, summary, tags, useLimitations from layer metadata
        - Exports draft to `.sddraft` file in `Publish\` folder
      - **SD Draft XML modification** (Lines 632-680):
        - Parses `.sddraft` XML with DOM
        - Updates `maxRecordCount`: 2000 → 10000 (supports larger queries)
        - Updates `ServiceTitle` to feature service title
        - Writes modified XML back to `.sddraft`
        - Calls `feature_sharing_draft_report()` for validation display
      - **Service staging & upload** (Lines 682-710):
        - `arcpy.server.StageService()`: Creates `.sd` service definition from `.sddraft`
        - `arcpy.server.UploadServiceDefinition()`: Publishes to Portal with parameters:
          - `in_server = "HOSTING_SERVER"` (cloud-based Portal, not federated)
          - `in_folder_type = "FROM_SERVICE_DEFINITION"` (uses embedded folder path)
          - `in_startupType = "STARTED"` (service starts immediately after publishing)
          - `in_override = "OVERRIDE_DEFINITION"` (replaces existing service)
          - `in_my_contents = "NO_SHARE_ONLINE"` (no automatic sharing)
          - `in_public = "PRIVATE"` (private by default; organization can publish)
          - `in_organization = "NO_SHARE_ORGANIZATION"` (no org-wide sharing)
      - **Post-publishing**: Lists all maps in project, saves APRX, cleanup
      - **Integration**: Consumes layer files from `create_feature_class_layers()`, outputs web services on Portal

    4. **`create_image_services(project_gdb="")`** (Lines 902-1220)
      - **Status**: Partially implemented/commented out; framework present but not fully active
      - **Intended purpose**: Image service publishing for mosaic datasets (multidimensional rasters)
      - **Expected workflow** (from commented code):
        - Creates mosaic dataset from source rasters
        - Generates image service definition draft via `CreateImageSDDraft()`
        - Stages and uploads image service to Portal via ArcGIS Server
        - Supports multidimensional imagery with time and variable dimensions
      - **Current state**: Only skeleton implementation; all operational logic in commented sections
      - **Note**: Mosaic creation itself handled by `create_mosaics_director/worker` (prior stage); this would consume those mosaics

    5. **`create_maps(project_gdb="")` & metadata template functions** (Lines 1222-2550+)
      - **Status**: Mostly commented out (development/archive code)
      - **Purpose**: Map layout generation, XML metadata template creation/import, thumbnails
      - **Key archived patterns** (from commented code):
        - Dataset enumeration via `arcpy.da.Walk()` (GDB traversal)
        - Metadata template assignment per dataset type (Indicators, Sample_Locations, Mosaic, etc.)
        - XML metadata export/import: `saveAsXML()`, metadata copying from templates
        - Year range extraction for temporal datasets: `unique_years()` function
        - Layout creation and export to JPEG (map thumbnails)
      - **Note**: These functions likely evolve as Portal metadata publishing strategy matures

    6. **`script_tool(project_gdb="")`** (Lines 2563-2700)
      - **Orchestration driver**: Central control logic for all publishing functions
      - **Execution flags** (all currently False for development/testing):
        - `CreateFeatureClassLayers = False`
        - `CreateFeaturClasseServices = False`
        - `CreateImagesServices = False`
        - `CreateMaps = False`
      - **Timing & diagnostics**:
        - Captures start time via `time.time()`
        - Logs: Python version, environment name, execution location
        - Calculates elapsed time in H:M:S format
      - **Workspace setup**: Creates scratch GDB if missing; sets ArcPy environment
      - **Integration point**: Takes `project_gdb` parameter (default: `August 1 2025.gdb`)
      - **Error handling**: Wraps all function calls in try/except with SystemExit propagation

    **Data Pipeline Integration:**

    ```
    Upstream inputs:
    ├── Feature Classes (created by create_region_sample_locations)
    │   └── *Sample_Locations, DisMAP_Regions
    ├── Tables (created by create_indicators_table, create_species_year_image_name_table)
    │   └── Indicators, Species_Filter, LayerSpeciesYearImageName, Survey Info
    └── Mosaics & CRFs (created by create_mosaics_director/worker)
        └── {Region}_Mosaic, {Region}_Mosaic.crf

    Publishing outputs:
    ├── Feature Services (hosted on Portal)
    │   └── {Dataset Service Title} (with web-accessible points, regions, indicators)
    ├── Image Services (intended, currently inactive)
    │   └── Multidimensional mosaic services (species × year)
    ├── Layer Files (.lyrx format)
    │   └── Stored locally for reuse, metadata-enriched
    └── Metadata XML exports
        └── Formatted metadata in Metadata_Export folder
    ```

    **Technical Patterns & Features:**

    - **Metadata-driven architecture**: Uses `dataset_title_dict()` to lookup service titles, descriptions, credits from centralized metadata dictionary—enables dynamic naming without hardcoding
    - **XML DOM manipulation**: Direct parsing/modification of `.sddraft` files to adjust service parameters (maxRecordCount, ServiceTitle) before staging
    - **Layer file hierarchy**: `.lyrx` files serve as reusable layer definitions—contain symbology, field visibility (e.g., specific fields marked VISIBLE NONE for filtering), time configuration
    - **Portal folder organization**: All services grouped under `"DisMAP {project_name}"` folder for organizational clarity
    - **Temporal configuration**: Automatic time enablement for datasets with `StdTime` field; UTC timezone standardization
    - **Metadata synchronization**: `metadata.synchronize("ALWAYS")` ensures dataset metadata propagates to feature layers and maps
    - **Field visibility control**: Table views configured with specific field info string (26+ fields enumerated for Indicators table with VISIBLE/NONE flags)

    **Known Limitations & Development Notes:**

    - **Image services incomplete**: Framework present but all operational code commented out; mosaic publishing not yet activated
    - **Hardcoded test paths**: Default `project_gdb` points to `"August 1 2025"` directory; production deployment requires parameterization
    - **Portal connection**: Requires authenticated ArcGIS Pro environment; commented code shows Portal URL examples (`https://noaa.maps.arcgis.com/`)
    - **Single-script execution**: No multiprocessing (unlike previous 9 directors); sequential service publishing—upload time depends on dataset complexity
    - **Service definition draft report**: XML parsing via custom function; relies on specific key/value structure (fragile if ArcGIS service format changes)

    **Execution Dependencies & Prerequisites:**

    - ArcGIS Pro with valid Portal credentials
    - Active workspace: project GDB with all upstream datasets
    - Layer files pre-created (normally output from `create_feature_class_layers()`)
    - Scratch workspace for temporary operations
    - Network access to Portal for upload/publish operations

#### Suggestions and Comments

If you see that the data, product, or metadata can be improved, you are invited to create a [pull request](https://github.com/nmfs-fish-tools/DisMAP/pulls) or [submit an issue to the code’s repository](https://github.com/nmfs-fish-tools/DisMAP/issues).

#### NOAA-NMFS GitHub Enterprise Disclaimer

This repository is a scientific product and is not official communication of the National Oceanic and Atmospheric Administration, or the United States Department of Commerce. All NOAA GitHub project code is provided on an ‘as is’ basis and the user assumes responsibility for its use. Any claims against the Department of Commerce or Department of Commerce bureaus stemming from the use of this GitHub project will be governed by all applicable Federal law. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation or favoring by the Department of Commerce. 
The Department of Commerce seal and logo, or the seal and logo of a DOC bureau, shall not be used in any manner to imply endorsement of any commercial product or activity by DOC or the United States Government.

#### NOAA License

Software code created by U.S. Government employees is not subject to copyright in the United States (17 U.S.C. §105). The United States/Department of Commerce reserve all rights to seek and obtain copyright protection in countries other than the United States for Software authored in its entirety by the Department of Commerce. To this end, the Department of Commerce hereby grants to Recipient a royalty-free, nonexclusive license to use, copy, and create derivative works of the Software outside of the United States.

<img src="https://raw.githubusercontent.com/nmfs-general-modeling-tools/nmfspalette/main/man/figures/noaa-fisheries-rgb-2line-horizontal-small.png" alt="NOAA Fisheries" height="75"/>

[U.S. Department of Commerce](https://www.commerce.gov/) \| [National Oceanographic and Atmospheric Administration](https://www.noaa.gov) \| [NOAA Fisheries](https://www.fisheries.noaa.gov/)

