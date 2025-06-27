import datetime
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, List, Optional


def _prop(root: ET.Element, name: str) -> Optional[str]:
    el = root.find(f".//Property[@name='{name}']")
    return el.attrib.get("value") if el is not None else None


def _parse_ordered_at(folder_name: str) -> Optional[datetime.datetime]:
    try:
        parts = folder_name.split('_')[:2]
        stamp = ''.join(parts)
        dt = datetime.datetime.strptime(stamp, "%Y%m%d%H%M")
        return dt.replace(tzinfo=datetime.timezone.utc)
    except Exception:
        return None


def parse_case_xml(xml_path: Path, folder_path: Path) -> Dict[str, Any]:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    items: List[Dict[str, Any]] = []
    for obj in root.findall(".//Object[@type='TDM_Item_ToothElement']"):
        tooth = obj.find(".//Property[@name='ToothCode']")
        rtype = obj.find(".//Property[@name='RestorationTypeID']")
        if tooth is not None and rtype is not None:
            items.append({
                "tooth": int(tooth.attrib.get("value")),
                "type": rtype.attrib.get("value"),
            })

    shade = None
    mat_xml = folder_path / "Materials.xml"
    if mat_xml.exists():
        mroot = ET.parse(mat_xml).getroot()
        cid = _prop(mroot, "ColorID")
        mid = _prop(mroot, "MaterialID")
        if mid:
            shade = mid
            if cid:
                shade = f"{mid}_{cid}"

    patient_last = _prop(root, "Patient_LastName") or ""
    patient_first = _prop(root, "Patient_FirstName") or ""

    return {
        "case_id": _prop(root, "IntOrderID") or folder_path.name,
        "patient_name": f"{patient_last} {patient_first}".strip(),
        "patient_ref": _prop(root, "Patient_RefNo"),
        "ordered_at": _parse_ordered_at(folder_path.name),
        "restoration_items": items,
        "shade_material": shade,
    }
