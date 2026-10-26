"""IFC File Inspector module.

Extracts metadata, schema, unit info, and placement coordinates
for display in the GUI without heavy computation.
"""

import os
from typing import Dict, Any, Optional

try:
    import ifcopenshell.util.shape
except Exception:
    pass

import ifcopenshell
import ifcopenshell.util.unit
import ifcopenshell.util.placement


def inspect_ifc_file(file_path: str) -> Dict[str, Any]:
    """Inspects an IFC file and extracts summary information.

    :param file_path: Path to the .ifc file.
    :return: Dictionary with file details.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    size_bytes = os.path.getsize(file_path)
    filename = os.path.basename(file_path)

    try:
        model = ifcopenshell.open(file_path)
    except Exception as e:
        return {
            "valid": False,
            "filename": filename,
            "file_path": file_path,
            "size_bytes": size_bytes,
            "size_mb": size_bytes / (1024 * 1024),
            "error": str(e),
            "schema": "Unknown",
            "unit_name": "Unknown",
            "unit_scale": 1.0,
            "products_count": 0,
            "root_placements_count": 0,
            "current_origin": (0.0, 0.0, 0.0),
            "project_name": "—",
        }

    schema = getattr(model, "schema", "IFC2X3")

    # Project unit
    unit_name = "Unknown"
    unit_scale = 1.0
    try:
        proj_unit = ifcopenshell.util.unit.get_project_unit(model, "LENGTHUNIT")
        if proj_unit:
            unit_name = ifcopenshell.util.unit.get_full_unit_name(proj_unit)
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(model)
    except Exception:
        pass

    # Project info
    project_name = "—"
    try:
        projects = model.by_type("IfcProject")
        if projects and projects[0].Name:
            project_name = str(projects[0].Name)
    except Exception:
        pass

    # Products and placements
    products_count = 0
    products_with_placement = 0
    root_placements = set()
    current_origin = (0.0, 0.0, 0.0)

    try:
        for product in model.by_type("IfcProduct"):
            products_count += 1
            if product.ObjectPlacement:
                products_with_placement += 1
                pl = product.ObjectPlacement
                while getattr(pl, "PlacementRelTo", None) is not None:
                    pl = pl.PlacementRelTo
                if pl.is_a("IfcLocalPlacement"):
                    root_placements.add(pl)

        # Get origin of first root placement for preview
        if root_placements:
            first_root = next(iter(root_placements))
            mat = ifcopenshell.util.placement.get_local_placement(first_root)
            current_origin = (float(mat[0, 3]), float(mat[1, 3]), float(mat[2, 3]))
    except Exception:
        pass

    return {
        "valid": True,
        "filename": filename,
        "file_path": file_path,
        "size_bytes": size_bytes,
        "size_mb": size_bytes / (1024 * 1024),
        "schema": schema,
        "unit_name": unit_name,
        "unit_scale": unit_scale,
        "project_name": project_name,
        "products_count": products_count,
        "products_with_placement": products_with_placement,
        "root_placements_count": len(root_placements),
        "current_origin": current_origin,
    }
