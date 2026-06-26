#!/usr/bin/env python3
"""Simple validator for Metadata_Export XML files.

Checks multiple metadata elements for presence and reports which are
likely user-maintained vs automatically managed by ArcGIS Pro.

Fields checked and assumed source:
 - title (`resTitle`): user
 - abstract (`idAbs`): user
 - mdFileID (`mdFileID`): user
 - contact (email/org/person): user
 - keywords (`themeKeys`/`placeKeys`): user
 - publication date (`idCitation/date/pubDate`): user
 - maintenance frequency (`resMaint/maintFreq`): user
 - data presentation form (`presForm`): user
 - bounding box (west/east/north/south): arcgis
 - Esri creation date (`Esri/CreaDate`): arcgis

The script writes a CSV with boolean flags for each field plus a
`missing_user_action` column listing missing fields that need user input.
"""
import csv
import os
import sys
import xml.etree.ElementTree as ET


def find_text_by_localname(root, localname):
    for elem in root.iter():
        if isinstance(elem.tag, str) and elem.tag.endswith("}" + localname):
            return (elem.text or "").strip()
        if isinstance(elem.tag, str) and elem.tag == localname:
            return (elem.text or "").strip()
    return ""


def find_all_localnames(root, localname):
    vals = []
    for elem in root.iter():
        if not isinstance(elem.tag, str):
            continue
        if elem.tag.endswith("}" + localname) or elem.tag == localname:
            if (elem.text or "").strip():
                vals.append((elem.text or "").strip())
    return vals


def has_contact(root):
    # look for email or organization name in common contact elements
    for elem in root.iter():
        tag = elem.tag
        if not isinstance(tag, str):
            continue
        lname = tag.split("}")[-1]
        if lname in ("eMailAdd", "rpOrgName", "rpIndName"):
            if (elem.text or "").strip():
                return True
    return False


def has_bbox(root):
    # common ISO element names for bounding box
    required = (
        "westBoundLongitude",
        "eastBoundLongitude",
        "northBoundLatitude",
        "southBoundLatitude",
    )
    found = set()
    for elem in root.iter():
        if not isinstance(elem.tag, str):
            continue
        lname = elem.tag.split("}")[-1]
        if lname in required and (elem.text or "").strip():
            found.add(lname)
    return len(found) == 4


def has_keywords(root):
    # look for any <keyword> elements under themeKeys or placeKeys or elsewhere
    kws = find_all_localnames(root, "keyword")
    return len(kws) > 0


def validate_file(path):
    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except Exception as e:
        return {"error": str(e)}

    # basic checks
    title = find_text_by_localname(root, "resTitle")
    abstract = find_text_by_localname(root, "idAbs")
    mdFileID = find_text_by_localname(root, "mdFileID")
    contact = has_contact(root)

    # additional checks
    keywords = has_keywords(root)
    pubdate = find_text_by_localname(root, "pubDate")
    maintfreq = find_text_by_localname(root, "MaintFreqCd") or find_text_by_localname(
        root, "maintFreq"
    )
    presform = find_text_by_localname(root, "PresFormCd") or find_text_by_localname(
        root, "presForm"
    )
    esri_crea = find_text_by_localname(root, "CreaDate") or find_text_by_localname(
        root, "Esri/CreaDate"
    )
    bbox = has_bbox(root)
    # extended checks
    # extent CRS - ArcGIS usually populates spatial reference info
    extent_crs = bool(
        find_text_by_localname(root, "referenceSystemIdentifier")
        or find_text_by_localname(root, "srsName")
        or find_text_by_localname(root, "referenceSystem")
        or find_text_by_localname(root, "gmd:referenceSystemInfo")
    )

    # contact roles (e.g., originator, point of contact, metadata contact)
    contact_roles = False
    for elem in root.iter():
        if not isinstance(elem.tag, str):
            continue
        lname = elem.tag.split("}")[-1]
        if (
            lname in ("RoleCd", "role")
            and (elem.text or elem.get("value") or "").strip()
        ):
            contact_roles = True
            break

    # data sources and process steps
    data_sources = bool(
        find_all_localnames(root, "srcInfo")
        or find_all_localnames(root, "source")
        or find_all_localnames(root, "sourceDesc")
    )
    process_steps = bool(find_all_localnames(root, "processStep"))

    # distribution info
    distribution = bool(
        find_all_localnames(root, "distInfo")
        or find_all_localnames(root, "distributor")
        or find_all_localnames(root, "distorCont")
    )

    # license / use constraints
    license_info = bool(
        find_all_localnames(root, "useLimitation")
        or find_all_localnames(root, "accessConstraints")
        or find_all_localnames(root, "useConstraints")
    )

    # mapping of field -> (present_bool, source)
    checks = {
        "title": (bool(title), "user"),
        "abstract": (bool(abstract), "user"),
        "mdFileID": (bool(mdFileID), "user"),
        "contact": (contact, "user"),
        "keywords": (keywords, "user"),
        "publication_date": (bool(pubdate), "user"),
        "maintenance_frequency": (bool(maintfreq), "user"),
        "presentation_form": (bool(presform), "user"),
        "esri_creation_date": (bool(esri_crea), "arcgis"),
        "bbox": (bbox, "arcgis"),
        "extent_crs": (extent_crs, "arcgis"),
        "contact_roles": (contact_roles, "user"),
        "data_sources": (data_sources, "user"),
        "process_steps": (process_steps, "user"),
        "distribution": (distribution, "user"),
        "license": (license_info, "user"),
    }

    return {
        "checks": checks,
        "title": title,
        "mdFileID": mdFileID,
        "pubdate": pubdate,
        "error": None,
    }


def main():
    base = os.path.join(
        os.path.dirname(__file__), "..", "February 1 2026", "Metadata_Export"
    )
    base = os.path.normpath(base)
    if not os.path.isdir(base):
        print("Metadata_Export folder not found at", base)
        sys.exit(2)

    out_path = os.path.join(os.path.dirname(__file__), "metadata_validation_report.csv")
    files = [f for f in os.listdir(base) if f.lower().endswith(".xml")]
    files.sort()

    # define fields and output header
    fields = [
        ("title", "Title"),
        ("abstract", "Abstract"),
        ("mdFileID", "MD File ID"),
        ("contact", "Contact"),
        ("keywords", "Keywords"),
        ("publication_date", "Publication Date"),
        ("maintenance_frequency", "Maintenance Frequency"),
        ("presentation_form", "Presentation Form"),
        ("esri_creation_date", "EsriCreationDate"),
        ("bbox", "BoundingBox"),
    ]

    header = ["filename"]
    for key, label in fields:
        header.append(f"{label}_present")
        header.append(f"{label}_source")
    header += [
        "title",
        "mdFileID",
        "pubdate",
        "missing_user_action",
        "missing_arcgis_auto",
        "error",
    ]

    with open(out_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for fn in files:
            path = os.path.join(base, fn)
            res = validate_file(path)
            if "error" in res and res["error"]:
                # write row with error
                row = [fn] + [""] * (len(header) - 2) + [res["error"]]
                writer.writerow(row)
                continue

            checks = res.get("checks", {})
            row = [fn]
            missing_user = []
            missing_arcgis = []
            for key, _ in fields:
                present, source = checks.get(key, (False, "unknown"))
                row.append(str(bool(present)))
                row.append(source)
                if not present:
                    if source == "user":
                        missing_user.append(key)
                    elif source == "arcgis":
                        missing_arcgis.append(key)

            row.append(res.get("title", ""))
            row.append(res.get("mdFileID", ""))
            row.append(res.get("pubdate", ""))
            row.append(";".join(missing_user))
            row.append(";".join(missing_arcgis))
            row.append("")
            writer.writerow(row)

    print("Validation complete. Report at:", out_path)


if __name__ == "__main__":
    main()

# This is an autogenerated comment.
